# te-tracks phase 5 review (codex, read-only)

You are an independent reviewer of phase 5 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p5_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/15_phase5_consumer_fixtures.md`
2. The decisions: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md`
3. The wording and comment rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments"
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD --stat` and the full
   diff, plus untracked files from `git status --short`.
5. The implementer's own report, pasted below under "Implementer report".

## Judge, with evidence
- **Contract conformance**: every deliverable in the phase file present at the stated path with the stated
  content; every acceptance command re-run by you with its output quoted; any number that differs from the
  contract named.
- **Fixture adequacy**: do the fixtures and checks fail when they should? Try to break one (read-only: reason
  from the code, or run it against a modified copy under /tmp).
- **Silent assumptions**: anything the code or docs assume that the contract leaves open; anything that will
  bite phase 6.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 5 review (codex gpt-6-astra)
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

## Orchestrator notes (check these in addition)
- The plan file and `reviews/m2_rulings.md` ("Phase 5") bind: TElocal's `.locInd` built by its own indexer and
  loaded through its pickle reader; TEsingle's tuple at record grain from `record.gtf` and at subfamily grain
  from `subfamily.gtf`; the fixture roster of 11 records, 8 names, 10 instances stated in `prompts/p5_impl.md`.
- Rebuild the synthetic fixture set through `tests/lib/consumers.py` into your own refroot under
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p5/` and run `tests/run.sh consumers --refroot <yours>`;
  compare every fixture file's sha256 with the orchestrator's under
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/fixtures/consumers/` (read-only). Remove yours when done.
- Support honesty: for each check, state which status it reports here and why; confirm an absent executable, a
  missing checkout dependency and the Stellarscope boundary defect each yield exit 3 with the stated reason, and
  that any other failure yields exit 1. Confirm `tests/run.sh consumers` exits 0 here.
- Count molecules in each fixture BAM with pysam yourself and compare to the builder's intent and to what the
  checks assert; confirm every BAM is sorted and indexed.
- Confirm no write reached any checkout under `/workspaces/Meta-Aging/01_modules/.ref/` (`git status --short` in
  each) and no bytecode was written there.
- Fixture adequacy: on scratch copies, break one thing per check (a molecule count, a boundary read, the
  Stellarscope defect message, the TElocal pickle, the TEsingle tuple) and name the check that fails.
- Wording: every sentence and comment in `tests/lib/consumers.py`, the consumers checks, the OUTPUTS.md
  "Consumer contracts" section and the README diff.

- The implementer reports Stellarscope and MATES parser checks as unsupported because the checkouts' imports fail
  on absent dependencies (`setuptools_scm`, `pyranges`); judge whether the Stellarscope boundary gate and the
  attribute regex can be exercised from the checkout's source without that import, since the plan calls those
  parser-level tests "always supported".

## Implementer report
Implemented phase 5. Consumers: **6 passed, 5 unsupported, exit 0**. Core: **13 passed, exit 0**. No git writes, installs, or network access.

Files created or changed:

- [README.md](/workspaces/Meta-Aging/01_modules/te-tracks/README.md)
- [docs/OUTPUTS.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/OUTPUTS.md)
- [tests/lib/consumers.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/lib/consumers.py)
- [tests/fixtures/consumers/expected.json](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/consumers/expected.json)
- [00_tool_inventory.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/00_tool_inventory.py)
- [10_irescue_parser.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/10_irescue_parser.py)
- [11_stellarscope_parser.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/11_stellarscope_parser.py)
- [12_tesingle_parser.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/12_tesingle_parser.py)
- [13_tetranscripts_telocal_parser.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/13_tetranscripts_telocal_parser.py)
- [14_mates_parser.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/14_mates_parser.py)
- [20_irescue_exec.sh](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/20_irescue_exec.sh)
- [21_featurecounts_exec.sh](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/21_featurecounts_exec.sh)
- [22_bedtools_exec.sh](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/22_bedtools_exec.sh)
- [23_samtools_fixture_integrity.sh](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/23_samtools_fixture_integrity.sh)

Support matrix:

| Tool | Status | Reason |
|---|---|---|
| IRescue 1.2.0 | Parser supported; execution unsupported | Executable absent |
| Stellarscope 1.5 | Unsupported | `setuptools_scm` absent; executable absent |
| TEsingle 1.0 | Parser supported; execution unsupported | Executable absent |
| TEtranscripts 2.2.4 | Parser supported; execution unsupported | `TEcount` absent |
| TElocal 1.1.3 | Parser/index round trips supported; execution unsupported | Executable absent |
| MATES 0.1.8 | Unsupported | `pyranges` absent |
| featureCounts | Unsupported | Executable absent |
| bedtools 2.31.1 | Supported | Intersection, boundaries and strand checks pass |
| samtools 1.21 | Supported | All 11 BAMs pass integrity checks |
| DuckDB | Unsupported | Existing check requires absent `duckdb` module |

Deviations:

- Stellarscope stops at its missing dependency before boundary evaluation. The exact defect gate remains implemented with expected `0,1,1,0`.
- TEsingle’s cutoff comparison resides in `TEtools/Counters.py:247`; `TEsingle:92–93` defines the option. The check verifies both and exercises the actual filtering function.
- Six unrelated phase 6–9 planning files changed during the session. They appear in git status below and were left untouched.
- Expected values remained unchanged.

Acceptance outputs follow verbatim.

```text
syntax ok tests/run.sh
syntax ok tests/checks/consumers/20_irescue_exec.sh
syntax ok tests/checks/consumers/21_featurecounts_exec.sh
syntax ok tests/checks/consumers/22_bedtools_exec.sh
syntax ok tests/checks/consumers/23_samtools_fixture_integrity.sh
```

`tests/run.sh consumers; echo "exit=$?"`:

```text
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
```

`tests/run.sh core; echo "exit=$?"`:

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
pass  41_export_registration.py  registrations=18824745; five ID spellings cover every record once; seven inventory hashes and feature sets pass; count 7 stays 7 at record, subfamily and family levels
pass  42_exports_fixtures.py  hand-authored export bytes, membership selection, unresolved ranks, coordinate duplicates, shared instances, deterministic rebuild and identifier gates pass
checks=13 pass=13 fail=0 unsupported=0
exit=0
```

`ls -la "$TE_TRACKS_REFROOT/fixtures/consumers/"`:

```text
total 184
drwxrwsr-x+ 4 devuser devgroup  4096 Sep 16 14:01 .
drwxrwsr-x+ 3 devuser devgroup  4096 Sep 16 13:57 ..
-rw-rw-r--+ 1 devuser devgroup   537 Sep 16 14:01 allocation_3_3_arc.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:01 allocation_3_3_arc.bam.bai
-rw-rw-r--+ 1 devuser devgroup   774 Sep 16 14:01 allocation_3_3_ocm.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:01 allocation_3_3_ocm.bam.bai
-rw-rw-r--+ 1 devuser devgroup   534 Sep 16 14:01 allocation_4_2_arc.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:01 allocation_4_2_arc.bam.bai
-rw-rw-r--+ 1 devuser devgroup   776 Sep 16 14:01 allocation_4_2_ocm.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:01 allocation_4_2_ocm.bam.bai
-rw-rw-r--+ 1 devuser devgroup   519 Sep 16 14:01 arc_3prime.bam
-rw-rw-r--+ 1 devuser devgroup   176 Sep 16 14:01 arc_3prime.bam.bai
-rw-rw-r--+ 1 devuser devgroup 16786 Sep 16 14:01 bam_manifest.json
-rw-rw-r--+ 1 devuser devgroup   569 Sep 16 14:01 bulk_pe.bam
-rw-rw-r--+ 1 devuser devgroup   176 Sep 16 14:01 bulk_pe.bam.bai
drwxrwsr-x+ 3 devuser devgroup  4096 Sep 16 13:57 exports
-rw-rw-r--+ 1 devuser devgroup   211 Sep 16 14:01 featurecounts_onebase.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:01 featurecounts_onebase.bam.bai
-rw-rw-r--+ 1 devuser devgroup   360 Sep 16 14:01 featurecounts_pe.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:01 featurecounts_pe.bam.bai
-rw-rw-r--+ 1 devuser devgroup    74 Sep 16 14:01 irescue_comma_maps.tsv.gz
-rw-rw-r--+ 1 devuser devgroup   236 Sep 16 14:01 irescue_record_features.tsv.gz
-rw-rw-r--+ 1 devuser devgroup   195 Sep 16 14:01 irescue_record_maps.tsv.gz
-rw-rw-r--+ 1 devuser devgroup   345 Sep 16 14:01 irescue_simple_arc.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:01 irescue_simple_arc.bam.bai
-rw-rw-r--+ 1 devuser devgroup   444 Sep 16 14:01 irescue_simple_ocm.bam
-rw-rw-r--+ 1 devuser devgroup   104 Sep 16 14:01 irescue_simple_ocm.bam.bai
-rw-rw-r--+ 1 devuser devgroup   140 Sep 16 14:01 irescue_subfamily_features.tsv.gz
-rw-rw-r--+ 1 devuser devgroup   114 Sep 16 14:01 irescue_subfamily_maps.tsv.gz
-rw-rw-r--+ 1 devuser devgroup   699 Sep 16 14:01 ocm_5prime_pe.bam
-rw-rw-r--+ 1 devuser devgroup   176 Sep 16 14:01 ocm_5prime_pe.bam.bai
-rw-rw-r--+ 1 devuser devgroup    51 Sep 16 14:01 onebase.saf
-rw-rw-r--+ 1 devuser devgroup    23 Sep 16 14:01 query.bed
-rw-rw-r--+ 1 devuser devgroup  1993 Sep 16 14:01 record.locInd
-rw-rw-r--+ 1 devuser devgroup   427 Sep 16 14:01 record_mates.bed
-rw-rw-r--+ 1 devuser devgroup   427 Sep 16 14:01 record_mates.csv
-rw-rw-r--+ 1 devuser devgroup  8113 Sep 16 14:01 reference.fa
-rw-rw-r--+ 1 devuser devgroup    39 Sep 16 14:01 reference.fa.fai
-rw-rw-r--+ 1 devuser devgroup  1390 Sep 16 14:01 subfamily.locInd
drwxrwsr-x+ 2 devuser devgroup  4096 Sep 16 13:57 tables
-rw-rw-r--+ 1 devuser devgroup   237 Sep 16 14:01 universes.json
```

The generated subdirectories additionally contain:

```text
exports/ucsc/interspersed/full/record.bed
exports/ucsc/interspersed/full/subfamily.bed
exports/ucsc/interspersed/full/family.bed
exports/ucsc/interspersed/full/record.gtf
exports/ucsc/interspersed/full/subfamily.gtf
exports/ucsc/interspersed/full/subfamily.saf
exports/ucsc/interspersed/full/taxonomy_triple.saf
tables/rmsk_records.tsv.gz
tables/rmsk_records.parquet
tables/rmsk_instance_members.tsv.gz
tables/rmsk_taxonomy.tsv
tables/taxonomy_canonical.tsv
tables/taxonomy_resolution_report.tsv
tables/universe_members.tsv.gz
tables/export_feature_members.tsv.gz
tables/exports.tsv
```

`git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short`:

```text
 M README.md
 M docs/OUTPUTS.md
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/16_phase6_ensembl_preflight.md
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md
 M docs/_internal/redesign-2026-09/prompts/p6_impl.md
 M docs/_internal/redesign-2026-09/prompts/p7_impl.md
 M docs/_internal/redesign-2026-09/prompts/p8_impl.md
 M docs/_internal/redesign-2026-09/prompts/p9_impl.md
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
```

The status loop over `irescue`, `stellarscope`, `TEsingle`, `MATES`, `TEtranscripts`, and `TElocal` produced no output; all six checkouts are clean.
