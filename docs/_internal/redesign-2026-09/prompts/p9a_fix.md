# te-tracks phase 9a fix

You are the fix implementer for phase 9a of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phase 9a is implemented and
reviewed; the reviews are `docs/_internal/redesign-2026-09/reviews/p9a_codex.md` (BLOCKING) and
`reviews/p9a_opus.md` (PASS WITH ADVISORIES with one blocking documentation clause). The orchestrator's
rulings are `reviews/p9a_rulings.md`, which is authoritative where a review and the rulings differ. Read all
three, plus the contract in
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/19_phase9_acceptance_park.md` and the
implementer prompt `prompts/p9a_impl.md`.

Fix exactly the eleven items below. Change nothing else. This is the last change before the acceptance phase
and the host build, so two items deliberately move `BUILD_ID` and the unit rebuilds and republishes at the
end.

Environment for every shell:
```
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
```
`/tmp` is noexec: put scratch under `_scratch/te-tracks-audit/p9a-fix/` and remove it with Python
`shutil.rmtree`. No git writes of any kind. No installs. No network. Never write into
`/data2/users/shared/refcache`. Weaken or delete no test; if an existing check blocks you, name it and
report. Report a deviation instead of editing a number to fit.

## 1. Bind IRescue molecule conservation (codex B1, blocking)

In `tests/lib/consumers.py`, `irescue_check` reads the matrix and builds
`dict(zip((row[0] for row in features), counts))` before asserting conservation, so `zip` truncation hides
an extra matrix row and `dict` overwriting hides a duplicate feature name. Both were demonstrated by passing
a 100-count addition through the check.

Assert, before any dictionary exists: the matrix has exactly one row per feature-file line and one column
per barcode-file line; the feature names are unique; and the matrix total equals the expected molecule total
computed from the fixture. Then build the dictionary and keep the existing per-feature assertions. Add two
negative cases proving the new guard bites: a copy of a real IRescue output with one extra matrix row
carrying counts, and a copy with a duplicated feature line carrying counts. Each must make the check fail
with a named refusal. Keep the observed allocation recorded and unasserted.

## 2. Confine STARsolo support to the supported genes (codex B2, blocking)

In `tests/lib/consumers.py`, the STARsolo overlap case asserts the total and the two per-gene ranges and
never that support is confined to the genes the case's molecules support, so `HostGene=1.5`, `SubB=1.2`,
`Edge=0.3` satisfies every clause.

For every case and both `Gene` and `GeneFull`, require the set of genes carrying nonzero unique or
expectation-maximization support to be a subset of the genes the case's rows in
`tests/fixtures/consumers/starsolo_molecules.tsv` support, and require the total within that set to be
conserved. Keep the host against TE split observational, recorded and unasserted. Add a negative case
proving the guard bites: a replayed matrix placing support on a gene outside the case's supported set must
make the check fail with a named refusal.

## 3. Reattach the class-less rank claim to its cause (Opus B1, blocking)

`docs/OUTPUTS.md`, Dfam section, currently reads that class-less annotations retain their source `Unknown`
or `Unspecified` labels and explicit missing ranks. Measured: 54 names carry a class-less raw class, 53 leave
every Wicker rank `missing`, and those 53 are exactly the names whose Dfam classification leaf is `Unknown`.
`UCON4`, raw `Unspecified`, is an exact hit with leaf `Kolobok` and an inherited `wicker_class` of
`Class II (DNA transposons)`.

State the two facts separately: class-less annotations keep their source labels, and every Wicker rank is
`missing` for the names whose Dfam leaf is `Unknown`, of which there are 53. Name `UCON4` as the class-less
name that nevertheless inherits a code, so the rule cannot be misread.

## 4. Guard every derived rank cell (Opus A1, codex A1)

`tests/checks/core/33_taxonomy_dfam_view.py` censuses aggregates and `wicker_code`, so nine of the ten
Wicker value and status columns can be corrupted in the materialized table with the check still passing:
`wicker_class`, `wicker_subclass`, `wicker_subclass_status`, `wicker_order`, `wicker_order_status`,
`wicker_superfamily`, `wicker_superfamily_status`, `wicker_family`, `wicker_family_status`.

Re-derive every rank value and every rank status per row inside the check, from `wicker_code` and the node
tree of `dfam_lineage_nodes.tsv`, and compare cell by cell against the published table. Add a mutation case
per column against a scratch copy of the materialized table, each refused with a named discrepancy. In
`tests/checks/core/34_dfam_rule_fixtures.py` add the two untested build-error branches: a malformed Wicker
code with more than three slash-separated tokens, and an unknown superfamily letter.

## 5. Retain the snapshot provenance and bind `fetch_finished` (Opus A2, A3)

`fetch_finished` is the one `identity.build_sources` field anchored to nothing, because `verify_build`
passes `identity["build_sources"]` back as the tracked metadata and compares the field with itself; rewritten
to `1999-01-01T00:00:00.000000Z` with `BUILD_ID` recomputed, an archive verifies clean.

Retain `data/dfam/dfam_interspersed_mm39_snapshot.provenance.json` into the build under `source/` alongside
the snapshot, so it joins the inventory and the payload roster, and compare the tracked role's
`fetch_finished`, `dfam_version` and payload digest against that retained file in `verify_build`. Add the
case to `tests/checks/core/71_verify_build.py`: a rewritten `fetch_finished` with a recomputed `BUILD_ID`
must be refused by name. In `tests/fixtures/publication/build_fixture.py`, stop patching
`manifest.tracked_provenance` and let the fixture write a real provenance file, so the real branch and its
`"{role}: provenance sha256 differs"` refusal are exercised by a check.

This moves the payload roster from 51 to 52 entries and moves `BUILD_ID`. Update every place that states 51,
including `docs/OUTPUTS.md`, `docs/RELEASES.md`, `README.md` and any check or expectation, to the observed
number.

## 6. Enumerate the admitted source layouts (codex A2)

`src/lib/manifest.py` admits a hybrid archive that keeps `dfam_snapshot` while dropping `rmsk_out` from
`identity.build_sources`. No anchoring is lost, because `catalog.sources` binds `rmsk_out` and
`contig_set_sha256` binds `chrom_sizes`, so this is admission policy. Replace the permissive bound with an
explicit enumeration of the two supported layouts, the phase-8 three-role archive and the current
five-role build, each refused when its role set is neither. Add the hybrid as a refused case to check 71.

## 7. Name the parseable clade form and pin the rank scheme (Opus A4, A5)

The `clades` column of `taxonomy_dfam.tsv` and `taxonomy_dfam_models.tsv` joins whole clade paths with `;`,
the separator used inside each path, so the nine multi-clade cells cannot be split back. Plan 19 specified
that join, so keep it and document it: one sentence in `docs/OUTPUTS.md` naming `clades` a display field and
`dfam_model_clades.tsv` the join key for clade queries. Add a `clade_count` column to `taxonomy_dfam.tsv` so
a consumer detects the multi-clade case without parsing, and state its meaning.

`rank_scheme_wicker_v1` is named in `docs/DECISIONS.md` and `docs/OUTPUTS.md` and recorded in no artifact.
Record it in `identity` beside `taxonomy_rule_version` so a consumer can pin it, and state in
`docs/OUTPUTS.md` where it is recorded. This moves `BUILD_ID`.

## 8. Restore the measured producer range (Opus A6)

`docs/RELEASES.md` replaced the measured producer range of 5.5 GB to 6.0 GB resident across in-container
builds with a single figure. Restore the range as a range, keep the new observation beside it, and state
which stage each figure belongs to. The per-consumer and per-stage floors belong to `docs/RUNBOOK.md`, which
phase 9b writes; add nothing to the runbook here.

## 9. Derive the fetch script's output name (Opus A7)

`data/dfam/fetch_dfam_snapshot.py` requires `--universe` and hardcodes
`dfam_interspersed_mm39_snapshot.json.gz`, so a refresh for another universe writes a name contradicting its
contents. Derive the snapshot and provenance filenames from the universe and the genome. Keep the current
names identical for the current arguments, so the tracked bytes and their digests do not move.

## 10. Correct the stale contig roster message (codex A4, Opus A8)

`src/lib/contigs.py:134` says "eight UCSC inventory entries" while the effective roster holds nine. This
file is outside the phase 9a touch list and is allowed here for this one-line message alone. Make the
message state the roster size from the roster itself rather than a literal.

## 11. Describe the cellranger memory pin as a pin (Opus A9)

`cellranger mkref` completed without `--memgb` in the reviewer's run, so 3 GB is a defensive pin rather than
a documented minimum. Wherever the docs or the check's message present it as a requirement, state instead
that the check pins 3 GB.

## Rebuild and republish

Items 5 and 7 move `BUILD_ID`, so after the code and documentation changes:

1. Rebuild the core into `$TE_TRACKS_REFROOT/te_mm39/build` and publish it into
   `$TE_TRACKS_REFROOT/pubroot`, leaving the earlier archives in place.
2. Rebuild the child on the new parent into `$TE_TRACKS_REFROOT/te_mm39_gene/build` and publish it, leaving
   the earlier child archives in place.
3. Confirm `CATALOG_ID` is still
   `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` in core and child, that the child's
   `exon_subtraction_summary.tsv` is byte-identical to `tests/expectations/mm39/exon_subtraction_summary.tsv`,
   and that both earlier core archives still verify.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
for f in build.sh lib/common.sh src/*.sh src/gene/*.sh tests/run.sh tests/checks/consumers/*.sh; do bash -n "$f" && echo "syntax ok $f"; done
tests/run.sh core; echo "exit=$?"
source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh
tests/run.sh consumers; echo "exit=$?"
python3 src/99_verify.py "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive/9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d"; echo "exit=$?"
python3 src/99_verify.py "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive/763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c"; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39_gene; echo "exit=$?"
python3 -c "import json;i=json.load(open('$TE_TRACKS_REFROOT/te_mm39/build/MANIFEST.json'))['identity'];print(len(i['inventory']),len(i['export_contracts']),sorted(i['build_sources']),i.get('rank_scheme_version'))"
cat "$TE_TRACKS_REFROOT/te_mm39/build/BUILD_ID" "$TE_TRACKS_REFROOT/te_mm39/build/CATALOG_ID" "$TE_TRACKS_REFROOT/te_mm39_gene/build/BUILD_ID" "$TE_TRACKS_REFROOT/te_mm39_gene/build/CATALOG_ID"
cmp "$TE_TRACKS_REFROOT/te_mm39_gene/build/tables/exon_subtraction_summary.tsv" tests/expectations/mm39/exon_subtraction_summary.tsv && echo "child summary unchanged"
git status --short
```
Every suite must pass with no new unsupported check beyond Stellarscope's boundary defect.

## Final message
Each of the eleven items with the file and line you changed and the evidence the fix bites, naming the
refusal each new negative case produces; the new core and child `BUILD_ID`; the new payload roster size; the
acceptance outputs verbatim; every deviation.
