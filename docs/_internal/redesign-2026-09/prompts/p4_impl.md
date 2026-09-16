# te-tracks phase 4: `interspersed` exports in the UCSC namespace

You are the implementer for phase 4 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phases 0 to 3 have landed: read
`AGENTS.md`, `tests/run.sh` (checks: executables under `tests/checks/<mode>/`, exit 0 pass, 3 unsupported,
other fail; build dir `$TE_TRACKS_REFROOT/te_mm39/build`), `docs/OUTPUTS.md` (table contracts),
`src/lib/build_records.py`, `src/lib/build_universes.py`, `src/lib/build_taxonomy.py`, and the tables under
the build dir.

## Read first
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md` (your phase)
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` entries 1, 3, 5
3. `docs/_internal/redesign-2026-09/consults/ADR5_consult.md` sections 3 and 4 (path grammar; tool attribute
   mapping) and `docs/_internal/redesign-2026-09/consults/A_consumer_contracts.md` (what each parser reads;
   the safe name alphabet)
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding)

## Facts
- Universe `interspersed`: 3,764,949 records, 1,220 names, 1,240 raw triples; 20 names carry two raw labels.
- Safe name alphabet for every emitted identifier: `[A-Za-z0-9_.+/?()|:-]+`; forbidden anywhere: whitespace,
  `,` `#` `~` `%` `;` `"` `'` `\`. Every mm39 name complies; the validation exists for future assemblies.
- Consumers: IRescue reads BED col 4 as the feature and splits names on `,`; Stellarscope groups GTF rows by
  the `locus` attribute (default) and requires attributes `key "value";`; TEtranscripts groups by
  `gene_id:family_id:class_id`; TEsingle and TElocal read `transcript_id:gene_id:family_id:class_id`;
  featureCounts SAF is `GeneID Chr Start End Strand`, 1-based inclusive, header row, tab-separated.
- Record alias for GTF: `R|mm39|<rmsk_name>|<chrom>|<start_1>|<end_1>|<strand>` (colon-free, so
  `transcript_id:gene_id:family_id:class_id` splits cleanly). Instance alias: `I|mm39|<rmsk_instance_id>`.

## Deliverables (exact paths)
1. `src/30_build_exports.sh <build-dir> <config.env>` calling `src/lib/build_exports.py`. Reads
   `tables/rmsk_records.parquet`, `tables/universe_members.tsv.gz` (universe `interspersed`),
   `tables/taxonomy_canonical.tsv`, `universes.json` (default universe). Writes under
   `<build-dir>/exports/ucsc/interspersed/full/`:
   - `record.bed`: BED6, `chrom, start_1-1, end_1, rmsk_record_id, min(sw_score,1000), strand`.
   - `subfamily.bed`: BED6, name = `rmsk_name`.
   - `family.bed`: BED6, name = `<canonical_class>/<canonical_family>`, or `unresolved/<rmsk_name>` when
     either rank is unresolved.
   - `record.gtf`: one `exon` row per record: `chrom  te-tracks  exon  start_1  end_1  <sw_score>  strand  .`
     attributes in this order: `gene_id "<rmsk_name>"; transcript_id "<record alias>"; locus "<record
     alias>"; family_id "<canonical_family>"; class_id "<canonical_class>"; rmsk_family "<raw>";
     rmsk_class "<raw>"; instance_id "<instance alias>"; rmsk_record_id "<rmsk_record_id>";`. Unresolved
     ranks emit `unresolved` in `family_id`/`class_id`.
   - `subfamily.saf`: header `GeneID\tChr\tStart\tEnd\tStrand`, one row per record, `GeneID = rmsk_name`.
   - `taxonomy_triple.saf`: same rows, `GeneID = <rmsk_name>:<canonical_family>:<canonical_class>` (the
     legacy lab grouping made visible by its name).
   All exports sorted by (chrom C-locale, start_1, end_1, strand, rmsk_name); LF endings; no compression.
   Every emitted identifier (BED name, GTF attribute values, SAF GeneID) validated against the alphabet;
   a violation fails the export naming the offender and the file.
2. `tables/export_feature_members.tsv.gz`: `export_path` (relative to the build dir), `feature_level`
   (`record`, `subfamily`, `family`, `taxonomy_triple`), `emitted_feature_id`, `rmsk_record_id`,
   `block_start_1`, `block_end_1`; one row per (export, record); full exports register one block per record.
   `record.gtf` registers under level `record` with the record alias as the emitted id.
3. `tables/export_summary.tsv`: `export_path, feature_level, rows, distinct_features, sha256`.
4. Checks under `tests/checks/core/` (exit 3 when exports are absent):
   - `40_exports_shape.py`: row counts (each export 3,764,949 rows; SAF plus one header); BED start =
     start_1 - 1 for every row (vectorised against the parquet); GTF and SAF coordinates equal the table;
     `subfamily.bed` has 1,220 distinct names; `family.bed` distinct names equal the distinct
     `<class>/<family>` pairs over the universe's names in `taxonomy_canonical` (report the number);
     `taxonomy_triple.saf` distinct GeneIDs = 1,220 (canonical labels collapse the 20 doubled names);
     every emitted id matches the alphabet; GTF attribute order and quoting as specified on a 1,000-row
     sample parsed with a regex `(\w+) "([^"]*)";`.
   - `41_export_registration.py`: every `emitted_feature_id` in every export resolves to at least one
     record through `export_feature_members`; every universe record appears exactly once per export;
     conservation fixture: a synthetic count table `(emitted_feature_id, count)` with count 7 spread over
     3 records rolls up through the registration to 7 at record, subfamily and family level (pandas).
   - `42_exports_fixtures.py`: runs the exporter on hand-written fixtures under `tests/fixtures/exports/`
     (a small records parquet plus universe members and a taxonomy table built by the fixture): a name with
     a forbidden character fails naming it; an unresolved name yields `unresolved/<name>` in `family.bed`
     and `unresolved` in GTF attributes; the coordinate-duplicate pair yields two BED rows with distinct
     names; a two-record instance shares `instance_id` in the GTF; expected files authored by hand and
     compared byte-for-byte.
5. `docs/OUTPUTS.md`: one section per export with format, coordinate convention, feature identity and the
   GTF attribute mapping table (attribute → source column → consumer that reads it), stated once. README
   truth table rows for the five exports, `taxonomy_triple.saf`, `export_feature_members` to `tested`,
   phase 4. No consumer or modality vocabulary in file names.

## Rules
- Touch only: `src/30_build_exports.sh`, `src/lib/build_exports.py`, `tests/fixtures/exports/**`,
  `tests/checks/core/4*`, `docs/OUTPUTS.md`, `README.md` (truth table rows). Nothing else.
- No git writes. No installs (pandas, pyarrow, numpy available; duckdb absent). No network.
- Report a deviation instead of editing a number, an expectation or a plan file to fit.
- Memory is ample; write the large files with buffered text output, sorted once.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
time bash src/30_build_exports.sh "$TE_TRACKS_REFROOT/te_mm39/build" config/mm39.env; echo "exit=$?"
E="$TE_TRACKS_REFROOT/te_mm39/build/exports/ucsc/interspersed/full"
wc -l "$E"/*
head -2 "$E"/record.bed "$E"/subfamily.bed "$E"/family.bed "$E"/record.gtf "$E"/subfamily.saf "$E"/taxonomy_triple.saf
cut -f4 "$E"/subfamily.bed | sort -u | wc -l          # 1220
cut -f4 "$E"/family.bed | sort -u | wc -l             # report
tail -n +2 "$E"/taxonomy_triple.saf | cut -f1 | sort -u | wc -l   # 1220
cat "$TE_TRACKS_REFROOT/te_mm39/build/tables/export_summary.tsv"
tests/run.sh core; echo "exit=$?"
git status --short
```

## Final message
Every file created or changed; acceptance outputs verbatim; the observed `family.bed` distinct-name count;
any deviation.
