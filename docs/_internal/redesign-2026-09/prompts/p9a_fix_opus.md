Review the phase 9a fix of the te-tracks redesign. Repository:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). You are read-only: no edits,
no git writes, no installs, no network. The checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git
repositories too; `14839-DM-cGAS` and `sene/` there are the owner's own directories, so read the first only
if useful and leave both alone.

Environment: export `TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`,
`TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source` and
`PYTHONDONTWRITEBYTECODE=1`. `/tmp` is noexec, so put working copies under
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/p9a-fix-opus/` and remove that directory with Python
`shutil.rmtree` before you finish. Do not rebuild and do not publish; the builds under the reference root
are the reviewed artifact.

Read, in order:
1. `docs/_internal/redesign-2026-09/prompts/p9a_fix.md`, the eleven-item contract for this fix.
2. `docs/_internal/redesign-2026-09/reviews/p9a_rulings.md`, the orchestrator's rulings, authoritative where
   a review and the rulings differ.
3. `docs/_internal/redesign-2026-09/reviews/p9a_codex.md` and `reviews/p9a_opus.md`, the two reviews the fix
   answers. The second is your own earlier pass on the implementation; this pass judges the fix.
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".
5. The changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short` and
   `git diff HEAD`, plus the contents of untracked files.
6. The fix implementer's report, in
   `/tmp/scio-delegate/te-tracks-p9a-fix/<run>/final.md`, the newest run directory.

## What to judge

The fix exists because two checks passed mutations they should have refused and one documented claim was
false. Your job is to establish that each of the eleven items now bites, and that nothing else moved.

For the three blocking items, the standard of proof is a mutation you run yourself, not a reading of the
new code.

1. **IRescue conservation.** Copy a real IRescue output under your scratch directory and mutate it three
   ways: add an extra matrix row carrying counts, duplicate a feature line carrying counts, and change one
   feature's count. Each must now make the check fail with a named refusal. Confirm the matrix dimensions are
   compared against the feature and barcode roster lengths and the matrix total against the fixture's
   expected molecule total, all before any dictionary is built. Confirm the observed allocation is still
   recorded and unasserted.
2. **STARsolo support confinement.** For each case and both `Gene` and `GeneFull`, replay a matrix placing
   support on a gene outside the case's supported set and confirm the check refuses by name. Confirm the
   host against TE split is still observational. Establish whether any case's supported set is derived from
   `tests/fixtures/consumers/starsolo_molecules.tsv` rather than hardcoded, because a hardcoded set drifts
   from the fixture.
3. **The class-less rank claim.** Verify the new `docs/OUTPUTS.md` sentences against the table: 54 names
   carry a class-less raw class, 53 leave every Wicker rank `missing`, those 53 are exactly the names whose
   Dfam leaf is `Unknown`, and `UCON4` is the class-less exact hit that inherits `Class II (DNA
   transposons)`. A sentence that is true of the data but still readable as the old rule is a finding.

For the remaining eight, recompute or mutate as the item allows.

4. **Rank cell guards.** Mutate each of the ten Wicker value and status columns in a scratch copy of the
   materialized table and confirm check 33 refuses each by name. Confirm the check re-derives the ranks from
   `wicker_code` and the node tree rather than comparing the table with itself. Confirm check 34's two new
   branches, a code with more than three slash-separated tokens and an unknown superfamily letter, are
   reached and refused.
5. **Retained provenance.** Confirm `source/` now carries the snapshot provenance, that it appears in the
   inventory and the payload roster, and that rewriting `fetch_finished` to another valid instant with
   `BUILD_ID` recomputed is now refused by name. Confirm the publication fixture writes a real provenance
   file rather than patching `manifest.tracked_provenance`, so the real branch and its provenance-digest
   refusal are exercised.
6. **Enumerated source layouts.** Confirm the hybrid archive that keeps `dfam_snapshot` while dropping
   `rmsk_out` from `identity.build_sources` is now refused, and that the phase-8 three-role archive still
   verifies. Try one further role set of your own choosing.
7. **Clades and the rank scheme.** Confirm `clade_count` is present and correct for the nine multi-clade
   models, that `docs/OUTPUTS.md` names `clades` a display field and `dfam_model_clades.tsv` the join key,
   and that `rank_scheme_wicker_v1` is now recorded in `identity` and named in the docs where a consumer
   would look for it.
8. **The producer range.** Confirm `docs/RELEASES.md` states the 5.5 to 6.0 GB range as a range with the new
   observation beside it and each figure attributed to its stage, and that nothing was added to
   `docs/RUNBOOK.md`, which phase 9b writes.
9. **The fetch script's output name.** Confirm the filenames derive from the universe and the genome and
   that the current arguments still produce the current names, so the tracked bytes and their digests have
   not moved. Verify the tracked snapshot's sha256 is still
   `ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f`.
10. **The contig roster message.** Confirm it states the roster size from the roster, and that
    `src/lib/contigs.py` changed in that message alone.
11. **The cellranger memory pin.** Confirm the docs and the check message describe a pin rather than a
    requirement.

## Identity and scope

The fix moves `BUILD_ID` through items 5 and 7 and must not move `CATALOG_ID`. Recompute both ids yourself
from the canonical identity JSON for the core and the child. Confirm the payload roster moved from 51 to the
number the implementer reports, that every place stating 51 was updated, that the child pins the new parent,
that the child's `exon_subtraction_summary.tsv` is byte-identical to
`tests/expectations/mm39/exon_subtraction_summary.tsv`, and that all earlier core and child archives still
verify. Run both suites. Name anything touched beyond the eleven items and the one-line allowance on
`src/lib/contigs.py`.

Judge the added prose and comments against the wording rules: no contrastive negation, intent only, no
review or defect provenance, and no sentence describing a file, a count or a capability the build does not
have.

## Delivering your report

Write your complete report to
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/opus-p9a-fix-report.md` before you finish, because your
final message is truncated in transit. That path is outside every git repository. Report as:

```
# Phase 9a fix re-review (Opus)
Verdict: PASS | PASS WITH ADVISORIES | FAIL
## Blocking
- [B1] path:line — finding — evidence — fix
## Advisory
- [A1] ...
## Item-by-item
<table: item | bites | evidence>
## Mutations run
<table: target | mutation | outcome>
## Identity and scope
<ids recomputed, roster size, archives verified, suites, scope>
```
Under 150 lines. FAIL when an item does not bite, an identity moved that should not have, or a check still
passes a mutation it should refuse. Then summarise in your final message: the verdict, the count of blocking
and advisory findings, and a one-line title for each blocking finding.
