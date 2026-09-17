# te-tracks phase 9a review (codex, read-only)

You are an independent reviewer of phase 9a of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p9a_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/19_phase9_acceptance_park.md`
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
  bite phase 9b.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 9a review (codex gpt-6-astra)
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


## Phase 9a specifics

The contract is plan 19's section "Phase 9a: core additions before acceptance" and the implementer prompt
`docs/_internal/redesign-2026-09/prompts/p9a_impl.md`. The build under review is the scratch reference root
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`; export
`TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`,
`TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source` and
`PYTHONDONTWRITEBYTECODE=1`. Do not rebuild and do not publish; the builds are the reviewed artifact. `/tmp`
is noexec, so put any scratch under `_scratch/te-tracks-audit/p9a-review/` and remove it with Python
`shutil.rmtree` when you finish.

Judge these eleven points, each with its own recomputation rather than a reading of a check's output.

1. **The record profile.** Each of `exports/{ucsc,ensembl,gencode}/interspersed/full/record_starsolo.gtf`
   holds 3,764,949 data rows and 3,764,949 distinct `gene_id` values over 59 contigs, every feature `exon`,
   and exactly the twelve attributes in this order: `gene_id`, `transcript_id`, `gene_name`, `gene_type`,
   `locus`, `rmsk_name`, `family_id`, `class_id`, `rmsk_family`, `rmsk_class`, `instance_id`,
   `rmsk_record_id`. `gene_id`, `transcript_id` and `locus` equal the record alias; `gene_name` equals
   `rmsk_name`; `gene_type` is `transposable_element`. Sizes are 1,616,329,134, 1,604,983,782 and
   1,616,260,404 bytes. Check that the rows equal the registration for the profile as a multiset and that
   coordinates round-trip to the catalog, and say whether anything in the file could disagree with
   `rmsk_records.parquet` without a check failing.
2. **The Dfam view.** `tables/taxonomy_dfam.tsv` has 1,221 lines. Recompute the strict part rule yourself
   from `data/dfam/dfam_interspersed_mm39_snapshot.json.gz` and the catalog, and compare per name, not only
   in aggregate: 1,047 `exact`, 147 `part_model_set`, 26 `missing`; records 2,797,852, 928,528 and 38,569;
   part sets with three, two and one models 30, 9 and 108; six L2/CR1 sets; 1,263 model rows; 300
   classification nodes with 193 carrying a Wicker code; 9 multi-clade models; 33 primate-branch models over
   31 names; of the exact names 884 take a Wicker code at the leaf, 110 inherit and 53 are `missing` at every
   rank. Companion tables: `taxonomy_dfam_models.tsv` 1,264 lines, `dfam_lineage_nodes.tsv` 301 lines,
   `dfam_model_clades.tsv` 1,279 lines. Verify the companions join losslessly to the one-row-per-name view in
   both directions, and that `model_length_sum_bp` is never used as a full-length denominator anywhere in
   code or docs.
3. **The tracked source role.** `data/dfam/` holds the snapshot, its provenance and its fetch script, tracked
   past the `*.gz` ignore rule by `!data/dfam/**`. The snapshot's sha256 is
   `ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f`; confirm the config pin matches the
   bytes, that the build retains a copy under `source/`, and that `dfam_snapshot` appears in
   `identity.build_sources` while `identity.catalog.sources` stays `['rmsk_out']`, which is what keeps
   `CATALOG_ID` fixed.
4. **Identity movement.** New core `BUILD_ID`
   `763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c`, child `BUILD_ID`
   `693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0`, `CATALOG_ID`
   `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` in both core and child. The new core
   declares 51 inventory entries and 27 export contracts; the phase-8 archive declares 43 and 24 and must
   still verify. Run `python3 src/99_verify.py <pubroot>/te_mm39/archive/9ddf3622...` and
   `python3 src/release.py verify-current --root <pubroot> --family te_mm39_gene` and quote the exits.
5. **Backward admission.** The phase-8 archive declares three `build_sources` roles and the new one declares
   five. Read the verifier branch that admits both and say whether it admits an archive it should refuse,
   naming the input that would slip through.
6. **The binding fixture.** `43_matrix_binding.py` must demonstrate that a join on `(feature_level,
   key_grammar)` alone doubles and the four-field join does not: 1,000 shared records giving 2,000 rows and
   1,001,000 counts against 1,000 rows and 500,500 counts. Confirm the OUTPUTS sentence now reads
   `(universe_name, variant, feature_level, key_grammar)` and that no other place in the docs still binds on
   the pair.
7. **Records, instances and insertions.** The OUTPUTS section must state what a record, an instance and an
   insertion are, that per-locus counts are per record, and the annotation's limits, carrying 445,649
   multi-record instances and 722,280 LTR-only instances under `all_rmsk`, 30,569 mixed-name and 23,244
   mixed-strand instances and 8.07% overlapping records under the stated scopes, 588 L1 records at model base
   1, and `rmsk_overlap_flag` constant false. Every number must name its scope; flag any that does not.
8. **The IRescue rewrite.** `tests/lib/consumers.py` must assert identity joins, roster and molecule
   conservation and unique molecules landing on their feature, and record the ambiguous allocation without
   asserting it. Observed values are 5.5 and 3.5 for the 4/2/3 fixture and 4.5 and 4.5 for the 3/3 fixture.
   Confirm the check still fails if identity or conservation breaks; show how you established that.
9. **The new execution gates.** `24_starsolo_exec.sh` and `25_cellranger_mkref.sh` must report unsupported
   without their binaries and assert identities, support and conservation rather than allocation when the
   binaries are present. Observed allocations are 1.5 and 1.5 for `Gene` and 2.98266 and 0.0173415 for
   `GeneFull`. `17_starsolo_profile.required.py` is a parser check and must be required.
10. **Suites.** The orchestrator re-ran both suites from the frozen tree: core 26 of 26, and with the shims
    on PATH 16 consumer checks with 15 passing and Stellarscope unsupported. Re-run them and report any
    difference. Activation is
    `source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh`.
11. **Deviations to judge.** The implementer reported these; rule on each with evidence.
    D1 every Wicker rank is `missing` for the 53 exact `Unknown` names, following plan 19 rather than the
    prompt's general leaf-family rule.
    D2 the phase-8 archive declares three source roles and the new one five, and the earlier archive still
    verifies.
    D3 the fetch census totals 3,760,582 records against the catalog's 3,764,949, short by 4,367 across the 20
    multi-label names; the builder takes record weights from the catalog and leaves the fetch artifact as
    fetched.
    D4 the plan's instance figures are reported under explicit scopes, `all_rmsk` for some and `interspersed`
    for others.
    D5 `17_starsolo_profile.required.py` was required by a deliverable and missing from the enumerated touch
    list, and was added.
    D6 `src/lib/contigs.py:134` still says "eight UCSC inventory entries" in its missing-roster error while
    the effective roster holds nine files; the file sits outside the touch list.
    D7 a live edit to `tests/run.sh` during an intermediate run produced `line 103: one: command not found`
    and `exit=127`; the frozen run passed 26 of 26 and the orchestrator's independent re-run agrees.
    D8 `cellranger mkref` needs `--memgb=3`; a 2 GB attempt is refused.

The working tree holds 38 `git status --short` entries plus three files under `data/`, so 40 files created or
changed. Name anything touched beyond plan 19's scope for phase 9a.

## Implementer report

Implemented and published phase 9a in the scratch reference root. The final core run passed **26/26 checks**. With consumer shims active, **15 checks passed and Stellarscope remained unsupported**. Both archive families contain their previous and new builds, with `current` selecting the new builds. The child summary is unchanged. `p9a/` was removed with `shutil`.

- Core `BUILD_ID`: `763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c`
- Child `BUILD_ID`: `693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0`
- Unchanged `CATALOG_ID`: `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e`

The measured new payload files are:

| File | Bytes |
|---|---:|
| `exports/ucsc/interspersed/full/record_starsolo.gtf` | 1,616,329,134 |
| `exports/ensembl/interspersed/full/record_starsolo.gtf` | 1,604,983,782 |
| `exports/gencode/interspersed/full/record_starsolo.gtf` | 1,616,260,404 |
| `tables/taxonomy_dfam.tsv` | 777,844 |
| `tables/taxonomy_dfam_models.tsv` | 577,712 |
| `tables/dfam_lineage_nodes.tsv` | 75,154 |
| `tables/dfam_model_clades.tsv` | 367,180 |
| `source/dfam_interspersed_mm39_snapshot.json.gz` | 278,952 |
| **Complete 51-file payload** | **15,301,535,164** |
| **Scratch build, `du -sb`** | **15,301,655,992** |

Each new GTF has **3,764,949 rows and distinct gene IDs across 59 contigs**. Their sizes match the consult’s estimates.

| Operation | Wall seconds | Peak resident bytes |
|---|---:|---:|
| Core scratch rebuild | 717.201 | 9,026,424,832 |
| Core publication | 775.159 | 9,026,469,888 |
| Child scratch rebuild | 553.292 | 3,573,747,712 |
| Child publication | 908.313 | 3,813,830,656 |
| New core verifier | 35.719 | 2,391,437,312 |
| Earlier core verifier | 28.658 | 2,347,425,792 |
| Child `verify-current`, including parent | 171.060 | 3,481,579,520 |

RSS was recorded with `resource.getrusage`; build logs also retain shell `time` output. Core stage 30 peaked at **5,994,254,336 bytes**. Child subtraction took **155.333 seconds**, peaking at **889,823,232 bytes**.

The record measurements match the plan with explicit scopes:

| Measurement | Scope | Plan | Observed |
|---|---|---:|---:|
| Multi-record instances | `all_rmsk` | 445,649 | 445,649 |
| Mixed-name instances | `interspersed` | 30,569 | 30,569 |
| Mixed-strand instances | `interspersed` | 23,244 | 23,244 |
| Records overlapping another record | `all_rmsk`, either strand | 8.07% | 429,440 / 5,320,771 = 8.07101076% |
| LTR-only instance screen | LTR annotations | 722,280 | 722,280 |
| L1 records at model base 1 | Raw LINE/L1 | 588 | 588 |
| `rmsk_overlap_flag` | `all_rmsk` | Constant false | 0 true |

For comparison, `interspersed` has **434,707** multi-record instances and **10.48579941%** overlapping records. Across `all_rmsk`, mixed-name and mixed-strand counts are **30,699** and **23,245**.

The Dfam census matches plan 19:

| Measurement | Plan | Observed |
|---|---:|---:|
| Names: exact / parts / missing | 1,047 / 147 / 26 | 1,047 / 147 / 26 |
| Records: exact / parts / missing | 2,797,852 / 928,528 / 38,569 | 2,797,852 / 928,528 / 38,569 |
| Part sets with 3 / 2 / 1 models | 30 / 9 / 108 | 30 / 9 / 108 |
| L2/CR1 part sets | 6 | 6 |
| Model rows | 1,263 | 1,263 |
| Lineage nodes / coded nodes | 300 / 193 | 300 / 193 |
| Multi-clade models | 9 | 9 |
| Primate-branch models / names | 33 / 31 | 33 / 31 |
| Exact Wicker codes: mapped / inherited / missing | 884 / 110 / 53 | 884 / 110 / 53 |

STAR 2.7.11b preserved all fixture record genes, separated same-name records, gave zero TE support to the gap molecule, and conserved ambiguous-molecule support through EM. Observed host/TE overlap allocations were **1.5/1.5 for Gene** and **2.98266/0.0173415 for GeneFull**; allocation values are recorded, while assertions check identities, support and conservation. Cellranger 10.1.0 retained all **11 TE alias genes plus the host gene** and produced its STAR index with `--memgb=3`. IRescue observed **5.5/3.5** and **4.5/4.5** for both alignment representations.

Deviations and corrections:

- Plan 19 requires every Wicker rank to be `missing` for the 53 exact `Unknown` names. This differs from the prompt’s general leaf-family rule; the implementation follows the plan.
- The earlier archive has three `build_sources` roles, with `rmsk_out` in `catalog.sources`. New builds declare all four fetched roles plus `dfam_snapshot`; the earlier archive still verifies.
- The fetch census totals 3,760,582 records, **4,367 fewer** than catalog counts across the 20 multi-label names. The builder uses catalog weights; the fetch artifact remains unchanged.
- The plan’s instance figures use the scopes shown above.
- `17_starsolo_profile.required.py` was explicitly required by deliverable 2 but omitted from the enumerated touch list. It was added.
- The unchanged [contigs.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/lib/contigs.py:134) retains “eight UCSC inventory entries” in its missing-roster error. Its effective roster correctly contains nine files and passes the namespace checks. That file is outside the touch list.
- Without activation, bedtools and samtools remain available. IRescue, featureCounts, STAR and cellranger report absence. Stellarscope reports its existing boundary defect.
- The first ordered core run failed `82_child_identity.py` because the child still pinned the previous core. Rebuilding the child resolved it.
- I edited runner usage while an intermediate core run was active. All 26 individual checks passed, but the live edit disrupted the shell’s final summary:
  
```text
tests/run.sh: line 103: one: command not found
exit=127
```

The subsequent frozen-file run passed all 26 checks with exit 0. Cellranger’s preliminary 2 GB attempt also exposed its 3 GB minimum; the completed gate uses 3 GB.

The final Git status below lists the changed files. Its `data/` entry contains these three new files, giving **40 changed or created files total**:

- [dfam_interspersed_mm39_snapshot.json.gz](/workspaces/Meta-Aging/01_modules/te-tracks/data/dfam/dfam_interspersed_mm39_snapshot.json.gz)
- [dfam_interspersed_mm39_snapshot.provenance.json](/workspaces/Meta-Aging/01_modules/te-tracks/data/dfam/dfam_interspersed_mm39_snapshot.provenance.json)
- [fetch_dfam_snapshot.py](/workspaces/Meta-Aging/01_modules/te-tracks/data/dfam/fetch_dfam_snapshot.py)

Requested command outputs and the clean final core run follow verbatim.

Shell syntax and snapshot SHA:

```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok src/10_build_records.sh
syntax ok src/15_build_universes.sh
syntax ok src/20_build_taxonomy.sh
syntax ok src/25_build_dfam.sh
syntax ok src/30_build_exports.sh
syntax ok src/35_build_namespaces.sh
syntax ok src/gene/00_fetch_gene_sources.sh
syntax ok src/gene/10_copy_parent_inputs.sh
syntax ok src/gene/50_build_exon_subtracted.sh
syntax ok tests/run.sh
syntax ok tests/checks/consumers/20_irescue_exec.sh
syntax ok tests/checks/consumers/21_featurecounts_exec.sh
syntax ok tests/checks/consumers/22_bedtools_exec.required.sh
syntax ok tests/checks/consumers/23_samtools_fixture_integrity.required.sh
syntax ok tests/checks/consumers/24_starsolo_exec.sh
syntax ok tests/checks/consumers/25_cellranger_mkref.sh
ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f  data/dfam/dfam_interspersed_mm39_snapshot.json.gz
```

Core scratch rebuild:

```text
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build
[build] running 00_fetch_sources.sh
[00_fetch] cache: mm39.fa.out.gz
[00_fetch] cache: rmsk.txt.gz
[00_fetch] cache: mm39.chromAlias.txt
[00_fetch] cache: mm39.chrom.sizes
[00_fetch] sources ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/source
[build] running 05_qualify_source.sh
out_rows=5320771 table_rows=5320771 matched_rows=5320771 unmatched_out_rows=0 unmatched_table_rows=0 field_disagreements=0 distinct_ids=4696900 id_min=1 id_max=4696900 ids_contiguous=1 ids_spanning_contigs=0 starred_rows=0 coordinate_collision_pairs=3
[05_qualify] qualification ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/source/qualification.md
[build] running 10_build_records.sh
records=5320771 instances=4696900 names=18484 triples=18504
[10_build_records] canonical tables ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables
[build] running 15_build_universes.sh
universe_name=all_rmsk records=5320771 names=18484 triples=18504 length_sum_bp=1201573004
universe_name=compat_tetranscripts_mm39 records=3799629 names=1225 triples=1245 length_sum_bp=1121476301
universe_name=interspersed records=3764949 names=1220 triples=1240 length_sum_bp=1116605808
universe_name=interspersed_plus_satellites records=3802177 names=1228 triples=1248 length_sum_bp=1121742599
universe_name=retrotransposon_derived records=3593857 names=868 triples=868 length_sum_bp=1084886912
universe_name=satellites records=37228 names=8 triples=8 length_sum_bp=5136791
[15_build_universes] universes ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/universes.json
[build] running 20_build_taxonomy.sh
names=18484 multi_label_names=20 taxonomy_rule_version=taxonomy_rule_v1
[20_build_taxonomy] canonical taxonomy ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables
[build] running 25_build_dfam.sh
Dfam 4.0: names=1220 models=1263 nodes=300 clades=1278 matches={'exact': 1047, 'missing': 26, 'part_model_set': 147}
[build] running 30_build_exports.sh
universe=interspersed records=3764949 subfamilies=1220 families=49 taxonomy_triples=1220 instances=3152636 exports=8 registrations=30119592
universe=all_rmsk records=5320771 exports=1 registrations=5320771
[30_build_exports] UCSC exports ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc
[build] running 35_build_namespaces.sh
namespace=ensembl exports=9
namespace=gencode exports=9
aliases=61 coverage=61 inventory=27
[35_build_namespaces] Contig namespaces ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports
ok build paths: regular files and directories
ok inventory: 51 files, exact paths, bytes and sha256
ok BUILD_ID: 763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
ok catalog, source_run scope, assembly, contig digest and taxonomy rule
ok universe definitions and predicate grammar
ok export contracts: 27 namespace paths
ok export rows and sha256: exports/ensembl/all_rmsk/full/record.bed
ok export rows and sha256: exports/ensembl/interspersed/full/family.bed
ok export rows and sha256: exports/ensembl/interspersed/full/record.bed
ok export rows and sha256: exports/ensembl/interspersed/full/record.gtf
ok export rows and sha256: exports/ensembl/interspersed/full/record_starsolo.gtf
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.bed
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.saf
ok export rows and sha256: exports/ensembl/interspersed/full/taxonomy_triple.saf
ok export rows and sha256: exports/gencode/all_rmsk/full/record.bed
ok export rows and sha256: exports/gencode/interspersed/full/family.bed
ok export rows and sha256: exports/gencode/interspersed/full/record.bed
ok export rows and sha256: exports/gencode/interspersed/full/record.gtf
ok export rows and sha256: exports/gencode/interspersed/full/record_starsolo.gtf
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.bed
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.saf
ok export rows and sha256: exports/gencode/interspersed/full/taxonomy_triple.saf
ok export rows and sha256: exports/ucsc/all_rmsk/full/record.bed
ok export rows and sha256: exports/ucsc/interspersed/full/family.bed
ok export rows and sha256: exports/ucsc/interspersed/full/record.bed
ok export rows and sha256: exports/ucsc/interspersed/full/record.gtf
ok export rows and sha256: exports/ucsc/interspersed/full/record_starsolo.gtf
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.bed
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.saf
ok export rows and sha256: exports/ucsc/interspersed/full/taxonomy_triple.saf
ok records schema: 24 required typed columns
ok record identities: 5320771 unique keys and text instance ids
ok record bounds: source/mm39.chrom.sizes
ok universe_summary all_rmsk: 5320771 records
verified 763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
[build] done

real	11m57.197s
user	11m0.527s
sys	2m19.960s
exit=0
measurement {"wall_seconds": 717.201, "peak_rss_bytes": 9026424832, "exit": 0}
```

IDs, inventory, GTF samples and Dfam tables:

```text
763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
51 27 ['chromAlias', 'chrom_sizes', 'dfam_snapshot', 'rmsk_out', 'rmsk_table']
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ensembl/interspersed/full/record_starsolo.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/gencode/interspersed/full/record_starsolo.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/record_starsolo.gtf
  11294847 total
59
chr1	te-tracks	exon	3050294	3050775	3667	+	.	gene_id "R|mm39|L1MdA_VI|chr1|3050294|3050775|+"; transcript_id "R|mm39|L1MdA_VI|chr1|3050294|3050775|+"; gene_name "L1MdA_VI"; gene_type "transposable_element"; locus "R|mm39|L1MdA_VI|chr1|3050294|3050775|+"; rmsk_name "L1MdA_VI"; family_id "L1"; class_id "LINE"; rmsk_family "L1"; rmsk_class "LINE"; instance_id "I|mm39|1"; rmsk_record_id "L1MdA_VI|chr1:3050294-3050775|+";
chr1	te-tracks	exon	3051045	3051146	242	-	.	gene_id "R|mm39|ID2|chr1|3051045|3051146|-"; transcript_id "R|mm39|ID2|chr1|3051045|3051146|-"; gene_name "ID2"; gene_type "transposable_element"; locus "R|mm39|ID2|chr1|3051045|3051146|-"; rmsk_name "ID2"; family_id "ID"; class_id "SINE"; rmsk_family "ID"; rmsk_class "SINE"; instance_id "I|mm39|2"; rmsk_record_id "ID2|chr1:3051045-3051146|-";
rmsk_name	rmsk_class	rmsk_family	canonical_class	canonical_family	record_count	match_status	dfam_accessions	dfam_model_names	dfam_model_versions	dfam_model_lengths_bp	available_part_count	part_roles_present	model_length_sum_bp	classification_path	classification_leaf	clades	clade_leaves	clade_compatibility	dfam_release	wicker_code	wicker_code_uncertain	wicker_class	wicker_class_status	wicker_subcla
AmnHarb1	DNA	PIF-Harbinger	DNA	PIF-Harbinger	115	exact	DF000001731	AmnHarb1	1	1444	0		1444	root;Interspersed_Repeat;Transposable_Element;Class_II_DNA_Transposition;Transposase;PIF-Harbinger;Harbinger	Harbinger	root;cellular organisms;Eukaryota;Opisthokonta;Metazoa;Eumetazoa;Bilateria;Deuterostomia;Chordata;Craniata;Vertebrata;Gnathostomata;Teleostomi;Euteleostomi;Sarcopterygii;Dipnotetrapodomorpha
AmnL2-1	LINE	L2	LINE	L2	1311	exact	DF000001732	AmnL2-1	1	2613	0		2613	root;Interspersed_Repeat;Transposable_Element;Class_I_Retrotransposition;LINE;Group-II;Group-2;R1-like;CR1-group;L2-group;L2	L2	root;cellular organisms;Eukaryota;Opisthokonta;Metazoa;Eumetazoa;Bilateria;Deuterostomia;Chordata;Craniata;Vertebrata;Gnathostomata;Teleostomi;Euteleostomi;Sarcopterygii;Dipnotetrapodomorpha;Tetrapoda;A
   1264 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_dfam_models.tsv
   1221 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_dfam.tsv
    301 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/dfam_lineage_nodes.tsv
   1279 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/dfam_model_clades.tsv
   4065 total
   1047 exact
     26 missing
    147 part_model_set
```

Earlier archive verification:

```text
ok build paths: regular files and directories
ok inventory: 43 files, exact paths, bytes and sha256
ok BUILD_ID: 9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
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
verified 9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d
measurement {"wall_seconds": 28.658, "peak_rss_bytes": 2347425792, "exit": 0}
exit=0 (earlier archive stays verifiable)
```

First core run, before the child re-pin:

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
pass  33_taxonomy_dfam_view.py  Dfam census and catalog joins pass; {"coded_nodes": 193, "exact_names": 1047, "exact_records": 2797852, "exact_wicker_inherited": 110, "exact_wicker_mapped": 884, "exact_wicker_missing": 53, "l2_cr1_part_sets": 6, "lineage_nodes": 300, "missing_names": 26, "missing_records": 38569, "model_rows": 1263, "multi_clade_models": 9, "names": 1220, "part_model_set_names": 147, "part_model_set_records": 928528, "part_sets_1": 108, "part_sets_2": 9, "part_sets_3": 30, "primate_branch_models": 33, "primate_branch_names": 31, "records": 3764949}
pass  34_dfam_rule_fixtures.py  14 authored Dfam cases: codes, inherited ranks, uncertainty, subclasses, parts, clades and named disagreement pass
pass  40_exports_shape.py  eight exports: 3764949 rows each; subfamilies=1220 families=49 taxonomy_triples=1220; coordinates and identifiers pass
pass  41_export_registration.py  registrations: interspersed=30119592 all_rmsk=5320771; eight interspersed ID spellings; instances=3152636; 27 inventory hashes, feature sets and GTF tuple/instance joins pass; three record grammars; count 7 stays 7 at record, subfamily and family levels
pass  42_exports_fixtures.py  nine hand-authored exports and 46 registration rows; eight-export/40-row interspersed job; membership selection, unresolved ranks, coordinate duplicates, shared instances, deterministic rebuild, universe and identifier gates pass
pass  43_matrix_binding.py  1000 shared records: pair-only join=2000 rows/1001000 counts; four-field join=1000 rows/500500 counts
pass  60_contig_aliases.py  61 injective aliases and FASTA names/lengths; catalog=5320771 interspersed=3764949; all contigs carry catalog records; chr4_JH584295v1_random and chrM carry 2 and 4 catalog records, zero interspersed records
pass  61_namespace_exports.py  27 sorted exports and SHA-256 digests; 18 complete renamed files regenerated; interspersed=3764949 all_rmsk=5320771 per namespace; registrations=30119592+5320771
pass  62_preflight.sh  104 preflight cases; both universes, three namespaces, BED/GTF/SAF and sizes/FAI/BAM; covered=0, export-only=2, empty/shared-length/input errors=1; exact reports and enclosing build aliases pass
pass  70_manifest_identity.py  BUILD_ID=763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c CATALOG_ID=90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e; 51 payloads; identity mutations pass
pass  71_verify_build.py  real build verifies unchanged; fixture stray authoring payload, flipped byte, extra file, unpublished taxonomy rule and export roster mismatch fail with named discrepancies; fixture cases=3.535s
pass  72_publication_cases.py  identical and changed builds, export-roster evolution (4 archives), failed verification and interrupted staging cleanup, concurrent installs/selects (5 archives), old IDs, forged ID, corrupt current, selector and root cases, occupied targets, symlinks and 0444/0555 modes pass
pass  80_exon_subtraction.py  5320771 records conserve bases; registered blocks ordered, disjoint and contained; 200000-record sample exon-disjoint; summary census, 14805348 registrations, 12 SAF row multisets and sort orders, independent GTF coverage 38/61 with 2638 unannotated records pass
pass  81_exon_subtraction_fixtures.py  15 geometry cases, 12 SAFs, 96 registrations, annotation coverage, duplicate invariance and named refusals pass
Traceback (most recent call last):
  File "/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/82_child_identity.py", line 31, in <module>
    assert identity["parent_build_id"] == parent_bytes["BUILD_ID"].decode().strip()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
fail  82_child_identity.py
pass  83_child_publication_cases.sh  child install/select/verify-current require present, verified parent; repeated publication converges; archive resolution, preserved selection, immutable modes and earlier core selection pass
checks=26 pass=25 fail=1 unsupported=0
exit=1
```

Consumers without activation:

```text
pass  00_tool_inventory.required.py  supported tool_inventory reporting-only; irescue=absent; featureCounts=absent; stellarscope=absent; TEsingle=absent; TEcount=absent; TElocal=absent; bedtools=bedtools v2.31.1; samtools=samtools 1.21; STAR=absent; cellranger=absent
pass  10_irescue_parser.required.py  supported irescue 1.2.0 (v1.2.0-20-g26f36fb) checkout parser; record=11, subfamily=8; comma splits one name and exporter rejects it
unsupported  11_stellarscope_parser.py  unsupported: stellarscope right-boundary overlap defect, observed 0,1,1,1 expected 0,1,1,0; stellarscope 1.5 (1.5) checkout parser
pass  12_tesingle_parser.required.py  supported TEsingle 1.0 (1.0-8-g655f127) checkout parser; record=11, subfamily=8; 999 distinct UR dropped, 1000 kept; duplicate/QC-fail reads skipped
pass  13_tetranscripts_telocal_parser.required.py  supported TEtranscripts/TElocal 2.2.4 (2.2.4-13-ge7f9b93)/1.1.3 (1.1.3-4-g1a168c2) checkout parsers; TEtranscripts=8 groups; TElocal locInd record=11, subfamily=8
pass  14_mates_parser.required.py  supported MATES 0.1.8 (v0.1.8-9-g87c1218) checkout adapter; eight-column pair; underscore stem; ?/Unknown model groups dropped
pass  15_irescue_chrcat.py  supported irescue 1.2.0 (v1.2.0-20-g26f36fb) checkout chrcat; chrcat emitted record=11, subfamily=8 identities; mappings and feature index agree
pass  16_family_triple_readers.required.py  supported family/triple readers bedtools v2.31.1; Python SAF column reader; family buckets and 8 SAF GeneIDs registered; three TwoLab rows share one triple
pass  17_starsolo_profile.required.py  supported STARsolo/cellranger record profile parser; 12 ordered attributes; 11 record genes; same-name separation, registration, namespaces, one-base endpoints and host collisions pass
unsupported  20_irescue_exec.sh  unsupported: irescue absent
unsupported  21_featurecounts_exec.sh  unsupported: featureCounts absent
pass  22_bedtools_exec.required.sh  supported bedtools v2.31.1; duplicate names, half-open boundaries and -s/-S pass
pass  23_samtools_fixture_integrity.required.sh  supported samtools 1.21; 11 sorted, indexed BAMs; ARC=13 OCM=26 bulk=26 alignments, 11 molecules each; tagged main UB=11 UR=12; reverse strands and duplicate/QC-fail flags pass
unsupported  24_starsolo_exec.sh  unsupported: STAR absent
unsupported  25_cellranger_mkref.sh  unsupported: cellranger absent
pass  30_registration_duckdb.py  DuckDB registration targets and hand-computed totals pass; count 7 stays 7 at record, subfamily and family levels
checks=16 pass=11 fail=0 unsupported=5
exit=0
```

Consumers with activation:

```text
pass  00_tool_inventory.required.py  supported tool_inventory reporting-only; irescue=IRescue 1.2.0; featureCounts=featureCounts v2.1.1; stellarscope=1.5; TEsingle=TEsingle 1.0; TEcount=TEcount 2.2.4; TElocal=TElocal 1.1.3; bedtools=bedtools v2.31.1; samtools=samtools 1.21; STAR=2.7.11b; cellranger=cellranger 10.1.0
pass  10_irescue_parser.required.py  supported irescue 1.2.0 (v1.2.0-20-g26f36fb) checkout parser; record=11, subfamily=8; comma splits one name and exporter rejects it
unsupported  11_stellarscope_parser.py  unsupported: stellarscope right-boundary overlap defect, observed 0,1,1,1 expected 0,1,1,0; stellarscope 1.5 (1.5) checkout parser
pass  12_tesingle_parser.required.py  supported TEsingle 1.0 (1.0-8-g655f127) checkout parser; record=11, subfamily=8; 999 distinct UR dropped, 1000 kept; duplicate/QC-fail reads skipped
pass  13_tetranscripts_telocal_parser.required.py  supported TEtranscripts/TElocal 2.2.4 (2.2.4-13-ge7f9b93)/1.1.3 (1.1.3-4-g1a168c2) checkout parsers; TEtranscripts=8 groups; TElocal locInd record=11, subfamily=8
pass  14_mates_parser.required.py  supported MATES 0.1.8 (v0.1.8-9-g87c1218) checkout adapter; eight-column pair; underscore stem; ?/Unknown model groups dropped
pass  15_irescue_chrcat.py  supported irescue 1.2.0 (v1.2.0-20-g26f36fb) checkout chrcat; chrcat emitted record=11, subfamily=8 identities; mappings and feature index agree
pass  16_family_triple_readers.required.py  supported family/triple readers bedtools v2.31.1; Python SAF column reader; family buckets and 8 SAF GeneIDs registered; three TwoLab rows share one triple
pass  17_starsolo_profile.required.py  supported STARsolo/cellranger record profile parser; 12 ordered attributes; 11 record genes; same-name separation, registration, namespaces, one-base endpoints and host collisions pass
pass  20_irescue_exec.sh  supported irescue IRescue 1.2.0; SubA=2, records=1+1; {"arc_3_3": {"A": 4.5, "B": 4.5, "EM_x": 1.5}, "arc_4_2": {"A": 5.5, "B": 3.5, "EM_x": 1.5}, "ocm_3_3": {"A": 4.5, "B": 4.5, "EM_x": 1.5}, "ocm_4_2": {"A": 5.5, "B": 3.5, "EM_x": 1.5}}
pass  21_featurecounts_exec.sh  supported featureCounts v2.1.1; -s 0; two fragments per subfamily and triple SAF feature; inclusive one-base overlap
pass  22_bedtools_exec.required.sh  supported bedtools v2.31.1; duplicate names, half-open boundaries and -s/-S pass
pass  23_samtools_fixture_integrity.required.sh  supported samtools 1.21; 11 sorted, indexed BAMs; ARC=13 OCM=26 bulk=26 alignments, 11 molecules each; tagged main UB=11 UR=12; reverse strands and duplicate/QC-fail flags pass
pass  24_starsolo_exec.sh  supported STAR 2.7.11b; record gene identities and molecule conservation pass; {"gap": {"Gene": {"EM": {}, "unique": {}}, "GeneFull": {"EM": {"HostGene": 1.0}, "unique": {"HostGene": 1.0}}}, "intronic": {"Gene": {"EM": {"R|mm39|SubB-int|chrA|3201|3400|+": 1.0}, "unique": {"R|mm39|SubB-int|chrA|3201|3400|+": 1.0}}, "GeneFull": {"EM": {"HostGene": 0.5, "R|mm39|SubB-int|chrA|3201|3400|+": 0.5}, "unique": {}}}, "overlap": {"Gene": {"EM": {"HostGene": 1.5, "R|mm39|SubB|chrA|3001|3100|+": 1.5}, "unique": {"HostGene": 1.0, "R|mm39|SubB|chrA|3001|3100|+": 1.0}}, "GeneFull": {"EM": {"HostGene": 2.98266, "R|mm39|SubB|chrA|3001|3100|+": 0.0173415}, "unique": {"HostGene": 1.0}}}, "same_name": {"Gene": {"EM": {"R|mm39|SubA|chrA|1001|1200|+": 1.0, "R|mm39|SubA|chrA|2001|2200|-": 1.0}, "unique": {"R|mm39|SubA|chrA|1001|1200|+": 1.0, "R|mm39|SubA|chrA|2001|2200|-": 1.0}}, "GeneFull": {"EM": {"R|mm39|SubA|chrA|1001|1200|+": 1.0, "R|mm39|SubA|chrA|2001|2200|-": 1.0}, "unique": {"R|mm39|SubA|chrA|1001|1200|+": 1.0, "R|mm39|SubA|chrA|2001|2200|-": 1.0}}}}
pass  25_cellranger_mkref.sh  supported cellranger 10.1.0; mkgtf retains TE and host biotypes; mkref keeps 11 alias genes and its STAR index
pass  30_registration_duckdb.py  DuckDB registration targets and hand-computed totals pass; count 7 stays 7 at record, subfamily and family levels
checks=16 pass=15 fail=0 unsupported=1
exit=0
```

Core publication:

```text
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.GMEjhaBt
[build] running 00_fetch_sources.sh
[00_fetch] cache: mm39.fa.out.gz
[00_fetch] cache: rmsk.txt.gz
[00_fetch] cache: mm39.chromAlias.txt
[00_fetch] cache: mm39.chrom.sizes
[00_fetch] sources ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.GMEjhaBt/source
[build] running 05_qualify_source.sh
out_rows=5320771 table_rows=5320771 matched_rows=5320771 unmatched_out_rows=0 unmatched_table_rows=0 field_disagreements=0 distinct_ids=4696900 id_min=1 id_max=4696900 ids_contiguous=1 ids_spanning_contigs=0 starred_rows=0 coordinate_collision_pairs=3
[05_qualify] qualification ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.GMEjhaBt/source/qualification.md
[build] running 10_build_records.sh
records=5320771 instances=4696900 names=18484 triples=18504
[10_build_records] canonical tables ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.GMEjhaBt/tables
[build] running 15_build_universes.sh
universe_name=all_rmsk records=5320771 names=18484 triples=18504 length_sum_bp=1201573004
universe_name=compat_tetranscripts_mm39 records=3799629 names=1225 triples=1245 length_sum_bp=1121476301
universe_name=interspersed records=3764949 names=1220 triples=1240 length_sum_bp=1116605808
universe_name=interspersed_plus_satellites records=3802177 names=1228 triples=1248 length_sum_bp=1121742599
universe_name=retrotransposon_derived records=3593857 names=868 triples=868 length_sum_bp=1084886912
universe_name=satellites records=37228 names=8 triples=8 length_sum_bp=5136791
[15_build_universes] universes ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.GMEjhaBt/universes.json
[build] running 20_build_taxonomy.sh
names=18484 multi_label_names=20 taxonomy_rule_version=taxonomy_rule_v1
[20_build_taxonomy] canonical taxonomy ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.GMEjhaBt/tables
[build] running 25_build_dfam.sh
Dfam 4.0: names=1220 models=1263 nodes=300 clades=1278 matches={'exact': 1047, 'missing': 26, 'part_model_set': 147}
[build] running 30_build_exports.sh
universe=interspersed records=3764949 subfamilies=1220 families=49 taxonomy_triples=1220 instances=3152636 exports=8 registrations=30119592
universe=all_rmsk records=5320771 exports=1 registrations=5320771
[30_build_exports] UCSC exports ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.GMEjhaBt/exports/ucsc
[build] running 35_build_namespaces.sh
namespace=ensembl exports=9
namespace=gencode exports=9
aliases=61 coverage=61 inventory=27
[35_build_namespaces] Contig namespaces ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.GMEjhaBt/exports
ok build paths: regular files and directories
ok inventory: 51 files, exact paths, bytes and sha256
ok BUILD_ID: 763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
ok catalog, source_run scope, assembly, contig digest and taxonomy rule
ok universe definitions and predicate grammar
ok export contracts: 27 namespace paths
ok export rows and sha256: exports/ensembl/all_rmsk/full/record.bed
ok export rows and sha256: exports/ensembl/interspersed/full/family.bed
ok export rows and sha256: exports/ensembl/interspersed/full/record.bed
ok export rows and sha256: exports/ensembl/interspersed/full/record.gtf
ok export rows and sha256: exports/ensembl/interspersed/full/record_starsolo.gtf
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.bed
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.saf
ok export rows and sha256: exports/ensembl/interspersed/full/taxonomy_triple.saf
ok export rows and sha256: exports/gencode/all_rmsk/full/record.bed
ok export rows and sha256: exports/gencode/interspersed/full/family.bed
ok export rows and sha256: exports/gencode/interspersed/full/record.bed
ok export rows and sha256: exports/gencode/interspersed/full/record.gtf
ok export rows and sha256: exports/gencode/interspersed/full/record_starsolo.gtf
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.bed
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.saf
ok export rows and sha256: exports/gencode/interspersed/full/taxonomy_triple.saf
ok export rows and sha256: exports/ucsc/all_rmsk/full/record.bed
ok export rows and sha256: exports/ucsc/interspersed/full/family.bed
ok export rows and sha256: exports/ucsc/interspersed/full/record.bed
ok export rows and sha256: exports/ucsc/interspersed/full/record.gtf
ok export rows and sha256: exports/ucsc/interspersed/full/record_starsolo.gtf
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.bed
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.saf
ok export rows and sha256: exports/ucsc/interspersed/full/taxonomy_triple.saf
ok records schema: 24 required typed columns
ok record identities: 5320771 unique keys and text instance ids
ok record bounds: source/mm39.chrom.sizes
ok universe_summary all_rmsk: 5320771 records
verified 763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
installed 763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
selected 763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
[build] done

real	12m55.157s
user	12m4.300s
sys	2m27.596s
exit=0
measurement {"wall_seconds": 775.159, "peak_rss_bytes": 9026469888, "exit": 0}
```

Core `verify-current`:

```text
763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
```

Child scratch rebuild:

```text
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build
[build] running 00_fetch_gene_sources.sh
[00_fetch_gene] cache: gencode.vM37.primary_assembly.annotation.gtf.gz
stage_metrics {"stage": "00_fetch_gene_sources.sh", "wall_seconds": 0.586, "peak_rss_bytes": 118550528}
[build] running 10_copy_parent_inputs.sh
stage_metrics {"stage": "10_copy_parent_inputs.sh", "wall_seconds": 0.442, "peak_rss_bytes": 119365632}
[build] running 50_build_exon_subtracted.sh
universe_name	records	unchanged	trimmed	split	fully_subtracted	retained_records	blocks	retained_bp	removed_bp	records_on_unannotated_contigs
all_rmsk	5320771	5086684	61378	15495	157214	5163557	5179754	1172003155	29569849	2638
interspersed	3764949	3600721	52703	15406	96119	3668830	3684934	1090369890	26235918	1612
compat_tetranscripts_mm39	3799629	3633401	52842	15399	97987	3701642	3717740	1094973237	26503064	1754
stage_metrics {"stage": "50_build_exon_subtracted.sh", "wall_seconds": 155.333, "peak_rss_bytes": 889823232}
ok build paths: regular files and directories
ok inventory: 21 files, exact paths, bytes and sha256
ok BUILD_ID: 693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
ok parent dependency: te_mm39/763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
ok child identity: inherited catalog, copied inputs, annotation and policy
ok export contracts: 12 namespace paths
ok child registration: every parent key, feature and ordered retained block
ok child status: complete catalog conservation and summary
ok annotation coverage: 38 annotated contigs of 61
ok child SAF rows and distinct features: registration per universe and grouping
ok child SAF rows: content and order equal the registration in every namespace
verified 693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
[build] done

real	9m13.288s
user	9m22.617s
sys	1m2.322s
exit=0
measurement {"wall_seconds": 553.292, "peak_rss_bytes": 3573747712, "exit": 0}
```

Child ID, summary and byte comparisons:

```text
693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
universe_name	records	unchanged	trimmed	split	fully_subtracted	retained_records	blocks	retained_bp	removed_bp	records_on_unannotated_contigs
all_rmsk	5320771	5086684	61378	15495	157214	5163557	5179754	1172003155	29569849	2638
interspersed	3764949	3600721	52703	15406	96119	3668830	3684934	1090369890	26235918	1612
compat_tetranscripts_mm39	3799629	3633401	52842	15399	97987	3701642	3717740	1094973237	26503064	1754
child CATALOG_ID equal
child exon-subtraction summary unchanged
```

Child publication:

```text
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39_gene/.staging/build.nWnsUdLp
[build] running 00_fetch_gene_sources.sh
[00_fetch_gene] cache: gencode.vM37.primary_assembly.annotation.gtf.gz
stage_metrics {"stage": "00_fetch_gene_sources.sh", "wall_seconds": 0.616, "peak_rss_bytes": 119119872}
[build] running 10_copy_parent_inputs.sh
stage_metrics {"stage": "10_copy_parent_inputs.sh", "wall_seconds": 0.401, "peak_rss_bytes": 117596160}
[build] running 50_build_exon_subtracted.sh
universe_name	records	unchanged	trimmed	split	fully_subtracted	retained_records	blocks	retained_bp	removed_bp	records_on_unannotated_contigs
all_rmsk	5320771	5086684	61378	15495	157214	5163557	5179754	1172003155	29569849	2638
interspersed	3764949	3600721	52703	15406	96119	3668830	3684934	1090369890	26235918	1612
compat_tetranscripts_mm39	3799629	3633401	52842	15399	97987	3701642	3717740	1094973237	26503064	1754
stage_metrics {"stage": "50_build_exon_subtracted.sh", "wall_seconds": 161.575, "peak_rss_bytes": 899354624}
ok build paths: regular files and directories
ok inventory: 21 files, exact paths, bytes and sha256
ok BUILD_ID: 693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
ok parent dependency: te_mm39/763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
ok child identity: inherited catalog, copied inputs, annotation and policy
ok export contracts: 12 namespace paths
ok child registration: every parent key, feature and ordered retained block
ok child status: complete catalog conservation and summary
ok annotation coverage: 38 annotated contigs of 61
ok child SAF rows and distinct features: registration per universe and grouping
ok child SAF rows: content and order equal the registration in every namespace
verified 693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
installed 693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
selected 693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
[build] done

real	15m8.311s
user	15m18.690s
sys	1m19.316s
exit=0
measurement {"wall_seconds": 908.313, "peak_rss_bytes": 3813830656, "exit": 0}
```

Child `verify-current`:

```text
693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
exit=0
measurement {"wall_seconds": 171.06, "peak_rss_bytes": 3481579520, "exit": 0}
```

Runner self-test after the usage edit:

```text
runner statuses, required checks, diagnostics, dangling symlinks and usage exits pass
exit=0
```

Clean final core run:

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
pass  33_taxonomy_dfam_view.py  Dfam census and catalog joins pass; {"coded_nodes": 193, "exact_names": 1047, "exact_records": 2797852, "exact_wicker_inherited": 110, "exact_wicker_mapped": 884, "exact_wicker_missing": 53, "l2_cr1_part_sets": 6, "lineage_nodes": 300, "missing_names": 26, "missing_records": 38569, "model_rows": 1263, "multi_clade_models": 9, "names": 1220, "part_model_set_names": 147, "part_model_set_records": 928528, "part_sets_1": 108, "part_sets_2": 9, "part_sets_3": 30, "primate_branch_models": 33, "primate_branch_names": 31, "records": 3764949}
pass  34_dfam_rule_fixtures.py  14 authored Dfam cases: codes, inherited ranks, uncertainty, subclasses, parts, clades and named disagreement pass
pass  40_exports_shape.py  eight exports: 3764949 rows each; subfamilies=1220 families=49 taxonomy_triples=1220; coordinates and identifiers pass
pass  41_export_registration.py  registrations: interspersed=30119592 all_rmsk=5320771; eight interspersed ID spellings; instances=3152636; 27 inventory hashes, feature sets and GTF tuple/instance joins pass; three record grammars; count 7 stays 7 at record, subfamily and family levels
pass  42_exports_fixtures.py  nine hand-authored exports and 46 registration rows; eight-export/40-row interspersed job; membership selection, unresolved ranks, coordinate duplicates, shared instances, deterministic rebuild, universe and identifier gates pass
pass  43_matrix_binding.py  1000 shared records: pair-only join=2000 rows/1001000 counts; four-field join=1000 rows/500500 counts
pass  60_contig_aliases.py  61 injective aliases and FASTA names/lengths; catalog=5320771 interspersed=3764949; all contigs carry catalog records; chr4_JH584295v1_random and chrM carry 2 and 4 catalog records, zero interspersed records
pass  61_namespace_exports.py  27 sorted exports and SHA-256 digests; 18 complete renamed files regenerated; interspersed=3764949 all_rmsk=5320771 per namespace; registrations=30119592+5320771
pass  62_preflight.sh  104 preflight cases; both universes, three namespaces, BED/GTF/SAF and sizes/FAI/BAM; covered=0, export-only=2, empty/shared-length/input errors=1; exact reports and enclosing build aliases pass
pass  70_manifest_identity.py  BUILD_ID=763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c CATALOG_ID=90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e; 51 payloads; identity mutations pass
pass  71_verify_build.py  real build verifies unchanged; fixture stray authoring payload, flipped byte, extra file, unpublished taxonomy rule and export roster mismatch fail with named discrepancies; fixture cases=3.510s
pass  72_publication_cases.py  identical and changed builds, export-roster evolution (4 archives), failed verification and interrupted staging cleanup, concurrent installs/selects (5 archives), old IDs, forged ID, corrupt current, selector and root cases, occupied targets, symlinks and 0444/0555 modes pass
pass  80_exon_subtraction.py  5320771 records conserve bases; registered blocks ordered, disjoint and contained; 200000-record sample exon-disjoint; summary census, 14805348 registrations, 12 SAF row multisets and sort orders, independent GTF coverage 38/61 with 2638 unannotated records pass
pass  81_exon_subtraction_fixtures.py  15 geometry cases, 12 SAFs, 96 registrations, annotation coverage, duplicate invariance and named refusals pass
pass  82_child_identity.py  child identity fields, inherited pins, all policy/GTF/roster/parent mutations, dependency and payload refusals, SAF content and order refusals, parent/build-dir symlink refusals with trailing slashes, CLI usage gates pass
pass  83_child_publication_cases.sh  child install/select/verify-current require present, verified parent; repeated publication converges; archive resolution, preserved selection, immutable modes and earlier core selection pass
checks=26 pass=26 fail=0 unsupported=0
exit=0
```

Archive listing:

```text
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive:
763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d

/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39_gene/archive:
1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
```

Final size output:

```text
15301655992	/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build
payload files 51 bytes 15301535164
```

Final `git status --short`:

```text
 M .gitignore
 M README.md
 M config/mm39.env
 M docs/DECISIONS.md
 M docs/OUTPUTS.md
 M docs/RELEASES.md
 M docs/RUNBOOK.md
 M src/00_fetch_sources.sh
 M src/lib/build_exports.py
 M src/lib/manifest.py
 M tests/checks/core/40_exports_shape.py
 M tests/checks/core/41_export_registration.py
 M tests/checks/core/42_exports_fixtures.py
 M tests/checks/core/61_namespace_exports.py
 M tests/checks/core/62_preflight.sh
 M tests/checks/core/70_manifest_identity.py
 M tests/checks/core/71_verify_build.py
 M tests/checks/core/72_publication_cases.py
 M tests/fixtures/publication/build_fixture.py
 M tests/lib/consumers.py
 M tests/lib/records.py
 M tests/run.sh
?? data/
?? src/25_build_dfam.sh
?? src/lib/build_dfam.py
?? tests/checks/consumers/17_starsolo_profile.required.py
?? tests/checks/consumers/24_starsolo_exec.sh
?? tests/checks/consumers/25_cellranger_mkref.sh
?? tests/checks/core/33_taxonomy_dfam_view.py
?? tests/checks/core/34_dfam_rule_fixtures.py
?? tests/checks/core/43_matrix_binding.py
?? tests/expectations/mm39/dfam_census.tsv
?? tests/fixtures/consumers/starsolo_collision.gtf
?? tests/fixtures/consumers/starsolo_host.gtf
?? tests/fixtures/consumers/starsolo_molecules.tsv
?? tests/fixtures/consumers/starsolo_reserved.gtf
?? tests/fixtures/exports/expected/record_starsolo.gtf
?? tests/fixtures/taxonomy/dfam_rank_cases.tsv
```
