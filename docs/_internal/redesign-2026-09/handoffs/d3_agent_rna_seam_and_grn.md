# Brief for the D3 agent: the RNA seam, label harmonization, and the network runs

Paste `te_handover_to_14761.md` first, then this.

## What your endeavour becomes

You keep D3, the paired against unpaired seam, and it stops being only a schema question. The measured
anchor you hold is the reason: of 63 regulon transcription factors, 15 were shared, 34 appeared only with
whole-cell RNA and 14 only with paired nuclei, so nuclear RNA alone misses a third to a half of the circuit
space. That finding is what makes unpaired-mode corroboration necessary rather than optional, and nobody is
currently doing the thing that unpaired mode requires.

Your endeavour is that thing, and then the network runs.

**First, and independent of everything else: harmonize 14616-DM's annotation to this dataset's label
standards.** Unpaired-mode regulatory inference joins two cell universes that must never mix in one axis, so
they meet through harmonized labels and `condition_key` alone. Today 14761 carries 12 parent, 26 fine and 33
state labels from its own annotation campaign, and 14616 carries its own. Without a defensible correspondence
at a stated level, a metacell run across the two is joining populations that were never shown to be the same
populations.

This is the long pole and it has no dependency on the peak side, which is why it starts now and in parallel.
What it needs settled, each a decision to record rather than a parameter to pick:

- **Which level carries the correspondence.** Parent labels will map; state labels probably will not. A
  correspondence claimed at a finer level than the evidence supports is the failure mode, and the honest
  output is a crosswalk with a confidence and an explicit unmapped class rather than a total function.
- **What establishes it.** Marker concordance, label transfer, or the consensus annotation engine the
  umbrella already carries as a released package. The engine exists and 14782 ran a full campaign on it, so
  reusing it is the cheapest route to a defensible answer; evaluate it rather than assuming it.
- **What the crosswalk is as an artifact.** A table keyed by both label spaces with their versions, a
  status per pair, and the evidence that supports each mapping. It is an artifact other work will pin, so it
  carries its own version.
- **Which populations the pilot actually needs.** The effector compartment carried the earlier anchor. A
  crosswalk over the whole roster is the goal; a crosswalk over the compartment that the first run needs is
  the deliverable that unblocks it.

**Second, the network runs in `30_grn/`.** Paired multiome mode first, on v2 coordinates, consuming the other
agent's `10_requantify_embed/` outputs. Unpaired metacell mode after, once the crosswalk exists. Report the
two as separate products with the inference source on every edge and regulon, and keep the overlap class,
shared against paired-only against unpaired-only, as a first-class queryable column rather than a footnote.
That was already your design ruling; it now has runs to attach to.

Note the coordinate complication you found, because it lands on you: the regulatory branch goes through an
mm39 to mm10 crosswalk since the cisTarget databases are mm10. Whatever you produce carries both coordinate
systems and the chain identity, and says which one each artifact is in. A regulatory region silently in the
wrong assembly is the kind of error that survives review.

## The output contract

Every analysis yields two things. Its native artifact in the tool's own form, so the tool's diagnostics
remain available. And one universal queryable table per tool, typed, named, with its grain stated in a
sentence.

Two requirements, because they are what makes a later schema possible:

- **One grain per file.** A regulon row is one regulon in one run; an edge row is one factor, one region, one
  target, one group; a crosswalk row is one label pair. Do not mix them.
- **Identities travel with values.** The run identifier, the label version and level, the condition, the
  inference source, the coordinate system and chain, the motif and database releases, and a measurement
  status. A number whose provenance is not on its row cannot enter a schema later.

Do not build the ledger and do not create `03_results/objects/peakdb/`. How these tables integrate, including
the reconciliation between the star schema and the existing tall evidence grammar with its missingness
vocabulary, is the owner's decision after the runs exist.

## What is not yours

The requantification and the chromatin readouts, meaning motif enrichment, deviations, footprinting and
peak-gene linking, belong to the other agent. You consume one interface from them, the outputs of
`10_requantify_embed/`, and you should ask them to caption it as an interface and tell you when it is final.

The transposable-element concern is not yours; see the handover section above. In particular, do not plan a
TE dimension into the regulatory tables. When TE evidence joins a regulatory region it will join through
peak coordinates and a pinned reference build, and that join is designed later.

## The namespace question

Create `30_grn/` as the owner named it. The rename of the existing `scripts/foundation/` stays with D1 and is
not part of this work.

## Two prerequisites

The cisTarget snapshot, the motif collection and any database the run pins are external inputs that need a
release, a digest and a provenance entry before a run consumes them. One of them already sits in the shared
reference cache; name what you use.

Installing software is the owner's decision. If a route needs a package that is absent, ask for it with the
reason rather than installing, and say whether a route without it exists.

## How to open

Open with the crosswalk, not with the network. The crosswalk is the only thing on the critical path that
nobody else can start, its level decision is the one that most constrains what the unpaired run can claim,
and it is answerable with evidence you already hold. Bring the level you think the evidence supports and what
it rests on.
