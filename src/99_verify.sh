#!/usr/bin/env bash
# Verify a snapshot against its manifest and its expected shape.
# Run it after a build, and after any transfer to another reference root.
SCRIPT_NAME=99_verify
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

SNAP="${1:?usage: 99_verify.sh <snapshot-dir> <config.env>}"
CFG="${2:?usage: 99_verify.sh <snapshot-dir> <config.env>}"
# shellcheck disable=SC1090
source "$CFG"

MANIFEST="$SNAP/MANIFEST.json"
[ -f "$MANIFEST" ] || die "no manifest at $MANIFEST"

# Every recorded output is present and carries its recorded md5.
log "checking output md5s against the manifest"
python3 - "$SNAP" <<'PY'
import json, hashlib, os, sys
snap = sys.argv[1]
man = json.load(open(os.path.join(snap, "MANIFEST.json")))
bad = 0
for name, rec in man["outputs"].items():
    p = os.path.join(snap, name)
    if not os.path.exists(p):
        print("MISSING %s" % name); bad += 1; continue
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    if h.hexdigest() != rec["md5"]:
        print("MD5 %s got %s want %s" % (name, h.hexdigest(), rec["md5"])); bad += 1
print("checked %d outputs, %d problems" % (len(man["outputs"]), bad))
sys.exit(1 if bad else 0)
PY

# The canonical table holds the shape the config declares.
TBL="$SNAP/te_loci.tsv.gz"
[ -f "$TBL" ] || die "no canonical table at $TBL"
log "checking canonical shape"
assert_count "loci"        "$(( $(zcat "$TBL" | wc -l) - 1 ))" "$EXPECT_LOCI"
assert_count "contigs"     "$(zcat "$TBL" | awk -F'\t' 'NR>1{print $2}' | sort -u | wc -l)" "$EXPECT_CONTIGS"
assert_count "subfamilies" "$(zcat "$TBL" | awk -F'\t' 'NR>1{print $6}' | sort -u | wc -l)" "$EXPECT_SUBFAMILIES"
assert_count "triples"     "$(( $(wc -l < "$SNAP/te_dim.tsv") - 1 ))" "$EXPECT_TRIPLES"

# locus_id is the join key, so uniqueness is a hard requirement.
UNIQ=$(zcat "$TBL" | awk -F'\t' 'NR>1{print $1}' | sort -u | wc -l)
assert_count "unique locus_id" "$UNIQ" "$EXPECT_LOCI"

# Per-class counts guard against a silent change in the source or the filter.
if [ -f "$REPO_ROOT/tests/expectations/${GENOME}_class_counts.tsv" ]; then
  log "checking per-class counts"
  zcat "$TBL" | awk -F'\t' 'NR>1{c[$8]++} END{for (k in c) print k"\t"c[k]}' | sort -k1,1 \
    > "$SNAP/.class_observed.tsv"
  diff "$REPO_ROOT/tests/expectations/${GENOME}_class_counts.tsv" "$SNAP/.class_observed.tsv" \
    && log "ok per-class counts" \
    || die "per-class counts differ from tests/expectations/${GENOME}_class_counts.tsv"
  rm -f "$SNAP/.class_observed.tsv"
fi

log "snapshot verified"
