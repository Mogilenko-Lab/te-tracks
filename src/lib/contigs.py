"""Publish source contig aliases, measured coverage and namespace exports."""

import argparse
from collections import Counter
import csv
import hashlib
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
from build_exports import EXPORT_JOBS, write_inventory
from records_io import write_tsv


NAMES = ["chrom_ucsc", "chrom_ensembl", "chrom_gencode", "chrom_genbank", "chrom_refseq"]


def build_aliases(build_dir, genome):
    """Require complete, injective aliases and publish measured per-contig coverage."""
    source = build_dir / "source"
    sizes = {}
    with (source / f"{genome}.chrom.sizes").open() as stream:
        for line in stream:
            chrom, length = line.split()
            if chrom in sizes or int(length) <= 0:
                raise ValueError(f"invalid source contig size: {line.rstrip()!r}")
            sizes[chrom] = int(length)
    aliases = []
    with (source / f"{genome}.chromAlias.txt").open() as stream:
        columns = stream.readline().lstrip("# ").split()
        if columns != ["ucsc", "assembly", "ensembl", "genbank", "refseq"]:
            raise ValueError(f"unexpected chromAlias columns: {columns!r}")
        for line in stream:
            fields = line.split()
            if len(fields) != len(columns):
                raise ValueError(f"invalid chromAlias row: {line.rstrip()!r}")
            row = dict(zip(columns, fields))
            chrom = row["ucsc"]
            aliases.append([chrom, row["ensembl"],
                            row["genbank"] if "_" in chrom else chrom,
                            row["genbank"], row["refseq"], sizes[chrom]])
    aliases = pd.DataFrame(aliases, columns=[*NAMES, "length_bp"]).sort_values("chrom_ucsc")
    for column in NAMES:
        if aliases[column].duplicated().any() or aliases[column].isin(["", "na", "NA", "."]).any():
            raise ValueError(f"aliases require complete, injective names: {column}")
    if set(aliases["chrom_ucsc"]) != set(sizes):
        raise ValueError("chromAlias and chrom.sizes contig sets differ")
    records = pq.read_table(build_dir / "tables/rmsk_records.parquet", columns=[
        "rmsk_record_id", "chrom", "end_1", "query_left_bp",
    ]).to_pandas()
    if not set(records["chrom"]) <= set(sizes):
        raise ValueError("catalog contig absent from aliases")
    chrom_by_id = records.set_index("rmsk_record_id")["chrom"]
    interspersed = Counter()
    for chunk in pd.read_csv(
        build_dir / "tables/universe_members.tsv.gz", sep="\t", dtype=str, quoting=3,
        keep_default_na=False, usecols=["universe_name", "rmsk_record_id"], chunksize=500_000,
    ):
        selected = chunk.loc[chunk["universe_name"].eq("interspersed"), "rmsk_record_id"]
        chroms = selected.map(chrom_by_id)
        if chroms.isna().any():
            raise ValueError("interspersed member absent from catalog")
        interspersed.update(chroms.value_counts().to_dict())
    length_agrees = (records["end_1"] + records["query_left_bp"]).eq(records["chrom"].map(sizes))
    agrees = length_agrees.groupby(records["chrom"]).all()
    coverage = aliases[["chrom_ucsc", "length_bp"]].copy()
    coverage["records_all"] = coverage["chrom_ucsc"].map(records["chrom"].value_counts()).fillna(0).astype("int64")
    coverage["records_interspersed"] = coverage["chrom_ucsc"].map(interspersed).fillna(0).astype("int64")
    coverage["has_ensembl"] = aliases["chrom_ensembl"].ne("")
    coverage["has_gencode"] = aliases["chrom_gencode"].ne("")
    coverage["length_agrees"] = coverage["chrom_ucsc"].map(lambda chrom: bool(agrees.get(chrom, True)))
    if not coverage["length_agrees"].all():
        raise ValueError("catalog query lengths disagree with chrom.sizes")
    write_tsv(aliases, build_dir / "tables/contig_aliases.tsv")
    write_tsv(coverage, build_dir / "tables/contig_coverage.tsv")
    return aliases


def rename_export(source, target, aliases):
    """Preserve each row's payload and sort by its renamed contig and interval."""
    fields = {".bed": (0, ["-k1,1", "-k2,2n", "-k3,3n", "-k6,6", "-k4,4"]),
              ".gtf": (0, ["-k1,1", "-k4,4n", "-k5,5n", "-k7,7", "-k9,9"]),
              ".saf": (1, ["-k2,2", "-k3,3n", "-k4,4n", "-k5,5", "-k1,1"])}
    column, keys = fields[source.suffix]
    mapping = {key.encode(): value.encode() for key, value in aliases.items()}
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with TemporaryDirectory(prefix=".contigs-", dir=target.parent) as temporary:
        pending = Path(temporary) / target.name
        with source.open("rb") as incoming, pending.open("wb") as outgoing:
            if source.suffix == ".saf":
                header = incoming.readline()
                if header != b"GeneID\tChr\tStart\tEnd\tStrand\n":
                    raise ValueError(f"unexpected SAF header in {source}")
                outgoing.write(header)
                outgoing.flush()
            with subprocess.Popen(
                ["sort", "--stable", "--buffer-size=512M", "--parallel=2", "-T", temporary,
                 "-t", "\t", *keys], stdin=subprocess.PIPE, stdout=outgoing,
                env={**os.environ, "LC_ALL": "C"},
            ) as sorter:
                try:
                    for line in incoming:
                        parts = line.split(b"\t", column + 1)
                        parts[column] = mapping[parts[column]]
                        sorter.stdin.write(b"\t".join(parts))
                        rows += 1
                finally:
                    sorter.stdin.close()
                if sorter.wait():
                    raise ValueError(f"contig sorting failed for {target}")
        pending.replace(target)
    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return rows, digest


def build_namespaces(build_dir, genome):
    """Add renamed files to the inventory while preserving the shared registration rows."""
    aliases = build_aliases(build_dir, genome)
    with (build_dir / "tables/exports.tsv").open() as stream:
        inventory = list(csv.DictReader(stream, delimiter="\t"))
    ucsc = [row for row in inventory if row["namespace"] == "ucsc"]
    expected = {f"exports/ucsc/{universe}/full/{name}"
                for universe, export_set in EXPORT_JOBS for name, _ in export_set}
    if {row["export_path"] for row in ucsc} != expected or len(ucsc) != len(expected):
        raise ValueError("namespace exports require the eight UCSC inventory entries")
    combined = {row["export_path"]: row for row in inventory}
    for namespace in ("ensembl", "gencode"):
        mapping = aliases.set_index("chrom_ucsc")[f"chrom_{namespace}"].to_dict()
        for row in ucsc:
            source = build_dir / row["export_path"]
            relative = Path("exports") / namespace / Path(row["export_path"]).relative_to("exports/ucsc")
            count, digest = rename_export(source, build_dir / relative, mapping)
            if count != int(row["rows"]):
                raise ValueError(f"inventory row count differs from source: {source}")
            combined[relative.as_posix()] = {**row, "export_path": relative.as_posix(),
                                           "namespace": namespace, "rows": count, "sha256": digest}
        print(f"namespace={namespace} exports={len(ucsc)}", flush=True)
    write_inventory(build_dir, list(combined.values()))
    print(f"aliases={len(aliases)} coverage={len(aliases)} inventory={len(combined)}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--genome", required=True)
    args = parser.parse_args()
    try:
        build_namespaces(args.build_dir, args.genome)
    except (ValueError, KeyError, OSError, pa.ArrowException) as error:
        parser.exit(1, f"contigs: {error}\n")


if __name__ == "__main__":
    main()
