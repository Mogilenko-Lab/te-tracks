# te-tracks — implementation in progress (orchestration session 2026-09-16)

## Where the work stands

Branch `redesign-2026-09` in te-tracks, baseline commit `270afd4` (plan, audit, consults, taxonomy
evidence). The owner ruled on 2026-09-16: no manual taxonomy curation; phase 3 derives canonical labels
by `taxonomy_rule_v1` and checks them against the pinned Dfam snapshot in a test. The owner also
authorized fan-out without per-agent permission prompts and the per-phase commits (see
`plans/2026-09-16_te-tracks-redesign/02_orchestration.md`, "Standing authorizations").

**Phase 0** (decisions, scaffold, truth table, `tests/run.sh`) is complete and committed on the
branch. Loop: implemented by codex (`te-tracks-p0-impl`); codex review `reviews/p0_codex.md` (BLOCKING:
incomplete truth table, over-broad export promise, runner skipping non-executable checks, legacy
artifacts without disposition); fix `te-tracks-p0-fix`; Opus re-review `reviews/p0_opus.md` (FAIL:
`taxonomy_triple.saf` described with raw labels where the contract emits canonical ones, and the ADR 5
ledger sentence read as three te-tracks deliverables; seven advisories on the preflight signature, the
`docs/RELEASES.md` row, runner wording, dangling symlinks, relative `--refroot`, swallowed diagnostics);
fix `te-tracks-p0-fix2` from `prompts/p0_fix2.md` (all nine items); orchestrator re-verification
(runner exits 1/1/0/1/1/2 on fail, required-unsupported, unsupported, hidden `.py`, dangling symlink,
missing dir; relative `--refroot` exported absolute; failures print full stdout to stderr; negation
grep clean; no git write in any reachable repo). The phase 0 commit also carries the plan edits (ADR 3
enumerates the export matrix; ADR 5 ledger sentence; phase 4 adds `taxonomy_triple.saf`; phase 6 adds
the `gencode` contig namespace; phase 8 ships the child SAFs in all three namespaces), `audit/AUDIT.md`
§6 with `audit/gencode_grcm39_fasta_contigs.tsv`, both reviews and `redesign-2026-09/prompts/`.

**Phase 1** (pinned `.out` source, parser profile `rm_out_v1`, qualification against the UCSC table) is
complete and committed on the branch. Loop: implemented by codex (`te-tracks-p1-impl`); codex review
`reviews/p1_codex.md` and Opus re-review `reviews/p1_opus.md`, both PASS WITH ADVISORIES and both
reproducing every acceptance number independently; fix `te-tracks-p1-fix` from `prompts/p1_fix.md`
(phase 2 field names `divergence_pct`, `deletion_pct`, `insertion_pct`, `rmsk_instance_id` as the complete
token; check 11 asserts all 13 summary metrics, compares the build report with the tracked copy and the
SOURCES.json md5s with the config pins; cache files copied; dead helpers removed; public prose about the
legacy build corrected); that round stopped the build on six source rows with a negative consensus-left
value, recorded as `audit/AUDIT.md` section 7; fix `te-tracks-p1-fix2` from `prompts/p1_fix2.md`
(`query_left_bp` nonnegative, `consensus_left_bp` signed, Charlie17 row 669264 as fixture); orchestrator
re-verification from a clean build (5,320,771 rows matched, zero disagreements, 4,696,900 contiguous ids,
three collision pairs, report byte-identical to the tracked copy, both core checks pass, sign and report
mutations fail their checks, link count 1 on every retained source).

**Phase 2** (canonical records, instances, raw taxonomy, universes) is complete and committed on the
branch. Loop: implemented by codex (`te-tracks-p2-impl`, 1,313 s); codex review `reviews/p2_codex.md` and
Opus re-review `reviews/p2_opus.md`, both PASS WITH ADVISORIES, both reproducing every number and the
byte-identical build; fix `te-tracks-p2-fix` from `prompts/p2_fix.md` (README build and outputs paragraphs;
legacy `te_loci.tsv.gz`/`te_dim.tsv` dictionary restored in OUTPUTS.md with disposition rows; reviewed class
set moved to `config/mm39.classes.tsv` as the build's gate with counts kept in
`tests/expectations/mm39/class_census.tsv` and check 22 asserting the two sets agree; UCSC label
disagreement fixture; one interspersed class list and the `or` grammar key removed; redundant sample
assertion removed; census read with explicit dtypes; instance statistics keyed by the text token);
orchestrator re-verification from a clean build (all six table digests unchanged by the fix,
`universes.json` re-digested, six core checks pass, report byte-identical). Build time about five minutes;
the seven artifacts reproduce byte-for-byte across three independent builds (orchestrator, codex, Opus).

**Measured this session.** The GENCODE GRCm39 FASTA the lab aligns against names chromosomes
UCSC-style and scaffolds by GenBank accession (22 + 39 of 61 contigs); hence the third namespace
`gencode`. All-record taxonomy: 18,484 names, 18,504 triples, 1,201,573,004 bp summed length. Six `.out`
rows (all `C` strand) carry a negative consensus-left value; zero rows carry a negative query-left value
(`audit/AUDIT.md` section 7).

**Milestone 2 review** (after phase 2, tree `c28caea`) is complete and committed. Three parallel read-only
reviewers: codex on schema and identity (`reviews/m2_codex.md`, PASS WITH ADVISORIES, five advisories on
instance scope, grammar versioning, the `universes.json` byte profile, TElocal's pickle index and reader
settings), Opus on numbers and fixtures (`reviews/m2_opus.md`, PASS WITH ADVISORIES; every published number
re-derived from the pinned `.out` with independent code, zero mismatches over 5,320,771 rows and 24 columns,
rebuild byte-identical, every gate broken by mutation; six advisories), and a `divergent` pass on unstated
assumptions (`reviews/m2_divergent.md`, seven High, eight Medium, four Low). Every finding has a ruling in
`reviews/m2_rulings.md`; the rulings are written into the plan files for phases 3 to 9 and into
`02_orchestration.md`. Two fix rounds (`prompts/m2_fix.md`, `prompts/m2_fix2.md`; the first round stopped on two
prompt errors and reported them) landed the package changes: `config/mm39.classes.tsv` carries a `disposition`
column and the build asserts it agrees with the `interspersed` and `satellite` predicates class by class;
`SOURCES.json` carries the declared assembly FASTA pins and check 11 asserts them; `rmsk_name` rejects `:`;
each single-row gate fixture has its own one-row UCSC table; a runner self-test check exercises every runner
status and exit; four legacy disposition rows, the consensus ordering sentence and the class-set wording in
`docs/OUTPUTS.md` and `docs/DECISIONS.md` are corrected. Orchestrator re-verification: seven core checks pass,
every table digest and `universes.json` byte-identical to the phase 2 build, four class-file mutations and a
colon name fail with the intended messages.

Rulings the owner may still overturn before their phases: phase 7 publishes a second identity, `CATALOG_ID`
over the record catalog alone, for consuming ledgers to key on (H5); phase 4 adds `subfamily.gtf` because
TEsingle and TElocal key features on `transcript_id` (H2); the compat universe ships as membership only and
the legacy comparison is a phase 9 reconciliation (H1); `gene_context` for 14761 waits for the transcript-context
design session (H3).

**Phase 3** (canonical taxonomy by rule) is complete and committed on the branch. Loop: implemented by codex
(`te-tracks-p3-impl`); three reviews in parallel per ruling M7: codex `reviews/p3_codex.md` (BLOCKING: the
family fallback scoped across all classes, the Dfam release response absent from the provenance, the manifest
requirement belonging to phase 7), Opus `reviews/p3_opus.md` (FAIL: the same fallback defect; check 30 blind to
single-label corruption; provenance residue; independent re-derivation of every row otherwise exact) and divergent
`reviews/p3_divergent.md` (five High: record-count weighting rewards fragmentation, the admission gate's literals,
the one-class-wide oracle, float noise in the median, one unresolved token for two ranks). Rulings in
`reviews/p3_rulings.md`; the phase file was rewritten to the corrected contract before the fix: votes weight by
RepeatMasker instance (`rmsk_taxonomy` gains `instance_count`; every mm39 winner unchanged; minimum contested share
0.840 on `MER63C`, measured independently by the orchestrator, the divergent reviewer and the implementer),
`resolved_plurality` naming with `class_plurality_share`, `family_plurality_share` and `family_support_share`,
two-decimal medians, rank tokens `unresolved_class_<name>` / `unresolved_family_<name>`, the census in
`tests/expectations/mm39/taxonomy_census.tsv`, check 30 recomputing all 15 columns on every row, check 31 as a subset
gate reading count and date from evidence, the snapshot provenance recording the release response as the next
refresh's addition. Fix `te-tracks-p3-fix` from `prompts/p3_fix.md`; orchestrator re-verification (ten core checks;
every table outside the taxonomy trio byte-identical to the milestone build; an independent instance-weighted
implementation reproduces all 15 columns on all 18,484 rows); codex re-review of the fix `reviews/p3_codex2.md`
(PASS WITH ADVISORIES; every earlier finding closed; two phase 4 integration notes folded into `p4_impl.md`).
Digests: `rmsk_taxonomy.tsv` 26a9110f…, `taxonomy_canonical.tsv` a3663b64…, `taxonomy_resolution_report.tsv`
1f8c068f….

**Phase 4** (`interspersed` exports in the UCSC namespace) is complete and committed on the branch. Loop:
implemented by codex (`te-tracks-p4-impl`) from `prompts/p4_impl.md` aligned with the milestone 2 and phase 3
rulings: seven exports (`record.bed`, `subfamily.bed`, `family.bed`, `record.gtf`, `subfamily.gtf`,
`subfamily.saf`, `taxonomy_triple.saf`), `export_feature_members` keyed by `(universe_name, variant,
feature_level)` with both id spellings at level `record` (18,824,745 rows), `tables/exports.tsv` as the inventory
with measured rows and sha256, the component alphabet without `/` and `/` rejected in names, rank tokens in
position. Codex review `reviews/p4_codex.md` (BLOCKING on the DuckDB conservation query the plan asked for in a
container without DuckDB; three advisories) and Opus re-review `reviews/p4_opus.md` (PASS WITH ADVISORIES; every
export and both tables regenerated bit-identically with independent code; five gates broken on demand; the sort
statement corrected to text columns in byte order and coordinates numeric; the writer's 5.5 GB peak RSS recorded
in the phase 7 plan). Rulings in `reviews/p4_rulings.md`; fix `te-tracks-p4-fix` from `prompts/p4_fix.md`
(README count to seven; conservation fixture asserting targets and totals; the DuckDB form as
`tests/checks/consumers/30_registration_duckdb.py`, unsupported here; the `unresolved_` prefix reserved and
enforced with a fixture; sort sentences). Orchestrator verification: thirteen core checks; `consumers` one
unsupported, exit 0; an independent recount over all 3,764,949 universe records reproduces every export (offsets,
names, clipped scores, 49 family buckets, 1,220 triple GeneIDs, GTF attribute order and values, inventory digests,
two spellings per record, no character outside the alphabet); every export digest unchanged by the fix; the seven
exports measure 2.6 GB per namespace.

**Phase 5** (consumer fixtures) is complete and committed on the branch. Loop: implemented by codex
(`te-tracks-p5-impl`) from `prompts/p5_impl.md`; codex review `reviews/p5_codex.md` (BLOCKING: Stellarscope reported
unsupported on its top-level `setuptools_scm` import before its parser ran; the IRescue check asserted counts alone at
record grain; MATES unsupported on `pkg_resources` with `pyranges` misnamed as the dependency; two advisories) and Opus
re-review `reviews/p5_opus.md` (FAIL: the same three; every `ImportError` classed as unsupported; the acceptance
sentence contradicting the observed boundary; eight advisories on gzip nondeterminism, versions, `UB` equal to `UR`,
absent reverse and flagged reads, MATES scratch, the inventory oracle, contract wording, scope). Rulings in
`reviews/p5_rulings.md`; plan 15 gained the system-tool dependency clause and the amended acceptance sentence (a parser
test passes, or reports the documented upstream defect or a named system dependency as `unsupported`; the runner exits
0 in every case). Fix `te-tracks-p5-fix` from `prompts/p5_fix.md` (eight items): the Stellarscope `annotation`
subpackage loads in isolation and the check reaches the boundary gate, observes `0,1,1,1` and reports the documented
right-boundary defect; MATES functions execute from source with a `resource_filename`-only `pkg_resources` stand-in in
their own scratch directory; the IRescue identity check compares every BED row to the roster and
`15_irescue_chrcat.py` names `gawk` as the absent system tool; a `ModuleNotFoundError` outside the checkouts is
unsupported and every other import failure fails, with a self-test in the inventory check; deterministic gzip headers
and semantic `.locInd` comparison; versions read from the checkouts; the main BAMs carry raw `UR` one base from `UB`
on two copies (11 molecules by `UB`, 12 by `UR`), reverse-strand reads on both minus-strand records and one
duplicate-flagged and one QC-fail-flagged molecule; contract rows corrected. Orchestrator re-verification:
`consumers` 7 pass, 5 unsupported (Stellarscope defect, `gawk`, `irescue`, `featureCounts`, `duckdb`), exit 0; core 13
pass; an independent pysam recount over all eleven BAMs reproduces every alignment, template, molecule-by-tag and
flagged-read entry in `expected.json`; two fixture builds into fresh roots agree byte-for-byte on 51 of 53 files, the
two TElocal pickles differing only in the embedded GTF path; six checkouts clean at their clone commits; one stale
bytecode cache from the first round removed. Support matrix: parsers supported for IRescue identity, TEsingle,
TEtranscripts, TElocal and the MATES adapter; Stellarscope exercised to its defect; executables `irescue`,
`featureCounts`, `stellarscope`, `TEsingle`, `TEcount`, `TElocal`, `duckdb`, `gawk` absent in-container.

**Milestone 5 review** (after phase 5, commit `9ac66fb`) is complete and committed. Three parallel read-only
reviewers: codex on the consumer seam (`reviews/m5_codex.md`, BLOCKING: the registration carried five spellings and
matched none of the keys TEsingle, TElocal and a Stellarscope instance run emit on 1,000 sampled rows per export; three
advisories on split-piece uniqueness, the hardcoded namespace, universe and variant with an inventory writer that
replaces the file, and the manifest's export contracts), Opus on numbers and fixtures (`reviews/m5_opus.md`, PASS WITH
ADVISORIES; every phase 3 to 5 number re-derived by an independent route, the seven export digests reproduced from an
independent byte stream, thirteen mutations and two resolver probes each failing their check; seven advisories) and
divergent on assumptions (`reviews/m5_divergent.md`, 4 High, 8 Medium, 5 Low). Rulings in `reviews/m5_rulings.md`.
Divergent H1 (the compat universe short by 1,235 `LFSINE_Vert` records) was rejected on its premise: the directory it
measured was the audit's changed-policy experiment of the legacy release mechanics (`6ff3ee9-dirty`, prefix `tRNA-`),
which the orchestrator moved to `_scratch/te-tracks-audit/legacy_release_experiments/`; the legacy rule is `^tRNA` and
the compat count 3,799,629 stands. Fix `te-tracks-m5-fix` from `prompts/m5_fix.md` (fifteen items):
`export_feature_members` gains `key_grammar` and eight rows per record (`rmsk_record_id`, `record_alias` and
`four_tuple` at `record`; `rmsk_name` and `four_tuple` at `subfamily`; `family_bucket`; `taxonomy_triple`;
`instance_alias` at the new `instance` level), 30,119,592 rows over 3,152,636 instances, 255 MB; check 41 asserts the
eight slots and composes every GTF row's tuple and instance id for its joins; the 40 fixture rows hand-authored; every
consumer parser check joins its keys to the fixture registration; a family and triple reader check; `git describe` in
every support line; EM fixed-point assertions; the always-supported consumer checks renamed `.required`; contract
sentences on matrix binding, allocation, the clipped score, the single barcode, the fixture-only MATES pair and which
check proves what; README paragraphs current. Orchestrator re-verification: an independent regeneration of the
registration from the phase 2 and 3 tables reproduces its content digest; `exports.tsv` byte-identical; the 40 fixture
rows derived independently from the expected exports; core 13 pass; consumers 8 pass and 5 unsupported, exit 0;
checkouts clean. Export writer peak RSS 5.7 GB. Rulings the owner may overturn: the `all_rmsk` record BED for 14761's
ATAC route in phase 6 (divergent H2, widens ADR 3's export matrix) and the `key_grammar` column (H4).

**Phase 6** (contig namespaces, aliases, coverage, preflight, the `all_rmsk` record BED) is complete and committed on
the branch. Loop: implemented by codex (`te-tracks-p6-impl`, 2,008 s) from `prompts/p6_impl.md`; the implementer
reported three deviations instead of editing expectations (the two zero-interspersed contigs hold 2 and 4 catalog
records; the interspersed exports name 59 of 61 contigs so the literal preflight exits 2 for `gencode`; the export
fixture declared no `all_rmsk`). Codex review `reviews/p6_codex.md` (BLOCKING: those three plus a split builder entry,
`build_exports()` writing the interspersed set while `main()` wrote both universes; three advisories) and Opus re-review
`reviews/p6_opus.md` (FAIL: the same, four README rows claiming `tested` against failing checks; seven advisories, among
them the `ucsc` `family.bed` ordered by the invisible `rmsk_name` behind check 61's exception, preflight resolving
symlinks before locating the alias table, and check 61 sampling 0.27 % of rows). Rulings in `reviews/p6_rulings.md`:
milestone 2 ruling M1 amended to the counting-gate contract (exit 0 when every export contig is present at an agreeing
length, reference-only contigs informational, exit 2 for export contigs the reference lacks, exit 1 for a length
disagreement, an empty intersection or an unreadable input); every export in every namespace sorted by contig bytes,
numeric bounds, strand and its own name column; one builder entry `build_exports(build_dir, genome, jobs=EXPORT_JOBS)`;
check 42's fixture gains the third universe, six hand-authored catalog BED rows and 46 registration rows; check 60 pins
its FASTA fixture by digest; check 61 regenerates all sixteen renamed files; check 62 runs 82 cases over both universes,
three namespaces, three readers and three reference kinds; ADR 3 names GTF at record and subfamily level and the
`all_rmsk` record BED. Fix `te-tracks-p6-fix` from `prompts/p6_fix.md` (17 items). Orchestrator verification before and
after the fix: 24 inventory digests and row counts recomputed; the interspersed registration digest equals the milestone
5 value (`314098c5…`) with the 5,320,771 `all_rmsk` rows contiguous after it, one per record with the parquet bounds;
the three `all_rmsk` BEDs regenerated from the parquet byte-identically under either tiebreak; every renamed file equal
to its UCSC source as a row multiset after mapping the contig back, and sorted by the documented keys; the fixture's six
catalog rows and six registration rows derived independently; preflight reads the alias table of the root named on the
command line (symlink case); nine consumer checkouts clean; reflog at `c2a7a43`. Exports measure 3,021,714,346 /
2,926,266,953 / 3,021,140,740 bytes per namespace as sums of regular file sizes and the registration 347,526,106 bytes; one build is 10,461,884,289
bytes over 43 payload files before the child family. Stage 30 peaks at 5,891,116 KiB resident and stage 35 at 3,853,776 KiB (per-stage `RUSAGE_CHILDREN`, this container, 200 s and 100 s); a rebuild of stages 30 and 35 reproduced all 24 inventory digests and the registration digest `0726aa7b…`; `tests/run.sh core` 16 pass, `tests/run.sh consumers` 8 pass and 5 unsupported, both exit 0. Only the `ucsc` `family.bed` digest changed in the fix (4 rows at 3 coordinate
ties); the seven other UCSC interspersed digests equal the phase 4 inventory.

**Phase 7 and milestone 7** (identity and publication) are complete and committed: `9d16506` "Phase 7:
identity and publication" and `8589873` "Milestone 7: identity hardening after the publication review".
`MANIFEST.json` carries `identity` and `provenance`; `BUILD_ID` hashes the identity and `CATALOG_ID` the
catalog (the `rmsk_out` source, run identity, instance scope and the decompressed canonical text tables);
`99_verify.py` judges an archive against its own declaration and published version sets; `release.py`
installs into `archive/<BUILD_ID>/` under a lock and selects the relative `current`; `build.sh --root`
builds in staging and publishes. Reviews: `reviews/p7_codex.md` (BLOCKING), `p7_opus.md` (FAIL),
`m7_codex.md`, `m7_opus.md` (PASS WITH ADVISORIES), `m7_divergent.md` (5 High); rulings in
`reviews/p7_rulings.md` and `m7_rulings.md`. Scratch identities at `8589873`: `BUILD_ID`
`9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d`, `CATALOG_ID`
`90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e`; the 43 payload files are unchanged
since phase 6. Core suite 19 checks (about 13 min), consumers 13 checks (8 pass, 5 unsupported).

## Next session starts here

1. **Pick up here.** Three things were running when the 2026-09-16 session closed; each leaves its result on
   disk, so collect them first:
   - the scratch republish from the clean tree (`_scratch/te-tracks-audit/p7_verify/republish_clean.log`; expect
     `verify-current exit=0`, `builder_git_sha` `8589873…`, `dirty False`, and the same `BUILD_ID` as above). If the
     log is incomplete, reset `$TE_TRACKS_REFROOT/pubroot` (restore write modes first) and run
     `./build.sh --genome mm39 --root "$TE_TRACKS_REFROOT/pubroot"` again (about 12 min);
   - the codex field-practice consult (unit `te-tracks-field-consult`, prompt `prompts/field_consult.md`, output
     `consults/field_practice_consult.md`; `status.sh --unit te-tracks-field-consult` shows `codex_exit`);
   - the bioinf and divergent field reviews (`reviews/field_bioinf.md`, `reviews/field_divergent.md`, from
     `prompts/field_bioinf.md` and `field_divergent.md`).
   Then: write `consults/field_practice_synthesis.md` (what the field does at each rung, which counting it uses, what
   te-tracks adds or leaves to consumers, with the owner's questions from `consults/thesis_2023_excerpts.md`
   answered one by one) and amend `consults/gene_context_adr_brief.md` with the consult's recommendations; hold the
   ADR discussion with the owner on the brief's six candidate decisions plus the field recommendations (the owner
   asked for this discussion, 2026-09-16); record the rulings in `docs/DECISIONS.md` only by the owner's word;
   rewrite plan `18_phase8_gene_child_seam.md` from the rulings and the two consults; write `prompts/p8_impl.md`
   aligned with `reviews/{m5,p6,p7,m7}_rulings.md` (family and assembly separate, `GENOME=mm39` with
   `FAMILY=te_mm39_gene`, parent pinned by full `BUILD_ID`, child `.staging`, alias table copied by digest, explicit
   variant in exporter and registration, the GTF as a child source role outside `catalog.sources`, verifier branch
   for non-null parents). Commit the synthesis and brief as records before the discussion.
2. Phases 8 and 9 with `p8_impl.md` and `p9_impl.md`, each aligned with the rulings in its plan file before launch;
   phase 8 opens with a codex design consult on the child family's topology, architecture and approach, recorded under
   `redesign-2026-09/consults/` and ruled by the owner before `p8_impl.md` is finalized (owner, 2026-09-16); the
   orchestrator gathers the gene-context material (consult, D2 ledger needs, the lab's combined-mode counting,
   divergent H3) and then holds an ADR discussion with the owner on the transcript-context relation and
   `gene_context` before any child implementation (owner, 2026-09-16, second instruction); milestone review after 9; the owner runs the host build at phase 9 (`docs/RUNBOOK.md`; host floor 6 GB resident,
   10.5 GB disk per build), the orchestrator verifies the published bytes and records `BUILD_ID` and `CATALOG_ID`
   here; then the umbrella pin bumps and D2/D3 resume.

Prompts p5 to p9 carry pre-measured acceptance numbers; the plan files are authoritative where a prompt and a plan
file disagree, and the disagreement is a deviation to report. Rulings the owner may overturn: instance weighting
(`p3_rulings.md` H1), `CATALOG_ID` (`m2_rulings.md` H5), `subfamily.gtf` (H2), compat as membership (H1),
`gene_context` deferred (H3), pandas as the in-container conservation proof (`p4_rulings.md` B1).

## Open at handoff

- Gene context: the owner's ADR discussion has not been held; `consults/gene_context_adr_brief.md` lists six
  candidate decisions (one gene family with immutable snapshots; all-exon unstranded mask; sparse relation plus
  per-record status with context `not_computed` in phase 8; transcript and gene-body geometry with an explicit
  promoter window; consumers derive labels from published geometry; alias table copied into the child) and the
  point only the owner settles for each.
- Field practice: the codex consult and two reviews were running at handoff (see item 1 above); their synthesis
  joins the brief.
- Rulings the owner may overturn (recorded where made): instance weighting; `CATALOG_ID` scope (`rmsk_out` alone,
  decompressed text tables, `p7_rulings.md` Opus A2 and `m7_rulings.md` divergent H3); reader labels outside the
  identity (`m7_rulings.md` divergent H2); `subfamily.gtf`; compat as membership; `gene_context` deferred; pandas
  conservation proof; `all_rmsk` record BED; `key_grammar`; preflight gate; the payload roster at authoring.
- Phase 9 items collected in plan 19 (host modes and retention policy, clean-revision gate, id-mismatch remedy,
  the 14761 ledger's `te_catalog_id` and `te_build_id` columns as a consumer gate, acceptance checks and the
  runner's exit 2 for an empty mode); the compat oracle is the packaged `GRCm39_Ensembl_rmsk_TE.gtf.gz`.
- Unverified inputs for the gene-context decision: the nf-core "filtered" GTF recipe of the cGAS gene pass, the GTF
  inside the 10x cellranger-arc reference used by 14761, and whether either equals GENCODE vM37.

- Consumer executables absent in-container; phase 5 reports them `unsupported` until the owner decides
  installation (irescue, featureCounts, Stellarscope, TEsingle, TEtranscripts, TElocal).
- TElocal prepackaged annotation tables (Dropbox) not fetched; reconciliation belongs to the
  `compat_tetranscripts_mm39` fixture.
- Gene context stays a seam (phase 8); its design session follows.
- Deferred and recorded: hg38, ERV units, young/old tiers.

## Orchestration mechanics (for the next session)

- Environment: `TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`,
  `TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source`, `PYTHONDONTWRITEBYTECODE=1`;
  the build at `$TE_TRACKS_REFROOT/te_mm39/build`, the published root at `$TE_TRACKS_REFROOT/pubroot`; the
  orchestrator's verification scripts and logs under `_scratch/te-tracks-audit/p7_verify/` (`verify_c.sh` is the
  current template). `/tmp` is noexec; scratch lives under `_scratch/te-tracks-audit/`.
- Delegation: `.claude/skills/delegate-cli/assets/launch.sh --unit U --workdir <te-tracks> --effort xhigh
  [--parallel-ok] --prompt <file>` as a harness background task; the launcher's exit 32 is a blind-run false
  positive on every unit, so read `codex_exit` from `status.sh --unit U` and the report from
  `/tmp/scio-delegate/U/<run>/final.md`. Opus and divergent reviewers run as harness agents; a truncated Opus
  report is recovered from the longest `Verdict:`-bearing string in the agent's transcript under
  `~/.claude/projects/*/*.jsonl`. Reviewer prompts set `PYTHONDONTWRITEBYTECODE=1` and name the checkouts under
  `01_modules/.ref/` explicitly (DfamTEBrowser, irescue, mascarade, MATES, mLLMCelltype, scTE, scTEfinder,
  stellarscope, TElocal, TEsingle, TEsingle_benchmarking_scripts, TEsingle_Martirosyan_analysis_code, TEtranscripts,
  Thesis_2023; `14839-DM-cGAS` and `sene/` are the owner's plain directories).
- Protocol: `plans/2026-09-16_te-tracks-redesign/02_orchestration.md` (loop, standing authorizations, milestone
  reviews, umbrella pin bumps); package files change only through codex units, records and prompts under
  `docs/_internal/` are the orchestrator's; commits on `redesign-2026-09` without push; no AI attribution in
  commit messages; prose affirmative, comments state intent.
