"""Require clean provenance before installing or selecting an owner's release."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/fixtures/publication"))
from build_fixture import make_build


def provenance(path, dirty):
    manifest = path / "MANIFEST.json"
    manifest.chmod(0o644)
    data = json.loads(manifest.read_text())
    data["provenance"]["builder_git_dirty"] = dirty
    manifest.write_text(json.dumps(data, indent=2) + "\n")
    manifest.chmod(0o444)


with tempfile.TemporaryDirectory(prefix="clean-publication-") as temporary:
    root = Path(temporary)
    family = root / "te_mm39"

    def release(command, *args, status=0, message=""):
        result = subprocess.run([sys.executable, str(ROOT / "src/release.py"), command,
                                 "--root", str(root), "--family", family.name, *map(str, args)],
                                text=True, capture_output=True)
        output = result.stdout + result.stderr
        assert result.returncode == status, output
        assert message in output, output
        return output.strip()

    try:
        staging = make_build(family)
        identifier = (staging / "BUILD_ID").read_text().strip()
        refusal = f"te_mm39 build {identifier}: --require-clean refuses builder_git_dirty=true"
        provenance(staging, True)
        release("install", "--staging", staging, "--require-clean", status=1, message=refusal)
        assert staging.is_dir() and not (family / "current").exists()
        release("install", "--staging", staging)
        release("select", "--build-id", identifier, "--require-clean", status=1, message=refusal)
        assert not (family / "current").exists()
        release("select", "--build-id", identifier, message="selected " + identifier)
        release("select", "--build-id", identifier, "--require-clean", status=1, message=refusal)
        assert (family / "current").readlink() == Path("archive") / identifier
        duplicate = make_build(family)
        assert (duplicate / "BUILD_ID").read_text().strip() == identifier
        provenance(duplicate, False)
        release("install", "--staging", duplicate, "--select", "--require-clean", status=1, message=refusal)
        assert duplicate.is_dir()
        provenance(family / "archive" / identifier, False)
        release("install", "--staging", duplicate, "--select", "--require-clean", message="converged " + identifier)
        release("select", "--build-id", identifier, "--require-clean", message="selected " + identifier)
        assert (family / "archive" / identifier / "BUILD_ID").read_text().strip() == identifier
    finally:
        for directory, _, _ in os.walk(root):
            Path(directory).chmod(0o755)
print("dirty install/select refused; permissive defaults pass; selected dirty archive and dirty convergence refused; clean convergence/select pass; BUILD_ID preserved")
