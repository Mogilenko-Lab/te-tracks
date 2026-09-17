# te-tracks phase 9a: core additions before acceptance (unit `te-tracks-p9a-impl`)

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks` (branch `redesign-2026-09`, tree clean at HEAD
`393ca76`, the phase 8 commit). You implement phase 9a as specified in the "Phase 9a" section of
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/19_phase9_acceptance_park.md`; that plan is authoritative
where this prompt and the plan disagree, and a disagreement is a deviation to report. Every item changes the core
`BUILD_ID` and keeps `CATALOG_ID`.

## Read first
1. Plan 19's "Phase 9a" section in full, including "Constraints carried from the phase 8 review".
2. `docs/DECISIONS.md` sections 1, 7, 10, 12, 13, 14, 15 and 16; `docs/_internal/redesign-2026-09/consults/
   adr_rulings_2026-09-17.md` rounds three to five (Dfam value, Wicker's scheme, the fifth-round measurements).
3. `consults/loci_gtf_consult.md` Q3 and Q5 (the record profile, its fixture and the external STAR and cellranger
   contracts); `consults/structural_views_consult.md` (the measured instance numbers); `consults/
   unified_te_schema_consult.md` "Model-length correction" and "Schema sketch" rows for `dfam_model`,
   `lineage_node`, `subfamily_model`, `model_clade`, `subfamily_rank`.
4. The Dfam material: `docs/_internal/redesign-2026-09/taxonomy/dfam_interspersed_mm39_snapshot.json.gz` (keys
   `version`, `classes`, `summaries`, `records`), its `.provenance.json`, `dfam_snapshot_fetch_20260917.py` (the
   fetch script), `dfam_census_1220_20260917.tsv`.
5. The code you extend, in full: `build.sh`, `src/00_fetch_sources.sh`, `src/20_build_taxonomy.sh`,
   `src/lib/build_taxonomy.py`, `src/lib/build_exports.py`, `src/lib/contigs.py`, `src/lib/manifest.py`,
   `src/lib/gene_child.py` (the parent pin), `src/release.py`, `tests/run.sh`, `tests/lib/consumers.py`,
   `tests/lib/records.py`, `tests/fixtures/publication/build_fixture.py`, checks `31`, `40`, `41`, `42`, `61`, `62`,
   `70`, `71`, `72`, `82`, `83` and every check under `tests/checks/consumers/`.
6. `docs/OUTPUTS.md` (taxonomy, exports, registration, consumer contracts, phases 7 to 9), `docs/RELEASES.md`,
   `docs/RUNBOOK.md`, `README.md`, `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".

## Environment and rules
- `export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
  TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1`. The core
  build `$TE_TRACKS_REFROOT/te_mm39/build` (`BUILD_ID` `9ddf3622…`, `CATALOG_ID` `90cc18be…`) and the child
  `$TE_TRACKS_REFROOT/te_mm39_gene/build` (`1804f94e…`) are yours to rebuild in place at the end (item 12); the scratch
  root `$TE_TRACKS_REFROOT/pubroot` receives the new core and child archives beside the existing ones. Sources come
  from the cache; no network otherwise.
- Consumer binaries: `source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh` puts the shims (`STAR` 2.7.11b,
  `cellranger` 10.1.0, `irescue`, `featureCounts`, `stellarscope`, `TEsingle`, `TEtranscripts`, `TElocal`) on `PATH`.
  Run the consumer suite once without activation and once with it.
- Scratch under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/p9a/`, removed with Python `shutil` when you finish
  (`/tmp` is noexec). No git writes anywhere (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git
  repositories too; `14839-DM-cGAS` and `sene` there are the owner's plain directories, left alone), no installs, no
  edits outside the touch list. Files under `docs/_internal/` are the orchestrator's; read them, change nothing there.
- Never weaken or delete a test. Report a blocking test by name. Every numeric target is measured; when an
  observation differs, report the deviation instead of editing an artifact or an expectation to match.
- Public prose (README, docs, docstrings, comments, check messages) is affirmative and brief; comments state intent
  in one line; no history, provenance or review chatter in package files.
- Streaming and vectorised work over the 5,320,771 records and the 3,764,949 interspersed records; record peak
  resident memory and wall time of the core rebuild (stage 30 is instrumented) and of the child rebuild.

## Touch list
`.gitignore`, `config/mm39.env`, `data/dfam/` (new: the snapshot, its provenance, the fetch script), `build.sh`
(only if a stage needs a new argument), `src/00_fetch_sources.sh`, `src/25_build_dfam.sh` (new), `src/lib/build_dfam.py`
(new), `src/lib/build_exports.py`, `src/lib/manifest.py`, `src/release.py` (only if publication needs it),
`tests/run.sh` (usage text), `tests/lib/consumers.py`, `tests/lib/records.py`, `tests/fixtures/publication/
build_fixture.py`, `tests/fixtures/exports/**`, `tests/fixtures/taxonomy/dfam_rank_cases.tsv` (new),
`tests/fixtures/consumers/**`, `tests/expectations/mm39/dfam_census.tsv` (new), `tests/expectations/mm39/
taxonomy_census.tsv` (only rows this phase measures), checks `tests/checks/core/33_taxonomy_dfam_view.py` and
`34_dfam_rule_fixtures.py` (new), `43_matrix_binding.py` (new), `40`, `41`, `42`, `61`, `62`, `70`, `71`, `72`, `82`,
`83` (only where rosters and counts change), `tests/checks/consumers/24_starsolo_exec.sh` and
`25_cellranger_mkref.sh` (new), `20_irescue_exec.sh` (message), `docs/OUTPUTS.md`, `docs/RELEASES.md`,
`docs/RUNBOOK.md`, `docs/DECISIONS.md` (section 15 alone), `README.md`. Every other file stays as it is; the child
code changes only where the parent pin and roster require.

## Deliverables

1. **`record_starsolo.gtf`** (C8; DECISIONS 13; consult Q5). New entry in `EXPORT_CONTRACTS` and in the
   `interspersed` job: `exports/<ns>/interspersed/full/record_starsolo.gtf`, one exon row per record with the nine
   GTF columns of `record.gtf`, attributes in this order, each `key "value";` separated by one space: `gene_id`,
   `transcript_id`, `gene_name`, `gene_type`, `locus`, `rmsk_name`, `family_id`, `class_id`, `rmsk_family`,
   `rmsk_class`, `instance_id`, `rmsk_record_id`; `gene_id` = `transcript_id` = `locus` = the record alias;
   `gene_name` = `rmsk_name`; `gene_type` = `transposable_element`; the rest as in `record.gtf`. Contract:
   `feature_level` `record`, `feature_identity` `gene_id`, `attribute_sources` complete, `consumer_keys`
   `{"STARsolo": "gene_id", "cellranger": "gene_id"}`, `selectable_levels` `{"gene_id": "record"}`,
   `coordinate_convention` `1-based inclusive`. Registration reuses the existing `(record, record_alias)` rows: no
   new registration rows (interspersed registration stays 30,119,592 rows). Namespaces through `contigs.py` as for
   the other GTFs. Expected per namespace: 3,764,949 rows, 3,764,949 distinct `gene_id`s, 59 contigs, about
   1.616 GB (the consult's estimate; measure and report). Export contracts 24 → 27; `tables/exports.tsv` 27 rows.
2. **STARsolo and cellranger gates** (consult Q5 fixture, DECISIONS 12). `tests/lib/consumers.py` gains a
   `record_starsolo.gtf` parser check in the existing parser style (`tests/checks/consumers/17_starsolo_profile.required.py`:
   attribute order, `gene_id` = `transcript_id` = `locus`, two same-name records as two genes, `gene_type`, the
   registration join through `(interspersed, full, record, record_alias)`, namespace variants and one-base
   endpoints) and two execution checks that report `unsupported` naming the binary when it is absent from `PATH`:
   `24_starsolo_exec.sh` builds a STAR index of the fixture `reference.fa` with a combined GTF (a fixture host gene
   with two exons plus the fixture `record_starsolo.gtf`; `--genomeSAindexNbases 4`, `--sjdbOverhang` one below the
   read length), writes FASTQs from the fixture molecules (CB 16 + UMI 12 in read 1, cDNA in read 2), runs
   `--soloType CB_UMI_Simple --soloCBwhitelist None --soloFeatures Gene GeneFull --soloMultiMappers EM`, and asserts:
   `features.tsv` lists every TE record as its own gene with `gene_name` = `rmsk_name`; two same-name records
   receive one unique molecule each; the gap-only molecule gives zero TE support; a molecule aligning to a host
   exon and a TE record both is absent from the unique matrix and split by EM in `UniqueAndMult-EM.mtx` with the
   total conserved; identities join the registration; the allocation is recorded, never asserted to a value.
   `25_cellranger_mkref.sh` runs `cellranger mkgtf` keeping `gene_type:transposable_element` and the host biotype,
   then `cellranger mkref` on the tiny genome, and asserts the reference's `genes.gtf` keeps every TE gene with its
   alias `gene_id` and that the `star/` index exists; `cellranger count` is documented as the consumer module's
   recipe. A collision preflight lives in the parser check: a fixture host GTF whose `gene_id` collides with a TE
   alias, or uses the reserved `R|mm39|` prefix, fails with a named message.
3. **Dfam lineage, rank and clade view** (C10; DECISIONS 15; plan 19 bullet). (a) `data/dfam/` holds
   `dfam_interspersed_mm39_snapshot.json.gz` (byte-identical to the taxonomy record copy; sha256
   `ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f`, 278,952 bytes), its `.provenance.json` and
   `fetch_dfam_snapshot.py` (the fetch script generalized: names from a `taxonomy_canonical.tsv` restricted to a
   universe, output directory as an argument, identical payload rules; it documents production and never runs in a
   build). `.gitignore` gains `!data/dfam/**`. (b) `config/mm39.env` gains `DFAM_SNAPSHOT_PATH=data/dfam/
   dfam_interspersed_mm39_snapshot.json.gz` and `DFAM_SNAPSHOT_SHA256=<that digest>`; `src/00_fetch_sources.sh`
   copies the tracked file into `source/` after verifying the sha256 and declares role `dfam_snapshot` in
   `source/SOURCES.json` as `{"path": <repo-relative path>, "sha256", "bytes"}`. (c) `src/lib/manifest.py`: the
   fetched four roles stay `SOURCE_CONFIG`; a `TRACKED_SOURCE_CONFIG = {"dfam_snapshot": "DFAM_SNAPSHOT"}` maps the
   role to its config pin; `build_sources` gains `dfam_snapshot` with `path`, `sha256`, `bytes`, `dfam_version`
   (the snapshot's `version.dfam_version`, `4.0`) and `fetch_finished` from the provenance; the verifier admits an
   archive declaring the four fetched roles alone (the `9ddf3622…` archive keeps verifying) and an archive declaring
   the tracked role, comparing its bytes and sha256 with the inventory and the payload roster with what the archive
   declares; `CATALOG_ID` is untouched. (d) `src/25_build_dfam.sh` calling `src/lib/build_dfam.py`, after taxonomy
   and before exports, writing four tables:
   - `tables/taxonomy_dfam.tsv`, one row per `interspersed` name sorted by name, columns in this order: `rmsk_name`,
     `rmsk_class`, `rmsk_family` (the raw tokens of the name's plurality label as `taxonomy_canonical` resolved
     them), `canonical_class`, `canonical_family`, `record_count` (from the catalog by name), `match_status`
     (`exact`, `part_model_set`, `missing`), `dfam_accessions`, `dfam_model_names`, `dfam_model_versions`,
     `dfam_model_lengths_bp` (each `;`-joined in the role order `whole` or `5end`, `orf2`, `3end`),
     `available_part_count`, `part_roles_present` (`;`-joined subset of `5end;orf2;3end`, empty for exact),
     `model_length_sum_bp`, `classification_path`, `classification_leaf`, `clades` (every clade path of every matched
     model, `;`-joined, deduplicated, in first-seen order), `clade_leaves`, `clade_compatibility` (`compatible`,
     `primate_branch`, `multi_clade`, `missing`; `multi_clade` when any matched model carries several clades,
     `primate_branch` when any clade path contains `Primates`, `primate_branch` taking precedence), `dfam_release`,
     `wicker_code`, `wicker_code_uncertain` (a trailing `?` on the code), `wicker_class`, `wicker_class_status`,
     `wicker_subclass`, `wicker_subclass_status`, `wicker_order`, `wicker_order_status`, `wicker_superfamily`,
     `wicker_superfamily_status`, `wicker_family`, `wicker_family_status`, `subfamily`, `subfamily_status`,
     `dfam_repeat_type`, `dfam_repeat_subtype` (the models' `repeat_type_name` and `repeat_subtype_name`, one value
     when they agree, `;`-joined otherwise).
   - `tables/taxonomy_dfam_models.tsv`, one row per name × matched model: `rmsk_name`, `role` (`whole`, `5end`,
     `orf2`, `3end`), `accession`, `model_name`, `model_version`, `model_length_bp`, `classification_path`, `clades`
     (`;`-joined), `repeat_type`, `repeat_subtype`.
   - `tables/dfam_lineage_nodes.tsv`, one row per node of the classification tree: `full_path`, `parent_path`,
     `name`, `depth`, `wicker_code`, `repeatmasker_type`, `repeatmasker_subtype`, `family_count` (the node's
     `count` when present).
   - `tables/dfam_model_clades.tsv`, one row per model × clade path: `accession`, `clade_path`, `clade_leaf`.
   Rules. Match: the summary hit named exactly `rmsk_name` is `exact`; else the hits named `<name>_5end`,
   `<name>_orf2`, `<name>_3end` form a `part_model_set` (L1 and L2/CR1 alike); else `missing`. Every matched
   accession has a full record in `records`. Wicker: the code comes from the nearest node on the classification path
   carrying `wicker_equiv`, status `mapped` when that node is the leaf and `inherited` otherwise, `missing` when no
   node on the path carries one (the `Unknown` names) or the name is `missing`; a part set uses its parts' common
   path (parts agree; a disagreement is a build error) and takes status `part_model_set` at every derived rank. The
   code has the form `<class>[/<order letter>[ (<order>)][/<superfamily letter>[ (<superfamily>)]]][?|??]`: class
   `R` → `Class I (retrotransposons)`, `D` → `Class II (DNA transposons)`; the order name from the parentheses or, when
   absent, from the letter (`I` LINE, `L` LTR, `S` SINE, `P` PLE, `Y` DIRS for class I; `T` TIR, `Y` Crypton, `H`
   Helitron, `M` Maverick for class II); the superfamily name from its parentheses or, when absent, from Wicker's
   letter table for that order (`P` P element under TIR, `I` I under LINE, `H` Helitron under Helitron); `?` marks
   `wicker_code_uncertain` true; a code with fewer parts leaves the deeper ranks `missing`. Subclass: class II
   orders TIR and Crypton → `subclass 1`, Helitron and Maverick → `subclass 2`; class I → `inapplicable`.
   `wicker_family` is the Dfam leaf node name (`mapped` for exact, `part_model_set` for parts, `missing`
   otherwise); `subfamily` is `rmsk_name` with status `mapped`. Record weights come from the catalog; the census
   TSV is a record of the fetch. (e) Checks: `33_taxonomy_dfam_view.py` compares the census with
   `tests/expectations/mm39/dfam_census.tsv` authored from plan 19 (1,047 / 147 / 26 names; records 2,797,852 /
   928,528 / 38,569; part sets 30 / 9 / 108 by size; six L2/CR1 sets; 1,263 model rows; 300 nodes, 193 coded; 9
   multi-clade models, 33 primate-branch models, 31 `primate_branch` names; 884 `mapped`, 110 `inherited`, 53
   `missing` Wicker codes among exact names), joins every name to `taxonomy_canonical`, requires every
   `interspersed` name once, model rows consistent with the one-row table, every accession in the models table
   present in the clades table, every classification path present in the nodes table, and recomputes the sum of
   model lengths and `available_part_count`. `34_dfam_rule_fixtures.py` runs the rank derivation on
   `tests/fixtures/taxonomy/dfam_rank_cases.tsv`: a leaf code, an inherited code, an `Unknown` name, a two-part
   code, a code without a superfamily name (`D/T (TIR)/P`), an uncertain code (`R/S (SINE)/L (7SL)?`), a class II
   subclass 2 order, a class I `inapplicable` subclass, a three-part L1 set, a one-part L2 set, a primate-branch
   model, a multi-clade model, a missing name, and a part set whose parts disagree (a build error with a named
   message). Check 31 stays as it is. (f) `docs/OUTPUTS.md` gains "Dfam lineage, ranks and clades (phase 9a)" under
   the taxonomy section: the four tables with column contracts, the match rule, the Wicker ranks defined in Wicker's
   terms (class, subclass, order, superfamily, family, subfamily) with the dissertation's five names as an alias
   table (class, subclass, superfamily, family, subfamily map onto Wicker's class, order, superfamily, family,
   subfamily), the label surprises (B1 under `Alu`; `ERVL-MaLR`; hyphenated DNA superfamilies such as
   `hAT-Charlie`; class-less records), the part rule with its partial sets, and the clade caveat (a model's clade
   is its curated assignment; age tiers are consumer policy read from the clade path with `median_divergence_pct`
   beside it). `docs/DECISIONS.md` section 15: "a later core view" becomes "the phase 9 core view", the companion
   tables are named, and the status list gains `wicker_code_uncertain`; four sentences at most beyond the present
   ones, affirmative.
4. **Matrix binding** (C9; DECISIONS 14). `docs/OUTPUTS.md` line 436 reads: "A run's matrix binds to one
   `(universe_name, variant, feature_level, key_grammar)`." with the following sentences adjusted. New core check
   `43_matrix_binding.py`: from the real registration, take 1,000 records present in both `interspersed` and
   `all_rmsk` at `(record, rmsk_record_id)`, build a tiny count table, and show the join on `(feature_level,
   key_grammar)` alone returns two rows per feature while the four-field join returns one and conserves the total.
5. **Records, instances and insertions** (DECISIONS 10). A `docs/OUTPUTS.md` section "Records, instances and
   insertions" after the canonical records section: what a record, an instance and an insertion are; per-locus
   counts are per record; the annotation's limits (alignment to the pinned 2018 library; fragmentation and
   nesting; model-relative consensus coordinates; records overlapping one another; genic context depending on the
   annotation pin); the measured numbers, each measured by you from the build and reported beside the plan's
   figure: 445,649 multi-record instances; 30,569 mixed-name instances; 23,244 mixed-strand instances; 8.07% of
   records overlapping another record; 722,280 LTR-only instances; 588 L1 records at model base 1;
   `rmsk_overlap_flag` constant false in the mm39 source.
6. **IRescue execution check** (DECISIONS 12). In `tests/lib/consumers.py` `irescue_check`, the allocation cases
   assert identity joins (every feature is a roster key), roster and molecule conservation (the sum equals 9, each
   count between its unique floor and floor plus 3) and unique molecules on their feature (the simple cases), and
   record the observed allocation in `irescue_allocation.json` and in the pass message without asserting the
   fixed point. The check passes with the shims active (observed 5.5 / 3.5 and 4.5 / 4.5).
7. **Consumer environment** (DECISIONS 12 deferral). `docs/RUNBOOK.md` gains "Consumer environment": the
   bootstrap `/workspaces/Meta-Aging/01_modules/te-consumers/env/bootstrap.sh`, its lock files (`requirements.txt`,
   `MANIFEST.tsv`, `pip-freeze.txt`, `python-version.txt`), activation with `source
   /workspaces/Meta-Aging/.venv/te-consumers/activate.sh`, and the two suite outcomes (with and without activation).
   `tests/run.sh` usage text and README's test section name the activation line before `tests/run.sh consumers`.
8. **Publication case: a failed build's staging** (`72_publication_cases.py`, `docs/RELEASES.md`). A staging
   directory left by an interrupted build (a fixture build with `MANIFEST.json` removed and one table truncated)
   is refused by `install` with a named discrepancy, leaves `current` untouched, and is removable by its owner;
   `docs/RELEASES.md` recovery paragraph states the removal step.
9. **Check rosters and fixtures** follow the new export and tables: `40` (eight interspersed files), `41` and `61`
   (27 exports, 27 inventory digests), `42` (a hand-authored `record_starsolo.gtf` expectation for the fixture
   records), `62` (the new GTF in preflight), `70` (payload count 43 → 51: three GTFs, four Dfam tables, one
   tracked source), `71`, `72`, `82`, `83` (the tiny fixture builds carry the new files and the `dfam_snapshot` role;
   `make_build` writes a minimal snapshot with two names). Check 22's and 30's counts stay.
10. **Retention and README.** `docs/RELEASES.md` retention paragraph gains the measured sizes of the three new GTFs,
    the four tables and the tracked source, the new payload total and the `du -sb` figure; README truth table rows
    for `record_starsolo.gtf` (three namespaces), the four Dfam tables and the two execution gates, `delivered,
    tested` or `unsupported in-container` as observed; the export table in `docs/OUTPUTS.md` phase 4 section gains
    the profile's row, the attribute table its attributes, the consumer table STARsolo and cellranger rows.
11. **Child pin.** After the core rebuild the child's `parent_build_id` moves: rebuild the child against the new core
    (`--build-dir` mode, then `--root` publication) and confirm its `CATALOG_ID` bytes still equal the parent's and
    its exon-subtraction summary is unchanged.
12. **Rebuild and republish.** In this order: `./build.sh --genome mm39 --build-dir "$TE_TRACKS_REFROOT/te_mm39/build"`
    after moving the present build aside under your scratch (restore it if the rebuild fails); `tests/run.sh core`;
    `./build.sh --genome mm39 --root "$TE_TRACKS_REFROOT/pubroot"` (the new archive installs beside `9ddf3622…`);
    the child scratch rebuild with `--parent-dir`; the child `--root` publication with the new parent id; `release.py
    verify-current` for both families. Remove the set-aside core build only after everything passes.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1
for f in build.sh lib/common.sh src/*.sh src/gene/*.sh tests/run.sh tests/checks/consumers/*.sh; do bash -n "$f" && echo "syntax ok $f"; done
sha256sum data/dfam/dfam_interspersed_mm39_snapshot.json.gz
B="$TE_TRACKS_REFROOT/te_mm39/build"
time ./build.sh --genome mm39 --build-dir "$B"; echo "exit=$?"
cat "$B/BUILD_ID" "$B/CATALOG_ID"
python3 -c "import json;i=json.load(open('$B/MANIFEST.json'))['identity'];print(len(i['inventory']),len(i['export_contracts']),sorted(i['build_sources']))"
wc -l "$B"/exports/*/interspersed/full/record_starsolo.gtf; cut -f1 "$B/exports/ucsc/interspersed/full/record_starsolo.gtf" | sort -u | wc -l
head -2 "$B/exports/ucsc/interspersed/full/record_starsolo.gtf"
head -3 "$B/tables/taxonomy_dfam.tsv" | cut -c1-400; wc -l "$B"/tables/taxonomy_dfam*.tsv "$B"/tables/dfam_*.tsv
cut -f7 "$B/tables/taxonomy_dfam.tsv" | tail -n +2 | sort | uniq -c
python3 src/99_verify.py "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive/9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d"; echo "exit=$? (earlier archive stays verifiable)"
tests/run.sh core; echo "exit=$?"
tests/run.sh consumers; echo "exit=$?"
source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh; tests/run.sh consumers; echo "exit=$?"
time ./build.sh --genome mm39 --root "$TE_TRACKS_REFROOT/pubroot"; echo "exit=$?"
NEW=$(python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39); echo "$NEW"
C="$TE_TRACKS_REFROOT/te_mm39_gene/build"
time ./build.sh --genome mm39 --family gene --build-dir "$C" --parent-dir "$B"; echo "exit=$?"
cat "$C/tables/exon_subtraction_summary.tsv"; cmp "$C/CATALOG_ID" "$B/CATALOG_ID" && echo "child CATALOG_ID equal"
time ./build.sh --genome mm39 --family gene --root "$TE_TRACKS_REFROOT/pubroot" --parent-build-id "$NEW"; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39_gene; echo "exit=$?"
ls "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive" "$TE_TRACKS_REFROOT/pubroot/te_mm39_gene/archive"
du -sb "$B"; python3 - <<'PY'
import json,os
b=os.environ["TE_TRACKS_REFROOT"]+"/te_mm39/build"; inv=json.load(open(b+"/MANIFEST.json"))["identity"]["inventory"]
print("payload files",len(inv),"bytes",sum(e["bytes"] for e in inv))
PY
git status --short
```
Expected: `CATALOG_ID` `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` unchanged and a new
`BUILD_ID`; 51 inventory entries, 27 export contracts, `build_sources` with five roles; 3,764,949 rows and distinct
`gene_id`s per `record_starsolo.gtf`; `taxonomy_dfam.tsv` 1,221 lines with `match_status` 1,047 / 147 / 26; the
earlier archive verifies; core 26 checks pass; consumers with the shims: every parser check passes, IRescue passes,
STAR and cellranger gates pass or report a named refusal, Stellarscope unsupported; without the shims the execution
checks report `unsupported`; the child summary equals plan 18's table with the child `CATALOG_ID` equal to the
parent's; two core archives and two child archives in the scratch root with `current` on the new ones; `git status
--short` lists the touch list alone.

## Final message
Every file created or changed; acceptance outputs verbatim; the new core and child `BUILD_ID`s; measured sizes of
the new files and the payload total; peak resident memory and wall time of the core rebuild, the child rebuild and
the verifier; the measured records-and-instances numbers beside the plan's; the Dfam census beside plan 19's; the
STAR and cellranger observations; any deviation, with the observation and your reading of it.
