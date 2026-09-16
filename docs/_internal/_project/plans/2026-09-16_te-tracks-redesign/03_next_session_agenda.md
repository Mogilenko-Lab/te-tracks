# Next session starts here

1. Read `00_INDEX.md`, `01_decisions.md`, `02_orchestration.md`, then
   `../../../redesign-2026-09/consults/FINAL_REPORT.md` for the reasoning behind every decision.
2. Taxonomy needs no owner input: phase 3 derives canonical labels by rule and checks them against
   the Dfam snapshot in `redesign-2026-09/taxonomy/` (its `README.md` explains the evidence).
3. Run phase 0 through phase 2 with the protocol in `02_orchestration.md`, then the first
   milestone review.
4. Continue phases 3 to 7, milestone reviews after 5 and 7.
5. Phase 8 lands the gene child seam only. Open a dedicated design session for transcript context
   before any context table is written.
6. Phase 9 parks the release: full acceptance in a scratch root in-container, host build and
   publication by the owner, verification of the published bytes, handoff record.
7. Then D2 and D3 agents resume against the published `BUILD_ID`.

Open items carried into the session: install decisions for consumer executables (irescue,
featureCounts, Stellarscope, TEsingle, TEtranscripts, TElocal) so phase 5 execution fixtures run as
`supported`; the two remaining name choices are settled (short names, `_derived`,
`compat_`); hg38 is deferred.
