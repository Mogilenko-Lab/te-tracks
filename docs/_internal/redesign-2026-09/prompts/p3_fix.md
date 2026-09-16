# te-tracks phase 3 fix: review rulings

You are the implementer for the phase 3 fix round of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, uncommitted phase 3 tree from
`prompts/p3_impl.md`. The plan file
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md` has been rewritten to the
corrected contract and is authoritative for every column, status, token, check and number below; read it first and
follow it exactly. Then read `docs/_internal/redesign-2026-09/reviews/p3_rulings.md` (why each change exists),
`src/lib/build_records.py` (the `rmsk_taxonomy` writer), `src/lib/build_taxonomy.py`, `tests/lib/records.py`,
`tests/checks/core/{20,22,23}_*.py` (readers of `rmsk_taxonomy`), `tests/checks/core/3*.py`,
`tests/fixtures/taxonomy/*`, and the phase 2 and 3 sections of `docs/OUTPUTS.md`.

Binding prose rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".

## Changes

1. **Instance counts in `rmsk_taxonomy` (H1).** `build_records.py` writes `instance_count` (distinct
   `rmsk_instance_id` among the triple's records) between `record_count` and `record_length_sum_bp`. Every reader
   of the table (`tests/lib/records.py` schema, checks 20/22/23 and their fixture expectations under
   `tests/fixtures/records/`, `docs/OUTPUTS.md` phase 2 contract) follows. `rmsk_records.parquet`,
   `rmsk_records.tsv.gz`, `rmsk_instance_members.tsv.gz`, `universe_members.tsv.gz`, `universe_summary.tsv` and
   `universes.json` stay byte-identical; `rmsk_taxonomy.tsv` changes and you report its new sha256.
2. **The rule weights by instance (H1), fallback ruling (B1), plurality naming (M2), tokens (H5).** `resolve`
   takes `(class, family, instance_count)` votes; the winning class with no specified family publishes the class
   token with `unspecified`; statuses and shares are named `resolved_plurality`, `class_plurality_share`,
   `family_plurality_share`; `family_support_share` is added (M1); `median_divergence_pct` rounds to two decimals
   (H4); `instance_count` joins the canonical columns; the resolution report gains `rmsk_label_records` and renames
   `rule_fired` to `rule_version` (M7). Column orders exactly as the plan states. Unresolved ranks keep empty
   canonical fields; the rollup tokens `unresolved_class_<name>` / `unresolved_family_<name>` appear in the rule
   fixtures' rollup case and in `docs/OUTPUTS.md`.
3. **Expectations file (M4).** `tests/expectations/mm39/taxonomy_census.tsv` (`metric, value`) holding the plan's
   acceptance census, authored from your measurement of the rebuilt table; check 30 reads it. The values the plan
   states are the orchestrator's independent measurement; a difference is a deviation to report, and the file
   records what you observe.
4. **Check 30 (A1, M4).** Recompute every row through `resolve` from `rmsk_taxonomy` and the parquet median; compare
   all 15 columns exactly; assert the census; assert the report equals the multi-label subset.
5. **Check 31 (H2, H3, A2).** Subset gate as the plan states: diagnostics printed first, report ⊆ snapshot, snapshot
   names ⊆ canonical names, type compared only where Dfam names one, subtype only where named, row count from the
   census file, `fetched_on` from the provenance file; no literal count, date or URL in the check.
6. **Provenance (B2).** `dfam_snapshot.provenance.json` keys: `endpoint_pattern`, `fetched_on`, `source`, `role`,
   `build_reads_snapshot: false`, `version_evidence: "per-family dfam_version column of the snapshot"`,
   `release_endpoint_response: null`, `release_endpoint_response_status: "unrecorded at the 2026-09-16 fetch; the
   next snapshot refresh records it"`.
   Check 31 asserts every one of these keys with a named diagnostic (Opus A5, B3).
7. **Rule fixtures.** `rule_cases.tsv` counts mean instances; rename the status words; correct `winning_class_abstains`
   to the ruling; rollup cases use the rank tokens; add one case whose record counts and lengths would elect a
   different winner than its instance counts (Opus A3), carried through check 32's synthetic `rmsk_taxonomy` with
   `record_count` and `record_length_sum_bp` disproportionate to `instance_count`, so the instance weighting is
   pinned as behaviour. Check 32 follows.
8. **`docs/OUTPUTS.md`.** Phase 2 `rmsk_taxonomy` contract with `instance_count`; phase 3 sections rewritten to the
   plan: rule sentences with instance weighting, statuses, all 15 columns and both share denominators, the report
   columns, the rank tokens, the four spellings of "no family", family uniqueness within class, report membership
   over raw labels, ties on integer counts. README truth table gains a row for
   `tests/expectations/mm39/taxonomy_census.tsv` (`delivered, tested`, 3).

## Rules
- Touch only: `src/lib/build_records.py`, `src/lib/build_taxonomy.py`, `tests/lib/records.py`,
  `tests/checks/core/{20_records_schema.py,22_universes.py,23_records_fixtures.py,30_taxonomy_canonical.py,31_taxonomy_dfam_agreement.py,32_taxonomy_rule_fixtures.py}`,
  `tests/fixtures/records/**` (expectation files that carry taxonomy columns), `tests/fixtures/taxonomy/**`,
  `tests/expectations/mm39/taxonomy_census.tsv`, `docs/OUTPUTS.md`, `README.md` (that one row). Nothing else.
- No git writes. No installs. No network. Re-run stages 10, 15 and 20 on `$TE_TRACKS_REFROOT/te_mm39/build`.
- Report a deviation instead of editing a number, an expectation or a plan file to fit. Tests are strengthened only.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
B="$TE_TRACKS_REFROOT/te_mm39/build"
grep -v 'rmsk_taxonomy\|taxonomy_' /workspaces/Meta-Aging/_scratch/te-tracks-audit/m2fix_before.sha > /workspaces/Meta-Aging/_scratch/te-tracks-audit/p3fix_stable.sha
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
time bash src/10_build_records.sh "$B" config/mm39.env; echo "exit=$?"
bash src/15_build_universes.sh "$B" config/mm39.env; echo "exit=$?"
bash src/20_build_taxonomy.sh "$B" config/mm39.env; echo "exit=$?"
sha256sum -c /workspaces/Meta-Aging/_scratch/te-tracks-audit/p3fix_stable.sha
sha256sum "$B"/tables/rmsk_taxonomy.tsv "$B"/tables/taxonomy_canonical.tsv "$B"/tables/taxonomy_resolution_report.tsv
head -3 "$B"/tables/rmsk_taxonomy.tsv
awk -F'\t' 'NR>1{s+=$5} END{print "instance_count_sum", s}' "$B"/tables/rmsk_taxonomy.tsv
head -1 "$B"/tables/taxonomy_canonical.tsv | tr '\t' '\n' | nl
cut -f5 "$B"/tables/taxonomy_canonical.tsv | sort | uniq -c
cut -f4 "$B"/tables/taxonomy_canonical.tsv | sort | uniq -c
awk -F'\t' 'NR>1 && $5=="resolved_plurality"{print $7, $1}' "$B"/tables/taxonomy_canonical.tsv | sort -n | head -1
cat "$B"/tables/taxonomy_resolution_report.tsv
cat tests/expectations/mm39/taxonomy_census.tsv
python3 -c "
import sys; sys.path.insert(0,'src/lib')
from build_taxonomy import resolve
print(resolve([('DNA','DNA',7),('LINE','L1',3)]))
print(resolve([('DNA','hAT',2),('DNA','TcMar',2)]))"
tests/run.sh core; echo "exit=$?"
git status --short | grep -v docs/_internal
```
Expected: every stable digest `OK`; `instance_count_sum 4727623`; 15 columns in the plan's order; family statuses
1,095 `concordant`, 7 `resolved_plurality`, 5 `resolved_uncertainty_suffix`, 5 `resolved_unspecified`, 17,372
`unspecified`; class statuses 18,478 `concordant`, 6 `resolved_uncertainty_suffix`; minimum plurality share `0.84
MER63C`; the first probe publishes `DNA`/`DNA`/`resolved_plurality`/`unspecified`, the second `DNA`, empty family,
`concordant`/`unresolved`; `core` exits 0 with ten passes.

## Final message
Every file changed; acceptance outputs verbatim; the new `rmsk_taxonomy.tsv`, `taxonomy_canonical.tsv` and
`taxonomy_resolution_report.tsv` digests; any deviation.
