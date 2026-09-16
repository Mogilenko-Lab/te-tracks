# te-tracks phase 2: canonical tables and universes

You are the implementer for phase 2 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phases 0 and 1 have landed:
`AGENTS.md`, `README.md`, `docs/DECISIONS.md`, `tests/run.sh` (checks are executables under
`tests/checks/<mode>/`, exit 0 pass, 3 unsupported, other fail), `config/mm39.env`, `src/00_fetch_sources.sh`,
`src/05_qualify_source.sh`, `src/lib/rmsk_out.py` (parser profile `rm_out_v1`, generator `iter_records`),
`build.sh --genome <name> --build-dir <dir>` running `src/NN_*.sh <dir> <config>` in order.

## Read first
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/12_phase2_canonical.md` (your phase)
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` entries 1, 2, 5, 6
3. `docs/_internal/redesign-2026-09/consults/ADR5_consult.md` section "2. Exact canonical record schema"
   (the 24 columns, order, types, serialization contract)
4. `docs/_internal/redesign-2026-09/audit/AUDIT.md` F1, F2, F3, F6 and
   `docs/_internal/redesign-2026-09/audit/{policy_universes,class_census}.tsv`
5. `src/lib/rmsk_out.py`, `tests/run.sh`, `lib/common.sh`, `config/mm39.env`
6. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding)

## Universe predicates (raw `rmsk_class`, raw `rmsk_family`; measured on mm39, must reproduce)
| universe | predicate | records | names | (name,family,class) triples | length_sum_bp |
|---|---|---|---|---|---|
| `all_rmsk` | every record | 5,320,771 | 18,484 | 18,504 | 1,201,573,004 |
| `interspersed` (default) | class in {SINE, LTR, LINE, DNA, RC, Retroposon, Unknown, Unspecified, DNA?}; Unknown, Unspecified, DNA? members flagged `provisional` | 3,764,949 | 1,220 | 1,240 | 1,116,605,808 |
| `interspersed_plus_satellites` | `interspersed` or class = Satellite | 3,802,177 | 1,228 | 1,248 | 1,121,742,599 |
| `retrotransposon_derived` | class in {SINE, LTR, LINE, Retroposon} | 3,593,857 | 868 | 868 | 1,084,886,912 |
| `satellites` | class = Satellite | 37,228 | 8 | 8 | 5,136,791 |
| `compat_tetranscripts_mm39` | class in {SINE, LTR, LINE, DNA, Satellite, Retroposon, Unknown, RC, Unspecified, DNA?} and family does not start with `tRNA` | 3,799,629 | 1,225 | 1,245 | 1,121,476,301 |
`length_sum_bp` sums `end_1 - start_1 + 1` over member records, overlaps retained. Class census over all records (class: count): SINE 1495172, Simple_repeat 1339071, LTR 1105064,
LINE 976368, DNA 164783, Low_complexity 157808, Satellite 37228, Retroposon 17253, scRNA 12248,
Unknown 5786, snRNA 3649, tRNA 3508, rRNA 1514, srpRNA 796, RC 416, Unspecified 98, DNA? 9.
Other measured facts: `rmsk_record_id` = `<rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>` is unique over
all 5,320,771 records; a coordinate-only key (chrom,start_1,end_1,strand) collides for exactly 3 pairs
(chr11:67327100 ORR1B1-int/B1F, chr13:58658237 B1_Mus1/ORR1B1-int, chr16:37859045 ID_B1/B1_Mur3), all
kept as distinct records; 4,696,900 instances, each on one contig; 20 names carry more than one
(family,class) label, covering 6,517 records.

## Deliverables (exact paths)
1. `src/10_build_records.sh <build-dir> <config.env>` calling `src/lib/build_records.py`. Reads
   `<build-dir>/source/mm39.fa.out.gz` through `rmsk_out.iter_records`, `source/rmsk.txt.gz` for the three
   raw signed UCSC repeat fields (joined on chrom,start_1,end_1,strand,name; the join must be 1:1 or the
   build fails), and `source/mm39.chrom.sizes` for bounds. Writes:
   - `<build-dir>/tables/rmsk_records.tsv.gz` and `tables/rmsk_records.parquet`: exactly the 24 columns in
     ADR5 §2 order with those logical types; rows sorted by (`chrom` in C-locale order, `start_1`, `end_1`,
     `strand`, `rmsk_name`). TSV: UTF-8, LF, one header, `true`/`false` booleans, decimal integers,
     period decimal separator, no null in any of the 24 columns. Gzip with fixed header (Python
     `gzip.GzipFile(fileobj=..., mode='wb', mtime=0)` and no embedded filename) so identical input yields
     identical bytes. Parquet via pyarrow with explicit schema (int64, float64, bool, string); the two
     serializations must load to equal typed rows (assert it in a check on a sample plus row counts).
   - `tables/rmsk_instance_members.tsv.gz`: `rmsk_instance_id, rmsk_record_id`, sorted; `rmsk_instance_id`
     is the `.out` ID as text.
   - `tables/rmsk_taxonomy.tsv`: distinct `rmsk_name, rmsk_family, rmsk_class, record_count,
     record_length_sum_bp`, sorted by name, family, class.
   - Assertions that fail the build with a message naming the offender: record id unique; exact duplicate
     key; `1 <= start_1 <= end_1 <= contig length`; a chrom absent from `chrom.sizes`; every record in exactly
     one instance; an instance on more than one contig.
2. `src/15_build_universes.sh <build-dir> <config.env>` calling `src/lib/build_universes.py`:
   - `<build-dir>/universes.json`: `schema_version`, `default_universe: "interspersed"`, and one entry per
     universe with `name`, `description` (one sentence), `predicate` as a machine-readable object
     (`{"class_in": [...]}`, optional `"family_prefix_excluded": "tRNA"`, optional `"or": [...]`), and
     `provisional_classes` (for `interspersed` and `interspersed_plus_satellites`: Unknown, Unspecified,
     DNA?). The build evaluates predicates from this object; no second copy of the rule lives in code.
   - `tables/universe_members.tsv.gz`: `universe_name, rmsk_record_id, provisional` for every universe except
     `all_rmsk`, sorted.
   - `tables/universe_summary.tsv`: `universe_name, records, names, triples, length_sum_bp` for all six.
   - Class census gate: the set of observed classes must equal the class set in
     `tests/expectations/mm39/class_census.tsv` (move and rename the existing
     `tests/expectations/mm39_class_counts.tsv` there, two columns `rmsk_class, records`, tab-separated,
     header row); a class observed but absent from the file fails the build with its name, so a new
     assembly's classes are reviewed before any universe publishes. Counts are compared in the check, the
     class set in the build.
3. `tests/expectations/mm39/universe_summary.tsv`: authored by hand from the table above (records, names,
   triples, length_sum_bp per universe).
4. Checks (executables under `tests/checks/core/`, exit 3 with `unsupported: run build.sh first` when the
   build dir lacks the tables; the build dir is `$TE_TRACKS_REFROOT/te_mm39/build`):
   - `20_records_schema.py`: column names and order, dtypes when loaded with an explicit schema, row count
     5,320,771, id uniqueness, bounds, TSV/parquet equality on rows and on a 10,000-row sample.
   - `21_instances.py`: 4,696,900 instances, every record in exactly one, single contig per instance,
     instance sizes 1: 4,251,251; 2: 338,697; 3+: 106,952.
   - `22_universes.py`: counts equal `tests/expectations/mm39/universe_summary.tsv`; class census counts
     equal `class_census.tsv`; the 3 collision pairs present as distinct records; provisional flags only on
     Unknown/Unspecified/DNA? records; 20 names with more than one label in `rmsk_taxonomy`, 6,517 records.
   - `23_records_fixtures.py`: runs `build_records.py` and `build_universes.py` as functions or subprocesses
     on hand-written fixtures under `tests/fixtures/records/`: equal coordinates with different names stay
     two records; an exact duplicate key fails; a two-record instance; a record beyond its contig end fails
     bounds; a chrom absent from chrom.sizes fails; a class absent from the census file fails the gate; a
     `tRNA`-prefixed family is excluded from `compat_tetranscripts_mm39` and kept in `interspersed`.
     Expected values authored by hand. Each failure case asserts the failure message names the offender.
5. `docs/OUTPUTS.md`: replace the legacy table description with the 24-column schema (one row per column:
   name, type, one-line contract), the instance and taxonomy tables, `universes.json`, `universe_members`,
   `universe_summary`, the serialization contract, and the coordinate convention statement. Update the
   README truth table rows for these artifacts to `tested` with phase 2.

## Rules
- Touch only: `src/**`, `tests/**`, `docs/OUTPUTS.md`, `README.md` (truth table rows and one sentence in
  Outputs). Never `docs/_internal/**`, `config/**`, `lib/**`, `build.sh`, `docs/DECISIONS.md`.
- No git writes. No installs (pyarrow 25, pandas 2.2, numpy, pysam, pytest are available; duckdb is
  absent, so use pandas/pyarrow). No network.
- Report a deviation instead of editing a number, an expectation file, or a plan file to fit. If a measured
  number differs from the table above, stop, report both values, and leave the expectation at the value you
  observed with a clear note in the final message.
- Memory is ample (500 GB); a full run should finish in minutes. Stream where easy; loading 5.3M rows into
  pandas is fine.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
time ./build.sh --genome mm39 --build-dir "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
ls -la "$TE_TRACKS_REFROOT/te_mm39/build/tables/" "$TE_TRACKS_REFROOT/te_mm39/build/universes.json"
cat "$TE_TRACKS_REFROOT/te_mm39/build/tables/universe_summary.tsv"
zcat "$TE_TRACKS_REFROOT/te_mm39/build/tables/rmsk_records.tsv.gz" | head -3
sha256sum "$TE_TRACKS_REFROOT/te_mm39/build/tables/"*.gz "$TE_TRACKS_REFROOT/te_mm39/build/tables/"*.parquet
# rebuild into a second dir and compare digests: identical input must give identical bytes
./build.sh --genome mm39 --build-dir "$TE_TRACKS_REFROOT/te_mm39/build2" && cd "$TE_TRACKS_REFROOT/te_mm39" && sha256sum build/tables/* build2/tables/* build/universes.json build2/universes.json | sort -k2 | awk '{print $1, $2}' ; cd -
tests/run.sh core; echo "exit=$?"
git status --short
```

## Final message
Every file created, changed, moved or deleted; acceptance outputs verbatim including the digest comparison;
any deviation.
