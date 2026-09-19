"""Measure the mm39 contracts and their independent reference evidence."""

from collections import Counter
import gzip
import hashlib
import json
import os
import re
import stat
import subprocess
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from .common import ACCEPTANCE, EXPECT, FAMILIES, REFROOT, ROOT, core_checks, digest, rows
from .oracles import gene_child_oracle, legacy_reconciliation


def source(core, child):
    for pin in rows(EXPECT / "source_pins.tsv"):
        archive = child if pin["path"].startswith("gencode.") else core
        path = archive / "source" / pin["path"].rsplit("/", 1)[-1]
        assert digest(path, pin["algorithm"]) == pin["digest"], f"retained source pin differs: {path}"
    report = (core / "source/qualification.md").read_text()
    measured = {}
    for line in report.splitlines():
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == 2 and cells[1].replace(",", "").isdigit():
            assert cells[0] not in measured
            measured[cells[0]] = int(cells[1].replace(",", ""))
    expected = {r["metric"]: int(r["value"]) for r in rows(EXPECT / "source_qualification.tsv")}
    assert measured == expected, ("source qualification", measured, expected)
    assert "Status: PASS." in report
    assert report == (ROOT / "docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md").read_text()
    provenance = json.loads((core / "source/dfam_interspersed_mm39_snapshot.provenance.json").read_text())
    identity = json.loads((core / "MANIFEST.json").read_text())["identity"]
    assert identity["build_sources"]["dfam_snapshot"]["fetch_finished"] == provenance["fetch_finished"]
    print("seven retained input pins; 5320771 source/browser matches; zero field disagreements; 4696900 source-wide IDs; Dfam fetch_finished equals retained provenance")


def records_universes(core, child):
    results = core_checks(core, child, "20_records_schema.py", "21_instances.py", "22_universes.py")
    frame = pq.read_table(core / "tables/rmsk_records.parquet", columns=[
        "chrom", "start_1", "end_1", "strand", "rmsk_name", "rmsk_family", "rmsk_class",
        "rmsk_instance_id", "consensus_start_1", "consensus_end_1", "rmsk_overlap_flag", "sw_score",
    ]).to_pandas()
    selected = frame.loc[frame.rmsk_class.isin(
        ["SINE", "LTR", "LINE", "DNA", "RC", "Retroposon", "Unknown", "Unspecified", "DNA?"])]
    groups = selected.groupby("rmsk_instance_id", sort=False)
    names = groups.rmsk_name.nunique()
    multi = names.index[names.gt(1)]
    overlapped = 0
    for _, group in frame.groupby("chrom", sort=False):
        starts, ends = group.start_1.to_numpy(), group.end_1.to_numpy()
        previous = np.r_[0, np.maximum.accumulate(ends)[:-1]]
        following = np.r_[starts[1:], np.iinfo(np.int64).max]
        overlapped += int(((previous >= starts) | (following <= ends)).sum())
    internal = set(frame.loc[frame.rmsk_name.str.endswith("-int"), "rmsk_instance_id"])
    ltr = set(frame.loc[frame.rmsk_class.eq("LTR") & ~frame.rmsk_name.str.endswith("-int"), "rmsk_instance_id"])
    observed = {
        "all_multi_record_instances": int(frame.groupby("rmsk_instance_id").size().gt(1).sum()),
        "interspersed_instances": len(groups),
        "interspersed_multi_record_instances": int(groups.size().gt(1).sum()),
        "interspersed_mixed_name_instances": len(multi),
        "interspersed_mixed_name_records": int(selected.rmsk_instance_id.isin(multi).sum()),
        "interspersed_mixed_strand_instances": int(groups.strand.nunique().gt(1).sum()),
        "all_overlapping_records": overlapped,
        "all_ltr_only_instances": len(ltr - internal),
        "l1_model_base_one_records": int((frame.rmsk_class.eq("LINE") & frame.rmsk_family.eq("L1") & frame.consensus_start_1.eq(1)).sum()),
        "interspersed_score_above_1000": int(selected.sw_score.gt(1000).sum()),
        "consensus_start_above_end": int(frame.consensus_start_1.gt(frame.consensus_end_1).sum()),
        "overlap_flag_true": int(frame.rmsk_overlap_flag.sum()),
    }
    expected = {r["metric"]: int(r["value"]) for r in rows(EXPECT / "record_census.tsv")}
    assert observed == expected, ("record census", observed, expected)
    print("; ".join(results) + "; record/instance limits " + json.dumps(observed, sort_keys=True))


def taxonomy(core, child):
    results = core_checks(core, child, "30_taxonomy_canonical.py", "31_taxonomy_dfam_agreement.py",
                          "32_taxonomy_rule_fixtures.py")
    print("18484 canonical names; 20 multi-label names independently agree with Dfam; taxonomy census and hand-authored rule/rollup fixtures pass; " + results[0])


def taxonomy_dfam(core, child):
    results = core_checks(core, child, "33_taxonomy_dfam_view.py", "34_dfam_rule_fixtures.py")
    expected = {"taxonomy_dfam.tsv": 1220, "taxonomy_dfam_models.tsv": 1263,
                "dfam_lineage_nodes.tsv": 300, "dfam_model_clades.tsv": 1278}
    for name, count in expected.items():
        assert len(rows(core / "tables" / name)) == count, name
    print("1220 names: exact=1047 part_model_set=147 missing=26; models=1263 lineage_nodes=300 clades=1278; table lines=1221/1264/301/1279; every metadata/rank cell and dfam_census metric pass; " + results[1])


def exports(core, child):
    results = core_checks(core, child, "40_exports_shape.py", "41_export_registration.py", "43_matrix_binding.py")
    inventory = rows(core / "tables/exports.tsv")
    assert len(inventory) == 27
    assert any(row["feature_level"] == "family" for row in inventory), "family export level absent"
    for row in inventory:
        if row["feature_level"] == "family":
            assert int(row["distinct_features"]) == 49, "canonical family export census"
    for namespace, total, catalog, profile in (
        ("ucsc", 4638043480, 332554184, 1616329134),
        ("ensembl", 4531250735, 316524255, 1604983782),
        ("gencode", 4637401144, 332461688, 1616260404),
    ):
        directory = core / "exports" / namespace
        assert sum(p.stat().st_size for p in directory.rglob("*") if p.is_file()) == total, namespace
        assert (directory / "all_rmsk/full/record.bed").stat().st_size == catalog, namespace
        assert (directory / "interspersed/full/record_starsolo.gtf").stat().st_size == profile, namespace
    assert (core / "tables/export_feature_members.tsv.gz").stat().st_size == 347526106
    print("27 exports; 3764949 interspersed rows, 1220 names, 49 canonical families; registrations=30119592+5320771; full coordinates, grammars, conservation and matrix binding pass; " + results[-1])


def record_profile(core, child):
    keys = ["gene_id", "transcript_id", "gene_name", "gene_type", "locus", "rmsk_name",
            "family_id", "class_id", "rmsk_family", "rmsk_class", "instance_id", "rmsk_record_id"]
    pattern = re.compile(" ".join(f'{key} "([^"\\s]+)";' for key in keys))
    aliases = rows(core / "tables/contig_aliases.tsv")
    summaries = []
    for namespace in ("ucsc", "ensembl", "gencode"):
        mapping = {r["chrom_" + namespace]: r["chrom_ucsc"] for r in aliases}
        features, contigs, count = set(), set(), 0
        with (core / f"exports/{namespace}/interspersed/full/record_starsolo.gtf").open() as stream:
            for line in stream:
                fields = line.rstrip("\n").split("\t")
                assert len(fields) == 9 and fields[1:3] == ["te-tracks", "exon"] and fields[7] == "."
                matched = pattern.fullmatch(fields[8])
                assert matched, (namespace, count, "twelve ordered attributes")
                values = dict(zip(keys, matched.groups()))
                chrom, start, end, strand = mapping[fields[0]], fields[3], fields[4], fields[6]
                name = values["rmsk_name"]
                alias = f"R|mm39|{name}|{chrom}|{start}|{end}|{strand}"
                assert values["gene_id"] == values["transcript_id"] == values["locus"] == alias
                assert values["gene_name"] == name and values["gene_type"] == "transposable_element"
                assert values["rmsk_record_id"] == f"{name}|{chrom}:{start}-{end}|{strand}"
                assert re.fullmatch(r"I\|mm39\|[0-9]+", values["instance_id"])
                assert alias not in features, (namespace, "duplicate gene_id", alias)
                features.add(alias)
                contigs.add(fields[0])
                count += 1
        assert (count, len(features), len(contigs)) == (3764949, 3764949, 59), namespace
        summaries.append(f"{namespace}=3764949 rows/genes, 59 contigs")
    print("; ".join(summaries) + "; twelve ordered attributes and record identities pass")


def namespaces(core, child):
    results = core_checks(core, child, "60_contig_aliases.py", "61_namespace_exports.py", "62_preflight.sh")
    print("61 injective aliases; 59 interspersed contigs; 27 sorted exports; all 18 renamed files independently regenerated; preflight gates pass; " + results[0])


def publication(core, child):
    pins = {r["family"]: r for r in rows(EXPECT / "identity.tsv")}
    summaries, discrepancies = [], []
    for family, archive in zip(FAMILIES, (core, child)):
        manifest = json.loads((archive / "MANIFEST.json").read_text())
        identity = manifest["identity"]
        encode = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
        build_id = hashlib.sha256(b"te-tracks-build-v1\n" + encode(identity)).hexdigest()
        catalog_id = hashlib.sha256(b"te-tracks-catalog-v1\n" + encode(identity["catalog"])).hexdigest()
        assert (archive / "BUILD_ID").read_text() == build_id + "\n"
        assert (archive / "CATALOG_ID").read_text() == catalog_id + "\n"
        assert catalog_id == pins[family]["CATALOG_ID"], "CATALOG_ID difference: stop for investigation"
        if build_id != pins[family]["BUILD_ID"]:
            discrepancies.append(f"{family} BUILD_ID differs from the development pin: {build_id}; equal CATALOG_ID: compare toolchain and payload; publish the host build with the in-container build recorded as its content witness")
        assert identity["rank_scheme_version"] == "rank_scheme_wicker_v1"
        assert len(identity["inventory"]) == int(pins[family]["inventory_entries"])
        assert len(identity["export_contracts"]) == int(pins[family]["export_contracts"])
        assert os.readlink(ACCEPTANCE / family / "current") == "archive/" + build_id
        assert not any((ACCEPTANCE / family / ".staging").iterdir())
        for path in [archive, *archive.rglob("*")]:
            assert stat.S_IMODE(path.stat().st_mode) == (0o555 if path.is_dir() else 0o444), path
        verified = subprocess.run([sys.executable, str(ROOT / "src/release.py"), "verify-current",
                                   "--root", str(ACCEPTANCE), "--family", family], capture_output=True, text=True)
        assert verified.returncode == 0 and verified.stdout.strip() == build_id, verified.stdout + verified.stderr
        development = REFROOT / family / "build"
        if development.is_dir():
            other_catalog = (development / "CATALOG_ID").read_text().strip()
            assert catalog_id == other_catalog, f"{family} CATALOG_ID difference against {development}: stop for investigation"
            table_paths = {p.relative_to(archive).as_posix() for p in (archive / "tables").rglob("*") if p.is_file()}
            other_paths = {p.relative_to(development).as_posix() for p in (development / "tables").rglob("*") if p.is_file()}
            differences = sorted(table_paths ^ other_paths)
            differences += [p for p in sorted(table_paths & other_paths) if digest(archive / p) != digest(development / p)]
            if differences:
                discrepancies.append(f"{family} development table digests differ: {differences}")
            if (development / "BUILD_ID").read_text().strip() != build_id:
                discrepancies.append(f"{family} BUILD_ID difference with equal CATALOG_ID: compare toolchain and payload; publish the host build with the in-container build recorded as its content witness")
            comparison = "live development comparison ran: tables and IDs equal" if not differences and (development / "BUILD_ID").read_text().strip() == build_id else "live development comparison ran: differs"
        else:
            comparison = f"live development comparison skipped: build absent at {development}"
        if family == "te_mm39":
            assert sum(r["bytes"] for r in identity["inventory"]) == 15301538537
            for path, size in {
                "tables/taxonomy_dfam.tsv": 780296, "tables/taxonomy_dfam_models.tsv": 577712,
                "tables/dfam_lineage_nodes.tsv": 75154, "tables/dfam_model_clades.tsv": 367180,
                "source/dfam_interspersed_mm39_snapshot.json.gz": 278952,
                "source/dfam_interspersed_mm39_snapshot.provenance.json": 921,
            }.items():
                assert (archive / path).stat().st_size == size, path
            assert set(identity["build_sources"]) == {"rmsk_out", "rmsk_table", "chromAlias", "chrom_sizes", "dfam_snapshot"}
            assert list(identity["catalog"]["sources"]) == ["rmsk_out"]
        else:
            assert sum(r["bytes"] for r in identity["inventory"]) == 2157717760
            assert identity["parent_build_id"] == (core / "BUILD_ID").read_text().strip()
            assert identity["parent_catalog_id"] == catalog_id
        summaries.append(f"{family} BUILD_ID={build_id} CATALOG_ID={catalog_id}; identity.tsv reproduction pins checked; {comparison}")
    assert not discrepancies, "\n".join(discrepancies)
    print("; ".join(summaries) + "; immutable modes, independent hashes and verify-current pass")


def gene_child(core, child):
    results = core_checks(core, child, "80_exon_subtraction.py")
    summaries = {r["universe_name"]: r for r in rows(EXPECT / "exon_subtraction_summary.tsv")}
    coverage = {r["chrom_ucsc"]: r for r in rows(child / "tables/gene_annotation_coverage.tsv")}
    unannotated = {chrom for chrom, row in coverage.items() if row["annotated"] == "false"}
    census = {name: Counter() for name in summaries}
    status_chunks = pd.read_csv(child / "tables/exon_subtraction_status.tsv", sep="\t", chunksize=100000)
    parquet = pq.ParquetFile(core / "tables/rmsk_records.parquet")
    batches = parquet.iter_batches(batch_size=100000, columns=["rmsk_record_id", "chrom", "rmsk_class", "rmsk_family"])
    for batch in batches:
        records = batch.to_pandas()
        status = next(status_chunks)
        assert records.rmsk_record_id.tolist() == status.rmsk_record_id.tolist()
        status = status.reset_index(drop=True)
        inter = records.rmsk_class.isin(["SINE", "LTR", "LINE", "DNA", "RC", "Retroposon", "Unknown", "Unspecified", "DNA?"])
        masks = {"all_rmsk": pd.Series(True, index=records.index), "interspersed": inter,
                 "compat_tetranscripts_mm39": (inter | records.rmsk_class.eq("Satellite")) & ~records.rmsk_family.str.startswith("tRNA")}
        for universe, mask in masks.items():
            selected = status.loc[mask]
            census[universe].update(selected.status.value_counts().to_dict())
            census[universe].update(records=len(selected), retained_records=int(selected.n_blocks.gt(0).sum()),
                blocks=int(selected.n_blocks.sum()), retained_bp=int(selected.retained_bp.sum()),
                removed_bp=int(selected.removed_bp.sum()), records_on_unannotated_contigs=int((mask & records.chrom.isin(unannotated)).sum()))
    assert next(status_chunks, None) is None
    for universe, expected in summaries.items():
        assert dict(census[universe]) == {k: int(v) for k, v in expected.items() if k != "universe_name"}, universe
    print("all three subtraction census rows independently recomputed; " + results[0])
