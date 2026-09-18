# The transposable-element concern moves to te-tracks (handover from the TE orchestrator)

Paste this section into both the D2 and the D3 agent. It is the part of their brief that only the te-tracks
side can write, and it replaces two beliefs their re-orientation recorded.

## What changed

The transposable-element concern is no longer yours. A separate session owns it and has been building it for
several days. Two things you concluded are now out of date.

**"No RepeatMasker mm39 annotation exists anywhere on disk, in the lake or under references, so the TE
dimension has no source yet."** That is no longer true. A complete, tested reference projection of the mm39
RepeatMasker run exists at `/workspaces/Meta-Aging/01_modules/te-tracks`, built and verified, and is in its
final phase before publication to the shared reference cache.

**"Acquire the RepeatMasker mm39 annotation into the reference lake" as an action item you could start.**
Drop it. Acquiring, pinning, parsing, qualifying and exporting that annotation is te-tracks' whole job, and
duplicating it would create a second unpinned copy with no identity, which is the exact failure the package
exists to prevent. If you need TE intervals for a sanity check, ask for them rather than downloading them.

## What te-tracks is, in the terms your ledger cares about

It projects one checksum-pinned RepeatMasker run for one assembly into canonical tables, named universes and
registered exports, with every emitted feature joined back to its source record. It carries no knowledge of
what the annotation is used for; quantification and biological interpretation are the consumer's.

| fact | value |
|---|---|
| records in the mm39 run | 5,320,771 |
| the default counting universe, `interspersed` | 3,764,949 records over 1,220 subfamily names |
| the complete catalog, `all_rmsk` | every record; its record BED is the interval catalog a peak ledger keys on |
| contig namespaces | `ucsc`, `ensembl`, `gencode`, with an injective 61-contig alias table |
| coordinate conventions | tables, GTF and SAF are 1-based inclusive; BED is 0-based half-open |
| record identity | `rmsk_record_id` is `<name>\|<chrom>:<start_1>-<end_1>\|<strand>`; the export spelling is `R\|mm39\|<name>\|<chrom>\|<start>\|<end>\|<strand>` |
| instance identity | `I\|mm39\|<id>`, RepeatMasker's grouping hypothesis |
| feature levels | record, instance, subfamily, canonical family |
| lineage and rank | a pinned Dfam 4.0 view: classification path, clades per model, and Wicker class through subfamily with a status per rank |
| build identity | `BUILD_ID` over the manifest identity; `CATALOG_ID` binds the record-producing source, so a serializer change moves `BUILD_ID` alone |

Four measured facts bear directly on the `te.parquet` satellite you sketched, and each is a design
constraint rather than a detail.

- **8.07 percent of records overlap another record**, 429,440 of 5,320,771, and 198,956 of those overlapping
  pairs cross instance boundaries. The source's own overlap flag is constant false for this run, so it
  cannot be relied on. A peak-by-TE overlap relation therefore needs an explicit deduplicating rule before
  any cut count or accessibility figure is summed over TEs, or the same accessible base is counted twice.
- **An instance is a grouping hypothesis, not an insertion.** 30,569 interspersed instances mix subfamily
  names and 23,244 mix strands. A "TE locus" in the field is a record, and every per-locus count is a count
  per record. Insertion-level units are reconstructions and te-tracks defers them with their evidence gates
  written down.
- **A subfamily is one consensus model.** RepeatMasker's three tokens straddle the field's ranks, so filters
  surprise: mouse B1 and PB1 sit under family `Alu` across 558,808 records, `ERVL-MaLR` is the largest LTR
  family and nothing is spelled `MaLR`, DNA superfamilies appear only hyphenated, and a filter for `SINE/B1`
  returns nothing. The Dfam view exists to give aggregates a definition.
- **Mappability biases the TE side of every assay**, and your P4 note already says so. Keep that note. The
  reference cannot fix it; it can only make the bias nameable per record through divergence and lineage.

## What you must not do

Do not design the TE satellite, do not choose its grain, and do not block any run on the TE schema. How TE
evidence joins the ledger is a decision the owner takes later, once your analyses have produced their tables
and te-tracks is published. Treat it as absent.

## What you must do, so the seam stays open

This is the whole of your TE obligation, and it costs you nothing you were not already doing. A TE satellite
has to be addable later without re-releasing anything you publish now, so the peak spine carries what an
interval join will need:

1. **Exact coordinates with their convention declared**, not only a coordinate string. Half-open zero-based
   start and end as separate typed columns, beside whatever string key your existing tables use.
2. **A stable peak identity and a release identity.** Your `v2c_NNNNNNN` within a release and a content hash
   of the admitted set are exactly right; keep both, and keep the coordinate key for cross-release joins.
3. **The assembly and contig dictionary pinned by name on the release manifest.** te-tracks refuses any
   build that is not the assembly it declares, and normalizes contigs through its alias table. Your peaks
   are mm39 under `chr` names; say so as a recorded fact rather than an assumption, because the mm10 lift
   your gene-regulatory branch needs makes two coordinate systems live in one repository.
4. **Room for two identity columns you do not populate yet**, `te_catalog_id` and `te_build_id`. When TE
   evidence arrives it arrives pinned to an exact reference build, and a ledger that cannot say which build
   an overlap was computed against cannot be reproduced. Leaving the columns unpopulated is fine; leaving no
   place for them means a re-release.
5. **A measurement-status vocabulary that can express "not computed".** You already have one, with
   `structurally_absent`, `not_computed`, `below_detection` and `failed_qc`. TE evidence will arrive as
   `not_computed` for every peak until it does not, and that must be sayable without a schema change.

Nothing else. If you find yourself reasoning about TE classes, families or loci, you have crossed the seam.

## When you will be able to consume it

te-tracks is in its acceptance phase. The builds are complete and verified in a scratch reference root; the
publication to `/data2/users/shared/refcache` runs on the host because that path is read-only inside the
container. When it is published you receive the family name, the full `BUILD_ID` and `CATALOG_ID`, the paths
of the exports you would read, and the digests to pin. Until then, do not read from the scratch root: it
holds intermediate builds that are deliberately superseded, and pinning one would be worse than pinning
nothing.

Two things are already decided about that seam and are worth knowing so you design compatibly. The interval
catalog you would join against is `all_rmsk/full/record.bed`, the complete catalog rather than the counting
universe, because admitting a peak is your producer's decision and never the annotation's. And genic context,
meaning whether a TE sits in an exon, an intron, a promoter window or between genes, is not published as a
label: te-tracks publishes geometry and the consumer derives the label, under the owner's ruling that one
component is responsible for one thing.
