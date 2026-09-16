# te-tracks phase 4 review (codex, read-only)

You are an independent reviewer of phase 4 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p4_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md`
2. The decisions: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md`
3. The wording and comment rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments"
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD --stat` and the full
   diff, plus untracked files from `git status --short`.
5. The implementer's own report, pasted below under "Implementer report".

## Judge, with evidence
- **Contract conformance**: every deliverable in the phase file present at the stated path with the stated
  content; every acceptance command re-run by you with its output quoted; any number that differs from the
  contract named.
- **Fixture adequacy**: do the fixtures and checks fail when they should? Try to break one (read-only: reason
  from the code, or run it against a modified copy under /tmp).
- **Silent assumptions**: anything the code or docs assume that the contract leaves open; anything that will
  bite phase 5.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 4 review (codex gpt-6-astra)
Verdict: PASS | PASS WITH ADVISORIES | BLOCKING
## Blocking
- [B1] <file:line> <finding> — <evidence> — <what fixes it>
## Advisory
- [A1] ...
## Acceptance re-run
<commands and outputs, verbatim>
## Scope check
<git status / diff --stat summary>
```
BLOCKING means a contract deliverable is missing or wrong, an acceptance number differs, or a check cannot fail.
Keep the file under 200 lines. Facts over opinions; every finding cites a path and, where possible, a line.

## Orchestrator notes (check these in addition)
- The plan file carries the milestone 2 rulings (`reviews/m2_rulings.md`, "Phase 4") and the phase 3 tokens
  (`reviews/p3_rulings.md`, H5): seven exports including `subfamily.gtf`; `export_feature_members` keyed by
  `(universe_name, variant, feature_level)` with both id spellings at level `record`; `tables/exports.tsv` as the
  inventory; component alphabet `[A-Za-z0-9_.+/?()-]+` with `|` and `:` as separators; unresolved ranks spelled
  `unresolved_class_<name>` / `unresolved_family_<name>`; membership read from `universe_members.tsv.gz`.
- Run the export stage yourself into your own directory
  (`/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p4/build/` with `tables/` and `universes.json` symlinked
  from the orchestrator's build under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/`,
  read-only) and compare the sha256 of every export and of `export_feature_members.tsv.gz` and `exports.tsv` with the
  orchestrator's. Remove your directory when done.
- Recompute with your own code from the parquet and `universe_members.tsv.gz`: 3,764,949 `interspersed` records;
  1,220 names; BED start = start_1 - 1 on every row; GTF and SAF coordinates equal the table; `taxonomy_triple.saf`
  distinct GeneIDs 1,220; `family.bed` distinct names equal the distinct canonical pairs over the universe's names;
  `subfamily.gtf` `transcript_id == gene_id` on every row.
- Parse a 1,000-row sample of each GTF with the three vendored readers under `/workspaces/Meta-Aging/01_modules/.ref/`
  (`TEtranscripts/TEToolkit/TEindex.py`, `TEsingle/TEtools/TEindex.py`, `TElocal/TElocal_Toolkit/TEindex.py`) and
  Stellarscope's `annotation/utils.py`, as the milestone 2 codex review did, and state the feature tuple each
  produces from `record.gtf` and from `subfamily.gtf`.
- Fixture adequacy: on scratch copies, break the alphabet validation, the BED offset, the attribute order, the
  registration conservation and the `exports.tsv` sha256 one at a time; name the check that fails each time.
- Wording: every sentence and comment in `src/lib/build_exports.py`, `src/30_build_exports.sh`, the three checks,
  the `docs/OUTPUTS.md` diff and the README diff.

## Implementer report
__REPORT__
