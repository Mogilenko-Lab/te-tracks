# ADR discussion: the owner's rulings and the open items (2026-09-17)

The owner ruled on the candidates of `gene_context_adr_brief.md` after the orchestrator's elaboration. This
file records the rulings in the owner's terms, what each changes in plans 18 and 19, and the items still
open with the consult unit assigned to each. Entries in `docs/DECISIONS.md` follow from the ruled items
through a codex unit once the open items are ruled as well.

## Ruled

**C1 (one gene family, immutable snapshots): adopted.** The compat universe stays for now; the owner will
recount 18439-DM on the updated universe or universes. Owner's question under C1: whether ATAC introduces
its own annotation, motif notion or database dependency at this level. Orchestrator's answer, recorded for
the plan: the ATAC side consumes the core's record intervals and the child's geometry; peak sets are the
dataset's own annotation; motif databases (JASPAR, CisBP, the cisTarget snapshot already in
`/data2/users/shared/refcache/cistarget`) are a separate pinned input belonging to the ATAC framework
downstream. If te-tracks ever publishes motif content on TE consensus sequences, that is another child
family with its own inputs under the same rule; nothing of it enters phase 8.

**C3 (context representation) and C5 (who labels): te-tracks publishes geometry only; consumers derive.**
Owner's words: the intronic versus intergenic distinction is a downstream problem of the ATAC dataset; the
annotation repository should not carry that background knowledge; one component is responsible for one
thing and the downstream analysis bends to it where needed. Consequence: context stays `not_computed` in
phase 8; the relation arrives in a later snapshot after the chr1 then mm39 scaling gate; no convenience
label view (C5 option A); status per record × transcript pair with a per-record roll-up when the relation
ships; the ledger keys become `te_catalog_id` plus `te_build_id`. All three datasets are GRCm39, the same
assembly as mm39 under another naming; the alias table covers the names and the assembly check refuses
any other build.

**C6 (alias table copied into the child): confirmed.** Gene models are GENCODE, which is the Ensembl gene
set with GENCODE tags (`gencode.vM37.primary_assembly.annotation.gtf.gz`); RefSeq enters only as a contig
alias column and as the human T2T annotation of the TEsingle paper, outside scope.

**C7 (RNA route): STARsolo re-alignment; IRescue as the conservative published method; TEsingle as the
modern method; Stellarscope evaluated for loci.** Pilot order: 14761 RNA first (retain the cleaned barcode
universe; audit `CB`/`UR` and retained alternative alignments; decide BAM reuse versus FASTQ re-alignment;
validate strand and molecule handling; quantify subfamilies with IRescue; evaluate a locus configuration
against unique support and Stellarscope; TEsingle as a gene/TE-assignment sensitivity analysis with barcode
eligibility changes reported). Separate TE-associated RNA from evidence of autonomous transcription. ATAC:
coordinate overlaps and direct counts from existing fragments over TE intersections, TE sequence and
defensible promoter regions, under the stage-10 counting contract, no double shift, no custom ATAC EM at
first; a later multimapper-rescue branch needs an explicit measurement model and an independent simulation
benchmark. Fixtures and a small full-genome-background simulation panel (identical loci, host pre-mRNA,
nested repeats, duplicate molecules, 3′ versus 5′ capture, paired-end ATAC), family and locus accuracy
reported separately. Publication tests: failed builds, same-day rebuilds, stale manifests, concurrent
publication, resolution of archived `BUILD_ID`s. Sequencing: te-tracks is finalized first; D2
(`14761-DM/.../2026-09-11_codebase-topology/02_next_session_agenda.md`) resumes afterwards. Dataset roles:
14761 identifies accessible sequence, repeat annotation, motif sites, candidate TFs, linked genes and
independently quantified TE-associated RNA with the model source visible; 14616 establishes which TE and
gene-program changes reproduce across mice; 14782 tests tissue-dependent RNA responses through the
spleen–lung pairing.

**C9 (binding rule names universe and variant): confirmed; document well.** Phase 9.

**C10 (rank vocabulary and Dfam): documentation note now, rank view as a later snapshot, with a
feasibility assessment of the Dfam route.** The orchestrator's probe on 2026-09-17: the Dfam API is
reachable from the container and reports Dfam 4.0 (May 2026; 30,621 curated families); of the ten most
abundant names per class, all ten LTR, SINE and DNA names hit exactly with a classification lineage, and
none of the ten LINE names did (Dfam models L1 as `_5end`, `_orf2`, `_3end` parts). The census of all 1,220
interspersed names (2026-09-17, Dfam 4.0 API, `format=summary`, 590 s, no errors) is kept at
`../taxonomy/dfam_census_1220_20260917.tsv`. Exact-name hits by class:

| class | names | exact | records | records under exact names |
|---|---:|---:|---:|---:|
| LTR | 630 | 609 | 1,105,064 | 1,076,099 |
| SINE | 37 | 36 | 1,495,172 | 1,486,191 |
| LINE | 198 | 49 | 976,368 | 47,256 |
| DNA | 293 | 291 | 160,425 | 160,386 |
| RC, Retroposon, Unknown, Unspecified | 62 | 62 | 23,553 | 23,553 |
| total | 1,220 | 1,047 | 3,760,582 | 2,793,485 |

The 173 misses hold 967,097 records; 143 of them are L1 names (of 149), and for all but one the API returns the
same name with a `_5end`, `_orf2` or `_3end` suffix, so an L1 mapping rule joins the RepeatMasker whole-element
name to Dfam's part models and lifts coverage to nearly every record. The remaining misses are 21 LTR `-int`
names with no result (`ERVL-B4-int`, `ERVL-E-int`, ...), 12 ERVK and 8 ERVL names, 5 L2, 1 CR1, 2 DNA
(`Tigger1a_Art`, `Tigger1a_Mars`) and `ID`. Feasibility: the route works from the container for the 1,220
interspersed names in about ten minutes; a full admission adds the release pin (the version endpoint reports
Dfam 4.0, May 2026), the L1 part rule, an accession choice for the names returning several hits, and explicit
states for the misses. The lineage strings returned (for example
`...;Class_I_Retrotransposition;...;Gypsy-ERV;Retroviridae;Orthoretrovirinae;ERV2-group;ERV3;MaLR` and
`...;L1-dependent_Retroposon;SINE;7SL-RNA_Promoter;No-core;L1-dependent;Alu`) place B1 under the Alu branch and
the MaLR groups under ERV3, which is the rank material the view would publish.

## Open, with the consult unit assigned

**C2 (mask policy).** Owner's position: every mask is defensible; the protein-coding choice has no
principled stop before all exons; the strand-aware mask is attractive and must be measured and compared
against the conservative one, per chemistry, and live beside it; an EM-facing option where a joint
algorithm decides gene versus TE membership should be understood; the TEsingle paper's intron-retention
estimate may be relevant. Unit `te-tracks-mask-consult` → `mask_policy_consult.md`.

**C4 (promoter windows).** Owner's concern: promoter position may be annotation- and biology-sensitive;
which database, and where motifs map. Unit `te-tracks-structure-consult` → `structural_views_consult.md`
(section on host-promoter windows and TSS sources); motif mapping is downstream by the C1 ruling.

**C8 (loci GTF for STARsolo).** Owner: a second loci GTF seems necessary; first understand how Stellarscope
and IRescue work locus-wise and what annotation they expect. Unit `te-tracks-loci-consult` →
`loci_gtf_consult.md`.

**C11 (structural views).** Owner asked for a simpler explanation; the orchestrator's plain-language
version is in the session's reply and is repeated in `structural_views_consult.md`'s brief. Unit
`te-tracks-structure-consult` measures the candidate views.

**C5 addendum (which GTF the child pins).** The owner downloaded 10x's current references to
`.ref/14839-DM-cGAS/01_modules/TE-RNAseq-toolkit/cellranger-refs/` (`refdata-gex-GRCm39-2024-A` and
`refdata-gex-GRCh38-2024-A`; the ARC reference is absent). The gene GTF is being extracted to
`_scratch/te-tracks-audit/refs/refdata-gex-GRCm39-2024-A/genes/genes.gtf.gz` as a read-only input for the
units. The owner's rule: the consumer uses the same annotation the child was built on, either by choosing
the matching snapshot, by te-tracks pre-building it, or by running the build for the annotation needed.
Consequence for plan 18: the GTF is a parameter of the child; phase 8 acceptance runs on vM37 and a second
snapshot pinned to the 10x GTF is a phase 9 or post-host-build item, ruled after the mask consult reports
how the two GTFs differ.

## Consult results for the open items (collected and verified 2026-09-17)

Three codex consults (gpt-6-astra, xhigh, read-only, `--parallel-ok`) ran against `9c27b14` and each wrote one
file: `mask_policy_consult.md`, `loci_gtf_consult.md`, `structural_views_consult.md`. All three left the tree and
the checkouts untouched and removed their scratch. The orchestrator recomputed the numbers marked "verified"
below; the others are the consult's own, each produced with an internal two-method agreement check.

**C2, mask policy.** Verified genome-wide with an independent bedtools run on the `interspersed` universe
(3,764,949 records, 1,116,605,808 bp):

| mask | removed bp | records fully removed | retained records | retained blocks |
|---|---:|---:|---:|---:|
| vM37 all exons, unstranded (the default) | 26,235,918 | 96,119 | 3,668,830 | 3,684,934 |
| vM37 all exons, same strand only | 15,109,933 | 50,044 | 3,714,905 | 3,724,927 |
| 10x vM33-filtered exons, unstranded | 15,361,040 | 65,841 | 3,699,108 | 3,704,889 |
| 10x vM33-filtered exons, same strand only | 8,152,002 | 32,384 | 3,732,565 | 3,736,001 |

The compat anchor reproduces (26,503,064 bp; 97,987; 3,701,642; 3,717,740). The strand-aware mask restores
11,125,985 bp over 76,971 records and returns 46,075 fully removed records to the SAF. The 10x GTF (GENCODE
vM33 filtered; exon union 114,032,813 bp against vM37's 160,549,642, verified) changes the unstranded mask
outcome of 74,464 interspersed records (consult). Protein-coding and basic masks remove 5,979,867 and
19,798,260 bp (consult). Intron-retention views: pure intronic 799,877,668 bp and pure exonic 68,441,203 bp
under vM37; 678,389,216 and 61,447,575 under the 10x GTF (consult). Source facts: TEsingle and STARsolo EM
need the full gene GTF and unmasked TE features; IRescue's interface takes a TE BED and no gene GTF.
*Recommendation:* phase 8 ships `all_exons_unstranded_union_v1` alone; `all_exons_stranded_union_v1` joins in
the first later snapshot beside it once the chemistry pilot has measured which mate is RNA-sense (the records
establish that both 5′ mates align and nothing more); protein-coding and basic stay measured alternatives; a
10x-GTF-pinned child follows in phase 9 or right after the host build; the two intron-retention BEDs are an
optional later view. Each extra policy costs six SAF files and about 7.5 M registration rows per grouping.

**C4, promoter windows.** Exact chr1 pair counts of the context relation (verified for the body-overlap
component, 921,233 pairs): (0,0) 1,412,484; (1000,100) 1,431,274; (2000,200) 1,455,699; (10000,2000)
1,714,112; (20000,2000) 2,073,944; chr1-density extrapolations 19.9 M, 20.2 M, 20.5 M, 24.2 M, 29.2 M against
the earlier contig-stratified estimates of 21.8 M, 22.5 M and 26.8 M, so capacity planning keeps the higher
figures. Any narrower window is recovered exactly from the stored signed distance. TSS and TES come from the
GTF transcript rows (278,369; 78,317 tagged canonical; no MANE tag in mouse). FANTOM5 CAGE, EPDnew and
ENCODE cCREs are later pinned inputs of other snapshots; motif scanning is the ATAC framework's, with the
cisTarget snapshot already in the refcache. *Recommendation:* (10000,2000) as the first context snapshot's
search envelope; consumers name their promoter policy.

**C8, loci GTF and consumer expectations.** Verified: the 10x GEX dictionary matches the `gencode` namespace
on all 61 names and lengths (22 for ucsc, 39 for ensembl); record alias against 10x gene and transcript ids
collide zero times; registration holds 35,440,363 rows, 3,764,949 in each interspersed group; the proposed
profile adds 399,450,554 bytes per namespace (alias bytes 144,863,897; name bytes 21,159,819), so 4.84 GB over
three namespaces and a payload of about 15.30 GB per build; TEsingle collapses rows with an identical
four-tuple into one competitor (`TEindex.py:252-275,329-364`) while TElocal keeps each row separate; the
Martirosyan and benchmark STAR scripts set `outFilterMultimapNmax 100` and `winAnchorMultimapNmax 200`.
Source facts from the consult: Stellarscope forms a feature from all rows sharing its `--attribute` (default
`locus`), merges overlapping rows per contig or contig and strand, also merges one-base gaps, and chooses one
feature per alignment by largest overlap above a strict 0.2 threshold before EM, with `union` and
`intersection-strict` unimplemented stubs; its boundary defect is a 1-based against 0-based half-open mix
giving overlaps 0,1,2,1 at the fixture; its protocol recommends `outFilterMultimapNmax 500`. IRescue treats
BED column 4 as an opaque id, never splits it, and carries class and family only when encoded in the id; a
custom BED bypasses its RepeatMasker conversion; the te-tracks exporter rejects `#` and `~` today. An IRescue
qualification item: isolated calls to its counting and EM code return 5.5/3.5 where the te-tracks executable
fixture expects 6/3 (unique support does not seed its EM); unresolved, for a later authorized unit.
Specification: `exports/<ns>/interspersed/full/record_starsolo.gtf`, one exon per record, `gene_id` =
`transcript_id` = `locus` = record alias, `gene_name` = `rmsk_name`, `gene_type "transposable_element"`, the
current provenance attributes kept; contract with `feature_identity = gene_id`; registration reuses
`(record, record_alias)`; export roster 24 to 27, payload files 43 to 46, `BUILD_ID` changes and `CATALOG_ID`
stays; fixture of five cases (two same-name records as two genes; gene–TE overlap allocation; gap-only read
zero; collision preflight; namespaces and endpoints). `instance_starsolo.gtf` deferred behind mixed-name,
mixed-strand, gap and junction tests. *Recommendation:* admit the record profile in phase 9 by scope
amendment with the STAR and CellRanger execution gates recorded unsupported in-container; until then a
pinned consumer transform with its digest implements the same specification.

**C11, structural views.** Verified: the interspersed instance block union has 3,152,636 features, 434,707
multi-record, 3,688,115 blocks, 263,926,042 gap bases, a largest gap of 24,679 bp, a largest span of 31,513 bp
and no span above 50 kb; the LTR–internal adjacency rule at 1,000 bp (same family, same strand, either
order) yields 93,660 pair rows, 58,755 LTR records with a partner, 34,194 newly partnered beyond the instance
id, 20,072 of the 103,526 internal-only instances gaining a flank and 21,853 triplet combinations; L1
divergence bins at 5/10/20/30% hold 114,620 / 126,951 / 215,551 / 326,832 / 93,185 records. Consult figures:
single-strand instance export eligibility 3,129,392 features and 3,636,088 blocks; record-end windows for L1
at tolerance 0/10/100 give 588 / 2,342 / 11,226 eligible records, young L1 146 / 686 / 3,601, class LTR
284,044 / 410,467 / 552,142; adjacency at 100 and 5,000 bp gives 37,834 and 237,375 pair rows, and at 5 kb
181,443 pairs cross instance ids and 54,834 LTR records have several internal partners. Costs per namespace:
instance BED12 about 328 MB or GTF 1.18 GB; end windows 35 MB to 1.6 GB; pair tables about 30 MB; the context
relation 3.9 to 6.4 GB. *Recommendation:* after the host build, batched into one later core snapshot;
divergence queries serve the 14761 pilot now from existing columns; all views publish support and candidate
status, never "promoter-intact" or "solo LTR" as labels; a universe schema 2 with a typed divergence range is
the path to bin universes.

**Corrections applied to the records from these consults:** `field_practice_synthesis.md` (STAR anchor values;
TEsingle four-tuple collapse) and `tesingle_notes.md` (same two facts).

## Second round (2026-09-17, later): rulings, explanations and the open list

**C2 (mask policy): ruled, agreed.** Phase 8 ships `all_exons_unstranded_union_v1` with `min_retained_block_bp
= 1` alone; `all_exons_stranded_union_v1` joins in the first later snapshot beside it, after the pilot has
measured which mate is RNA-sense for each chemistry; protein-coding and basic masks stay measured alternatives;
the two intron-retention region sets are an optional later view; the EM routes take the unmasked record
exports and the full gene GTF.

**C8 (loci GTF): scope agreed.** `record_starsolo.gtf` enters phase 9 by scope amendment (roster 24 to 27,
payload about 15.30 GB per build). The owner asked what three phrases imply; the answers are recorded here for
the next session:

- *"Execution gates recorded as unsupported in the container."* te-tracks has two kinds of consumer checks.
  Parser checks run a tool's own reading code against our exports inside the container and pass or fail.
  Execution checks run the tool's binary end to end on a fixture BAM. STAR, cellranger, IRescue, Stellarscope,
  TEsingle, TEcount and featureCounts are absent from the container, so every execution check exits 3,
  "unsupported", and the suite records that instead of a pass. For the new GTF this means shape, identity,
  registration and parser semantics are verified now, while "STARsolo counts one locus per record from it" is
  verified only when someone runs STAR on the fixture, on the host or after installing the binaries. Whether to
  install them is the owner's standing decision.
- *IRescue 5.5/3.5 against 6/3.* The te-tracks executable fixture for IRescue feeds a designed input, four
  molecules unique to feature A, two unique to B, three ambiguous between them, and expects A = 6 and B = 3,
  which assumes the ambiguous molecules are split in proportion to the unique support. The loci consult called
  IRescue's counting and EM functions directly and obtained 5.5 and 3.5: IRescue fixes the unique counts, runs
  its EM over the ambiguous molecules only, from a uniform start, and adds the result, so the three split 1.5
  and 1.5. Two implications. The fixture's expectation is probably wrong about IRescue's algorithm and will fail
  when the binary first runs, so a later authorized unit must settle the oracle against the executable. And
  IRescue's locus-level allocation of ambiguous molecules does not use unique evidence, which is why it is the
  conservative subfamily counter in C7 and not the locus resolver.
- *TEsingle collapses identical four-tuples, TElocal does not.* TEsingle turns every GTF row into a competitor
  named by `transcript_id:gene_id:family_id:class_id`; rows with the same four values become one competitor.
  te-tracks' `record.gtf` gives every record its own `transcript_id`, so nothing collapses today. The finding
  matters only for a later instance view that repeats one alias across the fragments of an insertion: TEsingle
  would then count the fragments as one feature, TElocal would keep them apart. It is a design note for C11
  and a documentation line, with no action in phase 8 or 9.

**C4 (promoter windows): still open; plain explanation recorded.** The context relation is a table. Each row
pairs one TE record, a genomic interval on mm39, with one gene transcript, also a genomic interval from the
GTF, and stores how the two relate: whether the TE overlaps that transcript's exons, introns or UTRs, whether
the two are on the same strand, and the signed distance from the TE to the transcript's start and to its end.
Which pairs get a row is the whole question. Every TE overlapping a transcript body gets one row per
transcript it overlaps (921,233 rows on chr1). Every TE also gets rows for its nearest transcript start, end
and exon edge on its contig, however far away, with ties kept, so "distance to the nearest gene" is always
answerable. A *window* adds one more kind of row: a stretch of genome U bases upstream and D bases downstream
of a transcript's annotated start; there is one window per transcript (278,369 in vM37), all in genome
coordinates; a TE that overlaps a window gets a row with that transcript even though it touches no part of the
transcript body. Nothing is computed inside a window; the window only decides whether a pair exists, and the
row then carries the same geometry as every other row. The size of U and D therefore decides how far from a
gene start te-tracks bothers to record neighbours: with (10000, 2000), TEs up to 10 kb upstream or 2 kb
downstream of any start get rows, about 300,000 more on chr1 than body overlaps alone. A consumer wanting a
2 kb promoter definition filters those rows by the stored distance; a consumer wanting 20 kb cannot, because
those TEs never got rows. That is the only reason to prefer the wide envelope. The recommendation stands at
(10000, 2000) and awaits the owner's word.

**C11 (structural views): still open; the boundary recorded.** te-tracks' concern is the geometry that is a
pure function of its own catalog columns under declared parameters: the union of an instance's fragments with
gaps preserved, the first N bases of a record in its own orientation with the consensus-prefix eligibility, the
LTR–internal candidate pairs from family, strand and distance with their status, and the divergence bins.
These need identities, registration and acceptance like every other export, so they are te-tracks products,
published when a consumer names the need, after the one host build. Downstream are the biological calls and
anything that needs reads or outside evidence: which candidate pairs are real proviruses, which L1 copies keep
a working promoter, whether 5′ read ends pile up in a window, and any activity or age claim. Under the owner's
"one component, one thing", te-tracks ships the candidate tables with neutral names and status columns, and
the consuming analysis makes the calls. The ordering recommendation stands: after the host build, batched into
one later core snapshot.

## Open questions carried to the next session

1. **C4**: confirm the (10000, 2000) envelope for the first context snapshot, or name another.
2. **C11**: confirm "after the host build, batched", and that te-tracks publishes candidate geometry only.
3. **Which GTF the child pins first**: vM37 (the acceptance fixture and the refcache pin) or the 10x
   vM33-filtered GTF (what cellranger counted with, and the recommended index for the STARsolo re-alignment
   so gene counts stay comparable); or both as two snapshots. The ARC reference's GTF is still unverified; the
   GEX one is `gencode.vM33.primary_assembly.annotation.gtf.filtered`, md5 `7a998f670d6d0bdf599c046284da051b`.
4. **C7 details**: who owns the TEsingle qualification and the 14761 RNA pilot; the STAR recipe to pin
   (`outFilterMultimapNmax 100` with `winAnchorMultimapNmax` 100, 150 or 200, and `outSAMmultNmax -1`); the
   reporting contract in tiers (cross-tissue replicated, single-tissue replicated, Multiome descriptive).
5. **Consumer executables**: whether to install STAR, cellranger, IRescue, Stellarscope, TEsingle, TEcount and
   featureCounts in the container or run the execution gates on the host; until then those checks stay
   "unsupported".
6. **IRescue oracle**: the 6/3 fixture expectation against the 5.5/3.5 behaviour, settled only by the binary.
7. **Stellarscope**: a pinned corrected consumer for the boundary defect and the largest-overlap preselection
   before any ERV locus claim leans on it.
8. **C10 details**: the rank scheme (Dfam path as published, the dissertation's five ranks, or Wicker's) and
   the admission scope (the 1,220 interspersed names first); the L1 part-model rule.
9. **Phase 9 additions** to confirm as a set: C8 export; C9 binding rule and join fixture; C10 label-surprise
   and constant-flag notes; a failed-build cleanup case; the RNA qualification limits in the parking handoff;
   the host retention budget at about 15.3 GB per build.
10. **`docs/DECISIONS.md` entries** for every ruled item, written by a codex unit from the ruled text once C4
    and C11 close.
11. **18439-DM recount** on the updated universes (the owner's item under C1).
12. **Umbrella pin**: te-tracks is at `28f2be3` and later while the umbrella pins `6bf9a22`; bump at the next
    milestone.

## Third round (2026-09-17, later): rulings, answers and the consumer environment

The owner read `open_questions_premises_2026-09-17.md` and ruled on the twelve items; three questions came back
and are answered below. Evidence added this round: the Dfam classification tree
(`../taxonomy/dfam_classes_20260917.json`, 300 nodes, 193 carrying a Wicker equivalence and 236 a RepeatMasker
type), family records fetched for twenty representative mouse models, and the consumer-tool environment under
`../env/consumers/`.

**Ruled.**

- **C4: confirmed.** Envelope 10 kb upstream and 2 kb downstream of transcript starts; `mRNA_start_NF` and
  `Ensembl_canonical` carried per transcript; a wider window deferred. Measured for the record: vM37 flags 7,247
  transcripts `mRNA_start_NF` and holds 60,563 transcripts shorter than 2 kb, the only ones for which the
  downstream side adds pairs; the 10x GTF has 7,165 and 19,021.
- **C11: confirmed in general.** Geometry only with status columns and neutral names; after the host build, batched
  into one later core snapshot. The owner adds that the child family must serve the three current datasets on the
  10x 2024-A annotation (GENCODE vM33 filtered) and vM37 alike, which rules item 3: two snapshots, vM37 in phase 8
  where acceptance is pre-measured, the 10x child as the first phase 9 or post-host item, and the ARC GTF verified
  from the 14761 run's reference path before the pilot.
- **C7 details: confirmed** (100 and 200 pinned with cap saturation measured, 500 as a sensitivity run, forks in
  the consuming toolkit, the three reporting tiers), with the owner's boundary: alignment parameters are the
  consumer's responsibility; te-tracks records only the recipe its own execution fixtures run with.
- **Item 5, consumer executables: ruled and done.** A venv without conda, reproducible from pinned sources, the base
  venv used only where nothing conflicts; STAR 2.7.11b; cellranger 10.1.0 supplied by the owner. The environment
  is at `/workspaces/Meta-Aging/.venv/te-consumers`, recreated by `../env/consumers/bootstrap.sh`; manifest, freeze
  and README beside it.
- **Item 6, the IRescue oracle: outside te-tracks' direct responsibility.** The binary settled the fact today: with
  the shims on PATH, `20_irescue_exec.sh` observes 5.5 and 3.5 against the fixture's 6 and 3 and fails
  (`../env/consumers/consumers_run_20260917.log`). Consequence for phase 9: the execution check asserts what
  te-tracks guarantees, identity joins, roster and molecule conservation and unique molecules landing on their
  feature, and records the allocation of ambiguous molecules without asserting it.
- **Item 7, Stellarscope: downstream.** te-tracks makes no fork. The datasets compare each tool's own or
  auto-generated annotation with te-tracks' exports and use agreement and divergence for inference on biology and
  tool behaviour; for mm39 the natural corroboration is IRescue's automatic RepeatMasker conversion of the UCSC
  table, which is the same source te-tracks projects.
- **Packaging direction (owner).** IRescue, TEsingle and Stellarscope run the same reproducible way for 14616, 14782
  and 14761, packaged so that the datasets have little say in how the tools are run; the Multiome snRNA arm runs
  first; ATAC TE analysis uses what IRescue offers plus custom code under a peaks, motifs, TFs, GRN and TE schema
  still to be designed, outside this discussion. The environment prepared today is the seed of that packaging;
  its owner is the consuming toolkit.
- **C10 details: confirmed** (lineage stored as truth; a named rank scheme derived with per-rank status;
  `interspersed` names first; Dfam details included; the definitions relied on stated in te-tracks docs). The rank
  vocabulary is still to be named, the dissertation's five ranks or Wicker's; the owner asked what Wicker's scheme
  is and which reads best for the field. Answer and recommendation below.
- **New ruling, documentation.** The package documentation must state plainly what a record, an instance and an
  insertion are, that every per-locus count is a count per record, and the limitations of the annotation
  endeavour. A decisions entry and an OUTPUTS section follow (the entry through the decisions unit now, the section
  in phase 9).
- **Item 11: 18439-DM is out of scope**; its work is done. **Item 12: the umbrella pin bumps at milestone 9.**
- **Items 9 and 10: proceed as recommended.** C8 enters phase 9 by the round-two scope ruling with the rest of the
  addition set; the decisions unit (`../prompts/decisions.md`, unit `te-tracks-decisions`) launches now.

**Answer 1: what Dfam resolves, and when it is needed.** Dfam serves the aggregate stage of the analysis, which is
exactly where the owner wants the statistics to live; it serves nothing per locus. Four things it settles:

- *Which aggregates exist.* The tree gives one consistent nesting from class to subfamily, so a test on "all ERVs"
  or "the Alu branch" or "MaLR" has a definition. RepeatMasker's family token is inconsistent for that purpose:
  B1 sits under `Alu`, superfamilies survive only in hyphenated labels, and `ERVK` and `ERV2` name the same node.
- *What full length means per subfamily.* Each model has a pinned length; L1MdA_I is the sum of its three part
  models, 1,328 + 4,681 + 993 = 7,002 bp, where the catalog's row-implied lengths for that name range from 4,915
  to 8,042. A record's 5′ completeness is then judged against a defined model.
- *Age tiers with curated evidence.* Each model carries the clade it is assigned to, which is the evidence the
  deferred "young versus old" item needs beside divergence:

  | model | clade | model length | RepeatMasker type/subtype |
  |---|---|---:|---|
  | L1MdA_I_5end, L1MdTf_I_5end | Mus musculus | 1,328 / 1,314 | LINE/L1 |
  | L1_Mur3_5end | Muroidea | 1,328 | LINE/L1 |
  | B1_Mm / B1_Mus1 | Mus / Muridae | 147 / 148 | SINE/Alu |
  | B2_Mm2 / B3 | Murinae / Muroidea | 195 / 216 | SINE/B2 |
  | RSINE1 | Muroidea | 165 | SINE/B4 |
  | MIRb | Mammalia | 268 | SINE/MIR |
  | IAPEz-int / IAPLTR1a_Mm / RLTR10 | Mus / Mus musculus / Mus | 6,481 / 337 / 390 | LTR/ERVK |
  | RLTR4_Mm | Mus musculus | 742 | LTR/ERV1 |
  | MTA_Mm / ORR1A1 / MTD | Mus / Mus / Muroidea | 396 / 346 / 419 | LTR/ERVL-MaLR |
  | MER5A | Eutheria | 189 | DNA/hAT-Charlie |
  | Charlie1 / Tigger1 | Metatheria | 2,781 / 2,418 | DNA/hAT-Charlie, DNA/TcMar-Tigger |

- *Stable identities across assemblies.* Accessions name the same model in mm39 and hg38, so the later human
  comparison uses one hierarchy.

  It also carries coding sequences and features per model, which a later ERV reconstruction can use. It does
  not resolve read allocation, the record–insertion gap, or whether any copy's promoter works. Timing stays as
  ruled, a later core snapshot; the census of all 1,220 `interspersed` names is stored, so the "never queried" risk
  is closed, and the pilot's interim groupings come from RepeatMasker class and family.

**Answer 2: "reconstruction waits for a consumer", and how to prepare.** Reconstruction means assembling
insertion-level units from records: a full-length L1 copy with its 5′ region, a provirus from LTR, internal and
LTR records, a solo LTR after recombination. Nobody downstream consumes such units yet: the RNA pilot counts
records and subfamilies, the ATAC ledger counts records. Building the units now would mean choosing thresholds
(gap, tolerance, length) that no analysis has asked for, and paying acceptance for each. When an analysis asks a
question that needs the unit, it states the question, the parameters and the key it will join on, and te-tracks
publishes the candidate geometry as a view with those parameters declared and a status per row. Preparation is
mostly done: every export carries the instance id and the registration binds `instance_alias` to records; the
catalog holds consensus coordinates, strand and divergence per record; the exon-subtracted child keys blocks to
records, so instance joins survive; the status vocabularies and the measured shapes of all four views are in
`structural_views_consult.md`. Three things remain: the documentation ruling above; the Dfam model lengths and
part models as the pinned definition of full length; and a short recipe note, for the pilot's descriptive use,
on computing instance unions, 5′ eligibility and LTR–internal adjacency from the parquet. The first consumer is
foreseeable: the whole-cell 5′ arm's question whether molecule 5′ ends fall at retained L1 and LTR 5′ ends,
which needs the record 5′ windows and the instance union.

**Answer 3: Wicker's scheme, and the recommendation.** Wicker et al. (2007, *Nature Reviews Genetics* 8:973) is the
field's unified classification: class I (retrotransposons, RNA intermediate) and class II (DNA transposons);
within class II a subclass for cut-and-paste against rolling-circle and self-synthesizing elements; then order
(LTR, DIRS, PLE, LINE, SINE; TIR, Crypton, Helitron, Maverick), superfamily (Copia, Gypsy, Bel-Pao, Retrovirus,
ERV; R2, RTE, Jockey, L1, I; tRNA, 7SL, 5S; Tc1-Mariner, hAT, Mutator, Merlin, Transib, P, PiggyBac,
PIF-Harbinger, CACTA), family by the 80-80-80 rule, and subfamily. It gives each element a three-letter code,
class, order, superfamily, such as RIL for L1, RLE for ERV, RSL for 7SL-derived SINEs, DTA for hAT. The
dissertation's five ranks are Wicker's with the order rank renamed "subclass" and Wicker's own subclass dropped.
RepeatMasker's tokens straddle the ranks: its class is Wicker's order, its family mixes superfamily and family.

Dfam settles the derivation. Each node of its tree carries `wicker_equiv` (for example `R/L (LTR)/E (ERV)` on
`Orthoretrovirinae` and `MaLR`, `D/T (TIR)/A (hAT)` on `hAT` and `Charlie`, `R/S (SINE)/L (7SL)` on `Alu`,
`R/I (LINE)/L (L1)` on `L1`) and the RepeatMasker type and subtype it corresponds to. Of the 1,047 exact census
hits, 884 have a code on their own node, 110 inherit one from an ancestor within two levels, and the 53 without
one are the `Unknown` class, where "unclassified" is the correct status. Recommendation: Wicker's rank names
(class, subclass, order, superfamily, family, subfamily) as `rank_scheme_wicker_v1`, filled by lookup on the Dfam
path with the Wicker code read from the nearest coded node, the Dfam node name as the family value, and the
RepeatMasker class and family tokens beside every row; per-rank status `mapped`, `inherited`, `missing`,
`inapplicable` (subclass outside class II) and `part_model_set` (L1); the dissertation's five names as a
documented alias table so the thesis vocabulary reads onto the same rows. This is the most readable choice
because reviewers know Wicker's terms, the RepeatMasker tokens stay visible for everyone who counts with them,
and the word "subclass" keeps one meaning.

**Environment.** `../env/consumers/`: `bootstrap.sh` (idempotent; `TMPDIR` under the root because `/tmp` is
noexec), `requirements.txt` (five tools at the fixture checkouts' commits), `MANIFEST.tsv` (versions, sources,
archive sha256), `pip-freeze.txt`, `python-version.txt`, `README.md`, `consumers_run_20260917.log`. Root
`/workspaces/Meta-Aging/.venv/te-consumers`: venv 362 MB, STAR 14 MB, subread 151 MB, cellranger 2.6 GB.
`duckdb` 1.5.5 went into the root-owned base venv with sudo; `gawk` 5.1.0 came from apt; both need a line in the
devcontainer image. Suite with shims on PATH: 13 checks, 11 pass, 1 unsupported (Stellarscope boundary), 1 fail
(IRescue allocation, see item 6); without shims the suite is unchanged at 8 pass and 5 unsupported.

**Open after this round.** The rank vocabulary (Wicker recommended); the decisions entries as the unit writes them;
a TES-side window as a later addition if the 3′ pilot needs it. Everything else on the twelve-item list is closed.
Next: verify the decisions unit, rewrite plan 18, write `prompts/p8_impl.md`.

## Fourth round (2026-09-17, later): packaging, Dfam now, Wicker ruled, the schema consult

The owner replied mid-turn to the third-round report.

- **Packaging: ruled.** The joint run of IRescue, TEsingle and Stellarscope is packaged at the umbrella root as
  `/workspaces/Meta-Aging/01_modules/te-consumers/` (environment recipe under `env/`, run recipes under `recipes/`
  as the pilot settles them); the environment itself stays at `/workspaces/Meta-Aging/.venv/te-consumers`. The
  datasets keep the D2 outline (`02_analysis/scripts/00_foundation_peak_atlas` … `40_transposable_elements` …
  `90_integration_exports`) and call the module from `40_transposable_elements/`; the scRNA-seq datasets run the
  RNA part without ATAC. The D1 schema discussion is separate and downstream. The module directory is untracked in
  the umbrella until the owner commits it or asks for a repository.
- **Dfam: ruled, admitted now.** "No deferral, packaging now": the lineage, rank and clade view enters the core in
  phase 9a, before the host build, because the clade per model with divergence beside it is the evidence for the
  young-versus-old question the programme needs answered: the evolutionary origin of TE-driven aging signal. The
  build reads an offline snapshot of the Dfam metadata (fetched by the orchestrator on 2026-09-17: summaries for
  the 1,220 `interspersed` names, full records without sequences for every exact hit and L1 part model, the
  classification tree and the release string; provenance beside it under `../taxonomy/`). `docs/DECISIONS.md`
  section 15 says "a later core view" and is amended to phase 9 by the phase 9a unit.
- **Wicker: ruled.** Wicker's rank names as the named scheme, filled from the Dfam path with the Dfam node name as
  the family value, the RepeatMasker class and family tokens beside every row and per-rank status, so the scheme is
  fully programmatically derivable, uses the terms reviewers know, and every word keeps one meaning.
- **Reconstruction as a consumer: the owner names the consumer.** An interactive tool projecting onto genome
  coordinates where the remnants of a lineage lie, lighting up where the current dataset sees them, then filtering
  the unified schema down a funnel (L1 remnants → RNA support in the nuclei → open chromatin → TF families and motifs
  inside → the subset under the studied conditions that needs validation). This overlaps with the design of the
  unified schema queryable by plain SQL, interactively, or for statistical modelling, and must separate what the
  Multiome sustains within one nucleus from what needs the unpaired whole-cell runs. A dedicated consult at the
  highest reasoning effort is assigned: `../prompts/schema_consult.md`, unit `te-tracks-schema-consult`, one file
  `unified_te_schema_consult.md`.
- **IRescue criticality, answered.** The failing check is te-tracks' own expectation about IRescue's arithmetic,
  and the tool behaves as its authors designed, so nothing is broken in te-tracks or in IRescue. For te-tracks the
  fix is one test in phase 9: assert identity joins and conservation, record the allocation. For the science the
  finding characterizes IRescue: unique molecules are exact, ambiguous molecules are allocated by an EM that starts
  even and ignores unique support; when every ambiguous molecule shares one candidate set the EM cannot move and
  splits evenly, and in real data it learns only from how ambiguity sets differ across molecules. Subfamilies with
  strong unique evidence therefore receive less of the ambiguous share than a unique-seeded EM would give them,
  which is the conservative behaviour C7 wants from IRescue, and the young high-copy subfamilies, whose molecules
  are mostly ambiguous, are where the estimator choice matters. The difference between IRescue and TEsingle on the
  same molecules is a reported quantity of the pilot, and the ambiguous share per subfamily is one of its
  measurements.

**Launched at the end of this round:** `te-tracks-p8-impl` from `../prompts/p8_impl.md` against plan 18 as
rewritten; `te-tracks-schema-consult` from `../prompts/schema_consult.md`, read-only. Plan 19 gains section
"Phase 9a: core additions before acceptance".
