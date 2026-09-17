Divergent review of the te-tracks programme's stance on TE annotation, classification rungs, genic context and
counting, for three single-cell datasets. Repository: /workspaces/Meta-Aging/01_modules/te-tracks (branch
redesign-2026-09, commit __HEAD__). You are a read-only reviewer; write exactly one file,
/workspaces/Meta-Aging/01_modules/te-tracks/docs/_internal/redesign-2026-09/reviews/field_divergent.md, and change nothing
else. No git writes (the checkouts under /workspaces/Meta-Aging/01_modules/.ref/ are git repositories too).

Read, in order:
1. docs/_internal/redesign-2026-09/consults/thesis_2023_excerpts.md (the owner's brief and the three datasets).
2. docs/_internal/redesign-2026-09/consults/{sctefinder_scte_notes,tesingle_notes,gene_context_material,gene_child_consult,gene_context_adr_brief}.md (TEsingle is the dissertation author's production tool; treat it as the reference implementation of the excerpts' ideal).
3. docs/OUTPUTS.md, docs/DECISIONS.md, README.md; the build tables under
   /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/ (read-only) where a measurement settles a point.
4. The consumer checkouts under /workspaces/Meta-Aging/01_modules/.ref/ as needed, including Thesis_2023, TEsingle_benchmarking_scripts and TEsingle_Martirosyan_analysis_code.

Your question: what does the programme take for granted about TE annotation and counting that the record does not
defend? Attack, with a specific failure each:
- the rungs: that RepeatMasker class/family/name is the hierarchy consumers want; that subfamily is the right default
  aggregate; that a taxonomy triple is a stable key across releases; that a "locus" is a RepeatMasker record rather
  than an insertion (fragments sharing an instance id, nested copies, LTR and internal pairs);
- the counting: that the consumer will run EM; that a combined gene and TE GTF with single-exon TE transcripts is
  what STARsolo GeneFull needs; that our record.gtf is the dissertation's "subfamily GTF"; that multi-annotating
  gene-TE reads can be addressed by annotation at all; that sparsity rounding is the consumer's problem;
- the context: that an exon-subtracted SAF is what a single-cell consumer needs; that the sparse transcript relation
  is computable and consumable at 22 to 27 million pairs; that the four-state status vocabulary is enough; that
  intronic TE reads in nuclei are passive transcription;
- the datasets: 5' capture reads as promoter-proximal evidence given 5' PE OCM v3 read structure; cellranger 9 and
  10 references and their GTF versus GENCODE vM37; the pooled Multiome library with no replicates; the ATAC peak
  ledger keyed on TE loci and the nested-copy double counting; joining spleen scRNA, lung scRNA and spleen multiome
  TE results across chemistries;
- the annotation refinements: promoter-intact filtering from consensus coordinates; young versus old by divergence;
  solo LTR detection; a Dfam lineage rank table pinned to a Dfam release;
- process: a dissertation from 2023 as the field reference; consult files as records; the orchestrator's build as
  the reviewers' subject.

For each assumption: state it in one sentence, give the concrete failure it predicts (inputs and the wrong output or
the silent gap), rate the cost of being wrong (low, medium, high), and say which phase or which consumer should
address it. If an assumption is defended somewhere in the record, cite the file and line and move on.

Format:
# Field review: unstated assumptions (divergent)
## High
- [H1] assumption — failure — evidence — where it lands
## Medium
## Low
## Defended already
Under 150 lines. Specific over general; measure from the build tables where a measurement settles the point.
