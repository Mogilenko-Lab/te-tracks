# Unified TE schema consult (codex gpt-6-astra)

## Summary of recommendations

1. Q1: Publish a reference/dataset/integration constellation of immutable tables, with explicit feature, interval, cell-group and estimator grains; bind every matrix through all four registration fields.
2. Q2: Use a marimo query surface with compact jscatter panels and a genomic interval panel; fetch viewport tracks and precomputed summaries from manifest-pinned Parquet through DuckDB.
3. Q3: Make the explorer the first reconstruction consumer; store parameterized candidate geometry, membership and evidence separately from the analysis's structural verdicts.
4. Q4: Test prespecified subfamily/lineage RNA contrasts across animals; retain model clade and record divergence as separate evidence axes and measure mapping sensitivity.
5. Q5: Separate same-nucleus co-detection, condition-level concordance and animal replication; reserve “transcription supported in this region” for spatially attributable RNA evidence.
6. Q6: Export one animal × tissue × cell type × feature table per model, preserving raw count semantics, exposure, annotation pins and missingness.
7. Q7: Start 14761 RNA qualification and a small paired funnel in `40_transposable_elements/`; phase 9 supplies Dfam, the record STARsolo profile and binding fixtures; structural views follow the host build.

Citation roots: `C` = `docs/_internal/redesign-2026-09/consults`; `T` = `docs/_internal/redesign-2026-09/taxonomy`; `P` = `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign`; `D` = `/workspaces/Meta-Aging/14761-DM/docs/_internal/_project/plans/2026-09-11_codebase-topology`; `A` = `/workspaces/Meta-Aging/AGENTS.md`; `B` = `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build`; `K` = `/workspaces/Meta-Aging/01_modules/.ref/14839-DM-cGAS/01_modules/TE-RNAseq-toolkit`; `N` = `/workspaces/Meta-Aging/.claude/skills/notebook-exploration/SKILL.md`. Other paths are package-relative. JSON/gzip citations identify keys where line numbers are uninformative. M1–M3 below are this consult's measurements; other numbers retain their source attribution. All new tables, policies, thresholds and SQL views below are **proposals**, unless identified as existing.

## Q1. The unified schema

**Question and evidence.** Which identities and grains connect the assays without changing what was measured? Existing reference units are record, source instance and `rmsk_name`; the stable record key is `(te_catalog_id,rmsk_record_id)`, while `te_build_id` identifies the exact reference bytes. An instance groups records and may mix names/strands; insertion units need reconstruction (`docs/DECISIONS.md:5–11,74–80,111–133`; `docs/OUTPUTS.md:19–42,59–72,440–441`). Matrix binding includes `(universe_name,variant,feature_level,key_grammar)`; the older two-field sentence at `docs/OUTPUTS.md:436–440` is superseded by `docs/DECISIONS.md:158–163`. Child snapshots pin parent build, annotation digest and policies (`docs/DECISIONS.md:34–48`).

**Options and consequences.** One wide peak/TE table multiplies counts across transcripts, motifs, TF candidates and regulons. A peak-only star loses TEs outside admitted peaks and RNA-first queries. Separate reference dimensions and assay facts, connected by interval/membership relations, preserve each grain and support both entry points; small overview views provide browsing convenience (`D/01_consult_codex.md:143–172,194–210`; `D/02_next_session_agenda.md:35–52`). Recommend the latter, with keys in the sketch below. TE annotation follows the atlas's NEVER-GATE rule: attaching a registry changes annotation, while peak admission retains its own producer (`D/00_INDEX.md:74–82`).

**Identity/provenance recommendation.** Qualify aliases with catalog and registration identity; aliases are spellings, including `R|mm39|…` and `I|mm39|…`, and retain UCSC components across export namespaces (`docs/OUTPUTS.md:351–359,420–434`). Give each quantification attempt a `run_id` and each output channel a `matrix_id`; unique-only and total-with-EM are separate products. Store input digests, code/environment/recipe hashes, reference FASTA/dictionary, GTF, child, atlas and barcode-roster pins, chemistry, mate/strand/UMI rules, alignment caps, feature assignment/reporting levels and count unit. Keep artifact/long-hash provenance in manifests and expose it through SQL views. A registration identity distinguishes core and child block sets even when their four-field bindings agree. The consumer's `te_feature_registration` preserves source matrix IDs/axis ordinals and their mapping to emitted IDs; count views below use those mapped IDs. Gene/transcript IDs retain source spelling/version and locus; cross-annotation equivalence requires an explicit bridge (`docs/DECISIONS.md:59–61`; `C/loci_gtf_consult.md:57–59,135–149`; `C/gene_child_consult.md:45–59`).

**Storage recommendation.** Use typed Parquet in immutable manifest-listed generations, with one DuckDB connection per reader and disposable local materializations for repeated joins. Coordinate views convert core `[start_1,end_1]` to `[start_1-1,end_1)` and normalize contigs through the pinned alias table. Partition large interval relations by generation and chromosome, sort coordinate-oriented partitions, and retain compact integer surrogates with reversible ID dictionaries. Foreign-key, grain and completeness validation happens at publication (`docs/OUTPUTS.md:3–5,128–142,533–550`; `D/01_consult_codex.md:131–147,194–202`). General systems reasoning: Parquet alone supplies neither enforced relational constraints nor a genomic interval index; DuckDB scans do not replace tile serving, multiwriter transactions or a sparse matrix store. Keep full cell matrices in their assay storage, expose selected sparse slices and group summaries through SQL. A dense 3.8-million-record × million-cell table is the wrong physical representation; `D/00_INDEX.md:108–109` already separates the cell axis.

**Settling measurement.** For each output matrix, require every feature to resolve at its declared grain, zero unintended fan-out, and conserved total before/after a valid rollup; test overlapping blocks and both universes. Verify that sparse absence becomes zero only inside the measured feature × eligible-cell universe. Benchmark cold/warm viewport, grouped RNA and motif-intersection queries at full catalog size, ~30 million context pairs and simulated million-cell sparse workloads; retain wall time, RSS, bytes scanned and result cardinality. These are proposed admission measurements, not measurements performed here (`docs/DECISIONS.md:137–146,160–163`; `D/01_consult_codex.md:198–210`).

## Q2. The interactive genome projection

**Question and evidence.** The user's funnel requires intervals inside peaks and a visible distinction between measured zero and uncomputed evidence (`D/02_next_session_agenda.md:35–52`). M1 measures 3,764,949 interspersed records within 5,320,771 total; the context estimates are 24.2–26.8 million pairs at the ruled envelope, with exact full-genome serialization still outstanding (`C/structural_views_consult.md:35–45,158–166`). The current Multiome roster is documented as 14,265 nuclei; millions of cells are a future scaling target (`D/02_next_session_agenda.md:69–73`).

**Options and consequences.** Marimo plus jscatter fits linked cell/feature scatter panels over compact exports; an embedded igv.js or JBrowse panel is a candidate for detailed coordinate tracks; HiGlass is a candidate when multiscale genomic/contact views become central; a DuckDB-backed track service separates data queries from the UI but adds an API/cache/deployment contract. Browser-specific suitability is **general software knowledge beyond local inputs, unqualified offline**. Recommend marimo as the query/controller surface, 2–4 jscatter panels and a small embedded genome-browser prototype, then a track service only if latency requires it. The local skill supplies export-first, bounded-widget and read-only exploration conventions; its template is live-kernel `.qmd`, so a marimo implementation is an explicit adaptation to the owner's brief and existing marimo sessions (`N:17–25,57–63,69–108,119–124`; `A:185–199,277–284`).

**Query grammar recommendation.** Persist a typed query specification: `reference/atlas/roster pins → lineage selector → RNA support policy + run → accessibility scope + run → motif spatial predicate + scan → condition/cell-type selection → optional GRN source/replication tier`. Allow predicates to narrow in any order, with a visible count and denominator after every step. “All L1 remnants” selects reference records; a subfamily estimate colors an aggregate track, while locus-specific support colors attributable records. Offer `peak_open`, `cuts_in_record`, and `cuts_in_TE_peak_intersection` as distinct scopes. “Inside” defaults to full motif containment in the TE–peak intersection; partial overlap is another named rule. TF drill-down joins motif-to-TF candidates to annotation-matched gene expression in selected groups and to source-qualified GRN edges. Motif-to-TF is many-to-many, and a motif match remains sequence evidence (`D/01_consult_codex.md:158–192,229–239`; `docs/OUTPUTS.md:436–441`).

**Tracks and indexing recommendation.** Stack (1) strand-aware record blocks colored by one selected lineage/clade/divergence field, (2) instance/candidate blocks, (3) RNA unique and allocated support, (4) existing peak accessibility and separately counted TE/intersection cuts, (5) exact motif sites, (6) GRN region/gene links, and (7) annotation-matched gene/transcript context. Keep uncertainty/status visible in tooltips and filtering. Build a dataset-owned interval service/index on `(assembly,dictionary,chrom,start_0,end_0)` with bins referencing every bin an interval overlaps, followed by exact overlap filtering and ID deduplication. Overview tiles summarize occupied bases/support; zoomed queries return records. General engineering recommendation: send bounded viewports and compact cell selections to the browser, query context only for selected records, and precompute group/tile aggregates instead of drawing millions of intervals or shipping all context pairs.

**Settling measurement.** Prototype chromosome overview → 100-kb region → selected record → same-cell evidence on the same pinned release; target <1 s warm viewport response and bounded browser/kernel memory as provisional UX goals. Compare indexed results to a complete interval scan, including long intervals crossing bins and endpoints. Rebuild the jscatter grid repeatedly and confirm bounded live widgets (`N:88–108`). Existing ports 2716/2719/2782 serve named explorers; choose an additional configured port for any new service after inventorying listeners (`A:185–199`). Reference delivery order is given below; only interval/identity and qualification artifacts belong to te-tracks (`AGENTS.md:3–5`).

## Q3. Reconstruction as a consumer

**Question and evidence.** The explorer now names three concrete consumers: L1 completeness, proviral configurations and solo-LTR candidates (`C/adr_rulings_2026-09-17.md:378–392,450–457`). Existing instance membership supports 3,152,636 interspersed groups, including 30,569 mixed-name and 23,244 mixed-strand groups; block unions retain 263,926,042 gap bases outside repeat support (`C/structural_views_consult.md:61–84`).

**Options and consequences.** A record-length/prefix shortcut is useful for screening but loses fragmented copies and model correspondence. Same-instance reconstruction preserves the source hypothesis but misses cross-instance partners. A parameterized candidate graph over records/blocks, followed by sequence and model compatibility evidence, retains competing hypotheses. Recommend that graph, with te-tracks publishing catalog-only geometry and the analysis publishing reconstruction runs, candidates, component roles, alternatives and verdicts (`docs/DECISIONS.md:111–133`; `C/structural_views_consult.md:115–132`).

| Consumer question | Required parameters and evidence | First view and admission gate |
|---|---|---|
| Which L1 copies in each subfamily retain the model prefix and approach full model coverage? | Catalog/universe; seed instance or adjacency rule; strand/order; maximum gap/nesting policy; model accession/version set; prefix/suffix tolerances; minimum aligned coverage; treatment of discordant names and invalid consensus extents. Preserve genomic block coverage separately from model coverage. | Instance union plus eligible record 5′ windows; compare block support/gap-only negatives and both strands. A full-length verdict additionally needs a validated mapping from the 2018 RepeatMasker model coordinates to the selected Dfam model coordinate system. |
| Which LTR–internal–LTR configurations are provirus candidates? | Component-role and compatible-model-pair dictionary; same contig/orientation; TE-oriented flank order; internal fragment assembly; both gap thresholds; outer-span/nesting policy; retained alternative flanks; optional sequence/TSD/LTR similarity evidence. | LTR–internal pair table with `same_instance`, `adjacent_same_family`, `unpaired`, `ambiguous` evidence. Require endpoint/gap fixtures and measured competing partners; compare curated/sequence-supported configurations before a biological verdict. |
| Which LTRs are solo-LTR candidates? | Validated LTR role; searched neighborhood and compatible internal-model universe; assembly gaps/callability; reconstruction completeness; negative-search status and sequence evidence. | Complete component status plus pair/search relation. Absence becomes `unpaired_in_envelope`; the analysis can promote to `solo_candidate` after assessing missing/fragmented internals. |

The parameter/gate proposals follow the measured geometry and its limitations at `C/structural_views_consult.md:86–132`; sequence/TSD validation is **general biological reasoning**, unperformed here. At gaps 1 kb versus 5 kb the broad screen yields 93,660 versus 237,375 pairs; greater yield has unmeasured precision. Only 588 L1 records start at model base 1; two have invalid consensus extents elsewhere in the catalog (`C/structural_views_consult.md:88–128`; M1). Prefix presence establishes available reference support; functional promoter/ORF status requires sequence evidence and transcriptional evidence remains assay-specific.

**Model-length correction.** M1 finds 1,047 exact matches, 147 strict part sets and 26 missing names; 117 part sets contain fewer than three parts, and six sets are L2/CR1. All strictly selected accessions have full metadata; broad search-hit accessions can lack full records by the snapshot's declared scope (`T/dfam_interspersed_mm39_snapshot.json.gz:summaries,records`; `T/dfam_interspersed_mm39_snapshot.provenance.json:13–30`). L1MdA_I's three model lengths sum to 7,002 bp, but a sum of current part lengths supplies a metadata summary until their order/overlap and correspondence to old whole-model coordinates are validated. Preserve `available_part_count`, missing part roles and `model_projection_status`; do not use an incomplete sum as the full-length denominator. The phase-9 plan's 143-part/30-miss census anchor needs reconciliation with this strict rule (`P/19_phase9_acceptance_park.md:19–27`; `C/field_practice_synthesis.md:189–195`).

**Settling measurement.** Sweep prefix tolerance 0/10/100 bp and adjacency gaps 100/1000/5000 bp; report candidate yield, alternative-partner rate, mixed-name/strand exclusions, model-mapping failures and precision/recall on independently reviewed positive and negative examples. Store one evidence item per observation with method/input digest; retain alternative candidates sharing a record. Any counts assigned to reconstructed units require a declared molecule allocation or recount, because summing component counts can duplicate shared support (`docs/OUTPUTS.md:436–441`; `C/structural_views_consult.md:128–132`).

## Q4. The evolutionary-origin question

**Question and evidence.** Ask whether age-associated TE RNA/accessibility is concentrated in particular evolutionary lineages and divergence strata. Wicker names and the Dfam rank/clade view are already ruled for phase 9a, superseding earlier deferrals (`C/adr_rulings_2026-09-17.md:429–449`). Derive Wicker class/subclass/order/superfamily by named tree/code rules; store Dfam leaf as the ruled operational family value, with its path retained. This leaf label does not itself establish a sequence-based 80–80–80 family test (`C/adr_rulings_2026-09-17.md:394–415`).

**Options and consequences.** A binary “young” label hides discordant or missing evidence. Divergence alone depends on model and substitution history; clade alone is a model's taxonomic assignment. Recommend two query axes: curated clade path/tier and measured divergence, with explicit unknown/conflicting/assembly-incompatible states. Mus and Mus musculus are candidate mouse-restricted strata; Murinae/Muridae remain separate intermediate strata; Muroidea, Rodentia, Mammalia and deeper compatible clades remain separately queryable. Collapsing them is an analysis policy. M1 observes nine multi-clade models and 33 models with a Primates branch; preserve all clades and flag incompatibility instead of assigning these a mouse age tier. A zero observed count also needs callability/eligibility evidence (`T/dfam_interspersed_mm39_snapshot.json.gz:records.*.clades`; `C/adr_rulings_2026-09-17.md:353–368,474–480`; `C/structural_views_consult.md:134–152`).

**Aggregation recommendation.** Offer Wicker order/superfamily, any Dfam ancestor node, subfamily, clade tier and disjoint divergence bin as named aggregation sets. Store lineage-node membership as sets and publish one conserving feature-to-bucket mapping for each chosen partition; counting a subfamily under multiple ancestors answers overlapping-set questions. Subfamily counts support lineage/clade summaries; within-subfamily divergence-bin abundance requires record-level attribution. Never distribute a subfamily total among its copies using reference counts, length or median divergence. Keep raw RepeatMasker and canonical labels beside derived ranks (`docs/OUTPUTS.md:148–167,210–218`; `docs/DECISIONS.md:165–175`).

**Testability and settling measurement.** With four animals per condition, prespecified, adequately observed subfamilies and a small number of broad lineage/clade contrasts are candidates for animal-level inference; broad pooling gains counts while hiding opposing subfamily effects. Record drill-down, rare subfamilies, many nested lineage tests and clade × divergence × cell-state × treatment interactions are primarily exploratory until power/stability is demonstrated. Multiome condition effects remain descriptive. Require per-animal effect plots, minimum eligibility/prevalence, multiplicity control, leave-one-animal-out sensitivity, and power/dispersion estimates before fixing the test family. Compare unique-only versus allocated counts, saturation at alignment caps, callable fraction, host-context strata and estimator disagreement by clade/divergence (`A:35–47`; `C/open_questions_premises_2026-09-17.md:274–303`; `D/01_consult_codex.md:237–239`). These statistical recommendations are general knowledge beyond the inputs. Such results concern evolutionary distribution of associated signal; causal TE-driven aging, insertion dates and functional activity require additional evidence.

## Q5. Self-sustained Multiome against unpaired runs

**Question and evidence.** 14761 has four pooled condition libraries (three mice each), with paired RNA/ATAC nuclei and no recovered MouseID; 14616 and 14782 have the same 20 animals, four per five conditions, paired across spleen/lung (`A:35–58`). Whole-cell datasets use 5′ PE OCM v3, GRCm39 GEX 2024-A, both cDNA mates and introns; Multiome GEX is R2-only and ATAC paired, using ARC 2024-A. GEX's filtered vM33 annotation is verified; ARC annotation equivalence remains a pilot gate (`C/field_practice_synthesis.md:155–166`; `C/loci_gtf_consult.md:71,145–149`; `K/cellranger-refs/README.md:3–14`).

**Options and recommendation.** A single `supported` flag conflates spatial, cellular and cohort evidence. Use separate row-level fields: `pairing_level=same_nucleus|same_group|condition_cross_dataset`, `rna_attribution=unique_locus|model_allocated_locus|subfamily_only|unresolved`, `spatial_scope=record|TE_peak_intersection|whole_peak`, `replication_tier=multiome_descriptive|single_tissue_animal|paired_tissue_animals`, and `inference_source=paired_multiome|unpaired_wholecell|combined`, plus supporting run IDs. A combined model retains source-specific edges; “both” never invents a matched cell. Integration meets through `condition_key`, harmonized labels and registered features; spleen/lung additionally meet through the verified cohort-qualified MouseID (`D/02_next_session_agenda.md:54–76`; `A:45–58`).

**Operational transcription support.** At minimum, require eligible paired barcodes, deduplicated RNA molecules attributable to the record under a stated unique/posterior policy, and a cut in the specified interval of the same nucleus. Stronger “RNA observed in this TE-derived open region” requires RNA aligned blocks within that TE–peak intersection or independently supported transcript structure connecting the RNA to it. RNA assigned elsewhere in the record supports record-level co-detection; family EM support supports a family claim. Store unique/ambiguous support and the exact RNA/ATAC spatial predicates, ambient/doublet QC and posterior thresholds. A positive fractional EM allocation alone is insufficient to localize transcription. The strict SQL funnel below uses at least one unique locus-supported molecule with an aligned block in the intersection; an allocated-evidence sensitivity run has its own policy and evidence tier.

Autonomous transcription remains a further claim: compare matched transcript context, relative strand, host expression/read-through and intronic background; require initiation/structure evidence before interpreting a TE's own promoter. The 3′ nuclear assay usually leaves that origin unresolved. The optional pure-intronic/exonic no-repeat regions can support the consumer's intron-background diagnostic U; U is a coverage ratio, can exceed one and supplies no per-TE subtraction rule (`C/mask_policy_consult.md:109–130`; `C/field_practice_synthesis.md:201–211,240–243`; `K/docs/LIMITATIONS.md:128–137`). These operational thresholds are recommendations, to be calibrated; physical RNA/ATAC co-detection is observational and does not establish a regulatory link.

**Settling measurement.** Count the four per-nucleus detection cells (RNA+/ATAC+, +/−, −/+, −/−) over jointly eligible barcodes for each selected interval, retaining depth and assay dropout. Verify barcode namespace/concordance, unique versus allocated support and gene/TE competition on a full-genome-background simulation plus real examples. Within-library label/depth-matched permutations can assess technical co-detection; nuclei provide no condition replication. Whole-cell arms supply RNA replication and tissue interactions, plus additional TF-expression evidence for the same Multiome ATAC regions; they supply no same-cell ATAC validation (`C/adr_rulings_2026-09-17.md:33–50`; `D/02_next_session_agenda.md:56–76`).

## Q6. Statistical modelling entry points

**Question and evidence.** The harmonizing axis has five conditions; Multiome lacks `Old_Rapa_MetR`, and tissue pairing belongs to the whole-cell animals (`A:37–47`). Counts inherit tool-specific identities: IRescue reads BED column 4; Stellarscope reads `locus` or selected `instance_id`; TEsingle/TElocal report four-tuples; TEtranscripts reports taxonomy triples; featureCounts reads SAF GeneID; STARsolo's admitted record profile uses record alias as gene ID (`docs/OUTPUTS.md:472–484`; `docs/DECISIONS.md:148–163`). MATES ordinal identities additionally need their fixture/feature roster mapping (`docs/OUTPUTS.md:479,507–511`).

**Options and recommendation.** Per-cell condition tests inflate biological replication. One global TE total loses the lineage and mapping questions. Export separate, versioned tidy views for (a) subfamily RNA, (b) one specified lineage partition, (c) selected attributable records, (d) unique-mappable TE/intersection cuts, and (e) paired co-detection. Each row identifies dataset, tissue, cohort-qualified MouseID or condition-pool library, condition, cell-label version/level, feature, run/channel, observed value, exposure, eligible cells and claim tier. Retain a complete eligible feature/group grid through a zero-completion view; distinguish empty groups, excluded features and unsupported estimation. The reporting tiers follow the ruled animal/tissue/Multiome distinction (`C/adr_rulings_2026-09-17.md:311–313`; `C/open_questions_premises_2026-09-17.md:296–300`).

**Model recommendation (general statistical knowledge).** Start animal-pseudobulk models per tissue/cell type with `~ condition_key`, using a count likelihood only when the chosen count channel meets its assumptions and with a declared library-size offset. For matched tissues use `~ tissue * condition_key + (1|MouseID)` or equivalent paired contrasts; an animal fixed effect absorbs its between-animal condition main effect. Young-versus-old control tests age; the four old arms allow a treatment factorial question, with interaction power assessed separately. Fractional EM expectations stay float64; select an uncertainty-aware/validated analysis or an explicit sensitivity to integer assignment, rather than silently rounding into an integer-count model. Different chemistries, input compartments and estimator generations retain separate run strata. Report effect sizes/intervals and prespecified multiple-testing control; high-dimensional exploratory selections require subsequent validation.

**Conservation rules and settling measurement.** Sum a measured feature once after deduplicating its support map; avoid summing multi-universe registration rows, context pairs, motif-to-TF edges, overlapping record cut counts, nested label levels, independent estimator outputs, or unique counts plus a total that already includes them. An instance with several names requires allocation before a subfamily rollup. Union/deduplicate cuts within the target aggregate, or conserve explicitly allocated cut weights, to make ATAC totals meaningful. Track raw fractional counts and their ambiguous component; record-level and directly fitted subfamily estimates are separate estimators (`docs/OUTPUTS.md:414–441`; `C/field_practice_synthesis.md:213–224`; `C/loci_gtf_consult.md:47,57–59`). Require conservation checks, zero/missing fixtures, correct animal/condition design rank, four animals per eligible whole-cell condition, paired-tissue completeness and sensitivity to animal/label/estimator exclusions before fitting.

## Q7. Staging

**Options and recommendation.** A complete browser/reconstruction platform first delays the primary estimators; RNA-only deployment cannot exercise the genomic funnel. Build an RNA-first vertical slice with a minimal interval evidence contract, then extend the ATAC/GRN schema. The ruled reusable module is `/workspaces/Meta-Aging/01_modules/te-consumers/`, with environment/recipes owned there; datasets call it from `40_transposable_elements/`. This supersedes the older D1 consult's SoloTE/Telescope suggestion (`C/adr_rulings_2026-09-17.md:327–331,433–439`; `D/01_consult_codex.md:227`).

**First work in 40.** Publish input/roster/reference and matrix-binding manifests plus the namespace README's unique-mappability bias. Qualify 14761 RNA using the common STAR realignment, IRescue subfamilies, TEsingle assignment sensitivity and Stellarscope evaluation, preserving known limitations. Reuse v2 peak coordinates and the stage-10 count contract for peak accessibility; annotate `all_rmsk` intersections without altering admission. Existing corrected fragments can provide the explicitly unique-mappable TE cut channel; recovering alternatives requires BAM/FASTQ work and a separately validated ATAC model. This reconciles D1's raw-data ambition with the later ruling of no initial custom ATAC EM (`C/adr_rulings_2026-09-17.md:33–44,311–326`; `D/01_consult_codex.md:231–239`; `D/00_INDEX.md:65–82`).

**Smallest real slice.** Use 14761 Old_Control and Young_Control pooled libraries, their cleaned paired nuclei and v2 admitted peaks, with whole-genome RNA alignment/competition retained. Display one chr1 viewport containing L1 candidates and expose a cell-type filter; compute all admitted label groups identically, then select the narrative view. Required tables: `record`, `matrix_binding`, sparse RNA counts/block support, `cell`/`cell_group`, `peak`, `peak_record_overlaps`, existing `peak_counts`, new `intersection_cell_cuts`, motif hits and the derived `rna_region_cell`. Execute SQL 3 with both condition keys; show stepwise record/peak/paired-cell/motif counts and candidate TF families, including a valid empty result. Motif scanning needs a pinned genomic FASTA/motif collection; a GRN overlay waits for v2 region/source-qualified edges. This is a proposed production slice, not an analysis performed here (`D/02_next_session_agenda.md:35–49,63–76`; `C/loci_gtf_consult.md:135–149`).

**What waits and settling measurement.** Phase 9a provides Dfam/Wicker/clade metadata, `record_starsolo.gtf`, full-binding/conservation fixtures and environment documentation; phase 9b qualifies publication. The ARC GTF pin and matching gene child precede context interpretation; phase 8 explicitly has `not_computed` context. Full motif-to-TF/GRN edge semantics, cut allocation, advanced serving and multimapper ATAC depend on D2/D3 design. The first slice passes only when row/feature/barcode identities conserve, same-nucleus joins use the same library-qualified cell, motif sites lie in the claimed intersection, and an independent interval check reproduces a sample. Broaden to all four Multiome conditions, then the paired whole-cell RNA cohorts (`P/19_phase9_acceptance_park.md:3–48,84–94`; `docs/DECISIONS.md:96–109`; `A:35–47`).

## Schema sketch

All names below describe a proposed SQL surface. Existing physical contracts are `B/tables/rmsk_records.*`, `rmsk_instance_members.tsv.gz`, `rmsk_taxonomy.tsv`, `taxonomy_canonical.tsv`, `universe_members.tsv.gz`, `export_feature_members.tsv.gz` and alias/export inventories (`docs/OUTPUTS.md:12–167,399–457,533–551`). The loader injects file-scope catalog/build IDs from manifests into reference views. Abbreviations: `R=(te_catalog_id,rmsk_record_id)`, `I=(te_catalog_id,rmsk_instance_id)`, `S=(te_catalog_id,rmsk_name)`, `P=(atlas_id,peak_id)`, `C=(dataset_id,library_id,barcode)`; `cell_id` is a reversible surrogate for C. `generation_id` qualifies every dataset/integration satellite below, and is an implicit part of its key. Derived reference relations additionally key their build, child, snapshot or parameterized view identity. `group_id` globally identifies a pinned library/animal/label-level selection; groups at different hierarchy levels can overlap.

| Table(s) | Grain and primary key; essential fields | Owner / basis |
|---|---|---|
| `te_catalog`; `te_build` | Catalog `te_catalog_id`; build `te_build_id` FK catalog, manifest/source/dictionary digests, assembly | te-tracks; `docs/DECISIONS.md:74–82` |
| `record`; `instance`; `instance_member` | Record R, all canonical columns; instance I, grouping scope; membership `(I,R)`; record belongs to one instance | te-tracks, views of existing tables; `docs/OUTPUTS.md:19–63` |
| `subfamily`; `raw_taxonomy`; `canonical_taxonomy` | S; raw `(S,class,family)`; canonical `(te_build_id,S)` plus rule/status; canonical family key includes class | te-tracks; `docs/OUTPUTS.md:65–72,148–167,210–218` |
| `universe_member`; `feature_member` | `(te_build_id,universe,R)`; `(registration_id,universe_name,variant,feature_level,key_grammar,emitted_feature_id,R,block_start_1,block_end_1)`; registration pins build/child | te-tracks, logical complete-catalog membership includes implicit all_rmsk; `docs/OUTPUTS.md:105–109,399–429` |
| `dfam_model`; `lineage_node`; `lineage_closure` | Model `(snapshot_id,accession,model_version)` with length/release; node `(snapshot_id,full_path)` with parent/Wicker/RM equivalents; closure `(snapshot_id,ancestor_path,descendant_path)` | te-tracks, proposed normalized companion; `T/dfam_interspersed_mm39_snapshot.json.gz:records,classes` |
| `subfamily_model`; `model_clade`; `subfamily_rank` | `(te_build_id,S,snapshot_id,accession,version)` with match rule, exact/part role/status; `(model_key,clade_path)`; `(te_build_id,S,snapshot_id,rank_scheme_id,rank_name)` with value/status/source node and part-set agreement | te-tracks; preserves set metadata behind the planned one-row/name view, `P/19_phase9_acceptance_park.md:16–29` |
| `annotation`; `gene`; `transcript`; `transcript_segment` | Annotation digest; `(digest,source_gene_id,locus_key)`; `(digest,source_transcript_id,locus_key)` FK gene, flags; `(transcript_key,segment_kind,ordinal)` with exact intervals/strand | te-tracks gene child; geometry proposal, `C/gene_child_consult.md:43–59` |
| `gene_child_snapshot`; `record_context`; `context_block`; `context_boundary_tie`; `context_status`; `record_gene_distance` | Child snapshot ID = child BUILD_ID, parent CATALOG/BUILD and annotation/policy pins; `(child,R,transcript_key)`; `(pair,kind,ordinal)` exact overlap; `(pair,landmark_kind,position)` ties; `(child,R)` roll-up; `(child,R,gene_key)` distance/tie | te-tracks; pair reasons, signed TSS/TES distances, strand, exon/intron/UTR bp, per-pair status; separate gene-body distance, `docs/DECISIONS.md:34–44,96–109`; `C/gene_child_consult.md:45–51` |
| `instance_block`; `record_window`; `ltr_internal_pair`; `record_divergence_bin` | `(view_id,I,strand,block_no)`; `(view_id,R)` with N/tolerance/validity; `(view_id,ltr_R,internal_R)` with gap/orientation/status; `(bin_scheme,R)` | te-tracks later geometry; view IDs pin parameters/universe/build and block membership, `docs/DECISIONS.md:124–133` |
| `condition`; `animal`; `sample_animal`; `label_crosswalk` | `condition_key`; `(cohort_id,MouseID)`; `(dataset,library,animal)` known sample membership; `(crosswalk_id,dataset,label_version,label_id)` → harmonized label/status | integration; pooled membership conveys no per-nucleus animal assignment, `A:35–58` |
| `library`; `cell`; `cell_group`; `group_member` | `(dataset,library)` chemistry/tissue/condition/resolution; C with paired-cell mapping/QC; `group_id` library, nullable MouseID, condition, label version/level/cluster ID, roster digest; `(group_id,cell_id)` | dataset; cluster and cell-type labels are versioned annotations, `D/02_next_session_agenda.md:44–49,69–73` |
| `estimator_run`; `matrix_binding`; `measurement_domain` | `run_id` complete recipe/input provenance; `matrix_id` run, registration and full four-field key, channel/unit, assigned/reported levels; `(run_id,domain_id)` tested feature/cell sets and status | dataset; `docs/DECISIONS.md:137–163`; `D/01_consult_codex.md:198–202` |
| `te_feature_registration` | `(matrix_id,source_feature_id)` with source axis ordinal, emitted `feature_id`, registration ID, transformation digest/status; preserve gene features separately in joint matrices | dataset; `docs/DECISIONS.md:59–61`; `docs/OUTPUTS.md:472–484` |
| `rna_cell_count`; `group_counts`; `group_exposure` | `(matrix_id,feature_id,cell_id)` sparse molecules; `(matrix_id,feature_id,group_id)` float count; `(matrix_id,group_id)` library denominator, eligible-cell count and status | dataset; selected SQL slices over sparse matrices; independent runs/channels stay separate, `C/loci_gtf_consult.md:57–59,145–149` |
| `gene_expression` | `(gene_matrix_id,gene_key,group_id)` raw counts, eligible/detected cells and normalization provenance; gene key pins annotation, matrix manifest pins source cell axis | dataset; projects existing gene matrices for TF/host-expression evidence, `D/01_consult_codex.md:176–192`; `C/loci_gtf_consult.md:145` |
| `molecule_support`; `rna_region_cell` | `(run_id,cell_id,molecule_id,placement_id,block_no)` interval, strand, candidate/posterior, host competition; `(run_id,overlap_id,cell_id,support_policy)` unique/allocated molecule support in exact intersection | dataset; proposed regional evidence, with molecule identity and ambiguity dedup, `D/02_next_session_agenda.md:35–43`; Q5 |
| `peak`; `peak_record_overlaps` | P with immutable atlas/dictionary, half-open coordinates/admission; `(overlap_generation,P,R)` unique `overlap_id`, exact `start_0,end_0`, bp/fractions, te_build_id | dataset; geometry independent of counting, `C/field_practice_synthesis.md:213–224` |
| `peak_counts`; `record_cut_counts`; `intersection_cell_cuts`; `intersection_group_cuts` | `(run_id,P,group_id)`; `(run_id,R,group_id)`; `(run_id,overlap_id,cell_id)`; `(run_id,overlap_id,group_id)`; values, exposure and eligibility | dataset; peak estimator/unit retained; record/intersection cuts separately counted with shift, duplicate and overlap policies, `D/01_consult_codex.md:167,231–235` |
| `motif`; `motif_hit`; `motif_tf`; `motif_family` | Release-qualified motif ID/matrix digest; `(scan_id,P,motif_id,start_0,end_0,strand)` site; `(motif_id,annotation_pin,tf_gene_id,evidence_id)`; `(motif_id,family_vocab,family_id)` | dataset ATAC references/results; exact sites and many-to-many TF/complex/family bridges, `D/01_consult_codex.md:158–178` |
| `eregulon`; `eregulon_region`; `region_peak`; `grn_edge` | `(model_run_id,regulon_id)`; `(model_run_id,regulon_id,region_id)` exact coordinates; `(model_run_id,region_id,P)` intersection/mapping status; `(model_run_id,regulon_id,region_id,tf_gene_key,target_gene_key,group_id)` scores/signs/source | dataset; preserve paired/unpaired RNA source and v2 mapping accuracy, `D/01_consult_codex.md:170`; `D/02_next_session_agenda.md:63–76` |
| `reconstruction_candidate`; `candidate_member`; `candidate_evidence` | `(reconstruction_run_id,candidate_id)` kind/status/parameters/model-projection/coverage; `(candidate,R,role)`; `(candidate,evidence_id)` measurement/method/source/digest/threshold, nullable verdict | dataset analysis; candidates may share records; `docs/DECISIONS.md:111–133`; Q3 |
| `aggregate_set`; `feature_aggregate_member`; `effect`; `evidence_link` | Set ID pins partition/overlap semantics; `(set_id,matrix_id,feature_id,aggregate_id)` weight; `(model_id,contrast,feature,cell_label,tissue)` effect/SE/eligibility; `(integration_run,left_evidence,right_evidence,relation)` | integration; within-dataset aggregate production uses same contract; `A:35–58,71–79`; Q4–Q6 |

Every fact exposes `measurement_status`, `evidence_policy_id` and the relevant Q5 tier fields through its manifest-bound view. `not_computed`, `outside_universe`, `unsupported` and `failed` remain distinct from measured zero. Positive-only motif/count tables have declared tested domains; zero-completion is valid only within them (`D/02_next_session_agenda.md:50–52`; `D/01_consult_codex.md:170,198`). The phase-9 convenience `taxonomy_dfam.tsv` can coexist with normalized models/parts/clades; SQL should read ordered, keyed bridge rows rather than zip semicolon strings by position (`P/19_phase9_acceptance_park.md:19–25`).

Five examples follow. SQL 1 was run against B as `records` (M2). SQL 2–5 specify future contracts and were not executed against absent dataset products. Parameters are bound values. A release loader selects exactly one generation of each relation, validates shared catalog/atlas/annotation pins, and exposes the abbreviated views; SQL 3 pins RNA, cut, motif and TF-reference generations together. Zero-completion and exposure validation precede SQL 5.

**SQL 1 — genomic L1 viewport, using existing record columns.** The source LINE/L1 predicate is measured at `C/structural_views_consult.md:90`; a Dfam node selector later uses an EXISTS semijoin through model/lineage bridges.
```sql
SELECT rmsk_record_id, start_1-1 AS start_0, end_1 AS end_0, divergence_pct
FROM records
WHERE chrom='chr1' AND rmsk_class='LINE' AND rmsk_family='L1'
  AND start_1-1 < 3100000 AND end_1 > 3000000
ORDER BY start_1,end_1,rmsk_record_id;
```

**SQL 2 — conserving record-estimated RNA → subfamily rollup.** Restrict the selected matrix to record grain; `DISTINCT` collapses block support. Preflight requires exactly one name per measured feature and complete feature coverage (`docs/OUTPUTS.md:414–441`; `docs/DECISIONS.md:158–163`).
```sql
WITH fmap AS (
 SELECT DISTINCT b.matrix_id,m.emitted_feature_id AS feature_id,r.rmsk_name
 FROM matrix_binding b JOIN feature_member m
 ON m.registration_id=b.registration_id AND m.universe_name=b.universe_name
 AND m.variant=b.variant AND m.feature_level=b.feature_level AND m.key_grammar=b.key_grammar
 JOIN record r ON r.te_catalog_id=m.te_catalog_id AND r.rmsk_record_id=m.rmsk_record_id
 WHERE b.matrix_id=$matrix_id AND b.feature_level='record'
)
SELECT c.group_id,f.rmsk_name,SUM(c.count_value) AS molecules
FROM group_counts c JOIN fmap f USING(matrix_id,feature_id)
GROUP BY c.group_id,f.rmsk_name;
```

**SQL 3 — the owner's strict paired funnel.** Region-qualified unique RNA support and intersection cuts meet on the same nucleus; whole-peak counts remain a separate displayed channel. Motif containment applies to the exact TE–peak intersection. TF families are candidate annotations, and this result's condition tier is descriptive (`D/01_consult_codex.md:158–178,235`; Q5).
```sql
WITH paired AS (
 SELECT DISTINCT o.overlap_id,o.atlas_id,o.peak_id,o.te_catalog_id,o.rmsk_record_id,
   o.start_0,o.end_0,g.group_id,g.condition_key,a.cell_id
 FROM peak_record_overlaps o JOIN record r USING(te_catalog_id,rmsk_record_id)
 JOIN intersection_cell_cuts a USING(overlap_id)
 JOIN rna_region_cell u ON u.overlap_id=o.overlap_id AND u.cell_id=a.cell_id
 JOIN cell n ON n.cell_id=a.cell_id
 JOIN group_member gm ON gm.cell_id=a.cell_id JOIN cell_group g USING(group_id)
 WHERE r.rmsk_class='LINE' AND r.rmsk_family='L1'
   AND a.run_id=$cut_run AND u.run_id=$rna_run AND u.support_policy=$rna_policy
   AND a.cut_count>0 AND u.unique_locus_molecules>=1
   AND n.joint_eligible AND n.pairing_status='paired'
   AND a.measurement_status='measured' AND u.measurement_status='measured'
   AND g.dataset_id='14761-DM' AND g.label_version=$labels AND g.label_level=$level
   AND g.condition_key IN ('Young_Control','Old_Control')
)
SELECT q.overlap_id,q.group_id,q.condition_key,f.family_id,
 COUNT(DISTINCT q.cell_id) AS nuclei_with_both,
 'same_nucleus' AS pairing_level,'multiome_descriptive' AS replication_tier
FROM paired q JOIN motif_hit h USING(atlas_id,peak_id)
JOIN motif_family f USING(motif_id)
WHERE h.scan_id=$scan AND h.start_0>=q.start_0 AND h.end_0<=q.end_0
GROUP BY q.overlap_id,q.group_id,q.condition_key,f.family_id;
```

**SQL 4 — reconstructed L1 candidates with calibrated model coverage.** Candidate IDs are parameter/run-qualified; grouping counts hypotheses, and shared components require an explicit nonoverlapping selection before any insertion census (`docs/DECISIONS.md:111–133`; Q3).
```sql
SELECT candidate_id,rmsk_name,model_set_id,model_coverage_fraction,
       prefix_missing_bp,suffix_missing_bp,candidate_status
FROM reconstruction_candidate
WHERE reconstruction_run_id=$reconstruction_run AND candidate_kind='L1'
  AND model_projection_status='validated' AND component_consistency='supported'
  AND prefix_missing_bp<=$prefix_tolerance AND suffix_missing_bp<=$suffix_tolerance
  AND model_coverage_fraction>=$minimum_coverage;
```

**SQL 5 — animal/tissue lineage table ready for one model.** `feature_aggregate_member` must be a disjoint, weight-one partition for the selected set; a divergence partition additionally requires record-level inputs. Select compatible matrices with disjoint cell rosters and one estimator/channel; input groups partition each animal's cells at the chosen label level. `group_counts_complete` supplies measured zeros; technical libraries then sum within animal/tissue and retain their matrix provenance (`A:35–47`; Q4/Q6).
```sql
WITH totals AS (
 SELECT c.matrix_id,c.group_id,m.aggregate_id,SUM(c.count_value*m.weight) AS molecules
 FROM group_counts_complete c JOIN feature_aggregate_member m USING(matrix_id,feature_id)
 WHERE m.set_id=$aggregate_set AND c.matrix_id IN (SELECT unnest($matrix_ids))
 GROUP BY c.matrix_id,c.group_id,m.aggregate_id
)
SELECT g.dataset_id,g.cohort_id,g.MouseID,g.tissue,g.condition_key,g.label_id,
 t.aggregate_id,SUM(t.molecules) AS molecules,SUM(e.denominator_molecules) AS denominator,
 SUM(e.n_eligible_cells) AS n_cells,LIST(DISTINCT t.matrix_id) AS input_matrix_ids
FROM totals t JOIN cell_group g USING(group_id)
JOIN group_exposure e USING(matrix_id,group_id)
WHERE g.MouseID IS NOT NULL AND g.label_version=$labels AND g.label_level=$level
  AND e.measurement_status='measured' AND e.n_eligible_cells>0
GROUP BY g.dataset_id,g.cohort_id,g.MouseID,g.tissue,g.condition_key,g.label_id,t.aggregate_id;
```

## What te-tracks publishes next, in order

1. **Phase 9a: Dfam lineage/ranks/model parts/clades.** Serves lineage filters and evolutionary strata. Gate: verify offline digests and name coverage; derive per-rank statuses from paths/codes; preserve multiple clades, partial models and missing names; reconcile M1 against stale census anchors. Recommend normalized companions to the planned convenience table (`C/adr_rulings_2026-09-17.md:440–449`; `P/19_phase9_acceptance_park.md:16–29`).
2. **Phase 9a: `record_starsolo.gtf`, full matrix binding and consumer fixtures.** Serves separately counted records and honest estimator comparisons. Gate: distinct genes for same-name records, alias collisions, endpoints/gaps, gene–TE support, conservation and observed ambiguous allocation; parser and execution results remain separate. Pin the consumer environment and finish phase-9 acceptance/host publication (`P/19_phase9_acceptance_park.md:8–15,30–48`).
3. **10x annotation-matched child, then context relation in a later child snapshot.** Serves RNA-origin and TF/gene-context inspection. Verify actual ARC annotation digest/equivalence; preserve vM37 separately. Context gate: chr1 then full mm39 pair/block/tie cardinality, RSS/bytes, both-strand closest-base geometry, gene-body distance, exact subintervals and explicit incomplete status. Envelope is already ruled at 10 kb upstream/2 kb downstream (`docs/DECISIONS.md:34–44,96–109`; `C/gene_child_consult.md:43–59`).
4. **After host build, one structural batch: instance block union first.** Serves discontiguous source-group tracks and reconstruction seeds. Gate: preserve positive gaps, overlaps within each strand partition, member provenance and mixed-name/strand status; qualify a block-aware consumer (`C/structural_views_consult.md:61–84`; `C/adr_rulings_2026-09-17.md:306–310`).
5. **Record 5′ windows in that batch.** Serves L1-prefix visualization and a later whole-cell 5′ endpoint question. Gate: N/tolerance, invalid model extents, strand/end clipping and block registration; consumer separately verifies RNA-sense mate/end reconstruction. Model-to-genome base projection and promoter integrity remain additional evidence (`C/structural_views_consult.md:86–111`).
6. **LTR–internal candidate pairs in that batch.** Serves provirus/solo candidate inspection. Gate: compatible component-policy provenance, gap/orientation boundaries, alternative partners, complete unpaired status; biological reconstruction accuracy belongs to the consumer (`C/structural_views_consult.md:113–132`).
7. **Divergence-bin membership in that batch if a reusable view is needed.** Serves reproducible strata; direct queries over existing divergence serve the first pilot. Gate: disjoint endpoint conventions and record conservation; instance bins need a distinct rule. Publishing numeric-bin universes additionally requires the proposed predicate-schema extension (`C/structural_views_consult.md:134–152`).

## Measurements performed

Read-only input measurements; all shells exported `PYTHONDONTWRITEBYTECODE=1`. No build, quantifier, notebook, network request, install or git write ran. The owner's K documentation was read and `sene/` left untouched. Scratch was confined to the authorized directory and removed with Python `shutil`. Commands and outputs below are verbatim; M1 uses an in-memory DuckDB connection with spill confined to scratch. An initial probe used `CREATE VIEW … read_parquet(?)` and received `Binder Error: Unexpected prepared parameter. This type of statement can't be prepared!`; M1 uses the relation API instead.

M1 — catalog and strict Dfam matching:
```bash
export PYTHONDONTWRITEBYTECODE=1
python3 - <<'PY'
from pathlib import Path
from collections import Counter
import csv, gzip, hashlib, json, duckdb
B=Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build')
T=Path('docs/_internal/redesign-2026-09/taxonomy'); S=Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/schema-consult')
S.mkdir(parents=True,exist_ok=True)
z=(T/'dfam_interspersed_mm39_snapshot.json.gz').read_bytes(); raw=gzip.decompress(z); d=json.loads(raw)
p=json.loads((T/'dfam_interspersed_mm39_snapshot.provenance.json').read_text())
print('BUILD_ID', (B/'BUILD_ID').read_text().strip()); print('CATALOG_ID',(B/'CATALOG_ID').read_text().strip())
print('snapshot_sha256',hashlib.sha256(z).hexdigest(),'payload_verified',hashlib.sha256(raw).hexdigest()==p['payload_sha256'])
nodes=[]
def walk(n):
 nodes.append(n)
 for c in n.get('children',[]): walk(c)
walk(d['classes'])
print('Dfam',d['version']['dfam_version'],'names',len(d['summaries']),'models',len(d['records']),'nodes',len(nodes),'coded',sum(bool(n.get('wicker_equiv')) for n in nodes),'tree_equal',d['classes']==json.loads((T/'dfam_classes_20260917.json').read_text()))
chosen={n:([h for h in hs if h['name']==n] or [h for h in hs if h['name'] in {n+s for s in ('_5end','_orf2','_3end')}]) for n,hs in d['summaries'].items()}
status={n:('exact' if any(h['name']==n for h in hs) else 'part_model_set' if hs else 'missing') for n,hs in chosen.items()}
print('match_status',dict(Counter(status.values())))
parts={n:hs for n,hs in chosen.items() if status[n]=='part_model_set'}
print('part_sets',len(parts),'three_parts',sum(len(hs)==3 for hs in parts.values()),'partial',sum(len(hs)<3 for hs in parts.values()),'non_L1',[n for n,hs in parts.items() if not all(h.get('repeat_subtype_name')=='L1' for h in hs)])
print('missing',','.join(n for n,s in status.items() if s=='missing'))
print('full_metadata_missing',sum(h['accession'] not in d['records'] for hs in chosen.values() for h in hs),'part_lineage_clade_conflicts',sum(len({(h['classification'],tuple(h.get('clades',[]))) for h in hs})>1 for hs in parts.values()))
print('model_multi_clade',sum(len(r['clades'])>1 for r in d['records'].values()),'primate_branch_models',sum(any('Primates' in c.split(';') for c in r['clades']) for r in d['records'].values()))
print('L1MdA_I',[(h['name'],h['length'],[c.split(';')[-1] for c in h['clades']]) for h in chosen['L1MdA_I']])
c=duckdb.connect(':memory:'); c.execute('SET threads=2'); c.execute("SET memory_limit='1GB'"); c.execute('SET temp_directory=?',[str(S)])
c.read_parquet(str(B/'tables/rmsk_records.parquet')).create_view('r')
print('catalog_records_names_instances',c.execute('SELECT count(*),count(DISTINCT rmsk_name),count(DISTINCT rmsk_instance_id) FROM r').fetchone())
u=next(u for u in json.loads((B/'universes.json').read_text())['universes'] if u['name']=='interspersed'); classes=u['predicate']['class_in']
counts=dict(c.execute('SELECT rmsk_name,count(*) FROM r WHERE rmsk_class IN (SELECT unnest(?)) GROUP BY 1',[classes]).fetchall())
print('interspersed_records_names',sum(counts.values()),len(counts),'snapshot_names_equal',set(counts)==set(chosen))
rows=list(csv.DictReader((T/'dfam_census_1220_20260917.tsv').open(),delimiter='\t'))
print('census_record_sum',sum(int(r['record_count']) for r in rows),'census_undercoverage',sum(counts.values())-sum(int(r['record_count']) for r in rows))
print('actual_record_match_status',{s:sum(counts[n] for n in counts if status[n]==s) for s in ('exact','part_model_set','missing')})
print('L1_records_names_prefix1_invalid',c.execute("SELECT count(*),count(DISTINCT rmsk_name),count(*) FILTER (WHERE consensus_start_1=1),count(*) FILTER (WHERE consensus_start_1>consensus_end_1) FROM r WHERE rmsk_class='LINE' AND rmsk_family='L1'").fetchone())
print('duckdb',duckdb.__version__); c.close()
PY
```
```text
BUILD_ID 9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d
CATALOG_ID 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
snapshot_sha256 ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f payload_verified True
Dfam 4.0 names 1220 models 1263 nodes 300 coded 193 tree_equal True
match_status {'exact': 1047, 'missing': 26, 'part_model_set': 147}
part_sets 147 three_parts 30 partial 117 non_L1 ['L2a', 'L2b', 'L2c', 'L2d', 'L2d2', 'L3b']
missing ERVL-B4-int,ERVL-E-int,ERVL-int,ETnERV-int,ETnERV2-int,ETnERV3-int,HERV16-int,HERVL40-int,HERVL74-int,IAP-d-int,IAPA_MM-int,ID,L1M,L1P5,MERVK26-int,MERVL-int,MERVL_2A-int,MMERVK10C-int,MYSERV-int,MYSERV6-int,MurERV4-int,MurERV4_19-int,RNERVK23-int,RodERV21-int,Tigger1a_Art,Tigger1a_Mars
full_metadata_missing 0 part_lineage_clade_conflicts 0
model_multi_clade 9 primate_branch_models 33
L1MdA_I [('L1MdA_I_3end', 993, ['Mus musculus']), ('L1MdA_I_5end', 1328, ['Mus musculus']), ('L1MdA_I_orf2', 4681, ['Mus musculus'])]
catalog_records_names_instances (5320771, 18484, 4696900)
interspersed_records_names 3764949 1220 snapshot_names_equal True
census_record_sum 3760582 census_undercoverage 4367
actual_record_match_status {'exact': 2797852, 'part_model_set': 928528, 'missing': 38569}
L1_records_names_prefix1_invalid (877139, 149, 588, 2)
duckdb 1.5.5
```

M2 — branch, existing-table query and artifact presence:
```bash
export PYTHONDONTWRITEBYTECODE=1
git --no-optional-locks branch --show-current
python3 - <<'PY'
from pathlib import Path
import duckdb
b=Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build')
c=duckdb.connect(':memory:'); c.execute('SET threads=2'); c.read_parquet(str(b/'tables/rmsk_records.parquet')).create_view('records')
rows=c.execute("SELECT rmsk_record_id,start_1-1 AS start_0,end_1 AS end_0,divergence_pct FROM records WHERE chrom='chr1' AND rmsk_class='LINE' AND rmsk_family='L1' AND start_1-1<3100000 AND end_1>3000000 ORDER BY start_1,end_1,rmsk_record_id").fetchall()
print('SQL1_rows',len(rows),'first',rows[0]); print('new_profile_present',(b/'exports/gencode/interspersed/full/record_starsolo.gtf').exists(),'dfam_table_present',(b/'tables/taxonomy_dfam.tsv').exists())
print('consult_exists',Path('docs/_internal/redesign-2026-09/consults/unified_te_schema_consult.md').exists())
PY
```
```text
redesign-2026-09
SQL1_rows 36 first ('L1MdA_VI|chr1:3050294-3050775|+', 3050293, 3050775, 6.7)
new_profile_present False dfam_table_present False
consult_exists False
```

M3 — authorized scratch cleanup:
```bash
export PYTHONDONTWRITEBYTECODE=1
python3 - <<'PY'
from pathlib import Path
import shutil
p=Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/schema-consult')
shutil.rmtree(p)
print('scratch_exists',p.exists())
PY
```
```text
scratch_exists False
```

## Open for the owner

- Choose the first scientific contrast/cell-type focus and validation budget; recommend Young_Control versus Old_Control, with lineage/subfamily discovery in replicated whole-cell RNA and descriptive spatial corroboration in Multiome (`A:35–47`).
- Ratify the D2/D3 row-level evidence vocabulary, strict versus allocated RNA display modes and first browser prototype; recommend the strict intersection funnel plus a visibly separate allocated-support sensitivity. This consult supplies design choices; thresholds need the Q5 pilot.
- Set the reconstruction calibration panel and acceptable precision/recall; recommend L1-prefix/completeness first, then ERV configurations. The core's geometry-only boundary and later batched timing are already ruled (`C/adr_rulings_2026-09-17.md:306–310`).
- Settle phase-9 part-match scope: strict suffix matching gives 141 L1 and six L2/CR1 sets; an L1-only admission gives 1,047 exact/141 part/32 missing names. Recommend retaining all strict metadata matches with type and partial-coverage status, while qualifying whole-element reconstruction separately. Census record weights should be recomputed from the catalog (M1); Wicker vocabulary, Dfam-now timing and `te-consumers` ownership are already ruled (`C/adr_rulings_2026-09-17.md:433–449`).
