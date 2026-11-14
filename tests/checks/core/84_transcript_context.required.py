#!/usr/bin/env python3
"""Check hand-authored transcript geometry, policy identity and legacy payload bytes."""

from contextlib import redirect_stdout
import csv
import gzip
import io
import os
from pathlib import Path
import random
import sys
import tempfile

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/lib"))
from build_taxonomy import build_taxonomy
from build_universes import DEFINITIONS
from gene_child import build_child, policy_bundle, validate_policy
from manifest import config_values
from records_io import RECORD_SCHEMA, write_tsv
from transcript_context import Context, PAIR_COLUMNS, RECORD_COLUMNS, verify_context, Intervals, Points

FIXTURE = ROOT / "tests/fixtures/context"
policy = policy_bundle(config_values(ROOT / "config/mm39_gene.env"))
validate_policy(policy)
assert policy["context_capability"] == "transcript_geometry_v1"
for key in ("start_envelope_upstream_bp", "start_envelope_downstream_bp", "end_envelope_downstream_bp", "tie_rule"):
    try:
        validate_policy({**policy, key: "changed"})
    except ValueError:
        pass
    else:
        raise AssertionError(key)


def read(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


scratch = Path(os.environ["TE_TRACKS_REFROOT"]) / "tmp"
scratch.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="context-", dir=scratch) as temporary:
    base = Path(temporary)
    parent, child, old = (base / name for name in ("parent", "child", "old"))
    for path in (parent, child, old):
        (path / "tables").mkdir(parents=True)
    aliases = pd.read_csv(FIXTURE / "contig_aliases.tsv", sep="\t")
    for path in (child, old):
        write_tsv(aliases, path / "tables/contig_aliases.tsv")
    import json
    (parent / "universes.json").write_text(json.dumps(DEFINITIONS))
    records = pd.read_csv(FIXTURE / "records.tsv", sep="\t")
    last = records.loc[records.rmsk_record_id == "contig_last"].iloc[0]
    contig_length = int(aliases.set_index("chrom_ucsc").loc[last.chrom, "length_bp"])
    assert last.start_1 == last.end_1 == contig_length
    records["length_bp"] = records.end_1 - records.start_1 + 1
    records["rmsk_name"], records["rmsk_class"], records["rmsk_family"] = "Example", "LINE", "L1"
    for field in RECORD_SCHEMA:
        if field.name not in records:
            records[field.name] = "" if pa.types.is_string(field.type) else False if pa.types.is_boolean(field.type) else 0
    pq.write_table(pa.Table.from_pandas(records, preserve_index=False), parent / "tables/rmsk_records.parquet")
    write_tsv(pd.DataFrame([dict(rmsk_name="Example", rmsk_family="L1", rmsk_class="LINE",
                                record_count=len(records), instance_count=len(records), record_length_sum_bp=records.length_bp.sum())]),
              parent / "tables/rmsk_taxonomy.tsv")
    gtf = base / "annotation.gtf.gz"
    gtf.write_bytes(gzip.compress((FIXTURE / "annotation.gtf").read_bytes(), mtime=0))
    with redirect_stdout(io.StringIO()):
        build_taxonomy(parent)
        build_child(parent, old, gtf)
        build_child(parent, child, gtf, policy=policy)
    for path in old.rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (child / path.relative_to(old)).read_bytes(), path
    with gzip.open(child / "tables/record_context.tsv.gz", "rt") as stream:
        assert list(csv.DictReader(stream, delimiter="\t")) == read(FIXTURE / "record_context.tsv")
    with gzip.open(child / "tables/record_transcript_context.tsv.gz", "rt") as stream:
        pairs = list(csv.DictReader(stream, delimiter="\t"))
    expected = read(FIXTURE / "pair_geometry.tsv")
    assert [{k: row[k] for k in expected[0]} for row in pairs] == expected
    for row in pairs:
        suffix = row["transcript_id"][1:]
        assert row["gene_id"] == "g" + ("G.1" if suffix == "H.1" else suffix)
        assert row["ensembl_canonical"] == row["mrna_start_nf"] == ("true" if suffix == "A.1" else "false")
        assert row["gene_type"] == row["transcript_type"] == ("protein_coding" if suffix in ("A.1", "B.1") else "lncRNA")
    verify_context(child, parent, gtf, policy)
    path = child / "tables/record_context.tsv.gz"
    original = path.read_bytes()
    path.write_bytes(gzip.compress(gzip.decompress(original).replace(b"0.55", b"0.50"), mtime=0))
    try:
        verify_context(child, parent, gtf, policy)
    except ValueError as error:
        assert "record context geometry differs" in str(error)
    else:
        raise AssertionError("changed context accepted")
    path.write_bytes(original)
    pair_path = child / "tables/record_transcript_context.tsv.gz"
    original_pairs = pair_path.read_bytes()
    payload = gzip.decompress(original_pairs)
    pair_path.write_bytes(gzip.compress(payload.replace(b"\t10\t0\t10\t0\t", b"\t9\t1\t9\t0\t", 1), mtime=0))
    try:
        verify_context(child, parent, gtf, policy)
    except ValueError as error:
        assert "transcript context geometry differs" in str(error)
    else:
        raise AssertionError("changed pair accepted")
    pair_path.write_bytes(original_pairs)
    context = Context(gtf, child / "tables/contig_aliases.tsv", policy)
    baseline_rows = list(context.rows(records))
    lines = (FIXTURE / "annotation.gtf").read_text().splitlines(True)
    random.Random(17).shuffle(lines)
    gtf.write_bytes(gzip.compress("".join(lines + lines).encode(), mtime=0))
    assert list(Context(gtf, child / "tables/contig_aliases.tsv", policy).rows(records)) == baseline_rows

rng = random.Random(37)
intervals = [(a, a + rng.randrange(1, 200), i) for i, a in enumerate(rng.choices(range(1, 1000), k=200))]
index = Intervals(intervals)
points = Points([(p, i) for a, b, i in intervals for p in (a, b)])
for _ in range(300):
    a = rng.randrange(1, 1200)
    b = a + rng.randrange(100)
    assert index.query(a, b) == {i for x, y, i in intervals if x <= b and y >= a}
    distances = [(max(a - p, p - b, 0), i) for x, y, i in intervals for p in (x, y)]
    best = min(d for d, i in distances)
    assert points.nearest(a, b) == (best, {i for d, i in distances if d == best})
print("31 hand-authored records, 36 pairs, strand/UTR/envelope/tie geometry, policy refusals, payload refusal, "
      "annotation order/duplicate invariance, independent index oracle and all legacy fixture bytes pass")
