# te-tracks audit — 2026-09-15 (in-container, builder 6ff3ee9)

Every number below was measured in this session from the pinned sources; nothing is copied from
the repository's own documentation. Scratch root: `_scratch/te-tracks-audit/` (source/, refroot/,
report/, build_run*.log).

## 1. What exists on disk

- `/data2/users/shared/refcache/te_mm39/` does not exist. No te-tracks build has been published.
  The refcache mount is read-only inside the container; builds run on the host.
- `refcache/mm39/mm39_20260911/` (the older `mm39-updater` family) holds the GENCODE vM37 GTF,
  the GRCm39 FASTA and the TEtranscripts packaged `GRCm39_Ensembl_rmsk_TE.gtf.gz`.
- A build into scratch produces exactly: `te_loci.tsv.gz`, `te_dim.tsv`, `MANIFEST.json`,
  `BUILD_ID`, `source/`. BED/GTF/SAF/Parquet/locInd, `locus_context.tsv`, `rename_map.tsv`,
  `ensembl_named/`, the noExon and context variants: none exist. README's output grid is a plan.

## 2. Reproduction

| check | measured | config expectation |
|---|---|---|
| rmsk.txt.gz md5 | ca2e5542cab0390b5458e7935e891430 | match |
| chromAlias md5 | cd2f6474b8f0bceb862719430821a33b | match |
| GENCODE GTF md5 (refcache copy) | 702e27a8727db66cd23e9f66f5aa1d38 | match |
| GRCm39 FASTA md5 (refcache copy) | c4dfe32c560ffabf5068f57449a14511 | match (declared-only in the build; verified here by hand) |
| rule loci | 3,799,629 | 3,799,629 |
| contigs | 59 | 59 |
| subfamilies (repName) | 1,225 | 1,225 |
| triples | 1,245 | 1,245 |
| per-class counts | identical to tests/expectations | pass |
| BUILD_ID | 3e75dad5f3a8f077d132a33c3325641ced7c3f5afc393bafe2a4c17babe13566 | equals the id RELEASES.md cites from the host build → byte-identical across two machines |
| fragment end ≤ contig length | 0 violations over 59 contigs | (no such check in the build) |
| contigs absent from TE table | chr4_JH584295v1_random, chrM | expected (no repeats annotated) |

## 3. Findings

### F1. `rmsk_id` is not a fragment-linkage id (OUTPUTS.md column 13 is wrong)
UCSC's `rmsk.id` column is `char(1)`. Measured: 9 distinct values (`1`–`9`), and it is not even
the last digit of the true RepeatMasker ID (10% agreement = chance). The real ID lives in
`bigZips/mm39.fa.out.gz` (169 MB, md5 not yet pinned): 4,696,900 distinct ids, contiguous, never
spanning two contigs. Record sets are identical: 5,320,771 rows in both files, 1:1 on
(chrom,start,end,repName). Under the TE class rule: 3,186,920 insertions from 3,802,177 fragments;
437,463 insertions are multi-fragment (1,052,720 fragments, 28%). 30,569 multi-fragment insertions
mix repNames; on chr1 the dominant patterns are LTR+internal pairs (IAPEz-int+IAPLTR1a_Mm,
RLTR10+RLTR10-int, MERVL-int+MT2_Mm, MMERVK10C-int+RLTR10C) and SINE subfamily boundaries (B4+B4A,
B3+B3A, ID+ID_B1). The `.out` is therefore the source for `insertion_id`; the ERV provirus structure
comes for free. No `*` overlap flags are present in this `.out`.

### F2. Subfamily name is not a unique dimension key (confirmed)
20 repNames carry two (family,class) triples; 40 triple rows; 6,517 loci; all class DNA (or `DNA?`).
Two patterns: an uncertain-classification suffix (`hAT` vs `hAT?`, `DNA` vs `DNA?`, 1–35 loci on the
`?` side) and a family split (MER63A–D: hAT-Blackjack vs hAT-Tip100; MER53; UCON44/X4b_DNA:
TcMar vs TcMar-Tigger; Eutr2/2B: DNA vs MULE-MuDR; MER136: DNA vs Merlin). None are retrotransposons.
Full list: `report/subfamily_multiplicity.tsv`. A join `counts_by_repName ⋈ te_dim USING (subfamily)`
double-counts those 20 names.

### F3. Coordinate-only identity collides
3 pairs of rule-set records share (chrom,start,end,strand) with different repName: chr11:67327100
(ORR1B1-int vs B1F), chr13:58658237 (B1_Mus1 vs ORR1B1-int), chr16:37859045 (ID_B1 vs B1_Mur3).
The selfdesc `locus_id` is unique (3,799,629) because it carries repName; a coordinate key is not.
216,232 rule-set records start inside an earlier record's span (nesting/overlap is common).

### F4. Same-day rebuild writes into the live `current` snapshot (confirmed by test)
`build.sh --date <same>` reuses the published directory. With a changed policy, `10_build_master`
overwrote `te_dim.tsv` in `current`, left an uncompressed `te_loci.tsv` and `.work/`, then died on
the loci assert. `99_verify` on `current` then fails (te_dim md5 mismatch). `90_manifest` keeps the
stale manifest by design, so the manifest lies about the bytes. The subsequent archive step moved
that corrupted directory into `archive/te_mm39_20260915__3e75dad5f3a8` under the OLD id, because
`release.sh` reads the `BUILD_ID` file and never recomputes from content.

### F5. Publication paths that do work
Identical rebuild under a new date → `reconfirmed` row, redundant dir removed, `current` unchanged
(tested). Changed policy under a new date → new id `41b69cb17053…`, old snapshot archived, `current`
moved, `INDEX.tsv` gains archived+current rows, builder stamped `-dirty` (tested).

### F6. Policy universe sizes (from the full source, `report/policy_universes.tsv`)
| universe | loci | subfamilies | triples |
|---|---|---|---|
| tRNA-prefix-excluded rule (today's TE set) | 3,799,629 | 1,225 | 1,245 |
| carried classes, no family exclusion | 3,802,177 | 1,228 | 1,248 |
| carried classes minus Satellite | 3,764,949 | 1,220 | 1,240 |
| LINE+SINE+LTR+Retroposon | 3,593,857 | 868 | 868 |
| Satellite only | 37,228 | 8 | 8 |
| structural-RNA classes | 21,715 | 71 | 71 |
| Simple_repeat + Low_complexity | 1,496,879 | 17,185 | 17,185 |
The `tRNA` prefix drops exactly LFSINE_Vert 1,235 / MamSINE1 925 / AmnSINE2 388 (confirmed).

### F7. Manifest `counts` are the config's EXPECT_* values, not observations
Harmless today because `10_build_master` asserts them first, but the manifest records an
expectation. The per-class expectations file is keyed by genome, so any policy change also forces
an edit to `tests/expectations/mm39_class_counts.tsv` (a policy-keyed file would decouple them).

### F8. FASTA is declared, never checked
`00_fetch` fetches rmsk, chromAlias, GTF. The FASTA md5 is a declaration. The refcache copy does
match the pin (checked here), and every fragment end lies within `mm39.chrom.sizes`. Neither check
is in the build.

### F9. IRescue facts (local checkout `01_modules/.ref/irescue`, v1.2.0-20-g26f36fb, __version__ 1.2.0)
- `--locus-level` is `type=str, choices={disabled,fragment,instance}, default disabled`. The README's
  bare `--locus-level` example does not parse against this argparse. Confirmed discrepancy.
- Auto-annotation for mm39 downloads `bigZips/mm39.fa.out.gz` (same records as rmsk.txt) and skips
  classes Low_complexity, Simple_repeat, rRNA, scRNA, srpRNA, tRNA (`map.py makeRmsk`). It keeps
  snRNA and Satellite and applies no family rule. Measured universe: 3,805,826 records, 1,240
  subfamilies, 1,260 triples = the te-tracks rule set + snRNA 3,649 + the tRNA-prefix SINEs 2,548.
  Name grammar `subfamily#class/family`; `fragment` appends `~<per-subfamily ordinal>`; `instance`
  groups by the .out ID and names `subfams#classfam~<ID>` with `|`-joined sets.
- Custom `-r` BED: >=4 columns, column 4 = feature name. `chrcat` serializes feature sets with commas
  and strips a `#...` suffix when writing features.tsv.gz, so `,` and `#` are reserved in exported
  names; `|`, `:`, `-` and whitespace-free strings pass through. No rmsk repName/repFamily/repClass in
  mm39 contains `| : , # ~` or whitespace (measured 0). Strand is consulted only under
  `--strandedness forward|reverse`. `getRefs` skips BAM contigs absent from the BED with a warning
  when at least one matches, so contig-namespace concordance is not guaranteed by the tool.

### F10. Repo hygiene
No `AGENTS.md` in te-tracks (umbrella convention requires one per submodule). Working tree clean at
6ff3ee9; umbrella pin matches. The `.out.gz` md5 is unpinned. `EXCLUDE_FAMILY_PREFIX=""` cannot be
expressed (documented wart).

## 4. Second review (codex, gpt-6-astra, 2026-09-15) — verified corrections

Critique: `consult/codex_critique.md`. Items checked against code or source and accepted:
- F9 as first written claimed IRescue applies no class filter. Wrong; corrected above.
- Full-source uniqueness (all 5,320,771 records): selfdesc key unique; coordinate-only key has the
  same 3 collisions. F3 now holds for the full source, not only the filtered set.
- Triple counts: 1,248 is the carried-class set WITH Satellite; the proposed `interspersed` (no
  Satellite) has 1,240 triples / 3,764,949 fragments.
- F1 wording: the .out ID is a RepeatMasker-assigned instance grouping. Provirus structure is a
  hypothesis it enables, not a fact it delivers; orientation and nesting need validation.
- Equal BUILD_IDs prove equality of the fingerprinted delivered outputs only (source/, manifest and
  the id file are excluded by design).
- TElocal locInd compatibility is unverified; no TElocal source is available locally.

## 5. Source run identity (declared by UCSC, 2026-09-16)

`goldenPath/mm39/bigZips/README.txt` states: RepeatMasker "February 01 2017 (open-4-0-8) 1.332",
run with `-s`, libraries "RepBase RELEASE 20181026" and "Dfam_Consensus RELEASE 20181026". The
`.out.gz` carries no version line. The hgTrackUi page is generic. Record these as declared provenance
in the manifest with their source URL.

## 6. Contig namespace of the GENCODE GRCm39 FASTA (measured 2026-09-16)

`refcache/mm39/mm39_20260911/GRCm39.genome.fa.gz` carries 61 contigs whose names and lengths are in
`gencode_grcm39_fasta_contigs.tsv`. The 22 chromosomes are UCSC-named (`chr1` … `chrM`); the 39
scaffolds are GenBank accessions (`GL456210.1`, `JH584295.1`, `MU069434.1`). Against UCSC
`chrom.sizes`: 22 identical (name, length) lines, 39 differ by name only. So a BAM aligned to this
FASTA matches neither the UCSC nor the Ensembl namespace completely, and the exports need a third
namespace, `gencode`, built through `chromAlias` (ucsc column for chromosomes, genbank column for
scaffolds). Lengths agree for all 61 contigs.

## 7. Signed consensus-left values in the pinned `.out` (measured 2026-09-16)

Six of 5,320,771 rows carry a negative parenthesized consensus-left value; all six are on the `C`
strand, and zero rows carry a negative query-left value. A negative consensus left records an
alignment that runs past the consensus end, the mirror of a consensus start below 1. UCSC carries
the same values under its signed encoding, and the qualification matched all six. The parser
therefore treats `query_left_bp` as nonnegative and `consensus_left_bp` as signed; the ADR 5 consult's
nonnegative statement for the consensus remaining length is corrected by this measurement.

```
line     score div   del  ins  chrom  start_1  end_1    (query_left)  C  name       class/family      (cons_left) cons_end cons_start ID
669264   332   26.5  1.2  0.0  chr11  21327149 21327231 (100646138)   C  Charlie17  DNA/hAT-Charlie   (-1847)     2634     2551       590512
1099217  432   27.5  20.0 3.4  chr12  99817795 99818253 (20274504)    C  Charlie7   DNA/hAT-Charlie   (-231)      2612     2076       976795
1750645  242   23.1  17.5 0.0  chr15  86467501 86467604 (17606347)    C  Charlie17  DNA/hAT-Charlie   (-1998)     2785     2660       1551176
3752748  227   30.2  0.0  0.0  chr6   8693759  8693811  (140894233)   C  Tigger16b  DNA/TcMar-Tigger  (-19)       295      243        3326908
4480048  252   31.9  6.5  8.7  chr8   85592444 85592458 (44535236)    C  ID_B1      SINE/B4           (-1)        224      179        3969364
4754087  349   38.3  2.3  2.9  chr9   87195541 87195712 (37163988)    C  Tigger16b  DNA/TcMar-Tigger  (-60)       336      172        4214731
```
