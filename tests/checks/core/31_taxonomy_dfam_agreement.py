#!/usr/bin/env python3
"""Check Dfam admission coverage, named ranks and retained snapshot provenance."""

import csv
from datetime import date
import json
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlsplit

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/lib"))
from records import BUILD, require


def rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


require("tables/taxonomy_resolution_report.tsv", "tables/taxonomy_canonical.tsv")
fixture = ROOT / "tests/fixtures/taxonomy"
snapshot_rows = rows(fixture / "dfam_snapshot.tsv")
report_rows = rows(BUILD / "tables/taxonomy_resolution_report.tsv")
canonical_rows = rows(BUILD / "tables/taxonomy_canonical.tsv")
snapshot = {row["rmsk_name"]: row for row in snapshot_rows}
report = {row["rmsk_name"]: row for row in report_rows}
canonical = {row["rmsk_name"]: row for row in canonical_rows}
census = {row["metric"]: row["value"] for row in rows(
    ROOT / "tests/expectations/mm39/taxonomy_census.tsv")}
provenance = json.loads((fixture / "dfam_snapshot.provenance.json").read_text())
missing = sorted(report.keys() - snapshot.keys())
extra = sorted(snapshot.keys() - canonical.keys())
print(f"report names missing from snapshot: {missing}")
print(f"snapshot names outside canonical: {extra}")
print(f"snapshot names beyond report: {sorted(snapshot.keys() - report.keys())}")
disagreements = []
for name in sorted(snapshot.keys() & canonical.keys()):
    actual, expected = canonical[name], snapshot[name]
    for rank, field in [("class", "dfam_repeat_type"), ("family", "dfam_repeat_subtype")]:
        if expected[field] and actual[f"canonical_{rank}"] != expected[field]:
            disagreements.append(
                f"{name}: {rank} canonical={actual[f'canonical_{rank}']}; Dfam={expected[field]}")
for disagreement in disagreements:
    print(disagreement)

endpoint = urlsplit(str(provenance.get("endpoint_pattern", "")))
fetched_on = provenance.get("fetched_on", "")
try:
    valid_date = date.fromisoformat(fetched_on).isoformat() == fetched_on
except (TypeError, ValueError):
    valid_date = False
source = provenance.get("source", "")
checks = {
    "endpoint_pattern": (endpoint.scheme == "https" and endpoint.netloc == "dfam.org"
                         and endpoint.path == "/api/families" and not endpoint.fragment
                         and parse_qs(endpoint.query) == {"name": ["<name>"], "format": ["summary"]}),
    "fetched_on": valid_date and {row["fetched_on"] for row in snapshot_rows} == {fetched_on},
    "source": (isinstance(source, str) and source.endswith(".tsv")
               and not Path(source).is_absolute() and (ROOT / source).is_file()),
    "role": provenance.get("role") == "Pinned test evidence for canonical taxonomy agreement.",
    "build_reads_snapshot": provenance.get("build_reads_snapshot") is False,
    "version_evidence": (provenance.get("version_evidence") ==
                         "per-family dfam_version column of the snapshot"
                         and all(row["dfam_version"] for row in snapshot_rows)),
    "release_endpoint_response": ("release_endpoint_response" in provenance
                                  and provenance["release_endpoint_response"] is None),
    "release_endpoint_response_status": (provenance.get("release_endpoint_response_status") ==
        f"unrecorded at the {fetched_on} fetch; the next snapshot refresh records it"),
}
for key, valid in checks.items():
    print(f"provenance {key}: {'pass' if valid else 'fail'}")
assert set(provenance) == set(checks), ("provenance keys", sorted(provenance), sorted(checks))
for key, valid in checks.items():
    assert valid, f"provenance {key}: {provenance.get(key)!r}"
assert len(snapshot) == len(snapshot_rows), "snapshot name uniqueness"
assert len(report) == len(report_rows), "report name uniqueness"
assert len(canonical) == len(canonical_rows), "canonical name uniqueness"
assert len(snapshot_rows) == int(census["snapshot_rows"]), "snapshot row census"
assert not missing, f"report names missing from Dfam snapshot: {missing}"
assert not extra, f"Dfam snapshot names outside canonical table: {extra}"
assert not disagreements, f"{len(disagreements)} Dfam rank disagreements"
print(f"{len(snapshot)} of {len(snapshot_rows)} canonical labels agree with Dfam; "
      f"{len(report)} report names covered; snapshot names belong to canonical")
