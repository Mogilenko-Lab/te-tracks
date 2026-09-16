Re-review phase 6 of the te-tracks redesign. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(git branch redesign-2026-09, HEAD c2a7a43). You are read-only: no edits, no git writes anywhere (the checkouts under
/workspaces/Meta-Aging/01_modules/.ref/ are git repositories too), no installs, no network. Scratch work goes under
/workspaces/Meta-Aging/_scratch/te-tracks-audit/opus-p6/ (the /tmp filesystem is noexec) and is removed when you
finish; set PYTHONDONTWRITEBYTECODE=1 for every python invocation. The orchestrator's build at
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build is read-only for you.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/16_phase6_ensembl_preflight.md (the contract) and
   docs/_internal/redesign-2026-09/prompts/p6_impl.md (facts and numeric targets)
2. docs/_internal/redesign-2026-09/reviews/m2_rulings.md (M1, M5) and reviews/m5_rulings.md (codex A2, divergent H2)
3. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments"
4. The implementer's changes: `git status --short` and `git diff HEAD` (plus untracked files' contents)
5. The codex review already written: docs/_internal/redesign-2026-09/reviews/p6_codex.md

Your job is adversarial and independent of the codex review: recompute every acceptance number with your own
read-only code written from the contracts (import nothing from src/ or tests/), try to make each check fail, look for
what the implementer assumed silently, and judge the public prose against the wording rules. Where you agree with a
codex finding say so in one line; where you disagree, show the evidence.

Phase-6 specifics:
(a) From source/mm39.chromAlias.txt and source/mm39.chrom.sizes alone, derive the five name columns and lengths of
    tables/contig_aliases.tsv and compare every cell; apply the gencode rule (ucsc name without `_`, otherwise the
    genbank column) and compare with tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv; check injectivity per
    column; derive contig_coverage.tsv from the parquet and compare.
(b) Regenerate the ensembl and gencode copies of all eight exports (seven interspersed, one all_rmsk) from the ucsc
    files through your own alias mapping and your own sort (contig C-locale bytes, then start and end numeric, strand,
    name), and compare sha256 with tables/exports.tsv; confirm the seven ucsc interspersed rows of exports.tsv are
    unchanged from milestone 5 (compare against the orchestrator's baseline in
    /workspaces/Meta-Aging/_scratch/te-tracks-audit/m5fix_before.sha, read-only).
(c) Regenerate the all_rmsk ucsc record BED from tables/rmsk_records.parquet (5,320,771 rows, name rmsk_record_id,
    score min(sw_score, 1000)) and compare its digest; count the all_rmsk registration rows and confirm each catalog
    record appears once with grammar rmsk_record_id and its own bounds; confirm the 30,119,592 interspersed rows are
    byte-identical to the milestone 5 registration content (sha256 of the decompressed interspersed rows:
    314098c5c9c2f0c2e09d54f15360fce1f411f4c677550bd358f04bf051ee3c84 including the header line).
(d) Run bin/te-tracks-preflight yourself for the interspersed exports and the all_rmsk BED in each namespace: against
    the FASTA contig list, against a 21-chromosome UCSC-named sizes file, against a pysam BAM header with chr1 at a
    wrong length, and against a .fai you write; compute the expected lists independently. Measured fact: the
    interspersed universe has zero records on chrM and chr4_JH584295v1_random (catalog counts 4 and 2), so its exports
    name 59 of 61 contigs and the implementer's literal comparison exits 2 for gencode interspersed against the
    GENCODE FASTA; the all_rmsk BED exits 0 / 2 (39 each way) / 2 (22 each way) / 1 as plan 16 states. Judge which
    exit contract serves the handoff gate `te-tracks-preflight <export> <bam> && featureCounts …`: ruling M1 as
    written, or exit 0 whenever every export contig is present in the reference with an agreeing length, with
    reference-only contigs printed for information and exit 2 reserved for export contigs the reference lacks. Give
    your recommendation and the hazard each choice leaves open.
(d2) src/lib/build_exports.py has build_exports() writing the interspersed set alone and main() writing both
    universes; check 42 imports the function and runs the stage script, and tests/fixtures/exports/universes.json
    declares no all_rmsk, so check 42 fails today, as do checks 60 (zero-record assertion) and 62 (exit expectations).
    State what each of the three checks should assert and what the export fixture needs.
(e) Make checks 60, 61, 62 and 41 fail on scratch copies (one mutation each); verify tracked files by md5 before and
    after; verify every checkout under .ref is clean and holds no __pycache__.
(f) Every number in docs/OUTPUTS.md, docs/DECISIONS.md entry 3, README.md and plan 16 touched by this phase: confirm
    against disk or mark unverifiable.
(g) Confirm no git write happened: `git reflog -3` shows c2a7a43 as the latest entry and the phase 6 changes
    uncommitted.

Report as:
# Phase 6 re-review (Opus)
Verdict: PASS | PASS WITH ADVISORIES | FAIL
## Blocking
- [B1] path:line — finding — evidence — fix
## Advisory
- [A1] ...
## Numbers recomputed
<table: quantity | contract | observed | route>
## Agreement with codex review
<one line per codex finding: agree / disagree with evidence>
Under 150 lines. FAIL when a contract deliverable is missing or wrong, an acceptance number differs, or a check
cannot fail. Deliver the full report as your final message; the orchestrator saves it verbatim to
docs/_internal/redesign-2026-09/reviews/p6_opus.md.
