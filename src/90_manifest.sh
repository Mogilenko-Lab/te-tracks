#!/usr/bin/env bash
# Record the snapshot's provenance: source md5s, output md5s, row counts, builder version.
# A re-run over an existing snapshot leaves an existing manifest in place, so the recorded
# builder SHA keeps naming the version that produced the bytes.
SCRIPT_NAME=90_manifest
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

SNAP="${1:?usage: 90_manifest.sh <snapshot-dir> <config.env>}"
CFG="${2:?usage: 90_manifest.sh <snapshot-dir> <config.env>}"
# shellcheck disable=SC1090
source "$CFG"

MANIFEST="$SNAP/MANIFEST.json"
if [ -f "$MANIFEST" ]; then
  log "manifest present; provenance left intact"
  exit 0
fi

# Outputs are every delivered file, with source/ and dotfiles held aside.
mapfile -t OUTPUTS < <(cd "$SNAP" && find . -type f \
  -not -path './source/*' -not -name 'MANIFEST.json' -not -path './.work/*' \
  | sed 's|^\./||' | sort)

{
  printf '{\n'
  printf '  "family": "te_%s",\n' "$GENOME"
  printf '  "snapshot_tag": "%s",\n' "$(basename "$SNAP")"
  printf '  "built_at": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '  "assembly": "%s",\n' "$ASSEMBLY"
  printf '  "gene_annotation": "%s",\n' "$GENE_ANNOTATION"
  printf '  "produced_by": {\n'
  printf '    "repo": "te-tracks",\n'
  printf '    "git_sha": "%s",\n' "$(builder_sha)"
  printf '    "git_describe": "%s"\n' "$(builder_describe)"
  printf '  },\n'
  printf '  "policy": {\n'
  printf '    "te_classes": "%s",\n' "$TE_CLASSES"
  printf '    "exclude_family_prefix": "%s",\n' "$EXCLUDE_FAMILY_PREFIX"
  printf '    "locus_id_form": "%s",\n' "$LOCUS_ID_FORM"
  printf '    "intergenic_min": %s\n' "$INTERGENIC_MIN"
  printf '  },\n'
  printf '  "sources": %s,\n' "$(sed -n '/"sources"/,/^  }/p' "$SNAP/source/SOURCES.json" | sed '1s/.*"sources": //')"
  printf '  "counts": {\n'
  printf '    "loci": %s,\n' "$EXPECT_LOCI"
  printf '    "contigs": %s,\n' "$EXPECT_CONTIGS"
  printf '    "subfamilies": %s,\n' "$EXPECT_SUBFAMILIES"
  printf '    "triples": %s\n' "$EXPECT_TRIPLES"
  printf '  },\n'
  printf '  "outputs": {\n'
  local_first=1
  for f in "${OUTPUTS[@]}"; do
    [ "$local_first" -eq 1 ] && local_first=0 || printf ',\n'
    printf '    "%s": { "md5": "%s", "bytes": %s }' \
      "$f" "$(md5_of "$SNAP/$f")" "$(stat -c %s "$SNAP/$f")"
  done
  printf '\n  }\n}\n'
} > "$MANIFEST"

log "manifest written with ${#OUTPUTS[@]} outputs"
