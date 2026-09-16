#!/usr/bin/env bash
# Build the complete record catalog and source identity relations.
SCRIPT_NAME=10_build_records
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

[ "$#" -eq 2 ] || die "usage: 10_build_records.sh <build-dir> <config.env>"
BUILD_DIR="$1"
source "$2"
[ "$RMSK_OUT_PROFILE" = rm_out_v1 ] || die "unsupported .out profile: $RMSK_OUT_PROFILE"

python3 "$REPO_ROOT/src/lib/build_records.py" \
  --out "$BUILD_DIR/source/$(basename "$RMSK_OUT_URL")" \
  --table "$BUILD_DIR/source/$(basename "$RMSK_TABLE_URL")" \
  --sizes "$BUILD_DIR/source/$(basename "$CHROM_SIZES_URL")" \
  --tables-dir "$BUILD_DIR/tables"
log "canonical tables ready in $BUILD_DIR/tables"
