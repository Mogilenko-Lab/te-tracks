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
