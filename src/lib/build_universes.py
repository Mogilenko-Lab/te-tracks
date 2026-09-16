"""Evaluate versioned universe definitions against reviewed raw source classes."""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
from records_io import TAXONOMY_KEY, tsv_stream, write_frame, write_tsv


INTERSPERSED_CLASSES = [
    "SINE", "LTR", "LINE", "DNA", "RC", "Retroposon", "Unknown", "Unspecified", "DNA?"
]

DEFINITIONS = {
    "schema_version": 1,
    "default_universe": "interspersed",
    "universes": [
        {
            "name": "all_rmsk",
            "description": "Every record in the complete RepeatMasker catalog is included.",
            "predicate": {},
            "provisional_classes": [],
        },
        {
            "name": "interspersed",
            "description": "Interspersed repeat classes include tRNA-derived SINEs and provisional source classifications.",
            "predicate": {"class_in": INTERSPERSED_CLASSES},
            "provisional_classes": ["Unknown", "Unspecified", "DNA?"],
        },
        {
            "name": "interspersed_plus_satellites",
            "description": "Interspersed repeats and satellite records form the combined universe.",
            "predicate": {"class_in": INTERSPERSED_CLASSES + ["Satellite"]},
            "provisional_classes": ["Unknown", "Unspecified", "DNA?"],
        },
        {
            "name": "retrotransposon_derived",
            "description": "SINE, LTR, LINE and Retroposon records form the retrotransposon-derived universe.",
            "predicate": {"class_in": ["SINE", "LTR", "LINE", "Retroposon"]},
            "provisional_classes": [],
        },
        {
            "name": "satellites",
            "description": "Records classified as Satellite form the satellite universe.",
            "predicate": {"class_in": ["Satellite"]},
            "provisional_classes": [],
        },
        {
            "name": "compat_tetranscripts_mm39",
            "description": "The legacy mm39 class set applies the tRNA-family-prefix exclusion for TEtranscripts compatibility.",
            "predicate": {
                "class_in": INTERSPERSED_CLASSES + ["Satellite"],
                "family_prefix_excluded": "tRNA",
            },
            "provisional_classes": [],
        },
    ],
}


def evaluate_predicate(frame, predicate):
    """Conjoin object clauses; an empty object selects every row."""
    unknown = set(predicate) - {"class_in", "family_prefix_excluded"}
    if unknown:
        raise ValueError(f"unknown universe predicate keys: {sorted(unknown)}")
    selected = pd.Series(True, index=frame.index)
    if "class_in" in predicate:
        selected &= frame["rmsk_class"].isin(predicate["class_in"])
    if "family_prefix_excluded" in predicate:
        selected &= ~frame["rmsk_family"].str.startswith(predicate["family_prefix_excluded"])
    return selected


def check_class_set(frame, class_set_path):
    """Require reviewed dispositions to agree with observed classes and universes."""
    classes = pd.read_csv(class_set_path, sep="\t", dtype=str, keep_default_na=False)
    if list(classes) != ["rmsk_class", "disposition"]:
        raise ValueError(f"class set columns must be rmsk_class, disposition: {class_set_path}")
    duplicates = classes.loc[classes["rmsk_class"].duplicated(), "rmsk_class"]
    if not duplicates.empty:
        raise ValueError(f"duplicate rmsk_class in class set: {sorted(set(duplicates))}")
    vocabulary = {"interspersed", "satellite", "simple_repeat", "low_complexity", "structural_rna"}
    unknown = set(classes["disposition"]) - vocabulary
    if unknown:
        raise ValueError(f"unknown class disposition: {sorted(unknown)}")
    observed = set(frame["rmsk_class"])
    reviewed = set(classes["rmsk_class"])
    if observed != reviewed:
        raise ValueError(f"class set gate: unreviewed={sorted(observed - reviewed)}; "
                         f"absent={sorted(reviewed - observed)}")
    interspersed = set(classes.loc[classes["disposition"].eq("interspersed"), "rmsk_class"])
    for disposition, predicate_classes in (
        ("interspersed", set(INTERSPERSED_CLASSES)),
        ("satellite", {"Satellite"}),
    ):
        dispositioned = set(classes.loc[classes["disposition"].eq(disposition), "rmsk_class"])
        disposition_without_predicate = dispositioned - predicate_classes
        predicate_without_disposition = (reviewed & predicate_classes) - dispositioned
        if disposition_without_predicate or predicate_without_disposition:
            raise ValueError(f"{disposition} disposition gate: "
                             f"disposition_without_predicate={sorted(disposition_without_predicate)}; "
                             f"predicate_without_disposition={sorted(predicate_without_disposition)}")
    for universe in DEFINITIONS["universes"]:
        unreviewed = (set(universe["provisional_classes"]) & reviewed) - interspersed
        if unreviewed:
            raise ValueError(f"provisional disposition gate: universe={universe['name']}; "
                             f"outside_interspersed={sorted(unreviewed)}")


def build_universes(build_dir, class_set_path):
    """Write membership and summaries using the published predicate object."""
    build_dir = Path(build_dir)
    columns = ["rmsk_record_id", *TAXONOMY_KEY, "length_bp"]
    frame = pq.read_table(build_dir / "tables/rmsk_records.parquet", columns=columns).to_pandas()
    check_class_set(frame, class_set_path)
    serialized = json.dumps(DEFINITIONS, indent=2, ensure_ascii=False) + "\n"
    definitions = json.loads(serialized)
    frame = frame.sort_values("rmsk_record_id", ignore_index=True)
    summaries = []
    with tsv_stream(build_dir / "tables/universe_members.tsv.gz") as stream:
        header = True
        for universe in sorted(definitions["universes"], key=lambda item: item["name"]):
            members = frame.loc[evaluate_predicate(frame, universe["predicate"])]
            summaries.append({
                "universe_name": universe["name"], "records": len(members),
                "names": members["rmsk_name"].nunique(),
                "triples": len(members[TAXONOMY_KEY].drop_duplicates()),
                "length_sum_bp": int(members["length_bp"].sum()),
            })
            if universe["name"] != "all_rmsk":
                membership = pd.DataFrame({
                    "universe_name": universe["name"],
                    "rmsk_record_id": members["rmsk_record_id"],
                    "provisional": members["rmsk_class"].isin(universe["provisional_classes"]),
                })
                write_frame(membership, stream, header=header)
                header = False
    write_tsv(pd.DataFrame(summaries), build_dir / "tables/universe_summary.tsv")
    (build_dir / "universes.json").write_text(serialized, encoding="utf-8")
    for summary in summaries:
        print(" ".join(f"{key}={value}" for key, value in summary.items()), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--class-set", required=True, type=Path)
    args = parser.parse_args()
    try:
        build_universes(args.build_dir, args.class_set)
    except (ValueError, OSError) as error:
        parser.exit(1, f"build_universes: {error}\n")


if __name__ == "__main__":
    main()
