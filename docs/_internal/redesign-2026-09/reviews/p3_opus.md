# Phase 3 re-review (Opus)
Verdict: FAIL

## Blocking

- [B1] `src/lib/build_taxonomy.py:73` scopes the unspecified-family fallback to "no specified family *anywhere*", while the amended rule step 3 (`13_phase3_taxonomy.md:19-22`) scopes it to the winning class and states that losing-class families take no part in the family vote. — `resolve([("DNA","DNA",7),("LINE","L1",3)])` returns `canonical_class=DNA, canonical_family='', class_status=resolved_majority, family_status=unresolved`; the contract requires `DNA/DNA` with `unspecified`. `tests/fixtures/taxonomy/rule_cases.tsv:24` (`winning_class_abstains`) authors the divergent result, and `docs/OUTPUTS.md:152` and `:160` document it in public prose. My from-scratch implementation of the four rule sentences disagrees with exactly one of the 30 fixture cases — that one. mm39 carries **0** names with more than one distinct normalized class, so the branch is unreachable on this source: I applied the fix in a scratch copy and check 30 still passed with every acceptance number intact, while check 32 failed only on fixture row 24. — Drop the `all(...)` guard so the zero-family-votes branch publishes the winning class with `unspecified`; correct fixture row 24 to `DNA / DNA / resolved_majority / unspecified`; rewrite the two OUTPUTS sentences. No mm39 number moves.
- [B2] `tests/checks/core/30_taxonomy_canonical.py:54` compares canonical decisions only for the 20 multi-label names, leaving the rule's output for the other 18,464 names unchecked by anything. — In a scratch `TE_TRACKS_REFROOT` I published `B1_Mm` (42,591 records, the second-largest SINE subfamily) as `REVIEW_CLASS  REVIEW_FAMILY  NOT_A_STATUS  unspecified  0.5  0.5` — labels, both statuses (including an out-of-vocabulary class status) and both shares corrupted at once — and checks 30, 31 and 32 all exited 0 with their normal pass lines. Phase 4's `subfamily.bed`, `family.bed` and `taxonomy_triple.saf` read exactly those columns. Narrower mutations of `family_status` are caught incidentally by the table-wide `len(majority) == 7` assertion at `:49`, so the gap is specifically the label, class-status and share columns. — Recompute `resolve` per name inside check 30 from `rmsk_taxonomy` and compare all six decision columns on all 18,484 rows, retaining the hand-authored fixture expectations in check 32 as the independent oracle. (Codex filed this as advisory A1; I judge a derived table whose only guard is its own producer, consumed next phase, to be blocking.)
- [B3] `tests/fixtures/taxonomy/dfam_snapshot.provenance.json:1` satisfies two of the four items the amended contract sentence assigns it (`13_phase3_taxonomy.md:55-60`). — Present: `endpoint_pattern`, `fetched_on` (plus unasserted `source`, `role`, `build_reads_snapshot`). Absent: the per-family `dfam_version` values as retained version evidence — those live in the snapshot TSV column, not in the JSON — and the release-endpoint response named as the next refresh's addition. Check 31 asserts three keys, so the file passes. A repo-wide grep finds no Dfam release/version response anywhere, including `docs/_internal/redesign-2026-09/taxonomy/`; the only versions on hand are the per-family `2`/`4` values. — Either reword the contract sentence to place the version evidence in `dfam_snapshot.tsv:dfam_version`, or add `dfam_version_evidence` and `dfam_release_response` keys and assert them at `31_taxonomy_dfam_agreement.py:29-32`. This is the residue of codex B2 after the amendment, not a fresh objection to the ruling.

## Advisory

- [A1] `src/lib/build_taxonomy.py:113` publishes unrounded float64 medians: 765 of 18,484 rows carry 16–17 digits, e.g. `(AAAAAAT)n` → `7.949999999999999` and `(AAAACA)n` → `2.8499999999999996`, from a source with one decimal place. Not a reproducibility defect — stdlib `statistics.median` reproduces all 765 strings exactly, so the value is IEEE-determined — but it reads as noise beside the 3-decimal shares. Round to three decimals and state the rounding in the OUTPUTS column contract.
- [A2] Agree with codex A2: removing `Eulor5B` from the snapshot exits 1 with a bare `AssertionError` at `31_taxonomy_dfam_agreement.py:26`, before the loop that would name the missing mapping. Run the coverage diagnostics ahead of the fixed-size assertion.
- [A3] The record-count weighting of rule step 1 is only incidentally guarded. `32_taxonomy_rule_fixtures.py:83` sets `record_length_sum_bp = record_count * 4` for every fixture label, so length-weighted votes are proportional to record-weighted votes in all 30 cases, and **0** mm39 decisions change under length weighting. Swapping the caller at `build_taxonomy.py:124` to `record_length_sum_bp` fails check 32 only through the rollup length assertion at `:99`, never through a vote winner. Give one fixture label a length disproportionate to its count.
- [A4] Degenerate inputs (empty normalized class, nonpositive count) poison the whole name to unresolved at both ranks rather than dropping the offending label. The build rejects nonpositive counts upfront at `:107`, so mm39 never reaches it, and OUTPUTS documents the semantics. Recording the choice, since the status vocabulary has no token for invalid input.
- [A5] `dfam_snapshot.provenance.json`'s `source` and `role` fields are unasserted by check 31; dropping `endpoint_pattern` fails with a raw `KeyError` rather than a named diagnostic.
- Prose and comments: clean. The added OUTPUTS and README text carries no gratuitous contrastive negation (the one contrast, `unresolved/<name>` "distinct from RepeatMasker's literal `Unknown`", is the load-bearing point of ruling M2); all five new scripts carry one-line affirmative docstrings, no banners, no dates, names or review provenance.

## Numbers recomputed

| quantity | contract | observed | command |
|---|---|---|---|
| `taxonomy_canonical` rows | 18,484 | 18,484 | independent `csv` count over the built table |
| `has_multiple_labels` rows | 20 | 20 | same |
| rows `unresolved` at either rank | 0 | 0 | full-table status census |
| `family_status` over the 20 | 7 / 5 / 5 / 3 | `resolved_majority` 7, `resolved_unspecified` 5, `resolved_uncertainty_suffix` 5, `unspecified` 3 | `Counter` over multi-label rows |
| `canonical_class` over the 20 | all `DNA` | 20/20 `DNA` | same |
| min `family_majority_share` among `resolved_majority` | 0.734 | 0.734 (`MER63C`, 273/372) | full-table min |
| (h) full-table `family_status` | — | `unspecified` 17,372, `concordant` 1,095, +5 +5 +7 = 18,484 | full-table census |
| (h) full-table `class_status` | — | `concordant` 18,478, `resolved_uncertainty_suffix` 6 | same |
| independent re-derivation, 12 columns × 18,484 rows | equal | **0 mismatches** | own implementation of the four rule sentences from `rmsk_taxonomy.tsv` alone, importing nothing from `src/` or `tests/` |
| `median_divergence_pct`, all names | from `rmsk_records` | 0 mismatches | `pyarrow` batches + stdlib `statistics.median` |
| parent/child competitions | specific token | `MER53`→`hAT-Blackjack` (0.996), `UCON44`→`TcMar-Tigger` (0.967), `X4b_DNA`→`TcMar-Tigger` (0.962) | built table |
| resolution report rows | 20, `label_count > 1` | 20, names and order equal to the canonical multi-label rows | built table |
| (a) digest parity with the orchestrator's build | equal | `taxonomy_canonical` `fb5699c6…aeff`, report `6e9ca5b6…1f72` — both identical | `bash src/20_build_taxonomy.sh <scratch> config/mm39.env`; `sha256sum` |
| (d) snapshot vs evidence file | rows equal + `fetched_on` | 20/20 rows, 0 field mismatches, same order, one added column, all `fetched_on=2026-09-16` | row-by-row `csv` compare |
| (d) check 31 on a removed name / altered subtype | fails | exit 1 both (removal at `:26`, subtype with both labels printed) | scratch copies; tracked-file md5s verified unchanged before and after |
| (i) check 30 on an altered single-label canonical label | should fail | **passes, exit 0** | scratch `TE_TRACKS_REFROOT`, unchanged check |
| (e) fixture cases disagreeing with the rule text | 0 | 1 (`winning_class_abstains`) | hand computation of all 30 cases |
| mm39 names with >1 normalized class | — | 0 (B1 branch unreachable here) | `rmsk_taxonomy.tsv` |
| test suites | core passes | core 10/10 pass; consumers and acceptance register 0 checks (phases 4–5) | `tests/run.sh {core,consumers,acceptance}` |
| (g) git writes | none | `reflog -1` = the milestone 2 commit `4eb31f9`; phase 3 changes uncommitted | `git reflog -3`, `git status --short` |

Raw tables were read through symlinks and are byte-identical after the review; the stage ran with only `rmsk_taxonomy.tsv` and `rmsk_records.parquet` present in `tables/`, and `build_taxonomy.py` names no network, Dfam or fixture path. My scratch tree under `_scratch/te-tracks-audit/opus-p3/` is removed.

## Agreement with codex review

- **B1** — Agree, independently reproduced. Adds: mm39 has zero contested-class names, so fixing it moves no acceptance number (verified by applying the fix), and the amended contract now states the winning-class scope explicitly, which settles it as a code defect rather than a contract ambiguity.
- **B2** — Agree the required evidence is absent, and it exists nowhere in the repo, so it was unobtainable under the no-network constraint. The amendment is the right disposition; as written it does not yet match the file — see my B3.
- **B3** — Agree it was a scope conflict between phase 3 and phase 7. The deferral recorded at `13_phase3_taxonomy.md:53-54` resolves it; `TAXONOMY_RULE_VERSION` is in place at `build_taxonomy.py:16` and surfaces in the report's `rule_fired` column, so phase 7 has its reader.
- **A1** — Agree, and I raise it to blocking (my B2) on a wider mutation: labels, both statuses and both shares corrupted together still pass all three checks.
- **A2** — Agree, reproduced exactly.
- **A3** — Agree, and now closed: `13_phase3_taxonomy.md:44` and `:59` name the delivered paths.
- **Numeric-scope clarification** — Confirmed independently: 7/5/5/3 describes the 20 multi-label names; the full table is 17,372 `unspecified` + 1,095 `concordant` + 5 + 5 + 7.

A derived table is only as trustworthy as the check that recomputes it — a census over 20 rows cannot vouch for 18,484.
