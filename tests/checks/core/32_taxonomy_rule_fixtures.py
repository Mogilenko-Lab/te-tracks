#!/usr/bin/env python3
"""Exercise taxonomy decisions, deterministic builds and one-count-per-name rollups."""

import contextlib
import csv
import io
from itertools import permutations
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/lib"))
from build_taxonomy import TAXONOMY_RULE_VERSION, build_taxonomy, resolve


FIXTURES = ROOT / "tests/fixtures/taxonomy"
FIELDS = ["canonical_class", "canonical_family", "class_status", "family_status"]
assert TAXONOMY_RULE_VERSION == "taxonomy_rule_v1"
with (FIXTURES / "rule_cases.tsv").open(encoding="utf-8", newline="") as stream:
    cases = list(csv.DictReader(stream, delimiter="\t"))
labels_by_case = {}
resolved_by_case = {}
for case in cases:
    labels = []
    for label in case["labels"].split(";") if case["labels"] else []:
        pair, count = label.rsplit("=", 1)
        cls, fam = pair.split("/", 1)
        labels.append((cls, fam, int(count)))
    original = labels.copy()
    result = resolve(labels)
    assert labels == original, case["case"]
    for field in FIELDS:
        assert result[field] == case[field], (case["case"], field, result[field], case[field])
    for permutation in permutations(labels):
        assert resolve(list(permutation)) == result, (case["case"], permutation)
    assert result["has_uncertain_source"] == any(
        cls.endswith("?") or fam.endswith("?") for cls, fam, _ in labels)
    assert result["label_count"] == len(set((cls, fam) for cls, fam, _ in labels))
    assert result["instance_count"] == sum(count for _, _, count in labels)
    assert result["has_multiple_labels"] == (result["label_count"] > 1)
    for rank in ("class", "family"):
        assert 0 <= result[f"{rank}_plurality_share"] <= 1, case["case"]
        if result[f"{rank}_status"] == "unresolved":
            assert result[f"canonical_{rank}"] == "", case["case"]
    assert 0 <= result["family_support_share"] <= 1, case["case"]
    if result["class_status"] == "unresolved":
        assert result["family_status"] == "unresolved", case["case"]
    labels_by_case[case["case"]] = labels
    resolved_by_case[case["case"]] = result
assert len(labels_by_case) == len(cases)
assert {r["class_status"] for r in resolved_by_case.values()} == {
    "concordant", "resolved_uncertainty_suffix", "resolved_plurality", "unresolved"}
assert {r["family_status"] for r in resolved_by_case.values()} == {
    "concordant", "resolved_uncertainty_suffix", "resolved_unspecified",
    "resolved_plurality", "unspecified", "unresolved"}
for name, class_share, family_share, support_share in [
    ("class_competition", 0.7, 1.0, 0.7), ("family_plurality", 1.0, 0.84, 0.84),
    ("family_tie", 1.0, 0.5, 0.5), ("class_tie", 0.5, 0.0, 0.0),
    ("eulor5b", 1.0, 1.0, 0.971), ("mer124", 1.0, 0.0, 0.0),
    ("plurality_precedence", 1.0, 0.7, 0.233), ("winning_class_only", 0.538, 0.571, 0.308),
    ("plurality", 0.444, 1.0, 0.444), ("empty_input", 0.0, 0.0, 0.0),
    ("winning_class_abstains", 0.7, 0.0, 0.0), ("instance_weighting", 1.0, 0.7, 0.7),
]:
    result = resolved_by_case[name]
    assert (result["class_plurality_share"], result["family_plurality_share"],
            result["family_support_share"]) == (class_share, family_share, support_share), (name, result)
assert resolve([("DNA", "hAT", 3), ("DNA", "hAT", 4)]) == resolve([("DNA", "hAT", 7)])

counts = pd.read_csv(FIXTURES / "rollup_counts.tsv", sep="\t")
context = pd.read_csv(FIXTURES / "weighting_context.tsv", sep="\t").set_index(
    ["case", "rmsk_class", "rmsk_family"])
assert context.index.is_unique
assert set(context.index) == {("instance_weighting", cls, fam)
                              for cls, fam, _ in labels_by_case["instance_weighting"]}
with TemporaryDirectory(prefix="te-tracks-taxonomy-") as directory:
    build = Path(directory)
    tables = build / "tables"
    tables.mkdir()
    raw_rows = []
    record_rows = []
    for name in counts["rmsk_name"]:
        for cls, fam, count in labels_by_case[name]:
            record_count, length_sum = count, count * 4
            if (name, cls, fam) in context.index:
                record_count = int(context.at[(name, cls, fam), "record_count"])
                length_sum = int(context.at[(name, cls, fam), "record_length_sum_bp"])
            raw_rows.append({"rmsk_name": name, "rmsk_family": fam, "rmsk_class": cls,
                             "record_count": record_count, "instance_count": count,
                             "record_length_sum_bp": length_sum})
            record_rows.extend({"rmsk_name": name, "divergence_pct": 1.0 + 3.0 * index}
                               for index in range(record_count))
    record_rows[0]["divergence_pct"] = 1.1
    record_rows[1]["divergence_pct"] = 4.2
    raw = pd.DataFrame(raw_rows)
    raw.to_csv(tables / "rmsk_taxonomy.tsv", sep="\t", index=False)
    pq.write_table(pa.Table.from_pylist(record_rows), tables / "rmsk_records.parquet")
    with contextlib.redirect_stdout(io.StringIO()):
        build_taxonomy(build)
    canonical = pd.read_csv(tables / "taxonomy_canonical.tsv", sep="\t", keep_default_na=False)
    assert canonical["rmsk_name"].tolist() == sorted(counts["rmsk_name"])
    for row in canonical.to_dict("records"):
        expected = resolved_by_case[row["rmsk_name"]]
        assert all(row[field] == expected[field] for field in FIELDS), row
        for field in ["class_plurality_share", "family_plurality_share", "family_support_share",
                      "instance_count", "label_count"]:
            assert row[field] == expected[field], (row["rmsk_name"], field, row[field], expected[field])
    weighted = raw.loc[raw["rmsk_name"].eq("instance_weighting")]
    for weight in ["record_count", "record_length_sum_bp"]:
        alternative = resolve(list(weighted[["rmsk_class", "rmsk_family", weight]].itertuples(
            index=False, name=None)))
        assert alternative["canonical_family"] == "TcMar", (weight, alternative)
    weighting = canonical.set_index("rmsk_name").loc["instance_weighting"]
    assert weighting["canonical_family"] == "hAT"
    assert weighting["instance_count"] == 10 and weighting["record_count"] == 37
    assert weighting["record_length_sum_bp"] == 3028
    rollup = canonical.set_index("rmsk_name").loc["rollup_two_labels"]
    assert rollup["instance_count"] == 2 and rollup["record_count"] == 2 and rollup["record_length_sum_bp"] == 8
    assert rollup["median_divergence_pct"] == 2.65
    joined = counts.merge(canonical, on="rmsk_name", validate="one_to_one")
    assert len(joined) == len(counts)
    for rank, expected in [
        ("family", {"DNA/hAT": 7, "unresolved_family_family_tie": 2,
                    "unresolved_family_family_tie_other": 3, "unresolved_family_class_tie": 5,
                    "Unknown/Unknown": 4}),
        ("class", {"DNA": 12, "unresolved_class_class_tie": 5, "Unknown": 4}),
    ]:
        bucket = (joined["canonical_class"] + "/" + joined["canonical_family"]
                  if rank == "family" else joined["canonical_class"])
        unresolved = joined[f"{rank}_status"].eq("unresolved")
        bucket = bucket.mask(unresolved, f"unresolved_{rank}_" + joined["rmsk_name"])
        assert not bucket[unresolved].str.contains(r"[/|:]").any(), (rank, "rollup token separators")
        assert bucket.tolist() == joined[f"{rank}_bucket"].tolist(), (rank, "fixture rollup buckets")
        totals = joined.groupby(bucket)["count"].sum().to_dict()
        assert totals == expected, (rank, totals, expected)
        assert sum(totals.values()) == counts["count"].sum()
    outputs = [tables / "taxonomy_canonical.tsv", tables / "taxonomy_resolution_report.tsv"]
    original_bytes = [path.read_bytes() for path in outputs]
    report = pd.read_csv(outputs[1], sep="\t", keep_default_na=False)
    assert report["rmsk_name"].tolist() == [
        "class_tie", "family_tie", "family_tie_other", "instance_weighting", "rollup_two_labels"]
    assert report.set_index("rmsk_name").at["family_tie", "rmsk_labels"] == "DNA/TcMar=2;DNA/hAT=2"
    weighted_report = report.set_index("rmsk_name").loc["instance_weighting"]
    assert weighted_report["rmsk_labels"] == "DNA/hAT=7;DNA/TcMar=3"
    assert weighted_report["rmsk_label_records"] == "DNA/hAT=7;DNA/TcMar=30"
    assert report["rule_version"].eq(TAXONOMY_RULE_VERSION).all()
    raw.iloc[::-1].to_csv(tables / "rmsk_taxonomy.tsv", sep="\t", index=False)
    pq.write_table(pa.Table.from_pylist(record_rows[::-1]), tables / "rmsk_records.parquet")
    with contextlib.redirect_stdout(io.StringIO()):
        build_taxonomy(build)
    assert [path.read_bytes() for path in outputs] == original_bytes
    for column, value, diagnostic in [
        ("record_count", 0, "positive record counts"),
        ("instance_count", 0, "instance counts between one and record counts"),
        ("instance_count", -1, "instance counts between one and record counts"),
        ("instance_count", 2, "instance counts between one and record counts"),
        ("record_length_sum_bp", 0, "positive lengths for every record"),
        ("rmsk_class", "?", "names and normalized classes"),
        ("rmsk_name", "", "names and normalized classes"),
    ]:
        altered = raw.copy()
        altered.loc[0, column] = value
        altered.to_csv(tables / "rmsk_taxonomy.tsv", sep="\t", index=False)
        try:
            build_taxonomy(build)
        except ValueError as error:
            assert diagnostic in str(error), (column, value, str(error))
        else:
            raise AssertionError(f"accepted invalid taxonomy: {column}={value!r}")
        assert [path.read_bytes() for path in outputs] == original_bytes
print(f"{len(cases)} rule cases; permutations, rank shares, instance weighting, rounded median, deterministic builds, input gates and canonical rollups pass")
