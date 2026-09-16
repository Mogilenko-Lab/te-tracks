# Phase 4 re-review (Opus)
Verdict: PASS WITH ADVISORIES

Every delivered byte reproduces from the canonical tables with code that imports nothing from `src/`
or `tests/`; all seven exports and both tables are bit-identical to the orchestrator's build; every
acceptance number in the contract matches; each of the five gates fails on demand. Nothing in the
delivered work blocks. Two items entered the contract *during* this review as its own rulings
(`14_phase4_exports.md:43-46`, amended between my first read and my first md5 snapshot) and have no
implementation yet; they gate closing the phase, not the implementation.

## Blocking
- none in the delivered exports, tables, checks or fixtures.
- [O1] `tests/checks/consumers/` — holds only `.gitkeep`; the amended contract and
  `reviews/p4_rulings.md` name `tests/checks/consumers/30_registration_duckdb.py`. I agree with the
  B1 ruling on evidence: `python3 -c "import duckdb"` → `ModuleNotFoundError`, no `duckdb` on PATH,
  so pandas is the only in-container proof and the delivered fixture is the right in-container form.
- [O2] `src/lib/build_exports.py:90` — the amended contract requires the exporter to reject resolved
  canonical tokens beginning with `unresolved_`. It accepts them today (evidence in A3).

## Advisory
- [A1] `README.md:126` — "contain six files … GTF at record level" contradicts the same file's truth
  table (`README:83-89`, seven paths per namespace incl. `subfamily.gtf`) and `docs/OUTPUTS.md:249`,
  `:281`, `:421`. Agree with codex A1; the phase that added the seventh file left this sentence at six.
- [A2] `tests/checks/core/41_export_registration.py:24` — `target` is never asserted. Agree with
  codex A2; probe (h) below states exactly what the fixture does and does not prove.
- [A3] `src/lib/build_exports.py:90` — reproduced codex A3 independently. A scratch taxonomy where
  `Mystery` carries an unresolved family and `Impostor` carries a *resolved* `canonical_family`
  spelled `unresolved_family_Mystery`, both class `DNA`, emits one `family.bed` name
  `DNA/unresolved_family_Mystery` over both records, and the family-level registration lists both
  under that one id — two meanings in one bucket. mm39 exposure is zero: of 18,484 names, 0 carry an
  unresolved rank (statuses are `concordant`, `unspecified`, `resolved_*`) and 0 canonical labels
  begin with `unresolved_`. Hardening, matching the ruling.
- [A4] `docs/OUTPUTS.md:287` (and the pre-existing `:48`) — "sorted by `(chrom, start_1, end_1,
  strand, rmsk_name)` in C-locale text order" holds for the text columns only; the integer columns
  sort numerically, because they are `int64` in the parquet and `sort_values` orders them as numbers.
  `LC_ALL=C sort -c -t$'\t' -k1,1 -k2,2 record.bed` reports disorder at line 9122 (`chr1 9999956`
  then `chr1 10000000`); `-k1,1 -k2,2n` passes. A consumer who validates or re-derives the order from
  the documented rule reorders the file and breaks the digest it pinned. Say the text columns sort in
  C-locale byte order and the coordinates numerically ascending. Contig order is genuinely C-locale
  (`chr1, chr10, chr11, …`, 59 contigs, each contiguous).
- [A5] The writer's peak RSS is 5.5 GB for mm39: it materializes all 5,320,771 records × 9 columns
  before selecting the 3,764,949 members. 95 s wall, 2.6 GB written. Worth a line in the phase-7 host
  runbook beside the disk figure, since it sets the host floor.

## Probe (h): which assertion catches a corrupted registration
Mutations of the synthetic `registration` frame the fixture rolls up, one at a time:

| mutation | outcome |
|---|---|
| baseline | exit 0 |
| all nine `target` values → `WRONG` | **exit 0 — not caught** |
| `family` level dropped entirely | `assert total == 7` (line 31), `('family', 0)` |
| one `family` row dropped (`r3`) | `assert … .eq(21).all()` (line 32) |
| one `subfamily` row duplicated (`r1`) | line 32 |
| a `record` row relabelled `family` | line 32 |
| `r3` rows retargeted to an unregistered record | line 32 |
| membership duplicated (`F→r1` twice) | `MergeError` from `validate="one_to_many"` (line 27) |

So the fixture *does* fail when the registration is corrupted, and **line 32 is the assertion that
catches it** — every edge-multiplicity error lands there; line 31 catches only a wholly missing level;
line 27's validate catches duplicated membership. What no assertion reaches is the rolled-up feature
identity, so the printed line "count 7 stays 7 at record, subfamily and family levels" is true of the
arithmetic and overstates the coverage of the target. The ruling's fix (assert the target per feature
and the per-level totals) closes exactly this gap.

## Checks made to fail
Scratch refroots of per-file symlinks with one mutated copy; tracked and untracked repo md5s identical
before and after (176 tracked files, 18 phase-4 untracked files).

| mutation | check | assertion reached |
|---|---|---|
| `record.bed` row 1 start +1 | `40_exports_shape.py` | `:56` via `:90` — `('record.bed', 'start_0', 0)` |
| `record.gtf` row 1 `family_id`/`class_id` swapped | `40_exports_shape.py` | `:108` — `('record.gtf', 'attribute grammar', 0)` |
| last registration row dropped | `41_export_registration.py` | `:71` — "one row per record and ID spelling" |
| `exports.tsv` `family.bed` digest zeroed | `41_export_registration.py` | `:96` — `assert digest.hexdigest() == row.sha256` |
| fixture `rmsk_name` → `Bad,Name` | `42_exports_fixtures.py` | `:74` — `build_exports: invalid export identifier 'Bad,Name' in …/subfamily.bed` |

## Numbers recomputed

| quantity | contract | observed | command |
|---|---|---|---|
| `record.bed` rows | 3,764,949 | 3,764,949 | independent regeneration + line count |
| `subfamily.bed` rows / names | 3,764,949 / 1,220 | 3,764,949 / 1,220 | same |
| `family.bed` rows / buckets | 3,764,949 | 3,764,949 / 49 | same |
| `record.gtf`, `subfamily.gtf` rows | 3,764,949 each | 3,764,949 each | same |
| `subfamily.saf`, `taxonomy_triple.saf` | 3,764,949 + header | 3,764,950 lines each | same |
| `taxonomy_triple.saf` distinct GeneIDs | 1,220 | 1,220 | 1,240 distinct raw `(name,family,class)` over 1,220 names → the 20 doubled names collapse |
| BED offset | `start_1 - 1` every row | 0 mismatches | byte-identical regeneration of all 7 files |
| GTF/SAF coordinates | equal the table | 0 mismatches | same; SAF GeneIDs equal the table in order |
| GTF attributes, 10,000-row sample each | order + values | 0 mismatches in 20,000 rows | own regex parse vs table-derived expectation |
| registration rows | 5 per record | 18,824,745 = 5 × 3,764,949 (record 7,529,898; subfamily/family/triple 3,764,949 each) | own streaming pass |
| record level both spellings | every record | 3,764,949 id + 3,764,949 alias, each exactly once | same |
| every emitted id resolves | all | all 7 files ⊆ registration id sets | same |
| block bounds | record bounds | 0 mismatches over 18,824,745 rows | same |
| alphabet | component + `\|` `:` `/` | 0 outside; 0 of `, # ~ % ; "` or whitespace | scan of every BED name, GTF attribute value, SAF GeneID |
| conservation | 7 at 3 levels | 7, 7, 7 | own synthetic count table over 3 records |
| digests vs orchestrator | — | 9/9 identical, gzip bytes included | `sha256sum`; `cmp` on the decompressed registration |
| core suite | — | `checks=13 pass=13 fail=0 unsupported=0` | `tests/run.sh core` |
| build cost | — | 95 s, 5.5 GB peak RSS, 2.6 GB out | `time`; 2 s RSS poll |
| git | phase 3 commit latest, phase 4 uncommitted | `ba6682e` at `HEAD@{0}`, 8 modified + 14 untracked | `git reflog -3`, `git status --short` |

Silent assumptions checked: the sort key is unique by construction (the builder raises on duplicate
`RECORD_KEY`), so the emitted order is fully determined and pandas' lexsort stability is not load-bearing;
`min(sw_score, 1000)` clips 1,225,802 rows, BED scores run 180–1000 and cannot go negative (global
`sw_score` range 0–71,131), while the GTF keeps the raw score as documented; the unresolved-token path is
fixture-covered (`Mystery`, `Opaque`) though mm39 never reaches it; `/` stays legal in `chrom` at the record
layer and is rejected at export with a fixture, which is a defensible split. Comments and docstrings in the
new files state intent in one line, with no banners, history or provenance; the changed public prose adds no
contrastive negation; no file name carries consumer or modality vocabulary.

## Agreement with codex review
- **B1 (DuckDB conservation query):** agree the contract as authored required DuckDB and the delivery is
  pandas; agree with the orchestrator's ruling on evidence (module and executable both absent). No longer
  blocking; what remains is the `consumers`-mode check, which does not exist yet (O1).
- **A1 (README counts six):** agree, unchanged. `README.md:126` still says six and names GTF only at record
  level while the same file's truth table and `OUTPUTS.md` say seven.
- **A2 (`target` unused):** agree, and confirmed exactly — nine `WRONG` targets exit 0. I disagree with one
  implication readers might draw from "before citing this fixture as proof of rollups": the fixture is not
  inert. Line 32 catches every dropped, duplicated, relabelled or retargeted registration row, and line 27's
  `validate="one_to_many"` is a real duplication guard. The gap is the target identity alone.
- **A3 (reserved prefix unenforced):** agree, reproduced independently with a different fixture pair;
  mm39 exposure is zero on both sides of the collision.

Method note: I built into my own directory with `universes.json` and each input table as individual symlinks
inside a real `tables/`, rather than symlinking `tables/` itself — the writer creates
`export_feature_members.tsv.gz` and `exports.tsv` inside `tables/`, so a symlinked directory would have
overwritten the orchestrator's two generated tables. Reviewer scratch under
`_scratch/te-tracks-audit/opus-p4/` is removed; the orchestrator's build verifies unchanged
(`exports.tsv` sha256 `55a1eb21…`). No git write, install or network access occurred; this report is my
only output.
