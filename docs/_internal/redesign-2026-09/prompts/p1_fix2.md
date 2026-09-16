# te-tracks phase 1: second fix loop, signed consensus left

You are the implementer for phase 1 of the te-tracks redesign, returning after the first fix round.
Working directory (absolute): `/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`.
Your phase 1 work and the first fix round are in the working tree (uncommitted).

Your first-round report stopped the build on ruling F2: the pinned source holds six rows whose consensus-left
value is negative. The measurement is recorded in `docs/_internal/redesign-2026-09/audit/AUDIT.md` section 7
(read it): all six are on the `C` strand, zero rows carry a negative query-left value, and UCSC matches all
six under its signed encoding. The ruling is revised below. Wording rules: `/workspaces/Meta-Aging/AGENTS.md`
sections "Prose" and "Comments".

## Resolutions (the orchestrator's rulings; implement exactly)
- **F2 revised, domain policy.** `query_left_bp` is a parenthesized nonnegative integer. `consensus_left_bp`
  is a parenthesized signed integer; a negative value records an alignment that runs past the consensus end.
  Consensus start and end stay signed. Implement two decoders (or one with a sign flag) so each field's
  rule is explicit. The module docstring states the domain in two or three lines with this distinction.
- **Fixture.** Append the real source row from line 669264 to `tests/fixtures/source/records.out`, verbatim:
  `  332  26.5  1.2  0.0  chr11     21327149 21327231 (100646138) C  Charlie17      DNA/hAT-Charlie     (-1847) 2634   2551 590512`
  and its hand-authored row to `tests/fixtures/source/expected.tsv`: source_row_number 6, sw_score 332,
  divergence 26.5, deletion 1.2, insertion 0.0, chr11, start_1 21327149, end_1 21327231, query_left_bp
  100646138, raw_strand C, strand -, rmsk_name Charlie17, class/family token `DNA/hAT-Charlie`, class DNA,
  family hAT-Charlie, consensus_start_1 2551, consensus_end_1 2634, consensus_left_bp -1847,
  rmsk_instance_id 590512, overlap flag 0.
- **Check 10.** Update the expected statistics (6 records, 5 distinct ids, 0 spanning, 1 starred) and the pass
  message. Remove `(13, "(-6)")` from `bad_rows` and add a positive assertion that `(-6)` in the `+`-strand
  consensus-left slot parses to `consensus_left_bp == -6`. Keep `(7, "(-1)")` malformed (query left).
  Add the assertion that the Charlie17 row yields `consensus_left_bp == -1847`.
- **Report.** The rebuilt `source/qualification.md` must stay byte-identical to the tracked
  `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md`; a difference is a deviation to report,
  with both files' differing lines.

## Rules
Touch only `src/lib/rmsk_out.py`, `tests/fixtures/source/records.out`, `tests/fixtures/source/expected.tsv`
and `tests/checks/core/10_rmsk_out_parser.py`. No git writes, installs or network. Report a deviation instead
of editing a number, a fixture value, the tracked report or a plan file to fit.

## Acceptance (run and paste verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
python3 - <<'PY'
import shutil, pathlib
p = pathlib.Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build')
shutil.rmtree(p, ignore_errors=True); print('clean:', not p.exists())
PY
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
./build.sh --genome mm39 --build-dir "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
python3 src/lib/rmsk_out.py count "$TE_TRACKS_REFROOT/te_mm39/build/source/mm39.fa.out.gz"
python3 src/lib/rmsk_out.py head "$TE_TRACKS_REFROOT/te_mm39/build/source/mm39.fa.out.gz" 2
zcat "$TE_TRACKS_REFROOT/te_mm39/build/source/mm39.fa.out.gz" | sed -n '669264p'
cmp "$TE_TRACKS_REFROOT/te_mm39/build/source/qualification.md" docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md && echo "report identical"
tests/run.sh core; echo "exit=$?"
grep -c "(-1847)" tests/fixtures/source/records.out tests/fixtures/source/expected.tsv
git status --short
```
Mutation probe (scratch copy of the tree under `/workspaces/Meta-Aging/_scratch/`, removed afterwards): the
consensus-left decoder replaced by `abs(int(token[1:-1]))` → check 10 exit 1, quoting the assertion.

## Final message
What changed (file and line range); acceptance and probe outputs verbatim; any deviation.
