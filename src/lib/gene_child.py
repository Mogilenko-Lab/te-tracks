"""Subtract a pinned exon union and register retained blocks to the parent catalog."""

import argparse
from collections import Counter
from contextlib import ExitStack
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
from build_exports import (COMPONENT, IDENTIFIER, EXPORT_CONTRACTS, MEMBER_COLUMNS,
                           sort_export, taxonomy_labels, validate, write_inventory)
from build_universes import evaluate_predicate
from contigs import rename_export
from records_io import tsv_stream, write_frame, write_tsv


COPIED_INPUTS = ("universes.json", "tables/contig_aliases.tsv")
CHILD_UNIVERSES = ("interspersed", "compat_tetranscripts_mm39")
CHILD_ROSTER = (("subfamily.saf", "subfamily"), ("taxonomy_triple.saf", "taxonomy_triple"))
VARIANT = "exon_subtracted"
MASK_SENTENCE = "The mask unions every exon on both strands, merging overlapping or touching intervals."
STATUS_COLUMNS = ["rmsk_record_id", "status", "n_blocks", "retained_bp", "removed_bp"]
SUMMARY_COLUMNS = ["universe_name", "records", "unchanged", "trimmed", "split", "fully_subtracted",
                   "retained_records", "blocks", "retained_bp", "removed_bp", "records_on_unannotated_contigs"]
RECORD_COLUMNS = ["rmsk_record_id", "chrom", "start_1", "end_1", "strand", "rmsk_name",
                  "rmsk_class", "rmsk_family", "length_bp"]


def policy_bundle(config):
    policy = {"exon_mask_policy": config["EXON_MASK_POLICY"], "mask_definition": MASK_SENTENCE,
            "min_retained_block_bp": int(config["MIN_RETAINED_BLOCK_BP"]),
            "context_capability": config["CONTEXT_CAPABILITY"]}
    if policy["context_capability"] == "transcript_geometry_v1":
        from transcript_context import CONTEXT_POLICY
        policy.update({key: int(config[key.upper()]) if isinstance(value, int) else config[key.upper()]
                       for key, value in CONTEXT_POLICY.items()})
    return policy


def validate_policy(policy):
    from manifest import require
    from transcript_context import CONTEXT_POLICY
    legacy = {"exon_mask_policy": "all_exons_unstranded_union_v1",
              "mask_definition": MASK_SENTENCE, "min_retained_block_bp": 1,
              "context_capability": "not_computed"}
    geometry = {**legacy, "context_capability": "transcript_geometry_v1", **CONTEXT_POLICY}
    require(policy in (legacy, geometry), "unsupported gene policy bundle")


def write_sources(build_dir, parent_dir, config):
    from manifest import digest_file, read_json, require, source_path
    parent = read_json(parent_dir / "MANIFEST.json")["identity"]
    role = {"url": config["GENE_GTF_URL"], "md5": config["GENE_GTF_MD5"]}
    path = build_dir / source_path(role)
    require(digest_file(path, "md5") == role["md5"], "gene_gtf: source md5 mismatch")
    role["bytes"] = path.stat().st_size
    sources = {"genome": config["GENOME"], "assembly": config["ASSEMBLY"],
               "parent_family": config["PARENT_FAMILY"],
               "parent_build_id": (parent_dir / "BUILD_ID").read_text().strip(),
               "parent_catalog_id": (parent_dir / "CATALOG_ID").read_text().strip(),
               "gene_annotation_name": config["GENE_ANNOTATION_NAME"],
               "sources": {"gene_gtf": role}, "policy_bundle": policy_bundle(config),
               "child_universes": config["CHILD_UNIVERSES"].split()}
    require(parent["family"] == sources["parent_family"], "parent family differs")
    (build_dir / "source/SOURCES.json").write_text(json.dumps(sources, indent=2) + "\n")


def copy_parent_inputs(build_dir, parent_dir):
    from manifest import digest_file, read_json, require
    sources = read_json(build_dir / "source/SOURCES.json")
    entries = {item["path"]: item for item in read_json(parent_dir / "MANIFEST.json")["identity"]["inventory"]}
    digests = {}
    for relative in COPIED_INPUTS:
        target = build_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(parent_dir / relative, target)
        digests[relative] = digest_file(target)
        require(digests[relative] == entries[relative]["sha256"], f"copied input differs: {relative}")
    sources["copied_inputs"] = digests
    (build_dir / "source/SOURCES.json").write_text(json.dumps(sources, indent=2) + "\n")


def annotation_mask(gtf, alias_path):
    """Normalize every annotation row and merge inclusive exon intervals on each contig."""
    from manifest import require
    aliases = pd.read_csv(alias_path, sep="\t", dtype=str, keep_default_na=False)
    for column in ("chrom_ucsc", "chrom_gencode"):
        require(aliases[column].is_unique, f"ambiguous annotation alias: {column}")
    mapping = aliases.set_index("chrom_gencode")["chrom_ucsc"].to_dict()
    lengths = aliases.set_index("chrom_ucsc")["length_bp"].astype(int).to_dict()
    counts = {chrom: Counter() for chrom in lengths}
    exons = {chrom: [] for chrom in lengths}
    with gzip.open(gtf, "rt") as stream:
        for number, line in enumerate(stream, 1):
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            require(len(fields) == 9, f"GTF row {number}: expected nine columns")
            require(fields[0] in mapping, f"unmapped GTF contig: {fields[0]}")
            chrom = mapping[fields[0]]
            start, end = int(fields[3]), int(fields[4])
            require(1 <= start <= end <= lengths[chrom], f"GTF bounds differ: row {number}")
            counts[chrom]["rows"] += 1
            counts[chrom][fields[2]] += 1
            if fields[2] == "exon":
                exons[chrom].append((start, end))
    mask, coverage = {}, []
    for chrom in sorted(lengths):
        merged = []
        for start, end in sorted(exons.pop(chrom)):
            if merged and start <= merged[-1][1] + 1:
                merged[-1][1] = max(end, merged[-1][1])
            else:
                merged.append([start, end])
        mask[chrom] = np.asarray(merged, dtype=np.int64).reshape(-1, 2)
        coverage.append({"chrom_ucsc": chrom, **{f"{kind}_rows": counts[chrom][kind]
                         for kind in ("gene", "transcript", "exon")},
                         "exon_union_bp": sum(end - start + 1 for start, end in merged),
                         "annotated": bool(counts[chrom]["rows"])})
    return mask, pd.DataFrame(coverage)


def subtract_batch(records, mask):
    """Return ordered blocks and conserved status for every record in a batch."""
    start = records.start_1.to_numpy()
    end = records.end_1.to_numpy()
    counts = np.ones(len(records), dtype=np.int64)
    kept = end - start + 1
    affected, pieces = [], []
    for chrom, indices in records.groupby("chrom", sort=False).indices.items():
        intervals = mask[chrom]
        if not len(intervals):
            continue
        lo = np.searchsorted(intervals[:, 1], start[indices], side="left")
        hi = np.searchsorted(intervals[:, 0], end[indices], side="right")
        for offset in np.flatnonzero(lo < hi):
            index = int(indices[offset])
            cursor, bound = int(start[index]), int(end[index])
            blocks = []
            for left, right in intervals[lo[offset]:hi[offset]]:
                if cursor < left:
                    blocks.append((cursor, int(left) - 1))
                cursor = max(cursor, int(right) + 1)
            if cursor <= bound:
                blocks.append((cursor, bound))
            counts[index] = len(blocks)
            kept[index] = sum(b - a + 1 for a, b in blocks)
            affected.append(index)
            pieces.append(blocks)
    owners = np.repeat(np.arange(len(records)), counts)
    block_start, block_end = start[owners].copy(), end[owners].copy()
    offsets = np.r_[0, np.cumsum(counts)]
    for index, blocks in zip(affected, pieces):
        for offset, (left, right) in enumerate(blocks, int(offsets[index])):
            block_start[offset], block_end[offset] = left, right
    removed = end - start + 1 - kept
    status = np.where(counts == 0, "fully_subtracted", np.where(removed == 0, "unchanged",
                      np.where(counts > 1, "split", "trimmed")))
    statuses = pd.DataFrame({"rmsk_record_id": records.rmsk_record_id, "status": status,
                             "n_blocks": counts, "retained_bp": kept, "removed_bp": removed})
    blocks = records.iloc[owners].reset_index(drop=True)
    blocks["block_start_1"], blocks["block_end_1"] = block_start, block_end
    return blocks, statuses


def record_batches(parent_dir):
    parquet = pq.ParquetFile(parent_dir / "tables/rmsk_records.parquet")
    for batch in parquet.iter_batches(batch_size=100_000, columns=RECORD_COLUMNS):
        yield batch.to_pandas()


def registration_frame(blocks, universe, variant, level, labels):
    """Bind explicit block bounds to one namespace-invariant feature grammar."""
    feature = blocks.rmsk_name if level == "subfamily" else blocks.rmsk_name.map(lambda name: labels[name][3])
    return pd.DataFrame({"universe_name": universe, "variant": variant, "feature_level": level,
                         "key_grammar": "rmsk_name" if level == "subfamily" else "taxonomy_triple",
                         "emitted_feature_id": feature, "rmsk_record_id": blocks.rmsk_record_id,
                         "block_start_1": blocks.block_start_1, "block_end_1": blocks.block_end_1},
                        columns=MEMBER_COLUMNS)


def selections(parent_dir, universes):
    from manifest import read_json, require
    require(universes and len(universes) == len(set(universes))
            and set(universes) <= set(CHILD_UNIVERSES), "export universe outside CHILD_UNIVERSES")
    definitions = read_json(parent_dir / "universes.json")
    predicates = {item["name"]: item["predicate"] for item in definitions["universes"]}
    require(set(universes) <= set(predicates), "undeclared child export universe")
    return {name: predicates[name] for name in ("all_rmsk", *universes)}


def update_summary(totals, records, blocks, statuses, predicates, annotated):
    for universe, predicate in predicates.items():
        selected = evaluate_predicate(records, predicate)
        status = statuses.loc[selected]
        totals[universe].update(status.status.value_counts().to_dict())
        totals[universe].update(records=len(status), retained_records=int(status.n_blocks.gt(0).sum()),
                                blocks=int(status.n_blocks.sum()), retained_bp=int(status.retained_bp.sum()),
                                removed_bp=int(status.removed_bp.sum()),
                                records_on_unannotated_contigs=int((selected & ~records.chrom.isin(annotated)).sum()))


def summary_frame(totals):
    return pd.DataFrame([{column: universe if column == "universe_name" else counts[column]
                          for column in SUMMARY_COLUMNS} for universe, counts in totals.items()])


def write_block_exports(parent_dir, child_dir, universe, variant, blocks, roster, labels,
                        streams, registration, distinct, child_universes):
    """Write an explicit retained-block roster using parent taxonomy and child destinations."""
    from manifest import require
    require(universe in child_universes and universe in CHILD_UNIVERSES,
            "export universe outside CHILD_UNIVERSES")
    require(variant == VARIANT and tuple(roster) == CHILD_ROSTER, "unsupported child export roster")
    for column, pattern in (("rmsk_record_id", IDENTIFIER), ("chrom", COMPONENT)):
        for value in blocks[column].unique():
            validate(value, pattern, child_dir / "exports/ucsc" / universe / variant)
    require(blocks.strand.isin(["+", "-"]).all(), "child blocks require a valid strand")
    require(((blocks.block_start_1 >= blocks.start_1) & (blocks.block_end_1 <= blocks.end_1)
             & (blocks.block_start_1 <= blocks.block_end_1)).all(), "child block bounds differ")
    for filename, level in roster:
        members = registration_frame(blocks, universe, variant, level, labels)
        write_frame(members, registration, header=False)
        saf = pd.DataFrame({"GeneID": members.emitted_feature_id, "Chr": blocks.chrom,
                            "Start": blocks.block_start_1, "End": blocks.block_end_1, "Strand": blocks.strand})
        write_frame(saf, streams[(universe, filename)], header=False)
        distinct[(universe, level)].update(members.emitted_feature_id.unique())


def build_child(parent_dir, child_dir, gtf, universes=CHILD_UNIVERSES, variant=VARIANT, roster=CHILD_ROSTER, policy=None):
    """Stream the complete catalog into status, summaries, SAFs and block registration."""
    parent_dir, child_dir = Path(parent_dir), Path(child_dir)
    if policy is not None:
        validate_policy(policy)
    predicates = selections(parent_dir, universes)
    mask, coverage = annotation_mask(gtf, child_dir / "tables/contig_aliases.tsv")
    write_tsv(coverage, child_dir / "tables/gene_annotation_coverage.tsv")
    annotated = set(coverage.loc[coverage.annotated, "chrom_ucsc"])
    totals = {name: Counter() for name in predicates}
    taxonomy = pd.read_csv(parent_dir / "tables/taxonomy_canonical.tsv", sep="\t", dtype=str, keep_default_na=False)
    labels = taxonomy_labels(parent_dir, taxonomy[["rmsk_name"]], child_dir / "exports")
    distinct = {(universe, level): set() for universe in universes for _, level in roster}
    with ExitStack() as stack:
        registration = stack.enter_context(tsv_stream(child_dir / "tables/export_feature_members.tsv.gz"))
        registration.write("\t".join(MEMBER_COLUMNS) + "\n")
        status_stream = stack.enter_context(tsv_stream(child_dir / "tables/exon_subtraction_status.tsv"))
        status_stream.write("\t".join(STATUS_COLUMNS) + "\n")
        streams = {}
        for universe in universes:
            directory = child_dir / "exports/ucsc" / universe / variant
            directory.mkdir(parents=True, exist_ok=True)
            for filename, _ in roster:
                streams[(universe, filename)] = stack.enter_context(tsv_stream(directory / filename))
                streams[(universe, filename)].write("GeneID\tChr\tStart\tEnd\tStrand\n")
        for records in record_batches(parent_dir):
            blocks, statuses = subtract_batch(records, mask)
            write_frame(statuses, status_stream, header=False)
            update_summary(totals, records, blocks, statuses, predicates, annotated)
            for universe in universes:
                selected = blocks.loc[evaluate_predicate(blocks, predicates[universe])].reset_index(drop=True)
                write_block_exports(parent_dir, child_dir, universe, variant, selected, roster, labels,
                                    streams, registration, distinct, universes)
    write_tsv(summary_frame(totals), child_dir / "tables/exon_subtraction_summary.tsv")
    aliases = pd.read_csv(child_dir / "tables/contig_aliases.tsv", sep="\t", dtype=str, keep_default_na=False)
    from manifest import digest_file
    inventory = []
    for universe in universes:
        for filename, level in roster:
            relative = f"exports/ucsc/{universe}/{variant}/{filename}"
            source = child_dir / relative
            sort_export(source)
            row = {"export_path": relative, "namespace": "ucsc", "universe_name": universe,
                   "variant": variant, "feature_level": level, "format": "saf",
                   "rows": totals[universe]["blocks"], "distinct_features": len(distinct[(universe, level)]),
                   "sha256": digest_file(source)}
            inventory.append(row)
            for namespace in ("ensembl", "gencode"):
                target = relative.replace("/ucsc/", f"/{namespace}/")
                count, digest = rename_export(source, child_dir / target,
                    aliases.set_index("chrom_ucsc")[f"chrom_{namespace}"].to_dict())
                if count != row["rows"]:
                    raise ValueError(f"namespace rows differ: {target}")
                inventory.append({**row, "export_path": target, "namespace": namespace, "sha256": digest})
    write_inventory(child_dir, inventory)
    if policy and policy["context_capability"] == "transcript_geometry_v1":
        from transcript_context import write_context
        write_context(parent_dir, child_dir, gtf, policy)
    print(summary_frame(totals).to_csv(sep="\t", index=False), end="", flush=True)


def child_contracts(universes, roster=CHILD_ROSTER):
    return sorted([{"export_path": f"exports/{namespace}/{universe}/{VARIANT}/{filename}",
                    "namespace": namespace, "universe_name": universe, "variant": VARIANT, "format": "saf",
                    **{key: value for key, value in EXPORT_CONTRACTS[filename].items() if key != "consumer_keys"}}
                   for namespace in ("ucsc", "ensembl", "gencode") for universe in universes
                   for filename, _ in roster], key=lambda row: row["export_path"])


def verify_products(child_dir, parent_dir, identity, emit):
    """Join every registration and status to the pinned catalog and expected exon geometry."""
    from manifest import read_tsv, require, source_path
    mask, coverage = annotation_mask(child_dir / source_path(identity["build_sources"]["gene_gtf"]),
                                     child_dir / "tables/contig_aliases.tsv")
    observed = pd.read_csv(child_dir / "tables/gene_annotation_coverage.tsv", sep="\t")
    require(coverage.equals(observed), "gene_annotation_coverage differs from retained GTF")
    universes = identity["child_universes"]
    predicates = selections(parent_dir, universes)
    totals = {name: Counter() for name in predicates}
    annotated = set(coverage.loc[coverage.annotated, "chrom_ucsc"])
    taxonomy = pd.read_csv(parent_dir / "tables/taxonomy_canonical.tsv", sep="\t", dtype=str, keep_default_na=False)
    labels = taxonomy_labels(parent_dir, taxonomy[["rmsk_name"]], child_dir / "exports")
    ids = pd.Index(pq.read_table(parent_dir / "tables/rmsk_records.parquet",
                                 columns=["rmsk_record_id"]).column(0).to_pandas())
    size = len(ids)
    aliases = read_tsv(child_dir / "tables/contig_aliases.tsv")
    contigs = pd.Index([row["chrom_ucsc"] for row in aliases])
    namespace_chroms = {namespace: [row["chrom_" + namespace].encode() for row in aliases]
                       for namespace in ("ucsc", "ensembl", "gencode")}
    record_chroms = np.empty(size, dtype=np.int32)
    record_strands = np.empty(size, dtype="S1")
    expected = {key: np.zeros(size, dtype=np.int64) for key in ("n_blocks", "retained_bp", "removed_bp")}
    first_start, first_end = np.zeros(size, dtype=np.int64), np.zeros(size, dtype=np.int64)
    extra_blocks = set()
    selected = {universe: np.zeros(size, dtype=bool) for universe in universes}
    offset = 0
    for records in record_batches(parent_dir):
        blocks, statuses = subtract_batch(records, mask)
        require(ids[offset:offset + len(records)].equals(pd.Index(records.rmsk_record_id)),
                "parent catalog order differs")
        chrom_positions = contigs.get_indexer(records.chrom)
        require((chrom_positions >= 0).all(), "parent contigs differ from aliases")
        record_chroms[offset:offset + len(records)] = chrom_positions
        record_strands[offset:offset + len(records)] = records.strand.to_numpy(dtype="S1")
        for key in expected:
            expected[key][offset:offset + len(records)] = statuses[key]
        owners = pd.Index(records.rmsk_record_id).get_indexer(blocks.rmsk_record_id) + offset
        first = ~blocks.rmsk_record_id.duplicated().to_numpy()
        first_start[owners[first]] = blocks.block_start_1.to_numpy()[first]
        first_end[owners[first]] = blocks.block_end_1.to_numpy()[first]
        extra_blocks.update(zip(owners[~first], blocks.block_start_1.to_numpy()[~first],
                                blocks.block_end_1.to_numpy()[~first]))
        for universe in universes:
            selected[universe][offset:offset + len(records)] = evaluate_predicate(records, predicates[universe])
        update_summary(totals, records, blocks, statuses, predicates, annotated)
        offset += len(records)
    seen_status = np.zeros(size, dtype=bool)
    for chunk in pd.read_csv(child_dir / "tables/exon_subtraction_status.tsv", sep="\t",
                             keep_default_na=False, quoting=3, chunksize=100_000):
        require(list(chunk) == STATUS_COLUMNS, "exon_subtraction_status columns differ")
        positions = ids.get_indexer(chunk.rmsk_record_id)
        require((positions >= 0).all() and len(np.unique(positions)) == len(positions)
                and not seen_status[positions].any(), "exon_subtraction_status parent keys differ")
        seen_status[positions] = True
        for key in expected:
            require(np.array_equal(chunk[key], expected[key][positions]),
                    "exon_subtraction_status differs from parent conservation or mask")
        n, removed = expected["n_blocks"][positions], expected["removed_bp"][positions]
        status = np.where(n == 0, "fully_subtracted", np.where(removed == 0, "unchanged",
                          np.where(n > 1, "split", "trimmed")))
        require(np.array_equal(chunk.status, status), "exon_subtraction_status differs from parent conservation or mask")
    require(seen_status.all(), "exon_subtraction_status missing parent records")
    groups = {(universe, level) for universe in universes for _, level in CHILD_ROSTER}
    counts = {key: np.zeros(size, dtype=np.int32) for key in groups}
    seen_first = {key: np.zeros(size, dtype=bool) for key in groups}
    seen_extra = set()
    distinct = {key: set() for key in groups}
    registration_digests = {key: dict.fromkeys(namespace_chroms, 0) for key in groups}
    digest_modulus = 1 << 128
    for chunk in pd.read_csv(child_dir / "tables/export_feature_members.tsv.gz", sep="\t",
                             keep_default_na=False, quoting=3, chunksize=200_000):
        require(list(chunk) == MEMBER_COLUMNS and chunk.variant.eq(VARIANT).all(),
                "registration columns or variant differ")
        for key, group in chunk.groupby(["universe_name", "feature_level"], sort=False):
            require(key in groups, "registration universe or feature level differs")
            universe, level = key
            positions = ids.get_indexer(group.rmsk_record_id)
            require((positions >= 0).all() and selected[universe][positions].all(),
                    "registration parent records or universe differs")
            names = group.rmsk_record_id.str.split("|", n=1).str[0]
            features = names if level == "subfamily" else names.map(lambda name: labels[name][3])
            grammar = "rmsk_name" if level == "subfamily" else "taxonomy_triple"
            require(np.array_equal(features, group.emitted_feature_id) and group.key_grammar.eq(grammar).all(),
                    "registration feature identities differ")
            left, right = group.block_start_1.to_numpy(), group.block_end_1.to_numpy()
            first = (left == first_start[positions]) & (right == first_end[positions]) & (left >= 1)
            first_positions = positions[first]
            require(len(np.unique(first_positions)) == len(first_positions) and not seen_first[key][first_positions].any(),
                    "duplicate registration block")
            seen_first[key][first_positions] = True
            for position, start, end in zip(positions[~first], left[~first], right[~first]):
                block = (position, start, end)
                require(block in extra_blocks, "registration differs from parent records, blocks or feature identities")
                token = (*key, *block)
                require(token not in seen_extra, "duplicate registration block")
                seen_extra.add(token)
            np.add.at(counts[key], positions, 1)
            distinct[key].update(group.emitted_feature_id.unique())
            digests = registration_digests[key]
            for feature, chrom, start, end, strand in zip(group.emitted_feature_id, record_chroms[positions],
                                                         left, right, record_strands[positions]):
                prefix = feature.encode() + b"\t"
                suffix = f"\t{start}\t{end}\t".encode() + strand
                for namespace, chrom_names in namespace_chroms.items():
                    payload = prefix + chrom_names[chrom] + suffix
                    digests[namespace] += int.from_bytes(hashlib.blake2b(payload, digest_size=16).digest(), "big")
            for namespace in digests:
                digests[namespace] %= digest_modulus
    for key, observed_counts in counts.items():
        require(np.array_equal(observed_counts, np.where(selected[key[0]], expected["n_blocks"], 0)),
                "registration block counts differ from parent subtraction")
    observed = pd.read_csv(child_dir / "tables/exon_subtraction_summary.tsv", sep="\t")
    require(summary_frame(totals).equals(observed), "exon_subtraction_summary differs from parent records")
    for row in read_tsv(child_dir / "tables/exports.tsv"):
        universe, level = row["universe_name"], row["feature_level"]
        content_error = "SAF rows differ from registration: " + row["export_path"]
        order_error = "SAF order differs: " + row["export_path"]
        registered_count = int(counts[(universe, level)].sum())
        require(int(row["rows"]) == registered_count, content_error)
        require(int(row["distinct_features"]) == len(distinct[(universe, level)]), "SAF distinct features differ")
        with (child_dir / row["export_path"]).open("rb") as stream:
            require(stream.readline() == b"GeneID\tChr\tStart\tEnd\tStrand\n", "SAF header differs")
            count, digest, previous, ordered = 0, 0, None, True
            for line in stream:
                fields = line.rstrip(b"\n").split(b"\t")
                require(len(fields) == 5, content_error)
                feature, chrom, start, end, strand = fields
                order = (chrom, int(start), int(end), strand, feature)
                ordered = ordered and (previous is None or previous <= order)
                previous = order
                digest += int.from_bytes(hashlib.blake2b(b"\t".join(fields), digest_size=16).digest(), "big")
                count += 1
        require(count == registered_count and digest % digest_modulus
                == registration_digests[(universe, level)][row["namespace"]], content_error)
        require(ordered, order_error)
    if identity["policy_bundle"]["context_capability"] == "transcript_geometry_v1":
        from transcript_context import verify_context
        verify_context(child_dir, parent_dir,
                       child_dir / source_path(identity["build_sources"]["gene_gtf"]), identity["policy_bundle"])
        emit("ok transcript context: complete relation and record geometry")
    emit("ok child registration: every parent key, feature and ordered retained block")
    emit("ok child status: complete catalog conservation and summary")
    emit(f"ok annotation coverage: {int(coverage.annotated.sum())} annotated contigs of {len(coverage)}")
    emit("ok child SAF rows and distinct features: registration per universe and grouping")
    emit("ok child SAF rows: content and order equal the registration in every namespace")


def main():
    from manifest import config_values, read_json, require, source_path, validate_parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("parent", "sources", "copy", "build"))
    parser.add_argument("--build-dir", type=Path)
    parser.add_argument("--parent-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    try:
        config = config_values(args.config)
        if args.command == "parent":
            validate_parent(args.parent_dir, config["PARENT_FAMILY"], config["GENOME"])
        elif args.command == "sources":
            write_sources(args.build_dir, args.parent_dir, config)
        elif args.command == "copy":
            copy_parent_inputs(args.build_dir, args.parent_dir)
        else:
            validate_policy(policy_bundle(config))
            sources = read_json(args.build_dir / "source/SOURCES.json")
            require(sources["policy_bundle"] == policy_bundle(config), "configured gene policy differs")
            build_child(args.parent_dir, args.build_dir,
                        args.build_dir / source_path(sources["sources"]["gene_gtf"]),
                        config["CHILD_UNIVERSES"].split(), policy=policy_bundle(config))
    except (ValueError, KeyError, TypeError, OSError, StopIteration) as error:
        parser.exit(1, f"gene_child: {error}\n")


if __name__ == "__main__":
    main()
