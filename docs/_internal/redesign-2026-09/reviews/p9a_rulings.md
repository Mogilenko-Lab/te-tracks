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

Investigated rather than retried. The build directory and the current core archive both verify clean at exit
0 afterwards, and every publication check isolates its own work in a `TemporaryDirectory` under
`$TE_TRACKS_REFROOT/pubtest`, so neither the artifact nor the checks' shared scratch explains it. The
remaining explanation is the reviewer's method: the earlier Opus pass reported mutating "a hardlinked copy"
of the build, and a hardlink shares its inode, so a write to the copy writes through to the real build for
as long as the mutation is live. A concurrent reader sees a corrupted payload and one check fails, and the
build verifies clean again once the mutation is reverted.

Three consequences, recorded so the remaining reviews do not repeat it.

- A read-only contract is not violated by this, and the reviewer did nothing outside its instructions; the
  hazard is that "copy then mutate" is only safe when the copy is real. Reviewer prompts from here on require
  a real copy and forbid `cp -al`, `cp -l` and `shutil.copytree` with a linking copy function, and ask the
  reviewer to verify the build and every archive as its last step.
- The orchestrator does not run a verification suite concurrently with a mutation-testing reviewer against
  the same reference root. Either the suite waits, or the reviewer is given its own `TE_TRACKS_REFROOT`.
- Capturing a suite run through `tail` discards the failing check's identity and the runner's exit status.
  Suite output is captured whole.

The clean re-run after the reviewer finishes is the record of the fix's suite result.
