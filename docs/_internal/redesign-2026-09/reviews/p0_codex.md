# Phase 0 review (codex gpt-6-astra)
Verdict: BLOCKING

Plan-file citations below resolve under `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/`.

## Blocking

- [B1] `README.md:45` Artifact accounting is incomplete — phase 0 requires a truth table for every artifact (`10_phase0_decisions_scaffold.md:10`). Missing groups include the source qualification report and source fixtures (`11_phase1_source.md:22,30`), `tests/fixtures/taxonomy/dfam_snapshot.tsv` and its provenance JSON (`13_phase3_taxonomy.md:48`), consumer fixtures (`15_phase5_consumer_fixtures.md:5`), and nested acceptance expectations (`19_phase9_acceptance_park.md:5`). The named data-export rows agree with phases 4, 6 and 8; the generic path at README line 57 describes a naming rule — add the missing artifact groups with status and phase, and place the naming rule outside the inventory.
- [B2] `docs/DECISIONS.md:23` The release promise exceeds the scheduled export matrix — “record, subfamily and family level in BED, GTF and full-interval SAF, in UCSC and Ensembl” reads as all level/format/namespace combinations. Phase 4 schedules five full exports (`14_phase4_exports.md:5`); the initial phase 6 adds two Ensembl exports (`HEAD:16_phase6_ensembl_preflight.md:6`). Even the concurrent phase-6 expansion (`16_phase6_ensembl_preflight.md:11`, see Scope check) leaves family GTF and record SAF unscheduled. This ambiguity is inherited from `01_decisions.md:23`; phase 0 expressly requires promises deliverable by phase 9 — state the actual level/format pairings and namespace coverage explicitly.
- [B3] `tests/run.sh:30` Required checks can silently disappear from the result — executable-only discovery skips a mode-0644 `hidden.required.py` whose direct Python execution exits 1; the runner reports zero checks and exits 0. Changing only its mode to 0755 produces fail and exit 1. Removing the check directory also prints a find error followed by zero checks and exit 0 because process-substitution failure is discarded. Phase 1 inherits an undocumented executable-bit prerequisite — enumerate supported check files and reject unexecutable required checks (or invoke their interpreter), propagate discovery failures, and preserve success for an existing, intentionally empty directory.
- [B4] `docs/OUTPUTS.md:52` Several former planned artifacts disappear instead of receiving the required deferral — `HEAD:docs/OUTPUTS.md:55,60,62,65` names locus SAF, distributed locInd, context SAFs and `rename_map.tsv`; the new Deferred section gives none an explicit disposition. Phase 0 says every planned claim moves under deferred (`10_phase0_decisions_scaffold.md:11`) — record their deferral and prerequisites, and identify replacements where a contract supersedes an old artifact.

## Advisory

- [A1] `README.md:39`, `docs/OUTPUTS.md:8` Public prose includes commit-history framing (“At `6ff3ee9`”, “old layout that the redesign replaces”) — state the currently generated artifacts directly and keep historical narration in internal evidence. The requested negation grep has zero hits; the added runner and ignore-rule comments state intent.
- [A2] `docs/DECISIONS.md:1` The missing title is a formatting issue only — all eight numbered ADRs and four recorded deferrals are present, and phase 0 specifies no title requirement. An optional `# Decisions` would give the document a top-level heading.

## Acceptance re-run

All required paths exist. `AGENTS.md:1` has 33 lines and all required subjects; `CLAUDE.md` contains exactly the bytes `b"@AGENTS.md\n"`. `docs/OUTPUTS.md:28` correctly identifies the legacy UCSC field; `README.md:86` and `docs/DECISIONS.md:37` give exon-disjoint support and joint-run molecule exclusivity. Nine nested fixture/expectation/internal-table ignore probes are trackable; `work/example.tsv` stays ignored. The three mode placeholders are empty; phase 0 requires zero registered checks.

No standard acceptance-number deviations: all eight shell scripts pass syntax, all three modes report zero checks, and the negation grep has no matches (exit 1). Outputs below are verbatim.

```bash
for script in $(rg --files --hidden -g '!.git' -g '*.sh' | LC_ALL=C sort); do bash -n "$script" || exit; printf 'syntax ok %s\n' "$script"; done
for mode in core consumers acceptance; do tests/run.sh "$mode"; printf 'exit=%s\n' "$?"; done
tests/run.sh; printf 'exit=%s\n' "$?"
tests/run.sh core --refroot /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot; printf 'exit=%s\n' "$?"
grep -n "not " docs/DECISIONS.md README.md; printf 'grep_exit=%s\n' "$?"
```
```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/10_build_master.sh
syntax ok src/90_manifest.sh
syntax ok src/99_verify.sh
syntax ok src/release.sh
syntax ok tests/run.sh
checks=0 pass=0 fail=0 unsupported=0
no checks registered for mode core
exit=0
checks=0 pass=0 fail=0 unsupported=0
no checks registered for mode consumers
exit=0
checks=0 pass=0 fail=0 unsupported=0
no checks registered for mode acceptance
exit=0
usage: tests/run.sh <core|consumers|acceptance> [--refroot DIR]
exit=2
checks=0 pass=0 fail=0 unsupported=0
no checks registered for mode core
exit=0
grep_exit=1
```

Scratch challenge: executable failure and both required-unsupported suffixes return 1; plain unsupported returns 0; later checks still run after failure. The last discovery cases reproduce B3. Assertions on those cases record observed behavior. The harness normalizes its random scratch path in output and removes its copy.

```bash
python3 - <<'PY'
from pathlib import Path
import os, shutil, subprocess, tempfile
repo = Path.cwd()
with tempfile.TemporaryDirectory(prefix='te-tracks-p0-codex-', dir='/workspaces/Meta-Aging/_scratch') as temp:
    root = Path(temp)
    (root / 'lib').mkdir()
    (root / 'tests').mkdir()
    for rel in ('tests/run.sh', 'lib/common.sh'):
        shutil.copy2(repo / rel, root / rel)
    for mode in ('core', 'consumers', 'acceptance'):
        (root / 'tests/checks' / mode).mkdir(parents=True)
    checks = root / 'tests/checks/core'
    cases = [
        ('failing check', [('fail.sh', '#!/usr/bin/env bash\nexit 9\n', 0o755)], 1),
        ('plain unsupported', [('optional.sh', '#!/usr/bin/env bash\nexit 3\n', 0o755)], 0),
        ('required shell unsupported', [('need.required.sh', '#!/usr/bin/env bash\nexit 3\n', 0o755)], 1),
        ('required Python unsupported', [('need.required.py', '#!/usr/bin/env python3\nraise SystemExit(3)\n', 0o755)], 1),
        ('continue after failure', [('a_fail.sh', '#!/usr/bin/env bash\nexit 1\n', 0o755), ('z_pass.sh', '#!/usr/bin/env bash\nexit 0\n', 0o755)], 1),
        ('non-executable required check', [('hidden.required.py', '#!/usr/bin/env python3\nraise SystemExit(1)\n', 0o644)], 0),
    ]
    for name, fixtures, observed_exit in cases:
        for old in checks.iterdir():
            old.unlink()
        for filename, source, mode in fixtures:
            path = checks / filename
            path.write_text(source)
            path.chmod(mode)
        result = subprocess.run([str(root / 'tests/run.sh'), 'core'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(f'CASE: {name}')
        print(result.stdout, end='')
        print(f'exit={result.returncode}')
        assert result.returncode == observed_exit
    for old in checks.iterdir():
        old.unlink()
    probe = checks / 'refroot.sh'
    probe.write_text('#!/usr/bin/env bash\nprintf "refroot=%s\\n" "$TE_TRACKS_REFROOT"\n')
    probe.chmod(0o755)
    result = subprocess.run([str(root / 'tests/run.sh'), 'core', '--refroot', str(root / 'custom root')], text=True, capture_output=True)
    print('CASE: --refroot propagation')
    print(result.stdout.replace(str(root), '<scratch-copy>'), end='')
    print(f'exit={result.returncode}')
    assert result.returncode == 0 and f'refroot={root}/custom root' in result.stdout
    shutil.rmtree(checks)
    result = subprocess.run([str(root / 'tests/run.sh'), 'core'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print('CASE: missing check directory')
    print(result.stdout.replace(str(root), '<scratch-copy>'), end='')
    print(f'exit={result.returncode}')
    assert result.returncode == 0
print('scratch copy removed')
PY
```
```text
CASE: failing check
fail  fail.sh
checks=1 pass=0 fail=1 unsupported=0
exit=1
CASE: plain unsupported
unsupported  optional.sh
checks=1 pass=0 fail=0 unsupported=1
exit=0
CASE: required shell unsupported
unsupported  need.required.sh
checks=1 pass=0 fail=0 unsupported=1
exit=1
CASE: required Python unsupported
unsupported  need.required.py
checks=1 pass=0 fail=0 unsupported=1
exit=1
CASE: continue after failure
fail  a_fail.sh
pass  z_pass.sh
checks=2 pass=1 fail=1 unsupported=0
exit=1
CASE: non-executable required check
checks=0 pass=0 fail=0 unsupported=0
no checks registered for mode core
exit=0
CASE: --refroot propagation
pass  refroot.sh  refroot=<scratch-copy>/custom root
checks=1 pass=1 fail=0 unsupported=0
exit=0
CASE: missing check directory
find: '<scratch-copy>/tests/checks/core': No such file or directory
checks=0 pass=0 fail=0 unsupported=0
no checks registered for mode core
exit=0
scratch copy removed
```

## Scope check

Pre-review `git status --short --untracked-files=all` and `git diff HEAD --stat`:

```text
 M .gitignore
 M README.md
 M docs/DECISIONS.md
 M docs/OUTPUTS.md
?? AGENTS.md
?? CLAUDE.md
?? tests/checks/acceptance/.gitkeep
?? tests/checks/consumers/.gitkeep
?? tests/checks/core/.gitkeep
?? tests/run.sh
 .gitignore        |   4 ++
 README.md         | 150 +++++++++++++++++++++++++-----------------------
 docs/DECISIONS.md | 162 ++++++++++++++++++++++++++++------------------------
 docs/OUTPUTS.md   | 168 +++++++++++++++++++++++++++++++++++-------------------
 4 files changed, 282 insertions(+), 202 deletions(-)
```

All ten initial implementation files belong to the phase-0 deliverables/scaffold. The extra recursive expectation exception supports the phase-9 nested layout. Final content/mode comparison found all ten unchanged during this review, plus these concurrent changes outside phase 0:

```text
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/16_phase6_ensembl_preflight.md
 M docs/_internal/redesign-2026-09/audit/AUDIT.md
?? docs/_internal/redesign-2026-09/audit/gencode_grcm39_fasta_contigs.tsv
```

The final tracked diff is six files, 312 insertions and 211 deletions. These changes appeared after the initial inspection; attribution to the phase-0 implementer is unestablished. The new phase-6 plan adds `gencode`, BED mirrors and `taxonomy_triple.saf`; README/OUTPUTS/ADR 3 will also need reconciliation with that expanded contract. B2 still applies to its specified matrix.

Existing umbrella/other-submodule changes were left untouched. My sole package write is this review; scratch copies were removed. No git writes, installs, network access or reference-cache writes.
