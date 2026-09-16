#!/usr/bin/env python3
"""Check complete typed serialization equality, identity and genomic bounds."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from records import BUILD, KEY, SCHEMA, TAXONOMY_SCHEMA, read_tsv, require


require("tables/rmsk_records.tsv.gz", "tables/rmsk_records.parquet", "source/mm39.chrom.sizes",
        "tables/rmsk_taxonomy.tsv")
taxonomy = read_tsv(BUILD / "tables/rmsk_taxonomy.tsv", TAXONOMY_SCHEMA).to_pandas()
assert taxonomy["instance_count"].between(1, taxonomy["record_count"]).all()
tsv = read_tsv(BUILD / "tables/rmsk_records.tsv.gz", SCHEMA)
parquet = pq.read_table(BUILD / "tables/rmsk_records.parquet")
assert parquet.schema.names == SCHEMA.names
assert [field.type for field in parquet.schema] == [field.type for field in SCHEMA]
assert all(not field.nullable for field in parquet.schema)
assert all(column.null_count == 0 for column in parquet.columns)
assert len(tsv) == len(parquet) == 5320771, (len(tsv), len(parquet))
assert tsv.equals(parquet.cast(SCHEMA)), "complete TSV/Parquet typed rows differ"
ordered = pc.sort_indices(parquet, sort_keys=[(name, "ascending") for name in KEY])
assert np.array_equal(ordered.to_numpy(), np.arange(len(parquet))), "record sort order"
frame = parquet.select([*KEY, "rmsk_record_id", "length_bp", "source_row_number",
                        "query_left_bp", "consensus_left_bp"]).to_pandas()
assert frame["rmsk_record_id"].is_unique
assert not frame.duplicated(KEY).any()
assert frame["strand"].isin(["+", "-"]).all()
assert not frame["rmsk_name"].str.contains(r"[|\s]").any()
assert not frame["chrom"].str.contains(r"[|:\s]").any()
constructed = (frame["rmsk_name"] + "|" + frame["chrom"] + ":"
               + frame["start_1"].astype(str) + "-" + frame["end_1"].astype(str)
               + "|" + frame["strand"])
assert constructed.equals(frame["rmsk_record_id"])
sizes = pd.read_csv(BUILD / "source/mm39.chrom.sizes", sep="\t", header=None,
                    names=["chrom", "length"], dtype={"chrom": str, "length": "int64"})
limits = frame["chrom"].map(sizes.set_index("chrom")["length"])
assert limits.notna().all()
assert ((frame["start_1"] >= 1) & (frame["end_1"] >= frame["start_1"])
        & (frame["end_1"] <= limits)).all()
assert frame["length_bp"].equals(frame["end_1"] - frame["start_1"] + 1)
assert np.array_equal(np.sort(frame["source_row_number"]), np.arange(1, len(frame) + 1))
assert (frame["query_left_bp"] >= 0).all()
assert (frame["consensus_left_bp"] < 0).sum() == 6
header = (BUILD / "tables/rmsk_records.tsv.gz").open("rb").read(10)
assert header[:4] == b"\x1f\x8b\x08\x00" and header[4:8] == b"\x00" * 4, header
print("5320771 records; 24 typed columns; all typed rows equal; identities and bounds pass")
