# te-tracks milestone 7 fix 2 (unit `te-tracks-m7-fix2`): the publication fixture under the payload roster

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks` (branch `redesign-2026-09`, HEAD `9d16506`; the
milestone 7 fix sits uncommitted on top and is your starting point). The fix added an authoring gate in
`src/lib/manifest.py` (`CORE_PAYLOAD_PATHS`): the non-export inventory must equal the core roster, so
`tests/fixtures/publication/build_fixture.py` now fails `write_manifest` with
`payload roster differs: ['policy.txt', 'source/qualification.md']`, and checks 71 and 72 fail at fixture creation.
The gate stays; the fixture conforms. Read `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" first,
then the three files in the touch list in full.

## Environment and rules
- `export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot PYTHONDONTWRITEBYTECODE=1`. The
  build and the published root are read-only for you. Scratch under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/m7fix2/`,
  removed with Python `shutil` when you finish.
- No git writes anywhere (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too), no
  installs, no network, no edits outside the touch list. Never weaken a test beyond what an item below rules.

## Items
1. **Fixture** (`tests/fixtures/publication/build_fixture.py`). `_make_build` writes `source/qualification.md` with one
   line carrying the `note` (for example `synthetic qualification: <note>\n`), so `note` still distinguishes builds;
   `policy.txt` is no longer written; the `extra` parameter and `additional.txt` go (`make_build(family, note="first",
   added_export=False)`). Everything else stays.
2. **Check 72** (`tests/checks/core/72_publication_cases.py`). Every use of `policy.txt` as a corruption or damage
   target becomes `source/qualification.md` (the corrupt staging case, the damaged existing archive, the damaged
   selected archive, the payload symlink target); the added-payload case (`make_build(family, extra=True)` and its
   assertions) is removed, since a stray payload now fails authoring and check 71 covers it; archive counts asserted
   afterwards drop by one (after the concurrency cases 5, and any later literal accordingly). Messages asserted on
   corruption name `source/qualification.md`. The success message drops "added payload".
3. **Fixture README** (`tests/fixtures/publication/README.md`): the description names `source/qualification.md` as the
   note-bearing payload and states that the fixture matches the core payload roster.

## Touch list (exact)
`tests/fixtures/publication/build_fixture.py`, `tests/fixtures/publication/README.md`,
`tests/checks/core/72_publication_cases.py`.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot PYTHONDONTWRITEBYTECODE=1
python3 -m py_compile tests/fixtures/publication/build_fixture.py tests/checks/core/72_publication_cases.py && echo compiles
time python3 tests/checks/core/71_verify_build.py; echo "exit=$?"
time python3 tests/checks/core/72_publication_cases.py; echo "exit=$?"
ls "$TE_TRACKS_REFROOT/pubtest"   # empty
git status --short -- tests/
```
Final message: the files changed, acceptance outputs verbatim, the archive counts now asserted, any deviation.
