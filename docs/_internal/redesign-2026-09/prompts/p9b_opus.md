Review phase 9b of the te-tracks redesign, the acceptance suite and the host runbook. Repository:
/workspaces/Meta-Aging/01_modules/te-tracks (git branch redesign-2026-09, HEAD `204ee66`). You are
read-only: no edits, no git writes, no installs, no network.

No review of phase 9b exists yet. A codex reviewer is working in parallel on a different question, the
release as a whole at its consumer seam, so do not spend effort on runbook followability or on the
consumer map. Your question is narrower and harder: **can this acceptance suite fail?**

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/19_phase9_acceptance_park.md (the contract)
2. docs/_internal/redesign-2026-09/prompts/p9b_impl.md (what was asked)
3. `git -C /workspaces/Meta-Aging/01_modules/te-tracks show --stat 204ee66` and the full diff of that commit
4. tests/checks/acceptance/ in full, including lib/
5. tests/expectations/mm39/ in full, including its README.md
6. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments"

## Environment

```
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_CONSUMER_FIXTURES=/workspaces/Meta-Aging/_scratch/te-tracks-audit/p9b-opus/consumers
```
Put every scratch file under `_scratch/te-tracks-audit/p9b-opus/` and remove it with Python `shutil.rmtree`
when you finish; `/tmp` is noexec. The reference root holds six development archives under `pubroot/` and
the acceptance pair under `acceptance/`. Leave all ten in place. Do not rebuild and do not publish.

## What to do

**1. Mutate the build, not the check.** This is the centre of the review. For each of the eleven acceptance
areas, construct a defect a real build could plausibly have, apply it to a real copy of an archive, point
the check at the copy, and record whether the check fails and with what message. A defect the suite accepts
is a blocking finding. Cover at least: a dropped export row; a duplicated `gene_id` in
`record_starsolo.gtf`; a single flipped strand; an off-by-one interval boundary in the child SAF; a
reordered attribute in the STARsolo profile; a truncated taxonomy table; a changed `rank_scheme_version`;
an inventory entry whose byte count no longer matches its file; a coherently re-signed identity, meaning one
where `BUILD_ID` was recomputed after the edit; and a payload file replaced by a same-size file of different
bytes. Report each as: defect, area that should catch it, observed outcome.

**2. Ask where each expectation came from.** `tests/expectations/mm39/README.md` claims an independent
authoring provenance per file. For each of the six files added in 9b, decide whether its values are
traceable to a plan, ruling or earlier review under `docs/_internal/`, or whether they could only have been
read out of a build. Quote the source you found for each value you traced. A literal that traces only to the
build under test is a finding even when the number is right, and the fix is to name its derivation.

**3. Judge `core_checks()`.** `tests/checks/acceptance/lib/common.py` re-runs existing core checks against an
acceptance archive by symlinking the archive as `build` under a private reference root. Establish whether
that symlink can let a core check write into the archive, whether any core check depends on paths the
private root does not provide, and whether a core check silently passing on a missing input would be visible.
Then say which acceptance areas rest only on replayed core checks.

**4. Recompute the numbers.** Every literal in `areas.py` and in the six expectation files: the per-namespace
export byte totals, the registration size, the payload sums, the per-file sizes, the Dfam table row counts,
the record census, the subtraction census, the oracle metrics, the inventory and export-contract counts, and
both identities. Recompute each with your own code from the acceptance archives. Recompute `BUILD_ID` and
`CATALOG_ID` yourself from the manifests without using `src/release.py`.

**5. Judge the new prose in the diff.** `AGENTS.md`, `README.md`, `docs/RELEASES.md`, `docs/PROVENANCE.md`
and `docs/OUTPUTS.md` changed. Check every number and path in the changed lines against the artifacts, and
judge the wording against the project's rules: affirmative, brief, comments state intent. The README's
deferral table and the RELEASES acceptance witness are new text; both make claims.

## Mutation safety

When a finding needs a mutation, copy the target and mutate the copy, and make the copy a real one. A
hardlinked copy shares its inode, so writing to it writes through to the artifact under review and a
concurrent reader sees a corrupted payload. Never use `cp -al`, `cp -l`, or `shutil.copytree` with a linking
copy function on a build, an archive or a fixture. As your last step verify that nothing you did persisted:
run `src/99_verify.py` on every archive under `pubroot/` and `acceptance/` for both families, and
`release.py verify-current` for both families under both roots, and report those exits.

Write exactly one file: `docs/_internal/redesign-2026-09/reviews/p9b_opus.md`.

Report as:
# Phase 9b review (Opus)
Verdict: PASS | PASS WITH ADVISORIES | FAIL
## Can the suite fail?
<table: defect injected | area that should catch it | caught | message>
## Blocking
- [B1] path:line — finding — evidence — fix
## Advisory
- [A1] ...
## Expectation provenance
<table: expectation file | value traced to | verdict>
## Numbers recomputed
<table: quantity | stated | observed | command>
## Closing verification
<verifier and verify-current exits for all ten archives and both families under both roots>

Under 170 lines. FAIL when any injected defect passes, when an expectation traces only to the build under
test, or when a stated number differs from the artifact.
