Milestone review after phase 7 of the te-tracks redesign: what identity and publication still assume. Repository:
/workspaces/Meta-Aging/01_modules/te-tracks (git branch redesign-2026-09, commit 9d16506). You are a read-only
reviewer working from the documented artifacts, the build and the published root; write exactly one file,
docs/_internal/redesign-2026-09/reviews/m7_divergent.md, and change nothing else. No git writes (the checkouts
under /workspaces/Meta-Aging/01_modules/.ref/ are git repositories too). Export PYTHONDONTWRITEBYTECODE=1.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/00_INDEX.md, 16_ to 19_ (the remaining phases).
2. docs/_internal/redesign-2026-09/reviews/{m2_divergent,m5_divergent,m5_rulings,p6_rulings,p7_rulings}.md: your
   predecessors' findings and how they were ruled.
3. docs/_internal/redesign-2026-09/consults/{owner_context_2026-09-15,ADR67_consult,ADR38_consult,gene_context_material}.md.
4. The public contract: README.md, docs/DECISIONS.md, docs/OUTPUTS.md, docs/RELEASES.md.
5. The consumer's need: /workspaces/Meta-Aging/14761-DM/AGENTS.md and the D2/D3 plan under
   /workspaces/Meta-Aging/14761-DM/docs/_internal/_project/plans/2026-09-11_codebase-topology/.
6. The code: build.sh, src/release.py, src/lib/manifest.py, src/lib/build_exports.py (EXPORT_CONTRACTS),
   bin/te-tracks-preflight; the build under /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build
   and the published root .../refroot/pubroot (read-only; BUILD_ID 0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a, CATALOG_ID 0c0a959dea69e397890b590b640162d5bd45e71a88f6468cadd4b7615022b4a4).

Your question is the one the other two reviewers do not ask: what do identity and publication take for granted
that the record does not defend? Attack, with a specific failure each:
- the host: /data2/users/shared/refcache is a bind mount whose filesystem, group ownership and ACLs differ from
  this container's ext4 scratch; flock as cooperative locking; rename atomicity and one-filesystem staging; a
  relative `current` symlink resolved by consumers on other machines; umask 002 and mode 2775 against the host's
  users; readers holding an archive open across a selector swap;
- the identity: `export_contracts` inside BUILD_ID, so renaming a consumer in a docstring-like field mints a new
  build; `consumer_keys` as a file-format fact; the narrowed CATALOG_ID (rmsk_out alone) against a UCSC rmsk table
  or chromAlias change that qualification would have caught; the published-version tuples as the only forward
  compatibility; SPECIES as a hand-kept table; the devcontainer image identity that cannot be recorded here;
- the verifier: judging an archive against its own declaration, so a build that declared a wrong contract verifies
  forever; the authoring-time cross-check as the only defence; `schema_version` with one value;
- the consumer pins: raw MANIFEST.json sha256 as a pin when converged rebuilds keep the first manifest; the ledger
  key `(te_catalog_id, rmsk_record_id)` across a CATALOG_ID change; preflight walking up to the nearest alias table
  from a published archive path;
- the remaining phases: the child family pinning `parent_build_id` in a root whose `current` may move (8); the
  gene-context ADR discussion the owner has yet to hold (8); the compat reconciliation against the legacy SAF and the
  host-versus-container build comparison (9); the owner's first host build at 6 GB resident and 10.5 GB disk;
- process: seven phases of rulings files; a fix prompt as the only record of some contract amendments; reviewers
  reading the orchestrator's build; the dossier written by an agent and spot-checked by the orchestrator.

For each assumption: state it in one sentence, give the concrete failure it predicts (inputs and the wrong output or
the silent gap), rate the cost of being wrong (low, medium, high), and say which phase should address it or whether
it is a recorded deferral already. If an assumption is defended somewhere in the record, cite the file and line and
move on.

Format:
# Milestone 7 review: unstated assumptions (divergent)
## High
- [H1] assumption — failure — evidence — phase
## Medium
- [M1] ...
## Low
- [L1] ...
## Defended already
- one line each, with citation
Under 150 lines. Specific over general; measure from the build and the published root where a measurement settles
the point.
