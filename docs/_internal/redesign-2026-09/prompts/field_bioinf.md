Bioinformatics-methods review of the te-tracks programme's treatment of TE annotation, classification rungs,
genic context and counting, for three single-cell datasets. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(branch redesign-2026-09, commit 8589873). You are read-only; write exactly one file,
/workspaces/Meta-Aging/01_modules/te-tracks/docs/_internal/redesign-2026-09/reviews/field_bioinf.md, and change nothing
else. No git writes (the checkouts under /workspaces/Meta-Aging/01_modules/.ref/ are git repositories too), no installs.
Web search is allowed for published methods and benchmarks; cite what you use.

Read, in order:
1. docs/_internal/redesign-2026-09/consults/thesis_2023_excerpts.md (the owner's brief: excerpts of a 2023 dissertation
   on single-cell TE quantification, the three datasets, and the owner's questions).
2. docs/_internal/redesign-2026-09/consults/{sctefinder_scte_notes,tesingle_notes,gene_context_material,gene_child_consult,gene_context_adr_brief}.md (TEsingle is the dissertation author's production tool; treat it as the reference implementation of the excerpts' ideal).
3. docs/OUTPUTS.md (exports, registration, taxonomy, universes), docs/DECISIONS.md, README.md.
4. The consumer checkouts' annotation handling as you need them: TEtranscripts, TElocal, TEsingle, stellarscope,
   irescue, MATES, scTE under /workspaces/Meta-Aging/01_modules/.ref/, and the dissertation code under
   /workspaces/Meta-Aging/01_modules/.ref/Thesis_2023/quantification_method/, and the TEsingle paper's code under /workspaces/Meta-Aging/01_modules/.ref/TEsingle_benchmarking_scripts/ and /workspaces/Meta-Aging/01_modules/.ref/TEsingle_Martirosyan_analysis_code/.

Your lens is methods correctness and field convention:
- Classification: how the field's class, subclass, superfamily, family, subfamily rungs map onto RepeatMasker's
  class, family and name and onto Dfam lineages for mouse; where the mapping is conventional and where it is
  contested (ERV internal and LTR pairs, MaLR, B1/B2/ID, L1 subfamilies, DNA superfamilies).
- Counting: which aggregation the field primarily reports (subfamily counts, locus counts, family rollups), which
  tools use EM over loci versus subfamily metagenes, how multi-annotating gene-TE reads are treated, and what the
  dissertation's benchmark implies for our choice of counting level per dataset (5' PE OCM whole cells; Multiome
  nuclei with ATAC).
- Genic context: what context metadata published methods use (TE-Seq labels, exon/intron/intergenic, UTR overlap,
  promoter windows, gene-body distance, sense/antisense) and whether the drafted context relation and mask policy
  (gene_child_consult.md Q3 to Q6) are sound, over- or under-specified.
- 5' chemistry: the dissertation's claim that 5' capture separates promoter-driven from passive TE transcription;
  whether 5' PE OCM v3 reads land near TE promoters in practice and what the annotation must provide for that
  question (TE 5' ends from consensus coordinates, full-length L1, solo LTRs).
- Nuclei and ATAC: intronic read fraction, GeneFull counting, ATAC cuts within TE intervals and promoter windows,
  and what a peak ledger keyed on TE loci needs from the annotation.
- Statistical validity: what the pooled, replicate-free Multiome design permits at condition level and what the
  paired 20-animal design permits, for TE-level claims.

Format:
# Field review: methods and conventions (bioinf)
## Verdict on the drafted direction (sound / amend / reconsider), one paragraph
## Findings
- [F1] finding — evidence (path:line or citation) — what it changes in te-tracks or the consumer plan — phase
## Field conventions table
<table: question rung | primary tool(s) | counting level | multi-annotating treatment | context metadata used>
## Recommendations by dataset
## Open questions for the owner
Under 200 lines. Specific over general; separate what the checkouts show from what the literature says.
