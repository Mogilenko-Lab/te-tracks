#!/usr/bin/env python3
"""Prove full registration scope conserves a matrix over shared catalog features."""

from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from records import BUILD, require

require("tables/export_feature_members.tsv.gz")
keys, selected = set(), []
for chunk in pd.read_csv(BUILD / "tables/export_feature_members.tsv.gz", sep="\t", dtype=str,
                          keep_default_na=False, chunksize=250_000):
    chunk = chunk.loc[chunk.feature_level.eq("record") & chunk.key_grammar.eq("rmsk_record_id")]
    if len(keys) < 1000:
        keys.update(chunk.loc[chunk.universe_name.eq("interspersed"), "emitted_feature_id"].head(1000 - len(keys)))
    selected.append(chunk.loc[chunk.emitted_feature_id.isin(keys)])
registration = pd.concat(selected, ignore_index=True)
assert len(keys) == 1000 and len(registration) == 2000
assert registration.groupby("emitted_feature_id").universe_name.agg(set).eq({"interspersed", "all_rmsk"}).all()
counts = pd.DataFrame({"emitted_feature_id": sorted(keys), "count": np.arange(1, 1001),
                       "universe_name": "interspersed", "variant": "full", "feature_level": "record",
                       "key_grammar": "rmsk_record_id"})
pair = counts.merge(registration, on=["emitted_feature_id", "feature_level", "key_grammar"], validate="one_to_many")
full = counts.merge(registration, on=["emitted_feature_id", "universe_name", "variant", "feature_level", "key_grammar"],
                     validate="one_to_one")
assert len(pair) == 2000 and pair.groupby("emitted_feature_id").size().eq(2).all()
assert len(full) == 1000 and full.groupby("emitted_feature_id").size().eq(1).all()
assert pair["count"].sum() == 2 * counts["count"].sum() == 1001000
assert full["count"].sum() == counts["count"].sum() == 500500
print("1000 shared records: pair-only join=2000 rows/1001000 counts; four-field join=1000 rows/500500 counts")
