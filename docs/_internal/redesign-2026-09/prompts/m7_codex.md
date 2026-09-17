# te-tracks milestone review after phase 7: publication seam (codex, read-only)

You review the committed state of the te-tracks redesign after phases 0 to 7. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, commit `__HEAD__`. You write
exactly one file: `docs/_internal/redesign-2026-09/reviews/m7_codex.md`. You change nothing else. No git writes
anywhere (the eleven consumer checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too:
DfamTEBrowser, irescue, mascarade, MATES, mLLMCelltype, scTE, scTEfinder, stellarscope, TElocal, TEsingle, TEtranscripts; the
directory also holds `14839-DM-cGAS` and `sene/`, the owner's copies, which you leave alone), no installs, no network. Export
`PYTHONDONTWRITEBYTECODE=1` for every Python process. Scratch work goes under
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/` and is removed when you finish (Python `shutil`;
`/tmp` is noexec). The orchestrator's build at `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build`
and the published root `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot` are read-only for you;
`BUILD_ID` `0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a`, `CATALOG_ID` `0c0a959dea69e397890b590b640162d5bd45e71a88f6468cadd4b7615022b4a4`.

Your question is the publication seam: does every party (a consumer, an operator transferring or selecting, a
later builder with a different roster) meet a published archive only through the documented contract, and does
identity survive each of those meetings unchanged? Two other reviewers cover numbers (Opus) and unstated
assumptions (divergent); leave those to them.

## Read
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/00_INDEX.md`, `16_phase6_ensembl_preflight.md`,
   `17_phase7_publication.md`, then the downstream `18_phase8_gene_child_seam.md`, `19_phase9_acceptance_park.md`.
2. The rulings so far: `docs/_internal/redesign-2026-09/reviews/{m2,m5}_rulings.md`, `p6_rulings.md`, `p7_rulings.md`.
3. `docs/_internal/redesign-2026-09/consults/ADR67_consult.md` (identity and publication) and `ADR38_consult.md`.
4. Public contract: `README.md`, `docs/DECISIONS.md`, `docs/OUTPUTS.md`, `docs/RELEASES.md`, `AGENTS.md`.
5. Code: `build.sh`, `src/90_manifest.py`, `src/99_verify.py`, `src/release.py`, `src/lib/manifest.py`,
   `src/lib/build_exports.py` (`EXPORT_CONTRACTS`), `src/lib/contigs.py`, `bin/te-tracks-preflight`,
   `tests/checks/core/{6,7}*`, `tests/fixtures/publication/**`, `tests/lib/consumers.py`, `tests/checks/consumers/*`.
6. The phase reviews `reviews/p{6,7}_*.md`.

## Judge, with evidence
- **Identity from the outside.** With your own canonical encoder (import nothing from `src/`), recompute both ids
  from `MANIFEST.json` in the build directory and in `pubroot/te_mm39/current`; confirm the identity sections are
  equal and name every provenance key that differs.
- **Verification against the archive's own declaration.** Build two tiny fixture builds through
  `tests/fixtures/publication/build_fixture.py` into your own root, one under the current roster and one with the
  added export; install and select in both orders, re-select the older one, run `verify-current`; then verify an
  archive from a scratch copy of the repository whose `EXPORT_JOBS` carries one more export and whose
  `TAXONOMY_RULE_VERSION` is bumped without extending the published tuple, and state which commands accept and which
  refuse, with messages.
- **Transfer.** Follow `docs/RELEASES.md` "Transfer and recovery" literally on a fixture build into a second root:
  copy into that root's staging, verify there, install, select. State whether the procedure as written produces the
  same `BUILD_ID` and whether any step needs knowledge the document omits.
- **Consumers meet the archive.** Resolve `current` once as a consumer would; run `bin/te-tracks-preflight` on one
  export per namespace under the published archive against the FASTA contig fixture; drive one vendored parser
  (IRescue or TEtranscripts) over a published export and confirm its feature key resolves through the published
  `export_feature_members.tsv.gz` to `rmsk_record_id`; compare the keys with `identity.export_contracts`.
- **Ledger key stability.** On fixture builds, change only the `chromAlias` source bytes and confirm `CATALOG_ID`
  holds while `BUILD_ID` changes; change one byte of `rmsk_out` and confirm both change.
- **Phase 8 readiness.** What the child family needs from this seam: `parent_build_id`/`parent_catalog_id`
  validation, the family regex and `SPECIES` admission, a per-family `.staging`, the alias table for child
  preflight, and anything in `manifest.py` or `release.py` that hardcodes the core family where the child needs a
  parameter.

## Output format (the review file)
```
# Milestone 7 review: publication seam (codex gpt-6-astra)
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
BLOCKING means a consumer, an operator or a later builder cannot use a published archive without changing a
published file, identity or key. Keep the file under 200 lines. Facts over opinions; every finding cites a path
and, where possible, a line.
