Milestone review after phase 5 of the te-tracks redesign: numbers and fixtures. Repository:
/workspaces/Meta-Aging/01_modules/te-tracks (git branch redesign-2026-09, commit __HASH__). You are
read-only: no edits, no git writes anywhere (the checkouts under /workspaces/Meta-Aging/01_modules/.ref/ are git
repositories too), no installs, no network. Scratch work goes under
/workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-opus/ (the /tmp filesystem is noexec) and is removed when
you finish. The orchestrator's build at /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build
is read-only for you.

Your question: does every number phases 3 to 5 publish or assert follow from the phase 2 tables by an
independent route, and does every check fail when its subject is wrong? Two other reviewers cover the consumer
seam (codex) and unstated assumptions (divergent); leave those to them.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/{13_phase3_taxonomy,14_phase4_exports,15_phase5_consumer_fixtures}.md
2. docs/_internal/redesign-2026-09/reviews/{m2_rulings,p3_rulings}.md and any p4_rulings.md / p5_rulings.md
3. README.md (truth table), docs/OUTPUTS.md, tests/expectations/mm39/*.tsv
4. tests/run.sh, tests/lib/*.py, tests/checks/core/{3,4}*, tests/checks/consumers/*, tests/fixtures/**
5. docs/_internal/redesign-2026-09/reviews/p{3,4,5}_*.md

Do, with your own code (write it from the contracts; import nothing from src/ or tests/):
(a) From tables/rmsk_records.parquet, tables/rmsk_taxonomy.tsv and tables/universe_members.tsv.gz, re-derive
    taxonomy_canonical (all 15 columns, instance-weighted rule), every export row (offsets, names, attribute
    values, GeneIDs) on the full 3,764,949 interspersed records, the distinct-feature counts, and the registration
    table's row count per level; compare to the build and to tests/expectations/mm39/*.tsv.
(b) Recompute every sha256 in tables/exports.tsv.
(c) Rebuild stages 20 and 30 once into your own directory (symlink the phase 2 tables and universes.json) and
    compare every output digest with the orchestrator's.
(d) Consumer fixtures: rebuild the synthetic fixture set through tests/lib/consumers.py into your own refroot, count
    molecules per BAM with pysam yourself, and compare to the builder's intended counts and to what
    tests/checks/consumers/* assert; run tests/run.sh consumers --refroot <yours> and state every supported and
    unsupported line with its reason.
(e) Fixture adequacy across phases 3 to 5: list every failure mode the plan files name and, for each, the check
    and fixture; mutate one thing per check on scratch copies and confirm each check fails (tracked files unchanged;
    verify by md5 before and after).
(f) Every number in README.md, docs/OUTPUTS.md and plan files 13 to 15: confirm against disk or mark unverifiable.
(g) Confirm no git write happened: git reflog -3 shows __HASH__ as the latest entry and a clean tree; each checkout
    under .ref shows a clean status.

Report as:
# Milestone 5 re-review: numbers and fixtures (Opus)
Verdict: PASS | PASS WITH ADVISORIES | FAIL
## Blocking
- [B1] path:line — finding — evidence — fix
## Advisory
- [A1] ...
## Numbers recomputed
<table: quantity | published | observed | route>
## Fixture coverage
<table: failure mode | check | fixture | mutation result>
Under 200 lines. FAIL when a published number differs from your derivation, or a check passes on a mutated
subject.
