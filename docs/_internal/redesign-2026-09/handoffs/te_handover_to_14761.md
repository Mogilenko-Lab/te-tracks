# Shared handover to the 14761 agents (from the te-tracks orchestrator)

Paste this into both the D2 and the D3 agent, before their own brief. It is the part only the te-tracks side
can write. The namespace and the environment policy in it are the owner's, confirmed 2026-09-18.

## Why the separation, for the record

Four boundaries, each of a different kind.

**A reference is not an analysis.** te-tracks pins one RepeatMasker run into identities and intervals and
knows nothing about what reads it. It is built once, published immutably and pinned by digest. Inside an
analysis namespace every analysis rerun becomes a potential reference change, which is the failure the
package exists to prevent, so it arrives in `40_transposable_elements/` as a pinned dependency rather than
as code the dataset owns.

**Only one of the two downstream lines has a dependency.** Requantification gates the chromatin readouts and
the paired network run. The 14616 label crosswalk gates the unpaired network run and nothing else. One agent
doing both serializes the crosswalk behind work it does not need; two agents put the only unblocked
critical-path item in flight immediately.

**The split matches accumulated context.** One agent has been reasoning about the peak ledger, sub-peak grain
and the admission law; the other holds the paired-against-unpaired measurement and the inference-source
design. Each receives the runs that produce the evidence its own design question needs.

**Export format is a decision, not a byproduct.** `90_integration_exports/` exists so that how results leave
this dataset is settled once, deliberately, after the tables exist.

## The namespace, settled

`02_analysis/scripts/` becomes `00_foundation_peak_atlas/` for the frozen arc from raw through annotated
object to the v2 atlas, `10_requantify_embed/` for peak by cell on v2 with embeddings and the
weighted-nearest-neighbour refresh, `20_chromatin_readouts/` for motif work, footprinting and peak-gene
links on v2 coordinates, `30_grn/` for the network rework, `40_transposable_elements/` for the TE branch, and
`90_integration_exports/` for cross-dataset handoff surfaces. Create the folders your own work needs. The
rename of the existing `scripts/foundation/` is ruled and belongs to D1's migration, performed against the
literal-path checklist in one sitting rather than piecemeal during a run.

## `40_transposable_elements/` is not yours

A separate session owns the whole TE endeavour: acquiring, pinning, parsing, qualifying, exporting and
publishing the mm39 RepeatMasker projection, and later the branch that lands in that folder. Two statements
in your re-orientation are now out of date.

**"No RepeatMasker mm39 annotation exists anywhere on disk, in the lake or under references, so the TE
dimension has no source yet."** False. A complete, tested projection exists at
`/workspaces/Meta-Aging/01_modules/te-tracks`, built and verified, in its last phase before publication to
the shared reference cache.

**"Acquire the RepeatMasker mm39 annotation into the reference lake."** Dropped. A second unpinned copy with
no identity is exactly the failure that package prevents. If you need TE intervals for a sanity check, ask.

## Do not design the TE schema, and do not block on it

How TE evidence joins anything is decided later, after your tables exist and te-tracks is published. Treat it
as absent. Your entire TE obligation is five things, none of which is designing a satellite, and they exist
so one is addable later without re-releasing what you publish now.

1. **Exact coordinates with the convention declared.** Half-open zero-based start and end as separate typed
   columns, beside whatever string key your existing tables use.
2. **A stable peak identity and a release identity.** The within-release identifier plus a content hash of
   the admitted set, and a coordinate key for cross-release joins.
3. **The assembly and contig dictionary pinned by name on the release manifest**, as a recorded fact rather
   than an assumption. This matters because the mm10 lift the regulatory branch needs makes two coordinate
   systems live in one repository.
4. **Room for `te_catalog_id` and `te_build_id`, unpopulated.** An overlap that cannot say which reference
   build produced it cannot be reproduced, and leaving no place for them means a re-release.
5. **A measurement status that can express "not computed".** Yours already does.

If you find yourself reasoning about TE classes, families or loci, you have crossed the seam.

## Four measured facts, so the eventual satellite is not designed against wrong assumptions

- **429,440 of 5,320,771 records overlap another record**, 198,956 of those pairs crossing instance
  boundaries, and the source's own overlap flag is constant false for this run. A peak-by-TE relation needs
  an explicit deduplicating rule before any accessible base is summed over TEs.
- **An instance is a grouping hypothesis, not an insertion.** 30,569 interspersed instances mix subfamily
  names and 23,244 mix strands. Every per-locus count in the field is a count per record.
- **RepeatMasker's three tokens straddle the field's ranks**, so filters surprise: 558,808 records sit under
  family `Alu`, nothing is spelled `MaLR`, and a filter for `SINE/B1` returns nothing. The pinned Dfam view
  exists to give aggregates a definition.
- **Mappability biases the TE side of every assay**, as your P4 note already says. Keep that note: the
  reference can make the bias nameable per record through divergence and lineage, never remove it.

## When you can consume it

te-tracks is in acceptance. Publication runs on the host because the reference cache is read-only in the
container. When it publishes you receive the family name, the full `BUILD_ID` and `CATALOG_ID`, the export
paths and the digests to pin. Until then do not read from its scratch root: it holds deliberately superseded
intermediate builds, and pinning one would be worse than pinning nothing.

Two things about the seam are already decided, so design compatibly. The interval catalog you would join
against is the complete catalog rather than the counting universe, because admitting a peak is your
producer's decision and never the annotation's. And genic context, meaning exon, intron, promoter window or
intergenic, is not published as a label: te-tracks publishes geometry and the consumer derives the label.

## Environments are yours to build, under three conditions

You may create virtual environments and install into them, and you may install into the base environment.

1. **Every install is frozen and reproducible**: a pinned requirements file, the resolved versions, and the
   command that recreates the environment from scratch.
2. **The container's environment state is documented as it now stands**: which environments exist, what each
   is for, and which scripts run under which.
3. **Prefer an environment beside the scripts it serves**, so the correspondence is visible rather than
   remembered.

A route needing a package nobody has documented is not reproducible yet, so document first and install
second.

## `90_integration_exports/` is a planned decision point

How each analysis leaves this dataset for meta-level consumers is settled deliberately once the tables
exist. What you owe it meanwhile is that every universal table carries its own grain in one sentence and the
identities it was computed from, because an export format can be chosen over tables like that and cannot be
chosen over tables without them.
