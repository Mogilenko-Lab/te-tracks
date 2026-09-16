# te-tracks milestone review after phase 5: consumer seam (codex, read-only)

You review the committed state of the te-tracks redesign after phases 0 to 5. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, commit `__HASH__`. You
write exactly one file: `docs/_internal/redesign-2026-09/reviews/m5_codex.md`. You change nothing else. No
git writes anywhere (the consumer checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories
too), no installs, no network. Scratch work goes under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex/`
and is removed when you finish; the orchestrator's build at
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` is read-only for you.

Your question is the consumer seam: does feature identity survive every tool the package names, from the export
bytes through each real parser and back through `export_feature_members` to `rmsk_records`, without a later
rename of a file, an attribute or a key? Two other reviewers cover numbers and fixtures (Opus) and unstated
assumptions (divergent); leave those to them.

## Read
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/00_INDEX.md`, `14_phase4_exports.md`,
   `15_phase5_consumer_fixtures.md`, then the downstream `16_phase6_ensembl_preflight.md`,
   `17_phase7_publication.md`, `18_phase8_gene_child_seam.md`, `19_phase9_acceptance_park.md`.
2. The rulings so far: `docs/_internal/redesign-2026-09/reviews/m2_rulings.md`, `p3_rulings.md`, and any
   `p4_rulings.md` / `p5_rulings.md` present.
3. `docs/_internal/redesign-2026-09/consults/ADR5_consult.md` (attribute mapping, ledger relations, conservation
   rule) and `consults/A_consumer_contracts.md`.
4. Public contract: `README.md`, `docs/DECISIONS.md`, `docs/OUTPUTS.md`, `AGENTS.md`.
5. Code: `src/lib/build_exports.py`, `tests/lib/consumers.py`, `tests/checks/core/4*`, `tests/checks/consumers/*`,
   `tests/fixtures/exports/**`, `tests/fixtures/consumers/**`.
6. The phase reviews `reviews/p{3,4,5}_*.md`.

## Judge, with evidence
- **Feature identity per tool.** For IRescue (BED name), Stellarscope (`locus`, `instance_id`), TEtranscripts
  (`gene_id:family_id:class_id`), TEsingle and TElocal (`transcript_id:gene_id:family_id:class_id` from both
  GTFs), featureCounts (SAF `GeneID`) and bedtools: drive the vendored parser or the format reader over the mm39
  exports (a bounded sample where the parser is slow) and state the exact feature key each produces; confirm that
  key resolves through `export_feature_members` to `rmsk_record_id` and that the conservation rule (a count on a
  feature rolls up to the same total at record, subfamily and family level) holds under each tool's key.
- **Two GTF grains.** `record.gtf` and `subfamily.gtf` differ only in `transcript_id` and `locus` and the record
  attributes; judge whether any parser reads an attribute the other file lacks, and whether the contract states
  which tool reads which.
- **The registration as the ledger's join.** `(universe_name, variant, feature_level, emitted_feature_id)` keys the
  registration, namespace-invariant. Judge whether phase 6's renamed-contig copies and phase 8's split pieces
  (`block_start_1`, `block_end_1`) fit that key without a new column, and whether `exports.tsv` supplies phase 7's
  `export_contracts` identity input.
- **Unresolved tokens.** `unresolved_class_<name>` and `unresolved_family_<name>` in `family.bed`, both GTFs and
  the triple SAF: judge every parser's treatment of `_` and the positional grammar; mm39 has none, so reason from
  the fixture.
- **Support honesty.** `tests/run.sh consumers` reports `supported` or `unsupported` per tool. Judge whether an
  absent executable, a missing Python dependency of a checkout and a known upstream defect (Stellarscope's right
  boundary) each land on the right status with the right reason, and whether a future install flips the
  execution-level checks on without edits.
- **Namespace and child readiness.** What phase 6 must add so a renamed-contig export registers to the same
  features; what phase 8 must add so a split piece registers to its record; anything in the phase 4 or 5 code that
  hardcodes `ucsc`, `interspersed` or `full` where the later phases need a parameter.

## Output format (the review file)
```
# Milestone 5 review: consumer seam (codex gpt-6-astra)
Verdict: PASS | PASS WITH ADVISORIES | BLOCKING
## Blocking
- [B1] <file:line> <finding> — <evidence> — <what fixes it, and in which phase>
## Advisory
- [A1] ...
## Evidence
<commands and outputs, verbatim, for every measured claim>
## Scope check
<git status before and after, in te-tracks and in each checkout under .ref; files you wrote>
```
BLOCKING means a later phase or a consumer cannot proceed without changing a published file, attribute or key.
Keep the file under 200 lines. Facts over opinions; every finding cites a path and, where possible, a line.
