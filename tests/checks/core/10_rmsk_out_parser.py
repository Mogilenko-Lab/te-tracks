#!/usr/bin/env python3
"""Check source fields against hand-authored records and malformed input."""

import csv
import gzip
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src" / "lib"))
from rmsk_out import RecordStats, iter_records


FIXTURES = ROOT / "tests" / "fixtures" / "source"
INT_FIELDS = {
    "source_row_number", "sw_score", "start_1", "end_1", "query_left_bp",
    "consensus_start_1", "consensus_end_1", "consensus_left_bp",
}
FLOAT_FIELDS = {"divergence_pct", "deletion_pct", "insertion_pct"}
STRING_FIELDS = {
    "chrom", "raw_strand", "strand", "rmsk_name", "rmsk_class_family",
    "rmsk_class", "rmsk_family", "rmsk_instance_id",
}


def expected_records():
    with (FIXTURES / "expected.tsv").open() as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            yield {
                key: (int(value) if key in INT_FIELDS else
                      float(value) if key in FLOAT_FIELDS else
                      bool(int(value)) if key == "rmsk_overlap_flag" else value)
                for key, value in row.items()
            }


def assert_malformed(path, line_number, text):
    try:
        list(iter_records(path))
    except ValueError as error:
        assert str(path) in str(error), str(error)
        assert f"line {line_number}:" in str(error), str(error)
        assert text in str(error), str(error)
    else:
        raise AssertionError(f"accepted malformed row: {text}")


observed = list(iter_records(FIXTURES / "records.out"))
charlie17 = next(row for row in observed if row["rmsk_name"] == "Charlie17")
assert charlie17["consensus_left_bp"] == -1847, charlie17["consensus_left_bp"]
expected = list(expected_records())
assert observed == expected, (observed, expected)
for row in observed:
    assert set(row) == INT_FIELDS | FLOAT_FIELDS | STRING_FIELDS | {"rmsk_overlap_flag"}
    for key, value in row.items():
        want_type = (int if key in INT_FIELDS else float if key in FLOAT_FIELDS
                     else bool if key == "rmsk_overlap_flag" else str)
        assert type(value) is want_type, (key, type(value), want_type)
id2 = observed[1]
assert (id2["chrom"], id2["start_1"], id2["end_1"], id2["strand"]) == (
    "chr1", 3051045, 3051146, "-"
)
assert (id2["consensus_start_1"], id2["consensus_end_1"], id2["consensus_left_bp"]) == (5, 104, 48)
assert next(row for row in observed if row["rmsk_name"] == "SplitName")["consensus_start_1"] == -2
malformed_text = (FIXTURES / "unparenthesized_reverse_left.out").read_text().splitlines()[3]
assert_malformed(FIXTURES / "unparenthesized_reverse_left.out", 4, malformed_text)

with TemporaryDirectory(prefix="te-tracks-parser-") as directory:
    compressed = Path(directory) / "records.out.gz"
    with gzip.open(compressed, "wt") as stream:
        stream.write((FIXTURES / "records.out").read_text())
    assert list(iter_records(compressed)) == expected
    misnamed = Path(directory) / "compressed.out"
    misnamed.write_bytes(compressed.read_bytes())
    try:
        list(iter_records(misnamed))
    except ValueError as error:
        assert str(misnamed) in str(error), str(error)
    else:
        raise AssertionError(f"accepted gzip bytes as plain text: {misnamed}")
    tokens = "3667 6.7 0.0 1.0 chr1 3050294 3050775 (192103504) + L1MdA_VI LINE/L1 6094 6570 (6) 1".split()
    leading_zero_id = Path(directory) / "leading_zero_id.out"
    leading_zero_id.write_text(" ".join(tokens[:-1] + ["007"]) + "\n")
    assert list(iter_records(leading_zero_id))[0]["rmsk_instance_id"] == "007"
    negative_consensus_left = Path(directory) / "negative_consensus_left.out"
    row = tokens.copy()
    row[13] = "(-6)"
    negative_consensus_left.write_text(" ".join(row) + "\n")
    assert list(iter_records(negative_consensus_left))[0]["consensus_left_bp"] == -6
    bad_rows = [tokens[:-1], tokens + ["?"], tokens + ["*", "*"]]
    for index, replacement in ((0, "score?"), (1, "nan"), (5, "(3050294)"),
                               (7, "192103504"), (7, "(-1)"), (8, "-"), (11, "(6094)"),
                               (13, "6"), (14, "1.5"), (14, "(6)"),
                               (14, "+7"), (14, "1_000"), (14, "\u0667")):
        row = tokens.copy()
        row[index] = replacement
        bad_rows.append(row)
    for row in bad_rows:
        text = " ".join(row)
        path = Path(directory) / "unparenthesized_reverse_left.out"
        path.write_text("\n" + text + "\n")
        assert_malformed(path, 2, text)

stats = RecordStats()
for row in observed:
    stats.add(row)
assert stats.summary() == {"records": 6, "distinct_ids": 5, "ids_spanning_contigs": 0, "starred_rows": 1}
stats.add({**observed[0], "chrom": "chrOther"})
assert stats.summary()["ids_spanning_contigs"] == 1
print("6 expected records; plain/gzip, signed consensus, ID tokens, malformed/unreadable input and ID statistics pass")
