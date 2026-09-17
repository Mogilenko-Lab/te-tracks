# te-tracks mask-policy consult: exon masks, strand, the EM-facing route and intron-retention views (codex, read-only)

You are consulted on design; you measure and recommend, you implement nothing. Working directory
`/workspaces/Meta-Aging/01_modules/te-tracks`, branch `redesign-2026-09`, commit `9c27b14`. You write exactly one
file: `docs/_internal/redesign-2026-09/consults/mask_policy_consult.md`. You change nothing else. No git writes anywhere
(the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too; `14839-DM-cGAS` and `sene/`
are the owner's directories, read the first, leave both alone), no installs, no network. Export
`PYTHONDONTWRITEBYTECODE=1`. Scratch only under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/mask-consult/`,
removed when you finish (Python `shutil`; `/tmp` is noexec). bedtools 2.31.1, pandas, pyarrow and numpy are available.

Read-only inputs: the core build `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` (tables
`rmsk_records.parquet`, `contig_aliases.tsv`, `universe_summary.tsv`, `universes.json`); GENCODE vM37 at
`/data2/users/shared/refcache/mm39/mm39_20260911/gencode.vM37.primary_assembly.annotation.gtf.gz`; the 10x
cellranger reference GTF at `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refs/refdata-gex-GRCm39-2024-A/genes/genes.gtf.gz`
with its `reference.json` beside it (if that directory is absent when you start, say so and measure vM37 alone).

## Read first, in order
1. `docs/_internal/redesign-2026-09/consults/adr_rulings_2026-09-17.md` (the owner's rulings; C2 is your subject).
2. `consults/gene_context_adr_brief.md` (C2 as drafted, the measured facts table), `consults/gene_child_consult.md`
   Q3 and Q4 (the mask as designed, 3,701,642 retained records and 3,717,740 blocks for compat under the all-exon
   unstranded mask, 26,503,064 bp removed), `consults/field_practice_synthesis.md` sections 3 and 5,
   `consults/tesingle_notes.md`, `consults/sctefinder_scte_notes.md`.
3. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md`, `docs/OUTPUTS.md`
   (universes, SAF exports), `docs/DECISIONS.md`.

## The owner's words (verbatim, 2026-09-17)
> All of them are defensible in their own sense. If we go with protein-coding masks, I don't fully understand though
> why wouldn't we also remove lncRNA and pseudogene exons, but then I could see then extending the logic to all
> exons. The strand-aware masking keeping TE bases that lie antisense to an exon is attractive, but the effect would
> have to be specifically measured, modelled and compared to the conservative one, and I suspect different chemistry
> like 5' or 3' stranded might have different results (with 5' having better coverage for promoters), and so such an
> option needs to live along the conservative one. I could see though how we could have options for the end user to
> choose from, exon-disjoint, or maybe something more EM facing where we would have to rely on some EM algorithm to
> decide on whether a read jointly belongs to exon or TE or TE within that exon, not sure. The TEsingle also
> modelled intron-retention, not sure if that's relevant.

The TEsingle paper's intron-retention estimate (owner's excerpt): the unspliced fraction U equals the fraction of
total coverage over purely intronic sequence divided by the fraction of evaluated bases that are intronic; it uses a
BED of regions within gene transcripts but never in exons or TEs, and a BED of regions within exons but never in
introns or TEs, computing coverage over each.

## Questions
1. **Mask census.** On the `interspersed` universe (3,764,949 records) and on `compat_tetranscripts_mm39`
   (3,799,629), measure bases removed, records fully removed, records partly cut and retained block count under:
   (a) vM37 all exon rows, unstranded union; (b) vM37 all exon rows, strand-aware, removing only same-strand exon
   bases; (c) opposite-strand-only removal, for information; (d) vM37 protein-coding transcripts' exons; (e) vM37
   `basic` tag exons; (f) the 10x 2024-A GTF exons, unstranded and strand-aware. Report the strand-aware gain as the
   TE bases that overlap exons only on the opposite strand. Use two methods on chr1 (bedtools and an independent
   Python sweep) and confirm agreement before running the genome. Normalize GTF contigs through `contig_aliases.tsv`
   and report the 10x GTF's contig names against the te-tracks namespaces.
2. **What the 10x GTF is.** From `reference.json` and the file: GENCODE release, biotype filter, gene and exon counts,
   exon union size against vM37's 160,549,642 bp, and the records whose mask outcome differs between the two GTFs.
3. **Strand and chemistry.** State what a strand-aware SAF assumes about the counting run (which read is sense to
   the transcript for 10x 3′ and 5′ chemistries; what featureCounts `-s 1`/`-s 2` and STARsolo `--soloStrand` do with
   it) from the checkouts and documentation you can read; where the chemistry evidence is missing, say what the
   consumer pilot must measure. Do not assert a chemistry fact you cannot cite.
4. **The EM-facing route.** Confirm from source (TEsingle `TEtools/`, IRescue `irescue/`, STARsolo route as described
   in the records) that EM counters need unmasked TE features and the full gene GTF, so that the exon-subtracted SAF
   is a bulk-overlap product and the EM route's te-tracks inputs are the record GTF/BED plus, later, the context
   relation. State what, if anything, the child should ship for that route.
5. **Intron-retention views.** Define from vM37 (and the 10x GTF) plus the records: (i) bases inside transcript spans,
   outside every exon and outside every `all_rmsk` record; (ii) bases inside exons, outside every intron of any
   transcript and outside every record. Measure their sizes; propose them as optional child views with acceptance
   numbers; state what the consumer computes (coverage sums, U) and what U tells an analyst about intronic TE signal
   in nuclei versus whole cells.
6. **Recommendation.** The phase 8 policy set: the default (`all_exons_unstranded_union_v1`, `min_retained_block_bp
   = 1`), whether `all_exons_stranded_union_v1` ships beside it in phase 8 or in the first later snapshot, the cost of
   each extra policy (SAF pair, acceptance numbers, identity), and whether a 10x-GTF-pinned snapshot changes the
   recommendation. Each recommendation states what it prevents and its settling measurement.

## Output format
```
# Mask-policy consult (codex gpt-6-astra)
## Summary
## Q1 .. Q6
## Measurements performed (methods, agreement checks, exact numbers)
## Open for the owner
```
Under 250 lines. Facts over opinions; cite paths and lines; where you rely on knowledge beyond the inputs, say so in
the sentence. Recommend; do not implement.
