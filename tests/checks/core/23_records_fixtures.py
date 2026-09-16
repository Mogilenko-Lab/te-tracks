#!/usr/bin/env python3
"""Exercise record and universe gates with hand-authored source fixtures."""

import contextlib
import gzip
import io
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/lib"))
from records import SCHEMA, TAXONOMY_SCHEMA, read_tsv, require
sys.path.insert(0, str(ROOT / "src/lib"))
from build_records import build_records, validate_records
from build_universes import build_universes, check_class_set


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
    reviewed = pd.read_csv(ROOT / "config/mm39.classes.tsv", sep="\t", dtype=str,
                           keep_default_na=False)
    for disposition, message in (
        ("interspersed", "interspersed disposition gate: disposition_without_predicate=['Simple_repeat']"),
        ("novel_disposition", "unknown class disposition"),
    ):
        altered_classes = reviewed.copy()
        altered_classes.loc[altered_classes["rmsk_class"].eq("Simple_repeat"), "disposition"] = disposition
        class_set = scratch / f"{disposition}.classes.tsv"
        altered_classes.to_csv(class_set, sep="\t", index=False)
        offender = "Simple_repeat" if disposition == "interspersed" else disposition
        expect_failure(lambda: check_class_set(reviewed, class_set), message, offender)
    fixture_classes = pd.read_csv(FIXTURES / "classes.tsv", sep="\t", dtype=str,
                                 keep_default_na=False)
    altered_classes = fixture_classes.copy()
    altered_classes.loc[altered_classes["rmsk_class"].eq("LINE"), "disposition"] = "structural_rna"
    class_set = scratch / "structural_rna.classes.tsv"
    altered_classes.to_csv(class_set, sep="\t", index=False)
    expect_failure(lambda: check_class_set(fixture_classes, class_set),
                   "interspersed disposition gate", "predicate_without_disposition=['LINE']")
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
    assert read_tsv(tables / "rmsk_taxonomy.tsv", TAXONOMY_SCHEMA).equals(
        read_tsv(FIXTURES / "expected_taxonomy.tsv", TAXONOMY_SCHEMA))
    assert (tables / "rmsk_taxonomy.tsv").read_bytes() == (FIXTURES / "expected_taxonomy.tsv").read_bytes()
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
    identity_sizes = scratch / "identity.chrom.sizes"
    identity_sizes.write_text((FIXTURES / "chrom.sizes").read_text() + "chr:Bad\t100\n")
    for filename, table, message, offender in (
        ("duplicate.out", "rmsk.tsv", "exact duplicate key", "Duplicate"),
        ("beyond_end.out", "beyond_end.tsv", "outside contig bounds", "BeyondEnd"),
        ("missing_chrom.out", "missing_chrom.tsv", "absent from chrom.sizes", "chrMissing"),
        ("spanning_instance.out", "spanning_instance.tsv", "instance spans multiple contigs", "007"),
        ("invalid_name.out", "invalid_name.tsv", "invalid rmsk_name", "Bad|Name"),
        ("invalid_chrom.out", "invalid_chrom.tsv", "invalid chrom", "chr:Bad"),
        ("colon_name.out", "colon_name.tsv", "invalid rmsk_name for record identity", "Bad:Name"),
        ("slash_name.out", "slash_name.tsv", "invalid rmsk_name for record identity", "Bad/Name"),
    ):
        sizes = identity_sizes if filename == "invalid_chrom.out" else FIXTURES / "chrom.sizes"
        expect_failure(lambda: build_records(FIXTURES / filename, FIXTURES / table,
                                             sizes, scratch / "failed"),
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
