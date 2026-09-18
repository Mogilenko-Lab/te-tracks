# Brief for the D2 agent: the chromatin readouts chain on the v2 atlas

Paste `te_handover_to_14761.md` first, then this.

## What your endeavour becomes

The three rulings stay on the table and you keep D2, but the peak ledger is no longer the thing that gates
progress. Your endeavour is to unblock everything downstream of the frozen peak atlas and to run it, so that
the schema question is answered later against real tables rather than in advance against imagined ones. The
owner's words: run these, then decide how to integrate them.

Your half of that is the peak side, in two namespaces, in order:

**`10_requantify_embed/`** — the rerun family, act one. Peak by cell requantification on the v2 atlas,
embeddings recomputed, the weighted-nearest-neighbour graph refreshed. Everything after this consumes it, so
it is the critical path and it comes first. Nothing downstream should start before its outputs are on disk
and captioned.

**`20_chromatin_readouts/`** — four analyses, each producing its own evidence, none of them a schema:

1. **Classical motif enrichment.** A pinned motif collection, JASPAR2022 or another named release, added to
   the object, then differential accessibility per compartment and motif enrichment over the differential
   peaks. The recipe in the field is a differential test with the fragment count as a latent variable, a
   significance and per-group-fraction threshold on the resulting peaks, and an enrichment test over that
   set. **The background set is an architectural decision, not a parameter**, and it is the first thing you
   write an architecture decision record for, because the enrichment answer moves with it. At minimum
   compare a GC-and-accessibility-matched background against the all-admitted-peaks background, on one
   compartment, and report how much the ranking moves. Whichever you recommend, the release manifest states
   it.
2. **Motif deviations.** chromVAR, per cell, which is a parallel instrument to the enrichment above rather
   than a confirmation of it: enrichment asks which motifs are over-represented in a peak set, deviations
   ask how accessible a motif's peaks are in one cell against a background expectation. Report them side by
   side and say where they disagree, because a disagreement is informative about the compartment rather than
   an error.
3. **Footprinting.** Differential footprinting for the compartments of focus, TOBIAS-style. This is the one
   with real prerequisites: it needs bias correction, adequate depth per group, and a decision about which
   groups have enough fragments to footprint at all. Write the depth floor you adopt and the groups it
   excludes, and report excluded groups as a missingness code rather than dropping them.
4. **Peak-gene linking.** The standard correlation-based linking on v2 coordinates, with the gene coordinate
   table and the transcription-start-site bed that already exist. State the window, the correlation method,
   the significance handling and the direction convention.

Compute over every label of the roster, all 12 parent, 26 fine and 33 state labels across the four
conditions, identically. Narrative focus is a filter applied when reading, never a boundary applied when
computing. That rule is already yours; it now applies to four more instruments.

## The output contract

Every analysis yields two things. First, its native artifact, in the form the tool produces, so the tool's
own ecosystem can read it and so a reviewer can rerun the tool's own diagnostics. Second, one universal
queryable table per tool, comma-separated, tab-separated or Parquet, whose columns are typed and named and
whose grain is stated in one sentence at the top of its caption.

Two requirements on the universal table, because they are what makes the later schema possible:

- **Its grain is explicit and single.** One row is one what. A motif enrichment row is one motif in one peak
  set in one contrast; a deviation row is one motif in one cell group; a footprint row is one motif in one
  group; a link row is one peak and one gene. Do not mix grains in one file.
- **It carries the identities it was computed from**, not only the values: the peak identity and release, the
  label version and level, the condition, the motif collection release, the run's own identifier, and a
  measurement status. A value without the identity of what produced it cannot enter any schema later.

Beyond that, do not build the ledger. Do not create `03_results/objects/peakdb/`. The star schema you
reconciled against the tall evidence grammar is a good design and it is not this task; it is the decision
the owner takes once these tables exist. Your reconciliation argument is worth keeping in writing for that
conversation.

## The namespace question

The owner's message names `10_requantify_embed/`, `20_chromatin_readouts/` and `30_grn/` directly, so create
those as named. The rename of the existing `scripts/foundation/` to `00_foundation_peak_atlas/` is a
separate matter and stays with D1: do not perform it as part of this work, because it touches literal paths
across a frozen arc and deserves its own sitting.

## What is not yours

The gene-regulatory-network rework is the other agent's, and so is the harmonization of 14616-DM's
annotation to this dataset's label standards, which is what unpaired-mode corroboration needs. You own one
handoff to them: the outputs of `10_requantify_embed/`, which the paired-mode network run consumes. Caption
them as an interface, name the files they will read, and tell them when the outputs are final rather than
letting them discover it.

The transposable-element concern is not yours; see the handover section above.

## Two prerequisites, one of which needs the owner

DuckDB is absent from both the Python environment and R, and Arrow is absent from R. **Installing anything is
the owner's decision and you do not have it yet, so ask rather than install.** Note that nothing in the four
analyses above requires it: pyarrow and polars exist in Python, and every universal table can be written and
read without a query engine. DuckDB becomes necessary when the ledger becomes real, which is after this work,
so the install is worth requesting in its own right rather than as a blocker on these runs.

The motif collection is a pinned external input and needs a release, a digest and a recorded provenance
entry, the same way the registry inputs already have. Name it before you scan with it.

## How to open

Do not open with the schema. Open with the run order and the two decisions that gate it: the background set
for motif enrichment, and the depth floor for footprinting. Both are architecture decision records, both are
cheap to measure and expensive to get wrong, and both are invisible in the output once chosen. Bring the
measurement, not the preference.
