#!/usr/bin/env bash
# Evaluate reviewed universe predicates over the complete catalog.
SCRIPT_NAME=15_build_universes
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

[ "$#" -eq 2 ] || die "usage: 15_build_universes.sh <build-dir> <config.env>"
BUILD_DIR="$1"
source "$2"

python3 "$REPO_ROOT/src/lib/build_universes.py" \
  --build-dir "$BUILD_DIR" \
  --class-set "$REPO_ROOT/config/${GENOME}.classes.tsv"
log "universes ready in $BUILD_DIR/universes.json"
