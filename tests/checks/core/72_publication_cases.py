#!/usr/bin/env python3
"""Exercise publication success, corruption, concurrency and immutable payload modes."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import stat
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Barrier

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/fixtures/publication"))
from build_fixture import make_build


SCRATCH = Path(os.environ.get("TMPDIR", str(Path(os.environ["TE_TRACKS_REFROOT"]) / "pubtest")))
SCRATCH.mkdir(parents=True, exist_ok=True)


def identifier(path):
    return (path / "BUILD_ID").read_text().strip()


def catalog(path):
    return (path / "CATALOG_ID").read_text().strip()


def writable(path):
    for directory, directories, files in os.walk(path):
        Path(directory).chmod(0o775)
        for name in files:
            if not (Path(directory) / name).is_symlink():
                (Path(directory) / name).chmod(0o664)


with TemporaryDirectory(prefix="cases-", dir=SCRATCH) as directory:
    root = Path(directory)
    family = root / "te_mm39"

    def release(command, *args, status=0, message=""):
        result = subprocess.run([sys.executable, str(ROOT / "src/release.py"), command,
                                 "--root", str(root), "--family", "te_mm39", *map(str, args)],
                                capture_output=True, text=True)
        assert result.returncode == status, result.stdout + result.stderr
        assert message in result.stdout + result.stderr, result.stdout + result.stderr
        return result.stdout

    try:
        first = make_build(family)
        first_id, first_catalog = identifier(first), catalog(first)
        release("install", "--staging", first, "--select", message="installed " + first_id)
        archive = family / "archive"
        current = family / "current"
        old = archive / first_id
        raw_manifest = (old / "MANIFEST.json").read_bytes()
        assert current.readlink() == Path("archive") / first_id and not first.exists()
        identical = make_build(family)
        assert identifier(identical) == first_id
        release("install", "--staging", identical, "--select", message="converged " + first_id)
        assert len(list(archive.iterdir())) == 1 and not identical.exists()
        assert (old / "MANIFEST.json").read_bytes() == raw_manifest
        changed = make_build(family, note="second")
        second_id = identifier(changed)
        assert second_id != first_id and catalog(changed) == first_catalog
        release("install", "--staging", changed, "--select")
        assert current.readlink() == Path("archive") / second_id and old.is_dir()
        assert len(list(archive.iterdir())) == 2
        evolution_a = make_build(family, note="evolution")
        evolution_a_id = identifier(evolution_a)
        release("install", "--staging", evolution_a, "--select")
        assert current.readlink() == Path("archive") / evolution_a_id
        evolution_b = make_build(family, note="evolution", added_export=True)
        evolution_b_id = identifier(evolution_b)
        assert evolution_b_id != evolution_a_id
        release("install", "--staging", evolution_b, "--select")
        assert current.readlink() == Path("archive") / evolution_b_id
        assert (archive / evolution_a_id).is_dir() and (archive / evolution_b_id).is_dir()
        release("select", "--build-id", evolution_a_id, message="selected " + evolution_a_id)
        release("verify-current", message=evolution_a_id)
        assert current.readlink() == Path("archive") / evolution_a_id
        assert catalog(archive / evolution_a_id) == catalog(archive / evolution_b_id) == first_catalog
        for value, count in ((evolution_a_id, 27), (evolution_b_id, 30)):
            declared = json.loads((archive / value / "MANIFEST.json").read_text())
            assert len(declared["identity"]["export_contracts"]) == count
        assert len(list(archive.iterdir())) == 4
        release("select", "--build-id", second_id)
        bad = make_build(family)
        (bad / "source/qualification.md").write_text("corrupt\n")
        release("install", "--staging", bad, "--select", status=1, message="source/qualification.md")
        assert bad.exists() and current.readlink() == Path("archive") / second_id
        interrupted = make_build(family, note="interrupted")
        (interrupted / "MANIFEST.json").unlink()
        (interrupted / "tables/taxonomy_dfam.tsv").write_bytes(b"rmsk_name\t")
        selected_before = current.readlink()
        archives_before_failure = set(archive.iterdir())
        release("install", "--staging", interrupted, "--select", status=1, message="MANIFEST.json")
        assert interrupted.is_dir() and current.readlink() == selected_before
        assert set(archive.iterdir()) == archives_before_failure
        shutil.rmtree(interrupted)
        assert not interrupted.exists()
        candidates = [make_build(family, note="concurrent") for _ in range(2)]
        race_id = identifier(candidates[0])
        assert identifier(candidates[1]) == race_id
        barrier = Barrier(2)

        def concurrent_install(path):
            barrier.wait(timeout=10)
            return release("install", "--staging", path, "--select")

        with ThreadPoolExecutor(max_workers=2) as pool:
            outputs = list(pool.map(concurrent_install, candidates))
        assert sum("installed " + race_id in output for output in outputs) == 1
        assert sum("converged " + race_id in output for output in outputs) == 1
        assert all(not path.exists() for path in candidates)
        assert len(list(archive.iterdir())) == 5
        assert current.readlink() == Path("archive") / race_id
        release("verify-current", message=race_id)
        old_payload = old / "source/qualification.md"
        old_payload.chmod(0o644)
        old_bytes = old_payload.read_bytes()
        old_payload.write_text("damaged existing archive\n")
        existing_bad = make_build(family)
        release("install", "--staging", existing_bad, status=1, message=str(old))
        assert existing_bad.exists()
        old_payload.write_bytes(old_bytes)
        old_payload.chmod(0o444)
        (old / "BUILD_ID").chmod(0o644)
        (old / "BUILD_ID").write_text("0" * 64 + "\n")
        release("select", "--build-id", first_id, status=1, message="BUILD_ID")
        (old / "BUILD_ID").write_text(first_id + "\n")
        (old / "BUILD_ID").chmod(0o444)
        selected_payload = archive / race_id / "source/qualification.md"
        selected_payload.chmod(0o644)
        original = selected_payload.read_bytes()
        selected_payload.write_text("damaged\n")
        release("select", "--build-id", first_id, status=1, message="source/qualification.md")
        release("verify-current", status=1, message=f"current -> archive/{race_id}: ")
        assert current.readlink() == Path("archive") / race_id
        selected_payload.write_bytes(original)
        selected_payload.chmod(0o444)
        empty = make_build(family, note="empty-target")
        empty_target = archive / identifier(empty)
        empty_target.mkdir()
        release("install", "--staging", empty, status=1, message="empty archive target")
        assert empty.exists() and list(empty_target.iterdir()) == []
        empty_target.rmdir()
        linked = make_build(family, note="symlink-target")
        linked_target = archive / identifier(linked)
        linked_target.symlink_to(old, target_is_directory=True)
        release("install", "--staging", linked, status=1, message="invalid archive target")
        assert linked.exists() and linked_target.is_symlink()
        linked_target.unlink()
        payload_link = make_build(family, note="payload-link")
        (payload_link / "link").symlink_to("source/qualification.md")
        release("install", "--staging", payload_link, status=1, message="symlink inside build: link")
        assert payload_link.exists()
        unreadable = make_build(family, note="unreadable")
        hidden = unreadable / "hidden"
        hidden.mkdir()
        (hidden / "payload.txt").write_text("retained payload\n")
        hidden.chmod(0)
        try:
            release("install", "--staging", unreadable, status=1, message="hidden")
        finally:
            hidden.chmod(0o755)
        barrier = Barrier(2)

        def concurrent_select(value):
            barrier.wait(timeout=10)
            return release("select", "--build-id", value)

        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(concurrent_select, [first_id, second_id]))
        assert current.readlink() in {Path("archive") / first_id, Path("archive") / second_id}
        release("verify-current")
        selected_link = current.readlink()
        for invalid_target in ("archive/" + "0" * 64, "../escape"):
            current.unlink()
            current.symlink_to(invalid_target)
            release("select", "--build-id", first_id, status=1, message="target")
            assert current.readlink() == Path(invalid_target)
        current.unlink()
        current.symlink_to(selected_link)
        archives_before = set(archive.iterdir())
        dangling = make_build(family, note="dangling-current")
        current.unlink()
        current.symlink_to("archive/" + "0" * 64)
        release("install", "--staging", dangling, "--select", status=1,
                message="current -> archive/" + "0" * 64 + ": invalid archive target")
        assert dangling.is_dir() and current.readlink() == Path("archive") / ("0" * 64)
        assert set(archive.iterdir()) == archives_before
        current.unlink()
        current.symlink_to(selected_link)
        removed = make_build(family, note="removed-archive")
        removed_id = identifier(removed)
        release("install", "--staging", removed, "--select")
        writable(archive / removed_id)
        shutil.rmtree(archive / removed_id)
        for command, args in (("select", ("--build-id", first_id)), ("verify-current", ())):
            release(command, *args, status=1,
                    message=f"current -> archive/{removed_id}: invalid archive target")
            assert current.readlink() == Path("archive") / removed_id
            assert set(archive.iterdir()) == archives_before
        current.unlink()
        release("select", "--build-id", first_id)
        release("verify-current", message=first_id)
        current.unlink()
        current.write_text("regular selector\n")
        for command, args in (("select", ("--build-id", second_id)), ("verify-current", ()),
                              ("install", ("--staging", dangling, "--select"))):
            release(command, *args, status=1, message="current requires a relative symlink")
            assert current.is_file() and not current.is_symlink()
            assert current.read_text() == "regular selector\n" and dangling.is_dir()
            assert set(archive.iterdir()) == archives_before
        current.unlink()
        current.symlink_to(old)
        for command, args in (("select", ("--build-id", second_id)), ("verify-current", ()),
                              ("install", ("--staging", dangling, "--select"))):
            release(command, *args, status=1, message="invalid current target")
            assert current.readlink() == old and dangling.is_dir()
            assert set(archive.iterdir()) == archives_before
        current.unlink()
        release("select", "--build-id", first_id)
        outside = root / "outside-staging"
        dangling.rename(outside)
        release("install", "--staging", outside, "--select", status=1,
                message="staging must be a direct directory under")
        assert outside.is_dir() and current.readlink() == Path("archive") / first_id
        assert set(archive.iterdir()) == archives_before
        release("select", "--build-id", "non-hex", status=1, message="invalid BUILD_ID")
        assert current.readlink() == Path("archive") / first_id
        assert set(archive.iterdir()) == archives_before
        actual_family = root / "actual-family"
        family.rename(actual_family)
        family.symlink_to(actual_family, target_is_directory=True)
        try:
            release("verify-current", status=1, message="family root is a symlink")
            assert family.readlink() == actual_family
            assert current.readlink() == Path("archive") / first_id
            assert set(archive.iterdir()) == archives_before
        finally:
            family.unlink()
            actual_family.rename(family)
        assert stat.S_IMODE(archive.stat().st_mode) == 0o2775
        for installed in archive.iterdir():
            for path in [installed, *installed.rglob("*")]:
                expected = 0o555 if path.is_dir() else 0o444
                assert stat.S_IMODE(path.stat().st_mode) == expected, path
        assert old.is_dir() and identifier(old) == first_id
    finally:
        writable(root)
print("identical and changed builds, export-roster evolution (4 archives), failed verification and interrupted staging cleanup, "
      "concurrent installs/selects (5 archives), old IDs, forged ID, corrupt current, selector and root cases, "
      "occupied targets, symlinks and 0444/0555 modes pass")
