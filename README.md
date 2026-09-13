# te-tracks

Reproducible transposable-element annotation tracks, built from RepeatMasker.

One canonical table holds one row per TE locus. Every delivered track is a projection of that table,
so bulk RNA-seq, single-cell RNA and single-cell ATAC share one subfamily universe and one locus
identity. A TE locus in an ATAC peak and a TE locus in a bulk locus-level call are the same object,
joined by string equality on `locus_id`.

## Sources

Two public URLs and one gene annotation. All three are md5-pinned in `config/<genome>.env`.

| Source | Provides |
|---|---|
| UCSC `<genome>/database/rmsk.txt.gz` | the RepeatMasker run: coordinates, subfamily, family, class, divergence |
| UCSC `<genome>/bigZips/<genome>.chromAlias.txt` | exact contig-name mapping, UCSC to Ensembl, scaffolds included |
| GENCODE gene annotation | gene bodies and exons, for genic context and for the bulk exon-subtracted view |

## Build

```
./build.sh --genome mm39 --dest /data2/users/shared/refcache
```

The build writes a dated snapshot and moves `current` onto it. Transfer the snapshot to any other
root and verify it with `src/99_verify.sh --check`.

## Outputs

`docs/OUTPUTS.md` states every file, its columns and its consumer.

| Family | Files | Consumer |
|---|---|---|
| canonical | `te_loci.tsv.gz`, `te_loci.parquet`, `te_dim.tsv` | ledger joins, rollups, any new view |
| bulk | `subfamily.saf`, `subfamily_noExon.saf`, `context_*.saf`, `te_loci.locInd` | featureCounts, TElocal |
| single cell | `te_subfamily.bed`, `te_locus.bed`, `te_loci.gtf` | IRescue, scTE, SoloTE, Telescope |
| namespace | `ensembl_named/` | consumers on Ensembl contig names |

## Guarantees

- A re-run reproduces byte-identical outputs. `src/99_verify.sh --check` proves it by md5.
- Scripts run under `LC_ALL=C`, so sort order is stable across machines and locales.
- Data files carry coordinates and annotation. `MANIFEST.json` carries timestamps, input md5s,
  output md5s and the builder's git SHA.
- Table coordinates are 1-based inclusive. BED coordinates are 0-based half-open. `docs/OUTPUTS.md`
  states which applies to each file.
- Contig names ship in UCSC (`chr1`) and Ensembl (`1`) flavours, mapped through `chromAlias`.
- Every assertion in `src/99_verify.sh` carries an expected number, held in `tests/expectations/`.

## Genomes

`--genome mm39` is built today. `rmsk` and `chromAlias` are published for `mm10` and `hg38`, so the
same pins and the same rule extend to them by adding a `config/<genome>.env`.

## Design

`docs/DECISIONS.md` records the choices that shape every output: the `locus_id` form, the contig
namespace, exon subtraction as a view, and the class policy.

`docs/PROVENANCE.md` records the derivation and the evidence that it reproduces the annotation the
lab has been using.
