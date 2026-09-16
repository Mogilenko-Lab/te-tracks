# te-tracks phase 2 review (codex, read-only)

You are an independent reviewer of phase 2 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p2_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/12_phase2_canonical.md`
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
  bite phase 3.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 2 review (codex gpt-6-astra)
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
- Build once into your own directory, `/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p2/build`, with
  `TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source` (about five minutes), and
  compare the sha256 of every file under `tables/` and `universes.json` with the orchestrator's build at
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` (read it, leave it untouched).
  Run the core checks against your own build through `tests/run.sh core --refroot <a scratch refroot whose
  te_mm39/build points at your build>`. Remove your build directory when done.
- The implementer's prompt is `docs/_internal/redesign-2026-09/prompts/p2_impl.md`; the 24-column schema is
  `docs/_internal/redesign-2026-09/consults/ADR5_consult.md` section 2. Compare column names, order and
  types in `src/lib/records_io.py`, `tests/lib/records.py` and the `docs/OUTPUTS.md` table against it.
- `README.md` line 38 says the current build produces the source layer under `source/`; line 106 says it
  produces the source layer, canonical tables and universes. Judge the inconsistency.
- `docs/OUTPUTS.md` dropped the description of the published legacy release's `te_loci.tsv.gz` columns.
  Judge whether `README.md` line 38 and the "Legacy names and their disposition" table leave a consumer of
  the published legacy release with what they need.
- `src/lib/build_universes.py` holds the universe definitions as a Python dict and serializes it to
  `universes.json`; the build then evaluates the parsed JSON. Judge whether that meets "no second copy of
  the rule lives in code" and whether a tracked data file under `config/` would serve review better.
- The build reads `tests/expectations/<genome>/class_census.tsv` as its class-census gate, so a test
  expectation is a build input. Judge that dependency.
- Determinism: `pyarrow.parquet.write_table` embeds the writer version in the footer. State what the
  byte-identity claim in `docs/OUTPUTS.md` depends on.
- Fixture adequacy: on a scratch copy, break one thing at a time (sort order in `build_records.py`, the
  `or` clause evaluation, the `provisional` flag, the class-census gate) and confirm which check fails.

## Implementer report
Implemented phase 2. All six core checks pass, all supplied measurements match, and both builds have identical digests for all seven artifacts. No deviations, git writes, installs, or network access.

Changed [README.md](/workspaces/Meta-Aging/01_modules/te-tracks/README.md) and [docs/OUTPUTS.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/OUTPUTS.md).

Moved and expanded the census:
`tests/expectations/mm39_class_counts.tsv` → `tests/expectations/mm39/class_census.tsv`.

Created:

```text
src/10_build_records.sh
src/15_build_universes.sh
src/lib/build_records.py
src/lib/build_universes.py
src/lib/records_io.py
tests/checks/core/20_records_schema.py
tests/checks/core/21_instances.py
tests/checks/core/22_universes.py
tests/checks/core/23_records_fixtures.py
tests/expectations/mm39/universe_summary.tsv
tests/lib/records.py
tests/fixtures/records/beyond_end.out
tests/fixtures/records/chrom.sizes
tests/fixtures/records/class_census.tsv
tests/fixtures/records/duplicate.out
tests/fixtures/records/expected_instances.tsv
tests/fixtures/records/expected_records.tsv
tests/fixtures/records/expected_universes.tsv
tests/fixtures/records/invalid_chrom.out
tests/fixtures/records/invalid_name.out
tests/fixtures/records/missing_chrom.out
tests/fixtures/records/records.out
tests/fixtures/records/rmsk.tsv
tests/fixtures/records/spanning_instance.out
tests/fixtures/records/unreviewed.out
tests/fixtures/records/unreviewed.tsv
```

Acceptance outputs, verbatim:

```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok src/10_build_records.sh
syntax ok src/15_build_universes.sh
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
[build] running 10_build_records.sh
records=5320771 instances=4696900 names=18484 triples=18504
[10_build_records] canonical tables ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables
[build] running 15_build_universes.sh
universe_name=all_rmsk records=5320771 names=18484 triples=18504 length_sum_bp=1201573004
universe_name=compat_tetranscripts_mm39 records=3799629 names=1225 triples=1245 length_sum_bp=1121476301
universe_name=interspersed records=3764949 names=1220 triples=1240 length_sum_bp=1116605808
universe_name=interspersed_plus_satellites records=3802177 names=1228 triples=1248 length_sum_bp=1121742599
universe_name=retrotransposon_derived records=3593857 names=868 triples=868 length_sum_bp=1084886912
universe_name=satellites records=37228 names=8 triples=8 length_sum_bp=5136791
[15_build_universes] universes ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/universes.json
[build] done

real	4m46.648s
user	4m31.406s
sys	0m32.323s
exit=0
```

```text
-rw-rw-r--+ 1 devuser devgroup 2513 Sep 16 09:39 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/universes.json

/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/:
total 812636
drwxrwsr-x+ 2 devuser devgroup      4096 Sep 16 09:39 .
drwxrwsr-x+ 4 devuser devgroup      4096 Sep 16 09:39 ..
-rw-rw-r--+ 1 devuser devgroup  63215760 Sep 16 09:38 rmsk_instance_members.tsv.gz
-rw-rw-r--+ 1 devuser devgroup 378232086 Sep 16 09:38 rmsk_records.parquet
-rw-rw-r--+ 1 devuser devgroup 246337861 Sep 16 09:38 rmsk_records.tsv.gz
-rw-rw-r--+ 1 devuser devgroup    815459 Sep 16 09:38 rmsk_taxonomy.tsv
-rw-rw-r--+ 1 devuser devgroup 143499930 Sep 16 09:39 universe_members.tsv.gz
-rw-rw-r--+ 1 devuser devgroup       325 Sep 16 09:39 universe_summary.tsv
universe_name	records	names	triples	length_sum_bp
all_rmsk	5320771	18484	18504	1201573004
compat_tetranscripts_mm39	3799629	1225	1245	1121476301
interspersed	3764949	1220	1240	1116605808
interspersed_plus_satellites	3802177	1228	1248	1121742599
retrotransposon_derived	3593857	868	868	1084886912
satellites	37228	8	8	5136791
rmsk_record_id	chrom	start_1	end_1	strand	rmsk_name	rmsk_family	rmsk_class	rmsk_instance_id	sw_score	divergence_pct	deletion_pct	insertion_pct	length_bp	consensus_start_1	consensus_end_1	consensus_left_bp	query_left_bp	rmsk_overlap_flag	rmsk_class_family	ucsc_rep_start	ucsc_rep_end	ucsc_rep_left	source_row_number
L1MdA_VI|chr1:3050294-3050775|+	chr1	3050294	3050775	+	L1MdA_VI	L1	LINE	1	3667	6.7	0.0	1.0	482	6094	6570	6	192103504	false	LINE/L1	6094	6570	-6	1
ID2|chr1:3051045-3051146|-	chr1	3051045	3051146	-	ID2	ID	SINE	2	242	26.5	2.2	3.9	102	5	104	48	192103133	false	SINE/ID	-48	104	5	2
c8d0d19d9a97eb4e7cc49e765d5abc228cf1b27e0773999fadf6f9758ebc9589  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_instance_members.tsv.gz
1df8eb9da246daa435eb9aea53a4eaf64bbfea699afe25226d3a06740b022016  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_records.tsv.gz
bb851f1004e7a0b7e9f397de6ef569b3da4e2dbb19c8e2c75452ad3140b250c8  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/universe_members.tsv.gz
d5deabd4ae015204a2277093bf41ef4bbb597a74313e54d13e0f479eab17f33a  /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_records.parquet
```

Second build and digest comparison:

```text
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build2
[build] running 00_fetch_sources.sh
[00_fetch] cache: mm39.fa.out.gz
[00_fetch] cache: rmsk.txt.gz
[00_fetch] cache: mm39.chromAlias.txt
[00_fetch] cache: mm39.chrom.sizes
[00_fetch] sources ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build2/source
[build] running 05_qualify_source.sh
out_rows=5320771 table_rows=5320771 matched_rows=5320771 unmatched_out_rows=0 unmatched_table_rows=0 field_disagreements=0 distinct_ids=4696900 id_min=1 id_max=4696900 ids_contiguous=1 ids_spanning_contigs=0 starred_rows=0 coordinate_collision_pairs=3
[05_qualify] qualification ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build2/source/qualification.md
[build] running 10_build_records.sh
records=5320771 instances=4696900 names=18484 triples=18504
[10_build_records] canonical tables ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build2/tables
[build] running 15_build_universes.sh
universe_name=all_rmsk records=5320771 names=18484 triples=18504 length_sum_bp=1201573004
universe_name=compat_tetranscripts_mm39 records=3799629 names=1225 triples=1245 length_sum_bp=1121476301
universe_name=interspersed records=3764949 names=1220 triples=1240 length_sum_bp=1116605808
universe_name=interspersed_plus_satellites records=3802177 names=1228 triples=1248 length_sum_bp=1121742599
universe_name=retrotransposon_derived records=3593857 names=868 triples=868 length_sum_bp=1084886912
universe_name=satellites records=37228 names=8 triples=8 length_sum_bp=5136791
[15_build_universes] universes ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build2/universes.json
[build] done
c8d0d19d9a97eb4e7cc49e765d5abc228cf1b27e0773999fadf6f9758ebc9589 build2/tables/rmsk_instance_members.tsv.gz
d5deabd4ae015204a2277093bf41ef4bbb597a74313e54d13e0f479eab17f33a build2/tables/rmsk_records.parquet
1df8eb9da246daa435eb9aea53a4eaf64bbfea699afe25226d3a06740b022016 build2/tables/rmsk_records.tsv.gz
ee26c6aa3cf867219cea4f298f5c7262e10d1d90243a6321d7b374c6cb3d545c build2/tables/rmsk_taxonomy.tsv
bb851f1004e7a0b7e9f397de6ef569b3da4e2dbb19c8e2c75452ad3140b250c8 build2/tables/universe_members.tsv.gz
66c205dfe7025a512de76fa7f0332b551e02e7f2b98b8c62319440af2b4b9458 build2/tables/universe_summary.tsv
f5563514a65538af20b8f480d8562b54c99edd4d61e2d3d4c8a1e12e509c6509 build2/universes.json
c8d0d19d9a97eb4e7cc49e765d5abc228cf1b27e0773999fadf6f9758ebc9589 build/tables/rmsk_instance_members.tsv.gz
d5deabd4ae015204a2277093bf41ef4bbb597a74313e54d13e0f479eab17f33a build/tables/rmsk_records.parquet
1df8eb9da246daa435eb9aea53a4eaf64bbfea699afe25226d3a06740b022016 build/tables/rmsk_records.tsv.gz
ee26c6aa3cf867219cea4f298f5c7262e10d1d90243a6321d7b374c6cb3d545c build/tables/rmsk_taxonomy.tsv
bb851f1004e7a0b7e9f397de6ef569b3da4e2dbb19c8e2c75452ad3140b250c8 build/tables/universe_members.tsv.gz
66c205dfe7025a512de76fa7f0332b551e02e7f2b98b8c62319440af2b4b9458 build/tables/universe_summary.tsv
f5563514a65538af20b8f480d8562b54c99edd4d61e2d3d4c8a1e12e509c6509 build/universes.json
/workspaces/Meta-Aging/01_modules/te-tracks
```

Core checks and final status:

```text
pass  10_rmsk_out_parser.py  6 expected records; plain/gzip, signed consensus, ID tokens, malformed/unreadable input and ID statistics pass
pass  11_source_qualification.sh  13 summary metrics and 10 field disagreements verified; reports identical; four source md5s match config pins
pass  20_records_schema.py  5320771 records; 24 typed columns; all rows and 10000 sampled rows equal; identities and bounds pass
pass  21_instances.py  4696900 instances; one instance per record; single contig; sizes 1=4251251 2=338697 3+=106952
pass  22_universes.py  six universe summaries and every membership match; 17 classes; 3 collision pairs; 20 multi-label names / 6517 records
pass  23_records_fixtures.py  hand-authored records, collisions, text IDs, signed fields, instances, bounds, joins, census and tRNA-family rules pass
checks=6 pass=6 fail=0 unsupported=0
exit=0
```

```text
 M README.md
 M docs/OUTPUTS.md
 D tests/expectations/mm39_class_counts.tsv
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
```

