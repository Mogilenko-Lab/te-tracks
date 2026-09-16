# te-tracks phase 1: fix loop after review

You are the implementer for phase 1 of the te-tracks redesign, returning to fix review findings. Working
directory (absolute): `/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Your
earlier phase 1 work is in the working tree (uncommitted).

Read both reviews first: `docs/_internal/redesign-2026-09/reviews/p1_codex.md` and
`docs/_internal/redesign-2026-09/reviews/p1_opus.md`. Both pass with advisories; the orchestrator rules that
the items below are fixed now, before the phase commits. Then re-read the phase contract
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/11_phase1_source.md`, the phase 2 record schema
in `docs/_internal/redesign-2026-09/prompts/p2_impl.md` (the column list) and
`docs/_internal/redesign-2026-09/consults/ADR5_consult.md` lines 40 to 60. Wording rules:
`/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".

## Resolutions (the orchestrator's rulings; implement exactly)
- **F1, field names (codex A1, Opus A4).** `FIELDS` in `src/lib/rmsk_out.py` uses the phase 2 names:
  `divergence_pct`, `deletion_pct`, `insertion_pct` and `rmsk_instance_id`. `rmsk_instance_id` is the complete
  `.out` ID token as a string, validated against `^[0-9]+$`; statistics that need an integer
  (`RecordStats`, `id_min`, `id_max`, `ids_contiguous` in `tools/qualify_source.py`) convert it where they use
  it. `raw_strand` stays. Update the module docstring, `tests/fixtures/source/expected.tsv` (header only),
  `tests/checks/core/10_rmsk_out_parser.py` (its int, float and string field sets) and the `head` CLI output,
  which prints `FIELDS` as its header.
- **F2, domain policy (codex A2, Opus A1, A5).** `left_bp` accepts only a nonnegative integer inside
  parentheses; a negative left quantity is malformed. Consensus start and end stay signed integers (source
  overhang). The module docstring states the domain in two or three lines: whitespace-separated tokens,
  15 fields plus an optional `*`, both left quantities parenthesized and nonnegative, consensus start and
  end signed, the ID token digits only, names and class tokens taken verbatim. Add malformed cases to the
  check's `bad_rows`: `(-1)` in field 8, `(-6)` in field 14, and `(6)` in field 15 (the ID slot), and add the
  assertion that the `SplitName` row still yields `consensus_start_1 = -2`.
- **F3, unreadable input (Opus A6).** `iter_records` converts decode and gzip failures into `ValueError`
  carrying the path (and the line number when one is known), so the docstring's promise holds for every
  failure. Add one check case: gzip bytes under a `.out` name raise `ValueError` mentioning the path.
- **F4, check 11 coverage (codex A3, Opus A2, A3).** `tests/checks/core/11_source_qualification.sh` asserts
  every summary metric: `out_rows`, `table_rows`, `matched_rows` = 5,320,771; `unmatched_out_rows`,
  `unmatched_table_rows`, `field_disagreements`, `ids_spanning_contigs`, `starred_rows` = 0;
  `distinct_ids` = 4,696,900; `id_min` = 1; `id_max` = 4,696,900; `ids_contiguous` = 1;
  `coordinate_collision_pairs` = 3; every per-field disagreement = 0; `Status: PASS.` present. It then
  compares the build report byte-for-byte (`cmp`) with the tracked copy
  `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md`, located relative to the check's own
  path, and asserts that the four md5 values in `<build>/source/SOURCES.json` equal the pins in
  `config/mm39.env`. The pass message names what was verified in one line.
- **F5, cache copy (Opus A7).** `src/00_fetch_sources.sh` copies a matching cache file (`cp`) so the build's
  bytes are independent of the cache; the hardlink branch goes. The comment states that intent in one line.
- **F6, dead helpers (codex A4, Opus A9).** Remove `builder_sha`, `builder_describe`, `assert_count` and
  `to_bed_start` from `lib/common.sh` together with their comment lines. Keep `log`, `die`, `md5_of`,
  `verify_md5`, `fetch`, `LC_ALL`, `umask`, `set -euo pipefail`, `REPO_ROOT`.
- **F7, public prose (codex A5, Opus A8).** `README.md` line 38 and `docs/OUTPUTS.md` line 8 read:
  "Published legacy releases in the reference cache carry `te_loci.tsv.gz`, `te_dim.tsv`, `MANIFEST.json` and
  `BUILD_ID`; the current build produces the source layer under `source/`, and the redesign phases supply the
  remaining artifacts." The `docs/OUTPUTS.md` heading `## Built today` becomes `## Published legacy release`.
  In `docs/RELEASES.md`, replace the "Verifying a snapshot" section body (code block and sentence) with one
  sentence: "Phase 7 supplies the snapshot verification command together with the new manifest; a
  transferred legacy snapshot is checked by recomputing the md5s listed in its `MANIFEST.json`." In
  `docs/PROVENANCE.md` line 27, replace "`99_verify.sh`" with "the legacy verifier".
- **F8, README lines (Opus A9).** Wrap `README.md` lines 21 and 22 at about 95 characters.

## Rules
Touch only: `src/lib/rmsk_out.py`, `tools/qualify_source.py`, `src/00_fetch_sources.sh`, `lib/common.sh`,
`tests/fixtures/source/expected.tsv` (header), `tests/checks/core/10_rmsk_out_parser.py`,
`tests/checks/core/11_source_qualification.sh`, `README.md` (lines 21, 22, 38), `docs/OUTPUTS.md` (line 8 and
the heading), `docs/RELEASES.md` (the one section), `docs/PROVENANCE.md` (the one phrase). Regenerate the
tracked report `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md` only if its content
changes (the ID rename must leave it byte-identical; report a deviation if it changes). No git writes,
installs or network. Report a deviation instead of editing a number, a fixture value or a plan file to fit.

## Acceptance (run and paste verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
rm -rf "$TE_TRACKS_REFROOT/te_mm39/build"
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
./build.sh --genome mm39 --build-dir "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
stat -c '%h %n' "$TE_TRACKS_REFROOT"/te_mm39/build/source/*        # link count 1 for every file
python3 src/lib/rmsk_out.py count "$TE_TRACKS_REFROOT/te_mm39/build/source/mm39.fa.out.gz"
python3 src/lib/rmsk_out.py head "$TE_TRACKS_REFROOT/te_mm39/build/source/mm39.fa.out.gz" 2
cmp "$TE_TRACKS_REFROOT/te_mm39/build/source/qualification.md" docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md && echo "report identical"
tests/run.sh core; echo "exit=$?"
grep -n -E "\brmsk_id\b|perc_div|perc_del|perc_ins" src tools tests README.md docs/OUTPUTS.md -r || echo "no stale names"
grep -n -E "builder_sha|builder_describe|assert_count|to_bed_start" -r lib src tools tests || echo "no dead helpers"
grep -n -E "99_verify|Built today|current build generates" README.md docs/*.md || echo "no stale prose"
awk 'length > 100 {print FILENAME": "FNR": "length}' README.md || true
git status --short
```
Mutation probes (scratch copies under `/workspaces/Meta-Aging/_scratch/`, removed afterwards; paste outputs):
1. A copy of the build report with `ids_spanning_contigs` set to 1 → check 11 exit 1.
2. A copy of the tracked report with one byte changed, presented as the tracked copy → check 11 exit 1.
3. `left_bp` replaced by `abs(int(token[1:-1]))` in a scratch copy of the tree → check 10 exit 1.

## Final message
Each finding with what changed (file and line range); acceptance and probe outputs verbatim; any
deviation.
