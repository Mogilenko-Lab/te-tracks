#!/usr/bin/env bash
# Build the canonical table: one row per TE locus, with a stable locus_id.
# Every delivered track is a projection of this file.
SCRIPT_NAME=10_master
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

SNAP="${1:?usage: 10_build_master.sh <snapshot-dir> <config.env>}"
CFG="${2:?usage: 10_build_master.sh <snapshot-dir> <config.env>}"
# shellcheck disable=SC1090
source "$CFG"

SRC="$SNAP/source"
OUT="$SNAP/te_loci.tsv"
WORK="$SNAP/.work"
mkdir -p "$WORK"

# rmsk column order: 1 bin, 2 swScore, 3 milliDiv, 4 milliDel, 5 milliIns, 6 genoName,
# 7 genoStart, 8 genoEnd, 9 genoLeft, 10 strand, 11 repName, 12 repClass, 13 repFamily,
# 14 repStart, 15 repEnd, 16 repLeft, 17 id
#
# Two filters define the TE set, and together they reproduce the annotation the lab has used:
# carried classes, and the exclusion of tRNA-derived SINE families.
# genoStart is 0-based, so the table start is genoStart + 1.
log "selecting the TE set from rmsk"
zcat "$SRC/rmsk.txt.gz" \
| awk -F'\t' -v classes="$TE_CLASSES" -v fampfx="$EXCLUDE_FAMILY_PREFIX" 'BEGIN{
    n = split(classes, a, " "); for (i = 1; i <= n; i++) keep[a[i]] = 1
  }
  ($12 in keep) && ($13 !~ "^" fampfx) {
    printf "%s\t%d\t%d\t%s\t%s\t%s\t%s\t%d\t%.1f\t%.1f\t%.1f\t%d\n", \
           $6, $7 + 1, $8, $10, $11, $13, $12, $2, $3/10, $4/10, $5/10, $17
  }' \
| sort -k1,1 -k2,2n -k3,3n -k4,4 -k5,5 > "$WORK/te_sorted.tsv"

# locus_id is coordinate-derived, so it survives any change to the filters above.
# dup_index travels beside it for tools that expect subfamily_dupN naming.
log "assigning locus_id and dup_index"
{
  printf 'locus_id\tchrom\tstart\tend\tstrand\tsubfamily\tfamily\tclass\tsw_score\tperc_div\tperc_del\tperc_ins\trmsk_id\tlength_bp\tdup_index\n'
  awk -F'\t' -v form="$LOCUS_ID_FORM" 'BEGIN{OFS="\t"}
    {
      chrom=$1; start=$2; end=$3; strand=$4; sfam=$5; fam=$6; cls=$7
      sw=$8; pdiv=$9; pdel=$10; pins=$11; rid=$12
      dup[sfam]++
      if (form == "selfdesc") lid = sfam "|" chrom ":" start "-" end "|" strand
      else                    lid = sfam "_dup" dup[sfam]
      print lid, chrom, start, end, strand, sfam, fam, cls, sw, pdiv, pdel, pins, rid, end - start + 1, dup[sfam]
    }' "$WORK/te_sorted.tsv"
} > "$OUT"

# The dimension table carries the hierarchy, so views hold only the key.
log "writing the dimension table"
{
  printf 'subfamily\tfamily\tclass\tn_loci\ttotal_bp\n'
  awk -F'\t' 'NR>1{k=$6"\t"$7"\t"$8; n[k]++; bp[k]+=$14} END{for (k in n) print k"\t"n[k]"\t"bp[k]}' "$OUT" \
  | sort -k1,1 -k2,2 -k3,3
} > "$SNAP/te_dim.tsv"

LOCI=$(( $(wc -l < "$OUT") - 1 ))
assert_count "loci" "$LOCI" "$EXPECT_LOCI"
assert_count "contigs" "$(awk -F'\t' 'NR>1{print $2}' "$OUT" | sort -u | wc -l)" "$EXPECT_CONTIGS"
assert_count "subfamilies" "$(awk -F'\t' 'NR>1{print $6}' "$OUT" | sort -u | wc -l)" "$EXPECT_SUBFAMILIES"
assert_count "triples" "$(( $(wc -l < "$SNAP/te_dim.tsv") - 1 ))" "$EXPECT_TRIPLES"

gzip -nf "$OUT"        # -n keeps the gzip header timestamp-free, so re-runs match byte for byte
rm -rf "$WORK"
log "canonical table ready: $(basename "$OUT").gz"
