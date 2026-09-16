# te-tracks phase 1 review (codex, read-only)

You are an independent reviewer of phase 1 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p1_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/11_phase1_source.md`
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
  bite phase 2.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 1 review (codex gpt-6-astra)
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
- Run every acceptance command that builds into your own directory,
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p1/build`, and leave
  `$TE_TRACKS_REFROOT/te_mm39/build` untouched; other processes read it. The source cache is
  `TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source` (all four files present).
  Remove your build directory when done.
- Compare the parser's output field names (`src/lib/rmsk_out.py` `FIELDS`) with the phase 2 record schema in
  `12_phase2_canonical.md` and `docs/_internal/redesign-2026-09/prompts/p2_impl.md`; name every field whose
  name differs from the column phase 2 will publish. `docs/OUTPUTS.md` describes the legacy `rmsk_id` as the
  UCSC one-character field; judge whether the parser's use of the same name for the `.out` ID is safe.
- The fixture row `SplitName ... (7) 18 -2 4` gives a negative consensus start; say whether the parser's
  acceptance of negative consensus coordinates is a contract or an assumption.
- `lib/common.sh` keeps helpers whose callers were deleted in this phase; list them.
- The removed README sentence about the read-only reference cache: is that fact still stated in a public
  file consumers read?

## Implementer report
Implemented phase 1. Qualification reproduced **5,320,771 matched rows**, **zero unmatched rows or field disagreements**, **4,696,900 contiguous IDs**, **zero cross-contig IDs**, **zero starred rows**, and **three collision pairs**. Both core checks pass.

Repository files, one per line:

- Changed [config/mm39.env](/workspaces/Meta-Aging/01_modules/te-tracks/config/mm39.env): source pins and declared run identity.
- Changed [build.sh](/workspaces/Meta-Aging/01_modules/te-tracks/build.sh): explicit build directory and ordered stages.
- Changed [src/00_fetch_sources.sh](/workspaces/Meta-Aging/01_modules/te-tracks/src/00_fetch_sources.sh): verified cache reuse and source metadata.
- Created [src/05_qualify_source.sh](/workspaces/Meta-Aging/01_modules/te-tracks/src/05_qualify_source.sh): qualification stage.
- Created [src/lib/rmsk_out.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/lib/rmsk_out.py): parser and count/head CLI.
- Created [tools/qualify_source.py](/workspaces/Meta-Aging/01_modules/te-tracks/tools/qualify_source.py): streaming multiset comparison and report.
- Created [records.out](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/source/records.out): valid parser fixtures.
- Created [malformed.out](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/source/malformed.out): malformed fixture.
- Created [expected.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/source/expected.tsv): hand-authored parsed expectations.
- Created [10_rmsk_out_parser.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/10_rmsk_out_parser.py): executable parser check.
- Created [11_source_qualification.sh](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/11_source_qualification.sh): executable qualification check.
- Created [source_qualification_mm39.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md): full qualification evidence.
- Changed [README.md](/workspaces/Meta-Aging/01_modules/te-tracks/README.md): Build section and source truth-table rows.
- Deleted `src/10_build_master.sh`.
- Deleted `src/90_manifest.sh`.
- Deleted `src/99_verify.sh`.
- Deleted `src/release.sh`.

Acceptance outputs, verbatim:

```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok tests/run.sh
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build
[build] running 00_fetch_sources.sh
[00_fetch] cache: mm39.fa.out.gz
[00_fetch] cache: rmsk.txt.gz
[00_fetch] cache: mm39.chromAlias.txt
[00_fetch] cache: mm39.chrom.sizes
[00_fetch] sources ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/source
[build] running 05_qualify_source.sh
out_rows=5320771 table_rows=5320771 matched_rows=5320771 unmatched_out_rows=0 unmatched_table_rows=0 field_disagreements=0 distinct_ids=4696900 id_min=1 id_max=4696900 ids_contiguous=1 ids_spanning_contigs=0 starred_rows=0 coordinate_collision_pairs=3
[05_qualify] qualification ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/source/qualification.md
[build] done
exit=0
```

```text
total 303960
drwxrwsr-x+ 2 devuser devgroup      4096 Sep 16 08:39 .
drwxrwsr-x+ 3 devuser devgroup      4096 Sep 16 08:38 ..
-rw-rw-r--+ 3 devuser devgroup      3478 Sep 15 00:01 mm39.chromAlias.txt
-rw-rw-r--+ 2 devuser devgroup      1350 Sep 15 00:14 mm39.chrom.sizes
-rw-rw-r--+ 2 devuser devgroup 169199039 Sep 15 00:05 mm39.fa.out.gz
-rw-rw-r--+ 1 devuser devgroup      2346 Sep 16 08:39 qualification.md
-rw-rw-r--+ 2 devuser devgroup 142017372 Sep 15 00:01 rmsk.txt.gz
-rw-rw-r--+ 1 devuser devgroup      1029 Sep 16 08:38 SOURCES.json
records=5320771 distinct_ids=4696900 ids_spanning_contigs=0 starred_rows=0
source_row_number	sw_score	perc_div	perc_del	perc_ins	chrom	start_1	end_1	query_left_bp	raw_strand	strand	rmsk_name	rmsk_class_family	rmsk_class	rmsk_family	consensus_start_1	consensus_end_1	consensus_left_bp	rmsk_id	rmsk_overlap_flag
1	3667	6.7	0.0	1.0	chr1	3050294	3050775	192103504	+	+	L1MdA_VI	LINE/L1	LINE	L1	6094	6570	6	1	0
2	242	26.5	2.2	3.9	chr1	3051045	3051146	192103133	C	-	ID2	SINE/ID	SINE	ID	5	104	48	2	0
3	13	11.6	0.0	6.7	chr1	3051160	3051191	192103088	+	+	(TGCT)n	Simple_repeat	Simple_repeat	Simple_repeat	1	30	0	3	0
| field | disagreements |
|---|---:|
| swScore | 0 |
| milliDiv | 0 |
| milliDel | 0 |
| milliIns | 0 |
| genoLeft | 0 |
| repClass | 0 |
| repFamily | 0 |
| repStart | 0 |
| repEnd | 0 |
| repLeft | 0 |

## Unmatched .out rows

Count: 0.

## Unmatched UCSC table rows

Count: 0.

## Coordinate-only collision pairs

Pairs group `.out` rows by `(chrom, start_1, end_1, strand)` and distinct names; `start_0` aligns with the audit coordinates.

| chrom | start_0 | start_1 | end_1 | strand | name_a | name_b |
|---|---:|---:|---:|---|---|---|
| chr11 | 67327100 | 67327101 | 67327210 | - | B1F | ORR1B1-int |
| chr13 | 58658237 | 58658238 | 58658287 | - | B1_Mus1 | ORR1B1-int |
| chr16 | 37859045 | 37859046 | 37859109 | + | B1_Mur3 | ID_B1 |
pass  10_rmsk_out_parser.py  5 expected records; plain/gzip, ID2 consensus, malformed rows and ID statistics pass
pass  11_source_qualification.sh  5,320,771 matched rows; zero unmatched rows and field disagreements
checks=2 pass=2 fail=0 unsupported=0
exit=0
 M README.md
 M build.sh
 M config/mm39.env
 M src/00_fetch_sources.sh
 D src/10_build_master.sh
 D src/90_manifest.sh
 D src/99_verify.sh
 D src/release.sh
?? docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md
?? src/05_qualify_source.sh
?? src/lib/
?? tests/checks/core/10_rmsk_out_parser.py
?? tests/checks/core/11_source_qualification.sh
?? tests/fixtures/
?? tools/
```

Additional checks passed for duplicate multiplicity, all ten field-disagreement cases, unmatched-row limits, cache hardlinks, metadata, report equality and allowed-path scope. No git writes, installs or network requests were performed.

No measured deviations. The cleanup command was rejected by automatic review because `rm -f` style commands are prohibited; the target directory was already absent, so the clean build proceeded. Existing legacy-output prose outside the permitted README sections remains unchanged.

