# Open items before phase 8: biology, premises, routes (orchestrator, 2026-09-17)

The owner asked for a re-orientation in the biology behind the twelve open items of
`adr_rulings_2026-09-17.md` ("Open questions carried to the next session"), for the premises and pain
points the programme is weighing, and for each item the premise, the routes, their tradeoffs,
implications and caveats. Sources: the rulings file, `gene_context_adr_brief.md`,
`field_practice_synthesis.md`, the three consults (`mask_policy_consult.md`, `loci_gtf_consult.md`,
`structural_views_consult.md`), plan 18, and two measurements made for this file (section 3, item 1).
Nothing here is a ruling; the recommendations are the orchestrator's.

## 1. The biology we stand on

**A record is an alignment.** RepeatMasker scans the mm39 assembly with a library of consensus models,
one per subfamily, and reports every stretch of genome that matches a model: which model, where, on
which strand, how far the copy has drifted from the model, and which part of the model the stretch
covers. te-tracks calls one such row a record. mm39 has 5,320,771 records; 3,764,949 of them form the
`interspersed` universe (LINE, SINE, LTR, DNA and the small RC, Retroposon and unclassified groups).
Because a record is an alignment it carries the model's coordinate system: `consensus_start_1` is the
model base at which the genomic copy begins, and `divergence_pct` is the copy's distance from the model.

**Records, insertions and instances.** A transposition event leaves one contiguous piece of DNA. Over
millions of years that piece is truncated, interrupted by later insertions, and matched piecewise to
different models, so one insertion is often several records. RepeatMasker groups records it believes
descend from one element under an instance id; 445,649 instances hold more than one record. The instance
id is a starting hypothesis for "one insertion" and it errs in both directions: fragments of one provirus
can carry different instance ids, and one instance can hold records with different names or strands.
Every "per locus" count in the field is a count per record; every biological statement is about
insertions. That gap is the largest single source of confusion in this programme.

**The hierarchy.** RepeatMasker labels each record with three tokens: class (LINE, SINE, LTR, DNA),
family (L1; B1 spelled `Alu`; ERVK; ERVL-MaLR; hAT-Charlie) and name, which the field calls the
subfamily (L1MdA_I, B1_Mus1, IAPEz-int, RLTR10). A subfamily is a consensus model, hence a lineage of
copies descended from one active source element in one period. Dfam holds a deeper lineage per model
(for B1: L1-dependent retroposon, SINE, 7SL-RNA promoter, Alu branch) and models L1 as three parts where
RepeatMasker uses one whole-element name. The dissertation's five ranks and Wicker's scheme are
vocabularies laid over these lineages; the tools materialize only the three tokens.

**Why aging counts TEs.** As I read the programme, the hypothesis is derepression: with age the
heterochromatin over TEs relaxes, young L1 and ERV copies transcribe, and their RNA or reverse-transcribed
cDNA feeds innate sensors such as cGAS–STING and the interferon axis; rapamycin and methionine restriction
are candidate suppressors. The claim that matters is therefore autonomous transcription of a TE from its
own promoter. The measurement sees TE-associated RNA of every origin: a TE inside an intron carried by a
host pre-mRNA, a TE exonized into a host transcript, a TE past a gene's end picked up by read-through,
and a TE transcribed from its own LTR or 5′ UTR. Separating those origins is the whole difficulty, and
nuclei make it harder: in the 14761 GEX window 55% of reads are intronic against 20% in the whole-cell
arm, so intronic TE signal there is mostly host pre-mRNA background.

**Where the promoters are.** A full L1 is about 6 to 7 kb with its promoter in the 5′ UTR; most copies
are 5′-truncated because reverse transcription stops before the RNA's 5′ end, so a copy that starts deep
inside the model has no promoter of its own. In mm39, 588 of 877,139 L1 records begin at model base 1;
the young mouse subfamilies L1MdA, L1MdTf and L1MdGf hold the polymorphic, still-active copies. An ERV
provirus is LTR, internal region, LTR, with the promoter in the LTR; recombination between the two LTRs
leaves a solo LTR that can still act as a promoter or enhancer. RepeatMasker models LTR and internal
regions separately, so a provirus is at least three records, and a naive "LTR without a same-instance
internal" rule calls 722,280 solo LTRs, which is why the field reconstructs proviruses before naming them.

**Why the RNA is hard to count.** Copies of one subfamily are near-identical, so a read from one copy
aligns to many; the aligner either drops the read as mapping to too many loci or reports a list of
alternatives, and an expectation–maximization step then distributes each read over its alternatives.
Close to half of repeat sequence lies inside gene bodies, so a read there has a competing explanation.
10x reads are short and end-biased (3′ in the Multiome GEX, 5′ in the OCM whole-cell kits), and cellranger
keeps one alignment per read even for multimappers, so every EM route starts with a STAR re-alignment
that keeps the alternatives. No published method resolves intronic TEs; in the dissertation's benchmark
every tool scored near zero there.

**Genic context.** Whether a TE is exonic, intronic, promoter-proximal or intergenic depends on which
gene annotation, which isoform, which strand and which distance rule. GENCODE vM37 has 278,369 transcript
models for 78,317 genes; the 10x 2024-A reference has 125,556 transcripts of 33,696 genes after filtering
to protein-coding, lncRNA and IG/TR types. No counting tool writes such a label; cellranger's per-read
E/N/I tag and peak annotators' nearest-gene labels are the closest analogues. In the counting tools,
context is a gene-model choice at counting time (exon-only competition or full-span competition), never
an output column.

**ATAC.** The ATAC arm sees accessible DNA as Tn5 cut sites; a TE is accessible when cuts fall inside
its interval, and TE-derived enhancers and promoters appear as peaks over LTRs and young L1 5′ ends. The
reference need is the record interval catalog with identities (the `all_rmsk` record BED) and, later, the
geometry relation; peaks, motif scans and TF inference are the ATAC framework's own pinned inputs (C1).

## 2. Premises and pain points

1. **The reference stops where interpretation starts.** te-tracks projects RepeatMasker into identities,
   intervals and joins. A geometric fact under a declared parameter (distance to a transcript start, bases
   retained after an exon mask, an LTR within 1 kb of an internal record) is reference. A verdict that
   needs a biological threshold or assay reads (promoter-intact, solo LTR, young, intronic) is analysis.
   The owner's "one component, one thing" is the ruling form of this premise (C3, C5, C11). The pain:
   consumers want the verdicts, and some tool formats force a verdict into the file; a GTF `gene_id` is a
   grouping decision.

2. **Every input is a release, and parity is a hard requirement.** The RepeatMasker run, the GENCODE
   release, the Dfam release, the 10x reference and the tool versions all move. The design answers with
   immutable snapshots pinning every input by digest (`BUILD_ID`, `CATALOG_ID`, parent pins, GTF md5) and
   with the owner's rule that a consumer counts against the annotation its child was built on. The pain
   is multiplication: three single-cell datasets and one bulk dataset already imply two or three gene
   GTFs, hence two or three children, each with acceptance work.

3. **Three units, one word "locus".** The field reports subfamilies, estimates at records and reasons
   about insertions. Each tool builds its competitor from a different key: Stellarscope from the
   attribute it is told, IRescue from the BED name, TEsingle from a four-field tuple, TElocal from each
   row, STARsolo from `gene_id`. te-tracks carries record, instance and subfamily identities side by side
   and registers every emitted feature id back to records, so any tool's output can be joined and
   compared; reconstruction of insertions waits for a consumer that names the need.

4. **Ambiguity is the data.** Multimapping and gene overlap are properties of the biology, and two
   paradigms handle them: exclude ambiguous support before counting (the exon-subtracted SAF for bulk
   featureCounts), or keep every candidate and let a model allocate (the EM routes over full intervals
   with the full gene GTF). te-tracks serves both and says which file serves which. The guarantee it can
   give is exon-disjoint sequence support; molecule exclusivity is a property of the counting run.

5. **Enumeration decides answerability.** Anything enumerated can be filtered down; anything left out
   cannot be filtered in. A window never enumerated, an export never built, a name never queried against
   Dfam: each is a question a consumer cannot ask later without a new build. Envelopes therefore err
   wide, within cost.

6. **Cost lives in acceptance.** Bytes are cheap next to what each artifact requires: an identity, a
   registration, fixtures that break on mutation, documentation and a review loop. The payload moves from
   10.5 to 15.3 GB per build if C8 lands; the acceptance work for six new files is the real budget. Hence
   "batched into one later snapshot" and "when a consumer names the need".

7. **Verified means run.** A parser check proves a tool's own reader accepts our file; an execution gate
   proves the tool's binary counts what we expect. The IRescue oracle shows that even our expectation of
   a published tool can be wrong. Until the binaries run somewhere, every execution claim stays
   "unsupported", visibly.

8. **The replication structure decides what may be claimed.** Twenty animals in two tissues license
   TE-level tests with tissue pairing; one pooled library per condition licenses description. The
   reference is silent on this; the pipeline contract must say it, and the reporting tiers are the place.

## 3. The open items

### 1. C4: the context envelope

**Premise.** The context relation pairs records with transcripts and stores geometry per pair: exon,
intron and UTR overlap, relative strand, signed distance to the transcript's start and end. A pair gets a
row for one of three reasons: the record overlaps the transcript body; the transcript is the record's
nearest start, end or exon edge on its contig; or the record falls in a window U bases upstream to D
bases downstream of the transcript's annotated start. Only the window has a parameter to rule, and it
decides which non-overlapping neighbours are recorded at all.

Two facts measured today sharpen the choice. The downstream side D adds pairs only for transcripts
shorter than D, because downstream of a start is inside the body for any longer transcript and body
overlap already yields the row. And a share of annotated starts are cDNA ends flagged incomplete.

| GTF | transcripts | shorter than 2 kb | shorter than 10 kb | `mRNA_start_NF` |
|---|---:|---:|---:|---:|
| vM37 | 278,369 | 60,563 | 155,093 | 7,247 |
| 10x vM33 filtered | 125,556 | 19,021 | 62,874 | 7,165 |

Chr1 pair counts and the genome extrapolation (structure consult Q1):

| envelope | chr1 pairs | added over no window | genome estimate |
|---|---:|---:|---:|
| none | 1,412,484 | 0 | 19.9 M |
| 1 kb up, 100 bp down | 1,431,274 | 18,790 | 20.2 M |
| 2 kb up, 200 bp down | 1,455,699 | 43,215 | 20.5 M |
| 10 kb up, 2 kb down | 1,714,112 | 301,628 | 24.2 M |
| 20 kb up, 2 kb down | 2,073,944 | 661,460 | 29.2 M |

**Routes.**
- No window: body and nearest rows only. Cheapest; "distance to the nearest gene" stays answerable for
  every record; "all transcripts within X kb" is lost.
- Narrow, 2 kb upstream: matches common promoter definitions; a 5 kb or 10 kb upstream question is
  unanswerable afterwards.
- Wide, 10 kb upstream and 2 kb downstream: covers every promoter definition in use by filtering on the
  stored distance; about a fifth more pairs than the no-window relation; 3.9 to 6.4 GB.
- Wider, 20 kb: enumerates all transcripts within the bulk 20 kb adjacency distance rather than the
  nearest gene; nearly half again as many pairs.

**Implications.** The envelope is part of the child's policy bundle, so a change mints a new snapshot.
Narrower is free afterwards; wider costs a rebuild. Storage scales with pairs, and the relation is the
largest artifact the gene child will ever carry.

**Caveats.** A window is a candidate envelope around an annotated start, and the annotation is a model of
transcription: alternative starts, tissue-specific promoters and unannotated starts are absent, and the
starts flagged `mRNA_start_NF` should carry that flag into the relation so consumers can drop them.
Windows sit on starts only; a TE just past a transcript's end, where 3′ read-through lands, is covered by
the nearest-end rows alone, so a TES-side window is a possible later addition if the 3′ Multiome pilot
needs it. Experimental start sets (FANTOM5 CAGE, EPDnew, ENCODE cCREs) are later pinned inputs of other
snapshots. Motif position is downstream.

**Recommendation.** 10 kb upstream, 2 kb downstream; carry `mRNA_start_NF` and `Ensembl_canonical` per
transcript; leave a TES window to a later snapshot with a named need.

### 2. C11: structural views, boundary and ordering

**Premise.** Four views are pure functions of catalog columns under declared parameters: the block union
of an instance's records with gaps preserved; the first N bases of a record in its own orientation,
eligible when the record covers the model's prefix within a tolerance; LTR–internal candidate pairs by
family, strand and gap; divergence bins. Each answers a structural question the biology asks (is this copy
full at its 5′ end, is this LTR part of a provirus, how diverged is this copy) with geometry alone.

| view | measured shape | what it cannot settle |
|---|---|---|
| instance union | 3,152,636 features, 3,688,115 blocks; 23,244 mixed-strand, 30,569 mixed-name | that an instance is one insertion |
| record 5′ windows, L1, tolerance 0 / 10 / 100 bp | 588 / 2,342 / 11,226 eligible records | promoter integrity; host read-through |
| LTR–internal pairs, gap 1 kb / 5 kb | 93,660 / 237,375 pair rows; at 5 kb 181,443 cross instance ids | that a pair is one provirus |
| divergence bins, L1, 5 / 10 / 20 / 30 % | 114,620 / 126,951 / 215,551 / 326,832 / 93,185 records | age or activity |

**Routes on the boundary.**
- Geometry with status columns and neutral names: `same_instance`, `adjacent_same_family`, `unpaired`,
  `ambiguous` for pairs; eligibility with N and tolerance for windows; bins by pinned thresholds.
  Consumers make the calls.
- Geometry plus labels such as `solo_LTR`, `full_length`, `young`: convenient, and wrong often enough to
  mislead; the naive solo rule calls 722,280.
- Nothing from te-tracks, consumers compute from the parquet: fastest, and every consumer reinvents the
  geometry without identities or acceptance.

**Routes on ordering.**
- After the host build, batched into one later core snapshot: one baseline retained, one review loop,
  views built when a consumer names them; the pilot queries divergence from the parquet meanwhile.
- Into phase 9 now: delays the host build and the umbrella pin for consumers that are months away.
- One build per view: each retains a fresh 10.5 GB baseline.

**Implications.** Every view changes `BUILD_ID` and keeps `CATALOG_ID`. The instance view cannot express a
mixed-strand instance as one BED12 or GTF transcript; those stay in the table with an
unsupported-transcript status. An instance GTF meets TEsingle's four-tuple collapse and TElocal's row-wise
competitors, so its grammar must be tested against both. Pairs at 5 kb offer many alternatives per LTR;
precision is unmeasured until a sequence-based reconstruction (the field's target is Bailly-Bechet's "One
code to find them all") is compared.

**Caveats.** Divergence is distance to the consensus under this RepeatMasker run; rate variation and model
choice make it a ranking rather than a clock. Model-prefix coverage says the promoter region is present in
the copy and says nothing about its sequence integrity. Same-family adjacency in broad families such as
ERVK can pair LTR and internal models that are incompatible.

**Recommendation.** Geometry only with status columns; after the host build, batched; the first view is
chosen by the first named consumer (record 5′ windows for the 5′ whole-cell arm, or the instance union for
locus counting).

### 3. Which GTF the child pins first

**Premise.** The gene child is one snapshot per gene annotation. Three annotations are live: GENCODE vM37
(the refcache pin and the phase 8 acceptance fixture); the 10x 2024-A GTF (GENCODE vM33 filtered to
protein-coding, lncRNA and IG/TR; what cellranger counted the three single-cell datasets with; verified
from the owner's download); and whatever the bulk pipeline of 18439-DM used (an nf-core filtered GTF,
unverified). The ARC reference's GTF is presumed equal to the GEX one and unverified.

| | vM37 | 10x vM33 filtered |
|---|---:|---:|
| genes / transcripts / exon rows | 78,317 / 278,369 / 1,298,921 | 33,696 / 125,556 / 834,423 |
| exon union | 160.5 Mb | 114.0 Mb |
| unstranded mask, bases removed from `interspersed` | 26.2 Mb | 15.4 Mb |
| records fully removed | 96,119 | 65,841 |
| `interspersed` records whose mask outcome differs between the two | 74,464 | |

**Routes.**
- vM37 first: acceptance numbers are pre-measured; the mask is the more conservative one, since pseudogene
  and small-RNA exons are masked too; consumers who counted with 2024-A reconcile by the C5 rule.
- The 10x GTF first: exact parity with the gene matrices the datasets already carry and with the
  recommended STARsolo index; the smaller mask returns about 30,000 records the vM37 mask removes;
  phase 8 acceptance must be re-measured on it.
- Both, as two snapshots: the child is small next to the core (six SAF files and a status table per
  policy), so the cost is acceptance and bookkeeping, and both consumers are served.

**Implications.** Whatever is first, the STARsolo re-alignment should index the 10x GTF so gene counts stay
comparable to cellranger's, which makes the 10x child the one the RNA pilot needs. The bulk recount (item
11) needs a child on the bulk GTF, or the owner's own subtraction over the full record BED. Each child pins
its GTF by digest and its parent by full `BUILD_ID`.

**Caveats.** The ARC GTF can be verified cheaply: the 14761 BAM header's program line records the reference
path used on the host, and `reference.json` and `genes/genes.gtf` sit there if the directory survives.
"Filtered" means 10x's biotype filter with versionless ids; TE-derived pseudogene exons are unmasked under
it, consistent with a gene pass that ignored them.

**Recommendation.** vM37 in phase 8 as planned; the 10x child as the first phase 9 or post-host item,
admitted with the GTF as a pinned source; verify the ARC GTF from the run's reference path before the
14761 pilot; decide the bulk GTF child when the recount is scheduled.

### 4. C7 details: ownership, STAR recipe, reporting tiers

**Premise.** Three routes are ruled: IRescue for conservative subfamily counts, TEsingle as the modern
gene/TE joint estimator, Stellarscope evaluated for loci, all on one STARsolo re-alignment. Open are who
qualifies the tools, which alignment recipe is pinned, and how claims are tiered.

**The recipe.** Two STAR parameters decide which alignments exist before any estimator sees them: the cap
on reported loci per read, above which the read is discarded as unmapped, and the cap on anchor loci
during seed search, which must be at least as large for the aligner to find those loci.

| source | loci cap | anchor cap |
|---|---:|---:|
| IRescue README | 100 | 100 |
| dissertation text | 100 | 150 |
| TEsingle scripts (Martirosyan and benchmark) | 100 | 200 |
| Stellarscope protocol | 500 | unspecified |

Routes: pin 100/200 as the published TEsingle recipe; 100/100 as the IRescue minimum; 500 as
Stellarscope's. The tradeoff: a cap of 100 discards reads from the highest-copy subfamilies, which are the
young ones the hypothesis is about, while 500 keeps them and spreads them thin across alternatives with
larger BAMs. The pilot should measure cap saturation, the share of reads reported at exactly the cap. One
recipe for all three tools, so differences between routes are estimator differences.

**Ownership.** Routes: te-tracks keeps parser fixtures and records each tool's limits while the consuming
toolkit (the owner's TE-RNAseq toolkit or a satellite) owns executable qualification and any pinned fork;
or te-tracks owns qualification end to end; or 14761-DM's D2 owns it. A fork is quantification code,
outside te-tracks' declared scope, so the first route follows the scope rule.

**Reporting tiers.** Cross-tissue replicated: the same subfamily or locus moves in the same direction in
spleen and lung across the four animals per condition. Single-tissue replicated: four against four animals
in one tissue. Multiome descriptive: direction and effect size, no p-value, one library per condition.
te-tracks carries none of this in code; the D2 and D3 contracts do. At record grain across 3.7 million
loci a test has no power; subfamily is the tested rung and locus claims need unique support.

**Recommendation.** 100/200 pinned with saturation measured and 500 as a sensitivity run; qualification and
forks in the consuming toolkit; the three tiers as written.

### 5. Consumer executables

**Premise.** Parser checks run in the container and pass; execution gates need STAR, cellranger, IRescue,
Stellarscope, TEsingle, TEcount, featureCounts, gawk and duckdb, all absent, so they exit "unsupported".
Installing is the owner's word alone.

**Routes.**
- Install the pip and conda tools into the image (STAR, subread, gawk, duckdb, irescue, TEsingle, TElocal,
  TEtranscripts, stellarscope) at pinned versions recorded in te-tracks: execution gates run in every
  review loop; the image grows; versions must be pinned and recorded.
- Run the execution gates on the host at publication: no image change; manual and outside the loop; the
  IRescue oracle and the C8 GTF acceptance wait for a host session.
- A consumer-qualification container of the TE-RNAseq toolkit mounting te-tracks fixtures read-only:
  quantification tools live where quantification lives; a second image to maintain.
- Leave unsupported: the pilot becomes the first execution.

**Implications.** Cellranger is a licensed download of about a gigabyte and belongs on the host in any
route. Until STAR runs, "STARsolo counts one locus per record from `record_starsolo.gtf`" and "cellranger
accepts pipe characters in `gene_id`" are unproven, and item 6 cannot close.

**Recommendation.** The light tools into the image at pinned versions; cellranger as a host gate.

### 6. The IRescue oracle

**Premise.** The executable fixture feeds four molecules unique to A, two unique to B and three ambiguous,
and expects 6 and 3, which assumes the ambiguous molecules follow the unique evidence two to one.
IRescue's code, called in isolation, gives 5.5 and 3.5: unique counts are fixed, the EM runs over the
ambiguous molecules alone from a uniform start, and with every ambiguous molecule sharing the same two
candidates the EM has no information and stays even. That is the mechanism behind "conservative": unique
support is exact, ambiguous support is spread without evidence, and a subfamily with strong unique support
is under-credited for its ambiguous share.

**Routes.**
- Rewrite the oracle to the tool's behaviour once the binary confirms it: the fixture then documents
  IRescue's contract.
- Keep 6 and 3 and mark IRescue as deviating: the fixture would document a preference for how a counter
  should behave, which is outside te-tracks' role.
- Redesign the fixture with heterogeneous ambiguity so that uniform and unique-seeded starts converge
  differently and the test discriminates the algorithm.
- Wait for the binary before touching anything.

**Implications.** The fixture is a test file, so a codex unit changes it after the binary rules. The
finding also fixes IRescue's role in C7: subfamily counter, with locus mode as a sensitivity only.

**Caveat.** The consult exercised the counting functions and not the mapping step, whose gawk dependency
is absent; the binary may add a deduplication that changes the arithmetic.

**Recommendation.** Wait for the binary (item 5), then rewrite the oracle to the observed contract with the
mechanism stated in the fixture's docstring.

### 7. Stellarscope as a pinned corrected consumer

**Premise.** Stellarscope is the field's locus-level ERV tool. Its checkout stores GTF intervals as 1-based
inclusive with one added to the end and queries 0-based half-open read blocks with one added to their end
as well, so the base right after a feature gains a false one-base overlap (presence 0,1,1,1 where 0,1,1,0
is right). Before EM it picks one feature per alignment by largest overlap above a strict 20% threshold,
so an alignment overlapping two features contributes to one; its `union` and `intersection-strict` modes
are stubs; one-base gaps merge.

**Routes.**
- Pin a corrected fork for the boundary and document the preselection: known behaviour, a research fork
  to maintain.
- Use upstream as is, defects recorded, locus counts as sensitivity only.
- Drop it in favour of TEsingle and STARsolo for loci: loses the published ERV-focused comparator that
  reviewers know.

**Implications.** A one-base false overlap rarely passes the threshold for a long read, so the defect
matters at boundaries and for short blocks; the preselection is the larger issue because it is a hard
assignment before EM, which means Stellarscope's EM resolves multi-alignment ambiguity only. Any ERV locus
claim leaning on it needs the fork or the caveat in print.

**Recommendation.** A small pinned fork owned by the consuming toolkit; evaluation route per C7.

### 8. C10 details: rank scheme, scope, L1 rule

**Premise.** The Dfam 4.0 census covers the 1,220 `interspersed` names.

| class | names | exact hits | records under exact names |
|---|---:|---:|---|
| LTR | 630 | 609 | 1,076,099 of 1,105,064 |
| SINE | 37 | 36 | 1,486,191 of 1,495,172 |
| LINE | 198 | 49 | 47,256 of 976,368 |
| DNA | 293 | 291 | 160,386 of 160,425 |
| RC, Retroposon, Unknown, Unspecified | 62 | 62 | 23,553 of 23,553 |

143 of the 173 misses are L1 names Dfam models as `_5end`, `_orf2` and `_3end` parts; 21 are LTR `-int`
names with no result; the rest are scattered.

**Routes for the scheme.**
- Store the Dfam lineage as published, with accession and release: faithful and machine-readable; depth
  varies by branch, so there is no fixed "superfamily" position.
- Derive the dissertation's five ranks by a named rule per branch: readable, with exceptions recorded per
  rank.
- Wicker's scheme: the academic standard; Dfam emits no Wicker codes, so the mapping is hand-made.

**Routes for scope.** The 1,220 `interspersed` names first (ten minutes of API time, the counting
universe), or all 18,484 names (simple repeats, satellites and RNA genes are mostly inapplicable).

**L1 rule.** A whole-element name maps to the set of its part models; the lineage is read from any part;
the accession column holds the set; the row's status says `part_model_set`.

**Implications.** No count changes; the view serves grouping and reporting (all MaLR, the Alu branch). It
changes `BUILD_ID` and keeps `CATALOG_ID`. Dfam is CC0, so redistribution is clean.

**Caveats.** The RepeatMasker run used a 2018 library; names may have merged or been renamed since, and the
21 `-int` misses are likely models absent from Dfam. Some names return several hits and need an accession
choice. The API is live, so the pinned artifact is the stored responses with the release string.

**Recommendation.** Store the lineage as truth; derive `rank_scheme_v1` with per-rank status as a named
derivation; `interspersed` names first; the L1 part rule as stated.

### 9. Phase 9 additions as a set

**Premise.** Phase 9 was acceptance and parking. The discussion accrued: the C8 export (roster 24 to 27,
payload 10.46 to 15.30 GB), the C9 binding rule with a join fixture over both universes, the C10
label-surprise and constant-flag notes, a failed-build cleanup case, the RNA qualification limits in the
parking handoff, and the retention budget.

**Routes.** Admit the set with C8: one host build carries the STARsolo profile and no second core baseline
is retained soon after. Defer C8 to a later core snapshot: the host build stays at 10.5 GB and a second
10.5 GB baseline follows within months. Split phase 9 into two implementer units (documentation and
fixtures; export and acceptance) to respect the per-phase context budget.

**Implications.** The host retention policy (how many builds are kept) must be set with the 15.3 GB figure.
The new export's acceptance numbers are pre-measured: 3,764,949 rows and distinct gene ids per namespace,
59 contigs, zero id collisions with the 10x GTF, about 1.616 GB per namespace.

**Recommendation.** Admit the set with C8; split the implementer unit in two.

### 10. The decisions record

**Premise.** Entries land in `docs/DECISIONS.md` only by ruling, through a codex unit. Routes: write the
ruled items now and add C4 and C11 later, or write everything once C4 and C11 close.

**Implication, and a correction of the orchestrator's earlier statement.** C4 parameterizes the context
relation, which ships after the host build while phase 8 declares context `not_computed`; C11 is a later
core snapshot. Neither gates phase 8. What gates phase 8 is the decisions unit for the ruled items and the
GTF choice of item 3. The entries can be written now with C4 recorded as a deferred parameter and C11 as a
deferred view, and phase 8 can open.

**Recommendation.** One unit now for C1, C2, C3 with C5, C6, C7, C8 scope, C9 and C10, with C4 and C11 as
deferred entries completed by ruling.

### 11. The 18439-DM recount

**Premise.** The bulk dataset was counted on the legacy SAF, exon-subtracted with the bulk pipeline's own
GTF. The redesign changed the universe: `compat_tetranscripts_mm39` keeps the legacy membership
(3,799,629 records) for reproduction; `interspersed` is the go-forward set (3,764,949).

**Routes.** Recount on compat with the child's exon-subtracted SAF, which is the phase 9 reconciliation
against the legacy numbers; recount on `interspersed`; or both and report subfamily-level deltas.

**Implications.** The recount needs a child on the bulk GTF, or the owner's own subtraction over the full
record BED; that decides whether a third GTF pin is needed (item 3). The recount is downstream work.

**Recommendation.** Both universes, once a child exists on the bulk GTF; the delta table is the
reconciliation record.

### 12. The umbrella pin

**Premise.** The umbrella pins te-tracks at the milestone 7 commit `6bf9a22`; the record commits since sit
above it. Routes: bump now, or at milestone 9 per protocol. Implication: none for the build; one umbrella
commit either way, no push. **Recommendation.** Milestone 9, unless a collaborator reads the umbrella
meanwhile.

## 4. What blocks what

Phase 8 needs the decisions entries for the ruled items (item 10) and the GTF choice (item 3). C4 and C11
gate later snapshots. Items 4 to 8 gate the RNA pilot and the phase 9 fixtures. Items 9 and 10 are the
next two orchestration units. Items 11 and 12 follow the host build.
