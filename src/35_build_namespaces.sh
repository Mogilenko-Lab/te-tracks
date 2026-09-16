#!/usr/bin/env bash
# Publish contig aliases, coverage and renamed exports.
SCRIPT_NAME=35_build_namespaces
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

[ "$#" -eq 2 ] || die "usage: 35_build_namespaces.sh <build-dir> <config.env>"
BUILD_DIR="$1"
source "$2"

python3 "$REPO_ROOT/src/lib/contigs.py" --build-dir "$BUILD_DIR" --genome "$GENOME"
log "Contig namespaces ready in $BUILD_DIR/exports"
