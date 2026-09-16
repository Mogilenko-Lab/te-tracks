#!/usr/bin/env python3
"""Check source instance membership, contig scope and measured size distribution."""

import sys
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from records import BUILD, read_tsv, require


require("tables/rmsk_records.parquet", "tables/rmsk_instance_members.tsv.gz")
columns = ["rmsk_instance_id", "rmsk_record_id"]
members = read_tsv(BUILD / "tables/rmsk_instance_members.tsv.gz",
                   pa.schema([(name, pa.string()) for name in columns])).to_pandas()
records = pq.read_table(BUILD / "tables/rmsk_records.parquet", columns=columns + ["chrom"]).to_pandas()
assert len(members) == len(records) == 5320771
assert members["rmsk_record_id"].is_unique
assert members["rmsk_instance_id"].str.fullmatch(r"[0-9]+").all()
expected = records[columns].sort_values(columns, ignore_index=True)
pd.testing.assert_frame_equal(members, expected)
assert records.groupby("rmsk_instance_id")["chrom"].nunique().eq(1).all()
sizes = members.groupby("rmsk_instance_id").size()
assert len(sizes) == 4696900, len(sizes)
distribution = {"1": int(sizes.eq(1).sum()), "2": int(sizes.eq(2).sum()),
                "3+": int(sizes.ge(3).sum())}
assert distribution == {"1": 4251251, "2": 338697, "3+": 106952}, distribution
print("4696900 instances; one instance per record; single contig; sizes 1=4251251 2=338697 3+=106952")
