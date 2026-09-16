# te-tracks phase 4: `interspersed` exports in the UCSC namespace

You are the implementer for phase 4 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phases 0 to 3 have landed: read
`AGENTS.md`, `tests/run.sh` (checks are `tests/checks/<mode>/*.sh` and `*.py`, run by name order through `bash`
or `python3`; exit 0 pass, 3 unsupported, other fail; build dir `$TE_TRACKS_REFROOT/te_mm39/build`;
`tests/lib/records.py` supplies `BUILD`, `require` and a typed TSV reader), `docs/OUTPUTS.md` (table contracts),
`src/lib/build_records.py`, `src/lib/build_universes.py`, `src/lib/build_taxonomy.py`, and the tables under
the build dir.

## Read first
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md` (your phase) and the
   phase 4 rulings in `docs/_internal/redesign-2026-09/reviews/m2_rulings.md` (binding where they refine the plan)
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` entries 1, 3, 5
3. `docs/_internal/redesign-2026-09/consults/ADR5_consult.md` sections 3 and 4 (path grammar; tool attribute
   mapping) and `docs/_internal/redesign-2026-09/consults/A_consumer_contracts.md` (what each parser reads;
   the safe name alphabet)
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding)

## Facts
- Universe `interspersed`: 3,764,949 records, 1,220 names, 1,240 raw triples; 20 names carry two raw labels.
- Component alphabet for `rmsk_name`, contig, canonical label and unresolved token: `[A-Za-z0-9_.+?()-]+`; emitted
  identifiers add the separators `|`, `:` and `/`; forbidden anywhere: whitespace, `,` `#` `~` `%` `;` `"` `'` `\`.
  Every mm39 component complies; the validation exists for future assemblies.
- A rank unresolved for a name reads `unresolved_class_<rmsk_name>` or `unresolved_family_<rmsk_name>` wherever a
  canonical label at that rank is emitted (`family.bed`, GTF `family_id`/`class_id`, `taxonomy_triple.saf`), one
  bucket per name per rank, tokens free of separators. mm39 has none.
- Membership comes from `tables/universe_members.tsv.gz`; the exporter never re-evaluates a predicate.
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
   - `family.bed`: BED6, name = `<canonical_class>/<canonical_family>`; an unresolved rank reads its
     `unresolved_<rank>_<rmsk_name>` token in its place.
   - `record.gtf`: one `exon` row per record: `chrom  te-tracks  exon  start_1  end_1  <sw_score>  strand  .`
     attributes in this order: `gene_id "<rmsk_name>"; transcript_id "<record alias>"; locus "<record
     alias>"; family_id "<canonical_family>"; class_id "<canonical_class>"; rmsk_family "<raw>";
     rmsk_class "<raw>"; instance_id "<instance alias>"; rmsk_record_id "<rmsk_record_id>";`. An unresolved
     rank emits its `unresolved_<rank>_<rmsk_name>` token in `family_id`/`class_id`.
   - `subfamily.gtf`: one `exon` row per record, same fixed columns; attributes in this order: `gene_id
     "<rmsk_name>"; transcript_id "<rmsk_name>"; locus "<rmsk_name>"; family_id "<canonical_family>"; class_id
     "<canonical_class>"; rmsk_family "<raw>"; rmsk_class "<raw>";`. This is the subfamily-grain input for
     TEsingle and TElocal, whose feature key includes `transcript_id`.
   - `subfamily.saf`: header `GeneID\tChr\tStart\tEnd\tStrand`, one row per record, `GeneID = rmsk_name`.
   - `taxonomy_triple.saf`: same rows, `GeneID = <rmsk_name>:<canonical_family>:<canonical_class>` (the
     legacy lab grouping made visible by its name).
   All exports sorted by (chrom C-locale, start_1, end_1, strand, rmsk_name); LF endings; no compression.
   Every emitted identifier (BED name, GTF attribute values, SAF GeneID) validated against the alphabet;
   a violation fails the export naming the offender and the file.
2. `tables/export_feature_members.tsv.gz`: `universe_name, variant, feature_level` (`record`, `subfamily`,
   `family`, `taxonomy_triple`), `emitted_feature_id, rmsk_record_id, block_start_1, block_end_1`; one row per
   (emitted id, record); `full` registers one block per record equal to the record bounds. Emitted ids carry
   UCSC contig names inside the record alias and are namespace-invariant, so this one registration serves the
   phase 6 namespaces too. Level `record` registers both spellings, `rmsk_record_id` (BED) and the record alias
   (GTF); level `subfamily` registers `rmsk_name` once for the BED, SAF and GTF that emit it.
3. `tables/exports.tsv`: one row per export file: `export_path` (relative to the build dir), `namespace`,
   `universe_name`, `variant`, `feature_level`, `format`, `rows`, `distinct_features`, `sha256`.
4. Checks under `tests/checks/core/` (exit 3 when exports are absent):
   - `40_exports_shape.py`: row counts (each of the seven exports 3,764,949 rows; SAF plus one header); BED start =
     start_1 - 1 for every row (vectorised against the parquet); GTF and SAF coordinates equal the table;
     `subfamily.bed` has 1,220 distinct names; `family.bed` distinct names equal the distinct
     `<class>/<family>` pairs over the universe's names in `taxonomy_canonical` (report the number);
     `taxonomy_triple.saf` distinct GeneIDs = 1,220 (canonical labels collapse the 20 doubled names);
     every emitted id matches the alphabet; GTF attribute order and quoting as specified on a 1,000-row
     sample of each GTF parsed with a regex `(\w+) "([^"]*)";`; `subfamily.gtf` carries `transcript_id` equal
     to `gene_id` on every row.
   - `41_export_registration.py`: every `emitted_feature_id` in every export resolves to at least one
     record through `export_feature_members`; every universe record appears exactly once per (level, id spelling)
     and `exports.tsv` lists every file under `exports/` with its measured rows and sha256;
     conservation fixture: a synthetic count table `(emitted_feature_id, count)` with count 7 spread over
     3 records rolls up through the registration to 7 at record, subfamily and family level (pandas).
   - `42_exports_fixtures.py`: runs the exporter on hand-written fixtures under `tests/fixtures/exports/`
     (a small records parquet plus universe members and a taxonomy table built by the fixture): a name with
     a forbidden character fails naming it; an unresolved name yields `unresolved_family_<name>` in `family.bed`,
     in the GTF `family_id` and in the triple GeneID; the coordinate-duplicate pair yields two BED rows with distinct
     names; a two-record instance shares `instance_id` in the GTF; expected files authored by hand and
     compared byte-for-byte.
5. `src/lib/build_records.py`: `rmsk_name` rejects `/` beside `|`, `:` and whitespace (same message); add
   `tests/fixtures/records/slash_name.{out,tsv}` (name `Bad/Name`) to check 23's failure table; one OUTPUTS.md
   sentence in the record contract follows. Unresolved tokens are then separator-free by construction.
6. `docs/OUTPUTS.md`: one section per export with format, coordinate convention, feature identity and the
   GTF attribute mapping table (attribute → source column → consumer that reads it), stated once for both
   GTFs; the registration and inventory tables; the phase 4 sentence "All six exports" becomes seven; the
   `family.bed` row emits the unresolved token positionally inside `<class>/<family>` (phase 3 re-review A2). README
   truth table rows for the seven exports, `export_feature_members` and `exports.tsv` to `tested`, phase 4
   (add rows that the table lacks, and the phase 3 row `tests/fixtures/taxonomy/weighting_context.tsv`, `delivered,
   tested`, 3, which the phase 3 round omitted). No consumer or modality vocabulary in file names.

## Rules
- Touch only: `src/30_build_exports.sh`, `src/lib/build_exports.py`, `src/lib/build_records.py` (that one pattern),
  `tests/fixtures/records/slash_name.{out,tsv}`, `tests/checks/core/23_records_fixtures.py` (that one row),
  `tests/fixtures/exports/**`, `tests/checks/core/4*`, `docs/OUTPUTS.md`, `README.md` (truth table rows). Nothing else.
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
head -2 "$E"/record.bed "$E"/subfamily.bed "$E"/family.bed "$E"/record.gtf "$E"/subfamily.gtf "$E"/subfamily.saf "$E"/taxonomy_triple.saf
cut -f4 "$E"/subfamily.bed | sort -u | wc -l          # 1220
cut -f4 "$E"/family.bed | sort -u | wc -l             # report
tail -n +2 "$E"/taxonomy_triple.saf | cut -f1 | sort -u | wc -l   # 1220
cat "$TE_TRACKS_REFROOT/te_mm39/build/tables/exports.tsv"
zcat "$TE_TRACKS_REFROOT/te_mm39/build/tables/export_feature_members.tsv.gz" | tail -n +2 | cut -f3 | sort | uniq -c
tests/run.sh core; echo "exit=$?"
git status --short
```

## Final message
Every file created or changed; acceptance outputs verbatim; the observed `family.bed` distinct-name count;
any deviation.
