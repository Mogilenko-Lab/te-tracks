# Open questions after phase 8: biology, premises, routes (orchestrator, 2026-09-17, later)

The owner asked, with phase 8 committed and phase 9a running, for a re-orientation in the biology behind the
questions still open, for the premises and pain points the programme is weighing, and for each question the
premise, the routes, their tradeoffs, implications and caveats. This file succeeds
`open_questions_premises_2026-09-17.md`, whose twelve items are ruled in rounds one to four of
`adr_rulings_2026-09-17.md`. Sources: the rulings file through its fifth round, `docs/DECISIONS.md` at
`393ca76`, the consults (`mask_policy_consult.md`, `loci_gtf_consult.md`, `structural_views_consult.md`,
`gene_child_consult.md`, `unified_te_schema_consult.md`), `field_practice_synthesis.md`, plan 19, and the
14761 agenda `plans/2026-09-11_codebase-topology/02_next_session_agenda.md`. Every number below was
recomputed by the orchestrator in an earlier record. Statements marked *general knowledge* come from the
field's literature and need a pinned source before they carry weight in a ruling. Nothing here is a ruling;
the recommendations are the orchestrator's.

## 1. The biology we stand on

**The hypothesis.** The programme reads transposable elements through derepression. With age the
heterochromatin that silences them relaxes; copies that still carry a working promoter transcribe; their RNA,
or the cDNA reverse transcription makes from it, reaches the innate sensors of the interferon axis.
Rapamycin and methionine restriction are the candidate suppressors, one through mTORC1 and one through the
methyl-donor supply that heterochromatin maintenance draws on (*general knowledge* as mechanism; the cohort
design is the record's). The claim the programme wants is about autonomous transcription from a TE's own
promoter, in named cell types, rising with age and moved back by treatment. The measurement sees
TE-associated RNA of every origin: a TE inside an intron carried by host pre-mRNA, a TE exonized into a host
transcript, a TE past a gene's end picked up by read-through, and a TE transcribed from its own LTR or 5′
UTR. The owner's standing instruction is to keep the two apart, and every open question below is a facet of
that instruction.

**What each arm can see.**

| arm | material | can support | cannot support |
|---|---|---|---|
| 14616 spleen and 14782 lung: whole-cell 5′ PE OCM v3; 20 animals, 4 per condition, spleen–lung pairs | cytoplasmic and nuclear RNA; both cDNA mates aligned; about one read in five intronic; molecule 5′ ends near the transcript start | animal-replicated tests; tissue pairing within animal; initiation evidence from 5′ ends once the RNA-sense mate is measured | same-cell chromatin |
| 14761 spleen Multiome GEX: 3′ nuclear, R2 only; one pooled library per condition; four conditions | nuclear RNA; more than half intronic | same-nucleus pairing with ATAC; direction-level corroboration | replication; initiation; the Rapa+MetR arm |
| 14761 ATAC | Tn5 cuts, peaks, motif sites, GRN edges | accessibility at TE intervals and TE–peak intersections in the same nucleus; TF candidates by motif | RNA origin |

**The units.** A record is one RepeatMasker alignment of a genome stretch to a consensus model. An instance is
RepeatMasker's grouping hypothesis for records descended from one element. An insertion is the DNA left by
one transposition event and exists in our data only as a reconstruction. A subfamily is one consensus model,
hence one lineage of copies from one source element in one period. Above it the Dfam lineage supplies
family, superfamily, order and class in Wicker's terms; RepeatMasker's three tokens straddle those ranks
(its class is Wicker's order, its family mixes superfamily and family, B1 sits under `Alu`). Every per-locus
count in the field is a count per record, and every biological statement is about insertions.

| fact, mm39 | value |
|---|---:|
| records / `interspersed` records / distinct `interspersed` names | 5,320,771 / 3,764,949 / 1,220 |
| source instances / instances holding several records | 4,696,900 / 445,649 |
| `interspersed` instances mixing names / mixing strands | 30,569 / 23,244 |
| records overlapping another record | 8.07% |
| `interspersed` median record length / share under 90 bp | 160 bp / 17.6% |

**Where the promoters are, and what the catalog can say about them.** A full L1 carries its promoter in the
5′ UTR (a sense promoter and, *general knowledge*, an antisense one); reverse transcription usually stops
before the RNA's 5′ end, so most copies are 5′-truncated and a copy that begins deep inside the model has no
promoter of its own. An ERV provirus is LTR, internal region, LTR, with the promoter in the LTR;
recombination between the LTRs leaves a solo LTR that can still act as promoter or enhancer. RepeatMasker
models LTR and internal regions separately, so a provirus is at least three records. B1 derives from 7SL RNA
and B2 from a tRNA; both carry Pol III internal promoters (*general knowledge*).

| structural fact, mm39 | value |
|---|---:|
| L1 records / names | 877,139 / 149 |
| L1 records beginning at model base 1 / within 10 / within 100 | 588 / 2,342 / 11,226 |
| young L1 names (`L1MdA`, `L1MdTf`, `L1MdGf`): records / instances / median divergence against all L1 | 70,628 / 53,756 / 2.1% against 19.3% |
| L1MdA_I model length from Dfam parts (5end + orf2 + 3end) against row-implied lengths in the catalog | 7,002 bp against 4,915 to 8,042 bp |
| LTR-class records; instances holding LTR and internal / internal only / LTR only | 1,105,064; 17,947 / 103,526 / 722,280 |
| LTR–internal same-family same-strand pairs within 1 kb / within 5 kb; of the 5 kb pairs crossing instance ids | 93,660 / 237,375; 181,443 |

The naive rule "an LTR without a same-instance internal is a solo LTR" calls 722,280 solo LTRs; the naive
rule "a record at model base 1 is promoter-intact" calls 588 L1 loci where the insertion answer is hundreds
to a few thousand. Both are why the field reconstructs before it names.

**Age has four meanings.** Lineage restriction: the clade Dfam assigns to a model, a curator's statement
about where the model's copies occur. Divergence: one copy's distance from its consensus under this
library and this run, a ranking rather than a clock. Polymorphism: presence or absence between strains,
absent from our data. Intactness: full length, open reading frames, a promoter present, which needs
reconstruction and sequence. The ruled design publishes the first two as separate columns and leaves the
tier to the consumer. The library gap matters here: the RepeatMasker run used RepBase and Dfam_Consensus of
20181026, while the snapshot is Dfam 4.0 of May 2026, so names and models have drifted.

| Dfam clade of the matched `interspersed` names (one clade per name) | names |
|---|---:|
| Eutheria / Mus / Murinae / Amniota / Mammalia / Theria | 367 / 172 / 169 / 96 / 67 / 64 |
| Muroidea / Boreoeutheria / Euarchontoglires / Muridae / Tetrapoda / Primates | 57 / 36 / 30 / 29 / 19 / 17 |
| models with several clades / models carrying a Primates branch / mouse names carrying such a model | 9 / 33 / 31 |

**Why the RNA is hard to count, and where it is hardest.** Copies of a young subfamily are near-identical,
so most of their reads align to many loci; the young subfamilies are the hypothesis's target and the hardest
to count. Cellranger keeps one alignment per read, so every EM route starts with a STAR re-alignment that
keeps the alternatives, and the cap on reported loci decides which reads exist before any estimator runs.
IRescue fixes unique molecules exactly and allocates ambiguous ones by an EM that starts even and ignores
unique support, the conservative behaviour C7 asked of it. TEsingle models gene and TE competition jointly
and ends in a hard assignment per molecule. A unique-only count is the floor everything is compared to.
Near half of repeat sequence lies in gene bodies, so a read there has a competing host explanation.
Capture chemistry shapes the universe before alignment (*general knowledge*): 10x chemistries prime on
poly-A, so full-length L1 and proviral Pol II transcripts are captured while autonomous Pol III SINE
transcripts largely are not; SINE signal in these data mostly reports SINEs embedded in host transcripts.

| counting fact | value |
|---|---|
| STAR loci cap / anchor cap in the sources (IRescue README; dissertation; TEsingle scripts; Stellarscope protocol) | 100/100; 100/150; 100/200; 500/– |
| reads carrying several alignments in a gene-rich window, 14616 whole-cell / 14761 nuclei | 14.8% / 3.8% |
| IRescue on the 4/2/3 fixture, observed against the old expectation | 5.5 and 3.5 against 6 and 3 |
| every published method on intronic TEs in the dissertation's benchmark | near zero |

**Genic context is a function of the annotation.** Whether a TE is exonic, intronic, promoter-proximal or
intergenic depends on the gene set, the isoform, the strand and the distance rule. Two annotations are live:
GENCODE vM37, the refcache pin and the phase 8 fixture, and the 10x 2024-A GTF, GENCODE vM33 filtered to
protein-coding, lncRNA and IG/TR types, which cellranger counted all three datasets with.

| annotation | genes / transcripts / exon rows | exon union | `interspersed` bases removed by the unstranded mask / records fully removed |
|---|---|---:|---|
| GENCODE vM37 | 78,317 / 278,369 / 1,298,921 | 160.5 Mb | 26,235,918 bp / 96,119 |
| 10x 2024-A, vM33 filtered | 33,696 / 125,556 / 834,423 | 114.0 Mb | 15,361,040 bp / 65,841 |
| `interspersed` records whose mask outcome differs between the two | 74,464 | | |
| same-strand mask under vM37: bases restored / records gaining / fully removed records returned | 11,125,985 / 76,971 / 46,075 | | |

The first child declares context `not_computed`; the relation follows in a later child snapshot at the
ruled envelope of 10 kb upstream and 2 kb downstream of transcript starts, and the exon-subtracted SAF is the
bulk product, since every single-cell EM route takes unmasked record exports with the full gene GTF.

**Replication and what nuclei miss.** Twenty animals in two tissues license TE-level tests with tissue
pairing; one pooled library per condition licenses description. Nuclear RNA sees a different transcriptome
from whole-cell RNA: the 14761 paired-against-unpaired anchor found, of 63 regulon TFs, 15 shared, 34 seen
only with whole-cell RNA and 14 only with paired nuclei. Aging also shifts cell-type composition (*general
knowledge*), so the grain of any TE contrast is animal by cell type, computed identically over every label
of the roster (12 parent, 26 fine, 33 state labels in 14761), with the narrative focus a filter at query
time.

## 2. Premises and pain points

The eight premises of the earlier file stand; six more have surfaced since.

1. **The reference stops where interpretation starts.** A geometric fact under a declared parameter is
   reference; a verdict that needs a biological threshold or assay reads is analysis. Ruled as "one
   component, one thing" (C3, C5, C11). The pain: consumers want verdicts, and some formats force one into
   the file; a GTF `gene_id` is a grouping decision, which is why `record_starsolo.gtf` exists beside
   `record.gtf`.
2. **Every input is a release, and parity is a hard requirement.** RepeatMasker run, GENCODE release, Dfam
   release, 10x reference and tool versions all move; immutable snapshots pin each by digest. The pain is
   multiplication: two gene GTFs already imply two children, each with acceptance.
3. **Three units, one word "locus".** The field reports subfamilies, estimates at records and reasons about
   insertions; every tool builds its competitor from a different key. te-tracks carries record, instance
   and subfamily identities side by side and registers every emitted feature back to records.
4. **Ambiguity is the data.** Two paradigms: exclude ambiguous support before counting, or keep every
   candidate and let a model allocate. te-tracks serves both and says which file serves which; its
   guarantee is exon-disjoint sequence support, and molecule exclusivity belongs to the counting run.
5. **Enumeration decides answerability.** Anything enumerated can be filtered down; anything left out cannot
   be filtered in without a new build. Envelopes err wide within cost.
6. **Cost lives in acceptance.** Bytes are cheap next to identity, registration, mutation-breaking fixtures,
   documentation and a review loop per artifact. Hence "batched into one later snapshot" and "when a
   consumer names the need".
7. **Verified means run.** A parser check proves a reader accepts the file; an execution gate proves the
   binary counts what we expect. The IRescue oracle showed our expectation of a published tool was wrong.
8. **The replication structure decides what may be claimed.** The reporting tiers, cross-tissue
   replicated, single-tissue replicated and Multiome descriptive, are the pipeline contract's to state.
9. **Unmeasured is a value.** `not_computed`, `outside_universe`, `unsupported` and `failed` are distinct
   from a measured zero, and the distinction becomes user-facing the moment an app queries the ledger.
   "No motif hit" and "motif scan never ran on this generation" must read differently.
10. **Evidence is layered and the layers are orthogonal.** Spatial scope (record, TE–peak intersection,
    whole peak), cellular pairing (same nucleus, same group, cross-dataset by condition), RNA attribution
    (unique locus, allocated locus, subfamily only), cohort replication (descriptive, single tissue, paired
    tissues) and inference source (paired, unpaired, combined). One `supported` flag conflates them; a
    row that names its rung on each axis can be filtered honestly.
11. **Curated and measured are different kinds of evidence.** A model's clade is a curator's assignment; a
    record's divergence is a measurement of one copy under one library. Kept apart, their discordance is
    informative; collapsed into one "young" label, it is hidden.
12. **Reconstruction has no ground truth inside these data.** Yield is measurable (pairs at 1 kb against
    5 kb); precision needs an external positive set or sequence evidence. Until one is named every unit is a
    candidate with a status, and counts on units need a declared allocation because component sums double
    shared support.
13. **The strict funnel is biased against the hypothesis.** Unique mappability rises with divergence, so a
    unique-only funnel sees old copies best while the young subfamilies live in the allocated share.
    Display strict and allocated side by side and report the ambiguous share per subfamily.
14. **Capture chemistry is part of the universe** (*general knowledge*). Poly-A priming decides which TE
    transcripts exist to be counted at all, before alignment caps and estimators decide anything.

## 3. The open questions

Ordered by what they gate. Items 1 to 3 shape the science of the pilot; 4 and 5 shape the 14761 schema;
6 to 8 shape te-tracks' next snapshots; 9 and 10 are packaging and administration.

### 1. The first contrast, and where discovery happens

**Premise.** Five conditions on one axis; the hypothesis is age-derepression and the treatments are
modifiers of it. The whole-cell arm holds twenty animals in two tissues; the Multiome holds four pooled
libraries and lacks the combined arm.

| route | gains | costs |
|---|---|---|
| A. Young_Control against Old_Control first; subfamily and lineage discovery in the whole-cell RNA; descriptive spatial corroboration in the Multiome | the cleanest question, the most power (4 against 4 in two paired tissues), and an eligible feature set that the treatment questions then test on | the intervention story waits one step |
| B. Treatment contrasts first (Old_Control against each old arm) | asks the lab's intervention question directly | a reversal claim has no age baseline to be read against; the eligible set is undefined |
| C. One factorial model over all five conditions at once | one fit, interactions visible | four animals per cell, interactions underpowered, the Multiome lacks one arm; the model's feature set is still chosen somewhere |

**Implications.** Route A defines eligibility and prevalence per feature before any treatment test, so
"does Rapa or MetR move the age-associated features back toward young" becomes a second prespecified test
on a named set rather than a second discovery. The tier vocabulary then labels each result.

**Caveats.** Composition shift with age confounds any pseudobulk over all cells; the grain is animal by cell
type under harmonized labels. The discovery arm is 5′ whole-cell and the corroboration arm is 3′ nuclear,
so corroboration is direction-level and cannot be a replicate. Effects concentrated in cell types the
whole-cell arm captures poorly will be missed by design.

**Recommendation.** A, as the consult proposed and the orchestrator's stance records.

### 2. What "young" means: the age-tier policy behind the evolutionary-origin question

**Premise.** The programme's stated need for Dfam now is the evolutionary origin of the TE-driven aging
signal: is age-associated signal concentrated in lineages that entered the mouse genome recently and may
still be active, or in old lineages whose signal is more plausibly host transcription. te-tracks publishes
the clade path of every matched model and the divergence of every record, with `clade_compatibility` for
models assigned outside the mouse lineage; the tier is consumer policy.

| route | what it is | strength | weakness |
|---|---|---|---|
| A. Clade strata | mouse-restricted (Mus, Mus musculus), rodent (Murinae, Muridae, Muroidea, Rodentia), mammalian and deeper, as separate queryable strata | curated, stable across assemblies, applies at subfamily grain where RNA is counted | model-level: every copy of a subfamily inherits one stratum whatever its own age |
| B. Divergence bins | five disjoint record-level bins at 5, 10, 20, 30 percent | copy-level, measured, already in the catalog | a ranking under one library and run; within-subfamily bin abundance needs record-level RNA attribution, which is where multimapping is worst |
| C. Joint clade by divergence with discordance flagged | both axes on every row; a mouse-clade record at high divergence or a mammalian-clade record near zero divergence carries a status | the most informative; discordance becomes evidence about the model or the copy | more cells, more sparsity, a policy to write |
| D. Literature name lists | `L1MdA`, `L1MdTf`, `L1MdGf`, `IAPEz`, `MMERVK10C`, `RLTR4`, `ETn` as "young" by citation | what reviewers know | ad hoc; silent on the rest of the catalog |

**Implications.** RNA counted at subfamily grain admits only clade or name tiers; divergence-bin claims
need record-level estimation with its allocation caveat. A prespecified contrast of mouse-restricted against
deeper strata is testable with four animals; many nested lineage tests are exploratory until power is
shown. Zero observed counts need callability evidence beside them.

**Caveats.** Clade is a distribution statement about the model, so a mouse name matched to a primate-assigned
model gets a compatibility status and never a tier. The library gap of 2018 against 2026 means some names
map through part models or drift; the 26 missing names are mostly LTR internal models. Divergence varies with
model choice and substitution rate; low divergence alone establishes neither recent insertion nor
transcription. Full-length and ORF status need the structural batch.

**Recommendation.** C as the stored structure with A as the primary prespecified contrast and D kept as a
documented alias set for readers; te-tracks' side of this is already in the running 9a unit.

### 3. Autonomous transcription: the evidence ladder and which assay supports which rung

**Premise.** The measurement is TE-associated RNA; the claim is transcription from the TE's own promoter.
Between them stands a ladder, and each arm reaches a different rung.

| rung | evidence | arm that supplies it | te-tracks product |
|---|---|---|---|
| 1 | TE-associated molecules under any counter | all | record and subfamily exports, registration |
| 2 | exon-disjoint support, or joint gene/TE allocation | all | exon-subtracted SAF for bulk; unmasked exports plus the full GTF for EM |
| 3 | relative strand to the host transcript | stranded chemistries once the RNA-sense mate is measured | context relation later; stranded mask companion later |
| 4 | intronic background of the sample or cell group | all, as a coverage ratio | optional pure-intronic and pure-exonic region sets later |
| 5 | molecule 5′ ends at a retained model 5′ end | whole-cell 5′ arm only | record 5′ windows with prefix eligibility, after the host build |
| 6 | open chromatin at the TE 5′ end or LTR in the same nucleus | Multiome only | record intervals now; TE–peak intersections are the dataset's |
| 7 | the source copy is structurally intact | reconstruction | instance union, pairs, Dfam model lengths, after the host build |

| display route | gains | costs |
|---|---|---|
| A. Strict funnel (a unique locus molecule with an aligned block inside the TE–peak intersection and a cut in the same nucleus) beside an allocated-support sensitivity | interpretable and honest about attribution; the allocated view shows where the young subfamilies are | two channels to explain |
| B. Allocated only | more signal, covers young subfamilies | locus attribution is a model output presented as observation |
| C. Unique only everywhere | simplest claim | nearly blind to the hypothesis's target |

**Implications.** The row-level vocabulary of question 4 is how a result records the rung it reached. The
5′ whole-cell arm is the only initiation evidence available, and it is also the replicated arm, so
rungs 5 and 1 to 3 together are where a defensible transcription claim can be made; the Multiome adds rung
6 as same-nucleus co-detection without replication. Rung 7 needs the structural batch and an oracle.

**Caveats.** The 3′ nuclear assay leaves origin unresolved by design. Antisense-to-host TE signal needs its
own support policy, since a same-strand exon mask admits host RNA into a TE-antisense count. The intronic
diagnostic is a ratio over a sample and supplies no per-TE subtraction. Poly-A capture (*general knowledge*)
makes rung 5 an L1 and ERV question and leaves SINE initiation unobservable in these chemistries. Physical
co-detection is observational and establishes no regulatory link.

**Recommendation.** A, with the ladder written into the D2 and D3 contract as the meaning of the tiers.

### 4. The evidence vocabulary and measured-zero semantics for the 14761 ledger

**Premise.** D2 makes the peak ledger a directory of immutable Parquet generations queried by DuckDB with
sub-peak grain for TEs, motifs and cuts; D3 adds an inference-source dimension because nuclear RNA misses a
share of the circuit. The consult proposes five row-level fields: `pairing_level`, `rna_attribution`,
`spatial_scope`, `replication_tier`, `inference_source`.

| route | gains | costs |
|---|---|---|
| A. Five orthogonal fields plus a table of allowed combinations | queryable, composable, each axis keeps one meaning | many combinations, some meaningless (same nucleus with an unpaired source); the validity table must exist |
| B. One ordinal evidence tier | simple to read | lossy; forces an ordering across axes that have none |
| C. Free-text provenance | no schema work | unqueryable; the app cannot filter on it |

**Implications.** This is 14761's D2 and D3 material; te-tracks contributes the reference statuses only.
Run and matrix identities (`run_id`, `matrix_id`) and the four-field binding make every count traceable to
its estimator and registration. Every fact table exposes `measurement_status` so zero and unmeasured differ.

**Caveats.** Thresholds inside `rna_attribution` (posterior cutoffs) and `spatial_scope` are the pilot's to
calibrate; the vocabulary fixes names, and the pilot fixes values.

**Recommendation.** A, with the allowed-combination table written before the first satellite lands.

### 5. Reconstruction calibration: what an insertion is, and how we know we found one

**Premise.** The named consumer is the projection tool's funnel, which begins at L1 remnants. Records are
alignments, instance ids err both ways, and the field's units are full-length L1, proviruses and solo LTRs.
te-tracks publishes catalog-only geometry after the host build; the analysis publishes runs, candidates,
evidence and verdicts.

| route | oracle and sweep | tractability | risk |
|---|---|---|---|
| A. L1 first | model-prefix coverage against Dfam part models; sweep prefix tolerance 0, 10 and 100 bp; positives from an external full-length L1 set (*general knowledge*: L1Base-type catalogs exist for mm10 and need lift-over) or from copies spanning the model | one linear model per subfamily, hundreds to low thousands of candidates | the 2018 model coordinates against Dfam 4.0 parts are unvalidated; row-implied lengths vary within 145 of 149 names; HAL1 matches a whole model and is no autonomous L1 |
| B. ERV first | LTR–internal adjacency at 100, 1,000 and 5,000 bp with a compatibility dictionary of which LTR belongs with which internal, compared to "One code to find them all" | the provirus question is the LTR promoter question the ATAC arm cares about | far more candidates; same-family adjacency pairs incompatible models; nesting; precision unmeasured |
| C. Both at once | one batch, one review | the calibration effort doubles before either has an oracle |

**Implications.** Yield at 1 kb against 5 kb is measured; precision is the missing number, and it needs a
positive and negative set named before the sweep. Counts assigned to a reconstructed unit need a declared
molecule allocation, since summing components double counts shared support. Every candidate carries
alternatives and a status; verdicts stay in the analysis.

**Caveats.** Prefix coverage says the promoter region is present in the copy and says nothing about its
sequence integrity or activity. Mixed-strand instances cannot be one transcript in BED12 or GTF. Solo status
is a negative search result and needs the searched envelope and callability recorded.

**Recommendation.** A first with the external positive set named before the sweep; B second with the
compatibility dictionary derived from the Dfam lineage (same ERV group) rather than the raw family token.

### 6. The 10x-matched child: when, and the ARC verification

**Premise.** Ruled: two snapshots, vM37 done in phase 8, the 10x vM33-filtered child next. The 10x GTF is what
cellranger counted with and what the STARsolo re-alignment should index so gene counts stay comparable. The
ARC reference's GTF is presumed equal to the GEX one and unverified.

| route | gains | costs |
|---|---|---|
| A. Build the 10x child before the host build | one publication event carries both children | one more implementer loop and re-measured acceptance before the host build; the umbrella pin waits |
| B. Build it after the host build as the first later child snapshot | clean sequencing; the host build is not delayed | a second host publication |
| C. Defer until a consumer needs the exon-subtracted SAF on the 10x annotation | cheapest | risk that a bulk-style count on single-cell data happens without it |

**Implications.** No single-cell route consumes the mask; the EM routes take unmasked exports and the full
GTF. The child's single-cell product is the context relation, which is post-host in any case, so annotation
parity matters when the relation ships. The ARC verification is a fact-fetch from the 14761 run's reference
path (`reference.json` and the GTF digest); if it differs from the GEX GTF, a third pin appears.

**Caveats.** The 10x GTF is filtered to three biotype groups with versionless ids; TE-derived pseudogene exons
are unmasked under it, consistent with a gene pass that ignored them. Its 26 unannotated contigs against
vM37's 23 change the coverage table.

**Recommendation.** Verify the ARC GTF now as a fact; build the 10x child after the host build together with
the context relation's first snapshot, so parity and the product that needs it arrive together.

### 7. The stranded mask companion and the chemistry gate

**Premise.** The same-strand mask restores support that the unstranded mask removes, and it presumes the
counting run reconstructs RNA orientation. The records establish that both OCM mates align and nothing about
which is RNA-sense; the ARC recipe assumes R2 is sense.

| route | gains | costs |
|---|---|---|
| A. The pilot measures the sense fraction per mate against isolated unambiguous genes on both strands; the companion joins the first later child snapshot | rigorous; one audit settles both chemistries | the companion waits for the pilot |
| B. Adopt the vendor's stated mate convention (*general knowledge*, unverified for this kit) | fast | wrong for this kit means a mask that admits host RNA into the wrong channel |
| C. Drop the stranded companion | simplest | forfeits the restored support for bulk counting |

**Implications.** Ownership sits with te-consumers by the C7 ruling: alignment and strand are the consumer's
responsibility, and te-tracks records only the recipe its own fixtures run with. SAF cannot encode the
read-to-RNA conversion; the companion's guarantee is zero same-strand exon overlap.

**Caveats.** The TE-antisense channel needs its own declared policy under any mask. TEsingle's paired-mate
handling and IRescue's block strand rule belong in the same fixture.

**Recommendation.** A, as the first recipe te-consumers lands.

### 8. Reconstruction's consumer: the projection tool

**Premise.** The owner names an interactive tool that projects a lineage's remnants onto genome
coordinates, lights up where the dataset sees them, and filters the schema down the funnel from L1 remnants
through RNA support and open chromatin to TF families and a validation subset.

| route | gains | costs |
|---|---|---|
| A. marimo as controller, two to four jscatter panels, an embedded genome-browser prototype (igv.js or JBrowse), DuckDB over manifest-pinned Parquet, a track service only if latency demands | fits the existing marimo sessions and the export-first exploration convention; warm viewport under one second as the provisional target | a browser widget dependency; a dataset-owned interval index to build |
| B. A full track-server stack (HiGlass class) | multiscale views | a service to deploy and maintain before any question is asked |
| C. Static review notebooks only | nothing to run | the funnel cannot be walked interactively |

**Implications.** D2's decision. te-tracks supplies intervals and identities alone; the dataset owns the
interval index on assembly, dictionary and half-open coordinates, with bins and exact overlap filtering.
Millions of intervals are never drawn raw; overview tiles summarize and zoomed queries return records.

**Caveats.** Browser suitability is general software knowledge, unqualified offline. A new service needs a
configured port after inventorying listeners.

**Recommendation.** A.

### 9. te-consumers: packaging and ownership

**Premise.** The module sits at the umbrella root, untracked, with its environment recipe; the environment
itself lives outside every repository; the datasets call it from `40_transposable_elements/`. The
cellranger tarball sits beside it in the umbrella tree.

| route | gains | costs |
|---|---|---|
| A. Commit the directory in the umbrella | simplest | three datasets cannot pin a version of it |
| B. Its own repository as a submodule, hub-wired through `prov` | versionable, pinnable per dataset, releasable on its own timeline | onboarding once |
| C. Fold into the owner's TE-RNAseq toolkit | reuses the bulk toolkit's docs and recipes | mixes bulk and single-cell contracts in one package |

**Implications.** The tarball is a licensed 2.6 GB download and belongs in a host cache with a sha256 pin
under any route; the environment manifest already records the archive digest.

**Recommendation.** B when the first recipe lands; meanwhile move the tarball out of the umbrella tree.

### 10. Administration awaiting a word

- The reading of `docs/DECISIONS.md` as written since `829e0ad`, sixteen sections and the deferrals.
- The Dfam companion tables and the part-match scope (L1 and L2/CR1 part sets alike), adopted by the
  orchestrator for 9a and overturnable; a 9a fix loop absorbs an overturn.
- Host retention: about 15.3 GB per core build plus children; the runbook should state that every build a
  consumer pins is retained beside `current`, so the pins are the retention rule.
- Who owns the chemistry audit of question 7 (recommendation: te-consumers' first recipe).
- The ATAC TE arm's schema (peaks, motifs, TFs, GRN, TE) is parked by the owner's word; two facts wait
  for it: overlapping records need a deduplicating cut assignment, and unique-mappability bias in cut
  counting mirrors the RNA problem in young TEs.

## 4. What blocks what

| work | blocked on |
|---|---|
| te-tracks 9a, 9b, host build, umbrella pin | nothing biological; two overturnable adoptions are in the running unit |
| the 10x-matched child and the context relation | the ARC GTF fact; the timing word of question 6 |
| the stranded companion and the intron-retention sets | the chemistry audit of question 7 |
| the RNA pilot in `40_transposable_elements` | the contrast of question 1; the vocabulary of question 4; the STAR recipe is ruled |
| the 14761 ledger and app | D1 to D3 rulings with the consult's sketch as material; questions 4 and 8 |
| the structural batch and reconstruction | the host build; an oracle named under question 5 |
| age-tier claims | question 2's policy; the 9a Dfam view supplies the columns |
