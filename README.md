# te-tracks

Transposable-element annotation is fiddly and goes stale; keeping it current by hand gave each project a different annotation.
The projects needed one way to build it: RepeatMasker's three tokens straddle the field's ranks, leaving 558,808 mm39 records under family `Alu` and zero hits for `SINE/B1`.
Counting tools build features from different keys, so their numbers for one locus fail to join.
Counts carry no record of the annotation they came from, so two analyses cannot be shown to share one.

## What this is

te-tracks projects one RepeatMasker run for one assembly into canonical tables, named universes and registered exports, with every emitted feature joined back to its source record.
Every input is pinned by digest. Every published build is immutable and addressable by its full `BUILD_ID`.

## Inputs

| Pinned source | Role |
|---|---|
| RepeatMasker `.out` | Primary records, instance keys, source labels, consensus coordinates and overlap flags |
| UCSC browser `rmsk` table | Source qualification against the `.out`, with a retained report |
| UCSC `chromAlias` | UCSC, Ensembl, GenBank and RefSeq contig mappings |
| UCSC `chrom.sizes` | Contig lengths and coordinate bounds |
| Dfam metadata snapshot | Model lengths, classification lineage, Wicker ranks and curated clades |
| Declared genome FASTA digest | Alignment assembly pin; consumers retain the sequence bytes |

The gene annotation is the parameter of child family `te_<assembly>_gene`, which pins one parent core build and one GTF by digest; the delivered child uses GENCODE vM37.
[Source provenance](docs/PROVENANCE.md) records the pins, qualification, measured censuses and independent Dfam, legacy-GTF and bedtools evidence.

## Outputs

Each build contains `source/`, `tables/`, `universes.json`, `exports/`, `MANIFEST.json`, `BUILD_ID` and `CATALOG_ID`.
Canonical tables describe records, source instances, subfamilies and canonical families; family and class rollups use `taxonomy_canonical`.
Six universes select records by raw source classification, with `interspersed` as the default.
`rmsk_record_id` is `<rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>`; export registration joins each emitted feature and interval block to its records.
Tables, GTF and SAF use 1-based inclusive coordinates; BED uses 0-based half-open coordinates.
Tables retain UCSC contigs, and exports use `ucsc`, `ensembl` or `gencode` names while preserving record identity.
Exports follow `exports/<contig_namespace>/<universe>/<interval_variant>/<level>[_<profile>].<format>`.
The [artifact status table](docs/OUTPUTS.md#artifact-status) records each delivered artifact and its test status; [OUTPUTS.md](docs/OUTPUTS.md) defines schemas, serialization and export contracts.

## What each output supports

The first seven rows give suffixes below `exports/<contig_namespace>/<universe>/`; the [consumer map](docs/OUTPUTS.md#consumer-map) gives full paths, bindings and qualification limits.

| Artifact | Universe | Consumer and counting question |
|---|---|---|
| `full/{record,subfamily}.bed` | `interspersed` | IRescue: RNA support per record or subfamily |
| `full/family.bed` | `interspersed` | bedtools and family overlap readers: interval support per canonical class/family bucket |
| `full/record.gtf` | `interspersed` | TEsingle and TElocal: record assignment through their subfamily grammar; TEtranscripts: canonical taxonomy triples; Stellarscope: record/instance support after its boundary gate |
| `full/record_starsolo.gtf` | `interspersed` | STARsolo and cellranger: record counts through record-as-gene grammar |
| `full/subfamily.gtf` | `interspersed` | TEsingle, TElocal, TEtranscripts and qualified Stellarscope: subfamily sensitivity counting |
| `full/{subfamily,taxonomy_triple}.saf` | `interspersed` | featureCounts: full-interval sensitivity counts |
| Child `exon_subtracted/{subfamily,taxonomy_triple}.saf` | `interspersed`; `compat_tetranscripts_mm39` for legacy reproduction | The bulk featureCounts product: RNA counts over exon-disjoint sequence |
| `all_rmsk/full/record.bed` | `all_rmsk` | The interval catalog a chromatin-accessibility ledger keys on |
| Child `tables/record_transcript_context.tsv.gz` | `all_rmsk` | Reference joins: transcript overlap, strand, flags and endpoint distances for consumer context labels |
| Child `tables/record_context.tsv.gz` | `all_rmsk` | Reference joins: per-record exon support, gene-body overlap and nearest outside gene endpoints |
| `tables/taxonomy_dfam.tsv` and normalized companions | `interspersed` | Aggregate reporting: lineage, rank and clade vocabulary joined to names |

Expectation-maximization routes take the unmasked record exports with the full gene annotation.
Exon subtraction guarantees exon-disjoint sequence under the declared mask; the joint counting run determines molecule allocation between genes and TEs.

## Biological questions

The outputs support measurements of transposable-element RNA per cell or sample at record, subfamily, family and class grain, with lineage and divergence strata.
They support measurements of accessible annotated intervals and the exon-disjoint portions of their sequence.
They do not settle whether a copy transcribes from its own promoter, whether it is structurally intact, which insertion a group of records belongs to, or any age or activity verdict.
[DECISIONS.md](docs/DECISIONS.md) records the decisions and the evidence those interpretations require.

### Deferrals and required evidence

| Artifact | Status | Evidence for the next decision |
|---|---|---|
| hg38 catalog and exports | deferred | Source pins, reviewed class census, packaged-file reconciliation and source-wide instance numbering or a contig-scoped key. |
| ERV reconstruction units | deferred | LTR–internal candidate membership, strand/gap parameters, source instances and validated structural examples. |
| Age tiers | deferred | Pinned Dfam clade paths, record/median divergence and explicit consumer thresholds; structural evidence for full-length/ORF claims. |
| Stranded exon-mask companion | deferred | Chemistry pilot establishing the RNA-sense mate and strand-specific counting behavior. |
| 10x-annotation child | deferred | The exact 10x 2024-A filtered GENCODE vM33 annotation digest and geometry reconciliation with the counting reference. |
| Instance-level STARsolo profile | deferred | Mixed-name, mixed-strand, gap and junction fixtures with a declared feature grammar. |

RNA pilots qualify TEsingle's paired-mate handling, UMI graph and hard ties; Stellarscope's right-boundary defect and largest-overlap preselection; and IRescue's even-start expectation-maximization.
Consumers own barcode thresholds, whitelist/empty-cell handling and molecule allocation.
Downstream adoption requires whole-release review, the owner's clean host build, host filesystem qualification, CRI backup verification, `te_catalog_id`/`te_build_id` in the 14761 ledger, the umbrella pin bump and D2/D3 pilot evidence.

## Build and test

`./build.sh --genome mm39 --build-dir <dir>` runs the stages, writes the manifest and IDs, and verifies the directory in place.
`./build.sh --genome mm39 --root <refroot>` builds and verifies in unique staging, installs at `te_mm39/archive/<BUILD_ID>/` and atomically selects the relative `current` symlink; `--no-select` preserves the existing selection.
`./build.sh --genome mm39 --family gene --root <refroot> --parent-build-id <full-parent-id>` publishes the GENCODE vM37 child for `interspersed` and `compat_tetranscripts_mm39`.
[The runbook](docs/RUNBOOK.md) gives parent resolution, scratch and host commands; [RELEASES.md](docs/RELEASES.md) defines publication and transfer.
`BUILD_ID = sha256("te-tracks-build-v1\n" + canonical_json(identity))` covers the schema, sources, run identity, universes, export contracts and complete file inventory; builder and validation evidence live in `provenance` outside the hash.
`CATALOG_ID` binds the record-producing `.out`, run identity, source-wide instance scope and decompressed canonical tables for ledger keys; serializer or compressor changes move `BUILD_ID` alone.
Every published build stays on disk; consumers resolve `current` once and pin the full ID and file digests.
Scripts use `LC_ALL=C`; `TE_TRACKS_SOURCE_CACHE` reuses checksum-matching sources, and host builds compare recorded toolchain versions.

```bash
tests/run.sh core
source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh
tests/run.sh consumers
tests/run.sh acceptance --build
tests/run.sh acceptance
```

Tests use the scratch root `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`; `--refroot DIR` selects another root.
Each check reports `pass`, `fail` or `unsupported`; all eleven acceptance checks are required.
An absent archive yields exit 1 and `unsupported: run tests/run.sh acceptance --build`; a selected archive missing `BUILD_ID`, `CATALOG_ID` or `MANIFEST.json` fails.
`acceptance --build` requires an empty `$TE_TRACKS_REFROOT/acceptance/` and publishes a fresh core/child pair there; `acceptance` checks that pair again, with development archives retained.
The offline build uses `TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source`.
[Acceptance anchors](tests/expectations/mm39/README.md) name independent census evidence; the [consumer environment](docs/RUNBOOK.md#consumer-environment) gives activation and outcomes with and without executable shims.
The qualified test surface has 30 core passes, 11 acceptance passes, and 16 consumer checks with 15 passes and one unsupported Stellarscope boundary check; all three commands exit 0.
Core covers runner prerequisites, parsing, source qualification, records, instances, universes, taxonomy (30–34), exports and matrix binding (40–43), contigs (60–62), publication (70–73) and gene subtraction and dependencies (80–83).
Consumer runs share private generated fixtures across checks; `TE_TRACKS_CONSUMER_FIXTURES` selects a retained override.
`tests/run.sh` and `build.sh` disable Python bytecode writes.

## Genomes

mm39 builds and publishes through `build.sh --genome mm39 --root <refroot>`; a genome config requires its `SPECIES` entry in `src/lib/manifest.py`.
hg38 admission requires source pins, a class census, packaged-file reconciliation and source-wide instance numbering or a contig-scoped instance key.
