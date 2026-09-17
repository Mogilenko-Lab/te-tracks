# Phase 8: the gene child family, first snapshot

Goal: `te_mm39_gene` exists as a build family. Its first immutable snapshot pins the parent core build by full
`BUILD_ID`, the GENCODE vM37 annotation by digest and a versioned policy bundle, and publishes the exon-subtracted
SAF pair for the `interspersed` and `compat_tetranscripts_mm39` universes in the three contig namespaces, with a
per-record subtraction status, block registration, its own inventory and identity, verification and publication
through the release mechanics, and context capability `not_computed`.

Rulings binding this phase: `docs/DECISIONS.md` sections 4, 8, 9, 10, 12 and 16; milestone 2 H3 and H5; milestone 5
A1 and A2; phase 6 A2; phase 7 A3; milestone 7 A1 and A2; the ADR discussion rulings in
`redesign-2026-09/consults/adr_rulings_2026-09-17.md` (C1, C2, C3 with C5, C4, C6; item 3: vM37 first, the 10x
2024-A child follows). Design sources: `consults/gene_child_consult.md` Q1 to Q4, Q7 and Q8;
`consults/mask_policy_consult.md` Q1 and Q6. The plan file is authoritative where a prompt disagrees.

## Design

1. **Family and dispatch.** `build.sh --genome mm39 --family gene` selects `config/mm39_gene.env`; the core
   invocation stays exactly as it is. The family name is `te_<GENOME>_<FAMILY>`, here `te_mm39_gene`; the assembly
   stays `mm39` and `SPECIES` admits assemblies alone. Child stages live in `src/gene/[0-9][0-9]_*.sh` and run in
   name order; no core stage runs for the child. `--root` mode stages under `<root>/te_mm39_gene/.staging/<unique>/`
   and installs through `release.py`; `--build-dir` mode builds a scratch child.
2. **Parent.** `--parent-build-id <64 hex>` names the parent. In `--root` mode it resolves to
   `<root>/te_mm39/archive/<id>`; in `--build-dir` mode `--parent-dir <verified core build dir>` names the scratch
   core build directly, and the two forms exclude each other. The parent is verified before any read: `verify_build`
   recomputes both ids, and family `te_mm39` and assembly `mm39` are checked against the child config. A `current`
   symlink is refused as a parent argument; the runbook obtains the id from `release.py verify-current`. The child
   copies `universes.json` and `tables/contig_aliases.tsv` byte for byte, recording their digests as copied inputs,
   and copies nothing else; it reads the parent's `tables/rmsk_records.parquet`, `tables/taxonomy_canonical.tsv`
   and universe definitions at build time.
3. **Config `config/mm39_gene.env`.** `GENOME=mm39`, `ASSEMBLY=GRCm39`, `FAMILY=gene`, `PARENT_FAMILY=te_mm39`,
   `GENE_GTF_URL=https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M37/gencode.vM37.primary_assembly.annotation.gtf.gz`,
   `GENE_GTF_MD5=702e27a8727db66cd23e9f66f5aa1d38`, `GENE_ANNOTATION_NAME="GENCODE vM37"`,
   `EXON_MASK_POLICY=all_exons_unstranded_union_v1`, `MIN_RETAINED_BLOCK_BP=1`, `CONTEXT_CAPABILITY=not_computed`,
   `CHILD_UNIVERSES="interspersed compat_tetranscripts_mm39"`. The child fetch stage retains the GTF under
   `source/` as source role `gene_gtf` (cache `TE_TRACKS_SOURCE_CACHE`, md5 verified), outside `catalog.sources`.
4. **Mask and subtraction.** GTF contigs are normalized through the copied alias table's `chrom_gencode` column,
   scaffolds included; an unmapped contig fails the build. The mask is the union of every `exon` row on both
   strands, merged when overlapping or touching. Every record of the parent catalog is subtracted and every
   positive-length block is retained. Status per record: `unchanged` (zero removed bases), `trimmed` (one shorter
   block), `split` (several blocks), `fully_subtracted` (no block). Invariants: `retained_bp + removed_bp =
   length_bp` per record; zero residual overlap between any block and the mask; blocks per record disjoint,
   ordered and contained in the record.
5. **Products.**
   - `exports/{ucsc,ensembl,gencode}/{interspersed,compat_tetranscripts_mm39}/exon_subtracted/{subfamily,taxonomy_triple}.saf`:
     header `GeneID Chr Start End Strand`; one row per retained block; `GeneID` is `rmsk_name` for `subfamily.saf`
     and `<rmsk_name>:<family_id>:<class_id>` with the parent's canonical labels and unresolved tokens for
     `taxonomy_triple.saf`; `Chr` in the namespace; `Start` and `End` the block bounds, 1-based inclusive; `Strand`
     the record's; sorted like the parent's exports (contig bytes, numeric bounds, strand, `GeneID`).
   - `tables/export_feature_members.tsv.gz`: the parent's eight columns; per block one row at
     `(universe, exon_subtracted, subfamily, rmsk_name)` and one at `(universe, exon_subtracted, taxonomy_triple,
     taxonomy_triple)`, with `block_start_1` and `block_end_1`; namespace-invariant; uniqueness over the eight
     columns.
   - `tables/exports.tsv`: twelve rows in the parent's columns, with measured rows, distinct features and sha256.
   - `tables/exon_subtraction_status.tsv`: `rmsk_record_id, status, n_blocks, retained_bp, removed_bp` for every
     catalog record.
   - `tables/exon_subtraction_summary.tsv`: per universe `all_rmsk`, `interspersed`, `compat_tetranscripts_mm39`:
     `records, unchanged, trimmed, split, fully_subtracted, retained_records, blocks, retained_bp, removed_bp,
     records_on_unannotated_contigs`.
   - `tables/gene_annotation_coverage.tsv`: per parent contig `chrom_ucsc, gene_rows, transcript_rows, exon_rows,
     exon_union_bp, annotated`.
   - `tables/contig_aliases.tsv` and `universes.json`: exact copies of the parent's.
   - `source/<gtf basename>` and `source/SOURCES.json` in the child form: genome, assembly, parent family and ids,
     the `gene_gtf` role (url, md5, bytes) and the policy bundle.
   - `MANIFEST.json`, `BUILD_ID`, `CATALOG_ID`; the catalog identity is the parent's, copied, so the `CATALOG_ID`
     bytes equal the parent's.
6. **Identity and verification.** The child identity keeps `schema_version` `te-tracks-manifest-1` and the core
   field set, with non-null `parent_build_id` and `parent_catalog_id` and the additions `parent_family`,
   `copied_inputs` (path to sha256), `gene_annotation` (name, url, md5, sha256, bytes), `policy_bundle`
   (`exon_mask_policy`, one sentence defining the mask, `min_retained_block_bp`, `context_capability`) and
   `child_universes`. `catalog`, `species`, `assembly`, `declared_assembly`, `contig_set_sha256`, `universes` and
   `taxonomy_rule_version` are inherited from the verified parent; `build_sources` holds the `gene_gtf` role alone;
   `export_contracts` is the child roster (two contracts, two universes, three namespaces). `verify_build`
   branches on non-null parent ids: family `te_<assembly>_<kind>`; well-formed parent ids; catalog equal to the
   resolved parent's; copied inputs digest-equal to the parent's inventory entries; every registration record id
   present in the parent catalog with its blocks inside the record bounds; SAF rows equal registration rows per
   grouping and universe; status conservation on a sample; the coverage table consistent with the retained GTF.
   The parent resolves from `--parent-dir`, or from the sibling `te_mm39/archive/<parent_build_id>` under the root
   that encloses a `.staging` or `archive` build; a child without a resolvable parent fails verification.
   `release.py install`, `select` and `verify-current` for a child family require the parent archive present and
   verified under the same root (milestone 7 A1). Changing the GTF digest, any policy value, the roster or a
   parent id changes the child `BUILD_ID`; the parent's ids stay fixed.
7. **Fixtures and checks.** Independent oracles under `tests/fixtures/gene/`; checks `tests/checks/core/80_…` to
   `83_…`, exiting 3 while the child build is absent at `$TE_TRACKS_REFROOT/te_mm39_gene/build`.
   - Geometry cases (consult Q8): record 101..200 with exon 141..160 gives blocks 101..140 and 161..200, 80 and 20
     bases, `split`, both blocks under the parent id and group id; an intronic record stays `unchanged` beside a
     matched intergenic control (H3); a fully covered record has no block, status `fully_subtracted` and a status
     row; a record on a contig without annotation stays `unchanged` and its coverage row holds zeros; GTF `chr1` and
     scaffold `GL456210.1` map through the alias table to `chr1` and `chr1_GL456210v1_random`, an exon on the
     scaffold included, and the same split appears in all three namespaces; a one-base remainder; touching exon
     endpoints; an opposite-strand exon masks; adjacent exons merge; duplicate exon rows change nothing; an unknown
     GTF contig fails the build.
   - Dependency and identity cases through `tests/fixtures/publication/build_fixture.py` extended with a tiny child
     on the tiny core: missing parent; wrong parent id; one corrupt parent byte; a parent of another family or
     assembly; alias copy corruption; GTF digest change, policy change and roster change each move the child
     `BUILD_ID` while the parent ids stay; repeated child publication converges; a child install is refused when the
     parent archive is absent under the root; `select` and `verify-current` verify the parent too; an earlier core
     stays selectable after a child lands.
   - Full-build census: the acceptance numbers below, authored into
     `tests/expectations/mm39/exon_subtraction_summary.tsv` from this plan rather than from the build under test.
8. **Documentation.** `docs/OUTPUTS.md` child section: exports, tables, the mask sentence, the conservation
   guarantee, status semantics with H3's two sentences (`exon_subtraction_status` describes counting-support
   geometry; `unchanged` covers intronic and intergenic records alike), the coverage table, copied inputs, capability
   `not_computed`. `docs/RELEASES.md`: child identity fields, parent-first build order, dependency verification, the
   transfer rule that parent archives move before children. `docs/RUNBOOK.md`: the child invocation with the id
   from `verify-current`. README truth table rows for phase 8 to `tested`, the compat pair added.

## Acceptance

Pre-measured on parent `BUILD_ID 9ddf3622…` and the vM37 GTF (`consults/gene_child_consult.md`,
`consults/mask_policy_consult.md`; bedtools agreement in both). An observation that differs is a deviation to
report, never an expectation to edit.

| universe | records | retained records | blocks | fully_subtracted | split | trimmed | unchanged | removed bp | retained bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `all_rmsk` | 5,320,771 | 5,163,557 | 5,179,754 | 157,214 | 15,495 | 61,378 | 5,086,684 | 29,569,849 | 1,172,003,155 |
| `interspersed` | 3,764,949 | 3,668,830 | 3,684,934 | 96,119 | 15,406 | 52,703 | 3,600,721 | 26,235,918 | 1,090,369,890 |
| `compat_tetranscripts_mm39` | 3,799,629 | 3,701,642 | 3,717,740 | 97,987 | 15,399 | 52,842 | 3,633,401 | 26,503,064 | 1,094,973,237 |

Registration rows 7,369,868 (`interspersed`) and 7,435,480 (compat), 14,805,348 in total. Records on the 23
unannotated contigs: 2,638 / 1,612 / 1,754. GTF: 78,317 genes, 278,369 transcripts, 1,298,921 exons, exon union
160,549,642 bp, 38 annotated contigs of 61, md5 `702e27a8727db66cd23e9f66f5aa1d38`, sha256
`0d1673f3c0fff7d28ff63f4443a0863fa25f817d391982e465f7ec20f256bcd0`. Each SAF's data rows equal its universe's
blocks; distinct `GeneID`s per SAF are measured and reported. `tests/run.sh core` passes with the child checks;
`99_verify.py` on the child exits 0 with the parent resolved; `build.sh --root` on the scratch published root
installs the child beside the parent archive and `release.py verify-current --family te_mm39_gene` verifies it.
Peak resident memory and wall time of the child build are measured and recorded in the report.

## Deferred, recorded here so nothing pretends otherwise

- The record-by-transcript context relation: envelope 10 kb upstream and 2 kb downstream of transcript starts,
  `Ensembl_canonical` and `mRNA_start_NF` per transcript, per-pair status with per-record roll-up, gene-body
  geometry beside transcript geometry, UTR flags; a later snapshot of this family after the chr1 then mm39 scaling
  gate (DECISIONS 9).
- The 10x 2024-A annotation child (GENCODE vM33 filtered, md5 `7a998f670d6d0bdf599c046284da051b`): phase 9 or the
  first post-host snapshot, after the ARC GTF is verified from the 14761 run's reference path.
- The same-strand mask companion (after the chemistry pilot), a TES-side window (if the 3′ pilot needs it),
  subtracted BED or GTF views (with a named consumer), and the compat legacy comparison (phase 9 reconciliation).
