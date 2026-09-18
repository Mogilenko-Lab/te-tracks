#!/usr/bin/env python3
"""Install verified immutable builds and atomically select a family archive."""

import argparse
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import re
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from manifest import read_json, require, verify_build


def validate_id(identifier):
    require(re.fullmatch(r"[0-9a-f]{64}", identifier) is not None,
            f"invalid BUILD_ID: {identifier!r}")
    return identifier


def family_root(root, family):
    require(re.fullmatch(r"te_[A-Za-z0-9_-]+", family) is not None,
            f"invalid family: {family!r}")
    path = Path(root).resolve() / family
    require(not path.is_symlink(), f"family root is a symlink: {path}")
    return path


@contextmanager
def publication_lock(family, create=False):
    """Serialize cooperative publishers across destination checks, rename and selection."""
    archive = family / "archive"
    if create:
        family.mkdir(parents=True, exist_ok=True)
        try:
            archive.mkdir(mode=0o2775)
        except FileExistsError:
            pass
        else:
            archive.chmod(0o2775)
    require(archive.is_dir() and not archive.is_symlink(), f"invalid archive directory: {archive}")
    descriptor = os.open(archive, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield archive
    finally:
        os.close(descriptor)


def verify_archive(path, family, identifier):
    """Require a complete archive whose directory, manifest family and ID agree."""
    require(path.is_dir() and not path.is_symlink(), f"invalid archive target: {path}")
    require(any(path.iterdir()), f"empty archive target refused: {path}")
    try:
        require((path / "BUILD_ID").read_bytes() == (identifier + "\n").encode(),
                f"BUILD_ID differs from archive name {identifier}")
        observed = verify_build(path, emit=lambda line: None, root=family.parent)
        require(observed == identifier, f"archive name differs from recomputed BUILD_ID {observed}")
        require(read_json(path / "MANIFEST.json")["identity"]["family"] == family.name,
                f"manifest family differs from {family.name}")
    except (ValueError, KeyError, TypeError, StopIteration, OSError) as error:
        raise ValueError(f"archive {path}: {error}") from error
    return identifier


def verify_current(family):
    """Resolve the relative selector once and verify its complete archive."""
    archive = family / "archive"
    require(archive.is_dir() and not archive.is_symlink(), f"invalid archive directory: {archive}")
    current = family / "current"
    require(current.is_symlink(), f"current requires a relative symlink: {current}")
    target = os.readlink(current)
    match = re.fullmatch(r"archive/([0-9a-f]{64})", target)
    require(match is not None, f"invalid current target: {current} -> {target}")
    try:
        return verify_archive(family / target, family, match[1])
    except (ValueError, KeyError, TypeError, StopIteration, OSError) as error:
        raise ValueError(f"current -> {target}: {error}") from error


def require_clean_builder(path, family, identifier):
    """Enforce the owner's clean-builder publication policy on the retained manifest."""
    manifest = read_json(path / "MANIFEST.json")
    require(manifest["provenance"]["builder_git_dirty"] is not True,
            f"{family.name} build {identifier}: --require-clean refuses builder_git_dirty=true")


def select_locked(family, identifier, verified=False, existing_id=None, require_clean=False):
    """Replace the sole selector after validating the candidate and existing selection."""
    target = family / "archive" / identifier
    current = family / "current"
    if require_clean:
        require_clean_builder(target, family, identifier)
    if os.path.lexists(current):
        selected = existing_id or verify_current(family)
        if selected == identifier:
            print(f"selected {identifier}")
            return
    if not verified:
        verify_archive(target, family, identifier)
    temporary = family / f"current.tmp.{os.getpid()}"
    os.symlink(f"archive/{identifier}", temporary)
    try:
        os.replace(temporary, current)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"selected {identifier}")


def normalize_modes(staging):
    for directory, directories, files in os.walk(staging, topdown=False):
        for name in files:
            (Path(directory) / name).chmod(0o444)
        Path(directory).chmod(0o755 if Path(directory) == staging else 0o555)


def discard_staging(staging):
    """Restore directory write access solely to remove a redundant private build."""
    for directory, directories, files in os.walk(staging):
        Path(directory).chmod(0o775)
    shutil.rmtree(staging)


def install(family, staging, select=False, require_clean=False):
    staging = Path(os.path.abspath(staging))
    parent = family / ".staging"
    require(not parent.is_symlink() and not staging.is_symlink()
            and staging.parent.resolve() == parent.resolve(),
            f"staging must be a direct directory under {parent}: {staging}")
    require(staging.is_dir(), f"missing staging directory: {staging}")
    identifier = verify_build(staging, emit=lambda line: None, root=family.parent)
    require(read_json(staging / "MANIFEST.json")["identity"]["family"] == family.name,
            f"staging manifest family differs from {family.name}")
    if require_clean:
        require_clean_builder(staging, family, identifier)
    with publication_lock(family, create=True) as archive:
        target = archive / identifier
        existing_id = None
        if select and os.path.lexists(family / "current"):
            existing_id = verify_current(family)
        if os.path.lexists(target):
            # Reuse the selected archive's verification under the held lock.
            if existing_id != identifier:
                verify_archive(target, family, identifier)
            if require_clean:
                require_clean_builder(target, family, identifier)
            discard_staging(staging)
            print(f"converged {identifier}")
        else:
            require(staging.stat().st_dev == archive.stat().st_dev,
                    f"staging and archive require one filesystem: {staging}, {archive}")
            normalize_modes(staging)
            # The archive lock keeps the destination absent through the directory rename.
            os.rename(staging, target)
            target.chmod(0o555)
            print(f"installed {identifier}")
        if select:
            select_locked(family, identifier, verified=True, existing_id=existing_id,
                          require_clean=require_clean)
    return identifier


def main():
    os.umask(0o002)
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "select", "verify-current"):
        command = commands.add_parser(name)
        command.add_argument("--root", required=True, type=Path)
        command.add_argument("--family", required=True)
        if name in ("install", "select"):
            command.add_argument("--require-clean", action="store_true",
                                 help="refuse manifests recording a dirty builder tree")
        if name == "install":
            command.add_argument("--staging", required=True, type=Path)
            command.add_argument("--select", action="store_true")
        if name == "select":
            command.add_argument("--build-id", required=True)
    args = parser.parse_args()
    try:
        family = family_root(args.root, args.family)
        if args.command == "install":
            install(family, args.staging, args.select, args.require_clean)
        elif args.command == "select":
            identifier = validate_id(args.build_id)
            with publication_lock(family):
                select_locked(family, identifier, require_clean=args.require_clean)
        else:
            print(verify_current(family))
    except (ValueError, KeyError, TypeError, StopIteration, OSError) as error:
        parser.exit(1, f"release: {error}\n")


if __name__ == "__main__":
    main()
