# Outputs

Coordinates are **1-based inclusive** in tables and **0-based half-open** in BED. Each entry states
which applies.

## Built today

### `te_loci.tsv.gz` — the canonical table, 1-based

One row per TE locus.

| # | Column | Note |
|---|---|---|
| 1 | `locus_id` | `<subfamily>|<chrom>:<start>-<end>|<strand>`, the cross-modality join key |
| 2 | `chrom` | UCSC names in the default view |
| 3 | `start` | 1-based inclusive |
| 4 | `end` | inclusive |
| 5 | `strand` | `+` or `-` |
| 6 | `subfamily` | rmsk `repName` |
| 7 | `family` | rmsk `repFamily` |
| 8 | `class` | rmsk `repClass` |
| 9 | `sw_score` | RepeatMasker Smith-Waterman score |
| 10 | `perc_div` | percent divergence from the consensus; separates young copies from old |
| 11 | `perc_del` | percent deletion |
| 12 | `perc_ins` | percent insertion |
| 13 | `rmsk_id` | RepeatMasker fragment id, joins fragments of one insertion |
| 14 | `length_bp` | `end - start + 1` |
| 15 | `dup_index` | per-subfamily ordinal, for `subfamily_dupN` compatibility |

### `te_dim.tsv` — the dimension table, one row per triple

`subfamily`, `family`, `class`, `n_loci`, `total_bp`.

Views carry the key; this table carries the hierarchy. Rollups from locus to subfamily to family to
class are a join and a `GROUP BY`.

### `MANIFEST.json`

Source URLs and md5s, output md5s and byte counts, row counts, the class and identity policy, and
the builder's git SHA. A re-run over an existing snapshot leaves it in place, so the recorded SHA
keeps naming the version that produced the bytes.

## Planned

These land once the identity and policy questions settle. Each is a projection of the canonical
table, so adding one changes no upstream stage.

Views are named `te_<level>[_<variant>].<format>`. The level sets the name field, the format sets the
container, and the two are independent. Consumers appear here rather than in the layout, so one file
serves every tool that reads its format.

| File | Coordinates | Name field | Consumer |
|---|---|---|---|
| `te_subfamily.saf` | 1-based | `subfamily` | featureCounts |
| `te_locus.saf` | 1-based | `locus_id` | featureCounts, locus-level bulk counting |
| `te_subfamily.bed` | 0-based | `subfamily` | IRescue default, scTE, SoloTE |
| `te_locus.bed` | 0-based | `locus_id` | `irescue --locus-level`, ATAC peak intersection |
| `te_subfamily.gtf` | 1-based | `gene_id` = `subfamily` | TEtranscripts |
| `te_locus.gtf` | 1-based | locus attribute | Telescope |
| `te_locus.locInd` | 1-based | `locus_id` | TElocal |
| `te_subfamily_noExon.saf` | 1-based | `subfamily` | featureCounts, joint gene + TE matrices |
| `te_context_{intronic,adjacent,intergenic}.saf` | 1-based | `subfamily` | context-stratified counting |
| `te_loci.parquet` | 1-based | — | DuckDB ledgers |
| `locus_context.tsv` | — | — | `locus_id`, `genic_context`, signed `dist_to_gene`, `nearest_gene_id`, `nearest_gene_strand` |
| `rename_map.tsv` | — | — | packaged-annotation names mapped to rmsk names, for comparisons against earlier results |
| `ensembl_named/` | as above | as above | consumers on Ensembl contig names |

`te_subfamily.gtf` and `te_locus.gtf` differ in the attribute that names the feature, so each tool
reads the file built for it. The exact attribute keys are confirmed against each tool's
documentation when the view stage is written.

### BED column layout

BED6 core keeps `bedtools` and IRescue working unmodified. Columns 7 onward carry the annotation and
are ignored by tools that read the first six.

```
1 chrom  2 start(0-based)  3 end  4 name  5 score  6 strand
7 subfamily  8 family  9 class  10 perc_div  11 genic_context  12 dist_to_gene
```

`score` is `min(sw_score, 1000)`, inside the BED range. Column 10 carries divergence for anyone
filtering young families.

### `locus_context.tsv`

`dist_to_gene` is signed and exact, so a context threshold is a query parameter.
`nearest_gene_strand` supports separating co-oriented from antiparallel read-through.
