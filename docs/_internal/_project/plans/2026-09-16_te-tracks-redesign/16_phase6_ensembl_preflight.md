# Phase 6: Ensembl namespace, aliases, coverage, preflight

Deliverables
- `tables/contig_aliases.tsv`: `chrom_ucsc, chrom_ensembl, chrom_genbank, chrom_refseq, length_bp`
  from `chromAlias.txt` and `chrom.sizes`; injectivity asserted; 61 rows.
- `exports/ensembl/interspersed/full/{record.gtf, subfamily.saf}` and phase 8's SAF: same rows,
  contig column renamed through the alias table; `rmsk_record_id` unchanged (UCSC names inside).
- `tables/contig_coverage.tsv`: per contig: records, in `interspersed`, has alias, length agrees.
  `chr4_JH584295v1_random` and `chrM` carry zero records.
- `bin/te-tracks-preflight <export> <bam|fai>`: reports contigs in the BAM absent from the export,
  contigs in the export absent from the BAM, and length disagreements; non-zero exit on any.

Acceptance: `record.gtf` UCSC and Ensembl row counts equal; scaffold `chr1_GL456210v1_random`
maps to `GL456210.1`; preflight against `/data2/users/shared/refcache/mm39/.../GRCm39.genome.fa.gz`
index passes for UCSC and fails for Ensembl with the expected list.
