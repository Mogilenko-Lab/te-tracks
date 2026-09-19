# Claim validation rulings

Three validators read disjoint scopes of the parked package and asked one question of every
sentence: is it true of the artifacts on disk. Their tallies:

| Scope | Sentences | True | False | Unverifiable |
|---|---:|---:|---:|---:|
| `docs/OUTPUTS.md` | 636 | 614 | 12 | 10 |
| `docs/RELEASES.md`, `docs/PROVENANCE.md`, `docs/RUNBOOK.md` | 288 | 260 | 6 | 22 |
| `README.md`, `AGENTS.md`, `docs/DECISIONS.md` | 170 | 143 | 12 | 15 |
| **total** | **1,094** | **1,017** | **30** | **47** |

`docs/PROVENANCE.md` and `AGENTS.md` carry no false claim.

## What the orchestrator reproduced independently

Four findings were recomputed here before ruling, and every one matched the validator exactly.

| Finding | Claim | Measurement |
|---|---|---|
| outputs F9 | `canonical_family` is unique within `canonical_class` | 18,484 name rows hold 59 distinct pairs; `LINE/L1` spans 149 rows, `LTR/ERVK` 285 |
| outputs F12 | provisional status recoverable by a name join | six names carry both a definite and a provisional raw class: Eulor5B, Eulor6A, Eutr16, MER124, MER131, UCON2 |
| publication F5 | the 14761 ledger adopts `te_catalog_id` and `te_build_id` | `inputs.py:121` sets both to `NaN`; `counts.py:90` raises on any populated value |
| publication F6 | abandoned staging removes with bare `shutil.rmtree` | `release.py:117` leaves nested directories `0o555`; `discard_staging` exists to restore write access first |
| narrative F2 | 26 core passes | 28 core checks on disk, 28 passes in this orchestrator's run |

## Dispositions

**Accepted as written, mechanical.** outputs F1 through F7 restore the `tables/` prefix that
compressing the artifact list into prose dropped, leaving seven sentences naming files at a root
where they do not exist. outputs F10 and F11 state fixture locations the same parking pass changed
to private per-run directories.

**Accepted, substantive.** outputs F8, F9 and F12; publication F1, F5 and F6; narrative F2, F9, F10
and F12. Each describes a behaviour a consumer would act on and find absent.

**Accepted, and caused here.** publication F2, F3, F4 and narrative F11 cite
`01_modules/te-consumers`, which this orchestrator renamed to `01_modules/te-quant` while the
parking pass ran. The module path changes; the installed environment path
`/workspaces/Meta-Aging/.venv/te-consumers` stays, because `tests/run.sh` resolves it by that name
and moving both at once would break the suite mid-parking. Both validators noticed that distinction
unprompted and were right to keep it.

**Accepted, one class.** narrative F3 through F8 all share a cause: `docs/DECISIONS.md` states
deferred products in the present tense, so a proposed transcript-context relation and proposed core
candidate views read as published tables. Every child declares `context_capability=not_computed`
and no inventory carries those views. The fix is tense and framing across six sections rather than
six separate corrections.

**Accepted with a different correction.** narrative F1 challenges the README's fourth sentence,
"An annotation change between analyses silently makes their counts incomparable," on the ground
that a changed annotation can preserve byte-identical counting support. The challenge is right: as
an absolute the sentence is falsified by one counterexample. The validator's replacement drops the
problem the package exists to solve. This ruling keeps the pain and states only what is:

> Counts carry no record of the annotation they came from, so two analyses cannot be shown to
> share one.

That is unconditionally true, affirmative, and it is what `BUILD_ID` answers.

## Unverifiable

Forty-seven claims could not be settled under the review constraints, which forbade a fresh
complete build, publication, installs and network. They name what would settle them: two complete
builds for byte-identical reproduction, an R Arrow environment for one reader row, an observed
atomic replacement for the publication claim, an installed MATES for its version cutoff. None is
recorded as a defect and none blocks parking.

One is worth carrying forward rather than filing. outputs U8 reports that a complete TElocal index
build over the full record GTF was stopped while still reading the annotation, because its feature
list makes each new record more expensive to insert. The eleven-record round trip passes. A
consumer planning a full-scale TElocal run needs that cost measured before committing to it.
