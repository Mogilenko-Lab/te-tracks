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
- `tables/contig_coverage.tsv`: per contig: records, in `interspersed`, has alias, length agrees.
  `chr4_JH584295v1_random` and `chrM` carry zero records.
- `bin/te-tracks-preflight <export> <bam|fai|sizes>`: reads contig names and lengths from a BAM header, a
  `.fai`, or a two-column sizes file; reports contigs in the alignment reference absent from the export,
  contigs in the export absent from the reference, and length disagreements. Exit 0 when the contig sets
  agree and every length matches; exit 2 when the sets differ with a non-empty agreeing intersection,
  both lists printed; exit 1 when a shared contig disagrees in length or the intersection is empty
  (milestone 2 ruling M1).

Acceptance: row counts equal across the three namespaces for every export; scaffold
`chr1_GL456210v1_random` maps to `GL456210.1` in both `ensembl` and `gencode`, `chrM` maps to `MT` in
`ensembl` and stays `chrM` in `gencode`; preflight against the GENCODE FASTA contig list
(`redesign-2026-09/audit/gencode_grcm39_fasta_contigs.tsv`, 61 contigs) exits 0 for `gencode`, exits 2
for `ucsc` with the 39 scaffolds listed in both directions, exits 2 for `ensembl` with the 22
chromosomes listed in both directions, and exits 1 for `ensembl` against a 21-chromosome UCSC sizes
file (empty intersection); all 61 lengths agree. `docs/DECISIONS.md` entry 3 names the three namespaces.
