#!/usr/bin/env bash
# Retain the pinned annotation and its child source declaration.
SCRIPT_NAME=00_fetch_gene
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/common.sh"
[ "$#" -eq 3 ] || die "usage: 00_fetch_gene_sources.sh <build-dir> <config.env> <parent-dir>"
BUILD_DIR="$1"
CFG="$2"
source "$CFG"
SRC="$BUILD_DIR/source"
mkdir -p "$SRC"
[[ "$GENE_GTF_MD5" =~ ^[0-9a-f]{32}$ ]] || die "invalid gene GTF md5 pin"
filename="$(basename "$GENE_GTF_URL")"
dest="$SRC/$filename"
cache="${TE_TRACKS_SOURCE_CACHE:-}/$filename"
if [ -n "${TE_TRACKS_SOURCE_CACHE:-}" ] && [ -f "$cache" ] && [ "$(md5_of "$cache")" = "$GENE_GTF_MD5" ]; then
  cp "$cache" "$dest"
  log "cache: $filename"
else
  fetch "$GENE_GTF_URL" "$dest"
fi
verify_md5 "$dest" "$GENE_GTF_MD5" >/dev/null
python3 "$REPO_ROOT/src/lib/gene_child.py" sources --build-dir "$BUILD_DIR" --config "$CFG" --parent-dir "$3"
