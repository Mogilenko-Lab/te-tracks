# Provenance

The tracks derive from UCSC's RepeatMasker run. This file records the rule and the evidence that the
rule reproduces the annotation the lab has been using.

## The rule

```
UCSC <genome>/database/rmsk.txt.gz
  1. carry repClass in {SINE LTR LINE DNA Satellite Retroposon Unknown RC Unspecified DNA?}
  2. carry repFamily outside the source-RNA-named families (repFamily !~ ^tRNA)
  3. start = genoStart + 1          rmsk is 0-based half-open; the table is 1-based inclusive
  4. gene hierarchy = repName (subfamily), repFamily (family), repClass (class)
  5. contig names map through <genome>.chromAlias.txt for the Ensembl-named views
```

Rule 1 carries `Satellite`, so "TE" in these tracks means "interspersed repeat plus satellite". It
also holds the Pol III and structural-RNA classes out, `tRNA` among them, so mm39's 3,508 annotated
tRNA genes stay outside the TE set.

Rule 2 removes 2,548 SINE records in mm39, one subfamily per family: `tRNA` → `LFSINE_Vert` 1,235,
`tRNA-RTE` → `MamSINE1` 925, `tRNA-Deu` → `AmnSINE2` 388. It selects on RepeatMasker nomenclature,
and `docs/DECISIONS.md` records its standing.

Rule 1 is a whitelist and the snippet under "Reproducing this" is the complementary blacklist. Both
yield 3,799,629 records against the current class census, measured. The whitelist is the rule in
force, so a class new to a future `rmsk` release arrives excluded and surfaces in `99_verify.sh`.

## Evidence, mm39

Measured 2026-09-12 against `GRCm39_Ensembl_rmsk_TE.gtf.gz`
(md5 `1d6770be131fc1b47402a633f4401cbd`), the TEtranscripts-packaged file that produced 13036-DM,
14839-DM and the earlier Yasmine analysis.

**The locus set is identical.** Both sides hold **3,799,629 records** across **59 contigs**, and they
join **1:1 on coordinates**. A record-level comparison on chr1 covers **266,428 records** with every
coordinate, strand, family and class matching.

**Per-class counts agree on nine of ten classes.** The tenth explains exactly:

| Class | rmsk | packaged |
|---|---|---|
| SINE | 1,495,172 | 1,492,624 → the 2,548 records removed by rule 2 |
| LTR | 1,105,064 | equal |
| LINE | 976,368 | equal |
| DNA | 164,783 | equal |
| Satellite | 37,228 | equal |
| Retroposon | 17,253 | equal |
| Unknown | 5,786 | equal |
| RC | 416 | equal |
| Unspecified | 98 | equal |
| DNA? | 9 | equal |

## Where the labels differ

The packaged file applies two transformations to the hierarchy. These tracks carry the rmsk values.

**A character substitution, applied partially.** Lowercase `v` appears as `.` in some records and
survives in others, so one RepeatMasker name arrives as two identities:

| RepeatMasker | Packaged | Records |
|---|---|---|
| subfamily `ID4_v` | `ID4_.` and `ID4_v` | 25,263 and 17 |
| subfamily `LTR33A_v` | `LTR33A_.` | 432 |
| subfamily `MER34C_v` | `MER34C_.` | 328 |
| family `RTE-BovB` | `RTE-Bo.B` and `RTE-BovB` | 4,239 and 9 |

**A family relabelling for unclassified repeats.** Where rmsk records `repFamily = Unknown`, the
packaged file writes the subfamily name as the family — `UCON1:Unknown:Unknown` arrives as
`UCON1:UCON1:Unknown`. This keeps family-level rollups distinct for unclassified repeats, and it is
a reasonable choice. These tracks keep `Unknown`, and `te_dim.tsv` supplies the rollup instead.

**Label counts follow from those two transformations.**

| | these tracks | packaged |
|---|---|---|
| subfamilies | 1,225 | 1,226 |
| `subfamily:family:class` triples | 1,245 | 1,243 |

Four records out of 3,799,629 carry a class difference (two `LTR`↔`SINE` each way). The cause is
open, and the magnitude places it below any analysis threshold. A full label-level reconciliation
against the packaged file stays deferred; the locus-set and coordinate identity above is what the
migration rests on.

## Migrating results that used the packaged annotation

`ID4_.` and `ID4_v` name one subfamily. `LTR33A_.`, `MER34C_.` and family `RTE-Bo.B` carry the
substitution. Any comparison against 13036-DM, 14839-DM or the earlier Yasmine matrices maps those
names first, and `rename_map.tsv` in each snapshot carries the mapping.

## Reproducing this

```
curl -sL -o rmsk.txt.gz https://hgdownload.soe.ucsc.edu/goldenPath/mm39/database/rmsk.txt.gz
zcat rmsk.txt.gz | awk -F'\t' '
  $12!="Simple_repeat" && $12!="Low_complexity" && $12!="scRNA" && $12!="snRNA" &&
  $12!="tRNA" && $12!="rRNA" && $12!="srpRNA" && $13!~/^tRNA/' | wc -l     # 3799629
```
