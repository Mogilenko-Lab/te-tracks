# te-tracks claim validation, scope publication (codex, read-only)

You are one of three independent validators of the parked te-tracks package. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Every phase has landed, been
reviewed, and been through a parking pass that rewrote the prose. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p11_publication.md`. You change nothing else. No git writes, no
installs, no network.

Your single question: **is every statement in your scope true of the artifacts on disk?** Not whether it is
well written, not whether the design is right, not whether something is missing. Whether each sentence that
asserts a fact asserts a true one. The prose was rewritten after the last review, so no earlier review
covered the text you are reading.

## Your scope

`docs/RELEASES.md` (284 lines), `docs/PROVENANCE.md` (187 lines) and `docs/RUNBOOK.md` (334 lines).

These three carry the identity, the pinned inputs and the host procedure. The claims that matter most:

- every digest, `BUILD_ID`, `CATALOG_ID`, payload byte count and inventory count. Recompute each from the
  archive it describes. A build id is recomputed by the documented rule over the identity block, never read
  from the manifest that is itself under test.
- the threat-model paragraph in `RELEASES.md`, which states what the verifier detects and what pinning
  protects. Demonstrate both halves: corrupt a real copy of an archive and show the verifier refusing it,
  then edit an identity coherently in another real copy and show that its recomputed id is self-consistent.
  That pair is the claim.
- every command in `RUNBOOK.md`. Run what a read-only container can run. For each step that needs the host,
  state exactly which mount or permission it needs and why the container cannot supply it, rather than
  marking it unverifiable without a reason.
- the source pin table in `PROVENANCE.md`, checked against `config/mm39.env` and the cached files, including
  the Dfam snapshot and its provenance file.
- the stated build durations and the consumer resident-memory floors. These were measured on a particular
  run; confirm they still describe the artifacts, or report the figure you observe.

Two other validators hold the remaining documents. Stay inside your scope: a claim in someone else's file is
theirs, even when you notice it. The exception is a contradiction **between** your scope and theirs, which
you report under "Cross-scope contradictions" with both paths.

## Environment

```
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_CONSUMER_FIXTURES=/workspaces/Meta-Aging/_scratch/te-tracks-audit/p11_publication/consumers
```
`/tmp` is noexec: every scratch file goes under `_scratch/te-tracks-audit/p11_publication/` and that
directory is removed with Python `shutil.rmtree` when you finish. Setting the fixture variable above is not
optional: the generated fixture directory is otherwise a fixed path under the reference root and three
validators running at once would overwrite each other's fixtures.

Do not rebuild and do not publish. The builds and archives under the reference root are the artifacts your
claims are checked against. When a check needs a mutation, mutate a **real** copy, never a hardlinked one,
and never use `cp -al`, `cp -l` or `shutil.copytree` with a linking copy function. Run the build verifier on
each build directory and `release.py verify-current` for both families as your last step and report the
exits.

## Method

Work sentence by sentence. For every sentence in scope that asserts a fact, classify it and act:

- **A number**: a count, a size in bytes, a duration, a resident-memory figure, a percentage, a digest, a
  build id. Recompute it yourself from the artifact. Never accept a check's summary line as evidence for the
  number the check reports, because that is the claim under test.
- **A path**: confirm the file or directory exists at exactly that path, with the type claimed.
- **A command**: run it, or state precisely why a read-only container cannot and what would have to be true
  for it to work.
- **A capability** ("consumer X reads file Y", "the verifier refuses Z", "a mismatch stops the build"):
  demonstrate it. A capability claim backed only by prose is unverified, and you say so.
- **A version**: read it from the installed tool or the pinned source, not from another document.
- **A pointer** ("recorded in `docs/DECISIONS.md`", "see the runbook"): follow it and confirm the target says
  what the pointer says it says.

Quantify your pass. Report how many fact-asserting sentences your scope contains, how many you verified true,
how many are false, how many you could not verify and why. A scope where most claims are unverified is a
finding about the documents.

Three failure modes to look for specifically, because the prose was just rewritten:

1. **A number that moved.** The package rebuilt several times; a figure written against an earlier build may
   survive in prose. Payload sizes, inventory counts, build ids, durations and resident-memory figures are
   the likely survivors.
2. **A claim that was true of a narrower thing.** A statement proved on an eleven-record fixture presented as
   a property of the whole catalog, or a per-stage measurement presented as a whole-build one.
3. **A capability stated in the present tense that is actually deferred.** The package defers real work
   deliberately and records it; a sentence that describes a deferred thing as present is the worst kind of
   error here, because a consumer plans around it.

## Output format (the review file)

```
# Claim validation: publication (codex gpt-6-astra)
Verdict: TRUE | TRUE WITH CORRECTIONS | FALSE CLAIMS PRESENT
## Tally
<table: file | fact-asserting sentences | verified true | false | unverifiable>
## False claims
- [F1] <file:line> "<the sentence, quoted>" — <what is actually true> — <the corrected sentence>
## Unverifiable claims
- [U1] <file:line> "<quoted>" — <why it cannot be checked here> — <what would settle it>
## Numbers recomputed
<table: claim | stated | observed | command>
## Capabilities demonstrated
<table: claim | how demonstrated | outcome>
## Cross-scope contradictions
<table: your path | other path | the contradiction>
## Closing verification
<verifier and verify-current exits>
```

Keep the file under 220 lines. The verdict is FALSE CLAIMS PRESENT when any sentence in scope asserts
something the artifacts contradict, however small, because the point of this pass is that a consumer can
trust the text. A corrected sentence is offered for every false claim, written in the package's voice:
affirmative, stating what the thing is.
