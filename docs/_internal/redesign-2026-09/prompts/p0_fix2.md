# te-tracks phase 0: second fix loop, after the Opus re-review

You are the implementer for phase 0 of the te-tracks redesign, returning to fix re-review findings. Working
directory (absolute): `/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Your
earlier work is in the working tree (uncommitted): `README.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`,
`docs/DECISIONS.md`, `docs/OUTPUTS.md`, `tests/run.sh`, `tests/checks/*/.gitkeep`.

Read the re-review first: `docs/_internal/redesign-2026-09/reviews/p0_opus.md` (the codex review it
builds on is `reviews/p0_codex.md`). Then the phase contract
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/10_phase0_decisions_scaffold.md`, the export
contract `14_phase4_exports.md` (GeneID of `taxonomy_triple.saf`), the preflight contract
`16_phase6_ensembl_preflight.md`, and entry 5 of `01_decisions.md` (the ledger sentence, already
corrected there). Wording rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".

## Resolutions (the orchestrator's rulings; implement exactly)
- **B1, `taxonomy_triple.saf` labels.** In the phase 4 table of `docs/OUTPUTS.md`, the row reads
  `Canonical taxonomy-triple grouping; GeneID = <rmsk_name>:<canonical_family>:<canonical_class>`
  (backticks around the code parts). Below the table add one sentence: canonical labels are a function of
  the name, so `taxonomy_triple.saf` carries one `GeneID` per `rmsk_name`, and a name whose raw labels
  differ across records appears once, under its canonical triple.
- **B2, ledger sentence.** Replace the last sentence of `docs/DECISIONS.md` entry 5 with the text now in
  `01_decisions.md` entry 5: "Consuming projects keep their quantification ledger in their own tables,
  `peak_record_overlaps` and `te_feature_registration`, keyed to `rmsk_records`, with `feature_level` as
  the measurement grain column."
- **A1, preflight signature.** `docs/OUTPUTS.md` phase 6: `bin/te-tracks-preflight <export> <bam|fai|sizes>`
  checks contig sets and lengths for the selected export against an alignment, a FASTA index or a
  chrom.sizes file.
- **A2, truth table.** Add the row `docs/RELEASES.md | deferred | 7` next to the `docs/RUNBOOK.md` row.
  The expectations move is covered by the existing `tests/expectations/mm39/` row; no further row.
- **A3.** No change: the table tracks redesign artifacts and the sentence above it names the legacy
  outputs generated today.
- **A4, runner semantics in `AGENTS.md`.** Replace the paragraph after the command block with: "The
  default `TE_TRACKS_REFROOT` is `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`; `--refroot DIR`
  selects another scratch root for any mode and is exported as an absolute path. Checks are
  `tests/checks/<mode>/*.sh` and `*.py`, run in name order through `bash` or `python3` regardless of file
  mode. A check exit of 0 is pass, 3 is unsupported and any other exit is fail. A failing check makes the
  runner exit 1, as does an unsupported check whose name ends in `.required.sh` or `.required.py`. Bad
  usage and a missing check directory exit 2."
- **A5, dangling symlink.** In `tests/run.sh`, a `*.sh` or `*.py` entry that is a symlink to a missing
  target is reported as `fail  <name>  dangling symlink`, counted as a failure, and makes the runner exit 1.
- **A6, relative `--refroot`.** Resolve a relative `--refroot` against the caller's working directory
  before `cd "$REPO_ROOT"`, so the exported `TE_TRACKS_REFROOT` is always absolute.
- **A7, swallowed diagnostics.** On `fail`, print the check's complete stdout to stderr after the status
  line, each line indented two spaces. Pass and unsupported keep the one-line form.
- **`.gitignore`.** Delete the line `!tests/expectations/*.tsv`; `!tests/expectations/**` covers it.

## Rules
Touch only `README.md`, `AGENTS.md`, `docs/DECISIONS.md`, `docs/OUTPUTS.md`, `tests/run.sh` and
`.gitignore`. No git writes, installs or network. Report a deviation instead of editing a plan file or a
review file. Comments in `tests/run.sh` state intent in one line; no history.

## Acceptance (run and paste verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
for m in core consumers acceptance; do tests/run.sh $m; echo "exit=$?"; done
tests/run.sh bogus; echo "exit=$?"
grep -n -E "\bnot\b|rather than|instead of|never|no longer|unlike|doesn't" README.md AGENTS.md docs/DECISIONS.md docs/OUTPUTS.md || echo "no hits"
grep -n -E "raw taxonomy-triple|Ledger tables|<bam\|fai>|expectations/\*\.tsv" README.md AGENTS.md docs/DECISIONS.md docs/OUTPUTS.md .gitignore || echo "no hits"
grep -n "rmsk_name>:<canonical_family>:<canonical_class>" docs/OUTPUTS.md
grep -n "RELEASES.md" README.md
grep -c "^| " README.md      # report the number; it is one more than before your edit
git status --short
```

Scratch harness, under `/workspaces/Meta-Aging/_scratch/` (the `/tmp` filesystem is noexec): copy
`tests/run.sh` and `lib/common.sh` into a throwaway tree with an empty `tests/checks/core/`, and run each
case alone, pasting output and exit:
1. `fail.sh` exiting 9 → `fail`, exit 1.
2. `optional.sh` exiting 3 → `unsupported`, exit 0.
3. `need.required.sh` exiting 3 → `unsupported`, exit 1.
4. `hidden.required.py` mode 0644 raising `SystemExit(1)` → `fail`, exit 1.
5. `ln -s /nonexistent/zzz tests/checks/core/dangling.sh` → `fail  dangling.sh  dangling symlink`, exit 1.
6. `verbose.sh` printing three lines then exiting 1 → status line, then all three lines on stderr, exit 1.
7. `probe.sh` printing `$TE_TRACKS_REFROOT`, run as `cd /workspaces/Meta-Aging/_scratch && <copy>/tests/run.sh core --refroot ./relroot` → `refroot=/workspaces/Meta-Aging/_scratch/relroot`, exit 0.
8. Empty check directory → `no checks registered`, exit 0; removed directory → runner error, exit 2.
Remove the throwaway tree afterwards.

## Final message
Each finding with what changed (file and line range); acceptance and harness outputs verbatim; any
deviation.
