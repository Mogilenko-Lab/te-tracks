# Phase 2 review (codex gpt-6-astra)
Verdict: PASS WITH ADVISORIES

## Blocking

- None.

## Advisory

- [A1] `README.md:41` retains the source-only build description and defers the remaining artifacts, contradicting the tested rows at lines 64–72 and the updated sentence at line 106 — the fresh build produces all seven phase 2 artifacts — update this paragraph and the build/check overview at lines 21–36 together.
- [A2] `docs/OUTPUTS.md:123` leaves published legacy consumers without their schema — the diff removes the 15-column `te_loci.tsv.gz` dictionary and `te_dim.tsv` fields; the disposition table supplies replacement filenames, while `README.md:40` still identifies the legacy release as published — retain a linked legacy schema, including the UCSC `rmsk_id` meaning. The implementation prompt explicitly requested replacement, so this is a documentation continuity advisory.
- [A3] `src/15_build_universes.sh:12` makes `tests/expectations/<genome>/class_census.tsv` a production build input — this follows `docs/_internal/redesign-2026-09/prompts/p2_impl.md:76`; dropping test data from a packaged builder will break universe publication — ship this path as runtime data or move reviewed class policy into configuration in a later authorized phase, retaining count expectations in tests.

All phase deliverables exist at the prescribed paths: both stages and helpers, four record/identity artifacts, JSON and both universe tables, both expectation files, four checks, hand-authored fixtures, and the public schema/truth-table updates. All measured acceptance numbers match. The collision starts in `tests/checks/core/22_universes.py:93` are 67,327,101; 58,658,238; 37,859,046 in `start_1`; the prompt lists their UCSC 0-based starts. The builder, test schema and public table match ADR5's 24 names, order and logical types (`src/lib/records_io.py:11`, `tests/lib/records.py:14`, `docs/OUTPUTS.md:19`). Six signed `consensus_left_bp` values follow the explicit correction in `docs/_internal/redesign-2026-09/prompts/p2_impl.md:14` and `docs/_internal/redesign-2026-09/audit/AUDIT.md:151` to `docs/_internal/redesign-2026-09/consults/ADR5_consult.md:58`. The expanded census restores the 2,548 tRNA-family SINE records (1,492,624 → 1,495,172) and seven additional classes as required by the prompt.

`src/lib/build_universes.py:15` authors one definition object; lines 105–112 serialize, parse and evaluate it with the generic evaluator at line 68. This meets “no second copy of the rule lives in code”; the independent test oracle is appropriate. A tracked configuration JSON would improve policy review and reuse; the present contract permits the Python data object. Phase 3 receives all 18,504 raw triples, including the 20 ambiguous names and their 6,517 records.

`docs/OUTPUTS.md:112` correctly limits byte identity to the same builder and serialization libraries. `src/lib/build_records.py:120` writes Parquet with an Arrow-version footer; cross-host reproduction also depends on matching Arrow/compression libraries and writer options, plus pandas/Python/zlib for TSV/gzip. Observed: Python 3.11.15, pandas 2.2.3, pyarrow 25.0.0, zlib 1.2.11; footer `parquet-cpp-arrow version 25.0.0`. Record this toolchain in the publication work.

Added public prose and comments follow the affirmative wording rule; the compatibility description's legacy terminology identifies its selection policy. No added contrastive negation or review/history chatter was found.

## Acceptance re-run

The orchestrator's one-fresh-build instruction replaces the prompt's second rebuild with a read-only comparison against its existing build. The scratch reference root's `te_mm39/build` symlink resolves to my build. Outputs below are verbatim.

```text
$ export PYTHONDONTWRITEBYTECODE=1
$ export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
$ export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/refroot
$ for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok src/10_build_records.sh
syntax ok src/15_build_universes.sh
syntax ok tests/run.sh

$ { time ./build.sh --genome mm39 --build-dir /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build; echo "exit=$?"; }
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build
[build] running 00_fetch_sources.sh
[00_fetch] cache: mm39.fa.out.gz
[00_fetch] cache: rmsk.txt.gz
[00_fetch] cache: mm39.chromAlias.txt
[00_fetch] cache: mm39.chrom.sizes
[00_fetch] sources ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/source
[build] running 05_qualify_source.sh
out_rows=5320771 table_rows=5320771 matched_rows=5320771 unmatched_out_rows=0 unmatched_table_rows=0 field_disagreements=0 distinct_ids=4696900 id_min=1 id_max=4696900 ids_contiguous=1 ids_spanning_contigs=0 starred_rows=0 coordinate_collision_pairs=3
[05_qualify] qualification ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/source/qualification.md
[build] running 10_build_records.sh
records=5320771 instances=4696900 names=18484 triples=18504
[10_build_records] canonical tables ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/tables
[build] running 15_build_universes.sh
universe_name=all_rmsk records=5320771 names=18484 triples=18504 length_sum_bp=1201573004
universe_name=compat_tetranscripts_mm39 records=3799629 names=1225 triples=1245 length_sum_bp=1121476301
universe_name=interspersed records=3764949 names=1220 triples=1240 length_sum_bp=1116605808
universe_name=interspersed_plus_satellites records=3802177 names=1228 triples=1248 length_sum_bp=1121742599
universe_name=retrotransposon_derived records=3593857 names=868 triples=868 length_sum_bp=1084886912
universe_name=satellites records=37228 names=8 triples=8 length_sum_bp=5136791
[15_build_universes] universes ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/universes.json
[build] done

real	4m46.335s
user	4m31.066s
sys	0m30.692s
exit=0

$ ls -la "$TE_TRACKS_REFROOT/te_mm39/build/tables/" "$TE_TRACKS_REFROOT/te_mm39/build/universes.json"
-rw-rw-r--+ 1 devuser devgroup 2513 Sep 16 10:00 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/refroot/te_mm39/build/universes.json

/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/refroot/te_mm39/build/tables/:
total 812636
drwxrwsr-x+ 2 devuser devgroup      4096 Sep 16 10:00 .
drwxrwsr-x+ 4 devuser devgroup      4096 Sep 16 10:00 ..
-rw-rw-r--+ 1 devuser devgroup  63215760 Sep 16 09:59 rmsk_instance_members.tsv.gz
-rw-rw-r--+ 1 devuser devgroup 378232086 Sep 16 09:59 rmsk_records.parquet
-rw-rw-r--+ 1 devuser devgroup 246337861 Sep 16 09:59 rmsk_records.tsv.gz
-rw-rw-r--+ 1 devuser devgroup    815459 Sep 16 09:59 rmsk_taxonomy.tsv
-rw-rw-r--+ 1 devuser devgroup 143499930 Sep 16 10:00 universe_members.tsv.gz
-rw-rw-r--+ 1 devuser devgroup       325 Sep 16 10:00 universe_summary.tsv

$ cat "$TE_TRACKS_REFROOT/te_mm39/build/tables/universe_summary.tsv"
universe_name	records	names	triples	length_sum_bp
all_rmsk	5320771	18484	18504	1201573004
compat_tetranscripts_mm39	3799629	1225	1245	1121476301
interspersed	3764949	1220	1240	1116605808
interspersed_plus_satellites	3802177	1228	1248	1121742599
retrotransposon_derived	3593857	868	868	1084886912
satellites	37228	8	8	5136791

$ zcat "$TE_TRACKS_REFROOT/te_mm39/build/tables/rmsk_records.tsv.gz" | head -3
rmsk_record_id	chrom	start_1	end_1	strand	rmsk_name	rmsk_family	rmsk_class	rmsk_instance_id	sw_score	divergence_pct	deletion_pct	insertion_pct	length_bp	consensus_start_1	consensus_end_1	consensus_left_bp	query_left_bp	rmsk_overlap_flag	rmsk_class_family	ucsc_rep_start	ucsc_rep_end	ucsc_rep_left	source_row_number
L1MdA_VI|chr1:3050294-3050775|+	chr1	3050294	3050775	+	L1MdA_VI	L1	LINE	1	3667	6.7	0.0	1.0	482	6094	6570	6	192103504	false	LINE/L1	6094	6570	-6	1
ID2|chr1:3051045-3051146|-	chr1	3051045	3051146	-	ID2	ID	SINE	2	242	26.5	2.2	3.9	102	5	104	48	192103133	false	SINE/ID	-48	104	5	2

$ sha256sum "$TE_TRACKS_REFROOT/te_mm39/build/tables/"*.gz "$TE_TRACKS_REFROOT/te_mm39/build/tables/"*.parquet
c8d0d19d9a97eb4e7cc49e765d5abc228cf1b27e0773999fadf6f9758ebc9589  /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/refroot/te_mm39/build/tables/rmsk_instance_members.tsv.gz
1df8eb9da246daa435eb9aea53a4eaf64bbfea699afe25226d3a06740b022016  /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/refroot/te_mm39/build/tables/rmsk_records.tsv.gz
bb851f1004e7a0b7e9f397de6ef569b3da4e2dbb19c8e2c75452ad3140b250c8  /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/refroot/te_mm39/build/tables/universe_members.tsv.gz
d5deabd4ae015204a2277093bf41ef4bbb597a74313e54d13e0f479eab17f33a  /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/refroot/te_mm39/build/tables/rmsk_records.parquet

$ sha256sum /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/tables/* /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/* /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/universes.json /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/universes.json | sort -k2 | awk '{print $1, $2}'
c8d0d19d9a97eb4e7cc49e765d5abc228cf1b27e0773999fadf6f9758ebc9589 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_instance_members.tsv.gz
d5deabd4ae015204a2277093bf41ef4bbb597a74313e54d13e0f479eab17f33a /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_records.parquet
1df8eb9da246daa435eb9aea53a4eaf64bbfea699afe25226d3a06740b022016 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_records.tsv.gz
ee26c6aa3cf867219cea4f298f5c7262e10d1d90243a6321d7b374c6cb3d545c /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_taxonomy.tsv
bb851f1004e7a0b7e9f397de6ef569b3da4e2dbb19c8e2c75452ad3140b250c8 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/universe_members.tsv.gz
66c205dfe7025a512de76fa7f0332b551e02e7f2b98b8c62319440af2b4b9458 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/universe_summary.tsv
f5563514a65538af20b8f480d8562b54c99edd4d61e2d3d4c8a1e12e509c6509 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/universes.json
c8d0d19d9a97eb4e7cc49e765d5abc228cf1b27e0773999fadf6f9758ebc9589 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/tables/rmsk_instance_members.tsv.gz
d5deabd4ae015204a2277093bf41ef4bbb597a74313e54d13e0f479eab17f33a /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/tables/rmsk_records.parquet
1df8eb9da246daa435eb9aea53a4eaf64bbfea699afe25226d3a06740b022016 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/tables/rmsk_records.tsv.gz
ee26c6aa3cf867219cea4f298f5c7262e10d1d90243a6321d7b374c6cb3d545c /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/tables/rmsk_taxonomy.tsv
bb851f1004e7a0b7e9f397de6ef569b3da4e2dbb19c8e2c75452ad3140b250c8 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/tables/universe_members.tsv.gz
66c205dfe7025a512de76fa7f0332b551e02e7f2b98b8c62319440af2b4b9458 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/tables/universe_summary.tsv
f5563514a65538af20b8f480d8562b54c99edd4d61e2d3d4c8a1e12e509c6509 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build/universes.json

$ diff <(cd /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build && sha256sum tables/* universes.json) <(cd /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build && sha256sum tables/* universes.json); echo "digest_diff_exit=$?"
digest_diff_exit=0

$ tests/run.sh core --refroot /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/refroot; echo "exit=$?"
pass  10_rmsk_out_parser.py  6 expected records; plain/gzip, signed consensus, ID tokens, malformed/unreadable input and ID statistics pass
pass  11_source_qualification.sh  13 summary metrics and 10 field disagreements verified; reports identical; four source md5s match config pins
pass  20_records_schema.py  5320771 records; 24 typed columns; all rows and 10000 sampled rows equal; identities and bounds pass
pass  21_instances.py  4696900 instances; one instance per record; single contig; sizes 1=4251251 2=338697 3+=106952
pass  22_universes.py  six universe summaries and every membership match; 17 classes; 3 collision pairs; 20 multi-label names / 6517 records
pass  23_records_fixtures.py  hand-authored records, collisions, text IDs, signed fields, instances, bounds, joins, census and tRNA-family rules pass
checks=6 pass=6 fail=0 unsupported=0
exit=0
```

All four new checks also returned exit 3 and `unsupported: run build.sh first` against an absent scratch root (`tests/lib/records.py:31`). Each mutation below ran independently in a fresh `/tmp` copy with `python3 tests/checks/core/23_records_fixtures.py`; production files and expectations stayed unchanged.

| Isolated mutation | Result |
|---|---|
| Unmodified fixture baseline | exit 0; all fixture assertions pass |
| `src/lib/build_records.py:102`: add `ascending=False` | exit 1; `tests/checks/core/23_records_fixtures.py:49` rejects record order |
| `src/lib/build_universes.py:81`: replace OR accumulation with AND (`&=`) | exit 1; `tests/checks/core/23_records_fixtures.py:55` rejects universe summary |
| `src/lib/build_universes.py:123`: force `provisional` to `False` | exit 1; `tests/checks/core/23_records_fixtures.py:62` rejects missing flags |
| `src/lib/build_universes.py:104`: remove census gate call | exit 1; `tests/checks/core/23_records_fixtures.py:95` reaches line 33: `AssertionError: accepted invalid fixture: ('class census gate', 'Novel')` |

## Scope check

Implementation changes stay within `src/**`, `tests/**`, `docs/OUTPUTS.md`, and the allowed README rows/sentence. The 27 untracked source/test files include every reported helper, check, expectation and fixture. Outside that set, status lists orchestration prompts: `p2_opus.md` and `p2_review.md` were present at initial inspection; the three `m2_*.md` prompts appeared during review. Their headers identify later review tasks. This reviewer wrote only this report in the repository and removed the owned build, scratch reference root and mutation copies. No git writes, installs or network access occurred.

Status captured before writing this report:
```text
$ git status --short
 M README.md
 M docs/OUTPUTS.md
 D tests/expectations/mm39_class_counts.tsv
?? docs/_internal/redesign-2026-09/prompts/m2_codex.md
?? docs/_internal/redesign-2026-09/prompts/m2_divergent.md
?? docs/_internal/redesign-2026-09/prompts/m2_opus.md
?? docs/_internal/redesign-2026-09/prompts/p2_opus.md
?? docs/_internal/redesign-2026-09/prompts/p2_review.md
?? src/10_build_records.sh
?? src/15_build_universes.sh
?? src/lib/build_records.py
?? src/lib/build_universes.py
?? src/lib/records_io.py
?? tests/checks/core/20_records_schema.py
?? tests/checks/core/21_instances.py
?? tests/checks/core/22_universes.py
?? tests/checks/core/23_records_fixtures.py
?? tests/expectations/mm39/
?? tests/fixtures/records/
?? tests/lib/

$ git diff HEAD --stat
 README.md                                |  20 ++--
 docs/OUTPUTS.md                          | 162 ++++++++++++++++++++-----------
 tests/expectations/mm39_class_counts.tsv |  10 --
 3 files changed, 115 insertions(+), 77 deletions(-)
```
