#!/usr/bin/env bash
# Publish a snapshot under a content-addressed BUILD_ID, and keep every earlier build reachable.
#
# BUILD_ID is a sha256 over the md5 of every output, so it names the content and nothing else.
# Two builds from the same sources carry the same BUILD_ID, which is what makes a re-run a no-op.
# A build that changes any output carries a new BUILD_ID, the previous snapshot moves into
# archive/, and INDEX.tsv records both. Projects cite a BUILD_ID and get exactly those bytes.
SCRIPT_NAME=release
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

SNAP="${1:?usage: release.sh <snapshot-dir> <config.env>}"
CFG="${2:?usage: release.sh <snapshot-dir> <config.env>}"
# shellcheck disable=SC1090
source "$CFG"

FAMILY="$(dirname "$SNAP")"
ARCHIVE="$FAMILY/archive"
INDEX="$FAMILY/INDEX.tsv"
mkdir -p "$ARCHIVE"

# The fingerprint covers the delivered outputs. source/, the manifest and the id file stay out,
# so a re-download or a fresh timestamp leaves the fingerprint untouched.
compute_build_id() {  # compute_build_id <snapshot-dir>
  local d="$1"
  (cd "$d" && find . -type f \
      -not -path './source/*' -not -path './.work/*' \
      -not -name 'MANIFEST.json' -not -name 'BUILD_ID' \
    | sed 's|^\./||' | sort \
    | while read -r f; do printf '%s  %s\n' "$(md5sum "$f" | cut -d' ' -f1)" "$f"; done) \
  | sha256sum | cut -c1-64
}

BUILD_ID="$(compute_build_id "$SNAP")"
BUILD_SHORT="${BUILD_ID:0:12}"
log "BUILD_ID $BUILD_ID"

printf '%s\n' "$BUILD_ID" > "$SNAP/BUILD_ID"

CURRENT="$FAMILY/current"
SNAP_NAME="$(basename "$SNAP")"

# An identical fingerprint means the sources and the logic both produced the same annotation.
# The published snapshot stays where it is, and the redundant directory goes away.
if [ -L "$CURRENT" ]; then
  CUR_TARGET="$(readlink "$CURRENT")"
  CUR_DIR="$FAMILY/$CUR_TARGET"
  if [ -f "$CUR_DIR/BUILD_ID" ] && [ "$CUR_TARGET" != "$SNAP_NAME" ]; then
    CUR_ID="$(cat "$CUR_DIR/BUILD_ID")"
    if [ "$CUR_ID" = "$BUILD_ID" ]; then
      log "content matches current ($CUR_TARGET); removing the redundant snapshot $SNAP_NAME"
      rm -rf "$SNAP"
      printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$BUILD_ID" "$CUR_TARGET" "reconfirmed" "$(builder_describe)" >> "$INDEX"
      log "current stays at $CUR_TARGET"
      exit 0
    fi
    log "content differs from current ($CUR_ID); archiving $CUR_TARGET"
    mv "$CUR_DIR" "$ARCHIVE/${CUR_TARGET}__${CUR_ID:0:12}"
    printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$CUR_ID" "archive/${CUR_TARGET}__${CUR_ID:0:12}" "archived" "-" >> "$INDEX"
  fi
fi

[ -f "$INDEX" ] || printf 'recorded_at\tbuild_id\tpath\tstatus\tbuilder\n' > "$INDEX"
ln -sfn "$SNAP_NAME" "$CURRENT"
printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$BUILD_ID" "$SNAP_NAME" "current" "$(builder_describe)" >> "$INDEX"

# A short, greppable pointer for consumers that read one file.
printf 'build_id\t%s\nsnapshot\t%s\nbuilt_at\t%s\nbuilder\t%s\n' \
  "$BUILD_ID" "$SNAP_NAME" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(builder_describe)" \
  > "$FAMILY/CURRENT_BUILD.tsv"

log "current -> $SNAP_NAME  build_id ${BUILD_SHORT}"
