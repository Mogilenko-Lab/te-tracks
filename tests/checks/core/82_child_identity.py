#!/usr/bin/env python3
"""Exercise child identity boundaries and named dependency verification refusals."""

from copy import deepcopy
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/fixtures/publication"))
from build_fixture import make_build, make_child
from manifest import INHERITED_KEYS, build_id, catalog_id, digest_file, read_json, verify_build

REF = Path(os.environ["TE_TRACKS_REFROOT"])
CHILD, PARENT = REF / "te_mm39_gene/build", REF / "te_mm39/build"
if not CHILD.is_dir():
    print("gene child build is absent")
    raise SystemExit(3)
identity = read_json(CHILD / "MANIFEST.json")["identity"]
parent = read_json(PARENT / "MANIFEST.json")["identity"]
parent_bytes = {name: (PARENT / name).read_bytes() for name in ("BUILD_ID", "CATALOG_ID")}
assert identity["family"] == "te_mm39_gene" and identity["parent_family"] == "te_mm39"
assert identity["parent_build_id"] == parent_bytes["BUILD_ID"].decode().strip()
assert identity["parent_catalog_id"] == parent_bytes["CATALOG_ID"].decode().strip()
assert (CHILD / "CATALOG_ID").read_bytes() == parent_bytes["CATALOG_ID"]
assert set(identity["build_sources"]) == {"gene_gtf"}
for key in INHERITED_KEYS:
    assert identity[key] == parent[key], key
assert identity["gene_annotation"]["md5"] == "702e27a8727db66cd23e9f66f5aa1d38"
assert identity["gene_annotation"]["sha256"] == "0d1673f3c0fff7d28ff63f4443a0863fa25f817d391982e465f7ec20f256bcd0"
assert len(identity["export_contracts"]) == 12
assert set(identity["copied_inputs"]) == {"universes.json", "tables/contig_aliases.tsv"}
for path, digest in identity["copied_inputs"].items():
    assert digest_file(PARENT / path) == digest_file(CHILD / path) == digest
original = build_id(identity)
assert (CHILD / "BUILD_ID").read_text().strip() == original
mutations = [("gene_annotation", "md5", "0" * 32), ("gene_annotation", "sha256", "0" * 64),
             *[("policy_bundle", key, str(value) + "_changed") for key, value in identity["policy_bundle"].items()],
             (None, "parent_build_id", "0" * 64), (None, "parent_catalog_id", "0" * 64),
             (None, "export_contracts", identity["export_contracts"][:-1]),
             (None, "child_universes", identity["child_universes"][:1])]
for section, key, value in mutations:
    changed = deepcopy(identity)
    (changed[section] if section else changed)[key] = value
    assert build_id(changed) != original and catalog_id(changed["catalog"]) == catalog_id(parent["catalog"])
    assert all((PARENT / path).read_bytes() == content for path, content in parent_bytes.items())
SCRATCH = Path(os.environ["TE_TRACKS_REFROOT"]) / "pubtest"
SCRATCH.mkdir(parents=True, exist_ok=True)
with TemporaryDirectory(prefix="identity-", dir=SCRATCH) as temporary:
    root = Path(temporary)
    core = make_build(root / "te_mm39")
    with patch.dict(os.environ, {"FAMILY": "ambient_value"}):
        ambient = make_build(root / "te_mm39")
    assert (ambient / "BUILD_ID").read_bytes() == (core / "BUILD_ID").read_bytes()
    child = make_child(root / "te_mm39_gene", core)
    core_pin = (core / "BUILD_ID").read_bytes(), (core / "CATALOG_ID").read_bytes()
    changed_gtf = make_child(root / "te_mm39_gene", core, annotation_note="changed annotation bytes")
    assert (child / "BUILD_ID").read_bytes() != (changed_gtf / "BUILD_ID").read_bytes()
    assert core_pin == ((core / "BUILD_ID").read_bytes(), (core / "CATALOG_ID").read_bytes())

    def refused(message, parent_dir=core):
        try:
            verify_build(child, emit=lambda _: None, parent_dir=parent_dir)
        except (ValueError, OSError) as error:
            assert message in str(error), str(error)
        else:
            raise AssertionError("expected refusal: " + message)

    def save(path, manifest):
        (path / "MANIFEST.json").write_text(json.dumps(manifest))
        (path / "BUILD_ID").write_text(build_id(manifest["identity"]) + "\n")

    refused("child verification requires the parent archive", root / "absent")
    refused("child verification requires the parent archive", None)
    manifest = read_json(child / "MANIFEST.json")
    for field in ("parent_build_id", "parent_catalog_id"):
        changed = deepcopy(manifest)
        changed["identity"][field] = "bad"
        save(child, changed)
        refused("invalid " + field)
        changed["identity"][field] = "0" * 64
        save(child, changed)
        refused("parent " + ("BUILD_ID" if field == "parent_build_id" else "CATALOG_ID") + " differs")
    save(child, manifest)
    core_manifest = read_json(core / "MANIFEST.json")
    for field, value, message in (("family", "te_other", "parent family differs"),
                                  ("assembly", {"ucsc":"hg38", "name":"GRCh38"}, "parent assembly differs")):
        changed = deepcopy(core_manifest)
        changed["identity"][field] = value
        save(core, changed)
        refused(message)
    save(core, core_manifest)
    path = core / "source/qualification.md"
    content = path.read_bytes()
    path.write_bytes(bytes([content[0] ^ 1]) + content[1:])
    refused("inventory bytes or sha256 mismatch: source/qualification.md")
    result = subprocess.run([str(ROOT / "build.sh"), "--genome", "mm39", "--family", "gene",
                             "--build-dir", str(root / "out"), "--parent-dir", str(core)],
                            capture_output=True, text=True)
    assert result.returncode == 1 and "source/qualification.md" in result.stderr
    assert not (root / "out").exists(), "parent verification precedes child stages"
    path.write_bytes(content)
    path = child / "tables/contig_aliases.tsv"
    content = path.read_bytes()
    path.write_bytes(content.replace(b"100", b"101"))
    refused("inventory bytes or sha256 mismatch: tables/contig_aliases.tsv")
    changed = deepcopy(manifest)
    copied_digest = digest_file(path)
    changed["identity"]["copied_inputs"]["tables/contig_aliases.tsv"] = copied_digest
    sources_path = child / "source/SOURCES.json"
    source_bytes = sources_path.read_bytes()
    sources = read_json(sources_path)
    sources["copied_inputs"]["tables/contig_aliases.tsv"] = copied_digest
    sources_path.write_text(json.dumps(sources))
    for relative in ("tables/contig_aliases.tsv", "source/SOURCES.json"):
        entry = next(row for row in changed["identity"]["inventory"] if row["path"] == relative)
        entry.update(bytes=(child / relative).stat().st_size, sha256=digest_file(child / relative))
    save(child, changed)
    refused("copied input differs from parent: tables/contig_aliases.tsv")
    sources_path.write_bytes(source_bytes)
    path.write_bytes(content)
    save(child, manifest)
    for name, message in (("exon_subtraction_status.tsv", "exon_subtraction_status differs"),
                          ("export_feature_members.tsv.gz", "registration differs")):
        import gzip
        path = child / "tables" / name
        content = path.read_bytes()
        payload = gzip.decompress(content) if name.endswith("gz") else content
        payload = payload.replace(b"\t2\t2\n", b"\t1\t2\n") if name.endswith("gz") else payload.replace(b"split", b"trimmed")
        path.write_bytes(gzip.compress(payload, mtime=0) if name.endswith("gz") else payload)
        changed = deepcopy(manifest)
        entry = next(row for row in changed["identity"]["inventory"] if row["path"] == "tables/" + name)
        entry.update(bytes=path.stat().st_size, sha256=digest_file(path))
        save(child, changed)
        refused(message)
        path.write_bytes(content)
        save(child, manifest)
    import gzip
    registration = child / "tables/export_feature_members.tsv.gz"
    original_registration = registration.read_bytes()
    rows = gzip.decompress(original_registration).splitlines(keepends=True)
    registration.write_bytes(gzip.compress(rows[0] + b"".join(reversed(rows[1:])), mtime=0))
    reordered = deepcopy(manifest)
    entry = next(row for row in reordered["identity"]["inventory"]
                 if row["path"] == "tables/export_feature_members.tsv.gz")
    entry.update(bytes=registration.stat().st_size, sha256=digest_file(registration))
    save(child, reordered)
    verify_build(child, emit=lambda _: None, parent_dir=core)
    registration.write_bytes(original_registration)
    save(child, manifest)
    verify_build(child, emit=lambda _: None, parent_dir=core)
    export_path = "exports/ensembl/interspersed/exon_subtracted/subfamily.saf"
    saf = child / export_path
    original_saf = saf.read_bytes()
    exports = child / "tables/exports.tsv"
    original_exports = exports.read_bytes()

    def rehash_saf():
        rows = list(csv.DictReader(io.StringIO(original_exports.decode()), delimiter="\t"))
        next(row for row in rows if row["export_path"] == export_path)["sha256"] = digest_file(saf)
        with exports.open("w") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        changed = deepcopy(manifest)
        for relative in (export_path, "tables/exports.tsv"):
            entry = next(row for row in changed["identity"]["inventory"] if row["path"] == relative)
            entry.update(bytes=(child / relative).stat().st_size, sha256=digest_file(child / relative))
        save(child, changed)

    for mutation, message in (("content", "SAF rows differ from registration"), ("order", "SAF order differs")):
        rows = original_saf.splitlines(keepends=True)
        if mutation == "content":
            fields = rows[2].rstrip(b"\n").split(b"\t")
            assert fields[2] == b"4"
            fields[2] = b"3"
            rows[2] = b"\t".join(fields) + b"\n"
        else:
            rows[1], rows[2] = rows[2], rows[1]
        saf.write_bytes(b"".join(rows))
        rehash_saf()
        refused(message + ": " + export_path)
        saf.write_bytes(original_saf)
        exports.write_bytes(original_exports)
        save(child, manifest)
        verify_build(child, emit=lambda _: None, parent_dir=core)
    base = [str(ROOT / "build.sh"), "--genome", "mm39", "--family", "gene"]
    parent_link = root / "parent-link"
    parent_link.symlink_to(core, target_is_directory=True)
    for suffix in ("", "/", "///"):
        result = subprocess.run([*base, "--build-dir", str(root / "out"),
                                 "--parent-dir", str(parent_link) + suffix], capture_output=True, text=True)
        assert result.returncode == 2 and "usage:" in result.stderr, result.stdout + result.stderr
        assert not (root / "out").exists()
        result = subprocess.run([*base, "--build-dir", str(parent_link) + suffix,
                                 "--parent-dir", str(core)], capture_output=True, text=True)
        assert result.returncode == 2 and "usage:" in result.stderr, result.stdout + result.stderr
    for args in (("--build-dir", root / "out"), ("--root", root, "--parent-dir", core),
                 ("--build-dir", root / "out", "--parent-build-id", "0" * 64),
                 ("--root", root, "--parent-build-id", "bad"),
                 ("--build-dir", root / "out", "--parent-dir", root / "current"),
                 ("--build-dir", root / "out", "--parent-dir", core, "--parent-build-id", "0" * 64)):
        result = subprocess.run([*base, *map(str, args)], capture_output=True, text=True)
        assert result.returncode == 2 and "usage:" in result.stderr, result.stdout + result.stderr
    assert not (root / "out").exists()
print("child identity fields, inherited pins, all policy/GTF/roster/parent mutations, dependency and payload refusals, "
      "SAF content and order refusals, parent/build-dir symlink refusals with trailing slashes, CLI usage gates pass")
