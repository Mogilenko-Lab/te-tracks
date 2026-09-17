"""Create tiny complete mm39 builds through the production manifest and export writers."""

from contextlib import contextmanager, redirect_stdout
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/lib"))
import build_exports as exporter
from build_taxonomy import build_taxonomy
from build_universes import DEFINITIONS
import contigs
from manifest import write_manifest
from records_io import RECORD_SCHEMA, write_tsv


@contextmanager
def export_roster(added_export):
    """Extend the fixture writer and namespace roster for one complete build."""
    if not added_export:
        yield
        return
    jobs = tuple((universe, files + (("record_extra.bed", "record"),)
                  if universe == "all_rmsk" else files) for universe, files in exporter.EXPORT_JOBS)
    contracts = {**exporter.EXPORT_CONTRACTS, "record_extra.bed": exporter.EXPORT_CONTRACTS["record.bed"]}
    original = exporter.export_universe

    def export_universe(build_dir, genome, universe, export_set, registration):
        base = tuple(job for job in export_set if job[0] != "record_extra.bed")
        rows = original(build_dir, genome, universe, base, registration)
        if base != export_set:
            row = next(row for row in rows if row["export_path"].endswith("/record.bed"))
            extra_path = str(Path(row["export_path"]).with_name("record_extra.bed"))
            (build_dir / extra_path).write_bytes((build_dir / row["export_path"]).read_bytes())
            rows.append({**row, "export_path": extra_path})
        return rows

    with patch.multiple(exporter, EXPORT_JOBS=jobs, EXPORT_CONTRACTS=contracts,
                        export_universe=export_universe), patch.object(contigs, "EXPORT_JOBS", jobs):
        yield


def make_build(family, note="first", added_export=False):
    with export_roster(added_export):
        return _make_build(family, note)


def _make_build(family, note):
    family = Path(family)
    staging = family / ".staging"
    staging.mkdir(parents=True, exist_ok=True)
    build = Path(tempfile.mkdtemp(prefix="fixture-", dir=staging))
    source, tables = build / "source", build / "tables"
    source.mkdir()
    tables.mkdir()
    files = {
        "rmsk_out": ("mm39.fa.out.gz", gzip.compress(
            b"100 0.0 0.0 0.0 chr1 2 5 (95) + Example LINE/L1 1 4 (0) 007\n", mtime=0)),
        "rmsk_table": ("rmsk.txt.gz", gzip.compress(
            b"0\t100\t0\t0\t0\tchr1\t1\t5\t-95\t+\tExample\tLINE\tL1\t0\t4\t0\t0\n", mtime=0)),
        "chromAlias": ("mm39.chromAlias.txt", b"# ucsc assembly ensembl genbank refseq\nchr1 1 1 CM1.1 NC1.1\n"),
        "chrom_sizes": ("mm39.chrom.sizes", b"chr1\t100\n"),
    }
    metadata = {
        "genome": "mm39", "assembly": "GRCm39", "rm_version": "fixture",
        "rm_library": "fixture", "rm_run_evidence": "synthetic publication fixture",
        "rmsk_out_profile": "rm_out_v1",
        "declared_assembly": {"genome_fa_url": "https://example.invalid/mm39.fa.gz",
                              "genome_fa_md5": "0" * 32, "status": "declared"}, "sources": {},
    }
    config = {"GENOME": "mm39", "ASSEMBLY": "GRCm39", "RM_VERSION": "fixture",
              "RM_LIBRARY": "fixture", "RM_RUN_EVIDENCE": "synthetic publication fixture",
              "RMSK_OUT_PROFILE": "rm_out_v1", "GENOME_FA_URL": "https://example.invalid/mm39.fa.gz",
              "GENOME_FA_MD5": "0" * 32}
    prefixes = {"rmsk_out": "RMSK_OUT", "rmsk_table": "RMSK_TABLE", "chromAlias": "CHROMALIAS",
                "chrom_sizes": "CHROM_SIZES"}
    for role, (name, content) in files.items():
        (source / name).write_bytes(content)
        md5 = hashlib.md5(content).hexdigest()
        url = "https://example.invalid/" + name
        metadata["sources"][role] = {"url": url, "md5": md5, "bytes": len(content)}
        config[prefixes[role] + "_URL"] = url
        config[prefixes[role] + "_MD5"] = md5
    (source / "SOURCES.json").write_text(json.dumps(metadata, indent=2) + "\n")
    config_path = family.parent / "fixture.env"
    config_path.write_text("".join(f"{key}='{value}'\n" for key, value in config.items()))
    row = {field.name: ("" if pa.types.is_string(field.type) else False
                       if pa.types.is_boolean(field.type) else 0) for field in RECORD_SCHEMA}
    row.update(rmsk_record_id="Example|chr1:2-5|+", chrom="chr1", start_1=2, end_1=5,
               strand="+", rmsk_name="Example", rmsk_family="L1", rmsk_class="LINE",
               rmsk_instance_id="007", sw_score=100, length_bp=4, consensus_start_1=1,
               consensus_end_1=4, query_left_bp=95, rmsk_class_family="LINE/L1",
               ucsc_rep_end=4, source_row_number=1)
    records = pd.DataFrame([row])
    table = pa.Table.from_pylist([row], schema=RECORD_SCHEMA)
    pq.write_table(table, tables / "rmsk_records.parquet", compression="snappy", version="2.6")
    write_tsv(records, tables / "rmsk_records.tsv.gz")
    write_tsv(records[["rmsk_instance_id", "rmsk_record_id"]], tables / "rmsk_instance_members.tsv.gz")
    write_tsv(pd.DataFrame([{"rmsk_name": "Example", "rmsk_family": "L1", "rmsk_class": "LINE",
                            "record_count": 1, "instance_count": 1, "record_length_sum_bp": 4}]),
              tables / "rmsk_taxonomy.tsv")
    (build / "universes.json").write_text(json.dumps(DEFINITIONS, indent=2, ensure_ascii=False) + "\n")
    write_tsv(pd.DataFrame([{"universe_name": "interspersed", "rmsk_record_id": row["rmsk_record_id"],
                            "provisional": False}]), tables / "universe_members.tsv.gz")
    write_tsv(pd.DataFrame([{"universe_name": "all_rmsk", "records": 1, "names": 1,
                            "triples": 1, "length_sum_bp": 4}]), tables / "universe_summary.tsv")
    with redirect_stdout(io.StringIO()):
        build_taxonomy(build)
        exporter.build_exports(build, "mm39", jobs=exporter.EXPORT_JOBS)
        contigs.build_namespaces(build, "mm39")
    (source / "qualification.md").write_text(f"synthetic qualification: {note}\n")
    write_manifest(build, config_path, argv=["publication fixture"])
    return build
