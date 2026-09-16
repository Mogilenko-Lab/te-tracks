# Phase 4 rulings (orchestrator, 2026-09-16, implementer tree over `ba6682e`)

Inputs: `p4_codex.md` (BLOCKING: B1; A1 to A3), `p4_opus.md` (appended when it lands). Orchestrator
verification before the reviews: thirteen core checks; an independent recount over all 3,764,949 `interspersed`
records reproduces every export (offsets, names, clipped scores, 49 family buckets, 1,220 triple GeneIDs, GTF
attribute order and values on a thousand-row sample of each GTF, seven inventory digests, two id spellings per
record in the registration, no character outside the component alphabet); stable digests and git untouched.

## Codex

- **B1 DuckDB conservation query.** The plan asked for the conservation fixture "as a DuckDB query in tests" and
  the prompt asked for pandas because DuckDB is absent in this container. Ruling: pandas is the in-container proof;
  the same query lands in `tests/checks/consumers/30_registration_duckdb.py`, which exits 3 naming the module where
  `duckdb` is absent and runs the query where it is present (the host at phase 9 and the ledger's own environment).
  Plan 14 amended to state both.
- **A1 README guarantee counts six files.** Fix: seven files, both GTF grains named, in every README sentence that
  counts or lists the exports.
- **A2 conservation fixture leaves its target unused.** Fix: the fixture asserts the intended target per feature
  and the rolled-up totals at each level, so a wrong registration fails the fixture and a wrong target fails too.
- **A3 reserved prefix unenforced.** A resolved canonical label that begins with `unresolved_` would pool with a
  generated token. Fix: the exporter rejects any resolved canonical token beginning with `unresolved_`, with a
  fixture; OUTPUTS.md states the reserved prefix.

## Opus (PASS WITH ADVISORIES; O1, O2, A1 to A5)

Every export and both tables regenerated bit-identically from the canonical tables with independent code;
every acceptance number confirmed; five gates broken on demand; probe (h) shows the conservation fixture
catches every registration corruption at its multiplicity assertion and none of the target values.

- **O1, O2** are the two rulings entered during the review (DuckDB check, reserved prefix); both land in the fix.
- **A1 to A3** agree with codex; in the fix.
- **A4 sort statement.** The contract says the five-key sort is C-locale text order; the coordinate keys sort
  numerically. Fix: OUTPUTS.md states text columns in C-locale byte order and coordinates ascending numerically,
  in both the records section and the exports section.
- **A5 writer memory.** 5.5 GB peak RSS for mm39 because the writer materializes every record before selecting
  members. Recorded in the phase 7 plan as the host floor beside the disk figure; a streaming rewrite is a
  recorded option for a later phase, since the figure is within the host.
