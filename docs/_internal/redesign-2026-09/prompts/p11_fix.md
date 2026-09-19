# te-tracks claim-validation fix (codex)

Working directory `/workspaces/Meta-Aging/01_modules/te-tracks`, branch `redesign-2026-09`, HEAD
`26f0c7e` with the parking pass uncommitted in the worktree. Three validators read disjoint scopes
and found 30 false claims. You correct exactly those, and nothing else.

Read first, in this order:
- `docs/_internal/redesign-2026-09/reviews/p11_rulings.md` — the dispositions that bind you
- `docs/_internal/redesign-2026-09/reviews/p11_outputs.md`
- `docs/_internal/redesign-2026-09/reviews/p11_publication.md`
- `docs/_internal/redesign-2026-09/reviews/p11_narrative.md`

Each review gives every finding a quoted original and a proposed correction. Apply the correction
unless the rulings document says otherwise.

## Touch only

`README.md`, `docs/OUTPUTS.md`, `docs/RELEASES.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`.

Change nothing under `docs/_internal/`. The reviews and rulings record what was said and stay as
they are. If a correction seems to require editing anything outside the list, stop and report it in
your final message instead of doing it.

## The corrections

1. **outputs F1 to F7** — restore the `tables/` prefix on every companion path at
   `docs/OUTPUTS.md:27-33`. Verify each corrected path exists under a real archive before writing it.
2. **outputs F8, F9, F12** — apply the reviews' corrections. F9 and F12 were independently
   reproduced by the orchestrator; the numbers in the rulings are measured, use them.
3. **outputs F10, F11** — state the private per-run fixture directory and the
   `TE_TRACKS_CONSUMER_FIXTURES` override, matching what `tests/run.sh` now does.
4. **publication F1, F5, F6** — apply as written. F6 also needs the imperative at
   `docs/RUNBOOK.md:304-306` to gain the restore-write-access step.
5. **publication F2, F3, F4 and narrative F11** — the consuming module directory is now
   `/workspaces/Meta-Aging/01_modules/te-quant`. Replace every `01_modules/te-consumers` path.
   **Leave `/workspaces/Meta-Aging/.venv/te-consumers` exactly as it is** — the installed
   environment keeps that path and both validators confirmed it is correct. Check the whole of
   `docs/` for other occurrences of the old module path, not only the cited lines.
6. **narrative F3 to F8** — one class. `docs/DECISIONS.md` states deferred products in the present
   tense so proposals read as published tables. Recast those six sections so a reader can tell what
   exists from what is designed. Keep every parameter and threshold the sections record.
7. **narrative F9, F10, F12** — apply as written.
8. **narrative F2** — `README.md:105`. The on-disk surface is 28 core checks, 16 consumer checks of
   which 15 pass and one is unsupported, and 11 acceptance checks. The orchestrator ran all three
   suites: core 28 pass 0 fail, consumers 15 pass 1 unsupported 0 fail, acceptance 11 pass 0 fail,
   every command exit 0. State the fresh-build acceptance count only if you verify it without
   running a build.
9. **narrative F1** — the rulings override the review here. Replace `README.md:6` with exactly:

   `Counts carry no record of the annotation they came from, so two analyses cannot be shown to share one.`

## Constraints

- No git writes of any kind. No installs. No network. Scratch under
  `_scratch/te-tracks-audit/p11fix/`, removed with Python `shutil`; `/tmp` is noexec. Set
  `PYTHONDONTWRITEBYTECODE=1`.
- Do not weaken, skip or delete any test. Report a blocking test by name.
- Do not change a claim the validators marked true. After editing, the numbers, paths and
  behaviours a reader can act on must be the same as before except where a finding required it.
- `README.md` stays under 120 lines and keeps opening from the owner's problem.
- Prose states what a thing is. No contrastive negation. Comments state intent only.
- The shell's `grep` is `ugrep --ignore-files` and silently skips ignored paths. Use
  `/usr/bin/grep` for any sweep that must be complete.

## Acceptance

Run these yourself and report each result:

```
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export PYTHONDONTWRITEBYTECODE=1
source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh
bash tests/run.sh core          # expect 28 pass 0 fail, exit 0
bash tests/run.sh consumers     # expect 15 pass 1 unsupported 0 fail, exit 0
bash tests/run.sh acceptance    # expect 11 pass 0 fail, exit 0
```

Also report: `/usr/bin/grep -rn '01_modules/te-consumers' docs/ README.md AGENTS.md` returns
nothing, `wc -l README.md` is at most 120, and for each of the 30 findings one line naming the file,
the line, and the corrected text.

## Final message

A table of the 30 findings with their disposition, the three suite results, any correction you
refused and why, and any claim you found false that no validator caught.
