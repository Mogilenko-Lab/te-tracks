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
entries = manifest["identity"]["inventory"]
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
assert len(manifest["identity"]["export_contracts"]) == 24
print(f"BUILD_ID={original[0]} CATALOG_ID={original[1]}; {len(entries)} payloads; identity mutations pass")
