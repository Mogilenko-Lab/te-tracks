# Phase 6: contig namespaces, aliases, coverage, preflight

Measured (audit §6): the GENCODE GRCm39 FASTA the lab aligns against names chromosomes UCSC-style
(`chr1` … `chrM`) and scaffolds by GenBank accession (`GL456210.1`). Neither `ucsc` nor `ensembl`
matches it completely, so the exports ship in three namespaces: `ucsc`, `ensembl` and `gencode`
(chromosomes from the ucsc alias column, scaffolds from the genbank column).

Deliverables
- `tables/contig_aliases.tsv`: `chrom_ucsc, chrom_ensembl, chrom_genbank, chrom_refseq, length_bp`
  from `chromAlias.txt` and `chrom.sizes`, plus `chrom_gencode`; injectivity asserted per column; 61 rows.
- `exports/{ensembl,gencode}/interspersed/full/{record.bed, subfamily.bed, family.bed, record.gtf,
  subfamily.saf, taxonomy_triple.saf}` and phase 8's SAF: same rows as the `ucsc` files, contig column
  renamed through the alias table; `rmsk_record_id` unchanged (UCSC names inside); registered in
  `export_feature_members` under their own paths.
- `tables/contig_coverage.tsv`: per contig: records, in `interspersed`, has alias, length agrees.
  `chr4_JH584295v1_random` and `chrM` carry zero records.
- `bin/te-tracks-preflight <export> <bam|fai|sizes>`: reads contig names and lengths from a BAM header, a
  `.fai`, or a two-column sizes file; reports contigs in the alignment reference absent from the export,
  contigs in the export absent from the reference, and length disagreements; non-zero exit on any.

Acceptance: row counts equal across the three namespaces for every export; scaffold
`chr1_GL456210v1_random` maps to `GL456210.1` in both `ensembl` and `gencode`, `chrM` maps to `MT` in
`ensembl` and stays `chrM` in `gencode`; preflight against the GENCODE FASTA contig list
(`redesign-2026-09/audit/gencode_grcm39_fasta_contigs.tsv`, 61 contigs) passes for `gencode`, fails
for `ucsc` with the 39 scaffolds listed, and fails for `ensembl` with the 22 chromosomes listed; all
61 lengths agree. `docs/DECISIONS.md` entry 3 names the three namespaces.
