# Provenance

te-tracks projects the checksum-pinned mm39 RepeatMasker run into a complete record catalog,
six named universes and registered counting exports. The gene child pins that catalog and
GENCODE vM37. Acceptance remeasures the published bytes against independently authored
[expectations](../tests/expectations/mm39/README.md).

## Sources and qualification

The declared assembly is GRCm39/mm39, with RepeatMasker `open-4.0.8` and library
`RepBase 20181026; Dfam_Consensus 20181026`. The retained run evidence is the UCSC mm39
`bigZips/README.txt` URL recorded in `source/SOURCES.json` and the manifest.

| Source | Role | Pin |
|---|---|---|
| UCSC `mm39/bigZips/mm39.fa.out.gz` | Primary records, source-wide instance IDs, consensus coordinates and overlap flags | MD5 `ffc8399d05f3388d80b78c93482a5b95` |
| UCSC `mm39/database/rmsk.txt.gz` | Independent browser-table qualification and raw taxonomy/coordinate correspondence | MD5 `ca2e5542cab0390b5458e7935e891430` |
| UCSC `mm39/bigZips/mm39.chromAlias.txt` | UCSC, Ensembl, GenBank and RefSeq contig correspondence | MD5 `cd2f6474b8f0bceb862719430821a33b` |
| UCSC `mm39/bigZips/mm39.chrom.sizes` | Contig lengths and genomic bounds | MD5 `967c609a714df35c86a4f52ac85db377` |
| GENCODE release M37 `GRCm39.genome.fa.gz` | Declared alignment assembly | MD5 `c4dfe32c560ffabf5068f57449a14511` |
| GENCODE release M37 `gencode.vM37.primary_assembly.annotation.gtf.gz` | Gene child exon mask | MD5 `702e27a8727db66cd23e9f66f5aa1d38` |
| Tracked Dfam metadata snapshot | Lineage, model, Wicker-rank and clade view | SHA-256 `ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f` |

The builder retains acquired inputs under `source/`. The FASTA pin declares the assembly;
consumer alignment references own the sequence bytes. The source cache is seeded from the
retained in-container copy, with every checksum checked before the host build.

`source/qualification.md` compares all 5,320,771 `.out` rows with all 5,320,771 browser-table rows
on contig, inclusive start/end, strand and source name. All rows match. Unmatched rows and field
disagreements are zero, including score, divergence, deletion, insertion, query-left, raw class,
raw family and all three strand-dependent consensus-coordinate fields. Qualification records
4,696,900 contiguous IDs spanning 1–4,696,900, zero IDs spanning contigs, zero starred rows and
three equal-coordinate/different-name pairs. The checked report also lives in the project's
[source qualification record](_internal/redesign-2026-09/audit/source_qualification_mm39.md).

## Catalog and universe census

The canonical catalog has 5,320,771 unique records, 24 required typed columns, 18,484 names and
18,504 raw taxonomy triples across 61 contigs. Its TSV and Parquet contain equal typed rows.
Instance sizes are 4,251,251 single-record, 338,697 two-record and 106,952 three-or-more-record
groups. Six records retain negative consensus-left values; two retain consensus start above end.
The source `rmsk_overlap_flag` is constant `false`.

| Universe | Records | Names | Raw triples | Summed record bp |
|---|---:|---:|---:|---:|
| `all_rmsk` | 5,320,771 | 18,484 | 18,504 | 1,201,573,004 |
| `interspersed` | 3,764,949 | 1,220 | 1,240 | 1,116,605,808 |
| `interspersed_plus_satellites` | 3,802,177 | 1,228 | 1,248 | 1,121,742,599 |
| `retrotransposon_derived` | 3,593,857 | 868 | 868 | 1,084,886,912 |
| `satellites` | 37,228 | 8 | 8 | 5,136,791 |
| `compat_tetranscripts_mm39` | 3,799,629 | 1,225 | 1,245 | 1,121,476,301 |

Summed lengths retain overlap. There are 429,440 records overlapping another catalog record on
the same contig, either strand (8.0710%). The interspersed selection has 3,152,636 instances,
434,707 multi-record instances, 30,569 mixed-name instances holding 95,830 records, and 23,244
mixed-strand instances. Across `all_rmsk`, 445,649 instances have several records. The LTR-only
composition screen finds 722,280 instances with an LTR non-`-int` member and zero `-int` members;
588 raw LINE/L1 records begin at model base 1. These are annotation measurements used as inputs
to later structural qualification.

## Class census

Every source class has a reviewed disposition in `config/mm39.classes.tsv`. Acceptance compares
the complete census with `tests/expectations/mm39/class_census.tsv`.

| Raw class | Records |
|---|---:|
| DNA | 164,783 |
| DNA? | 9 |
| LINE | 976,368 |
| LTR | 1,105,064 |
| Low_complexity | 157,808 |
| RC | 416 |
| Retroposon | 17,253 |
| SINE | 1,495,172 |
| Satellite | 37,228 |
| Simple_repeat | 1,339,071 |
| Unknown | 5,786 |
| Unspecified | 98 |
| rRNA | 1,514 |
| scRNA | 12,248 |
| snRNA | 3,649 |
| srpRNA | 796 |
| tRNA | 3,508 |

`interspersed` includes the nine raw TE classes and preserves tRNA-derived SINE families.
`Unknown`, `Unspecified` and `DNA?` carry provisional membership. The compatibility universe
adds satellites and applies the historical `tRNA` family-prefix exclusion.

## Taxonomy rule evidence

`taxonomy_rule_v1` resolves each name by source-instance votes: normalize a trailing `?`,
resolve class, then resolve specified families within that class. Unspecified families abstain
at family rank. Ties publish empty canonical labels with an explicit unresolved status;
exported rollups retain separate unresolved buckets per name. Hand-authored rule fixtures cover
ties, invalid votes, refinement competitions, weighting and count conservation.

The canonical table has 18,484 rows and zero unresolved names. Twenty multi-label DNA names
account for 6,517 records. Class status is 18,478 concordant and six uncertainty-suffix resolutions.
Family status is 1,095 concordant, five uncertainty-suffix resolutions, five specified-family
resolutions beside abstentions, seven plurality resolutions and 17,372 unspecified families.
The minimum winning family plurality share is 0.840 for MER63C. Summed per-label instance
counts are 4,727,623; a mixed-label source instance contributes to each label it supports.

The independently pinned 20-name Dfam fixture in `tests/fixtures/taxonomy/` covers every
resolution-report name and agrees at every named type/subtype rank. The builder derives
canonical labels from the catalog. Acceptance checks the full table against the rule, the rule
against its hand-authored cases, and the multi-label decisions against that external fixture.

## Dfam snapshot pin

`data/dfam/` tracks the compressed snapshot, its provenance JSON and its refresh script.
The snapshot records Dfam 4.0, release date May 2026, fetched from the Dfam API on 2026-09-17;
`fetch_finished` is `2026-09-17T15:10:29.831392Z`. Its compressed bytes have SHA-256
`ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f`; decompressed JSON has SHA-256
`053c728b2bf2054b84a66d31d8cd27bc70128e3f9ef2ae618a394df9a34f41e1`. The provenance pin is
`a5e0eb4920fc1f9e50463f68fd6802c7e4e74bd83dad462cf53b8b6df987913b`.
Both tracked inputs are checksum-checked and retained under `source/`; the manifest's
`fetch_finished` is checked against the retained provenance. The recorded rank scheme is
`rank_scheme_wicker_v1`.

The 1,220 selected names comprise 1,047 exact matches (2,797,852 records), 147 part-model sets
(928,528 records) and 26 missing names (38,569 records). Part sets contain three, two and one
models for 30, nine and 108 names; six are L2/CR1 sets. The normalized view contains 1,263
name/model rows, 300 lineage nodes with 193 coded nodes, and 1,278 model/clade rows. Nine models
have multiple clades; 33 models across 31 names have a Primates branch. Among exact names,
884 take a leaf Wicker code, 110 inherit one and 53 have missing ranks under the `Unknown` leaf.
`UCON4` retains its raw `Unspecified` class and inherits DNA class from Dfam's Kolobok lineage.
Complete curated clade paths support consumer-defined age tiers beside record divergence.

## Gene child and independent geometry

The child retains 78,317 gene rows, 278,369 transcript rows and 1,298,921 exon rows from
GENCODE vM37. Annotation covers 38 of 61 contigs; 2,638 catalog records occupy the other 23.
The unstranded exon union spans 160,549,642 bp. The `interspersed` subtraction retains
3,684,934 blocks from 3,668,830 records, totaling 1,090,369,890 bp, with 26,235,918 bp removed.
The compatibility subtraction retains 3,717,740 blocks totaling 1,094,973,237 bp.
All three complete status censuses are independently recomputed against the phase 8 expectation.

Acceptance's independent bedtools pipeline converts the retained GTF exons to BED, sorts and
merges them, and subtracts that union from the parent's record BED. It compares exact block
multisets `(start, end, strand, name)` with the child SAF on chr18, chr19,
`chr1_MU069434v1_random` and chr7. All four comparisons passed against the acceptance archive:

| Contig | Parent records | GTF exons | Exon-union intervals | Exon-union bp | Retained blocks | Retained bp |
|---|---:|---:|---:|---:|---:|---:|
| chr18 | 118,502 | 35,853 | 9,708 | 4,528,733 | 116,425 | 34,253,394 |
| chr19 | 86,429 | 39,613 | 10,373 | 4,434,265 | 84,268 | 21,565,706 |
| chr1_MU069434v1_random | 4 | 0 | 0 | 0 | 4 | 385 |
| chr7 | 214,663 | 90,795 | 24,978 | 12,521,871 | 207,048 | 60,028,394 |
| Covered blocks / child interspersed blocks | — | — | — | — | 407,745 / 3,684,934 (11.07%) | — |

The original three contigs agree with the independently recorded phase 8 block/length anchors.
The chr7 measurements are new milestone 9 bedtools anchors in
[`gene_oracle_m9.tsv`](../tests/expectations/mm39/gene_oracle_m9.tsv), carried by the
[milestone 9 rulings](_internal/redesign-2026-09/reviews/m9_rulings.md#fix-round-evidence).

## Packaged legacy reconciliation

The external oracle is
`/data2/users/shared/refcache/mm39/mm39_20260911/GRCm39_Ensembl_rmsk_TE.gtf.gz`,
MD5 `1d6770be131fc1b47402a633f4401cbd`. Acceptance checks its 3,799,629 data rows against
`compat_tetranscripts_mm39` membership and compares the full coordinate/strand multiset after
contig normalization. The comparison retains duplicate coordinate multiplicity and reports each
direction of an interval difference. The check reports the named path as unsupported when the
packaged file is unavailable.

The acceptance comparison found 3,799,629 rows on each side, with zero compatibility-only
and zero legacy-only intervals, including duplicate multiplicity.

The legacy selection removes 2,548 tRNA-derived SINE records: LFSINE_Vert 1,235, MamSINE1 925
and AmnSINE2 388. Its net difference from `interspersed` is 34,680 records after adding satellites.
Earlier lab audits recorded spelling substitutions in the packaged labels: `ID4_v` appeared as
`ID4_.` and `ID4_v` in 25,263 and 17 records, `LTR33A_v` as `LTR33A_.` in 432, `MER34C_v` as
`MER34C_.` in 328, and `RTE-BovB` as `RTE-Bo.B` and `RTE-BovB` in 4,239 and nine. They also
recorded Unknown-family relabeling and four class differences. Those historical label findings
remain migration evidence; the acceptance oracle qualifies coordinates and membership.
Consumers comparing older matrices apply an explicit label mapping before joining canonical names.

## Independent evidence and release identity

The UCSC browser table qualifies the primary `.out`; the pinned Dfam fixture checks canonical
multi-label decisions; the tracked Dfam snapshot checks the metadata view; the packaged legacy
GTF qualifies compatibility membership; bedtools qualifies child subtraction geometry. These
oracles have origins outside the builder's output. Fixture answers and acceptance anchors retain
their independently authored values when an observation differs.

The core has 52 inventoried files, 27 export contracts and five build-source roles, with
`catalog.sources = ['rmsk_out']`. Its payload is 15,301,538,537 bytes. The child has 21
inventoried files and 12 export contracts. [RELEASES.md](RELEASES.md) records the acceptance IDs,
measured retention budget and their development-build comparison; [RUNBOOK.md](RUNBOOK.md)
records the host procedure and qualification limits.
