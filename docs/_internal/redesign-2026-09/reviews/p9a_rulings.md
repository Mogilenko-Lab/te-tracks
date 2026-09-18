# Phase 9a rulings (orchestrator, 2026-09-17)

Phase 9a landed from `te-tracks-p9a-impl` (codex `gpt-6-astra`, xhigh, run `20260917T173249Z-3759311`,
2 h 45 m). The launcher recorded `result_exit=32` with `codex_exit=0`; the cause is now known and is not a
run failure, see "The launcher's blind-run guard" below. Two reviews ran in parallel and independently:
`te-tracks-p9a-review` (codex `gpt-6-astra`, xhigh) wrote `reviews/p9a_codex.md`, and the `opus-reviewer`
agent `opus-p9a` wrote `reviews/p9a_opus.md`. The Opus pass did not read the codex review, which appeared in
the tree during its run.

## Orchestrator verification before the reviews

Run by the orchestrator against the frozen tree, each measurement with its own code rather than by reading a
check's output.

| item | result |
|---|---|
| `tests/run.sh core` | 26 of 26 pass, exit 0 |
| `tests/run.sh consumers` with the shims on PATH | 16 checks, 15 pass, 1 unsupported (Stellarscope boundary) |
| each `record_starsolo.gtf`, own streaming parse | 3,764,949 rows and 3,764,949 distinct `gene_id`, 59 contigs, every feature `exon`, zero attribute-order violations |
| Dfam strict part rule recomputed from the snapshot | 1,047 exact, 147 part_model_set, 26 missing; all 1,220 published rows agree per name |
| companion tables | `taxonomy_dfam_models.tsv` 1,264 lines, `dfam_lineage_nodes.tsv` 301, `dfam_model_clades.tsv` 1,279 |
| identity | 51 inventory entries, 27 export contracts, five `build_sources` roles, `catalog.sources` `['rmsk_out']` |
| ids | core `763815187e…`, child `693ba1aa15…`, `CATALOG_ID` `90cc18be5d…` in both |
| phase-8 core archive | 43 entries, 24 contracts, `99_verify.py` exit 0 |
| child | `release.py verify-current` exit 0, pins the new parent, `exon_subtraction_summary.tsv` byte-identical to the committed expectation |
| working tree | 38 `git status --short` entries plus three files under `data/dfam/`, so 40 created or changed |

Every number the implementer reported is confirmed. The two reviews then found what counting cannot: checks
that pass mutations they should refuse.

## Codex rulings

**B1 accepted, blocking.** `tests/lib/consumers.py` builds the IRescue count dictionary as
`dict(zip((row[0] for row in features), counts))` and only then asserts conservation. The orchestrator
confirmed the mechanism by reading the code: `zip` truncates silently when the matrix carries more rows than
the feature file, and `dict` overwrites when a feature name repeats, so mass disappears before the sum is
taken. The reviewer demonstrated both: an extra 100-count matrix row passed, and a duplicate registered
feature row with 100 counts passed. Molecule conservation is the guarantee the third-round ruling asked this
check to assert, so an unbindable conservation assertion is a contract failure.

**B2 accepted, blocking.** The STARsolo overlap case asserts the total and per-gene ranges for `HostGene`
and the `SubB` record, and never that support is confined to the genes the case's molecules support. The
orchestrator confirmed by reading the assertions: `HostGene=1.5`, `SubB=1.2`, `Edge=0.3` satisfies every
clause while placing support on a gene `tests/fixtures/consumers/starsolo_molecules.tsv` does not support.

**A1 accepted, folded into Opus A1**, which measures the same gap precisely.

**A2 accepted.** The source-layout bound admits a hybrid archive that keeps `dfam_snapshot` while dropping
`rmsk_out` from `identity.build_sources`. Opus's seam 3 establishes that no anchoring is lost, because
`catalog.sources` binds `rmsk_out` and `contig_set_sha256` binds `chrom_sizes`, so this is admission policy
rather than a hole. Enumerating the supported layouts is cheap and the package is being parked, so it lands.

**A3 accepted.** `docs/OUTPUTS.md` states the LTR-only measurement without naming `all_rmsk`, and the
consumer registration table still labels rows by `(feature_level, key_grammar)` with no table-wide universe
and variant default. The matrix-binding sentence itself is correct.

**A4 accepted**, the same finding as Opus A8 and the implementer's D6.

## Opus rulings

**B1 accepted, blocking, documentation only.** The Dfam section of `docs/OUTPUTS.md` says class-less
annotations carry explicit missing ranks. The orchestrator reproduced the counterexample: 54 names carry a
class-less raw class, 53 leave every Wicker rank `missing`, and those 53 are exactly the names whose Dfam
leaf is `Unknown`; `UCON4`, raw `Unspecified`, is an exact hit with leaf `Kolobok` and an inherited
`wicker_class` of `Class II (DNA transposons)`. A consumer reading the sentence as a rule mis-handles that
row. The claim is reattached to its cause.

**A1 accepted.** Nine of the ten Wicker value and status columns can be corrupted in the materialized table
with check 33 still passing, because the check censuses aggregates and the code, never the per-row derived
values. The published cells are all correct today, confirmed by two independent rederivations, so this is a
drift gap rather than a defect in the data. A drift gap in the flagship new table becomes permanent at
parking, so it closes now, together with check 34's missing malformed-code and unknown-superfamily-letter
cases.

**A2 accepted.** `fetch_finished` is compared with itself, because `verify_build` passes
`identity["build_sources"]` back in as the tracked metadata, and the snapshot's provenance JSON is not
retained in the payload. Retaining it under `source/` puts it in the inventory and the roster and gives
`fetch_finished` something to be compared against. This moves the payload roster and `BUILD_ID`, which is
the right moment for it: before the host build rather than after.

**A3 accepted**, and it follows from A2: with a retained provenance file the publication fixture can
exercise the real provenance branch and its refusal instead of patching it out.

**A4 accepted as documentation.** The `clades` cell joins whole clade paths with `;`, the separator used
inside each path, so the nine multi-clade cells cannot be split back. Plan 19 specified that join and
`dfam_model_clades.tsv` is the parseable form, so the fix names `clades` a display field and the clade table
the join key, and adds a count so a consumer detects the multi-clade case without parsing.

**A5 accepted.** `rank_scheme_wicker_v1` is named in `docs/DECISIONS.md` and `docs/OUTPUTS.md` and recorded
in no artifact, so a consumer told to pin the scheme has nothing to pin. It joins `identity` beside
`taxonomy_rule_version`.

**A6 accepted.** `docs/RELEASES.md` replaced the measured 5.5 to 6.0 GB producer range with a single figure,
and the new 9 GB peak is recorded in no artifact. The range returns to `docs/RELEASES.md`; the per-stage
floors belong to the runbook, which phase 9b writes.

**A7 accepted.** `data/dfam/fetch_dfam_snapshot.py` requires `--universe` and hardcodes the output filename,
so a refresh for another universe writes a name that contradicts its contents.

**A8 accepted**, the same as codex A4 and D6, with an explicit allowance to touch `src/lib/contigs.py`.

**A9 accepted as a wording correction.** `cellranger mkref` completed without `--memgb` in the reviewer's
run, so the 3 GB figure is a defensive pin rather than a documented minimum, and D8's necessity claim does
not stand as stated. The pin stays; the sentence describes it as a pin.

## Deviations

D1 to D7 accepted by both reviewers with evidence, and by the orchestrator: the plan governs the
`Unknown`-name rank rule; the three-role phase-8 archive still verifies beside the five-role build; the
census shortfall of 4,367 records across 20 multi-label names is the fetch artifact's plurality row and the
builder takes its weights from the catalog; the instance figures are correct under their stated scopes; the
required parser check was named by a deliverable and omitted from the touch list, which is a prompt defect;
the stale contigs message is reported rather than silently fixed, which was the right restraint; and the
transient runner failure from a live edit leaves no defect, since the frozen tree passes 26 of 26 in three
independent runs. D8 is corrected by Opus A9.

## The launcher's blind-run guard

`launch.sh` sets `result_exit=32` when it finds `bwrap`, `landlock`, `new namespace` or `sandbox helper`
anywhere in the stream log, on the theory that the sandbox blocked file access and the worker wrote blind.
The phase 9a stream matched exactly once, on the word `bwrap` at line 575, which is the umbrella
`AGENTS.md` sentence recording that codex's bwrap sandbox cannot start in this container. Codex reads
`AGENTS.md` as project context and echoes it, so every codex run in this repository trips the guard
deterministically. Nothing was written blind; `codex_exit` was 0 and the 49,618-byte report matches the
repository state. The guard belongs to the scio toolkit and propagates to every dataset, so it is reported
to the owner rather than edited here; the fix is to require a co-occurring failure signature instead of the
bare word.

## The fix

One unit, `prompts/p9a_fix.md`, with eleven items: the two blocking check defects, the blocking
documentation clause, the rank-drift gap and its two fixture cases, the retained provenance with its
verifier comparison and publication case, the enumerated source layouts, the clades and rank-scheme
documentation, the restored producer range, the fetch script's output name, the stale contigs message, and
the cellranger wording. Items that move `BUILD_ID` are the retained provenance and the recorded rank
scheme, so the unit rebuilds the core and then the child and republishes both into the scratch root.

## Full-scale consumer validation (orchestrator, after the reviews)

Both reviews exercised the consumer grammars on the eleven-record fixture, which is what the checks cover.
The parking claim is that a downstream consumer can read the published exports, so the orchestrator ran the
two readers that parse a whole export at genome scale. Scratch under
`_scratch/te-tracks-audit/scale-check/`, removed with Python `shutil.rmtree`.

| reader | input | result |
|---|---|---|
| `cellranger mkgtf` 10.1.0 | `exports/gencode/interspersed/full/record_starsolo.gtf`, 1.6 GB | exit 0 in 64.6 s, all 3,764,949 rows retained under `gene_type:transposable_element` |
| `featureCounts` v2.1.1 | the child's `exports/ucsc/interspersed/exon_subtracted/subfamily.saf`, 3,684,935 lines | annotation loaded as 3,684,934 features, 1,220 meta-features, 59 contigs, in 4.4 s; three reads placed on the first three chr1 blocks assigned at 100% |

The first establishes that the record-as-gene grammar survives cellranger's reference filter at full scale,
with `|` and `:` in every `gene_id`, which the eleven-record fixture cannot establish. The second
establishes that the bulk product's `GeneID` grouping collapses to exactly the 1,220 subfamilies over the 59
contigs the catalog carries.

## Consumer annotation floors (orchestrator, for the milestone 5 ruling H3 anchor)

Measured on this image from a 50,000-row head of `exports/ucsc/interspersed/full/record.gtf`, with
`resource.getrusage` around the annotation load alone. Scratch removed with Python `shutil.rmtree`.

| reader | resident bytes for 50,000 rows | seconds | bytes per row | projected to 3,764,949 rows |
|---|---:|---:|---:|---|
| Stellarscope 1.5 `IntervalTreeAnnotation(gtf, 'locus', 'exon')` | 134,418,432 | 1.79 | 2,688 | 10.1 GB, 2.2 min |
| TElocal 1.1.3 `TEfeatures.build` | 51,904,512 | 12.21 | 1,038 | 3.9 GB, 15.3 min |

A consumer loading the whole record profile therefore needs about 10 GB resident for Stellarscope and about
4 GB for TElocal, against the producer's own peak of 9.0 GB for the core build. These are the figures the
runbook states, so phase 9b reproduces rather than re-derives them.

## An orchestration hazard found while verifying the fix

The orchestrator ran `tests/run.sh core` while the Opus fix reviewer was running its mutation tests against
the same reference root, and that run recorded 26 checks with 25 passing and 1 failing, against the
implementer's and the orchestrator's earlier clean runs. The failing check's name was lost because the
command piped through `tail`, which also masked the runner's exit status.

Investigated rather than retried, and the first hypothesis was wrong. The build directory and the current
core archive both verify clean at exit 0 afterwards, and every publication check isolates its own work in a
`TemporaryDirectory` under `$TE_TRACKS_REFROOT/pubtest`. The orchestrator then suspected the reviewer's
method, because an earlier Opus pass reported mutating "a hardlinked copy" of the build and a hardlink shares
its inode, so a write to the copy would write through to the real build. That suspicion was wrong twice over,
and the reviewer's own account is the authority on its method. It did use `cp -al`, and every write into that
copy went through `unlink()` followed by `write_bytes()`, which breaks the link and allocates a new inode, so
the three files it touched left the archive's copies holding their original inodes at mode 0444 with their
published digests, while an untouched file still showed two links. No write reached the reviewed build or any
archive, which the closing verification of all six archives and both families confirms. The distinction worth
keeping is narrower than the warning the orchestrator sent: a hardlinked copy is safe to replace a file in
and unsafe to modify a file in place in, and `unlink` then write is a replacement.

The cause is undetermined, and saying so is the honest end of this. The orchestrator's second hypothesis
was a shared path: `tests/lib/consumers.py` resolves its generated fixture directory to
`$TE_TRACKS_REFROOT/fixtures/consumers` unless `TE_TRACKS_CONSUMER_FIXTURES` overrides it, 226 files were
rewritten there during the overlap, and the reviewer had not been told to redirect it. That does not explain
this failure either: no check under `tests/checks/core/` imports that library, so a core run never touches
that directory. The reviewer offers a third explanation, resource pressure, since check 41 alone holds about
9.4 GB resident and two concurrent instances approach 19 GB; this host carries 502 GB, so that is weak on its
own. The decisive fact was destroyed by the orchestrator's own command: piping the run through `tail`
discarded the failing check's name and the runner's exit status, so nothing can now attribute it.

What is established: the fix's own suite run, the reviewer's independent run and the orchestrator's clean
re-run with an isolated fixture directory each pass 26 of 26 at exit 0, every one of the six published
archives verifies, and `verify-current` exits 0 for both families. A single unattributable failure in a
concurrent run against a package that passes cleanly three times over is recorded as transient and
unexplained rather than given a cause it has not earned.

Four practices follow anyway, each worth keeping on its own terms.

- Capture a suite run whole. A run summarised through `tail` cannot be diagnosed.
- Do not run a verification suite concurrently with a mutation-testing reviewer against one reference root.
  Sequence them, or give the reviewer its own root.
- Reviewer prompts set `TE_TRACKS_CONSUMER_FIXTURES` into the reviewer's own scratch, because the default is
  a fixed path under the shared reference root and two consumer-suite runs would overwrite each other.
- Reviewer prompts require a real copy for every mutation and forbid `cp -al`, `cp -l` and `shutil.copytree`
  with a linking copy function, and ask for a closing verification. The reviewer's own account shows why the
  rule is worth more than the hazard it names: its isolation held only because every write went through
  `unlink` then `write_bytes`, and one `open("w")` would have reached a published archive through the shared
  inode. A rule that removes the need to get that right under time pressure is the cheaper instrument.

The clean re-run after the reviewer finishes is the record of the fix's suite result.

## Rulings on the Opus review of the fix

`reviews/p9a_fix_opus.md`: PASS WITH ADVISORIES, zero blocking, five advisory, every one of the eleven items
biting under 64 mutations of which 57 refused by name and 5 were accepted by design. The reviewer recomputed
both ids from the canonical identity JSON, confirmed `CATALOG_ID` unmoved, confirmed the 52-entry roster and
that every statement of 51 is gone, verified all six published archives and both families, and found the
scope exactly the eleven items across fifteen files. The orchestrator had already read both new guards and
found them fixture-derived; the reviewer proved the derivation by adding a fixture molecule and watching a
refused replay turn into a pass, which is the stronger demonstration.

**A1 accepted as a documentation defect, and the verifier is left as it is.** The retained provenance anchors
`fetch_finished` only for archives that carry `rank_scheme_version`, and the reviewer presented the old shape
by dropping the rank scheme, the provenance and its inventory entry together, forging the timestamp and
recomputing `BUILD_ID`, which verified clean. The branch has a live caller, the phase-9a implementation
archive, so the condition is the same backward compatibility the phase-8 archive receives. Tightening it
would make that archive unverifiable, and the exposure it closes is a hand-edited archive, which is outside
what this design promises: the verifier detects corruption and drift, while a consumer's protection is
pinning the full id and the digests of the files it reads. Every archive this builder writes carries the
provenance unconditionally. What is actually wrong is one sentence, `docs/RELEASES.md:54`, which states
unconditionally what the code does only for archives that retain the file. The sentence is corrected and the
threat model is stated plainly beside it. The input boundary, where an edit would really enter, is closed by
A4 instead.

**A2 accepted.** Check 33 prints its refusal list before its census and the runner shows a passing check's
first line alone, so the Dfam census that the reviews and these rulings quote has left the suite output.
Checks 34 and 71 already print the summary first and append their refusals; check 33 matches them.

**A3 accepted.** Two of the ten rank-column mutations are caught by an earlier assertion than the new one, so
their diagnostic does not name the column, and one of those assertions carries no message at all. The rank
comparison runs before the census comparison and the bare assertion gains a message.

**A4 accepted, and it is the substantive one.** `config/mm39.env` pins the snapshot path and digest while the
provenance file that now anchors `fetch_finished` carries no pin, so an edited provenance JSON flows through
the fetch stage into `identity.build_sources` with nothing refusing it at build time. Its digest is pinned
beside the snapshot's. This is the right place for the guarantee: a pin at the input refuses the edit before
it can become an identity, which is stronger than a verifier branch that can only judge an archive against
itself.

**A5 accepted.** The pinned provenance JSON came from the ad-hoc fetch script and carries `census_sha256`,
while the packaged `fetch_dfam_snapshot.py` writes `taxonomy_sha256` and `universe`, so a refresh yields a
different key set. The four keys the verifier reads are in both, so nothing breaks today. The packaged
script's key set is reconciled and the keys the verifier reads are named, without touching the pinned bytes,
whose digest A4 now pins.

**On the reviewer's own account of its copy method**, recorded because it corrects the orchestrator: its
isolation held, and it held because every write went through `unlink` then `write_bytes`, which breaks a
hardlink rather than writing through it. The three files it touched left the archive's inodes intact at mode
0444 with their published digests. The stricter rule stays in the templates because one `open("w")` would
have reached a published archive, and a rule that removes that distinction is cheaper than getting it right
under time pressure.

**The second fix** is `prompts/p9a_fix2.md`, five items, and none of them moves `BUILD_ID`: A1, A2, A3 and A5
touch documentation, checks and a package script outside the payload, and A4 adds a build-time gate rather
than an identity field. The unit confirms the ids are unchanged rather than rebuilding.

## The orchestrator's clean suite run after the fix

Run alone, with `TE_TRACKS_CONSUMER_FIXTURES` pointed into the orchestrator's own scratch and the output
captured whole to a file rather than through `tail`:

```
checks=26 pass=26 fail=0 unsupported=0
runner_exit=0
```

Three independent runs of the fixed tree therefore pass at 26 of 26 with the runner exiting 0: the
implementer's, the reviewer's and this one. The earlier single failure in a concurrent run is transient and
unattributable, as recorded above.
