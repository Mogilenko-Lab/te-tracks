# te-tracks phase 4 fix: review findings

You are the implementer for the phase 4 fix round of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, uncommitted phase 4 tree from
`prompts/p4_impl.md`. Read `docs/_internal/redesign-2026-09/reviews/p4_rulings.md` (every change below and why),
`reviews/p4_codex.md`, `reviews/p4_opus.md`, the plan file
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md`, `src/lib/build_exports.py`,
`tests/checks/core/4*.py`, `tests/fixtures/exports/**`, `README.md` and the phase 4 sections of `docs/OUTPUTS.md`.

Binding prose rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".

## Changes

1. **README export count (A1).** Every README sentence that counts or lists the exports says seven files and names
   both GTF grains (`record.gtf`, `subfamily.gtf`); the three namespace inventories agree with `docs/OUTPUTS.md`.
2. **Conservation fixture asserts its targets (A2).** In `41_export_registration.py`, the synthetic count table's
   intended target per feature is asserted, and the rolled-up totals at record, subfamily and family level are
   asserted against hand-computed expectations, so a corrupted registration row and a wrong target each fail.
3. **DuckDB form of the conservation query (B1).** New `tests/checks/consumers/30_registration_duckdb.py` (the
   `consumers` mode reports support per tool, and DuckDB is the ledger's consumer of the registration): exits 3 with
   `unsupported: python module duckdb absent` when `import duckdb` fails; otherwise runs the conservation query in
   DuckDB over `export_feature_members.tsv.gz` and the same synthetic count table and asserts the same totals.
   Mirror the SQL in a comment-free docstring of one line stating the contract.
4. **Reserved prefix (A3).** `build_exports.py` rejects any resolved canonical class or family token that begins
   with `unresolved_` (message names the token and the name); `42_exports_fixtures.py` adds a failing case with a
   resolved family literally named `unresolved_family_U`; `docs/OUTPUTS.md` states the reserved prefix in one
   sentence beside the token rule.

5. **Sort statement (Opus A4).** In `docs/OUTPUTS.md`, both sentences that describe the five-key sort (the records
   section and the exports section) state that text columns sort in C-locale byte order and the coordinate columns
   ascending numerically; `LC_ALL=C sort -c -t$'\t' -k1,1 -k2,2n -k3,3n` on `record.bed` is the check a consumer can run.

## Rules
- Touch only: `README.md`, `src/lib/build_exports.py`, `tests/checks/core/{41_export_registration.py,42_exports_fixtures.py}`,
  `tests/checks/consumers/30_registration_duckdb.py`,
  `tests/fixtures/exports/**`, `docs/OUTPUTS.md`. Nothing else.
- No git writes. No installs. No network. Re-run stage 30 on `$TE_TRACKS_REFROOT/te_mm39/build`; every export
  digest in `tables/exports.tsv` and the registration digest must be unchanged (record them before and compare).
- Report a deviation instead of editing a number, an expectation or a fixture to fit. Tests are strengthened only.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
B="$TE_TRACKS_REFROOT/te_mm39/build"
sha256sum "$B"/tables/exports.tsv "$B"/tables/export_feature_members.tsv.gz > /workspaces/Meta-Aging/_scratch/te-tracks-audit/p4fix_before.sha
bash src/30_build_exports.sh "$B" config/mm39.env; echo "exit=$?"
sha256sum -c /workspaces/Meta-Aging/_scratch/te-tracks-audit/p4fix_before.sha
grep -n 'seven\|six' README.md
tests/run.sh core; echo "exit=$?"
tests/run.sh consumers; echo "exit=$?"
git status --short | grep -v docs/_internal
```
Expected: stage exits 0; both digests `OK`; `core` exits 0 with thirteen passes; `consumers` exits 0 with one
`unsupported` line naming the duckdb module; the status list equals the phase 4 file set plus the new check.

## Final message
Every file changed; acceptance outputs verbatim; any deviation.
