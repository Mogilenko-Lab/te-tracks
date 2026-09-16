# te-tracks — implementation in progress (orchestration session 2026-09-16)

## Where the work stands

Branch `redesign-2026-09` in te-tracks, baseline commit `270afd4` (plan, audit, consults, taxonomy
evidence). The owner ruled on 2026-09-16: no manual taxonomy curation; phase 3 derives canonical labels
by `taxonomy_rule_v1` and checks them against the pinned Dfam snapshot in a test. The owner also
authorized fan-out without per-agent permission prompts and the per-phase commits (see
`plans/2026-09-16_te-tracks-redesign/02_orchestration.md`, "Standing authorizations").

**Phase 0** (decisions, scaffold, truth table, `tests/run.sh`) is complete and committed on the
branch. Loop: implemented by codex (`te-tracks-p0-impl`); codex review `reviews/p0_codex.md` (BLOCKING:
incomplete truth table, over-broad export promise, runner skipping non-executable checks, legacy
artifacts without disposition); fix `te-tracks-p0-fix`; Opus re-review `reviews/p0_opus.md` (FAIL:
`taxonomy_triple.saf` described with raw labels where the contract emits canonical ones, and the ADR 5
ledger sentence read as three te-tracks deliverables; seven advisories on the preflight signature, the
`docs/RELEASES.md` row, runner wording, dangling symlinks, relative `--refroot`, swallowed diagnostics);
fix `te-tracks-p0-fix2` from `prompts/p0_fix2.md` (all nine items); orchestrator re-verification
(runner exits 1/1/0/1/1/2 on fail, required-unsupported, unsupported, hidden `.py`, dangling symlink,
missing dir; relative `--refroot` exported absolute; failures print full stdout to stderr; negation
grep clean; no git write in any reachable repo). The phase 0 commit also carries the plan edits (ADR 3
enumerates the export matrix; ADR 5 ledger sentence; phase 4 adds `taxonomy_triple.saf`; phase 6 adds
the `gencode` contig namespace; phase 8 ships the child SAFs in all three namespaces), `audit/AUDIT.md`
§6 with `audit/gencode_grcm39_fasta_contigs.tsv`, both reviews and `redesign-2026-09/prompts/`.

**Measured this session.** The GENCODE GRCm39 FASTA the lab aligns against names chromosomes
UCSC-style and scaffolds by GenBank accession (22 + 39 of 61 contigs); hence the third namespace
`gencode`. All-record taxonomy: 18,484 names, 18,504 triples, 1,201,573,004 bp summed length.

## Next session starts here

1. Phase 1: launch `launch.sh --unit te-tracks-p1-impl --workdir <te-tracks> --effort xhigh --prompt
   docs/_internal/redesign-2026-09/prompts/p1_impl.md` as a harness background task; on completion read
   `status.sh --unit` (codex_exit; launcher exit 32 is the blind-run detector's false positive) and the
   final message; re-run the acceptance block yourself; fill `review_template.md` (N=1, phase file
   `11_phase1_source.md`, paste the report) and launch `te-tracks-p1-review` writing
   `reviews/p1_codex.md`; then the `opus-reviewer` agent from `opus_template.md`, saved as
   `reviews/p1_opus.md`; fix loop through `prompts/p1_fix.md`; commit "Phase 1: pinned .out source,
   parser profile, qualification".
2. Phase 2 the same way (`p2_impl.md`), then the **milestone review**: three parallel read-only reviewers
   with disjoint questions (codex on schema and identity; Opus on numbers and fixtures; `divergent` agent on
   silent assumptions), each writing one file under `reviews/m2_*.md`.
3. Phases 3 to 9 follow with `p3_impl.md` … `p9_impl.md`; milestone reviews after 5, 7, 9; the owner runs
   the host build at phase 9 (`docs/RUNBOOK.md`), the orchestrator verifies the published bytes and records
   the `BUILD_ID`s here; then the umbrella pin bumps and D2/D3 resume.

Prompts p1 to p9 carry pre-measured acceptance numbers; the plan files are authoritative where a prompt
and a plan file disagree, and the disagreement is a deviation to report.

## Open at handoff

- Consumer executables absent in-container; phase 5 reports them `unsupported` until the owner decides
  installation (irescue, featureCounts, Stellarscope, TEsingle, TEtranscripts, TElocal).
- TElocal prepackaged annotation tables (Dropbox) not fetched; reconciliation belongs to the
  `compat_tetranscripts_mm39` fixture.
- Gene context stays a seam (phase 8); its design session follows.
- Deferred and recorded: hg38, ERV units, young/old tiers.
