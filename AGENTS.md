# te-tracks

This package owns a reference projection of RepeatMasker for one assembly: canonical tables,
universes, exports and fixtures. Quantification, biological interpretation and knowledge of
downstream assays belong to consuming projects and sit outside this package's scope.

## Execution

`/data2/users/shared/refcache` is read-only inside the container. Builds and publication run on
the host. Tests run in-container against a scratch reference root.

```bash
tests/run.sh core
tests/run.sh consumers
tests/run.sh acceptance
tests/run.sh core --refroot /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
```

The default `TE_TRACKS_REFROOT` is `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`;
`--refroot DIR` selects another scratch root for any mode and is exported as an absolute path.
Checks are `tests/checks/<mode>/*.sh` and `*.py`, run in name order through `bash` or `python3`
regardless of file mode. A check exit of 0 is pass, 3 is unsupported and any other exit is fail.
A failing check makes the runner exit 1, as does an unsupported check whose name ends in
`.required.sh` or `.required.py`. Bad usage and a missing check directory exit 2.

## Review

Follow the [review protocol](docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/02_orchestration.md).
Git writes require the owner's explicit authorization. Commit messages describe the change;
AI attribution and co-authorship trailers are excluded.

## Writing

Public prose is affirmative and brief: state what a thing is. Omit contrastive negation.
Comments state intent only, briefly and affirmatively, in one line.
