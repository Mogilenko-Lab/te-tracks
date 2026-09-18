# te-tracks

te-tracks builds a reference projection of RepeatMasker for one assembly. Canonical tables,
named universes, registered exports and consumer fixtures share record identities and source
provenance. The mm39 package supplies the contracts below; the host publication follows
[the runbook](docs/RUNBOOK.md).

## Sources

| Source | Role in the redesign |
|---|---|
| Checksum-pinned RepeatMasker `.out` | Primary records, instance keys, source labels, consensus coordinates and overlap flags |
| UCSC browser `rmsk` table | One-time source qualification against the `.out`, with a retained report |
| UCSC `chromAlias` | Contig mappings across UCSC, Ensembl, GenBank and RefSeq namespaces |
| UCSC `chrom.sizes` | Contig lengths and coordinate bounds |
| Pinned Dfam metadata snapshot | Model lengths, classification lineage, Wicker ranks and curated clades |

The gene GTF belongs to the child family `te_<assembly>_gene`, which pins its parent core build
and one gene annotation.

## Build

`./build.sh --genome mm39 --build-dir <dir>` runs the registered stages, writes
`MANIFEST.json`, `BUILD_ID` and `CATALOG_ID`, and verifies the completed directory in place.
`./build.sh --genome mm39 --root <refroot>` builds in a unique staging directory, verifies,
installs at `te_mm39/archive/<BUILD_ID>/` and selects the relative `current` symlink.
Add `--no-select` to install while preserving the existing selection.
`./build.sh --genome mm39 --family gene --root <refroot> --parent-build-id <full-parent-id>`
publishes a GENCODE vM37 child with exon-subtracted SAFs for `interspersed` and
`compat_tetranscripts_mm39`. [docs/RUNBOOK.md](docs/RUNBOOK.md) gives the parent resolution
and scratch build commands.
`BUILD_ID` identifies the complete build; `CATALOG_ID` binds the record-producing RepeatMasker
`.out`, run identity, source-wide instance scope and decompressed canonical text tables for consumer
ledger keys, so a serializer or compressor change moves `BUILD_ID` alone.
[docs/RELEASES.md](docs/RELEASES.md) describes publication and transfer.
Set `TE_TRACKS_SOURCE_CACHE` to reuse checksum-matching cached sources; in-container builds use
a scratch directory, and host builds compare the recorded toolchain versions.

Tests run in-container against a scratch reference root:

```bash
tests/run.sh core
source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh
tests/run.sh consumers
tests/run.sh acceptance --build
tests/run.sh acceptance
```

The default reference root is `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`.
Each mode reports `pass`, `fail` or `unsupported` per check. All eleven acceptance checks are
required: acceptance exits 1 when it has no archive to judge, with
`unsupported: run tests/run.sh acceptance --build` naming the creation command.
A selected archive missing `BUILD_ID`, `CATALOG_ID` or `MANIFEST.json` fails. `acceptance --build` creates fresh
core and child archives under `$TE_TRACKS_REFROOT/acceptance/`; `acceptance` checks that pair again.
Set `TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source` for the offline
acceptance build. Existing archives stay retained. [Acceptance anchors](tests/expectations/mm39/README.md)
name the independent evidence behind each expected census.
[Consumer environment](docs/RUNBOOK.md#consumer-environment) records the activation recipe
and suite outcomes with and without executable shims. Core checks cover runner and acceptance prerequisites, the parser fixtures,
the qualification report, the record schema, instances, universes, the record fixtures,
taxonomy (30 to 34), exports and matrix binding (40 to 43), contigs (60 to 62), identity and publication (70 to 73),
and gene subtraction, identity and dependencies (80 to 83).

Phase 9b qualification recorded 11 passes for fresh-build acceptance, 11 for its rerun,
26 for core, and 15 passes plus one unsupported check for the activated consumer suite.
All four final commands exited 0. The unsupported check records Stellarscope's right-boundary
overlap defect; [RUNBOOK.md](docs/RUNBOOK.md#consumer-environment) gives its qualification limits.

## Outputs

Each build contains `source/`, `tables/`, `universes.json`, `exports/`, `MANIFEST.json`,
`BUILD_ID` and `CATALOG_ID`. Publication installs that directory under `archive/<BUILD_ID>/`
and selects it through the relative `current` symlink.

The truth table tracks the redesign artifacts: `delivered` means generated, `tested` means
verified against their contract, and `deferred` names the next evidence gate.
Exports follow `exports/<contig_namespace>/<universe>/<interval_variant>/<level>[_<profile>].<format>`.

| artifact | status | phase |
|---|---|---|
| `source/{mm39.fa.out.gz,rmsk.txt.gz,mm39.chromAlias.txt,mm39.chrom.sizes,SOURCES.json}` | delivered, tested | 1 |
| `source/qualification.md` | delivered, tested | 1 |
| `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md` | delivered, tested | 1 |
| `tests/fixtures/source/` | delivered, tested | 1 |
| `tests/fixtures/records/` | delivered, tested | 2 |
| `tests/expectations/mm39/` | delivered, tested | 2 |
| `tests/expectations/mm39/taxonomy_census.tsv` | delivered, tested | 3 |
| `tests/expectations/mm39/exon_subtraction_summary.tsv` | delivered, tested | 8 |
| `tests/fixtures/taxonomy/dfam_snapshot.tsv` | delivered, tested | 3 |
| `tests/fixtures/taxonomy/dfam_snapshot.provenance.json` | delivered, tested | 3 |
| `tests/fixtures/taxonomy/rule_cases.tsv` | delivered, tested | 3 |
| `tests/fixtures/taxonomy/rollup_counts.tsv` | delivered, tested | 3 |
| `tests/fixtures/taxonomy/weighting_context.tsv` | delivered, tested | 3 |
| `tests/fixtures/exports/` | delivered, tested | 4 |
| `tests/fixtures/consumers/` | delivered, tested: parser identities, registration, IRescue conservation, featureCounts, STARsolo, cellranger reference, bedtools, samtools and DuckDB; Stellarscope unsupported on its right-boundary defect | 5, 9a |
| `tests/lib/consumers.py` | delivered, tested | 5 |
| `tests/lib/records.py` | delivered, tested | 2 |
| `tests/fixtures/contigs/` | delivered, tested | 6 |
| `tests/fixtures/publication/` | delivered, tested | 7 |
| `tables/rmsk_records.tsv.gz` | delivered, tested | 2 |
| `tables/rmsk_records.parquet` | delivered, tested | 2 |
| `tables/rmsk_instance_members.tsv.gz` | delivered, tested | 2 |
| `tables/rmsk_taxonomy.tsv` | delivered, tested | 2 |
| `tables/taxonomy_canonical.tsv` | delivered, tested | 3 |
| `tables/taxonomy_resolution_report.tsv` | delivered, tested | 3 |
| `source/dfam_interspersed_mm39_snapshot.json.gz` | delivered, tested | 9a |
| `source/dfam_interspersed_mm39_snapshot.provenance.json` | delivered, tested; core payload has 52 files | 9a |
| `tables/taxonomy_dfam.tsv` | delivered, tested | 9a |
| `tables/taxonomy_dfam_models.tsv` | delivered, tested | 9a |
| `tables/dfam_lineage_nodes.tsv` | delivered, tested | 9a |
| `tables/dfam_model_clades.tsv` | delivered, tested | 9a |
| `tests/checks/consumers/17_starsolo_profile.required.py` | delivered, tested | 9a |
| `tests/checks/consumers/24_starsolo_exec.sh` | delivered, tested with consumer environment | 9a |
| `tests/checks/consumers/25_cellranger_mkref.sh` | delivered, tested with consumer environment | 9a |
| `universes.json` | delivered, tested | 2 |
| `tables/universe_members.tsv.gz` | delivered, tested | 2 |
| `tables/universe_summary.tsv` | delivered, tested | 2 |
| `tables/export_feature_members.tsv.gz` | delivered, tested | 4 |
| `tables/exports.tsv` | delivered, tested | 4 |
| `tables/contig_aliases.tsv` | delivered, tested | 6 |
| `tables/contig_coverage.tsv` | delivered, tested | 6 |
| `exports/ucsc/interspersed/full/record.bed` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/subfamily.bed` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/family.bed` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/record.gtf` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/record_starsolo.gtf` | delivered, tested | 9a |
| `exports/ucsc/interspersed/full/subfamily.gtf` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/subfamily.saf` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/taxonomy_triple.saf` | delivered, tested | 4 |
| `exports/ensembl/interspersed/full/record.bed` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/subfamily.bed` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/family.bed` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/record.gtf` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/record_starsolo.gtf` | delivered, tested | 9a |
| `exports/ensembl/interspersed/full/subfamily.gtf` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/subfamily.saf` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/taxonomy_triple.saf` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/record.bed` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/subfamily.bed` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/family.bed` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/record.gtf` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/record_starsolo.gtf` | delivered, tested | 9a |
| `exports/gencode/interspersed/full/subfamily.gtf` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/subfamily.saf` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/taxonomy_triple.saf` | delivered, tested | 6 |
| `exports/ucsc/all_rmsk/full/record.bed` | delivered, tested | 6 |
| `exports/ensembl/all_rmsk/full/record.bed` | delivered, tested | 6 |
| `exports/gencode/all_rmsk/full/record.bed` | delivered, tested | 6 |
| `te_mm39_gene`: `exports/ucsc/interspersed/exon_subtracted/subfamily.saf` | delivered, tested | 8 |
| `te_mm39_gene`: `exports/ensembl/interspersed/exon_subtracted/subfamily.saf` | delivered, tested | 8 |
| `te_mm39_gene`: `exports/gencode/interspersed/exon_subtracted/subfamily.saf` | delivered, tested | 8 |
| `te_mm39_gene`: `exports/{ucsc,ensembl,gencode}/interspersed/exon_subtracted/taxonomy_triple.saf` | delivered, tested | 8 |
| `te_mm39_gene`: `tables/exon_subtraction_status.tsv` | delivered, tested | 8 |
| `te_mm39_gene`: `exports/{ucsc,ensembl,gencode}/compat_tetranscripts_mm39/exon_subtracted/{subfamily,taxonomy_triple}.saf` | delivered, tested | 8 |
| `te_mm39_gene`: `tables/exon_subtraction_summary.tsv`, `tables/gene_annotation_coverage.tsv` | delivered, tested | 8 |
| `te_mm39_gene`: copied `universes.json`, `tables/contig_aliases.tsv`, registration and export inventory | delivered, tested | 8 |
| `te_mm39_gene`: retained GTF, source declaration, manifest and identities | delivered, tested | 8 |
| `tests/fixtures/gene/` | delivered, tested | 8 |
| `MANIFEST.json` | delivered, tested | 7 |
| `BUILD_ID` | delivered, tested | 7 |
| `CATALOG_ID` | delivered, tested | 7 |
| `bin/te-tracks-preflight` | delivered, tested | 6 |
| `docs/RUNBOOK.md`: gene child build and verification | delivered, tested | 8 |
| `docs/RUNBOOK.md`: host procedure and measured resource floors | delivered; commands reviewed and scratch publication tested; host filesystem qualification pending | 9b |
| `tests/checks/acceptance/`: eleven complete-build checks | delivered, tested | 9b |
| `tests/expectations/mm39/{source_pins,source_qualification,record_census,identity,gene_oracle,gene_oracle_m9}.tsv` | delivered, tested | 9b |
| `data/dfam/`: tracked snapshot, provenance and refresh script | delivered; retained input pins tested; refresh qualification recorded in phase 9a | 9a |
| `docs/OUTPUTS.md`: consumer map | delivered, tested: artifact bindings agree with registered contracts | 9b |
| `docs/PROVENANCE.md`: qualification and measured census | delivered, tested | 9b |
| `docs/RELEASES.md` | delivered, tested | 7 |

[docs/OUTPUTS.md](docs/OUTPUTS.md) specifies the schemas, serialization and deferred export contracts.

## Guarantees

The published contracts establish these guarantees:

- Four feature levels describe record, instance, subfamily and canonical family. Family and
  class rollups use `taxonomy_canonical`.
- Universes are named predicates over raw source classification in the complete catalog;
  `interspersed` is the default.
- `rmsk_record_id` is `<rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>`. Export membership
  registers each emitted feature and interval block to its source records.
- The `interspersed` full-interval exports contain eight files in each of `ucsc`, `ensembl` and
  `gencode`: `record.bed`, `subfamily.bed`, `family.bed`, `record.gtf`, `subfamily.gtf`,
  `record_starsolo.gtf`, `subfamily.saf` and `taxonomy_triple.saf`.
- Tables, GTF and SAF use 1-based inclusive coordinates; BED uses 0-based half-open coordinates.
  Contig aliases preserve record identity across `ucsc`, `ensembl` and `gencode` exports.
- Exon subtraction guarantees exon-disjoint sequence support under the declared mask;
  molecule exclusivity between gene and TE counts is a property of the joint counting run.
- `BUILD_ID` is the SHA-256 of the manifest `identity` section, computed as
  `sha256("te-tracks-build-v1\n" + canonical_json(identity))`. The identity covers the schema,
  sources, declared run identity, universe predicates, export contracts and complete file
  inventory; builder and validation evidence live in `provenance` outside the hash.
- Builds complete and verify in staging, install once into `archive/<BUILD_ID>/`, and become
  selected by an atomic replacement of the single `current` symlink. Every published build stays
  on disk; consumers pin the full id and the digests of the files they read.
- Scripts use `LC_ALL=C` for stable sort order.

## Genomes

mm39 builds and publishes through `build.sh --genome mm39 --root <refroot>`; admitting a genome
config requires its `SPECIES` entry in `src/lib/manifest.py`. hg38 is deferred pending source pins,
a class census, packaged-file reconciliation and source-wide instance numbering or a contig-scoped instance key.

## Design

[docs/DECISIONS.md](docs/DECISIONS.md) records the redesign choices and recorded deferrals.
[docs/PROVENANCE.md](docs/PROVENANCE.md) records source qualification, measured censuses and
the independent Dfam, legacy-GTF and bedtools evidence.


## Parking gates

| Artifact | Status | Evidence for the next decision |
|---|---|---|
| hg38 catalog and exports | deferred | Source pins, reviewed class census, packaged-file reconciliation and source-wide instance numbering or a contig-scoped key. |
| Transcript-context relation | deferred | ADR 9 geometry, transcript flags and tied-distance cases; chr1 then whole-mm39 scaling measurements. |
| ERV reconstruction units | deferred | LTR–internal candidate membership, strand/gap parameters, source instances and validated structural examples. |
| Age tiers | deferred | Pinned Dfam clade paths, record/median divergence and explicit consumer thresholds; structural evidence for full-length/ORF claims. |
| Stranded exon-mask companion | deferred | Chemistry pilot establishing the RNA-sense mate and strand-specific counting behavior. |
| 10x-annotation child | deferred | The exact 10x 2024-A filtered GENCODE vM33 annotation digest and geometry reconciliation with the counting reference. |
| Instance-level STARsolo profile | deferred | Mixed-name, mixed-strand, gap and junction fixtures with a declared feature grammar. |

The RNA pilot qualifies TEsingle's paired-mate handling, UMI graph and hard ties;
Stellarscope's right-boundary defect and largest-overlap preselection; and IRescue's even-start
expectation-maximization. Each consumer owns barcode thresholds, whitelist/empty-cell handling
and molecule allocation. Host publication and CRI backup verification precede downstream adoption.
The next gates are whole-release milestone review, the owner's clean host build, host filesystem
qualification, adoption of `te_catalog_id`/`te_build_id` in the 14761 ledger, the umbrella pin bump,
and the D2/D3 consumer pilots.
