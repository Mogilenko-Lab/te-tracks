#!/usr/bin/env python3
"""Verify a completed build in place and report each assertion."""

import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from manifest import verify_build


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_dir", type=Path)
    parent = parser.add_mutually_exclusive_group()
    parent.add_argument("--parent-dir", type=Path)
    parent.add_argument("--root", type=Path)
    args = parser.parse_args()
    try:
        verify_build(args.build_dir, parent_dir=args.parent_dir, root=args.root)
    except (ValueError, KeyError, TypeError, StopIteration, OSError) as error:
        parser.exit(1, f"verify: {error}\n")
