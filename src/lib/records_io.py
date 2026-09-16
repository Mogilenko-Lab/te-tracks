"""Share explicit record types and deterministic TSV serialization."""

import csv
import gzip
import io
from contextlib import contextmanager

import pyarrow as pa


RECORD_SCHEMA = pa.schema([
    pa.field(name, dtype, nullable=False)
    for name, dtype in [
        ("rmsk_record_id", pa.string()), ("chrom", pa.string()),
        ("start_1", pa.int64()), ("end_1", pa.int64()),
        ("strand", pa.string()), ("rmsk_name", pa.string()),
        ("rmsk_family", pa.string()), ("rmsk_class", pa.string()),
        ("rmsk_instance_id", pa.string()), ("sw_score", pa.int64()),
        ("divergence_pct", pa.float64()), ("deletion_pct", pa.float64()),
        ("insertion_pct", pa.float64()), ("length_bp", pa.int64()),
        ("consensus_start_1", pa.int64()), ("consensus_end_1", pa.int64()),
        ("consensus_left_bp", pa.int64()), ("query_left_bp", pa.int64()),
        ("rmsk_overlap_flag", pa.bool_()), ("rmsk_class_family", pa.string()),
        ("ucsc_rep_start", pa.int64()), ("ucsc_rep_end", pa.int64()),
        ("ucsc_rep_left", pa.int64()), ("source_row_number", pa.int64()),
    ]
])
RECORD_KEY = ["chrom", "start_1", "end_1", "strand", "rmsk_name"]
TAXONOMY_KEY = ["rmsk_name", "rmsk_family", "rmsk_class"]


@contextmanager
def tsv_stream(path):
    """Write UTF-8 LF text with reproducible gzip headers where requested."""
    with open(path, "wb") as raw:
        if str(path).endswith(".gz"):
            with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0,
                               compresslevel=6) as compressed:
                with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as text:
                    yield text
        else:
            with io.TextIOWrapper(raw, encoding="utf-8", newline="") as text:
                yield text


def write_frame(frame, stream, header=True):
    """Serialize typed rows with lowercase booleans and literal text."""
    frame = frame.copy(deep=False)
    for name in frame.select_dtypes(include="bool"):
        frame[name] = frame[name].map({True: "true", False: "false"})
    frame.to_csv(stream, sep="\t", index=False, header=header, lineterminator="\n",
                 quoting=csv.QUOTE_NONE, chunksize=100_000)


def write_tsv(frame, path):
    with tsv_stream(path) as stream:
        write_frame(frame, stream)
