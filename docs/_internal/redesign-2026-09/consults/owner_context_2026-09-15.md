# Owner context for te-tracks design (verbatim intent, 2026-09-15)

Consumers named by the owner, all with local read-only checkouts under
/workspaces/Meta-Aging/01_modules/.ref/: irescue (v1.2.0-20-g26f36fb), stellarscope (1.5),
TEsingle (1.0-8-g655f127), MATES (v0.1.8-9-g87c1218).

The repository must not carry background knowledge of what the annotations are used for, but the
annotations must be rich enough to support many biological questions across bulk RNA-seq, single-cell
RNA (5' PE OCM whole-cell), single-nucleus RNA (3' ARC), and single-nucleus ATAC (ARC).
Namespace clarity is a first-class requirement. Provenance and publication: simple, robust, clear,
coherent, not over-engineered.

## Future 40_transposable_elements branch (context, out of te-tracks scope)

Preserve established RepeatMasker annotations and publish explicit policy views; do not invent a de
novo TE discovery project. Retain enough source information for later structural annotation without
pretending every fragment is intact. Implement only the consumer exports actually needed first;
validate each with its real parser and a tiny known-answer fixture. Custom BED/GTF syntax and feature
naming must be tested, not assumed universal.

RNA: IRescue with pinned custom subfamily features first; locus investigation with IRescue's tested
locus configuration and/or Stellarscope against a conservative uniquely-supported-molecule baseline;
TEsingle as a joint gene/TE assignment sensitivity analysis (audit its default barcode threshold).
Separate TE-associated RNA from evidence of autonomous transcription.

ATAC: coordinate overlaps and direct cut counts from existing fragments over TE intersections, TE
sequence, and defensible promoter regions; stage-10 counting contract; no double Tn5 shift; no custom
ATAC EM to start; MATES optional model-based branch.

## The ledger (peak-centered entry point)

Directory-of-Parquet star schema queried by DuckDB via a manifest of selected files. Logical tables
include: peaks, contexts, analysis_runs, accessibility, motif_sites, motif_tf_map, motif_groups /
tf_families, peak_gene_links, grn_triplets, regulons, tf_model_status, rna_summaries,
**repeat_fragments** (reference build x fragment identity; exists independently of peak overlap),
**peak_te_overlaps** (peak x TE fragment; intersection coordinates and fractions),
**te_feature_registration** (quantifier feature x catalog object; explicit resolution and one-to-many
mappings). RNA joins at gene / TF / regulon / explicitly resolved TE feature. A subfamily RNA
measurement cannot be assigned to every accessible insertion in that subfamily; a count for a
reconstructed insertion cannot be copied onto each constituent fragment. Direct subfamily
quantification and a sum of separately inferred locus counts may differ; preserve both. Joins must not
create signal (unit test, not documentation).

## Validation tiers

Annotation contracts: recompute row counts and taxonomy multiplicities; coordinate round-trips;
source vs exported strand; contig lengths against the actual reference; every output feature
registers back to the canonical catalog; generate actual alias/conflict tables (a single mismatched
record could be the locus later prioritized).

Adversarial fixtures (required outcomes): motif in a TE-overlapping peak but outside TE sequence ->
no "motif inside TE"; ATAC fragment spans a TE with both cuts outside -> overlap signal distinct from
cut signal; one insertion with separated annotation blocks -> intervening non-TE sequence not counted;
two indistinguishable loci in one subfamily -> subfamily support retained without pretending locus
identity; duplicates/multi-alignments -> counts do not inflate; a subfamily name with two
classification triples -> aggregation does not duplicate; a TF filtered from a GRN input -> status
"filtered", not absence; one peak joining several motifs/TEs/genes -> accessibility conserved.
RNA fixtures test 3' ARC and 5' PE OCM layouts separately.

Biological simulations: identifiability (old vs young copies), transcript origin (autonomous TE,
TE-containing host transcript, host pre-mRNA with intronic TE), assay (3' nuclear, 5' whole-cell,
51-bp PE ATAC with empirical fragment lengths), technical variation. Evaluate subfamily and locus
accuracy separately. A host-pre-mRNA simulation may legitimately yield TE-associated counts under an
inclusive counter; the failure is labelling them autonomous transcription.
