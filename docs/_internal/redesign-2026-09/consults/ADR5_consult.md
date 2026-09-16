# ADR-5 consult — namespace

**Ruling: AMEND.** The missing distinction is between a catalog object, the bases retained in an export, and the feature a quantifier actually measures. The proposed nouns identify the first; `<universe>/<level>.<format>` cannot identify all three. A release also needs explicit key scope: identical names in two builds establish a candidate correspondence, while a measured feature belongs to a particular export and analysis run.

This is an offline, read-only design review. The supplied measurements are accepted. Consumer claims below were checked against local source; no consumer execution, installation, build, network access, or git operation was performed. This consult is the sole file written.

Citation prefixes, relative to `/workspaces/Meta-Aging`: **T** = `01_modules/te-tracks`; **I** = `01_modules/.ref/irescue`; **S** = `01_modules/.ref/stellarscope`; **E** = `01_modules/.ref/TEsingle`; **M** = `01_modules/.ref/MATES`; **A** = `_scratch/te-tracks-audit`; **L** = `14761-DM/docs/_internal/_project/plans/2026-09-11_codebase-topology/01_consult_codex.md`; **K** = `14761-DM/01_modules/scio/skills`. `L:165` therefore names a particular local file and line. DECISION_STATE was read first, followed by its audit, synthesis, owner context, earlier consults, and the relevant repository files.

## 1. Vocabulary with enforceable scope

| Proposed term | Concrete meaning and naming decision | Collision or silent assumption resolved |
|---|---|---|
| **record** | One source RepeatMasker annotation row. Table `rmsk_records`; key `rmsk_record_id`. Use `record` as the short export level. | A CSV row, SAM alignment record and GTF row also qualify as records. The `rmsk_` qualifier belongs in shared table/key names. Exon subtraction can turn one source record into several exported blocks. |
| **instance** | The grouping asserted by the primary `.out` ID. Table `rmsk_instance_members`; key `rmsk_instance_id`. Use `instance` as the short export level. | An instance can contain several records and several `rmsk_name` values. Its sequence support is the union of member blocks. A single family, subfamily, promoter, span or count per member requires additional reasoning. |
| **subfamily** | The operational counting level keyed by the source `repName`, stored as `rmsk_name`. | Across `all_rmsk`, a name may describe a simple-repeat pattern or structural RNA. The column name should faithfully describe the source field. Across species/library releases, equal names alone establish neither the same consensus sequence nor orthology. |
| **family** | Source label `rmsk_family`; curated rollup label `canonical_family`. | The ledger already has TF `family_id` and `family_name`, and te-tracks prose uses “family” for a release directory. Call that directory the reference root. Family identity for rollups includes its class and build. |
| **class** | Source label `rmsk_class`; curated rollup label `canonical_class`. | TF classification already occupies `class_id`/`class_name`. Bare `class` also carries language-level meaning for R and Python readers. Preserve literal `Unknown`, `Unspecified` and uncertainty punctuation as source labels. |
| **universe** | A named predicate selecting complete source records in one build, with a machine-readable definition in `universes.json`. Shared field `universe_name`. | A quantifier's competing-feature set, a cell roster and a statistical testing universe are separate objects. Exon subtraction changes support within selected records; it belongs to an interval variant. |
| **build** | One immutable te-tracks publication, identified by `BUILD_ID`; shared field `te_build_id`. | A genome assembly, RepeatMasker run, software build and analysis run have different identities. Use `assembly_name`, `genome_code`, pinned source digests and `analysis_run_id` for those roles. |
| **`rmsk_` / `rm_`** | Use **`rmsk_` throughout** for the RepeatMasker-derived namespace; retire `rm_`. Qualify UCSC-specific raw encodings with `ucsc_`. | Two abbreviations invite a fictitious distinction between two authorities. “Derived from RepeatMasker” permits declared coordinate/strand normalization; “as asserted” is reserved for the unmodified source labels, tokens and grouping. An ID constructed by te-tracks is explicitly identified as constructed. |

Use `rmsk_taxonomy` for the distinct source triples and retain `taxonomy_canonical` for the one-row-per-name rollup map. Its columns include `rmsk_name`, `canonical_family`, `canonical_class`, and `taxonomy_status`; a null canonical parent and the literal source label `Unknown` remain distinguishable. A family rollup uses `(te_build_id, canonical_class, canonical_family)`, rather than presuming a family name is globally unique. A subfamily rollup uses `(te_build_id, rmsk_name)`.

The collision with the ledger is concrete: its TF tables use `family_id` and `class_id` (L:161–162), its initial TE proposal uses `te_locus_dim.locus_id` (L:165–166), and its context table uses `resolution` for biological sampling resolution (L:168). Rename the proposed TE reference relation to `rmsk_records`, the TE overlap relation to `peak_record_overlaps`, and the TE measurement field to **`feature_level`**. Retain `resolution` for `condition_pool` and similar biological units. In prose, `locus` remains a genomic location requiring a stated object type; it supplies no additional catalog entity.

Reserve `atac_fragment` for the experimental paired-end fragment and `peak` for the called interval scoped by `atlas_id`. IRescue's CLI word `fragment` maps to our `record` only in its automatic annotation mode: it assigns a per-label ordinal, whereas `instance` follows `.out` IDs (I/irescue/map.py:137–158,174–187). A custom BED returns before that construction (I/irescue/map.py:61–84). Recording `--locus-level instance` beside a record-named custom BED would therefore falsely advertise the counting unit. The BED's feature names define that unit.

**Key rule.** A record's ledger key is `(te_build_id, rmsk_record_id)`; an instance's is `(te_build_id, rmsk_instance_id)`. Preserve the current self-description using explicitly **1-based inclusive** coordinates:

```text
rmsk_record_id = <rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>
```

Keep the component columns authoritative for computations. Source labels and coordinate tuples must pass uniqueness and delimiter checks in each new assembly. The measured mouse uniqueness supports this spelling for mm39; it supplies no guarantee about another RepeatMasker run. A future duplicate tuple must stop publication for an explicit identity decision, rather than acquire an unnoticed ordinal suffix. Retain the `.out` instance token as text and validate its grouping scope; concatenating independently numbered per-contig outputs requires explicit source partitioning before instance keys can be published. This avoids inventing a second release identifier while exposing the assumption behind the current source-wide instance ID.

## 2. Exact canonical record schema

Publish `tables/rmsk_records.tsv.gz` and `tables/rmsk_records.parquet` with the following **24 columns, in this order**. Types below are logical types: `text` = DuckDB `VARCHAR` / Arrow UTF-8 / R character; `int64` = signed `BIGINT` / Arrow int64 / R integer64; `float64` = `DOUBLE` / Arrow float64 / R double; `bool` = boolean / R logical. Every column is required in this schema. Source empty text remains empty text; unavailable required numeric fields cause a source-contract failure.

| # | Column | Type | Exact contract |
|---|---|---|---|
| 1 | `rmsk_record_id` | text | Constructed self-description above; unique within this build. |
| 2 | `chrom` | text | Canonical source contig name, matched to the pinned sequence dictionary. |
| 3 | `start_1` | int64 | Genomic start, 1-based inclusive. |
| 4 | `end_1` | int64 | Genomic end, 1-based inclusive. |
| 5 | `strand` | text | `+` or `-`; source `.out` `C` maps to `-`. |
| 6 | `rmsk_name` | text | Exact `repName`, including case and punctuation. |
| 7 | `rmsk_family` | text | Exact matched UCSC `repFamily`, preserving the source taxonomy used by the audited universes. |
| 8 | `rmsk_class` | text | Exact matched UCSC `repClass`. |
| 9 | `rmsk_instance_id` | text | Complete primary `.out` grouping token; shared across member records. |
| 10 | `sw_score` | int64 | Source Smith–Waterman score. BED score clipping, if used, belongs to its exporter. |
| 11 | `divergence_pct` | float64 | Source percent divergence; `6.7` means 6.7 percent. |
| 12 | `deletion_pct` | float64 | Source percent deletion. |
| 13 | `insertion_pct` | float64 | Source percent insertion. |
| 14 | `length_bp` | int64 | `end_1 - start_1 + 1`; genomic record length. |
| 15 | `consensus_start_1` | int64 | Source repeat-model start in forward-model, 1-based coordinates, with reverse-strand field order normalized. Preserve source overhang values. |
| 16 | `consensus_end_1` | int64 | Corresponding forward-model end, inclusive. |
| 17 | `consensus_left_bp` | int64 | Source parenthesized remaining repeat-model length, parsed as a nonnegative number. |
| 18 | `query_left_bp` | int64 | Source parenthesized remaining query length, parsed as a nonnegative number. |
| 19 | `rmsk_overlap_flag` | bool | Presence of the `.out` trailing `*` marker. Its meaning is the source marker, independent of a downstream genomic-overlap query. |
| 20 | `rmsk_class_family` | text | Exact `.out` class/family token, preserving whether a family component was supplied. |
| 21 | `ucsc_rep_start` | int64 | Raw signed UCSC `repStart`; preserve its strand-dependent encoding. |
| 22 | `ucsc_rep_end` | int64 | Raw signed UCSC `repEnd`. |
| 23 | `ucsc_rep_left` | int64 | Raw signed UCSC `repLeft`. |
| 24 | `source_row_number` | int64 | One-based ordinal among annotation data rows in the primary `.out`, before filtering or sorting. Resolves back to the retained source bytes. |

This keeps the existing canonical coordinate convention while making it visible in column names. The current builder generates its ID from `genoStart + 1` and inclusive end (T/src/10_build_master.sh:25,32–33,41–49). Quietly changing the coordinates while renaming `locus_id` would change every key. BED and ledger intersections explicitly use `[start_1 - 1, end_1)`; the ledger's existing 0-based convention is stated at L:145. No downstream reader needs to guess what `start` means.

The raw UCSC fields are deliberately signed: the local source schema defines `repStart`, `repEnd`, and `repLeft` as signed integers (A/source/rmsk.sql:37–39). Preserve the source `.out` plus its row ordinal as well. This retains evidence for later structural work without declaring `length_bp` to be consensus coverage, full-element length or age. Consensus coordinates alone provide model-relative positions; an accession/sequence-backed model identity is still needed for cross-library structural comparisons.

There is a subtle provenance issue in `rmsk_family`: the primary `.out` can carry a class-only token while the UCSC table supplies a family label. For example, the inspected third annotation row carries `.out` token `Simple_repeat` and UCSC `repFamily=Simple_repeat` (A/source/mm39.fa.out.gz:6 after decompression; A/source/rmsk.txt.gz:3 after decompression). Carrying `rmsk_class_family` prevents this representational difference from disappearing. The source cross-check must declare its class-only mapping rule; splitting on `/` and silently generating a null family would change the previously audited taxonomy. Source row equality also needs strand and relevant field agreement, beyond a successful coordinate/name join.

The serialization contract belongs in `MANIFEST.json` under a versioned schema: exact column order/types/nullability; UTF-8 tab-separated text; one header; LF endings; decimal integers; period decimal separator; `true`/`false` booleans; explicit `\N` null token for nullable companion-table fields. Literal `Unknown` and empty text remain distinct from null. Require explicit reader schemas instead of inference, especially for numeric-looking IDs and R integer64 columns. Reject embedded tab/newline source values before TSV publication and retain the original source bytes. Canonical text equality is case-sensitive. Both serializations must load to equal typed rows.

`rmsk_instance_members` is the deterministic projection `(rmsk_instance_id, rmsk_record_id)` with a unique record key. It adds no independent grouping authority. `rmsk_taxonomy` is the distinct `(rmsk_name, rmsk_family, rmsk_class)` relation, optionally with explicitly named `record_count` and `record_length_sum_bp` summaries; the latter sums lengths with overlaps retained. A unique-name assertion belongs only to `taxonomy_canonical`.

**Hash scope matters here:** the physical files inside a build omit `te_build_id`. Putting the final content hash inside a table included in that hash creates self-reference. Ledger ingestion adds it from the verified release, yielding `te_build_id` followed by the 24 source-table columns. Assembly name, taxon identity, sequence dictionary, source digests and library declarations live in the manifest and are available through its build dimension. A copied standalone table requires its manifest or a separately scoped ingestion wrapper.

## 3. Paths need a variant and a consumer profile

Adopt this grammar, with directories created only for delivered exports:

```text
exports/<contig_namespace>/<universe_name>/<interval_variant>/<level>[_<profile>].<format>
```

`contig_namespace` starts with `ucsc`; `interval_variant` starts with `full` and `exon_subtracted`; `level` names the default counted feature (`record`, `instance`, `subfamily`, or the explicitly different `taxonomy_triple`). A profile suffix appears where the file schema requires it, initially `_mates`. The path is relative to one immutable build. Compression is a separate declared encoding and is used only where the consumer accepts it.

**Why a variant directory:** a transformation applies coherently to BED, SAF, mappings and multi-file bundles. `full/record.bed` and `exon_subtracted/record.bed` retain the same source identities with different support. Define `exon_subtracted` as subtraction of the union of the declared gene annotation's exon intervals, with the strandedness rule explicitly pinned; the first profile should state its existing unstranded subtraction. A surviving piece is an `export_block`, keyed within its export and source record. Preserve fully removed membership/status for comparisons. The readable spelling `exon_subtracted` replaces `noExon`; it says what happened to the bases. A future whole-record exclusion view needs its own variant.

**Why a profile suffix:** standard `record.bed` is BED6 with the record feature ID in column 4. MATES needs eight columns with the subfamily label in column 4 and integer reference index in column 5, which serves a different role from a BED score. Its coverage reader obtains the companion by replacing the CSV extension (M/MATES/scripts/count_coverage_10X.py:231–234). Publish `record_mates.csv` plus **the same-stem** `record_mates.bed`, registered as one bundle whose manifest entry lists both paths, schemas and digests. CSV and BED rows agree exactly apart from the delimiter. The numeric index is an export-local feature alias.

There is an additional source-level failure in the appealing spelling `record.mates.csv`: MATES's `split_count_10X_data` uses `ref_path.split('.')[0] + '.bed'` (M/MATES/bam_processor.py:17–18). That spelling resolves to `record.bed`. Dots in parent directories, including a leading `./`, can also truncate the path. Keep `_mates` in the stem and specify a tested caller convention with a dot-free relative path before the extension; a consumer workspace can stage the verified bundle under that convention. The other coverage reader prepends its working directory (M/MATES/scripts/count_coverage_10X.py:234), so absolute-path support must also be checked at the selected entry point. Changing extensions or compressing this pair casually breaks the API.

MATES's `exclusive` reference is a different transformation: the builder subtracts gene bodies with `A=True`, dropping whole overlapping records, then may clip records by coordinate side (M/build_reference.py:127–164). Calling it `noExon` would assert the wrong operation. Likewise, a future `5prime` or `3prime` variant needs a stated orientation and clipping rule; those names also describe library chemistry, and the stock clipping code applies coordinate-side operations independently of TE strand (M/build_reference.py:142–160).

Use `subfamily.saf` only for a GeneID representing `rmsk_name`. The existing lab builder makes `name:family:class` IDs (K/te-reference-saf-build/scripts/build_te_saf.sh:78–85). If that compatibility export is required, call it `taxonomy_triple.saf`. Its name makes the changed grouping visible. This is a necessary correction to the earlier proposal that called a triple-keyed output subfamily-level. The new default can directly implement ADR-1's name-level decision; any legacy triple export is separately registered and tested.

The path grammar identifies a usable artifact; the manifest supplies the complete semantics. `MANIFEST.json` owns the file inventory, profile schemas and bundle membership. `universes.json` owns the executable universe definitions and their source-class interpretation. The manifest references and fingerprints it. Duplicate editable copies of the predicates would recreate the ambiguity under different filenames.

## 4. Tool attributes are interface names; mappings provide consistency

Preserve the attributes required by each consumer. TEsingle explicitly searches for `gene_id`, `transcript_id`, `family_id`, and `class_id`, rejects missing/empty values, and constructs `transcript:gene:family:class` as its output feature (E/TEtools/TEindex.py:309–335,358–364; E/TEsingle:146–164). These labels occupy a TE-specific GTF interface. Importing them as canonical gene/transcript/TF identifiers would create false joins.

Define the first `record.gtf` profile as follows. `record_alias` and `instance_alias` below mean deterministic, registered strings safe for the target parser. Keep existing mm39-safe names where permitted; use a checked deterministic safe alias for an otherwise unrepresentable value. The mapping retains the original value and rejects alias collisions. Canonical keys remain unchanged.

| GTF attribute | Exported value | Canonical mapping / consequence |
|---|---|---|
| `gene_id` | Safe representation of `rmsk_name` | TE consensus-name group in this interface; map back to `rmsk_name`. |
| `transcript_id` | `record_alias` | Maps to `rmsk_record_id`. Use a colon-free alias because TEsingle emits colon-delimited tuples. |
| `family_id` | Safe representation of `rmsk_family` | Source-family metadata used in TEsingle's compound feature key. |
| `class_id` | Safe representation of `rmsk_class` | Source-class metadata used in the same key. |
| `locus` | The same `record_alias` | Default Stellarscope feature identity. |
| `instance_id` | `instance_alias` | Maps to `rmsk_instance_id`; selected explicitly for a Stellarscope instance run. |

For example, the colon-free alias `R|mm39|L1MdA_VI|chr1|3050294|3050775|+` can represent canonical `L1MdA_VI|chr1:3050294-3050775|+` for the inspected first source row. These coordinates remain 1-based in both strings. Fields containing unsafe delimiters require the registered fallback; validation of mouse names supplies no license to strip punctuation from a human or other-species label. In particular, percent escaping is unsuitable for the lab cleaner, whose `printf $1` interprets percent directives (K/te-gene-featurecounts/scripts/runFeatureCounts_TE_and_genes.sh:131–136).

The GTF profile uses exon-type rows with 1-based inclusive coordinates and standard quoted attributes. Here `exon` selects an annotation block for the consumer; it establishes no host-gene exon relationship. Preserve actual gene context in the separate transcript relation. If a required source family is empty in a future supported source, the profile needs a reserved, collision-checked missing-family alias registered as source-missing, while literal `Unknown` remains literal `Unknown`.

Stellarscope allows the grouping attribute to change and defaults to `locus` (S/stellarscope/cmdopts/stellarscope_assign.yaml:40–51; S/stellarscope/annotation/_intervaltree.py:41–60). Therefore `record.gtf` describes its default grouping and row provenance; `--attribute instance_id` produces a different `feature_level` from the same bytes. It also merges neighboring intervals using a distance of one (S/stellarscope/annotation/utils.py:17–43), so the downstream registration must distinguish intended catalog blocks from the tool's effective support if its endpoint/gap fixture fails. An annotation namespace cannot certify a counting implementation.

TEsingle combines all four attributes in the key. Sharing `transcript_id` across records of a mixed-name instance would still split its outputs when the other attributes differ. Register the exact output tuple and retain record-level TEsingle interpretation for this profile. The TEtranscripts-style attribute spelling is supported by the checked TEsingle parser and local SAF builder; a TEtranscripts implementation was unavailable in the supplied consumer checkouts, so its exact output behavior remains an adapter validation item.

Document these mappings once in the public output contract and encode the same definitions in the manifest's profile schema: source column, emitted attribute/position, value transformation, selected feature attribute, output-ID construction, coordinate conversion and required companion files. Publish `export_feature_members` with exact emitted feature keys, canonical record membership and retained blocks. Its rows are keyed by export and feature space, so a MATES numeric reference index, its subfamily output, and a TEsingle tuple each have their own interpretation. MATES explicitly aggregates predicted counts by its `group` column (M/MATES/scripts/make_prediction.py:92–95,150–158); that output must register at subfamily level even though the input file is named `record_mates.csv`.

Keep display labels separate from primary IDs. IRescue's feature writer removes `#...` from the display field, while its count index reads the first field (I/irescue/map.py:382–387; I/irescue/count.py:57–62). MATES rewrites final H5AD names as `chrom|start|end|TE_Name`, omitting strand, while its construction retains `TE_index` in variable metadata (M/MATES/TE_quantifier.py:15–23,150–154,185–191). A row index plus the preserved reference index identifies the output even when display names collide.

## 5. The three ledger relations and the conservation rule

Use the same canonical columns in the reference relation and source publication. No consumer should have to guess whether ledger `locus_id`, GTF `locus` and a MATES “locus” denote the same grain.

| Ledger relation | Grain, keys and necessary fields |
|---|---|
| `rmsk_records` | One source record per build, including records with zero peak overlaps. PK `(te_build_id, rmsk_record_id)`. The physical published-table schema is given above; ingestion adds `te_build_id`. |
| `peak_record_overlaps` | One peak–record intersection in one selected overlap generation. PK `(atlas_id, peak_id, te_build_id, rmsk_record_id)`. Carry `overlap_start_0:int64`, `overlap_end_0:int64`, `overlap_bp:int64`, `peak_overlap_fraction:float64`, `record_overlap_fraction:float64`. Scope the generation and algorithm through the ledger manifest. The record denominator is full `length_bp`; the peak denominator is its full interval length. |
| `te_feature_registration` | One measured output-feature–source-record–retained-block edge. Key `(analysis_run_id, matrix_id, feature_index_0, te_build_id, rmsk_record_id, block_index)`. Preserve exact `tool_feature_id`, separate `feature_display_name`, `feature_level`, the selected export/profile and its `universe_name`/variant, plus `block_start_0`, `block_end_0`. Every edge has a typed record FK. Export-level definitions are reused from `export_feature_members`; analysis-run metadata pins tool/version/options and the actual output matrix. |

`matrix_id` distinguishes separate output products within a run, and `feature_index_0` is the original matrix position. A display label alone is insufficient, especially after tool-generated aliases or `var_names_make_unique`. Feature definitions and registrations are reference/mapping facts; counts stay in the measurement table at their original feature grain. Unobserved input features remain available through the export membership relation, with measured-zero/filtered/unreported status handled at the run boundary. A missing registration edge must never manufacture a zero count.

`peak_record_overlaps` describes the full catalog intersection. A query against exon-subtracted support intersects the peak with the registered retained blocks and produces a separately named derived result. Reusing full-record overlap fractions for those blocks would imply support in removed exons. A motif-inside-TE claim similarly requires intersection with TE sequence; overlap with the enclosing peak alone is insufficient.

For instances, record both full-source and selected-record membership through the catalog and export mapping. An instance selected only partly by a universe remains visibly partial. Multiple disjoint pieces of one record are separate blocks of one member, and one record's length stays unchanged in the catalog.

The indispensable query test is: feature F has count 7 and three member records; selecting those records returns F once and total 7. Aggregate facts after selecting **distinct measured feature keys** or through an existence join. `SUM(DISTINCT count)` is wrong: it collapses different features that happen to have equal counts. A table name cannot prevent multiplication by a many-to-many join. Mixed-subfamily instance counts require an explicit inference/allocation before any subfamily attribution; membership supplies possible support. This implements the owner's conservation requirement (A/consult/fanout/owner_context_2026-09-15.md:35–42,51–57).

## 6. Species and modality adversarial test

| Arrival / question | Namespace failure to prevent | Required interpretation |
|---|---|---|
| **hg38 alongside mm39** — “are these the same repeat?” | A name/coordinate string or bare instance integer can repeat across builds; `chr1` carries no assembly identity. `hg38` also leaves the actual sequence dictionary and source run implicit. | Join through `te_build_id` and its manifest. Cross-species/model equivalence needs a separately evidenced correspondence, with accessions/sequences where available. Names, liftover or shared class labels alone establish different kinds of similarity. |
| **Another species/run** — “why did records disappear?” | Mouse-tested source alphabets, instance scope, class vocabulary, uniqueness and UCSC/Ensembl aliases may fail. A slash in a repeat label also makes it unsuitable as a directory component. | Keep biological labels in typed data. Validate source fields and declared universe predicates for every build; use path-safe controlled tokens for directories. Preserve canonical contig IDs when exporting aliases, and reject lossy/many-to-one mappings. A source unsupported by the current schema fails explicitly. |
| **3′ nuclear RNA** — “is the TE autonomously transcribed?” | `gene_id`, GTF `exon`, `noExon`, or a generic `expression` label can imply host-gene independence. Intronic host pre-mRNA can still contribute after exon subtraction. | Describe the measurement as TE-associated RNA at the recorded feature level; require record–transcript relation, strand and the assay/run specification for an origin claim. Exon subtraction is a defined support policy. |
| **5′ whole-cell RNA, paired-end** — “does this support a TE promoter?” | Library 5′ chemistry, a repeat-model 5′ boundary and a clipped file called `5prime` can be conflated. A truncated record lacks a demonstrated promoter. | Keep library geometry in analysis metadata, forward-model coordinates in the catalog, and structural/promoter evidence in its own later relation. Preserve molecule versus alignment/read-pair counting unit and explicit strand/mate interpretation. |
| **Paired-end ATAC** — “is this TE sequence accessible?” | A fragment spanning the TE, a cut inside it, and a peak overlapping it can all be called a TE hit. An instance bounding span can include unrelated sequence. | Use separately named fragment-overlap, cut-site and peak-overlap measurements; record `count_geometry`. Restrict TE-sequence queries to member-block unions. The ledger consult already separates corrected fragment endpoints from fragment-overlap estimators (L:231). |
| **External bulk** — “can these subfamily counts be combined?” | Bare-name inference, raw-taxonomy-triple counts, sums of record-level estimates and mixed-instance counts can share a display label. Reads, read pairs and inferred allocations may also differ. | Register `feature_level`, grouping components and `measurement_kind`/`counting_unit` through `analysis_runs`. Carry direct-subfamily and summed-record estimates as distinct products. A filename or name match establishes no estimator equivalence. |

The reference remains modality-independent. These distinctions belong in reusable source/profile metadata and downstream analysis-run records, rather than assay-named reference trees. In particular, a namespace amendment preserves the future question “which retained TE bases supported this measured feature?” while leaving autonomous transcription and intact-element status for analyses that can supply their evidence.

## 7. Directory reading test

This is an illustrative listing of one **future** published mm39 build, including the conditional instance BED. It makes no claim that these artifacts already exist. `<64_hex_build_id>` is the one ADR-7 content identifier.

```text
te_mm39/
  current -> archive/<64_hex_build_id>/
  archive/<64_hex_build_id>/
    BUILD_ID
    MANIFEST.json
    universes.json
    source/
      mm39.fa.out.gz
      rmsk.txt.gz
      chromAlias.txt
      mm39.chrom.sizes
      gencode.vM37.primary_assembly.annotation.gtf.gz
    tables/
      rmsk_records.tsv.gz
      rmsk_records.parquet
      rmsk_instance_members.tsv.gz
      rmsk_taxonomy.tsv
      taxonomy_canonical.tsv
      export_feature_members.tsv.gz
      export_feature_members.parquet
    exports/ucsc/interspersed/
      full/
        record.bed
        subfamily.bed
        instance.bed
        record.gtf
        record_mates.csv
        record_mates.bed
      exon_subtracted/
        subfamily.saf
```

A newcomer can locate the full source catalog, source grouping, original and curated taxonomy, tool-to-record membership, untouched interval exports, exon-subtracted counting support and MATES companion pair from this listing. `subfamily.bed` describes its feature-name level; it can contain many genomic rows for each name. `record_mates.bed` visibly belongs with its CSV and differs from ordinary `record.bed`. The universe and contig namespace apply to every export below them. Other declared universes receive export directories when a consumer needs them; `universes.json` defines all supported predicates independently of which formats ship.

The listing deliberately cannot promise everything: exact coordinate contracts, source library versions, the GTF's selectable grouping attributes, subtraction strandedness and effective quantifier behavior require the manifest/profile contract. Encoding every one of these in a filename would make filenames an unreliable second schema. This grammar passes the practical reading test—choosing the artifact and recognizing its transformation—and leaves exact interpretation to one machine-readable authority.

## Final ruling — AMEND; public DECISIONS.md text

te-tracks uses the `rmsk_` namespace for source records, RepeatMasker instances and source taxonomy, with build-scoped keys and a separate canonical taxonomy for rollups. Exports follow `exports/<contig_namespace>/<universe_name>/<interval_variant>/<level>[_<profile>].<format>`, and each declared profile specifies its feature keys, coordinate convention, attribute mapping and companion files. The ledger uses `rmsk_records`, `peak_record_overlaps` and `te_feature_registration` to connect measured features to retained source-record blocks while preserving each measurement at its recorded feature level.

## Open items before implementation

1. Freeze the source-normalization contract against the pinned inputs: class-only `.out` tokens versus UCSC family labels, reverse-strand consensus fields, grouping-ID scope and duplicate-key failure policy. The schema above supplies the fields; the full-source cross-check must supply the accepted cases.
2. Freeze the initial consumer-profile fixture contracts and exact MATES entry points/output products, including its path handling, TEsingle tuple aliases, the SAF grouping choice and registration conservation. Define the expected results before exporter implementation; execute the fixtures before publication, with Stellarscope endpoint/gap behavior treated as a consumer limitation to resolve explicitly.
