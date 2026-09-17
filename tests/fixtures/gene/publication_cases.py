"""Verify child publication dependency closure through tiny complete builds."""

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/fixtures/publication"))
from build_fixture import make_build, make_child

SCRATCH = Path(os.environ["TE_TRACKS_REFROOT"]) / "pubtest"
SCRATCH.mkdir(parents=True, exist_ok=True)
with TemporaryDirectory(prefix="publication-", dir=SCRATCH) as temporary:
    root = Path(temporary)

    def release(family, command, *args, status=0, message=""):
        result = subprocess.run([sys.executable, str(ROOT / "src/release.py"), command,
                                 "--root", str(root), "--family", family, *map(str, args)],
                                capture_output=True, text=True)
        assert result.returncode == status, result.stdout + result.stderr
        assert message in result.stdout + result.stderr, result.stdout + result.stderr
        return result.stdout

    def identifier(build):
        return (build / "BUILD_ID").read_text().strip()

    try:
        parent = make_build(root / "te_mm39")
        parent_id = identifier(parent)
        child = make_child(root / "te_mm39_gene", parent)
        child_id = identifier(child)
        release("te_mm39_gene", "install", "--staging", child, "--select", status=1,
                message="child verification requires the parent archive")
        assert child.is_dir() and not (root / "te_mm39_gene/current").exists()
        release("te_mm39", "install", "--staging", parent, "--select", message="installed " + parent_id)
        parent = root / "te_mm39/archive" / parent_id
        release("te_mm39_gene", "install", "--staging", child, "--select", message="installed " + child_id)
        child = root / "te_mm39_gene/archive" / child_id
        current = root / "te_mm39_gene/current"
        original_manifest = (child / "MANIFEST.json").read_bytes()
        assert current.readlink() == Path("archive") / child_id
        release("te_mm39_gene", "verify-current", message=child_id)
        preflight = subprocess.run([sys.executable, str(ROOT / "bin/te-tracks-preflight"),
            str(child / "exports/ucsc/interspersed/exon_subtracted/subfamily.saf"),
            str(parent / "source/mm39.chrom.sizes")], capture_output=True, text=True)
        assert preflight.returncode == 0 and str(child / "tables/contig_aliases.tsv") in preflight.stdout
        standalone = subprocess.run([sys.executable, str(ROOT / "src/99_verify.py"), str(child)],
                                    capture_output=True, text=True)
        assert standalone.returncode == 0, standalone.stderr
        repeat = make_child(root / "te_mm39_gene", parent)
        assert identifier(repeat) == child_id
        release("te_mm39_gene", "install", "--staging", repeat, "--select", message="converged " + child_id)
        assert len(list((root / "te_mm39_gene/archive").iterdir())) == 1
        assert (child / "MANIFEST.json").read_bytes() == original_manifest
        candidate = make_child(root / "te_mm39_gene", parent, annotation_note="second")
        hidden = root / "hidden-parent"
        parent.chmod(0o755)
        parent.rename(hidden)
        for command, args in (("install", ("--staging", candidate, "--select")),
                              ("select", ("--build-id", child_id)), ("verify-current", ())):
            release("te_mm39_gene", command, *args, status=1,
                    message="child verification requires the parent archive")
            assert current.readlink() == Path("archive") / child_id and candidate.is_dir()
        hidden.rename(parent)
        parent.chmod(0o555)
        path = parent / "source/qualification.md"
        content = path.read_bytes()
        path.chmod(0o644)
        path.write_bytes(bytes([content[0] ^ 1]) + content[1:])
        for command, args in (("install", ("--staging", candidate, "--select")),
                              ("select", ("--build-id", child_id)), ("verify-current", ())):
            release("te_mm39_gene", command, *args, status=1,
                    message="inventory bytes or sha256 mismatch: source/qualification.md")
            assert current.readlink() == Path("archive") / child_id and candidate.is_dir()
        path.write_bytes(content)
        path.chmod(0o444)
        release("te_mm39_gene", "install", "--staging", candidate)
        assert current.readlink() == Path("archive") / child_id
        newer = make_build(root / "te_mm39", note="newer core")
        release("te_mm39", "install", "--staging", newer, "--select")
        release("te_mm39_gene", "verify-current", message=child_id)
        release("te_mm39", "select", "--build-id", parent_id, message="selected " + parent_id)
        release("te_mm39", "verify-current", message=parent_id)
        release("te_mm39_gene", "verify-current", message=child_id)
        for build in (parent, child):
            for path in (build, *build.rglob("*")):
                assert path.stat().st_mode & 0o777 == (0o555 if path.is_dir() else 0o444)
    finally:
        for directory, _, files in os.walk(root):
            Path(directory).chmod(0o775)
            for name in files:
                path = Path(directory) / name
                if not path.is_symlink():
                    path.chmod(0o664)
print("child install/select/verify-current require present, verified parent; repeated publication converges; "
      "archive resolution, preserved selection, immutable modes and earlier core selection pass")
