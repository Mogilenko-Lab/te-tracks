Milestone review after phase 2 of the te-tracks redesign: numbers and fixtures. Repository:
/workspaces/Meta-Aging/01_modules/te-tracks (git branch redesign-2026-09, commit __P2_COMMIT__). You are
read-only: no edits, no git writes, no installs, no network. Scratch work goes under
/workspaces/Meta-Aging/_scratch/te-tracks-audit/m2-opus/ (the /tmp filesystem is noexec) and is removed when
you finish. The orchestrator's build at /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build
is read-only for you.

Your question: does every number the package publishes or asserts follow from the pinned source bytes by an
independent route, and does every check fail when its subject is wrong? Two other reviewers cover the schema
and identity seam (codex) and unstated assumptions (divergent); leave those to them.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/{10_phase0_decisions_scaffold,11_phase1_source,12_phase2_canonical}.md
2. docs/_internal/redesign-2026-09/audit/AUDIT.md (measured facts) and audit/{class_census,policy_universes}.tsv
3. README.md (truth table and Guarantees), docs/OUTPUTS.md, tests/expectations/mm39/*.tsv
4. tests/run.sh, tests/lib/records.py, tests/checks/core/*, tests/fixtures/**
5. docs/_internal/redesign-2026-09/reviews/p{0,1,2}_{codex,opus}.md

Do, with your own code (write it from the format specifications; import nothing from src/ or tests/):
(a) From the pinned source /workspaces/Meta-Aging/_scratch/te-tracks-audit/source/mm39.fa.out.gz, derive the
    record set, instance statistics, class census, the six universe summaries (records, names, triples,
    length_sum_bp) and the 20 multi-label names with their 6,517 records; compare each to
    tables/rmsk_records.parquet, tables/rmsk_taxonomy.tsv, tables/universe_summary.tsv,
    tables/universe_members.tsv.gz and tests/expectations/mm39/*.tsv in the orchestrator's build.
(b) Verify the 24-column parquet against your derivation column by column on all 5,320,771 rows, including
    the three ucsc_rep_* columns against rmsk.txt.gz and the six negative consensus_left_bp rows.
(c) Rebuild once into your own directory with TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
    and compare sha256 of every file under tables/ and universes.json with the orchestrator's build.
(d) Fixture adequacy across phases 0 to 2: list every failure mode the plan files name (duplicate key,
    bounds, missing chrom, spanning instance, census gate, tRNA exclusion, malformed rows, unreadable input,
    dangling symlink, required-unsupported) and, for each, the check and fixture that exercises it; name any
    failure mode without a fixture. Mutate one thing per check on scratch copies and confirm each check fails
    (tracked files unchanged; verify by md5 before and after).
(e) Every number in README.md, docs/OUTPUTS.md, docs/DECISIONS.md and the plan files 10 to 12: confirm it
    against disk or mark it unverifiable.
(f) Confirm no git write happened: git reflog -3 shows __P2_COMMIT__ as the latest entry and a clean tree.

Report as:
# Milestone 2 re-review: numbers and fixtures (Opus)
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
