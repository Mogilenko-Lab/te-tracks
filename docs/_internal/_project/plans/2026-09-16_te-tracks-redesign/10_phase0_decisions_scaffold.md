# Phase 0: decisions, scaffold, truth table

Goal: the repository states the new contract before any code moves.

Deliverables
- `docs/DECISIONS.md` rewritten from `01_decisions.md` (eight entries plus recorded deferrals).
- `AGENTS.md` at the te-tracks root: what the package owns (reference projection, universes,
  fixtures), what it refuses (quantification, biology claims), the read-only refcache fact, the
  test runner commands, the review protocol pointer, the prose rule. `CLAUDE.md` holds `@AGENTS.md`.
- `README.md` gains a three-column truth table for every artifact: delivered, tested, deferred.
  Every "planned" claim in `docs/OUTPUTS.md` moves under deferred until its phase lands.
- `docs/OUTPUTS.md` column 13 (`rmsk_id`) description corrected; the "counts each read once"
  sentences in `README.md` and `docs/DECISIONS.md` replaced by the exon-disjoint-support wording.
- `.gitignore` keeps `docs/_internal/**/*.tsv` tracked (done 2026-09-16) and adds `tests/fixtures/`
  as tracked.
- `tests/run.sh` skeleton with modes `core`, `consumers`, `acceptance`, each reporting
  `pass`, `fail` or `unsupported` per check, exit non-zero on any fail or on an unsupported
  required check.

Acceptance
- `bash -n` on every script; `tests/run.sh core` runs and reports zero checks with a clear message.
- `grep -n "not " docs/DECISIONS.md README.md` shows no contrastive negation in public prose.

Review focus: wording rule; nothing in the docs promises an artifact that phase 9 cannot deliver.
