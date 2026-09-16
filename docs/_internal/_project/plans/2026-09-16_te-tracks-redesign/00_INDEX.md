# te-tracks redesign: park a verified mm39 reference (plan, staged 2026-09-16)

Owner rulings (2026-09-16): short universe names; hg38 deferred; canonical taxonomy derives from
the source labels by a versioned rule and is checked against a pinned Dfam snapshot, with no manual
curation step; `family.bed` and Ensembl-named exports are in the first release; gene context sits
behind a seam and gets its own design session. Evidence and reasoning live in
`../../../redesign-2026-09/` (audit, consults, taxonomy) and are summarized in
`redesign-2026-09/consults/FINAL_REPORT.md`.

## Phases

One phase, one implementer, one review pair. Milestone reviews after phases 2, 5, 7 and 9; phase 3
adds a `divergent` pass on the rule.

| # | file | phase | seam it closes |
|---|---|---|---|
| 0 | `10_phase0_decisions_scaffold.md` | ADRs, AGENTS.md, README truth table, `.gitignore`, test runner skeleton | public contract |
| 1 | `11_phase1_source.md` | `.out` parser profile, revised config, fetch, source qualification vs UCSC table | source identity |
| 2 | `12_phase2_canonical.md` | `rmsk_records` (24 cols), instance members, raw taxonomy, `universes.json`, membership | **canonical identity (milestone review)** |
| 3 | `13_phase3_taxonomy.md` | `taxonomy_rule_v1` to `taxonomy_canonical`, rank statuses, Dfam agreement test | rollup safety |
| 4 | `14_phase4_exports.md` | `interspersed` UCSC exports: record, subfamily, family BED; record GTF; subfamily SAF; `export_feature_members` | feature identity |
| 5 | `15_phase5_consumer_fixtures.md` | synthetic fixtures, parser and execution tests per consumer, Stellarscope gate | **consumer seam (milestone review)** |
| 6 | `16_phase6_ensembl_preflight.md` | Ensembl-named exports, alias table, coverage report, preflight command | external bulk handoff |
| 7 | `17_phase7_publication.md` | two-section manifest, BUILD_ID, staging, install, symlink, transfer, smoke tests | **publication seam (milestone review)** |
| 8 | `18_phase8_gene_child_seam.md` | `te_mm39_gene` skeleton, parent pin, exon-subtracted SAF only, transcript context deferred | gene seam |
| 9 | `19_phase9_acceptance_park.md` | full mm39 acceptance, host runbook, docs truth, parking handoff | **park (final review)** |

`01_decisions.md` carries the eight ADR texts to land in phase 0. `02_orchestration.md` is the
implementer, review and re-review protocol. `03_next_session_agenda.md` is where the next
session starts.

## Standing constraints

- The refcache is read-only inside the container. Builds and publication run on the host; every
  phase's tests run in-container against a scratch reference root.
- Tools absent in-container today: irescue, featureCounts, TElocal, TEtranscripts, Stellarscope,
  TEsingle, MATES executables. Phase 5 declares each consumer test `supported` or `unsupported`
  by tool availability; the owner decides installation. Parsers are always testable from the
  local checkouts under `01_modules/.ref/`.
- No commit without the owner's word. Implementers never run git writes; the orchestrator commits
  per phase with an affirmative message and no AI attribution.
- Prose in every public file: affirmative, brief, no contrastive negation.
