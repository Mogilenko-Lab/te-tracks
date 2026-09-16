# te-tracks phase 3 fix re-review (codex, read-only)

You are an independent reviewer of the phase 3 fix round of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`, uncommitted tree over `4eb31f9`). The
fix implementer has finished; you judge the result against the rewritten contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p3_codex2.md`. You change nothing else. No git writes, no installs, no network.

## Read
1. The contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md` (rewritten;
   authoritative for every column, status, token, check and number).
2. The rulings behind it: `docs/_internal/redesign-2026-09/reviews/p3_rulings.md`; the three reviews of the first
   implementation: `reviews/p3_codex.md`, `reviews/p3_opus.md`, `reviews/p3_divergent.md`.
3. The fix prompt: `docs/_internal/redesign-2026-09/prompts/p3_fix.md`, and the implementer's report below.
4. The changes: `git diff HEAD --stat`, the full diff, and every untracked file under `src/`, `tests/`.
5. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".

## Judge, with evidence
- **Contract conformance**: every deliverable and number in the plan file; run the taxonomy stage into your own
  directory (`/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3b/build/tables/` with symlinks to the
  orchestrator's `rmsk_taxonomy.tsv` and `rmsk_records.parquet` under
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/`, read-only) and compare both
  output digests with the orchestrator's (`a3663b64…` canonical, `1f8c068f…` report). Remove your directory when done.
- **Rulings closed**: for each of codex B1 to B3, A1 to A3, Opus B1 to B3, A1 to A5, divergent H1 to H5, M1 to M7,
  L1 to L3, one line: closed by which change, or open.
- **Fixture adequacy** (scratch copies only; verify tracked files by md5 before and after): check 30 fails when one
  canonical label of a single-label name is altered in a copy of the table; check 31 fails with both name lists
  printed when a report name is removed from a snapshot copy, and passes when a concordant name is added to the
  snapshot with agreeing labels; check 31 fails on a missing provenance key with a named diagnostic; check 32 fails
  when `resolve` is made to weight by record count (swap the caller's column in a copy) through the instance-weighting
  fixture and not only through a rollup assertion; check 22 or 23 fails when `instance_count` is dropped from a copy
  of `rmsk_taxonomy.tsv`.
- **Silent assumptions**: anything the rewritten checks still hardcode; anything that will bite phase 4 (the
  `unresolved_class_<name>` / `unresolved_family_<name>` tokens, the `taxonomy_canonical` columns phase 4 reads).
- **Wording rule** on every new or changed sentence and comment in `src/`, `tests/`, `docs/OUTPUTS.md`, `README.md`.
- **Scope**: files touched outside the fix prompt's allowed set.

## Output format (the review file)
```
# Phase 3 fix re-review (codex gpt-6-astra)
Verdict: PASS | PASS WITH ADVISORIES | BLOCKING
## Blocking
- [B1] <file:line> <finding> — <evidence> — <what fixes it>
## Advisory
- [A1] ...
## Rulings closed
<one line per finding>
## Acceptance re-run
<commands and outputs, verbatim>
## Scope check
<git status / diff --stat summary>
```
Keep the file under 200 lines. Facts over opinions; every finding cites a path and, where possible, a line.

## Implementer report
Implemented the corrected contract. All ten core checks pass, all six stable digests match, and the measured census matches the plan. Deviations: none.

Changed repository files:

- [src/lib/build_records.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/lib/build_records.py)
- [src/lib/build_taxonomy.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/lib/build_taxonomy.py)
- [tests/lib/records.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/lib/records.py)
- [20_records_schema.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/20_records_schema.py)
- [22_universes.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/22_universes.py)
- [23_records_fixtures.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/23_records_fixtures.py)
- [30_taxonomy_canonical.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/30_taxonomy_canonical.py)
- [31_taxonomy_dfam_agreement.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/31_taxonomy_dfam_agreement.py)
- [32_taxonomy_rule_fixtures.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/32_taxonomy_rule_fixtures.py)
- [tests/fixtures/records/expected_taxonomy.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/records/expected_taxonomy.tsv)
- [dfam_snapshot.provenance.json](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/taxonomy/dfam_snapshot.provenance.json)
- [rollup_counts.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/taxonomy/rollup_counts.tsv)
- [rule_cases.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/taxonomy/rule_cases.tsv)
- [weighting_context.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/taxonomy/weighting_context.tsv)
- [tests/expectations/mm39/taxonomy_census.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/expectations/mm39/taxonomy_census.tsv)
- [docs/OUTPUTS.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/OUTPUTS.md)
- [README.md](/workspaces/Meta-Aging/01_modules/te-tracks/README.md)

Acceptance output follows verbatim, including the three new SHA-256 digests. The status command was rerun after removing the bytecode cache generated by the required probe.

```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok src/10_build_records.sh
syntax ok src/15_build_universes.sh
syntax ok src/20_build_taxonomy.sh
syntax ok tests/run.sh
records=5320771 instances=4696900 names=18484 triples=18504
[10_build_records] canonical tables ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables

real	3m12.954s
user	2m56.721s
sys	0m21.861s
exit=0
universe_name=all_rmsk records=5320771 names=18484 triples=18504 length_sum_bp=1201573004
universe_name=compat_tetranscripts_mm39 records=3799629 names=1225 triples=1245 length_sum_bp=1121476301
universe_name=interspersed records=3764949 names=1220 triples=1240 length_sum_bp=1116605808
universe_name=interspersed_plus_satellites records=3802177 names=1228 triples=1248 length_sum_bp=1121742599
universe_name=retrotransposon_derived records=3593857 names=868 triples=868 length_sum_bp=1084886912
universe_name=satellites records=37228 names=8 triples=8 length_sum_bp=5136791
[15_build_universes] universes ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/universes.json
exit=0
names=18484 multi_label_names=20 taxonomy_rule_version=taxonomy_rule_v1
[20_build_taxonomy] canonical taxonomy ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables
exit=0
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_instance_members.tsv.gz: OK
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_records.parquet: OK
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_records.tsv.gz: OK
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/universe_members.tsv.gz: OK
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/universe_summary.tsv: OK
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/universes.json: OK
26a9110fc332cbe94a05e61fa97f980b4468cfdf006a05c5b24bc22a365f1a4f  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_taxonomy.tsv
a3663b6447b409c6f87960519c2b380b62aca52063f7e0ca52f46d9cabb3b2b0  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_canonical.tsv
1f8c068fbeb3dd5aa4943556673d951feca4603e95a0b3067b629583f850d453  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_resolution_report.tsv
rmsk_name	rmsk_family	rmsk_class	record_count	instance_count	record_length_sum_bp
(A)n	Simple_repeat	Simple_repeat	43996	43926	1214091
(AA)n	Simple_repeat	Simple_repeat	2	2	43
instance_count_sum 4727623
     1	rmsk_name
     2	canonical_class
     3	canonical_family
     4	class_status
     5	family_status
     6	class_plurality_share
     7	family_plurality_share
     8	family_support_share
     9	label_count
    10	record_count
    11	instance_count
    12	record_length_sum_bp
    13	median_divergence_pct
    14	has_uncertain_source
    15	has_multiple_labels
   1095 concordant
      1 family_status
      7 resolved_plurality
      5 resolved_uncertainty_suffix
      5 resolved_unspecified
  17372 unspecified
      1 class_status
  18478 concordant
      6 resolved_uncertainty_suffix
0.84 MER63C
rmsk_name	rmsk_labels	rmsk_label_records	rule_version	canonical_class	canonical_family	class_status	family_status
Eulor5B	DNA/Crypton-A=34;DNA?/DNA?=1	DNA/Crypton-A=34;DNA?/DNA?=1	taxonomy_rule_v1	DNA	Crypton-A	resolved_uncertainty_suffix	resolved_unspecified
Eulor6A	DNA/Crypton=19;DNA?/DNA?=1	DNA/Crypton=19;DNA?/DNA?=1	taxonomy_rule_v1	DNA	Crypton	resolved_uncertainty_suffix	resolved_unspecified
Eulor8	DNA/TcMar=102;DNA/TcMar?=1	DNA/TcMar=104;DNA/TcMar?=2	taxonomy_rule_v1	DNA	TcMar	concordant	resolved_uncertainty_suffix
Eutr15	DNA/hAT-Tip100=105;DNA/hAT-Tip100?=1	DNA/hAT-Tip100=109;DNA/hAT-Tip100?=2	taxonomy_rule_v1	DNA	hAT-Tip100	concordant	resolved_uncertainty_suffix
Eutr16	DNA/hAT-Tip100=95;DNA?/hAT-Tip100?=1	DNA/hAT-Tip100=98;DNA?/hAT-Tip100?=2	taxonomy_rule_v1	DNA	hAT-Tip100	resolved_uncertainty_suffix	resolved_uncertainty_suffix
Eutr2	DNA/MULE-MuDR=40;DNA/DNA=4	DNA/MULE-MuDR=40;DNA/DNA=7	taxonomy_rule_v1	DNA	MULE-MuDR	concordant	resolved_unspecified
Eutr2B	DNA/MULE-MuDR=64;DNA/DNA=7	DNA/MULE-MuDR=68;DNA/DNA=7	taxonomy_rule_v1	DNA	MULE-MuDR	concordant	resolved_unspecified
MER121	DNA/hAT=548;DNA/hAT?=4	DNA/hAT=555;DNA/hAT?=6	taxonomy_rule_v1	DNA	hAT	concordant	resolved_uncertainty_suffix
MER124	DNA/DNA=246;DNA?/DNA?=1	DNA/DNA=247;DNA?/DNA?=2	taxonomy_rule_v1	DNA	DNA	resolved_uncertainty_suffix	unspecified
MER131	DNA/DNA=473;DNA?/DNA?=1	DNA/DNA=474;DNA?/DNA?=1	taxonomy_rule_v1	DNA	DNA	resolved_uncertainty_suffix	unspecified
MER136	DNA/Merlin=21;DNA/DNA=1	DNA/Merlin=21;DNA/DNA=2	taxonomy_rule_v1	DNA	Merlin	concordant	resolved_unspecified
MER53	DNA/hAT-Blackjack=1579;DNA/hAT=4	DNA/hAT-Blackjack=1633;DNA/hAT=7	taxonomy_rule_v1	DNA	hAT-Blackjack	concordant	resolved_plurality
MER63A	DNA/hAT-Tip100=700;DNA/hAT-Blackjack=1	DNA/hAT-Tip100=714;DNA/hAT-Blackjack=1	taxonomy_rule_v1	DNA	hAT-Tip100	concordant	resolved_plurality
MER63B	DNA/hAT-Tip100=400;DNA/hAT-Blackjack=11	DNA/hAT-Tip100=417;DNA/hAT-Blackjack=21	taxonomy_rule_v1	DNA	hAT-Tip100	concordant	resolved_plurality
MER63C	DNA/hAT-Tip100=246;DNA/hAT-Blackjack=47	DNA/hAT-Tip100=273;DNA/hAT-Blackjack=99	taxonomy_rule_v1	DNA	hAT-Tip100	concordant	resolved_plurality
MER63D	DNA/hAT-Tip100=897;DNA/hAT-Blackjack=49	DNA/hAT-Tip100=935;DNA/hAT-Blackjack=111	taxonomy_rule_v1	DNA	hAT-Tip100	concordant	resolved_plurality
MER99	DNA/hAT=138;DNA/hAT?=18	DNA/hAT=148;DNA/hAT?=35	taxonomy_rule_v1	DNA	hAT	concordant	resolved_uncertainty_suffix
UCON2	DNA/DNA=99;DNA?/DNA?=1	DNA/DNA=99;DNA?/DNA?=2	taxonomy_rule_v1	DNA	DNA	resolved_uncertainty_suffix	unspecified
UCON44	DNA/TcMar-Tigger=87;DNA/TcMar=2	DNA/TcMar-Tigger=87;DNA/TcMar=3	taxonomy_rule_v1	DNA	TcMar-Tigger	concordant	resolved_plurality
X4b_DNA	DNA/TcMar-Tigger=125;DNA/TcMar=3	DNA/TcMar-Tigger=125;DNA/TcMar=5	taxonomy_rule_v1	DNA	TcMar-Tigger	concordant	resolved_plurality
metric	value
names	18484
multi_label_names	20
raw_triples	18504
instance_count_sum	4727623
class_status.concordant	18478
class_status.resolved_uncertainty_suffix	6
class_status.resolved_plurality	0
class_status.unresolved	0
family_status.concordant	1095
family_status.resolved_uncertainty_suffix	5
family_status.resolved_unspecified	5
family_status.resolved_plurality	7
family_status.unspecified	17372
family_status.unresolved	0
multi_label_class_status.concordant	14
multi_label_class_status.resolved_uncertainty_suffix	6
multi_label_class_status.resolved_plurality	0
multi_label_class_status.unresolved	0
multi_label_family_status.concordant	0
multi_label_family_status.resolved_uncertainty_suffix	5
multi_label_family_status.resolved_unspecified	5
multi_label_family_status.resolved_plurality	7
multi_label_family_status.unspecified	3
multi_label_family_status.unresolved	0
minimum_family_plurality_share	0.840
minimum_family_plurality_share_name	MER63C
snapshot_rows	20
{'canonical_class': 'DNA', 'canonical_family': 'DNA', 'class_status': 'resolved_plurality', 'family_status': 'unspecified', 'class_plurality_share': 0.7, 'family_plurality_share': 0.0, 'family_support_share': 0.0, 'label_count': 2, 'instance_count': 10, 'has_uncertain_source': False, 'has_multiple_labels': True}
{'canonical_class': 'DNA', 'canonical_family': '', 'class_status': 'concordant', 'family_status': 'unresolved', 'class_plurality_share': 1.0, 'family_plurality_share': 0.5, 'family_support_share': 0.5, 'label_count': 2, 'instance_count': 4, 'has_uncertain_source': False, 'has_multiple_labels': True}
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
 M README.md
 M docs/OUTPUTS.md
 M src/lib/build_records.py
 M tests/checks/core/20_records_schema.py
 M tests/checks/core/22_universes.py
 M tests/checks/core/23_records_fixtures.py
 M tests/lib/records.py
?? src/20_build_taxonomy.sh
?? src/lib/build_taxonomy.py
?? tests/checks/core/30_taxonomy_canonical.py
?? tests/checks/core/31_taxonomy_dfam_agreement.py
?? tests/checks/core/32_taxonomy_rule_fixtures.py
?? tests/expectations/mm39/taxonomy_census.tsv
?? tests/fixtures/records/expected_taxonomy.tsv
?? tests/fixtures/taxonomy/
```
