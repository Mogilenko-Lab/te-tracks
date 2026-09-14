# te-tracks

Reproducible transposable-element annotation tracks, built from RepeatMasker.

One canonical table holds one row per TE locus. 
Every delivered track is a projection of that table.
So bulk RNA-seq, single-cell RNA and single-cell ATAC are intended to share 
* one subfamily universe 
* and one locus identity. 

A TE locus in an ATAC peak and a TE locus in a bulk locus-level call are the same object,
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

The build writes a dated snapshot, fingerprints it, and moves `current` onto it. 
A re-run that reproduces the same content leaves `current` alone and records a `reconfirmed` row. 
A build that changes any output archives the previous snapshot and records both.

Every build carries a `BUILD_ID`, so a project cites one id and gets exactly those bytes.
`docs/RELEASES.md` holds the contract.

## Outputs

One interval set, projected along two axes: the **level** the name field carries, and the **format**
the tool parses. Bulk and single-cell tools read the same cells of this grid.

| Format | subfamily level | locus level |
|---|---|---|
| SAF, 1-based — featureCounts | `te_subfamily.saf` | `te_locus.saf` |
| BED, 0-based — IRescue, scTE, SoloTE, bedtools | `te_subfamily.bed` | `te_locus.bed` |
| GTF, 1-based — TEtranscripts, Telescope | `te_subfamily.gtf` | `te_locus.gtf` |
| locInd — TElocal | | `te_locus.locInd` |

At subfamily level the name field holds `subfamily`, and a count means reads per subfamily summed
over its loci. At locus level it holds `locus_id`, and a count means reads per insertion.
featureCounts and IRescue read subfamily level by default; TElocal and `irescue --locus-level`
resolve loci.

**Canonical table** — `te_loci.tsv.gz`, `te_loci.parquet`, `te_dim.tsv`. Every cell above is a
projection of it, and ledger joins and rollups read it directly.

**Interval variants**, the views whose intervals depart from the canonical set:

| Variant | Purpose |
|---|---|
| `te_subfamily_noExon.saf` | a joint gene + TE bulk matrix counts each read once |
| `te_context_{intronic,adjacent,intergenic}.saf` | genic-context strata for the bulk ladder |

**Namespace** — `ensembl_named/` carries every view on Ensembl contig names.

`docs/OUTPUTS.md` states every file, its columns and its consumer.

## Guarantees

- A re-run reproduces byte-identical outputs, and `BUILD_ID` proves it by content.
- Every published build stays on disk. Superseded builds move to `archive/` complete, so a result
  produced against an earlier annotation stays reproducible against the bytes that produced it.
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

`docs/RELEASES.md` records the `BUILD_ID` contract, the archive behaviour and how a project cites a
build.

`docs/PROVENANCE.md` records the derivation and the evidence that it reproduces the annotation the
lab has been using.
