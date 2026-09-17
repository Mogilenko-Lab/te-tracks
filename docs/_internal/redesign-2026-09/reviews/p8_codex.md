# Phase 8 review (codex gpt-6-astra)
Verdict: BLOCKING

## Blocking

- [B1] `src/lib/gene_child.py:385` and `tests/checks/core/80_exon_subtraction.py:100`: SAF coordinates, contigs and strands are never compared with registration. The verifier checks row counts, declared distinct counts and headers; check 80 adds only actual GeneID sets. On the tiny publication fixture I changed `Example chr1 2..2 +` to masked exon `3..3`, retained registration `2..2,4..5`, updated the export digest and ran production `write_manifest`: creation and `99_verify.py` both succeeded (BUILD_ID `6f492ec154f5325e600b8348f07e51c261481ba45a95a887b0ada05c3f961721`). This misses plan item 6's SAF/registration equality and permits exon-overlapping published support. Compare each SAF's full row multiset against registration joined to parent strand/contig and namespace aliases; add this self-consistently rehashed mutation to check 82.
- [B2] `build.sh:65` and `build.sh:88`: trailing slashes bypass the symlinked-parent refusal. Against the same tiny parent, `--parent-dir parent-link` exits 2 with usage; `--parent-dir parent-link/` passes parent verification, creates child outputs and runs all three stages before the tiny parent's GTF bounds cause exit 1. The shell symlink test follows the trailing slash, then `realpath` erases the evidence before `validate_parent`. Validate the normalized lexical parent path before resolving symlinks, and cover both spellings in check 82.

## Advisory

- [A1] `tests/checks/core/81_exon_subtraction_fixtures.py:30`, `82_child_identity.py:53`, `tests/fixtures/gene/publication_cases.py:14`: scratch is fixed to `/workspaces/Meta-Aging/_scratch/te-tracks-audit/p8impl`. `tests/run.sh:29` exports the selected absolute `--refroot`, while checks 71/72 use its `pubtest`. The new checks read the selected root but write to another location, requiring this workspace layout even with `--refroot`. Use `$TE_TRACKS_REFROOT/pubtest` and `TemporaryDirectory`; the implementer's scratch instruction should remain an execution detail.
- [A2] `tests/checks/core/80_exon_subtraction.py:39` and `src/lib/gene_child.py:296`: shared `annotation_mask` lets a coherently wrong mask pass coverage comparison and sampled residual checks; shared `subtract_batch` at `gene_child.py:315` also reproduces coherent subtraction defects. Check 80 independently catches conservation, containment, ordering, registration-length and sampled residual errors against that mask; pinned censuses catch aggregate changes. Check 81's hand-authored outputs close the specified central split, intronic/intergenic, full loss, unannotated, scaffold, one-base, endpoint, opposite-strand, adjacency and duplicate cases. A copied implementation with `left-1` changed to `left` failed its Central assertion. They do not exhaust nested/nonidentical overlapping exons, three-plus blocks or batch-boundary defects; preserve an independent bedtools acceptance oracle.
- [A3] `src/lib/gene_child.py:42`, `src/lib/manifest.py:364`: policy validation and payload admission describe the current snapshot only. Future context or mask work must retain published policy/schema branches and admit its additional tables without invalidating vM37 archives. The vM33-filtered child must pin the actual counting GTF (and verify the ARC source separately); contig preflight in `docs/RUNBOOK.md:37` proves names/lengths, not annotation equivalence. Core source-role verification also compares against live `SOURCE_CONFIG` (`src/lib/manifest.py:150`): adding `dfam_snapshot` to that set must preserve admission of these four-source parent archives. Phase 9's STARsolo profile and Dfam view change the core BUILD_ID, requiring a new child parent pin while preserving CATALOG_ID. The pair-only matrix prose in `docs/OUTPUTS.md:436` still needs the scheduled phase 9 amendment; its fixture must bind `(universe_name, variant, feature_level, key_grammar)` across these overlapping universes (`docs/DECISIONS.md:160`).

Documentation conforms to plan item 8: `docs/OUTPUTS.md:580` supplies the mask, conservation, four statuses, both H3 sentences, coverage, copies and `not_computed`; `docs/RELEASES.md:180` supplies identity, parent-first publication and transfer dependencies. `docs/RUNBOOK.md:9` is a scratch invocation, with the full host qualification correctly deferred by `README.md:133`. Creation of the missing runbook is justified. New public prose, comments, docstrings and check messages contain no gratuitous contrastive negation or review/history chatter. The report omits B1/B2 and the scratch portability departure; measured census values have no deviation.

Dispatch otherwise passes exclusivity, current/nonhex and both overlap refusals. `config_values` clears ambient FAMILY (`src/lib/manifest.py:379`); RSS_FILE is removed before the 21-file inventory (`build.sh:159`). `.staging`/`archive` root inference (`manifest.py:291`) matches the contract; every release verification supplies `root=family.parent` (`src/release.py:60,125`). The two export-contract calls (`manifest.py:371,551`) repeat a small roster/count/digest comparison. Check 83 exercises missing/corrupt-parent refusal for install/select/verify-current, repeated publication and earlier-core selection.

## Acceptance re-run

All commands used the environment below. Build/publication destinations were moved under S to keep the four supplied trees read-only; the parent family was copied with `cp -a --reflink=auto` into S/pubroot first. Repeated census and successful-verifier output blocks from both builds are quoted once in the direct acceptance output. All other output lines below are verbatim. The initial publication attempt before the parent copy completed exited 1, `gene_child: child verification requires the parent archive`; the completed-copy rerun is shown.
```text
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1
S=/workspaces/Meta-Aging/_scratch/te-tracks-audit/codex-p8; C="$TE_TRACKS_REFROOT/te_mm39_gene/build"; TIMEFORMAT="real %3R user %3U sys %3S"
$ for f in build.sh lib/common.sh src/*.sh src/gene/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
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
$ time ./build.sh --genome mm39 --family gene --build-dir "$S/build" --parent-dir "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/codex-p8/build
[build] running 00_fetch_gene_sources.sh
[00_fetch_gene] cache: gencode.vM37.primary_assembly.annotation.gtf.gz
stage_metrics {"stage": "00_fetch_gene_sources.sh", "wall_seconds": 0.81, "peak_rss_bytes": 119689216}
[build] running 10_copy_parent_inputs.sh
stage_metrics {"stage": "10_copy_parent_inputs.sh", "wall_seconds": 0.436, "peak_rss_bytes": 118788096}
[build] running 50_build_exon_subtracted.sh
stage_metrics {"stage": "50_build_exon_subtracted.sh", "wall_seconds": 177.802, "peak_rss_bytes": 874946560}
[build] done
real 442.160 user 454.411 sys 62.370
exit=0
$ cat "$C/tables/exon_subtraction_summary.tsv"
universe_name	records	unchanged	trimmed	split	fully_subtracted	retained_records	blocks	retained_bp	removed_bp	records_on_unannotated_contigs
all_rmsk	5320771	5086684	61378	15495	157214	5163557	5179754	1172003155	29569849	2638
interspersed	3764949	3600721	52703	15406	96119	3668830	3684934	1090369890	26235918	1612
compat_tetranscripts_mm39	3799629	3633401	52842	15399	97987	3701642	3717740	1094973237	26503064	1754
$ cat "$C/BUILD_ID" "$C/CATALOG_ID" "$TE_TRACKS_REFROOT/te_mm39/build/CATALOG_ID"
1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
$ python3 -c "import json;i=json.load(open('$C/MANIFEST.json'))['identity'];print(i['family'],i['parent_build_id'],i['parent_catalog_id'],i['policy_bundle'],i['copied_inputs'],i['gene_annotation']['md5'])"
te_mm39_gene 9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e {'context_capability': 'not_computed', 'exon_mask_policy': 'all_exons_unstranded_union_v1', 'mask_definition': 'The mask unions every exon on both strands, merging overlapping or touching intervals.', 'min_retained_block_bp': 1} {'tables/contig_aliases.tsv': '4c2c18fdfae512f44789831b3eb2b8716e65e80da7fab41208a36e0053ca50c9', 'universes.json': '617feb99e7711f413df3e7935e532abcc12d4ecf7cfbcc4009a6cf31f2cb1b4c'} 702e27a8727db66cd23e9f66f5aa1d38
$ cat "$C/tables/exports.tsv"
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
$ for ns in ucsc ensembl gencode; do for u in interspersed compat_tetranscripts_mm39; do wc -l "$C/exports/$ns/$u/exon_subtracted/"*.saf; done; done
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
$ zcat "$C/tables/export_feature_members.tsv.gz" | tail -n +2 | cut -f1,3 | sort | uniq -c
3717740 compat_tetranscripts_mm39	subfamily
3717740 compat_tetranscripts_mm39	taxonomy_triple
3684934 interspersed	subfamily
3684934 interspersed	taxonomy_triple
$ python3 src/99_verify.py "$C" --parent-dir "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
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
$ python3 src/99_verify.py "$C"; echo "exit=$? (expected 1: parent required)"
verify: child verification requires the parent archive
ok build paths: regular files and directories
ok inventory: 21 files, exact paths, bytes and sha256
ok BUILD_ID: 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
exit=1 (expected 1: parent required)
$ time ./build.sh --genome mm39 --family gene --root "$S/pubroot" --parent-build-id 9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d; echo "exit=$?"
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/codex-p8/pubroot/te_mm39_gene/.staging/build.26gghEbq
[build] running 00_fetch_gene_sources.sh
[00_fetch_gene] cache: gencode.vM37.primary_assembly.annotation.gtf.gz
stage_metrics {"stage": "00_fetch_gene_sources.sh", "wall_seconds": 0.616, "peak_rss_bytes": 119582720}
[build] running 10_copy_parent_inputs.sh
stage_metrics {"stage": "10_copy_parent_inputs.sh", "wall_seconds": 0.408, "peak_rss_bytes": 118775808}
[build] running 50_build_exon_subtracted.sh
stage_metrics {"stage": "50_build_exon_subtracted.sh", "wall_seconds": 177.94, "peak_rss_bytes": 910753792}
installed 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
selected 1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
[build] done
real 535.837 user 548.222 sys 73.125
exit=0
$ python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39_gene; echo "exit=$?"
1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
exit=0
$ python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39; echo "exit=$?"
9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d
exit=0
$ ls "$TE_TRACKS_REFROOT/pubroot/te_mm39_gene/archive"; readlink "$TE_TRACKS_REFROOT/pubroot/te_mm39_gene/current"
1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
archive/1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
$ ./build.sh --genome mm39 --build-dir /workspaces/Meta-Aging/_scratch/te-tracks-audit/codex-p8/core_smoke --help >/dev/null; echo "core usage exit=$?"
core usage exit=0
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
pass  41_export_registration.py  registrations: interspersed=30119592 all_rmsk=5320771; eight interspersed ID spellings; instances=3152636; 24 inventory hashes, feature sets and GTF tuple/instance joins pass; three record grammars; count 7 stays 7 at record, subfamily and family levels
pass  42_exports_fixtures.py  eight hand-authored exports and 46 registration rows; seven-export/40-row interspersed job; membership selection, unresolved ranks, coordinate duplicates, shared instances, deterministic rebuild, universe and identifier gates pass
pass  60_contig_aliases.py  61 injective aliases and FASTA names/lengths; catalog=5320771 interspersed=3764949; all contigs carry catalog records; chr4_JH584295v1_random and chrM carry 2 and 4 catalog records, zero interspersed records
pass  61_namespace_exports.py  24 sorted exports and SHA-256 digests; 16 complete renamed files regenerated; interspersed=3764949 all_rmsk=5320771 per namespace; registrations=30119592+5320771
pass  62_preflight.sh  85 preflight cases; both universes, three namespaces, BED/GTF/SAF and sizes/FAI/BAM; covered=0, export-only=2, empty/shared-length/input errors=1; exact reports and enclosing build aliases pass
pass  70_manifest_identity.py  BUILD_ID=9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d CATALOG_ID=90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e; 43 payloads; identity mutations pass
pass  71_verify_build.py  real build verifies unchanged; fixture stray authoring payload, flipped byte, extra file, unpublished taxonomy rule and export roster mismatch fail with named discrepancies; fixture cases=2.573s
pass  72_publication_cases.py  identical and changed builds, export-roster evolution (4 archives), failed verification, concurrent installs/selects (5 archives), old IDs, forged ID, corrupt current, selector and root cases, occupied targets, symlinks and 0444/0555 modes pass
pass  80_exon_subtraction.py  5320771 records conserve bases; registered blocks ordered, disjoint and contained; 200000-record sample exon-disjoint; summary census, 14805348 registrations, 12 SAFs and coverage 38/61 with 2638 unannotated records pass
pass  81_exon_subtraction_fixtures.py  12 geometry cases, 12 SAFs, 64 registrations, annotation coverage, duplicate invariance and named refusals pass
pass  82_child_identity.py  child identity fields, inherited pins, all policy/GTF/roster/parent mutations, dependency and payload refusals, CLI usage gates pass
pass  83_child_publication_cases.sh  child install/select/verify-current require present, verified parent; repeated publication converges; archive resolution, preserved selection, immutable modes and earlier core selection pass
checks=23 pass=23 fail=0 unsupported=0
exit=0
```
Independent audit: gzip GTF rows normalized with the copied alias table, exon BED sorted then merged/subtracted unstranded with bedtools; SAF tuples compared as multisets including name, bounds and strand. Status rows joined by record ID to parent parquet and summarized with independently evaluated raw-class predicates; coverage checked from GTF rows and the bedtools union. Independent JSON/SHA-256 mutations covered both GTF digests, all four policy values, roster, both parent IDs and child_universes.
```text
$ python3 "$S/independent.py"
bedtools v2.31.1
GTF independent coverage: genes=78317 transcripts=278369 exons=1298921 union_bp=160549642 annotated=38/61
chr18: exon_union_intervals=9708 exon_union_bp=4528733 records=118502 blocks=116425 retained_bp=34253394 exact_block_multiset_equal=True
chr1_MU069434v1_random: exon_union_intervals=0 exon_union_bp=0 records=4 blocks=4 retained_bp=385 exact_block_multiset_equal=True
all_rmsk independent_summary={"blocks": 5179754, "fully_subtracted": 157214, "records": 5320771, "records_on_unannotated_contigs": 2638, "removed_bp": 29569849, "retained_bp": 1172003155, "retained_records": 5163557, "split": 15495, "trimmed": 61378, "unchanged": 5086684}
interspersed independent_summary={"blocks": 3684934, "fully_subtracted": 96119, "records": 3764949, "records_on_unannotated_contigs": 1612, "removed_bp": 26235918, "retained_bp": 1090369890, "retained_records": 3668830, "split": 15406, "trimmed": 52703, "unchanged": 3600721}
compat_tetranscripts_mm39 independent_summary={"blocks": 3717740, "fully_subtracted": 97987, "records": 3799629, "records_on_unannotated_contigs": 1754, "removed_bp": 26503064, "retained_bp": 1094973237, "retained_records": 3701642, "split": 15399, "trimmed": 52842, "unchanged": 3633401}
identity independent encoder: 10 mutations move BUILD_ID only; parent/child CATALOG_ID bytes equal
provenance stage_metrics and peak_rss_measurement: outside both hashes; inventory_files=21
published child: payload=0444 directories=0555 relative current=archive/1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b staging_empty=True
$ python3 "$S/verify_purity.py"
99_verify.py and release verify-current: all four input trees retain size, mtime and mode; identity-document bytes unchanged; paths=216
```

## Scope check

`git status --short` at acceptance: nine modified files and twelve untracked entries before writing this review; the 25 implementation files are all on the touch list. Two additional entries, `docs/_internal/redesign-2026-09/prompts/p8_review.md` and `p8_opus.md`, are review prompts outside that list, so the supplied ten-entry count is stale. `git diff HEAD --stat`: 9 files changed, 386 insertions(+), 44 deletions(-). HEAD remains `cf1b150`, branch `redesign-2026-09`. A third internal file, `docs/_internal/redesign-2026-09/consults/unified_te_schema_consult.md`, appeared after the initial file-hash snapshot; it is concurrent work outside the implementation touch list. All 14 git checkouts under `.ref` report clean; the two named plain directories were left alone.
Only this review was written in the repository; initial repository-file hashes remain unchanged. Reviewer scratch and the suite-created empty p8impl directory were removed with Python shutil. No installs, network or git write commands.
