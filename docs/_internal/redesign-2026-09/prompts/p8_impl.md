# te-tracks phase 8: the gene child family, seam only

You are the implementer for phase 8 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phases 0 to 7 have landed: read
`AGENTS.md`, `build.sh` (two modes: `--build-dir` and `--root`), `src/*.sh`, `src/lib/*.py` (records,
universes, taxonomy, exports, contigs, manifest), `src/90_manifest.py`, `src/99_verify.py`, `src/release.py`,
`tests/run.sh`, `docs/OUTPUTS.md`, `docs/RELEASES.md`.

## Read first
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md` (your phase,
   including the deferred list that this phase must leave untouched, and ruling H3 on `gene_context`)
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` entries 4, 5, 7
3. `docs/_internal/redesign-2026-09/consults/ADR4_consult.md` (exon subtraction semantics; registration of
   pieces) and `A_consumer_contracts.md` featureCounts section (the lab's exon-subtraction recipe)
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding)

## Facts
- Gene annotation: GENCODE vM37 primary assembly GTF,
  `https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M37/gencode.vM37.primary_assembly.annotation.gtf.gz`,
  md5 `702e27a8727db66cd23e9f66f5aa1d38`; a cached copy with that md5 sits in the read-only refcache at
  `/data2/users/shared/refcache/mm39/mm39_20260911/gencode.vM37.primary_assembly.annotation.gtf.gz`; put a
  copy (hardlink is impossible across filesystems, so copy once) into
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/source/` under the URL basename, and let the fetch stage
  find it through `TE_TRACKS_SOURCE_CACHE`.
- GENCODE contig names: chromosomes `chr1` … `chrM`, scaffolds by GenBank accession
  (`GL456210.1`); map them to UCSC names through `tables/contig_aliases.tsv` (`chrom_gencode` column) of the
  parent build before subtraction.
- Legacy expectation (to re-measure, then record): the lab's no-exon SAF for the `compat_tetranscripts_mm39`
  universe retained 3,717,740 of 3,799,629 records with at least one piece.

## Deliverables (exact paths)
1. `config/mm39_gene.env`: `GENOME=mm39`, `FAMILY=te_mm39_gene`, `PARENT_FAMILY=te_mm39`, `GENE_GTF_URL`,
   `GENE_GTF_MD5`, `GENE_ANNOTATION="GENCODE vM37"`, `EXON_MASK_POLICY="all_exons_unstranded_union_v1"`.
   Comments state intent only.
2. `build.sh` accepts `--genome mm39 --family gene` (or reads `FAMILY` from `config/mm39_gene.env` given as
   `--config`); a child build requires `--parent <dir-or-archive>`: in `--build-dir` mode the parent is the
   core build dir; in `--root` mode the parent is `<root>/te_mm39/current` resolved to its archive, and the
   manifest pins `parent_build_id` and `parent_catalog_id` to the parent's two ids. Child stages: `00_fetch_sources.sh`
   (GTF only, for the child config), `50_build_exon_subtracted.sh`, then manifest and verify as for the core.
   The child build dir holds `source/` (the GTF), `tables/`, `exports/`, `MANIFEST.json`, `BUILD_ID`, plus
   `parent/BUILD_ID` and `parent/CATALOG_ID` (copies of the parent ids); nothing else from the parent is copied.
3. `src/50_build_exon_subtracted.sh <build-dir> <config.env>` calling `src/lib/exon_subtract.py`:
   - mask = union of every `exon` row of the GTF, both strands merged, contigs renamed to UCSC;
   - for every record in the parent's `interspersed` universe: subtract the mask from
     `[start_1, end_1]`; emit surviving pieces;
   - `exports/{ucsc,ensembl,gencode}/interspersed/exon_subtracted/subfamily.saf` (GeneID = rmsk_name, one
     row per piece) and `taxonomy_triple.saf`, sorted like the parent's exports;
   - `tables/export_feature_members.tsv.gz` for these exports keyed `(universe_name, variant =
     exon_subtracted, feature_level)` with `block_start_1`, `block_end_1` per piece, namespace-invariant like the
     parent's; `tables/exports.tsv` with one row per export file;
   - `tables/exon_subtraction_status.tsv`: `rmsk_record_id, status (unchanged|trimmed|split|fully_subtracted),
     pieces, retained_bp, removed_bp`; assert `retained_bp + removed_bp = length_bp` for every record and zero
     residual overlap between any piece and the mask (interval check, vectorised);
   - `tables/exon_subtraction_summary.tsv`: counts per status, records retaining at least one piece, for the
     `interspersed` universe and, computed alongside, for `compat_tetranscripts_mm39` (so the legacy number can
     be compared).
4. Checks under `tests/checks/core/` (exit 3 when the child build is absent at
   `$TE_TRACKS_REFROOT/te_mm39_gene/build`):
   - `80_exon_subtraction.py`: conservation identity per record; zero residual overlap on a 100,000-record
     sample against the mask; status counts equal `tests/expectations/mm39/exon_subtraction_summary.tsv`
     (author it from your first measured run and say so in the report; the orchestrator confirms
     independently); the `compat_tetranscripts_mm39` retained count reported next to the legacy 3,717,740
     (equal or a stated difference with a reason: the legacy recipe stripped `chr` and used bedtools
     subtract on the same GTF; differences point at contig handling or the exon set).
   - `81_exon_subtraction_fixtures.py`: hand-authored GTF + records fixtures under
     `tests/fixtures/gene/`: central exon splits a record into two pieces with the parent id; exon covering
     the record fully subtracts it; exon on the opposite strand still masks (unstranded union); adjacent
     exons merge; a GENCODE scaffold name maps through the alias table; expected outputs authored by hand.
   - `82_child_manifest.py`: the child `MANIFEST.json` identity carries `parent_build_id` and `parent_catalog_id`
     equal to the parent's ids, `gene_annotation` with url and md5, `exon_mask_policy`; changing either parent id
     in a copy changes the child `BUILD_ID`.
5. `docs/OUTPUTS.md`: the child family section (exports, status and summary tables, the mask definition in
   one sentence, the conservation guarantee) and, per ruling H3, two sentences: `exon_subtraction_status`
   describes counting-support geometry under the exon mask, and `unchanged` covers intronic and intergenic
   records alike; a gene-context relation waits for the transcript-context design session. `docs/RELEASES.md`:
   child build procedure (parent first, then child; the child pins both parent ids). README truth table rows for
   phase 8 to `tested`. Leave the deferred list in the phase file untouched and add nothing that interprets gene
   context.

## Rules
- Touch only: `config/mm39_gene.env`, `build.sh`, `src/00_fetch_sources.sh` (child GTF handling),
  `src/50_build_exon_subtracted.sh`, `src/lib/exon_subtract.py`, `src/lib/manifest.py` (child identity
  fields), `tests/checks/core/8*`, `tests/fixtures/gene/**`, `tests/expectations/mm39/exon_subtraction_summary.tsv`,
  `docs/OUTPUTS.md`, `docs/RELEASES.md`, `README.md` (truth table).
- No git writes. No installs. No network (the GTF is in the refcache). Never write into the refcache.
- Report a deviation instead of editing a number or a plan file to fit.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
time ./build.sh --genome mm39 --config config/mm39_gene.env --build-dir "$TE_TRACKS_REFROOT/te_mm39_gene/build" --parent "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
C="$TE_TRACKS_REFROOT/te_mm39_gene/build"
cat "$C/tables/exon_subtraction_summary.tsv"; cat "$C/BUILD_ID" "$C/CATALOG_ID"; cat "$C/parent/BUILD_ID" "$C/parent/CATALOG_ID"
python3 -c "import json;m=json.load(open('$C/MANIFEST.json'));print(m['identity']['parent_build_id'], m['identity']['parent_catalog_id'], m['identity'].get('exon_mask_policy'))"
for ns in ucsc ensembl gencode; do wc -l "$C/exports/$ns/interspersed/exon_subtracted/"*; done
python3 src/99_verify.py "$C"; echo "exit=$?"
tests/run.sh core; echo "exit=$?"
git status --short
```

## Final message
Every file created or changed; acceptance outputs verbatim; the measured status counts and the retained
count for `compat_tetranscripts_mm39` beside the legacy 3,717,740 with your explanation of any difference;
any deviation.
