#!/usr/bin/env bash
# Project pinned Dfam models into lineage, rank and clade tables.
SCRIPT_NAME=25_build_dfam
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

[ "$#" -eq 2 ] || die "usage: 25_build_dfam.sh <build-dir> <config.env>"
BUILD_DIR="$1"
source "$2"
python3 "$REPO_ROOT/src/lib/build_dfam.py" --build-dir "$BUILD_DIR" \
  --snapshot "$BUILD_DIR/source/$(basename "$DFAM_SNAPSHOT_PATH")"
