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

The canonical table carries every TE locus at full length. An `exon_overlap_bp` column lands with the
genic-context stage, so a consumer reads the overlap and cuts its own threshold.

Subtraction serves one purpose: keeping a read from counting toward both a gene and a TE inside a
joint matrix. `te_subfamily_noExon.saf` applies it, and the joint bulk matrix reads that view. Every
other view carries full-length intervals, which is what locus-level EM and peak intersection need.

So subtraction follows the analysis that needs it rather than the modality. A single-cell joint
gene + TE matrix reads the subtracted view on the same grounds.

## Contig names ship in both flavours

The default views carry UCSC names (`chr1`). `ensembl_named/` carries the same views with Ensembl
names (`1`), mapped through `chromAlias.txt`.

UCSC names match the genome FASTA, the GENCODE gene annotation, the bulk alignments and the 10x
references, so the default view aligns with the BAMs every consumer already has. Shipping both
flavours from one build keeps the mapping in one place, and each flavour carries its own md5.

## The class policy is explicit

Two filters define the TE set, and they rest on different grounds.

**`TE_CLASSES` carries the biology.** `repClass` `tRNA`, `rRNA`, `scRNA`, `snRNA` and `srpRNA` name
Pol III and structural-RNA loci, and holding them out keeps abundant structural RNA clear of a TE
count. In mm39 that leaves the 3,508 annotated tRNA genes outside the set. The carried classes
include `Satellite`, so "TE" in these tracks means "interspersed repeat plus satellite".

**`EXCLUDE_FAMILY_PREFIX` carries provenance.** `"tRNA"` matches `repFamily` `tRNA`, `tRNA-RTE` and
`tRNA-Deu` — the families RepeatMasker names for the ancestral source RNA rather than for a lineage.
In mm39 it drops one subfamily each: `LFSINE_Vert` 1,235, `MamSINE1` 925, `AmnSINE2` 388, all
ancient conserved vertebrate and amniote SINEs. The tRNA-derived SINE families carrying lineage
names stay in the set: `B4` 380,688, `B2` 370,294, `MIR` 120,815, `ID` 60,640 loci. So this filter
selects on nomenclature, and it earns its place by reproducing the packaged annotation behind
13036-DM, 14839-DM and the earlier Yasmine results, which `docs/PROVENANCE.md` records exactly.

Setting `EXCLUDE_FAMILY_PREFIX=""` requires a code change, since an empty prefix anchors to `^` and
matches every family.

Changing either policy is a config edit. It yields a new `BUILD_ID`, the previous build stays in
`archive/`, and `src/99_verify.sh` compares the result against
`tests/expectations/<genome>_class_counts.tsv`.
