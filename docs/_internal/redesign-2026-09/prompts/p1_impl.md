# te-tracks phase 1: source layer

You are the implementer for phase 1 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phase 0 has landed: read
`AGENTS.md`, `README.md`, `docs/DECISIONS.md`, `tests/run.sh` to see the contract and the test runner's
check interface (`tests/checks/<mode>/*.sh` and `*.py`, run by name order through `bash` or `python3`; exit 0 pass, 3 unsupported, other fail).

## Read first
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/11_phase1_source.md` (your phase)
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` entries 5, 6, 7
3. `docs/_internal/redesign-2026-09/audit/AUDIT.md` sections F1, F3, 5 (measured facts about the sources)
4. `docs/_internal/redesign-2026-09/audit/audit_out.py` and `audit_rmsk.py` (how the numbers below were measured; write your own code, cite theirs)
5. Current `config/mm39.env`, `lib/common.sh`, `build.sh`, `src/*.sh`
6. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding for every file you write)

## Source facts (verified by the orchestrator; your code must reproduce them)
Cached pinned sources, all four present with matching checksums, at
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/source/`:
```
ffc8399d05f3388d80b78c93482a5b95  mm39.fa.out.gz        https://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/mm39.fa.out.gz
ca2e5542cab0390b5458e7935e891430  rmsk.txt.gz           https://hgdownload.soe.ucsc.edu/goldenPath/mm39/database/rmsk.txt.gz
cd2f6474b8f0bceb862719430821a33b  mm39.chromAlias.txt   https://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/mm39.chromAlias.txt
967c609a714df35c86a4f52ac85db377  mm39.chrom.sizes      https://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/mm39.chrom.sizes
```
`.out` layout: two header lines (first token `SW`, then `score`) and one blank line, then data rows of 15
whitespace-separated fields: `sw_score perc_div perc_del perc_ins chrom begin end (query_left) strand name
class/family cons_a cons_b cons_c ID`, plus an optional 16th field `*`. Strand is `+` or `C`. On `+` the
consensus fields are `begin end (left)`; on `C` they are `(left) end begin`. Parentheses wrap only the two
"left" quantities. First three data rows:
```
 3667   6.7  0.0  1.0  chr1      3050294 3050775 (192103504) +  L1MdA_VI       LINE/L1               6094 6570    (6)      1
  242  26.5  2.2  3.9  chr1      3051045 3051146 (192103133) C  ID2            SINE/ID               (48)  104      5      2
   13  11.6  0.0  6.7  chr1      3051160 3051191 (192103088) +  (TGCT)n        Simple_repeat            1   30    (0)      3
```
Matching UCSC `rmsk.txt.gz` rows (tab-separated; columns bin swScore milliDiv milliDel milliIns genoName
genoStart genoEnd genoLeft strand repName repClass repFamily repStart repEnd repLeft id):
```
608 3667  67  0 10 chr1 3050293 3050775 -192103504 + L1MdA_VI LINE          L1            6094 6570  -6 1
608  242 265 22 39 chr1 3051044 3051146 -192103133 - ID2      SINE          ID             -48  104   5 2
608   13 116  0 67 chr1 3051159 3051191 -192103088 + (TGCT)n  Simple_repeat Simple_repeat    1   30   0 3
```
So: genoStart = begin - 1; milli* = round(perc * 10); genoLeft = -(query_left); `C` -> `-`; on `+`
repStart=begin, repEnd=end, repLeft=-left; on `-` repStart=-left, repEnd=end, repLeft=begin; a `.out` token
without `/` is copied by UCSC into repFamily; UCSC `id` is a one-character field with no relation to the
`.out` ID. Measured on the full files: 5,320,771 data rows in each; 5,320,771 rows match 1:1 on
(chrom, start_1, end_1, strand, name); 4,696,900 distinct `.out` IDs, contiguous 1..4,696,900, each ID on a
single contig; zero rows carry `*`; 3 coordinate-only collisions (same chrom,start,end,strand, different
name) at chr11:67327100, chr13:58658237, chr16:37859045.

## Deliverables (exact paths)
1. `config/mm39.env` revised. Keep `GENOME`, `ASSEMBLY`, `UCSC_BASE`, `GENOME_FA_URL`, `GENOME_FA_MD5` (declared
   only). Add `RMSK_OUT_URL`, `RMSK_OUT_MD5=ffc8399d05f3388d80b78c93482a5b95`,
   `RMSK_TABLE_URL`, `RMSK_TABLE_MD5` (the current `RMSK_URL`/`RMSK_MD5`, renamed), `CHROMALIAS_URL`,
   `CHROMALIAS_MD5`, `CHROM_SIZES_URL`, `CHROM_SIZES_MD5`, `RMSK_OUT_PROFILE="rm_out_v1"`,
   `RM_VERSION="open-4.0.8"`, `RM_LIBRARY="RepBase 20181026; Dfam_Consensus 20181026"`,
   `RM_RUN_EVIDENCE="https://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/README.txt"`. Remove
   `GENE_ANNOTATION`, `GENCODE_BASE`, `GENE_GTF_URL`, `GENE_GTF_MD5` (they move to the child family config in
   phase 8), `TE_CLASSES`, `EXCLUDE_FAMILY_PREFIX`, `LOCUS_ID_FORM`, `INTERGENIC_MIN`, and every `EXPECT_*`
   key (phase 2 authors expectations under `tests/expectations/mm39/`). Every comment states intent in one
   line; no dates, no measurement history.
2. `src/00_fetch_sources.sh`: usage `00_fetch_sources.sh <build-dir> <config.env>`. Fetches the four
   sources into `<build-dir>/source/` under their URL basenames. Honors `TE_TRACKS_SOURCE_CACHE`: when set
   and the cache holds a file of that basename whose md5 matches the pin, hardlink (fall back to copy) instead
   of downloading; otherwise `fetch` from the pinned URL. Verifies every pin; writes `source/SOURCES.json`
   with url, md5, bytes per source and the declared run identity (`rm_version`, `rm_library`,
   `rm_run_evidence`, `rmsk_out_profile`).
3. `src/lib/rmsk_out.py`: parser profile `rm_out_v1` as a module with a generator
   `iter_records(path) -> dict` and a CLI (`python3 src/lib/rmsk_out.py count <out.gz>` printing records,
   distinct ids, ids spanning more than one contig, starred rows; `... head <out.gz> N` printing parsed
   rows as TSV). Header recognition by the first token; blank lines skipped; parentheses stripped only from
   the two left fields; `C` mapped to `-` with `raw_strand` kept; consensus normalized to
   `consensus_start_1, consensus_end_1, consensus_left_bp` (on `C`: left,end,start order as shown);
   `query_left_bp`; `rmsk_class_family` raw token, split once at `/` into `rmsk_class`, `rmsk_family`
   (family = class when the token has no `/`, the UCSC convention, stated in a one-line comment);
   `rmsk_overlap_flag` from `*`; `source_row_number` 1-based over data rows; a malformed row raises with
   the line number and the offending text. Integers as int, percentages as float.
4. `tools/qualify_source.py`: usage `qualify_source.py --out <out.gz> --table <rmsk.txt.gz> --report <md>`.
   Streams both files, joins on (chrom, start_1, end_1, strand, name), and compares every shared field under
   the declared conversions above (score, three milli fields, query left, class/family with the class-only
   projection, the three consensus fields in UCSC's signed encoding). Reports row counts on each side,
   matched rows, unmatched rows on each side (list up to 20), per-field disagreement counts, distinct IDs,
   IDs spanning contigs, starred rows, and the coordinate-only collision pairs. Exit 0 only when both sides
   have equal row counts, every row matches, and every field agrees. Memory is ample (500 GB) but stream
   anyway; a run takes a few minutes. Write the report to
   `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md` (the one file under `docs/_internal`
   you may write). Also register it as `src/05_qualify_source.sh <build-dir> <config.env>`, which runs the tool
   against `<build-dir>/source/` and writes the same report into `<build-dir>/source/qualification.md`.
5. Legacy removal, so the repository does exactly what exists: delete `src/10_build_master.sh`,
   `src/90_manifest.sh`, `src/99_verify.sh`, `src/release.sh` (their replacements arrive in phases 2 and 7).
   `build.sh` becomes `build.sh --genome <name> --build-dir <dir>`: runs `src/[0-9][0-9]_*.sh <dir> <config>`
   in order and stops; usage text updated; the `--dest`/`--date` snapshot logic and the release call removed.
   Update `README.md` Build section and the truth table row(s) for `source/` accordingly (one or two
   sentences). Leave `tests/expectations/mm39_class_counts.tsv` in place.
6. Fixtures under `tests/fixtures/source/`: hand-written `.out` files (plain text is fine) covering a plus
   row, a `C` row, `(TGCT)n`, a starred row, a class-only token, and a malformed row; expected parsed values
   authored by hand in a sibling `expected.tsv`. Check `tests/checks/core/10_rmsk_out_parser.py`
   (executable): parses the fixtures, asserts the expected values, asserts the malformed fixture raises with
   its line number, asserts the ID2 example (`chr1:3051045-3051146 -` -> consensus start 5, end 104,
   left 48). Check `tests/checks/core/11_source_qualification.sh` (executable): if
   `$TE_TRACKS_REFROOT/te_mm39/build/source/qualification.md` is absent, exit 3 with the message
   `unsupported: run build.sh first`; otherwise assert the report states 5,320,771 matched rows and zero
   disagreements.

## Rules
- Touch only: `config/mm39.env`, `build.sh`, `src/**`, `tools/**`, `tests/fixtures/source/**`,
  `tests/checks/core/**`, `README.md` (Build section and truth table only), `docs/OUTPUTS.md` (only if a
  sentence about sources needs the new file names), and the single report file named above.
- No git writes of any kind. No installs. Network only to the four pinned URLs, and only when the cache
  lacks a file (it lacks none).
- Report a deviation instead of editing a number, a fixture expectation, or a plan file to fit. If a
  measured value differs from the facts above, stop and report both values.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
rm -rf "$TE_TRACKS_REFROOT/te_mm39/build"
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
./build.sh --genome mm39 --build-dir "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
ls -la "$TE_TRACKS_REFROOT/te_mm39/build/source/"
python3 src/lib/rmsk_out.py count "$TE_TRACKS_REFROOT/te_mm39/build/source/mm39.fa.out.gz"
#   expect records=5320771 distinct_ids=4696900 ids_spanning_contigs=0 starred_rows=0
python3 src/lib/rmsk_out.py head "$TE_TRACKS_REFROOT/te_mm39/build/source/mm39.fa.out.gz" 3
tail -n 30 docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md
tests/run.sh core; echo "exit=$?"     # expect both checks pass
git status --short                    # only the allowed paths
```

## Final message
Every file created, changed or deleted, one line each; the acceptance outputs verbatim; the qualification
summary numbers; any deviation.
