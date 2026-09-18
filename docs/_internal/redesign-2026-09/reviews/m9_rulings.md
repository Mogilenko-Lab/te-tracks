# Milestone 9 rulings

Phase 9b landed as `204ee66`. The seam review is `m9_codex.md`, verdict BLOCKING, 437 claims checked, four
false operational claims and one overbroad characterization. This file records the orchestrator's own
verification, the ruling on every finding, and the observations that lost their carrier.

## Orchestrator verification of phase 9b, before the reviews

Run whole, with output captured and exit status recorded, against
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`.

| Subject | Result |
|---|---|
| `tests/run.sh core` | 26 pass, exit 0 |
| `tests/run.sh acceptance` | 11 pass, exit 0 |
| `tests/run.sh consumers`, activated | 15 pass, 1 unsupported (Stellarscope right-boundary defect), exit 0 |
| four malformed invocations | exit 2 each: `--build --build`, `core --build`, bare `--refroot`, unknown mode |
| `src/99_verify.py` on six development and two acceptance archives | exit 0 each |
| `release.py verify-current`, both families under both roots | exit 0 each, each printing the expected full id |
| both identities recomputed from the manifests with an independent canonical-JSON encoder | equal to the files, without calling `release.py` |
| core inventory | 52 entries, payload 15,301,538,537 bytes, every entry's byte count equal to its file's size |
| child inventory | 21 entries, payload 2,157,717,760 bytes, same |
| `RELEASES.md` regular-file claim | 15,301,581,825 bytes over 55 files, exact |
| every path in the new consumer map | 66 of 66 present across three namespaces and both families |
| writers into `tests/expectations/` | none; the directory is read-only to every build |
| vendored word aside, the six pinned clones | all 16 `.ref` checkouts clean, at the commits the runbook's pin table names |

The acceptance build reproduced both development identities across a different commit because `provenance`
sits outside `identity`. The manifests record `builder_git_sha 51c016243c8991b27f0da112a00d90a815ead929`
with `builder_git_dirty: true`, disclosed in `RELEASES.md`.

## Rulings

**B1, consumer parser sources with no public reconstruction procedure. Upheld, fixed two ways.** The
required consumer checks load six sibling clones under `01_modules/.ref/`; the umbrella ignores that
directory and the referenced bootstrap creates none of them. The reviewer's probe made required IRescue
check 10 exit 1 through `git describe` exit 128. Both halves are defects: the prerequisite is undocumented,
and its absence surfaces as a traceback rather than as a sentence. The runbook publishes the six URLs,
destination paths, pinned commits and clone commands, and every helper that reaches into the checkout
directory raises `Unsupported` with the restoration command named. Check 10 stays required, so the runner
still exits 1; the operator learns why in one line. The word `vendored` is corrected wherever it describes
these clones, since they are pinned clones in an ignored sibling directory.

**B2, a clean-builder gate that stops nothing. Upheld, and moved into the tool.** The runbook asserted
`builder_git_dirty is False` in a heredoc under `bash -l` with no `set -e`, so the reviewer's probe printed
`AssertionError`, reached the selection step and returned 0. A gate written in prose is a suggestion.
`release.py install` and `select` gain `--require-clean`, which refuses a dirty manifest by name and exits
nonzero; the default stays permissive so in-container builds and `acceptance --build` keep working against
their deliberately dirty trees. The runbook drops both heredocs, passes the flag on the host calls, and
reads fail-fast. A core check proves the refusal and the permissive default.

**A1, the reproducibility claim. Upheld as a wording defect.** The sibling bootstrap upgrades packaging
tools without pins, installs git requirements without consuming `pip-freeze.txt`, and extracts downloads
without enforcing hashes. That package is not ours to edit, so the claim narrows to what the recipe
reproduces today, the five pinned tool commits and the recorded installed versions, with the three gaps
named as the consuming module's work.

**A2, a delivered thing recorded as deferred. Upheld.** `DECISIONS.md` still defers the consumer
environment to phase 9; it is delivered by reference in the runbook. The deferral is replaced with the
delivered state and the pilot gates that remain.

**A3, reproduction pins described as correctness evidence. Upheld, and it sharpens a distinction worth
keeping.** `identity.tsv` carries two build ids and file-size literals taken from an earlier development
build and preserved before the build they judge. That is evidence of reproduction. Nine of the ten
expectation tables trace to a plan, ruling or independent review; the reviewer traced each one and answered
"could only the judged build supply this?" with no for all nine. The expectations README splits its column
so a reader sees which rows are external or authored oracles and which are prior-output fingerprints. Every
pin and the fatal discrepancy assertion stay.

**A4, an oracle whose evidence is half pinned. Upheld, with the reviewer's count preferred over mine.**
The file holds eleven literals, so ten of the eighteen printed metrics are pinned, rather than the twelve I
first counted. Every printed metric gets a pin sourced from an internal record; a value no record carries is
reported rather than read from the build.

**The identity model, tested rather than read. No finding.** The reviewer changed a gzip timestamp and moved
`BUILD_ID` while `CATALOG_ID` held; changed a canonical record score and moved both; appended a byte to
qualification and alias copies and moved `BUILD_ID` alone. No canonical-record change preserved the catalog
and no inventoried-byte change preserved the build. The one published-byte exception, raw manifest
provenance, is specified at `RELEASES.md:101-104` and is the same boundary the phase 9a threat-model ruling
drew. Dependency refusal holds: an absent parent and an earlier valid parent sharing the catalog both exit 1.

**The acceptance suite can fail. No finding, with one characterization corrected.** `core_checks()` replays
existing core contracts at full scale against the acceptance archives, which is scale coverage rather than
fresh authoring. Taxonomy and namespaces have no fresh acceptance algorithm of their own; their claims rest
on external fixtures and reference evidence, which is what keeps them meaningful. Source, record profile,
publication, the bedtools oracle and the legacy reconciliation are fresh measurements. No acceptance check
is incapable of failing.

## Observations that lost their carrier

The phase scratch holding phase 9b's build and floor logs was removed by its own prompt, so nine raw
observations in the public documents have no witness a reader can reach: the initial export peak
6,807,732,224 bytes; the initial child 874,917,888 bytes and 152.012 seconds; and the two reader triples in
the resource-floor table. The final manifests independently retain 4,936,556,544, 881,565,696 and 154.376.

Ruling: a number in a public document has a carrier a reader can reach. Each of the nine either cites the
internal record that carries it or moves here as a recorded observation. The consumer annotation-load
projections stay, since a consumer plans with them, carried by the reproduction command and their anchor's
internal record.

Standing consequence for every later prompt: a prompt that asks for a measurement names the durable place
its log lands, outside the scratch it will delete.

## The export peak spread

Two fresh builds of identical payload measured 4,936,556,544 and 6,807,732,224 resident bytes in the export
writer, a spread of 1,871,175,680 bytes, 38 percent of the smaller. Equal output digests do not imply equal
allocation. The 16 GB single-producer reservation has headroom over both and over the historical complete
peak near 9 GB, and two observations establish no upper bound, which is why the runbook asks for a complete
host measurement rather than treating a stage figure as the floor.

## The Opus review of phase 9b

`p9b_opus.md`, verdict PASS WITH ADVISORIES. Twenty-two defects injected into real copies of the acceptance
archives; twenty-one make the suite fail, and all ten the brief named are caught by the area that owns them.
Every literal in `areas.py` and in the ten expectation tables was recomputed from the archive bytes and
matched, including both identities re-derived from the manifests without `src/`. The reviewer traced every
expectation to a plan, ruling or earlier review: `source_pins.tsv` to the two config files,
`source_qualification.tsv` to `p1_codex.md:56` and `m2_opus.md`, `record_census.tsv` across plan 19 and four
reviews, `identity.tsv` to `p9a_rulings.md:301` and `p8_codex.md:102,107`, `gene_oracle.tsv` to two
reviewers' own bedtools runs adopted in `p8_rulings.md`. No expectation traces only to the build it judges.

**A1, the suite cannot fail on a damaged archive. Upheld; this is the defect class the project treats as
most expensive.** With `MANIFEST.json` removed from an archive whose `current` still resolves, eleven checks
report `unsupported` and the runner exits 0, indistinguishable from an empty reference root, while the
README and the phase commit cite that exit as the witness. Two changes: an archive that resolves but is
incomplete fails rather than reporting unsupported, and all eleven checks become `*.required.py` so a suite
that judged nothing cannot exit 0. An acceptance root with no build stays a legitimate state and now exits 1
with the message naming `acceptance --build`.

**A2, the geometry oracle covers 5.4 percent of child blocks. Upheld, fixed by widening rather than by
disclosure alone.** Three contigs hold 200,697 of 3,684,934 interspersed blocks; an off-by-one on chr7
passes the oracle and is caught only by the area that compares the SAF against the builder's own
registration, which is self-consistency. One large annotated autosome joins the contig list, the check's
summary line reports the block coverage, and `PROVENANCE.md`'s oracle table states the covered fraction.
The new contig's metrics are new anchors and are reported as such rather than presented as a prior record's.

**A3, a locale-dependent sort feeding a codepoint merge. Upheld.** GNU `sort` under `en_US.UTF-8` orders
`chr10` before `chr1 100`, Python's codepoint comparison does not. Equal multisets still compare line for
line, so the passing verdict stands and a real difference still fails; the directional counts and sampled
examples were unreliable. `env LC_ALL=C sort` for both streams.

**A4, the acceptance scratch ignores `--refroot`. Upheld**, and it is the same defect as the hardcoded path
in `consumer_floor.py`. Both derive their scratch from `TE_TRACKS_REFROOT`.

**A5, a vacuous assertion. Upheld.** The 49-family census is asserted only inside a loop over rows carrying
that level, so renaming the level satisfies it with no iterations. The level's presence is asserted first.

**A6, a conditional comparison with an unconditional-sounding summary. Upheld as wording.** The
development-build comparison runs when that build exists; the unconditional protection beside it is the
pinned `identity.tsv` comparison, which stays. The summary line says which ran.

One measurement worth carrying: a full `tests/run.sh acceptance` against the untouched reference root took
54 minutes 33 seconds at 11 of 11. That goes beside the acceptance commands, since a consumer planning a
verification needs it.

One count settled between the two reviews: `gene_oracle.tsv` holds eleven data rows. The codex count is
right, mine of twelve and the Opus table's twelve both counted the header.

## Fix-round evidence

The nine phase 9b observations below are retained here as historical observations after their
original raw logs were removed. The fix removes them from the public resource tables. The final
acceptance-manifest measurements remain in the public documents.

| Observation | Recorded value | Public disposition |
|---|---:|---|
| Initial core export peak RSS | 6,807,732,224 bytes | Moved here from RUNBOOK and RELEASES |
| Initial child subtraction peak RSS | 874,917,888 bytes | Moved here from RUNBOOK and RELEASES |
| Initial child subtraction elapsed time | 152.012 s | Moved here from RUNBOOK and RELEASES |
| Stellarscope annotation resident increase | 133,443,584 bytes | Moved here from RUNBOOK |
| Stellarscope process peak RSS | 152,317,952 bytes | Moved here from RUNBOOK |
| Stellarscope annotation load time | 1.751 s | Moved here from RUNBOOK |
| TElocal annotation resident increase | 51,904,512 bytes | Moved here from RUNBOOK; the separate phase 9a anchor stays with its citation |
| TElocal process peak RSS | 70,189,056 bytes | Moved here from RUNBOOK |
| TElocal annotation load time | 12.367 s | Moved here from RUNBOOK |

The six newly pinned earlier-oracle metrics come from `p8_codex.md:178–179` and the annotation
absence adopted in `p8_rulings.md:41–42`: chr18 input_records=118502 and union_bp=4528733;
random-contig exon_rows=0, union_intervals=0, union_bp=0 and retained_bp=385. No earlier internal
review or ruling carrying chr18 or chr19 exon_rows was found; those two literals remain unpinned.

The additional contig chr7 has new anchors measured by this fix's bedtools merge/subtract run:
input_records=214663, exon_rows=90795, union_intervals=24978, union_bp=12521871,
blocks=207048 and retained_bp=60028394. They are saved separately in `gene_oracle_m9.tsv`.
Together chr18, chr19, chr1_MU069434v1_random and chr7 cover 407745 of 3684934 child interspersed
blocks (11.07%). The measurement logs are retained in the repository at
`docs/_internal/redesign-2026-09/measurements/m9fix/`: `focused-initial.log` carries the oracle run,
`demonstrations.log` the five demonstrations verbatim, `validation.log` the suite run the implementer
completed, `checkout-origins.tsv` the six clone URLs read from the checkouts themselves, and
`implementer_state.md` the unit's own account of what it did before its quota ended.

The orchestrator then reproduced the chr7 anchors with an independently written bedtools pipeline and
obtained every value exactly: input_records 214,663, exon_rows 90,795, union_intervals 24,978, union_bp
12,521,871, blocks 207,048 and retained_bp 60,028,394, with multiset equality against the child SAF on
chr7, chr18 and chr19. Two independent pipelines therefore stand behind them, so they are anchors rather
than the implementer's own output. That run also supplied the two literals no earlier record carried,
chr18 exon_rows 35,853 and chr19 exon_rows 39,613, which are now pinned in `gene_oracle_m9.tsv`. Every
metric the oracle prints is pinned.
