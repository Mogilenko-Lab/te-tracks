# Phase 6: contig namespaces, aliases, coverage, preflight

Measured (audit §6): the GENCODE GRCm39 FASTA the lab aligns against names chromosomes UCSC-style
(`chr1` … `chrM`) and scaffolds by GenBank accession (`GL456210.1`). Neither `ucsc` nor `ensembl`
matches it completely, so the exports ship in three namespaces: `ucsc`, `ensembl` and `gencode`
(chromosomes from the ucsc alias column, scaffolds from the genbank column).

Deliverables
- `tables/contig_aliases.tsv`: `chrom_ucsc, chrom_ensembl, chrom_genbank, chrom_refseq, length_bp`
  from `chromAlias.txt` and `chrom.sizes`, plus `chrom_gencode`; injectivity asserted per column; 61 rows.
- `exports/{ensembl,gencode}/interspersed/full/{record.bed, subfamily.bed, family.bed, record.gtf,
  subfamily.gtf, subfamily.saf, taxonomy_triple.saf}` and phase 8's SAF: same rows as the `ucsc` files, contig
  column renamed through the alias table; `rmsk_record_id` unchanged (UCSC names inside). Emitted ids are
  namespace-invariant, so the renamed files add no registration rows; each renamed file gains one `exports.tsv`
  row (milestone 2 rulings M5, H2).
- `exports/{ucsc,ensembl,gencode}/all_rmsk/full/record.bed` (milestone 5 ruling H2, subject to the owner): the
  record BED over the complete catalog for 14761's ATAC route, registered under universe `all_rmsk`, level `record`,
  grammar `rmsk_record_id` (5,320,771 rows); the inventory grows to 24 rows.
- `tables/contig_coverage.tsv`: per contig: catalog records, `interspersed` records, has alias, length agrees.
  `chr4_JH584295v1_random` and `chrM` carry zero `interspersed` records; their catalog counts are 2 and 4
  (Low_complexity, Simple_repeat, rRNA and tRNA records), so the interspersed exports name 59 of the 61 contigs
  and the `all_rmsk` BED names all 61.
- `bin/te-tracks-preflight <export> <bam|fai|sizes>`: reads contig names from the export (BED and GTF column 1, SAF
  column 2), their lengths from the build's alias table, and the reference's names and lengths from a BAM header, a
  `.fai` or a two-column sizes file; prints `only_in_reference`, `only_in_export` and `length_disagreements`. Exit 0
  when every export contig is present in the reference with an agreeing length; reference-only contigs are
  informational, since a universe with no records on a contig is a fact about the universe. Exit 2 when the export
  names contigs the reference lacks and the shared set is nonempty, because a counter would drop those features. Exit
  1 when a shared contig disagrees in length, the intersection is empty, or an input cannot be read (milestone 2
  ruling M1 as amended by phase 6 ruling B2). Export completeness against its inventory is the manifest's job (phase 7).

Acceptance: row counts equal across the three namespaces for every export; scaffold
`chr1_GL456210v1_random` maps to `GL456210.1` in both `ensembl` and `gencode`, `chrM` maps to `MT` in
`ensembl` and stays `chrM` in `gencode`; against the GENCODE FASTA contig list
(`redesign-2026-09/audit/gencode_grcm39_fasta_contigs.tsv`, 61 contigs) preflight exits 0 for both `gencode`
universes (the interspersed exports list `JH584295.1` and `chrM` as reference-only), exits 2 for `ucsc` (`all_rmsk`:
39 scaffolds each way; interspersed: 38 export-only UCSC scaffolds and 40 reference-only names) and for `ensembl`
(`all_rmsk`: 22 chromosomes each way; interspersed: 21 export-only and 23 reference-only), and exits 1 for `ensembl`
against a 21-chromosome UCSC sizes file (empty intersection); all 61 lengths agree. `docs/DECISIONS.md` entry 3
names the three namespaces and the `all_rmsk` record BED.
