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

__SPECIFICS__
