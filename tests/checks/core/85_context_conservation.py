#!/usr/bin/env python3
"""Compare complete context roll-ups with independently built mask conservation."""

import os
from pathlib import Path
import sys

import pandas as pd

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/lib"))
from transcript_context import RECORD_COLUMNS

child = Path(os.environ["TE_TRACKS_REFROOT"]) / "te_mm39_gene/build"
if not child.is_dir():
    print("gene child build is absent")
    raise SystemExit(3)
coverage = pd.read_csv(child / "tables/gene_annotation_coverage.tsv", sep="\t")
annotated = set(coverage.loc[coverage.annotated, "chrom_ucsc"])
context = pd.read_csv(child / "tables/record_context.tsv.gz", sep="\t", keep_default_na=False,
                      dtype={**dict.fromkeys(RECORD_COLUMNS, str), "length_bp": "int64"}, chunksize=100_000)
status = pd.read_csv(child / "tables/exon_subtraction_status.tsv", sep="\t", chunksize=100_000)
count, absent = 0, 0
for rows in context:
    subtraction = next(status)
    assert list(rows) == RECORD_COLUMNS
    assert rows.rmsk_record_id.equals(subtraction.rmsk_record_id)
    assert rows.length_bp.equals(subtraction.retained_bp + subtraction.removed_bp)
    chroms = rows.rmsk_record_id.str.rsplit("|", n=2).str[1].str.split(":").str[0]
    has_annotation = chroms.isin(annotated)
    assert rows.annotated.eq("true").equals(has_annotation)
    assert rows.loc[~has_annotation, RECORD_COLUMNS[3:]].eq("NA").all().all()
    values = rows.loc[has_annotation]
    assert pd.to_numeric(values.exon_bp_any).equals(subtraction.loc[has_annotation, "removed_bp"])
    assert pd.to_numeric(values.body_frac_max).between(0, 1).all()
    assert pd.to_numeric(values.body_genes_same).ge(0).all()
    assert pd.to_numeric(values.body_genes_opposite).ge(0).all()
    assert pd.to_numeric(values.nearest_exon_edge_bp).ge(0).all()
    count += len(rows)
    absent += (~has_annotation).sum()
assert next(status, None) is None
assert count == 5_320_771 and absent == 2638
print(f"{count} context rows conserve parent lengths and mask exon bases; {absent} unannotated records retain NA geometry")
