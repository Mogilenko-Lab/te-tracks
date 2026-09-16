# te-tracks — redesign staged, implementation next

## Where the work stands

The repository at `6ff3ee9` builds a reproducible canonical table from UCSC's RepeatMasker table
and reproduces its declared counts byte-identically on host and container (`BUILD_ID
3e75dad5f3a8…`). Nothing is published to the refcache yet. An audit, three fan-out consults and
six per-ADR consults (codex gpt-6-astra, xhigh) redesigned identity, universes, namespace, source,
build identity and scope; the owner ruled on 2026-09-16. Evidence: `redesign-2026-09/`.

## Next session starts here

`_project/plans/2026-09-16_te-tracks-redesign/03_next_session_agenda.md`, then `00_INDEX.md`.
Taxonomy resolves by rule in phase 3 and is checked against the Dfam snapshot in
`redesign-2026-09/taxonomy/`; the owner ruled out a manual curation step.

## Open at handoff

- Working tree carries uncommitted `docs/_internal/` and a `.gitignore` line; the owner decides the
  commit.
- Consumer executables are absent in-container; phase 5 reports them `unsupported` until installed.
- Gene context is a seam (phase 8) with its own design session to come.
