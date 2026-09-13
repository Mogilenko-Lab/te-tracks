# Decisions

Four choices shape every output. Each is recorded with its reason.

## One canonical table, generated views

`te_loci.tsv.gz` holds one row per TE locus. Every delivered track is a projection of it.

This keeps one subfamily universe and one locus identity across bulk RNA-seq, single-cell RNA and
single-cell ATAC. A TE locus in an ATAC peak and a TE locus in a bulk locus-level call are the same
object, joined by string equality on `locus_id`.

## `locus_id` is coordinate-derived

```
locus_id = <subfamily>|<chrom>:<start>-<end>|<strand>
example    L1MdA_VI|chr1:3050294-3050775|+
```

The form is set by `LOCUS_ID_FORM` in the genome config.

`locus_id` is the join key across bulk locus-level calls, ATAC peak intersections and any ledger
built on top. A coordinate-derived key stays stable when the class filter changes, when a source
release adds records, and when views are added.

`dup_index` travels beside it as a separate column, so tools expecting `subfamily_dupN` naming have
what they need. The column is assigned after a deterministic sort, and `locus_id` carries the
identity.

## Exon subtraction is a view

The canonical table carries every TE locus at full length and an `exon_overlap_bp` column.

Subtraction serves one purpose: keeping a read from counting toward both a gene and a TE inside a
joint bulk matrix. The bulk views apply it. Single-cell TE tools quantify TEs on their own terms, so
they read the full-length intervals, and locus boundaries stay intact for locus-level EM.

## Contig names ship in both flavours

The default views carry UCSC names (`chr1`). `ensembl_named/` carries the same views with Ensembl
names (`1`), mapped through `chromAlias.txt`.

UCSC names match the genome FASTA, the GENCODE gene annotation, the bulk alignments and the 10x
references, so the default view aligns with the BAMs every consumer already has. Shipping both
flavours from one build keeps the mapping in one place, and each flavour carries its own md5.

## The class policy is explicit

`TE_CLASSES` in the genome config lists the carried classes, and `EXCLUDE_FAMILY_PREFIX` removes the
tRNA-derived SINE families.

The carried set includes `Satellite`, so "TE" in these tracks means "interspersed repeat plus
satellite". `docs/PROVENANCE.md` records the record counts each rule accounts for. Changing the
policy is a config edit, and `src/99_verify.sh` compares the result against
`tests/expectations/<genome>_class_counts.tsv`.
