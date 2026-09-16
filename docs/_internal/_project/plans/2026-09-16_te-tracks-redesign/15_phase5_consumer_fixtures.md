# Phase 5: consumer fixtures

Goal: each export authorized by its real parser, with the assay layouts kept apart.

Deliverables under `tests/fixtures/consumers/`
- Synthetic contig FASTA (long enough for 1 kb windows) and synthetic exports for two records of
  one subfamily, one two-record instance, a missing-family name, and a two-triple name.
- Synthetic BAMs: 3' ARC layout (CB, UB/UR, single cDNA read), 5' PE OCM layout (mates, CB,
  UB), bulk paired-end; molecules that are unique, duplicated, multimapping, gap-only, and
  boundary-adjacent (`[99,100)`, `[100,101)`, `[109,110)`, `[110,111)` against GTF `101..110`).
- Parser-level tests from the local checkouts (always supported, loading each checkout's modules in isolation
  from its top-level package initializer; a code path that needs a system tool, such as IRescue's `chrcat`
  needing `gawk`, names that tool as its dependency and reports `unsupported` where it is absent): IRescue
  `makeRmsk` and
  `chrcat` name handling; Stellarscope `_intervaltree` grouping and the boundary gate (expected
  `0,1,1,0`; current source predicts a failing final overlap, keep the assertion and label the
  consumer version unsupported until fixed upstream); TEsingle four-attribute tuple at record
  grain from `record.gtf` and at subfamily grain from `subfamily.gtf`, and the 999/1,000 UR cutoff;
  TEtranscripts `gene_id:family_id:class_id` grain; TElocal `.locInd` built from `record.gtf` by
  TElocal's own indexer (`TElocal_Toolkit/TEindex.py`) and loaded back through the pickle reader TElocal
  uses (milestone 2 rulings A4, H2); MATES eight-column pair parsing (optional adapter).
- Execution-level tests (supported only where the executable exists): IRescue subfamily run
  A=2, record run 1+1, 4/2 vs 3/3 allocation; featureCounts one feature with two molecules,
  one-base feature; bedtools intersect with the coordinate-duplicate pair.
- `tests/run.sh consumers` reports supported/unsupported per tool with the version it found.

Acceptance: every parser test passes, or reports the documented upstream defect (Stellarscope 1.5's right
boundary) or a named system dependency as `unsupported`; every execution test passes or reports
`unsupported` with the missing executable named; the runner exits 0 in every case. Fixture reads carry a raw
`UR` distinct from the corrected `UB` on a designated subset, reverse-strand reads on minus-strand records,
and one duplicate-flagged and one QC-fail-flagged read. No fixture edits an expected value to match an
observed one (phase 5 reviews B4, A3, A4, A7).

Milestone review after this phase: consumer seam (feature identity survives every tool).
