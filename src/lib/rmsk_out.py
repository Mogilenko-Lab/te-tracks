"""Parse rm_out_v1: query_left_bp is a parenthesized nonnegative integer;
consensus_left_bp is a parenthesized signed integer; negatives extend past the consensus end.
Consensus start and end are signed; IDs, names and class tokens retain their text.
"""

import argparse
import csv
import gzip
import math
import re
import sys
import zlib
from itertools import islice
from pathlib import Path


PROFILE = "rm_out_v1"
FIELDS = (
    "source_row_number", "sw_score", "divergence_pct", "deletion_pct", "insertion_pct",
    "chrom", "start_1", "end_1", "query_left_bp", "raw_strand", "strand",
    "rmsk_name", "rmsk_class_family", "rmsk_class", "rmsk_family",
    "consensus_start_1", "consensus_end_1", "consensus_left_bp", "rmsk_instance_id",
    "rmsk_overlap_flag",
)


def open_text(path):
    """Read plain text or a gzip stream selected by the .gz suffix."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    return opener(path, "rt", encoding="utf-8")


def query_left_bp(token):
    """Decode query left as a parenthesized nonnegative integer."""
    if not re.fullmatch(r"\([0-9]+\)", token):
        raise ValueError("expected a parenthesized nonnegative integer query left")
    return int(token[1:-1])


def consensus_left_bp(token):
    """Decode consensus left as a parenthesized signed integer."""
    if not re.fullmatch(r"\([+-]?[0-9]+\)", token):
        raise ValueError("expected a parenthesized signed integer consensus left")
    return int(token[1:-1])


def iter_records(path):
    """Yield typed records; malformed or unreadable input raises ValueError with path.

    Malformed rows include line and text; read failures include the last known line.
    """
    source_row_number = 0
    line_number = 0
    try:
        with open_text(path) as stream:
            for line_number, line in enumerate(stream, 1):
                tokens = line.split()
                if not tokens or tokens[0] in {"SW", "score"}:
                    continue
                try:
                    if len(tokens) not in (15, 16):
                        raise ValueError("expected 15 fields and an optional *")
                    if len(tokens) == 16 and tokens[15] != "*":
                        raise ValueError("expected * as field 16")
                    raw_strand = tokens[8]
                    if raw_strand not in {"+", "C"}:
                        raise ValueError("expected + or C strand")
                    sw_score = int(tokens[0])
                    percentages = tuple(float(token) for token in tokens[1:4])
                    if not all(math.isfinite(value) for value in percentages):
                        raise ValueError("expected finite percentages")
                    start, end = int(tokens[5]), int(tokens[6])
                    query_left = query_left_bp(tokens[7])
                    if raw_strand == "+":
                        cons_start, cons_end = int(tokens[11]), int(tokens[12])
                        cons_left = consensus_left_bp(tokens[13])
                    else:
                        cons_left = consensus_left_bp(tokens[11])
                        cons_end, cons_start = int(tokens[12]), int(tokens[13])
                    rmsk_instance_id = tokens[14]
                    if not re.fullmatch(r"[0-9]+", rmsk_instance_id):
                        raise ValueError("expected a digits-only ID token")
                    rmsk_class, separator, rmsk_family = tokens[10].partition("/")
                    # Project class-only tokens into family using the UCSC convention.
                    if not separator:
                        rmsk_family = rmsk_class
                    if not rmsk_class or not rmsk_family:
                        raise ValueError("expected a class or class/family token")
                except ValueError as error:
                    raise ValueError(
                        f"{path}: line {line_number}: {error}; text={line.rstrip()!r}"
                    ) from error
                source_row_number += 1
                yield dict(zip(FIELDS, (
                    source_row_number, sw_score, *percentages, tokens[4], start, end,
                    query_left, raw_strand, "+" if raw_strand == "+" else "-",
                    tokens[9], tokens[10], rmsk_class, rmsk_family, cons_start,
                    cons_end, cons_left, rmsk_instance_id, len(tokens) == 16,
                )))
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        location = f"{path}: after line {line_number}" if line_number else str(path)
        raise ValueError(f"{location}: {error}") from error


class RecordStats:
    """Accumulate row totals and contig membership for each .out ID."""

    def __init__(self):
        self.records = 0
        self.starred_rows = 0
        self.id_contigs = {}
        self.spanning_ids = set()

    def add(self, record):
        self.records += 1
        self.starred_rows += record["rmsk_overlap_flag"]
        rmsk_instance_id = int(record["rmsk_instance_id"])
        chrom = sys.intern(record["chrom"])
        if self.id_contigs.setdefault(rmsk_instance_id, chrom) != chrom:
            self.spanning_ids.add(rmsk_instance_id)

    def summary(self):
        return {
            "records": self.records,
            "distinct_ids": len(self.id_contigs),
            "ids_spanning_contigs": len(self.spanning_ids),
            "starred_rows": self.starred_rows,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    count = commands.add_parser("count")
    count.add_argument("path", type=Path)
    head = commands.add_parser("head")
    head.add_argument("path", type=Path)
    head.add_argument("n", type=int)
    args = parser.parse_args()
    if args.command == "count":
        stats = RecordStats()
        for record in iter_records(args.path):
            stats.add(record)
        print(" ".join(f"{key}={value}" for key, value in stats.summary().items()))
    else:
        if args.n < 0:
            parser.error("N must be nonnegative")
        writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
        writer.writerow(FIELDS)
        for record in islice(iter_records(args.path), args.n):
            writer.writerow(int(record[key]) if isinstance(record[key], bool)
                            else record[key] for key in FIELDS)


if __name__ == "__main__":
    main()
