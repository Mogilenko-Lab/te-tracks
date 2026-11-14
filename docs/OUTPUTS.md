# Outputs

Canonical tables, GTF and SAF use **1-based inclusive** coordinates. BED uses **0-based
half-open** coordinates: `[start_1 - 1, end_1)`. Record lengths sum `end_1 - start_1 + 1`,
with overlaps retained.

## Consumer map

Every export row below is published in `ucsc`, `ensembl` and `gencode` namespaces. Choose the
namespace matching the alignment reference and run `bin/te-tracks-preflight` before counting.
Core paths are relative to `te_mm39/archive/<BUILD_ID>/`; child paths belong to `te_mm39_gene`.

| Published artifact | Universe / variant | Reader | Counting question or reference join |
|---|---|---|---|
| `exports/<ns>/interspersed/full/record.bed` | `interspersed / full` | IRescue, bedtools | Which annotated record supports each RNA molecule or interval overlap? |
| `exports/<ns>/interspersed/full/subfamily.bed` | `interspersed / full` | IRescue | How much RNA support belongs to each RepeatMasker subfamily? |
| `exports/<ns>/interspersed/full/family.bed` | `interspersed / full` | bedtools and family overlap readers | Which canonical class/family bucket supplies interval support? |
| `exports/<ns>/interspersed/full/record.gtf` | `interspersed / full` | TEsingle, TElocal; TEtranscripts; Stellarscope after its boundary gate | Record assignment with the subfamily grammar TEsingle and TElocal consume; TEtranscripts groups by the canonical taxonomy triple. Stellarscope reads `locus` or `instance_id`. |
| `exports/<ns>/interspersed/full/record_starsolo.gtf` | `interspersed / full` | STARsolo, cellranger | Record counts through the record-as-gene grammar, combined with the full gene annotation. |
| `exports/<ns>/interspersed/full/subfamily.gtf` | `interspersed / full` | TEsingle, TElocal, TEtranscripts; Stellarscope after its boundary gate | Subfamily-grain sensitivity counting with shared subfamily transcript IDs. |
| `exports/<ns>/interspersed/full/subfamily.saf` | `interspersed / full` | featureCounts | Full-interval subfamily support for sensitivity comparisons. |
| `exports/<ns>/interspersed/full/taxonomy_triple.saf` | `interspersed / full` | featureCounts | Full-interval counts labeled by canonical subfamily:family:class. |
| Child `exports/<ns>/interspersed/exon_subtracted/subfamily.saf` | `interspersed / exon_subtracted` | Bulk RNA-seq featureCounts | The bulk featureCounts product: subfamily counts over support outside the GENCODE vM37 exon union. |
| Child `exports/<ns>/interspersed/exon_subtracted/taxonomy_triple.saf` | `interspersed / exon_subtracted` | Bulk RNA-seq featureCounts | The same retained blocks grouped with canonical taxonomy-triple IDs. |
| Child `exports/<ns>/compat_tetranscripts_mm39/exon_subtracted/{subfamily,taxonomy_triple}.saf` | `compat_tetranscripts_mm39 / exon_subtracted` | Bulk RNA-seq featureCounts | Legacy-universe reproduction under the pinned exon mask. |
| `exports/<ns>/all_rmsk/full/record.bed` | `all_rmsk / full` | a chromatin-accessibility ledger | The interval catalog the ledger keys on, including satellites, simple repeats and structural RNAs. |
| `tables/rmsk_records.{tsv.gz,parquet}`, `tables/rmsk_instance_members.tsv.gz`, `tables/rmsk_taxonomy.tsv` | `all_rmsk` | RNA result joins and chromatin-accessibility ledger | Resolve record identities, source grouping, coordinates, divergence and raw taxonomy. |
| `universes.json`, `tables/universe_members.tsv.gz`, `tables/universe_summary.tsv` | All six named universes | Every consuming ledger | Pin eligibility and reconcile the selected reference census. |
| `tables/taxonomy_canonical.tsv`, `tables/taxonomy_resolution_report.tsv` | `all_rmsk` | Subfamily-to-family/class rollups | Assign each name once under the instance-weighted taxonomy rule. |
| `tables/taxonomy_dfam.tsv`, `tables/taxonomy_dfam_models.tsv`, `tables/dfam_lineage_nodes.tsv`, `tables/dfam_model_clades.tsv` | `interspersed` | Consumer annotation and age-tier policies | Join pinned Dfam models, rank statuses and complete curated clade paths to names. |
| `tables/export_feature_members.tsv.gz`, `tables/exports.tsv` in each family | Each declared universe / variant | Matrix binding and provenance ledgers | Join measured features through `(universe_name, variant, feature_level, key_grammar)` and verify export digests. |
| `tables/contig_aliases.tsv`, core `tables/contig_coverage.tsv` | `all_rmsk`, with interspersed coverage | Preflight and namespace readers | Match contig identity, lengths and reference coverage. |
| Child `tables/record_transcript_context.tsv.gz`, `tables/record_context.tsv.gz` | `all_rmsk` | Reference joins | Derive genic-context labels from stored transcript and gene geometry. |
| Child `tables/exon_subtraction_status.tsv`, `tables/exon_subtraction_summary.tsv`, `tables/gene_annotation_coverage.tsv` | `all_rmsk`, `interspersed`, `compat_tetranscripts_mm39` | Bulk reference audit | Reconcile retained/removed bases and annotation coverage under the mask. |
| `source/`, `MANIFEST.json`, `BUILD_ID`, `CATALOG_ID` in each family | Family declaration | Publisher and every consumer | Verify source pins, qualification evidence, immutable bytes and parent dependencies. |

The expectation-maximization routes take the unmasked record exports with the full gene annotation.
The exon-subtracted SAF is the bulk featureCounts product. Joint counting owns gene/TE molecule
allocation and records its counting unit, strand policy, barcode thresholds and estimator parameters.
The three single-cell and single-nucleus pilots qualify those choices in the consuming toolkit;
the bulk pilot qualifies its featureCounts recipe. [RUNBOOK.md](RUNBOOK.md) gives the build and pin procedure.

## Artifact status

`delivered` means generated; `tested` means verified against the artifact contract.
Deferred artifacts and their required evidence appear in the [README](../README.md#deferrals-and-required-evidence).

| artifact | status |
|---|---|
| `source/{mm39.fa.out.gz,rmsk.txt.gz,mm39.chromAlias.txt,mm39.chrom.sizes,SOURCES.json}` | delivered, tested |
| `source/qualification.md` | delivered, tested |
| `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md` | delivered, tested |
| `tests/fixtures/source/` | delivered, tested |
| `tests/fixtures/records/` | delivered, tested |
| `tests/expectations/mm39/` | delivered, tested |
| `tests/expectations/mm39/taxonomy_census.tsv` | delivered, tested |
| `tests/expectations/mm39/exon_subtraction_summary.tsv` | delivered, tested |
| `tests/fixtures/taxonomy/dfam_snapshot.tsv` | delivered, tested |
| `tests/fixtures/taxonomy/dfam_snapshot.provenance.json` | delivered, tested |
| `tests/fixtures/taxonomy/rule_cases.tsv` | delivered, tested |
| `tests/fixtures/taxonomy/rollup_counts.tsv` | delivered, tested |
| `tests/fixtures/taxonomy/weighting_context.tsv` | delivered, tested |
| `tests/fixtures/exports/` | delivered, tested |
| `tests/fixtures/consumers/` | delivered, tested: parser identities, registration, IRescue conservation, featureCounts, STARsolo, cellranger reference, bedtools, samtools and DuckDB; Stellarscope unsupported on its right-boundary defect |
| `tests/lib/consumers.py` | delivered, tested |
| `tests/lib/records.py` | delivered, tested |
| `tests/fixtures/contigs/` | delivered, tested |
| `tests/fixtures/publication/` | delivered, tested |
| `tables/rmsk_records.tsv.gz` | delivered, tested |
| `tables/rmsk_records.parquet` | delivered, tested |
| `tables/rmsk_instance_members.tsv.gz` | delivered, tested |
| `tables/rmsk_taxonomy.tsv` | delivered, tested |
| `tables/taxonomy_canonical.tsv` | delivered, tested |
| `tables/taxonomy_resolution_report.tsv` | delivered, tested |
| `source/dfam_interspersed_mm39_snapshot.json.gz` | delivered, tested |
| `source/dfam_interspersed_mm39_snapshot.provenance.json` | delivered, tested; core payload has 52 files |
| `tables/taxonomy_dfam.tsv` | delivered, tested |
| `tables/taxonomy_dfam_models.tsv` | delivered, tested |
| `tables/dfam_lineage_nodes.tsv` | delivered, tested |
| `tables/dfam_model_clades.tsv` | delivered, tested |
| `tests/checks/consumers/17_starsolo_profile.required.py` | delivered, tested |
| `tests/checks/consumers/24_starsolo_exec.sh` | delivered, tested with consumer environment |
| `tests/checks/consumers/25_cellranger_mkref.sh` | delivered, tested with consumer environment |
| `universes.json` | delivered, tested |
| `tables/universe_members.tsv.gz` | delivered, tested |
| `tables/universe_summary.tsv` | delivered, tested |
| `tables/export_feature_members.tsv.gz` | delivered, tested |
| `tables/exports.tsv` | delivered, tested |
| `tables/contig_aliases.tsv` | delivered, tested |
| `tables/contig_coverage.tsv` | delivered, tested |
| `exports/ucsc/interspersed/full/record.bed` | delivered, tested |
| `exports/ucsc/interspersed/full/subfamily.bed` | delivered, tested |
| `exports/ucsc/interspersed/full/family.bed` | delivered, tested |
| `exports/ucsc/interspersed/full/record.gtf` | delivered, tested |
| `exports/ucsc/interspersed/full/record_starsolo.gtf` | delivered, tested |
| `exports/ucsc/interspersed/full/subfamily.gtf` | delivered, tested |
| `exports/ucsc/interspersed/full/subfamily.saf` | delivered, tested |
| `exports/ucsc/interspersed/full/taxonomy_triple.saf` | delivered, tested |
| `exports/ensembl/interspersed/full/record.bed` | delivered, tested |
| `exports/ensembl/interspersed/full/subfamily.bed` | delivered, tested |
| `exports/ensembl/interspersed/full/family.bed` | delivered, tested |
| `exports/ensembl/interspersed/full/record.gtf` | delivered, tested |
| `exports/ensembl/interspersed/full/record_starsolo.gtf` | delivered, tested |
| `exports/ensembl/interspersed/full/subfamily.gtf` | delivered, tested |
| `exports/ensembl/interspersed/full/subfamily.saf` | delivered, tested |
| `exports/ensembl/interspersed/full/taxonomy_triple.saf` | delivered, tested |
| `exports/gencode/interspersed/full/record.bed` | delivered, tested |
| `exports/gencode/interspersed/full/subfamily.bed` | delivered, tested |
| `exports/gencode/interspersed/full/family.bed` | delivered, tested |
| `exports/gencode/interspersed/full/record.gtf` | delivered, tested |
| `exports/gencode/interspersed/full/record_starsolo.gtf` | delivered, tested |
| `exports/gencode/interspersed/full/subfamily.gtf` | delivered, tested |
| `exports/gencode/interspersed/full/subfamily.saf` | delivered, tested |
| `exports/gencode/interspersed/full/taxonomy_triple.saf` | delivered, tested |
| `exports/ucsc/all_rmsk/full/record.bed` | delivered, tested |
| `exports/ensembl/all_rmsk/full/record.bed` | delivered, tested |
| `exports/gencode/all_rmsk/full/record.bed` | delivered, tested |
| `te_mm39_gene`: `exports/ucsc/interspersed/exon_subtracted/subfamily.saf` | delivered, tested |
| `te_mm39_gene`: `exports/ensembl/interspersed/exon_subtracted/subfamily.saf` | delivered, tested |
| `te_mm39_gene`: `exports/gencode/interspersed/exon_subtracted/subfamily.saf` | delivered, tested |
| `te_mm39_gene`: `exports/{ucsc,ensembl,gencode}/interspersed/exon_subtracted/taxonomy_triple.saf` | delivered, tested |
| `te_mm39_gene`: `tables/exon_subtraction_status.tsv` | delivered, tested |
| `te_mm39_gene`: `tables/record_transcript_context.tsv.gz`, `tables/record_context.tsv.gz` | delivered, tested |
| `te_mm39_gene`: `exports/{ucsc,ensembl,gencode}/compat_tetranscripts_mm39/exon_subtracted/{subfamily,taxonomy_triple}.saf` | delivered, tested |
| `te_mm39_gene`: `tables/exon_subtraction_summary.tsv`, `tables/gene_annotation_coverage.tsv` | delivered, tested |
| `te_mm39_gene`: copied `universes.json`, `tables/contig_aliases.tsv`, registration and export inventory | delivered, tested |
| `te_mm39_gene`: retained GTF, source declaration, manifest and identities | delivered, tested |
| `tests/fixtures/gene/` | delivered, tested |
| `MANIFEST.json` | delivered, tested |
| `BUILD_ID` | delivered, tested |
| `CATALOG_ID` | delivered, tested |
| `bin/te-tracks-preflight` | delivered, tested |
| `docs/RUNBOOK.md`: gene child build and verification | delivered, tested |
| `docs/RUNBOOK.md`: host procedure and measured resource floors | delivered; commands reviewed and scratch publication tested; host filesystem qualification required |
| `tests/checks/acceptance/`: eleven complete-build checks | delivered, tested |
| `tests/expectations/mm39/{source_pins,source_qualification,record_census,identity,gene_oracle,gene_oracle_m9}.tsv` | delivered, tested |
| `data/dfam/`: tracked snapshot, provenance and refresh script | delivered; retained input pins tested; refresh qualification recorded |
| `docs/OUTPUTS.md`: consumer map | delivered, tested: artifact bindings agree with registered contracts |
| `docs/PROVENANCE.md`: qualification and measured census | delivered, tested |
| `docs/RELEASES.md` | delivered, tested |

## Canonical records and universes

The build writes the complete source catalog under `tables/` and six executable universe
definitions in `universes.json`. The default universe is `interspersed`.

### `tables/rmsk_records.tsv.gz` and `tables/rmsk_records.parquet`

Each row represents one primary RepeatMasker annotation. The 24 required columns appear in
this order; `text` is Arrow UTF-8, and every column has a value.

| Column | Type | Contract |
|---|---|---|
| `rmsk_record_id` | text | Unique constructed key `<rmsk_name>\|<chrom>:<start_1>-<end_1>\|<strand>` within the build. |
| `chrom` | text | Source contig name matched to the pinned sequence dictionary. |
| `start_1` | int64 | Genomic start, 1-based inclusive. |
| `end_1` | int64 | Genomic end, inclusive and bounded by the contig length. |
| `strand` | text | `+` or `-`, with source `C` mapped to `-`. |
| `rmsk_name` | text | Exact source repeat name, preserving case and punctuation. |
| `rmsk_family` | text | Exact matched UCSC `repFamily`, verified against the parsed source label. |
| `rmsk_class` | text | Exact matched UCSC `repClass`, verified against the parsed source label. |
| `rmsk_instance_id` | text | Complete primary `.out` grouping token, preserving leading zeros. |
| `sw_score` | int64 | Source Smith–Waterman score. |
| `divergence_pct` | float64 | Source percent divergence; `6.7` denotes 6.7 percent. |
| `deletion_pct` | float64 | Source percent deletion. |
| `insertion_pct` | float64 | Source percent insertion. |
| `length_bp` | int64 | Genomic record length, `end_1 - start_1 + 1`. |
| `consensus_start_1` | int64 | Signed forward-model start, 1-based, with reverse-strand field order normalized. |
| `consensus_end_1` | int64 | Signed forward-model end, inclusive. |
| `consensus_left_bp` | int64 | Signed remaining model length; negative values retain alignments past the consensus end. |
| `query_left_bp` | int64 | Nonnegative remaining query length from the parenthesized source token. |
| `rmsk_overlap_flag` | bool | Presence of the source trailing `*` marker. |
| `rmsk_class_family` | text | Exact `.out` class/family token, including class-only spelling. |
| `ucsc_rep_start` | int64 | Raw signed UCSC `repStart`, retaining its strand-dependent encoding. |
| `ucsc_rep_end` | int64 | Raw signed UCSC `repEnd`. |
| `ucsc_rep_left` | int64 | Raw signed UCSC `repLeft`. |
| `source_row_number` | int64 | One-based ordinal among primary `.out` annotation rows before sorting. |

Consensus start and end follow the source; two mm39 records carry start above end
(`L1MdFanc_II|chr1:9847889-9847905|-`, `L1MdF_III|chr2:116363011-116363342|-`), so a derived
consensus-match length is signed.

Rows sort by `(chrom, start_1, end_1, strand, rmsk_name)`, with text columns in C-locale byte
order and coordinate columns ascending numerically. Source and UCSC rows join one-to-one
on these five fields. Class-only `.out` tokens project the
class into both raw taxonomy fields under the qualified UCSC convention.

Record components remain authoritative for computation. Names and contig names are free of
`|`, `:` and whitespace, so each record key parses back into its
components. Repeat names also exclude `/`, keeping unresolved rank tokens separator-free.
Genomic bounds satisfy `1 <= start_1 <= end_1 <= contig length`. Equal coordinates
with different names retain separate record identities; exact duplicate keys fail the build.

### Records, instances and insertions

A record is one RepeatMasker alignment of a genome stretch to a consensus model.
Record-grain counts measure individual records; instance-grain counts measure source groupings.
An instance is the source grouping of
records hypothesized to descend from one element; its member records preserve
fragmentation and nesting. An insertion is the DNA produced by one insertion
event. Insertion-level candidates require reconstruction parameters and supporting
evidence for full-length copies, proviruses or solo LTRs.

The mm39 records align to the pinned 2018 repeat library. Consensus coordinates
are model-relative; fragmentation, nesting and overlapping alignments affect
record support. Genic context depends on the gene-annotation pin.
`rmsk_overlap_flag` records the source `*` marker and is constant `false` in mm39.
Genomic interval intersection measures overlap independently of that source flag.

| Measurement | Scope | Observed |
|---|---|---:|
| Multi-record instances | `all_rmsk` | 445,649 |
| Multi-record instances | `interspersed` | 434,707 |
| Mixed-name instances | `interspersed` | 30,569 |
| Mixed-strand instances | `interspersed` | 23,244 |
| Records overlapping another record on the same contig | `all_rmsk`, either strand | 429,440 / 5,320,771 (8.0710%) |
| LTR-only instances | Class LTR, a non-`-int` name and zero `-int` members | 722,280 |
| L1 records starting at consensus base 1 | Raw LINE/L1 | 588 |

The LTR-only screen measures source annotation composition; solo-LTR status
requires structural evidence. The L1 prefix screen measures model-base coverage;
promoter function requires sequence and experimental evidence.

### `tables/rmsk_instance_members.tsv.gz`

Columns are `rmsk_instance_id` (text) and `rmsk_record_id` (text), sorted by both columns.
Every record has exactly one membership row. The `.out` token defines the instance, and all
members of an instance share one contig. Instance text sorts lexically, preserving leading zeros.

### `tables/rmsk_taxonomy.tsv`

Columns are `rmsk_name` (text), `rmsk_family` (text), `rmsk_class` (text), `record_count`
(int64), `instance_count` (int64) and `record_length_sum_bp` (int64), in that order.
Each distinct source triple has one row, sorted by name, family and class. `instance_count`
counts distinct `rmsk_instance_id` values among the triple's records. The length sum retains
overlapping records. A name may carry several source labels; canonical rollups join through
`taxonomy_canonical`.

### `universes.json`

Schema version `1` defines `default_universe: "interspersed"` and a `universes` array. Each
entry contains `name`, a one-sentence `description`, `predicate` and `provisional_classes`.
The build evaluates the same predicate objects that it publishes.

`class_in` selects exact raw class labels. `family_prefix_excluded` applies a case-sensitive
prefix exclusion to raw family labels. Clauses within an object combine with AND; `{}` selects
every record.

| Universe | Predicate |
|---|---|
| `all_rmsk` | Every record. |
| `interspersed` | Class in SINE, LTR, LINE, DNA, RC, Retroposon, Unknown, Unspecified, DNA?. |
| `interspersed_plus_satellites` | Class in the `interspersed` classes plus Satellite. |
| `retrotransposon_derived` | Class in SINE, LTR, LINE, Retroposon. |
| `satellites` | Class equals Satellite. |
| `compat_tetranscripts_mm39` | `interspersed_plus_satellites` classes with the `tRNA` family-prefix exclusion. |

`interspersed` and `interspersed_plus_satellites` flag Unknown, Unspecified and DNA? members
as provisional. The other universes have empty `provisional_classes` arrays.
`config/<genome>.classes.tsv` has exactly two columns, `rmsk_class` and `disposition`, with one
row per class and dispositions from `interspersed`, `satellite`, `simple_repeat`, `low_complexity`
and `structural_rna`. The build requires the observed class set to equal the reviewed set,
the disposition `interspersed` to agree with the authored predicate class by class, the
disposition `satellite` to mark exactly `Satellite`, and every provisional class to be dispositioned
`interspersed`. Core checks compare measured counts with `tests/expectations/<genome>/class_census.tsv`.

The core `compat_tetranscripts_mm39` view supplies membership. Acceptance compares all 3,799,629
members with the checksum-pinned packaged legacy GTF, including the coordinate multiset.
The gene child publishes the corresponding exon-subtracted SAFs.

### `tables/universe_members.tsv.gz`

Columns are `universe_name` (text), `rmsk_record_id` (text) and `provisional` (bool), sorted
by universe and record key. Each selected record appears once per universe. Membership for
`all_rmsk` is implicit in the complete canonical table; the file contains the other five universes.

### `tables/universe_summary.tsv`

Columns are `universe_name` (text), `records` (int64), `names` (int64), `triples` (int64) and
`length_sum_bp` (int64), sorted by universe name. All six universes appear. `triples` counts
distinct raw `(rmsk_name, rmsk_family, rmsk_class)` labels; summed record lengths retain overlaps.

### Serialization

TSV files use UTF-8, LF endings, tabs and one header. Integers use decimal notation, floating
point values use a period decimal separator, and booleans use `true` and `false`. Text retains
case, literal `Unknown` and empty strings. Every field in these tables is required; source values must
be free of embedded tabs and line endings. Readers supply explicit schemas, including text
instance IDs. The reserved null token for nullable companion fields is `\N`.

`universes.json` uses insertion order, indent 2, `ensure_ascii=False`, UTF-8 and one final LF.
Its `schema_version` owns predicate semantics; adding a predicate key requires a version bump.

Readers use the column schemas above, including text `rmsk_instance_id`, signed int64 numeric
fields and literal empty strings. TSV quoting is disabled. Each nullable column declares its
null literal before publication.

| Reader | Explicit settings |
|---|---|
| pandas | `read_csv(path, sep="\t", dtype=types, quoting=csv.QUOTE_NONE, keep_default_na=False, na_filter=False)`; `types` maps text to `str`, integers to `"int64"`, floats to `"float64"` and booleans to `bool`. |
| DuckDB | `read_csv(path, delim='\t', header=true, auto_detect=false, columns=types, quote='', escape='', nullstr='\N')`; `types` maps text to `VARCHAR`, integers to `BIGINT`, floats to `DOUBLE` and booleans to `BOOLEAN`. |
| R data.table | `fread(path, sep="\t", header=TRUE, quote="", na.strings=NULL, strip.white=FALSE, colClasses=types, integer64="integer64")`; `types` maps text to `character`, int64 fields to `integer64`, floats to `numeric` and booleans to `logical`. |
| R arrow | `read_delim_arrow(path, delim="\t", col_types=types, quote="", escape_double=FALSE, escape_backslash=FALSE, na=character(), as_data_frame=FALSE)`; the Arrow schema uses `utf8()`, `int64()`, `float64()` and `boolean()`. `read_parquet(path, as_data_frame=FALSE)` retains the embedded typed schema. |

Gzip files have `mtime=0` and an empty embedded filename. Parquet uses an explicit required
schema with int64, float64, bool and UTF-8 string types. Both record serializations load to equal
typed rows. Identical input produces byte-identical tables and universe definitions under the
same builder and serialization libraries.

## Canonical taxonomy

### `tables/taxonomy_canonical.tsv`

One row per `rmsk_name`, sorted by name, derives canonical labels and rank statuses from the raw
taxonomy. The 15 columns appear in this order. Canonical family identity is
`(canonical_class, canonical_family)`; several names share a family.

| Column | Type | Contract |
|---|---|---|
| `rmsk_name` | text | Unique source repeat name within the build. |
| `canonical_class` | text | Winning normalized class; empty for an unresolved class. |
| `canonical_family` | text | Winning normalized family, class token for an unspecified family, or empty for an unresolved family. |
| `class_status` | text | Class resolution status under `taxonomy_rule_v1`. |
| `family_status` | text | Family resolution status under `taxonomy_rule_v1`. |
| `class_plurality_share` | float64 | Largest normalized class instance count divided by every label instance of the name, rounded to three decimals. |
| `family_plurality_share` | float64 | Largest specified family instance count divided by specified-family instances within the winning class, rounded to three decimals. |
| `family_support_share` | float64 | Largest specified family instance count within the winning class divided by every label instance of the name, rounded to three decimals. |
| `label_count` | int64 | Number of distinct raw class/family labels for the name. |
| `record_count` | int64 | Sum of raw label record counts for the name. |
| `instance_count` | int64 | Sum of raw label instance counts for the name. |
| `record_length_sum_bp` | int64 | Sum of raw label record lengths for the name, retaining overlaps. |
| `median_divergence_pct` | float64 | Median of `divergence_pct` across the name's records, rounded to two decimals. |
| `has_uncertain_source` | bool | Any raw class or family token carries a trailing `?`. |
| `has_multiple_labels` | bool | `label_count > 1`. |

The versioned rule `taxonomy_rule_v1` weights each raw label by `instance_count` and resolves
class first, then family within the winning class. Record counts and lengths supply context.

1. Strip a trailing `?` from every class and family token and set `has_uncertain_source = true` when any raw token carries that suffix.
2. Treat an empty family or a normalized family equal to its normalized class as unspecified, contributing its instance count to the class vote and abstaining from the family vote.
3. Select the class with the most instances and the specified family with the most instances within that class; a winning class with zero specified-family votes publishes `canonical_family = canonical_class` and `family_status = unspecified`.
4. Publish `unresolved` at a tied rank and below, with empty canonical fields at those ranks; ties use integer instance counts, and shares supply display values.

Class statuses are `concordant`, `resolved_uncertainty_suffix`, `resolved_plurality` and
`unresolved`. Family statuses are `concordant`, `resolved_uncertainty_suffix`,
`resolved_unspecified`, `resolved_plurality`, `unspecified` and `unresolved`.
Status precedence per rank is plurality over unspecified abstentions over uncertainty suffix
over concordant. `resolved_plurality` identifies a contested vote's winner;
`resolved_unspecified` identifies a specified family chosen alongside abstentions;
`unspecified` identifies the class-token family convention.

Family votes come exclusively from specified families within the winning class. A rank with zero
available votes publishes share `0`; tied ranks retain their tied shares. Both family shares are
`0` when class is unresolved or the winning class has zero specified-family votes.
The pure `resolve` function is total over typed votes: empty inputs, empty normalized classes
and nonpositive counts return both ranks unresolved. The build validates distinct raw triples,
names, normalized classes, positive counts and lengths, instance counts bounded by record counts,
and agreement with parquet name sets and record counts.

### `tables/taxonomy_resolution_report.tsv`

One row per name with `label_count > 1`, sorted by name, records its raw votes and canonical decision.
Membership counts distinct raw labels, so a `?` variant alone places a name in the report and
exposes its suffix decision. Columns appear in this order:

| Column | Type | Contract |
|---|---|---|
| `rmsk_name` | text | Source repeat name with multiple distinct raw labels. |
| `rmsk_labels` | text | Raw `class/family=<instances>;...` labels sorted by descending instance count, then class and family. |
| `rmsk_label_records` | text | Raw `class/family=<records>;...` labels in the same order as `rmsk_labels`. |
| `rule_version` | text | Applied rule version, `taxonomy_rule_v1`. |
| `canonical_class` | text | Canonical class from `taxonomy_canonical`. |
| `canonical_family` | text | Canonical family from `taxonomy_canonical`. |
| `class_status` | text | Class status from `taxonomy_canonical`. |
| `family_status` | text | Family status from `taxonomy_canonical`. |

Family and class rollups join each name once through `taxonomy_canonical` and conserve each
name's count. Resolved family buckets use `<canonical_class>/<canonical_family>`; resolved class
buckets use `<canonical_class>`. Unresolved ranks retain empty canonical fields, and rollups use
`unresolved_class_<rmsk_name>` or `unresolved_family_<rmsk_name>`, one bucket per name per rank.
These tokens are free of `/`, `:` and `|` and occupy the corresponding rank's export field.

The four spellings of "no family" are `<class>/<class>` under the abstention convention,
`Unknown/Unknown`, `Unspecified/Unspecified` and `unresolved_family_<name>` for a tied family
rank. `Unknown` and `Unspecified` retain their literal source classification.

The pinned Dfam snapshot under `tests/fixtures/taxonomy/` supplies test evidence; the build derives
labels from the two source tables under `tables/`. Every report name requires a snapshot row,
and every snapshot name belongs to the canonical table. Agreement compares each type and subtype
that Dfam names. Snapshot rows may also cover concordant names. The snapshot covers class
`DNA`; `Unknown` and `Unspecified` have their evidence in the raw source labels.
`tests/expectations/mm39/taxonomy_census.tsv` records the measured acceptance census, including
snapshot row count. The snapshot provenance records its fetch date, endpoint pattern, source,
role and per-family version evidence; the release endpoint response is required for its next refresh.

Check 30 proves the published canonical table equals the rule's output on every row.
`tests/fixtures/taxonomy/rule_cases.tsv` through check 32 proves the rule itself, including ties, plurality and weighting cases mm39 never exercises.

### Dfam lineage, ranks and clades

The tracked Dfam 4.0 snapshot under `data/dfam/` supplies metadata for the 1,220
`interspersed` names. Stage 25 reads its checksum-verified copy under `source/`.
The snapshot provenance JSON is retained beside it in the 52-file core payload.
The verifier reads its `file_sha256`, `payload_sha256`, `dfam_version` and `fetch_finished` keys.
The fetch script accepts a canonical taxonomy path, query census (`--census`), universe
and output directory. The census TSV's `rmsk_name` column contains each selected name once;
`census_sha256` and `taxonomy_sha256` record the respective input file digests.
Source refresh is an explicit preparation step. Canonical RepeatMasker labels remain
resolved by `taxonomy_rule_v1`.

`tables/taxonomy_dfam.tsv` contains one row per selected name, sorted by `rmsk_name`.
Its columns appear in the following order; text uses empty strings for absent values,
counts and lengths use decimal integers, and the uncertainty flag uses `true`/`false`.

| Columns, in order | Contract |
|---|---|
| `rmsk_name`, `rmsk_class`, `rmsk_family` | Name and raw tokens of its canonical plurality label; remaining raw-label ties sort by instance count descending, class and family ascending. |
| `canonical_class`, `canonical_family`, `record_count` | Canonical labels and selected catalog records counted by name. |
| `match_status` | `exact`, `part_model_set` or `missing`. |
| `dfam_accessions`, `dfam_model_names`, `dfam_model_versions`, `dfam_model_lengths_bp` | Parallel `;`-joined model fields in role order: `whole`, or `5end`, `orf2`, `3end`. |
| `available_part_count`, `part_roles_present`, `model_length_sum_bp` | Available part count (zero for exact/missing), ordered part roles, and sum of selected model lengths (zero for missing). |
| `classification_path`, `classification_leaf` | Common Dfam classification path and its final node name. |
| `clades`, `clade_count`, `clade_leaves`, `clade_compatibility` | Every model clade path and leaf, deduplicated in first-seen order and joined with `;`; count of distinct complete clade paths across the selected models (zero for missing); compatibility status. |
| `dfam_release`, `wicker_code`, `wicker_code_uncertain` | Snapshot release, nearest coded ancestor's Wicker equivalent, and a trailing `?` uncertainty flag. |
| `wicker_class`, `wicker_class_status`, `wicker_subclass`, `wicker_subclass_status` | Wicker class and subclass with separate statuses. |
| `wicker_order`, `wicker_order_status`, `wicker_superfamily`, `wicker_superfamily_status` | Wicker order and superfamily with separate statuses. |
| `wicker_family`, `wicker_family_status`, `subfamily`, `subfamily_status` | Dfam leaf family and RepeatMasker name with separate statuses. |
| `dfam_repeat_type`, `dfam_repeat_subtype` | Matched models' type/subtype names, deduplicated in role order and joined with `;`. |

A summary hit named exactly `rmsk_name` wins. Otherwise, hits named `<name>_5end`,
`<name>_orf2` and `<name>_3end` form a part set, including L1 and L2/CR1 models.
Every selected accession requires a full metadata record. Part paths must agree;
a disagreement fails with `Dfam part classification disagreement: <name>`.
There are 1,047 exact names (2,797,852 records), 147 part sets (928,528 records),
and 26 missing names (38,569 records). The part sets contain three, two and one
models for 30, 9 and 108 names respectively. The six L2/CR1 sets are L2a, L2b,
L2c, L2d, L2d2 and L3b. `model_length_sum_bp` summarizes available metadata;
full-length inference requires a validated projection between the part models
and the pinned RepeatMasker model coordinates.

The rank scheme is `rank_scheme_wicker_v1`, recorded in
`MANIFEST.json` at `identity.rank_scheme_version`. Wicker class I comprises
retrotransposons with an RNA intermediate; class II comprises DNA transposons.
Class II subclass 1 contains TIR and Crypton orders, and subclass 2 contains
Helitron and Maverick. Class I subclass is `inapplicable`. Order identifies the
transposition group: LINE, LTR, SINE, PLE, DIRS, TIR, Crypton, Helitron or Maverick.
Superfamily identifies a lineage within an order, such as L1, ERV, hAT or
Tc1-Mariner. Wicker families use the 80-80-80 sequence-similarity convention;
this view takes the curated Dfam leaf name as its family label. A subfamily here
is the set of catalog records sharing one RepeatMasker name.

| Dissertation rank alias | Wicker rank |
|---|---|
| class | class |
| subclass | order |
| superfamily | superfamily |
| family | family |
| subfamily | subfamily |

The nearest classification node carrying `wicker_equiv` supplies the code.
Parenthesized names supply order and superfamily; bare letters use the Wicker
letter table, including P element under TIR, I under LINE and Helitron under
Helitron. Derived ranks are `mapped` for a leaf code and `inherited` for an
ancestor code; absent code parts leave deeper ranks `missing`. A part set uses
`part_model_set` on derived ranks, with the class I subclass `inapplicable`.
`wicker_family` uses the leaf with `mapped` or `part_model_set`; an absent code
leaves every Wicker rank `missing`. `subfamily` always holds the name with status
`mapped`. Among exact names, 884 have leaf codes, 110 inherit codes and 53 have
missing codes under `Unknown`.

RepeatMasker tokens span several ranks. B1 names sit under `Alu`; `ERVL-MaLR`
identifies a curated LTR branch; hyphenated labels such as `hAT-Charlie` combine
superfamily and family information. Class-less annotations retain their source
labels. Every Wicker rank is `missing` for the 53 names whose Dfam leaf is `Unknown`.
The class-less name `UCON4`, labeled `Unspecified` in the source, has the Dfam leaf
`Kolobok` and inherits code `D` and class `Class II (DNA transposons)`.

The normalized companions provide direct SQL joins. Their columns appear in order:

| Table | Grain and columns |
|---|---|
| `tables/taxonomy_dfam_models.tsv` | 1,263 name × model rows: `rmsk_name`, `role`, `accession`, `model_name`, `model_version`, `model_length_bp`, `classification_path`, `clades`, `repeat_type`, `repeat_subtype`. Sorted by name and declared role order. |
| `tables/dfam_lineage_nodes.tsv` | 300 classification nodes: `full_path`, `parent_path`, `name`, `depth`, `wicker_code`, `repeatmasker_type`, `repeatmasker_subtype`, `family_count`. Sorted by path; root depth is zero and parent is empty. `family_count` is the node's count when present, otherwise empty. 193 nodes carry a code. |
| `tables/dfam_model_clades.tsv` | 1,278 model × clade rows: `accession`, `clade_path`, `clade_leaf`. Sorted by accession and path, with unique pairs. |

Paths use `;` between nodes; the normalized clade table preserves each complete
path separately. `clades` is a display field in both taxonomy tables;
`dfam_model_clades.tsv` supplies the accession join key and complete paths for clade queries.
A model's clade is its curated assignment. `clade_compatibility`
is `primate_branch` when any path contains the `Primates` node, then `multi_clade`
when any model has several clades, otherwise `compatible`; a missing match is
`missing`. Nine models have multiple clades; 33 models across 31 names have a
Primates branch. Consumers derive age tiers from the clade path with
`taxonomy_canonical.median_divergence_pct` and per-record divergence beside it.

## Legacy audit schemas

The earlier audit experiments used `te_loci.tsv.gz` and `te_dim.tsv`; those experiments reside
under `_scratch/te-tracks-audit/legacy_release_experiments/`. The retained external reconciliation
oracle is `GRCm39_Ensembl_rmsk_TE.gtf.gz` in the host refcache. The schemas below document
the migration vocabulary of the earlier experiments.

### `te_loci.tsv.gz` — legacy canonical table, 1-based

One row per locus admitted by the legacy class and family filters.

| # | Column | Note |
|---|---|---|
| 1 | `locus_id` | `<subfamily>\|<chrom>:<start>-<end>\|<strand>`, the legacy join key |
| 2 | `chrom` | UCSC names |
| 3 | `start` | 1-based inclusive |
| 4 | `end` | Inclusive |
| 5 | `strand` | `+` or `-` |
| 6 | `subfamily` | UCSC `repName` |
| 7 | `family` | UCSC `repFamily` |
| 8 | `class` | UCSC `repClass` |
| 9 | `sw_score` | RepeatMasker Smith-Waterman score |
| 10 | `perc_div` | Percent divergence from the consensus |
| 11 | `perc_del` | Percent deletion |
| 12 | `perc_ins` | Percent insertion |
| 13 | `rmsk_id` | UCSC `id`, a one-character value without fragment-linking meaning |
| 14 | `length_bp` | `end - start + 1` |
| 15 | `dup_index` | Per-subfamily ordinal for `subfamily_dupN` compatibility |

The RepeatMasker `.out` ID column is the instance key; `tables/rmsk_instance_members.tsv.gz`
records its membership.

### `te_dim.tsv` — legacy dimension table

Columns are `subfamily`, `family`, `class`, `n_loci` and `total_bp`. Each row summarizes one
source `(subfamily, family, class)` triple.

## Exports

Exports follow `exports/<contig_namespace>/<universe>/<interval_variant>/<level>[_<profile>].<format>`.
The core release supplies eight `interspersed` full-interval exports in each of the `ucsc`,
`ensembl` and `gencode` contig namespaces. The gene child family supplies `exon_subtracted`
intervals under its GENCODE vM37 annotation pin. Each emitted feature and block registers to source records through
`tables/export_feature_members.tsv.gz`.

### Legacy names and their disposition

| Legacy name | Disposition |
|---|---|
| `te_subfamily.saf` | `subfamily.saf` |
| `te_locus.saf` | A record-level SAF enters a release with a named consumer and a passing fixture ([ADR 3](DECISIONS.md#3-delivered-scope)); record-level counting reads `record.bed` or `record.gtf` |
| `te_subfamily.bed` | `subfamily.bed` |
| `te_locus.bed` | `record.bed` |
| `te_subfamily.gtf` | `subfamily.gtf` |
| `te_locus.gtf` | `record.gtf` |
| `te_locus.locInd` | `.locInd` index built from `record.gtf` by TElocal's own indexer (fixture) |
| `te_subfamily_noExon.saf` | `exon_subtracted/subfamily.saf` in `te_mm39_gene` |
| `te_context_*.saf` | Delivered as child `tables/record_transcript_context.tsv.gz` |
| `locus_context.tsv` | Delivered as child `tables/record_context.tsv.gz` |
| `rename_map.tsv` | Superseded by `tables/taxonomy_canonical.tsv`; the legacy selection is reproducible as the `compat_tetranscripts_mm39` membership |
| `te_loci.tsv.gz` | `tables/rmsk_records.tsv.gz` |
| `te_loci.parquet` | `tables/rmsk_records.parquet` |
| `te_dim.tsv` | `tables/rmsk_taxonomy.tsv` and `tables/universe_summary.tsv` |
| Legacy `MANIFEST.json` | `MANIFEST.json` with `identity` and `provenance` sections |
| Legacy `BUILD_ID` | `BUILD_ID` computed from the manifest `identity` section |
| `ensembl_named/` | `exports/ensembl/` |

### UCSC full-interval exports

Nine exports reside under `exports/ucsc/`: eight interspersed files under
`exports/ucsc/interspersed/full/` and the complete-catalog record BED under `exports/ucsc/all_rmsk/full/`.
The builder accepts an explicit universe and export set, validates the universe in `universes.json`,
and selects interspersed records through `tables/universe_members.tsv.gz`. Interspersed provisional
flags follow each record's raw class and are keyed by `(universe_name, rmsk_record_id)` in
`tables/universe_members.tsv.gz`.

Every file is uncompressed UTF-8 with LF endings, sorted by its contig column in C-locale
byte order, start and end numerically, strand, then its own name column in byte order
(BED column 4, GTF column 9, SAF `GeneID`). Each selected record supplies
one full interval in every export. Identifier components match `[A-Za-z0-9_.+?()-]+`; emitted
identifiers additionally admit the separators `|`, `:` and `/`. The builder validates every
BED name, GTF attribute value and SAF GeneID and reports the offending value and file on failure.

| File | Coordinates | Feature identity |
|---|---|---|
| `record.bed` | 0-based half-open | BED6 name = `rmsk_record_id` |
| `subfamily.bed` | 0-based half-open | BED6 name = `rmsk_name` |
| `family.bed` | 0-based half-open | BED6 name = `<class>/<family>`; each position carries its canonical label or `unresolved_<rank>_<rmsk_name>` token |
| `record.gtf` | 1-based inclusive | Exon rows; `gene_id` = `rmsk_name`; `transcript_id` and `locus` = record alias |
| `record_starsolo.gtf` | 1-based inclusive | Exon rows; `gene_id`, `transcript_id` and `locus` = record alias; `gene_name` = `rmsk_name` |
| `subfamily.gtf` | 1-based inclusive | Exon rows; `gene_id`, `transcript_id` and `locus` = `rmsk_name` |
| `subfamily.saf` | 1-based inclusive | `GeneID` = `rmsk_name` |
| `taxonomy_triple.saf` | 1-based inclusive | Canonical taxonomy-triple grouping; `GeneID` = `<rmsk_name>:<canonical_family>:<canonical_class>` |

#### `record.bed`

BED6 columns are `chrom`, `start_1 - 1`, `end_1`, `rmsk_record_id`, `min(sw_score, 1000)` and
`strand`. Coordinates are 0-based half-open. Column 4 identifies the source record for IRescue
and interval operations.

The clipped BED score is a display convention; `rmsk_records.sw_score` is the filterable value.
Among interspersed records, 1,224,713 (32.5%) have a source score above 1,000.

Check contig and coordinate order with `LC_ALL=C sort -c -t$'\t' -k1,1 -k2,2n -k3,3n record.bed`.

#### `subfamily.bed`

BED6 uses the same 0-based half-open columns and clipped score as `record.bed`, with
`rmsk_name` in column 4. Repeated names group records into subfamilies for IRescue.

#### `family.bed`

BED6 uses 0-based half-open coordinates and the clipped score, with `<class>/<family>` in
column 4. The two positions carry the name's canonical labels. An unresolved class occupies
the class position as `unresolved_class_<rmsk_name>`; an unresolved family occupies the family
position as `unresolved_family_<rmsk_name>`. Family identity includes its class.
The prefix `unresolved_` is reserved for generated rank tokens; the exporter rejects resolved
canonical class or family labels beginning with it.

#### `record.gtf`

One exon row per record uses the nine GTF columns: `chrom`, `te-tracks`, `exon`, `start_1`,
`end_1`, `sw_score`, `strand`, `.`, and attributes. Coordinates are 1-based inclusive and the
score retains its source value. The colon-free record alias is
`R|mm39|<rmsk_name>|<chrom>|<start_1>|<end_1>|<strand>`; the instance alias is
`I|mm39|<rmsk_instance_id>`. Record aliases retain UCSC contig names; both aliases stay fixed
across namespace exports.

Attributes appear in this order: `gene_id`, `transcript_id`, `locus`, `family_id`, `class_id`,
`rmsk_family`, `rmsk_class`, `instance_id`, `rmsk_record_id`. Each is written as `key "value";`,
with one space between attributes. Stellarscope's default `locus` groups by record;
`--attribute instance_id` selects the source instance grouping.

#### `record_starsolo.gtf`

One exon per record uses the fixed columns of `record.gtf`. Attributes appear in
this order: `gene_id`, `transcript_id`, `gene_name`, `gene_type`, `locus`, `rmsk_name`,
`family_id`, `class_id`, `rmsk_family`, `rmsk_class`, `instance_id`, `rmsk_record_id`.
`gene_id`, `transcript_id` and `locus` equal the record alias; `gene_name` and
`rmsk_name` equal the source name; `gene_type` is `transposable_element`.
Canonical and source taxonomy and instance/record identities use the mappings below.
Each namespace has 3,764,949 rows and distinct genes on 59 contigs. Registration
reuses `(interspersed, full, record, record_alias)` and retains 30,119,592 rows.

#### `subfamily.gtf`

One exon row per record uses the same fixed GTF columns and 1-based inclusive coordinates.
Attributes appear in this order: `gene_id`, `transcript_id`, `locus`, `family_id`, `class_id`,
`rmsk_family`, `rmsk_class`. The first three values equal `rmsk_name`, supplying subfamily
identity for Stellarscope, TEsingle and TElocal.

The following attribute mapping covers the GTF profiles. TEtranscripts groups by
`gene_id:family_id:class_id`; TEsingle and TElocal use
`transcript_id:gene_id:family_id:class_id`. Canonical ranks come from the name's row in
`taxonomy_canonical`; an unresolved rank emits `unresolved_<rank>_<rmsk_name>` in its position.

| Attribute | Source column or transformation | Consumer that reads it |
|---|---|---|
| `gene_id` | Record alias in `record_starsolo.gtf`; `rmsk_records.rmsk_name` in the other profiles | STARsolo, cellranger, TEtranscripts, TEsingle, TElocal |
| `gene_name`, `rmsk_name` (STARsolo profile) | `rmsk_records.rmsk_name` | Display and taxonomy joins |
| `gene_type` (STARsolo profile) | `transposable_element` | cellranger `mkgtf` filter |
| `transcript_id` | Record alias in `record.gtf` and `record_starsolo.gtf`; `rmsk_name` in `subfamily.gtf` | TEsingle, TElocal |
| `locus` | Record alias in `record.gtf` and `record_starsolo.gtf`; `rmsk_name` in `subfamily.gtf` | Stellarscope default grouping |
| `family_id` | `taxonomy_canonical.canonical_family` or unresolved family token | TEtranscripts, TEsingle, TElocal |
| `class_id` | `taxonomy_canonical.canonical_class` or unresolved class token | TEtranscripts, TEsingle, TElocal |
| `rmsk_family` | `rmsk_records.rmsk_family` | Source-taxonomy audit readers |
| `rmsk_class` | `rmsk_records.rmsk_class` | Source-taxonomy audit readers |
| `instance_id` (record GTF profiles) | `I\|mm39\|<rmsk_instance_id>` | Stellarscope with `--attribute instance_id` |
| `rmsk_record_id` (record GTF profiles) | `rmsk_records.rmsk_record_id` | Registration and catalog joins |

#### `subfamily.saf`

Tab-separated SAF starts with the header `GeneID`, `Chr`, `Start`, `End`, `Strand`.
Each data row contains `rmsk_name`, `chrom`, `start_1`, `end_1`, `strand`, using 1-based
inclusive coordinates. featureCounts groups intervals sharing the subfamily GeneID.

#### `taxonomy_triple.saf`

Tab-separated SAF uses the same header and 1-based inclusive intervals as `subfamily.saf`.
GeneID is `<rmsk_name>:<canonical_family>:<canonical_class>`, with unresolved rank tokens in
their family or class positions. Canonical labels are a function of the name, so the 1,220
interspersed names yield 1,220 GeneIDs, including the 20 names carrying two raw labels.
The filename identifies the legacy lab taxonomy grouping read by featureCounts.

#### `tables/export_feature_members.tsv.gz`

Columns appear in this order:

| Column | Type | Contract |
|---|---|---|
| `universe_name` | text | Selected membership, `interspersed` or `all_rmsk`. |
| `variant` | text | Interval support, `full`. |
| `feature_level` | text | `record`, `subfamily`, `family`, `taxonomy_triple` or `instance`. |
| `key_grammar` | text | `rmsk_record_id`, `record_alias`, `four_tuple`, `rmsk_name`, `family_bucket`, `taxonomy_triple` or `instance_alias`. |
| `emitted_feature_id` | text | Exact emitted feature identifier at that level and grammar. |
| `rmsk_record_id` | text | Member record in the canonical table. |
| `block_start_1` | int64 | Retained block start, 1-based inclusive. |
| `block_end_1` | int64 | Retained block end, inclusive. |

Uniqueness holds over `(universe_name, variant, feature_level, key_grammar, emitted_feature_id,
rmsk_record_id, block_start_1, block_end_1)`. The `full` variant registers one block per member
at each level and grammar, equal to the record bounds. Each interspersed record registers eight
spellings in this order; `name` is `rmsk_name`, and `family_id` and `class_id` are the canonical
or positional unresolved tokens emitted by the GTFs.

| Order | `feature_level` | `key_grammar` | `emitted_feature_id` |
|---|---|---|---|
| 1 | `record` | `rmsk_record_id` | `rmsk_record_id` |
| 2 | `record` | `record_alias` | `R\|mm39\|<name>\|<chrom>\|<start_1>\|<end_1>\|<strand>` |
| 3 | `record` | `four_tuple` | `<record alias>:<name>:<family_id>:<class_id>` |
| 4 | `subfamily` | `rmsk_name` | `rmsk_name` |
| 5 | `subfamily` | `four_tuple` | `<name>:<name>:<family_id>:<class_id>` |
| 6 | `family` | `family_bucket` | `<class_id>/<family_id>` |
| 7 | `taxonomy_triple` | `taxonomy_triple` | `<name>:<family_id>:<class_id>` |
| 8 | `instance` | `instance_alias` | `I\|mm39\|<rmsk_instance_id>` |

Emitted IDs retain UCSC names inside record identities and are namespace-invariant; the same
registration serves all three namespaces. Rows follow export record order, then the spelling
order above. Gzip uses the deterministic table serialization above. The mm39 interspersed
registration has 30,119,592 rows and 3,152,636 distinct instance aliases.

A run's matrix binds to one `(universe_name, variant, feature_level, key_grammar)`.
Counts join the registration through the run's measured feature IDs at that full scope.
Check 43 joins 1,000 shared records: the level/grammar pair returns 2,000 rows,
while the four-field scope returns 1,000 and conserves the count total.
A traversal from records to registration lists possible support; counts come from the scoped matrix join.
Selecting supporting records selects each distinct measured feature once before summing its count.
A mixed-name instance attributes to a subfamily only through an explicit allocation.
The mm39 interspersed selection includes 30,569 mixed-name instances holding 95,830 records.

#### `tables/exports.tsv`

One row per export file, sorted by `export_path`, inventories these columns in order:

| Column | Type | Contract |
|---|---|---|
| `export_path` | text | Path relative to the build directory. |
| `namespace` | text | Contig-column namespace: `ucsc`, `ensembl` or `gencode`. |
| `universe_name` | text | Registered universe, `interspersed` or `all_rmsk`. |
| `variant` | text | Registered interval variant, `full`. |
| `feature_level` | text | Export's default feature level. |
| `format` | text | `bed`, `gtf` or `saf`. |
| `rows` | int64 | Data rows; SAF headers are counted separately. |
| `distinct_features` | int64 | Distinct values of the declared feature identity: BED names, GTF `locus` or STARsolo-profile `gene_id`, and SAF GeneIDs. |
| `sha256` | text | SHA-256 of the complete emitted file bytes. |

### Consumer contracts

`tests/run.sh consumers` reports parser and executable support separately. The local checkout
parsers establish feature identity; executable fixtures establish the stated counting and overlap
behavior. Each consumer suite run shares a private temporary fixture directory across its checks;
`TE_TRACKS_CONSUMER_FIXTURES` selects a retained directory.
`00_tool_inventory.required.py` is reporting-only for executable availability; its in-process import
self-test verifies exit 1 for a missing symbol and exit 3 for an absent external module.
Every checkout parser support line reports its declared version and `git describe --tags --always`.
The table names the checkout commit each fixture authorizes; an installed release may differ in
the exercised entry points, including IRescue's `makeRmsk` and MATES's `split_count_10X_data`.
Checks 00, 10, 12, 13, 14, 16, 17, 22 and 23 are required; unsupported status in any of them fails the runner.
Checks 11, 15, 20, 21, 24, 25 and 30 report optional support.

| Consumer / authorized checkout | Export read | Feature identity | Registration `(feature_level, key_grammar)` | Fixture in `tests/checks/consumers/` | Support in-container |
|---|---|---|---|---|---|
| IRescue 1.2.0, `26f36fb` | `record.bed`, `subfamily.bed` | BED column 4 | `(record, rmsk_record_id)`, `(subfamily, rmsk_name)` | `10_irescue_parser.required.py`: roster identities and coordinates, 11 record features, 8 names, comma splitting and exporter rejection; `15_irescue_chrcat.py`: real `chrcat` serialization; `20_irescue_exec.sh`: 2 molecules versus 1+1, 4/2 and 3/3 allocation | Identity parser and `chrcat` supported; execution supported with consumer environment |
| STARsolo 2.7.11b | `record_starsolo.gtf` plus host GTF | `gene_id`; `gene_name` supplies display labels | `(record, record_alias)` under `interspersed/full` | `17_starsolo_profile.required.py`: attributes, namespaces, one-base endpoints, collision preflight; `24_starsolo_exec.sh`: index, Gene/GeneFull matrices, same-name genes, gaps, gene–TE EM conservation | Parser and execution supported with consumer environment |
| cellranger 10.1.0 | `record_starsolo.gtf` plus host GTF | `gene_id` | `(record, record_alias)` under `interspersed/full` | `25_cellranger_mkref.sh`: `mkgtf` retains TE/host biotypes; `mkref` preserves aliases and creates STAR index | Reference construction supported with consumer environment |
| Stellarscope 1.5, `0e0d594` | `record.gtf`, `subfamily.gtf` | `locus` for records or subfamilies; `instance_id` in record GTF | `(record, record_alias)`, `(subfamily, rmsk_name)`, `(instance, instance_alias)` | `11_stellarscope_parser.py`: isolated annotation package, 11 records, 10 instances, attributes, registration joins, endpoint gate | Parser exercised; unsupported: right-boundary overlap defect, observed `0,1,1,1`, expected `0,1,1,0`; executable `stellarscope` available through the consumer environment |
| TEsingle 1.0, `655f127` | `record.gtf`, `subfamily.gtf` | `transcript_id:gene_id:family_id:class_id` | `(record, four_tuple)`, `(subfamily, four_tuple)` | `12_tesingle_parser.required.py`: 11 record tuples, 8 subfamily tuples, registration joins, BAM `UR` cutoff at 1,000, reverse-strand annotation and duplicate/QC-fail read filtering | Parser supported; executable `TEsingle` available through the consumer environment |
| TEtranscripts 2.2.4, `e7f9b93` | `record.gtf`, `subfamily.gtf` | `gene_id:family_id:class_id` | `(taxonomy_triple, taxonomy_triple)` | `13_tetranscripts_telocal_parser.required.py`: 8 groups through either GTF, registration joins | Parser supported; executable `TEcount` available through the consumer environment |
| TElocal 1.1.3, `1a168c2` | `.locInd` built from `record.gtf` by TElocal's own indexer; `subfamily.gtf` supplies subfamily grain | `transcript_id:gene_id:family_id:class_id` | `(record, four_tuple)`, `(subfamily, four_tuple)` | `13_tetranscripts_telocal_parser.required.py`: index construction and the checkout's pickle loader, semantic feature-tuple comparison, registration joins, 11 record or 8 subfamily features; the pickle embeds the GTF path | Parser and index round trip supported; executable `TElocal` available through the consumer environment |
| MATES 0.1.8, `87c1218`, optional adapter | Fixture-only `record_mates.csv` and `record_mates.bed`, eight columns each | Column 5 fixture roster ordinal; column 4 `TE_Name` group; column 7 raw class/family model group | `TE_Name`: `(subfamily, rmsk_name)`; integer index maps through the fixture roster | `14_mates_parser.required.py`: isolated source functions, pair agreement, companion stem, `?`/`Unknown` model filters; minimal `pkg_resources.resource_filename` stand-in | Adapter supported in isolation; installed package depends on `pkg_resources` (setuptools below 82), absent here |
| featureCounts | `subfamily.saf`, `taxonomy_triple.saf`; fixture `onebase.saf` | SAF `GeneID` | `(subfamily, rmsk_name)`, `(taxonomy_triple, taxonomy_triple)`; `OneBase` is fixture-only | `21_featurecounts_exec.sh`: `-s 0`, shared subfamily and triple features each count 2 fragments; one-base feature counts 1 read | Execution supported with consumer environment |
| bedtools 2.31.1 | `record.bed`, `family.bed` | BED column 4 retained by `intersect -wa -wb` | `(record, rmsk_record_id)`, `(family, family_bucket)` | `22_bedtools_exec.required.sh`: equal-coordinate names, right-adjacent query, `-s`/`-S`; `16_family_triple_readers.required.py`: canonical buckets and registration joins | Execution supported |
| 14761 ATAC route | `exports/<namespace>/all_rmsk/full/record.bed` | BED column 4, `rmsk_record_id` | `(record, rmsk_record_id)` under `all_rmsk` | Core checks 41 and 61: complete catalog, bounds, score clipping, one registered block per record and namespace identity | Export and registration supported |
| SAF column reader | `taxonomy_triple.saf` | SAF `GeneID` | `(taxonomy_triple, taxonomy_triple)` | `16_family_triple_readers.required.py`: 8 GeneIDs, three `TwoLab` rows sharing one triple, registration joins | Reader supported |
| samtools 1.21 | Fixture BAMs and their sequence dictionaries | BAM query name, strand and filter flags, `CB`/`UB`/`UR` tags | BAM integrity check | `23_samtools_fixture_integrity.required.sh`: sort order, indexes, alignment accounting, molecule counts by tag and flagged read names | Execution supported |

The authored oracle in `tests/fixtures/consumers/expected.json` specifies 11 records, 8 names and
10 instances. The production taxonomy resolver elects `TwoLab`'s `hAT-Tip100` family by 2:1
instance plurality; both GTFs retain its raw family labels. The production exporter writes all
eight exports from those tables. TElocal's loader branch is executed directly from its checkout.

The FASTA has seed 1729 and contigs `chrA` (5,000 bp) and `chrB` (3,000 bp). The ARC, OCM and
bulk BAMs each encode eleven molecules: one unique, one repeated, one multimapping, one in the
instance gap, four at the `Edge` boundaries, one on minus-strand `TwoLab` and two carrying
duplicate/QC-fail flags. They contain 13, 26 and 26 alignment records, respectively. Both
minus-strand roster records have reverse-strand reads. The ARC and OCM layouts carry `CB`, `UB`
and raw `UR`: `unique_a` copy 0 and `duplicate_b` copy 1 have one-base raw errors, yielding
11 corrected `UB` identities and 12 raw `UR` identities. The oracle includes flagged molecules
in these totals and records flagged query names per BAM. Bulk carries query and mate identities.
Separate counting fixtures preserve each assay layout and report IRescue's fitted
allocation in `irescue_allocation.json` when its executable is available.
The allocation check asserts registered identities, unique-molecule floors, upper bounds of
floor plus three, and a conserved total of nine. The activated environment observes
5.5/3.5 for 4/2 unique support and 4.5/4.5 for 3/3 in both ARC and OCM fixtures.
Every tagged fixture BAM carries one barcode, so whitelist, empty-cell and per-barcode threshold behaviour are the consumer's audit.

Stellarscope's endpoint gate expects `0,1,1,0` for the four reads against GTF `101..110`.
The checkout observes `0,1,1,1` and reports the right-boundary defect as unsupported. The gate
passes on `0,1,1,0` and fails on every other result. Its annotation dependency is `intervaltree`.
MATES resolves
`record_mates.csv` to its companion correctly; a dotted stem resolves to `record.bed`.
Its preparation fixture supplies coverage vectors and executes the upstream model-group filter.
MATES uses `consumers_scratch/mates/` beside the selected fixture directory and removes that workspace.
The MATES pair is fixture-only, its index is the fixture roster's ordinal, and a MATES release export requires a named consumer.
IRescue's five parser `.tsv.gz` files have mtime 0 and an empty gzip filename. TElocal indexes
are compared by feature tuples across GTF paths.
The DuckDB registration query verifies identity joins and conserved count totals.

The STARsolo fixture uses the seeded FASTA, eleven TE records and a two-exon host
gene. Read 1 carries a 16-base barcode and 12-base UMI; read 2 carries 40-base cDNA.
The index uses `--genomeSAindexNbases 4 --sjdbOverhang 39`; counting uses
`--soloType CB_UMI_Simple --soloCBwhitelist None --soloFeatures Gene GeneFull
--soloMultiMappers EM --soloStrand Unstranded --soloCellFilter None`.
Two same-name genes each receive one unique molecule. The gap molecule has zero
TE support, with host support in GeneFull. The exon-overlap fixture conserves
three molecules: Gene reports one unique molecule per host/TE and EM 1.5/1.5;
GeneFull reports one unique host molecule and EM 2.98266/0.0173415. The host-intronic
TE molecule gives Gene TE support 1 and GeneFull EM 0.5/0.5. These allocations are
recorded in `starsolo_allocation.json`; checks assert identity and conservation.
The unique matrix and `UniqueAndMult-EM.mtx` are separate outputs; the latter
already includes unique support.

The combined-annotation preflight requires distinct TE gene and transcript aliases,
consistent host transcript-to-gene identity, and host IDs outside the reserved
`R|mm39|` prefix. `cellranger mkgtf` retains `gene_type:transposable_element` and
`gene_type:protein_coding`; the check pins 3 GB with `mkref --nthreads=1 --memgb=3` and retains all eleven TE
genes and the host gene. `cellranger count`, chemistry and barcode policy belong
to the consuming module's recipe. Execution checks report the binary name when
it is absent from PATH. [RUNBOOK.md](RUNBOOK.md#consumer-environment) gives activation.

### Contig namespaces and qualification

The release supplies nine files per namespace: eight under
`exports/<namespace>/interspersed/full/` and `record.bed` under
`exports/<namespace>/all_rmsk/full/`.
The complete-catalog BED supplies 5,320,771 intervals to the 14761 ATAC route, with
`rmsk_record_id` as its name and the same clipped display score as the interspersed BED.
Stage 30 appends one `all_rmsk`, `record`, `rmsk_record_id` registration per catalog record
after the 30,119,592 interspersed registration rows.

The `ucsc` namespace uses the source `ucsc` alias column.
The `ensembl` namespace uses the source `ensembl` alias column.
The `gencode` namespace uses UCSC names without `_` and the GenBank alias for names containing `_`.
The GENCODE rule reproduces all 61 measured GRCm39 FASTA names and lengths.

#### Alias and coverage tables

`tables/contig_aliases.tsv` has 61 rows, sorted by `chrom_ucsc`, with columns
`chrom_ucsc`, `chrom_ensembl`, `chrom_gencode`, `chrom_genbank`, `chrom_refseq` and `length_bp`.
Each name column is injective; lengths come from the pinned `chrom.sizes` list.
Every catalog contig belongs to the alias table.

`tables/contig_coverage.tsv` has one row per source contig, sorted by `chrom_ucsc`, with columns
`chrom_ucsc`, `length_bp`, `records_all`, `records_interspersed`, `has_ensembl`, `has_gencode`
and `length_agrees`.
Counts include zero-record contigs; alias availability and length agreement are booleans.
Length agreement checks each source record's `end_1 + query_left_bp` against `chrom.sizes`;
zero-record contigs retain their source-list length.
`chr4_JH584295v1_random` and `chrM` carry zero interspersed records and 2 and 4 catalog records,
so the interspersed exports name 59 of the 61 contigs and the `all_rmsk` BED names all 61.

Stage 35 renames the contig column of each UCSC export through the alias table and sorts by
renamed contig in C-locale byte order, numeric start and end, strand and name.
Every other field retains its bytes, including UCSC names inside record IDs and GTF aliases.
The three namespaces share the same feature registrations.
`tables/exports.tsv` contains the sorted union of all 27 export paths and their measured SHA-256 digests.

#### Preflight

```bash
bin/te-tracks-preflight <export> <bam|fai|sizes>
```

Preflight reads contig names from BED/GTF column 1 or SAF column 2 and reference lengths from
a BAM header through pysam, a FASTA index or a two-column sizes TSV.
It walks up from the absolute export path as given, with symlinks unresolved, to the nearest
parent directory containing `MANIFEST.json` and requires that build's `tables/contig_aliases.tsv`.
The report prints `only_in_reference`, `only_in_export` and `length_disagreements` as JSON lists,
then `alias_table` as a JSON path string.
Exit 0 means every export contig is present in the reference with an agreeing length;
`only_in_reference` is informational. Exit 2 means the export names contigs the reference lacks
and the shared set is nonempty. Exit 1 means a shared contig disagrees in length, the
intersection is empty, or an input cannot be read.
Export completeness against its inventory is the manifest's job.

### Identity and publication

`MANIFEST.json` separates build `identity` from builder and validation `provenance`.
`BUILD_ID = sha256("te-tracks-build-v1\n" + canonical_json(identity))` covers the identity,
including the complete file inventory with SHA-256 digests. Verified staging builds install
once into `archive/<BUILD_ID>/`; an atomic replacement selects the single `current` symlink.

### Gene child family

`te_mm39_gene` pins one verified `te_mm39` parent by full `BUILD_ID`, one gene annotation
and a versioned policy bundle. The transcript-geometry snapshot uses GENCODE vM37 and keeps
the parent's `CATALOG_ID`. Context capability is `transcript_geometry_v1`.

The mask unions every exon on both strands, merging overlapping or touching intervals.
The policy `all_exons_unstranded_union_v1` retains every positive-length block
(`min_retained_block_bp = 1`). GTF contigs normalize through the copied `chrom_gencode`
alias column, including scaffolds; every annotation contig must resolve.
`min_retained_block_bp = 1` preserves every positive-length block. The context policy pins
`start_envelope_upstream_bp = 10000`, `start_envelope_downstream_bp = 2000`,
`end_envelope_downstream_bp = 10000` and `tie_rule = keep all ties`.

Twelve SAFs occupy
`exports/{ucsc,ensembl,gencode}/{interspersed,compat_tetranscripts_mm39}/exon_subtracted/{subfamily,taxonomy_triple}.saf`.
Each has the header `GeneID`, `Chr`, `Start`, `End`, `Strand`, with one row per retained block
in 1-based inclusive coordinates and the source record's strand. `subfamily` uses `rmsk_name`;
`taxonomy_triple` uses `<rmsk_name>:<family_id>:<class_id>` with the parent's canonical labels
and positional unresolved tokens. Rows sort by contig bytes, numeric bounds, strand and GeneID.
Each interspersed SAF contains 3,684,934 data rows; each compat SAF contains 3,717,740.

`tables/export_feature_members.tsv.gz` uses the eight registration columns above. Each retained
block registers its parent record at `(subfamily, rmsk_name)` and
`(taxonomy_triple, taxonomy_triple)` in its universe and `exon_subtracted` variant. Uniqueness
includes both block bounds. Registration is shared across namespaces and holds 7,369,868
interspersed rows and 7,435,480 compat rows. `tables/exports.tsv` inventories all twelve files
with measured rows, distinct GeneIDs and SHA-256 digests.
Verification compares every SAF's rows and order with the registration joined to the parent
record's strand and contig in each namespace.
Registration row order is outside the contract; each SAF's sort order is part of it.

`tables/exon_subtraction_status.tsv` contains `rmsk_record_id`, `status`, `n_blocks`,
`retained_bp` and `removed_bp` for every parent catalog record. `unchanged` means zero removed
bases; `trimmed` means one shorter block; `split` means several retained blocks;
`fully_subtracted` means zero blocks. Fully subtracted records retain their status rows.
`exon_subtraction_status` describes counting-support geometry.
`unchanged` covers intronic and intergenic records alike.

Every record conserves `retained_bp + removed_bp = length_bp`. Retained blocks are disjoint,
ordered, contained in their record and exon-disjoint under the declared mask. Molecule
exclusivity between gene and TE counts is a property of the joint counting run.

`tables/exon_subtraction_summary.tsv` contains `universe_name`, `records`, `unchanged`,
`trimmed`, `split`, `fully_subtracted`, `retained_records`, `blocks`, `retained_bp`, `removed_bp`
and `records_on_unannotated_contigs`, for `all_rmsk`, `interspersed` and
`compat_tetranscripts_mm39`. Base totals sum record support, preserving overlaps between records.

`tables/gene_annotation_coverage.tsv` contains `chrom_ucsc`, `gene_rows`, `transcript_rows`,
`exon_rows`, `exon_union_bp` and `annotated` for every parent contig, sorted by `chrom_ucsc`.
`annotated` means the retained GTF has at least one row on that contig. The vM37 annotation
covers 38 of 61 contigs; 2,638 catalog records lie on the 23 remaining contigs and retain their
full support. Coverage counts are 78,317 gene rows, 278,369 transcript rows and 1,298,921 exon
rows; the exon union spans 160,549,642 bp.

`universes.json` and `tables/contig_aliases.tsv` are exact parent copies whose SHA-256 digests
appear in `identity.copied_inputs`. The child retains the GTF and `source/SOURCES.json`, which
records assembly, parent family and IDs, the `gene_gtf` source role and policy bundle.
The transcript-context relation requires its chr1 and mm39 scaling checks for snapshot admission.

### Transcript context tables

`tables/record_transcript_context.tsv.gz` has one row per selected parent record × transcript pair.
`tables/record_context.tsv.gz` has one row per parent catalog record, across all universes.
Both join through `rmsk_record_id`; `export_feature_members.tsv.gz` binds exported features to records.
Rows follow parent record order, then transcript ID byte order within each record.
Booleans serialize as `true` and `false`; unavailable geometry serializes as `NA`.

Pair columns appear in this order:

| Columns | Meaning |
|---|---|
| `rmsk_record_id`, `transcript_id`, `gene_id` | Record key and versioned annotation IDs |
| `gene_type`, `transcript_type` | Annotation biotypes |
| `ensembl_canonical`, `mrna_start_nf` | Transcript tags `Ensembl_canonical` and `mRNA_start_NF` |
| `strand_relation` | `same` or `opposite` relative to the record |
| `pair_status` | Semicolon-joined reasons in order: `body`, `nearest_start`, `nearest_end`, `nearest_exon_edge`, `start_envelope`, `end_envelope` |
| `exon_bp`, `intron_bp`, `utr5_bp`, `utr3_bp` | Bases in transcript exon union, body outside exons, 5′ UTR and 3′ UTR |
| `body_bp`, `gene_body_bp` | Bases in transcript body and gene span |
| `dist_start`, `dist_end` | Signed closest-base distance to oriented transcript endpoints |
| `dist_exon_edge` | Unsigned closest-base distance to transcript exons; exon overlap gives zero |
| `dist_gene_start`, `dist_gene_end` | Signed closest-base distance to oriented gene endpoints |

Endpoints are the first and last inclusive bases in transcription orientation. Distance is zero
when the record contains the endpoint, negative upstream and positive downstream; an adjacent
base has magnitude one. Nearest selections compare absolute distances and retain every tied
transcript. Every transcript with exon overlap ties at exon distance zero.
Envelopes include their endpoints: start positions span signed offsets −10000 through +2000;
end positions span 0 through +10000. Overlap with any envelope base selects the pair.
Exon and UTR overlaps use interval unions within each transcript. Generic GTF `UTR` rows before
and after the CDS bounds become oriented 5′ and 3′ UTRs; explicit `five_prime_utr` and
`three_prime_utr` rows carry their annotated orientation. Transcripts without those UTRs have
zero UTR overlap. Gene and transcript rows define their respective body spans.

Roll-up columns appear in this order:

| Columns | Meaning |
|---|---|
| `rmsk_record_id`, `length_bp` | Parent record key and inclusive length |
| `annotated` | Contig has annotation rows, matching `gene_annotation_coverage.tsv` |
| `exon_bp_any` | Bases in the unstranded exon union; equals mask `removed_bp` on annotated contigs |
| `body_frac_max` | Maximum overlap with one gene span divided by record length; zero for no overlap |
| `body_genes_same`, `body_genes_opposite` | Distinct overlapping gene spans by strand relation |
| `nearest_exon_edge_bp` | Unsigned distance to any transcript exon; exon overlap gives zero |
| `nearest_gene_end_bp`, `nearest_gene_end_strand` | Unsigned distance to the nearest gene entirely upstream of the record in gene orientation, and its strand relation |
| `nearest_gene_start_bp`, `nearest_gene_start_strand` | Unsigned distance to the nearest gene entirely downstream of the record in gene orientation, and its strand relation |

Outside-gene endpoint queries use all gene spans on the contig. Tied strand relations serialize
as `same;opposite`, with each relation present once. An absent eligible endpoint gives `NA` for
both distance and strand. Unannotated contigs have `annotated = false` and `NA` in all nine
geometry columns. Consumer labels and distance thresholds are derived views over these tables.

### Acceptance and host runbook

`docs/RUNBOOK.md` supplies the host build, verification, publication, transfer and recovery
procedure. `tests/run.sh acceptance --build` builds both families into
`$TE_TRACKS_REFROOT/acceptance/`; `tests/run.sh acceptance` checks those archives again. Eleven
areas cover the source, records/universes, canonical taxonomy, Dfam, exports, record gene profile,
namespaces, publication, child census, independent bedtools geometry and packaged-GTF reconciliation.
[Acceptance anchors](../tests/expectations/mm39/README.md) name the authoring evidence for every census.
