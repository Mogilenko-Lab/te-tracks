"""Export full UCSC intervals and register their feature identities to source records."""

import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import re
import sys

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
from records_io import RECORD_KEY, tsv_stream, write_tsv


COMPONENT = re.compile(r"[A-Za-z0-9_.+?()-]+")
IDENTIFIER = re.compile(r"[A-Za-z0-9_.+?()|:/-]+")
EXPORTS = (
    ("record.bed", "record"), ("subfamily.bed", "subfamily"),
    ("family.bed", "family"), ("record.gtf", "record"),
    ("subfamily.gtf", "subfamily"), ("subfamily.saf", "subfamily"),
    ("taxonomy_triple.saf", "taxonomy_triple"),
)
MEMBER_COLUMNS = [
    "universe_name", "variant", "feature_level", "key_grammar", "emitted_feature_id",
    "rmsk_record_id", "block_start_1", "block_end_1",
]


def validate(value, pattern, path):
    """Name the export and offending value when its identifier grammar fails."""
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise ValueError(f"invalid export identifier {value!r} in {path}")
    return value


def load_members(build_dir):
    """Select the declared default universe through its recorded membership."""
    definitions = json.loads((build_dir / "universes.json").read_text(encoding="utf-8"))
    universe = definitions["default_universe"]
    if universe != "interspersed" or universe not in {
        entry["name"] for entry in definitions["universes"]
    }:
        raise ValueError("UCSC full exports require the declared interspersed default universe")
    chunks = []
    for chunk in pd.read_csv(
        build_dir / "tables/universe_members.tsv.gz", sep="\t", dtype=str,
        keep_default_na=False, quoting=3, usecols=["universe_name", "rmsk_record_id"],
        chunksize=500_000,
    ):
        chunks.append(chunk.loc[chunk["universe_name"].eq(universe), "rmsk_record_id"])
    members = pd.concat(chunks, ignore_index=True)
    if members.empty or members.duplicated().any():
        raise ValueError("interspersed membership requires nonempty, unique record IDs")
    columns = ["rmsk_record_id", *RECORD_KEY, "rmsk_family", "rmsk_class",
               "rmsk_instance_id", "sw_score"]
    records = pq.read_table(build_dir / "tables/rmsk_records.parquet",
                            columns=columns).to_pandas()
    selected = records.loc[records["rmsk_record_id"].isin(members)]
    missing = members.loc[~members.isin(selected["rmsk_record_id"])]
    if not missing.empty:
        raise ValueError(f"universe member absent from records: {missing.iloc[0]!r}")
    if selected["rmsk_record_id"].duplicated().any() or selected.duplicated(RECORD_KEY).any():
        raise ValueError("export membership requires unique record identities")
    return universe, selected.sort_values(RECORD_KEY, ignore_index=True)


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


def build_exports(build_dir, genome):
    """Write seven sorted exports, namespace-invariant membership and their inventory."""
    build_dir = Path(build_dir)
    universe, records = load_members(build_dir)
    export_dir = build_dir / "exports/ucsc" / universe / "full"
    validate(genome, COMPONENT, export_dir / "record.gtf")
    labels = taxonomy_labels(build_dir, records, export_dir)
    for column, filename, pattern in (
        ("chrom", "record.bed", COMPONENT),
        ("rmsk_record_id", "record.bed", IDENTIFIER),
        ("rmsk_family", "record.gtf", COMPONENT),
        ("rmsk_class", "record.gtf", COMPONENT),
        ("rmsk_instance_id", "record.gtf", COMPONENT),
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
            for filename, _ in EXPORTS
        }
        registration = stack.enter_context(tsv_stream(
            build_dir / "tables/export_feature_members.tsv.gz"))
        registration.write("\t".join(MEMBER_COLUMNS) + "\n")
        for filename in ("subfamily.saf", "taxonomy_triple.saf"):
            streams[filename].write("GeneID\tChr\tStart\tEnd\tStrand\n")
        for record in records.itertuples(index=False):
            name, chrom = record.rmsk_name, record.chrom
            start, end, strand = record.start_1, record.end_1, record.strand
            key = record.rmsk_record_id
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
            streams["subfamily.gtf"].write(
                gtf_prefix + f'gene_id "{name}"; transcript_id "{name}"; locus "{name}"; '
                + taxonomy + "\n")
            saf_suffix = f"\t{chrom}\t{start}\t{end}\t{strand}\n"
            streams["subfamily.saf"].write(name + saf_suffix)
            streams["taxonomy_triple.saf"].write(triple + saf_suffix)
            registration.write("".join(
                f"{universe}\tfull\t{level}\t{grammar}\t{feature}\t{key}\t{start}\t{end}\n"
                for level, grammar, feature in (
                    ("record", "rmsk_record_id", key),
                    ("record", "record_alias", alias),
                    ("record", "four_tuple", record_tuple),
                    ("subfamily", "rmsk_name", name),
                    ("subfamily", "four_tuple", subfamily_tuple),
                    ("family", "family_bucket", family_id),
                    ("taxonomy_triple", "taxonomy_triple", triple),
                    ("instance", "instance_alias", instance),
                )
            ))
    distinct = {"record": len(records), "subfamily": len(labels),
                "family": len({value[2] for value in labels.values()}),
                "taxonomy_triple": len({value[3] for value in labels.values()}),
                "instance": records["rmsk_instance_id"].nunique()}
    inventory = []
    for filename, level in EXPORTS:
        path = export_dir / filename
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        inventory.append({
            "export_path": path.relative_to(build_dir).as_posix(), "namespace": "ucsc",
            "universe_name": universe, "variant": "full", "feature_level": level,
            "format": path.suffix[1:], "rows": len(records),
            "distinct_features": distinct[level], "sha256": digest,
        })
    write_tsv(pd.DataFrame(inventory).sort_values("export_path"), build_dir / "tables/exports.tsv")
    print(f"universe={universe} records={len(records)} subfamilies={distinct['subfamily']} "
          f"families={distinct['family']} taxonomy_triples={distinct['taxonomy_triple']} "
          f"instances={distinct['instance']} exports={len(EXPORTS)} "
          f"registrations={len(records) * 8} (eight rows per record)", flush=True)


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
