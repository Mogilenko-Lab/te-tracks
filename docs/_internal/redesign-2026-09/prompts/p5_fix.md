# te-tracks phase 5 fix: review findings

You are the implementer for the phase 5 fix round of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, uncommitted phase 5 tree from
`prompts/p5_impl.md`. Read `docs/_internal/redesign-2026-09/reviews/p5_rulings.md` (every change below and why),
`reviews/p5_codex.md`, `reviews/p5_opus.md`, `tests/lib/consumers.py`, `tests/checks/consumers/*`,
`tests/fixtures/consumers/expected.json`, and the "Consumer contracts" section of `docs/OUTPUTS.md`.

Binding prose rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".

## Changes

1. **Stellarscope parser test runs here.** `checkout_import` gains a subpackage mode (or a sibling helper) that
   loads `stellarscope/annotation/__init__.py` as a package via `importlib.util.spec_from_file_location` with
   `submodule_search_locations=[<annotation dir>]`, registers it in `sys.modules` under a private name, and imports
   `utils` and `_intervaltree` beneath it, so the top-level `stellarscope/__init__.py` (which needs
   `setuptools_scm`) never executes. `11_stellarscope_parser.py` uses it; `unsupported` names an absent
   `intervaltree` module only. Report the observed boundary result verbatim: the check passes on `0,1,1,0`, exits 3
   with the documented defect message on `0,1,1,1`, and fails on anything else. The README truth-table row and the
   OUTPUTS.md consumer-contracts row for Stellarscope state the observed status.

2. **MATES parser test runs here (codex B1, Opus B5, A5).** `14_mates_parser.py` loads only the two functions it
   exercises from `MATES/MATES/bam_processor.py` and `MATES/scripts/calculate_MU.py` in isolation (source-level
   module load or executing the needed function nodes, as the TElocal check does). Where the exercised path imports
   `pkg_resources`, supply a minimal in-test stand-in limited to the attribute used and state that in the check's
   docstring. Work in `$TE_TRACKS_REFROOT/fixtures/consumers_scratch/mates/` and remove it; write nothing into the
   fixture input directory. The OUTPUTS.md and README rows name `pkg_resources` (setuptools below 82) as the installed
   package's dependency and drop `pyranges`.
3. **IRescue identity oracle and `chrcat` (codex B2, Opus B2, B4).** `10_irescue_parser.py` asserts, at record grain,
   that the parsed name set equals the roster's record keys and every parsed coordinate equals the roster's, and at
   subfamily grain that the names equal the roster's names; replacing every BED name or shifting every coordinate
   must fail the check. New `15_irescue_chrcat.py` runs the checkout's real `chrcat` on synthetic intersection rows
   built from `record.bed` and `subfamily.bed` and asserts the emitted identities; it reports
   `unsupported: irescue system tool gawk absent` when `gawk` is missing (it is missing here; `awk` is mawk), and
   any other failure exits 1.
4. **Import-failure classification (codex B3, Opus B3).** `run_check` (or `checkout_import`) treats a
   `ModuleNotFoundError` whose missing top-level name is outside the checkout as `unsupported: <tool> python module
   <name> absent` and every other `ImportError` (missing symbol, checkout-internal failure, bare `ImportError`) as a
   failure with exit 1 and the message. A small in-process self-test in `00_tool_inventory.py` shows a
   missing-symbol import from an installed module yields exit 1 and an absent module yields exit 3; write nothing
   under `.ref`.
5. **Fixture determinism (codex A1, Opus A1).** The five `irescue_*.tsv.gz` files that `10_irescue_parser.py` writes
   use deterministic gzip headers (mtime 0, empty filename); `13_tetranscripts_telocal_parser.py` compares the
   restored `.locInd` index semantically (feature tuples), and the OUTPUTS.md TElocal row says the pickle embeds the
   GTF path. Report the sha256 of every file under two consecutive fixture builds into two refroots and state which
   differ.
6. **Parser versions read from the checkouts (codex A2, Opus A2).** `setup.py` for TEsingle, TEtranscripts, TElocal
   and MATES; `irescue/_version.py`; Stellarscope from `git -C <checkout> describe --tags --always` (a read-only git
   command). A literal version appears nowhere in the checks; each reported line carries what was read.
7. **UMI tags, strand and flags in the fixtures (Opus A3, A4).** `tests/lib/consumers.py` writes, for a designated
   subset of molecules, a raw `UR` one base away from the corrected `UB`; adds reverse-strand reads on the two
   minus-strand roster records; adds one duplicate-flagged and one QC-fail-flagged read. `expected.json` states
   molecule counts by `UB` and by `UR` per BAM and the flagged read names, authored from the roster and the
   builder's intent. `12_tesingle_parser.py` runs the UR-cutoff path on `UR` and asserts the flagged reads are
   skipped by the checkout's read filter where it is reachable; `23_samtools_fixture_integrity.sh` asserts the new
   counts; `21_featurecounts_exec.sh` records its strand option (`-s 0`) for when the executable exists.
8. **Contract rows.** The OUTPUTS.md "Consumer contracts" section and the README truth-table row state the exercised
   support status per tool after this round, name `gawk` for the `chrcat` check, and say `00_tool_inventory.py` is
   reporting-only.

## Rules
- Touch only: `tests/lib/consumers.py`, `tests/checks/consumers/**`, `tests/fixtures/consumers/**`,
  `docs/OUTPUTS.md` (consumer contracts section), `README.md` (truth table). Nothing under `src/`; nothing under
  `01_modules/.ref/`.
- No git writes anywhere (the checkouts are git repositories). No installs. No network.
- Never edit an expected value to match an observed one; report every deviation.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
tests/run.sh consumers; echo "exit=$?"
tests/run.sh core | tail -1; echo "exit=$?"
git status --short | grep -v docs/_internal
for d in irescue stellarscope TEsingle MATES TEtranscripts TElocal; do git -C /workspaces/Meta-Aging/01_modules/.ref/$d status --short --ignored | head -3; done
```
Expected: `11_stellarscope_parser.py` reports the documented defect `unsupported` line (the orchestrator measured
`0,1,1,1`); `14_mates_parser.py` passes; `15_irescue_chrcat.py` reports `unsupported` naming `gawk`; every other
parser check passes; execution checks unchanged; runner exit 0; `core` thirteen passes; checkouts clean.

## Final message
Every file changed; acceptance outputs verbatim; the observed boundary result; any deviation.
