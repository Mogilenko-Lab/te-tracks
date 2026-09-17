# te-tracks field-practice consult: TE annotation, classification rungs, genic context and counting (codex, read-only)

You are consulted on design and field practice. Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks`,
branch `redesign-2026-09`, commit `8589873`. You write exactly one file:
`docs/_internal/redesign-2026-09/consults/field_practice_consult.md`. You change nothing else. No git writes anywhere
(the eleven consumer checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too:
DfamTEBrowser, irescue, mascarade, MATES, mLLMCelltype, scTE, scTEfinder, stellarscope, TElocal, TEsingle,
TEtranscripts; `Thesis_2023`, `TEsingle_benchmarking_scripts` and `TEsingle_Martirosyan_analysis_code` are further checkouts you read; `14839-DM-cGAS` and `sene/` are the owner's copies, read
the first and leave both alone), no installs, no network. Export `PYTHONDONTWRITEBYTECODE=1`. Scratch under
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/field-consult/`, removed when you finish (Python `shutil`; `/tmp` is
noexec). Read-only inputs: the core build at `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build`
and the GENCODE vM37 GTF at `/data2/users/shared/refcache/mm39/mm39_20260911/gencode.vM37.primary_assembly.annotation.gtf.gz`.

The owner asked three things, recorded in `consults/thesis_2023_excerpts.md`: how the field treats TE annotation
(where TEs are mapped, where they are separated into classes, families and subfamilies, and what genic-context
metadata is used: exon, intron, intergenic, 5' and 3' UTR, or else); that te-tracks cover the rungs of questions one
asks when counting TE features as aggregates of classes, families, subfamilies or loci, knowing which counting the
field primarily uses; and what the te-tracks endeavour and the wider single-cell TE programme should take into
account for three datasets: two whole-cell 5' PE OCM v3 libraries (spleen and lung, same 20 animals, cellranger 9
and 10) and one Multiome ATAC+GEX v1 nuclei library per condition (spleen, cellranger-arc 2.1.0, pooled animals,
no replicates). The owner keeps the dissertation's ideal method in view even where it is unattainable.

## Read, in order
1. `consults/thesis_2023_excerpts.md` (the owner's excerpts and dataset table; treat the quotations as the owner's
   brief) and the code behind them under `/workspaces/Meta-Aging/01_modules/.ref/Thesis_2023/quantification_method/`
   and the TEsingle paper's code under `/workspaces/Meta-Aging/01_modules/.ref/TEsingle_benchmarking_scripts/` (index generation per tool) and `/workspaces/Meta-Aging/01_modules/.ref/TEsingle_Martirosyan_analysis_code/` (`eqc_generation/scripts/annotate.sh` in the thesis code shows the TE GTF grammar `gene_id` subfamily, `transcript_id` locus,
   `family_id`, `class_id`, joined by bedtools with `-s -split`; `EM/` the effective-length EM).
2. `consults/sctefinder_scte_notes.md`, `consults/tesingle_notes.md` (TEsingle is the dissertation author's production tool; treat it as the reference implementation of the excerpts' ideal), `consults/gene_context_material.md`, `consults/gene_child_consult.md`,
   `consults/gene_context_adr_brief.md` (what is already known and proposed; do not repeat it, build on it).
3. te-tracks' public contract: `README.md`, `docs/DECISIONS.md`, `docs/OUTPUTS.md` (exports, registration,
   taxonomy, universes), `docs/RELEASES.md`; and the tables `tables/rmsk_records.parquet` (24 typed columns
   including `rmsk_class`, `rmsk_family`, `rmsk_name`, `rmsk_instance_id`, consensus coordinates, divergence),
   `tables/taxonomy_canonical.tsv`, `tables/rmsk_taxonomy.tsv`, `universes.json`, `tests/fixtures/taxonomy/dfam_snapshot.tsv`
   (Dfam lineage strings such as `root;Interspersed_Repeat;Transposable_Element;Class_I_Retrotransposition;LTR;...`).
4. The consumer checkouts' annotation handling: TEtranscripts and TElocal (`GeneFeatures`, `TEindex`, the
   `gene_id:family_id:class_id` grammar), TEsingle, stellarscope (`locus`, `--attribute`), irescue (BED name
   parsing, subfamily and family columns), MATES (`build_reference.py`), scTE (`bin/scTE_build`), and
   DfamTEBrowser (a family-consensus browser: instances map to a consensus through Dfam seed alignments; the
   Dfam `classification` lineage is the hierarchy). Read the D2 plan at
   `/workspaces/Meta-Aging/14761-DM/docs/_internal/_project/plans/2026-09-11_codebase-topology/01_consult_codex.md`
   for the ATAC ledger's needs, and the bulk toolkit `K/docs/{METHODOLOGY,LIMITATIONS}.md` under
   `/workspaces/Meta-Aging/01_modules/.ref/14839-DM-cGAS/01_modules/TE-RNAseq-toolkit`.

## Questions, each with evidence, options and consequences, a recommendation, and the settling measurement
1. **Classification rungs.** The dissertation names class, subclass, superfamily, family, subfamily and coordinates.
   RepeatMasker gives te-tracks class, family and name (subfamily); Dfam gives a lineage string. Map the two onto the
   dissertation's rungs for mm39 (which rmsk class/family pairs are superfamilies, which are subclasses; where LTR
   `-int` and LTR pairs, ERV1/ERVK/ERVL/ERVL-MaLR, L1 and L2, B1/B2/ID/Alu-like SINEs, DNA superfamilies land).
   Should te-tracks publish a rank table (lineage per subfamily from Dfam, with the rmsk class and family beside it)
   so a consumer can aggregate at any rung; what its identity and versioning would be (Dfam release pin); how the 20
   multi-label names and the unresolved ranks behave. Measure the Dfam coverage of the 18,484 names from the
   snapshot fixture and state what a full Dfam admission would need.
2. **Where the field maps TEs and how it separates them.** Survey the checkouts and the dissertation: genome
   alignment with multimappers kept (STAR with `outFilterMultimapNmax 100`, `winAnchorMultimapNmax 100/150`),
   consensus alignment (Dfam/RepeatMasker seed alignments; Stellarscope's and TEtranscripts' EM over loci), and
   transcriptome selective alignment (Alevin-fry with unspliced transcripts). State for each consumer at which rung it
   separates features (locus, subfamily, family, class) and how it treats multi-annotating reads (discard, prioritize
   genes, random one, EM). Which counting does the field primarily use, and which does each of our three datasets
   need.
3. **Genic-context metadata in the field.** What metadata the consumers and the dissertation actually use: exon
   overlap, intron, intergenic, 5' and 3' UTR (GENCODE `UTR` rows exist: 186,133 in vM37), promoter windows, gene
   body distance, TE-Seq's Exonic/Intronic/Intergenic label, scTE's exclusive/nointron deletion. Judge whether the
   context relation drafted in `gene_child_consult.md` Q5 covers what the field asks (UTR overlap as a separate
   flag? sense/antisense to the host gene? exon-cut distance?) and what to add or cut.
4. **Rungs of counting questions te-tracks must serve.** For each aggregate (locus, instance, subfamily, family,
   class, taxonomy triple, and the dissertation's superfamily and subclass), name the export or table that serves it
   today (`record.gtf`, `subfamily.gtf`, `family.bed`, `subfamily.saf`, `taxonomy_triple.saf`, the registration's
   conservation rule) and what is missing. In particular: a "loci GTF" variant where `gene_id` is the record id, so
   STARsolo GeneFull counts loci as genes as the dissertation did (is our `record.gtf` with `gene_id = rmsk_name`
   the "subfamily GTF" of the dissertation, and does a `gene_id = record` variant belong in te-tracks or is a
   consumer rename enough given the registration?); an instance-merged view where the fragments of one insertion
   (shared `rmsk_instance_id`) form one feature, so EM does not split a copy against itself; a class-level rollup.
   Say which belong to the core family, which to a view, and which to the consumer.
5. **The three datasets.** For 5' PE OCM whole cells: the dissertation names 5' capture as the way to separate
   promoter-driven TE transcription from passive intronic transcription. State what te-tracks can publish so a
   consumer can ask "reads whose 5' ends fall in a TE's own 5' region" (a TE 5'-anchored interval view? consensus
   coordinates already carry 5' truncation: `consensus_start_1` against the consensus length; which records are
   promoter-bearing L1 or solo/5' LTRs) and how STARsolo GeneFull plus EM on a combined gene and TE GTF would use
   the exports. For Multiome nuclei: intron-rich reads, GeneFull counting, the context relation's role, and the ATAC
   side (cuts within TE intervals, TE promoter regions, `all_rmsk` record BED, peak ledger keys). Name what the
   consumers must do themselves (UMI handling for multi-annotating reads, EM, sparsity rounding) and what te-tracks
   must not attempt.
6. **Annotation refinement the dissertation asks for.** Promoter-intact filtering (full-length L1, solo LTRs, LTR and
   internal pairing via `rmsk_instance_id`), young versus old tiers by divergence, a TE transcriptome from long
   reads. Which of these te-tracks can express as universes or views from the columns it already has (consensus
   coordinates, divergence, instance ids, class and family), which need new inputs, and what the acceptance
   measurement for each would be on mm39 (measure where a bounded computation on the build allows: for example how
   many L1 records begin within N bp of their consensus 5' end; how many LTR records have a same-instance internal
   partner).
7. **TEsingle as the reference consumer.** Given `tesingle_notes.md`, judge how far TEsingle realizes the
   dissertation's ideal (UMI graph, EM, intron inclusion, locus features, the `te_frac` gene-TE prior), what it needs
   from te-tracks beyond `record.gtf` (the gene GTF it is run with, strandedness for 5' PE OCM, contig namespace),
   and how its locus counts join the context relation and the registration for the rung questions. State whether
   TEsingle should be the primary RNA consumer for the two whole-cell datasets and what that implies for the
   Multiome GEX side.
8. **What the te-tracks programme should change now.** Given phases 8 and 9 as planned (`P/18_phase8_gene_child_seam.md`,
   `P/19_phase9_acceptance_park.md`), list the concrete additions or amendments you recommend, each with its
   phase (8, 9, or a later snapshot), its cost, and what it prevents; and the things you recommend leaving to
   consumers with the reason.

## Output format (the consult file)
```
# Field-practice consult: TE annotation, rungs, context and counting (codex gpt-6-astra)
## Summary of recommendations
## Q1 .. Q7
## Candidate ADR statements or amendments for the owner
## Measurements performed
## Open for the owner
```
Under 350 lines. Facts over opinions; every claim about a tool, a document or the field cites a path and, where
possible, a line; where you rely on knowledge beyond the checkouts, say so in the sentence. Recommend; do not implement.
