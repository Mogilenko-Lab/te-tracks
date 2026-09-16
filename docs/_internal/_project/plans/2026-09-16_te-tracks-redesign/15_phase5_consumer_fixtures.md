# Phase 5: consumer fixtures

Goal: each export authorized by its real parser, with the assay layouts kept apart.

Deliverables under `tests/fixtures/consumers/`
- Synthetic contig FASTA (long enough for 1 kb windows) and synthetic exports for two records of
  one subfamily, one two-record instance, a missing-family name, and a two-triple name.
- Synthetic BAMs: 3' ARC layout (CB, UB/UR, single cDNA read), 5' PE OCM layout (mates, CB,
  UB), bulk paired-end; molecules that are unique, duplicated, multimapping, gap-only, and
  boundary-adjacent (`[99,100)`, `[100,101)`, `[109,110)`, `[110,111)` against GTF `101..110`).
- Parser-level tests from the local checkouts (always supported): IRescue `makeRmsk` and
  `chrcat` name handling; Stellarscope `_intervaltree` grouping and the boundary gate (expected
  `0,1,1,0`; current source predicts a failing final overlap, keep the assertion and label the
  consumer version unsupported until fixed upstream); TEsingle four-attribute tuple and the
  999/1,000 UR cutoff; TEtranscripts `gene_id:family_id:class_id` grain; TElocal ingestion of
  `record.gtf` as `.locInd`; MATES eight-column pair parsing (optional adapter).
- Execution-level tests (supported only where the executable exists): IRescue subfamily run
  A=2, record run 1+1, 4/2 vs 3/3 allocation; featureCounts one feature with two molecules,
  one-base feature; bedtools intersect with the coordinate-duplicate pair.
- `tests/run.sh consumers` reports supported/unsupported per tool with the version it found.

Acceptance: every parser test passes; every execution test passes or reports `unsupported` with
the missing executable named. No fixture edits an expected value to match an observed one.

Milestone review after this phase: consumer seam (feature identity survives every tool).
