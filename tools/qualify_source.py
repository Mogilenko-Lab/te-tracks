#!/usr/bin/env python3
"""Qualify rm_out_v1 against the UCSC rmsk table as keyed multisets."""

import argparse
import hashlib
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "lib"))
from rmsk_out import PROFILE, RecordStats, iter_records, open_text


SHARED_FIELDS = (
    "swScore", "milliDiv", "milliDel", "milliIns", "genoLeft",
    "repClass", "repFamily", "repStart", "repEnd", "repLeft",
)


def iter_table(path):
    """Yield the join key and shared UCSC fields from each 17-column row."""
    with open_text(path) as stream:
        for line_number, line in enumerate(stream, 1):
            try:
                fields = line.rstrip("\r\n").split("\t")
                if len(fields) != 17:
                    raise ValueError("expected 17 tab-separated fields")
                if fields[9] not in {"+", "-"}:
                    raise ValueError("expected + or - strand")
                key = (sys.intern(fields[5]), int(fields[6]) + 1,
                       int(fields[7]), fields[9], sys.intern(fields[10]))
                shared = (
                    *(int(fields[i]) for i in (1, 2, 3, 4, 8)),
                    sys.intern(fields[11]), sys.intern(fields[12]),
                    *(int(fields[i]) for i in (13, 14, 15)),
                )
            except ValueError as error:
                raise ValueError(
                    f"{path}: line {line_number}: {error}; text={line.rstrip()!r}"
                ) from error
            yield key, shared


def project_record(record):
    """Encode normalized .out values in UCSC's signed coordinate convention."""
    if record["strand"] == "+":
        rep_start = record["consensus_start_1"]
        rep_left = -record["consensus_left_bp"]
    else:
        rep_start = -record["consensus_left_bp"]
        rep_left = record["consensus_start_1"]
    key = (sys.intern(record["chrom"]), record["start_1"], record["end_1"],
           record["strand"], sys.intern(record["rmsk_name"]))
    shared = (
        record["sw_score"],
        *(round(record[field] * 10)
          for field in ("divergence_pct", "deletion_pct", "insertion_pct")),
        -record["query_left_bp"], record["rmsk_class"], record["rmsk_family"],
        rep_start, record["consensus_end_1"], rep_left,
    )
    return key, shared


def qualify(out_path, table_path):
    """Stream sources into a multiset join, retaining every row's multiplicity."""
    table = defaultdict(list)
    table_rows = 0
    for key, shared in iter_table(table_path):
        table[key].append(shared)
        table_rows += 1

    stats = RecordStats()
    pending = defaultdict(list)
    coordinate_names = {}
    collisions = defaultdict(set)
    matched_rows = 0
    for record in iter_records(out_path):
        stats.add(record)
        key, shared = project_record(record)
        coordinate, name = key[:4], key[4]
        first_name = coordinate_names.setdefault(coordinate, name)
        if name != first_name:
            collisions[coordinate].update((first_name, name))
        candidates = table.get(key)
        if candidates and shared in candidates:
            candidates.remove(shared)
            matched_rows += 1
            if not candidates:
                del table[key]
        else:
            pending[key].append(shared)

    # Pair exact shared values first so source order preserves multiset equality.
    disagreements = dict.fromkeys(SHARED_FIELDS, 0)
    unmatched_out_rows = 0
    unmatched_out_examples = []
    for key in sorted(pending):
        out_values = sorted(pending[key])
        table_values = sorted(table.get(key, []))
        pairs = min(len(out_values), len(table_values))
        matched_rows += pairs
        for out_shared, table_shared in zip(out_values, table_values):
            for field, out_value, table_value in zip(SHARED_FIELDS, out_shared, table_shared):
                disagreements[field] += out_value != table_value
        unmatched_out_rows += len(out_values) - pairs
        for shared in out_values[pairs:]:
            if len(unmatched_out_examples) < 20:
                unmatched_out_examples.append((key, shared))
        if table_values[pairs:]:
            table[key] = table_values[pairs:]
        else:
            table.pop(key, None)

    unmatched_table_rows = sum(len(values) for values in table.values())
    unmatched_table_examples = []
    for key in sorted(table):
        for shared in sorted(table[key]):
            unmatched_table_examples.append((key, shared))
            if len(unmatched_table_examples) == 20:
                break
        if len(unmatched_table_examples) == 20:
            break
    collision_pairs = [
        (*coordinate, first, second)
        for coordinate, names in sorted(collisions.items())
        for first, second in combinations(sorted(names), 2)
    ]
    id_min = min(stats.id_contigs, default=0)
    id_max = max(stats.id_contigs, default=0)
    metrics = {
        "out_rows": stats.records,
        "table_rows": table_rows,
        "matched_rows": matched_rows,
        "unmatched_out_rows": unmatched_out_rows,
        "unmatched_table_rows": unmatched_table_rows,
        "field_disagreements": sum(disagreements.values()),
        "distinct_ids": len(stats.id_contigs),
        "id_min": id_min,
        "id_max": id_max,
        "ids_contiguous": int(bool(stats.id_contigs) and id_max - id_min + 1 == len(stats.id_contigs)),
        "ids_spanning_contigs": len(stats.spanning_ids),
        "starred_rows": stats.starred_rows,
        "coordinate_collision_pairs": len(collision_pairs),
    }
    passed = (stats.records == table_rows == matched_rows
              and unmatched_out_rows == unmatched_table_rows == 0
              and metrics["field_disagreements"] == 0)
    return metrics, disagreements, unmatched_out_examples, unmatched_table_examples, collision_pairs, passed


def md5_of(path):
    digest = hashlib.md5()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_report(path, out_path, table_path, result):
    metrics, disagreements, out_examples, table_examples, collisions, passed = result
    lines = [
        "# RepeatMasker source qualification", "",
        f"Status: {'PASS' if passed else 'FAIL'}. Parser profile: `{PROFILE}`.", "",
        "| source | md5 | bytes |", "|---|---|---:|",
        *(f"| `{source.name}` | `{md5_of(source)}` | {source.stat().st_size:,} |"
          for source in (out_path, table_path)), "",
        "The multiset join uses `(chrom, start_1, end_1, strand, name)` and preserves row multiplicity.",
        "The key converts `genoStart + 1` and maps `.out` strand `C` to `-`.",
        "Shared fields compare score directly, percentages as `round(perc * 10)`, and query left as `-(query_left_bp)`.",
        "Class/family splits once at `/`; class-only tokens project the class into both UCSC fields.",
        "On `+`, `(repStart, repEnd, repLeft) = (consensus_start_1, consensus_end_1, -consensus_left_bp)`.",
        "On `-`, `(repStart, repEnd, repLeft) = (-consensus_left_bp, consensus_end_1, consensus_start_1)`.",
        "The `.out` ID supplies grouping statistics; UCSC `bin` and its independent one-character `id` remain table metadata.",
        "Exact shared values pair first; remaining values pair in sorted order within each key for field diagnostics.", "",
        "Measurement references: `docs/_internal/redesign-2026-09/audit/audit_out.py` and `docs/_internal/redesign-2026-09/audit/audit_rmsk.py`.", "",
        "## Summary", "", "| metric | value |", "|---|---:|",
        *(f"| {key} | {value:,} |" for key, value in metrics.items()), "",
        "## Shared-field disagreements", "", "| field | disagreements |", "|---|---:|",
        *(f"| {field} | {count:,} |" for field, count in disagreements.items()), "",
    ]
    for label, examples in ((".out", out_examples), ("UCSC table", table_examples)):
        lines += [f"## Unmatched {label} rows", ""]
        if examples:
            lines += ["First 20 rows at most; columns are the join key followed by the shared fields above.",
                      "", "```tsv"]
            lines += ["\t".join(map(str, (*key, *shared))) for key, shared in examples]
            lines += ["```", ""]
        else:
            lines += ["Count: 0.", ""]
    lines += [
        "## Coordinate-only collision pairs", "",
        "Pairs group `.out` rows by `(chrom, start_1, end_1, strand)` and distinct names; `start_0` aligns with the audit coordinates.",
        "", "| chrom | start_0 | start_1 | end_1 | strand | name_a | name_b |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    lines += [f"| {chrom} | {start - 1} | {start} | {end} | {strand} | {first} | {second} |"
              for chrom, start, end, strand, first, second in collisions]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--table", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    result = qualify(args.out, args.table)
    write_report(args.report, args.out, args.table, result)
    print(" ".join(f"{key}={value}" for key, value in result[0].items()))
    return 0 if result[-1] else 1


if __name__ == "__main__":
    sys.exit(main())
