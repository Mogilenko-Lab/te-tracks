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

**Field practice** (owner's question of 2026-09-16, answered the same day): the codex consult
`redesign-2026-09/consults/field_practice_consult.md` (gpt-6-astra, eight questions, measurements M0 to M5),
the bioinf review `reviews/field_bioinf.md` (verdict: sound, documentation amendments) and the divergent review
`reviews/field_divergent.md` (7 High) were collected; every measured claim was recomputed by the orchestrator
and ruled in `reviews/field_rulings.md`; `consults/field_practice_synthesis.md` answers the owner's questions
rung by rung and `consults/gene_context_adr_brief.md` now carries eleven candidate decisions (C1 to C6 amended,
C7 to C11 added). Dataset facts from the BAM headers: 14616 and 14782 share `Single Cell 5' PE OCM v3` and
`refdata-cellranger-GRCm39-2024-A` with fully paired BAMs; 14761 used `refdata-cellranger-arc-GRCm39-2024-A`
with a single-end GEX BAM; all cellranger BAMs keep one alignment per read, so EM routes need a STARsolo
re-alignment. TEsingle 1.0 appends paired mates as alternative alignments with opposite strands
(`tesingle_notes.md`, corrections section). The scratch republish from the clean tree verified with exit 0:
`BUILD_ID 9ddf3622…`, `builder_git_sha 6bf9a22`, `dirty False`.

**ADR discussion, first round** (2026-09-17): the owner ruled C1, C3, C5 (option A), C6, C7, C9 and C10 and asked
for measurement and consultation on C2, C4, C8 and C11; the rulings and the owner's words are in
`redesign-2026-09/consults/adr_rulings_2026-09-17.md`. Three codex consults were launched against `9c27b14` with
`--parallel-ok`: `te-tracks-mask-consult` (`prompts/mask_consult.md` → `consults/mask_policy_consult.md`),
`te-tracks-loci-consult` (`prompts/loci_consult.md` → `consults/loci_gtf_consult.md`) and
`te-tracks-structure-consult` (`prompts/structure_consult.md` → `consults/structural_views_consult.md`). The 10x
GRCm39-2024-A gene GTF was extracted from the owner's download to
`_scratch/te-tracks-audit/refs/refdata-gex-GRCm39-2024-A/genes/genes.gtf.gz` (GENCODE vM33 filtered, 33,696 genes,
834,423 exon rows, md5 `7a998f670d6d0bdf599c046284da051b`; contigs `chr`-named, 61). A Dfam census of the 1,220
interspersed names against the live API (Dfam 4.0, May 2026) is complete: 1,047 exact hits; 143 of the 173 misses
are L1 names that Dfam models as `_5end`, `_orf2` and `_3end` parts; summary in `consults/adr_rulings_2026-09-17.md`,
file at `redesign-2026-09/taxonomy/dfam_census_1220_20260917.tsv`.

**Consults collected** (2026-09-17, later): all three units succeeded; every number the orchestrator rechecked
reproduces (mask census by bedtools for both GTFs, instance union, LTR adjacency, divergence bins, chr1 body pairs,
STARsolo GTF size arithmetic, contig dictionary, registration counts). Results and recommendations are in
`consults/adr_rulings_2026-09-17.md`; two corrections landed in the synthesis and the TEsingle notes (STAR anchors
100/200 in the scripts; TEsingle collapses identical four-tuples).

**ADR discussion, third round** (2026-09-17, later): the owner ruled C4 (10 kb upstream, 2 kb downstream; `mRNA_start_NF`
and `Ensembl_canonical` flags), C11 (geometry only, after the host build, batched; the child family serves the 10x vM33
filtered annotation and vM37 alike, so item 3 is two snapshots with vM37 first), C7 details (100/200 with saturation, 500
as sensitivity, forks in the consuming toolkit, three tiers; alignment parameters are the consumer's), the executables
(a venv without conda, now prepared), the IRescue oracle (outside te-tracks' responsibility; the binary returns 5.5/3.5
and check 20 fails until phase 9 rewrites it to conservation and identity), Stellarscope (downstream; no fork), C10
details (lineage as truth, named rank scheme with per-rank status, interspersed first; Wicker's names recommended and
awaiting the owner's word), a new documentation ruling on records, instances and insertions, 18439-DM out of scope, and
the umbrella pin at milestone 9. Answers and evidence in `consults/adr_rulings_2026-09-17.md` (third round),
`taxonomy/dfam_classes_20260917.json`, and `consults/open_questions_premises_2026-09-17.md`. Consumer environment:
`/workspaces/Meta-Aging/.venv/te-consumers` from `redesign-2026-09/env/consumers/bootstrap.sh` (STAR 2.7.11b, subread
2.1.1, gawk, cellranger 10.1.0, the five Python tools at the fixture checkouts' commits, duckdb in the base venv); with
`source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh` the consumers suite runs 11 pass, 1 unsupported, 1 fail
(IRescue allocation); without it 8 pass and 5 unsupported. The decisions unit `te-tracks-decisions`
(`prompts/decisions.md`) writes the ruled entries into `docs/DECISIONS.md`.

**Fourth round and launches** (2026-09-17, later): the owner ruled the packaging module at
`/workspaces/Meta-Aging/01_modules/te-consumers/` (untracked in the umbrella; environment stays under `.venv/`), Dfam
admitted now as a phase 9a core view (offline snapshot fetched; `redesign-2026-09/taxonomy/`), Wicker's rank names, and asked
for the unified-schema and reconstruction consult (`prompts/schema_consult.md`). Plan 18 was rewritten and `prompts/p8_impl.md`
written from the rulings; plan 19 gained "Phase 9a: core additions before acceptance". `docs/DECISIONS.md` carries the ruled
entries (sections 4, 8 to 15, deferrals) from unit `te-tracks-decisions`, verified and committed. Launched: `te-tracks-p8-impl`
(package files, builds the child into `$TE_TRACKS_REFROOT/te_mm39_gene/build` and publishes it into the scratch pubroot) and
`te-tracks-schema-consult` (one consult file). The IRescue execution check fails by design until phase 9a rewrites it.

**Phase 8 in progress and the schema consult running** (2026-09-17, at compaction): `te-tracks-p8-impl` (run
`20260917T150935Z`, gpt-6-astra xhigh) had built the child into `$TE_TRACKS_REFROOT/te_mm39_gene/build`, verified it with the
parent resolved (child `BUILD_ID 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b`; `CATALOG_ID` bytes equal to
the parent's `90cc18be…`), published it into the scratch root (`$TE_TRACKS_REFROOT/pubroot/te_mm39_gene/`, same identity as the
scratch build) and was running the tail of its acceptance commands; its package changes sit uncommitted in the tree (`build.sh`,
`src/90_manifest.py`, `src/99_verify.py`, `src/lib/manifest.py`, `src/release.py`, `tests/fixtures/publication/build_fixture.py`
modified; new `config/mm39_gene.env`, `src/gene/`, `src/lib/gene_child.py`, `tests/checks/core/80_…83_…`,
`tests/expectations/mm39/exon_subtraction_summary.tsv`, `tests/fixtures/gene/`; docs and README edits expected). Nothing of it
is verified by the orchestrator yet. `te-tracks-schema-consult` (run `20260917T152435Z`) is the relaunch after a first run ended
with the server's "Selected model is at capacity" refusal and no output; it writes `consults/unified_te_schema_consult.md`.
Commits since the third round: `829e0ad` (decisions record), `cea3756` (plan 18 rewrite, `prompts/p8_impl.md`,
`prompts/schema_consult.md`, plan 19 phase 9a, fourth-round record), `bb8fcbe` (Dfam snapshot), `940da67` (prompt note).

**Phase 8 fixed and verified, commit pending; schema consult landed; phase 9a prompt written** (2026-09-17, later).
`te-tracks-p8-impl` finished (codex exit 0, 3,011 s); the orchestrator re-verified every plan 18 number on disk, cross-checked
chr19 with bedtools (identical block sets) and ran the core suite (23 pass). Codex review `reviews/p8_codex.md`: BLOCKING (B1 SAF
content unbound from the registration beyond count and digest; B2 trailing slash bypasses the symlinked-parent refusal; A1
hardcoded scratch path; A2 shared mask code; A3 phase 9 constraints). Opus re-review `reviews/p8_opus.md`: FAIL on the same two
bindings plus the three geometry cases the amended plan 18 requires, advisories A1 to A7. `reviews/p8_rulings.md` accepts all of
it. Fix unit `te-tracks-p8-fix` (run `20260917T164350Z-3711107`, codex exit 0, 1,765 s) implemented the seven items of
`prompts/p8_fix.md` in twelve files; orchestrator verification (recorded in the rulings): verifier exit 0 with the new `ok child SAF
rows` line, 159 s, peak 3,493,396,480 bytes; builds and published root byte-untouched (140 files); both symlink spellings exit 2;
fixture coverage row recomputed; scratch through `$TE_TRACKS_REFROOT/pubtest`; `.ref` clean; reflog `cf1b150`. The orchestrator's
own `tests/run.sh core` re-run after the fix passed (23 pass, 15 min 14 s; `pubtest` empty, no `p8impl/`). The orchestrator's records
(plans 18 and 19 amended, the fifth round, the schema consult, the p8 prompts, reviews and rulings, `prompts/p9a_impl.md`, this
record) are committed as `4b117f2`; the phase 8 implementation with its fix is committed as `393ca76` ("Phase 8: the gene child family, first
snapshot"). The schema consult
landed as `consults/unified_te_schema_consult.md` (328 lines); its measurements were recomputed by the orchestrator (all equal; the
census TSV's 4,367-record shortfall sits on the 20 multi-label names) and the fifth round is recorded in
`consults/adr_rulings_2026-09-17.md`; plan 19's Dfam bullet is corrected (147 part sets and 26 missing; partial sets with
`available_part_count`; every clade kept with `clade_compatibility`; three normalized companion tables) and carries the phase 8
review constraints and a bedtools acceptance oracle for 9b. `prompts/p9a_impl.md` (263 lines) is written from plan 19 as amended
and launches after the phase 8 commit with `__HEAD__` replaced by that commit.

**Phase 9a implemented, reviewed twice, fix running; parking is now the goal** (2026-09-17, later).
The owner ruled: te-tracks is parked in a state supporting the discussed inference for the three single-cell and
single-nucleus datasets and the out-of-scope bulk RNA-seq dataset; contrasts leave the critical path and the multiome
schema becomes the primary question; codex `gpt-6-astra` implements, Opus reviews each implementation and codex reviews
each major seam; a final pass then cleans fixtures, laconicizes comments and distills `README.md`, followed by a codex
fan-out validating every claim against the real repository outputs. `gpt-6-astra-pro` and `gpt-6-pro` are refused by this
account, so implementers stay on `gpt-6-astra` at xhigh. Sixth-round rulings and the three technical answers (the
RepeatMasker-Dfam release split, one STARsolo alignment feeding every consumer, the consensus-space route of McKerrow et
al. with its measured mask reproduction) are in `consults/adr_rulings_2026-09-17.md`; the post-phase-8 lay-out of biology,
premises and routes is `consults/open_questions_premises_after_phase8_2026-09-17.md`.
`te-tracks-p9a-impl` finished (codex exit 0, 9,872 s, 40 files). Orchestrator verification before the reviews: core 26 of
26 on the frozen tree, consumers 15 pass and 1 unsupported with the shims, each `record_starsolo.gtf` parsed row by row
at 3,764,949 rows and distinct `gene_id`s over 59 contigs with the twelve attributes in order, the Dfam strict part rule
recomputed from the snapshot agreeing with all 1,220 published rows, 51 inventory entries and 27 contracts, five
`build_sources` roles with `catalog.sources` still `['rmsk_out']`, core `BUILD_ID` `763815187e…`, child `693ba1aa15…`,
`CATALOG_ID` `90cc18be…` in both, the phase-8 archive verifying at exit 0, the child pinning the new parent with a
byte-identical summary. The two reviews ran in parallel and independently: `reviews/p9a_codex.md` BLOCKING on two checks
that pass mutations they should refuse (IRescue conservation defeated by `zip` truncation and `dict` overwrite; STARsolo
support permitted on a gene the fixture does not support), both reproduced by the orchestrator in the code;
`reviews/p9a_opus.md` PASS WITH ADVISORIES with one blocking documentation clause (`UCON4` is class-less and still
inherits a Wicker code, so the missing-rank claim belonged to the 53 `Unknown`-leaf names) and nine advisories, the
largest being that nine of ten derived rank columns can drift with check 33 still passing. `reviews/p9a_rulings.md`
accepts every finding; `prompts/p9a_fix.md` carries eleven items and rebuilds and republishes because retaining the
snapshot provenance and recording `rank_scheme_wicker_v1` in the identity both move `BUILD_ID`.
The launcher's `result_exit=32` is explained: its blind-run guard greps the stream for `bwrap`, and the umbrella
`AGENTS.md` sentence about bwrap is echoed by every codex run in this repository. Reported to the owner, unedited, because
the guard belongs to the scio toolkit.


## Next session starts here

1. **Pick up here: the phase 9a fix has landed and is reviewed; commit it, then run 9b.** The fix unit
   `te-tracks-p9a-fix` implemented all eleven items of `prompts/p9a_fix.md` in 15 files and republished both
   families: core `BUILD_ID` `5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813`, child
   `198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1`, `CATALOG_ID` unchanged at
   `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` in both, payload roster 52 entries and
   15,301,538,537 bytes, `rank_scheme_wicker_v1` now recorded in `identity` and inherited by the child, three
   archives per family with `current` on the new builds. The orchestrator verified the identity, the archives,
   the retained provenance and both new guards by reading them: the IRescue guard binds matrix shape to both
   rosters, feature-name uniqueness and total mass before any dictionary exists, with the expected total
   derived from the fixture's own molecules; the STARsolo guard derives each case's allowed gene set from the
   combined GTF against the fixture's molecule coordinates. `opus-p9a-fix` reports PASS WITH ADVISORIES, zero
   blocking, five advisory, all eleven items biting under 64 mutations of which 57 refused by name, ids
   recomputed independently, all six archives verifying. Read its final report at
   `_scratch/te-tracks-audit/opus-p9a-fix-report.md`, copy it to `reviews/p9a_fix_opus.md`, rule the five
   advisories in `reviews/p9a_rulings.md`, re-run the suite cleanly with
   `TE_TRACKS_CONSUMER_FIXTURES` pointed at your own scratch, and commit the whole of phase 9a as
   "Phase 9a: core additions before acceptance". Then launch 9b from `prompts/p9b_impl.md` with `__HEAD__`
   replaced by that commit. Every later prompt is written and committed: `m9_seam_review.md`,
   `p10_cleanup.md`, `p11_validate_template.md`. Remaining sequence: 9b, its Opus review, the milestone 9
   seam review, the parking pass, the three-way claim validation, the owner's host build, the umbrella pin.
   Two facts measured for the runbook: Stellarscope's interval tree needs about 10.1 GB resident to load the
   full record profile and TElocal's index about 3.9 GB. Full-scale consumer validation passed: cellranger
   mkgtf accepted all 3,764,949 record rows, and featureCounts loaded the child SAF as 1,220 meta-features
   over 59 contigs. Do not run a suite concurrently with a mutation-testing reviewer against one reference
   root: the generated fixture directory is a fixed path under it.
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
`gene_context` deferred (H3), pandas as the in-container conservation proof (`p4_rulings.md` B1), the compat exon-subtracted pair as a published child view
(C1), the child's copied alias and universe inputs (C6), Wicker's rank names (round four).

## Open at handoff

- ADR discussion: every item of the twelve-item list is ruled (rounds one to four) and the schema consult's fifth round is
  recorded in `consults/adr_rulings_2026-09-17.md`: measurements recomputed and equal; plan 19's Dfam bullet corrected (147 part
  sets, 26 missing; partial sets with `available_part_count`; every clade kept with `clade_compatibility`; the companion tables
  `taxonomy_dfam_models.tsv`, `dfam_lineage_nodes.tsv` and `dfam_model_clades.tsv`, adopted by the orchestrator and overturnable).
  Awaiting the owner's word, the orchestrator's stance recorded beside each: the first contrast (Young_Control against
  Old_Control, discovery in the whole-cell RNA, spatial corroboration in the Multiome; agree), the D2/D3 row-level evidence
  vocabulary (`pairing_level`, `rna_attribution`, `spatial_scope`, `replication_tier`, `inference_source`; agree, 14761's
  discussion), reconstruction calibration (L1 prefix and completeness first, then ERV; agree), part-match scope (adopted), the
  projection tool (marimo with jscatter panels and an embedded genome-browser prototype over DuckDB and Parquet; agree, D2's
  decision). The owner has not yet read `docs/DECISIONS.md` as written (`829e0ad`); invite that reading. The owner asked for a second re-orientation after phase 8; the lay-out of the biology, fourteen premises and ten
  open questions with routes is `consults/open_questions_premises_after_phase8_2026-09-17.md`, the successor of the pre-phase-8 file. Pending design inputs:
  the ARC GTF verification for the 10x child; a TES-side window if the 3′ pilot needs it. The `te-consumers` directory and the
  cellranger tarball are untracked in the umbrella until the owner commits them or asks for a repository.
- Rulings the owner may overturn (recorded where made): instance weighting; `CATALOG_ID` scope (`rmsk_out` alone,
  decompressed text tables, `p7_rulings.md` Opus A2 and `m7_rulings.md` divergent H3); reader labels outside the
  identity (`m7_rulings.md` divergent H2); `subfamily.gtf`; compat as membership; `gene_context` deferred; pandas
  conservation proof; `all_rmsk` record BED; `key_grammar`; preflight gate; the payload roster at authoring.
- Phase 9 items collected in plan 19 (host modes and retention policy, clean-revision gate, id-mismatch remedy,
  the 14761 ledger's `te_catalog_id` and `te_build_id` columns as a consumer gate, acceptance checks and the
  runner's exit 2 for an empty mode); the compat oracle is the packaged `GRCm39_Ensembl_rmsk_TE.gtf.gz`.
- Unverified inputs for the gene-context decision: the GTF bytes inside `refdata-cellranger-GRCm39-2024-A` and
  `refdata-cellranger-arc-GRCm39-2024-A` (the GEX reference's metadata names GENCODE vM33 filtered, verified 2026-09-17 from the owner's download;
  the ARC reference is unverified), and the nf-core "filtered" GTF recipe of the cGAS gene pass.

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
- Consumer tools: `source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh` before `tests/run.sh consumers` (11 pass, 1
  unsupported, 1 fail on the IRescue allocation until phase 9a); recreate with
  `bash /workspaces/Meta-Aging/01_modules/te-consumers/env/bootstrap.sh` (sudo for duckdb into the root-owned base venv and
  for gawk; `TMPDIR` under the root because `/tmp` is noexec).
- Launching: one `launch.sh` per harness background task, never chained with `&` in one shell (a chained launch lost its
  variable scope and the second launcher never started). A run ending with "Selected model is at capacity" writes no
  `final.md` and is relaunched as is. `--parallel-ok` only for units with disjoint write scopes (an implementer and a read-only
  consult qualify).
- Dfam: the API is reachable from the container; the offline snapshot for builds is
  `redesign-2026-09/taxonomy/dfam_interspersed_mm39_snapshot.json.gz` (force-added past `*.gz`), fetched by
  `taxonomy/dfam_snapshot_fetch_20260917.py`; the classification tree with `wicker_equiv` per node is
  `taxonomy/dfam_classes_20260917.json`.
- Protocol: `plans/2026-09-16_te-tracks-redesign/02_orchestration.md` (loop, standing authorizations, milestone
  reviews, umbrella pin bumps); package files change only through codex units, records and prompts under
  `docs/_internal/` are the orchestrator's; commits on `redesign-2026-09` without push; no AI attribution in
  commit messages; prose affirmative, comments state intent.

**Learned this window.** Opus reviewer results arrive as teammate messages truncated near 4,000 characters; ask the agent by
name through SendMessage to write the full report to a file under `_scratch/te-tracks-audit/` and copy it into `reviews/`
(the agent is read-only inside repositories by contract). The delegate launcher's `result_exit=32` with `codex_exit=0` is a
false positive seen on every unit today; the final message is in `/tmp/scio-delegate/<unit>/<run>/final.md`. Parallel Bash
calls that `cd` move the persistent working directory; use absolute paths and `git -C`. A codex run that prints
`Reconnecting... 5/5` can still finish; judge a stall by the stream's mtime, and relaunch only when the launcher records a
failure without a final message.
