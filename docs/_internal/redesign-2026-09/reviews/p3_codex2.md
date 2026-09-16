# Phase 3 fix re-review (codex gpt-6-astra)
Verdict: PASS WITH ADVISORIES

## Blocking

- None. The rebuilt artifacts, independent recomputation, census and requested mutation checks satisfy the current phase 3 acceptance contract.

## Advisory

- [A1] `tests/checks/core/31_taxonomy_dfam_agreement.py:56` retains the endpoint host, path and query as literals, despite `docs/_internal/redesign-2026-09/prompts/p3_fix.md:39` requiring the URL to come from evidence. Lines 67–70 also require a null release response and the exact deferral sentence. — A scratch provenance containing a retained response fails with `provenance release_endpoint_response`; count/date changes and concordant snapshot expansion work. The null matches today's pinned contract, but the promised refresh still requires check edits. — Read endpoint policy from provenance and schedule validation of retained release responses with the next refresh.
- [A2] `docs/OUTPUTS.md:287` gives `family.bed` a bare `unresolved_family_<name>` fallback, while `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md:8` substitutes tokens in each rank's position. — A family tie named `F` under DNA becomes `unresolved_family_F` under the public table and `DNA/unresolved_family_F` under the phase 4 contract; a class tie also needs both rank tokens. — Align the public BED row with positional substitution before phase 4, keeping the phase 3 rollup bucket convention explicit.
- [A3] `docs/OUTPUTS.md:198` promises separator-free unresolved tokens, while phase 4's component alphabet (`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md:28`) accepts `/` in names. `tests/checks/core/32_taxonomy_rule_fixtures.py:136` simply prefixes the name and tests only separator-free fixture names. — `A/B` passes that alphabet and produces `unresolved_family_A/B`; all 18,484 current names avoid `/`, `:` and `|`. — Define encoding or explicit rejection for separator-bearing unresolved names and add an export fixture before admitting such names.

Remaining fixed assumptions: `tests/checks/core/30_taxonomy_canonical.py:82` requires every multi-label class to be DNA; lines 89 and 101 select mm39 expectations and require a nonempty plurality subset. `tests/lib/records.py:13` selects `te_mm39/build`. These match this assembly's contract; another assembly needs explicit adaptation. The literal rule version in check 30:71 and check 32:24 intentionally pins v1. Phase 4's named `rmsk_name`, `canonical_class`, `canonical_family`, `class_status` and `family_status` columns are present and checked on every row; empty unresolved fields require substitution by status.

Wording: reviewed every added/changed sentence, docstring and comment in `src/`, `tests/`, `docs/OUTPUTS.md` and `README.md`; the prose and comments follow the affirmative, brief intent rule. README's absent `weighting_context.tsv` row is already scheduled in `docs/_internal/redesign-2026-09/prompts/p4_impl.md:92`.

## Rulings closed

- Codex B1: CLOSED — `src/lib/build_taxonomy.py:73` scopes the fallback to the winning class; `tests/fixtures/taxonomy/rule_cases.tsv:24` expects DNA/DNA, unspecified.
- Codex B2: CLOSED by recorded deferral — `tests/fixtures/taxonomy/dfam_snapshot.provenance.json:7` identifies per-family evidence and the pending release response; phase 3 contract:77 records the deferral.
- Codex B3: CLOSED by phase 7 deferral — `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md:75`; `src/lib/build_taxonomy.py:16` supplies the constant.
- Codex A1: CLOSED — `tests/checks/core/30_taxonomy_canonical.py:77` compares all 15 columns exactly; single-label corruption fails.
- Codex A2: CLOSED — `tests/checks/core/31_taxonomy_dfam_agreement.py:35` prints coverage lists before assertions; removing Eulor5B names it.
- Codex A3: CLOSED — phase 3 contract `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md:57` and :89 name the delivered module and check.
- Opus B1: CLOSED — `src/lib/build_taxonomy.py:73` and `docs/OUTPUTS.md:158` implement and document winning-class abstention.
- Opus B2: CLOSED — `tests/checks/core/30_taxonomy_canonical.py:77`; the altered B1_Mm family fails exact comparison.
- Opus B3: CLOSED — `tests/fixtures/taxonomy/dfam_snapshot.provenance.json:7` and `tests/checks/core/31_taxonomy_dfam_agreement.py:55` supply and validate all eight provenance keys.
- Opus A1: CLOSED — `src/lib/build_taxonomy.py:139` rounds medians to two decimals; independent stdlib medians match every name.
- Opus A2: CLOSED — `tests/checks/core/31_taxonomy_dfam_agreement.py:35` emits missing/extra lists before the row census assertion.
- Opus A3: CLOSED — `tests/fixtures/taxonomy/weighting_context.tsv:2` reverses the record/length winner; a caller-column swap fails check 32:109 on instance_weighting's canonical family, before rollups.
- Opus A4: CLOSED as the recorded choice — `docs/OUTPUTS.md:172` documents total typed-vote semantics; `src/lib/build_taxonomy.py:109` validates build inputs.
- Opus A5: CLOSED — `tests/checks/core/31_taxonomy_dfam_agreement.py:72` prints named provenance diagnostics; removing endpoint_pattern fails by name.
- Divergent H1: CLOSED — `src/lib/build_records.py:116` counts distinct instances per triple; `src/lib/build_taxonomy.py:132` passes instance votes; check 22 recomputes the counts.
- Divergent H2: OPEN in the refresh-policy portion (A1); `tests/checks/core/31_taxonomy_dfam_agreement.py:80` uses census/provenance and subset gates, and a 21st concordant snapshot name passes.
- Divergent H3: CLOSED within the ruling — `tests/checks/core/31_taxonomy_dfam_agreement.py:42` guards both ranks; `docs/OUTPUTS.md:207` states DNA coverage; expansion remains deferred.
- Divergent H4: CLOSED — `src/lib/build_taxonomy.py:139` rounds and `tests/checks/core/30_taxonomy_canonical.py:77` checks exactly.
- Divergent H5: CLOSED for rank-specific spelling — `docs/OUTPUTS.md:197` and `tests/checks/core/32_taxonomy_rule_fixtures.py:127`; phase 4 integration advisories A2/A3 remain.
- Divergent M1: CLOSED — `src/lib/build_taxonomy.py:79` adds family_support_share; `docs/OUTPUTS.md:144` states its denominator.
- Divergent M2: CLOSED — `src/lib/build_taxonomy.py:17` and :59 use plurality columns/statuses; `tests/fixtures/taxonomy/rule_cases.tsv:26` retains the sub-majority class winner.
- Divergent M3: CLOSED by recorded deferral — `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md:126` schedules hg38's uncertain-family census.
- Divergent M4: CLOSED for the required census — `tests/expectations/mm39/taxonomy_census.tsv:1` includes both ranks and zero unresolved counts; check 30:88 reads it; remaining assumptions are recorded above.
- Divergent M5: CLOSED — `docs/OUTPUTS.md:200` lists all four no-family spellings.
- Divergent M6: CLOSED — `docs/OUTPUTS.md:133` scopes family identity to class; :195 uses the class/family pair for resolved rollups.
- Divergent M7: CLOSED — `src/lib/build_taxonomy.py:24` names the report column rule_version.
- Divergent L1: CLOSED as the ruling's audit choice — `docs/OUTPUTS.md:179` defines report membership over raw labels and suffix decisions.
- Divergent L2: CLOSED as documented semantics — `docs/OUTPUTS.md:172` separates the total pure function's contract from build validation.
- Divergent L3: CLOSED — `src/lib/build_taxonomy.py:54` and :80 decide ties on integer counts; 1001:1000 publishes resolved_plurality at displayed share 0.5.

## Acceptance re-run

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks`. Scratch scripts used only local inputs; the independent implementation imported neither builder nor checks. Commands and stdout below are verbatim; mutation diagnostics are verbatim excerpts. `R=/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b`; the scratch tree, including probe scripts, was removed afterward.

```bash
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
bash src/20_build_taxonomy.sh /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b/build config/mm39.env
printf 'exit=%s\n' "$?"
sha256sum /workspaces/Meta-Aging/_scratch/te-tracks-audit/{review-p3b,refroot/te_mm39}/build/tables/taxonomy_{canonical,resolution_report}.tsv
```
```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok src/10_build_records.sh
syntax ok src/15_build_universes.sh
syntax ok src/20_build_taxonomy.sh
syntax ok tests/run.sh
names=18484 multi_label_names=20 taxonomy_rule_version=taxonomy_rule_v1
[20_build_taxonomy] canonical taxonomy ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b/build/tables
exit=0
a3663b6447b409c6f87960519c2b380b62aca52063f7e0ca52f46d9cabb3b2b0  /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b/build/tables/taxonomy_canonical.tsv
1f8c068fbeb3dd5aa4943556673d951feca4603e95a0b3067b629583f850d453  /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b/build/tables/taxonomy_resolution_report.tsv
a3663b6447b409c6f87960519c2b380b62aca52063f7e0ca52f46d9cabb3b2b0  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_canonical.tsv
1f8c068fbeb3dd5aa4943556673d951feca4603e95a0b3067b629583f850d453  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_resolution_report.tsv
```

`build/tables/` initially held only symlinks to the orchestrator's `rmsk_taxonomy.tsv` and `rmsk_records.parquet`. The stage wrote the two derived tables. Read-only digest verification:
```bash
sha256sum -c /workspaces/Meta-Aging/_scratch/te-tracks-audit/p3fix_stable.sha
sha256sum /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_taxonomy.tsv
```
```text
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_instance_members.tsv.gz: OK
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_records.parquet: OK
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_records.tsv.gz: OK
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/universe_members.tsv.gz: OK
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/universe_summary.tsv: OK
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/universes.json: OK
26a9110fc332cbe94a05e61fa97f980b4468cfdf006a05c5b24bc22a365f1a4f  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_taxonomy.tsv
```

```bash
PYTHONDONTWRITEBYTECODE=1 python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b/independent.py
```
```text
independent canonical comparison: names=18484 columns=15 mismatches=0
raw_triples=18504 instance_count_sum=4727623 report_rows=20
all class_status: {'concordant': 18478, 'resolved_uncertainty_suffix': 6}
all family_status: {'concordant': 1095, 'resolved_plurality': 7, 'resolved_uncertainty_suffix': 5, 'resolved_unspecified': 5, 'unspecified': 17372}
multi_label class_status: {'concordant': 14, 'resolved_uncertainty_suffix': 6}
multi_label family_status: {'resolved_plurality': 7, 'resolved_uncertainty_suffix': 5, 'resolved_unspecified': 5, 'unspecified': 3}
multi_label classes: {'DNA': 20}
minimum family plurality: (0.84, 'MER63C')
snapshot source comparison: 20 rows preserved; fetched_on=2026-09-16
phase4 component probe: name=A/B accepted=True token=unresolved_family_A/B separator_free=False
mm39 names containing /, : or |: 0
```

```bash
bash tests/run.sh core > /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b/core.log 2>&1
result=$?
cat /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b/core.log
printf 'exit=%s\n' "$result"
```
```text
pass  01_runner_selftest.sh  runner statuses, required checks, diagnostics, dangling symlinks and usage exits pass
pass  10_rmsk_out_parser.py  6 expected records; plain/gzip, signed consensus, ID tokens, malformed/unreadable input and ID statistics pass
pass  11_source_qualification.sh  13 summary metrics and 10 field disagreements verified; reports identical; four source md5s and declared assembly match config pins
pass  20_records_schema.py  5320771 records; 24 typed columns; all typed rows equal; identities and bounds pass
pass  21_instances.py  4696900 instances; one instance per record; single contig; sizes 1=4251251 2=338697 3+=106952
pass  22_universes.py  six universe summaries and every membership match; 17 classes; 3 collision pairs; 20 multi-label names / 6517 records
pass  23_records_fixtures.py  hand-authored records, collisions, text IDs, signed fields, instances, bounds, joins, class sets and tRNA-family rules pass
pass  30_taxonomy_canonical.py  18484 names; all 15 columns recomputed exactly; 20 report rows equal the multi-label subset; census matches; minimum plurality share 0.840 MER63C
pass  31_taxonomy_dfam_agreement.py  report names missing from snapshot: []
pass  32_taxonomy_rule_fixtures.py  31 rule cases; permutations, rank shares, instance weighting, rounded median, deterministic builds, input gates and canonical rollups pass
checks=10 pass=10 fail=0 unsupported=0
exit=0
```

Scratch mutations: change only B1_Mm's canonical_family to REVIEW_FAMILY; remove Eulor5B from the snapshot; add B1_Mm with SINE/Alu and update the copied snapshot_rows census to 21; remove endpoint_pattern; swap only the build caller's instance_count column to record_count; drop instance_count from the copied raw taxonomy. Restore each copy before the next probe. The additional release-response probe supplies a non-null object. The runner invokes the copied checks via `python3 <scratch>/repo/tests/checks/core/<check>` with TE_TRACKS_REFROOT pointing at the copied tables.
```bash
PYTHONDONTWRITEBYTECODE=1 python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b/probes.py
```
```text
single_label_corruption: 30_taxonomy_canonical.py exit=1
AssertionError: all canonical columns.iloc[:, 2] (column name="canonical_family") are different
all canonical columns.iloc[:, 2] (column name="canonical_family") values are different (0.00541 %)
removed_snapshot_name: 31_taxonomy_dfam_agreement.py exit=1
report names missing from snapshot: ['Eulor5B']
snapshot names outside canonical: []
snapshot names beyond report: []
AssertionError: snapshot row census
added_concordant_snapshot_name: 31_taxonomy_dfam_agreement.py exit=0
report names missing from snapshot: []
snapshot names outside canonical: []
snapshot names beyond report: ['B1_Mm']
21 of 21 canonical labels agree with Dfam; 20 report names covered; snapshot names belong to canonical
missing_provenance_key: 31_taxonomy_dfam_agreement.py exit=1
report names missing from snapshot: []
snapshot names outside canonical: []
snapshot names beyond report: []
provenance endpoint_pattern: fail
AssertionError: ('provenance keys', ['build_reads_snapshot', 'fetched_on', 'release_endpoint_response', 'release_endpoint_response_status', 'role', 'source', 'version_evidence'], ['build_reads_snapshot', 'endpoint_pattern', 'fetched_on', 'release_endpoint_response', 'release_endpoint_response_status', 'role', 'source', 'version_evidence'])
record_weighting_caller: 32_taxonomy_rule_fixtures.py exit=1
AssertionError: {'rmsk_name': 'instance_weighting', 'canonical_class': 'DNA', 'canonical_family': 'TcMar', 'class_status': 'concordant', 'family_status': 'resolved_plurality', 'class_plurality_share': 1.0, 'family_plurality_share': 0.811, 'family_support_share': 0.811, 'label_count': 2, 'record_count': 37, 'instance_count': 37, 'record_length_sum_bp': 3028, 'median_divergence_pct': 34.0, 'has_uncertain_source': False, 'has_multiple_labels': True}
dropped_instance_count: 22_universes.py exit=1
AssertionError: (PosixPath('/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b/mutation-refroot/te_mm39/build/tables/rmsk_taxonomy.tsv'), rmsk_name: string
instance_count: int64
retained_release_response: 31_taxonomy_dfam_agreement.py exit=1
report names missing from snapshot: []
snapshot names outside canonical: []
snapshot names beyond report: []
provenance release_endpoint_response: fail
AssertionError: provenance release_endpoint_response: {'version': 'review-refresh'}
repository md5 verification: 167 files checked; changed=[]
```

## Scope check

`git branch --show-current` returned `redesign-2026-09`; `git rev-parse --short HEAD` returned `4eb31f9`. `git diff --check` exited 0. All 155 tracked files and all 12 untracked `src/`/`tests/` files retained their baseline MD5s before and after the probes. The reviewer wrote only this repository file; scratch copies and symlinks were removed. No git writes, installs or network calls were made.

Status summary before writing this review: 13 modified tracked files (seven implementation/public-doc files and six internal planning/prompt files), 12 untracked `src/`/`tests/` files, and eight untracked internal prompt/review files. Outside the fix allowlist: tracked `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/{02_orchestration,12_phase2_canonical,13_phase3_taxonomy,14_phase4_exports}.md`, tracked `docs/_internal/redesign-2026-09/prompts/{p3_review,p4_impl}.md`, untracked `src/20_build_taxonomy.sh`, untracked internal `prompts/{p3_fix,p3_review2,p4_opus,p4_review}.md` and `reviews/{p3_codex,p3_opus,p3_divergent,p3_rulings}.md`. The stage and earlier README delivery rows are documented first-round carryover; the internal files are orchestration records. A diff against HEAD cannot attribute these to the fix implementer. Every file listed in the implementer's fix report is allowed.

`git diff HEAD --stat`:
```text
 README.md                                          |  12 +-
 docs/OUTPUTS.md                                    | 107 ++++++++++++++--
 .../02_orchestration.md                            |   3 +-
 .../12_phase2_canonical.md                         |   1 +
 .../13_phase3_taxonomy.md                          | 136 +++++++++++++--------
 .../14_phase4_exports.md                           |   6 +-
 .../redesign-2026-09/prompts/p3_review.md          |  98 ++++++++++++++-
 docs/_internal/redesign-2026-09/prompts/p4_impl.md |  67 ++++++----
 src/lib/build_records.py                           |   4 +-
 tests/checks/core/20_records_schema.py             |   7 +-
 tests/checks/core/22_universes.py                  |  13 +-
 tests/checks/core/23_records_fixtures.py           |   5 +-
 tests/lib/records.py                               |   5 +
 13 files changed, 359 insertions(+), 105 deletions(-)
```
