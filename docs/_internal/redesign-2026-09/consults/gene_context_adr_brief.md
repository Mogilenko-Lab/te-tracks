# Gene context: ADR discussion brief for the owner (2026-09-16)

Prepared by the orchestrator from `gene_context_material.md` (evidence pack, verified in its section 8)
and `gene_child_consult.md` (codex design consult, measurements reproduced there). Nothing here is
adopted; candidate decisions land in `docs/DECISIONS.md` only by the owner's ruling
(`02_orchestration.md`). Each candidate states the decision, what it prevents, and what only the owner
can settle.

## Measured facts the decisions rest on

| fact | value | source |
|---|---|---|
| GENCODE vM37 exon union, all transcript types | 160,549,642 bp | dossier §4, consult Q3 |
| `basic` / `Ensembl_canonical` / protein-coding exon unions | 132,600,517 / 112,655,476 / 75,875,592 bp | dossier §4 |
| gene-body union / transcript-body union | 1,488,096,243 / 1,486,451,442 bp | consult Q6 |
| records overlapping a gene body and no transcript body | 2,073 | consult Q6 |
| bulk 10 kb / 20 kb flags that change when transcript spans replace gene bodies | 500 / 98 | consult Q6 |
| compat universe under the all-exon mask | 3,799,629 records → 3,701,642 retained records, 3,717,740 blocks; 97,987 fully removed; 26,503,064 bp removed | consult Q4, independent bedtools agreement |
| interspersed universe under the same mask | 3,764,949 → 3,668,830 retained records, 3,684,934 blocks; 96,119 fully removed | consult Q8 |
| blocks shorter than 20 bp among retained compat blocks | 56,863 | consult Q3 |
| record-bearing contigs without gene annotation | 23 contigs, 2,638 records | consult Q5 |
| exact record × transcript body-overlap pairs | 14,021,883 | consult Q5 |
| sparse context pairs, estimated, promoter (U,D) = (0,0) / (2000,200) / (10000,2000) | 21.8 M / 22.5 M / 26.8 M | consult Q5 |
| scTE exclusive mask with current GENCODE | protein-coding exons only, whole-locus removal; the `lincRNA` string no longer matches | scTE source (`scTE_build:83,194-200`) |

The lab's counting recipe subtracts every exon row with `bedtools subtract` and counts genes over
every exon row (`build_te_saf.sh:96-97,115`; `runFeatureCounts_TE_and_genes.sh:170-178`). Two gene
models are live among the TE tools: exon-only (TEtranscripts, TElocal, featureCounts gene pass) and
whole-span (TEsingle, MATES gene bodies, scTE `nointron`).

## Candidate decisions

**C1. One gene family, immutable snapshots.** `te_mm39_gene` publishes snapshots that each pin one
exact parent core archive (`parent_build_id`, `parent_catalog_id`), one gene annotation digest and one
versioned policy bundle (mask, minimum block, context capability, later the geometry parameters).
The exon-subtracted SAF and the transcript-context relation are products inside that scope with
explicit capability states; `CATALOG_ID` is the parent's. A GENCODE or policy change mints another
snapshot and leaves the core and every ATAC key untouched. Prevents a SAF and a context table built
from different annotations being joined as one reference.
*Owner settles:* whether the compat SAF pair (legacy membership) is a published view of the family.

**C2. The default mask is every exon row, both strands; all positive-length blocks retained.**
Named `all_exons_unstranded_union_v1`, with `min_retained_block_bp = 1` recorded. Narrower masks
(`basic`, canonical, protein-coding) and size filters are separately named policies that need a
consumer. Acceptance pins 3,717,740 blocks from 3,701,642 records under compat, zero residual overlap,
per-record base conservation. Prevents unmasked counted-exon support (85 Mb under a protein-coding
mask) and the piece-versus-record confusion in the old anchor. The guarantee is exon-disjoint support;
molecule exclusivity remains a property of the joint counting run.
*Owner settles:* whether any narrower mask ships in phase 8 (recommendation: none).

**C3. Context is a sparse record × transcript relation plus a complete per-record status; subtraction
status stays a separate table.** Status vocabulary `evaluated`, `contig_outside_annotation`,
`unsupported_structure`, `not_computed`. Any scalar `gene_context` is a named, versioned derivation
that keeps isoform disagreement visible. Prevents `unchanged` or an uncomputed record reading as
intergenic, the H3 failure, and prevents a convenience scalar from erasing its evidence.
*Owner settles:* phase 8 ships the SAF with context declared `not_computed`, and context arrives in a
later snapshot after a scaling gate on chr1 then mm39 (estimated 1.6 to 5.4 GB of pairs). Or phase 8
expands to context now, an approved scope expansion.

**C4. Geometry: transcript-oriented, genomic, signed; plus gene-body geometry.** TSS and TES per
transcript, distance zero when the record covers the landmark, negative upstream, positive
downstream, closest-base rule; relative strand `same | opposite | unknown`; all isoforms with ties;
promoter bases stored as coordinates under `(U, D, promoter_policy_id)`; `Ensembl_canonical` as a flag
(`MANE_Select` is absent in vM37). Gene-body distance is kept beside transcript distance because the
bulk rules ask "distance from any gene" and the two differ for 2,073 records. Prevents a 3' assay's
signal at the TES being read against TSS distances, a promoter width baked into a column, and
transcript-union gaps being read as outside genes.
*Owner settles:* the promoter window `(U, D)` for the first snapshot; whether spliced distance is ever
wanted.

**C5. te-tracks publishes pinned reference geometry; consumers publish versioned labels with their
own counting-annotation pins.** Replaces the dossier's G5. A digest mismatch between the child's GTF
and a consumer's counting GTF triggers documented geometry reconciliation (exon support, spans and
identifiers compared after normalization) or another annotation-pinned child. Bulk adjacency
windows (10 kb, 20 kb, with an explicit intermediate band) derive from gene-body distance as a
consumer policy. A te-tracks convenience view (`mixed_exon_intron`, `exon_overlap`, `intron_only`,
`gene_body_gap`, `intergenic`, in that precedence) is an alternative once a named consumer agrees its
semantics. Prevents a reference-relative label being presented as the counting annotation's context.
*Owner settles:* A (consumers derive) or B (te-tracks ships the convenience view too); label scope
full record versus retained piece; the D2 column change from `te_release` to `te_catalog_id` plus
`te_build_id`.

**C6. The child carries an exact copy of the parent's alias and length table, verified by digest,
and its own annotation coverage table.** GTF contigs are normalized through the declared alias
columns, including the 16 GenBank scaffolds; an unmapped contig fails the build. Prevents the silent
scaffold miss prefix stripping yields, and keeps preflight local to the child.
*Owner settles:* nothing beyond confirmation.

## Architecture points already ruled by the reviews, for information

- Family and assembly stay separate identities (`FAMILY=te_mm39_gene`, `GENOME=mm39`); `SPECIES`
  admits assemblies.
- The child names its parent by full `BUILD_ID` under a root or by an explicit verified directory;
  `current` is resolved once and checked against the requested id.
- The child's verifier resolves the parent's immutable archive, recomputes both ids, checks family,
  assembly and catalog equality, and validates child registration against parent records; install,
  select and verify-current require the dependency present.
- The child exporter takes universe, variant and block bounds as explicit inputs and writes its own
  `tables/exports.tsv`, registration and inventory; registration keys carry `block_start_1` and
  `block_end_1`.

## Facts still unverified

The GTF inside the 10x references: the two whole-cell datasets were aligned against
`refdata-cellranger-GRCm39-2024-A` and the Multiome against `refdata-cellranger-arc-GRCm39-2024-A` (BAM headers
and web summaries, 2026-09-16); 10x documents both as GENCODE vM32 filtered by biotype, and the reference
directories live on the sequencing core's machine, so the GTF bytes are unverified here. The nf-core "filtered"
gene GTF the cGAS gene pass used (its filter recipe) and the TE-Seq behaviour cited second-hand remain
unverified. The compat count is measured and no longer open.

## Additions from the field consult and the field reviews (2026-09-16, later the same day)

Sources: `field_practice_consult.md` (codex), `../reviews/field_bioinf.md`, `../reviews/field_divergent.md`,
ruled in `../reviews/field_rulings.md` and synthesized in `field_practice_synthesis.md`. Every number was
recomputed by the orchestrator (synthesis section 9).

### Dataset facts the decisions now rest on

| dataset | pipeline and chemistry | reference | BAM layout | multimappers in the BAM |
|---|---|---|---|---|
| 14616 spleen | cellranger 9.0.1, `Single Cell 5' PE OCM v3`, introns included | `refdata-cellranger-GRCm39-2024-A` | both cDNA mates aligned, proper pairs | one record per read; 14.8% carry `NH>1`, none secondary |
| 14782 lung | cellranger 10.0.0, same chemistry, introns included | same reference | same | same pattern |
| 14761 spleen GEX | cellranger-arc 2.1.0, Multiome v1, introns included | `refdata-cellranger-arc-GRCm39-2024-A` | single-end (R2) | one record per read; 3.8% `NH>1` |
| 14761 spleen ATAC | cellranger-arc 2.1.0 | same | paired fragments | |

Consequence: every EM route needs a re-alignment that emits all alternatives; the 10x references are five
GENCODE releases behind the child's vM37 pin, so C5's reconciliation applies to every consumer.

### Amendments to C1 to C6

- **C3.** Status becomes per record × transcript pair with a per-record roll-up (the four-state vocabulary
  otherwise conflates "no body overlap" with "annotation present, nothing in the window" and drops a host
  when one of six isoforms is unsupported). Phase 8 states in `README.md` and `docs/DECISIONS.md` that the
  exon-subtracted SAF is the bulk product and the single-cell context product is the deferred relation.
- **C4.** The relation carries `utr5` and `utr3` flags, bases and exact segments per pair with a
  coding-boundary status (vM37: 186,133 UTR rows, 95,682 5′ and 90,451 3′ by strand and CDS bounds; 10,247
  records touch a 5′ UTR and 46,588 a 3′ UTR). Host-gene promoter windows and TE-end windows stay separate
  relations.
- **C5.** The reconciliation target for all three datasets is the 10x 2024-A GTF (documented as vM32)
  against vM37; the D2 keys become `te_catalog_id` plus `te_build_id`, with intersection coordinates and a
  counting-run id (consult Q5).
- **C1, C2, C6** stand as written.

### New candidate decisions

**C7. The RNA route and grain for 14616 and 14782, and who qualifies it.** Neither dataset has a written
TE requirement. Recommendation: record-level estimation with multimappers retained, subfamily as the
reported rung, family and class as descriptive rollups; TEsingle as the first consumer to qualify, with
STARsolo GeneFull plus `soloMultiMappers EM` and a unique-only run as comparators, all on a STARsolo
re-alignment with `outFilterMultimapNmax 100`, `winAnchorMultimapNmax 100` or `150` and `outSAMmultNmax -1`.
Promotion criteria for TEsingle: paired-mate handling (its reader appends mates as alternative alignments
with opposite strands), UMI-collision behaviour (unconstrained Hamming-1 components) and hard-tie policy
(argmax, first index), accepted or corrected in a pinned fork. Reporting contract: animal-replicated,
tissue-paired claims from the whole-cell arm; descriptive, direction-corroborating use of the Multiome arm.
*Owner settles:* the route, the grain, the qualification owner, and the reporting contract.

**C8. A STARsolo locus-as-gene GTF profile, `record_starsolo.gtf`.** `gene_id = transcript_id = locus =`
record alias, `rmsk_name` and canonical taxonomy as attributes, its own export contract and a fixture in
which two records of one name become two genes. Prevents STARsolo GeneFull counting 1,220 subfamilies where
3,764,949 loci were meant; today's `record.gtf` has the dissertation's subfamily grammar and stays as
TEsingle's input. *Owner settles:* phase 9 by scope amendment, or the next core snapshot; until then a
pinned consumer rename with its digest recorded is acceptable.

**C9. The matrix binding rule names the universe and variant.** `docs/OUTPUTS.md` binds a run's matrix to
`(feature_level, key_grammar)`; the registration holds 3,764,949 `interspersed` and 5,320,771 `all_rmsk`
rows at `(record, rmsk_record_id)`, so a join on the documented pair doubles every interspersed count. The
rule becomes `(universe_name, variant, feature_level, key_grammar)` with a join fixture over both universes.
Phase 9 documentation and check. *Owner settles:* confirmation.

**C10. Rank vocabulary and Dfam admission scope.** A later core view with one row per name carrying the Dfam
lineage, accession and model version, a named rank scheme, per-rank status (mapped, missing, ambiguous,
inapplicable) and the raw and canonical RepeatMasker labels beside it; pinned to a Dfam release. Now: a
label-surprise note in `docs/OUTPUTS.md` (B1 under `Alu`, 558,808 records; `ERVL-MaLR`; hyphenated DNA
superfamilies; 5,893 class-less records) and `rmsk_overlap_flag` documented as constant false for the mm39
source. *Owner settles:* the rank scheme and whether admission covers all 18,484 names or the 1,220
interspersed names first.

**C11. Structural and end-window views, keyed on insertions.** Later snapshots publish an instance
block-union view (gaps preserved, mixed-name and mixed-strand status kept), strand-aware record-end windows
with consensus-prefix eligibility, divergence-bin universes with pinned thresholds, and LTR–internal
candidate pairs with strand, order and distance rules. Measured reasons: 445,649 multi-record instances;
17,947 LTR instances hold both an internal and an LTR name while 722,280 hold LTR names only; promoter-intact
L1 at the record is 588 loci (75 ≥ 6 kb) and at the insertion 583 to 2,221; row-implied consensus lengths
vary within 145 of 149 L1 names. *Owner settles:* ordering against phase 9 and the host build; nothing ships
before its evidence gate.
