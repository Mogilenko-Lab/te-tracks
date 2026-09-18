"""Resolve acceptance archives and run existing contracts against their bytes."""

from contextlib import contextmanager
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
REFROOT = Path(os.environ.get("TE_TRACKS_REFROOT",
    "/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot")).resolve()
ACCEPTANCE = REFROOT / "acceptance"
SCRATCH = (Path(os.environ.get("TMPDIR", str(REFROOT / "tmp")))
           / ("te-tracks-" + hashlib.sha256(str(REFROOT).encode()).hexdigest()[:12]) / "acceptance")
EXPECT = ROOT / "tests/expectations/mm39"
FAMILIES = ("te_mm39", "te_mm39_gene")


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def digest(path, algorithm="sha256"):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


@contextmanager
def scratch(prefix):
    SCRATCH.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix=prefix, dir=SCRATCH))
    try:
        yield path
    finally:
        shutil.rmtree(path)


def build():
    cache = Path(os.environ.get("TE_TRACKS_SOURCE_CACHE", "/workspaces/Meta-Aging/_scratch/te-tracks-audit/source"))
    for row in rows(EXPECT / "source_pins.tsv"):
        path = (ROOT if row["location"] == "package" else cache) / row["path"]
        assert path.is_file(), f"offline source missing: {path}; seed the retained cache before building"
        assert digest(path, row["algorithm"]) == row["digest"], f"source checksum mismatch: {path}; stop for a re-pin decision"
    assert not ACCEPTANCE.exists() or not any(ACCEPTANCE.iterdir()), (
        f"fresh acceptance build requires an empty {ACCEPTANCE}; preserve existing archives and choose another --refroot")
    with scratch("build-") as temporary:
        env = {**os.environ, "TE_TRACKS_SOURCE_CACHE": str(cache), "TMPDIR": str(temporary),
               "PYTHONDONTWRITEBYTECODE": "1"}
        subprocess.run(["bash", str(ROOT / "build.sh"), "--genome", "mm39", "--root", str(ACCEPTANCE)],
                       check=True, env=env, stdout=sys.stderr)
        parent = (ACCEPTANCE / "te_mm39/current/BUILD_ID").read_text().strip()
        subprocess.run(["bash", str(ROOT / "build.sh"), "--genome", "mm39", "--family", "gene",
                        "--root", str(ACCEPTANCE), "--parent-build-id", parent],
                       check=True, env=env, stdout=sys.stderr)


def require_builds():
    selected = []
    for family in FAMILIES:
        current = ACCEPTANCE / family / "current"
        if not os.path.lexists(current):
            print("unsupported: run tests/run.sh acceptance --build")
            raise SystemExit(3)
        assert current.is_symlink(), f"acceptance selector requires a symlink: {current}"
        assert current.exists(), f"damaged acceptance selector: {current} -> {current.readlink()}"
        path = current.resolve(strict=True)
        assert path.parent == ACCEPTANCE / family / "archive", f"acceptance archive escaped its family: {path}"
        missing = [name for name in ("BUILD_ID", "CATALOG_ID", "MANIFEST.json")
                   if not (path / name).is_file()]
        assert not missing, f"damaged acceptance archive: {path}; missing {', '.join(missing)}"
        assert path.name == (path / "BUILD_ID").read_text().strip(), f"archive name differs: {path}"
        selected.append(path)
    return selected


def core_checks(core, child, *names):
    """Apply the established full-data contracts through private archive aliases."""
    summaries = []
    with scratch("contracts-") as reference:
        for family, archive in zip(FAMILIES, (core, child)):
            (reference / family).mkdir()
            (reference / family / "build").symlink_to(archive, target_is_directory=True)
        env = {**os.environ, "TE_TRACKS_REFROOT": str(reference), "TMPDIR": str(reference),
               "PYTHONDONTWRITEBYTECODE": "1"}
        for name in names:
            command = ["bash" if name.endswith(".sh") else sys.executable,
                       str(ROOT / "tests/checks/core" / name)]
            result = subprocess.run(command, env=env, text=True, capture_output=True)
            assert result.returncode == 0, f"{name}: exit {result.returncode}\n{result.stdout}\n{result.stderr}"
            summaries.append(f"{name}: " + result.stdout.strip().replace("\n", "; "))
    return summaries


def run(area):
    if area == "10_source" and os.environ.get("TE_TRACKS_ACCEPTANCE_BUILD") == "1":
        build()
    core, child = require_builds()
    from . import areas
    getattr(areas, area.split("_", 1)[1])(core, child)
