# te-tracks phase 9: acceptance and parking

You are the implementer for phase 9 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phases 0 to 8 have landed. Read
`AGENTS.md`, `README.md`, `build.sh`, `src/`, `tests/`, `docs/*.md`, and the plan file
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/19_phase9_acceptance_park.md`.

## Deliverables
1. `tests/checks/acceptance/`: a full in-container acceptance suite that runs against a fresh build of both
   families into `$TE_TRACKS_REFROOT/acceptance/` (`--root` mode: `te_mm39` then `te_mm39_gene`) and
   compares every measured number from phases 1 to 8 with `tests/expectations/mm39/` (the expectation files
   are authored independently of the build under test: copy nothing from build outputs into them; where a
   number exists only in a build table, the check states the expected value literally). One check per
   phase area (`10_source`, `20_records_universes`, `30_taxonomy`, `40_exports`, `60_namespaces`,
   `70_publication`, `80_gene_child`), each exit 3 with `unsupported: run tests/run.sh acceptance --build`
   when the acceptance root lacks the builds. Add `tests/run.sh acceptance --build` (a flag the runner passes
   as `TE_TRACKS_ACCEPTANCE_BUILD=1` so the first check performs the two builds).
2. `docs/RUNBOOK.md` (host runbook): prerequisites and versions (python 3, pyarrow, pandas, numpy, pysam,
   bash, coreutils; the exact versions the container has, read them and state them), the writable host root
   `/data2/users/shared/refcache` versus the read-only container mount, the source cache and how to seed it,
   `build.sh --genome mm39 --root <refroot>` then the child with `--config config/mm39_gene.env --root`,
   verification (`src/release.py verify-current`), transfer to the CRI root
   (`/gpfs/data/rathmell-lab/data/refdata`) via staging and `install`, interruption recovery, resolving
   `current` once per consumer operation and pinning the id.
3. `README.md` truth table updated to `delivered` and `tested` per artifact as observed by the acceptance
   run; `AGENTS.md` final (test commands including acceptance; the host-only steps named);
   `docs/OUTPUTS.md`, `docs/PROVENANCE.md` (rewritten: the sources, the qualification report summary, the
   measured numbers, the class census, the taxonomy rule evidence) and `docs/RELEASES.md` accurate to the
   bytes the acceptance build produced.
4. A parking summary for the orchestrator (in your final message, the orchestrator writes the session record):
   what is published locally in `$TE_TRACKS_REFROOT/acceptance/` with both `BUILD_ID`s, what is tested, what
   is unsupported (tool executables), what is deferred (hg38, transcript context, ERV units, age tiers), and
   the next gates.

## Rules
- Touch only: `tests/checks/acceptance/**`, `tests/run.sh` (the `--build` flag), `docs/RUNBOOK.md`,
  `docs/PROVENANCE.md`, `docs/RELEASES.md`, `docs/OUTPUTS.md`, `README.md`, `AGENTS.md`.
- No git writes. No installs. No network. Never write into the refcache.
- Report a deviation instead of editing a number or an expectation to fit.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
rm -rf "$TE_TRACKS_REFROOT/acceptance"
time tests/run.sh acceptance --build; echo "exit=$?"
tests/run.sh acceptance; echo "exit=$?"
tests/run.sh core; echo "exit=$?"
tests/run.sh consumers; echo "exit=$?"
cat "$TE_TRACKS_REFROOT/acceptance/te_mm39/current/BUILD_ID" "$TE_TRACKS_REFROOT/acceptance/te_mm39_gene/current/BUILD_ID"
grep -c "| delivered\|| tested" README.md; grep -c "| deferred" README.md
git status --short
```

## Final message
Every file created or changed; acceptance outputs verbatim; both BUILD_IDs; the parking summary; any deviation.
