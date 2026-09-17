# Field review rulings (orchestrator, 2026-09-16)

Subject: te-tracks `8589873`. Inputs: `field_bioinf.md` (bioinf agent), `field_divergent.md` (divergent
agent), and the codex consult `../consults/field_practice_consult.md`. Every measured claim was recomputed
before ruling; the recomputation is section 9 of `../consults/field_practice_synthesis.md`. "Accepted"
means the finding enters the synthesis and, where it changes the plan, the ADR brief; the owner rules on
anything that changes a published contract or adds scope.

## Codex consult

Accepted in full as recommendations. Its measurements M1 to M4 reproduce exactly (Dfam coverage 20/18,484
names and 6,517 records; the L1 prefix table; `-int` partners 25,055 records in 17,947 instances; UTR
186,133 = 95,682 + 90,451; 10,247 and 46,588 overlapping records). Its M5 corrections to
`../consults/tesingle_notes.md` are confirmed from source and recorded there: unconstrained Hamming-1 UMI
components, `te_frac` from anchored TE-only and gene-only molecules, hard argmax allocation, mates appended
as alternative alignments, and the Martirosyan index built from the gene GTF alone. Its recommendations
land in the brief as C7 (RNA route and TEsingle qualification), C8 (`record_starsolo.gtf`), C10 (Dfam rank
view) and C11 (structural and end-window views), and as amendments to C3 and C4.

## Bioinf review (verdict: sound, documentation amendments)

| finding | ruling | evidence and landing |
|---|---|---|
| F1 B1 under family `Alu` | accepted | 558,808 records, 15 names, measured; note beside `family.bed` in `docs/OUTPUTS.md`, phase 9 docs |
| F2 `ERVL-MaLR`, hyphenated superfamilies | accepted | 534,111; 105,223; 13,741; 27,962 measured; same note |
| F3 ERV unit needs LTR–internal assembly ("One code to find them all") | accepted as the target for the deferred structural stage | consistent with consult M3 and divergent H4 |
| F4 locus-level EM as the default counting level | accepted as the recommendation for all three RNA datasets | consult Q2 and Q4 agree; owner rules in C7 |
| F5 gene–TE ambiguity is a field-wide open problem | accepted; `docs/DECISIONS.md` wording stays | |
| F6 H3 safeguard stays a hard constraint | accepted | already ruled in `m2_rulings.md` |
| F7 gene-body geometry beside transcript geometry | accepted | brief C4 already carries it |
| F8 MATES mouse reference is mm10 | accepted; adapter stays fixture-only | |
| F9 Stellarscope boundary defect | accepted as a tracking item before any ERV claim leans on it | `docs/OUTPUTS.md:504-506` |
| F10 IRescue is grain-agnostic | accepted | one sentence in the IRescue consumer row, phase 9 docs |
| F11 5′ chemistry pile-up is an empirical pilot question | accepted | consult Q5 agrees; consumer pilot |
| F12 full-length columns shipped, derivation deferred | accepted | |
| F13 ATAC TE-locus counting is a real gap; count Tn5 insertions | accepted | 14761 ledger design note |
| F14 ledger joins through registration for de-duplication | amended | registration carries instance membership only; record overlaps cross instances in 198,956 pairs (divergent H3), so the ledger also needs a record-overlap relation |
| F15 Multiome arm is descriptive only; paired arm carries the tests | accepted | reporting contract in the brief |

## Divergent review

| finding | ruling | evidence and landing |
|---|---|---|
| H1 duplicate registration rows across universes at `(record, rmsk_record_id)` | accepted | measured 3,764,949 `interspersed` and 5,320,771 `all_rmsk` rows; binding rule becomes `(universe_name, variant, feature_level, key_grammar)` with a join fixture; C9, phase 9 |
| H2 `record.gtf` is the subfamily GTF; no STARsolo route in the repository | accepted | grep confirms; C8 |
| H3 record ≠ locus; overlaps; constant-false `rmsk_overlap_flag` | accepted | all figures reproduce; ledger overlap relation; the flag documented as constant for this source, phase 9 docs |
| H4 instance-id solo-LTR rule over-calls and misses proviruses | accepted | 17,947 / 103,526 / 722,280 / 583,277 reproduce; structural stage, C11 |
| H5 promoter-intact filtering must be keyed on insertions; fixtures write constant consensus columns | accepted | 588 / 75 / 583 / 2,221 / 104 / 323 reproduce; `consumers.py:338` confirmed; structural stage; a truncated-consensus fixture accompanies any end-window view |
| H6 phase 8 SAF is a bulk product | accepted as a scope statement | C3 names the single-cell product as the deferred relation; README and DECISIONS say so in phase 8 |
| H7 14616 and 14782 have no written TE route | accepted | grep confirms; C7 asks the owner to name the route and grain |
| M1 no Class I/II rollup; class-less records | accepted with a corrected count | 5,893 (5,786 + 98 + 9), the review says 5,884; C10 |
| M2 subfamily record counts weight fragments | accepted; partly served | `rmsk_taxonomy.tsv` already carries `instance_count` beside `record_count`; LTR 1,105,064 records over 843,753 instances |
| M3 triple spellings drift against packaged GTFs | accepted | from the audit record; phase 9 reconciliation |
| M4 no consumer specified the sparse relation's collapse | accepted for the context session | C3 and C5 keep the collapse a consumer policy |
| M5 four-state status conflates cases | accepted | C3 amended: per-pair status with per-record roll-up |
| M6 spleen and lung counted under different gene references | corrected | both used `refdata-cellranger-GRCm39-2024-A`; only cellranger versions differ; the reconciliation is 10x 2024-A against vM37 |
| M7 fixtures cannot encode 5′ position semantics | accepted | consumer pilot measures read-end distributions; te-tracks fixtures stay reference-level |
| M8 pooled Multiome supports no condition inference | accepted | reporting contract |
| M9 Dfam snapshot has no release identity | accepted | recorded for the next refresh; C10 |
| M10 dated note on what holds from the dissertation | accepted | synthesis section 6 |
| L1 rounding policy recorded per analysis run | accepted | ledger `analysis_runs` |
| L2 divergence tiers need within-name spread and zero handling | accepted | 468,810 zero-divergence records and B1 quantiles reproduce; C11 |
| L3 annotation cannot resolve gene–TE reads | accepted | claim tier in the consuming analysis |
| L4 published root missing at review time | explained | the root had been reset for the clean republish; it now holds `archive/9ddf3622…` and `current`, verified exit 0, `.staging` empty |
| L5 consult files cite mutable paths | accepted risk, as before | pins recorded in the consult M0 |

## Deviations noted

The divergent review's Unknown/Unspecified/`DNA?` total is 5,884 against a measured 5,893. The republish
recorded `builder_git_sha 6bf9a22` rather than the `8589873` the session record expected, because the
handoff commit landed before the provenance stage ran; the tree was clean at both commits and `BUILD_ID` is
unchanged.
