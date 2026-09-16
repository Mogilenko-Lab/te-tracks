# ADR-3 / ADR-8 consultation

**Ruling: AMEND ADR-3; KEEP ADR-8.** The missing decision is the acceptance contract for a parked release: which assembly, contig namespace, feature identity, interval view and consumer version have actually passed together. Counting export files leaves those obligations implicit.

This is a read-only design review. I accepted the supplied measurements and inspected the local implementations; I ran no builds, quantifiers, installs, network operations or git commands. All tests below are proposed acceptance requirements. This file is the sole write.

Citation prefixes, relative to `/workspaces/Meta-Aging`: `T` = `01_modules/te-tracks`; `I` = `01_modules/.ref/irescue/irescue`; `S` = `01_modules/.ref/stellarscope/stellarscope`; `E` = `01_modules/.ref/TEsingle`; `M` = `01_modules/.ref/MATES`; `L` = `14761-DM/01_modules/scio/skills`; `A` = `_scratch/te-tracks-audit`. Each shortened reference below denotes an exact local file and line.

## Part 1 — What the proposed stopping point misses

### 1. Bulk support needs a usable starting annotation

Add full-interval `subfamily.saf`. A group starting with its own BAM and gene annotation needs a gene-independent TE reference before choosing an exon mask. The local SAF builder already creates both full and exon-subtracted files (`L/te-reference-saf-build/scripts/build_te_saf.sh:65`, `:78`, `:115`, `:124`); retaining only its subtracted endpoint discards a useful, cheaper contract.

Keep one plain `record.gtf` carrying the four TE attributes plus record and instance identifiers. A shared GTF is a reasonable target; shared scientific feature identity requires a consumer-specific check. TEsingle requires all four attributes and constructs `transcript_id:gene_id:family_id:class_id` (`E/TEtools/TEindex.py:315`, `:324`, `:329`), while Stellarscope groups rows by the selected attribute (`S/annotation/_intervaltree.py:41`, `:49`). TEsingle requires a `.gtf` filename and sorts it before indexing (`E/TEsingle:118`); Stellarscope opens ordinary text (`S/annotation/utils.py:103`). Shipping only `.gtf.gz` would already miss these entry points.

The four named checkouts contain no TEtranscripts or TElocal implementation, and the targeted search also found neither in the base Python environment. TEsingle's parser cannot certify those products. **TEtranscripts acceptance and TElocal's actual annotation/index route are mandatory evidence before advertising their compatibility.** Ship the portable GTF and a version-specific, tested ingestion/index recipe; defer a distributed `.locInd` binary until a consumer needs that exact serialization. Establish TElocal's route from its selected release rather than guessing a CLI or treating the GTF suffix as sufficient.

There is also a feature-grain choice inside the GTF. I recommend `gene_id` identify the build-scoped repName, `transcript_id` and `locus` identify a registered colon-free record alias, and `instance_id` identify its source grouping. Use the one-row-per-name canonical family/class in `family_id` and `class_id`, with an explicit reserved value for an unresolved rank; preserve exact source labels in additional `rmsk_family` / `rmsk_class` attributes and the catalog. This gives one taxonomy tuple per subfamily in the consumer-facing fields while retaining every source assertion. The two-family/one-name fixture must verify the actual bulk output grain before the shared GTF is certified.

`subfamily.noExon.saf` should likewise use repName, consistently with ADR-1. The established lab builder emits the different grain `repName:family:class` (`L/te-reference-saf-build/scripts/build_te_saf.sh:80`). Preserve a requested historical export as `taxonomy_triple.noExon.saf` under its explicit legacy universe; do not quietly substitute its contents under a subfamily filename. The lab's downstream documentation expects three-field names (`L/annotate-bulk-rnaseq-data/references/te-annotation.md:13`), so migration needs an explicit mapping and its own validation.

### 2. Exon subtraction solves an interval question

Choose a precise default: subtract the unstranded union of all `exon` rows in the pinned gene GTF, across its transcripts, preserving the remaining blocks and their parent record IDs. Record wholly removed records and retained base counts. The existing recipe performs that block subtraction (`L/te-reference-saf-build/scripts/build_te_saf.sh:95`, `:115`). A differently stranded or transcript-filtered mask is a separately named view.

The current README promises that the noExon SAF makes a joint gene/TE matrix count each read once (`T/README.md:61`), and the current ADR gives subtraction the same rationale (`T/docs/DECISIONS.md:35`). A paired molecule can place one mate in an exon and its other mate in a retained TE block; a spliced read or its alternative alignments can connect both annotations too. Separate counters can therefore count the same molecule. The contract should promise zero retained exon-overlap bases; exclusive molecule assignment belongs to the joint counting procedure.

This also exposes the missing downstream question: “Is the RNA at this TE explained by a host transcript?” Full intervals, strand and transcript relations preserve the evidence needed to investigate it. Exon subtraction alone leaves intronic host pre-mRNA in the TE view. A future transcript-context stage must represent overlapping and alternative isoforms and explicitly distinguish `not_computed`, outside annotated transcripts, and outside annotation coverage.

### 3. Human and another species test assumptions hidden by mm39

I recommend implementing mm39 first and requiring **a verified hg38 release as the second assembly before the broad reusable parking milestone**. A mouse-only milestone is useful and should be labelled `mm39 verified`; a human configuration stub would leave an external human bulk group doing the unfinished integration work. This is the concrete scope amendment to “human next.”

Assembly names alone are insufficient. Each configuration must identify the actual FASTA sequence set, contig lengths, RepeatMasker run/library, gene annotation and alias table. Primary, alternate, unplaced and decoy sequences need an explicit coverage policy. The contig report must distinguish an absent alias, a sequence absent from the chosen FASTA, a contig with zero annotated repeats, and a contig outside gene-annotation coverage. In particular, missing gene annotation on an alternate contig must remain visible in the noExon view.

Ensembl-named bulk exports are a day-one requirement. Use the named `ensembl` column of the pinned alias table and verify injectivity and sequence-length agreement. Even mouse scaffolds require real aliases: `chr1_GL456210v1_random` maps to `GL456210.1` (`A/source/chromAlias.txt:13`). Prefix stripping cannot supply that mapping. Partial mismatch is especially dangerous because IRescue warns and continues with matching contigs (`I/map.py:231`); MATES checks only that some contigs intersect (`M/MATES/scripts/count_coverage_10X.py:255`). Publish a small preflight command that checks the requested export against a BAM header or FASTA index and reports this coverage explicitly.

Five biological universe names can remain shared. `legacy_tetranscripts_mm39` is an assembly-specific, measured compatibility definition; an hg38 legacy universe requires its own packaged reference and reconciliation. Applying the mouse `tRNA*` predicate to human does not establish that history. New class vocabularies must trigger a reviewed mapping before they enter the shared universes; publish the observed class census and explicit inclusion/exclusion decisions.

Build scope also matters below the species level. Equal repNames across mouse and human provide a label match; homologous consensus identities require a separate accession/sequence crosswalk. A new `.out` must pass record-key uniqueness and instance-scope checks, including IDs reused across independently generated input chunks. Preserve source run/chunk identity where needed and reject ambiguous grouping. The measured mm39 uniqueness and single-contig grouping are acceptance examples, not universal RepeatMasker guarantees.

### 4. Modality coverage is more than parser acceptance

| Modality | Failure hidden by a successful file load | Required boundary of the parked contract |
|---|---|---|
| 3′ nuclear RNA | Intronic host RNA becomes TE-associated signal; raw-UMI filtering changes the nucleus roster. | Keep full intervals and source strand; exercise spliced and intronic alignments, actual CB/UMI tags and low-depth cells; report associated RNA at the measured feature grain. |
| 5′ paired-end whole-cell RNA | Treating both genomic mates as the same transcript orientation can change strand assignment or count a molecule twice. | Use a separate paired fixture with opposite-strand mates, shared CB/UMI, duplicate and secondary alignments, and alignments crossing feature boundaries; define accepted molecular counts before running it. |
| Paired-end ATAC | A fragment spanning a TE can have both cuts outside it; a TE-overlapping peak can hold a motif outside TE sequence. | Supply unchanged BED6 intervals and block membership; demonstrate fragment overlap, cut overlap and sequence intersection as distinct operations, with the supplied fragment coordinates' shift convention recorded. |
| External bulk RNA | A fixed paired-end, unstranded or Random-One recipe silently selects a counting model for another group's libraries. | Supply full and exon-subtracted SAF plus GTF; validate single-end and paired-end examples and explicit strand/multimapper settings; pin the user's matching gene reference for gene-aware views. |

These are concrete concerns in the checked code: TEsingle uses `CB` and `UR`, determines direction separately for each aligned read, and creates UMI entries before annotation overlap (`E/TEtools/AlignmentIO.py:34`, `:44`, `:57`, `:65`). Its default cutoff is 1,000 raw UMIs (`E/TEsingle:92`; `E/TEtools/Counters.py:244`). IRescue applies read-strand `-s` / `-S` and then extracts barcode/UMI-feature associations (`I/map.py:316`, `:328`). The lab bulk driver fixes `-M -s 0 -p --countReadPairs -B -C` (`L/te-gene-featurecounts/scripts/runFeatureCounts_TE_and_genes.sh:122`). None of those facts establishes the correct settings for every assay named here.

Keep the biological experiments and the full ledger outside te-tracks. Its fixtures should establish interoperability, geometry and conservation; identifiability benchmarks, autonomous-transcription inference, regulatory causality and GRN validation remain downstream work.

### Minimal complete deliverables

Each numbered item is required for the proposed parked milestone; optional branches follow separately.

1. **Full-source `rmsk_records.tsv.gz`, `rm_instance_members.tsv.gz`, `taxonomy_rmsk.tsv`, `taxonomy_canonical.tsv` and `universes.json`:** these preserve record identity, raw classification, classification uncertainty and original grouping before any consumer selection, including raw and normalized consensus coordinates, divergence, scores and available overlap flags for later structural work.
2. **Five UCSC-named `interspersed` exports: `subfamily.bed`, `record.bed`, `record.gtf`, `subfamily.saf`, `subfamily.noExon.saf`:** these cover direct subfamily RNA, record-based RNA/ATAC investigation, the GTF consumers and both independent and gene-aware bulk counting with one explicit feature contract per file.
3. **Ensembl-named copies of the GTF and both SAFs, plus `contig_aliases.tsv` and a contig-coverage/length report:** these make the bulk handoff usable on an independently assembled reference while preserving canonical record IDs across renamed coordinate columns.
4. **Export contracts, alias maps and retained-block registration wherever an export transforms identity or geometry:** these let every emitted feature resolve to its canonical support, with fully masked records and partial-universe instances represented explicitly and one count retained at its original grain.
5. **Pinned mm39 and hg38 configurations, retained/retrievable inputs and independently reviewed source/policy expectations:** these establish actual two-assembly operation and let a future maintainer reproduce the promised coverage and taxonomy decisions.
6. **`MANIFEST.json`, `BUILD_ID`, an exact-inventory verifier and immutable `archive/<BUILD_ID>/` publication:** these bind the delivered data and policy, protect published bytes through rebuilds and transfers, and make a consumer's pin directly resolvable.
7. **A CI-free `tests/run.sh` with committed tiny fixtures and separate `core`, `consumers` and full-source acceptance modes:** this makes the claims executable from a checkout using declared local prerequisites and produces an explicit failure or unsupported status for missing required tools.
8. **Accurate `README.md`, `docs/{OUTPUTS,DECISIONS,PROVENANCE,RELEASES}.md`, consumer examples and a host-build runbook:** these give an external group a shortest path from its assembly/BAM namespace to verified files and distinguish delivered, tested and deferred capabilities.
9. **Repository `AGENTS.md` and a recorded parking handoff:** these preserve scope, invariants, verification commands, known incompatibilities, the accepted release IDs and the next extension gates across maintainer sessions.

This is five default track files and three Ensembl bulk counterparts per accepted assembly, plus shared tables and receipts. The same exporter can emit another declared universe or Ensembl BED when selected for a build; its output then enters that build's inventory. Universe definitions and membership validation belong in every release, while unused format/universe combinations remain unmaterialized.

The export registration can stay small: ordinary full-record and repName memberships are derivable from the catalog and contract, with explicit maps only for changed aliases, composite tool IDs and retained blocks. Count/run/cell metadata belongs to downstream `te_feature_registration`. A mixed-name instance exposes its member names and selected/full membership; a subfamily rollup of its count requires an explicit allocation model.

**Cut from required scope:** the MATES CSV/BED pair, conditional `instance.bed`, distributed `locInd`, locus SAF, duplicate subfamily/instance GTFs, Parquet copies, context-specific SAFs and the full format grid. MATES is explicitly optional in the owner's plan (`A/consult/fanout/owner_context_2026-09-15.md:26`); its direct reader requires a dedicated eight-column pair (`M/MATES/scripts/count_coverage_10X.py:231`), and its stock preparation changes interval lengths and removes whole gene-overlapping records (`M/build_reference.py:133`, `:142`). That is a separate adapter and model-validation obligation. Add `instance.bed` when an IRescue instance run is selected; custom BED returns before auto-instance reconstruction (`I/map.py:61`), so the flag alone cannot turn `record.bed` into instance features. Keep historical triple SAFs and packaged-label reconciliation as explicit compatibility work, with their existing evidence preserved in provenance.

The host runbook must state writable host destination versus the read-only container mount, prerequisites and versions, source-cache and temporary-space requirements, offline verification, staging/build/verify/publish commands, the resulting immutable path, and transfer/restore verification. It should cover interruption recovery and resolving `current` once per consumer operation. `AGENTS.md` should state that the package owns reference projections and fixtures, and that every newly claimed assembly/consumer runs the appropriate acceptance checks. Record actual commands and results at parking time; this consultation supplies no passing certificate.

### Mandatory fixtures before “tested”

`tests/run.sh` should use disposable directories and declared tool paths, never install or fetch tools, and leave source checkouts and published snapshots untouched. Core success and consumer success are separate summaries; a required consumer skip fails the release acceptance command. Keep expected outputs independently authored and pin parser/executable versions in the test report.

| Fixture | Known answer / required assertion |
|---|---|
| Source parser and coordinates | Plus/minus `.out` records, parenthesized consensus fields, an optional `*`, missing family component, one-base intervals and contig-end intervals retain raw provenance and round-trip exactly between 1-based tables/GTF/SAF and half-open BED; malformed or out-of-bounds input fails explicitly. |
| Identity and universes | Equal coordinates with different repNames remain two records; an exact duplicate key is rejected; a two-family repName contributes once through canonical taxonomy; uncertainty, structural RNA, tRNA-derived SINEs, satellites and an unfamiliar class exercise explicit membership and review gates. |
| Instance blocks and projection | Two separated member intervals contribute only their interval union; a nested record and gap-only query cannot add coverage to that instance; a universe retaining one member records partial membership, and reused IDs across source scopes cannot merge silently. |
| Aliases and assembly coverage | Include `chr1`/`1`, a scaffold/accession, an alternate contig, a zero-repeat contig, missing gene coverage, a missing alias and a many-to-one alias; accepted mappings preserve IDs, sequence lengths and interval sets, while an incompatible requested namespace fails preflight. |
| Consumer name round-trip | Test actual mm39 punctuation and synthetic comma/hash/colon/percent/quote/space hazards; deterministic safe aliases recover exact raw names through registration, preserve distinct identities, and retain the exact consumer output ID. |
| Exon subtraction | A central exon splits one record into two pieces; overlapping exons across isoforms subtract their union once; complete removal is recorded; antisense overlap follows the declared unstranded policy; residual exon overlap is zero and retained-plus-removed bases equal the original interval length. |
| IRescue, two RNA layouts | Two unique molecules in disjoint records of A yield A=2 in the subfamily run and one per record in the record run; gap-only support gives zero; repeated alignments/UMIs preserve molecular totals; 3′ nuclear and 5′ paired fixtures separately establish strand, mate and barcode behaviour. |
| GTF consumers | TEsingle preserves the exact four-part output identity with explicit cutoff, and 999/1,000 distinct raw URs exercise its default threshold; TEtranscripts must recover the declared subfamily grain despite two source taxonomy assertions; TElocal must survive its actual versioned ingestion/index round-trip and register its exact output identities. |
| Stellarscope boundary gate | GTF `101..110` queried with BAM blocks `[99,100)`, `[100,101)`, `[109,110)`, `[110,111)` must give overlaps `0,1,1,0`; same-instance blocks `101..110` and `112..120` must leave base 111 uncovered; attribute switching must change feature grouping as declared. |
| featureCounts | Full SAF rows with shared repName yield one feature with two uniquely assignable molecules; one-base, strand, single-end and paired-end examples pass under explicit options; split noExon blocks retain one feature; a cross-exon/TE paired molecule demonstrates why separate counters provide no exclusive-assignment guarantee. |
| ATAC geometry | A fragment spanning a TE with both cuts outside yields one interval overlap and zero in-TE cuts; a motif inside the surrounding peak but outside the TE fails the sequence intersection; repeat the cut test using the supplied fragment shift convention exactly once. |
| Registration and absence | Count 7 supported by three records remains 7 after membership selection; two taxonomy assertions preserve that total; fully masked, filtered, unsupported and unobserved features retain distinct statuses; independent quantification runs remain distinct facts. |
| Publication | Same-input rebuilds converge; same-day changed inputs produce another immutable directory; added/missing/corrupt payloads, forged BUILD_ID and stale policy are rejected; interrupted publication preserves a complete selection; concurrent identical/different publishers leave complete archives; verification works with read-only snapshots. |
| Full mm39 and hg38 acceptance | Independently reviewed per-source/per-universe counts, taxonomy multiplicities, joins, sequence bounds, aliases, retained-base totals and export registrations pass; a repeated build reproduces the defined data fingerprint; transferred bytes verify independently. |

The Stellarscope test is an immediate compatibility gate: the checked parser stores `[f.start,f.end+1)` and queries `[b_start,b_end+1)` (`S/annotation/_intervaltree.py:55`, `:78`), while alignment blocks come from `get_blocks()` (`S/utils/calignment.pyx:95`). Its merger also joins intervals separated by distance one (`S/annotation/utils.py:17`, `:42`). This predicts the endpoint/gap failures above; execution is still required. A failing result leaves that consumer/version labelled unsupported until corrected. Preserve standards-compliant GTF coordinates and use the tested IRescue record route for the initial locus workflow. MATES-specific parser and prediction fixtures become mandatory when its adapter is promoted.

### Two maintainer objections to settle in the design

**The hash promise needs an exact boundary.** ADR-7 currently combines “over delivered bytes” with an excluded builder SHA inside the delivered manifest. Define BUILD_ID as SHA-256 of the canonical, sorted-key, compact UTF-8 JSON serialization of MANIFEST with only its top-level `builder_sha` removed and one terminal newline. The manifest's `outputs` map contains observed MD5s for every delivered data path; its source digests, schema, assembly, universes, gene-dependent view recipes and observed counts remain included. `BUILD_ID`, the manifest itself and retained `source/` files are outside `outputs`; source bytes are verified against their manifest digests. Omit build IDs from hashed data to avoid self-reference, and include no timestamps in this manifest.

On an identical-data rebuild, verify the existing directory and preserve its original producer manifest. A changed GTF dependency changes the build even if the resulting subtraction happens to be identical. A build with no gene-dependent view has no GTF dependency. This supplies one precise content identity while acknowledging that builder provenance lies outside its equality claim. The present verifier only checks listed files and writes temporary output inside the snapshot (`T/src/99_verify.sh:22`, `:52`); both behaviours need replacing before the immutable claim passes.

**The supported source envelope needs a boundary.** Mouse source parity does not establish parity for hg38 or another species. Compare each configured `.out` with its matching UCSC table and retain a reconciliation report; mismatched releases require an explicit source decision before publication. A species supplied through a local RepeatMasker run needs its own source adapter, run metadata and fixtures. A configuration file should represent verified inputs and vocabulary, rather than imply universal compatibility.

## Part 2 — Eight proposed entries for `docs/DECISIONS.md`

The status/reason lines are consultation annotations; the paragraphs beneath them are the proposed public text. The recorded young/old deferral is included in ADR-4, keeping eight entries.

### ADR-1 — Feature identity and taxonomy

**AMENDED — Scope names to a build and keep consumer grouping consistent when source taxonomy disagrees.**

Subfamily identity is `repName` within a pinned RepeatMasker build, and each quantification records its chosen record, instance or subfamily resolution. Every record retains its source taxonomy, while `taxonomy_canonical` supplies one row per name with resolved, uncertain-source or unresolved status and preserves each supported rank. Subfamily exports use one canonical classification tuple per name, and family/class rollups use that table with explicit unresolved categories. Feature registration preserves the original measurement grain through joins.

### ADR-2 — Named universes

**AMENDED — Historical compatibility requires evidence for each assembly.**

The catalog defines `all_rmsk`, `interspersed`, `interspersed_plus_satellite`, `retrotransposons` and `satellites` through explicit, versioned predicates. The default `interspersed` view retains tRNA-derived SINEs and records uncertain classifications as candidates. Each assembly records its class census and the mapping into these shared views. `legacy_tetranscripts_mm39` preserves the measured historical interval selection, and each additional legacy universe carries its own reference pin and reconciliation.

### ADR-3 — Deliver and park a verified reference

**AMENDED — Add complete bulk inputs and acceptance evidence; promote optional adapters when consumed.**

The parked release contains the full catalog, instance membership, taxonomy, universe definitions and registered `interspersed` BED6, GTF, full-interval SAF and exon-subtracted SAF exports. Verified mm39 and hg38 builds include Ensembl-named bulk exports and explicit contig coverage. Every supported consumer/version passes known-answer fixtures through a local Bash runner, and the release includes reference verification, immutable publication, usage documentation, `AGENTS.md` and a host-build runbook. Additional adapters enter a release with a named consumer and passing fixtures.

### ADR-4 — Gene-dependent views and later interpretation

**AMENDED — Specify the present exon mask and record the interpretation deferrals explicitly.**

The noExon view subtracts the unstranded union of annotated exons from full record intervals and records the gene-annotation digest, retained blocks and removed records. Later transcript context forms a record-by-transcript relation with overlap bases and relative strand, keyed by the reference build and gene-annotation digest. Assembly configurations bind their sources, sequence sets, aliases and accepted vocabulary. Young/old evolutionary tiers and full-length/ORF annotation remain deferred to a structural stage, with per-record divergence and consensus coordinates retained as inputs.

### ADR-5 — Names and registration

**AMENDED — Encode transformed geometry and contig namespace in export paths.**

The namespace distinguishes record, instance, subfamily, family, class, universe and build; `rmsk_` identifies source assertions and `rm_instance` identifies RepeatMasker grouping. Canonical tables are `rmsk_records`, `rm_instance_members`, `taxonomy_rmsk`, `taxonomy_canonical` and `universes.json`, with provenance in `MANIFEST.json`. Exports use `<universe>/<level>[.<view>].<format>`, with `ensembl_named/` selecting renamed contigs and registered aliases preserving canonical identity. Downstream joins use build-scoped `rmsk_records`, `peak_record_overlaps` and `te_feature_registration` keys.

### ADR-6 — RepeatMasker source provenance

**KEEP — Clarify the checks and preserve declared run provenance.**

The pinned `bigZips/<genome>.fa.out.gz` supplies records and RepeatMasker instance IDs, and the matching pinned `rmsk.txt.gz` supplies an independent record and taxonomy cross-check. The manifest records observed source digests alongside declared RepeatMasker software, library and run metadata with their evidence sources. Each configured assembly validates source agreement, record identity and grouping scope before publication.

### ADR-7 — Build identity and publication

**AMENDED — Make the builder-SHA exclusion and conditional gene dependency precise.**

One BUILD_ID fingerprints all delivered data checksums and canonical manifest content, with builder SHA retained as separately scoped provenance. Source digests, schema, policies and every gene-dependent view's GTF digest participate in that fingerprint. A build completes and verifies in staging, enters immutable `archive/<BUILD_ID>/`, and becomes selected through an atomic `current` symlink replacement. Consumers resolve that pointer once, verify the snapshot and retain its full ID and file checksums.

### ADR-8 — Public decision wording

**KEEP — The wording rule remains useful once the scope and guarantees are concrete.**

Each decision states the chosen behaviour and its reason in two to four brief, affirmative sentences. Detailed contracts and test evidence live in the linked technical documentation, and deferred work names the evidence needed for its next decision.

## Final ruling

**AMEND ADR-3; KEEP ADR-8.**

te-tracks parks as a verified mm39 and hg38 reference with canonical records, instance membership, taxonomy, explicit universes and registered BED, GTF and full/exon-subtracted SAF exports in documented contig namespaces. Each supported consumer and assay layout has executable known-answer evidence, and each release includes immutable publication, local tests and maintainer/build documentation. Optional adapters and biological interpretation stages advance when their named consumers and validation evidence are ready.

## Open items before implementation

1. **Freeze the bulk parser targets:** inspect pinned TEtranscripts and TElocal releases, establish the exact GTF/index/output identity contracts, and confirm the canonical-taxonomy GTF projection against their grouping logic.
2. **Freeze the hg38 source package:** select and pin its matching RepeatMasker sources, FASTA sequence set, aliases and gene annotation, then review class vocabulary and source/grouping discrepancies; pin the already measured mm39 `.out` digest as part of the same source contract.
3. **Freeze fixture BAM conventions:** identify the actual mate orientation, CB/UMI tags and alignment-retention settings for 3′ ARC and 5′ OCM, plus the accepted single-/paired-end bulk examples, so expected molecular counts precede implementation.
