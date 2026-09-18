#!/usr/bin/env python3
"""Recompute both identities independently and exercise their mutation boundaries."""

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path


BUILD = Path(os.environ["TE_TRACKS_REFROOT"]) / "te_mm39/build"


def identifier(prefix, value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                         allow_nan=False).encode("utf-8")
    return hashlib.sha256(prefix + encoded).hexdigest()


def identities(manifest):
    return (identifier(b"te-tracks-build-v1\n", manifest["identity"]),
            identifier(b"te-tracks-catalog-v1\n", manifest["identity"]["catalog"]))


manifest = json.loads((BUILD / "MANIFEST.json").read_text())
original = identities(manifest)
assert (BUILD / "BUILD_ID").read_bytes() == (original[0] + "\n").encode()
assert (BUILD / "CATALOG_ID").read_bytes() == (original[1] + "\n").encode()
changed = deepcopy(manifest)
changed["provenance"]["built_at"] = "2000-01-01T00:00:00Z"
assert identities(changed) == original
changed = deepcopy(manifest)
changed["identity"]["universes"]["universes"][0]["predicate"] = {"class_in": ["LINE"]}
assert identities(changed)[0] != original[0] and identities(changed)[1] == original[1]
changed = deepcopy(manifest)
changed["identity"]["catalog"]["sources"]["rmsk_out"]["sha256"] = "0" * 64
assert all(left != right for left, right in zip(identities(changed), original))
changed = deepcopy(manifest)
changed["identity"]["build_sources"]["chromAlias"]["sha256"] = "0" * 64
assert identities(changed)[0] != original[0] and identities(changed)[1] == original[1]
changed = deepcopy(manifest)
changed["identity"]["taxonomy_rule_version"] = "taxonomy_rule_v2"
assert identities(changed)[0] != original[0] and identities(changed)[1] == original[1]
changed = deepcopy(manifest)
parquet = next(item for item in changed["identity"]["inventory"]
               if item["path"] == "tables/rmsk_records.parquet")
parquet["sha256"] = "0" * 64
assert identities(changed)[0] != original[0] and identities(changed)[1] == original[1]
changed = deepcopy(manifest)
changed["identity"]["catalog"]["tables"]["rmsk_records.tsv"] = "0" * 64
assert all(left != right for left, right in zip(identities(changed), original))
entries = manifest["identity"]["inventory"]
assert len(entries) == 52
assert set(manifest["identity"]["build_sources"]) == {"rmsk_out", "rmsk_table", "chromAlias", "chrom_sizes", "dfam_snapshot"}
changed = deepcopy(manifest)
changed["identity"]["build_sources"]["dfam_snapshot"]["sha256"] = "0" * 64
assert identities(changed)[0] != original[0] and identities(changed)[1] == original[1]
paths = [item["path"] for item in entries]
assert paths == sorted(set(paths))
files = []
for path in BUILD.rglob("*"):
    assert not path.is_symlink(), path
    if path.is_file() and path.relative_to(BUILD).as_posix() not in {"MANIFEST.json", "BUILD_ID", "CATALOG_ID"}:
        files.append(path.relative_to(BUILD).as_posix())
assert paths == sorted(files)
for entry in entries:
    path = BUILD / entry["path"]
    assert ".." not in Path(entry["path"]).parts
    assert path.stat().st_size == entry["bytes"], path
    with path.open("rb") as stream:
        assert hashlib.file_digest(stream, "sha256").hexdigest() == entry["sha256"], path
assert manifest["identity"]["catalog"]["instance_id_scope"] == "source_run"
assert manifest["identity"]["taxonomy_rule_version"] == "taxonomy_rule_v1"
assert manifest["identity"]["rank_scheme_version"] == "rank_scheme_wicker_v1"
assert len(manifest["identity"]["export_contracts"]) == 27
identity_fields = {"export_path", "namespace", "universe_name", "variant", "format", "feature_level",
                   "feature_identity", "attribute_sources", "selectable_levels", "coordinate_convention"}
for contract in manifest["identity"]["export_contracts"]:
    assert set(contract) == identity_fields and "consumer_keys" not in contract
assert set(manifest["identity"]["catalog"]["tables"]) == {
    "rmsk_records.tsv", "rmsk_instance_members.tsv", "rmsk_taxonomy.tsv"}
print(f"BUILD_ID={original[0]} CATALOG_ID={original[1]}; {len(entries)} payloads; identity mutations pass")
