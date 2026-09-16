#!/usr/bin/env bash
# Run the registered build stages in numeric order.
SCRIPT_NAME=build
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

GENOME=""
BUILD_DIR=""

usage() {
  cat <<'USAGE'
usage: build.sh --genome <name> --build-dir <dir>

  --genome     a config present in config/<name>.env
  --build-dir  directory receiving the registered stages' outputs
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --genome|--build-dir)
      [ "$#" -ge 2 ] && [ -n "$2" ] && [[ "$2" != --* ]] || { usage >&2; exit 2; }
      case "$1" in
        --genome) GENOME="$2" ;;
        --build-dir) BUILD_DIR="$2" ;;
      esac
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

[ -n "$GENOME" ] && [ -n "$BUILD_DIR" ] || { usage >&2; exit 2; }
[[ "$GENOME" =~ ^[A-Za-z0-9_-]+$ ]] || die "invalid genome name: $GENOME"
CFG="$REPO_ROOT/config/${GENOME}.env"
[ -f "$CFG" ] || die "no config for genome '$GENOME' at $CFG"
BUILD_DIR=$(realpath -m -- "$BUILD_DIR")
mkdir -p "$BUILD_DIR"

log "genome=$GENOME  build_dir=$BUILD_DIR"
for stage in "$REPO_ROOT"/src/[0-9][0-9]_*.sh; do
  log "running $(basename "$stage")"
  bash "$stage" "$BUILD_DIR" "$CFG"
done
log "done"
