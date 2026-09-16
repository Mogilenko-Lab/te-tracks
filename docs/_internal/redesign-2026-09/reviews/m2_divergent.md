# Milestone 2 review: unstated assumptions (divergent)

Read at c28caea: the plan, `audit/AUDIT.md`, every `consults/` file, the public contract, `reviews/p{0,1,2}_*.md`, and
the consumer's need in `14761-DM/AGENTS.md` and `.../plans/2026-09-11_codebase-topology/`. Measurements are read-only
passes over `_scratch/te-tracks-audit/{refroot/te_mm39/build/tables,source}/` and `01_modules/.ref/`.

## High
- [H1] **The `compat_tetranscripts_mm39` universe is the stated bridge to the legacy quantifications and ships no
  export.** Every export path is `interspersed` (`README.md:79-100`), while `docs/OUTPUTS.md:172` says `rename_map.tsv`
  is "superseded by `taxonomy_triple.saf` and the `compat_tetranscripts_mm39` universe". Failure: swapping the legacy
  triple SAF for the shipped `exports/ucsc/interspersed/full/taxonomy_triple.saf` moves the interval set by 34,680
  records (37,228 satellites leave, 2,548 tRNA-ancestry SINEs arrive), the 8 satellite triples vanish from the GeneID
  space, and the 20 doubled names lose their second triple key; a join of new counts to an archived matrix drops rows
  in both directions and raises nothing. Cost high. Phase 4 or 6: publish the compat exports with raw labels, or state
  in `OUTPUTS.md` that the compat universe is a membership table and the legacy comparison needs its own export.
- [H2] **One record-level GTF assumes consumers pick their grain by attribute.** Measured:
  `TEsingle/TEtools/TEindex.py:329-330` and `TElocal/TElocal_Toolkit/TEindex.py:419` name every group
  `transcript_id:gene_id:family_id:class_id[:strand]`; `TEtranscripts/TEToolkit/TEindex.py:436-437` reports
  `gene_id:family_id:class_id`. With `transcript_id` the per-record alias (`14_phase4_exports.md:9`), TEsingle and
  TElocal are pinned to record grain, TEtranscripts to subfamily; Stellarscope alone reads `--attribute`. Failure: the
  owner's subfamily-level TEsingle sensitivity run (`consults/owner_context_2026-09-15.md:23`) has no input, because
  the second GTF carrying `transcript_id = rmsk_name` was cut (`FINAL_REPORT.md:213`). `docs/OUTPUTS.md:166-167` states
  the attribute claim for all GTF consumers. Cost high. Phases 4 and 5.
- [H3] **The gene child seam assumes the exon-subtracted view answers the consumer's context question.** D2 requires
  `te_locus_dim.gene_context` and sub-peak TE intervals positioned against promoters and TSSs
  (`14761-DM/.../01_consult_codex.md:165-166`, `.../02_next_session_agenda.md:36-43`); the transcript relation is
  deferred (`18_phase8_gene_child_seam.md:21-27`). The nearest shipped field is `exon_subtraction_status.tsv`
  (`unchanged | trimmed | split | fully_subtracted`). Failure: a record wholly inside an intron reads `unchanged`,
  exactly like an intergenic record, so `gene_context` populated from that table labels every intronic TE intergenic —
  the one distinction snRNA needs, since an intronic TE read can be unspliced host transcription
  (`14761-DM/.../01_consult_codex.md:229`). Cost high; D2 ratification gates every downstream stage. Phase 8: name the
  minimum context fields D2 may assume, or state that `gene_context` waits for the design session.
- [H4] **The class census gate proves a class was listed and treats that as a disposition.** `config/mm39.classes.tsv`
  names 17 classes with `DNA?` the only `?` spelling; `interspersed` hardcodes nine classes (`docs/OUTPUTS.md:79`);
  publication requires only set equality against that file (`docs/OUTPUTS.md:87-88`). ADR-2 asked for "one reviewed
  disposition per observed label" (`FINAL_REPORT.md:76`) and no artifact records one. Failure: hg38 or a library
  refresh emits `LTR?`; the operator appends it to clear the gate; the predicate stays at nine classes; every `LTR?`
  record leaves the default universe silently. Cost high — that is the ERV class the aging story turns on. Phase 2 or
  3: add a `disposition` column and assert the predicate covers every class dispositioned `interspersed`.
- [H5] **Hashing the complete file inventory assumes the consuming ledger tolerates id churn.** `codex_critique.md:11`
  asked for an annotation identity separate from the delivery id — "Adding a BED view should not change every
  annotation foreign key" — and `FINAL_REPORT.md:135-142,244` adopts the two-section manifest without answering it.
  `DECISIONS.md:32` promises adapters keep entering releases, so each addition mints a new core `BUILD_ID`. Failure:
  adding `instance.bed` forces 14761's `te` and `te_locus_dim`, keyed `(te_release, locus_id)`, either to re-key 3.76M
  rows and every peak overlap or to hold a `te_release` that no longer resolves through `current`. The GENCODE-bump
  protection (`FINAL_REPORT.md:238`) covers a different axis. Cost high. Phase 7.
- [H6] **Host-only publication assumes the host build equals the tested build.** Acceptance runs in-container into
  `_scratch` (`19_phase9_acceptance_park.md:4`); the owner produces the published bytes on the host (`:10`);
  `99_verify.py` compares a snapshot against its own manifest. `reviews/p2_codex.md:18` measured that byte identity
  depends on the Python, pandas, pyarrow and zlib line, and the repository carries no environment pin. Failure: a host
  pyarrow one minor version off writes a different parquet footer, a different inventory digest and a different
  `BUILD_ID`, while every acceptance number still passes and nothing compares the two ids. Cost high: the published id
  is what every consumer pins. Phases 7 and 9: record the toolchain in `provenance`; make phase 9 compare the ids.
- [H7] **`taxonomy_rule_v1` assumes a record-count majority ranks family labels, with no notion of refinement.**
  Measured over `rmsk_taxonomy.tsv`: mm39 has exactly three parent/child family competitions — `MER53` (hAT 7,
  hAT-Blackjack 1,633), `UCON44` (TcMar 3, TcMar-Tigger 87), `X4b_DNA` (TcMar 5, TcMar-Tigger 125) — and in all three
  the specific label holds the majority, so the rule agrees with Dfam by arithmetic rather than by design. Failure: a
  library revision that puts the majority on the coarse parent publishes `canonical_family = TcMar` with
  `family_status = resolved_majority` and discards the Dfam-endorsed subtype; the agreement test catches it only inside
  the 20-name snapshot, and extending the snapshot is a recorded deferral (`13_phase3_taxonomy.md:78-79`).
  `codex_critique.md:10` raised the objection ("majority frequency alone does not establish the correct family") and
  the record carries no answer. Cost high. Phase 3: let a family token extending another with `-` win regardless of
  count, or make the snapshot extension a gate.

## Medium
- [M1] **The preflight is the only guard and exits non-zero on the configurations consumers run.** It reports both
  contig-set directions and length disagreements with "non-zero exit on any" (`16_phase6_ensembl_preflight.md:17-19`).
  14761's peak atlas is 21 UCSC chromosomes (`14761-DM/03_results/objects/mm39.chrom.sizes`), so the `ucsc` export
  against it reports 38 extra contigs and fails — the same signal as the fatal direction, which IRescue only warns
  about (`AUDIT.md:110-111`). Phase 6 acceptance already expects `ucsc` and `ensembl` to fail. A guard that fails on
  correct input gets its exit code ignored. Phase 6: separate the directions into distinct exits.
- [M2] **`unresolved` has two contradictory spellings in one release.** `docs/OUTPUTS.md:186` and
  `13_phase3_taxonomy.md:61-62` route unresolved names into one shared bucket; `family.bed` names them
  `unresolved/<rmsk_name>`, one bucket per name (`14_phase4_exports.md:8`, `docs/OUTPUTS.md:196`), while
  `record.gtf`'s `family_id` carries the bare `unresolved` and pools them. mm39 publishes zero unresolved rows
  (`13_phase3_taxonomy.md:66`), so the first assembly that ties ships a family BED and a family-grouped GTF that
  disagree on how many family groups exist. Phases 3 and 4.
- [M3] **The reference FASTA is declared and nothing reads it.** `GENOME_FA_URL` and `GENOME_FA_MD5`
  (`config/mm39.env:21-22`) have zero readers outside the config and the prompts, stay out of `SOURCES.json`
  (`src/00_fetch_sources.sh:15`), and `11_phase1_source.md:9` keeps them "as declared". Bounds check against
  `chrom.sizes`, which `codex_critique.md:39` notes cannot prove sequence identity; AUDIT F8 stands. So the assembly
  whose coordinates every export asserts is identified nowhere a consumer can verify, and phase 7 would hash an
  unverified claim. `AGENTS.md`'s own rule deletes a config key with no reader. Phases 1 and 7.
- [M4] **The retention estimate predates the adopted export list.** `FINAL_REPORT.md:157` sizes ten builds at "about
  1.5 GB per root". The adopted scope is 18 uncompressed export files (six levels x three namespaces) over 3,764,949
  records plus a phase-8 child, and the record GTF alone approaches 1 GB per namespace. "Keep every published build"
  plus a staged transfer into the CRI root (`17_phase7_publication.md:20`) then needs tens of GB on a shared
  filesystem. Phase 7 or 9: measure a build and restate the number.
- [M5] **`export_feature_members` carries no information for `full` exports.** Each row is (export path, feature id,
  record id, the record's own bounds), one block per record (`14_phase4_exports.md:15-16`), so 18 x 3,764,949 = 67.8M
  rows restate a join of universe membership against `rmsk_records`; the table earns its keep for phase 8's split
  pieces. It also sits inside the `BUILD_ID` inventory, compounding H5. Phase 4: register `exon_subtracted` and derive
  the full-interval case, or state that the table is a materialized convenience.
- [M6] **The instance key is fail-closed for the next assembly with no designed remedy.** `rmsk_instance_id` is the
  bare `.out` ID, asserted single-contig by check 21. RepeatMasker numbers per run, and the plan points at
  repeatmasker.org `.out` files for other assemblies (`FINAL_REPORT.md:121-123`). A source whose IDs restart per
  sequence trips the assertion and stops the build, and `DECISIONS.md:91`'s claim that the schema is ready for hg38
  carries no plan for namespacing the id by contig. The hg38 deferral is recorded; this condition is not.
- [M7] **Phases 3, 4, 6 and 8 get no divergent pass and have no external oracle.** Milestones sit after 2, 5, 7 and 9
  (`00_INDEX.md:12`), so phase 3 — the only phase introducing a new algorithm — is reviewed against the orchestrator's
  own rule text and its own acceptance numbers, with Dfam covering 20 of 18,484 names. Phase 8's single external
  anchor, the lab's 3,717,740-record no-exon count, is marked "to be re-measured" (`18_phase8_gene_child_seam.md:16-18`).
  A systematic rule defect then enters `tests/expectations/mm39/` and phase 9 confirms the build against its own
  numbers. Phase 3: add a divergent pass, or move a milestone onto phase 3.
- [M8] **Cross-build record correspondence is undelivered and unrecorded.** `rmsk_record_id` embeds the subfamily name,
  so a library revision renaming a subfamily yields a disjoint id set for unchanged coordinates.
  `FINAL_REPORT.md:191-192` calls equal strings across builds "a candidate correspondence" and ships no artifact, so a
  ledger on build A cannot carry to build B without recomputing every overlap, and no deferral names the gap. The fix
  is cheap: `rmsk_records` already carries the coordinates. Phase 7, or a recorded deferral.

## Low
- [L1] **The emitted-name whitelist permits the separator its own composite keys use.** `[A-Za-z0-9_.+/?()|:-]+`
  (`14_phase4_exports.md:17`) admits `:`, and `taxonomy_triple.saf` joins three components with `:`. mm39 carries zero
  colons across 18,484 names and 61 contigs (measured); hg38 is unmeasured. Phase 4: narrow the component alphabet.
- [L2] **Provisional membership is invisible in the files consumers read.** 5,893 records — Unknown 5,786, Unspecified
  98, `DNA?` 9 (`reviews/p2_opus.md:34`) — are provisional members of the default universe, and the flag lives only in
  `universe_members.tsv.gz`. Provisional status follows the class and the class follows the name, so a name-level
  reader recovers it and a `record.bed` reader needs a join. The `_candidates` suffix ADR-2 designed for this
  visibility gave way to short names (`FINAL_REPORT.md:241`). 0.16% of the default universe. Phase 4.
- [L3] **Prompts are the record, and out-of-band amendments live outside them.** `02_orchestration.md:48` makes prompt
  files the record; `p2_codex.md:24` shows a prompt's second rebuild replaced verbally at run time, leaving the review
  file as the only trace of what ran. Phase: orchestration.
- [L4] **UCSC dump stability.** `database/rmsk.txt.gz` and `bigZips/*.chrom.sizes` are regenerated without version
  paths, so a re-dump changes the md5 and `00_fetch_sources.sh` fails closed. A published build retains its own source
  bytes by copy (`src/00_fetch_sources.sh:28-30`, closing `reviews/p1_opus.md:16`), so the exposure is the window
  before first publication, where the only copies sit under `_scratch/te-tracks-audit/source`. Phases 1 and 9.

## Defended already
- The `.out` ID as a source-wide instance key for mm39: contiguity, uniqueness and single-contig scope measured and
  asserted — `AUDIT.md:41-44`, `p2_opus.md:28-30`, `tests/checks/core/21_instances.py`.
- Field-level agreement between the `.out` and the UCSC table, including the six negative consensus-left values —
  `AUDIT.md:149-166`, `audit/source_qualification_mm39.md`, `reviews/p1_opus.md:32`.
- RepeatMasker software and library identity recorded as declared — `AUDIT.md:132-137`, `config/mm39.env:16-18`.
- Alias coverage for the three namespaces: all 61 rows of `source/mm39.chromAlias.txt` carry non-empty, distinct
  values in every column (measured); the 39 scaffolds share one accession between ensembl and genbank, which is what
  makes `gencode` a rename of 22 chromosomes.
- Test data as a production build input, and the census gate ignoring its count column — `reviews/p2_codex.md:12`,
  `reviews/p2_opus.md:12`.
- Byte identity scoped to one builder and serialization line — `docs/OUTPUTS.md:112`.
- "Counts each read once" replaced by exon-disjoint sequence support — `DECISIONS.md:41-42`, `FINAL_REPORT.md:104-107`.
- Stellarscope's tied-locus zeroing, with the boundary gate kept as a failing assertion and the consumer version
  labelled unsupported — `FINAL_REPORT.md:24`, `15_phase5_consumer_fixtures.md:12-14`.
- `docs/RELEASES.md` still carrying the legacy id recipe, `INDEX.tsv` and `CURRENT_BUILD.tsv`: scheduled for phase 7,
  deferred at `README.md:106`. A consumer reading it first gets the superseded recipe: the live cost of that deferral.
- R `make.names()` mangling of exported ids: I predicted collisions and measured none — all 18,484 names and the 49
  canonical `<class>/<family>` labels map injectively, parentheses included (17,181 simple-repeat names).

Predicted first bite: H1 — the compat universe is already written into the public contract as the thing that supersedes
`rename_map.tsv`, and phase 4 ships the only triple SAF over a different interval set.
