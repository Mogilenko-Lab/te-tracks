#!/usr/bin/env python3
"""Recompute reviewed universes, taxonomy and collision pairs from canonical records."""

import json
import sys
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from records import BUILD, KEY, ROOT, TRIPLE, read_tsv, require
sys.path.insert(0, str(ROOT / "src/lib"))
from build_universes import DEFINITIONS, INTERSPERSED_CLASSES


require("tables/rmsk_records.parquet", "tables/rmsk_taxonomy.tsv", "universes.json",
        "tables/universe_members.tsv.gz", "tables/universe_summary.tsv")
frame = pq.read_table(BUILD / "tables/rmsk_records.parquet",
                      columns=list(dict.fromkeys([*KEY, *TRIPLE, "rmsk_record_id", "length_bp"]))).to_pandas()
frame = frame.sort_values("rmsk_record_id", ignore_index=True)
census = frame["rmsk_class"].value_counts().sort_index().rename_axis("rmsk_class").reset_index(name="records")
expected_census = pd.read_csv(
    ROOT / "tests/expectations/mm39/class_census.tsv", sep="\t",
    dtype={"rmsk_class": str, "records": "int64"}, keep_default_na=False,
)
classes = pd.read_csv(ROOT / "config/mm39.classes.tsv", sep="\t",
                      dtype=str, keep_default_na=False)
assert list(classes) == ["rmsk_class", "disposition"], "class set columns differ"
assert classes["rmsk_class"].is_unique, "duplicate reviewed class"
assert set(classes["disposition"]) <= {
    "interspersed", "satellite", "simple_repeat", "low_complexity", "structural_rna"
}, "unknown class disposition"
assert set(frame["rmsk_class"]) == set(classes["rmsk_class"]), "observed/reviewed class sets differ"
assert set(expected_census["rmsk_class"]) == set(classes["rmsk_class"]), "census/config class sets differ"
pd.testing.assert_frame_equal(census, expected_census)
interspersed_classes = set(classes.loc[classes["disposition"].eq("interspersed"), "rmsk_class"])
satellite_classes = set(classes.loc[classes["disposition"].eq("satellite"), "rmsk_class"])
assert classes["disposition"].eq("interspersed").equals(
    classes["rmsk_class"].isin(INTERSPERSED_CLASSES)
), "interspersed disposition/predicate classes differ"
assert classes["disposition"].eq("satellite").equals(
    classes["rmsk_class"].eq("Satellite")
), "satellite disposition/predicate classes differ"
assert set(INTERSPERSED_CLASSES) <= set(classes["rmsk_class"]), "mm39 predicate classes require review"
for universe in DEFINITIONS["universes"]:
    assert set(universe["provisional_classes"]) <= interspersed_classes, universe["name"]
interspersed = frame["rmsk_class"].isin(interspersed_classes)
satellites = frame["rmsk_class"].isin(satellite_classes)
masks = {
    "all_rmsk": pd.Series(True, index=frame.index),
    "interspersed": interspersed,
    "interspersed_plus_satellites": interspersed | satellites,
    "retrotransposon_derived": frame["rmsk_class"].isin(["SINE", "LTR", "LINE", "Retroposon"]),
    "satellites": satellites,
    "compat_tetranscripts_mm39": (interspersed | satellites) & ~frame["rmsk_family"].str.startswith("tRNA"),
}
definitions = json.loads((BUILD / "universes.json").read_text())
assert definitions["schema_version"] == 1
assert definitions["default_universe"] == "interspersed"
assert len(definitions["universes"]) == 6
assert {item["name"] for item in definitions["universes"]} == set(masks)


def declared_mask(predicate):
    assert set(predicate) <= {"class_in", "family_prefix_excluded"}
    result = pd.Series(True, index=frame.index)
    if "class_in" in predicate:
        result &= frame["rmsk_class"].isin(predicate["class_in"])
    if "family_prefix_excluded" in predicate:
        result &= ~frame["rmsk_family"].str.startswith(predicate["family_prefix_excluded"])
    return result


membership_schema = pa.schema([("universe_name", pa.string()), ("rmsk_record_id", pa.string()),
                               ("provisional", pa.bool_())])
members = read_tsv(BUILD / "tables/universe_members.tsv.gz", membership_schema).to_pandas()
assert members["universe_name"].is_monotonic_increasing
assert set(members["universe_name"]) == set(masks) - {"all_rmsk"}
groups = members.groupby("universe_name", sort=False)
summaries = []
for universe in sorted(definitions["universes"], key=lambda item: item["name"]):
    name = universe["name"]
    assert universe["description"].endswith(".")
    assert set(universe["provisional_classes"]) <= interspersed_classes, name
    if name == "interspersed":
        assert set(universe["predicate"]["class_in"]) == interspersed_classes, name
    if name == "satellites":
        assert set(universe["predicate"]["class_in"]) == satellite_classes, name
    assert declared_mask(universe["predicate"]).equals(masks[name]), name
    selected = frame.loc[masks[name]]
    provisional = (["Unknown", "Unspecified", "DNA?"] if name in
                   {"interspersed", "interspersed_plus_satellites"} else [])
    assert universe["provisional_classes"] == provisional, name
    if name != "all_rmsk":
        observed = groups.get_group(name).reset_index(drop=True)
        expected = pd.DataFrame({
            "universe_name": name, "rmsk_record_id": selected["rmsk_record_id"],
            "provisional": selected["rmsk_class"].isin(provisional),
        }).reset_index(drop=True)
        pd.testing.assert_frame_equal(observed, expected, obj=name)
    summaries.append([name, len(selected), selected["rmsk_name"].nunique(),
                      len(selected[TRIPLE].drop_duplicates()), int(selected["length_bp"].sum())])
summary_schema = pa.schema([("universe_name", pa.string()), *[(name, pa.int64()) for name in
                           ("records", "names", "triples", "length_sum_bp")]])
summary = read_tsv(BUILD / "tables/universe_summary.tsv", summary_schema).to_pandas()
expected_summary = read_tsv(ROOT / "tests/expectations/mm39/universe_summary.tsv", summary_schema).to_pandas()
pd.testing.assert_frame_equal(summary, expected_summary)
pd.testing.assert_frame_equal(pd.DataFrame(summaries, columns=summary_schema.names), expected_summary)
collisions = frame.loc[frame.duplicated(KEY[:4], keep=False)]
observed_pairs = {
    (chrom, start, end, strand, tuple(sorted(group["rmsk_name"])))
    for (chrom, start, end, strand), group in collisions.groupby(KEY[:4])
}
assert observed_pairs == {
    ("chr11", 67327101, 67327210, "-", ("B1F", "ORR1B1-int")),
    ("chr13", 58658238, 58658287, "-", ("B1_Mus1", "ORR1B1-int")),
    ("chr16", 37859046, 37859109, "+", ("B1_Mur3", "ID_B1")),
}, observed_pairs
assert collisions["rmsk_record_id"].nunique() == 6
taxonomy_schema = pa.schema([*[(name, pa.string()) for name in TRIPLE],
                            ("record_count", pa.int64()), ("record_length_sum_bp", pa.int64())])
taxonomy = read_tsv(BUILD / "tables/rmsk_taxonomy.tsv", taxonomy_schema).to_pandas()
expected_taxonomy = frame.groupby(TRIPLE, sort=True).agg(
    record_count=("rmsk_record_id", "size"), record_length_sum_bp=("length_bp", "sum")
).reset_index()
pd.testing.assert_frame_equal(taxonomy, expected_taxonomy)
ambiguous = taxonomy.loc[taxonomy["rmsk_name"].duplicated(keep=False)]
assert ambiguous["rmsk_name"].nunique() == 20
assert ambiguous["record_count"].sum() == 6517
print("six universe summaries and every membership match; 17 classes; 3 collision pairs; 20 multi-label names / 6517 records")
