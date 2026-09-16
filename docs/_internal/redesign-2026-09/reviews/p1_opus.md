# Phase 1 re-review (Opus)
Verdict: PASS WITH ADVISORIES

## Blocking

None. Every contract deliverable is present, every acceptance number reproduces under an independent parser and an independent multiset comparison, and both checks fail on corrupted copies.

## Advisory

- [A1] `tests/fixtures/source/expected.tsv:1`, `src/lib/rmsk_out.py:29` — the suite does not pin sign preservation on the two parenthesized left fields, the one property the contract's review focus names ("no silent absolute values"). Evidence: in a scratch copy of the repo tree, rewriting `left_bp` as `return abs(int(token[1:-1]))` leaves `tests/run.sh core` at exit 0. Every other semantic mutation I tried exits 1: C-strand consensus order not swapped, `rpartition` instead of `partition`, `C` not mapped to `-`, header skip removed, overlap flag forced False, parentheses made optional. The fixtures' only negative value, `SplitName`'s `-2`, is the unparenthesized consensus begin, which `int()` parses. Fix: add a fixture row with a negative `(left)` and assert it.
- [A2] `tests/checks/core/11_source_qualification.sh:22` — the check asserts 6 of the report's 13 summary metrics. I copied the report into a scratch refroot and changed one metric at a time: `out_rows`, `table_rows`, `matched_rows`, `unmatched_out_rows`, `field_disagreements`, a per-field count, and `Status: PASS` each exit 1; `distinct_ids`, `id_max`, `ids_contiguous`, `ids_spanning_contigs`, `starred_rows`, `coordinate_collision_pairs` each still exit 0. Two of those (4,696,900 distinct ids; ids never span two contigs) are named acceptance numbers in `11_phase1_source.md:20`. The narrow scope matches `p1_impl.md:101`. Fix: extend the zero/equality loops with the identity metrics.
- [A3] `README.md:46` — the row marks `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md` `delivered, tested`, and `README.md:40` defines `tested` as verified against its contract, while no check reads that file; check 11 reads the build copy at `$TE_TRACKS_REFROOT/te_mm39/build/source/qualification.md`. The two are byte-identical today (md5 `8f92a01349f7ae375c4c1ab334538a07`), so a hand edit to the tracked copy would pass everything. `SOURCES.json` in the `README.md:44` row has the same gap. Fix: have check 11 `cmp` the build report against the tracked copy.
- [A4] `src/lib/rmsk_out.py:13` — four parser fields are published under other names in phase 2: `perc_div` → `divergence_pct`, `perc_del` → `deletion_pct`, `perc_ins` → `insertion_pct`, `rmsk_id` → `rmsk_instance_id` as text (`ADR5_consult.md:43,44,45,50`). `raw_strand` has no published column; phase 2 adds `rmsk_record_id`, `length_bp`, `ucsc_rep_start/end/left`. On the `rmsk_id` reuse: `docs/OUTPUTS.md:28` gives that name to the UCSC one-character field with no fragment-linking meaning, and the parser's line-1 docstring gives the same name the opposite meaning — two live definitions in one repo's published docs. `int(tokens[14])` also drops the spelling ADR5:50 calls the "complete primary `.out` grouping token": `007`, `+7` and `1_000` all parse silently to integers. The integer typing earns its keep in phase 1, since `id_min`/`id_max`/`ids_contiguous` need it. Fix: name it `rmsk_instance_id` at the parser boundary and carry the raw token beside the integer.
- [A5] Silent assumptions, sorted by what the code commits to. **Defined**: a header with leading spaces (the `   SW` line in both `records.out` and the real `.out`); a negative consensus start (`-2`, asserted in `expected.tsv:6`); a two-slash class/family token (`DNA/hAT/Tip100` → family `hAT/Tip100`); an ID reused within a contig (fixture rows 4 and 5 share ID 4) with cross-contig reuse counted by `RecordStats`; gzip and plain input for correctly-suffixed paths (check 10 round-trips both). **Merely tolerated**: negative `consensus_left_bp` and `query_left_bp`, which `ADR5_consult.md:58,59` require nonnegative (I got `-7` and `-140` accepted); a chromosome name containing a colon and a repeat name containing `|`, both of which break the phase-2 `rmsk_record_id` spelling (mm39 carries zero of each across 61 contigs and 18,484 names, measured); `start_1 > end_1` and `start_1 = 0`; CRLF and tab-separated rows; three or more slashes folding into family (`a/b/c/d` → class `a`, family `b/c/d`). Fix: state the parser's domain policy in the module docstring and enforce the remaining-length constraints in phase 2.
- [A6] `src/lib/rmsk_out.py:37` — the docstring promises "malformed data raises ValueError with line and text", and decode and compression failures escape that contract because the decode happens in the `for` header, outside the `try`. Observed: gzip bytes named `.out` → `UnicodeDecodeError` at a byte offset; plain bytes named `.out.gz` → `BadGzipFile`; one non-UTF-8 byte inside an otherwise-valid row → `UnicodeDecodeError`, no line number, no path. Fix: wrap the iteration, or narrow the docstring to token-level failures.
- [A7] `src/00_fetch_sources.sh:29` — `ln "$cache" "$dest"` hardlinks the cache file into the build, so a build's retained source shares an inode with a writable cache directory (link counts 3–4 observed in both my build and the shared refroot). `cp` keeps the build's bytes independent of later cache edits, which matters once phase 7 hashes them.
- [A8] `docs/RELEASES.md:57`, `docs/PROVENANCE.md:27` — both direct a reader to run `src/99_verify.sh`, deleted this phase; `README.md:38` and `docs/OUTPUTS.md:8` still describe the legacy build products. All four sit outside the `p1_impl.md:105` allowlist, so leaving them was correct; they need the scheduled documentation phase.
- [A9] `lib/common.sh:14,15,44,52` — `builder_sha`, `builder_describe`, `assert_count` and `to_bed_start` have zero callers outside their definitions (`fetch` 1, `verify_md5` 1, `md5_of` 3). `lib/` is outside phase 1's allowed paths. Separately, `README.md:21,22` are the file's two longest lines at 156 and 155 characters against roughly 95 elsewhere.

## Numbers recomputed

Build at `_scratch/te-tracks-audit/opus-p1/build` with `TE_TRACKS_SOURCE_CACHE=_scratch/te-tracks-audit/source`; all four sources came from cache, so no network. The shared `refroot/te_mm39/build` was untouched (its `qualification.md` still carries its 08:42 mtime and md5 `8f92a01…`). Every row below comes from my own parser and projection, written from the format spec, not from `src/lib/` or `tools/`.

| quantity | contract | observed | command |
|---|---|---|---|
| records parsed | 5,320,771 | 5,320,771 | own `gzip`+`split()` reader over `mm39.fa.out.gz` |
| distinct instance ids | 4,696,900 | 4,696,900 | same pass, `dict` of id → contig |
| ids contiguous | contiguous | `id_min=1 id_max=4,696,900`, span equals count | same pass |
| ids spanning two contigs | 0 | 0 | same pass |
| starred rows | 0 | 0 | same pass |
| UCSC table rows | 5,320,771 | 5,320,771 | own 17-column reader over `rmsk.txt.gz` |
| matched rows / unmatched / field disagreements | 5,320,771 / 0 / 0 | sorted 15-field projections byte-identical on both sides | `sort -S 1G` each side, then `cmp` → exit 0 |
| coordinate-only collision pairs | 3 at chr11:67327100, chr13:58658237, chr16:37859045 (0-based) | 3 coordinates, 2 names each, at exactly those 0-based starts (`B1F`/`ORR1B1-int`, `B1_Mus1`/`ORR1B1-int`, `B1_Mur3`/`ID_B1`) | own `(chrom,start,end,strand)` → name-set scan |
| ID2 `chr1:3051045-3051146 -` | consensus start 5, end 104, left 48 | 5, 104, 48 | own C-strand field order (`t11`=left, `t12`=end, `t13`=begin) |
| `source/qualification.md` vs the retained audit report | byte-for-byte | `cmp` exit 0, both md5 `8f92a01349f7ae375c4c1ab334538a07` | `cmp`, `md5sum` |
| check 10 on a mutated `expected.tsv` | must fail | exit 1 on each of 10 single-value mutations and on a dropped row; exit 0 unmutated | scratch repo copy, tracked fixtures unchanged (md5s re-verified) |
| check 11 on a mutated report | must fail | exit 1 (see A2 for the metrics it does not cover) | scratch refroot holding the copy |
| `unsupported` path | check 11 unsupported, runner exit 0 | `unsupported  11_source_qualification.sh  unsupported: run build.sh first`, `checks=2 pass=1 fail=0 unsupported=1`, exit 0 | `tests/run.sh core --refroot <empty dir>` |

Wording: the changed and new files carry no contrastive negation in prose or comments, no dates, no names, no defect provenance. Every `not` I found is a boolean in code. The report's "Measurement references" line names the two audit scripts, which is the evidence `p1_impl.md:85` asks the report to carry. `RM_VERSION`/`RM_LIBRARY` have in-repo evidence at `AUDIT.md:134`, which quotes the pinned UCSC README.

No git write happened: `git reflog -3` still leads with `9ac83d4 HEAD@{0}: commit: Phase 0: decisions, scaffold, truth table and test runner`, and `git status --short` matches the pre-review snapshot. My scratch tree under `_scratch/te-tracks-audit/opus-p1/` is removed.

## Agreement with codex review

- A1 (four canonical renames, `rmsk_id` reuse unsafe, `int()` loses the token spelling) — agree; my A4 reaches the same four renames independently and adds that `raw_strand` is unpublished and that the integer typing is load-bearing for the phase-1 contiguity statistic.
- A2 (negative consensus start is a permissive domain assumption; `consensus_left_bp` and `query_left_bp` should be nonnegative per ADR5) — agree, and I reproduced `-7` and `-140`. My A1 sharpens it: the missing constraint is also a missing fixture, and `abs()` on those fields passes the whole suite today.
- A3 (check 11 leaves identity statistics unchecked; `ids_spanning_contigs=1` returns exit 0) — agree, confirmed, and broadened in A2 to six passing mutations.
- A4 (`builder_sha`, `builder_describe`, `assert_count`, `to_bed_start` unused; `lib/` outside scope) — agree, counts confirmed.
- A5 (stale public descriptions and the advertised deleted verifier, outside the allowlist) — agree, and add `docs/PROVENANCE.md:27`, which also instructs running `99_verify.sh`.
- Codex's acceptance table and its "both checks fail on corrupted copies" claim — agree; I reproduced every number independently and reached the same verdict on my own evidence.

A parser that reads a fixed-column source by `split()` inherits the source's whitespace habits as its grammar: it will accept a tab-separated or CRLF variant of that source without noticing the file changed shape.
