# te-tracks milestone 9 seam review: the parked release as a whole (codex, read-only)

You are the independent reviewer of the te-tracks release at its last seam, the boundary between a reference
package and the analyses that consume it. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Every phase from 0 to 9b has
landed and each was reviewed on its own contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/m9_codex.md`. You change nothing else. No git writes, no installs,
no network.

This is not another phase review. The per-phase reviews established that each deliverable matches its
contract. Your question is different and only answerable now: **does the package cohere as one thing a
stranger can use?** Judge it as the consumer it is being handed to, a team that will quantify transposable
elements for three single-cell and single-nucleus datasets and one bulk RNA-seq dataset, on a host you will
never see, months from now, without being able to ask anyone a question.

## Environment

```
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_CONSUMER_FIXTURES=/workspaces/Meta-Aging/_scratch/te-tracks-audit/m9-review/consumers
```
`/tmp` is noexec: put every scratch file under `_scratch/te-tracks-audit/m9-review/` and remove it with
Python `shutil.rmtree` when you finish. The reference root already holds the development and acceptance
builds of both families with several published archives each; leave every one of them in place, do not
rebuild, and do not publish. The fixture-directory variable above matters: the generated fixture directory is
a fixed path under the reference root, so setting it keeps your suite runs from colliding with anyone else's.

When a finding needs a mutation, copy the target and mutate a **real** copy, never a hardlinked one, because
a hardlink shares its inode and a write reaches the artifact under review. Never use `cp -al`, `cp -l` or
`shutil.copytree` with a linking copy function. As your last step run the build verifier on each build
directory and each archive and `release.py verify-current` for both families, and report those exits, so the
record shows nothing you did persisted.

## Read

1. `README.md` and `AGENTS.md`.
2. `docs/DECISIONS.md`, `docs/OUTPUTS.md`, `docs/RELEASES.md`, `docs/PROVENANCE.md`, `docs/RUNBOOK.md`.
3. The plan: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/`, all of it, `00_INDEX.md` first.
4. The rulings, which are authoritative over any review they rule on:
   `docs/_internal/redesign-2026-09/reviews/*_rulings.md`.
5. `build.sh`, `src/`, `tests/`, `config/`.

## Judge, with evidence

**1. Can a stranger build it?** Follow `docs/RUNBOOK.md` as written, as far as a read-only container allows,
and name every step that is ambiguous, out of order, assumes knowledge the document does not supply, or names
a path, version or command that does not exist. A runbook step you cannot follow without guessing is a
blocking finding. State explicitly which steps you could execute and which you could only read.

**2. Can a stranger use the outputs?** For each consumer named in the package, establish from the documents
alone which file it reads, at which grain, in which namespace, under which universe, and what it must pin.
Then check that against the bytes. A consumer named without a file, or a file without a named consumer, is a
finding. The four counting routes that matter are bulk `featureCounts` over the exon-subtracted SAF, the
expectation-maximization routes over the unmasked record exports with a full gene annotation, `STARsolo` and
`cellranger` over `record_starsolo.gtf`, and `IRescue` over a record or subfamily BED.

**3. Do the identities compose?** Take one record and follow it end to end yourself: from the source `.out`
row through `rmsk_records`, its universes, its canonical taxonomy, its Dfam ranks and clades, each of its
export spellings in all three namespaces, its registration rows, and its exon-subtracted blocks in the child.
Then take one subfamily and one instance and do the same. Report any join that needs knowledge absent from
the documents, and any grain where a naive join doubles.

**4. Is the identity model sound at the seam?** `CATALOG_ID` must survive everything that is not a change of
records, and `BUILD_ID` must move for everything that changes published bytes. Test the claim rather than
reading it: find, or establish the absence of, a change that moves published bytes while leaving `BUILD_ID`
fixed, and a change of records that leaves `CATALOG_ID` fixed. Confirm the child's dependency on its parent
is enforced and not merely declared, and that an earlier archive stays verifiable and selectable.

**5. Does the acceptance suite accept?** Read every check under `tests/checks/acceptance/`. For each, state
what would have to be wrong in the build for it to fail, and name any acceptance number that is compared
against a value taken from the build under test rather than authored independently. An acceptance suite that
cannot fail is the most expensive defect available here.

**6. What does the package claim that is not true?** Every count, size, duration, path, version and
capability in the public documents, checked against the artifacts. Quantify: how many claims you checked and
how many were wrong.

**7. What will the first consumer hit?** The single thing most likely to cost the consuming team a day. One
finding, argued, with the evidence. This is the most valuable line in your review, so spend effort on it.

**8. What is deferred, and is each deferral honest?** `docs/DECISIONS.md` records deferrals with the evidence
each next decision needs. Check that each deferred item is genuinely absent rather than half-present, and
that nothing shipped whose deferral the documents still assert.

## Output format (the review file)

```
# Milestone 9 seam review (codex gpt-6-astra)
Verdict: PASS | PASS WITH ADVISORIES | BLOCKING
## The one thing the first consumer will hit
<finding 7, argued>
## Blocking
- [B1] <file:line> <finding> — <evidence> — <what fixes it>
## Advisory
- [A1] ...
## Runbook walk
<table: step | executed or read | outcome>
## One record, one subfamily, one instance, followed end to end
<the joins, with the values at each hop>
## Claims checked
<table: claims checked | wrong | where>
## Acceptance suite: what would have to break
<table: check | what it would catch | independently authored>
## Closing verification
<verifier and verify-current exits for every build and archive>
```

Keep the file under 250 lines. BLOCKING means a stranger cannot build or use the package from the documents,
an identity claim is false, or an acceptance check cannot fail. Facts over opinions; every finding cites a
path and, where possible, a line. Where you agree with an earlier review's ruling, say so in one line rather
than re-arguing it.

## Phase 9b specifics

Phase 9b landed as commit `__HEAD9B__`, the last implementation commit on the branch. It added eleven
acceptance checks, their library, six expectation tables, the `--build` mode, the host section of the
runbook, the acceptance witness in `docs/RELEASES.md`, and the deferral table in `README.md`.

The eleven checks under `tests/checks/acceptance/` are five-line wrappers. The work sits in
`tests/checks/acceptance/lib/`: `common.py` resolves the acceptance archives, runs `build()` for
`--build`, and offers `core_checks()`, which re-runs existing `tests/checks/core/` checks against an
acceptance archive by symlinking it as `build` under a private reference root. `areas.py` holds the nine
measuring areas. `oracles.py` holds the bedtools exon-subtraction oracle and the packaged legacy-GTF
reconciliation. `consumer_floor.py` is a probe the runbook invokes by hand.

Spend your effort in judgement 5 on two specific questions, because they decide whether this suite is worth
having:

- **Does `core_checks()` make an acceptance check, or does it re-run a contract?** Re-running a core
  contract at full scale is a real measurement, and it is also not independent authoring. State for each
  area which part is a fresh measurement written for acceptance and which part is a core check replayed,
  and say whether the mixture leaves any acceptance claim resting only on a replay.
- **Could each expectation literal have been produced by the build it now judges?** `tests/expectations/mm39/README.md`
  claims a provenance per file. Test that claim: for each expectation table, decide whether its values are
  derivable from an earlier plan, ruling or review in `docs/_internal/`, or whether they could only have come
  from running the build. Name any file where the second is true.

Four deviations the implementer reported, each of which you should confirm or correct rather than accept:

1. It edited `tests/run.sh` during that runner's own first invocation; the invocation ended with a shell
   parse error and exit 2. It then froze the runner and repeated the complete fresh build successfully. Judge
   whether the frozen runner is correct, including its argument parsing and every usage exit.
2. The orchestrator's prompt named a `--config` flag that `build.sh` does not have. The implementation and
   the runbook use `--family gene`, which selects `config/mm39_gene.env`. Confirm the runbook's commands
   match the CLI as built.
3. The repository's HEAD advanced through documentation-only commits while the build ran, so the acceptance
   manifests record revision `51c0162` with `builder_git_dirty: true`. The source and configuration bytes
   retain the phase 9a identities. Confirm that, and confirm the dirty flag cannot reach a host publication.
4. The export writer's peak resident bytes measured 6,807,732,224 in the first fresh build and
   4,936,556,544 in the second, against an earlier measured range of 5.5 to 6.0 GB, while both builds
   reproduced the same payload identity. Say what a 1.9 GB spread across two identical-output builds means
   for the 16 GB reservation the runbook asks a host to make.

Three smaller things to check while you are in the files:

- `tests/expectations/mm39/gene_oracle.tsv` pins twelve metrics while the oracle measures eighteen across
  its three contigs. Name the unpinned ones and say whether their absence weakens the oracle.
- `consumer_floor.py` lives under `tests/checks/acceptance/lib/` and no check imports it; the runbook calls
  it directly. Judge the placement.
- `areas.publication()` collects identity differences into a `discrepancies` list before asserting. Confirm
  that a `BUILD_ID` difference fails the check rather than printing a warning.

The measured identities to hold against the artifacts: core `BUILD_ID`
`5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813`, child
`198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1`, `CATALOG_ID`
`90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` in both, 52 core inventory entries and
27 export contracts, 21 child inventory entries and 12 export contracts, core payload 15,301,538,537 bytes
and child payload 2,157,717,760 bytes.

The orchestrator has already re-run all four suite modes and verified all ten archives; do not repeat that
as your contribution. Your contribution is the seam.

