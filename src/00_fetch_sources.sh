#!/usr/bin/env bash
# Fetch the pinned sources into the snapshot's source/ directory and record their md5s.
SCRIPT_NAME=00_fetch
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

SNAP="${1:?usage: 00_fetch_sources.sh <snapshot-dir> <config.env>}"
CFG="${2:?usage: 00_fetch_sources.sh <snapshot-dir> <config.env>}"
# shellcheck disable=SC1090
source "$CFG"

SRC="$SNAP/source"
mkdir -p "$SRC"

fetch "$RMSK_URL"       "$SRC/rmsk.txt.gz"
fetch "$CHROMALIAS_URL" "$SRC/chromAlias.txt"
fetch "$GENE_GTF_URL"   "$SRC/$(basename "$GENE_GTF_URL")"

RMSK_OBSERVED="$(verify_md5 "$SRC/rmsk.txt.gz" "$RMSK_MD5")"
ALIAS_OBSERVED="$(verify_md5 "$SRC/chromAlias.txt" "$CHROMALIAS_MD5")"
GTF_OBSERVED="$(verify_md5 "$SRC/$(basename "$GENE_GTF_URL")" "$GENE_GTF_MD5")"

# The source md5s become the provenance of every derived track.
cat > "$SRC/SOURCES.json" <<JSON
{
  "genome": "$GENOME",
  "assembly": "$ASSEMBLY",
  "gene_annotation": "$GENE_ANNOTATION",
  "sources": {
    "rmsk":        { "url": "$RMSK_URL",       "md5": "$RMSK_OBSERVED" },
    "chromAlias":  { "url": "$CHROMALIAS_URL", "md5": "$ALIAS_OBSERVED" },
    "gene_gtf":    { "url": "$GENE_GTF_URL",   "md5": "$GTF_OBSERVED" }
  }
}
JSON

log "sources ready in $SRC"
