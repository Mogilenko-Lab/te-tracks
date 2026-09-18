# te-tracks milestone 9 fix: the two operational blockers and the document truth

You are the implementer of the fix round after the milestone 9 seam review. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, HEAD `c98ce26`. Read
`docs/_internal/redesign-2026-09/reviews/m9_codex.md` first: it is the review you are answering, it checked
437 claims and found four false operational claims, and its findings are numbered B1, B2 and A1 to A4.
Then read `AGENTS.md`, `README.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, `tests/lib/consumers.py`,
`src/release.py` and `tests/expectations/mm39/README.md`.

The orchestrator has ruled on every finding. Implement the rulings below. Where a ruling names a number,
report a deviation rather than editing an artifact to match it.

## 1. B1, the consumer parser sources a fresh host cannot reconstruct

The required consumer checks load six sibling checkouts under `/workspaces/Meta-Aging/01_modules/.ref/`
(`irescue`, `stellarscope`, `TEsingle`, `TEtranscripts`, `TElocal`, `MATES`). The umbrella ignores that
directory, the referenced bootstrap creates none of them, and the reviewer's probe made required IRescue
check 10 exit 1 through `git describe` exit 128 before any fixture was built. Two changes, both required.

**A missing prerequisite reports what to do.** `tests/lib/consumers.py:checkout_import` already raises
`Unsupported` when a checkout is absent; `checkout_version` and every other helper that reaches into
`CHECKOUTS` does not. Give every one of them the same guard, with a message naming the absent path and the
restoration command. A consumer check whose source is absent reports `unsupported` with an actionable
sentence. Check 10 stays `.required.py`, so the runner still exits 1; the difference is that its operator
learns the cause in one line instead of reading a traceback.

**The restoration procedure is published.** Add a section to `docs/RUNBOOK.md` beside the consumer
environment that gives, for each of the six, the upstream URL, the destination path and the full commit the
runbook's pin table already names, plus the exact clone-and-checkout commands that place them. Read each
checkout's `origin` URL from the checkout itself rather than guessing it. State that the clone needs network
access at setup time and that the pinned commit is what qualification measures.

Correct the word `vendored` wherever it describes these checkouts in any public file: they are pinned clones
in an ignored sibling directory, so say that.

## 2. B2, a clean-builder gate that does not stop anything

The publication sequence in `docs/RUNBOOK.md` asserts `provenance.builder_git_dirty is False` inside a
`python3 - <<'CLEAN'` heredoc, in a `bash -l` shell with neither `set -e` nor `|| exit`. The reviewer's probe
printed `AssertionError`, then reached the selection step, and returned 0. The gate the milestone 7 ruling
assigned to the runbook is therefore unenforced.

Move the gate into the tool, because a gate written in prose is a suggestion. Add `--require-clean` to
`src/release.py` for `install` and `select`: with the flag, a manifest whose `provenance.builder_git_dirty`
is true is refused with a message naming the family, the build id and the flag, and the command exits
nonzero. Without the flag the behaviour is unchanged, which keeps every in-container build and the
`acceptance --build` path working, since those trees are deliberately dirty.

Then rewrite the runbook's publication sequence to use it: drop both fragile heredocs, pass
`--require-clean` on the host `install` and `select` calls, and make the documented sequence fail-fast so
no step can run after a failed gate. Say in one sentence why the flag exists and when the owner would
omit it.

Add a core check that proves the refusal: a fixture manifest with the dirty flag true must make
`select --require-clean` exit nonzero, and the same manifest without the flag must succeed.

## 3. A1, the reproducibility claim the bootstrap does not support

`docs/RUNBOOK.md` calls the consumer environment reproducible. The sibling `te-consumers/env/bootstrap.sh`
upgrades packaging tools without pins, installs git requirements without consuming `pip-freeze.txt`, and
extracts downloads without enforcing recorded hashes. You may not edit that sibling package. Narrow the
claim instead: state exactly what the recipe reproduces today, which is the five pinned tool commits and the
recorded installed versions, and name the three gaps as the consuming module's own work. The sentence a
reader acts on must be true of the script it points at.

## 4. A2, a delivered thing still recorded as deferred

`docs/DECISIONS.md:202-203` defers the consumer-environment promotion to phase 9. It is delivered, by
reference, at `docs/RUNBOOK.md`. Replace the deferral with the delivered state and the pilot gates that
genuinely remain.

## 5. A3, reproduction pins described as correctness evidence

`tests/expectations/mm39/README.md` heads its second column "Independent authoring evidence" and lists
`identity.tsv` under it. Those two build ids and the file-size literals are reproduction pins taken from an
earlier development build, preserved before the build they now judge. That makes them evidence of
reproduction, and the table should say so. Split the column, or add a per-row kind, so a reader sees which
rows are external or authored oracles and which are prior-output fingerprints. Keep every pin and keep the
fatal discrepancy assertion.

## 6. A4, an oracle whose evidence is half pinned

`tests/expectations/mm39/gene_oracle.tsv` holds eleven literals, so ten of the eighteen metrics the oracle
prints are pinned. Unpinned: chr18 `input_records`, `exon_rows` and `union_bp`; chr19 `exon_rows`;
`chr1_MU069434v1_random` `exon_rows`, `union_intervals`, `union_bp` and `retained_bp`. Pin every metric the
oracle prints, taking each value from the review and ruling records that already carry it, and where no
earlier record carries a value, report that rather than reading it from the build.

## 7. The measurements with no durable carrier

The review found nine raw observations in the public documents with no surviving witness, because the phase
scratch that held their logs was removed: the initial export peak 6,807,732,224; the initial child
874,917,888 and 152.012 s; and the two reader triples in the resource-floor tables. The final manifests do
retain 4,936,556,544, 881,565,696 and 154.376 s.

Rule: a number in a public document has a carrier a reader can reach. Keep the manifest-retained figures
where they are. For each of the nine, either cite the internal record that carries it, in which case it
stays with that citation, or move it out of the public documents into
`docs/_internal/redesign-2026-09/reviews/m9_rulings.md` as a recorded observation. State which you did for
each. The consumer annotation-load floors keep their projections, since a consumer plans with them; give
them the carrier of the reproduction command and the anchor's internal record.

## 8. Two of the orchestrator's own findings

`tests/checks/acceptance/lib/consumer_floor.py` hard-codes its scratch directory to a phase-named path and
hard-codes the 3,764,949-row projection constant. A host operator runs this tool after the phases are
history, and pointing it at another export yields a wrong projection. Take the scratch directory from
`TMPDIR` with a documented default, and derive the total row count from the file it was given. Keep the
50,000-row head and the two anchors.

`docs/OUTPUTS.md` names "14761 chromatin-accessibility ledger" as a reader in the consumer map. The
published map names readers by what they are, so say "a chromatin-accessibility ledger".

## 9. The Opus review of phase 9b

`docs/_internal/redesign-2026-09/reviews/p9b_opus.md` is the second review, verdict PASS WITH ADVISORIES.
It injected twenty-two defects into real copies of the acceptance archives; twenty-one make the suite fail
and all ten the brief named are caught by the area that owns them. Read it. Six advisories, all ruled here.

**9a. The acceptance suite cannot fail on a damaged archive. Two changes, both required.** With
`MANIFEST.json` removed from an archive whose `current` still resolves, all eleven checks report
`unsupported` and the runner exits 0, which is the same output an empty reference root gives. The exit code
is load-bearing: `README.md` and the phase commit both cite "exited 0" as the qualification witness.

Separate the two states. An acceptance root with no build is `unsupported`, because a fresh checkout has
not run `acceptance --build` yet. An archive that resolves through `current` but lacks `BUILD_ID`,
`CATALOG_ID` or `MANIFEST.json` is damaged, so it fails rather than reporting unsupported.

Then rename all eleven checks to `*.required.py`, so a suite that judged nothing cannot exit 0. Update
`AGENTS.md` and `README.md` to say that acceptance exits 1 when it has no archive to judge, and that the
message names the command that makes one.

**9b. The geometry oracle covers three of sixty-one contigs.** Those three hold 200,697 of the child's
3,684,934 interspersed blocks, 5.4 percent. An off-by-one `Start` on chr7 passes the oracle at exit 0 and is
caught only by `80_gene_child`, which compares the SAF against the builder's own registration table, so the
outside witness misses it. Add one large annotated autosome to the oracle's contig list, report the
resulting block coverage in the check's summary line, and state the covered fraction in the oracle table in
`docs/PROVENANCE.md`. Take the new contig's pinned metrics from your own bedtools run and report them as
new anchors for the ruling record rather than writing them into `gene_oracle.tsv` as though an earlier
record carried them; say clearly in your report which values are new.

**9c. A locale-dependent sort feeding a codepoint merge.** `oracles.py:124` sorts both interval streams with
GNU `sort` under the ambient locale and merges them at 127 to 141 with Python's codepoint comparison. Under
`LANG=en_US.UTF-8` the two orders differ, so equal multisets still compare line for line and a real
difference still fails, while the reported directional counts and sampled examples are unreliable. Use
`env LC_ALL=C sort` for both streams. Confirm the reconciliation still reports zero differences in both
directions.

**9d. The acceptance scratch ignores `--refroot`.** `lib/common.py:17` hardcodes
`_scratch/te-tracks-audit/p9b`, so `--refroot` does not isolate a run and every replay writes into a path
the runner never names. Derive it from `TE_TRACKS_REFROOT`, keep `tempfile.mkdtemp` beneath it, and name the
derived path in the runner's usage text or in `AGENTS.md` beside the acceptance description. This is the
same defect as item 8's hardcoded path; fix both the same way.

**9e. A vacuous assertion.** `areas.py:100-102` asserts 49 distinct family features only for rows whose
`feature_level` is `family`, so a roster with that level renamed satisfies the loop with no iterations.
Assert that the level is present before asserting its census.

**9f. A conditional comparison whose summary reads unconditional.** The development-build comparison at
`areas.py:177-191` runs only when `$TE_TRACKS_REFROOT/<family>/build` exists and otherwise prints
`development comparison unavailable` and passes. The unconditional protection is the pinned `identity.tsv`
comparison beside it, which stays. Make the summary line say which of the two ran, in words a reader cannot
mistake, and check that `docs/RELEASES.md` describes the comparison as conditional on the development build
being present.

One number to carry into the runbook: the reviewer's full `tests/run.sh acceptance` run against the
untouched reference root took **54 minutes 33 seconds** at 11 of 11 passes. A consumer planning a
verification needs that figure; put it beside the acceptance commands with its carrier named.

One correction to make in both places that state it: `tests/expectations/mm39/gene_oracle.tsv` holds
**eleven** data rows, not twelve.

## Rules
- Touch only: `docs/RUNBOOK.md`, `docs/DECISIONS.md`, `docs/OUTPUTS.md`, `README.md`, `AGENTS.md`,
  `src/release.py`, `tests/lib/consumers.py`, `tests/checks/core/**`, `tests/checks/acceptance/**`,
  `tests/expectations/mm39/**`, `tests/fixtures/**`, `tests/run.sh`.
- No behaviour change to any build output. If any change of yours moves a `BUILD_ID`, stop and report.
- No git writes. No installs. No network. Never write into `/data2/users/shared/refcache`. Do not edit
  anything under `/workspaces/Meta-Aging/01_modules/te-consumers/` or `01_modules/.ref/`.
- Weaken or delete no check.
- Scratch under `_scratch/te-tracks-audit/m9fix/`, removed with Python `shutil.rmtree`; `/tmp` is noexec.
- Export `PYTHONDONTWRITEBYTECODE=1` in every shell.
- Where a log matters, write it under `_scratch/te-tracks-audit/m9fix/` and name the path in your report.
  Write no log into the repository tree.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_CONSUMER_FIXTURES=/workspaces/Meta-Aging/_scratch/te-tracks-audit/m9fix/consumers
for f in build.sh lib/common.sh src/*.sh src/gene/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
tests/run.sh core; echo "core exit=$?"
tests/run.sh acceptance; echo "acceptance exit=$?"
source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh
tests/run.sh consumers; echo "consumers exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39_gene; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/acceptance" --family te_mm39; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/acceptance" --family te_mm39_gene; echo "exit=$?"
git status --short
```
Also demonstrate, with commands and outputs pasted:
- a consumer check reporting `unsupported` with its restoration sentence when a checkout path is redirected
  to an absent directory, and the same check passing when it is not;
- `select --require-clean` refusing a dirty fixture manifest with its message and exit, and succeeding
  without the flag;
- `consumer_floor.py` run against the core `interspersed/full/record.gtf` and against one other export,
  showing that the projection follows the file;
- an acceptance run against a copy of an archive with `MANIFEST.json` removed, showing a failure and the
  runner exiting 1, and an acceptance run against an empty acceptance root, showing `unsupported` and the
  runner exiting 1 with the message that names `acceptance --build`;
- the geometry oracle's new contig list with its block coverage, and the off-by-one on a contig inside the
  new list being caught by area 85 itself;
- the legacy reconciliation under `LC_ALL=C`, reporting zero differences in both directions;
- the derived acceptance scratch path printed for two different `--refroot` values.

## Final message
Every file changed; for each of B1, B2 and A1 to A4 and items 7 and 8, what you changed and the evidence;
the three demonstrations verbatim; the nine measurements and what you did with each; every suite exit; any
number you could not source from an internal record; every deviation.
