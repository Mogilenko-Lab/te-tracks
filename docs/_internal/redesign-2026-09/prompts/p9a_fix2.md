# te-tracks phase 9a second fix: the five advisories

You are the implementer of the second and last fix of phase 9a. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phase 9a is implemented, fixed
once, and reviewed twice. Read `docs/_internal/redesign-2026-09/reviews/p9a_fix_opus.md` (the review these
five items come from), `reviews/p9a_rulings.md` (the orchestrator's rulings, authoritative where a review and
the rulings differ), and `prompts/p9a_fix.md` (the eleven items already landed).

**None of these five items moves `BUILD_ID`.** Four touch documentation, checks and a package script outside
the payload; the fifth adds a build-time gate rather than an identity field. You therefore do not rebuild and
do not republish. You confirm at the end that the ids are unchanged: core
`5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813`, child
`198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1`, `CATALOG_ID`
`90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` in both, roster 52 entries. If any change
of yours would move an id, stop and report it as a deviation instead of rebuilding.

Environment for every shell:
```
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_CONSUMER_FIXTURES=/workspaces/Meta-Aging/_scratch/te-tracks-audit/p9a-fix2/consumers
```
`/tmp` is noexec: scratch under `_scratch/te-tracks-audit/p9a-fix2/`, removed with Python `shutil.rmtree`.
No git writes. No installs. No network. Never write into `/data2/users/shared/refcache`. Weaken or delete no
test. Report a deviation instead of editing a number to fit.

## 1. Say what the verifier actually compares, and name the threat model (A1)

`docs/RELEASES.md:54` reads that the verifier compares the fetch timestamp, Dfam version and payload digest
with the retained provenance. That is true only for an archive that retains the provenance file. An archive
declaring `dfam_snapshot` without it, which the phase-9a implementation archive
`763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c` is, falls back to comparing the field with
itself, and that branch stays so the archive keeps verifying.

Correct the sentence to state the condition. Then add one short paragraph stating the threat model plainly,
because the package is about to be handed to strangers: the verifier detects corruption and accidental drift
in an archive judged against its own declaration, and a consumer's protection against a deliberately edited
archive is pinning the full `BUILD_ID` and the digests of the files it reads, which the release
documentation already tells it to do. Say that every archive this builder writes retains the provenance
unconditionally. Change no code for this item.

## 2. Put check 33's summary back in the suite output (A2)

`tests/checks/core/33_taxonomy_dfam_view.py` prints its refusal list before its census, and `tests/run.sh`
shows a passing check's first line alone, so the suite line for check 33 is now ten mutation messages and the
Dfam census has left the output. Checks 34 and 71 print the summary first and append `refused: …`. Match
them: the census first, the refusals appended.

## 3. Make every rank-column refusal name its column (A3)

Two of the ten rank-column mutations are caught before the new comparison runs: `wicker_class_status` trips
the census equality at `33:213` with a dict diff because that status feeds the `exact_wicker_*` counters, and
giving an uncoded row a class trips a message-less assertion at `33:202`. Both refuse, so nothing is
unguarded, but neither names the column.

Call `check_rank_cells` before the census comparison so the specific diagnostic wins, and give the assertion
at `33:202` a message naming what it found. Confirm afterwards that each of the ten columns refuses with
`Dfam rank cell differs: <name>: <column>`.

## 4. Pin the provenance digest at the input boundary (A4)

`config/mm39.env` pins `DFAM_SNAPSHOT_PATH` and `DFAM_SNAPSHOT_SHA256`. The provenance JSON beside the
snapshot now anchors `fetch_finished` in every archive this builder writes, and it carries no pin, so an
edited `data/dfam/*.provenance.json` flows through `src/00_fetch_sources.sh` into `identity.build_sources`
with nothing refusing it at build time.

Pin its digest beside the snapshot's, as `DFAM_PROVENANCE_SHA256`, and refuse in the fetch stage when the
file on disk does not match, with a named refusal in the style of the existing source-pin refusals. Add the
case to a check that already exercises the fetch stage's pins, so a mismatched provenance file is refused by
the suite and not only by a build. Keep the pin a build-time gate: do not record it in `identity`, because
the file's digest is already in the inventory and adding it to the identity would move `BUILD_ID`. Verify
that the ids are unchanged after your change.

## 5. Reconcile the fetch script's provenance keys (A5)

The pinned provenance JSON came from the ad-hoc
`docs/_internal/redesign-2026-09/taxonomy/dfam_snapshot_fetch_20260917.py` and carries `census_sha256`, while
the packaged `data/dfam/fetch_dfam_snapshot.py` writes `taxonomy_sha256` and `universe`, so a refresh yields
a different key set from the file the package ships. The four keys `verify_build` reads are in both, so
nothing breaks today, and a future refresh would produce a provenance the build still accepts but a reader
cannot compare with the shipped one.

Reconcile the packaged script's key set with the shipped file, keeping every key the shipped file has and any
the script adds, and name in `docs/OUTPUTS.md` the keys the verifier reads. Do not touch the shipped
provenance bytes: item 4 pins their digest and they are in the payload, so a byte change would move
`BUILD_ID`.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
for f in build.sh lib/common.sh src/*.sh src/gene/*.sh tests/run.sh tests/checks/consumers/*.sh; do bash -n "$f" && echo "syntax ok $f"; done
tests/run.sh core > core.log 2>&1; echo "core_exit=$?"; cat core.log
source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh
tests/run.sh consumers > consumers.log 2>&1; echo "consumers_exit=$?"; cat consumers.log
python3 src/99_verify.py "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39_gene; echo "exit=$?"
for a in "$TE_TRACKS_REFROOT"/pubroot/te_mm39/archive/*; do python3 src/99_verify.py "$a" >/dev/null 2>&1; echo "exit=$? $(basename $a)"; done
cat "$TE_TRACKS_REFROOT/te_mm39/build/BUILD_ID" "$TE_TRACKS_REFROOT/te_mm39/build/CATALOG_ID"
python3 -c "import json;i=json.load(open('$TE_TRACKS_REFROOT/te_mm39/build/MANIFEST.json'))['identity'];print(len(i['inventory']),len(i['export_contracts']),i['rank_scheme_version'])"
grep -n "verifier compares" docs/RELEASES.md
git status --short
```
Write the suite logs to files and print them whole, as shown: a run summarised through `tail` loses the
failing check's name and the runner's exit status. Both suites must pass with no new unsupported check beyond
Stellarscope's boundary defect, all six archives must verify, and the ids must be unchanged.

## Final message
Each of the five items with the file and line you changed and the evidence it bites, naming the refusal each
new case produces; confirmation that all three ids and the 52-entry roster are unchanged, with the commands;
both suite logs whole; every deviation.
