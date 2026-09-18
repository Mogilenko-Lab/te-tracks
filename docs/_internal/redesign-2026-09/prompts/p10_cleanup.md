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

## 2c. Stop the suite leaving bytecode in a consumer's checkout

`.gitignore` has no `__pycache__` or `*.pyc` rule, and the orchestrator found `src/lib/__pycache__/` in the
working tree after a python run that did not set `PYTHONDONTWRITEBYTECODE=1`. Every prompt in this project
exports that variable, so the project has never noticed; a consumer reading `AGENTS.md` and running
`tests/run.sh` will not set it.

Fix it at the source rather than in the ignore file alone: have `tests/run.sh` and `build.sh` export
`PYTHONDONTWRITEBYTECODE=1` themselves, so a consumer gets the intended behaviour without knowing the
variable exists, and add `__pycache__/` to `.gitignore` as the belt to that braces. Confirm afterwards that a
full suite run from a clean tree leaves `git status --short` empty of anything the run produced.

## 3. `README.md`

Rewrite it as the document a downstream consumer reads first. It currently speaks in the project's in-flight
voice, with "the redesign contract below lands in phases 1-9" and "as the listed phases land"; the phases are
done, so the README states what the package is.

**Open with the problem that started the package, in the owner's own terms.** Transposable-element
annotation is fiddly and goes stale. Keeping it current across several projects by hand produced a different
annotation in each one, so the projects needed one way of building a TE annotation. That is the first thing a
reader meets, in three or four short sentences, before any description of the package. Ground it in the
facts this repository measured, so the difficulty is shown rather than asserted: RepeatMasker's three tokens
straddle the field's ranks, so 558,808 records sit under family `Alu` and a filter for `SINE/B1` returns
nothing; each counting tool builds its features from a different key, so two tools' numbers for one locus do
not join; and an annotation that changes between two analyses makes their counts incomparable with no
symptom.

Then, each in its own short section, in this order:

1. **What this is.** One paragraph: a reference projection of one RepeatMasker run for one assembly into
   canonical tables, named universes and registered exports, with every emitted feature joined back to its
   source record. State the two guarantees as facts: every input is pinned by digest, and every published
   build is immutable and addressable by its full id.
2. **Inputs.** The pinned sources with their roles, and the gene annotation as the child family's parameter.
3. **Outputs.** What is published, at which grain, in which contig namespace, in which coordinate
   convention.
4. **What each output supports.** One table binding each artifact to the consumer that reads it and the
   counting question it serves. It must state plainly that the exon-subtracted SAF is the bulk
   featureCounts product; that the expectation-maximization routes take the unmasked record exports with the
   full gene annotation; that `record.gtf` carries the subfamily grammar TEsingle and TElocal consume; that
   `record_starsolo.gtf` carries the record-as-gene grammar STARsolo and cellranger consume; that IRescue
   reads a record or subfamily BED; that `all_rmsk/full/record.bed` is the interval catalog a
   chromatin-accessibility ledger keys on; and that the Dfam view supplies the lineage, rank and clade
   vocabulary for aggregate reporting. Name the universe each serves. If `docs/OUTPUTS.md` already carries
   this table, the README carries the short form and points to it.
5. **Which biological questions the outputs support, and which they do not.** Affirmative and precise. They
   support: how much transposable-element RNA a cell or sample holds at record, subfamily, family and class
   grain; which lineages and divergence strata that signal sits in; which annotated intervals are accessible
   and which of their sequence is exon-disjoint. They do not settle: whether a copy transcribed from its own
   promoter, whether a copy is structurally intact, which insertion a group of records belongs to, and any
   age or activity verdict. Each of those is named in `docs/DECISIONS.md` with the evidence its next
   decision needs, and the README points there rather than restating it.

Keep the build, test and genome sections. Keep every link that resolves and add none that does not.

## 3b. The prose standard, for `README.md` and every file under `docs/`

The owner's standard, and it binds this whole pass:

- **Laconic.** `README.md` comes in under 120 lines. A section that can be three sentences is three
  sentences. Delete a sentence that repeats its neighbour at a different length.
- **Simple and direct.** Short sentences, one idea each, present tense, concrete nouns. A number or a path
  in place of an adjective wherever one exists.
- **Affirmative only.** Every sentence states what a thing is. Remove contrastive negation everywhere,
  including the reflexive "X, not Y" and "rather than" constructions used for emphasis. Keep a negative
  clause only where it carries a contract, as in a guarantee's stated boundary or a "they do not settle"
  list.
- **No in-flight voice.** No phases, no roadmap, no "will", no "currently", no apology for scope.

Apply the same standard to `docs/*.md` as a wording pass with a hard constraint: change no claim, number,
path, identifier, command, table row or contract. Compress and clarify sentences only. Where a sentence
reads as wrong rather than as verbose, leave it and report it; a false claim is the next pass's subject and
rewriting it here hides it.

## 3c. Where the 120 lines come from, and what the phase numbers become

`README.md` is 225 lines and 105 of them are the artifact truth table, so the budget is met by moving that
table rather than by thinning prose. Move it into `docs/OUTPUTS.md` as its own section, which is where the
schemas and export contracts already live, and leave the README one sentence naming what the table records
and where it is. Move nothing else out of the README; the six questions above are its content.

The phase numbers leave the public documents, because a consumer cannot act on them:

- the truth table's `phase` column goes. The `status` column stays, and it says what is true of the artifact
  now: delivered, tested, or deferred with the evidence its next decision needs.
- `docs/OUTPUTS.md` headings carry "(phase 2)" and "(phase 3)". Name the subject instead.
- the README paragraph beginning "Phase 9b qualification recorded" states suite counts as a phase result.
  State them as the package's current test surface, in the build and test section, with the counts intact.
- the "Parking gates" heading names the project's process. The table under it is the list of deferrals with
  the evidence each needs, so name it that, and place it beside the questions the outputs do not settle.

The internal records under `docs/_internal/` keep every phase number; they are the history, and this
instruction is about the documents a consumer reads.

## Rules
- Touch only: `README.md`, `AGENTS.md`, `tests/fixtures/**`, `tests/checks/**`, `tests/lib/**`, `src/**`,
  `config/**`, `build.sh`, `lib/**`, and `docs/*.md`. In `docs/*.md` the licence is wording alone: every
  claim, number, path, identifier, command, table row and contract survives the pass byte-identical in
  meaning. Leave `docs/_internal/**` alone.
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
wc -l README.md docs/*.md
grep -rniE "not just|rather than a|instead of a| not a | not an |isn't|aren't" README.md docs/*.md | grep -v _internal
git status --short
```
Every archive must still verify and every suite must pass with no new unsupported check.

## Final message
Every file created, changed, renamed or removed; for each removed fixture the check that still covers its
case; every comment or docstring removed for provenance or history rather than reworded, counted by file;
the README's new section list with its line count, and its opening paragraph quoted in full; the line count
of every `docs/*.md` before and after the wording pass; every sentence you left because it reads as wrong
rather than verbose, quoted with its file and line; each contrastive-negation hit the grep returns, with
either the rewrite or the reason the negative clause carries a contract; any config key or single-value
knob you found and left alone; the four archive verifications and the three suite results verbatim;
every deviation.
