# te-tracks phase 6 fix (unit `te-tracks-p6-fix`)

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks` (branch `redesign-2026-09`, HEAD `c2a7a43`; the phase 6
implementer's tree sits uncommitted on top and is your starting point). You implement the rulings in
`docs/_internal/redesign-2026-09/reviews/p6_rulings.md`; the reviews they answer are `reviews/p6_codex.md` and
`reviews/p6_opus.md`.

## Read first
1. `docs/_internal/redesign-2026-09/reviews/p6_rulings.md` (every item below is a ruling there).
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/16_phase6_ensembl_preflight.md` (the amended contract:
   coverage sentence, preflight exit contract, acceptance numbers).
3. `docs/_internal/redesign-2026-09/reviews/p6_codex.md` B1 to B3, A1, A3; `reviews/p6_opus.md` where present.
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".
5. The files in the touch list, in full, before editing them.

## Environment and rules
- `export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot PYTHONDONTWRITEBYTECODE=1`. The build
  under `$TE_TRACKS_REFROOT/te_mm39/build` is yours to rebuild with stages 30 and 35 (about 4.5 minutes together);
  every other table there stays untouched. Scratch under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/p6fix/`,
  removed with Python `shutil` when you finish (`/tmp` is noexec).
- No git writes anywhere (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too), no
  installs, no network, no edits outside the touch list.
- Never weaken or delete a test. Report a blocking test by name. Every numeric target below is measured; when an
  observation differs, report the deviation instead of editing an artifact or an expectation to match.
- Public prose (README, docs, docstrings, comments, check messages) is affirmative and brief; comments state intent in
  one line; no history, provenance or review chatter in package files.

## Items

1. **Preflight exit contract** (`bin/te-tracks-preflight`, ruling B2). Exit 0 when every export contig is present in
   the reference with an agreeing length; `only_in_reference` stays printed and is informational. Exit 2 when the
   export names contigs the reference lacks and the shared set is nonempty. Exit 1 when a shared contig disagrees in
   length, the intersection is empty, or an input cannot be read. Module docstring and `--help` text state the
   contract in those terms. Report order and JSON formatting unchanged.
2. **Check 60** (`tests/checks/core/60_contig_aliases.py`). Replace the zero-total assertion: `records_interspersed`
   is zero on exactly `chr4_JH584295v1_random` and `chrM`; `records_all` is at least 1 on every contig and equals 2
   and 4 on those two; sums 5,320,771 and 3,764,949 stay asserted. Success message states the measured facts.
3. **Check 62** (`tests/checks/core/62_preflight.sh`). Expectations follow item 1 and cover both universes
   (`interspersed`, `all_rmsk`) in all three namespaces, the BED, GTF and SAF readers, and sizes, FAI and BAM
   references. Against the 61-contig FASTA list: `gencode` exits 0 for both universes (interspersed lists
   `JH584295.1` and `chrM` under `only_in_reference`, `all_rmsk` lists nothing); `ucsc` exits 2 (`all_rmsk`: 39
   GenBank names reference-only and 39 UCSC scaffolds export-only; interspersed: 40 reference-only, the 39 plus
   `chrM`, and 38 export-only); `ensembl` exits 2 (`all_rmsk`: 22 chromosomes each way; interspersed: 23
   reference-only, the 22 plus `JH584295.1`, and 21 export-only). Against a 21-chromosome UCSC sizes file: `ensembl`
   exits 1 (empty intersection), `ucsc` and `gencode` exit 2 (scaffolds export-only, 38 interspersed or 40 `all_rmsk`
   with `chrM`). A pysam BAM header with `chr1` at length 1 against `ucsc` exits 1 with one disagreement. A sizes file
   or FAI naming exactly the export's contigs exits 0 for both universes. An empty sizes file and a missing reference
   path exit 1 with a message on stderr. Compute every expected list from the alias table and the export, never from
   literals copied out of a report.
4. **One builder entry with explicit jobs** (`src/lib/build_exports.py`, ruling B3). Define
   `EXPORT_JOBS = (("interspersed", EXPORTS), ("all_rmsk", (("record.bed", "record"),)))`. `build_exports(build_dir,
   genome, jobs=EXPORT_JOBS)` is the single entry: it checks the default universe, writes the registration header
   once, runs every job in order into the one registration stream, and writes the inventory from all jobs. `main()`
   calls `build_exports(args.build_dir, args.genome)`. `export_universe` keeps its explicit universe and export set.
   `tests/lib/consumers.py` calls `build_exports(FIXTURES, "mm39", jobs=(("interspersed", EXPORTS),))` (import
   `EXPORTS` beside `build_exports`); nothing else in that file changes.
5. **Stage 35 derives its expected UCSC paths from the jobs** (`src/lib/contigs.py`, codex A1): import `EXPORT_JOBS`
   and build the expected inventory path set from it; the literal eight-path set goes.
6. **Check 42 and the export fixture** (`tests/checks/core/42_exports_fixtures.py`, `tests/fixtures/exports/`).
   `universes.json` declares `all_rmsk` (`{"name": "all_rmsk", "predicate": {}, "provisional_classes": []}`) beside
   the two existing universes. New expected file `tests/fixtures/exports/expected/all_rmsk/record.bed`, hand-authored,
   six rows in this order:
   ```
   chr1	4	9	Excluded|chr1:5-9|+	7	+
   chr10	0	1	Mystery|chr10:1-1|+	9	+
   chr10	8	12	Opaque|chr10:9-12|-	1000	-
   chr2	9	20	A|chr2:10-20|+	1000	+
   chr2	9	20	B|chr2:10-20|+	50	+
   chr2	29	35	A|chr2:30-35|-	42	-
   ```
   `expected/export_feature_members.tsv` gains six rows after the existing forty, in the same record order:
   `all_rmsk	full	record	rmsk_record_id	<id>	<id>	<start_1>	<end_1>`. The check asserts, after the stage
   run: the seven existing expected files byte-equal (unchanged), the `all_rmsk` BED byte-equal to the new expected
   file, the registration byte-equal to the expected file (46 rows; the forty interspersed rows still eight per
   record; the six `all_rmsk` rows one per catalog record), the inventory with eight rows (seven with 5 rows; the
   `all_rmsk` row with 6 rows, 6 distinct features, level `record`, universe `all_rmsk`) and every sha256 matching.
   `build_exports(scratch, "mm39")` reproduces every file byte-identically (the existing before/after assertion now
   covers eight exports). An explicit interspersed-only call writes seven exports, forty registration rows and a
   seven-row inventory into a second scratch directory. Removing `all_rmsk` from `universes.json` fails with
   `undeclared export universe`. Every existing gate stays. Success message updated. `tests/fixtures/exports/README.md`
   describes the third universe and the `all_rmsk` expected rows in two sentences.
7. **ADR 3** (`docs/DECISIONS.md` entry 3, codex A3). The delivered-scope sentence names GTF at record and subfamily
   level and adds the complete-catalog record BED under `all_rmsk`, each in the three namespaces. One sentence, affirmative.
8. **README truth table**: the rows for `tables/contig_coverage.tsv` and `bin/te-tracks-preflight` read
   `delivered, tested`; the facts live in OUTPUTS.
9. **OUTPUTS.md phase 6**: the preflight paragraph states the contract of item 1 and adds one sentence that export
   completeness against its inventory is the manifest's job; the coverage sentence says the interspersed exports name
   59 of the 61 contigs and the `all_rmsk` BED names all 61.
10. **Measurement only**: run stages 30 and 35 through the Python wrapper in the acceptance block and report the
    printed peak resident sizes; edit nothing to change them.

11. **Uniform per-file sort order** (Opus A1). Every export in every namespace is sorted by its contig column in
    C-locale byte order, start and end numerically, strand, then its own name column in byte order (BED column 4, GTF
    column 9, SAF `GeneID`). Stage 30 establishes that order for the seven UCSC files (sorting `family.bed` by the
    family bucket moves 4 rows at 3 coordinate ties; the other six already comply and their digests stay); stage 35
    preserves it under renaming. Check 61 drops its `ucsc` `family.bed` exception and asserts the order on every file;
    check 40 follows if it asserts an order. `docs/OUTPUTS.md` phase 4 states the sort in these terms. The `ucsc`
    `family.bed` digest and its inventory row change; every other digest and the registration stay. The export
    fixture's expected `family.bed` stays byte-identical (its one coordinate tie shares a bucket); report otherwise.
12. **Stage 30 log line for the `all_rmsk` pass** (Opus A2): report the counts that pass emits (records, exports,
    registrations); the instance figure and the zero subfamily, family and triple counts go.
13. **Docstring of `build_namespaces`** in `src/lib/contigs.py` (Opus A3): renamed files add inventory rows and no
    registration rows; say so.
14. **OUTPUTS.md phase 4 opening** (Opus A4): the sentence beginning "All seven exports land under" becomes the
    eight-file statement (seven interspersed files plus the `all_rmsk` record BED under `exports/ucsc/all_rmsk/full/`).
15. **Check 60's fixture pin** (Opus A5): the check asserts a literal sha256 of
    `tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv` (compute it, paste it) and reads nothing under
    `docs/_internal/`.
16. **Preflight alias table location** (Opus A6): walk up from the export path as given (made absolute, symlinks
    unresolved) to the nearest `tables/contig_aliases.tsv`; print a fourth report line `alias_table\t"<path>"` after
    the three lists; check 62 parses and asserts it.
17. **Check 61 becomes total** (Opus A7): for each of the sixteen renamed files, regenerate the file in scratch from
    its `ucsc` source through the alias mapping and the sort of item 11, and compare sha256 with the file and the
    inventory; the 10,000-row sample goes. Budget about two minutes.

## Touch list (exact)
`bin/te-tracks-preflight`, `src/lib/build_exports.py`, `src/lib/contigs.py`, `tests/lib/consumers.py` (one call),
`tests/checks/core/40_exports_shape.py` (only its order assertion, if any), `tests/checks/core/42_exports_fixtures.py`,
`tests/checks/core/60_contig_aliases.py`, `tests/checks/core/61_namespace_exports.py`, `tests/checks/core/62_preflight.sh`, `tests/fixtures/exports/universes.json`,
`tests/fixtures/exports/expected/all_rmsk/record.bed` (new), `tests/fixtures/exports/expected/export_feature_members.tsv`,
`tests/fixtures/exports/README.md`, `docs/OUTPUTS.md`, `docs/DECISIONS.md`, `README.md`.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot PYTHONDONTWRITEBYTECODE=1
B=$TE_TRACKS_REFROOT/te_mm39/build; V=/workspaces/Meta-Aging/_scratch/te-tracks-audit/p6_verify
for f in build.sh lib/common.sh src/*.sh tests/run.sh bin/te-tracks-preflight; do bash -n "$f" 2>/dev/null || python3 -m py_compile "$f"; echo "syntax ok $f"; done
python3 - <<'PY'
import os, resource, subprocess, time
build = os.environ["TE_TRACKS_REFROOT"] + "/te_mm39/build"
for stage in ("30_build_exports", "35_build_namespaces"):
    started = time.time()
    run = subprocess.run(["bash", f"src/{stage}.sh", build, "config/mm39.env"])
    print(stage, "exit", run.returncode, "seconds", round(time.time() - started),
          "maxrss_children_kib", resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss, flush=True)
PY
diff "$B/tables/exports.tsv" "$V/exports_before_fix.tsv"; echo "expect exactly the exports/ucsc/interspersed/full/family.bed row to differ"
sha256sum "$B/tables/export_feature_members.tsv.gz" "$B/tables/contig_aliases.tsv" "$B/tables/contig_coverage.tsv"; cat "$V/before_fix.sha"   # digests equal the snapshot
LC_ALL=C sort -c -s -t "$(printf '\t')" -k1,1 -k2,2n -k3,3n -k6,6 -k4,4 "$B/exports/ucsc/interspersed/full/family.bed" && echo "ucsc family.bed sorted by its name column"
F=tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv
for u in interspersed all_rmsk; do for ns in gencode ucsc ensembl; do echo "-- $ns $u"; bin/te-tracks-preflight "$B/exports/$ns/$u/full/record.bed" "$F" | python3 -c 'import sys,json; [print(" ", l.split("\t")[0], len(json.loads(l.split("\t")[1]))) for l in sys.stdin]'; echo "  exit=${PIPESTATUS[0]}"; done; done
grep -P '^chr([0-9]+|X|Y)\t' "$B/source/mm39.chrom.sizes" > /workspaces/Meta-Aging/_scratch/te-tracks-audit/p6fix/ucsc21.sizes
bin/te-tracks-preflight "$B/exports/ensembl/interspersed/full/record.gtf" /workspaces/Meta-Aging/_scratch/te-tracks-audit/p6fix/ucsc21.sizes | cut -c1-80; echo "exit=${PIPESTATUS[0]}"   # 1
bin/te-tracks-preflight "$B/exports/ucsc/interspersed/full/subfamily.saf" /workspaces/Meta-Aging/_scratch/te-tracks-audit/p6fix/ucsc21.sizes | cut -c1-80; echo "exit=${PIPESTATUS[0]}"   # 2
tests/run.sh core; echo "exit=$?"          # 16 pass
tests/run.sh consumers; echo "exit=$?"     # 8 pass, 5 unsupported, exit 0
git status --short
```
Expected preflight exits against the FASTA list: gencode 0/0, ucsc 2/2, ensembl 2/2 (interspersed/all_rmsk), with the
list sizes stated in item 3.

## Final message
Every file created or changed; acceptance outputs verbatim; the two peak resident sizes; any deviation from a stated
number or from the touch list, named.
