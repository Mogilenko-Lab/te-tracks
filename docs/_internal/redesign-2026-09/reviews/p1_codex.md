# Phase 1 review (codex gpt-6-astra)
Verdict: PASS WITH ADVISORIES

## Blocking

None. Every phase 1 deliverable is present, every measured acceptance value agrees, and both checks fail on corrupted copies.

## Advisory

- [A1] `src/lib/rmsk_out.py:13` — Four parser fields need explicit canonical mappings: `perc_div` → `divergence_pct`, `perc_del` → `deletion_pct`, `perc_ins` → `insertion_pct`, and integer `rmsk_id` → text `rmsk_instance_id`. `raw_strand` has no published column; phase 2 additionally supplies `rmsk_record_id`, `length_bp`, `ucsc_rep_start`, `ucsc_rep_end`, and `ucsc_rep_left`. Evidence: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/12_phase2_canonical.md:7` delegates the schema to `docs/_internal/redesign-2026-09/consults/ADR5_consult.md:40`; `docs/_internal/redesign-2026-09/prompts/p2_impl.md:43` requires that order and types. Reusing `rmsk_id` is unsafe as an undocumented consumer interface: `docs/OUTPUTS.md:28` gives that name to the unrelated UCSC one-character field. Current qualification correctly excludes UCSC `id`. Make the phase 2 mapping explicit and check complete source-token preservation: `int(tokens[14])` at parser line 64 loses spelling such as leading zeroes, while ADR5 line 50 requires the complete token.
- [A2] `tests/fixtures/source/records.out:10`, `src/lib/rmsk_out.py:29` — `SplitName` explicitly expects `consensus_start_1=-2` in `expected.tsv:6`. Phase 1 specifies signed-value preservation and field normalization, with no consensus-domain bounds; accepting negative consensus starts is a permissive domain assumption in that phase, consistent with ADR5's explicit source-overhang contract at `docs/_internal/redesign-2026-09/consults/ADR5_consult.md:56`. A separate probe also accepted `consensus_left_bp=-7` and `query_left_bp=-140`; ADR5 lines 58–59 require those remaining-length fields to be nonnegative. State the parser's domain policy and enforce the canonical remaining-length constraints in phase 2; preserve legitimate overhang starts.
- [A3] `tests/checks/core/11_source_qualification.sh:22` — The retained-report check covers row matching and disagreements, leaving identity statistics unchecked. A copied report with `matched_rows=5,320,770` failed with exit 1; changing only `ids_spanning_contigs` to 1 returned exit 0. This meets the narrow check contract in `docs/_internal/redesign-2026-09/prompts/p1_impl.md:99`; the full-source run independently reproduced correct identity statistics. Cover distinct IDs, contig scope, and the other pinned summary values in the phase 2 checks or extend this check.
- [A4] `lib/common.sh:14` — `builder_sha`, `builder_describe`, and `assert_count` remain after this phase removes their callers; searches of current executable sources find only their definitions (lines 14, 15, 44). `to_bed_start` at line 52 is also unused, and was already unused at HEAD. Schedule cleanup when `lib/` is in scope; phase 1's allowed paths exclude it.
- [A5] `README.md:38`, `docs/OUTPUTS.md:8`, `docs/RELEASES.md:57` — Public descriptions still say the current build generates legacy tables/manifests and advertise the deleted verifier. The completed build contains only six source-layer files. These unchanged passages sit outside the implementer's permitted edits; update them in the scheduled documentation phases. The removed README cache sentence remains publicly available at `docs/RELEASES.md:66`, which explicitly states that `/data2/users/shared/refcache` is mounted read-only into the container.

## Acceptance re-run

Paths below are repository-relative unless absolute. The phase contract is `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/11_phase1_source.md`; the executable acceptance commands and allowed set are in `docs/_internal/redesign-2026-09/prompts/p1_impl.md`.

| Deliverable | Evidence |
|---|---|
| `config/mm39.env` | Lines 2–22 retain assembly/FASTA declarations, supply all four matching pins and the declared profile/version/library/evidence, and remove the specified gene/filter/expectation keys. |
| `src/00_fetch_sources.sh` | Lines 20–61 verify pins, reuse matching cache files, and write `source/SOURCES.json`; all four hardlinks, byte counts, and run-identity metadata verified independently. |
| `src/lib/rmsk_out.py` | Lines 36–81 implement typed, numbered records, header/blank recognition, two parenthesized left fields, strand/consensus normalization, literal names and split-once class/family; malformed input includes physical line and text. |
| Qualification tool, stage, and audit | `tools/qualify_source.py:65` preserves multiplicity and compares all ten shared fields; `src/05_qualify_source.sh:14` runs it. The rebuilt report exactly matches `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md`. |
| Build and legacy removal | `build.sh:37` uses the explicit directory and numeric stages; all four required legacy scripts are deleted. README changes are confined to Build and source truth-table rows. |
| Fixtures and core checks | `records.out`, `malformed.out`, and `expected.tsv` under `tests/fixtures/source/` cover every required case. Both checks are executable (mode 775); `tests/expectations/mm39_class_counts.tsv` is unchanged. |

Changed public prose and comments contain no gratuitous contrastive negation, implementation history, or reviewer chatter. Source metadata and audit citations supply the required qualification evidence.

The review build was initially absent, so the clean-start deletion was unnecessary. Every build/read command below uses the isolated directory. The core runner receives a temporary reference-root symlink to that directory; the shared reference build remains untouched.

```bash
cd /workspaces/Meta-Aging/01_modules/te-tracks
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export REVIEW_BUILD=/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p1/build
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
./build.sh --genome mm39 --build-dir "$REVIEW_BUILD"; echo "exit=$?"
```
```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok tests/run.sh
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p1/build
[build] running 00_fetch_sources.sh
[00_fetch] cache: mm39.fa.out.gz
[00_fetch] cache: rmsk.txt.gz
[00_fetch] cache: mm39.chromAlias.txt
[00_fetch] cache: mm39.chrom.sizes
[00_fetch] sources ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p1/build/source
[build] running 05_qualify_source.sh
out_rows=5320771 table_rows=5320771 matched_rows=5320771 unmatched_out_rows=0 unmatched_table_rows=0 field_disagreements=0 distinct_ids=4696900 id_min=1 id_max=4696900 ids_contiguous=1 ids_spanning_contigs=0 starred_rows=0 coordinate_collision_pairs=3
[05_qualify] qualification ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p1/build/source/qualification.md
[build] done
exit=0
```
```bash
ls -la "$REVIEW_BUILD/source/"
```
```text
total 303960
drwxrwsr-x+ 2 devuser devgroup      4096 Sep 16 08:46 .
drwxrwsr-x+ 3 devuser devgroup      4096 Sep 16 08:45 ..
-rw-rw-r--+ 4 devuser devgroup      3478 Sep 15 00:01 mm39.chromAlias.txt
-rw-rw-r--+ 3 devuser devgroup      1350 Sep 15 00:14 mm39.chrom.sizes
-rw-rw-r--+ 3 devuser devgroup 169199039 Sep 15 00:05 mm39.fa.out.gz
-rw-rw-r--+ 1 devuser devgroup      2346 Sep 16 08:46 qualification.md
-rw-rw-r--+ 3 devuser devgroup 142017372 Sep 15 00:01 rmsk.txt.gz
-rw-rw-r--+ 1 devuser devgroup      1029 Sep 16 08:45 SOURCES.json
```
```bash
python3 src/lib/rmsk_out.py count "$REVIEW_BUILD/source/mm39.fa.out.gz"
python3 -B src/lib/rmsk_out.py head "$REVIEW_BUILD/source/mm39.fa.out.gz" 3
```
```text
records=5320771 distinct_ids=4696900 ids_spanning_contigs=0 starred_rows=0
source_row_number	sw_score	perc_div	perc_del	perc_ins	chrom	start_1	end_1	query_left_bp	raw_strand	strand	rmsk_name	rmsk_class_family	rmsk_class	rmsk_family	consensus_start_1	consensus_end_1	consensus_left_bp	rmsk_id	rmsk_overlap_flag
1	3667	6.7	0.0	1.0	chr1	3050294	3050775	192103504	+	+	L1MdA_VI	LINE/L1	LINE	L1	6094	6570	6	1	0
2	242	26.5	2.2	3.9	chr1	3051045	3051146	192103133	C	-	ID2	SINE/ID	SINE	ID	5	104	48	2	0
3	13	11.6	0.0	6.7	chr1	3051160	3051191	192103088	+	+	(TGCT)n	Simple_repeat	Simple_repeat	Simple_repeat	1	30	0	3	0
```
```bash
tail -n 30 docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md
```
```text
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
```
```bash
cmp "$REVIEW_BUILD/source/qualification.md" docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md; echo "report_cmp_exit=$?"
python3 -B - <<'PY'
import os, subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory(prefix='te-tracks-p1-core-') as refroot:
    family = Path(refroot) / 'te_mm39'
    family.mkdir()
    (family / 'build').symlink_to(os.environ['REVIEW_BUILD'], target_is_directory=True)
    run = subprocess.run(['tests/run.sh', 'core', '--refroot', refroot], env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    print(f'exit={run.returncode}')
PY
```
```text
report_cmp_exit=0
pass  10_rmsk_out_parser.py  5 expected records; plain/gzip, ID2 consensus, malformed rows and ID statistics pass
pass  11_source_qualification.sh  5,320,771 matched rows; zero unmatched rows and field disagreements
checks=2 pass=2 fail=0 unsupported=0
exit=0
```

Additional `/tmp` probes used a hand-authored five-row UCSC table: all ten individually changed shared fields returned exit 1 with `field_disagreements=1`; extra duplicates on either side and a changed join key failed; equal duplicate multiplicity with reversed table order passed. Unmatched examples capped correctly at 20 of 25. A corrupted expected score made the parser check exit 1; an absent qualification report returned exit 3 with `unsupported: run build.sh first`. A changed matched-row metric failed; the identity-metric gap is A3. All temporary copies were removed.

## Scope check

`git status --short` and `git diff HEAD --stat` before writing this review:
```text
 M README.md
 M build.sh
 M config/mm39.env
 M src/00_fetch_sources.sh
 D src/10_build_master.sh
 D src/90_manifest.sh
 D src/99_verify.sh
 D src/release.sh
?? docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md
?? docs/_internal/redesign-2026-09/prompts/p1_opus.md
?? docs/_internal/redesign-2026-09/prompts/p1_review.md
?? src/05_qualify_source.sh
?? src/lib/
?? tests/checks/core/10_rmsk_out_parser.py
?? tests/checks/core/11_source_qualification.sh
?? tests/fixtures/
?? tools/
 README.md               | 16 +++++------
 build.sh                | 56 +++++++++++++++----------------------
 config/mm39.env         | 74 +++++++++----------------------------------------
 src/00_fetch_sources.sh | 74 ++++++++++++++++++++++++++++++++++---------------
 src/10_build_master.sh  | 69 ---------------------------------------------
 src/90_manifest.sh      | 59 ---------------------------------------
 src/99_verify.sh        | 60 ---------------------------------------
 src/release.sh          | 71 -----------------------------------------------
 8 files changed, 94 insertions(+), 385 deletions(-)
```
All implementer-reported changes are within the allowed set. Expanded untracked directories contain only the reported parser, qualification tool, and three source fixtures. The two extra prompt files contain orchestration instructions; they are outside the implementation allowlist and absent from the implementer's file report. `p1_review.md` was present at initial inspection; `p1_opus.md` appeared during review setup.

Repository content/mode fingerprints were unchanged through testing. The sole review write is this file. No git writes, installs, or network requests were performed; the latest reflog entry remains `9ac83d4 commit: Phase 0: decisions, scaffold, truth table and test runner`. The isolated build and its empty parent were removed; cleanup printed `review build removed`.
