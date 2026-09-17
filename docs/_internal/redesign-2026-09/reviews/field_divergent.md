# Field review: unstated assumptions (divergent)

Subject: te-tracks at `8589873` (`redesign-2026-09`), read against the owner's excerpts, the TEsingle and scTE notes, the
gene-context material, and the mm39 build at `_scratch/te-tracks-audit/refroot/te_mm39/build`. Measurements are read-only from
that build's tables, `source/mm39.fa.out.gz` and `A/*.tsv`; nothing was built, installed or written outside this file. Prefixes:
`T` = repository; `C`/`R`/`A` = its `consults`/`reviews`/`audit` siblings here; `D` = `14761-DM/.../2026-09-11_codebase-topology`.

## High

- [H1] **A run's matrix binds to `(feature_level, key_grammar)`, so counts join the registration on that pair**
  (`T/docs/OUTPUTS.md:436-437`). Measured: `L1MdA_VI|chr1:3050294-3050775|+` holds two rows at `(record, rmsk_record_id)`,
  one `interspersed` and one `all_rmsk`, identical in `emitted_feature_id`, `rmsk_record_id` and both block bounds. Failure:
  a record-level matrix joined on the documented pair fans out 2× for all 3,764,949 interspersed records and any sum doubles
  every count; uniqueness needs `universe_name` (`:414-415`), which the ATAC row carries (`:482`) and the IRescue row omits
  (`:474`). It fails the owner's own test, "Joins must not create signal" (`C/owner_context_2026-09-15.md:42`). Cost high.
  Lands: phase 4 binding rule, with a phase 9 join fixture.
- [H2] **`record.gtf` is the dissertation's locus annotation, so record-level counting reads it** (`T/docs/OUTPUTS.md:280`).
  Measured, export line 1: `gene_id "L1MdA_VI"`, locus in `transcript_id`. Failure: STARsolo GeneFull counts per `gene_id`,
  so a combined index over `record.gtf` yields 1,220 subfamily columns where the consumer expects 3,764,949 loci, silently.
  The dissertation moved the locus into `gene_id` for this reason (`C/thesis_2023_excerpts.md:141-145`);
  `C/tesingle_notes.md:39-41` names the mechanism and declines the export; the reference index route is a combined
  gene-and-TE GTF (`:138-140`); `STARsolo` and `cellranger` appear in no `docs/*.md`, `README.md`, `src/`, `tests/` or
  `config/` file (grep). Cost high. Lands: phase 4/5 — a `gene_id = locus` GTF and a STARsolo fixture, or a stated scope.
- [H3] **A locus is a RepeatMasker record.** Measured: 5,320,771 records over 4,696,900 instances; 445,649 instances hold 2
  to 22 fragments (1,069,520 records); 429,440 records (8.07%) overlap another record across 237,686 pairs and 9,190,866 bp,
  198,956 of those pairs crossing instances, so `rmsk_instance_members` deduplicates at most 16%. Interspersed median length
  is 160 bp, and 17.6% of records are shorter than one 90 bp read. Failure: the ATAC ledger over `all_rmsk/full/record.bed`
  (`:521`) sums overlapping intervals, and `rmsk_overlap_flag` (`:37`) is `false` for all 5,320,771 records because the
  pinned `.out` carries zero trailing `*` markers (measured) — filtering on it removes nothing and reads as overlap handled.
  Cost high. Lands: 14761 peak ledger (a record-overlap relation); phase 2 records the constant flag.
- [H4] **The ERV unit follows from the instance id plus consensus coordinates** (`T/docs/DECISIONS.md:91-92`). Measured over
  843,753 LTR-class instances: 17,947 hold both an `-int` and a non-int LTR; 103,526 are `-int`-only; 722,280 are LTR-only,
  583,277 of them single-record. Failure: "an LTR whose instance holds no internal" calls 722,280 solo LTRs for mm39, while
  the 103,526 internal-only instances show that real proviruses' flanking LTRs carry other instance ids — one rule both
  over-calls solo LTRs and loses the proviruses. Stellarscope's published reference is a curated HERV and full-length L1 set
  (`C/DECISION_STATE.md:25`), the unit the field counts ERVs at. Cost high. Lands: the structural stage.
- [H5] **Promoter-intact filtering is computable from the shipped consensus columns** (`C/thesis_2023_excerpts.md:288-296`;
  `T/docs/OUTPUTS.md:33-35`). Measured: 588 of 877,139 LINE/L1 records carry `consensus_start_1 = 1` (0.067%), 75 of them
  spanning ≥6 kb; reconstructed per instance, 583 at `= 1` and 2,221 at `<= 10`, of which 104 and 323 reach ≥6 kb. Failure: a
  promoter-intact L1 universe built per record keeps ~75 loci where the insertion-level answer is 300 to 2,200, discarding
  nearly every young L1 the programme means to measure, with the re-mapping risk at `:303-305` unmitigated. No fixture catches
  it: every consumer-fixture record is written `consensus_start_1=1, consensus_end_1=length, consensus_left_bp=0`
  (`T/tests/lib/consumers.py:338`). Cost high. Lands: the structural stage, keyed on insertions.
- [H6] **The exon-subtracted SAF answers the single-cell context question.** Phase 8 ships three SAFs and a status table
  (`T/README.md:113-117`); featureCounts is a bulk counter and the GTF and context products are deferred
  (`T/docs/OUTPUTS.md:588-589`). Failure: subtraction removes 26,503,064 bp, 2.363% of TE support, while 54.59% of retained
  intervals lie inside a gene body (`C/gene_context_material.md:110-114`) — the only gene-dependent product on the roadmap
  leaves the measured failure untouched, near-zero accuracy on gene-overlapping TEs for every method including EM
  (`C/thesis_2023_excerpts.md:217-221`). Cost high. Lands: phase 8 — a single-cell product, or the bulk-only scope stated.
- [H7] **The datasets these counting decisions serve have written requirements.** Measured: grep over `14616-DM/docs` and
  `14782-DM/docs` for `transposable|repeatmasker|te-tracks|te_locus` returns zero files; the only written TE contract is
  14761's (`D/01_consult_codex.md:166`), the pooled multiome with one library per condition and no replicates
  (`C/thesis_2023_excerpts.md:14`). Failure: every rung, grammar and counting choice is specified for the two datasets that
  carry true replicates and per-mouse spleen–lung pairing and have no named consumer, so the first real run discovers its
  grain requirement after parking. Cost high. Lands: an owner step before phase 8 — name the 14616/14782 route and grain.

## Medium

- [M1] **RepeatMasker class/family/name is the hierarchy consumers want.** The brief carries five ranks
  (`C/thesis_2023_excerpts.md:18-30`) and the pinned Dfam rows a seven-token lineage (`root;…;Transposase;hAT;Tip100`,
  `T/tests/fixtures/taxonomy/dfam_snapshot.tsv`); te-tracks publishes three, with `LTR`/`LINE`/`SINE` in the class slot — the
  brief's subclass and superfamily. Failure: Class I versus Class II, the brief's top rung, is no rollup from
  `taxonomy_canonical`; a consumer hand-maps it, and the 5,884 Unknown, Unspecified and `DNA?` records carry no Class. Cost
  medium. Lands: phase 3 — a rank column, or a statement that class means the source token.
- [M2] **Subfamily is the right default aggregate.** A subfamily is the records sharing one `repName`
  (`T/docs/DECISIONS.md:5`), so its record count aggregates fragments: LTR holds 1,105,064 records over 843,753 instances
  (31% inflation), and an ERV's LTR and `-int` are separate names, splitting one transcription unit in two. Failure: the
  aggregate weights each insertion by how many pieces RepeatMasker cut it into, the artifact `R/p3_divergent.md:8-17` found
  in the taxonomy vote. Cost medium. Lands: phase 4 — instance counts beside record counts where the aggregate is emitted.
- [M3] **The taxonomy triple is a stable key across releases.** Measured against the packaged TEtranscripts GRCm39 GTF:
  `ID4_.` versus `ID4_v` over 25,263 records, `LTR33A_.`/`LTR33A_v` 432, `MER34C_.`/`MER34C_v` 328, `RTE-Bo.B`/`RTE-BovB`
  4,239, plus 58 families the packaged file names where rmsk says `Unknown` (`A/alias_subfamily.tsv`, `A/alias_family.tsv`;
  `C/SYNTHESIS.md:128-134`). `taxonomy_triple.saf` keys on all three fields (`T/docs/OUTPUTS.md:394`). Failure: a matrix counted
  on the packaged spellings fails to join for 25,263 loci, presenting as new features with no history. Cost medium. Lands:
  phase 9 reconciliation and the ledger's `te_feature_registration`.
- [M4] **The sparse transcript relation is consumable at 22 to 27 million pairs.** The sizing is a producer estimate
  (`C/gene_child_consult.md:51`); the one consumer with a written requirement asked for a scalar (`D/01_consult_codex.md:166`).
  Failure: the relation's first act is a precedence collapse over ~6 transcripts per record that no named consumer has
  specified, so delivery needs a second unbudgeted design step before anyone reads it. Cost medium. Lands: the context
  session — fix the consumer and its precedence before sizing.
- [M5] **The four-state context status is enough.** Status is per record; geometry is per (record, transcript). Failure: a
  record evaluated against six isoforms, one with unsupported structure, reads either `evaluated` (a host dropped silently)
  or `unsupported_structure` (five good pairs discarded), and `evaluated` covers both "no body overlap" and "annotation
  present, nothing in the window" (`C/gene_child_consult.md:49`) — the distinction the intronic case turns on. Cost medium.
  Lands: the context session — per-pair status with a per-record roll-up.
- [M6] **One gene annotation describes the three datasets.** The child pins GENCODE vM37, Ensembl 114
  (`C/gene_context_material.md:214-216`); 14616 ran cellranger 9.0.1, 14782 cellranger 10.0.0, 14761 cellranger-arc 2.1.0
  (`C/thesis_2023_excerpts.md:12-14`), and the refcache holds vM37 alone, so none is inspectable here. Failure: the same 20
  animals' spleen and lung were counted under two different gene references, so the matched-pair TE comparison crosses two
  annotations before te-tracks enters; the record flags only the arc GTF (`C/gene_context_adr_brief.md:104-105`). Cost
  medium. Lands: the consuming datasets, under C5's reconciliation rule.
- [M7] **The fixtures test 3' ARC and 5' PE OCM layouts separately** (`C/owner_context_2026-09-15.md:58`). Measured:
  `arc_3prime.bam` and `ocm_5prime_pe.bam` come from the identical molecule list and differ only in `paired`
  (`T/tests/lib/consumers.py:383-394`). Failure: nothing encodes position within a transcript, so a wrong 5'-proximal
  convention passes every check; the promoter-proximal argument for 5' capture (`C/thesis_2023_excerpts.md:318-325`) needs
  the transcript's first base inside the TE — ~75 L1 records by H5 — and has no test. Cost medium. Lands: phase 5 fixtures
  and the 14616/14782 plan.
- [M8] **The pooled multiome supports a condition contrast.** One ARC library per condition, three mice pooled inside, makes
  condition and library one factor (`C/thesis_2023_excerpts.md:14`). Failure: every locus-level accessibility difference is a
  single-library difference, so the ledger's `accessibility` facts joined through the TE interval table report effects no
  design separates from batch. Cost medium here, high for a published claim. Lands: the 14761 analysis design.
- [M9] **The Dfam evidence is pinned to a Dfam release.** `T/tests/fixtures/taxonomy/dfam_snapshot.provenance.json` carries
  per-family `dfam_version` and `release_endpoint_response: null`, "unrecorded at the 2026-09-16 fetch". Failure: the
  agreement test's baseline is a mutable API response with no release identity, so a reclassification and a fetch-date
  difference are indistinguishable at refresh; Dfam is read as a label check, never as M1's rank table. Cost medium. Lands:
  phase 3, at the next refresh.
- [M10] **A 2023 dissertation is the field reference.** Its benchmark is human GRCh38 on simulated data, its top pick
  (Alevin-Fry, `C/thesis_2023_excerpts.md:234-237`) is superseded by its own author's 2026 tool
  (`C/tesingle_notes.md:97-100`), and it sets 5' capture aside on 10x v2 experience (`:322-325`) — the chemistry of two of
  three datasets. Failure: the programme inherits an ideal whose two concrete recommendations the record reconciles with
  neither the preprint nor the data in hand. Cost medium. Lands: the consults — one dated note on what still holds.

## Low

- [L1] **Sparsity rounding is the consumer's problem.** Half-to-even rounding moved TE accuracy by up to 20 points in the
  dissertation's benchmark (`C/thesis_2023_excerpts.md:261-266`) and sits outside TEsingle (`C/tesingle_notes.md:36`).
  Failure: two projects round one release's fractional EM counts differently and publish different call sets under the same
  `te_catalog_id`, with no field recording which ran. Cost low here, medium for the claim. Lands: the ledger's `analysis_runs`.
- [L2] **Young versus old follows from divergence.** Measured within-name spread swamps the tier: B1_Mus1 median 8.9
  (p05–p95 4.1 to 21.8), B1_Mus2 7.5 (3.2 to 22.0), B3 23.1 (15.7 to 31.5); 468,810 records read exactly 0.0. Failure: a
  per-name median (`T/docs/DECISIONS.md:88-90`) gives one age to a distribution overlapping three other names, and 0.0 is an
  alignment statistic read as an age. Cost low now, high once published as age. Lands: the structural stage.
- [L3] **Multi-annotating gene–TE reads are addressable by annotation.** Every method including EM scores near zero on
  intronic TEs (`C/thesis_2023_excerpts.md:217-221`); TEsingle's answer is a per-cell `te_frac` prior
  (`C/tesingle_notes.md:28-31`). Failure: carving exons or labelling context changes which features compete while the read
  stays ambiguous, so a consumer can report an intronic TE as expressed on evidence that does not separate it from host
  pre-mRNA. Cost low here, high for interpretation. Lands: the consuming analysis, as a claim tier.
- [L4] **The reviewers' subject is a published build.** `pubroot/te_mm39/` holds no `archive/` and no `current`, only an
  abandoned group-unreadable `.staging/build.NFU5wpRH`, so the `published_identity_equal` assertion
  (`C/gene_child_consult.md:114-115`) reads a path that no longer exists. The scratch build itself is sound: I recomputed both
  ids from `MANIFEST.json` and checked all 43 inventory entries for presence, size and (under 3 MB) digest, with no extras.
  Cost low. Lands: phase 9 — publish once and cite the archive.
- [L5] **Consult files are the record.** They cite mutable paths (the refcache GTF, `.ref` checkouts named by HEAD) and
  second-hand quotes (`C/gene_context_material.md:327-334`), so a decision can rest on a line no tracked file holds. Cost
  low; raised at `R/m2_divergent.md:120`, `R/m5_divergent.md:134`, `R/m7_divergent.md:122`.

## Defended already

- The instance id as the fragment grouping, and the rule against summing a traversal — `T/docs/OUTPUTS.md:436-441`,
  `C/owner_context_2026-09-15.md:39-42`, `T/tests/checks/core/21_instances.py`.
- Intronic TE reads in nuclei stay undeclared: exon, intronic, intergenic and strand context plus a sensitivity analysis
  "without declaring every excluded intronic locus biologically silent" — `D/01_consult_codex.md:229`; nesting named at `:233`.
- `gene_context` waits for the context session and populates nothing from the subtraction status — `R/m2_rulings.md:95-97`,
  `R/m5_divergent.md:140`.
- Molecule exclusivity replaced by exon-disjoint sequence support — `T/docs/DECISIONS.md:41-42`, `T/README.md:142-143`.
- The Dfam oracle's one-class width, all 20 snapshot rows class DNA — `R/p3_divergent.md:28-35`,
  `T/docs/_internal/redesign-2026-09/taxonomy/README.md:3-4`.
- EM as the RNA route with no ATAC EM to start: IRescue, Stellarscope and TEsingle each fit one —
  `C/owner_context_2026-09-15.md:21-28`.
- The tRNA family-prefix exclusion as legacy-only, its three SINE families named — `C/SYNTHESIS.md:121-126`; one artifact
  under every review pass — `R/m5_divergent.md:128-133`.

Predicted first bite: H1 — the duplicate `(record, rmsk_record_id)` registration is on disk today, the binding rule that
misses it is published, and the owner already wrote the unit test it fails.
