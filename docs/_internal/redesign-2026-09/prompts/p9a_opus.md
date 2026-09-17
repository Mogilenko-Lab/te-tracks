Re-review phase 9a of the te-tracks redesign. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(git branch redesign-2026-09). You are read-only: no edits, no git writes, no installs, no network.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/19_phase9_acceptance_park.md (the contract)
2. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md
3. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments" (wording rules for public files)
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short` and
   `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD` (plus untracked files' contents)
5. The codex review already written: docs/_internal/redesign-2026-09/reviews/p9a_codex.md

Your job is adversarial and independent of the codex review: recompute every acceptance number in the
contract with your own read-only shell or python (working copies under /tmp only), try to make each check
fail, look for what the implementer assumed silently, and judge the public prose against the wording rules.
Where you agree with a codex finding say so in one line; where you disagree, show the evidence.


## Phase 9a specifics

The contract is plan 19's section "Phase 9a: core additions before acceptance" plus the implementer prompt
`docs/_internal/redesign-2026-09/prompts/p9a_impl.md`. A codex review is running in parallel and its file
may not exist yet; do not wait for it and do not read it if it appears mid-run, so that your findings are
independent. Skip step 5 of the list above.

Environment: export `TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`,
`TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source` and
`PYTHONDONTWRITEBYTECODE=1`. `/tmp` is noexec on this host, so put working copies under
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/p9a-opus/` instead and remove that directory with Python
`shutil.rmtree` before you finish. Do not rebuild and do not publish; the existing builds under the
reference root are the reviewed artifact. Never run a git write; the checkouts under
`/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too. `14839-DM-cGAS` and `sene/` under
`.ref` are the owner's own directories: read the first if useful and leave both alone.

Recompute these, each with your own code rather than by reading a check's output.

| quantity | contract |
|---|---|
| `record_starsolo.gtf` rows and distinct `gene_id`, each of three namespaces | 3,764,949 and 3,764,949 |
| its contigs, feature type, attribute count and order | 59, `exon`, twelve in the order `gene_id`, `transcript_id`, `gene_name`, `gene_type`, `locus`, `rmsk_name`, `family_id`, `class_id`, `rmsk_family`, `rmsk_class`, `instance_id`, `rmsk_record_id` |
| its bytes, ucsc / ensembl / gencode | 1,616,329,134 / 1,604,983,782 / 1,616,260,404 |
| `taxonomy_dfam.tsv` lines | 1,221 |
| names exact / part_model_set / missing | 1,047 / 147 / 26 |
| records under those | 2,797,852 / 928,528 / 38,569 |
| part sets with three / two / one models; L2-CR1 sets | 30 / 9 / 108; 6 |
| model rows; nodes; nodes carrying a Wicker code | 1,263; 300; 193 |
| multi-clade models; primate-branch models and names | 9; 33 and 31 |
| exact names with a Wicker code mapped / inherited / missing | 884 / 110 / 53 |
| companion table lines, models / nodes / clades | 1,264 / 301 / 1,279 |
| core `BUILD_ID` | `763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c` |
| child `BUILD_ID` | `693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0` |
| `CATALOG_ID`, core and child | `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` |
| new core inventory entries and export contracts | 51 and 27 |
| phase-8 core archive inventory entries and contracts | 43 and 24, and it must still verify |
| snapshot sha256 | `ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f` |
| binding fixture, pair-only join then four-field join | 2,000 rows and 1,001,000 counts, then 1,000 rows and 500,500 counts |
| records section: multi-record instances, LTR-only, mixed-name, mixed-strand, overlapping, L1 at base 1 | 445,649 and 722,280 under `all_rmsk`; 30,569 and 23,244 under `interspersed`; 8.07%; 588 |
| suites: core, then consumers with the shims | 26 of 26; 16 checks, 15 pass, 1 unsupported |

Then attack these six seams, which is where the value of this pass lies.

1. **Can the record profile disagree with the catalog without a check failing?** The profile is 4.8 GB over
   three namespaces. Establish whether rows, coordinates, strand and identity are bound to
   `rmsk_records.parquet` and to the registration as a multiset, or only counted.
2. **Can the Dfam view drift from the snapshot without a check failing?** Compare per name, not in
   aggregate. The snapshot is Dfam 4.0 while the RepeatMasker run used a 2018 library, so the join is over
   names that may have moved; judge whether every drift outcome has an explicit status and whether
   `model_length_sum_bp` is anywhere used or documented as a full-length denominator, which it must not be.
3. **Does the tracked source role weaken the verifier?** `dfam_snapshot` enters `identity.build_sources` as
   a package file with its sha256, outside the fetched set and outside `catalog.sources`. The phase-8
   archive declares three roles and the new one five. Find an input that now slips past the verifier, or
   state that none does and show how you established it.
4. **Do the new checks fail when they should?** Mutate a copy of the build or the fixtures under your
   scratch directory and confirm `33_taxonomy_dfam_view.py`, `34_dfam_rule_fixtures.py`,
   `43_matrix_binding.py` and `17_starsolo_profile.required.py` each refuse. Name any that passes a
   mutation it should catch.
5. **The IRescue rewrite.** It must assert identity joins, roster and molecule conservation and unique
   molecules on their feature, and record the ambiguous allocation without asserting it. Observed are 5.5
   and 3.5 for the 4/2/3 fixture and 4.5 and 4.5 for the 3/3 fixture. Confirm it still fails if identity or
   conservation breaks.
6. **Public prose.** `docs/DECISIONS.md`, `docs/OUTPUTS.md`, `docs/RELEASES.md`, `docs/RUNBOOK.md` and
   `README.md` changed. Judge them against the wording rules and against the bytes: any sentence that
   describes a file, a count or a capability that the build does not have is a blocking finding.

Rule on the implementer's own reported deviations, with evidence for each:
D1 every Wicker rank is `missing` for the 53 exact `Unknown` names, following plan 19 rather than the
prompt's general leaf-family rule.
D2 three source roles in the phase-8 archive against five in the new one, with the earlier archive still
verifying.
D3 the fetch census totals 3,760,582 records against the catalog's 3,764,949, short by 4,367 across the 20
multi-label names; the builder takes weights from the catalog.
D4 the plan's instance figures are reported under explicit `all_rmsk` or `interspersed` scopes.
D5 `17_starsolo_profile.required.py` was added though the enumerated touch list omitted it.
D6 `src/lib/contigs.py:134` still says "eight UCSC inventory entries" while the roster holds nine; the file
is outside the touch list.
D7 a live edit to `tests/run.sh` during an intermediate run produced `exit=127`; the frozen run and the
orchestrator's independent re-run both passed 26 of 26.
D8 `cellranger mkref` needs `--memgb=3`.

The working tree holds 38 `git status --short` entries plus three files under `data/`. Name anything touched
outside plan 19's phase 9a scope.

## Delivering your report

Write your complete report to
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/opus-p9a-report.md` before you finish, because your final
message is truncated in transit. That path is outside every git repository. Then give a short summary in
your final message: the verdict, the count of blocking and advisory findings, and the one-line title of each
blocking finding.


Report as:
# Phase 9a re-review (Opus)
Verdict: PASS | PASS WITH ADVISORIES | FAIL
## Blocking
- [B1] path:line — finding — evidence — fix
## Advisory
- [A1] ...
## Numbers recomputed
<table: quantity | contract | observed | command>
## Agreement with codex review
<one line per codex finding: agree / disagree with evidence>
Under 150 lines. FAIL when a contract deliverable is missing or wrong, an acceptance number differs, or a
check cannot fail.
