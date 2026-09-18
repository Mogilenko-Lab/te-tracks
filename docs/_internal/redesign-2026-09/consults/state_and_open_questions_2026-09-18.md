# Where the programme stands, what is still open, and when te-tracks is parked (orchestrator, 2026-09-18)

Written at the owner's request as the compaction record for this session and as a re-orientation in the
biology after the sixth round of rulings. It supersedes
`open_questions_premises_after_phase8_2026-09-17.md` as the current open-question list, because nine of that
file's ten questions are now ruled. Sources: `adr_rulings_2026-09-17.md` rounds one to six,
`docs/DECISIONS.md`, plan 19, the phase 9a reviews and rulings, and the measurements named inline. Nothing
here is a ruling; recommendations are the orchestrator's.

## 1. Where we are in the grand plan

The grand plan is three layers. te-tracks is the reference layer and is nearly parked. `te-consumers` is the
quantification layer and has an environment but no recipes. The datasets are the analysis layer, where D1 to
D3 of 14761 design the schema that everything lands in.

| layer | state |
|---|---|
| te-tracks core, phases 0 to 7 | committed and reviewed |
| te-tracks gene child, phase 8 | committed as `393ca76`, reviewed twice, fixed once |
| te-tracks phase 9a, core additions | implemented, reviewed twice, fixed once, second fix running; not yet committed |
| te-tracks phase 9b, acceptance and runbook | prompt written and pinned to the post-fix identity |
| milestone 9 seam review, parking pass, claim validation | prompts written |
| host build and publication | the owner's step; the runbook is 9b's deliverable |
| umbrella pin bump | at milestone 9, ruled |
| te-consumers | environment built and pinned; its own repository ruled; no recipes yet |
| 14761 D1 to D3 | unruled; promoted to the primary question by the owner this session |

What phase 9a adds, all verified independently by the orchestrator and by two reviewers: the STARsolo
record-as-gene profile in three namespaces at 3,764,949 rows each, the Dfam lineage, rank, part and clade
view in four tables, the four-field matrix binding with its join fixture, a records-instances-insertions
section in the documentation, an IRescue check that asserts what te-tracks guarantees and records what
IRescue does, the consumer environment promoted into the package, and a failed-build publication case.

Identity after the first fix: core `BUILD_ID` `5e2a156362cddc58…`, child `198f39f0ef168751…`, `CATALOG_ID`
`90cc18be5d4ee934…` in both, payload 52 files and 15,301,538,537 bytes, `rank_scheme_wicker_v1` recorded in
the identity and inherited by the child.

Two things were proved at full scale this session, which no fixture can establish: `cellranger mkgtf`
accepted all 3,764,949 rows of the record profile in 64.6 s with every row retained, and `featureCounts`
loaded the child's exon-subtracted SAF as 3,684,934 features collapsing to 1,220 meta-features over 59
contigs in 4.4 s. Two consumer memory floors were measured for the runbook: Stellarscope's interval tree
needs about 10.1 GB resident to hold the whole record profile and TElocal's index about 3.9 GB, against the
producer's own 9.0 GB peak.

## 2. The biology, re-oriented after the rulings

The hypothesis has not moved: with age the heterochromatin over transposable elements relaxes, copies that
retain a working promoter transcribe, and their RNA or its reverse-transcribed cDNA reaches the innate
sensors of the interferon axis, with rapamycin and methionine restriction as candidate suppressors. What has
moved is which biological questions still gate work, because the owner ruled the contrast question off the
critical path: counting comes first, contrasts afterwards, and no estimator takes a condition label.

Five biological problems remain, and each is now a schema problem as much as a biological one.

**Attribution.** A read from a young subfamily aligns to many copies. Unique molecules are exact; ambiguous
molecules are allocated by a model. IRescue fixes the unique share and spreads the ambiguous share from a
uniform start, TEsingle assigns hard after joint gene and TE competition, STARsolo's expectation
maximization spreads fractionally. The same molecules therefore yield different per-locus numbers under
different estimators, and the difference is a reported quantity rather than an error. The schema consequence
is that a count is meaningless without its `run_id` and `matrix_id`, and that unique-only and
allocated channels are separate products that must never be summed.

**Origin.** The measurement sees TE-associated RNA of every provenance: a TE inside an intron carried by
host pre-mRNA, a TE exonized into a host transcript, a TE past a gene's end caught by read-through, and a TE
transcribed from its own promoter. Separating them needs the host transcript's geometry and strand, which is
the deferred context relation, and initiation evidence, which only the 5′ whole-cell arm can supply. In the
14761 nuclear window more than half the reads are intronic against about a fifth in the whole-cell window,
so intronic TE signal in nuclei is mostly host pre-mRNA background.

**Stratification.** Age has four separate meanings and the design keeps them apart: the clade Dfam assigns
to a model, a curator's statement about where the model's copies occur; the divergence of one copy from its
consensus under this library and run, a ranking rather than a clock; polymorphism between strains, absent
from these data; and structural intactness, which needs reconstruction. The owner ruled the working tier to
be the literature name lists with a later manual check against Dfam, so the 9a view's clade paths and
per-rank statuses are the material that check reads.

**Intactness.** A full L1 carries its promoter in the 5′ untranslated region, and most copies are
5′-truncated because reverse transcription stops before the RNA's 5′ end. In mm39, 588 of 877,139 L1 records
begin at model base 1. For the three young mouse subfamilies the picture is worse and it explains a design
choice: of the 10,351 records under `L1MdA_I`, `L1MdGf_I` and `L1MdTf_I`, only 18 begin at model base 1,
because RepeatMasker splits the tandem monomer array of the mouse 5′ untranslated region. Genomic 5′
windows are therefore weak for exactly the subfamilies the hypothesis is about, which is why McKerrow's
group went to consensus space instead.

**Co-detection.** The Multiome sees RNA and chromatin in one nucleus, which is the only place a
same-nucleus claim can be made, and it has one pooled library per condition, so it licenses description and
not inference. The whole-cell arms carry twenty animals in two tissues and license tests, and they carry no
chromatin. A claim therefore has to name which arm supplied which rung of its evidence, which is what the
five-field row vocabulary is for.

## 3. Premises and pain points

The fourteen premises of the previous lay-out stand. Four more were earned this session, each from something
that went wrong.

15. **A check that cannot fail is the most expensive artifact in the package.** Two checks counted correctly
    and could be fooled: the IRescue conservation assertion was taken after a dictionary that silently
    discarded an extra matrix row or a duplicate feature name, and the STARsolo case asserted totals and two
    per-gene ranges while permitting support on a gene the fixture never supported. Both had passed every
    previous review, because reading a check and mutating a check are different acts. Reviews in this
    programme now mutate.
16. **A reference's guarantee is bounded by its threat model, and the boundary must be written down.** The
    verifier judges an archive against its own declaration, so it detects corruption and accidental drift and
    it cannot detect a coherent forgery, since `BUILD_ID` is recomputable by anyone editing the identity. The
    consumer's protection is pinning the full id and the digests of the files it reads. A sentence promising
    more than that is a defect, and one such sentence is being corrected now.
17. **Scale is a separate claim from correctness.** An eleven-record fixture cannot establish that pipe and
    colon characters in 3.76 million gene identifiers survive a vendor's reference builder, or that a
    3.68-million-feature annotation collapses to the intended 1,220 meta-features. Both are now measured on
    the real exports.
18. **The measuring instrument leaves marks, and process discipline is part of the deliverable.** A suite run
    summarised through `tail` destroyed the identity of a failing check and the runner's exit status, so one
    anomaly in this session is permanently unattributable. Two concurrent suite runs against one reference
    root produced it. A reviewer's isolation held only because every write happened to go through unlink and
    rewrite rather than in-place modification of a hardlinked copy. None of these is a defect in the package
    and all three are now rules.

## 4. The open questions

Nine of the previous ten are ruled. What follows is what is genuinely undecided, in the order it gates work.

### 1. The multiome schema: freeze the spine now, or wait for a tool run

**Premise.** The owner promoted this to the primary question: a database for the Multiome data supporting
every granularity and every forking query path from peaks through motifs to transcription-factor families and
named factors and gene-regulatory-network edges, with transposable elements layered onto it, and added that a
run of the TE tools may be needed before the shape is fully understood. The spine is a rule rather than a
table: one relation per grain, and every fork a bridge table keyed on both sides. The TE layering is exactly
two joins, one geometric and one of identity; everything else about TEs is read from te-tracks as dimensions.

| route | gains | costs |
|---|---|---|
| A. Freeze the invariant spine now, run the smallest real pilot, then freeze the estimator-facing tables from its actual output | the parts that cannot change without breaking every consumer are settled while the parts that depend on what a tool emits wait for evidence; the pilot has a target to write into | two freezing events and the discipline to respect the first |
| B. Freeze everything after the pilot | one event, fully evidence-led | the pilot has no contract to write into, so it invents one, and that invention becomes the schema by default |
| C. Freeze everything now | fastest to a queryable database | the estimator tables will be wrong in their grain, because nobody has seen a real feature identifier string or learned whether a channel is integer or fractional |

**Implications.** What only a run can settle is short and specific: the realized feature-identifier strings
each tool emits, whether each channel is integer or fractional, whether the re-aligned barcodes equal the
existing nuclei roster, and the sparsity that decides partitioning. What a run cannot settle, and what
therefore belongs in the frozen spine, is the identity of a record, an instance and a subfamily; the grain of
every relation; the bridge tables and their keys; the status vocabulary that distinguishes unmeasured from
measured zero; the four-field matrix binding; and the conservation rules that forbid summing across grains.

**Caveats.** Sub-peak grain is not optional: without within-peak offsets for motifs and exact intersection
intervals for TEs, "a motif inside a TE" degrades into a conjunction of two peak-level booleans, which is the
claim the owner's own D2 note already rejected. The cell axis must never mix datasets. And a fork that
returns nothing has to say why, which is why every fact carries a measurement status.

**Recommendation.** A, with the smallest real slice being one 14761 library, the existing peak set, and the
strict funnel, and with the allowed-combination table of the five evidence fields written before the first
satellite lands.

### 2. Feature space: does the schema admit consensus coordinates

**Premise.** Everything designed so far lives in genomic coordinates. McKerrow's route masks the L1 family
from the genome, appends consensus sequences as decoy chromosomes, and counts proper read pairs whose first
read begins in the model's 5′ region under strict mismatch and clipping filters. It answers how much
transcript initiating at a subfamily's 5′ untranslated region a cell holds, and it surrenders locus identity
deliberately. For the mouse it is the only credible initiation assay available, because of the 18-of-10,351
fact above.

| route | gains | costs |
|---|---|---|
| A. Admit a `feature_space` dimension now, with genomic and model spaces as its values | the consensus route's counts have somewhere to live, and the rule that they never sum with genomic counts is structural rather than remembered | a dimension on every count table before a consumer exists |
| B. Keep the schema genomic and treat a consensus run as a separate product outside it | simplest today | the two products meet only in a person's head, and someone will eventually sum them |
| C. Do not adopt the consensus route | nothing to design | forfeits the one initiation assay the 5′ arms can support |

**Implications.** Consensus-space features are keyed by model accession, model version and a window, and
cannot join to peaks by geometry at all; their only bridge to the peak world is subfamily identity. They need
their own index, so the "one alignment feeds every consumer" rule holds for the genomic routes and not this
one. The counter reads the mismatch, cell-barcode and molecule-barcode tags that STARsolo emits, so
cellranger is not required.

**Caveats.** The published materials are internally inconsistent about the decoy set: the paper's mouse
decoys are Dfam part models, which our snapshot holds with accessions and lengths, while the shipped archive
carries 25 full-length RepBase-style consensi at 6.2 to 7.5 kb whose names its own instructions do not
address. Pinning which set is used precedes adoption. The masking interval set is reproducible from our
catalog exactly, and doing so exposes that the published filter was case-insensitive, pulling six ancient
subfamilies and 15,629 extra records into the mask alongside the 25 intended young ones.

**Recommendation.** A for the dimension, because it is one column and it prevents a category error; adoption
of the route itself waits for the 5′ arm to be the active pilot, with the decoy set pinned by accession and
the mask supplied by te-tracks as a name-explicit export.

### 3. Which annotation the bulk arm is served on

**Premise.** The owner requires the parked annotation to serve the out-of-scope bulk RNA-seq dataset as well
as the three single-cell ones. Bulk counting is the one route that consumes the exon-subtracted SAF, and a
mask is only meaningful against the annotation the gene pass used. Three annotations are live: GENCODE vM37,
which the child is built on and whose acceptance is pre-measured; the 10x 2024-A filtered set, which
cellranger counted the three single-cell datasets with; and whatever nf-core filtered set the bulk pipeline
used, which is unverified.

| route | gains | costs |
|---|---|---|
| A. Serve bulk on the vM37 child as built | nothing further to build; the more conservative mask, since pseudogene and small-RNA exons are masked too | the bulk gene counts were made against a different annotation, so gene and TE support are not exon-disjoint against the same model |
| B. Build a third child on the bulk annotation once it is verified | exact parity for the arm that actually uses the mask | a third acceptance surface, and the annotation is not yet identified |
| C. Give bulk the full record exports and let it subtract with its own annotation | no new child; the consumer owns the geometry it already owns | the guarantee te-tracks offers, exon-disjoint support under a declared mask, is not delivered; the consumer reimplements it without acceptance |

**Implications.** The recount question the owner set aside touches this: reproduction of the legacy numbers
runs on the compat universe, while going forward runs on `interspersed`, and a delta table between them is
the reconciliation record. Whichever route is taken, the identity rule holds that a consumer counts against
the annotation its child was built on, or documents a reconciliation.

**Caveats.** The bulk annotation's identity is a fact nobody has read yet; it is cheap to obtain from the
pipeline's own reference path. Until it is read, route B cannot be scheduled and route A is an assumption
rather than a decision.

**Recommendation.** Read the bulk annotation's digest as a fact now, the same way the ARC reference is being
read; then A if it matches vM37 closely enough that the mask outcome is unchanged for the subfamilies the
analysis reports, and B otherwise. Route C only as an interim, with the reconciliation stated.

### 4. When the deferred views arrive, and which first

**Premise.** Five things are deliberately absent and each is recorded with the evidence its next decision
needs: the same-strand mask companion, the record-by-transcript context relation, the instance block union
with record 5′ windows and LTR-internal candidate pairs and divergence bins, the 10x-annotation child, and
the instance-level STARsolo profile. The ruling is that the structural batch follows the host build, batched
into one later core snapshot, when a consumer names the need.

| route | gains | costs |
|---|---|---|
| A. Park as ruled, add the batch when a consumer names it | one host build, one retained baseline, no acceptance work for artifacts nobody reads yet | the first consumer to need a structural view waits for a build and a review loop |
| B. Add the context relation before parking | the origin question gets its geometry immediately, and it is the largest single gap | the relation is the biggest artifact the child will ever carry, at roughly 24 to 27 million pairs and 3.9 to 6.4 GB, and it needs its own scaling gate |
| C. Add the whole structural batch before parking | everything in one baseline | delays parking substantially for views whose parameters no analysis has yet chosen |

**Implications.** The context relation is the one deferral that touches the central hypothesis, because
intronic against intergenic against promoter-proximal is how host-carried signal is separated from
autonomous signal. It is also the one a consumer can derive for itself, by intersecting our record intervals
with its own annotation, which is precisely the operation its own counting already performs. So its absence
costs convenience and acceptance, not capability.

**Caveats.** A consumer deriving context itself will do so without our registration, so its labels will not
join to anyone else's. That is the cost of route A and it should be stated in the parking handoff rather
than discovered.

**Recommendation.** A, unchanged, with the parking handoff stating plainly that context is derivable from
the published intervals and that a derived label does not join across analyses until the relation ships.

### 5. What happens when the literature tier and Dfam disagree

**Premise.** The owner ruled the working age tier to be the literature name lists, with a later manual check
against Dfam. The 9a view publishes each matched model's clade path and a compatibility status, and the
disagreements are already visible: 31 mouse names carry a model with a primate branch, 26 names have no model
at all, and 147 resolve only through part models.

| route | gains | costs |
|---|---|---|
| A. The literature list is the tier; Dfam disagreement is recorded beside it and reported | the tier is what reviewers know, and the disagreement becomes a measurement | two vocabularies in every table a reader sees |
| B. Dfam clade is the tier; the literature list becomes a documented alias | machine-derivable and consistent across assemblies | a mouse name matched to a primate-assigned model has no defensible tier, so the exceptions need their own rule anyway |
| C. Reconcile once by hand and publish a single merged tier | one column for a reader | the merge is a judgement that will need revisiting, and it hides its own basis |

**Implications.** This is a consumer-side policy in the ruled design, so te-tracks publishes both axes and
neither tier. What te-tracks owes is that the disagreement is visible per row, which the
`clade_compatibility` status and the per-rank statuses deliver.

**Caveats.** The join crosses library versions, a 2018 RepeatMasker library against Dfam 4.0, and no status
today says "same name, different model". That is the honest residual: a name can match and its model can
have changed shape underneath, and the only remedy is the per-name projection comparison that the structural
batch needs anyway for full-length denominators.

**Recommendation.** A, with the young-name list written as a cited alias set in the consuming layer, and the
per-name model-projection status added when the structural batch lands.

## 5. When te-tracks is parked, and what fraction of questions it answers

The owner's question is how soon the annotation satisfies eight or nine questions in ten that a single-cell,
single-nucleus, chromatin-accessibility or bulk dataset would ask of it. Answering it needs the question
classes enumerated rather than a number asserted.

| question a consumer asks | served by the parked state |
|---|---|
| how much TE RNA per subfamily, family or class, per sample or per cell | yes, every estimator, every namespace |
| how much per locus, at record grain | yes, four grammars and a registration that joins them |
| are counts from two different tools comparable | yes, through the registration and the four-field binding |
| which lineage, rank and clade a subfamily belongs to | yes, four Dfam tables with per-rank statuses |
| exon-disjoint support for a bulk gene-and-TE pass | yes, under the declared mask, on the annotation the child pins |
| unmasked features and a full gene annotation for a joint estimator | yes |
| which TE intervals overlap my peaks, with identities | yes, the complete-catalog record intervals |
| which families are enriched in accessible regions | yes, through the taxonomy and Dfam views |
| reproducing a count months later against the same bytes | yes, immutable archives, full ids, per-file digests |
| a stranger building and publishing it on a host | yes, once 9b's runbook lands |
| intronic against intergenic against promoter-proximal per record | derivable by the consumer from published intervals; not published, and a derived label does not join across analyses |
| relative strand to the host transcript | derivable; the same-strand mask companion is deferred behind a chemistry audit |
| divergence strata | queryable from the published per-record divergence; named bins deferred |
| which copies retain the model 5′ end | partly, from the published consensus coordinates; eligibility windows deferred |
| whether a molecule's 5′ end sits at a model 5′ end | no; needs the record 5′ windows or the consensus-space route |
| which insertion a group of records belongs to | instance identities are published as a grouping hypothesis; reconstruction is deferred |
| whether a copy is structurally intact | no; needs the structural batch and a validated model projection |
| how to avoid double-counting overlapping records | documented and measured at 8.07 percent; the deduplicating rule is the consumer's |

Ten of eighteen are served outright, four are derivable from what is published with our identities, and four
are genuinely absent. So the parked state satisfies roughly four questions in five as delivered, and about
nine in ten if a consumer is willing to derive context and strand geometry itself from the intervals we
publish. The four absent ones are the structural and initiation questions, which is exactly where the
hypothesis's sharpest claim lives, and they are absent by ruling rather than by oversight, each with its
gate written down.

**Timing.** The remaining work is a sequence of delegated units with a review after each, and the only step
outside the container is the host build.

| step | state |
|---|---|
| phase 9a second fix, five advisories | running |
| verify it, commit phase 9a whole | after it returns |
| phase 9b: acceptance suite, runbook, consumer map, parking handoff | prompt written; the acceptance build alone is about fifty minutes |
| Opus review of 9b, rulings, fix | prompts from the templates |
| milestone 9 seam review: can a stranger build it and use it | prompt written |
| parking pass: fixtures, comments, suite concurrency, the README narrative | prompt written |
| Opus review of the parking pass | template |
| claim validation, three units in parallel over the rewritten prose | template written |
| umbrella pin bump | minutes, at the milestone |
| host build and publication, then verification of the published bytes | the owner's step |

In-container that is on the order of twelve to eighteen hours of mostly delegated wall clock, which is one
more working session rather than several. The gate on calling it parked is the owner's host build, because
the reference cache is read-only inside the container by design.
