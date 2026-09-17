# Gene context material for the phase 8 ADR discussion (gathered 2026-09-16)

Evidence pack for the owner–orchestrator discussion on how te-tracks relates TE records to gene
annotation: the exon-subtracted counting SAF and the record-by-transcript context relation. Every
file:line below was read in this session; quotes are verbatim. Paragraphs marked **Synthesis** are
my reading; everything else reports the source. No build, test, quantifier, install, network or
git operation ran. This file is the only write.

Path prefixes: `T` = `/workspaces/Meta-Aging/01_modules/te-tracks`; `C` = `T/docs/_internal/redesign-2026-09/consults`;
`R` = `T/docs/_internal/redesign-2026-09/reviews`; `P` = `T/docs/_internal/_project/plans/2026-09-16_te-tracks-redesign`;
`D` = `/workspaces/Meta-Aging/14761-DM/docs/_internal/_project/plans/2026-09-11_codebase-topology`;
`G` = `/workspaces/Meta-Aging/01_modules/.ref/14839-DM-cGAS`; `K` = `G/01_modules/TE-RNAseq-toolkit`;
`L` = `/workspaces/Meta-Aging/14761-DM/01_modules/scio/skills`; `X` = `/workspaces/Meta-Aging/01_modules/.ref`;
`F` = `/data2/users/shared/refcache/mm39/mm39_20260911`.

## 1. Sources read

- te-tracks: `C/{FINAL_REPORT,ADR4_consult,ADR67_consult,ADR38_consult,A_consumer_contracts,SYNTHESIS,DECISION_STATE,codex_critique,owner_context_2026-09-15}.md`;
  `T/docs/DECISIONS.md`; `T/docs/OUTPUTS.md`; `T/docs/RELEASES.md`; `T/docs/PROVENANCE.md`; `T/README.md`; `T/config/mm39.env`;
  `P/{00_INDEX,01_decisions,02_orchestration,18_phase8_gene_child_seam}.md`; `R/{m2_divergent,m2_rulings,m5_rulings,p6_rulings}.md`;
  `T/docs/_internal/redesign-2026-09/audit/AUDIT.md`; `T/docs/_internal/_project/session.md`; `T/src/lib/*.py` (grep for exon and GTF).
- 14761-DM: `D/{00_INDEX,01_consult_codex,02_next_session_agenda}.md`; grep over `14761-DM/docs/_internal/` for
  `te_locus|gene_context|transposable|TE|exon` (hits limited to the three files above plus `_project/session.md:53`).
- Bulk pipeline: `K/docs/{METHODOLOGY,LIMITATIONS}.md`; `K/README.md`; `K/scripts/{runFeatureCounts,runFeatureCounts_TE_and_genes}.sh`;
  `K/docs/_internal/research/2026-06-16-TE-annotation-prep/{SAF_on_disk,_SYNTHESIS,cross_repo_overlap_handling}.md`;
  `K/docs/_internal/notes/2026-06-16-docs-provenance/annotation-prep.md`; `G/02_analysis/config/analysis_config.yaml`;
  `G/02_analysis/scripts/{00_annotate_data,20_te_qc_filter,21_te_de_model_fit,23_te_autonomy_sentinel}.R`; `G/02_analysis/helpers/te_helpers.R`;
  `L/te-reference-saf-build/{SKILL.md,scripts/build_te_saf.sh}`; `L/te-gene-featurecounts/SKILL.md`; `L/annotate-bulk-rnaseq-data/references/te-annotation.md`.
- Tools: `X/TEsingle/{TEsingle,TEtools/GeneIndex.py,TEtools/AlignmentIO.py,TEtools/Counters.py,README.rst}`;
  `X/TEtranscripts/{bin/TEtranscripts,bin/TEcount,TEToolkit/GeneFeatures.py,README.rst}`; `X/TElocal/{TElocal,TElocal_Toolkit/GeneFeatures.py,README.rst}`;
  `X/stellarscope/stellarscope/cmdopts/stellarscope_assign.yaml` and grep over the package; `X/irescue/irescue/*.py` and `README.md` (grep);
  `X/MATES/{build_reference.py,MATES/TE_quantifier_Intronic.py,MATES/scripts/Ref2csv.py,MATES/scripts/Intronic/*.py,README.md}`.
- Gene annotation: `F/{MANIFEST.json,gencode.vM37.primary_assembly.annotation.gtf.gz,GRCm39_Ensembl_rmsk_TE.gtf.gz}` (read-only census).

## 2. What each consumer needs from gene context

### 2a. 14761-DM, D2 (peak ledger) and D3 (paired/unpaired seam)

The codex-consult schema declares a required scalar on the TE dimension (`D/01_consult_codex.md:166`):
`te_locus_dim | te_release:str, locus_id:str, assembly:str, chrom:str, start:i64, end:i64, strand:str, rep_name:str, rep_family:str, rep_class:str, divergence_pct:f64?, gene_context:str`.
Every other field marked nullable carries `?`; `gene_context` carries none. The peak-side fact table is
`te | P, te_release, locus_id, overlap_bp, peak_fraction, locus_fraction, summit_in_te` (`:165`), with the
note "Raw rmsk fragments that belong to one reconstructed insertion need an explicit component relation."

The snRNA requirement, in the consult's words (`:229`): "For snRNA, a TE-overlapping intronic read can be
unspliced host-gene transcription. Keep exon-overlap, intronic, intergenic and strand context; provide a
conservative intergenic/no-exon sensitivity analysis without declaring every excluded intronic locus
biologically silent." The mappability pilot asks for callable fraction "stratified by divergence and genic
context" (`:239`). Layer 2 (`:235`): "For 'accessibility within TE sequence' count only cuts inside the
intersection or full TE locus." Nested copies (`:233`): "Summing locus counts will double-count nested copies."

D2's owner-added pressure (`D/02_next_session_agenda.md:35-43`): "TEs are transcription units positioned
relative to motif sites, promoters, TSSs — so satellites must carry INTERVALS, not peak-level booleans …
TE overlaps as sub-intervals (class/family/subfamily/locus_id, overlap bp, position in peak);
distance-to-nearest-TSS and SCREEN class on the spine … any sub-peak claim needs sub-peak grain. TE
transcription itself (TE-derived transcripts) is an RNA-side satellite keyed on TE locus, joined to peaks
only through the interval table." The unmeasured/measured-zero distinction is user-facing (`:50-52`).

D3 (`:54-76`) concerns the inference-source dimension for GRN edges and the two cell universes; its only
TE-adjacent statement is that the ledger "meets RNA only at gene/TF/regulon level" (`:71`). The P4 branch
plan (`D/00_INDEX.md:65-82`) names RepeatMasker as "another annotation registry" under the NEVER-GATE law,
`te.parquet` as "rmsk class/family/subfamily/locus overlaps" (`:96`), and a possible "te ledger keyed on rmsk
locus_id" (`:114`); the tooling pick is open (`:123`).

**Synthesis.** D2 needs three things from te-tracks: an interval-grain overlap (already served by the core
build's records), a TSS/TES/promoter geometry per record (the context relation), and a scalar or
small-vocabulary label whose absence is distinguishable from "intergenic". D3 needs nothing gene-context
specific. The one scalar D2 wrote down, `gene_context:str`, is the field the H3 finding says the child
cannot yet supply.

### 2b. The lab's bulk pipeline (14839-DM-cGAS and the toolkit)

Exon mask recipe (`L/te-reference-saf-build/scripts/build_te_saf.sh`): exon BED is every `exon` row of the
gene GTF regardless of transcript type or strand (`:96-97`: `$3=="exon"{print $1,$4-1,$5,".",".",$7}`);
the TE BED is the grouped SAF with `GeneID = Subfamily:Family:Class` (`:78-86`); both are `chr`-stripped
(`:103-106`); subtraction is `bedtools subtract -a te_grouped.bed -b exons.bed` with no `-s` (`:115`), then
`bedtools intersect … -u | wc -l` must be 0 (`:116-120`), then the SAF is rebuilt with the GeneID carried
through every surviving piece (`:123-124`). The header warns (`:24-26`) that a contig-name mismatch
"silently yields zero overlap".

Counting driver (`K/scripts/runFeatureCounts_TE_and_genes.sh`): TE pass `featureCounts -M -F SAF -a "$TE_SAF"
-s 0 -p --countReadPairs -B -C` (`:117-123`); optional sense/antisense passes at `-s 2` and `-s 1` for a
reverse library (`:143-158`); gene pass through `runFeatureCounts.sh … -f exon -g gene_id -p yes` on the gene
GTF, unique-only (`:170-178`); row-bind of the two matrices (`:185-187`). The example gene GTF is
`gencode.vM37.primary_assembly.annotation.filtered.gtf` (`:15`, `:54`); the example SAF is
`GRCm39_rmsk_TE_GROUPED_all_noExon.saf` (`:16`).

The cGAS dataset consumes exactly this (`G/02_analysis/config/analysis_config.yaml:694-697`): genes
"78,317 genes, -s2, unique-only (no -M)"; TE sense "-s2, -M Random-One"; TE antisense "-s1, -M Random-One";
`te_id_format: "subfamily:family:class"` (`:54`); `combined_te_channel: "sense"` (`:55`). Stage 00 states the
kernel rule (`G/02_analysis/scripts/00_annotate_data.R:22-24`): "gene rows are unique-only (no -M), TE rows
are -M Random-One. The combined object is for within-feature-type DE only".

What the toolkit says the mask does (`K/docs/METHODOLOGY.md:168`): "This toolkit assumes you have
subtracted exon regions from the TE SAF … This ensures no read is double-counted." And (`:183`): "Exon
subtraction is double-counting hygiene, not autonomy isolation … Intronic TEs are not exonic, so they remain
in the SAF and still catch host read-through. Isolating the autonomous-candidate signal — intergenic vs
intronic — is genic-context stratification (Rung 2 …), which the field handles by labelling TEs by context
(e.g. TE-Seq's Exonic/Intronic/Intergenic), not by carving the annotation."

What the bulk side wants next (`K/docs/LIMITATIONS.md:30-31`): "The grouped SAF carries no genic context
(intergenic / intronic / adjacent) and no locus identity … Those axes were deliberately thrown away at
SAF-build time." Rung 2 (`:130`): "tag each TE copy by its genic context — intergenic, intronic, or
gene-adjacent (treat a copy within ~10 kb of a gene as adjacent, and require ≥20 kb from any gene for a
clean intergenic set). Then re-count the same alignments through the tagged annotation." Known
non-resolutions (`:135-137`): young families, "interferon-inducible enhancer-RNA LTRs", "distal read-through".
Stage 23 declares the autonomy call out of scope pending "Rung 2 (genic-context-stratified SAF + intergenic
survival)" (`G/02_analysis/scripts/23_te_autonomy_sentinel.R:14-16`).

Measured on the delivered SAF (`K/docs/_internal/research/2026-06-16-TE-annotation-prep/SAF_on_disk.md`):
3,799,629 rows before and 3,717,740 after subtraction; 26,503,064 bp removed (2.363%); 0 residual exon
overlap; of the retained intervals, 2,029,692 (54.59%; 44.71% of bp) overlap a `gene` body and 1,688,048
(45.41%; 55.29% of bp) overlap none. The audit also records that the recipe-named `…filtered.gtf` "has no
`gene` feature rows" and that its exon count equals the unfiltered GTF's 1,298,921.

The toolkit's survey of four reference tools (`…/cross_repo_overlap_handling.md:10`): "not one of them does
exon-subtraction of the TE annotation"; TEtranscripts and atena resolve overlap at read assignment; SQuIRE
and TE-Seq run separate engines; TE-Seq labels every locus Exonic/Intronic/Intergenic and stratifies DE on
the label (`:33-47`).

**Synthesis.** The bulk consumer needs two gene-dependent products with one pinned GTF: the exon-subtracted
SAF as counting support, and a per-record genic-context label (with a distance-to-gene parameter) to build
a Rung-2 stratified SAF. Its gene pass counts `-t exon` over every exon row of the whole GTF, so any TE mask
narrower than "all exon rows" reintroduces double-counting against exactly the intervals the gene pass
counts. The lab has already computed intronic/intergenic by hand once, against `gene` rows with no
distance window; the child can make that computation reproducible.

### 2c. Each TE counting tool

| Tool | Gene handling (file:line) | Gene/TE read resolution |
|---|---|---|
| TEsingle 1.0 | Gene GTF indexed as `transcript` rows keyed by `gene_id`: `X/TEsingle/TEsingle:107` prints "Processing genes as full-length transcripts."; `:112` `GeneFeatures(args.gtffile, args.stranded, "transcript", "gene_id")`; `TEtools/GeneIndex.py:166-185` collects `(start, end)` per feature row, `:205-224` builds interval trees, so gene support spans introns. `--stranded` default `forward` (`TEsingle:83-87`). | Each read gets `(genes, tes)` (`TEtools/AlignmentIO.py:74-76`). An anchored UMI with both gene and TE hits sets category 4 and is split by a global `te_frac` (`TEtools/Counters.py:126-181`, `:36-45`); an intronic TE read therefore competes with its host gene. |
| TEtranscripts 2.2.4 | Gene GTF indexed as `exon` rows: `X/TEtranscripts/bin/TEtranscripts:764` `GeneFeatures(args.gtffile, args.stranded, "exon", "gene_id")`. `--stranded` default `no` (`:57`); `--mode uniq|multi`, default `multi` (`:61-63`). | `:388-402`: a multi-read is "prior to TE", a unique read "prior to gene"; a read hitting several genes goes to `leftOver_gene` and is split by current gene abundance (`:481-520`). Intronic TE reads never touch an exon-only gene index, so they fall to the TE. |
| TElocal 1.1.3 | Same exon-only gene index: `X/TElocal/TElocal:605` `GeneFeatures(args.gtffile, "exon", "gene_id")`; `--GTF` required (`:109`); TE input is a `.locInd` (`:111-112`); `--mode uniq|multi` (`:117-119`); `--stranded` default `no` (`:113`). | Identical priority logic (`:401-413`, `:438-441`). |
| Stellarscope 1.5 | No gene input. Annotation options are `--attribute` (default `locus`) and `--feature_type` (default `exon`) on one GTF (`X/stellarscope/stellarscope/cmdopts/stellarscope_assign.yaml:40-51`); the package grep for "gene" returns only "Generate" strings. | Competition is among TE features only. |
| IRescue 1.2.0 | No gene input. The only mentions are a help string "STARSolo or your gene expression quantifier of choice" (`X/irescue/irescue/main.py:80`) and README advice to reuse gene-derived whitelists (`README.md:132`). | None. |
| MATES 0.1.8 | `build_reference.py:88-89` keeps `Feature == 'gene'` rows; "exclusive" reference removes whole TE records overlapping gene bodies, `b.subtract(a, A=True)` (`:127-135`), then clips records to `--cut_length` 1000 (`:142-150`); `--intronic` (`:23`) builds a separate reference. `Ref2csv.py:9-10` pins mm10 and GENCODE vM10 for Mouse. | `TE_quantifier_Intronic.py:44` runs velocyto on a gene GTF; `scripts/Intronic/substract_unspliced.py:16-20` subtracts velocyto unspliced counts from unique intronic-TE counts per cell. |

**Synthesis.** Two gene models are in live use among the consumers: exon-only (TEtranscripts, TElocal,
featureCounts gene pass) and full transcript span (TEsingle; MATES gene bodies). Under the first, an
intronic TE read reaches the TE by default; under the second, it is contested with the host gene. A
context relation that carries exon, intron and transcript-span overlap separately lets an analysis state
which of the two models its counts were produced under, and lets the ledger compare them.

## 3. The current te-tracks position

Adopted text (`T/docs/DECISIONS.md:34-42`): "Gene-dependent views form a child build family
`te_<assembly>_gene` that pins its parent core build and one gene annotation. The first child view is the
exon-subtracted SAF: subtraction of the unstranded union of all annotated exons, with every retained piece
registered to its record. The record-by-transcript context relation follows in its own design session.
Exon subtraction guarantees exon-disjoint sequence support under the declared mask; molecule exclusivity
between gene and TE counts is a property of the joint counting run." Deferral (`:96-97`): "Transcript
context: a dedicated design session follows the phase 8 gene child seam."

Two build families (`C/FINAL_REPORT.md:143-150`): "`te_<assembly>_gene` holds the noExon view and the
later transcript-context relation, and its manifest pins `parent_core_build_id`. A GENCODE bump creates a
new child and leaves the core id, and every ATAC and peak-ledger key, untouched … The core build then
drops its GTF fetch." `T/config/mm39.env` now carries no gene GTF pin; `T/src/` has no exon or GTF reader
(the string `exon` appears once, as the GTF column 3 constant, `src/lib/build_exports.py:275`).

The ADR-4 unit preferred one build (`C/ADR4_consult.md:87-91`): "A satellite keyed only by
`(rmsk_records_md5, gene_annotation_md5)` is insufficient: promoter widths, transcript selection, alias
normalization, and schema/algorithm semantics can change with both inputs held constant." The orchestrator
resolved for two families with the child pinning its parent (`C/FINAL_REPORT.md:238`).

Mask policy as drafted (`C/FINAL_REPORT.md:100-102`): "The mask is the union of all exons of all
transcripts, both strands. Each surviving piece registers to its parent record with piece index and status
(unchanged, trimmed, split, fully subtracted). Retained plus removed equals original length." ADR-38
(`C/ADR38_consult.md:25`): "A differently stranded or transcript-filtered mask is a separately named view."

Phase 8 draft (`P/18_phase8_gene_child_seam.md:14-15`): `config/mm39_gene.env` with `PARENT_FAMILY=te_mm39`,
GENCODE vM37 primary assembly GTF, `GENE_GTF_MD5=702e27a8727db66cd23e9f66f5aa1d38`,
`EXON_MASK_POLICY=all_exons_unstranded_union_v1`. Deliverables (`:18-24`): SAFs in three namespaces, pieces
registered with `block_start_1`, `block_end_1` (milestone 5 ruling A1, `R/m5_rulings.md:26-28`), the child
exporter taking "universe, variant and block bounds as explicit inputs" and writing its own inventory
(ruling A2, `:29-35`), `tables/exon_subtraction_status.tsv`. Acceptance anchor (`:26-29`): 3,717,740 records
retaining a piece under `compat_tetranscripts_mm39`, "to be re-measured". The entry condition (`:5-11`) names
the consult questions: one child per pin or many views; mask, registration and context relation; combined-mode
SAF needs; the child exporter's explicit inputs; "a pinned alias and length source for child preflight, since
the parent's `contig_aliases.tsv` sits beside the parent build" (also `R/p6_rulings.md:80-82`).

The H3 warning (`R/m2_divergent.md:24-32`): "The nearest shipped field is `exon_subtraction_status.tsv`
(`unchanged | trimmed | split | fully_subtracted`). Failure: a record wholly inside an intron reads
`unchanged`, exactly like an intergenic record, so `gene_context` populated from that table labels every
intronic TE intergenic — the one distinction snRNA needs". Ruling (`R/m2_rulings.md:95-97`):
"`gene_context` for the 14761 ledger waits for the transcript-context design session, and D2 populates
nothing from the status table." The plan records the same (`P/18_phase8_gene_child_seam.md:39-42`).

The corrected exclusivity claim (`C/ADR4_consult.md:61`): "A paired-end molecule with one aligned block in a
gene exon and another in retained TE sequence can enter separate gene and TE runs. The lab driver executes
those runs separately and row-binds their matrices … TEsingle indexes `transcript` rows … so its gene
support includes introns. The precise reference guarantee is exon-disjoint sequence support under the
declared mask." `C/FINAL_REPORT.md:103-107` adopts it; `T/README.md:140` and `T/docs/OUTPUTS.md:586-587` carry it.

The context relation as drafted (`C/ADR4_consult.md:13-22`): transcript reference; transcript geometry
(`exon`, `intron`, `promoter` segments with `promoter_policy_id`); record–transcript context with
`relation_flags`, `relative_strand`, `body_overlap_bp`, `exon_overlap_bp`, `intron_overlap_bp`,
`promoter_overlap_bp`, `tss_signed_bp`, `tes_signed_bp`, `nearest_exon_boundary_bp`; exact intersections;
boundary ties; per-record `context_status`. Sparse: "include every body overlap, every promoter overlap, and
every same-contig transcript tied for the globally nearest TSS, TES, or exon boundary." Distance rule (`:26`):
"choose the closest record base `q=min(max(p,a),b)` and report `s*(q-p)`. This yields zero when the record
covers the landmark, negative upstream, positive downstream." Promoter (`:28`): bases with
`-U <= s*(x-tss1) <= D`, both parameters stored. "The extra landmark ADR-4 misses is TES" (`:30`).
`C/SYNTHESIS.md:180-185` and `C/codex_critique.md:50` state the same principle: "Absence before that stage
means uncomputed, not intergenic. Remove the ledger's premature required scalar `gene_context`".

Owner intent (`C/owner_context_2026-09-15.md:23`): "Separate TE-associated RNA from evidence of autonomous
transcription"; `:26`: ATAC counts "over TE intersections, TE sequence, and defensible promoter regions".
Orchestration (`P/02_orchestration.md:72-74`): "candidate ADRs are drafted for that discussion and land in
`docs/DECISIONS.md` only by the owner's ruling."

## 4. The pinned gene annotation (measured in this session, read-only)

`F/MANIFEST.json`: `gene_annotation: "GENCODE vM37"`, GTF md5 `702e27a8727db66cd23e9f66f5aa1d38` (equals the
phase 8 pin and `AUDIT.md:23`), TE GTF md5 `1d6770be131fc1b47402a633f4401cbd`, GTF contigs "chr-prefixed",
TE GTF "unprefixed". GTF header: "version M37 (Ensembl 114)", date 2025-01-19.

Feature rows: gene 78,317; transcript 278,369; exon 1,298,921; CDS 522,521; UTR 186,133; start_codon 59,738;
stop_codon 55,494; Selenocysteine 64. Vocabulary: 37 `gene_type` values (lncRNA 32,897; protein_coding
21,807; processed_pseudogene 9,317; TEC 3,219 …) and 43 `transcript_type` values (lncRNA 152,152;
protein_coding 58,686; retained_intron 22,064; protein_coding_CDS_not_defined 14,273; nonsense_mediated_decay
7,247 …). Tags on transcripts: `Ensembl_canonical` 78,317 (one per gene), `basic` 127,903, `CCDS` 32,962,
`CAGE_supported_TSS` 1,490; `MANE_Select` 0. Contigs with annotation: 38 (chr1–19, chrX, chrY, chrM and 16
GenBank-named scaffolds `GL4562xx.1`/`JH5842xx.1`). The RepeatMasker catalog spans 59 contigs (`AUDIT.md:26`)
and the FASTA 61 (`AUDIT.md:139-147`), so at least 21 record-bearing contigs carry no gene annotation.

Exon rows by transcript type: protein_coding 528,434; lncRNA 510,649; retained_intron 96,114;
nonsense_mediated_decay 67,719; protein_coding_CDS_not_defined 63,964. Genomic union of exon intervals
(0-based merge, all contigs): all exon rows 160,549,642 bp; `basic`-tagged 132,600,517 bp;
`Ensembl_canonical` 112,655,476 bp; protein_coding transcripts 75,875,592 bp. Gene-body union 1,488,096,243 bp.

**Synthesis.** A protein-coding-only mask retains ~85 Mb of lncRNA, retained-intron and NMD exon sequence
inside the TE counting support; a `basic`-only mask retains ~28 Mb. The lab's gene pass counts every exon
row, so those retained bases would be counted twice. The 21+ contigs without annotation make the
"outside annotation scope" status a real row set rather than an edge case.

## 5. Open design questions for the owner

1. **One child per gene annotation pin, or one child with many views.** Sources: `C/FINAL_REPORT.md:143-150`
   and `C/ADR67_consult.md:76-99` (child per pin; `parent_core_build_id`); `C/ADR4_consult.md:87-91` (policy
   must be in the identity, two md5s under-specify); `P/18_phase8_gene_child_seam.md:34-37` ("a child build
   per gene annotation pin is the mechanism, the policy for choosing and reconciling them is the open
   question"). Sub-question: does one child hold both the SAF and the context relation, or are they two
   children on one pin?
2. **Exon mask policy.** Drafted: all `exon` rows, all transcript types, both strands. Alternatives measured
   in §4. Sources: `build_te_saf.sh:96-97,115`; `C/ADR38_consult.md:25`; `K/docs/METHODOLOGY.md:168`. Related:
   whether a minimum retained block length exists (`C/ADR67_consult.md:99` lists it as a field to record).
3. **Piece registration.** Decided at milestone 5 (block columns in the key, `R/m5_rulings.md:26-28`); open is
   whether `exon_subtraction_status` stays a separate table or becomes columns of the context relation's
   per-record status row (H3 says the two answer different questions).
4. **Context relation geometry.** Landmarks TSS and TES (`C/ADR4_consult.md:26-30`); signed genomic distances
   with the closest-base rule; promoter window as stored coordinates plus `(U, D)` parameters versus a fixed
   field; isoform handling (all isoforms with ties versus `Ensembl_canonical`/`basic` selection; `MANE_Select`
   is absent in vM37); spliced versus genomic distance; per-record status `evaluated | contig_outside_annotation |
   unsupported_structure | not_computed`; and whether the bulk Rung-2 adjacency window (10 kb, 20 kb;
   `K/docs/LIMITATIONS.md:130`) is a te-tracks parameter or a consumer derivation from signed distances.
5. **Where `gene_context` is computed.** te-tracks child (one relation; consumers derive labels) versus
   consumer (each project against its own counting GTF). Sources: `D/01_consult_codex.md:166` (D2 wants a
   scalar); `C/SYNTHESIS.md:180-185` and `C/codex_critique.md:50` (a scalar cannot represent isoform
   disagreement); `K/docs/LIMITATIONS.md:130` and `SAF_on_disk.md` (the lab computed it ad hoc once);
   `P/18_phase8_gene_child_seam.md:34-37` (bulk datasets carry their own GTF; 10x references may differ).
6. **The child's own preflight alias source.** Preflight walks up from the export path to the nearest
   `tables/contig_aliases.tsv` (`T/docs/OUTPUTS.md:561-562`); the child directory has none
   (`R/p6_rulings.md:80-82`). Copy, pin by digest, or symlink; and how GTF contig names (chr-prefixed plus
   GenBank scaffolds, the `gencode` namespace) map into the canonical namespace without prefix stripping
   (`build_te_saf.sh:24-26`).
7. **GENCODE bump propagation.** New child `BUILD_ID`, parent untouched (`C/FINAL_REPORT.md:143-150`); the
   ledger keys records on `te_catalog_id` (`T/docs/DECISIONS.md:70-72`). Open: does the 14761 ledger hold
   `gene_child_build_id` on the context satellite only, and what the reconciliation rule is when a consumer's
   counting GTF differs from the child's pin (`C/ADR4_consult.md:96`: run metadata records "the actual
   gene-counting annotation/filter, gene feature type").

## 6. Candidate ADR statements — for discussion; none is adopted

**G1. One child per (parent core build, gene annotation pin, gene policy); SAF and context share it.**
`te_<assembly>_gene` pins `parent_build_id`, `parent_catalog_id`, the GTF digest and one policy id covering
the exon mask and the context parameters; the exon-subtracted SAF and the record-by-transcript relation are
two tables of that one child. A GTF or policy revision mints a new child and leaves the parent, the peak
ledger keys and every ATAC join untouched. Rests on `C/FINAL_REPORT.md:143-150`, `C/ADR4_consult.md:87-91`,
`C/ADR67_consult.md:76-99`. Prevents a SAF and a context table built from different GENCODE releases
disagreeing about which bases are exonic while a consumer joins them as one reference.

**G2. The counting mask is the unstranded union of every `exon` row of the pinned GTF, named
`all_exons_unstranded_union_v1`; narrower masks are separately named variants.** Acceptance reproduces the
lab's 3,717,740 retained records under `compat_tetranscripts_mm39` and asserts zero residual overlap and
`retained_bp + removed_bp = length_bp` per record. Rests on `build_te_saf.sh:96-97,115-120`,
`K/scripts/runFeatureCounts_TE_and_genes.sh:170-178` (the gene pass counts `-t exon` over the same rows),
`C/ADR38_consult.md:25`, and the §4 measurement (a protein-coding mask leaves ~85 Mb of counted exon
sequence in the TE support). Prevents double-counting between the gene pass and the TE pass on exactly the
lncRNA, retained-intron and NMD exons the gene pass counts.

**G3. The context relation is sparse record × transcript plus one status row per record; any scalar
`gene_context` is a named, versioned derivation from it, computed by the consumer or shipped as a
documented convenience view.** The status row distinguishes `evaluated`, `contig_outside_annotation`,
`unsupported_structure` and `not_computed`; `exon_subtraction_status` remains a counting-support table.
Rests on `C/ADR4_consult.md:13-24`, `C/SYNTHESIS.md:180-185`, `C/codex_critique.md:50`, `R/m2_rulings.md:95-97`,
and the 21+ unannotated contigs in §4. Prevents a record exonic in one isoform and intronic in another
receiving one word, and `unchanged` being read as intergenic (H3).

**G4. Geometry is transcript-oriented, genomic and signed: TSS and TES landmarks per transcript, distance
zero when the record covers the landmark, negative upstream, positive downstream; relative strand
`same | opposite | unknown`; promoter bases stored as coordinates under a `promoter_policy_id` with
`(U, D)` recorded; all isoforms kept with ties preserved and `Ensembl_canonical` available as a flag.** Rests
on `C/ADR4_consult.md:26-30`, `D/02_next_session_agenda.md:35-43` (distance-to-TSS on the spine),
`C/owner_context_2026-09-15.md:26` ("defensible promoter regions"), the vM37 tag census (`MANE_Select`
absent; `Ensembl_canonical` one per gene). Prevents a 3' assay's signal at the TES being read against
TSS-only distances, and a promoter width being baked into a column name.

**G5. te-tracks computes the relation once against the child's pinned GTF; every consumer records the GTF
its own counting used and reconciles by digest.** The child manifest carries the GTF digest; a consumer
whose counting GTF differs states the mismatch in run metadata and derives labels from the child relation
regardless. The bulk Rung-2 SAF (intronic / adjacent / intergenic at 10 kb and 20 kb) is a consumer
derivation from `tss_signed_bp`, `tes_signed_bp` and `body_overlap_bp`. Rests on `K/docs/LIMITATIONS.md:30-31,130`,
`SAF_on_disk.md` (the split was computed once by hand), `P/18_phase8_gene_child_seam.md:34-37`,
`C/ADR4_consult.md:96`. Prevents three projects computing three incompatible genic-context labels from three
GTFs and the ledger joining them as one.

**G6. The child carries its own `tables/contig_aliases.tsv` and coverage report, copied from the parent by
digest and extended with `has_gene_annotation` per contig; GTF contigs map into the canonical namespace
through that table, and an unmapped GTF contig fails the build.** Rests on `R/p6_rulings.md:80-82`,
`T/docs/OUTPUTS.md:561-562`, `AUDIT.md:139-147` (GTF names are the `gencode` namespace), `build_te_saf.sh:24-26`.
Prevents an exon on `GL456210.1` never meeting a record on `chr1_GL456210v1_random`, which prefix stripping
yields silently.

## 7. Facts I could not verify

- The cGAS dataset's own `README.md` and `te_counting_record.md` are absent from the `.ref` checkout
  (`G/` holds `00_data/metabolomics/README.md` only); their quotes come second-hand from `SAF_on_disk.md`.
- The nf-core "filtered" gene GTF used for the cGAS gene pass: `SAF_on_disk.md` reports it lacks `gene` rows
  and has 1,298,921 exons; the filter rule itself is unrecorded here.
- Whether te-tracks' `compat_tetranscripts_mm39` membership plus this mask reproduces 3,717,740 (the plan
  marks it "to be re-measured", `P/18_phase8_gene_child_seam.md:26-29`).
- TE-Seq's `annotate_rtes.R` line citations come from the toolkit's research note; no TE-Seq checkout exists
  under `X/`.
- featureCounts behaviour for a fragment touching a gene exon in one run and a retained TE piece in another
  is inferred from the driver's two independent invocations; no counting was executed.
- The GTF version inside the 10x cellranger-arc reference used for 14761, and therefore whether it equals
  GENCODE vM37 (`P/18_phase8_gene_child_seam.md:34-37` flags the possibility of a difference).
- MATES `--intronic` semantics beyond the code read (`build_reference.py:23`, `TE_quantifier_Intronic.py:44`,
  `substract_unspliced.py:16-20`); the velocyto step was read from imports and README, never run.
- D3 carries no TE-annotation requirement in the sources read; if one exists elsewhere in 14761-DM it is
  outside the grep hits listed in §1.

## 8. Orchestrator verification (2026-09-16)

Spot checks of the cited lines returned the quoted text verbatim: the D2 `te_locus_dim` schema and
snRNA requirement (`D/01_consult_codex.md:166,229`), the exon-mask recipe and residual gate
(`build_te_saf.sh:96-97,115-120`), the toolkit limitations and Rung 2 window
(`K/docs/LIMITATIONS.md:30-31,130`), the methodology sentences (`K/docs/METHODOLOGY.md:168,183`), the
gene-model lines of TEsingle (`transcript`), TEtranscripts and TElocal (`exon`), the Stellarscope
option block, the MATES gene-body subtraction, H3 and its ruling, the ADR-4 distance rule, and the
`SAF_on_disk.md` counts. The GENCODE vM37 census in section 4 was recomputed from the refcache GTF
with an independent script and reproduced every figure: feature rows, 38 contigs, 43 transcript
types, the tag counts (`MANE_Select` absent), the exon rows by transcript type and the five
genomic unions (all exons 160,549,642 bp; `basic` 132,600,517; `Ensembl_canonical` 112,655,476;
protein-coding 75,875,592; gene bodies 1,488,096,243). The material is fit for the owner
discussion; section 7 lists what stays unverified.
