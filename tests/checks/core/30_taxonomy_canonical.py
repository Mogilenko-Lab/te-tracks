#!/usr/bin/env python3
"""Recompute every canonical field, resolution report row and acceptance census metric."""

from pathlib import Path
import sys

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from records import BUILD, ROOT, TAXONOMY_SCHEMA, read_tsv, require
sys.path.insert(0, str(ROOT / "src/lib"))
from build_taxonomy import resolve


SCHEMA = pa.schema([
    ("rmsk_name", pa.string()), ("canonical_class", pa.string()),
    ("canonical_family", pa.string()), ("class_status", pa.string()),
    ("family_status", pa.string()), ("class_plurality_share", pa.float64()),
    ("family_plurality_share", pa.float64()), ("family_support_share", pa.float64()),
    ("label_count", pa.int64()), ("record_count", pa.int64()),
    ("instance_count", pa.int64()), ("record_length_sum_bp", pa.int64()),
    ("median_divergence_pct", pa.float64()), ("has_uncertain_source", pa.bool_()),
    ("has_multiple_labels", pa.bool_()),
])
REPORT_SCHEMA = pa.schema([(name, pa.string()) for name in [
    "rmsk_name", "rmsk_labels", "rmsk_label_records", "rule_version", "canonical_class",
    "canonical_family", "class_status", "family_status",
]])
STATUSES = {
    "class": ["concordant", "resolved_uncertainty_suffix", "resolved_plurality", "unresolved"],
    "family": ["concordant", "resolved_uncertainty_suffix", "resolved_unspecified",
               "resolved_plurality", "unspecified", "unresolved"],
}
require("tables/taxonomy_canonical.tsv", "tables/taxonomy_resolution_report.tsv",
        "tables/rmsk_taxonomy.tsv", "tables/rmsk_records.parquet")
canonical = read_tsv(BUILD / "tables/taxonomy_canonical.tsv", SCHEMA).to_pandas()
report = read_tsv(BUILD / "tables/taxonomy_resolution_report.tsv", REPORT_SCHEMA).to_pandas()
raw = read_tsv(BUILD / "tables/rmsk_taxonomy.tsv", TAXONOMY_SCHEMA).to_pandas()
records = pq.read_table(BUILD / "tables/rmsk_records.parquet",
                        columns=["rmsk_name", "divergence_pct"]).to_pandas()
medians = records.groupby("rmsk_name")["divergence_pct"].median().round(2)
assert set(raw["rmsk_name"]) == set(medians.index), "taxonomy/parquet name coverage"
assert canonical["rmsk_name"].is_unique, "canonical name uniqueness"
assert canonical["rmsk_name"].tolist() == sorted(canonical["rmsk_name"]), "canonical name order"
assert canonical["has_multiple_labels"].equals(canonical["label_count"].gt(1))
for rank, statuses in STATUSES.items():
    assert canonical[f"{rank}_status"].isin(statuses).all(), (rank, "status vocabulary")
    assert canonical[f"{rank}_plurality_share"].between(0, 1).all(), (rank, "share bounds")
    assert canonical[f"canonical_{rank}"].eq("").equals(
        canonical[f"{rank}_status"].eq("unresolved")), (rank, "unresolved field")
assert canonical["family_support_share"].between(0, 1).all(), "family support bounds"

expected_rows = []
expected_report = []
for name, group in raw.groupby("rmsk_name", sort=True):
    resolved = resolve(list(group[["rmsk_class", "rmsk_family", "instance_count"]].itertuples(
        index=False, name=None)))
    expected_rows.append({
        "rmsk_name": name, **resolved,
        "record_count": int(group["record_count"].sum()),
        "record_length_sum_bp": int(group["record_length_sum_bp"].sum()),
        "median_divergence_pct": medians.at[name],
    })
    if len(group) > 1:
        ordered = sorted(group.itertuples(index=False),
                         key=lambda row: (-row.instance_count, row.rmsk_class, row.rmsk_family))
        expected_report.append({
            "rmsk_name": name, **resolved, "rule_version": "taxonomy_rule_v1",
            "rmsk_labels": ";".join(f"{row.rmsk_class}/{row.rmsk_family}={row.instance_count}"
                                     for row in ordered),
            "rmsk_label_records": ";".join(f"{row.rmsk_class}/{row.rmsk_family}={row.record_count}"
                                           for row in ordered),
        })
pd.testing.assert_frame_equal(canonical, pd.DataFrame(expected_rows, columns=SCHEMA.names),
                              check_exact=True, obj="all canonical columns")
pd.testing.assert_frame_equal(report, pd.DataFrame(expected_report, columns=REPORT_SCHEMA.names),
                              check_exact=True, obj="complete resolution report")
multiple = canonical.loc[canonical["has_multiple_labels"]]
assert multiple["canonical_class"].eq("DNA").all(), "multi-label class census"
assert report["rmsk_name"].is_unique, "report name uniqueness"
columns = ["rmsk_name", "canonical_class", "canonical_family", "class_status", "family_status"]
pd.testing.assert_frame_equal(report[columns], multiple[columns].reset_index(drop=True),
                              check_exact=True, obj="multi-label report membership")

census_schema = pa.schema([("metric", pa.string()), ("value", pa.string())])
census = read_tsv(ROOT / "tests/expectations/mm39/taxonomy_census.tsv", census_schema).to_pandas()
assert census["metric"].is_unique, "census metric uniqueness"
observed = {
    "names": str(len(canonical)), "multi_label_names": str(len(multiple)),
    "raw_triples": str(len(raw)), "instance_count_sum": str(canonical["instance_count"].sum()),
}
for prefix, frame in [("", canonical), ("multi_label_", multiple)]:
    for rank, statuses in STATUSES.items():
        for status in statuses:
            observed[f"{prefix}{rank}_status.{status}"] = str(frame[f"{rank}_status"].eq(status).sum())
plurality = canonical.loc[canonical["family_status"].eq("resolved_plurality")].sort_values(
    ["family_plurality_share", "rmsk_name"])
assert len(plurality), "plurality census requires a measured minimum"
minimum = plurality.iloc[0]
observed["minimum_family_plurality_share"] = f"{minimum['family_plurality_share']:.3f}"
observed["minimum_family_plurality_share_name"] = minimum["rmsk_name"]
snapshot = pd.read_csv(ROOT / "tests/fixtures/taxonomy/dfam_snapshot.tsv", sep="\t",
                       dtype=str, keep_default_na=False)
observed["snapshot_rows"] = str(len(snapshot))
expected_census = census.set_index("metric")["value"].to_dict()
assert observed == expected_census, ("taxonomy census", observed, expected_census)
assert int(raw["instance_count"].sum()) == int(observed["instance_count_sum"]), "instance conservation"
print(f"{len(canonical)} names; all {len(SCHEMA)} columns recomputed exactly; "
      f"{len(report)} report rows equal the multi-label subset; census matches; "
      f"minimum plurality share {minimum['family_plurality_share']:.3f} {minimum['rmsk_name']}")
