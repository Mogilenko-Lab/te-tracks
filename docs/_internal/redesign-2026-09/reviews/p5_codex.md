# Phase 5 review (codex gpt-6-astra)
Verdict: BLOCKING

## Blocking

- [B1] `tests/checks/consumers/11_stellarscope_parser.py:14`, `tests/checks/consumers/14_mates_parser.py:16`: package imports prevent required parser assertions from running — the suite reports missing `setuptools_scm` and `pyranges`. The binding phase contract, `15_phase5_consumer_fixtures.md:11`, requires always-supported parser tests. Loading Stellarscope's actual annotation package under an isolated package name bypassed its version-only initializer: grouping and attributes passed, then the real boundary gate returned the required defect message and exit 3. Executing MATES's actual `split_count_10X_data` function with its source helpers and loading `calculate_MU.py` directly passed the entire adapter check, exit 0. All needed parser dependencies are present — isolate these source imports, retain the real assertions, and update `docs/OUTPUTS.md:429`, `:433`, `:451` and `README.md:64` to the exercised support states.
- [B2] `tests/checks/consumers/10_irescue_parser.py:28`: the required IRescue `chrcat` name-handling test is missing — the check authors its own feature and mapping files, then calls `index_features`/`parse_maps`. Replacing the checkout module's `chrcat` with a function that raises `AssertionError` still produced exit 0. The contract explicitly names `chrcat` at `15_phase5_consumer_fixtures.md:12`; its actual feature serialization is in `../.ref/irescue/irescue/map.py:386` — run real `chrcat` on synthetic intersection rows and assert emitted record/subfamily identities before reading them back.
- [B3] `tests/lib/consumers.py:88`: every `ImportError` becomes unsupported, including failures in an installed module's API — a probe importing a nonexistent symbol from installed NumPy printed `unsupported: review_probe python module numpy absent` and exited 3. Such a failed check leaves the runner successful, violating the requested distinction between missing dependencies and other failures — classify confirmed missing modules separately; return exit 1 for incompatible APIs and internal import failures.

## Advisory

- [A1] `tests/checks/consumers/10_irescue_parser.py:29`, `:34`, `:41`; `tests/checks/consumers/13_tetranscripts_telocal_parser.py:43`: 7 of 53 fixture hashes differ across roots — the five `irescue_{record_features,record_maps,subfamily_features,subfamily_maps,comma_maps}.tsv.gz` files differ only in gzip MTIME. `record.locInd` and `subfamily.locInd` embed the absolute GTF path (`../.ref/TElocal/TElocal_Toolkit/TEindex.py:368`); their bytes become equal after normalizing that field. Pickle sizes are 2,009/1,406 bytes here versus 1,993/1,390 in the report. All remaining 46 hashes match, including every BAM, BAM/FASTA index, table and export. Use deterministic gzip headers and explicitly distinguish pickle semantic equality from byte equality when carrying these fixtures into later phases.
- [A2] `tests/checks/consumers/12_tesingle_parser.py:52`, `13_tetranscripts_telocal_parser.py:57`, `14_mates_parser.py:64`: reported parser versions are literals. They match the present checkout `setup.py` versions, but checkout changes can leave the support table stale — read or assert those versions when the parsers load.

## Acceptance re-run

All exact deliverable paths in `prompts/p5_impl.md` exist. Generated data belongs under the scratch root per its scope rule; the repository fixture directory contains the authored `expected.json`. The production resolver/exporter rebuilt 11 records, 8 names, 10 instances, seven exports and TwoLab's 2:1 plurality. TEsingle verifies both grains and the real 999/1,000 cutoff; TElocal builds both indexes with its own indexer and executes its actual pickle-reader branch. The numerical oracles agree with the contract; Stellarscope's admitted observed boundary is `0,1,1,1` against expected `0,1,1,0`.

I called `consumers.build_fixture()` with `tests/lib` on `sys.path` on the review root below. Commands ran with `PYTHONDONTWRITEBYTECODE=1` and `GIT_OPTIONAL_LOCKS=0`. The consumer acceptance command uses the requested `--refroot` override because the default command rebuilds the orchestrator's read-only fixtures. Core used the existing default build. Outputs below are verbatim.

```text
$ for f in tests/run.sh tests/checks/consumers/*.sh; do bash -n "$f" && echo "syntax ok $f"; done
syntax ok tests/run.sh
syntax ok tests/checks/consumers/20_irescue_exec.sh
syntax ok tests/checks/consumers/21_featurecounts_exec.sh
syntax ok tests/checks/consumers/22_bedtools_exec.sh
syntax ok tests/checks/consumers/23_samtools_fixture_integrity.sh
$ tests/run.sh consumers --refroot /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p5/codex/refroot; echo "exit=$?"
pass  00_tool_inventory.py  supported tool_inventory 1; irescue=absent; featureCounts=absent; stellarscope=absent; TEsingle=absent; TEcount=absent; TElocal=absent; bedtools=bedtools v2.31.1; samtools=samtools 1.21
pass  10_irescue_parser.py  supported irescue 1.2.0 checkout parser; record=11, subfamily=8; comma splits one name and exporter rejects it
unsupported  11_stellarscope_parser.py  unsupported: stellarscope python module setuptools_scm absent
pass  12_tesingle_parser.py  supported TEsingle 1.0 checkout parser; record=11, subfamily=8; 999 distinct UR dropped, 1000 kept
pass  13_tetranscripts_telocal_parser.py  supported TEtranscripts/TElocal 2.2.4/1.1.3 checkout parsers; TEtranscripts=8 groups; TElocal locInd record=11, subfamily=8
unsupported  14_mates_parser.py  unsupported: MATES python module pyranges absent
unsupported  20_irescue_exec.sh  unsupported: irescue absent
unsupported  21_featurecounts_exec.sh  unsupported: featureCounts absent
pass  22_bedtools_exec.sh  supported bedtools v2.31.1; duplicate names, half-open boundaries and -s/-S pass
pass  23_samtools_fixture_integrity.sh  supported samtools 1.21; 11 sorted, indexed BAMs; ARC=10 OCM=20 bulk=20 alignments, 8 molecules each
unsupported  30_registration_duckdb.py  unsupported: python module duckdb absent
checks=11 pass=6 fail=0 unsupported=5
exit=0
$ tests/run.sh core; echo "exit=$?"
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
pass  41_export_registration.py  registrations=18824745; five ID spellings cover every record once; seven inventory hashes and feature sets pass; count 7 stays 7 at record, subfamily and family levels
pass  42_exports_fixtures.py  hand-authored export bytes, membership selection, unresolved ranks, coordinate duplicates, shared instances, deterministic rebuild and identifier gates pass
checks=13 pass=13 fail=0 unsupported=0
exit=0
$ export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p5/codex/refroot
$ ls -la "$TE_TRACKS_REFROOT/fixtures/consumers/"
total 184
drwxrwsr-x+ 4 devuser devgroup  4096 Sep 16 14:12 .
drwxrwsr-x+ 3 devuser devgroup  4096 Sep 16 14:12 ..
-rw-rw-r--+ 1 devuser devgroup   537 Sep 16 14:12 allocation_3_3_arc.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:12 allocation_3_3_arc.bam.bai
-rw-rw-r--+ 1 devuser devgroup   774 Sep 16 14:12 allocation_3_3_ocm.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:12 allocation_3_3_ocm.bam.bai
-rw-rw-r--+ 1 devuser devgroup   534 Sep 16 14:12 allocation_4_2_arc.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:12 allocation_4_2_arc.bam.bai
-rw-rw-r--+ 1 devuser devgroup   776 Sep 16 14:12 allocation_4_2_ocm.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:12 allocation_4_2_ocm.bam.bai
-rw-rw-r--+ 1 devuser devgroup   519 Sep 16 14:12 arc_3prime.bam
-rw-rw-r--+ 1 devuser devgroup   176 Sep 16 14:12 arc_3prime.bam.bai
-rw-rw-r--+ 1 devuser devgroup 16786 Sep 16 14:12 bam_manifest.json
-rw-rw-r--+ 1 devuser devgroup   569 Sep 16 14:12 bulk_pe.bam
-rw-rw-r--+ 1 devuser devgroup   176 Sep 16 14:12 bulk_pe.bam.bai
drwxrwsr-x+ 3 devuser devgroup  4096 Sep 16 14:12 exports
-rw-rw-r--+ 1 devuser devgroup   211 Sep 16 14:12 featurecounts_onebase.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:12 featurecounts_onebase.bam.bai
-rw-rw-r--+ 1 devuser devgroup   360 Sep 16 14:12 featurecounts_pe.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:12 featurecounts_pe.bam.bai
-rw-rw-r--+ 1 devuser devgroup    74 Sep 16 14:12 irescue_comma_maps.tsv.gz
-rw-rw-r--+ 1 devuser devgroup   236 Sep 16 14:12 irescue_record_features.tsv.gz
-rw-rw-r--+ 1 devuser devgroup   195 Sep 16 14:12 irescue_record_maps.tsv.gz
-rw-rw-r--+ 1 devuser devgroup   345 Sep 16 14:12 irescue_simple_arc.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:12 irescue_simple_arc.bam.bai
-rw-rw-r--+ 1 devuser devgroup   444 Sep 16 14:12 irescue_simple_ocm.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:12 irescue_simple_ocm.bam.bai
-rw-rw-r--+ 1 devuser devgroup   140 Sep 16 14:12 irescue_subfamily_features.tsv.gz
-rw-rw-r--+ 1 devuser devgroup   114 Sep 16 14:12 irescue_subfamily_maps.tsv.gz
-rw-rw-r--+ 1 devuser devgroup   699 Sep 16 14:12 ocm_5prime_pe.bam
-rw-rw-r--+ 1 devuser devgroup   176 Sep 16 14:12 ocm_5prime_pe.bam.bai
-rw-rw-r--+ 1 devuser devgroup    51 Sep 16 14:12 onebase.saf
-rw-rw-r--+ 1 devuser devgroup    23 Sep 16 14:12 query.bed
-rw-rw-r--+ 1 devuser devgroup  2009 Sep 16 14:12 record.locInd
-rw-rw-r--+ 1 devuser devgroup   427 Sep 16 14:12 record_mates.bed
-rw-rw-r--+ 1 devuser devgroup   427 Sep 16 14:12 record_mates.csv
-rw-rw-r--+ 1 devuser devgroup  8113 Sep 16 14:12 reference.fa
-rw-rw-r--+ 1 devuser devgroup    39 Sep 16 14:12 reference.fa.fai
-rw-rw-r--+ 1 devuser devgroup  1406 Sep 16 14:12 subfamily.locInd
drwxrwsr-x+ 2 devuser devgroup  4096 Sep 16 14:12 tables
-rw-rw-r--+ 1 devuser devgroup   237 Sep 16 14:12 universes.json
$ for d in irescue stellarscope TEsingle MATES TEtranscripts TElocal; do git -C /workspaces/Meta-Aging/01_modules/.ref/$d status --short | head -3; done
```

The consumer output states every check's status and reason: inventory, IRescue parser, TEsingle, TEtranscripts/TElocal, bedtools and samtools pass; Stellarscope, MATES, IRescue execution, featureCounts and the unchanged DuckDB check exit 3. Inventory intentionally always passes. Actual IRescue and featureCounts execution remains unverified here.

Independent pysam accounting read every BAM and checked coordinates, header sort order and usable indexes. Tagged molecules use `(CB, UB)`; untagged molecules use the authored query-name prefix before `_copy`. Bulk therefore has nine query templates representing eight intended molecules. The simple IRescue and paired featureCounts inputs each include a third, gap-only molecule; their execution assertions expect two assigned molecules. These counts equal both `expected.json` and the builder manifest:

```text
allocation_3_3_arc.bam: alignments=12 templates=9 molecules=9 sorted=True indexed=True
allocation_3_3_ocm.bam: alignments=24 templates=9 molecules=9 sorted=True indexed=True
allocation_4_2_arc.bam: alignments=12 templates=9 molecules=9 sorted=True indexed=True
allocation_4_2_ocm.bam: alignments=24 templates=9 molecules=9 sorted=True indexed=True
arc_3prime.bam: alignments=10 templates=9 molecules=8 sorted=True indexed=True
bulk_pe.bam: alignments=20 templates=9 molecules=8 sorted=True indexed=True
featurecounts_onebase.bam: alignments=1 templates=1 molecules=1 sorted=True indexed=True
featurecounts_pe.bam: alignments=6 templates=3 molecules=3 sorted=True indexed=True
irescue_simple_arc.bam: alignments=4 templates=4 molecules=3 sorted=True indexed=True
irescue_simple_ocm.bam: alignments=8 templates=4 molecules=3 sorted=True indexed=True
ocm_5prime_pe.bam: alignments=20 templates=9 molecules=8 sorted=True indexed=True
All 11 BAMs equal expected.json and the builder manifest; bulk molecule identity uses the authored _copy suffix.
```

Scratch mutation probes froze rebuilding after copying fixtures, preserving the damaged inputs for the existing assertions. Stellarscope used its unchanged annotation source under an isolated package name; MATES used source extraction as described in B1. Executable count probes injected output tables into the actual assertion bodies because those binaries are absent. Results:

| Check | Scratch mutation or probe | Exit and evidence |
|---|---|---|
| `10_irescue_parser.py` | Replace one SubA BED name with BROKEN | 1, unexpected ninth name |
| `10_irescue_parser.py` | Make `chrcat` raise | 0, B2 |
| `11_stellarscope_parser.py` | Actual source with original inputs | 3, `unsupported: stellarscope 1.5 right-boundary overlap defect, observed 0,1,1,1 expected 0,1,1,0` |
| `11_stellarscope_parser.py` | Move `edge_100` to start 98 | 1, observed `[0, 0, 1, 1]` |
| `11_stellarscope_parser.py` | Change `gene_id` to `gene-id` | 1, attribute-set assertion |
| `11_stellarscope_parser.py` | Replace the defect message with WRONG MESSAGE | 3, altered text survives; the runner has no independent message oracle |
| `12_tesingle_parser.py` | Change one record transcript ID to BROKEN | 1, tuple-set assertion |
| `13_tetranscripts_telocal_parser.py` | Write invalid pickle bytes immediately before the loader | 1, actual TElocal loader exits 1 |
| `14_mates_parser.py` | Source-loaded original / change BED SubA name only | 0 / 1, CSV/BED disagreement |
| `20_irescue_exec.sh` assertion body | Inject SubA count 1 | 1, expected 2 |
| `21_featurecounts_exec.sh` assertion body | Inject SubA count 1 | 1, expected 2 |
| `22_bedtools_exec.sh` | Extend Edge BED end from 110 to 111 | 1, right-adjacent query hits Edge |
| `23_samtools_fixture_integrity.sh` | Give duplicated copy a distinct UB / move boundary read | 1 / 1, molecule-tag / block-coordinate assertions |
| `run_check` / executable dispatch | Missing module / absent irescue / ValueError | 3 naming module / 3 naming executable / 1 |
| `run_check` | Missing symbol in installed NumPy | 3, B3 |

Every sentence/docstring/comment in the requested files and both public diffs was read. The additions contain no contrastive negation, history or review-provenance chatter. Support-status statements require the B1 correction. Phase 6 inherits synthetic UCSC `chrA`/`chrB` inputs (`tests/lib/consumers.py:27`, `:300`); namespace preflight will need its own alias-aware fixture, as planned.

## Scope check

Entry status and full diff were inspected on `redesign-2026-09`. The six phase 6–9 planning changes named in the implementer report, plus the populated `prompts/p5_review.md`, were already present outside phase 5's allowed set. Their authorship cannot be established from this diff; the reported implementation files are within scope. Entry command output:

```text
$ git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short
 M README.md
 M docs/OUTPUTS.md
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/16_phase6_ensembl_preflight.md
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md
 M docs/_internal/redesign-2026-09/prompts/p5_review.md
 M docs/_internal/redesign-2026-09/prompts/p6_impl.md
 M docs/_internal/redesign-2026-09/prompts/p7_impl.md
 M docs/_internal/redesign-2026-09/prompts/p8_impl.md
 M docs/_internal/redesign-2026-09/prompts/p9_impl.md
?? docs/_internal/redesign-2026-09/prompts/p5_fix.md
?? docs/_internal/redesign-2026-09/reviews/p5_rulings.md
?? tests/checks/consumers/00_tool_inventory.py
?? tests/checks/consumers/10_irescue_parser.py
?? tests/checks/consumers/11_stellarscope_parser.py
?? tests/checks/consumers/12_tesingle_parser.py
?? tests/checks/consumers/13_tetranscripts_telocal_parser.py
?? tests/checks/consumers/14_mates_parser.py
?? tests/checks/consumers/20_irescue_exec.sh
?? tests/checks/consumers/21_featurecounts_exec.sh
?? tests/checks/consumers/22_bedtools_exec.sh
?? tests/checks/consumers/23_samtools_fixture_integrity.sh
?? tests/fixtures/consumers/
?? tests/lib/consumers.py
$ git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD --stat
 README.md                                          |   4 +-
 docs/OUTPUTS.md                                    |  40 ++++-
 .../16_phase6_ensembl_preflight.md                 |   7 +-
 .../18_phase8_gene_child_seam.md                   |   4 +-
 .../redesign-2026-09/prompts/p5_review.md          | 189 ++++++++++++++++++++-
 docs/_internal/redesign-2026-09/prompts/p6_impl.md |  48 +++---
 docs/_internal/redesign-2026-09/prompts/p7_impl.md |  78 ++++++---
 docs/_internal/redesign-2026-09/prompts/p8_impl.md |  29 ++--
 docs/_internal/redesign-2026-09/prompts/p9_impl.md |  37 ++--
 9 files changed, 354 insertions(+), 82 deletions(-)
```

All nine Git checkouts under `../.ref/` have empty `git status --short`; their non-Git file bytes and modification times match the entry snapshot. Stellarscope already contained three ignored `annotation/__pycache__/*.cpython-311.pyc` files at entry (mtime 2026-09-16 19:11:22 UTC); they are unchanged. The review created no checkout bytecode. A clean Git status alone cannot establish that an earlier session wrote no ignored files.

The orchestrator's 53 fixture files retain their original hashes and modification times. Repository content matches the entry snapshot except this review. Review scratch data was removed after validation; no installs, network access or Git write commands were used.
