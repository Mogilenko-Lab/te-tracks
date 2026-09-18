"""Export full UCSC intervals and register their feature identities to source records."""

import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
from records_io import RECORD_KEY, tsv_stream, write_tsv


COMPONENT = re.compile(r"[A-Za-z0-9_.+?()-]+")
IDENTIFIER = re.compile(r"[A-Za-z0-9_.+?()|:/-]+")
_RECORD_ALIAS = "R|{assembly.ucsc}|{rmsk_records.rmsk_name}|{rmsk_records.chrom}|{rmsk_records.start_1}|{rmsk_records.end_1}|{rmsk_records.strand}"
_INSTANCE_ALIAS = "I|{assembly.ucsc}|{rmsk_records.rmsk_instance_id}"
_GTF_SOURCES = {
    "gene_id": "rmsk_records.rmsk_name",
    "family_id": "taxonomy_canonical.canonical_family; unresolved: unresolved_family_{rmsk_name}",
    "class_id": "taxonomy_canonical.canonical_class; unresolved: unresolved_class_{rmsk_name}",
    "rmsk_family": "rmsk_records.rmsk_family",
    "rmsk_class": "rmsk_records.rmsk_class",
}
FEATURE_LEVELS = ("record", "subfamily", "family", "taxonomy_triple", "instance")
EXPORT_CONTRACTS = {
    "record.bed": {
        "feature_level": "record", "feature_identity": "name",
        "attribute_sources": {"name": "rmsk_records.rmsk_record_id"},
        "consumer_keys": {"IRescue": "name", "bedtools": "name"},
        "selectable_levels": {"name": "record"},
        "coordinate_convention": "0-based half-open",
    },
    "subfamily.bed": {
        "feature_level": "subfamily", "feature_identity": "name",
        "attribute_sources": {"name": "rmsk_records.rmsk_name"},
        "consumer_keys": {"IRescue": "name"},
        "selectable_levels": {"name": "subfamily"},
        "coordinate_convention": "0-based half-open",
    },
    "family.bed": {
        "feature_level": "family", "feature_identity": "name",
        "attribute_sources": {"name": "{class_id}/{family_id}",
                              "class_id": _GTF_SOURCES["class_id"],
                              "family_id": _GTF_SOURCES["family_id"]},
        "consumer_keys": {"bedtools": "name"},
        "selectable_levels": {"name": "family"},
        "coordinate_convention": "0-based half-open",
    },
    "record.gtf": {
        "feature_level": "record", "feature_identity": "locus",
        "attribute_sources": {
            **_GTF_SOURCES, "transcript_id": _RECORD_ALIAS, "locus": _RECORD_ALIAS,
            "instance_id": _INSTANCE_ALIAS, "rmsk_record_id": "rmsk_records.rmsk_record_id",
        },
        "consumer_keys": {
            "Stellarscope": {"default": "locus", "--attribute instance_id": "instance_id"},
            "TEsingle": "transcript_id:gene_id:family_id:class_id",
            "TElocal": "transcript_id:gene_id:family_id:class_id",
            "TEtranscripts": "gene_id:family_id:class_id",
        },
        "selectable_levels": {"locus": "record", "instance_id": "instance",
                              "transcript_id:gene_id:family_id:class_id": "record",
                              "gene_id:family_id:class_id": "taxonomy_triple"},
        "coordinate_convention": "1-based inclusive",
    },
    "record_starsolo.gtf": {
        "feature_level": "record", "feature_identity": "gene_id",
        "attribute_sources": {
            **_GTF_SOURCES, "gene_id": _RECORD_ALIAS, "transcript_id": _RECORD_ALIAS,
            "gene_name": "rmsk_records.rmsk_name", "gene_type": "transposable_element",
            "locus": _RECORD_ALIAS, "rmsk_name": "rmsk_records.rmsk_name",
            "instance_id": _INSTANCE_ALIAS, "rmsk_record_id": "rmsk_records.rmsk_record_id",
        },
        "consumer_keys": {"STARsolo": "gene_id", "cellranger": "gene_id"},
        "selectable_levels": {"gene_id": "record"},
        "coordinate_convention": "1-based inclusive",
    },
    "subfamily.gtf": {
        "feature_level": "subfamily", "feature_identity": "locus",
        "attribute_sources": {**_GTF_SOURCES, "transcript_id": "rmsk_records.rmsk_name",
                              "locus": "rmsk_records.rmsk_name"},
        "consumer_keys": {
            "Stellarscope": "locus",
            "TEsingle": "transcript_id:gene_id:family_id:class_id",
            "TElocal": "transcript_id:gene_id:family_id:class_id",
            "TEtranscripts": "gene_id:family_id:class_id",
        },
        "selectable_levels": {"locus": "subfamily",
                              "transcript_id:gene_id:family_id:class_id": "subfamily",
                              "gene_id:family_id:class_id": "taxonomy_triple"},
        "coordinate_convention": "1-based inclusive",
    },
    "subfamily.saf": {
        "feature_level": "subfamily", "feature_identity": "GeneID",
        "attribute_sources": {"GeneID": "rmsk_records.rmsk_name"},
        "consumer_keys": {"featureCounts": "GeneID"},
        "selectable_levels": {"GeneID": "subfamily"},
        "coordinate_convention": "1-based inclusive",
    },
    "taxonomy_triple.saf": {
        "feature_level": "taxonomy_triple", "feature_identity": "GeneID",
        "attribute_sources": {"GeneID": "{rmsk_records.rmsk_name}:{family_id}:{class_id}",
                              "class_id": _GTF_SOURCES["class_id"],
                              "family_id": _GTF_SOURCES["family_id"]},
        "consumer_keys": {"featureCounts": "GeneID", "SAF column reader": "GeneID"},
        "selectable_levels": {"GeneID": "taxonomy_triple"},
        "coordinate_convention": "1-based inclusive",
    },
}
EXPORTS = tuple((name, contract["feature_level"]) for name, contract in EXPORT_CONTRACTS.items())
EXPORT_JOBS = (("interspersed", EXPORTS), ("all_rmsk", (("record.bed", "record"),)))
MEMBER_COLUMNS = [
    "universe_name", "variant", "feature_level", "key_grammar", "emitted_feature_id",
    "rmsk_record_id", "block_start_1", "block_end_1",
]


def validate(value, pattern, path):
    """Name the export and offending value when its identifier grammar fails."""
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise ValueError(f"invalid export identifier {value!r} in {path}")
    return value


def load_members(build_dir, universe):
    """Select a declared universe through recorded or implicit catalog membership."""
    definitions = json.loads((build_dir / "universes.json").read_text(encoding="utf-8"))
    if universe not in {entry["name"] for entry in definitions["universes"]}:
        raise ValueError(f"undeclared export universe: {universe!r}")
    columns = ["rmsk_record_id", *RECORD_KEY, "rmsk_family", "rmsk_class",
               "rmsk_instance_id", "sw_score"]
    records = pq.read_table(build_dir / "tables/rmsk_records.parquet",
                            columns=columns).to_pandas()
    selected = records
    if universe != "all_rmsk":
        chunks = []
        for chunk in pd.read_csv(
            build_dir / "tables/universe_members.tsv.gz", sep="\t", dtype=str,
            keep_default_na=False, quoting=3, usecols=["universe_name", "rmsk_record_id"],
            chunksize=500_000,
        ):
            chunks.append(chunk.loc[chunk["universe_name"].eq(universe), "rmsk_record_id"])
        members = pd.concat(chunks, ignore_index=True)
        if members.empty or members.duplicated().any():
            raise ValueError(f"{universe} membership requires nonempty, unique record IDs")
        selected = records.loc[records["rmsk_record_id"].isin(members)]
        missing = members.loc[~members.isin(selected["rmsk_record_id"])]
        if not missing.empty:
            raise ValueError(f"universe member absent from records: {missing.iloc[0]!r}")
    if selected["rmsk_record_id"].duplicated().any() or selected.duplicated(RECORD_KEY).any():
        raise ValueError("export membership requires unique record identities")
    return selected.sort_values(RECORD_KEY, ignore_index=True)


def taxonomy_labels(build_dir, records, export_dir):
    """Resolve each exported name to separator-free canonical rank tokens."""
    taxonomy = pd.read_csv(build_dir / "tables/taxonomy_canonical.tsv", sep="\t",
                           dtype=str, keep_default_na=False, quoting=3)
    if taxonomy["rmsk_name"].duplicated().any():
        raise ValueError("taxonomy_canonical requires one row per name")
    taxonomy = taxonomy.set_index("rmsk_name")
    labels = {}
    for name in records["rmsk_name"].unique():
        validate(name, COMPONENT, export_dir / "subfamily.bed")
        if name not in taxonomy.index:
            raise ValueError(f"taxonomy_canonical missing exported name: {name!r}")
        row = taxonomy.loc[name]
        ranks = []
        for rank in ("class", "family"):
            label = row[f"canonical_{rank}"]
            unresolved = row[f"{rank}_status"] == "unresolved"
            if unresolved != (label == ""):
                raise ValueError(f"inconsistent canonical {rank} for {name!r}")
            if not unresolved and label.startswith("unresolved_"):
                raise ValueError(f"reserved canonical {rank} token {label!r} for {name!r}")
            token = f"unresolved_{rank}_{name}" if unresolved else label
            ranks.append(validate(token, COMPONENT, export_dir / "family.bed"))
        cls, family = ranks
        family_id = validate(f"{cls}/{family}", IDENTIFIER, export_dir / "family.bed")
        triple = validate(f"{name}:{family}:{cls}", IDENTIFIER,
                          export_dir / "taxonomy_triple.saf")
        labels[name] = (cls, family, family_id, triple)
    return labels


def write_inventory(build_dir, rows):
    """Replace the inventory with unique export paths in byte order."""
    inventory = pd.DataFrame(rows)
    if inventory.empty or inventory["export_path"].duplicated().any():
        raise ValueError("export inventory requires nonempty, unique paths")
    write_tsv(inventory.sort_values("export_path"), Path(build_dir) / "tables/exports.tsv")


def write_registration(stream, universe, key, start, end, features):
    """Register each emitted spelling against its source record and full block."""
    stream.write("".join(
        f"{universe}\tfull\t{level}\t{grammar}\t{feature}\t{key}\t{start}\t{end}\n"
        for level, grammar, feature in features
    ))


def sort_export(path):
    """Sort each file by contig, numeric bounds, strand and its emitted name column."""
    keys = {".bed": ["-k1,1", "-k2,2n", "-k3,3n", "-k6,6", "-k4,4"],
            ".gtf": ["-k1,1", "-k4,4n", "-k5,5n", "-k7,7", "-k9,9"],
            ".saf": ["-k2,2", "-k3,3n", "-k4,4n", "-k5,5", "-k1,1"]}
    with TemporaryDirectory(prefix=".exports-", dir=path.parent) as temporary:
        pending = Path(temporary) / path.name
        with path.open("rb", buffering=0) as incoming, pending.open("wb") as outgoing:
            if path.suffix == ".saf":
                outgoing.write(incoming.readline())
                outgoing.flush()
            result = subprocess.run(
                ["sort", "--stable", "--buffer-size=512M", "--parallel=2", "-T", temporary,
                 "-t", "\t", *keys[path.suffix]], stdin=incoming, stdout=outgoing,
                env={**os.environ, "LC_ALL": "C"},
            )
            if result.returncode:
                raise ValueError(f"export sorting failed for {path}")
        pending.replace(path)


def export_universe(build_dir, genome, universe, export_set, registration):
    """Emit an explicit export set and return its measured inventory rows."""
    build_dir = Path(build_dir)
    record_only = export_set == (("record.bed", "record"),)
    if export_set != EXPORTS and not record_only:
        raise ValueError(f"unsupported export set: {export_set!r}")
    records = load_members(build_dir, universe)
    export_dir = build_dir / "exports/ucsc" / universe / "full"
    validate(genome, COMPONENT, export_dir / "record.gtf")
    labels = {} if record_only else taxonomy_labels(build_dir, records, export_dir)
    for column, filename, pattern in (
        ("chrom", "record.bed", COMPONENT),
        ("rmsk_record_id", "record.bed", IDENTIFIER),
        *([] if record_only else [
            ("rmsk_family", "record.gtf", COMPONENT),
            ("rmsk_class", "record.gtf", COMPONENT),
            ("rmsk_instance_id", "record.gtf", COMPONENT),
        ]),
    ):
        for value in records[column].unique():
            validate(value, pattern, export_dir / filename)
    if not records["strand"].isin(["+", "-"]).all():
        raise ValueError(f"invalid strand in {export_dir / 'record.gtf'}")
    export_dir.mkdir(parents=True, exist_ok=True)
    with ExitStack() as stack:
        streams = {
            filename: stack.enter_context(open(export_dir / filename, "w", encoding="utf-8",
                                                newline="", buffering=1024 * 1024))
            for filename, _ in export_set
        }
        for filename in (name for name in streams if name.endswith(".saf")):
            streams[filename].write("GeneID\tChr\tStart\tEnd\tStrand\n")
        for record in records.itertuples(index=False):
            name, chrom = record.rmsk_name, record.chrom
            start, end, strand = record.start_1, record.end_1, record.strand
            key = record.rmsk_record_id
            if record_only:
                streams["record.bed"].write(
                    f"{chrom}\t{start - 1}\t{end}\t{key}\t{min(record.sw_score, 1000)}\t{strand}\n")
                write_registration(registration, universe, key, start, end,
                                   [("record", "rmsk_record_id", key)])
                continue
            cls, family, family_id, triple = labels[name]
            alias = validate(f"R|{genome}|{name}|{chrom}|{start}|{end}|{strand}",
                             IDENTIFIER, export_dir / "record.gtf")
            instance = validate(f"I|{genome}|{record.rmsk_instance_id}", IDENTIFIER,
                                export_dir / "record.gtf")
            record_tuple = validate(f"{alias}:{name}:{family}:{cls}", IDENTIFIER,
                                    export_dir / "record.gtf")
            subfamily_tuple = validate(f"{name}:{name}:{family}:{cls}", IDENTIFIER,
                                       export_dir / "subfamily.gtf")
            bed_prefix = f"{chrom}\t{start - 1}\t{end}\t"
            bed_suffix = f"\t{min(record.sw_score, 1000)}\t{strand}\n"
            for filename, feature in (("record.bed", key), ("subfamily.bed", name),
                                      ("family.bed", family_id)):
                streams[filename].write(bed_prefix + feature + bed_suffix)
            gtf_prefix = f"{chrom}\tte-tracks\texon\t{start}\t{end}\t{record.sw_score}\t{strand}\t.\t"
            taxonomy = (f'family_id "{family}"; class_id "{cls}"; '
                        f'rmsk_family "{record.rmsk_family}"; rmsk_class "{record.rmsk_class}";')
            streams["record.gtf"].write(
                gtf_prefix + f'gene_id "{name}"; transcript_id "{alias}"; locus "{alias}"; '
                + taxonomy + f' instance_id "{instance}"; rmsk_record_id "{key}";\n')
            streams["record_starsolo.gtf"].write(
                gtf_prefix + f'gene_id "{alias}"; transcript_id "{alias}"; '
                + f'gene_name "{name}"; gene_type "transposable_element"; '
                + f'locus "{alias}"; rmsk_name "{name}"; ' + taxonomy
                + f' instance_id "{instance}"; rmsk_record_id "{key}";\n')
            streams["subfamily.gtf"].write(
                gtf_prefix + f'gene_id "{name}"; transcript_id "{name}"; locus "{name}"; '
                + taxonomy + "\n")
            saf_suffix = f"\t{chrom}\t{start}\t{end}\t{strand}\n"
            streams["subfamily.saf"].write(name + saf_suffix)
            streams["taxonomy_triple.saf"].write(triple + saf_suffix)
            write_registration(registration, universe, key, start, end, (
                ("record", "rmsk_record_id", key),
                ("record", "record_alias", alias),
                ("record", "four_tuple", record_tuple),
                ("subfamily", "rmsk_name", name),
                ("subfamily", "four_tuple", subfamily_tuple),
                ("family", "family_bucket", family_id),
                ("taxonomy_triple", "taxonomy_triple", triple),
                ("instance", "instance_alias", instance),
            ))
    distinct = {"record": len(records), "subfamily": len(labels),
                "family": len({value[2] for value in labels.values()}),
                "taxonomy_triple": len({value[3] for value in labels.values()}),
                "instance": records["rmsk_instance_id"].nunique()}
    inventory = []
    for filename, level in export_set:
        path = export_dir / filename
        sort_export(path)
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        inventory.append({
            "export_path": path.relative_to(build_dir).as_posix(), "namespace": "ucsc",
            "universe_name": universe, "variant": "full", "feature_level": level,
            "format": path.suffix[1:], "rows": len(records),
            "distinct_features": distinct[level], "sha256": digest,
        })
    ranks = ("" if record_only else f"subfamilies={distinct['subfamily']} "
             f"families={distinct['family']} taxonomy_triples={distinct['taxonomy_triple']} "
             f"instances={distinct['instance']} ")
    print(f"universe={universe} records={len(records)} {ranks}exports={len(export_set)} "
          f"registrations={len(records) * (1 if record_only else 8)}", flush=True)
    return inventory


def build_exports(build_dir, genome, jobs=EXPORT_JOBS):
    """Build ordered universe jobs with one registration stream and complete inventory."""
    build_dir = Path(build_dir)
    definitions = json.loads((build_dir / "universes.json").read_text(encoding="utf-8"))
    if definitions["default_universe"] != "interspersed":
        raise ValueError("full exports require the interspersed default universe")
    with tsv_stream(build_dir / "tables/export_feature_members.tsv.gz") as registration:
        registration.write("\t".join(MEMBER_COLUMNS) + "\n")
        rows = []
        for universe, export_set in jobs:
            rows.extend(export_universe(build_dir, genome, universe, export_set, registration))
    write_inventory(build_dir, rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--genome", required=True)
    args = parser.parse_args()
    try:
        build_exports(args.build_dir, args.genome)
    except (ValueError, KeyError, OSError, pa.ArrowException) as error:
        parser.exit(1, f"build_exports: {error}\n")


if __name__ == "__main__":
    main()
