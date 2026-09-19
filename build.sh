#!/usr/bin/env bash
# Build and verify a private directory, then install when a reference root is supplied.
export PYTHONDONTWRITEBYTECODE=1
SCRIPT_NAME=build
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

export TE_TRACKS_INVOCATION
TE_TRACKS_INVOCATION=$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "$0" "$@")
GENOME=""
BUILD_DIR=""
REFROOT=""
NO_SELECT=0
CHILD_FAMILY=""
PARENT_DIR=""
PARENT_BUILD_ID=""

usage() {
  cat <<'USAGE'
usage: build.sh --genome <name> --build-dir <dir>
       build.sh --genome <name> --root <refroot> [--no-select]
       build.sh --genome <name> --family gene --build-dir <dir> --parent-dir <core-build>
       build.sh --genome <name> --family gene --root <refroot> --parent-build-id <64-hex> [--no-select]

  --genome     a config present in config/<name>.env
  --build-dir  directory receiving the stages, manifest and verification
  --root       reference root receiving an immutable family archive
  --family     child config <genome>_<family>.env and stages src/<family>/
  --parent-dir explicit verified core build directory for a scratch child
  --parent-build-id full parent archive identity under the publication root
  --no-select  install the completed archive and preserve the current selection
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --genome|--build-dir|--root|--family|--parent-dir|--parent-build-id)
      [ "$#" -ge 2 ] && [ -n "$2" ] && [[ "$2" != --* ]] || { usage >&2; exit 2; }
      case "$1" in
        --genome) GENOME="$2" ;;
        --build-dir) BUILD_DIR="$2" ;;
        --root) REFROOT="$2" ;;
        --family) CHILD_FAMILY="$2" ;;
        --parent-dir) PARENT_DIR="$2" ;;
        --parent-build-id) PARENT_BUILD_ID="$2" ;;
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
if [ -n "$BUILD_DIR" ]; then
  while [[ "$BUILD_DIR" == */ ]]; do BUILD_DIR=${BUILD_DIR%/}; done
  BUILD_DIR=${BUILD_DIR:-/}
  [ ! -L "$BUILD_DIR" ] || { usage >&2; exit 2; }
fi
[[ "$GENOME" =~ ^[A-Za-z0-9_-]+$ ]] || die "invalid genome name: $GENOME"
if [ -n "$CHILD_FAMILY" ]; then
  [[ "$CHILD_FAMILY" =~ ^[A-Za-z0-9_-]+$ ]] || { usage >&2; exit 2; }
  if [ -n "$BUILD_DIR" ]; then
    [ -n "$PARENT_DIR" ] && [ -z "$PARENT_BUILD_ID" ] || { usage >&2; exit 2; }
    while [[ "$PARENT_DIR" == */ ]]; do PARENT_DIR=${PARENT_DIR%/}; done
    PARENT_DIR=${PARENT_DIR:-/}
    case "/$PARENT_DIR/" in */current/*) usage >&2; exit 2 ;; esac
    [ ! -L "$PARENT_DIR" ] || { usage >&2; exit 2; }
  else
    [ -z "$PARENT_DIR" ] && [[ "$PARENT_BUILD_ID" =~ ^[0-9a-f]{64}$ ]] || { usage >&2; exit 2; }
  fi
else
  [ -z "$PARENT_DIR" ] && [ -z "$PARENT_BUILD_ID" ] || { usage >&2; exit 2; }
fi
CFG="$REPO_ROOT/config/${GENOME}${CHILD_FAMILY:+_$CHILD_FAMILY}.env"
FAMILY_NAME="te_${GENOME}${CHILD_FAMILY:+_$CHILD_FAMILY}"
STAGE_DIR="$REPO_ROOT/src${CHILD_FAMILY:+/$CHILD_FAMILY}"
parent_args=()
[ -f "$CFG" ] || die "no config for genome '$GENOME' at $CFG"
if [ -n "$CHILD_FAMILY" ]; then
  expected_parent=$(bash -eu -c 'source "$1"; printf "%s" "$PARENT_FAMILY"' child-config "$CFG")
  if [ -n "$REFROOT" ]; then
    PARENT_DIR="$(realpath -m -- "$REFROOT")/$expected_parent/archive/$PARENT_BUILD_ID"
  fi
  if [ -n "$BUILD_DIR" ]; then
    child_target=$(realpath -m -- "$BUILD_DIR")
    parent_target=$(realpath -m -- "$PARENT_DIR")
    case "$child_target/" in "$parent_target/"*) die "child build-dir overlaps parent directory" ;; esac
    case "$parent_target/" in "$child_target/"*) die "parent directory is inside child build-dir" ;; esac
  fi
  PARENT_DIR=$(realpath -m -- "$PARENT_DIR")
  python3 "$REPO_ROOT/src/lib/gene_child.py" parent --parent-dir "$PARENT_DIR" --config "$CFG"
  if [ -n "$PARENT_BUILD_ID" ]; then
    [ "$(cat "$PARENT_DIR/BUILD_ID")" = "$PARENT_BUILD_ID" ] || die "parent BUILD_ID differs"
  fi
  parent_args=(--parent-dir "$PARENT_DIR")
fi
if [ -n "$REFROOT" ]; then
  REFROOT=$(realpath -m -- "$REFROOT")
  FAMILY="$REFROOT/$FAMILY_NAME"
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

if [ -n "$CHILD_FAMILY" ]; then
  RSS_FILE=$(mktemp "$BUILD_DIR/.stage-metrics.XXXXXXXX")
else
  RSS_FILE=$(mktemp)
fi
trap 'rm -f "$RSS_FILE"' EXIT
log "genome=$GENOME  build_dir=$BUILD_DIR"
for stage in "$STAGE_DIR"/[0-9][0-9]_*.sh; do
  log "running $(basename "$stage")"
  if [ -n "$CHILD_FAMILY" ]; then
    python3 - "$stage" "$BUILD_DIR" "$CFG" "$PARENT_DIR" "$RSS_FILE" <<'PYMETRICS'
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

started = time.perf_counter()
result = subprocess.run(["bash", *sys.argv[1:5]])
measurement = {"stage": Path(sys.argv[1]).name, "wall_seconds": round(time.perf_counter() - started, 3),
               "peak_rss_bytes": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024}
with Path(sys.argv[5]).open("a") as stream:
    stream.write(json.dumps(measurement) + "\n")
print("stage_metrics " + json.dumps(measurement), flush=True)
raise SystemExit(result.returncode)
PYMETRICS
  elif [[ "$(basename "$stage")" == 30_* ]]; then
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
if [ -n "$CHILD_FAMILY" ]; then
  export TE_TRACKS_CHILD_STAGE_METRICS
  TE_TRACKS_CHILD_STAGE_METRICS=$(python3 -c 'import json,sys; print(json.dumps([json.loads(s) for s in open(sys.argv[1])]))' "$RSS_FILE")
  TE_TRACKS_EXPORT_PEAK_RSS_BYTES=$(python3 -c 'import json,sys; print(max(x["peak_rss_bytes"] for x in json.loads(sys.argv[1])))' "$TE_TRACKS_CHILD_STAGE_METRICS")
else
  TE_TRACKS_EXPORT_PEAK_RSS_BYTES=$(cat "$RSS_FILE")
fi
[ -z "$CHILD_FAMILY" ] || rm -f "$RSS_FILE"
python3 "$REPO_ROOT/src/90_manifest.py" "$BUILD_DIR" "$CFG" "${parent_args[@]}"
python3 "$REPO_ROOT/src/99_verify.py" "$BUILD_DIR" "${parent_args[@]}"
if [ -n "$REFROOT" ]; then
  selection=()
  [ "$NO_SELECT" -eq 1 ] || selection=(--select)
  python3 "$REPO_ROOT/src/release.py" install --root "$REFROOT" --family "$FAMILY_NAME" \
    --staging "$BUILD_DIR" "${selection[@]}"
fi
log "done"
