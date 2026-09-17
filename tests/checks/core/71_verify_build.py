#!/usr/bin/env python3
"""Verify a real build unchanged and require named discrepancies on a tiny fixture."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter


ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tests/fixtures/publication"))
from build_fixture import make_build


BUILD = Path(os.environ["TE_TRACKS_REFROOT"]) / "te_mm39/build"
VERIFY = [sys.executable, str(ROOT / "src/99_verify.py")]


def run(path, status, message):
    result = subprocess.run([*VERIFY, str(path)], capture_output=True, text=True)
    assert result.returncode == status, result.stdout + result.stderr
    assert message in result.stdout + result.stderr, result.stdout + result.stderr


def rewrite_manifest(build, manifest):
    encoded = json.dumps(manifest["identity"], sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    identifier = hashlib.sha256(b"te-tracks-build-v1\n" + encoded).hexdigest()
    (build / "MANIFEST.json").write_text(json.dumps(manifest) + "\n")
    (build / "BUILD_ID").write_text(identifier + "\n")


before = {path.relative_to(BUILD): (path.stat().st_size, path.stat().st_mtime_ns)
          for path in BUILD.rglob("*")}
run(BUILD, 0, "verified " + (BUILD / "BUILD_ID").read_text().strip())
after = {path.relative_to(BUILD): (path.stat().st_size, path.stat().st_mtime_ns)
         for path in BUILD.rglob("*")}
assert before == after, "verifier changed the build"
started = perf_counter()
scratch = Path(os.environ["TE_TRACKS_REFROOT"]) / "pubtest"
scratch.mkdir(parents=True, exist_ok=True)
with TemporaryDirectory(prefix="verify-fixture-", dir=scratch) as directory:
    try:
        fixture = make_build(Path(directory) / "te_mm39")
        path = fixture / "source/mm39.chrom.sizes"
        data = path.read_bytes()
        path.write_bytes(bytes([data[0] ^ 1]) + data[1:])
        run(fixture, 1, "source/mm39.chrom.sizes")
        path.write_bytes(data)
        extra = fixture / "unexpected.txt"
        extra.write_text("unexpected payload\n")
        run(fixture, 1, "unexpected.txt")
        extra.unlink()
        manifest = json.loads((fixture / "MANIFEST.json").read_text())
        manifest["identity"]["taxonomy_rule_version"] = "taxonomy_rule_v9"
        rewrite_manifest(fixture, manifest)
        run(fixture, 1, "unsupported taxonomy_rule_version")
        manifest["identity"]["taxonomy_rule_version"] = "taxonomy_rule_v1"
        roster = fixture / "tables/exports.tsv"
        roster.write_text("".join(roster.read_text().splitlines(keepends=True)[:-1]))
        entry = next(item for item in manifest["identity"]["inventory"]
                     if item["path"] == "tables/exports.tsv")
        entry.update(bytes=roster.stat().st_size, sha256=hashlib.sha256(roster.read_bytes()).hexdigest())
        rewrite_manifest(fixture, manifest)
        run(fixture, 1, "export roster differs")
    finally:
        for parent, _, files in os.walk(directory):
            Path(parent).chmod(0o775)
            for name in files:
                path = Path(parent) / name
                if not path.is_symlink():
                    path.chmod(0o664)
elapsed = perf_counter() - started
print("real build verifies unchanged; fixture flipped byte, extra file, unpublished taxonomy rule and "
      f"export roster mismatch fail with named discrepancies; fixture cases={elapsed:.3f}s")
