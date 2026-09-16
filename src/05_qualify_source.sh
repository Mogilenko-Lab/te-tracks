#!/usr/bin/env bash
# Qualify the primary records against the UCSC browser table.
SCRIPT_NAME=05_qualify
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

[ "$#" -eq 2 ] || die "usage: 05_qualify_source.sh <build-dir> <config.env>"
BUILD_DIR="$1"
CFG="$2"
source "$CFG"
[ "$RMSK_OUT_PROFILE" = rm_out_v1 ] || die "unsupported .out profile: $RMSK_OUT_PROFILE"

SRC="$BUILD_DIR/source"
rm -f "$SRC/qualification.md"
python3 "$REPO_ROOT/tools/qualify_source.py" \
  --out "$SRC/$(basename "$RMSK_OUT_URL")" \
  --table "$SRC/$(basename "$RMSK_TABLE_URL")" \
  --report "$SRC/qualification.md"
log "qualification ready in $SRC/qualification.md"
