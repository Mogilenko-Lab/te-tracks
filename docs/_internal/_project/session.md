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

## Next session starts here

1. Phase 4: `launch.sh --unit te-tracks-p4-impl --workdir <te-tracks> --effort xhigh --prompt
   docs/_internal/redesign-2026-09/prompts/p4_impl.md` (aligned with milestone 2 and phase 3 rulings: seven exports
   including `subfamily.gtf`, registration keyed by level, `exports.tsv`, component alphabet without `/`, rank
   tokens, `/` rejected in names); verify (export stage on the existing build dir); codex review
   (`prompts/p4_review.md`, paste the implementer report) then Opus (`prompts/p4_opus.md`); fix loop; commit
   "Phase 4: interspersed exports in the UCSC namespace".
2. Phase 5 with `p5_impl.md` after aligning it with the rulings (TElocal index built by its own indexer; TEsingle grain
   fixtures from both GTFs); milestone review m5 (codex, Opus, divergent). Phases 6 to 9 follow; milestone reviews
   after 7 and 9; the owner runs the host build at phase 9 (`docs/RUNBOOK.md`), the orchestrator verifies the
   published bytes and records `BUILD_ID` and `CATALOG_ID` here; then the umbrella pin bumps and D2/D3 resume.

Prompts p4 to p9 carry pre-measured acceptance numbers; the plan files are authoritative where a prompt and a plan
file disagree, and the disagreement is a deviation to report. Rulings the owner may overturn: instance weighting
(`p3_rulings.md` H1), `CATALOG_ID` (`m2_rulings.md` H5), `subfamily.gtf` (H2), compat as membership (H1),
`gene_context` deferred (H3).

## Open at handoff

- Consumer executables absent in-container; phase 5 reports them `unsupported` until the owner decides
  installation (irescue, featureCounts, Stellarscope, TEsingle, TEtranscripts, TElocal).
- TElocal prepackaged annotation tables (Dropbox) not fetched; reconciliation belongs to the
  `compat_tetranscripts_mm39` fixture.
- Gene context stays a seam (phase 8); its design session follows.
- Deferred and recorded: hg38, ERV units, young/old tiers.
