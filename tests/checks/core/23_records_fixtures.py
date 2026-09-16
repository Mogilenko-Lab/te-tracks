#!/usr/bin/env python3
"""Exercise record and universe gates with hand-authored source fixtures."""

import contextlib
import gzip
import io
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pyarrow.parquet as pq

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/lib"))
from records import SCHEMA, read_tsv, require
sys.path.insert(0, str(ROOT / "src/lib"))
from build_records import build_records, validate_records
from build_universes import build_universes


FIXTURES = ROOT / "tests/fixtures/records"
require("tables/rmsk_records.parquet", "tables/universe_summary.tsv")


def expect_failure(action, *messages):
    try:
        action()
    except ValueError as error:
        for message in messages:
            assert message in str(error), (message, str(error))
    else:
        raise AssertionError(f"accepted invalid fixture: {messages}")


with TemporaryDirectory(prefix="te-tracks-records-") as directory:
    scratch = Path(directory)
    source = scratch / "source"
    source.mkdir()
    for original, target in (("records.out", "records.out.gz"), ("rmsk.tsv", "rmsk.txt.gz")):
        with gzip.open(source / target, "wb") as stream:
            stream.write((FIXTURES / original).read_bytes())
    tables = scratch / "tables"
    with contextlib.redirect_stdout(io.StringIO()):
        build_records(source / "records.out.gz", source / "rmsk.txt.gz",
                      FIXTURES / "chrom.sizes", tables)
        build_universes(scratch, FIXTURES / "classes.tsv")
    expected = read_tsv(FIXTURES / "expected_records.tsv", SCHEMA)
    assert read_tsv(tables / "rmsk_records.tsv.gz", SCHEMA).equals(expected)
    assert pq.read_table(tables / "rmsk_records.parquet").cast(SCHEMA).equals(expected)
    with gzip.open(tables / "rmsk_records.tsv.gz", "rb") as stream:
        assert stream.read() == (FIXTURES / "expected_records.tsv").read_bytes()
    with gzip.open(tables / "rmsk_instance_members.tsv.gz", "rb") as stream:
        assert stream.read() == (FIXTURES / "expected_instances.tsv").read_bytes()
    assert (tables / "universe_summary.tsv").read_bytes() == (FIXTURES / "expected_universes.tsv").read_bytes()
    with gzip.open(tables / "universe_members.tsv.gz", "rt") as stream:
        members = stream.read().splitlines()
    assert "interspersed\tA|chr2:10-20|+\tfalse" in members
    assert "compat_tetranscripts_mm39\tA|chr2:10-20|+\tfalse" not in members
    for name in ("interspersed", "interspersed_plus_satellites"):
        for key in ("Mystery|chr10:5-9|+", "Maybe|chr2:70-74|+", "Unassigned|chr2:80-84|+"):
            assert f"{name}\t{key}\ttrue" in members
    for filename, message, offender in (
        ("duplicate.out", "exact duplicate key", "Duplicate"),
        ("beyond_end.out", "outside contig bounds", "BeyondEnd"),
        ("missing_chrom.out", "absent from chrom.sizes", "chrMissing"),
        ("spanning_instance.out", "instance spans multiple contigs", "007"),
        ("invalid_name.out", "invalid rmsk_name", "Bad|Name"),
        ("invalid_chrom.out", "invalid chrom", "chr:Bad"),
    ):
        expect_failure(lambda: build_records(FIXTURES / filename, FIXTURES / "rmsk.tsv",
                                             FIXTURES / "chrom.sizes", scratch / "failed"),
                       message, offender)
    for column, value in (("rmsk_name", "Bad Name"), ("chrom", "chr Bad")):
        malformed = expected.to_pandas()
        malformed.loc[0, column] = value
        expect_failure(lambda: validate_records(malformed, {"chr2": 100, "chr10": 100}),
                       f"invalid {column}", value)
    original_table = (FIXTURES / "rmsk.tsv").read_text().splitlines(keepends=True)
    for label, lines, message, offender in (
        ("duplicate", original_table + original_table[:1], "UCSC exact duplicate key", "'A'"),
        ("missing", original_table[1:], "UCSC join requires a 1:1 match", "'A'"),
        ("extra", original_table + [(FIXTURES / "unreviewed.tsv").read_text()],
         "UCSC join requires a 1:1 match", "NovelName"),
        ("disagree", (FIXTURES / "disagree.tsv").read_text().splitlines(keepends=True),
         "UCSC rmsk_family disagreement", "Split"),
    ):
        altered = scratch / f"{label}.tsv"
        altered.write_text("".join(lines))
        expect_failure(lambda: build_records(FIXTURES / "records.out", altered,
                                             FIXTURES / "chrom.sizes", scratch / "failed"),
                       message, offender)
    unknown = scratch / "unreviewed"
    with contextlib.redirect_stdout(io.StringIO()):
        build_records(FIXTURES / "unreviewed.out", FIXTURES / "unreviewed.tsv",
                      FIXTURES / "chrom.sizes", unknown / "tables")
    expect_failure(lambda: build_universes(unknown, FIXTURES / "classes.tsv"),
                   "class set gate", "Novel")
    assert not (unknown / "universes.json").exists()
    assert not (unknown / "tables/universe_members.tsv.gz").exists()
print("hand-authored records, collisions, text IDs, signed fields, instances, bounds, joins, class sets and tRNA-family rules pass")
