# Shared settings and helpers. Every script sources this first.

# Sort order stays identical across machines and locales.
export LC_ALL=C

# Shared caches stay group-writable.
umask 002

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log()  { printf '[%s] %s\n' "${SCRIPT_NAME:-te-tracks}" "$*" >&2; }
die()  { printf '[%s] FATAL %s\n' "${SCRIPT_NAME:-te-tracks}" "$*" >&2; exit 1; }

md5_of() { md5sum "$1" | cut -d' ' -f1; }

# Verify a file against an expected md5. An empty expectation records the observed value.
verify_md5() {  # verify_md5 <file> <expected|"">
  local f="$1" want="${2:-}" got
  got="$(md5_of "$f")"
  if [ -n "$want" ] && [ "$got" != "$want" ]; then
    die "md5 mismatch for $f: got $got, expected $want"
  fi
  printf '%s' "$got"
}

# Download to a .part file and rename on success, so an interrupted fetch leaves a re-runnable
# state and a later run repeats the download.
fetch() {  # fetch <url> <dest>
  local url="$1" dest="$2"
  [ -f "$dest" ] && { log "present: $(basename "$dest")"; return 0; }
  rm -f "$dest.part"
  log "fetch: $(basename "$dest")"
  curl -fsSL --retry 3 -o "$dest.part" "$url"
  mv "$dest.part" "$dest"
}
