"""Load phase 2 artifacts against independently authored test schemas."""

import os
from pathlib import Path

import pyarrow as pa
import pyarrow.csv as pacsv


ROOT = Path(__file__).resolve().parents[2]
BUILD = Path(os.environ.get(
    "TE_TRACKS_REFROOT", "/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot"
)) / "te_mm39/build"
SCHEMA = pa.schema([
    ("rmsk_record_id", pa.string()), ("chrom", pa.string()),
    ("start_1", pa.int64()), ("end_1", pa.int64()), ("strand", pa.string()),
    ("rmsk_name", pa.string()), ("rmsk_family", pa.string()), ("rmsk_class", pa.string()),
    ("rmsk_instance_id", pa.string()), ("sw_score", pa.int64()),
    ("divergence_pct", pa.float64()), ("deletion_pct", pa.float64()),
    ("insertion_pct", pa.float64()), ("length_bp", pa.int64()),
    ("consensus_start_1", pa.int64()), ("consensus_end_1", pa.int64()),
    ("consensus_left_bp", pa.int64()), ("query_left_bp", pa.int64()),
    ("rmsk_overlap_flag", pa.bool_()), ("rmsk_class_family", pa.string()),
    ("ucsc_rep_start", pa.int64()), ("ucsc_rep_end", pa.int64()),
    ("ucsc_rep_left", pa.int64()), ("source_row_number", pa.int64()),
])
KEY = ["chrom", "start_1", "end_1", "strand", "rmsk_name"]
TRIPLE = ["rmsk_name", "rmsk_family", "rmsk_class"]


def require(*paths):
    if any(not (BUILD / path).is_file() for path in paths):
        print("unsupported: run build.sh first")
        raise SystemExit(3)


def read_tsv(path, schema):
    table = pacsv.read_csv(
        path, parse_options=pacsv.ParseOptions(delimiter="\t", quote_char=False),
        convert_options=pacsv.ConvertOptions(
            column_types=schema, null_values=[], strings_can_be_null=False,
            true_values=["true"], false_values=["false"],
        ),
    )
    assert table.schema.equals(schema, check_metadata=False), (path, table.schema, schema)
    assert all(column.null_count == 0 for column in table.columns), path
    return table
