#!/usr/bin/env python3
"""Exercise export identities and failure gates with hand-authored expected bytes."""

import contextlib
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/lib"))
from records import SCHEMA, require
sys.path.insert(0, str(ROOT / "src/lib"))
from build_exports import build_exports


FIXTURES = ROOT / "tests/fixtures/exports"
FILES = ["record.bed", "subfamily.bed", "family.bed", "record.gtf", "subfamily.gtf",
         "subfamily.saf", "taxonomy_triple.saf"]
require(*(f"exports/ucsc/interspersed/full/{filename}" for filename in FILES))


def expect_failure(action, *messages):
    try:
        action()
    except ValueError as error:
        for message in messages:
            assert message in str(error), (message, str(error))
    else:
        raise AssertionError(f"accepted invalid export fixture: {messages}")


with TemporaryDirectory(prefix="te-tracks-exports-") as directory:
    scratch = Path(directory)
    tables = scratch / "tables"
    tables.mkdir()
    records = pd.read_csv(FIXTURES / "records.tsv", sep="\t", keep_default_na=False,
                          dtype={"rmsk_instance_id": str})
    for field in SCHEMA:
        if field.name not in records:
            records[field.name] = (False if pa.types.is_boolean(field.type) else
                                   "LINE/L1" if pa.types.is_string(field.type) else 0)
    records["length_bp"] = records["end_1"] - records["start_1"] + 1
    records["source_row_number"] = range(1, len(records) + 1)

    def write_records(frame):
        pq.write_table(pa.Table.from_pandas(frame[SCHEMA.names], schema=SCHEMA,
                                            preserve_index=False), tables / "rmsk_records.parquet")

    write_records(records)
    taxonomy = (FIXTURES / "taxonomy.tsv").read_bytes()
    (tables / "taxonomy_canonical.tsv").write_bytes(taxonomy)
    membership = (FIXTURES / "universe_members.tsv").read_bytes()

    def write_members(content):
        with gzip.open(tables / "universe_members.tsv.gz", "wb") as stream:
            stream.write(content)

    write_members(membership)
    definitions = (FIXTURES / "universes.json").read_bytes()
    (scratch / "universes.json").write_bytes(definitions)
    completed = subprocess.run(["bash", str(ROOT / "src/30_build_exports.sh"), str(scratch),
                                str(ROOT / "config/mm39.env")], capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    exports = scratch / "exports/ucsc/interspersed/full"
    for filename in FILES:
        assert (exports / filename).read_bytes() == (FIXTURES / "expected" / filename).read_bytes(), filename
    with gzip.open(tables / "export_feature_members.tsv.gz", "rb") as stream:
        assert stream.read() == (FIXTURES / "expected/export_feature_members.tsv").read_bytes()
    bed = pd.read_csv(exports / "record.bed", sep="\t", header=None)
    duplicates = bed.loc[bed[0].eq("chr2") & bed[1].eq(9) & bed[2].eq(20)]
    assert set(duplicates[3]) == {"A|chr2:10-20|+", "B|chr2:10-20|+"}
    attributes = [dict(re.findall(r'(\w+) "([^"]*)";', line.split("\t")[8]))
                  for line in (exports / "record.gtf").read_text().splitlines()]
    assert [row["instance_id"] for row in attributes if row["gene_id"] == "A"] == ["I|mm39|007"] * 2
    for filename in ("record.gtf", "subfamily.gtf"):
        assert 'family_id "unresolved_family_Mystery";' in (exports / filename).read_text()
    assert "DNA/unresolved_family_Mystery" in (exports / "family.bed").read_text()
    assert "Mystery:unresolved_family_Mystery:DNA" in (exports / "taxonomy_triple.saf").read_text()
    inventory = pd.read_csv(tables / "exports.tsv", sep="\t")
    assert len(inventory) == 7
    for row in inventory.itertuples(index=False):
        assert row.rows == 5
        assert hashlib.sha256((scratch / row.export_path).read_bytes()).hexdigest() == row.sha256
        assert row.distinct_features == {"record": 5, "subfamily": 4, "family": 3,
                                         "taxonomy_triple": 4}[row.feature_level]
    before = {path: path.read_bytes() for path in [*exports.iterdir(), tables / "exports.tsv",
                                                tables / "export_feature_members.tsv.gz"]}
    with contextlib.redirect_stdout(io.StringIO()):
        build_exports(scratch, "mm39")
    assert all(path.read_bytes() == content for path, content in before.items())
    for character in [" ", "\t", "\n", "\r", ",", "#", "~", "%", ";", '"', "'", "\\", "|", ":", "/"]:
        malformed = records.copy()
        offender = f"Bad{character}Name"
        malformed.loc[0, "rmsk_name"] = offender
        write_records(malformed)
        expect_failure(lambda: build_exports(scratch, "mm39"), repr(offender), "subfamily.bed")
    for column, offender, filename in (
        ("chrom", "chr/Bad", "record.bed"),
        ("rmsk_record_id", "Bad#ID", "record.bed"),
        ("rmsk_family", "Bad;Family", "record.gtf"),
        ("rmsk_class", "Bad:Class", "record.gtf"),
        ("rmsk_instance_id", "00:7", "record.gtf"),
    ):
        malformed = records.copy()
        malformed.loc[0, column] = offender
        write_records(malformed)
        if column == "rmsk_record_id":
            write_members(membership.replace(b"A|chr2:30-35|-", offender.encode()))
        expect_failure(lambda: build_exports(scratch, "mm39"), repr(offender), filename)
        write_members(membership)
    write_records(records)
    for rank in ("class", "family"):
        malformed = pd.read_csv(io.BytesIO(taxonomy), sep="\t", keep_default_na=False)
        malformed.loc[malformed["rmsk_name"].eq("A"), f"canonical_{rank}"] = "Bad/Label"
        malformed.to_csv(tables / "taxonomy_canonical.tsv", sep="\t", index=False)
        expect_failure(lambda: build_exports(scratch, "mm39"), "Bad/Label", "family.bed")
    for rank in ("class", "family"):
        for offender in ("unresolved_family_U", "unresolved_class_U", "unresolved_U"):
            malformed = pd.read_csv(io.BytesIO(taxonomy), sep="\t", keep_default_na=False)
            malformed.loc[malformed["rmsk_name"].eq("A"), f"canonical_{rank}"] = offender
            malformed.to_csv(tables / "taxonomy_canonical.tsv", sep="\t", index=False)
            expect_failure(lambda: build_exports(scratch, "mm39"),
                           f"reserved canonical {rank} token", repr(offender), "'A'")
    (tables / "taxonomy_canonical.tsv").write_bytes(taxonomy)
    write_members(membership + b"interspersed\tA|chr2:30-35|-\tfalse\n")
    expect_failure(lambda: build_exports(scratch, "mm39"), "unique record IDs")
    write_members(membership + b"interspersed\tMissing|chr2:1-2|+\tfalse\n")
    expect_failure(lambda: build_exports(scratch, "mm39"), "absent from records", "Missing")
    write_members(membership)
    malformed = json.loads(definitions)
    malformed["default_universe"] = "satellites"
    (scratch / "universes.json").write_text(json.dumps(malformed))
    expect_failure(lambda: build_exports(scratch, "mm39"), "default universe")
print("hand-authored export bytes, membership selection, unresolved ranks, coordinate duplicates, "
      "shared instances, deterministic rebuild and identifier gates pass")
