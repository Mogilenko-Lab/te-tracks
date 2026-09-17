#!/usr/bin/env bash
# Build and verify a private directory, then install when a reference root is supplied.
SCRIPT_NAME=build
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

export TE_TRACKS_INVOCATION
TE_TRACKS_INVOCATION=$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "$0" "$@")
GENOME=""
BUILD_DIR=""
REFROOT=""
NO_SELECT=0

usage() {
  cat <<'USAGE'
usage: build.sh --genome <name> --build-dir <dir>
       build.sh --genome <name> --root <refroot> [--no-select]

  --genome     a config present in config/<name>.env
  --build-dir  directory receiving the stages, manifest and verification
  --root       reference root receiving an immutable family archive
  --no-select  install the completed archive and preserve the current selection
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --genome|--build-dir|--root)
      [ "$#" -ge 2 ] && [ -n "$2" ] && [[ "$2" != --* ]] || { usage >&2; exit 2; }
      case "$1" in
        --genome) GENOME="$2" ;;
        --build-dir) BUILD_DIR="$2" ;;
        --root) REFROOT="$2" ;;
      esac
      shift 2
      ;;
    --no-select) NO_SELECT=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

[ -n "$GENOME" ] || { usage >&2; exit 2; }
if { [ -z "$BUILD_DIR" ] && [ -z "$REFROOT" ]; } || { [ -n "$BUILD_DIR" ] && [ -n "$REFROOT" ]; }; then
  usage >&2
  exit 2
fi
[ "$NO_SELECT" -eq 0 ] || [ -n "$REFROOT" ] || { usage >&2; exit 2; }
[[ "$GENOME" =~ ^[A-Za-z0-9_-]+$ ]] || die "invalid genome name: $GENOME"
CFG="$REPO_ROOT/config/${GENOME}.env"
[ -f "$CFG" ] || die "no config for genome '$GENOME' at $CFG"
if [ -n "$REFROOT" ]; then
  REFROOT=$(realpath -m -- "$REFROOT")
  FAMILY="$REFROOT/te_$GENOME"
  [ ! -L "$FAMILY" ] && [ ! -L "$FAMILY/.staging" ] || die "family and staging roots require directories"
  mkdir -p "$FAMILY/.staging"
  BUILD_DIR=$(mktemp -d "$FAMILY/.staging/build.XXXXXXXX")
else
  BUILD_DIR=$(realpath -m -- "$BUILD_DIR")
  case "$BUILD_DIR/" in
    */archive/*) die "build-dir is inside an archive: $BUILD_DIR" ;;
  esac
  mkdir -p "$BUILD_DIR"
fi

RSS_FILE=$(mktemp)
trap 'rm -f "$RSS_FILE"' EXIT
log "genome=$GENOME  build_dir=$BUILD_DIR"
for stage in "$REPO_ROOT"/src/[0-9][0-9]_*.sh; do
  log "running $(basename "$stage")"
  if [[ "$(basename "$stage")" == 30_* ]]; then
    python3 - "$stage" "$BUILD_DIR" "$CFG" "$RSS_FILE" <<'PY'
import resource
import subprocess
import sys
from pathlib import Path

result = subprocess.run(["bash", *sys.argv[1:4]])
Path(sys.argv[4]).write_text(str(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024))
raise SystemExit(result.returncode)
PY
  else
    bash "$stage" "$BUILD_DIR" "$CFG"
  fi
done
export TE_TRACKS_EXPORT_PEAK_RSS_BYTES
TE_TRACKS_EXPORT_PEAK_RSS_BYTES=$(cat "$RSS_FILE")
python3 "$REPO_ROOT/src/90_manifest.py" "$BUILD_DIR" "$CFG"
python3 "$REPO_ROOT/src/99_verify.py" "$BUILD_DIR"
if [ -n "$REFROOT" ]; then
  selection=()
  [ "$NO_SELECT" -eq 1 ] || selection=(--select)
  python3 "$REPO_ROOT/src/release.py" install --root "$REFROOT" --family "te_$GENOME" \
    --staging "$BUILD_DIR" "${selection[@]}"
fi
log "done"
