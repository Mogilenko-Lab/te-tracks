# te-tracks phase 0: decisions, scaffold, truth table

You are the implementer for phase 0 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`. It is a git repository on branch `redesign-2026-09`.

## Read first, in this order
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/10_phase0_decisions_scaffold.md` (your phase)
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` (the eight ADR texts to land verbatim in spirit, edited only for flow)
3. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/00_INDEX.md` (the whole phase table, so the truth table names the right artifacts)
4. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md`, `14_phase4_exports.md`, `17_phase7_publication.md`, `18_phase8_gene_child_seam.md` (artifact names and paths the README must list as deferred)
5. The current public files you will rewrite: `README.md`, `docs/DECISIONS.md`, `docs/OUTPUTS.md`, `.gitignore`.
6. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (the wording rules, binding for every public file you write).

## Deliverables (exact paths)
- `docs/DECISIONS.md`: rewritten from `01_decisions.md`. Eight numbered entries plus "Recorded deferrals". Each entry two to four brief affirmative sentences. Nothing else in the file.
- `AGENTS.md` at the repo root (new): what this package owns (a reference projection of RepeatMasker for one assembly: canonical tables, universes, exports, fixtures), what it refuses (quantification, biological interpretation, knowledge of downstream assays), the refcache fact (`/data2/users/shared/refcache` is read-only inside the container; builds and publication run on the host; tests run in-container against a scratch root), the test runner commands, a pointer to `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/02_orchestration.md` for the review protocol, the prose rule (affirmative, brief, no contrastive negation), the comment rule (intent only), no AI attribution in commits. Under 60 lines.
- `CLAUDE.md` at the repo root (new) containing exactly one line: `@AGENTS.md`.
- `README.md`: rewritten. Sections: one-paragraph purpose; Sources (the `.out` as primary, UCSC table for qualification, chromAlias, chrom.sizes; gene GTF belongs to the child family); Build (host runbook pointer, in-container tests); Outputs as a **truth table** with columns `artifact | status | phase`, where status is one of `delivered`, `tested`, `deferred`, listing every artifact named in the phase files: `tables/rmsk_records.{tsv.gz,parquet}`, `tables/rmsk_instance_members.tsv.gz`, `tables/rmsk_taxonomy.tsv`, `tables/taxonomy_canonical.tsv`, `tables/taxonomy_resolution_report.tsv`, `universes.json`, `tables/universe_members.tsv.gz`, `tables/export_feature_members.tsv.gz`, `tables/contig_aliases.tsv`, `tables/contig_coverage.tsv`, `exports/<contig_namespace>/<universe>/<interval_variant>/<level>[_<profile>].<format>` with the concrete first-release set (`exports/ucsc/interspersed/full/{record.bed,subfamily.bed,family.bed,record.gtf,subfamily.saf}`, `exports/ensembl/interspersed/full/{record.gtf,subfamily.saf}`, `exports/{ucsc,ensembl}/interspersed/exon_subtracted/subfamily.saf` in the child family `te_mm39_gene`), `MANIFEST.json`, `BUILD_ID`, `bin/te-tracks-preflight`. Today every row is `deferred` with its phase number; the currently generated legacy files (`te_loci.tsv.gz`, `te_dim.tsv`, `MANIFEST.json`, `BUILD_ID` in the old layout) are listed in one sentence as the state at `6ff3ee9` that the redesign replaces. Guarantees section rewritten to the new contract (four feature levels; universes as predicates; `rmsk_record_id` = `<rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>`; `BUILD_ID` as the SHA-256 of the manifest identity section; archive plus atomic `current`). Replace every "counts each read once" claim with the exon-disjoint-support wording from ADR 4. Keep the Genomes section truthful: mm39 built; hg38 deferred.
- `docs/OUTPUTS.md`: correct the description of column 13 `rmsk_id` in the legacy table to state what UCSC's `id` column actually is (a one-character value with no fragment-linking meaning; the `.out` ID column is the instance key and lands in phase 2). Move every "Planned" item under a heading "Deferred" that names the phase where each lands, using the new export grammar and file names, and delete file names that no longer exist in the plan (`te_subfamily.saf`, `te_locus.*`, `te_context_*`, `locus_context.tsv`, `rename_map.tsv`, `ensembl_named/`). Keep the "Built today" legacy section accurate.
- `.gitignore`: keep the existing rules and the `!docs/_internal/**/*.tsv` negation; add negations so everything under `tests/fixtures/` is tracked whatever its extension (`!tests/fixtures/**`), and so `tests/expectations/**` stays tracked recursively.
- `tests/run.sh` (new, executable): `usage: tests/run.sh <core|consumers|acceptance> [--refroot DIR]`. It discovers checks as executable files under `tests/checks/<mode>/` in sorted order, runs each with `TE_TRACKS_REFROOT` exported (default `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`), and interprets exit codes: 0 `pass`, 3 `unsupported`, anything else `fail`. It prints one line per check `pass|fail|unsupported  <check name>  <first line of the check's stdout, if any>`, then a summary `checks=N pass=P fail=F unsupported=U`. It exits 1 on any fail; a check whose file name ends in `.required.sh` or `.required.py` that reports unsupported also causes exit 1. With zero checks it prints `checks=0 ... ` plus the message `no checks registered for mode <mode>` and exits 0. Create `tests/checks/{core,consumers,acceptance}/.gitkeep`. Source `lib/common.sh` for `LC_ALL=C` and `umask`, then override `set -e` behaviour as needed so one failing check does not abort the runner.

## Rules
- Touch only: `README.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/DECISIONS.md`, `docs/OUTPUTS.md`, `tests/run.sh`, `tests/checks/**`. Nothing under `src/`, `lib/`, `config/`, `docs/_internal/`, `docs/PROVENANCE.md`, `docs/RELEASES.md` (those belong to later phases).
- No git writes of any kind (no add, commit, stash, checkout, branch, reset). No installs. No network.
- Prose rule for every public file: affirmative, brief, state what a thing is. Cut contrastive negation ("X, not Y", "rather than", "instead of", "never", "no longer") unless the contrast is logically load-bearing and reads cleanly. Comments state intent in one line.
- Report a deviation rather than editing a plan file or a rule to fit. If a deliverable conflicts with the plan, stop that item, keep the rest, and say so in your final message.

## Acceptance (run these yourself before finishing; report the exact output)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
tests/run.sh core; echo "exit=$?"            # expect: checks=0 ... and 'no checks registered for mode core', exit 0
tests/run.sh consumers; echo "exit=$?"       # same shape, exit 0
tests/run.sh bogus; echo "exit=$?"           # usage error, non-zero
grep -n -E "\bnot\b|rather than|instead of|never|no longer" README.md AGENTS.md docs/DECISIONS.md docs/OUTPUTS.md   # expect no hits, or only hits you can justify one by one in the final message
test "$(cat CLAUDE.md)" = "@AGENTS.md" && echo "CLAUDE.md ok"
git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short   # expect only the files listed under Touch only
```

## Final message
List every file you created or changed with one line each, the acceptance output verbatim, every grep hit you kept with its justification, and any deviation from the phase file.
