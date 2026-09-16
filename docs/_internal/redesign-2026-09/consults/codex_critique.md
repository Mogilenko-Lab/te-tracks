# Second review: te-tracks redesign

## P1 — AMEND

The three grains are useful, but annotation identity, counting identity and biological insertion identity need separate contracts.

- Keep `fragment_id`, with its embedded coordinates explicitly **1-based inclusive in the UCSC namespace**, even when a delivered interval uses BED coordinates or Ensembl contig names. The ledger uses 0-based half-open coordinates: convert its columns, preserve the key. Rename ledger `locus_id`/`locus_fraction` to `fragment_id`/`fragment_fraction`, and `te_locus_dim` to `te_fragment_dim`.
- Assert uniqueness over **all** source records. F3 establishes uniqueness only in the legacy filtered set. Preserve source checksum plus data-record ordinal as an independent record locator; fail on unexpected key collisions rather than silently deduplicating.
- Treat `ins<ID>` as a **RepeatMasker-assigned instance**, not a validated biological insertion. Keep its raw ID, fragment membership, member taxonomy IDs, span and union-covered bp. Rename `is_composite` to `has_multiple_repnames`; a subfamily boundary is not evidence of a composite provirus. Quantification uses member intervals, never the bounding span, which can include nested elements and gaps. Declare whether counts describe full-source or universe-selected members.
- Use raw `taxonomy_id` for the default counting views. Canonicalization is an explicitly curated rollup with mapping version, evidence and unresolved cases; majority frequency alone does not establish the correct family. Canonical targets belong in a separately unique dimension: multiple raw rows may share one canonical target.
- Separate a source/annotation identity from the delivery `BUILD_ID`. Adding a BED view should not change every annotation foreign key. Hash a deterministic source/schema descriptor; keep delivery identity and canonicalization-policy identity alongside it. Avoid a circular definition in which table rows contain the hash of those same output bytes.

**Count correction:** 1,248 triples describes the set **with Satellite**. Proposed `interspersed` has 1,240 triples and 3,764,949 fragments.

## P2 — AMEND

Keep all 5,320,771 records in one logical canonical repeat table. Call it `repeat_fragments`, since its rows include non-TE repeats. Keep the additional 1,496,879 Simple_repeat/Low_complexity rows there; compressed Parquet with class filtering is a reasonable representation. Physical partitions are compatible with one logical table and do not require a second independently maintained authority.

Version each universe's exact predicate, including its handling of uncertain classes and missing values. Derive membership from **raw** classification; canonicalization must not silently change eligibility. Publish observed counts and unique feature inventories per universe. Changing the quantification universe changes competing assignments, so filtering a completed all-repeat count matrix is not generally equivalent to quantifying the smaller universe.

Simple/low-complexity overlap is useful for ATAC quality assessment and blacklist sensitivity analyses. It does not establish that every such interval should be blacklisted. Keep empirical blacklist release and overlap policy separate.

Suggested names: `all_rmsk`, `interspersed`, `interspersed_plus_satellite`, `retrotransposons`, `satellites`, `legacy_tetranscripts_mm39`. The last reproduces the packaged **interval selection**, not its exact labels or every TEtranscripts annotation. Add `simple_low_complexity` only when needed. Remove the claim that `all_rmsk` equals local IRescue auto-annotation (see F9 below).

## P3 — AMEND

Use the pinned `.out` as the primary record source, retaining the compressed source and header. Record-set equality on `(chrom,start,end,repName)` does not establish equality of strand, taxonomy, scores or consensus coordinates. Validate those fields before claiming that only `bin` and `genoLeft` are lost.

Specify `.out` parsing explicitly: genomic coordinates are already 1-based; `C` becomes minus strand; reverse-strand consensus fields change position and carry parenthesized remaining lengths. Preserve raw tokens plus normalized consensus start/end, remaining length and coordinate convention. Class/family arrives as a combined token; define how a token without `/` maps to the raw triple, verifying against rmsk rather than silently substituting an empty family for `Unknown`. Preserve overlap flags even though this source has none.

## P4 — AMEND

Staging, locking and verification address the measured corruption. One directory rename does **not** make directory publication, `current`, the index and the receipt one atomic operation.

Promote into an absent immutable snapshot path; then atomically replace `current` using a temporary symlink and rename. Keep old snapshots at stable paths so readers resolving the previous target retain access. Treat `current` as authoritative and make index/receipt updates recoverable and idempotent. A same-date collision must never overwrite an existing snapshot. Pass the family root explicitly: `dirname(staging_snapshot)` now resolves to `.staging`, so the existing release code cannot infer it correctly.

Under the family lock, verify current's manifest, complete expected file inventory and recomputed fingerprint against its recorded identity. If corrupt, fail and report corruption; do not legitimize it by assigning its changed bytes a fresh release identity. Guard every mutating entry point, including directly invoked stages. Verification should leave snapshot bytes untouched.

Fingerprint deterministic provenance too: schema, source pins, universe predicates and canonicalization map. Exclude volatile timestamps. Key expectations by source release and universe-policy version as well as genome. Check bounds against the actual pinned FASTA sequence dictionary, with explicit alias mapping; a second independently downloaded `chrom.sizes` file alone cannot prove sequence identity. Record verified and declared references distinctly.

## P5 — AMEND

The proposed boundary is sensible. Add now:

- Schema/identity versions, canonical contig namespace, alias-map checksum, FASTA sequence dictionary, and explicit genomic **and consensus** coordinate conventions.
- Raw source record locator, raw RepeatMasker instance ID, Smith–Waterman score, overlap flag, and raw class/family token. Record RepeatMasker/library version when recoverable; otherwise mark it unknown.
- Canonicalization version/evidence/status, universe-predicate versions, fragment length, insertion union-covered length, and explicit units/null meanings for divergence and indel percentages. Divergence is an annotation measurement, not a calibrated insertion age.
- For each delivered view: feature grain, name-to-dimension mapping, interval transformation and consumer/version contract. Ordinals for tool compatibility must be assigned over a fixed universe and mapped back to stable fragment IDs.

Keep transcript context as a separate many-to-many relation with pinned gene annotation, transcript/gene IDs, exon/intron relation, relative strand and union overlap bp per relation. Absence before that stage means **uncomputed**, not intergenic. Remove the ledger's premature required scalar `gene_context`; a fragment can be exonic in one transcript and intronic in another.

## Specific consumer decisions

**a. Name field:** choose raw `taxonomy_id` for IRescue custom BED and featureCounts SAF. This retains the measured classification distinctions and gives a unique raw-dimension join. Its cost is splitting 20 nominal subfamilies into separate count features, changing ambiguity/EM groups and complicating legacy comparisons. Summing post-EM triple counts need not reproduce an EM fit with repName groups. Label the grain `taxonomy`, rather than promising ordinary subfamily counts.

Keeping `repName` is valid for an explicitly requested subfamily estimator with a unique repName dimension and reviewed canonical mapping. Its failure is irreversible loss of raw family/class attribution in those counts; joining directly to the raw triple dimension multiplies rows. A canonical mapping fixes join cardinality, not the lost evidence. Neither naming choice makes two quantifiers' estimators equivalent.

**b. Canonical table:** retain simple/low-complexity records in it, as above. Separate filtered views or physical partitions preserve one source of truth and support ATAC overlap checks.

**c. Grammar:** the proposed punctuation is usable as opaque text in BED names, SAF GeneID values and DuckDB VARCHAR values. Store the component columns; never recover coordinates by splitting an ID. GTF values need quoted, escaped attributes with the keys required by each consumer; valid punctuation alone does not establish TEtranscripts/Telescope compatibility. Validate raw components for reserved delimiters, tabs, newlines, quotes and whitespace; `:` concatenation is unambiguous only if components cannot contain `:` or have a reversible escape convention.

IRescue `map.py` propagates BED column 4 into intersections, but `chrcat()` uses **commas** to serialize feature sets and whitespace-based awk fields, and strips `#...` from the display-name column. Reject commas/whitespace in exported identifiers. The proposed `|`, `:` and strand suffix do not trigger those operations. Use BED6; custom `-r` determines the grouping, while `--locus-level` does not reconstruct custom intervals into instances. Preserve its valid explicit option syntax.

TElocal `locInd` compatibility remains **unverified**: the requested files provide no TElocal parser or index builder, and no matching files were found under `01_modules/.ref`. Do not advertise locInd as a generic text projection or assume arbitrary IDs survive its builder. Pin and inspect that implementation before shipping; provide a reversible tool-ID map if it requires a particular naming convention. SAF/GTF consumer-specific acceptance was not executed in this read-only review.

**d–e.** Universe names and missing required metadata are specified in P2 and P5.

## f. Audit corrections and interpretation limits

- **F9 is contradicted by the requested local code.** `makeRmsk()` explicitly skips `Low_complexity`, `Simple_repeat`, `rRNA`, `scRNA`, `srpRNA`, and `tRNA`. `snRNA` is absent from that exclusion list. The audit's “NO class filter” and P2's IRescue equivalence are false for the code read here; this may reflect a checkout change since the audit. No replacement count is inferred.
- **F9 opacity needs qualification:** `chrcat()` does name processing and comma serialization. `getRefs()` warns and skips unmatched references when some references match; it does not guarantee full contig concordance.
- **F1 overstates biology:** instance linkage is valuable, but “ERV provirus structure comes for free” goes beyond the measured ID grouping and examples. Full-length structure, orientation and nested components still require validation.
- **F3 is scoped evidence:** filtered-set uniqueness and the reported overlap statistic do not prove full-source uniqueness or count all overlap pairs.
- Equal `BUILD_ID`s support equality of the fingerprinted delivered outputs, not whole-snapshot/source/manifest byte identity. The current fingerprint explicitly excludes those files.

All explicitly requested files were readable. No network, installations, builds or git writes were performed. This critique is the only file written.
