#!/usr/bin/env bash
# Derive canonical taxonomy from the source labels and record divergences.
SCRIPT_NAME=20_build_taxonomy
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

[ "$#" -eq 2 ] || die "usage: 20_build_taxonomy.sh <build-dir> <config.env>"
BUILD_DIR="$1"
source "$2"

python3 "$REPO_ROOT/src/lib/build_taxonomy.py" --build-dir "$BUILD_DIR"
log "canonical taxonomy ready in $BUILD_DIR/tables"
