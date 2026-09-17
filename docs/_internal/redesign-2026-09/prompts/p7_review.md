# te-tracks phase 7 review (codex, read-only)

You are an independent reviewer of phase 7 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p7_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/17_phase7_publication.md`
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
  bite phase 8.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 7 review (codex gpt-6-astra)
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


## Phase 7 specifics
Facts: HEAD is `99bf646` (phase 6 committed); the implementer's uncommitted changes are the phase 7 work plus three
orchestrator edits under `docs/_internal/` (`session.md`, `02_orchestration.md`, `prompts/p7_impl.md`) that are out of
your scope. The orchestrator's build sits at `$TE_TRACKS_REFROOT/te_mm39/build`
(`TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`,
`TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source`); the implementer's published root
is `$TE_TRACKS_REFROOT/pubroot/te_mm39/` (one archive, `d9e6c18c…`, selected). Treat both as read-only. Scratch
work goes under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/codex-p7/` (`/tmp` is noexec) and is removed
when you finish; set `PYTHONDONTWRITEBYTECODE=1` for every python invocation. The checkouts under
`/workspaces/Meta-Aging/01_modules/.ref/` are git repositories: no writes there either.

Read also: `docs/_internal/redesign-2026-09/prompts/p7_impl.md` (the exact interfaces and numeric targets),
`docs/_internal/redesign-2026-09/reviews/m2_rulings.md` ("Phase 7") and `reviews/m5_rulings.md` (codex A2, A3;
divergent M1), `docs/_internal/redesign-2026-09/consults/ADR67_consult.md`.

Judge these in particular, each with evidence:
1. Identity: recompute `BUILD_ID` and `CATALOG_ID` from `MANIFEST.json` with your own encoder; confirm the 43
   inventory entries against disk; confirm the installed archive's `identity` equals the build directory's and name
   the provenance keys that differ. Optional if disk and time allow (about 12 minutes, 10.5 GB): run
   `./build.sh --genome mm39 --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/codex-p7/pubroot` once and
   compare the resulting `BUILD_ID` and `CATALOG_ID` with `d9e6c18c…` and `9a42ec53…`; remove that root afterwards.
2. `export_contracts`: compare the consumer keys, attribute sources and selectable levels in
   `build_exports.EXPORT_CONTRACTS` with what the consumer checks under `tests/checks/consumers/` and
   `tests/lib/consumers.py` actually construct from each export (milestone 5 ruling A3). Name any key a real reader
   emits that the contract misstates, and any consumer named that no check exercises.
3. `release.py`: read the lock, rename and selection path and state which failure cases the contract lists are
   covered, and by which line of check 72. State what happens when `current` dangles (its archive removed), when the
   staging root sits on another filesystem, and when a second publisher holds the lock while the first verifies.
   Judge the triple verification in `install --select` (staging, existing archive, current selection: each a full
   read of 10.5 GB) against the contract.
4. Check 71 copies the whole 10.5 GB build with `cp -a --reflink=auto` on every core run. Measure or estimate the
   cost on this filesystem, state whether the reflink takes effect, and propose the cheapest arrangement that still
   proves the two named failures without writing into the real build.
5. Retention numbers: `docs/RELEASES.md` states the exports as 3,021,713,838 / 2,926,268,559 / 3,021,138,299
   bytes and the total as 10,461,962,113; the implementer reports observed sums 3,021,714,346 / 2,926,266,953 /
   3,021,140,740. Measure the per-namespace file sums and the 43-file payload sum yourself and state which figures
   a public document should carry.
6. `build.sh`: the RSS wrapper covers stage 30 alone; `TE_TRACKS_INVOCATION`; the `--root` and `--build-dir`
   exclusivity; a `--build-dir` inside an archive refused. Confirm `tests/run.sh core` still passes with the manifest
   files present in the build directory (checks 40 to 62 unchanged).
7. Verifier: confirm `99_verify.py` writes nothing (compare mtimes and sizes before and after) and that the
   hardcoded `SPECIES` table and `universes.schema_version == 1` are stated somewhere public or name them as silent
   assumptions.
8. Deviations reported by the implementer: `docs/DECISIONS.md` entry 7 edited beyond the two deferral sentences
   (the prompt's contract section asked for it while the touch list did not; say which you hold binding); the
   cross-parent rename requiring a writable directory (state whether that is POSIX or filesystem-specific).
9. Prose: `docs/RELEASES.md`, `docs/OUTPUTS.md`, `README.md`, `docs/DECISIONS.md`, the fixture README and every
   comment and docstring in the new code, against the wording rules.

## Implementer report
Implemented phase 7. Both full builds passed and converged to one archive; all 19 core checks passed. The first installed manifest was preserved.

Changed:

- [build.sh](/workspaces/Meta-Aging/01_modules/te-tracks/build.sh)
- [src/lib/build_exports.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/lib/build_exports.py)
- [docs/RELEASES.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/RELEASES.md)
- [docs/OUTPUTS.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/OUTPUTS.md)
- [docs/DECISIONS.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/DECISIONS.md)
- [README.md](/workspaces/Meta-Aging/01_modules/te-tracks/README.md)

Created:

- [src/lib/manifest.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/lib/manifest.py)
- [src/90_manifest.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/90_manifest.py)
- [src/99_verify.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/99_verify.py)
- [src/release.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/release.py)
- [70_manifest_identity.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/70_manifest_identity.py)
- [71_verify_build.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/71_verify_build.py)
- [72_publication_cases.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/72_publication_cases.py)
- [publication/build_fixture.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/publication/build_fixture.py)
- [publication/README.md](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/publication/README.md)

Deleted: none. The three internal documentation modifications shown in Git status were pre-existing or made externally; I left them intact.

Recorded image evidence: Ubuntu 22.04.5 LTS, `/etc/cloud/build.info` containing `serial: 20260627`; container image digest unavailable. Toolchain: Python 3.11.15, pyarrow 25.0.0, pandas 2.2.3, zlib 1.2.11.

Deviations:

- Included the explicitly requested DECISIONS entry 7 update alongside the two deferrals, despite the narrower edit rule.
- This filesystem rejects cross-parent renames of 0555 directories. The build root receives 0555 immediately after rename, under the publication lock and before selection.
- Supplied namespace sizes differ from both verified builds. The supplied values remain documented as the retention baseline:

| Namespace | Supplied bytes | Observed bytes |
|---|---:|---:|
| ucsc | 3,021,713,838 | 3,021,714,346 |
| ensembl | 2,926,268,559 | 2,926,266,953 |
| gencode | 3,021,138,299 | 3,021,140,740 |

Registration matches 347,526,106 bytes. Payload plus directory sizes matches 10,461,962,113 bytes before identity files.

Acceptance outputs follow verbatim.

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
syntax ok tests/run.sh
d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
9a42ec53135a203c4b458b0c7e77584917db1cc205fe2b7ae1932dd1f491340b
['identity', 'provenance']
['assembly', 'catalog', 'contig_set_sha256', 'declared_assembly', 'export_contracts', 'family', 'inventory', 'parent_build_id', 'parent_catalog_id', 'schema_version', 'species', 'taxonomy_rule_version', 'universes']
43
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
```

```text
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.jCqEfILG
[build] running 00_fetch_sources.sh
[00_fetch] cache: mm39.fa.out.gz
[00_fetch] cache: rmsk.txt.gz
[00_fetch] cache: mm39.chromAlias.txt
[00_fetch] cache: mm39.chrom.sizes
[00_fetch] sources ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.jCqEfILG/source
[build] running 05_qualify_source.sh
out_rows=5320771 table_rows=5320771 matched_rows=5320771 unmatched_out_rows=0 unmatched_table_rows=0 field_disagreements=0 distinct_ids=4696900 id_min=1 id_max=4696900 ids_contiguous=1 ids_spanning_contigs=0 starred_rows=0 coordinate_collision_pairs=3
[05_qualify] qualification ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.jCqEfILG/source/qualification.md
[build] running 10_build_records.sh
records=5320771 instances=4696900 names=18484 triples=18504
[10_build_records] canonical tables ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.jCqEfILG/tables
[build] running 15_build_universes.sh
universe_name=all_rmsk records=5320771 names=18484 triples=18504 length_sum_bp=1201573004
universe_name=compat_tetranscripts_mm39 records=3799629 names=1225 triples=1245 length_sum_bp=1121476301
universe_name=interspersed records=3764949 names=1220 triples=1240 length_sum_bp=1116605808
universe_name=interspersed_plus_satellites records=3802177 names=1228 triples=1248 length_sum_bp=1121742599
universe_name=retrotransposon_derived records=3593857 names=868 triples=868 length_sum_bp=1084886912
universe_name=satellites records=37228 names=8 triples=8 length_sum_bp=5136791
[15_build_universes] universes ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.jCqEfILG/universes.json
[build] running 20_build_taxonomy.sh
names=18484 multi_label_names=20 taxonomy_rule_version=taxonomy_rule_v1
[20_build_taxonomy] canonical taxonomy ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.jCqEfILG/tables
[build] running 30_build_exports.sh
universe=interspersed records=3764949 subfamilies=1220 families=49 taxonomy_triples=1220 instances=3152636 exports=7 registrations=30119592
universe=all_rmsk records=5320771 exports=1 registrations=5320771
[30_build_exports] UCSC exports ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.jCqEfILG/exports/ucsc
[build] running 35_build_namespaces.sh
namespace=ensembl exports=8
namespace=gencode exports=8
aliases=61 coverage=61 inventory=24
[35_build_namespaces] Contig namespaces ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.jCqEfILG/exports
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
installed d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
selected d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
[build] done

real	11m26.237s
user	10m56.944s
sys	2m4.233s
exit=0
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/:
total 20
drwxrwsr-x+ 4 devuser devgroup 4096 Sep 16 18:42 .
drwxrwsr-x+ 3 devuser devgroup 4096 Sep 16 18:31 ..
drwxrwsr-x+ 3 devuser devgroup 4096 Sep 16 18:42 archive
lrwxrwxrwx  1 devuser devgroup   72 Sep 16 18:42 current -> archive/d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
drwxrwsr-x+ 2 devuser devgroup 4096 Sep 16 18:42 .staging

/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive/:
total 12
drwxrwsr-x+ 3 devuser devgroup 4096 Sep 16 18:42 .
drwxrwsr-x+ 4 devuser devgroup 4096 Sep 16 18:42 ..
dr-xr-xr-x+ 5 devuser devgroup 4096 Sep 16 18:41 d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
archive/d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
same id from both modes
[build] genome=mm39  build_dir=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.On0EQNu9
[build] running 00_fetch_sources.sh
[00_fetch] cache: mm39.fa.out.gz
[00_fetch] cache: rmsk.txt.gz
[00_fetch] cache: mm39.chromAlias.txt
[00_fetch] cache: mm39.chrom.sizes
[00_fetch] sources ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.On0EQNu9/source
[build] running 05_qualify_source.sh
out_rows=5320771 table_rows=5320771 matched_rows=5320771 unmatched_out_rows=0 unmatched_table_rows=0 field_disagreements=0 distinct_ids=4696900 id_min=1 id_max=4696900 ids_contiguous=1 ids_spanning_contigs=0 starred_rows=0 coordinate_collision_pairs=3
[05_qualify] qualification ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.On0EQNu9/source/qualification.md
[build] running 10_build_records.sh
records=5320771 instances=4696900 names=18484 triples=18504
[10_build_records] canonical tables ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.On0EQNu9/tables
[build] running 15_build_universes.sh
universe_name=all_rmsk records=5320771 names=18484 triples=18504 length_sum_bp=1201573004
universe_name=compat_tetranscripts_mm39 records=3799629 names=1225 triples=1245 length_sum_bp=1121476301
universe_name=interspersed records=3764949 names=1220 triples=1240 length_sum_bp=1116605808
universe_name=interspersed_plus_satellites records=3802177 names=1228 triples=1248 length_sum_bp=1121742599
universe_name=retrotransposon_derived records=3593857 names=868 triples=868 length_sum_bp=1084886912
universe_name=satellites records=37228 names=8 triples=8 length_sum_bp=5136791
[15_build_universes] universes ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.On0EQNu9/universes.json
[build] running 20_build_taxonomy.sh
names=18484 multi_label_names=20 taxonomy_rule_version=taxonomy_rule_v1
[20_build_taxonomy] canonical taxonomy ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.On0EQNu9/tables
[build] running 30_build_exports.sh
universe=interspersed records=3764949 subfamilies=1220 families=49 taxonomy_triples=1220 instances=3152636 exports=7 registrations=30119592
universe=all_rmsk records=5320771 exports=1 registrations=5320771
[30_build_exports] UCSC exports ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.On0EQNu9/exports/ucsc
[build] running 35_build_namespaces.sh
namespace=ensembl exports=8
namespace=gencode exports=8
aliases=61 coverage=61 inventory=24
[35_build_namespaces] Contig namespaces ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/.staging/build.On0EQNu9/exports
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
converged d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
selected d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
[build] done

real	11m54.957s
user	11m24.018s
sys	2m7.579s
exit=0 (expect converged, one archive)
1
d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9
exit=0
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
pass  62_preflight.sh  82 preflight cases; both universes, three namespaces, BED/GTF/SAF and sizes/FAI/BAM; covered=0, export-only=2, empty/shared-length/input errors=1; exact reports and nearest alias paths pass
pass  70_manifest_identity.py  BUILD_ID=d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9 CATALOG_ID=9a42ec53135a203c4b458b0c7e77584917db1cc205fe2b7ae1932dd1f491340b; 43 payloads; identity mutations pass
pass  71_verify_build.py  real build verifies unchanged; flipped byte and extra file fail with their paths
pass  72_publication_cases.py  identical and changed builds, failed verification, added payload, concurrent installs/selects, old IDs, forged ID, corrupt current, occupied targets, symlinks and 0444/0555 modes pass
checks=19 pass=19 fail=0 unsupported=0
exit=0
```

```text
 M README.md
 M build.sh
 M docs/DECISIONS.md
 M docs/OUTPUTS.md
 M docs/RELEASES.md
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/02_orchestration.md
 M docs/_internal/_project/session.md
 M docs/_internal/redesign-2026-09/prompts/p7_impl.md
 M src/lib/build_exports.py
?? src/90_manifest.py
?? src/99_verify.py
?? src/lib/manifest.py
?? src/release.py
?? tests/checks/core/70_manifest_identity.py
?? tests/checks/core/71_verify_build.py
?? tests/checks/core/72_publication_cases.py
?? tests/fixtures/publication/
```
