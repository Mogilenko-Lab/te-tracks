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
