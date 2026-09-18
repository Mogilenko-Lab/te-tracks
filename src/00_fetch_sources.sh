#!/usr/bin/env bash
# Retain checksum-verified sources and their declared provenance.
SCRIPT_NAME=00_fetch
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

[ "$#" -eq 2 ] || die "usage: 00_fetch_sources.sh <build-dir> <config.env>"
BUILD_DIR="$1"
CFG="$2"
source "$CFG"

SRC="$BUILD_DIR/source"
mkdir -p "$SRC"
rm -f "$SRC/SOURCES.json"

source_keys=(rmsk_out rmsk_table chromAlias chrom_sizes)
source_urls=("$RMSK_OUT_URL" "$RMSK_TABLE_URL" "$CHROMALIAS_URL" "$CHROM_SIZES_URL")
source_md5s=("$RMSK_OUT_MD5" "$RMSK_TABLE_MD5" "$CHROMALIAS_MD5" "$CHROM_SIZES_MD5")
source_metadata=()

for i in "${!source_keys[@]}"; do
  url="${source_urls[$i]}"
  pin="${source_md5s[$i]}"
  [[ "$pin" =~ ^[0-9a-f]{32}$ ]] || die "invalid md5 pin for $url"
  filename="$(basename "$url")"
  dest="$SRC/$filename"
  cache="${TE_TRACKS_SOURCE_CACHE:-}/$filename"
  if [ -n "${TE_TRACKS_SOURCE_CACHE:-}" ] && [ -f "$cache" ] && [ "$(md5_of "$cache")" = "$pin" ]; then
    # Keep retained source bytes independent of the cache.
    rm -f "$dest"
    cp "$cache" "$dest"
    log "cache: $filename"
  else
    fetch "$url" "$dest"
  fi
  observed="$(verify_md5 "$dest" "$pin")"
  source_metadata+=("${source_keys[$i]}" "$url" "$observed" "$dest")
done

python3 - "$SRC/SOURCES.json" "$GENOME" "$ASSEMBLY" \
  "$RM_VERSION" "$RM_LIBRARY" "$RM_RUN_EVIDENCE" "$RMSK_OUT_PROFILE" \
  "$GENOME_FA_URL" "$GENOME_FA_MD5" "$REPO_ROOT" "$DFAM_SNAPSHOT_PATH" "$DFAM_SNAPSHOT_SHA256" \
  "$DFAM_PROVENANCE_SHA256" "${source_metadata[@]}" <<'PY'
import json
import hashlib
import shutil
import sys
from pathlib import Path

output, genome, assembly, version, library, evidence, profile, fa_url, fa_md5, repo, tracked, pin, provenance_pin, *items = sys.argv[1:]
sources = {}
for i in range(0, len(items), 4):
    key, url, md5, path = items[i:i + 4]
    sources[key] = {"url": url, "md5": md5, "bytes": Path(path).stat().st_size}
payload = Path(repo) / tracked
with payload.open("rb") as stream:
    observed = hashlib.file_digest(stream, "sha256").hexdigest()
if observed != pin:
    raise SystemExit(f"dfam_snapshot sha256 mismatch: {tracked}: {observed} != {pin}")
provenance = payload.with_suffix("").with_suffix(".provenance.json")
with provenance.open("rb") as stream:
    provenance_observed = hashlib.file_digest(stream, "sha256").hexdigest()
if provenance_observed != provenance_pin:
    raise SystemExit(f"dfam_provenance sha256 mismatch: {provenance}: {provenance_observed} != {provenance_pin}")
shutil.copyfile(payload, Path(output).parent / payload.name)
shutil.copyfile(provenance, Path(output).parent / provenance.name)
sources["dfam_snapshot"] = {"path": tracked, "sha256": observed, "bytes": payload.stat().st_size}
metadata = {
    "genome": genome,
    "assembly": assembly,
    "declared_assembly": {"genome_fa_url": fa_url, "genome_fa_md5": fa_md5, "status": "declared"},
    "rm_version": version,
    "rm_library": library,
    "rm_run_evidence": evidence,
    "rmsk_out_profile": profile,
    "sources": sources,
}
Path(output).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
PY

log "sources ready in $SRC"
