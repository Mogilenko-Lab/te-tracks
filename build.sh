#!/usr/bin/env bash
# Build a dated snapshot of the TE tracks and point `current` at it.
#
# Stages live in src/ and run in numeric order. Adding a stage requires no change here.
SCRIPT_NAME=build
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

GENOME=""
DEST=""
DATE=""

usage() {
  cat <<'USAGE'
usage: build.sh --genome <name> --dest <refroot> [--date YYYYMMDD]

  --genome   a config present in config/<name>.env  (mm39 today)
  --dest     reference root; the snapshot lands at <refroot>/te_<genome>/te_<genome>_<date>/
  --date     snapshot tag; defaults to today in UTC

Roots in use:
  local   /data2/users/shared/refcache
  CRI     /gpfs/data/rathmell-lab/data/refdata
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --genome) GENOME="$2"; shift 2 ;;
    --dest)   DEST="$2";   shift 2 ;;
    --date)   DATE="$2";   shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$GENOME" ] || { usage; die "--genome is required"; }
[ -n "$DEST" ]   || { usage; die "--dest is required"; }
DATE="${DATE:-$(date -u +%Y%m%d)}"

CFG="$REPO_ROOT/config/${GENOME}.env"
[ -f "$CFG" ] || die "no config for genome '$GENOME' at $CFG"

FAMILY="$DEST/te_${GENOME}"
SNAP="$FAMILY/te_${GENOME}_${DATE}"
mkdir -p "$SNAP"

log "genome=$GENOME  snapshot=$SNAP  builder=$(builder_describe)"

for stage in "$REPO_ROOT"/src/[0-9][0-9]_*.sh; do
  log "--- $(basename "$stage") ---"
  bash "$stage" "$SNAP" "$CFG"
done

# Publication is content-addressed, so it runs after the stages and owns the `current` symlink.
log "--- release.sh ---"
bash "$REPO_ROOT/src/release.sh" "$SNAP" "$CFG"
log "done"
