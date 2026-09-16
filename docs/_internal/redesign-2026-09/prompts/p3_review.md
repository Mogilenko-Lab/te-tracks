# te-tracks phase 3 review (codex, read-only)

You are an independent reviewer of phase 3 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p3_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md`
2. The decisions: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md`
3. The wording and comment rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments"
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD --stat` and the full
   diff, plus untracked files from `git status --short`.
5. The implementer's own report, pasted below under "Implementer report".

## Judge, with evidence
- **Contract conformance**: every deliverable in the phase file present at the stated path with the stated
  content; every acceptance command re-run by you with its output quoted; any number that differs from the
  contract named.
- **Fixture adequacy**: do the fixtures and checks fail when they should? Try to break one (read-only: reason
  from the code, or run it against a modified copy under /tmp).
- **Silent assumptions**: anything the code or docs assume that the contract leaves open; anything that will
  bite phase 4.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 3 review (codex gpt-6-astra)
Verdict: PASS | PASS WITH ADVISORIES | BLOCKING
## Blocking
- [B1] <file:line> <finding> — <evidence> — <what fixes it>
## Advisory
- [A1] ...
## Acceptance re-run
<commands and outputs, verbatim>
## Scope check
<git status / diff --stat summary>
```
BLOCKING means a contract deliverable is missing or wrong, an acceptance number differs, or a check cannot fail.
Keep the file under 200 lines. Facts over opinions; every finding cites a path and, where possible, a line.

## Orchestrator notes (check these in addition)
- Run the taxonomy stage yourself into your own directory: create
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3/build/tables/` holding symlinks to the orchestrator's
  `tables/rmsk_taxonomy.tsv` and `tables/rmsk_records.parquet` under
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/` (read them, leave them untouched), run
  `bash src/20_build_taxonomy.sh <your build dir> config/mm39.env`, and compare the sha256 of
  `taxonomy_canonical.tsv` and `taxonomy_resolution_report.tsv` with the orchestrator's. Remove your directory when done.
- The implementer's prompt is `docs/_internal/redesign-2026-09/prompts/p3_impl.md`; the milestone 2 rulings that
  bind this phase are in `docs/_internal/redesign-2026-09/reviews/m2_rulings.md` under "Phase 3" (unresolved
  spelling `unresolved/<rmsk_name>`, one bucket per name; rule stays `taxonomy_rule_v1`; `MER53` shape fixture).
- The rule must be one pure function `resolve(labels) -> dict` with `TAXONOMY_RULE_VERSION = "taxonomy_rule_v1"`;
  judge whether any second copy of the rule lives in a check or a doc, and whether the precedence "majority over
  unspecified over uncertainty suffix over concordant" is applied per rank as the phase file states.
- Recompute from `tables/rmsk_taxonomy.tsv` with your own code: 18,484 names; 20 with more than one label; the
  status census 7 `resolved_majority`, 5 `resolved_unspecified`, 5 `resolved_uncertainty_suffix`, 3 `unspecified`;
  every multi-label name `canonical_class = DNA`; min `family_majority_share` 0.734 (`MER63C`); `Eulor5B`
  class `resolved_uncertainty_suffix` and family `resolved_unspecified`; `MER124` canonical `DNA/DNA`.
- `median_divergence_pct` per name over `divergence_pct` of `rmsk_records.parquet`: recompute for five names of
  your choice, including one multi-label name, and compare with the table.
- Fixture adequacy: on a scratch copy break the tie handling, the `?` stripping, the class-only abstention and the
  Dfam join one at a time; name the check that fails each time and quote its message. Confirm check 31 fails when
  one snapshot name is removed (set equality) and when one `dfam_repeat_subtype` is altered.
- The build reads no Dfam data and no network: confirm by reading `src/lib/build_taxonomy.py` imports and file opens.
- Orchestrator ruling to judge against: rule step 3 in the phase file now reads that a name whose winning class
  carries no specified family publishes `canonical_family = canonical_class` with `family_status = unspecified`,
  and specified families under losing classes take no part in the family vote. The implementation's
  `winning_class_abstains` fixture case (`DNA/DNA=7;LINE/L1=3`) and the matching `docs/OUTPUTS.md` sentence
  publish an unresolved family instead; treat that as a finding and state what changes (`resolve`, the fixture
  row, the sentence). mm39 has no such name, so no number moves.
- Wording: every sentence and comment in `src/lib/build_taxonomy.py`, `src/20_build_taxonomy.sh`, the three checks,
  the `docs/OUTPUTS.md` diff and the README diff.

## Implementer report
Implemented phase 3. All 10 core checks pass.

Changed:

- [README.md](/workspaces/Meta-Aging/01_modules/te-tracks/README.md)
- [docs/OUTPUTS.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/OUTPUTS.md)

Created:

- [src/20_build_taxonomy.sh](/workspaces/Meta-Aging/01_modules/te-tracks/src/20_build_taxonomy.sh)
- [src/lib/build_taxonomy.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/lib/build_taxonomy.py)
- [30_taxonomy_canonical.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/30_taxonomy_canonical.py)
- [31_taxonomy_dfam_agreement.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/31_taxonomy_dfam_agreement.py)
- [32_taxonomy_rule_fixtures.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/32_taxonomy_rule_fixtures.py)
- [dfam_snapshot.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/taxonomy/dfam_snapshot.tsv)
- [dfam_snapshot.provenance.json](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/taxonomy/dfam_snapshot.provenance.json)
- [rule_cases.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/taxonomy/rule_cases.tsv)
- [rollup_counts.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/taxonomy/rollup_counts.tsv)

Generated [taxonomy_canonical.tsv](/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_canonical.tsv) and [taxonomy_resolution_report.tsv](/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_resolution_report.tsv) in the scratch build.

Acceptance scope clarification: the 7/5/5/3 family-status expectation holds for the 20 multi-label names. The full table has 17,372 `unspecified` rows. No other deviations; no git writes, installs, or network access.

Acceptance outputs verbatim:

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
[20_build_taxonomy] canonical taxonomy ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables
exit=0
  18485 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_canonical.tsv
     21 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_resolution_report.tsv
  18506 total
   1095 concordant
      1 family_status
      7 resolved_majority
      5 resolved_uncertainty_suffix
      5 resolved_unspecified
  17372 unspecified
      1 class_status
  18478 concordant
      6 resolved_uncertainty_suffix
rmsk_name	rmsk_labels	rule_fired	canonical_class	canonical_family	class_status	family_status
Eulor5B	DNA/Crypton-A=34;DNA?/DNA?=1	taxonomy_rule_v1	DNA	Crypton-A	resolved_uncertainty_suffix	resolved_unspecified
Eulor6A	DNA/Crypton=19;DNA?/DNA?=1	taxonomy_rule_v1	DNA	Crypton	resolved_uncertainty_suffix	resolved_unspecified
Eulor8	DNA/TcMar=104;DNA/TcMar?=2	taxonomy_rule_v1	DNA	TcMar	concordant	resolved_uncertainty_suffix
Eutr15	DNA/hAT-Tip100=109;DNA/hAT-Tip100?=2	taxonomy_rule_v1	DNA	hAT-Tip100	concordant	resolved_uncertainty_suffix
Eutr16	DNA/hAT-Tip100=98;DNA?/hAT-Tip100?=2	taxonomy_rule_v1	DNA	hAT-Tip100	resolved_uncertainty_suffix	resolved_uncertainty_suffix
Eutr2	DNA/MULE-MuDR=40;DNA/DNA=7	taxonomy_rule_v1	DNA	MULE-MuDR	concordant	resolved_unspecified
Eutr2B	DNA/MULE-MuDR=68;DNA/DNA=7	taxonomy_rule_v1	DNA	MULE-MuDR	concordant	resolved_unspecified
MER121	DNA/hAT=555;DNA/hAT?=6	taxonomy_rule_v1	DNA	hAT	concordant	resolved_uncertainty_suffix
MER124	DNA/DNA=247;DNA?/DNA?=2	taxonomy_rule_v1	DNA	DNA	resolved_uncertainty_suffix	unspecified
MER131	DNA/DNA=474;DNA?/DNA?=1	taxonomy_rule_v1	DNA	DNA	resolved_uncertainty_suffix	unspecified
MER136	DNA/Merlin=21;DNA/DNA=2	taxonomy_rule_v1	DNA	Merlin	concordant	resolved_unspecified
MER53	DNA/hAT-Blackjack=1633;DNA/hAT=7	taxonomy_rule_v1	DNA	hAT-Blackjack	concordant	resolved_majority
MER63A	DNA/hAT-Tip100=714;DNA/hAT-Blackjack=1	taxonomy_rule_v1	DNA	hAT-Tip100	concordant	resolved_majority
MER63B	DNA/hAT-Tip100=417;DNA/hAT-Blackjack=21	taxonomy_rule_v1	DNA	hAT-Tip100	concordant	resolved_majority
MER63C	DNA/hAT-Tip100=273;DNA/hAT-Blackjack=99	taxonomy_rule_v1	DNA	hAT-Tip100	concordant	resolved_majority
MER63D	DNA/hAT-Tip100=935;DNA/hAT-Blackjack=111	taxonomy_rule_v1	DNA	hAT-Tip100	concordant	resolved_majority
MER99	DNA/hAT=148;DNA/hAT?=35	taxonomy_rule_v1	DNA	hAT	concordant	resolved_uncertainty_suffix
UCON2	DNA/DNA=99;DNA?/DNA?=2	taxonomy_rule_v1	DNA	DNA	resolved_uncertainty_suffix	unspecified
UCON44	DNA/TcMar-Tigger=87;DNA/TcMar=3	taxonomy_rule_v1	DNA	TcMar-Tigger	concordant	resolved_majority
X4b_DNA	DNA/TcMar-Tigger=125;DNA/TcMar=5	taxonomy_rule_v1	DNA	TcMar-Tigger	concordant	resolved_majority
pass  01_runner_selftest.sh  runner statuses, required checks, diagnostics, dangling symlinks and usage exits pass
pass  10_rmsk_out_parser.py  6 expected records; plain/gzip, signed consensus, ID tokens, malformed/unreadable input and ID statistics pass
pass  11_source_qualification.sh  13 summary metrics and 10 field disagreements verified; reports identical; four source md5s and declared assembly match config pins
pass  20_records_schema.py  5320771 records; 24 typed columns; all typed rows equal; identities and bounds pass
pass  21_instances.py  4696900 instances; one instance per record; single contig; sizes 1=4251251 2=338697 3+=106952
pass  22_universes.py  six universe summaries and every membership match; 17 classes; 3 collision pairs; 20 multi-label names / 6517 records
pass  23_records_fixtures.py  hand-authored records, collisions, text IDs, signed fields, instances, bounds, joins, class sets and tRNA-family rules pass
pass  30_taxonomy_canonical.py  18484 names; 20 multi-label DNA names; family statuses 7/5/5/3; minimum majority share 0.734; summaries pass
pass  31_taxonomy_dfam_agreement.py  20 of 20 canonical labels agree with Dfam; snapshot and resolution name sets are equal
pass  32_taxonomy_rule_fixtures.py  30 rule cases; permutations, rank shares, median, deterministic builds and canonical rollups pass
checks=10 pass=10 fail=0 unsupported=0
exit=0
 M README.md
 M docs/OUTPUTS.md
?? src/20_build_taxonomy.sh
?? src/lib/build_taxonomy.py
?? tests/checks/core/30_taxonomy_canonical.py
?? tests/checks/core/31_taxonomy_dfam_agreement.py
?? tests/checks/core/32_taxonomy_rule_fixtures.py
?? tests/fixtures/taxonomy/
```
