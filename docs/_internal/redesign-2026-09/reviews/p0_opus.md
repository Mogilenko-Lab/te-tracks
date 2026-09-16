# Phase 0 re-review (Opus)
Verdict: FAIL

Scope note: `docs/_internal/redesign-2026-09/prompts/`, `_project/session.md` and `02_orchestration.md` changed *during* this review (absent from the opening `git status`). I judged the four public files, `AGENTS.md`/`CLAUDE.md`, `.gitignore` and `tests/run.sh` as they stand now; the prompt files are the per-phase implementer specs and I used them only as evidence of grounding.

## Blocking

- **[B1] `docs/OUTPUTS.md:110` — `taxonomy_triple.saf` documented as *raw* triples where the build emits *canonical* ones, flipping a phase-4 acceptance number.** The row reads `Legacy raw taxonomy-triple grouping`. `14_phase4_exports.md:13` defines `GeneID = <rmsk_name>:<canonical_family>:<canonical_class>` and `:23` requires **1,220 distinct GeneIDs** "(canonical labels collapse the 20 doubled names)". Evidence: `12_phase2_canonical.md:22` gives `interspersed` 1,220 subfamilies / **1,240** triples; 1,240 − 1,220 = 20 = the doubled names (`12:28`, `13:66`). A raw-triple SAF therefore has 1,240 distinct GeneIDs, and the public contract points the phase-4 implementer at the wrong number. Compounding it: the GeneID formula appears in **no** public doc (`grep -n "rmsk_name>:" README.md docs/OUTPUTS.md docs/DECISIONS.md` → no hits), although `14:28` puts attribute mapping in `docs/OUTPUTS.md` once. This text is new (`git show HEAD:docs/OUTPUTS.md` names no `taxonomy_triple`). Fix: `Canonical taxonomy-triple grouping; GeneID = <rmsk_name>:<canonical_family>:<canonical_class>`, and add the 1,220-vs-1,240 distinction beside it.
- **[B2] `docs/DECISIONS.md:53` — public prose names two tables the package never ships, contradicting `AGENTS.md:5`.** "Ledger tables are `rmsk_records`, `peak_record_overlaps` and `te_feature_registration`". Evidence: `peak_record_overlaps` and `te_feature_registration` are the *downstream consuming project's* relations — `consults/ADR5_consult.md:135-136` keys them on `(atlas_id, peak_id, …)` and `(analysis_run_id, matrix_id, …)`, `ADR38_consult.md:141` calls them "downstream joins", `ADR4_consult.md:95-96` scopes them through "the ledger manifest". No phase 1–9 delivers either; neither appears in the README truth table; te-tracks publishes `tables/export_feature_members.tsv.gz` instead. "Ledger" occurs exactly once in the public docs and is never defined, while `rmsk_records` sits in the same list *and is* published here — so the sentence reads as three te-tracks deliverables. That is the promise phase 0 forbids (`10_phase0:24`) and it contradicts `AGENTS.md:5` ("Quantification … sit outside this package's scope"). Inherited verbatim from `01_decisions.md:45`, so the decision source needs the same edit. Fix: one clause — "The consuming ledger reserves `peak_record_overlaps` and `te_feature_registration` against these names; its measurement grain column is `feature_level`."

## Advisory

- **[A1] `docs/OUTPUTS.md:133`** — `bin/te-tracks-preflight <export> <bam|fai>` omits the `sizes` form. `16_phase6:17` delivers `<bam|fai|sizes>`, and `16:23-24` exercises exactly that form (`gencode_grcm39_fasta_contigs.tsv`, 61 contigs). The public signature excludes the input the acceptance test uses.
- **[A2] `README.md:45-99`** — the table inventories `docs/RUNBOOK.md` (phase 9) and `bin/te-tracks-preflight` (phase 6), so its implicit rule is "what a consumer reads or runs"; under that rule `docs/RELEASES.md`, rewritten at `17_phase7:15` and `:20`, is the one missing row. Also `tests/expectations/mm39_class_counts.tsv` exists tracked today and its move under `tests/expectations/mm39/` (per `prompts/p2_impl.md:68`) has no row.
- **[A3] `README.md:96-97`** — status never takes `delivered` or `tested`; `MANIFEST.json` and `BUILD_ID` read `deferred | 7` while `README.md:39` says both are generated now. `README.md:41-42` defines the scope, so a careful reader is safe; one `delivered` row for the legacy pair removes the ambiguity.
- **[A4] `AGENTS.md:21-22`** — "Failures and unsupported checks ending in `.required.sh` or `.required.py` cause runner exit 1" parses as requiring the suffix for failures too; a plain `fail.sh` also exits 1 (verified). Neither public doc records exit 2 (bad usage, missing directory) or the discovery rule; both live only in `usage()`.
- **[A5] `tests/run.sh:39`** — `-f` silently drops a dangling symlink: `ln -s /nonexistent/zzz checks/core/dangling.sh` → `checks=0 … no checks registered`, exit 0. Narrower than codex B3, same silent-disappearance class; a check symlinked into an unmounted path vanishes.
- **[A6] `tests/run.sh:28,34`** — `--refroot` is exported verbatim before `cd "$REPO_ROOT"`, so `--refroot ./relroot` resolves against the repo root, not the caller's directory (verified: `refroot=[./relroot] cwd=<repo>`). Rejecting a relative path, or absolutizing it, closes the trap before phase 1 depends on it.
- **[A7] `tests/run.sh:57,70`** — only the first stdout line survives; a failing check's remaining diagnostic output is swallowed by the command substitution unless it writes to stderr.

## Numbers recomputed

| quantity | contract | observed | command |
|---|---|---|---|
| `bash -n` all shell scripts | pass | 8/8 syntax ok | `find . -name '*.sh' … bash -n` |
| `run.sh core\|consumers\|acceptance` | 0 checks, exit 0 | `checks=0 …`, exit 0 (×3) | `./tests/run.sh $m; echo $?` |
| `grep -n "not "` DECISIONS+README | no hits | exit 1, 0 hits | `grep -n "not " docs/DECISIONS.md README.md` |
| same grep + AGENTS+OUTPUTS, widened to `never\|rather than\|instead of\|unlike\|doesn't` | no hits | exit 1, 0 hits | `grep -nE …` |
| failing check | exit 1 | **1** | scratch copy, `fail.sh` exit 9 |
| unsupported `.required.sh` | exit 1 | **1** | `need.required.sh` exit 3 |
| plain unsupported | exit 0 | **0** | `opt.sh` exit 3 |
| non-executable `.py` exiting 1 | exit 1 | **1** (`fail`, mode 0644, "py ran") | `hidden.required.py` |
| missing check directory | exit 2 | **2** + `runner error: missing check directory` | `rm -rf checks/core` |
| empty check directory | exit 0 | 0 + `no checks registered` | — |
| bad mode / missing `--refroot` value / extra arg | exit 2 | 2 (all 6 variants) | — |
| `tests/fixtures/x/y.tsv` | tracked-eligible | trackable; `git add --dry-run` → `add '…'` | `check-ignore -q` + `add --dry-run` |
| `tests/expectations/mm39/a.tsv` (+ `mm39/interspersed/u.tsv`) | tracked-eligible | trackable; both staged in dry-run | same |
| `…/taxonomy/dfam_lookup_20names.tsv` | tracked-eligible | trackable | same |
| `work/x.tsv` | ignored | ignored (`.gitignore:9:work/`) | same |
| class census total | = `compat_tetranscripts_mm39` 3,799,629 | **3,799,629** | `awk -F'\t' '{s+=$2}'` |
| Satellite class | `satellites` universe 37,228 | **37,228** | `grep -i satel` |
| `interspersed_plus_satellites` − `interspersed` | 37,228 | 3,802,177 − 3,764,949 = **37,228** | arithmetic |
| census non-Satellite vs `interspersed` | offset = tRNA-ancestry SINEs | 3,762,401 vs 3,764,949, Δ=**2,548** | `awk` class filter |
| `retrotransposon_derived` − census(LINE+SINE+LTR+Retroposon) | same offset | 3,593,857 − 3,591,309 = **2,548** | `awk` |
| `interspersed` triples − names | 20 doubled names | 1,240 − 1,220 = **20** | plan 12:22 |
| phase-3 `family_status` counts | sum 20 | 7+5+5+3 = **20** | plan 13:66-68 |
| full-interval export rows in README | 6 × 3 namespaces = 18 | **18** (README:73-90) | `sed -n '73,90p'` |
| `exon_subtracted` SAFs | 3 × 2 = 6 | **6** (README:91-94, one braced row) | `sed -n '91,94p'` |
| legacy artifacts disposed | 13 named at HEAD | **13/13** rows (OUTPUTS:62-76) | HEAD-vs-worktree name sets |
| `CLAUDE.md` | `@AGENTS.md` only | 11 bytes, `@AGENTS.md\n` | `od -c` |
| git writes | none | reflog head `270afd4`, tree uncommitted | `git reflog -3; git status --short` |

`.gitignore:12` (`!tests/expectations/*.tsv`) is fully subsumed by `:13` (`!tests/expectations/**`) — harmless, deletable.

## Agreement with codex review

- **B1 truth table incomplete** — agree; **resolved**. 53 rows now cover source qualification, all fixture/expectation groups, tables, 18 exports, 6 `exon_subtracted` SAFs, `MANIFEST.json`/`BUILD_ID`, preflight and runbook; the path-naming rule moved to `README.md:43`, above the inventory. Seven rows (`source/qualification.md`, `universe_summary.tsv`, `export_summary.tsv`, `tests/lib/consumers.py`, `fixtures/contigs/`, `fixtures/publication/`, `rule_cases.tsv`) appear in no phase file 11–19 but are each named in `prompts/p{1..7}_impl.md` — grounded, not invented. Residual gaps are advisory (A2).
- **B2 export matrix over-promise** — agree; **resolved**. `DECISIONS.md:26-29` now states exact pairings (BED@record/subfamily/family, GTF@record, SAF@subfamily/taxonomy-triple) across three namespaces; `14_phase4` gained `taxonomy_triple.saf` and `18_phase8` gained `gencode` + `taxonomy_triple`, so 18 = 6×3 reconciles with README and OUTPUTS. No unscheduled combination remains.
- **B3 required checks silently disappear** — agree; **resolved**. Discovery is now a sorted glob over `*.sh`/`*.py` with no mode test, and a missing directory exits 2. I reproduced all five mandated exits (1, 1, 0, 1, 2) plus ordering-after-failure, spaced filenames, `$TE_TRACKS_REFROOT` propagation and `.required.py` unsupported. One narrow residue survives (A5, dangling symlink).
- **B4 legacy artifacts vanish without deferral** — agree; **resolved**. `OUTPUTS.md:60-76` gives all 13 HEAD-named legacy artifacts an explicit disposition, including `te_locus.saf`, `te_locus.locInd`, `te_context_*.saf`, `locus_context.tsv` and `rename_map.tsv` (superseded, with the superseding artifact named).
- **A1 history framing** — agree; **resolved**. The commit ref is gone; `README.md:39` and `OUTPUTS.md:8` state the currently generated files. The `without fragment-linking meaning` at `OUTPUTS.md:28` is load-bearing and paired with the positive statement at `:32-33`, so it stays within the Prose rule.
- **A2 missing title** — agree; **resolved**. `docs/DECISIONS.md:1` is `# Decisions`.

Read-only throughout: no edits, no git writes, no installs, no network. My scratch copy (`_scratch/p0-opus-rerev`) and the four temporary ignore-probe files were removed; the final `git status` differs from the opening one only by the concurrent changes noted at the top.

The two blocking items are one-clause edits to public prose, and the runner survived every attack I could stage against it.
