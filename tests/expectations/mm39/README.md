# mm39 acceptance anchors

Acceptance compares fresh archives with reviewed source/census oracles and earlier-output
reproduction pins. Each mismatch is a deviation for investigation.

| Expectation | Evidence kind | Carrier |
|---|---|---|
| `source_pins.tsv` | External source pins | Reviewed configs and the phase 9b prompt. |
| `source_qualification.tsv` | Independent source comparison | Phase 1 qualification and milestone 2 recomputation against UCSC `rmsk`. |
| `class_census.tsv`, `universe_summary.tsv` | Independently derived census | Phase 2 plans and three derivations in milestone 2 ruling A5. |
| `taxonomy_census.tsv` | Authored rules and external oracle | Phase 3 plan, instance-weighted fixtures and the pinned 20-name Dfam oracle. |
| `dfam_census.tsv` | External metadata and catalog census | Phase 9a plan and pinned Dfam 4.0 snapshot. |
| `record_census.tsv` | Reviewed census | Phase 9a record/instance measurements in `docs/OUTPUTS.md` and plan 19. |
| `exon_subtraction_summary.tsv` | Independent geometry census | Phase 8 plan and reviewer recomputations. |
| `gene_oracle.tsv` | Earlier independent bedtools anchors | [Phase 8 codex review](../../../docs/_internal/redesign-2026-09/reviews/p8_codex.md), [Opus review](../../../docs/_internal/redesign-2026-09/reviews/p8_opus.md) and [rulings](../../../docs/_internal/redesign-2026-09/reviews/p8_rulings.md). |
| `gene_oracle_m9.tsv` | New independent bedtools anchors | Milestone 9 fix run on chr7 and the orchestrator's own reproduction of every value; logs at `../../../docs/_internal/redesign-2026-09/measurements/m9fix/`. |
| `identity.tsv` IDs | Prior-output fingerprints | Earlier development identities preserved in the phase 9b prompt before acceptance. |
| `identity.tsv` roster counts | Authored contract census | Phase 9a 52-file core and phase 8 21-file child rosters. |
| File-size literals in acceptance checks | Prior-output fingerprints | Earlier development outputs retained in `docs/RELEASES.md` and phase 9a rulings. |

The checks retain the authored 49-family census, the external 1,278-clade census and all
reproduction pins, including the 15,301,538,537-byte core payload. BUILD_ID discrepancies
remain fatal. Live development-table digest and ID comparisons run when those builds exist;
`identity.tsv` pins are checked on every publication acceptance run.

Before this fix, `gene_oracle.tsv` held eleven data rows: ten of the eighteen printed metrics
and one annotation-absence pin. Six added pins come from the earlier bedtools records: chr18
input records and union bp, and the random contig's exon rows, union intervals, union bp and
retained bp. Its zero exon count follows from the recorded absence of annotation. Earlier
internal reviews and rulings supply no chr18 or chr19 exon-row literal; the orchestrator measured
both with its own bedtools pipeline and they are pinned in `gene_oracle_m9.tsv`. The chr7 pins in that
file are new anchors from this fix, reproduced value for value by that same independent pipeline. Every
metric the oracle prints is pinned.
