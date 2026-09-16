# Phase 7: manifest, BUILD_ID, publication

Deliverables
- `src/90_manifest.py`: two-section manifest. `identity`: schema_version, family, species, assembly,
  contig set digest, sources with url and observed digests, declared run identity, universe
  predicates, export contracts, taxonomy rule version, parent build id (child family), complete file
  inventory with SHA-256. `provenance`: builder sha, tool versions, invocation, validation summary.
  `BUILD_ID = sha256("te-tracks-build-v1\n" + canonical_json(identity))`.
- `src/99_verify.py`: exact inventory equality, digests, id recomputation, schema and key
  assertions, bounds; scratch outside the snapshot.
- `src/release.py`: staging under `<root>/te_mm39/.staging/<tmp>/`; verify; no-replace install into
  `archive/<BUILD_ID>/`; `current` swapped by temporary symlink and `os.replace`; a corrupt existing
  `current` aborts with the discrepancy; explicit family root argument.
- `build.sh` rewritten around these; `INDEX.tsv`, `CURRENT_BUILD.tsv`, dated snapshots and
  archive-on-supersede removed; `docs/RELEASES.md` rewritten.
- `tests/run.sh core` publication smoke cases in a scratch root: identical rebuild converges;
  same-day changed policy yields a second archive; failed build leaves `current` valid; new export
  yields a new id; two concurrent identical builds converge; an old id resolves at
  `archive/<id>/`; forged `BUILD_ID` file rejected; corrupt current detected.
- `docs/RELEASES.md` transfer procedure: copy into destination staging, verify there, install.

Acceptance: all smoke cases pass in-container against `_scratch`; permissions normalized under
`umask 002`; verifier leaves the snapshot byte-identical.

Milestone review after this phase: publication seam, run on the host root by the owner.
