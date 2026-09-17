# Field practice synthesis: TE annotation, rungs, genic context and counting (orchestrator, 2026-09-16)

Answers the owner's questions in `thesis_2023_excerpts.md` ("The owner's questions to the programme") from
three inputs against te-tracks `8589873`: the codex consult `field_practice_consult.md` (gpt-6-astra, xhigh,
read-only), the bioinf review `../reviews/field_bioinf.md` and the divergent review
`../reviews/field_divergent.md`. Every number below that a reviewer or the consult measured was recomputed by
the orchestrator from the build at `_scratch/te-tracks-audit/refroot/te_mm39/build` (`BUILD_ID 9ddf3622…`,
`CATALOG_ID 90cc18be…`), from GENCODE vM37, from the `.ref` checkouts, or from the datasets' cellranger BAM
headers; the recomputation log is section 9. Rulings on each reviewer finding are in
`../reviews/field_rulings.md`. Recommendations are candidates for the owner; the ADR brief
`gene_context_adr_brief.md` carries them as decisions to rule.

Path shorthand: `X` = `/workspaces/Meta-Aging/01_modules/.ref`; `B` = the build directory above.

## 1. Where the field maps TEs

**Genome alignment with multimappers retained is the counting coordinate system.** Every counting tool in
the checkouts consumes genomic alignments and assigns reads to genomic TE intervals: TEtranscripts and TElocal
(`X/TEtranscripts/TEToolkit/TEindex.py`, `X/TElocal/TElocal_Toolkit/TEindex.py`), TEsingle
(`X/TEsingle/TEtools/AlignmentIO.py:13-81`), Stellarscope (`X/stellarscope/.../stellarscope_assign.yaml`),
IRescue (`X/irescue/irescue/map.py`), MATES (`X/MATES/build_reference.py`), scTE (`X/scTE/scTE/base.py`), and
the dissertation's STARsolo route. The alignment recipe that recurs is STAR with `outFilterMultimapNmax 100`
and `winAnchorMultimapNmax 100` or `150` (`thesis_2023_excerpts.md`, `X/TEsingle_Martirosyan_analysis_code/
TEsingle/run_STAR_TEsingle.sh:60`, `X/irescue/README.md`). Ambiguity between candidate loci is then resolved
after alignment, by EM over the retained alternatives.

**Consensus space is the curation and browsing coordinate system.** Dfam and RepeatMasker define a
subfamily by a consensus model; DfamTEBrowser renders a family's seed instances against that consensus
(`X/DfamTEBrowser/README.md`, `DfamLib/MultAlign.py`). The genome annotation te-tracks projects is the result
of that curation applied to mm39. No checkout counts RNA in consensus space.

**Transcriptome selective alignment** (Alevin, Alevin-fry with unspliced transcripts) is the dissertation's
comparator; it needs a pinned transcript target set and loses novel and chimeric TE transcripts
(`thesis_2023_excerpts.md`, "Single-cell counting caveats").

**What our BAMs carry.** The cellranger BAMs of all three datasets keep one alignment record per read: in a
gene-rich 10 Mb window of the 14616 sample BAM, 14.8% of records carry `NH>1` and none is flagged secondary,
although the run was configured `no-secondary,false` (section 9). The same holds for the 14761 GEX BAM (3.8%
`NH>1`, no secondaries). Every EM route therefore starts from a re-alignment that emits all alternatives
(`outSAMmultNmax -1`, the multimap parameters above). scTEfinder's `--outSAMmultNmax 1` recipe is the
opposite choice and forfeits EM (`sctefinder_scte_notes.md`).

## 2. Where the field separates classes, families and subfamilies

**Three RepeatMasker tokens carry the whole hierarchy in practice.** Every checkout derives class, family
and subfamily from `repClass`, `repFamily` and `repName` (TEtranscripts' `gene_id:family_id:class_id`,
TEsingle's four attributes, IRescue's `.out` parsing, MATES' `TE_Fam`). The dissertation's five rungs
(class, subclass, superfamily, family, subfamily) are a vocabulary the tools never materialize: the
superfamily rung survives only inside hyphenated family labels (`ERVL-MaLR`, `hAT-Charlie`, `TcMar-Tigger`)
and the Class I versus Class II distinction is absent from every output. The Dfam `classification` lineage is
the one machine-readable source of the missing rungs, and its depth varies by branch
(`Transposase;hAT;Tip100` against `Transposase;Tc1-Mariner;Tc2-group;Tigger`), so rank is a mapping policy
rather than a token position (consult Q1).

**Label surprises a consumer must know.** Measured from `B/tables/rmsk_taxonomy.tsv`:

| observation | records | names |
|---|---:|---:|
| mouse B1 and PB1 subfamilies carry `rmsk_family = Alu` | 558,808 | 15 |
| `ERVL-MaLR` is the largest LTR family; no family is spelled `MaLR` | 534,111 | 65 |
| DNA superfamilies appear only hyphenated: `hAT-Charlie`, `hAT-Tip100`, `TcMar-Tigger` | 105,223 / 13,741 / 27,962 | 80 / 54 / 57 |
| records with no class in the TE sense: `Unknown`, `Unspecified`, `DNA?` | 5,786 / 98 / 9 | |
| distinct names; multi-label names (two class/family pairs) | 18,484 names | 20 |

A filter for `SINE/B1` returns zero rows today. `docs/OUTPUTS.md` should say so beside `family.bed` and
`taxonomy_canonical` (bioinf F1, F2; consult Q1).

**Dfam as the rank source.** The pinned snapshot covers 20 of 18,484 names (6,517 records, all Class II
DNA); it is agreement evidence for the canonical taxonomy, and it carries no release identifier
(`tests/fixtures/taxonomy/dfam_snapshot.provenance.json`). A rank table for mm39 needs a full Dfam
admission: release pin, accession per name with alias reconciliation to the older library the source
RepeatMasker run used (`RepBase 20181026; Dfam_Consensus 20181026`), a named rank scheme, and explicit
states for missing, ambiguous and inapplicable names, prioritizing the 1,220 interspersed names. That is a
later core snapshot; the raw and canonical labels stay as they are (consult Q1; divergent M1, M9).

**The unit below subfamily is contested, and te-tracks measures why.** The field counts "loci" as
RepeatMasker records, while an insertion is often several records:

| fact, mm39 all records | value |
|---|---:|
| records / source instances | 5,320,771 / 4,696,900 |
| multi-record instances (2 to 22 records) / records in them | 445,649 / 1,069,520 |
| mixed-name instances in the interspersed selection / records | 30,569 / 95,830 |
| record pairs overlapping on the genome / records involved / bases | 237,686 / 429,440 (8.07%) / 9,190,866 |
| overlapping pairs whose records belong to different instances | 198,956 |
| interspersed median record length / share shorter than 90 bp | 160 bp / 17.6% |
| `rmsk_overlap_flag` true | 0 (the pinned source carries no `*` markers) |

LTR class alone: 843,753 instances, of which 17,947 hold both an `-int` and an LTR name, 103,526 hold
internal names only, and 722,280 hold LTR names only (583,277 of them single records). A rule "an LTR
without a same-instance internal is a solo LTR" would call 722,280 solo LTRs and would miss every provirus
whose flanking LTRs carry other instance ids (divergent H4; consult M3). The field's answer for ERVs is a
curated unit set (Telescope/Stellarscope references; "One code to find them all" for LTR–internal–LTR
assembly, bioinf F3), which is the structural stage already deferred in `docs/DECISIONS.md`.

## 3. Genic-context metadata the field uses

**In the counting tools, context is a gene model choice, never an output column.** TEtranscripts and
TElocal index genes by exon rows; TEsingle by full transcript spans (`X/TEsingle/TEsingle:112`); scTE's
`exclusive` mode deletes whole TE loci overlapping protein-coding exons and `nointron` deletes those inside
gene spans (`X/scTE/bin/scTE_build:65-87,129-208`); MATES removes TE records overlapping gene bodies or
requires intron containment (`X/MATES/build_reference.py:88-99,124-160`). None writes exon, intron,
intergenic or UTR labels for a TE. The dissertation's own pipeline intersects TE loci with gene spans
stranded and split-aware (`X/Thesis_2023/quantification_method/eqc_generation/scripts/annotate.sh:21-35`) and
also emits identities only.

**Where labels do exist.** cellranger tags every aligned read `RE:E|N|I` (exonic, intronic, intergenic)
against its own GTF: in the 14616 window 78% E, 20% N, 2.3% I; in the 14761 nuclei GEX window 39% E, 55%
N, 6.6% I (section 9). Peak annotators (ChIPseeker, HOMER) assign one nearest gene with a signed TSS
distance and a Promoter/Exon/UTR/Intron/Intergenic label. TE-Seq's Exonic/Intronic/Intergenic label is
known second-hand from the lab's toolkit notes (`gene_context_material.md`). Nothing in the field publishes a
TE-by-transcript relation with strand and geometry; the drafted relation (`gene_child_consult.md` Q5) is
more explicit than the field's practice, which is the reason to keep it sparse and evidence-preserving and
to let consumers derive the scalar label (brief C3, C5; bioinf verdict).

**UTR.** GENCODE vM37 has 186,133 generic `UTR` rows; strand plus each transcript's CDS bounds classify all
of them, 95,682 as 5′ and 90,451 as 3′, with zero unresolved. Unstranded, 10,247 records overlap a derived 5′
UTR and 46,588 a 3′ UTR. The relation should carry `utr5` and `utr3` flags, bases and segments per record ×
transcript, with a coding-boundary status, as a subset of exonic context (consult Q3, M4).

**Two additions the reviews justify.** Status per record × transcript pair with a per-record roll-up,
because one record evaluated against six isoforms otherwise reads either `evaluated` with a host dropped or
`unsupported_structure` with five good pairs discarded (divergent M5). Gene-body geometry beside transcript
geometry, because the two disagree for 2,073 records and flip 500 of the bulk 10 kb calls (brief C4; bioinf
F7).

## 4. The rungs of counting questions and what serves each

| rung | field practice | te-tracks today | missing |
|---|---|---|---|
| locus = RepeatMasker record | TEsingle, TElocal, Stellarscope `locus`, IRescue record BED, MATES, dissertation STARsolo | `record.bed`, `record.gtf`, registration `(record, *)` | a GTF with `gene_id` = record for STARsolo GeneFull (today `record.gtf` has `gene_id` = subfamily, the dissertation's "subfamily GTF") |
| insertion / instance | Stellarscope `instance_id`, IRescue instance mode; curated ERV and full-length L1 sets | `rmsk_instance_members`, `instance_id` in `record.gtf`, `(instance, instance_alias)` | a block-union view per instance preserving gaps and mixed-name status; TEsingle and TElocal append each GTF row as its own competitor, so an alias repeated on rows does not merge them |
| subfamily = `rmsk_name` | the common reporting rung; scTE/SoloTE metagenes count here directly | `subfamily.bed/.gtf/.saf`, `(subfamily, *)`, `rmsk_taxonomy.tsv` with `record_count` and `instance_count` | nothing; estimate at record then sum once per name, or count grouped features directly, and say which |
| family = canonical family | descriptive rollup | `family.bed`, `(family, family_bucket)`, `taxonomy_canonical` | none required |
| class = source `repClass` | descriptive rollup | `taxonomy_canonical.canonical_class` | a documented conserving rollup example; no class export |
| taxonomy triple | TEtranscripts key | `taxonomy_triple.saf`, `(taxonomy_triple, taxonomy_triple)` | spelling reconciliation against packaged GTFs (`ID4_.`/`ID4_v` over 25,263 records; divergent M3) |
| biological class, subclass, superfamily | Dfam lineage; Wicker vocabulary | none | the rank view of section 2 |

**Which counting the field uses.** Subfamily is the rung reported; locus-level estimation before aggregation
is the rung the accurate tools work at (TEsingle, Telescope/Stellarscope, MATES, TElocal, STARsolo EM). The
dissertation's benchmark found locus-specific methods ahead of subfamily metagene methods across the board,
including when locus results are aggregated to subfamily, and found metagene tools the weakest (bioinf F4).
The recommendation for all three RNA datasets is therefore: estimate at the record with multimappers
retained, report subfamily summaries as the principal comparison, and keep family and class as descriptive
rollups, each aggregation conserving the measured counts once per feature (consult Q2, Q4).

**The join rule needs its universe.** The registration is unique over eight columns including
`universe_name` (`docs/OUTPUTS.md:414-415`), while the binding sentence names only `(feature_level,
key_grammar)`. At `(record, rmsk_record_id)` the table holds 3,764,949 `interspersed` rows and 5,320,771
`all_rmsk` rows, so every interspersed record has two rows there and a join on the documented pair doubles
each count. The sentence must read `(universe_name, variant, feature_level, key_grammar)` and a join fixture
must prove it (divergent H1; consult Q4 "Conservation").

## 5. The three datasets

**Facts measured from the BAM headers and web summaries (section 9).** 14616 (cellranger 9.0.1) and 14782
(cellranger 10.0.0) share the chemistry `Single Cell 5' PE OCM v3`, the reference
`refdata-cellranger-GRCm39-2024-A` and `include-introns true`; their BAMs are fully paired (both cDNA mates
aligned as proper pairs). 14761 (cellranger-arc 2.1.0) used `refdata-cellranger-arc-GRCm39-2024-A` with
introns included; its GEX BAM is single-end (R2 only) and its ATAC BAM is paired. All three carry 61
`chr`-named contigs. 10x documents both 2024-A references as GENCODE vM32 filtered by biotype; that is
unverified on disk because the reference directories live on the sequencing core's machine. te-tracks pins
vM37, so the gene child and the counting GTF differ by five GENCODE releases whatever route is chosen; C5's
reconciliation rule applies. The divergent's M6 concern that spleen and lung were counted under different
gene references is answered: the reference is the same, the cellranger versions differ.

**Whole-cell 5′ PE OCM (14616 spleen, 14782 lung; 20 animals, 4 per condition, spleen–lung pairs).**

- The route with field support is TEsingle as the first consumer to qualify, with STARsolo GeneFull plus
  `soloMultiMappers EM` and a unique-only run as comparators, on a STARsolo re-alignment with the TE-tuned
  multimap parameters (consult Q2, Q7; bioinf F4). Both datasets have no written TE requirement today
  (divergent H7); the owner names the route and its grain before phase 8 closes.
- TEsingle 1.0 needs paired-end qualification before production: its reader groups records by read name and
  appends each mate as an alternative alignment with its own strand, and anchoring requires exactly one
  entry, so a proper pair changes anchoring and strand treatment (`X/TEsingle/TEtools/AlignmentIO.py:60-76`,
  `Counters.py:71-72`; verified by a probe BAM in the consult and by source reading here). Either a
  fragment-aware fix in a pinned fork or a declared single-mate route is required; the second forfeits paired
  evidence.
- Three further TEsingle behaviours to accept or correct: the UMI graph joins all Hamming-distance-1 UMIs of a
  cell into connected components without annotation constraint (`CellGrapher.py:4-39`); `te_frac` is anchored
  TE-only over anchored TE-only plus anchored gene-only (`Counters.py:36-41`); the TE EM ends in a hard argmax
  per molecule with first-index ties (`EM.py:30-36,114`). `tesingle_notes.md` carries these corrections.
- 5′ capture as promoter evidence is a testable advantage, unproven for this chemistry: the dissertation's
  disappointment was with the 10x v2 5′ kit. te-tracks can publish a strand-aware record-end window
  (`[a, min(b, a+N-1)]` on `+`, mirrored on `-`) with consensus-prefix eligibility; the consumer reconstructs
  each molecule's RNA-oriented 5′ end and asks whether it lies inside (consult Q5; bioinf F11). Plain
  interval overlap answers a different question.
- Promoter-intact filtering must be keyed on insertions with an evidence gate. Record-level `consensus_start_1
  = 1` keeps 588 L1 records (75 spanning ≥ 6 kb); instance-level reconstruction gives 583 at 1 and 2,221 at
  ≤ 10 (104 and 323 with ≥ 6 kb summed); at ≤ 100 there are 11,226 records and 11,095 instances. The young
  L1 subfamilies (L1MdA_I–VII, L1MdGf_I–II, L1MdTf_I–III) hold 70,628 records in 53,756 instances, 9,859 of
  them ≥ 6 kb summed, median divergence 2.1% against 19.3% for all L1. Row-implied consensus lengths vary
  within 145 of 149 L1 names (L1MdA_I 4,915 to 8,042), so "full length" is a per-subfamily structural
  definition, and HAL1 (about 2.5 kb) shows a whole-model match is not an autonomous L1 (consult M2;
  divergent H5).
- This is the arm that licenses TE-level hypothesis tests: four true biological replicates per condition and
  tissue pairing within animal. Design the analysis so a spleen or lung TE call replicates across the pair
  before it is a claim (bioinf F15).

**Multiome nuclei GEX (14761 spleen; one pooled library per condition, no replicates).**

- Intronic reads dominate (55% `RE:N` in the window), so full-span gene competition (GeneFull) is mandatory
  and the exon-subtracted SAF answers a bulk question only; the single-cell product is the context relation,
  with intron versus intergenic stratification and relative strand against the counting GTF (divergent H6;
  consult Q5). Passive intronic transcription remains undecidable from annotation; report it as a claim tier.
- The GEX BAM is single-end, which removes TEsingle's mate issue and leaves the UMI, tie and intronic
  ambiguity gates.
- Every condition contrast is a single-library contrast. Report descriptive effect sizes and use the arm to
  corroborate direction from the paired whole-cell arm; a TE-level p-value from this arm alone is
  indefensible (bioinf F15; divergent M8; consult Q5).

**Multiome ATAC (14761).**

- No vendored tool counts ATAC at TE-locus resolution; scTE's ATAC mode is subfamily-only. The record-keyed
  ledger over `all_rmsk/full/record.bed` fills a real gap (bioinf F13). Count Tn5 cut sites inside the TE or
  TE ∩ peak interval, as ArchR and chromVAR count insertions, and keep whole-peak accessibility separate.
- Overlapping records are the ledger's own problem: 8.07% of records overlap another and 198,956 of those
  pairs cross instances, while `rmsk_overlap_flag` is constant false. The ledger needs an explicit
  record-overlap relation or a deduplicating cut assignment; joining through the registration inherits
  instance membership only (divergent H3; bioinf F14).
- Keys: `(atlas_id, peak_id, te_catalog_id, rmsk_record_id)` with `te_build_id`, intersection coordinates and
  a counting-run id; context joins by child identity with a pending state until the relation ships (consult
  Q5; brief C5).

## 6. What still holds from the 2023 dissertation

Holds and is implemented: STAR genome alignment with multimappers, EM over loci, UMI handling that respects
multi-mapping, intron inclusion, locus features aggregated after estimation, the TE GTF grammar
(`gene_id` subfamily, `transcript_id` locus, `family_id`, `class_id`) that te-tracks' `record.gtf` emits and
TEsingle consumes unchanged, and the RepeatMasker class filter that equals `interspersed_plus_satellites`
exactly (3,802,177 records; `tesingle_notes.md`).

Superseded or qualified: the benchmark's top pick (Alevin-fry) is replaced by the author's own TEsingle;
the benchmark is human and simulated; the 5′-capture verdict rests on the v2 kit; the "future directions"
(promoter-intact filtering, solo LTRs, young/old tiers, TE transcriptome from long reads, cluster pooling,
EM sparsity) remain open and are the structural items te-tracks has deferred with their prerequisites
(consensus coordinates, divergence, instance ids) already in the catalog (consult Q6; divergent M10).

Unsolved by everyone: gene-overlapping TE reads. Every method including EM scored near zero on intronic TEs
in the benchmark; TEsingle's `te_frac` is a per-cell prior, not a resolution. te-tracks' guarantee stays
exon-disjoint sequence support; molecule exclusivity is a property of the joint counting run (bioinf F5;
divergent L3; `docs/DECISIONS.md`).

## 7. What the te-tracks programme changes now, later, and leaves to consumers

| when | change | prevents |
|---|---|---|
| phase 8 | child scope as planned (SAF, subtraction status, context `not_computed`); acceptance names 3,701,642 retained records and 3,717,740 blocks as prior measurements to remeasure on the selected parent; the design backlog records UTR flags, coding-boundary status, per-pair status with per-record roll-up | a block count read as a locus count; subtraction status read as intergenic |
| phase 9 docs | binding rule `(universe_name, variant, feature_level, key_grammar)` with a join fixture over both universes; label-surprise note (B1 under `Alu`, `ERVL-MaLR`, hyphenated DNA superfamilies, 5,893 class-less records); `rmsk_overlap_flag` documented as constant false for the mm39 source; a conserving class-rollup example; the RNA qualification limits (TEsingle paired input, UMI graph, hard ties; re-alignment required) in the parking handoff | doubled joins; zero-row filters; overlap read as handled; a parser pass read as a validated counter |
| phase 9 if the owner amends scope, else next core snapshot | `record_starsolo.gtf`: `gene_id = transcript_id = locus = record alias`, name and taxonomy as attributes, own contract and fixture (two records of one name become two genes) | STARsolo GeneFull counting 1,220 subfamilies where 3,764,949 loci were expected |
| later core snapshot | Dfam lineage/rank view pinned to a release; instance block-union view; strand-aware record-end windows with eligibility; divergence-bin universes with pinned thresholds | 20 DNA lookups presented as a hierarchy; fragments competing as separate loci; truncation boundaries called promoters; a median read as an age |
| later structural snapshot | curated ERV units (LTR–internal pairing with strand, order and distance rules), full-length and promoter evidence per insertion | 722,280 "solo LTRs"; 75 "promoter-intact" L1 records where the insertion answer is hundreds to thousands |
| later gene-child snapshot | the complete context relation after the chr1 then mm39 scaling gate | unannotated scaffolds or uncomputed context reading as intergenic in D2 |

Consumers own: chemistry-specific alignment and re-alignment, UMI correction, EM or hard assignment and tie
policy, cell pooling and fractional-count rounding (recorded per analysis run), read-end evidence,
mappability, ATAC cut counting and peak intersection, the scalar context label and its precedence,
normalization and inference. te-tracks owns registered intervals, identities and joins (`AGENTS.md`;
`docs/DECISIONS.md`).

## 8. Open for the owner

The ADR brief lists the decisions (C1 to C6 amended, C7 to C11 added). The owner's rulings settle: the RNA
route and grain for 14616 and 14782 and who qualifies TEsingle; whether phase 9 admits the STARsolo profile;
the binding-rule correction and its fixture; the Dfam admission scope and rank vocabulary; parameters only
after the named pilots (record-end N, consensus-prefix tolerance, promoter window U and D, label precedence);
and the reporting contract (animal-replicated, tissue-paired whole-cell claims; descriptive Multiome
integration; subfamily reporting with preserved locus evidence).

## 9. Measurements by the orchestrator

All read-only, `PYTHONDONTWRITEBYTECODE=1`, pandas and pyarrow over `B/tables/rmsk_records.parquet` and
`B/tables/rmsk_taxonomy.tsv`, pysam over the datasets' BAMs; scratch log
`_scratch/te-tracks-audit/field/orchestrator_measurements.txt`.

- Taxonomy: record and name counts of the table in section 2; distinct names 18,484 over 18,504 rows.
- Dfam fixture: 20 names, all present, 6,517 records.
- L1 (`LINE/L1`, 877,139 records, 610,410 instances, 149 names): `consensus_start_1 - 1 <= N` for N =
  0/10/50/100/500 gives 588/2,342/7,809/11,226/41,744 records over 583/2,314/7,753/11,095/40,368 instances,
  with both ends within N in 49/145/1,332/1,610/6,898 records; two rows have start > end. Record-level
  `consensus_start_1 = 1` with `length_bp >= 6000`: 75. Instance-level (min start over the instance's
  records) at 1 and at 10: 583 and 2,221, with summed length ≥ 6 kb in 104 and 323. Young L1 names: 70,628
  records, 53,756 instances, 9,859 instances ≥ 6 kb summed, 2,933 of those with min start ≤ 100.
  Divergence quantiles (10/50/90%): young L1 0.3/2.1/6.0, all L1 4.1/19.3/30.2, ERVK 6.8/18.1/30.2.
- LTR: 1,105,064 records, 843,753 instances; strict `-int` suffix 176,698 records; 25,055 LTR-named records
  in 17,947 instances share an instance with an internal; instance classes 17,947 both / 103,526 internal
  only / 722,280 LTR only (583,277 single-record).
- Instances, all records: 4,696,900; multi-record 445,649 holding 1,069,520. Record-record overlaps by a
  sweep per contig: 237,686 pairs, 429,440 records, 9,190,866 bp, 198,956 pairs across instances.
  `rmsk_overlap_flag` false for all 5,320,771. Interspersed median length 160 bp, 17.62% below 90 bp.
  `divergence_pct == 0` for 468,810 records; B1_Mus1 median 8.9 (5–95%: 4.1–21.8), B1_Mus2 7.5 (3.2–22.0),
  B3 23.1 (15.7–31.5).
- GENCODE vM37: 78,317 genes, 278,369 transcripts, 1,298,921 exons, 522,521 CDS, 186,133 UTR rows =
  95,682 5′ + 90,451 3′ (zero unresolved); records overlapping a 5′ UTR 10,247, a 3′ UTR 46,588.
- Registration: rows at `(record, rmsk_record_id)` by universe, `interspersed` 3,764,949 and `all_rmsk`
  5,320,771; the record `L1MdA_VI|chr1:3050294-3050775|+` appears once under each.
- Repository: no file under `docs/*.md`, `README.md`, `src/`, `tests/`, `config/` mentions STARsolo or
  cellranger; consumer fixtures write `consensus_start_1=1, consensus_end_1=length, consensus_left_bp=0`
  (`tests/lib/consumers.py:338`); `arc_3prime.bam` and `ocm_5prime_pe.bam` share one molecule list and
  differ in `paired` (`tests/lib/consumers.py:392-393`); `14616-DM/docs` and `14782-DM/docs` contain no file
  mentioning transposable elements, RepeatMasker, te-tracks or `te_locus`.
- TEsingle source: `AlignmentIO.py:60-76` (per-record append, per-record `is_reverse`, no mate pairing),
  `CellGrapher.py:4-39`, `EM.py:30-36,55-61,114`, `Counters.py:19-50,127-181,184-202`. Martirosyan builds the
  STAR index from the gene GTF alone (`setup_STAR_index.sh:92-96`) and passes the TE GTF to TEsingle
  (`run_STAR_TEsingle.sh:96`).
- Datasets: 14616 `sample_alignments.bam` header `cellranger-9.0.1`; web summary `Single Cell 5' PE OCM v3`,
  `refdata-cellranger-GRCm39-2024-A`, `include-introns,true`, `no-secondary,false`; first 200,000 records all
  paired and proper, tags `CB`, `UR`, `xf`, `RE`, `NH` on every record, `UB` on 190,836, `GX`/`GN` on
  183,287. 14782 header `10.0.0`, same chemistry and reference, all paired. 14761 GEX header
  `cellranger-arc-2.1.0`, `refdata-cellranger-arc-GRCm39-2024-A`, `Include introns True`, zero paired
  records; ATAC BAM paired. Window chr11:60–70 Mb: 14616 2,000,000 records, `NH` 1/2/3/4/5+ =
  1,703,862/239,606/38,484/14,222/3,826, zero secondary or supplementary, `RE` E/N/I =
  1,556,103/398,060/45,837; 14761 GEX 595,790 records, `NH>1` 22,573, `RE` E/N/I = 230,908/325,786/39,096.
- Republish from the clean tree: `BUILD_ID 9ddf3622…`, `verify-current exit 0`, `builder_git_sha 6bf9a22`,
  `dirty False`, peak RSS 5,983,178,752 bytes.
