# Milestone 2 rulings (orchestrator, 2026-09-16, reviewed tree `c28caea`)

Inputs: `m2_codex.md` (schema and identity; PASS WITH ADVISORIES, A1 to A5), `m2_divergent.md`
(unstated assumptions; H1 to H7, M1 to M8, L1 to L4), `m2_opus.md` (numbers and fixtures; section
appended below when it lands). Each ruling names the decision and where it lands. Plan-file edits are
applied in this commit; package changes ride `prompts/m2_fix.md` (unit `te-tracks-m2-fix`) or the
named phase prompt.

## Package changes before phase 3 (`te-tracks-m2-fix`)

- **H4 class disposition.** `config/mm39.classes.tsv` gains a `disposition` column over a closed
  vocabulary (`interspersed`, `satellite`, `simple_repeat`, `low_complexity`, `structural_rna`). The
  build gate asserts the observed class set equals the reviewed set, the classes dispositioned
  `interspersed` equal the `interspersed` predicate, `satellite` equals `{Satellite}`, and every
  provisional class is dispositioned `interspersed`. Check 22 asserts the same. The predicate stays
  authored once in `build_universes.py`; the disposition file is the review record it must agree with.
- **M3 declared assembly.** `SOURCES.json` gains `declared_assembly` (`genome_fa_url`,
  `genome_fa_md5`, `status: declared`) written from the config pins without a fetch; check 11 asserts the
  values equal the config. The FASTA pins thereby gain a reader, and phase 7 carries them into identity.
- **L1 component alphabet.** `rmsk_name` rejects `:` alongside `|` and whitespace, with a fixture row.
  Phase 4 states the component alphabet `[A-Za-z0-9_.+/?()-]+`; emitted ids add the separators `|` and `:`.
- **A4, H1, H2 disposition rows in `docs/OUTPUTS.md`.** `te_locus.locInd` becomes an index built from
  `record.gtf` by TElocal's own indexer (phase 5); `rename_map.tsv` is superseded by
  `tables/taxonomy_canonical.tsv` (phase 3) with the legacy selection reproducible as the
  `compat_tetranscripts_mm39` membership; `te_subfamily.gtf` maps to `subfamily.gtf` (phase 4) and
  `te_locus.gtf` to `record.gtf` (phase 4). The one-GTF claim is withdrawn.

## Phase 3

- **M2 unresolved spelling.** A name unresolved at a rank carries an empty canonical label there, and
  every rollup at that rank names it `unresolved/<rmsk_name>`, one bucket per name, so unrelated names
  never pool into one feature. `family.bed`, `record.gtf` attributes and `taxonomy_triple.saf` follow the
  same spelling. mm39 publishes zero unresolved names, so no number moves.
- **H7 majority versus refinement.** `taxonomy_rule_v1` stands. Check 31 asserts set equality between
  the resolution report and the Dfam snapshot, so every multi-label name is oracle-checked and a source
  whose multi-label names outgrow the snapshot fails the check until the snapshot covers them. That
  assertion is the admission gate for a new source. mm39's three parent/child competitions (`MER53`,
  `UCON44`, `X4b_DNA`) resolve to the specific token by count and gain an explicit rule fixture. A
  refinement-aware rule would be `taxonomy_rule_v2` and waits for a measured case.
- **M7 review coverage.** Phase 3 adds a `divergent` pass on the rule to the codex and Opus reviews.

## Phase 4

- **H2 subfamily GTF.** `subfamily.gtf` (`gene_id` and `transcript_id` = `rmsk_name`) joins the export
  set as the subfamily-grain input for TEsingle and TElocal, whose feature key includes `transcript_id`.
  Named consumer: the owner's TEsingle sensitivity run at subfamily grain. `record.gtf` stays the
  record-grain input; TEtranscripts reads either at `gene_id` grain.
- **M5 registration size.** `export_feature_members` is keyed by `(universe_name, variant,
  feature_level)`; emitted ids carry UCSC contig names inside the record alias and are therefore
  namespace-invariant, so one registration serves the three namespaces. `tables/exports.tsv` inventories
  every export path with its namespace, universe, variant, level and format.
- **A2 membership read.** Export builders read `universes.json` and `universe_members.tsv.gz` from the
  build and never re-evaluate predicates.
- **L2 provisional visibility.** Exports carry no provisional flag; the status is a class property
  recoverable by joining names to `rmsk_taxonomy` or records to `universe_members`. Stated in OUTPUTS.md.
- **H1 compat universe.** Ships as membership only. The legacy comparison is a phase 9 reconciliation.

## Phase 5

- **A4 TElocal index.** The `.locInd` fixture builds the index from `record.gtf` with TElocal's
  `TEindex` and loads the pickle back through TElocal's reader.
- **H2 grain fixtures.** TEsingle tuple asserted at record grain from `record.gtf` and at subfamily
  grain from `subfamily.gtf`.

## Phase 6

- **M1 preflight exits.** Exit 0 when contig sets agree and lengths match; exit 2 when the sets differ
  with a non-empty agreeing intersection, both lists printed; exit 1 when a shared contig disagrees in
  length or the intersection is empty. Amended by `p6_rulings.md` B2: exit 0 whenever every export contig is present
  with an agreeing length; reference-only contigs are informational; exit 2 for export contigs the reference lacks.

## Phase 7

- **H5 two identities.** `CATALOG_ID = sha256("te-tracks-catalog-v1\n" + canonical_json(catalog))`
  over source digests, declared run identity, parser profile, `instance_id_scope = source_run`, and the
  digests of the four canonical tables. Consuming ledgers key records on `(te_catalog_id,
  rmsk_record_id)` and record `te_build_id` as provenance. Adding an export, a universe or a taxonomy
  rule version mints a new `BUILD_ID` and keeps `CATALOG_ID`. The owner may overturn this before phase 7.
- **A1, M6 instance scope.** Identity publishes the single source-run requirement and
  `instance_id_scope`. hg38 admission requires a source-wide numbering or a contig-scoped instance key
  decision, recorded in the deferred list.
- **A2 grammar version.** `schema_version` owns predicate semantics; a new key bumps it.
- **A3 byte profile.** `universes.json` keeps the writer's profile (insertion order, indent 2,
  `ensure_ascii=False`, UTF-8, final LF), published in OUTPUTS.md; `canonical_json` sorts keys.
- **A5 readers.** OUTPUTS.md publishes reader settings for pandas, DuckDB and R (`data.table`,
  `arrow`); a nullable column defines its literal before it lands.
- **H6 toolchain.** `provenance` records Python, pandas, pyarrow, zlib and the devcontainer image; the
  host build runs inside the same image.
- **M4 retention.** Restated from a measured build size.
- **M8 correspondence.** Cross-build record correspondence on `(chrom, start_1, end_1, strand)` is a
  recorded deferral.

## Phase 8

- **H3 gene context.** `exon_subtraction_status` describes counting-support geometry under the exon
  mask; `unchanged` covers intronic and intergenic records alike. `gene_context` for the 14761 ledger
  waits for the transcript-context design session, and D2 populates nothing from the status table.

## Phase 9

- **H1 reconciliation.** The `compat_tetranscripts_mm39` membership count equals the row count of the
  published legacy `te_subfamily.saf`.
- **H6 id comparison.** Published table digests, `CATALOG_ID` and `BUILD_ID` equal the in-container build.
- **L4 source cache.** The runbook seeds the host `TE_TRACKS_SOURCE_CACHE` from the container's retained
  source copy; a checksum mismatch stops for a re-pin decision.

## Orchestration

- **L3 amendments.** Anything given to a running unit is appended to its prompt file under an
  `Amendments at run time` heading before the review launches.

## Opus review (numbers and fixtures; PASS WITH ADVISORIES, A1 to A6)

Every published number reproduced from the pinned `.out` with independent code, zero mismatches over
5,320,771 rows and 24 columns; rebuild byte-identical; every named gate broken by mutation on a scratch copy.

- **A1 runner self-test.** Accept, `te-tracks-m2-fix`: `tests/checks/core/01_runner_selftest.sh` copies
  `tests/run.sh` into a scratch tree with a probe check directory (pass, unsupported, required-unsupported,
  fail, dangling symlink) and asserts the runner's exit codes and status lines.
- **A2 gate fixtures share the eight-row UCSC table.** Accept, `te-tracks-m2-fix`: each single-row gate
  fixture gets a matching one-row UCSC table so the failure it proves is the one it names.
- **A3 "class census" in DECISIONS.md.** Accept, `te-tracks-m2-fix`: entry 2 states the gate as the
  observed class set matching the reviewed disposition file.
- **A4 consensus ordering.** Accept, `te-tracks-m2-fix`: OUTPUTS.md states beside the signed-column contract
  that consensus start and end follow the source, two mm39 records carry start above end, and a derived
  consensus-match length is signed.
- **A5 expectation provenance.** No byte changes. The independent recompute in check 22 is the oracle; the
  expectation file carries the same numbers by three independent derivations (orchestrator, codex, Opus).
- **A6 column re-derivation at check time.** No change now. The qualification report and its tracked copy
  are the seam; phase 7 identity carries the source digests and the report digest so the report is
  provably about these tables.

## Defended, no change

Codex confirmed the export alphabet against every measured name and the three TE parsers, the compat
predicate against the legacy class list (empty symmetric difference), and the record key's
reversibility. Divergent measured R `make.names()` injectivity over all names and labels and complete
chromAlias coverage. The consult's nonnegative consensus-left wording is superseded by the measured
signed contract (`audit/AUDIT.md` section 7).
