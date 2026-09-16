# Phase 3 review (codex gpt-6-astra)
Verdict: BLOCKING

## Blocking

- [B1] `src/lib/build_taxonomy.py:72` applies the unspecified-family fallback across all classes, contradicting rule step 3 (`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md:19`). — `DNA/DNA=7;LINE/L1=3` returns class `DNA`, empty family and `family_status=unresolved`; the contract requires `DNA/DNA` and `unspecified`. `tests/fixtures/taxonomy/rule_cases.tsv:24` endorses the wrong result. — Make the zero-family-votes branch publish the winning class with `unspecified`, correct that fixture row, and update both `docs/OUTPUTS.md:152` and `docs/OUTPUTS.md:160`. Losing classes contribute no family evidence. No mm39 number changes.
- [B2] `tests/fixtures/taxonomy/dfam_snapshot.provenance.json:1` omits the Dfam version endpoint response required by `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md:56`. — Its five fields record the family-query pattern, date, local source, role and build-use flag; the snapshot's `dfam_version` values are per-family versions. Check 31 passes without the required endpoint response. — Preserve the actual retained version response and check its presence, or obtain an explicit contract ruling if that evidence is unavailable under the no-network constraint.
- [B3] `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md:53` requires manifest identity to carry `taxonomy_rule_version`, but this deliverable is absent. — `src/lib/build_taxonomy.py:16`, `:134` and `:145` provide the constant, report value and log text; there is no manifest in the scratch build and no identity writer. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/17_phase7_publication.md:4` assigns the manifest to phase 7, while `docs/_internal/redesign-2026-09/prompts/p3_impl.md:61` excludes it from allowed phase 3 edits. — Resolve this scope conflict explicitly by deferring the phase 3 identity requirement to phase 7, or authorize and deliver the identity artifact.

## Advisory

- [A1] `tests/checks/core/30_taxonomy_canonical.py:54` compares canonical labels only for multi-label names; subsequent raw-table checks cover summaries. — Changing the single-label `B1_Mm` from `SINE/Alu` to `REVIEW_CLASS/REVIEW_FAMILY` passes checks 30, 31 and 32. Phase 4 could consume a corrupted family assignment. — Compare every emitted decision with the shared `resolve` result while retaining the independent hand-authored rule expectations.
- [A2] `tests/checks/core/31_taxonomy_dfam_agreement.py:26` masks missing-name diagnostics. — Removing `Eulor5B` exits 1 with a bare `AssertionError` before the name-set comparison; replacing its name while retaining 20 rows reaches the set-equality assertion and prints both missing mappings. — Perform coverage diagnostics before the fixed-size assertion, or add the missing names to that assertion.
- [A3] `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md:44` and `:58` retain paths `src/20_build_taxonomy.py` and `tests/checks/core/taxonomy_dfam_agreement.py`, which are absent. — The implementation follows the explicit replacements in `docs/_internal/redesign-2026-09/prompts/p3_impl.md:23` and `:41`: `src/lib/build_taxonomy.py` and `tests/checks/core/31_taxonomy_dfam_agreement.py`. — Synchronize the phase file with those authorized paths.

Conformance: both generated tables have the specified schemas, sorting and row counts; all four taxonomy fixtures and the stage/check files exist at the implementation-prompt paths. The snapshot preserves every source field and adds the specified fetch date. The 30 cases cover every status, both tie ranks, class competition, MER53, Eulor5B, MER124 and count-conserving rollups with distinct unresolved-name buckets (`tests/checks/core/32_taxonomy_rule_fixtures.py:101`). The numeric scope clarification is necessary: 7/5/5/3 describes the 20 multi-label names; the full table has 17,372 unspecified families and 1,095 concordant families.

Rule/code review: `resolve` is the sole executable resolver and leaves its input unchanged; checks import it and use hand-authored expectations. Rank precedence is applied separately at `src/lib/build_taxonomy.py:58` and `:83`. OUTPUTS contains the required prose rule, with B1's divergent fallback. Imports and reads at `:3`, `:96`, `:109` use only local libraries and the two source tables; writes at `:142` target the two derived tables. The build reads no Dfam data and makes no network request. All sentences, docstrings and comments in the five added scripts, OUTPUTS diff and README diff were reviewed; no gratuitous contrastive negation, history or provenance chatter was found.

## Acceptance re-run

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks`. The stage and table-inspection commands use the review build below to preserve the orchestrator's files. Commands and output:

```bash
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
review_build=/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3/build
mkdir -p "$review_build/tables"
ln -s "$TE_TRACKS_REFROOT/te_mm39/build/tables/rmsk_taxonomy.tsv" "$review_build/tables/rmsk_taxonomy.tsv"
ln -s "$TE_TRACKS_REFROOT/te_mm39/build/tables/rmsk_records.parquet" "$review_build/tables/rmsk_records.parquet"
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
bash src/20_build_taxonomy.sh "$review_build" config/mm39.env; echo "exit=$?"
wc -l "$review_build/tables/taxonomy_canonical.tsv" "$review_build/tables/taxonomy_resolution_report.tsv"
cut -f5 "$review_build/tables/taxonomy_canonical.tsv" | sort | uniq -c
cut -f4 "$review_build/tables/taxonomy_canonical.tsv" | sort | uniq -c
cat "$review_build/tables/taxonomy_resolution_report.tsv"
sha256sum "$review_build/tables/taxonomy_canonical.tsv" "$TE_TRACKS_REFROOT/te_mm39/build/tables/taxonomy_canonical.tsv" "$review_build/tables/taxonomy_resolution_report.tsv" "$TE_TRACKS_REFROOT/te_mm39/build/tables/taxonomy_resolution_report.tsv"
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
[20_build_taxonomy] canonical taxonomy ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3/build/tables
exit=0
  18485 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3/build/tables/taxonomy_canonical.tsv
     21 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3/build/tables/taxonomy_resolution_report.tsv
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
fb5699c62b871bbe04f73aa40e1862000502c006114a8ca284b4568d3747aeff  /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3/build/tables/taxonomy_canonical.tsv
fb5699c62b871bbe04f73aa40e1862000502c006114a8ca284b4568d3747aeff  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_canonical.tsv
6e9ca5b6eb7dc406735c592ba51e3c5475e038ad44ca243ca1c1c690154a1f72  /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3/build/tables/taxonomy_resolution_report.tsv
6e9ca5b6eb7dc406735c592ba51e3c5475e038ad44ca243ca1c1c690154a1f72  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_resolution_report.tsv
```

```bash
tests/run.sh core > /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3/core.log 2>&1
core_exit=$?
cat /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3/core.log
echo "exit=$core_exit"
```
```text
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
```

Independent recomputation used `python3 -` with stdlib CSV/Counter votes and PyArrow batches plus `statistics.median`, without importing the builder. Verbatim stdout excerpts:
```text
independent raw census: names=18484 multi_label_names=20 canonical_mismatches=0
multi-label family statuses: {'resolved_majority': 7, 'resolved_uncertainty_suffix': 5, 'resolved_unspecified': 5, 'unspecified': 3}
multi-label canonical classes: {'DNA': 20}
minimum resolved_majority family share: (0.734, 'MER63C')
Eulor5B: ('DNA', 'Crypton-A', 'resolved_uncertainty_suffix', 'resolved_unspecified', 1.0)
MER124: ('DNA', 'DNA', 'resolved_uncertainty_suffix', 'unspecified', 0.0)
median B1_Mm: records=42591 independent=6.2 canonical=6.2
median Eulor5B: records=35 independent=27.4 canonical=27.4
median L1MdA_I: records=4683 independent=0.3 canonical=0.3
median MER124: records=249 independent=29.1 canonical=29.1
median MER63C: records=372 independent=30.4 canonical=30.4
Dfam snapshot: all 20 source rows preserved; fetched_on=2026-09-16
```

Scratch copies ran `python3 <scratch>/tests/checks/core/{31_taxonomy_dfam_agreement,32_taxonomy_rule_fixtures}.py`. Mutations independently disabled tie guards, disabled normalization, counted class-only family votes, misdirected the Dfam lookup, then removed/renamed a snapshot name and changed a subtype. Diagnostic excerpts:
```text
baseline rule: 32_taxonomy_rule_fixtures.py exit=0
30 rule cases; permutations, rank shares, median, deterministic builds and canonical rollups pass
baseline Dfam: 31_taxonomy_dfam_agreement.py exit=0
20 of 20 canonical labels agree with Dfam; snapshot and resolution name sets are equal
tie picks first winner: 32_taxonomy_rule_fixtures.py exit=1
AssertionError: ('family_tie', 'canonical_family', 'hAT', '')
suffix normalization disabled: 32_taxonomy_rule_fixtures.py exit=1
AssertionError: ('family_uncertainty', 'family_status', 'resolved_majority', 'resolved_uncertainty_suffix')
class-only labels cast family votes: 32_taxonomy_rule_fixtures.py exit=1
AssertionError: ('resolved_unspecified', 'family_status', 'resolved_majority', 'resolved_unspecified')
Dfam join points Eulor5B at Eulor6A: 31_taxonomy_dfam_agreement.py exit=1
Eulor5B: canonical=DNA/Crypton; Dfam=DNA/Crypton-A
AssertionError: 1 Dfam disagreements
snapshot Eulor5B removed: 31_taxonomy_dfam_agreement.py exit=1
AssertionError
snapshot name replaced with cardinality 20: 31_taxonomy_dfam_agreement.py exit=1
Eulor5B: canonical=DNA/Crypton-A; Dfam=<absent>
Eulor5B_REVIEW: canonical=<absent>; Dfam=DNA/Crypton-A
AssertionError: resolution report and Dfam snapshot name sets differ
snapshot Eulor5B subtype altered: 31_taxonomy_dfam_agreement.py exit=1
Eulor5B: canonical=DNA/Crypton-A; Dfam=DNA/REVIEW_WRONG_SUBTYPE
AssertionError: 1 Dfam disagreements
winning class abstains: {'canonical_class': 'DNA', 'canonical_family': '', 'class_status': 'resolved_majority', 'family_status': 'unresolved', 'class_majority_share': 0.7, 'family_majority_share': 0.0, 'label_count': 2, 'record_count': 10, 'has_uncertain_source': False, 'has_multiple_labels': True}
mutation scratch removed
```

Check 30's absence behavior and a separate canonical-table mutation ran the unchanged checks against a temporary `TE_TRACKS_REFROOT`:
```text
canonical table absent: 30_taxonomy_canonical.py exit=3
unsupported: run build.sh first
single-label mutation: B1_Mm SINE/Alu -> REVIEW_CLASS/REVIEW_FAMILY
single-label corruption: 30_taxonomy_canonical.py exit=0
18484 names; 20 multi-label DNA names; family statuses 7/5/5/3; minimum majority share 0.734; summaries pass
single-label corruption: 31_taxonomy_dfam_agreement.py exit=0
20 of 20 canonical labels agree with Dfam; snapshot and resolution name sets are equal
single-label corruption: 32_taxonomy_rule_fixtures.py exit=0
30 rule cases; permutations, rank shares, median, deterministic builds and canonical rollups pass
table-mutation scratch removed
```

## Scope check

`git diff --check` exited 0. The two public-document changes and nine untracked implementation files match the phase allowlist. Four additional tracked paths are outside it: phase 3's contract/review prompt were already modified at review entry; phase 4's contract/implementation prompt changed during review. These are orchestration/planning changes; their author is unverified. Initial stat: 4 files, 169 insertions, 17 deletions. Final pre-review-file commands and output:

```text
$ git status --short
$ git diff HEAD --stat
 M README.md
 M docs/OUTPUTS.md
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md
 M docs/_internal/redesign-2026-09/prompts/p3_review.md
 M docs/_internal/redesign-2026-09/prompts/p4_impl.md
?? src/20_build_taxonomy.sh
?? src/lib/build_taxonomy.py
?? tests/checks/core/30_taxonomy_canonical.py
?? tests/checks/core/31_taxonomy_dfam_agreement.py
?? tests/checks/core/32_taxonomy_rule_fixtures.py
?? tests/fixtures/taxonomy/
 README.md                                          | 11 +--
 docs/OUTPUTS.md                                    | 72 ++++++++++++++--
 .../13_phase3_taxonomy.md                          |  5 +-
 .../14_phase4_exports.md                           |  3 +-
 .../redesign-2026-09/prompts/p3_review.md          | 98 +++++++++++++++++++++-
 docs/_internal/redesign-2026-09/prompts/p4_impl.md | 65 ++++++++------
 6 files changed, 212 insertions(+), 42 deletions(-)
```

The reviewer wrote only this repository file, performed no git writes, installs or network access, and removed the review build and all temporary mutation trees. Raw inputs were read through symlinks and left untouched.
