# Milestone 5 review: unstated assumptions (divergent)

Read at `9ac66fb`: plan `00_INDEX.md` and `14_` to `19_`; `reviews/{m2_rulings,m2_divergent,p3_rulings,p3_divergent,p4_rulings,p5_rulings}.md`;
`consults/{owner_context_2026-09-15,A_consumer_contracts,ADR5_consult}.md`; `README.md`, `docs/{DECISIONS,OUTPUTS}.md`; the consumer's need in
`14761-DM/AGENTS.md` and `.../plans/2026-09-11_codebase-topology/`; `src/lib/build_exports.py`, `tests/lib/consumers.py`,
`tests/checks/consumers/*`, `tests/fixtures/{consumers,exports}/**`. Measurements are read-only passes over
`_scratch/te-tracks-audit/refroot/te_mm39/{build,te_mm39_20260917}/` and `01_modules/.ref/`.

## High

- [H1] **`compat_tetranscripts_mm39` reproduces the legacy selection, so phase 9 can compare a count to it.**
  Failure: the reconciliation is already false by 1,235 records. Measured: compat membership 3,799,629
  (`tables/universe_summary.tsv`) against 3,800,864 legacy loci (`te_mm39_20260917/te_dim.tsv`, `n_loci` sum; `te_loci.tsv.gz`
  carries the same rows, and a SAF built from it carries one row each). The whole delta is one triple — `LFSINE_Vert/tRNA/SINE`,
  1,235 records, 125,908 bp — which the legacy release keeps and `family_prefix_excluded: "tRNA"` drops. The legacy rule
  excluded `tRNA-`: of the 2,548 tRNA-family SINE records in `interspersed_plus_satellites`, legacy dropped `tRNA-Deu` (388)
  and `tRNA-RTE` (925) and kept bare `tRNA` (1,235). `m2_rulings.md` ("Defended, no change") checked the compat *class* list;
  the family prefix was never compared to the legacy selection, and `m2_divergent.md` H1's 34,680 rests on the same premise
  (the measured interspersed-to-legacy delta is 35,915 = 37,228 satellites out, 1,313 tRNA-hyphen records in). Cost high: this
  is the only external oracle the compat universe has. Phase: fix the predicate before phase 7 hashes it; phase 9 fails its own gate otherwise.

- [H2] **One universe serves every consumer.** Failure: the consumer's ATAC channel has no registered feature. `interspersed`
  omits 1,555,822 records (29.2%, 85.0 Mbp), including all 37,228 Satellite records and 49 tRNA names (measured over
  `rmsk_records.parquet` and `universe_members.tsv.gz`), and every shipped BED, GTF and SAF is `interspersed`
  (`tables/exports.tsv`, 7 rows). 14761's ATAC route starts "from existing corrected fragments and the full RepeatMasker locus
  set" and its `te_locus_dim` is the full catalog (`01_consult_codex.md`, "ATAC counting choice"; "Keys, types and ownership").
  That stage builds its own BED from `rmsk_records.tsv.gz`, so its features never enter `export_feature_members` and the
  every-feature-registers rule (`owner_context_2026-09-15.md:46-49`) holds for none of them. Cost high. Phase 6: ship a record
  BED for `all_rmsk` or `interspersed_plus_satellites`, or record the deferral naming the consumer that then rolls its own.

- [H3] **A parser that passes on 11 rows authorizes the 3,764,949-row export.** Failure: the first real Stellarscope run
  exhausts the box. Measured: `IntervalTreeAnnotation(record.gtf, "locus", "exon")` over a 50,000-row head of the shipped file
  costs 129.2 MB resident, 2,709 B/row, projecting 10.2 GB for 3,764,949 rows before a BAM opens; TElocal's `TEindex` builds
  the equivalent structure from the same file, and `record.gtf` is 1.2 GB on disk. The only recorded floor is 5.5 GB for
  te-tracks' own writer (`p4_rulings.md` A5, carried into `17_phase7_publication.md`), and it describes the producer on a
  32 GB box. Cost high. Phase 9 runbook, with a measured floor per consumer.

- [H4] **Both record-id spellings sit at `feature_level = record`, and the conservation rule holds there.** Failure: a
  record-keyed rollup doubles. Measured: `export_feature_members.tsv.gz` carries 7,529,898 `record` rows over 3,764,949
  records (plus 3,764,949 each at `subfamily`, `family`, `taxonomy_triple`). Both conservation proofs delete the alias before
  proving anything — `tests/checks/core/41_export_registration.py:33-37` and `tests/checks/consumers/30_registration_duckdb.py:36`
  filter `emitted_feature_id = rmsk_record_id`, and both exclude `taxonomy_triple` entirely. `docs/OUTPUTS.md:398-400` tells the
  ledger to select "each distinct measured feature once" and publishes no such filter, so a peak overlapping one record returns
  two registration edges and the "count 7 stays 7" guarantee is proven on the one shape that cannot exhibit the defect.
  Cost high: `te_feature_registration` is the seam the whole ledger conserves through. Phase 4 or 7: separate the two levels, or publish the filter as contract.

## Medium

- [M1] **`CATALOG_ID` reaches the consuming ledger.** Failure: the ledger keys on `BUILD_ID` and re-keys on every export
  addition. `CATALOG_ID` and `te_catalog_id` appear in no `README.md`, `AGENTS.md` or `docs/*.md` (grep) — only in plans,
  prompts and `m2_rulings.md`, which rules the ledger key to be `(te_catalog_id, rmsk_record_id)`. 14761's `te_locus_dim` has
  one release column (`te_release`), so it binds the published id, and adding `instance.bed` re-keys 3.76M `te` rows plus every
  `peak_te_overlaps` row for a reference whose records did not move. Cost medium, high once D2 ratifies. Phase 7: publish both ids in DECISIONS.md §7.

- [M2] **Every export is authorized by its real parser.** Failure: two of the seven never meet one. `family.bed` and
  `taxonomy_triple.saf` appear in zero consumer check (grep over `tests/checks/consumers/`, `tests/lib/consumers.py`); the
  checks read `record.bed`, `subfamily.bed`, `record.gtf`, `subfamily.gtf`, `subfamily.saf`. ADR-3 (`DECISIONS.md:32`) requires
  a named consumer and a passing fixture per adapter. The owner's required case — "a subfamily name with two classification
  triples → aggregation does not duplicate" (`owner_context_2026-09-15.md:55`) — is unrepresentable in the shipped triple SAF:
  canonical labels collapse the 20 doubled names, so 1,240 raw interspersed triples become 1,220 GeneIDs (measured), where the
  legacy lab SAF keyed raw triples. Cost medium. Phase 5 fix, or phase 9 with the reconciliation.

- [M3] **A feature level is recoverable from the file it came from.** Failure: two estimators emit identical feature names.
  TEtranscripts' group from `record.gtf` is `gene_id:family_id:class_id`, byte-identical to `taxonomy_triple.saf`'s GeneID
  (verified row by row: `L1MdA_VI:L1:LINE`, `ID2:ID:SINE`, `Tigger9a:TcMar-Tigger:DNA`, …), while `tables/exports.tsv` declares
  `record.gtf` at `feature_level = record` and the registration carries the triple once under `taxonomy_triple`. A TEcount
  matrix over `record.gtf` and a featureCounts matrix over the triple SAF then share every feature name, and the registration
  attributes the TEcount features to a file that run never read. `ADR5_consult.md` §6 states that a name match establishes no
  estimator equivalence and nothing enforces it. Cost medium. Phase 4: record the secondary levels a file supports.

- [M4] **The vendored checkouts stand in for what the owner installs.** Failure: the authorized code is uninstallable by
  version. Measured `git describe`: irescue `v1.2.0-20-g26f36fb`, TEsingle `1.0-8`, MATES `v0.1.8-9`, TEtranscripts `2.2.4-13`,
  TElocal `1.1.3-4`, Stellarscope `1.5` (clean). `git diff v1.2.0..HEAD -- irescue/map.py` changes 138 lines and `makeRmsk`'s
  own signature; MATES's `split_count_10X_data` signature changed since `v0.1.8`. Those are exactly the entry points
  `10_irescue_parser.py`, `15_irescue_chrcat.py` and `14_mates_parser.py` exercise. `pip install irescue==1.2.0` gives a
  different `makeRmsk`. The checks report the version they read, so the record is honest and the inference is not.
  Cost medium. Phase 5 or 9: state which distribution each fixture authorizes.

- [M5] **The 4/2 versus 3/3 allocation fixture pins IRescue's EM.** Failure: it pins conservation alone. `irescue_check`
  (`tests/lib/consumers.py:518-534`) asserts `0 <= x <= 3`, `counts[B] == right + (3 - x)` and `sum == 9`, so an EM putting all
  three shared molecules on the record with less unique support passes both cases, and the two cases are indistinguishable by
  assertion. The observed split is written to `irescue_allocation.json` and reported. The check has never run (`irescue`
  absent). `02_orchestration.md` lists this fixture as a validation challenge deserving its own reviewer. Cost medium.
  Phase 5 fix: assert 2.0/1.0 and 1.5/1.5, the values proportional allocation predicts.

- [M6] **CB+UB is the molecule the pipelines count.** Failure: cohort-level loss is invisible. Every fixture BAM carries one
  barcode (`CELL`, `consumers.py:27`), so IRescue's whitelist path, Stellarscope's empty-cell retention and TEsingle's
  `--cutoff 1000` against a real per-nucleus distribution are all unexercised; the cutoff is tested on synthetic 999/1,000
  dictionaries. The owner asked to "audit its default barcode threshold" (`owner_context_2026-09-15.md:23`), and TEsingle
  counts distinct raw `UR` before any overlap test, dropping a barcode below 1,000 with one aggregate message
  (`A_consumer_contracts.md:35`). A 3' ARC nuclear library can lose its whole roster there while the fixture reports the export
  supported. Cost medium; the audit is the consumer's, and the record should say so. Phase 5 contract wording, phase 9 handoff.

- [M7] **`unsupported` distinguishes a missing capability from a broken contract.** Failure: a fully degraded run exits 0.
  `tests/run.sh:77-82` raises `runner_exit` for exit 3 only when the filename ends `.required.sh|.required.py`, and no file in
  `tests/checks/consumers/` does. An environment change that turns the seven passing checks into `ModuleNotFoundError` on an
  external module (classified unsupported at `consumers.py:114-147`) prints twelve `unsupported` lines and exits 0, which phase 9
  reads as the consumer seam met. Today 5 of 12 are unsupported, and of the four execution checks only `bedtools` and `samtools`
  ran: no TE quantifier executable has ever executed here. Cost medium. Phase 5 or 9: the plan calls the parser checks always
  supported, so name them `.required.py`.

- [M8] **Split pieces register under the published unique key.** Failure: phase 8 violates a phase 4 assertion by
  construction. `docs/OUTPUTS.md:392-393` states that each `(universe_name, variant, feature_level, emitted_feature_id,
  rmsk_record_id)` occurs once; `18_phase8_gene_child_seam.md:15,20` registers every retained piece with its own
  `block_start_1`/`block_end_1` and expects "two pieces with the parent id". The first split record writes two rows with an
  identical five-tuple, so either the assertion fails on the child build or it is relaxed and `exon_subtracted` loses its key.
  `ADR5_consult.md` §5 already carries `block_index` in the key for this reason. Cost medium. Phase 8, before it writes.

## Low

- [L1] **The BED score carries score information.** 1,224,713 of 3,764,949 interspersed records carry `sw_score > 1000`
  (32.5%, max 71,131; measured), so `min(sw_score, 1000)` reads exactly 1000 for a third of every BED while `record.gtf` keeps
  the raw value. Failure: filtering `score >= 1000` for high-scoring records selects a third of the universe with no ranking
  inside it. Phase 4: `docs/OUTPUTS.md` names the clipped score a display convention and `rmsk_records.sw_score` the filterable value.

- [L2] **The `unresolved_*` tokens are ready for a consumer.** They are exporter-tested — `tests/fixtures/exports/taxonomy.tsv`
  carries `Mystery` (family) and `Opaque` (both ranks) and the expected `family.bed`, `record.gtf` and `taxonomy_triple.saf`
  contain them — and the consumer roster (`consumers.py:29-41`) resolves every rank, so no real parser has read one. mm39
  publishes zero. Failure: the first tied name turns `family.bed`'s 49 buckets into 49 + n, each unresolved name its own
  family, and a family rollup stops rolling up for it. Phase 6 with the hg38 `?` sizing, or a recorded deferral.

- [L3] **MATES is covered.** `record_mates.csv` and `.bed` are fixture-only (`docs/OUTPUTS.md`, consumer table), so a named
  consumer has a passing fixture and no export; `write_mates_pair` (`consumers.py:184-191`) sets column 5 from
  `enumerate(records)`, a row ordinal, where `ADR5_consult.md` §4 requires the MATES numeric index be registered. Failure: a
  consumer regenerating the pair under another sort re-points every `TE_index`, and the locus MTX `features.csv`, which carries
  only that index, addresses different records. Phase 6 or 8, or state MATES outside the release.

- [L4] **Independent review of the numbers.** All three milestone passes measure one artifact,
  `_scratch/te-tracks-audit/refroot/te_mm39/build/`, and phase 9 compares a fresh build to `tests/expectations/mm39/`, whose
  values came from that builder's output by three derivations (`m2_rulings.md` A5). A deterministic builder defect reproduces
  identically in every pass; the external oracles are Dfam (20 of 18,484 names) and the legacy release, which H1 shows
  disagrees. Phase 9: the acceptance fixtures need an oracle the builder did not produce.

- [L5] **Prompts are the record.** `02_orchestration.md:48` makes prompt files the record; at `9ac66fb`
  `prompts/m5_{codex,divergent,opus}.md` are modified in the working tree and in no commit, so the brief governing three
  milestone-5 reviews exists only on disk while the reviews land committed. Orchestration.

## Defended already

- `gene_context` waits for the transcript-context session and D2 populates nothing from the status table — `m2_rulings.md` (Phase 8, H3), `18_phase8_gene_child_seam.md:29-33`.
- The Stellarscope right-boundary defect is kept as a failing assertion rather than a shifted GTF — `15_phase5_consumer_fixtures.md:12-14`, `11_stellarscope_parser.py:43-46`; the raw `get_blocks()` path the gate uses is what `_assign_pair_threshold` runs for a single-end read (`model.py:519-526`, `calignment.pyx:95-100`).
- `unsupported` is reserved for a third-party module the checkout itself needs, with internal import failures exiting 1 — `p5_rulings.md` B3, `consumers.py:114-147`, self-tested at `00_tool_inventory.py:22-34`.
- The MATES dotted-stem path hazard resolves to `record.bed` and the check asserts it — `14_mates_parser.py:78-83`.
- Emitted ids are namespace-invariant, so one registration serves three namespaces — `m2_rulings.md` M5, `docs/OUTPUTS.md:396-397`; measured, every alias carries a UCSC contig.
- The comma hazard in IRescue feature names, with exporter rejection on both patterns — `10_irescue_parser.py:41-53`.
- Deterministic gzip headers and semantic `.locInd` comparison across embedded GTF paths — `p5_rulings.md` A1.
- Score clipping belongs to the exporter and the table keeps the source value — `ADR5_consult.md` §2 (column 10), `build_exports.py:142`.

Predicted first bite: H1 — the compat universe is the release's one external oracle, and the artifacts on disk disagree with it by 1,235 records for a reason no file in the record names.
