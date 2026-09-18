# te-tracks parking pass: fixtures, comments and the README narrative

You are the implementer of the parking pass, the last change to te-tracks before it is consumed. Working
directory (absolute): `/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, HEAD
`__HEAD__`. Every phase from 0 to 9b has landed and been reviewed. Read `AGENTS.md`, `README.md`,
`docs/*.md`, `src/`, `tests/`, `config/` and
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/19_phase9_acceptance_park.md`.

This pass changes no behaviour. It has three jobs: prove every fixture earns its place, make every comment
state intent and nothing else, and turn `README.md` into the document a downstream consumer reads first.

The orchestrator measured the starting state so you spend your effort where the work is, rather than
rediscovering it: `tests/fixtures/` holds 66 files in 320 KB; no fixture file lacks a reader, counting
`tests/fixtures/publication/build_fixture.py`, which is imported as a module, and the two `README.md` files,
which are documentation; there are no banner or separator comments anywhere; and exactly one comment
mentions a review, `src/15_build_universes.sh:2`, where "reviewed" qualifies the disposition file and is a
domain term rather than provenance. The mechanical debt is therefore small, and the substance of this pass is
the README and a genuine read-through of the comments and fixtures rather than a pattern sweep.

## 1. Fixtures

Read every file under `tests/fixtures/` and the check that consumes it. For each fixture directory, the
sibling `README.md` (create one where it is missing) states in one line per fixture what that fixture proves
and which check reads it. Then:

- Remove any fixture whose only reader is another fixture, or whose case is already covered identically by a
  neighbour. Name every removal and the check that still covers the case; remove nothing whose removal
  changes a check's outcome.
- Where two fixtures differ only in a value, say so in the README rather than merging them; a case that
  reads as duplication but pins a distinct boundary stays, with its boundary named.
- Where a fixture's filename does not say what it pins, rename it and update its readers.
- Keep every hand-authored expectation hand-authored. Copy nothing from a build output into
  `tests/fixtures/` or `tests/expectations/`.

## 2. Comments and docstrings

Apply the `AGENTS.md` rules to `src/`, `tests/`, `config/`, `build.sh` and `lib/`. A comment states intent:
what the code or the config value is for, briefly, affirmatively, one line where one line does it. A
docstring adds the contract: what the function guarantees, what it refuses, what its caller must not do.

Remove: dates, names, review or defect provenance, before and after measurements, the history of how the
code came to look this way, and restatements of what the next line plainly says. Delete a comment that
would die in a rewrite. Where a comment needs six lines mid-function, the code wants a named helper instead;
make that change only where it is local and obvious, and report any place where it is not.

A config key with no reader is deleted rather than commented, and so is a knob with exactly one legal value.
Report any you find rather than removing a key some consumer may pin.

## 2b. Make the suite safe to run twice

`tests/lib/consumers.py` resolves its generated fixture directory to
`$TE_TRACKS_REFROOT/fixtures/consumers` unless `TE_TRACKS_CONSUMER_FIXTURES` overrides it, and
`build_fixture()` rewrites files there on every run, so two concurrent `tests/run.sh` invocations against one
reference root can read a partially written fixture. The orchestrator hit exactly that, as one
non-reproducible check failure.

Give each run its own generated-fixture directory, keeping `TE_TRACKS_CONSUMER_FIXTURES` as the explicit
override, or, if per-run isolation would break a check that depends on a fixture surviving between checks,
state the constraint instead: name the variable in `AGENTS.md` beside the test commands and in the runner's
usage text, and say that one reference root serves one suite run at a time. Whichever you choose, say which
and why, and confirm the whole suite still passes.

## 3. `README.md`

Rewrite it as the document a downstream consumer reads first. It currently speaks in the project's in-flight
voice, with "the redesign contract below lands in phases 1–9" and "as the listed phases land"; the phases are
done, so the README states what the package is. Keep it affirmative, keep it under about 150 lines, and let
it answer these six questions in this order, each in its own short section:

1. **What this is.** One paragraph: a reference projection of one RepeatMasker run for one assembly into
   canonical tables, named universes and registered exports, with every emitted feature joined back to its
   source record.
2. **Why it exists.** The problem it removes from a consuming analysis: the field's tools each build their
   counting features from a different key, so counts from different tools cannot be compared or joined
   without a registration; and a reference that moves silently makes a count irreproducible, so every input
   is pinned by digest and every published build is immutable and addressable by its full id.
3. **Inputs.** The pinned sources with their roles, and the gene annotation as the child family's parameter.
4. **Outputs.** What is published, at which grain, in which contig namespace, in which coordinate
   convention.
5. **What each output supports.** One table binding each artifact to the consumer that reads it and the
   counting question it serves. It must state plainly that the exon-subtracted SAF is the bulk
   featureCounts product; that the expectation-maximization routes take the unmasked record exports with the
   full gene annotation; that `record.gtf` carries the subfamily grammar TEsingle and TElocal consume; that
   `record_starsolo.gtf` carries the record-as-gene grammar STARsolo and cellranger consume; that IRescue
   reads a record or subfamily BED; that `all_rmsk/full/record.bed` is the interval catalog a
   chromatin-accessibility ledger keys on; and that the Dfam view supplies the lineage, rank and clade
   vocabulary for aggregate reporting. Name the universe each serves. If `docs/OUTPUTS.md` already carries
   this table, the README carries the short form and points to it.
6. **Which biological questions the outputs support, and which they do not.** Affirmative and precise. They
   support: how much transposable-element RNA a cell or sample holds at record, subfamily, family and class
   grain; which lineages and divergence strata that signal sits in; which annotated intervals are accessible
   and which of their sequence is exon-disjoint. They do not settle: whether a copy transcribed from its own
   promoter, whether a copy is structurally intact, which insertion a group of records belongs to, and any
   age or activity verdict. Each of those is named in `docs/DECISIONS.md` with the evidence its next
   decision needs, and the README points there rather than restating it.

State the guarantees as facts rather than as a contract that lands. Keep the build, test and genome
sections. Keep every link that resolves and add none that does not.

## Rules
- Touch only: `README.md`, `AGENTS.md`, `tests/fixtures/**`, `tests/checks/**`, `tests/lib/**`, `src/**`,
  `config/**`, `build.sh`, `lib/**`, and `docs/*.md` only where a sentence is made wrong by a fixture rename.
- No behaviour change. No git writes. No installs. No network. Never write into
  `/data2/users/shared/refcache`.
- Weaken or delete no check. Every case a removed fixture covered must still be covered; name the check that
  covers it.
- Change no published byte. The identity is a function of the sources and the export contracts, so a
  comment or a fixture cannot move it; if any change of yours moves `BUILD_ID`, you have changed behaviour,
  so stop and report instead.
- Scratch under `_scratch/te-tracks-audit/p10/`, removed with Python `shutil.rmtree`; `/tmp` is noexec.
- Export `PYTHONDONTWRITEBYTECODE=1` in every shell.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
for f in build.sh lib/common.sh src/*.sh src/gene/*.sh tests/run.sh tests/checks/**/*.sh; do bash -n "$f" && echo "syntax ok $f"; done
tests/run.sh core; echo "exit=$?"
source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh
tests/run.sh consumers; echo "exit=$?"
tests/run.sh acceptance; echo "exit=$?"
for a in "$TE_TRACKS_REFROOT"/pubroot/te_mm39/archive/*; do python3 src/99_verify.py "$a"; echo "exit=$? $a"; done
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39_gene; echo "exit=$?"
wc -l README.md
git status --short
```
Every archive must still verify and every suite must pass with no new unsupported check.

## Final message
Every file created, changed, renamed or removed; for each removed fixture the check that still covers its
case; every comment or docstring removed for provenance or history rather than reworded, counted by file;
the README's new section list with its line count; any config key or single-value knob you found and left
alone; the four archive verifications and the three suite results verbatim; every deviation.
