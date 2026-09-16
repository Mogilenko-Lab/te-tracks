# te-tracks phase 0: fix loop after review

You are the implementer for phase 0 of the te-tracks redesign, returning to fix review findings. Working
directory (absolute): `/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Your
earlier work is in the working tree (uncommitted): `README.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`,
`docs/DECISIONS.md`, `docs/OUTPUTS.md`, `tests/run.sh`, `tests/checks/*/.gitkeep`.

Read the review first: `docs/_internal/redesign-2026-09/reviews/p0_codex.md`. Then the phase contract
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/10_phase0_decisions_scaffold.md` and the
updated ADR texts in `01_decisions.md` (entry 3 now enumerates the export matrix). Wording rules:
`/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".

## Resolutions (the orchestrator's rulings; implement exactly)
- **B1, truth table completeness.** Add rows for every non-export artifact the phase files promise:
  `source/qualification.md` and `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md`
  (phase 1), `tests/fixtures/source/` (1), `tests/fixtures/records/` (2), `tests/expectations/mm39/`
  (2, 9), `tests/fixtures/taxonomy/dfam_snapshot.tsv` + `.provenance.json` and `rule_cases.tsv` (3),
  `tests/fixtures/exports/` (4), `tests/fixtures/consumers/` and `tests/lib/consumers.py` (5),
  `tests/fixtures/contigs/` (6), `tests/fixtures/publication/` (7), `tables/universe_summary.tsv` (2),
  `tables/export_summary.tsv` (4), `exports/ucsc/interspersed/full/taxonomy_triple.saf` (4), the
  `ensembl` and `gencode` namespace copies of all six exports (6). Move the generic path grammar line out
  of the table into the sentence above it. Keep one row per artifact or per fixture directory.
- **B2, release promise.** Replace `docs/DECISIONS.md` entry 3's first sentence with the enumerated text
  now in `01_decisions.md` entry 3 (BED at record, subfamily and family level; GTF at record level; SAF at
  subfamily level and at the legacy taxonomy-triple grouping; each in `ucsc`, `ensembl` and `gencode`).
  Update the README truth table and Guarantees to the same matrix (three namespaces; six files each).
- **B3, runner discovery.** `tests/run.sh` discovers checks by name, `tests/checks/<mode>/*.sh` and `*.py`
  in sorted order, regardless of mode bits; runs `.sh` through `bash` and `.py` through `python3`
  (so the executable bit is a convenience, never a gate); a missing check directory is a runner error
  (message, exit 2); an existing directory with no checks still reports zero checks and exits 0.
  Print the discovery rule in the usage text. Re-run the reviewer's scratch harness cases yourself
  (under `/workspaces/Meta-Aging/_scratch/`, the `/tmp` filesystem is noexec) and paste the outputs: failing
  check → 1; plain unsupported → 0; required unsupported `.sh` and `.py` → 1; continue after failure;
  non-executable `hidden.required.py` exiting 1 → reported `fail`, exit 1; missing directory → exit 2.
- **B4, legacy planned artifacts.** Add to `docs/OUTPUTS.md` a table "Legacy names and their
  disposition" with one row each: `te_subfamily.saf` → `subfamily.saf` (phase 4); `te_locus.saf` → a
  record-level SAF enters a release with a named consumer and a fixture (ADR 3), record-level counting
  reads `record.bed` or `record.gtf`; `te_subfamily.bed` → `subfamily.bed`; `te_locus.bed` → `record.bed`;
  `te_subfamily.gtf` and `te_locus.gtf` → `record.gtf` (one GTF; consumers group by attribute);
  `te_locus.locInd` → `record.gtf` read as `.locInd` (fixture, phase 5); `te_subfamily_noExon.saf` →
  `exon_subtracted/subfamily.saf` in `te_mm39_gene` (phase 8); `te_context_*.saf` and
  `locus_context.tsv` → deferred to the transcript-context design session after phase 8;
  `rename_map.tsv` → superseded by `taxonomy_triple.saf` and the `compat_tetranscripts_mm39` universe;
  `te_loci.parquet` → `tables/rmsk_records.parquet` (phase 2); `ensembl_named/` → `exports/ensembl/`.
- **A1, history framing.** State the current outputs directly: "The current build generates
  `te_loci.tsv.gz`, `te_dim.tsv`, `MANIFEST.json` and `BUILD_ID`; the redesign replaces them." Remove the
  commit hash from README.md and docs/OUTPUTS.md.
- **A2.** Add the title line `# Decisions` to `docs/DECISIONS.md`.

## Rules
Touch only the phase 0 files named above. No git writes, installs or network. Report a deviation instead
of editing a plan file or a review file.

## Acceptance (run and paste verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
tests/run.sh core; echo "exit=$?"
tests/run.sh bogus; echo "exit=$?"
grep -n -E "\bnot\b|rather than|instead of|never|no longer|6ff3ee9" README.md AGENTS.md docs/DECISIONS.md docs/OUTPUTS.md || echo "no hits"
head -1 docs/DECISIONS.md
grep -c "^| " README.md      # truth table rows, report the number
git status --short
```
plus the scratch harness outputs for B3.

## Final message
Each finding with what changed (file and line range); acceptance and harness outputs verbatim; any
deviation.
