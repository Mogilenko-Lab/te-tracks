"""Distinguish an absent acceptance build from a damaged selected archive."""

from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/checks/acceptance"))
from lib import common


with tempfile.TemporaryDirectory(prefix="acceptance-prerequisites-") as temporary:
    acceptance = Path(temporary) / "acceptance"
    with patch.object(common, "ACCEPTANCE", acceptance):
        output = io.StringIO()
        with redirect_stdout(output):
            try:
                common.require_builds()
            except SystemExit as error:
                assert error.code == 3
            else:
                raise AssertionError("missing acceptance build accepted")
        assert "unsupported: run tests/run.sh acceptance --build" in output.getvalue()
        builds = []
        for family in common.FAMILIES:
            archive = acceptance / family / "archive" / ("a" * 64)
            archive.mkdir(parents=True)
            for name in ("BUILD_ID", "CATALOG_ID", "MANIFEST.json"):
                (archive / name).write_text("a" * 64 + "\n")
            (acceptance / family / "current").symlink_to(Path("archive") / archive.name)
            builds.append(archive)
        assert common.require_builds() == builds
        for archive in builds:
            for name in ("BUILD_ID", "CATALOG_ID", "MANIFEST.json"):
                missing = archive / name
                content = missing.read_bytes()
                missing.unlink()
                try:
                    common.require_builds()
                except AssertionError as error:
                    assert "damaged acceptance archive" in str(error) and name in str(error)
                else:
                    raise AssertionError(f"missing {missing} accepted")
                finally:
                    missing.write_bytes(content)
        current = acceptance / common.FAMILIES[0] / "current"
        current.unlink()
        current.symlink_to("archive/absent")
        try:
            common.require_builds()
        except AssertionError as error:
            assert "damaged acceptance selector" in str(error)
        else:
            raise AssertionError("dangling acceptance selector accepted")
checks = list((ROOT / "tests/checks/acceptance").glob("*.py"))
assert len(checks) == 11 and all(path.name.endswith(".required.py") for path in checks)
print("absent builds unsupported; three missing identity files in either archive and dangling current fail; all eleven acceptance checks required")
