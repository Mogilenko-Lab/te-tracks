# Phase 7 review (codex gpt-6-astra)
Verdict: BLOCKING

## Blocking

- [B1] `src/lib/manifest.py:156`, `src/lib/manifest.py:347`, `src/release.py:129`: historical verification depends on the running builder's current export roster and taxonomy version. A genuine added-export build verifies and preserves CATALOG_ID, then `install --select` rejects the healthy old current archive because it lacks the newly expected paths. My tiny-build probe added `record_extra.bed` in all three namespaces, updated the inventory and job registry, and reproduced `tables/exports.tsv: export roster differs`; changing the verifier's taxonomy version likewise rejects the old build as `unsupported taxonomy_rule_version`. Check 72 at lines 74–78 only adds `additional.txt` (`tests/fixtures/publication/build_fixture.py:92`), so it misses the phase contract's new-export case. — Dispatch verification using the archived contract/version, retain support for published versions, and exercise genuine export addition followed by selection and old-ID verification.
- [B2] `docs/RELEASES.md:145`: the supplied namespace figures differ from the measured files: ucsc **3,021,714,346** (+508), ensembl **2,926,266,953** (−1,606), gencode **3,021,140,740** (+2,441) bytes. Registration matches **347,526,106**. The 43-file payload is **10,461,884,289** bytes; **10,461,962,113** includes **77,824** bytes of directory entries. — Resolve the contract's numeric discrepancy explicitly; publish the observed namespace sums and payload sum, with directory/storage overhead identified separately. The phase contract's “318 MB per namespace” is also approximate and uneven: `all_rmsk/full/record.bed` is 332,554,184 / 316,524,255 / 332,461,688 bytes. The implementer's deviation report correctly preserved the supplied targets pending a ruling; the namespace targets remain inaccurate as public measured sizes.

## Advisory

- [A1] `tests/checks/core/71_verify_build.py:30`: reflinks fail with `Operation not supported` on this ext4 filesystem. An identical `cp -a --reflink=auto` of the real build took **33.602 s**, physically copying about 10.46 GB; the two failed verification attempts each scan that payload again. — Keep the real-build verification and metadata comparison, then use a tiny publication fixture with a flipped byte and an extra file. This proves both named rejection paths with kilobytes of disposable data.
- [A2] `src/release.py:122`, `src/release.py:129`, `src/release.py:131`: convergent `install --select` verifies staging, current and the existing archive separately, even when the latter two resolve to the same directory. This satisfies the contract; it costs three complete payload reads (31.39 GB), plus record checks. A standalone real verification measured **26.508 s** here. — Reuse a successful archive verification within the same held lock when the exact target and ID coincide; retain staging verification and corruption detection.
- [A3] `src/lib/manifest.py:36`, `src/lib/manifest.py:159`, `src/lib/manifest.py:340`: the verifier is a core-mm39 implementation: fixed species admission, core family, null parents, three namespaces and `full` exports. Public mm39/hg38 scope appears in `README.md:153` and `docs/DECISIONS.md:99`, but the requirement to extend the SPECIES table when adding a config is implicit. Predicate schema **1** is explicit in `docs/OUTPUTS.md:76`; it is not a silent assumption. — Phase 8 needs family-specific identity/verification and parent dependency validation while preserving historical core verification.
- [A4] `src/lib/build_exports.py:37`: `14761 ATAC` has no consumer check; it is copied into both universes' record-BED contracts although `docs/OUTPUTS.md:482` names the `all_rmsk` route. Core checks 41/61 establish its export and registration, not downstream ingestion. — Bind consumer declarations to the applicable job and add a route fixture when claiming downstream support. All other named consumers have checks; featureCounts execution is presently unsupported. These checks assert reader keys independently but do not compare them to EXPORT_CONTRACTS; a direct comparison would catch future metadata drift.
- [A5] `docs/RELEASES.md:144`, `docs/RELEASES.md:150`: “supplied retention baseline” and “phase 6 fix verification” carry implementation provenance into public prose. `docs/DECISIONS.md:68` now has five sentences against the two-to-four rule at line 81. Existing `README.md:48`, `README.md:153` and `docs/DECISIONS.md:89` retain phase/history statements that lag delivered artifacts. — State the measured release properties directly, shorten entry 7 and schedule existing prose cleanup. New code comments/docstrings and the publication fixture README contain no gratuitous contrastive negation or review-history chatter; the verifier's no-write wording states its contract.
- [A6] `tests/checks/core/72_publication_cases.py:64`: the changed-policy case changes a note, and the concurrency cases have no synchronization barrier. Check 72 also leaves the ADR67 consult's interrupted-transfer, reader-during-swap, disk-full/rename/selector-permission, cross-filesystem and consumer ACL-access cases unexercised. — Add focused failure injection and host filesystem qualification; the implemented phase smoke checks are fallible, but their coverage should retain these limits.

Identity and deliverables: all requested implementation, documentation and fixture paths exist. My recursive JSON encoder independently reproduced both full IDs below; all 43 inventory paths, sizes and SHA-256 values match both the build and installed archive. Their `identity` objects are equal. Only provenance keys `built_at`, `invocation_argv`, `peak_rss_bytes` and `peak_rss_measurement` differ. Provenance records Python 3.11.15, pandas 2.2.3, pyarrow 25.0.0, zlib 1.2.11, Ubuntu 22.04.5 and image evidence `/etc/cloud/build.info` serial 20260627; image digest availability is explicitly limited (`src/lib/manifest.py:222`). Reader settings, byte profile, ledger key and both deferrals are present (`docs/OUTPUTS.md:125`, `docs/DECISIONS.md:70`, `docs/DECISIONS.md:98`). Legacy publication machinery is absent from the current scripts/runbook.

Consumer semantics: no emitted feature key was misstated in the exercised readers. BED name sources/levels agree with consumer check 10:17 and check 16:20; SAF GeneIDs agree with check 16:35 and `tests/lib/consumers.py:519`. GTF source mappings agree with `src/lib/build_exports.py:276`; record/subfamily four-tuples agree with checks 12:64 and 13:35, TEtranscripts triples with 13:39, and Stellarscope locus/instance keys with 11:25–44. The four-tuple, triple, record, subfamily, family and instance selectable levels agree with `tests/lib/consumers.py:173`. Stellarscope's boundary defect and absent executables remain explicitly unsupported.

Publication coverage (`tests/checks/core/72_publication_cases.py`): identical convergence/first manifest 59–63; changed payload/second archive 64–69; failed verification retains staging/current 70–73; added payload/unchanged catalog 74–78; concurrent identical installs 79–89; corrupt existing archive 90–98; forged ID 99–103; corrupt current 104–111; empty/symlink targets 112–123; payload symlink/unreadable directory 124–136; concurrent different selections 137–140; dangling/escaping current 142–146; 2775/0444/0555 modes and retained old ID 149–154. Installed disk modes also match independently: 46 files at 0444, 19 directories at 0555, archive parent 2775.

Publication behavior: `lexists` detects dangling current, so selection aborts naming its missing archive and preserves the link (`src/release.py:87`, `src/release.py:128`); my probe returned exit 1. A staging path outside the required direct `.staging` parent fails at line 118; a different-device staging mount fails at line 135 before a new installation. Existing identical archives can converge across devices because that branch removes staging without renaming. Staging verification runs before the lock; a competing holder makes the publisher wait at line 47, then current/destination are checked under the acquired lock. My held-lock probe confirmed waiting and successful continuation. Exclusive ownership of staging is public at `docs/RELEASES.md:106`. The writable root during cross-parent rename is a POSIX-permitted directory-write check implemented by Linux, not an ext4-specific defect: my 0555 probe failed EACCES and 0755 succeeded. Final 0555 is set before selection at `src/release.py:140`; this reported ordering deviation is justified by the permission requirement.

Build/verifier: `build.sh:6` captures the original argv in TE_TRACKS_INVOCATION; the installed manifest contains the actual `./build.sh --genome mm39 --root ...` invocation. Lines 70–86 measure stage 30 alone, as labeled in provenance (installed peak **5,968,367,616 bytes**); stage 35 has no RSS measurement here. Simultaneous `--root`/`--build-dir` returned 2, and an archive-contained `--build-dir` returned 1 before creating it. The standalone verifier preserved all **65** entries' sizes and nanosecond mtimes, including the root. Core checks 40–62 are unchanged; their results appear below.

## Acceptance re-run

All Python processes inherited `PYTHONDONTWRITEBYTECODE=1`; scratch and TMPDIR were under the review directory. The real build and published root were read-only. The manifest command ran on a full independent copy. The destructive original pubroot reset and two full builds were omitted under this review's read-only/optional-rebuild instruction; manifest regeneration, installed identity and hashes, and the tiny publication smoke cases were independently checked; stage-by-stage rebuild reproducibility was not re-run.

```text
$ export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
$ export REVIEW_SCRATCH=/workspaces/Meta-Aging/_scratch/te-tracks-audit/codex-p7
$ export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 TMPDIR="$REVIEW_SCRATCH/tmp"
$ export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
$ for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok src/10_build_records.sh
syntax ok src/15_build_universes.sh
syntax ok src/20_build_taxonomy.sh
syntax ok src/30_build_exports.sh
syntax ok src/35_build_namespaces.sh
syntax ok tests/run.sh
$ python3 -c "import json;m=json.load(open('$TE_TRACKS_REFROOT/te_mm39/build/MANIFEST.json'));print(sorted(m));print(sorted(m['identity']));print(len(m['identity']['inventory']))"
['identity', 'provenance']
['assembly', 'catalog', 'contig_set_sha256', 'declared_assembly', 'export_contracts', 'family', 'inventory', 'parent_build_id', 'parent_catalog_id', 'schema_version', 'species', 'taxonomy_rule_version', 'universes']
43
$ time cp -a --reflink=auto "$TE_TRACKS_REFROOT/te_mm39/build" "$REVIEW_SCRATCH/buildcopy"; echo "copy_exit=$?"

real	0m33.602s
user	0m0.021s
sys	0m7.097s
copy_exit=0
$ python3 src/90_manifest.py "$REVIEW_SCRATCH/buildcopy" config/mm39.env; echo "manifest_exit=$?"; cat "$REVIEW_SCRATCH/buildcopy/BUILD_ID" "$REVIEW_SCRATCH/buildcopy/CATALOG_ID"
manifest_exit=0
d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
9a42ec53135a203c4b458b0c7e77584917db1cc205fe2b7ae1932dd1f491340b
$ python3 src/99_verify.py "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
ok build paths: regular files and directories
ok inventory: 43 files, exact paths, bytes and sha256
ok BUILD_ID: d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
ok CATALOG_ID: 9a42ec53135a203c4b458b0c7e77584917db1cc205fe2b7ae1932dd1f491340b
ok catalog, source_run scope, assembly, contig digest and taxonomy rule
ok universe definitions and predicate grammar
ok export contracts: 24 namespace paths
ok export rows and sha256: exports/ensembl/all_rmsk/full/record.bed
ok export rows and sha256: exports/ensembl/interspersed/full/family.bed
ok export rows and sha256: exports/ensembl/interspersed/full/record.bed
ok export rows and sha256: exports/ensembl/interspersed/full/record.gtf
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.bed
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.saf
ok export rows and sha256: exports/ensembl/interspersed/full/taxonomy_triple.saf
ok export rows and sha256: exports/gencode/all_rmsk/full/record.bed
ok export rows and sha256: exports/gencode/interspersed/full/family.bed
ok export rows and sha256: exports/gencode/interspersed/full/record.bed
ok export rows and sha256: exports/gencode/interspersed/full/record.gtf
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.bed
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.saf
ok export rows and sha256: exports/gencode/interspersed/full/taxonomy_triple.saf
ok export rows and sha256: exports/ucsc/all_rmsk/full/record.bed
ok export rows and sha256: exports/ucsc/interspersed/full/family.bed
ok export rows and sha256: exports/ucsc/interspersed/full/record.bed
ok export rows and sha256: exports/ucsc/interspersed/full/record.gtf
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.bed
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.saf
ok export rows and sha256: exports/ucsc/interspersed/full/taxonomy_triple.saf
ok records schema: 24 required typed columns
ok record identities: 5320771 unique keys and text instance ids
ok record bounds: source/mm39.chrom.sizes
ok universe_summary all_rmsk: 5320771 records
verified d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
exit=0
$ ls -la "$TE_TRACKS_REFROOT/pubroot/te_mm39/" "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive/"
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/:
total 20
drwxrwsr-x+ 4 devuser devgroup 4096 Sep 16 18:42 .
drwxrwsr-x+ 3 devuser devgroup 4096 Sep 16 18:31 ..
drwxrwsr-x+ 3 devuser devgroup 4096 Sep 16 18:42 archive
lrwxrwxrwx  1 devuser devgroup   72 Sep 16 18:42 current -> archive/d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
drwxrwsr-x+ 2 devuser devgroup 4096 Sep 16 18:54 .staging

/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive/:
total 12
drwxrwsr-x+ 3 devuser devgroup 4096 Sep 16 18:42 .
drwxrwsr-x+ 4 devuser devgroup 4096 Sep 16 18:42 ..
dr-xr-xr-x+ 5 devuser devgroup 4096 Sep 16 18:41 d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
$ readlink "$TE_TRACKS_REFROOT/pubroot/te_mm39/current"; cat "$TE_TRACKS_REFROOT/pubroot/te_mm39/current/BUILD_ID"
archive/d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
$ diff <(cat "$TE_TRACKS_REFROOT/te_mm39/build/BUILD_ID") <(cat "$TE_TRACKS_REFROOT/pubroot/te_mm39/current/BUILD_ID") && echo "same id from both modes"
same id from both modes
$ ls "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive/" | wc -l
1
$ python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39; echo "exit=$?"
d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
exit=0
```

The review reference root points its `te_mm39` parent to the read-only real build; check scratch directories remain under `$REVIEW_SCRATCH/refroot`.

```text
$ time tests/run.sh core --refroot "$REVIEW_SCRATCH/refroot"; echo "exit=$?"
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
pass  62_preflight.sh  82 preflight cases; both universes, three namespaces, BED/GTF/SAF and sizes/FAI/BAM; covered=0, export-only=2, empty/shared-length/input errors=1; exact reports and nearest alias paths pass
pass  70_manifest_identity.py  BUILD_ID=d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9 CATALOG_ID=9a42ec53135a203c4b458b0c7e77584917db1cc205fe2b7ae1932dd1f491340b; 43 payloads; identity mutations pass
pass  71_verify_build.py  real build verifies unchanged; flipped byte and extra file fail with their paths
pass  72_publication_cases.py  identical and changed builds, failed verification, added payload, concurrent installs/selects, old IDs, forged ID, corrupt current, occupied targets, symlinks and 0444/0555 modes pass
checks=19 pass=19 fail=0 unsupported=0

real	15m31.630s
user	14m30.167s
sys	5m5.814s
exit=0
$ tests/run.sh consumers --refroot "$REVIEW_SCRATCH/refroot"; echo "exit=$?"
pass  00_tool_inventory.required.py  supported tool_inventory reporting-only; irescue=absent; featureCounts=absent; stellarscope=absent; TEsingle=absent; TEcount=absent; TElocal=absent; bedtools=bedtools v2.31.1; samtools=samtools 1.21
pass  10_irescue_parser.required.py  supported irescue 1.2.0 (v1.2.0-20-g26f36fb) checkout parser; record=11, subfamily=8; comma splits one name and exporter rejects it
unsupported  11_stellarscope_parser.py  unsupported: stellarscope right-boundary overlap defect, observed 0,1,1,1 expected 0,1,1,0; stellarscope 1.5 (1.5) checkout parser
pass  12_tesingle_parser.required.py  supported TEsingle 1.0 (1.0-8-g655f127) checkout parser; record=11, subfamily=8; 999 distinct UR dropped, 1000 kept; duplicate/QC-fail reads skipped
pass  13_tetranscripts_telocal_parser.required.py  supported TEtranscripts/TElocal 2.2.4 (2.2.4-13-ge7f9b93)/1.1.3 (1.1.3-4-g1a168c2) checkout parsers; TEtranscripts=8 groups; TElocal locInd record=11, subfamily=8
pass  14_mates_parser.required.py  supported MATES 0.1.8 (v0.1.8-9-g87c1218) checkout adapter; eight-column pair; underscore stem; ?/Unknown model groups dropped
unsupported  15_irescue_chrcat.py  unsupported: irescue system tool gawk absent; irescue 1.2.0 (v1.2.0-20-g26f36fb) checkout chrcat
pass  16_family_triple_readers.required.py  supported family/triple readers bedtools v2.31.1; Python SAF column reader; family buckets and 8 SAF GeneIDs registered; three TwoLab rows share one triple
unsupported  20_irescue_exec.sh  unsupported: irescue absent
unsupported  21_featurecounts_exec.sh  unsupported: featureCounts absent
pass  22_bedtools_exec.required.sh  supported bedtools v2.31.1; duplicate names, half-open boundaries and -s/-S pass
pass  23_samtools_fixture_integrity.required.sh  supported samtools 1.21; 11 sorted, indexed BAMs; ARC=13 OCM=26 bulk=26 alignments, 11 molecules each; tagged main UB=11 UR=12; reverse strands and duplicate/QC-fail flags pass
unsupported  30_registration_duckdb.py  unsupported: python module duckdb absent
checks=13 pass=8 fail=0 unsupported=5
exit=0
```

Scratch-only probes used two tiny fixture builds, an added export/job registry, a taxonomy-version change and a directory permission test (`$PROBE` is the disposable publication root):

```text
real added-export candidate verifies; BUILD_ID changed=True CATALOG_ID unchanged=True
added-export install --select: archive $PROBE/te_mm39/archive/a926832f1317fe0ee7932d31baefd6b9c0c7cc9215c936ef64b4252d51414f2b: tables/exports.tsv: export roster differs: ['exports/ensembl/all_rmsk/full/record_extra.bed', 'exports/gencode/all_rmsk/full/record_extra.bed', 'exports/ucsc/all_rmsk/full/record_extra.bed']
old selector retained=True candidate staging retained=True
historical taxonomy v1 under v2 verifier: unsupported taxonomy_rule_version
cross-parent rename of 0555 directory: errno=13 Permission denied
cross-parent rename of 0755 directory: passed
```

## Scope check

HEAD is `99bf646`, branch `redesign-2026-09`. `git diff HEAD --stat`: **9 files changed, 319 insertions(+), 80 deletions(-)**. Six tracked phase files are within the allowed set; the three tracked orchestrator edits (`session.md`, `02_orchestration.md`, `prompts/p7_impl.md`) are excluded. New deliverables: `src/{90_manifest.py,99_verify.py,release.py,lib/manifest.py}`, `tests/checks/core/{70_manifest_identity.py,71_verify_build.py,72_publication_cases.py}` and `tests/fixtures/publication/{build_fixture.py,README.md}`. No deletions. Existing untracked `prompts/p7_opus.md` and `prompts/p7_review.md` predated this review; `consults/gene_context_material.md` and `reviews/p7_rulings.md` appeared concurrently and are outside this review.

`docs/DECISIONS.md` entry 7 exceeds the narrow touch-list parenthesis. I hold the explicit manifest-contract instruction and milestone 5 M1 ruling binding: they specifically require both identities and the ledger key in entry 7, so this is an authorized conflict resolution. No other implementer scope deviation found. `src/lib/build_exports.py` only adds the shared contracts and derives the existing roster from them. No edits to checks 40–62.

This review writes only `docs/_internal/redesign-2026-09/reviews/p7_codex.md`; scratch is removed on completion. No git writes, installs or network calls. The `.ref` repositories report clean status.
