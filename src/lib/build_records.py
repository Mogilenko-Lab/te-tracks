"""Build the complete canonical RepeatMasker catalog and its identity relations."""

import argparse
import sys
from itertools import islice
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
from records_io import RECORD_KEY, RECORD_SCHEMA, TAXONOMY_KEY, write_tsv
from rmsk_out import iter_records


def fail_row(frame, mask, message, columns=RECORD_KEY):
    """Name the first offending record when an invariant fails."""
    if mask.any():
        offender = frame.loc[mask, columns].iloc[0].to_dict()
        raise ValueError(f"{message}: {offender}")


def load_out(path):
    """Retain parser types while limiting temporary Python record objects."""
    records = iter_records(path)
    batches = []
    while batch := list(islice(records, 100_000)):
        batches.append(pa.Table.from_pylist(batch))
    if not batches:
        raise ValueError(f"empty RepeatMasker source: {path}")
    return pa.concat_tables(batches).to_pandas()


def load_ucsc(path):
    """Read raw signed repeat coordinates and the qualified UCSC taxonomy."""
    names = ["bin", "swScore", "milliDiv", "milliDel", "milliIns", "chrom",
             "start_0", "end_1", "genoLeft", "strand", "rmsk_name",
             "rmsk_class", "rmsk_family", "ucsc_rep_start", "ucsc_rep_end",
             "ucsc_rep_left", "id"]
    selected = ["chrom", "start_0", "end_1", "strand", "rmsk_name",
                "rmsk_class", "rmsk_family", "ucsc_rep_start", "ucsc_rep_end",
                "ucsc_rep_left"]
    integers = {"start_0", "end_1", "ucsc_rep_start", "ucsc_rep_end", "ucsc_rep_left"}
    frame = pd.read_csv(path, sep="\t", header=None, names=names, usecols=selected,
                        dtype={name: "int64" if name in integers else str
                               for name in selected}, keep_default_na=False,
                        na_filter=False, quoting=3)
    frame["start_1"] = frame.pop("start_0") + 1
    fail_row(frame, frame.duplicated(RECORD_KEY), "UCSC exact duplicate key")
    return frame


def load_sizes(path):
    """Require a unique positive length for each contig."""
    sizes = {}
    with open(path, encoding="utf-8") as stream:
        for line in stream:
            chrom, length = line.split()
            if chrom in sizes or int(length) < 1:
                raise ValueError(f"invalid contig length or duplicate chrom: {chrom}")
            sizes[chrom] = int(length)
    return sizes


def validate_records(frame, sizes):
    """Enforce parseable unique identities, genomic bounds and instance scope."""
    for name, pattern in (("rmsk_name", r"[|:/\s]"), ("chrom", r"[|:\s]")):
        fail_row(frame, frame[name].str.contains(pattern) | frame[name].eq(""),
                 f"invalid {name} for record identity")
    fail_row(frame, frame.duplicated(RECORD_KEY), "exact duplicate key")
    fail_row(frame, ~frame["chrom"].isin(sizes), "chrom absent from chrom.sizes")
    limits = frame["chrom"].map(sizes)
    fail_row(frame, (frame["start_1"] < 1) | (frame["end_1"] < frame["start_1"]) |
             (frame["end_1"] > limits), "record outside contig bounds")
    fail_row(frame, frame["rmsk_instance_id"].eq("") | frame["rmsk_instance_id"].isna(),
             "record requires exactly one instance")
    scopes = frame[["rmsk_instance_id", "chrom"]].drop_duplicates()
    fail_row(scopes, scopes.duplicated("rmsk_instance_id"),
             "instance spans multiple contigs", ["rmsk_instance_id", "chrom"])
    frame["rmsk_record_id"] = (
        frame["rmsk_name"] + "|" + frame["chrom"] + ":" + frame["start_1"].astype(str)
        + "-" + frame["end_1"].astype(str) + "|" + frame["strand"]
    )
    fail_row(frame, frame["rmsk_record_id"].duplicated(), "duplicate rmsk_record_id",
             ["rmsk_record_id"])
    frame["length_bp"] = frame["end_1"] - frame["start_1"] + 1


def build_records(out_path, table_path, sizes_path, tables_dir):
    """Write typed canonical tables after all identity and source-join gates pass."""
    frame = load_out(out_path)
    validate_records(frame, load_sizes(sizes_path))
    browser = load_ucsc(table_path)
    frame = frame.merge(browser, on=RECORD_KEY, how="outer", validate="one_to_one",
                        suffixes=("", "_ucsc"), indicator=True)
    fail_row(frame, frame["_merge"].ne("both"), "UCSC join requires a 1:1 match")
    for name in ("rmsk_class", "rmsk_family"):
        fail_row(frame, frame[name].ne(frame[name + "_ucsc"]),
                 f"UCSC {name} disagreement")
        frame[name] = frame.pop(name + "_ucsc")
    frame = frame[RECORD_SCHEMA.names].sort_values(RECORD_KEY, ignore_index=True)
    for field in RECORD_SCHEMA:
        fail_row(frame, frame[field.name].isna(), f"null in {field.name}")
        if pa.types.is_string(field.type):
            fail_row(frame, frame[field.name].str.contains(r"[\t\r\n]"),
                     f"TSV delimiter in {field.name}")
    table = pa.Table.from_pandas(frame, schema=RECORD_SCHEMA, preserve_index=False)
    table = table.replace_schema_metadata(None)
    members = frame[["rmsk_instance_id", "rmsk_record_id"]].sort_values(
        ["rmsk_instance_id", "rmsk_record_id"], ignore_index=True)
    if len(members) != len(frame) or members["rmsk_record_id"].duplicated().any():
        raise ValueError("instance membership requires exactly one row per rmsk_record_id")
    taxonomy = frame.groupby(TAXONOMY_KEY, sort=True, dropna=False).agg(
        record_count=("rmsk_record_id", "size"),
        instance_count=("rmsk_instance_id", "nunique"),
        record_length_sum_bp=("length_bp", "sum")
    ).reset_index()
    tables_dir = Path(tables_dir)
    tables_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(frame, tables_dir / "rmsk_records.tsv.gz")
    pq.write_table(table, tables_dir / "rmsk_records.parquet", compression="snappy",
                   row_group_size=100_000, version="2.6")
    write_tsv(members, tables_dir / "rmsk_instance_members.tsv.gz")
    write_tsv(taxonomy, tables_dir / "rmsk_taxonomy.tsv")
    print(f"records={len(frame)} instances={members['rmsk_instance_id'].nunique()} "
          f"names={frame['rmsk_name'].nunique()} triples={len(taxonomy)}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for argument in ("out", "table", "sizes", "tables-dir"):
        parser.add_argument("--" + argument, required=True, type=Path)
    args = parser.parse_args()
    try:
        build_records(args.out, args.table, args.sizes, args.tables_dir)
    except (ValueError, OSError, pa.ArrowException) as error:
        parser.exit(1, f"build_records: {error}\n")


if __name__ == "__main__":
    main()
