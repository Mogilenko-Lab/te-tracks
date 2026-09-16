# te-tracks: directions and decisions after the per-ADR consults (2026-09-16)

Six codex units ran on gpt-6-astra at reasoning effort xhigh, one per major decision, each reading
the same decision state (`DECISION_STATE.md`), the measured audit, the earlier consults and the four
consumer checkouts. Every code claim I rely on below was re-read by me in the source. Reports:
`ADR1_consult.md`, `ADR2_consult.md`, `ADR4_consult.md`, `ADR5_consult.md`, `ADR67_consult.md`,
`ADR38_consult.md`. No unit wrote outside its one file; no git write reached any repository.

## The thing that was missing

Every unit found the same gap from a different side. A **universe** and a **level** were carrying
three different meanings at once:

1. the **annotation selection**: which records exist in an export file;
2. the **assignment reference**: the feature set a quantifier competes over, which for EM tools
   includes grouping, gene features, strand mode and overlap rules;
3. the **reported selection**: which features are kept when results are shown.

For a plain overlap counter these coincide, so filtering after counting equals filtering before.
For every EM tool in scope they differ. Removing a satellite feature before IRescue runs changes how
an ambiguous molecule is allocated; removing its row afterwards leaves the allocation as it was.
Fitting IRescue at family level gives F=3, G=3 on a six-molecule example where fitting at subfamily
level and summing gives F=4, G=2. Stellarscope's default reassignment zeroes a molecule whose best
posterior is tied between two loci, so a locus matrix summed to subfamily loses evidence that a
subfamily fit would keep (verified: `stellarscope/utils/model.py:431-448`). MATES deletes every
model group ending in `?` or equal to `Unknown` before fitting (verified: `calculate_MU.py:278-295`).

Consequence for te-tracks: it owns (1) and publishes enough levels that (2) can be chosen honestly.
Consequence for every analysis run: it must record assignment level, reported level, measurement
unit, estimator and taxonomy revision as separate fields. A count matrix header that says
"interspersed / subfamily" is incomplete without them.

## ADR-1 counting unit and taxonomy: AMEND

Kept: repName is the default aggregate feature. Amended in four ways.

- **What repName identifies.** "All selected records bearing that source name in this pinned
  annotation." The library model accession and consensus sequence are absent from the source, so
  "repName = the consensus" is an evidence claim, kept as a cross-reference relation when Dfam
  accessions are added, never as the key.
- **A fourth published level: canonical family.** `interspersed/family.bed` repeats the canonical
  `(class, family)` id across each record's blocks. Direct family fitting differs from summed
  subfamily fitting, so the family view is an export, and a family total must state which of the
  two it is.
- **ERV units are deferred.** An IAPEz-int count is RNA associated with internal-model intervals. A
  named `erv_unit` export waits for a structural stage that validates LTR-internal membership by
  strand, order, consensus coverage and separation. The instance relation and consensus coordinates
  published now are its prerequisites.
- **Canonical taxonomy is an independently versioned curation input** with a named accountable
  curator, rank-specific statuses (class may resolve while family stays uncertain), and a digest the
  build manifest pins. Raw `?` and `Unknown` stay exact in `rmsk_records` and `taxonomy_rmsk`;
  normalization happens only in the canonical layer. MATES and TEsingle embed taxonomy in their
  assignment keys, so adapters emit raw labels and canonical reporting happens through registration.

Fixtures this adds: IRescue 4/2 vs 3/3 allocation and UMI-graph merging; Stellarscope tied-locus
loss; TEsingle composite identity and integer rounding; featureCounts regrouping changing overlap
eligibility.

## ADR-2 universes: AMEND

Kept: six named selections over the complete catalog, default interspersed, satellites separate,
legacy kept for comparability. Amended:

- **Rename to say what they are.** `repeatmasker_all`, `interspersed_candidates` (default),
  `interspersed_candidates_plus_satellites`, `retrotransposon_derived`, `satellite_repeats`,
  `compat_tetranscripts_mm39`. "Candidates" makes visible that Unknown, Unspecified and `DNA?` are
  inside the default as flagged provisional members. "Derived" makes visible that solo LTRs and
  defective copies are inside the retrotransposon set.
- **Predicates on raw classification only.** A curation change that alters membership produces a new
  selection or build; the label never changes meaning when a taxonomy table is edited.
- **Satellite is both a class and a selection.** The combined selection has a live purpose: fit
  jointly, then report interspersed and satellite contributions separately. Satellite-only fits and
  pooled totals fail in different ways. Normalization basis is a separate declared field; the
  denominator argument decides that separation, and satellite exclusion follows from labelling and
  assembly under-representation.
- **Species onboarding is a class census**, one reviewed disposition per observed label, with
  publication of a biological selection blocked until review. hg38 acceptance cases: Alu and SVA
  present, B1 absent. A mouse B1 record carries RepeatMasker family `Alu`, so a family-only join
  across species asserts an equivalence at the wrong rank.
- **Tool comparability lives in versioned compatibility profiles**, one per tool revision, source
  and transformation. A seventh "auto tool" selection denotes no reproducible set.
- One biological correction to the earlier synthesis: B1 and Alu are 7SL-derived; B2, B4 and ID are
  tRNA-derived. Membership follows the pinned class label either way.

## ADR-4 transcript context and species: AMEND

Kept: one `config/<genome>.env` per assembly, universes global with membership per genome.
Amended:

- **One canonical build carries the gene-dependent artifacts.** Context relation and the noExon view
  share the build's pinned gene annotation and policy; a GENCODE or policy revision produces a new
  BUILD_ID. The record table stays byte-identical across such builds and its digest proves reuse.
  The satellite-table alternative keyed on two md5s under-specifies promoter widths, alias policy
  and schema, and makes consumers manage two release scopes.
- **Exact geometry beneath the summary.** Transcript reference and geometry tables; a sparse
  record-transcript relation carrying body, exon, intron, promoter overlap bp, relative strand,
  signed distances to TSS and to TES, nearest exon boundary with ties; exact intersection blocks; a
  per-record context-status row so "not computed" is distinguishable from "intergenic". TES is the
  landmark the earlier design missed and the one a 3' assay needs.
- **noExon registers its pieces.** The mask is the union of all exons of all transcripts, both
  strands. Each surviving piece registers to its parent record with piece index and status
  (unchanged, trimmed, split, fully subtracted). Retained plus removed equals original length.
- **Correct te-tracks' own claim.** Exon subtraction guarantees exon-disjoint sequence support under
  the declared mask. It does not make each molecule count once: the lab driver counts genes and TEs
  in separate featureCounts runs and row-binds them (verified), and TEsingle indexes genes as
  full-length transcripts including introns (verified: `TEsingle:112`). Molecule exclusivity is a
  joint-assignment contract, tested in the analysis, and DECISIONS.md and README say so.
- **Species.** Organism is data in the assembly config. hg38 needs a pinned GENCODE release, a
  contig-scope decision and a reconciled TEsingle human package before a compat selection exists.
  dm6 needs a FlyBase or Ensembl Metazoa GTF, arm-name aliasing, and has no legacy package. An
  assembly without a UCSC `.out` cannot meet the instance contract from the truncated table.

## ADR-6 source and ADR-7 build identity: AMEND

Kept: the `.out` as primary source; content-addressed immutable archive by full id; one `current`
symlink; deletion of the index and pointer files. Amended:

- **Pin the `.out.gz` now.** md5 `ffc8399d05f3388d80b78c93482a5b95`, 169,199,039 bytes, verified
  against my own download record. Declared run identity from UCSC's README: RepeatMasker
  open-4.0.8, RepBase and Dfam_Consensus release 20181026, sensitive mode, status `declared`.
- **The source is "a pinned RepeatMasker result on an identified assembly", qualified by provider
  and format profile.** UCSC is one provider. IRescue and MATES already point at repeatmasker.org
  paths for other assemblies. An assembly without an ID-bearing `.out` cannot meet the instance
  contract and stays pending.
- **Parser contract.** Fifteen whitespace fields plus optional `*`; parentheses stripped only from
  numeric fields, names such as `(TGCT)n` kept verbatim; `C` mapped to `-` with raw strand kept;
  consensus columns swap on `C` (ID2: `(48) 104 5` gives start 5, end 104, remaining 48); the `*`
  flag stored separately; the class/family token split once at `/`. Where the `.out` has no slash,
  UCSC duplicates the class into the family column (Simple_repeat, Low_complexity, Satellite, tRNA
  and others, verified below). te-tracks keeps the missing-family fact and provides the
  UCSC-compatible projection beside it.
- **`rmsk.txt.gz` moves from production dependency to source qualification.** Run the field-level
  comparison when a new source pair or a parser change is qualified, record the result, and keep
  ordinary builds on one pin.
- **BUILD_ID hashes the scientific contract, and only that.** The manifest has two sections.
  `identity` holds family, schema version, species and assembly, source digests, declared run
  identity, parent build ids, universe predicates, export contracts and the complete file inventory
  with SHA-256 digests; `BUILD_ID = sha256("te-tracks-build-v1\n" + canonical_json(identity))`.
  `provenance` holds builder commit, tool versions, invocation and validation evidence, outside the
  hash. A docs-only commit keeps the id. A change in coordinate semantics or a universe predicate
  changes the id even when table bytes agree. Independently reproduced builds can share an id with
  different provenance; deduplication keeps the first directory and never rewrites it.
- **Two build families with a parent edge.** `te_<assembly>` holds records, instance membership,
  taxonomy, universes and gene-independent exports. `te_<assembly>_gene` holds the noExon view and
  the later transcript-context relation, and its manifest pins `parent_core_build_id`. A GENCODE
  bump creates a new child and leaves the core id, and every ATAC and peak-ledger key, untouched.
  This is where ADR-4's unit and this unit disagree: ADR-4 preferred one build for consumer
  simplicity. I side with two families. The peak ledger is ATAC-only and must not churn when a gene
  annotation moves, the child reuses the same manifest and publication code, and the added cost is
  one directory and one parent field. The core build then drops its GTF fetch.
- **Publication contract extended** beyond the six tests: HPC transfer copies into destination
  staging, verifies inventory, id and parents there, then installs; installs require no-replace
  semantics and are tested against an empty or conflicting destination; final modes and ACLs are
  normalized before selection given the shared `umask 002`; the verifier keeps scratch outside the
  release; readers resolve `current` once and read from the immutable directory; crash durability is
  a separate promise from atomic visibility and needs fsync where claimed.
- **Retention.** Keep every published build. Ten builds cost about 1.5 GB per root. Deduplication
  machinery waits until sources dominate storage.

## ADR-5 namespace: AMEND

Kept: `record`, `instance`, `subfamily`, `family`, `class`, `universe`, `build` as the entity nouns;
`rmsk_records`, `peak_record_overlaps`, `te_feature_registration` on the ledger side. Amended:

- **One qualifier, `rmsk_`, throughout; `rm_` is retired.** `rmsk_` means "derived from RepeatMasker
  under declared normalization"; the unmodified source labels and tokens are the "as asserted" part.
  UCSC-specific raw encodings carry `ucsc_`. Column names say their convention: `start_1`, `end_1`
  are 1-based inclusive; the ledger's own intersections use `[start_1 - 1, end_1)`.
- **Collisions resolved.** The ledger already uses `family_id` and `class_id` for TF families, so the
  source labels are `rmsk_family` and `rmsk_class` and the curated ones `canonical_family` and
  `canonical_class`. The ledger uses `resolution` for biological sampling units, so the TE
  measurement grain is `feature_level`. The release directory is the "reference root", never the
  "family". `atac_fragment` and `peak` stay reserved.
- **The canonical record table has 24 declared columns**: the self-describing id, chrom, start_1,
  end_1, strand, rmsk_name, rmsk_family, rmsk_class, rmsk_instance_id, sw_score, divergence_pct,
  deletion_pct, insertion_pct, length_bp, consensus_start_1, consensus_end_1, consensus_left_bp,
  query_left_bp, rmsk_overlap_flag, rmsk_class_family (the raw token, so a missing family survives),
  the three raw signed UCSC repeat fields, and source_row_number. Physical files omit the build id;
  ingestion adds `te_build_id`.
- **Path grammar gains two axes**:
  `exports/<contig_namespace>/<universe_name>/<interval_variant>/<level>[_<profile>].<format>`.
  `interval_variant` is `full` or `exon_subtracted` (the readable spelling replaces `noExon`).
  `_mates` is a profile suffix because MATES needs a same-stem CSV and BED pair, and its reader
  derives the companion by splitting the path at the first dot, so dots are banned from stems and
  parent directories (verified in `bam_processor.py`). A triple-keyed SAF is `taxonomy_triple.saf`,
  never `subfamily.saf`.
- **GTF attributes are interface names, mapped once.** `gene_id` = rmsk_name, `transcript_id` and
  `locus` = a colon-free record alias, `family_id` and `class_id` = source labels, `instance_id` =
  instance alias. The mapping lives in the manifest's profile schema and in a published
  `export_feature_members` table with exact emitted feature keys and retained blocks.
- **Key scope.** A record key is `(te_build_id, rmsk_record_id)`. Equal strings across builds are a
  candidate correspondence. A future duplicate coordinate tuple stops publication for an identity
  decision instead of receiving a silent ordinal.
- **The reading test passes**: a newcomer can tell source, tables, curated taxonomy, untouched
  exports, exon-subtracted counting support and the MATES bundle apart from one directory listing,
  with exact semantics deferred to the manifest.

## ADR-3 scope: AMEND. ADR-8 wording: KEEP

The parked state is an **acceptance contract**, stated per assembly, contig namespace, feature
level, interval variant and consumer version, with executable evidence. Counting files leaves those
obligations implicit. Amendments to the deliverable list:

- **Add** the full-interval `subfamily.saf`: an external bulk group needs a gene-independent TE
  reference before it chooses an exon mask. The lab's own builder already emits both.
- **Add** Ensembl-named copies of the GTF and both SAFs, a `contig_aliases.tsv`, and a contig
  coverage and length report. Scaffolds need real aliases (`chr1_GL456210v1_random` to
  `GL456210.1`); prefix stripping cannot supply them, and IRescue and MATES continue on partial
  contig mismatch with only a warning.
- **Add** a preflight command that checks a chosen export against a BAM header or FASTA index.
- **Add** `family.bed` (from ADR-1) as the fourth level, because the family-versus-subfamily EM
  comparison is a planned analysis and the file is cheap.
- **Cut from required scope**: the MATES pair (owner marked MATES optional; its stock reference
  changes intervals), `instance.bed` until an IRescue instance run is selected, any `locInd`, a
  locus SAF, duplicate GTFs, the format grid. Keep Parquet for the canonical tables because the
  DuckDB ledger is a named consumer.
- **TEtranscripts and TElocal compatibility cannot be advertised.** Neither is present in the
  checkouts or the environment. The GTF ships; their acceptance is an open item.
- **Fixtures mandatory before "tested"** are enumerated in `ADR38_consult.md` §"Mandatory
  fixtures", one row per contract: parser and coordinates, identity and universes, instance blocks,
  aliases and coverage, name round-trip, exon subtraction, IRescue in both RNA layouts, GTF
  consumers, the Stellarscope boundary gate (`0,1,1,0`), featureCounts, ATAC geometry,
  registration conservation (7 stays 7), publication, and full-assembly acceptance.
- **"Parked" also means**: accurate README and docs, an `AGENTS.md`, a CI-free `tests/run.sh` with
  core, consumers and full-source modes, a host-build runbook covering the read-only container
  mount, and a recorded parking handoff.
- **hg38.** The unit wants a verified hg38 build before the reusable milestone. I recommend
  parking as "mm39 verified" now, since D2 and D3 wait on it, with hg38 as the named next gate and
  the schema, class-census gate and config already shaped for it.

ADR-8 stands. The unit drafted eight affirmative entries; they need the naming decisions below
applied before adoption.

## Where the units disagreed, and how I resolve it

| question | positions | resolution |
|---|---|---|
| one build or two families | ADR-4: one; ADR-67: core + gene child; ADR-38: GTF dependency only when a gene view ships | Two families. The peak ledger keys on the core id and never churns on a GENCODE bump; the child pins its parent. |
| qualifier | ADR-5: `rmsk_` only; ADR-38 keeps `rm_instance` | `rmsk_` throughout. One authority, one prefix. |
| export path | ADR-5: `exports/<ns>/<universe>/<variant>/<level>[_<profile>].<fmt>`; ADR-38: `<universe>/<level>[.<view>].<fmt>` + `ensembl_named/` | ADR-5's grammar. Variant is a directory so it applies coherently to every format; MATES's dot-splitting reader bans dots in stems. |
| universe names | ADR-2: `interspersed_candidates`, `retrotransposon_derived`, `satellite_repeats`, `compat_tetranscripts_mm39`, `repeatmasker_all` | Adopt `retrotransposon_derived` and `compat_tetranscripts_mm39`; keep `all_rmsk`, `interspersed`, `interspersed_plus_satellites`, `satellites` short, with the explicit predicate in `universes.json`. Owner may prefer the `_candidates` suffix. |
| GTF `family_id`/`class_id` | ADR-1 and ADR-5: raw labels; ADR-38: canonical labels with raw in extra attributes | Canonical in the four consumer attributes, raw in `rmsk_family`/`rmsk_class` attributes. A subfamily-grouping consumer then sees one feature per name, which is ADR-1's decision; the taxonomy digest is inside the build identity anyway. |
| `rmsk.txt.gz` cross-check | ADR-67: qualification-time; ADR-38: production-time | Qualification-time, with the reconciliation report retained in the build. One production pin. |
| BUILD_ID recipe | ADR-67: two-section manifest, hash `identity`; ADR-38: hash manifest minus builder sha | ADR-67's. The boundary is a named section, and provenance can grow without touching identity. |

## The decision list as it now stands

1. **Counting unit.** Subfamily = repName within a pinned build. Four published levels: record,
   instance, subfamily, canonical family. Raw taxonomy exact on every record; `taxonomy_canonical`
   is an independently versioned curation input with rank-specific statuses and a named curator.
   Every analysis records assignment level, reported level, unit, estimator and taxonomy revision.
2. **Universes.** Predicates on raw classification over the complete catalog: `all_rmsk`,
   `interspersed` (default), `interspersed_plus_satellites`, `retrotransposon_derived`,
   `satellites`, `compat_tetranscripts_mm39`. A universe is an annotation selection; assignment
   reference and reported selection are run metadata. New assemblies pass a class census.
3. **Scope.** Park as "mm39 verified": canonical tables in TSV and Parquet, instance membership,
   raw and canonical taxonomy, `universes.json`, five UCSC-named `interspersed` exports plus
   `family.bed`, Ensembl-named GTF and SAFs with alias table and coverage report, preflight,
   fixtures, runner, docs, AGENTS.md, runbook. hg38 is the next gate.
4. **Gene-dependent views.** A child build family `te_<assembly>_gene` pinning its parent: the
   exon-subtracted view with registered pieces now, the record-by-transcript relation with TSS and
   TES landmarks and exact blocks next. te-tracks corrects its "counts each read once" claim.
5. **Namespace.** `rmsk_` throughout; 24-column `rmsk_records`; `feature_level` on the ledger;
   `exports/<contig_namespace>/<universe>/<variant>/<level>[_<profile>].<format>`;
   `exon_subtracted` replaces `noExon`; `taxonomy_triple.saf` names the legacy grouping.
6. **Source.** `<genome>.fa.out.gz` pinned (mm39: `ffc8399d05f3388d80b78c93482a5b95`), format
   profile declared, class-only tokens preserved, declared run identity recorded with its source.
   UCSC table comparison at qualification time.
7. **Identity and publication.** Manifest `identity` section hashed to BUILD_ID, `provenance`
   outside; staging, verify, no-replace install into `archive/<id>`, atomic symlink swap; transfer,
   permission, reader and durability rules added; keep every build.
8. **Wording.** Two to four affirmative sentences per decision; the unit's drafts are the starting
   text once names are settled.

## Open items before implementation

1. Name the taxonomy curator; freeze canonical revision 1 with every conflict left unresolved.
2. Freeze the `.out` parser profile and the mm39 source-qualification report.
3. Freeze the exon mask and the first child build's contract.
4. Freeze fixture BAM conventions for 3' ARC and 5' OCM, and the bulk single- and paired-end
   examples, so expected molecule counts exist before adapters are written.
5. Settle the two owner-facing name choices: `_candidates` suffix or not; `_derived` on
   retrotransposons.
6. Decide whether hg38 verification precedes or follows the parking milestone.
