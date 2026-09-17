# te-tracks phase 8 review (codex, read-only)

You are an independent reviewer of phase 8 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`, HEAD `cf1b150`). The implementer has
finished; you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p8_codex.md`. You change nothing else. No git writes anywhere (the
checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too; `14839-DM-cGAS` and `sene` there
are plain directories you leave alone), no installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md`,
   and the implementer's prompt `docs/_internal/redesign-2026-09/prompts/p8_impl.md` (exact interfaces and targets).
2. The decisions: `docs/DECISIONS.md` sections 4, 8, 9, 10, 12 and 16;
   `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md`.
3. The design sources: `docs/_internal/redesign-2026-09/consults/gene_child_consult.md` Q1 to Q4, Q7, Q8;
   `consults/mask_policy_consult.md` Q1 and Q6; rulings `reviews/m7_rulings.md` A1 and A2, `reviews/m5_rulings.md`
   A1 and A2, `reviews/p6_rulings.md` A2, `reviews/p7_rulings.md` A3.
4. The wording and comment rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".
5. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD --stat` and the full
   diff, plus every untracked file from `git status --short`. Every uncommitted entry in the tree is phase 8 work.
6. The implementer's own report, pasted below under "Implementer report".

## Judge, with evidence
- **Contract conformance**: every deliverable in the phase file present at the stated path with the stated
  content; every acceptance command re-run by you with its output quoted; any number that differs from the
  contract named.
- **Fixture adequacy**: do the fixtures and checks fail when they should? Try to break one (read-only: reason
  from the code, or run it against a modified copy under your scratch directory).
- **Silent assumptions**: anything the code or docs assume that the contract leaves open; anything that will
  bite phase 9 (the STARsolo record profile, the Dfam view, the matrix-binding fixture, the host runbook, the
  10x vM33-filtered child, the transcript-context relation).
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 8 review (codex gpt-6-astra)
Verdict: PASS | PASS WITH ADVISORIES | BLOCKING
## Blocking
- [B1] <file:line> <finding> — <evidence> — <what fixes it>
## Advisory
- [A1] ...
## Acceptance re-run
<commands and outputs, verbatim>
## Scope check
<git status / diff --stat summary>
```
BLOCKING means a contract deliverable is missing or wrong, an acceptance number differs, or a check cannot fail.
Keep the file under 200 lines. Facts over opinions; every finding cites a path and, where possible, a line.

## Phase 8 specifics
Facts: HEAD is `cf1b150`; the implementer's uncommitted changes are the phase 8 work alone (nine modified files,
ten untracked entries). Environment for every command:
`TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`,
`TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source`, `PYTHONDONTWRITEBYTECODE=1`.
The parent core build is `$TE_TRACKS_REFROOT/te_mm39/build` (`BUILD_ID` `9ddf3622…`, `CATALOG_ID` `90cc18be…`);
the implementer's child is `$TE_TRACKS_REFROOT/te_mm39_gene/build` (`BUILD_ID` `1804f94e…`) and its published copy
sits in `$TE_TRACKS_REFROOT/pubroot/te_mm39_gene/archive/1804f94e…` beside the parent archive under
`pubroot/te_mm39/`. Treat all four as read-only. Scratch work goes under
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/codex-p8/` (`/tmp` is noexec) and is removed with Python `shutil`
when you finish. `tests/run.sh core` takes about seven minutes here and writes only under `$TE_TRACKS_REFROOT/pubtest`
and `/workspaces/Meta-Aging/_scratch/te-tracks-audit/p8impl/`. `bedtools` v2.31.1 is at `/usr/local/bin/bedtools`.

Judge these in particular, each with evidence:
1. Geometry, independently: recompute the exon-subtracted blocks for at least one whole chromosome from the
   retained GTF and the parent's `exports/ucsc/interspersed/full/record.bed` with `bedtools merge` and
   `bedtools subtract` (unstranded), and compare block count, retained bases and the exact block set with the
   child's `exports/ucsc/interspersed/exon_subtracted/subfamily.saf` rows on that chromosome. The orchestrator
   measured chr19: 10,373 exon-union intervals, 4,434,265 bp, 86,429 records, 84,268 blocks, 21,565,706 bp, block
   sets identical; choose another chromosome or scaffold, and include one contig without annotation.
2. Summary census: recompute `tables/exon_subtraction_summary.tsv` for `interspersed` from
   `tables/exon_subtraction_status.tsv` joined to the parent catalog with your own code, and confirm the
   `records_on_unannotated_contigs` column against `tables/gene_annotation_coverage.tsv`.
3. Check independence: `tests/checks/core/80_exon_subtraction.py` imports the production `annotation_mask` for its
   residual-overlap sample and its coverage comparison, and `verify_products` in `src/lib/gene_child.py`
   recomputes the subtraction with the same `subtract_batch` that produced the tables. State which failures of the
   mask or subtraction code these can and cannot detect, and whether the hand-authored cases in
   `tests/fixtures/gene/geometry.json` (check 81) close the gap.
4. Scratch convention: checks 81, 82 and `tests/fixtures/gene/publication_cases.py` hardcode
   `/workspaces/Meta-Aging/_scratch/te-tracks-audit/p8impl` while checks 71 and 72 use `$TE_TRACKS_REFROOT/pubtest`.
   Judge against the repository's convention and the runner's `--refroot` option.
5. Dispatch and identity: `build.sh` argument exclusivity and refusals (a `current` path, a non-hex id, a symlinked
   parent, a child directory overlapping the parent); `config_values` unsetting an ambient `FAMILY`; the child's
   `RSS_FILE` under the build directory removed before the manifest (inventory 21 files); `resolve_parent`
   inferring the root from a `.staging` or `archive` parent directory name; `release.py` passing
   `root=family.parent` on every verification; `verify_export_contracts` running twice on the child path (once in
   `child_identity_from_payload`, once in `verify_build`). Confirm `99_verify.py` writes nothing.
6. Identity mutations: with your own code on copies of the child manifest, confirm each of the GTF digest, every
   policy value, the roster, a parent id and `child_universes` moves `BUILD_ID` while `CATALOG_ID` stays; confirm
   the child `CATALOG_ID` bytes equal the parent's; name the provenance keys the child adds (`stage_metrics`,
   `peak_rss_measurement`) and confirm they sit outside both hashes.
7. Publication: the child archive's modes (payload 0444, directories 0555), the relative `current` symlink, an
   empty `.staging`; `release.py verify-current` for both families; the refusal of `install`, `select` and
   `verify-current` when the parent archive is absent or corrupt, as exercised by check 83; an earlier core staying
   selectable after a child lands.
8. Documentation: `docs/OUTPUTS.md` phase 8 section against plan item 8 (mask sentence, conservation guarantee,
   status semantics with H3's two sentences, coverage table, copied inputs, capability `not_computed`);
   `docs/RELEASES.md` "Gene child snapshots" (identity fields, parent-first order, dependency verification, the
   transfer rule); `docs/RUNBOOK.md`, which the implementer created because the pre-read named a file that did not
   exist (judge its content against plan item 8 and the README truth table's split into a phase 8 row and a
   deferred phase 9 row; note the scratch paths it carries); README truth table rows.
9. Deviation reported by the implementer: only the absent `docs/RUNBOOK.md`. Name any deviation the report omits.
10. Prose: every public file and every comment, docstring and check message in the new code, against the wording
    rules.

## Implementer report
Implemented and published phase 8. **All 23 core checks pass.** Scratch and published children share BUILD_ID:

`1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b`

The parent build and archive remain unchanged. All census targets match the plan exactly. Status counts below are **measured / planned**:

| Universe | Unchanged | Trimmed | Split | Fully subtracted |
|---|---:|---:|---:|---:|
| all_rmsk | 5,086,684 / 5,086,684 | 61,378 / 61,378 | 15,495 / 15,495 | 157,214 / 157,214 |
| interspersed | 3,600,721 / 3,600,721 | 52,703 / 52,703 | 15,406 / 15,406 | 96,119 / 96,119 |
| compat_tetranscripts_mm39 | 3,633,401 / 3,633,401 | 52,842 / 52,842 | 15,399 / 15,399 | 97,987 / 97,987 |

Each SAF has **1,220 distinct GeneIDs for interspersed** and **1,225 for compat**, for both groupings in all three namespaces.

The scratch build took **406.200 seconds**, with whole-build maximum RSS **3,571,302,400 bytes**, measured through `RUSAGE_CHILDREN`. Its stage measurements were:

| Stage | Wall seconds | Peak RSS bytes |
|---|---:|---:|
| 00 fetch | 0.756 | 118,243,328 |
| 10 copy | 0.398 | 119,525,376 |
| 50 subtraction and exports | 164.622 | 886,882,304 |

The publication build took **493.353 seconds**. The two builds overlapped in separate directories.

There were no numeric or scope deviations. The requested pre-read `docs/RUNBOOK.md` was absent; I created it. Temporary `p8impl/` scratch was removed with `shutil`. No network access, installs, or Git write commands were used.

All **25 changed or created repository files** are within the touch list. The final status output below names 17 files individually; its two directory entries contain:

- [src/gene/00_fetch_gene_sources.sh](/workspaces/Meta-Aging/01_modules/te-tracks/src/gene/00_fetch_gene_sources.sh), [src/gene/10_copy_parent_inputs.sh](/workspaces/Meta-Aging/01_modules/te-tracks/src/gene/10_copy_parent_inputs.sh), [src/gene/50_build_exon_subtracted.sh](/workspaces/Meta-Aging/01_modules/te-tracks/src/gene/50_build_exon_subtracted.sh)
- [tests/fixtures/gene/annotation.gtf](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/gene/annotation.gtf), [tests/fixtures/gene/contig_aliases.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/gene/contig_aliases.tsv), [tests/fixtures/gene/coverage.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/gene/coverage.tsv), [tests/fixtures/gene/geometry.json](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/gene/geometry.json), [tests/fixtures/gene/publication_cases.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/gene/publication_cases.py)

Acceptance outputs follow verbatim, grouped in the requested command order.

```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok src/10_build_records.sh
syntax ok src/15_build_universes.sh
syntax ok src/20_build_taxonomy.sh
syntax ok src/30_build_exports.sh
syntax ok src/35_build_namespaces.sh
syntax ok src/gene/00_fetch_gene_sources.sh
syntax ok src/gene/10_copy_parent_inputs.sh
syntax ok src/gene/50_build_exon_subtracted.sh
syntax ok tests/run.sh
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build
[build] running 00_fetch_gene_sources.sh
[00_fetch_gene] cache: gencode.vM37.primary_assembly.annotation.gtf.gz
stage_metrics {"stage": "00_fetch_gene_sources.sh", "wall_seconds": 0.756, "peak_rss_bytes": 118243328}
[build] running 10_copy_parent_inputs.sh
stage_metrics {"stage": "10_copy_parent_inputs.sh", "wall_seconds": 0.398, "peak_rss_bytes": 119525376}
[build] running 50_build_exon_subtracted.sh
universe_name	records	unchanged	trimmed	split	fully_subtracted	retained_records	blocks	retained_bp	removed_bp	records_on_unannotated_contigs
all_rmsk	5320771	5086684	61378	15495	157214	5163557	5179754	1172003155	29569849	2638
interspersed	3764949	3600721	52703	15406	96119	3668830	3684934	1090369890	26235918	1612
compat_tetranscripts_mm39	3799629	3633401	52842	15399	97987	3701642	3717740	1094973237	26503064	1754
stage_metrics {"stage": "50_build_exon_subtracted.sh", "wall_seconds": 164.622, "peak_rss_bytes": 886882304}
ok build paths: regular files and directories
ok inventory: 21 files, exact paths, bytes and sha256
ok BUILD_ID: 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
ok parent dependency: te_mm39/9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d
ok child identity: inherited catalog, copied inputs, annotation and policy
ok export contracts: 12 namespace paths
ok child registration: every parent key, feature and ordered retained block
ok child status: complete catalog conservation and summary
ok annotation coverage: 38 annotated contigs of 61
ok child SAF rows and distinct features: registration per universe and grouping
verified 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
[build] done

real	6m46.200s
user	6m52.626s
sys	1m3.253s
exit=0
```

```text
universe_name	records	unchanged	trimmed	split	fully_subtracted	retained_records	blocks	retained_bp	removed_bp	records_on_unannotated_contigs
all_rmsk	5320771	5086684	61378	15495	157214	5163557	5179754	1172003155	29569849	2638
interspersed	3764949	3600721	52703	15406	96119	3668830	3684934	1090369890	26235918	1612
compat_tetranscripts_mm39	3799629	3633401	52842	15399	97987	3701642	3717740	1094973237	26503064	1754
1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
te_mm39_gene 9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e {'context_capability': 'not_computed', 'exon_mask_policy': 'all_exons_unstranded_union_v1', 'mask_definition': 'The mask unions every exon on both strands, merging overlapping or touching intervals.', 'min_retained_block_bp': 1} {'tables/contig_aliases.tsv': '4c2c18fdfae512f44789831b3eb2b8716e65e80da7fab41208a36e0053ca50c9', 'universes.json': '617feb99e7711f413df3e7935e532abcc12d4ecf7cfbcc4009a6cf31f2cb1b4c'} 702e27a8727db66cd23e9f66f5aa1d38
export_path	namespace	universe_name	variant	feature_level	format	rows	distinct_features	sha256
exports/ensembl/compat_tetranscripts_mm39/exon_subtracted/subfamily.saf	ensembl	compat_tetranscripts_mm39	exon_subtracted	subfamily	saf	3717740	1225	11ffddf7d72d390a844855bf802780a3206660a9e09d1c286d738ba02b46b5a7
exports/ensembl/compat_tetranscripts_mm39/exon_subtracted/taxonomy_triple.saf	ensembl	compat_tetranscripts_mm39	exon_subtracted	taxonomy_triple	saf	3717740	1225	2ae6882befe7e4a42f017e806ece992e1d60d759d73d790b71e2b6f64f19574f
exports/ensembl/interspersed/exon_subtracted/subfamily.saf	ensembl	interspersed	exon_subtracted	subfamily	saf	3684934	1220	b96f80ad87c03beb3114fe2e45c73941db4bd7be5da6fb3bef6300626d43faea
exports/ensembl/interspersed/exon_subtracted/taxonomy_triple.saf	ensembl	interspersed	exon_subtracted	taxonomy_triple	saf	3684934	1220	40c0e21eeec26c1f9f8fb16db5672a0ea632ede787f268f4d3dc9345c7cf1820
exports/gencode/compat_tetranscripts_mm39/exon_subtracted/subfamily.saf	gencode	compat_tetranscripts_mm39	exon_subtracted	subfamily	saf	3717740	1225	33487f6f3fb4d7909944ad11f2808182c9c2a49d594e75d76544dd8465de4f89
exports/gencode/compat_tetranscripts_mm39/exon_subtracted/taxonomy_triple.saf	gencode	compat_tetranscripts_mm39	exon_subtracted	taxonomy_triple	saf	3717740	1225	065b4469df10c060359d50e079d5f8b69ade4365a1cf6f911afa718cc5cddc21
exports/gencode/interspersed/exon_subtracted/subfamily.saf	gencode	interspersed	exon_subtracted	subfamily	saf	3684934	1220	1f3a5158d78fe33980ab460222dbbd17fdb63892ea0b2555bf053ed6eddbb49b
exports/gencode/interspersed/exon_subtracted/taxonomy_triple.saf	gencode	interspersed	exon_subtracted	taxonomy_triple	saf	3684934	1220	d04fb63974e59b07004feff9150b284ea28529b24fee4725c683257b8fd4afe0
exports/ucsc/compat_tetranscripts_mm39/exon_subtracted/subfamily.saf	ucsc	compat_tetranscripts_mm39	exon_subtracted	subfamily	saf	3717740	1225	debd0e15d9c5811ae29051ee18b480c53922a4d9dc51452361d2f5dbb036019c
exports/ucsc/compat_tetranscripts_mm39/exon_subtracted/taxonomy_triple.saf	ucsc	compat_tetranscripts_mm39	exon_subtracted	taxonomy_triple	saf	3717740	1225	ae1e271ed27a7655e8391ca80eafdccb696e78bf60a84743cbad9fad379bf2a8
exports/ucsc/interspersed/exon_subtracted/subfamily.saf	ucsc	interspersed	exon_subtracted	subfamily	saf	3684934	1220	827235cdb032dafa1cbc65c0710e4366555b2c922e1d9da46e83492201f80733
exports/ucsc/interspersed/exon_subtracted/taxonomy_triple.saf	ucsc	interspersed	exon_subtracted	taxonomy_triple	saf	3684934	1220	6dcc28d84ec824eeca9d4ca9f9e46582cb4fb185cdc8728492781e7434bb9d91
  3684935 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/ucsc/interspersed/exon_subtracted/subfamily.saf
  3684935 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/ucsc/interspersed/exon_subtracted/taxonomy_triple.saf
  7369870 total
  3717741 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/ucsc/compat_tetranscripts_mm39/exon_subtracted/subfamily.saf
  3717741 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/ucsc/compat_tetranscripts_mm39/exon_subtracted/taxonomy_triple.saf
  7435482 total
  3684935 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/ensembl/interspersed/exon_subtracted/subfamily.saf
  3684935 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/ensembl/interspersed/exon_subtracted/taxonomy_triple.saf
  7369870 total
  3717741 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/ensembl/compat_tetranscripts_mm39/exon_subtracted/subfamily.saf
  3717741 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/ensembl/compat_tetranscripts_mm39/exon_subtracted/taxonomy_triple.saf
  7435482 total
  3684935 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/gencode/interspersed/exon_subtracted/subfamily.saf
  3684935 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/gencode/interspersed/exon_subtracted/taxonomy_triple.saf
  7369870 total
  3717741 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/gencode/compat_tetranscripts_mm39/exon_subtracted/subfamily.saf
  3717741 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build/exports/gencode/compat_tetranscripts_mm39/exon_subtracted/taxonomy_triple.saf
  7435482 total
3717740 compat_tetranscripts_mm39	subfamily
3717740 compat_tetranscripts_mm39	taxonomy_triple
3684934 interspersed	subfamily
3684934 interspersed	taxonomy_triple
ok build paths: regular files and directories
ok inventory: 21 files, exact paths, bytes and sha256
ok BUILD_ID: 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
ok parent dependency: te_mm39/9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d
ok child identity: inherited catalog, copied inputs, annotation and policy
ok export contracts: 12 namespace paths
ok child registration: every parent key, feature and ordered retained block
ok child status: complete catalog conservation and summary
ok annotation coverage: 38 annotated contigs of 61
ok child SAF rows and distinct features: registration per universe and grouping
verified 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
exit=0
verify: child verification requires the parent archive
ok build paths: regular files and directories
ok inventory: 21 files, exact paths, bytes and sha256
ok BUILD_ID: 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
exit=1 (expected 1: parent required)
```

```text
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39_gene/.staging/build.sRjN4JAx
[build] running 00_fetch_gene_sources.sh
[00_fetch_gene] cache: gencode.vM37.primary_assembly.annotation.gtf.gz
stage_metrics {"stage": "00_fetch_gene_sources.sh", "wall_seconds": 0.618, "peak_rss_bytes": 117370880}
[build] running 10_copy_parent_inputs.sh
stage_metrics {"stage": "10_copy_parent_inputs.sh", "wall_seconds": 0.377, "peak_rss_bytes": 118382592}
[build] running 50_build_exon_subtracted.sh
universe_name	records	unchanged	trimmed	split	fully_subtracted	retained_records	blocks	retained_bp	removed_bp	records_on_unannotated_contigs
all_rmsk	5320771	5086684	61378	15495	157214	5163557	5179754	1172003155	29569849	2638
interspersed	3764949	3600721	52703	15406	96119	3668830	3684934	1090369890	26235918	1612
compat_tetranscripts_mm39	3799629	3633401	52842	15399	97987	3701642	3717740	1094973237	26503064	1754
stage_metrics {"stage": "50_build_exon_subtracted.sh", "wall_seconds": 162.058, "peak_rss_bytes": 898154496}
ok build paths: regular files and directories
ok inventory: 21 files, exact paths, bytes and sha256
ok BUILD_ID: 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
ok parent dependency: te_mm39/9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d
ok child identity: inherited catalog, copied inputs, annotation and policy
ok export contracts: 12 namespace paths
ok child registration: every parent key, feature and ordered retained block
ok child status: complete catalog conservation and summary
ok annotation coverage: 38 annotated contigs of 61
ok child SAF rows and distinct features: registration per universe and grouping
verified 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
installed 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
selected 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
[build] done

real	8m13.353s
user	8m24.100s
sys	1m13.645s
exit=0
1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
exit=0
9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d
exit=0
1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
archive/1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
core usage exit=0
```

```text
pass  01_runner_selftest.sh  runner statuses, required checks, diagnostics, dangling symlinks and usage exits pass
pass  10_rmsk_out_parser.py  6 expected records; plain/gzip, signed consensus, ID tokens, malformed/unreadable input and ID statistics pass
pass  11_source_qualification.sh  13 summary metrics and 10 field disagreements verified; reports identical; four source md5s and declared assembly match config pins
pass  20_records_schema.py  5320771 records; 24 typed columns; all typed rows equal; identities and bounds pass
pass  21_instances.py  4696900 instances; one instance per record; single contig; sizes 1=4251251 2=338697 3+=106952
pass  22_universes.py  six universe summaries and every membership match; 17 classes; 3 collision pairs; 20 multi-label names / 6517 records
pass  23_records_fixtures.py  hand-authored records, collisions, text IDs, signed fields, instances, bounds, joins, class sets and tRNA-family rules pass
pass  30_taxonomy_canonical.py  18484 names; all 15 columns recomputed exactly; 20 report rows equal the multi-label subset; census matches; minimum plurality share 0.840 MER63C
pass  31_taxonomy_dfam_agreement.py  report names missing from snapshot: []
pass  32_taxonomy_rule_fixtures.py  31 rule cases; permutations, rank shares, instance weighting, rounded median, deterministic builds, input gates and canonical rollups pass
pass  40_exports_shape.py  seven exports: 3764949 rows each; subfamilies=1220 families=49 taxonomy_triples=1220; coordinates and identifiers pass
pass  41_export_registration.py  registrations: interspersed=30119592 all_rmsk=5320771; eight interspersed ID spellings; instances=3152636; 24 inventory hashes, feature sets and GTF tuple/instance joins pass; three record grammars; count 7 stays 7 at record, subfamily and family levels
pass  42_exports_fixtures.py  eight hand-authored exports and 46 registration rows; seven-export/40-row interspersed job; membership selection, unresolved ranks, coordinate duplicates, shared instances, deterministic rebuild, universe and identifier gates pass
pass  60_contig_aliases.py  61 injective aliases and FASTA names/lengths; catalog=5320771 interspersed=3764949; all contigs carry catalog records; chr4_JH584295v1_random and chrM carry 2 and 4 catalog records, zero interspersed records
pass  61_namespace_exports.py  24 sorted exports and SHA-256 digests; 16 complete renamed files regenerated; interspersed=3764949 all_rmsk=5320771 per namespace; registrations=30119592+5320771
pass  62_preflight.sh  85 preflight cases; both universes, three namespaces, BED/GTF/SAF and sizes/FAI/BAM; covered=0, export-only=2, empty/shared-length/input errors=1; exact reports and enclosing build aliases pass
pass  70_manifest_identity.py  BUILD_ID=9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d CATALOG_ID=90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e; 43 payloads; identity mutations pass
pass  71_verify_build.py  real build verifies unchanged; fixture stray authoring payload, flipped byte, extra file, unpublished taxonomy rule and export roster mismatch fail with named discrepancies; fixture cases=2.454s
pass  72_publication_cases.py  identical and changed builds, export-roster evolution (4 archives), failed verification, concurrent installs/selects (5 archives), old IDs, forged ID, corrupt current, selector and root cases, occupied targets, symlinks and 0444/0555 modes pass
pass  80_exon_subtraction.py  5320771 records conserve bases; registered blocks ordered, disjoint and contained; 200000-record sample exon-disjoint; summary census, 14805348 registrations, 12 SAFs and coverage 38/61 with 2638 unannotated records pass
pass  81_exon_subtraction_fixtures.py  12 geometry cases, 12 SAFs, 64 registrations, annotation coverage, duplicate invariance and named refusals pass
pass  82_child_identity.py  child identity fields, inherited pins, all policy/GTF/roster/parent mutations, dependency and payload refusals, CLI usage gates pass
pass  83_child_publication_cases.sh  child install/select/verify-current require present, verified parent; repeated publication converges; archive resolution, preserved selection, immutable modes and earlier core selection pass
checks=23 pass=23 fail=0 unsupported=0
exit=0
 M README.md
 M build.sh
 M docs/OUTPUTS.md
 M docs/RELEASES.md
 M src/90_manifest.py
 M src/99_verify.py
 M src/lib/manifest.py
 M src/release.py
 M tests/fixtures/publication/build_fixture.py
?? config/mm39_gene.env
?? docs/RUNBOOK.md
?? src/gene/
?? src/lib/gene_child.py
?? tests/checks/core/80_exon_subtraction.py
?? tests/checks/core/81_exon_subtraction_fixtures.py
?? tests/checks/core/82_child_identity.py
?? tests/checks/core/83_child_publication_cases.sh
?? tests/expectations/mm39/exon_subtraction_summary.tsv
?? tests/fixtures/gene/
```