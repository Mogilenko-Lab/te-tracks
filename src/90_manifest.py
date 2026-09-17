#!/usr/bin/env python3
"""Write the verified manifest, BUILD_ID and CATALOG_ID for a completed build."""

import argparse
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from manifest import write_manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_dir", type=Path)
    parser.add_argument("config", type=Path)
    parent = parser.add_mutually_exclusive_group()
    parent.add_argument("--parent-dir", type=Path)
    parent.add_argument("--root", type=Path)
    args = parser.parse_args()
    try:
        write_manifest(args.build_dir, args.config, parent_dir=args.parent_dir, root=args.root)
    except (ValueError, KeyError, TypeError, StopIteration, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"manifest: {error}\n")
