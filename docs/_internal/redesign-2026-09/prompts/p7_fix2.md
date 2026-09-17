# te-tracks phase 7 fix 2 (unit `te-tracks-p7-fix2`): two provisioning sentences

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks` (branch `redesign-2026-09`, HEAD `99bf646`; the phase 7
tree sits uncommitted on top). You edit exactly one file: `docs/RELEASES.md`. No git writes anywhere, no installs, no
network, no other edits. Read `/workspaces/Meta-Aging/AGENTS.md` section "Prose" first.

The phase 7 fix measured that two literals in the retention paragraph move from build to build: the `du -sb` total
changes with `MANIFEST.json` provenance bytes (10,462,001,814 before re-manifesting, 10,462,001,615 after, 10,462,001,625
in the published archive), and `provenance.peak_rss_bytes` differs per run (5,498,744,832 in the published build,
5,968,367,616 and 6,032,502,784 in earlier builds). Public prose states stable measured properties.

1. In `docs/RELEASES.md` "Consumer pins and retention", the sentence naming the `du -sb` figure becomes: the whole build
   directory measures about 10.46 GB by `du -sb`, the provisioning size, with the exact total varying by a few hundred
   bytes with the manifest's provenance. Keep the exact payload sum 10,461,884,289 and the per-namespace and registration
   figures as they are.
2. The resident-floor sentences become: the export writer peaks near 6.0 GB resident, measured between 5.5 GB and
   6.0 GB across in-container builds; `provenance.peak_rss_bytes` records each build's own measurement. The literal
   5,968,367,616 leaves the file.

Acceptance (run and paste):
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
grep -n "10,462,001\|5,968,367,616\|5,498,744,832" docs/RELEASES.md || echo "no per-build literals"
grep -n "10.46 GB\|10,461,884,289\|5.5 GB\|6.0 GB\|peak_rss_bytes" docs/RELEASES.md
git status --short docs/RELEASES.md
```
Final message: the two sentences as written, the acceptance output, any deviation.
