#!/usr/bin/env bash
# Export registered full intervals for the default universe.
SCRIPT_NAME=30_build_exports
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

[ "$#" -eq 2 ] || die "usage: 30_build_exports.sh <build-dir> <config.env>"
BUILD_DIR="$1"
source "$2"

python3 "$REPO_ROOT/src/lib/build_exports.py" --build-dir "$BUILD_DIR" --genome "$GENOME"
log "UCSC exports ready in $BUILD_DIR/exports/ucsc/interspersed/full"
