"""Derive one canonical taxonomy per name from instance-weighted source labels."""

import argparse
from collections import Counter
from pathlib import Path
import sys

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
from records_io import write_tsv


TAXONOMY_RULE_VERSION = "taxonomy_rule_v1"
CANONICAL_COLUMNS = [
    "rmsk_name", "canonical_class", "canonical_family", "class_status", "family_status",
    "class_plurality_share", "family_plurality_share", "family_support_share",
    "label_count", "record_count", "instance_count", "record_length_sum_bp",
    "median_divergence_pct", "has_uncertain_source", "has_multiple_labels",
]
REPORT_COLUMNS = [
    "rmsk_name", "rmsk_labels", "rmsk_label_records", "rule_version", "canonical_class",
    "canonical_family", "class_status", "family_status",
]


def resolve(labels: list[tuple[str, str, int]]) -> dict:
    """Resolve (class, family, instance_count) votes with empty unresolved ranks for invalid input."""
    raw = Counter()
    for cls, fam, count in labels:
        raw[cls, fam] += count
    result = {
        "canonical_class": "", "canonical_family": "",
        "class_status": "unresolved", "family_status": "unresolved",
        "class_plurality_share": 0.0, "family_plurality_share": 0.0,
        "family_support_share": 0.0,
        "label_count": len(raw), "instance_count": sum(raw.values()),
        "has_uncertain_source": any(cls.endswith("?") or fam.endswith("?")
                                    for cls, fam in raw),
        "has_multiple_labels": len(raw) > 1,
    }
    normalized = [(cls.removesuffix("?"), fam.removesuffix("?"), count)
                  for cls, fam, count in labels]
    if not normalized or any(not cls or count <= 0 for cls, _, count in normalized):
        return result

    classes = Counter()
    for cls, _, count in normalized:
        classes[cls] += count
    highest = max(classes.values())
    result["class_plurality_share"] = round(highest / result["instance_count"], 3)
    winners = [cls for cls, count in classes.items() if count == highest]
    if len(winners) != 1:
        return result
    winner = winners[0]
    result["canonical_class"] = winner
    result["class_status"] = (
        "resolved_plurality" if len(classes) > 1 else
        "resolved_uncertainty_suffix" if any(cls.endswith("?") for cls, _ in raw) else
        "concordant"
    )

    families = Counter()
    unspecified = False
    for cls, fam, count in normalized:
        if cls == winner:
            if fam and fam != cls:
                families[fam] += count
            else:
                unspecified = True
    if not families:
        result["canonical_family"] = winner
        result["family_status"] = "unspecified"
        return result
    highest = max(families.values())
    result["family_plurality_share"] = round(highest / sum(families.values()), 3)
    result["family_support_share"] = round(highest / result["instance_count"], 3)
    winners = [fam for fam, count in families.items() if count == highest]
    if len(winners) != 1:
        return result
    result["canonical_family"] = winners[0]
    result["family_status"] = (
        "resolved_plurality" if len(families) > 1 else
        "resolved_unspecified" if unspecified else
        "resolved_uncertainty_suffix" if any(
            cls.removesuffix("?") == winner and fam.endswith("?") for cls, fam in raw
        ) else "concordant"
    )
    return result


def build_taxonomy(build_dir):
    """Write sorted taxonomy and resolution evidence with conserved source counts."""
    tables = Path(build_dir) / "tables"
    taxonomy = pd.read_csv(
        tables / "rmsk_taxonomy.tsv", sep="\t", quoting=3, keep_default_na=False,
        dtype={"rmsk_name": str, "rmsk_class": str, "rmsk_family": str,
               "record_count": "int64", "instance_count": "int64",
               "record_length_sum_bp": "int64"},
    )
    expected_columns = ["rmsk_name", "rmsk_family", "rmsk_class", "record_count",
                        "instance_count", "record_length_sum_bp"]
    if list(taxonomy) != expected_columns:
        raise ValueError(f"rmsk_taxonomy columns must be {expected_columns}")
    if taxonomy.duplicated(expected_columns[:3]).any():
        raise ValueError("rmsk_taxonomy requires distinct raw triples")
    if (taxonomy["record_count"] <= 0).any():
        raise ValueError("rmsk_taxonomy requires positive record counts")
    if not taxonomy["instance_count"].between(1, taxonomy["record_count"]).all():
        raise ValueError("rmsk_taxonomy requires instance counts between one and record counts")
    if (taxonomy["record_length_sum_bp"] < taxonomy["record_count"]).any():
        raise ValueError("rmsk_taxonomy requires positive lengths for every record")
    if taxonomy["rmsk_name"].eq("").any() or taxonomy["rmsk_class"].str.removesuffix("?").eq("").any():
        raise ValueError("rmsk_taxonomy requires names and normalized classes")
    records = pq.read_table(tables / "rmsk_records.parquet",
                            columns=["rmsk_name", "divergence_pct"]).to_pandas()
    summaries = records.groupby("rmsk_name", sort=True).agg(
        record_count=("divergence_pct", "size"),
        median_divergence_pct=("divergence_pct", "median"),
    )
    counts = taxonomy.groupby("rmsk_name", sort=True)["record_count"].sum()
    if not counts.equals(summaries["record_count"]):
        raise ValueError("taxonomy and records require equal name sets and record counts")
    if summaries["median_divergence_pct"].isna().any():
        raise ValueError("each name requires a median record divergence")

    canonical_rows = []
    report_rows = []
    for name, group in taxonomy.groupby("rmsk_name", sort=True):
        labels = list(group[["rmsk_class", "rmsk_family", "instance_count"]].itertuples(
            index=False, name=None))
        resolved = resolve(labels)
        canonical_rows.append({
            "rmsk_name": name, **resolved,
            "record_count": int(group["record_count"].sum()),
            "record_length_sum_bp": int(group["record_length_sum_bp"].sum()),
            "median_divergence_pct": round(float(summaries.at[name, "median_divergence_pct"]), 2),
        })
        if resolved["has_multiple_labels"]:
            ordered = group.sort_values(
                ["instance_count", "rmsk_class", "rmsk_family"], ascending=[False, True, True])
            report_rows.append({
                "rmsk_name": name, **resolved, "rule_version": TAXONOMY_RULE_VERSION,
                "rmsk_labels": ";".join(
                    f"{row.rmsk_class}/{row.rmsk_family}={row.instance_count}"
                    for row in ordered.itertuples(index=False)
                ),
                "rmsk_label_records": ";".join(
                    f"{row.rmsk_class}/{row.rmsk_family}={row.record_count}"
                    for row in ordered.itertuples(index=False)
                ),
            })
    canonical = pd.DataFrame(canonical_rows, columns=CANONICAL_COLUMNS)
    report = pd.DataFrame(report_rows, columns=REPORT_COLUMNS)
    write_tsv(canonical, tables / "taxonomy_canonical.tsv")
    write_tsv(report, tables / "taxonomy_resolution_report.tsv")
    print(f"names={len(canonical)} multi_label_names={len(report)} "
          f"taxonomy_rule_version={TAXONOMY_RULE_VERSION}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        build_taxonomy(args.build_dir)
    except (ValueError, OSError, pa.ArrowException) as error:
        parser.exit(1, f"build_taxonomy: {error}\n")


if __name__ == "__main__":
    main()
