# te-tracks phase 9b: acceptance, runbook and parking

You are the implementer for phase 9b of the te-tracks redesign, the last implementation phase before the
package is parked. Working directory (absolute): `/workspaces/Meta-Aging/01_modules/te-tracks`, git branch
`redesign-2026-09`, HEAD `__HEAD__`. Phases 0 to 9a have landed. This prompt supersedes `p9_impl.md`.

Read `AGENTS.md`, `README.md`, `build.sh`, `src/`, `tests/`, `docs/*.md`, the plan file
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/19_phase9_acceptance_park.md` (which carries the
milestone 2, 5 and 7 rulings that land here) and the rulings files
`docs/_internal/redesign-2026-09/reviews/{m2,m5,m7,p8,p9a}_rulings.md`.

The purpose of this phase, stated so you can judge your own work against it: the package is being parked in a
state where a downstream consumer can build it once on the host and then quantify transposable elements for
three single-cell and single-nucleus datasets and one bulk RNA-seq dataset without asking anyone a question.
Everything you write is read by that consumer.

## What phase 9a added, which acceptance must now cover

| artifact | shape |
|---|---|
| `exports/{ucsc,ensembl,gencode}/interspersed/full/record_starsolo.gtf` | 3,764,949 rows and distinct `gene_id` each, 59 contigs, twelve ordered attributes |
| `tables/taxonomy_dfam.tsv` | 1,221 lines; `match_status` 1,047 exact, 147 part_model_set, 26 missing |
| `tables/taxonomy_dfam_models.tsv`, `tables/dfam_lineage_nodes.tsv`, `tables/dfam_model_clades.tsv` | 1,264, 301 and 1,279 lines |
| `data/dfam/` | the tracked snapshot, its provenance and its fetch script; snapshot sha256 `ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f` |
| core identity | 51 inventory entries, 27 export contracts, five `build_sources` roles, `catalog.sources` still `['rmsk_out']` |
| core payload | 15,301,535,164 bytes |

The development build ids at this HEAD are core `763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c`,
child `693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0`, and `CATALOG_ID`
`90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` in both. A fresh build from the same tree
must reproduce all three.

## Deliverables

1. **`tests/checks/acceptance/`**, a full in-container acceptance suite running against a fresh build of both
   families into `$TE_TRACKS_REFROOT/acceptance/` (`--root` mode: `te_mm39` then `te_mm39_gene`), comparing
   every measured number from phases 1 to 9a against `tests/expectations/mm39/`. Expectation files are
   authored independently of the build under test: copy nothing from a build output into them, and where a
   number exists only in a build table, state the expected value literally in the check. One check per area:
   `10_source`, `20_records_universes`, `30_taxonomy`, `35_taxonomy_dfam`, `40_exports`,
   `45_record_profile`, `60_namespaces`, `70_publication`, `80_gene_child`, `85_gene_child_oracle`,
   `90_legacy_reconciliation`. Each exits 3 with `unsupported: run tests/run.sh acceptance --build` when the
   acceptance root lacks the builds. Add `tests/run.sh acceptance --build`, a flag the runner passes as
   `TE_TRACKS_ACCEPTANCE_BUILD=1` so the first check performs the two builds.
2. **`85_gene_child_oracle`** (plan 19, from the phase 8 review's codex A2): recompute the exon union and the
   exon-subtracted blocks with `bedtools merge` and `bedtools subtract` for two whole chromosomes and one
   record-bearing contig without gene annotation, from the child's retained GTF and the parent's
   `interspersed` record BED, and require the block multiset over `(start, end, strand, name)` to equal the
   rows of the child's `exports/ucsc/interspersed/exon_subtracted/subfamily.saf` on those contigs. Report
   unsupported naming `bedtools` when the binary is absent. The oracle must be your own bedtools pipeline,
   never a call into `src/lib/gene_child.py`.
3. **`90_legacy_reconciliation`** (milestone 2 ruling H1, corrected by milestone 7 divergent H4): the
   `compat_tetranscripts_mm39` membership count equals the 3,799,629 data lines of the packaged
   `GRCm39_Ensembl_rmsk_TE.gtf.gz`, md5 `1d6770be131fc1b47402a633f4401cbd`, under
   `/data2/users/shared/refcache` (read-only; exit 3 naming the path when absent), and the check reports the
   interval-set difference when the counts differ. No legacy SAF exists on disk; do not look for one.
4. **`70_publication`** also compares the acceptance build's table digests, `CATALOG_ID` and `BUILD_ID` with
   the development build under `$TE_TRACKS_REFROOT/te_mm39/build` when present (milestone 2 ruling H6: same
   image, same ids), and states the remedy when they differ (milestone 7 ruling M5): a `CATALOG_ID`
   difference stops for investigation, while a `BUILD_ID` difference with an equal `CATALOG_ID` publishes the
   host build with the in-container build recorded as its content witness.
5. **`docs/RUNBOOK.md`**, which already exists from phase 8 and is extended rather than replaced, gains the
   host-build section: the host build runs inside this devcontainer image with the refcache mounted writable
   (ruling H6); prerequisites and versions read from the container and stated exactly (python3, pyarrow,
   pandas, numpy, pysam, zlib, bash, coreutils, bedtools); the measured producer floor (state the peak
   resident bytes you observe for the export writer and the child subtraction) and about 15.3 GB of payload
   per core build plus the child; the writable host root `/data2/users/shared/refcache` against the
   read-only container mount; the source cache seeded from the container's retained copy under
   `_scratch/te-tracks-audit/source/`, with a checksum mismatch stopping for a re-pin decision (ruling L4),
   and a note that `data/dfam/` is a tracked package input needing no fetch; `build.sh --genome mm39 --root
   <refroot>` then the child with `--config config/mm39_gene.env --root <refroot>`; verification with
   `python3 src/release.py verify-current --root <root> --family te_mm39` and the same for `te_mm39_gene`
   (milestone 7 codex A3); publication requiring `builder_git_dirty` false and a fresh complete `--root`
   build (ruling M2); after publication the family root and `archive/` tightened to owner-only write, or the
   group write stated as the publisher policy, with the host backup named (milestone 7 divergent M1);
   transfer to the CRI root `/gpfs/data/rathmell-lab/data/refdata` by staging and `install`; interruption
   recovery; resolving `current` once per consumer operation and pinning the resolved id; a measured floor
   per consumer projected from a 50,000-row head of `record.gtf` through Stellarscope's
   `IntervalTreeAnnotation` and TElocal's `TEindex`, stating the per-row cost and the projection (milestone 5
   ruling H3); consumer installs pinned to the vendored checkout commits from `git describe`, or the
   divergence recorded (ruling M4); the barcode-threshold audit named as the consumer's (ruling M6).
6. **A consumer map** in `docs/OUTPUTS.md`: one table binding each published artifact to the consumer that
   reads it and the counting question it serves. It must state plainly that the exon-subtracted SAF is the
   bulk featureCounts product, that the expectation-maximization routes take the unmasked record exports with
   the full gene annotation, that `record.gtf` carries the subfamily grammar TEsingle and TElocal consume,
   that `record_starsolo.gtf` carries the record-as-gene grammar STARsolo and cellranger consume, that
   IRescue reads a record or subfamily BED, and that `all_rmsk/full/record.bed` is the interval catalog the
   chromatin-accessibility ledger keys on. Name the universe each serves.
7. **`README.md`** truth table updated to `delivered` and `tested` per artifact as the acceptance run
   observed it; `AGENTS.md` final, naming the four test modes and the host-only steps;
   `docs/OUTPUTS.md`, `docs/PROVENANCE.md` (rewritten: the sources, the qualification summary, the measured
   numbers, the class census, the taxonomy rule evidence, the Dfam snapshot pin) and `docs/RELEASES.md`
   accurate to the bytes the acceptance build produced, including the retention statement that every build a
   consumer pins is retained beside `current`.
8. **A parking summary** in your final message, from which the orchestrator writes the session record: both
   families' `BUILD_ID` and `CATALOG_ID` from the acceptance build; which oracles the builder did not
   produce and what each confirmed (the UCSC `rmsk` table at source qualification, the pinned Dfam snapshot,
   the packaged legacy GTF, bedtools for the child geometry); what is tested; what is unsupported and why
   (Stellarscope's boundary defect); what is deferred with the evidence its next decision needs (hg38,
   transcript context, ERV units, age tiers, the stranded mask companion, the 10x-annotation child, the
   instance-level STARsolo profile); the RNA qualification limits for the pilot (TEsingle's paired-mate
   handling, its UMI graph and hard ties; Stellarscope's boundary and largest-overlap preselection;
   IRescue's even-start expectation-maximization); and the next gates.

## Rules
- Touch only: `tests/checks/acceptance/**`, `tests/expectations/mm39/**`, `tests/run.sh` (the `--build`
  flag), `docs/RUNBOOK.md`, `docs/PROVENANCE.md`, `docs/RELEASES.md`, `docs/OUTPUTS.md`, `README.md`,
  `AGENTS.md`.
- No git writes of any kind. No installs. No network. Never write into `/data2/users/shared/refcache`.
- Weaken or delete no existing test. If an existing check blocks you, name it and report.
- Report a deviation instead of editing a number or an expectation to fit an observation.
- Scratch under `_scratch/te-tracks-audit/p9b/`, removed with Python `shutil.rmtree`; `/tmp` is noexec.
- Export `PYTHONDONTWRITEBYTECODE=1` in every shell.
- Prose affirmative, comments state intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
rm -rf "$TE_TRACKS_REFROOT/acceptance"
time tests/run.sh acceptance --build; echo "exit=$?"
tests/run.sh acceptance; echo "exit=$?"
tests/run.sh core; echo "exit=$?"
source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh
tests/run.sh consumers; echo "exit=$?"
cat "$TE_TRACKS_REFROOT/acceptance/te_mm39/current/BUILD_ID" \
    "$TE_TRACKS_REFROOT/acceptance/te_mm39/current/CATALOG_ID" \
    "$TE_TRACKS_REFROOT/acceptance/te_mm39_gene/current/BUILD_ID" \
    "$TE_TRACKS_REFROOT/acceptance/te_mm39_gene/current/CATALOG_ID"
grep -c "delivered" README.md; grep -c "deferred" README.md
git status --short
```
The acceptance build takes about fifty minutes for both families. The core ids it produces must equal the
development ids quoted above; report a difference rather than adjusting anything.

## Final message
Every file created or changed; the acceptance outputs verbatim; both families' ids from the acceptance build
compared with the development build; the legacy reconciliation result; the child geometry oracle result on
each contig it used; the parking summary of deliverable 8; every deviation.
