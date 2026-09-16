# ADR-6 + ADR-7 consult

**Ruling: AMEND both decisions.** The missing contract is the boundary between an annotation, a gene-dependent interpretation, and evidence that a particular builder produced and validated them. As written, the decisions let a GENCODE update rename an unchanged ATAC reference, while leaving unclear whether a change to coordinate semantics renames identical data bytes. Those two consequences point in opposite directions.

This review used local reads only. Citation prefixes are relative to `/workspaces/Meta-Aging`: **T** = `01_modules/te-tracks`; **I** = `01_modules/.ref/irescue`; **M** = `01_modules/.ref/MATES`; **S** = `01_modules/.ref/stellarscope`; **E** = `01_modules/.ref/TEsingle`; **A** = `_scratch/te-tracks-audit`; **L** = `.agents/skills`. Line numbers for compressed sources refer to their decompressed text. Recommendations below are proposed contracts; no builder, quantifier, installation, network request, or git command was run. This document is the sole write.

**1. Keep `.out` as the primary representation; qualify the provider and format.**

The useful invariant is a pinned RepeatMasker result on a precisely identified assembly. A UCSC URL template is only one way to obtain it. IRescue explicitly configures hg38 and dm6 `.out.gz` URLs, and even mm10 uses a different `bigZips/initial/` path (`I/irescue/_genomes.py:6–19`). MATES declares versioned RepeatMasker-hosted hg38 and mm10 paths (`M/MATES/scripts/Ref2csv.py:7–22`). These local declarations establish candidate routes; this offline review establishes neither current remote availability nor equality between providers' runs.

For an assembly absent from UCSC, accept a qualified assembly-specific result from `repeatmasker.org/genomes`, an appropriate Dfam annotation distribution, or an externally completed RepeatMasker run. Each route needs exact files, assembly sequence scope, checksums, and a format profile. A Dfam library/model download belongs upstream of masking; genomic record coordinates and instance linkage require an annotation result. Dfam endpoint availability, formats, and instance-ID preservation remain unverified in the supplied local evidence. An unavailable source leaves that assembly pending. A fallback provider starts a separately identified run.

The missing mm39 pin can already be filled from the local cached bytes. A read-only streaming hash in this review gave:

```text
source: A/source/mm39.fa.out.gz
bytes:  169199039
md5:    ffc8399d05f3388d80b78c93482a5b95
sha256: 84af3a7a84aac1d5c980a75ded762c45559df55ef1c0281f430112ed2a596307
```

The parser must preserve information that the existing consumer adapters discard:

| Hazard | Required contract and acceptance case |
|---|---|
| Whitespace and headers | Parse whitespace-delimited fields under a named format profile; recognize permitted headers and blank lines, and fail with source line number on a malformed data row. The modern ID-bearing profile has 15 fields plus an optional final `*`. Exercise headerless input and repeated headers only if explicitly supported. IRescue blindly skips its configured header count and indexes fields; MATES drops the first two lines (`I/irescue/map.py:111–130`; `M/MATES/scripts/Ref2csv.py:58–64`). Neither adapter establishes a general parser contract. |
| Parentheses | Remove enclosing parentheses only from the numeric fields that use them. Preserve repeat names such as `(TGCT)n` verbatim. Preserve signed numeric values; apply profile-specific validation instead of a global punctuation strip or absolute value (`A/source/mm39.fa.out.gz:4–6`). |
| Strand and consensus coordinates | Accept `+` and `C` in the primary profile, mapping `C` to `-`. Preserve the raw strand and three consensus tokens. With one-based field numbers, `+` gives consensus start/end/remaining in fields 12/13/14; `C` gives remaining/end/start. The actual ID2 example is `(48),104,5`, yielding start 5, end 104, remaining 48 (`A/source/mm39.fa.out.gz:5`). A literal `-` requires an explicitly supported source dialect. IRescue maps every non-`+` value to minus, which would also conceal an invalid token (`I/irescue/map.py:154–156`). |
| `*` | Store the overlapping-match flag independently of the instance ID and retain the record in `all_rmsk`. A policy may later use the flag explicitly. Include a starred fixture: mm39's measured absence of stars gives this branch zero coverage (`A/report/AUDIT.md:39–45`). |
| Class/family | Preserve the combined source token; split once at `/`. Define the projection for a token with no family. UCSC duplicates `Simple_repeat` into both columns where `.out` has one token (`A/source/mm39.fa.out.gz:6`; `A/source/rmsk.txt.gz:3`). Preserve that missing-family distinction alongside any UCSC-compatible family projection. Otherwise the source switch silently changes taxonomy for some classes. |
| IDs and source scope | Retain the true raw ID and source-row locator. Scope instance membership to the source run/unit and query sequence; independently produced shards can reuse an ID. Qualify grouping before combining shards. An older or ID-less format needs a separate capability decision before instance exports can be enabled. UCSC's table cannot repair this information loss: its schema declares `id char(1)` (`A/source/rmsk.sql:40`). |

Validate genomic bounds against the actual assembly sequences, and validate record-key uniqueness on each new source. The mm39 key's uniqueness is an observed property of that source. A future duplicate with the same name, coordinates, and strand requires an explicit identity rule before admission. The manifest also needs species/taxon, assembly accession/version, included contigs, alias mapping, and sequence identity. For hg38, a primary-assembly gene annotation and a TE annotation containing additional contigs can both be legitimate inputs; their coverage relationship must be explicit. A contig absent from the gene annotation has unknown gene context.

The `.out` digest identifies the result bytes. It cannot recover the RepeatMasker executable, search engine, options, exact library, or consensus sequences. Preserve the supplied mm39 run/library declaration with its evidence and a `declared` status (`A/consult/adr/DECISION_STATE.md:30–33`); retain the upstream README when available. For other sources use explicit unknown fields where provenance is unavailable. For externally supplied runs, collect engine/version/options and actual library file digests as well as release labels. The downstream question “which consensus sequence and library did this name mean?” otherwise becomes unanswerable when a name is reassigned. Reproducing this projection from retained `.out` bytes and reconstructing the upstream masking computation are separate reproducibility claims.

**2. Move `rmsk.txt.gz` to source qualification.**

Keep the pinned mm39 comparison as evidence and run the comparison when qualifying a new source pair or changing the parser. Remove it from the mandatory production dependency graph. Both files derive from the same run, so agreement supplies a useful conversion check with limited independence. Requiring both on every build doubles provider coupling, prevents otherwise valid non-UCSC sources, and repeats the check when only an export changes.

The comparison should establish multiset equality, including multiplicity, over normalized coordinates, strand, name, class/family projection, scores, divergence/deletion/insertion values, and consensus coordinates wherever represented. State each conversion: UCSC genomic starts are zero-based; its parenthesized remaining values appear as negative integers; its divergence fields use tenths of a percent. The local first records demonstrate these encodings (`A/source/rmsk.txt.gz:1–3`; `A/source/mm39.fa.out.gz:4–6`). Exclude the lossy table ID from equality and check `.out` linkage separately. The audit script's set comparison proves a narrower coordinate/name correspondence (`A/audit_out.py:30–36`); it supplies no complete field-level parser certification.

A qualification result should bind the two source digests, parser revision, compared fields, and reviewed discrepancies. Ordinary builds verify their single primary pin and run known-answer parser fixtures. A missing table is an unavailable cross-check; a discrepancy between an advertised matched pair blocks qualification until explained.

**3. Define BUILD_ID over scientific identity and payloads.**

Keep builder SHA outside BUILD_ID, but put it in an explicitly excluded provenance section. Hashing output bytes alone leaves source identity, coordinate conventions, unit definitions, and universe semantics free to change under an existing ID. The current implementation excludes the whole manifest (`T/src/release.sh:21–30`); placing `schema_version` in that excluded manifest cannot fix this.

Use one manifest with two defined sections:

- `identity`: build family; schema version; species/assembly and source identities; declared RepeatMasker run/library identity; exact parent build IDs; executable universe definitions; export contracts; and the complete sorted file inventory with relative paths, byte counts, and SHA-256 digests. Gene-dependent builds include the actual GTF digest and transformation policy. Inventory every shipped data/source file, and identify external dependencies explicitly.
- `provenance`: producing builder SHA, resolved build-tool versions, invocation, and validation evidence. Record source acquisition locations and time here. Require a recoverable clean producing revision for publication. A SHA alone leaves compression and dependency versions unspecified.

Define the recipe once, including the canonical JSON encoding:

```text
BUILD_ID = SHA256("te-tracks-build-v1\n" + canonical_json(MANIFEST.identity))
```

Use SHA-256 directly for new file inventories; existing MD5 pins can remain source checks alongside it. The manifest and `BUILD_ID` file sit outside their own inventory. The current build's ID also stays out of its payload tables; ingestion adds build scope. Parent IDs in a derivative are ordinary inputs. Canonical encoding must fix ordering, UTF-8 handling, numeric representation and terminal newline; reject duplicate JSON keys and invalid paths. This supplies one build-identity algorithm for both families.

“Identical build” then means identical scientific contract and delivered payload bytes. Production history is separately recorded. A single hashed schema version can define a frozen contract, provided the verifier implements that version, rejects unsupported versions, and checks the declared schema, membership and interval invariants. Merely writing an integer supplies none of those guarantees.

| Change | Required outcome |
|---|---|
| Builder documentation or a fixture changes; contract and outputs agree | Same BUILD_ID after the current validation suite passes. Preserve the already published manifest and first producer; record a later validation/reproduction in that run's evidence. |
| A stronger fixture exposes an existing defect | Validation fails before deduplication or promotion. Matching an existing ID confers no exemption. |
| Schema meaning, source/library declaration, universe definition, or a real dependency changes while table bytes happen to agree | New BUILD_ID because the hashed scientific contract changes. |
| A new export is added | New BUILD_ID in the family delivering it. Keep the old directory immutable. |
| Different compression produces different bytes for equivalent rows | New BUILD_ID. Pin serialization/compression for reproducible bytes; use table comparisons to establish semantic equivalence. `gzip -n` currently removes header timestamps, but does not specify the complete compression implementation (`T/src/10_build_master.sh:67`). |

A consequence of excluding provenance deserves an explicit sentence in the implementation contract: independently reproduced builds can have the same BUILD_ID and different raw manifests. Deduplication preserves the first published directory; it never rewrites producer metadata. A transferred release preserves that manifest exactly. Consumers pin the full BUILD_ID, the raw manifest checksum, relative export paths and checksums, universe, feature resolution, and required parent IDs. A claim of byte-identical *entire directories*, including producer metadata, would require a different hash boundary.

Reject the alternative of hashing the whole producing commit into the scientific identity: a docs-only change would create a new reference and new ledger scope. Also reject a payload-only hash: the same integers can represent different coordinate systems. The explicit identity/provenance split handles both cases without introducing a second annotation ID.

**4. Use two build families, with an explicit parent edge.**

Keep core records, instance membership, taxonomy, universe definitions/membership, and gene-independent exports in `te_<assembly>`. Put exon-subtracted SAF and later record-by-transcript relations in `te_<assembly>_gene`. Each family uses `archive/<BUILD_ID>` and the same manifest/verification rules. A derivative manifest pins `parent_core_build_id`; its record foreign keys point to that parent's catalog. The ledger keeps the core build ID for annotation entities and the derivative ID for gene-dependent measurements and relations.

```text
species/taxon -> assembly accession + sequence/contig identity
assembly + RepeatMasker version/engine/options + library version/content
    -> RepeatMasker run/result (.out pin; upstream computation)
.out + assembly/aliases + universe definitions + taxonomy policy + export specs
    -> core build C [canonical annotation + gene-independent exports]
assembly + gene provider/release/content -> gene annotation G
C + G + exon/context policy + export specs
    -> gene-dependent build D [noExon SAF; later transcript relations]
C exports and/or D exports + D's exact C parent + alignment/reference pins
    + assay/counting parameters + consumer software -> consumer run
```

The upstream masking computation remains outside te-tracks. Species and assembly constrain source admission; run and library identify the annotation's origin; universe definitions are transformations of that run; exports are versioned serializations/views; the consumer run owns the measurement. GENCODE is one gene provider. Another species can supply an assembly-compatible annotation through a qualified GTF/GFF adapter.

A GTF update creates D2 while C remains usable unchanged. Two gene providers can produce D1 and D2 from the same C. Adding a core export creates C2; derivatives that adopt C2 get new IDs because their parent changed, even when their tables agree. Accept that bounded consequence of one ID per delivered bundle. Comparing canonical checksums supports reuse across C1/C2; a third export-only family is unnecessary at this stage. Consumers obtain the parent from D's manifest, rather than independently resolving two `current` links.

The existing fetch stage already makes the gene GTF mandatory before any gene-dependent table exists (`T/src/00_fetch_sources.sh:14–20`). Remove that core dependency. The first noExon deliverable can still ship alongside the first core release as a separate child build. This also prevents the later transcript-context stage from requiring an in-place edit of a published catalog.

The gene-dependent contract must pin the exact effective annotation after filtering and alias conversion. Define exon subtraction as interval clipping against the selected union of annotated exons, with the strand rule, minimum retained block length, contig coverage, and grouping unit recorded. The local SAF recipe uses all `exon` rows and unstranded `bedtools subtract`, retaining pieces (`L/te-reference-saf-build/scripts/build_te_saf.sh:95–124`). That is an available compatibility policy. MATES' stock path instead filters TE contigs through the gene annotation, removes whole records overlapping gene bodies, and clips long intervals (`M/build_reference.py:108–164`). A direct MATES serialization belongs in C; reproducing those gene-dependent transformations belongs in D.

The four modality challenges expose why this separation matters:

| Modality | Failure hidden by one undifferentiated build |
|---|---|
| 3-prime nuclear RNA | Exon subtraction retains intronic TE sequence in host pre-mRNA. A noExon count alone cannot identify autonomous TE transcription. Use C for the inclusive reference and D for transcript/strand context, with origin interpretation in the run. TEsingle actually consumes a separate gene GTF as full transcript spans, so that run has its own gene dependency even with a gene-independent TE GTF (`E/TEsingle:110–112`). Its default cutoff is 1,000 raw UMIs per barcode and must be pinned in the run (`E/TEsingle:92–93`). |
| 5-prime whole-cell RNA | A TE record start does not establish an active promoter or transcript origin. Pin actual genomic-mate layout, strand rule and molecule counting. Stellarscope distinguishes single-end F/R from paired-end FR/RF using different mates (`S/stellarscope/utils/calignment.pyx:54–68`). TEsingle's overlap path takes each alignment's reverse flag without consulting mate identity (`E/TEtools/AlignmentIO.py:65–76`), so a parser fixture alone cannot certify the paired-end assay contract. |
| Paired-end ATAC | Gene annotation changes should leave C's sequence intervals and peak joins intact. Preserve disjoint instance blocks; a pair can span a TE while both insertion sites lie outside it. The run must distinguish fragment overlap, cut counts, Tn5-shift convention and duplicate handling. A later TE promoter view would add an explicit structural dependency. |
| Bulk RNA | Pin the gene annotation used both to make D and to count genes, together with paired-fragment, strand and multimapper policies. Separate featureCounts passes can count a fragment that touches a retained TE block and a gene exon even after basewise exon subtraction; disjoint intervals alone cannot guarantee joint molecule conservation. The local TE pass uses `-M`, `-s 0`, and `-p --countReadPairs -B -C` (`L/te-gene-featurecounts/scripts/runFeatureCounts_TE_and_genes.sh:122–129`). |

These are consumer-run obligations. A tested annotation file establishes feature geometry and identity; assay-specific evidence establishes what its counts mean. In every modality, require BAM/reference contig and sequence-scope checks: IRescue otherwise warns and skips unmatched contigs while continuing on the remainder (`I/irescue/map.py:231–240`).

**5. Keep immutable archives and atomic selection; extend the failure contract.**

Staging, verification, immutable installation and one mutable selector remain the right design. The six earlier cases need the following additions:

- **Interrupted HPC transfer:** copy a resolved source build into fresh staging on the destination filesystem. Verify exact inventory, all checksums, BUILD_ID, raw-manifest transfer checksum, and every required parent there. Install parents before promoting a child. Only then install the destination archive directory and replace its local `current`. Interruption must leave the destination's old selection usable. Transferring the workstation's `current` link or copying directly into a final hash directory exposes incomplete releases. The present transfer guidance only says to verify after transfer (`T/docs/RELEASES.md:70–71`).
- **Filesystem semantics and occupied destinations:** directory installation and pointer replacement require qualified same-filesystem rename semantics. Put the temporary selector beside the final selector. Require an exclusive/no-replace install, or serialize cooperative publishers around checking and installing the destination. Plain directory rename can replace an existing empty directory, so test an empty hash destination, an escaping symlink and a conflicting nonempty destination as well as ordinary concurrent builds. A target lacking the required atomic operations remains unsupported for `current` publication; copying or unlinking/recreating the link cannot supply the promised visibility guarantee.
- **Permissions:** normalize final modes and ACLs before selection; test actual consumer traversal/read access and restricted write access. A `mktemp` staging directory can remain private after rename, while the current shared `umask 002` permits group modification (`T/lib/common.sh:6–7`). Protect the archive parent as well as payload files. Payload checksums do not establish accessibility or immutability. The verifier must keep scratch outside the release; it currently writes `.class_observed.tsv` inside it (`T/src/99_verify.sh:49–57`).
- **Readers during a swap:** an already open file continues to refer to the old file on the qualified POSIX filesystem. The dangerous reader opens file A through `current`, then file B through `current` after promotion. Require one initial resolution to an immutable directory, or a directory handle, for the entire read. Test both an open handle and a later second-file open. Retaining the old archive makes either complete selection safe; network-cache delay can select an older complete build.
- **Crash durability and write races:** atomic visibility and power-loss durability are distinct promises. Flush files and affected directories in publication order where crash durability is claimed; qualify that behavior at both roots. Freeze staging against concurrent writers before the final verification/install boundary. Reject unexpected files, payload symlinks and path traversal in manifests. The current verifier checks only listed files (`T/src/99_verify.sh:20–33`). Exercise disk-full and permission failure before installation and before selector replacement; an unselected complete archive is a valid recovery state.

For concurrent promotion of different valid builds, document last-successful-selection semantics. Reproducible jobs use exact IDs. A future requirement for controlled chronological promotion would justify additional coordination; the current use case needs no chronological index. Removing `INDEX.tsv`, `CURRENT_BUILD.tsv`, dated release identity and archive-on-supersede remains appropriate.

**6. Retain published builds; defer deduplication machinery.**

At the stated 150 MB of compressed payload per build, 10/100/1,000 builds require about 1.5/15/150 GB per root. Exact-ID reuse already deduplicates identical bundles. Keep every published build and its dependency closure now; reclaim abandoned staging under an explicit active-publisher check. Automatic expiry of published parents would break derivative pins and readers.

Treat 150 MB as a payload estimate: the cached `.out.gz` alone is 169,199,039 bytes, before other sources, exports, and transcript relations. Record total physical storage per release and account for both roots. If retained sources later dominate, a checksum-addressed source store or filesystem reflinks can be introduced behind the same logical contract. Mutable shared hardlinks would couple archive integrity across builds. No custom deduplication service or published-build pruning policy is needed for the first release.

**Public decision text — AMEND ADR-6 and ADR-7:**

te-tracks projects a checksum-pinned RepeatMasker `.out` from a qualified provider, records assembly, run and library provenance, and uses available UCSC table comparisons during source qualification. Core annotation and gene-dependent views form separate immutable build families whose BUILD_IDs bind versioned scientific contracts, exact dependencies and complete payload inventories, with builder and validation provenance recorded separately. Publication verifies complete snapshots and their parents at each destination before immutable installation and atomic selection, and consumers pin exact build IDs and exports.

**Open items before implementation:**

1. Freeze the supported `.out` profiles and reviewed parser/cross-check fixtures, including missing-family projection, starred rows and ID scope; preserve the mm39 run declaration's source evidence. Qualify hg38/dm6 pins and provider capabilities before enabling those assemblies.
2. Choose the first gene-view policy's effective GTF, exon/strand/retained-block rules and feature grouping; encode that choice in D's identity and its conservation fixture.
3. Confirm the two publishing roots' atomic install/replace, permissions and durability contract, and freeze the canonical identity encoding plus the failure cases above as implementation acceptance criteria.
