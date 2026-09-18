# Decisions

## 1. Feature identity and taxonomy

A subfamily is the set of records carrying one RepeatMasker `repName` within a pinned build.
The canonical tables publish four feature levels—record, instance, subfamily and canonical
family—and every quantification records its assigned and reported levels.
Each record keeps its exact source class and family; `taxonomy_canonical` supplies one row per
name through a versioned deterministic rule with rank-specific statuses, checked against a pinned
Dfam snapshot in the test suite.
Family and class rollups read only that table.

## 2. Universes

A universe is a named predicate over raw source classification selecting records from the complete
catalog, defined in `universes.json`.
The build defines `all_rmsk`, `interspersed` as the default, `interspersed_plus_satellites`,
`retrotransposon_derived`, `satellites` and `compat_tetranscripts_mm39`.
`interspersed` keeps the tRNA-ancestry SINE families and carries Unknown, Unspecified and `DNA?`
records as flagged provisional members.
The observed class set matches the reviewed disposition file (`config/<genome>.classes.tsv`) before any biological universe publishes.

## 3. Delivered scope

The parked mm39 release contains the canonical tables, instance membership, raw and canonical
taxonomy, universe definitions, and the `interspersed` full-interval exports: BED at record,
subfamily and family level, GTF at record and subfamily level, SAF at subfamily level and at the
legacy taxonomy-triple grouping, plus the complete-catalog record BED under `all_rmsk`, each in
the `ucsc`, `ensembl` and `gencode` contig namespaces with an alias table and a coverage report.
Every export ships with a known-answer consumer fixture, a local test runner, a preflight command,
a host-build runbook and `AGENTS.md`.
Additional adapters enter a release together with a named consumer and a passing fixture.

## 4. Gene annotation snapshots

`te_<assembly>_gene` publishes immutable snapshots pinning one parent core by full `BUILD_ID`,
one gene annotation by digest and one versioned policy bundle (mask, minimum retained block,
context capability and later context envelope), with the parent's `CATALOG_ID`.
Consumers match the snapshot's annotation digest to their counting annotation: the first snapshot
pins GENCODE vM37 and the second pins the 10x 2024-A annotation (GENCODE vM33 filtered) used for
the current single-cell counts; a mismatch requires documented geometry reconciliation or another
snapshot.
Each child carries an exact, digest-verified copy of the parent's contig alias and length table,
normalizes annotation contigs through it and fails on an unmapped contig; the
`compat_tetranscripts_mm39` exon-subtracted SAF pair stays a published family view for legacy
reproduction.
Peaks, motif databases and TF inference are the ATAC framework's own pinned inputs; motif content
on TE consensus sequences belongs to another child family.

## 5. Namespace

Source-derived tables carry the `rmsk_` qualifier: `rmsk_records`, `rmsk_instance_members` and
`rmsk_taxonomy`.
Derived artifacts carry plain names: `taxonomy_canonical`, `export_feature_members` and
`universes.json`.
Coordinate columns state their convention as `start_1` and `end_1`; exports follow
`exports/<contig_namespace>/<universe>/<interval_variant>/<level>[_<profile>].<format>`, with
`full` and `exon_subtracted` as variants.
Consuming projects keep their quantification ledger in their own tables,
`peak_record_overlaps` and `te_feature_registration`, keyed to `rmsk_records`, with
`feature_level` as the measurement grain column.

## 6. Source

The primary source is the checksum-pinned RepeatMasker `.out` for the assembly, parsed under a
declared format profile that keeps raw strand, raw class/family token, consensus coordinates and
the overlap flag.
The manifest records the assembly, contig set and declared RepeatMasker software and library
identity with their evidence.
The UCSC browser table is compared once at source qualification and the report is retained.

## 7. Build identity and publication

`BUILD_ID` hashes the complete manifest identity, while `CATALOG_ID` binds the record-producing
RepeatMasker source, run identity, source-wide instance scope and decompressed canonical text
tables for the ledger key `(te_catalog_id, rmsk_record_id)`, so a serializer or compressor change
moves `BUILD_ID` alone.
Builder commit and validation evidence live in the `provenance` section outside both hashes.
A build verifies in staging, installs once into `archive/<BUILD_ID>/`, becomes selected by atomic
replacement of `current`, and stays on disk with consumer pins to its full ID and file digests.
The verifier judges an archive against its own declaration and the published versions so earlier
archives stay verifiable and selectable.

## 8. Exon mask policy

The default mask, `all_exons_unstranded_union_v1`, subtracts the unstranded union of every exon
row in the pinned annotation and retains every positive-length block (`min_retained_block_bp = 1`),
registered to its record, because an all-exon gene pass counts every exon row and the guarantee
is exon-disjoint sequence support.
The same-strand companion, `all_exons_stranded_union_v1`, joins in a later snapshot after a
chemistry pilot establishes which mate is RNA-sense; protein-coding and basic masks stay measured
alternatives admitted with a named consumer.
EM routes use unmasked record exports with the full gene annotation; molecule exclusivity belongs
to the joint counting run.

## 9. Transcript context is geometry

te-tracks publishes a sparse record-by-transcript geometry relation with per-pair status and a
per-record roll-up, carrying exon, intron and UTR overlap, relative strand, and signed closest-base
distance to each transcript's start and end, with gene-body distance beside transcript distance
so consumers can derive their own labels.
Rows cover body overlaps, the nearest start, end and exon edge on the record's contig with ties
kept, and records overlapping a window from 10 kb upstream to 2 kb downstream of an annotated
transcript start; narrower promoter policies are consumer filters on the stored distance.
Each transcript carries `Ensembl_canonical` and `mRNA_start_NF` flags so consumers can exclude
incomplete starts.
The first child snapshot declares context `not_computed`; the relation follows in a later
snapshot after passing the chr1 then mm39 scaling gate, and consuming ledgers key on
`te_catalog_id` and `te_build_id`.

## 10. Records, instances and insertions

A record is one RepeatMasker alignment of a genome stretch to a consensus model, the unit
underlying every export and every per-locus count.
An instance id is RepeatMasker's grouping hypothesis for records descended from one element,
carried on every record and registered as its own feature level; it is a starting group whose
errors can split one insertion or combine distinct insertions.
Insertion-level units, including full-length copies, proviruses and solo LTRs, are reconstructions
with declared parameters and evidence, published later as candidate views.
Documentation states the annotation's limits so consumers can interpret these units: records align
to a pinned library, fragmentation and nesting split elements, consensus coordinates are
model-relative, records overlap one another, and genic context depends on the annotation pin.

## 11. Structural candidate views

Later core snapshots publish geometry computed solely from catalog columns under declared parameters:
the block union of an instance's records with gaps preserved, record 5′ windows with model-prefix
eligibility, LTR–internal candidate pairs by family, strand and gap with per-pair status, and
divergence bins with pinned thresholds.
Views carry neutral names, support and candidate status, and enter after the host build, batched
into a later core snapshot when a consumer names the need.
Biological verdicts such as promoter-intact, solo LTR and young belong to consuming analyses
because they require interpretation of the candidate evidence.

## 12. Consumer boundary and qualification

te-tracks ships registered intervals and identities and qualifies consumer tools at two levels:
parser checks run each tool's own reading code on exports, and execution checks run its pinned
binary on a fixture.
Execution checks assert identity joins, roster and molecule conservation, and unique molecules
landing on their feature; each tool's allocation of ambiguous molecules is recorded as observed
behaviour outside these assertions.
Alignment parameters, estimator choice, forks and allocation behaviour belong to the consuming
toolkit, so te-tracks documents its observed qualification limits.
Execution checks use a pinned, reproducible tool environment recorded with the repository and
report `unsupported` when a binary is absent.

## 13. STARsolo record profile

`record_starsolo.gtf` makes each record one gene and one single-exon transcript, with `gene_id`,
`transcript_id` and `locus` equal to the record alias, `gene_name` the RepeatMasker name,
`gene_type` `transposable_element`, and provenance attributes kept, so gene-level counters count
loci.
The existing `record.gtf` keeps the subfamily grammar consumed by TEsingle and TElocal.
The profile reuses record alias membership in registration and enters with its contract and
fixture; an instance-level profile awaits mixed-name, mixed-strand, gap and junction tests.

## 14. Matrix binding

A run's matrix binds to a registration through the full key
`(universe_name, variant, feature_level, key_grammar)` because registration holds each record
under multiple universes and joining on level and grammar alone doubles counts.
A join fixture over `interspersed` and `all_rmsk` proves the rule.

## 15. Rank vocabulary and Dfam

Raw and canonical RepeatMasker labels stay as they are; the phase 9 core view stores Dfam lineage,
accession, model version, model length, clade and release as truth, admitting `interspersed`
names first.
It derives a named rank scheme with per-rank status (`mapped`, `inherited`, `missing`,
`inapplicable`, `part_model_set`), with `wicker_code_uncertain` recording code uncertainty,
and maps L1 and L2/CR1 whole-element names to sets of Dfam part models.
The rank vocabulary is `rank_scheme_wicker_v1`, with Wicker's ranks and the dissertation's
five names kept as a documented alias table so both vocabularies read onto the same rows.
Documentation explains label surprises consumers need to interpret: B1 under `Alu`, `ERVL-MaLR`,
hyphenated DNA superfamilies and class-less records.
The normalized companions are `taxonomy_dfam_models`, `dfam_lineage_nodes` and
`dfam_model_clades`, beside the per-name `taxonomy_dfam` view.

## 16. Wording

Each decision states the chosen behaviour and its reason in two to four brief affirmative
sentences.
Contracts and test evidence live in [OUTPUTS.md](OUTPUTS.md), [RELEASES.md](RELEASES.md) and
[PROVENANCE.md](PROVENANCE.md).
Deferred work names the evidence its next decision needs.

## Recorded deferrals

- Young versus old tiers: Dfam clade assignment beside per-record divergence and per-subfamily
  median divergence supplies age-tier evidence; full-length and ORF status need structural evidence.
- ERV units: the LTR–internal candidate view, instance relation and consensus coordinates precede
  reconstruction; validated LTR–internal membership defines the unit.
- hg38: source pins and packaged-file reconciliation follow parking, using the shared schema,
  class-census gate and config shape.
- Transcript context: section 9 defines the relation and its chr1 then mm39 scaling gate.
- Stranded mask companion: the chemistry pilot establishes which mate is RNA-sense before
  `all_exons_stranded_union_v1` joins the default mask.
- TES-side window: evidence of need from the 3′ pilot admits a later context envelope.
- Instance-level STARsolo profile: mixed-name, mixed-strand, gap and junction tests qualify its
  feature grammar.
- Consumer environment: phase 9 promotes the pinned, reproducible environment into the package
  with its source manifest and execution evidence.
- Cross-build record correspondence on `(chrom, start_1, end_1, strand)` awaits an explicit mapping rule.
- hg38 admission requires source-wide instance numbering or a contig-scoped instance key.
