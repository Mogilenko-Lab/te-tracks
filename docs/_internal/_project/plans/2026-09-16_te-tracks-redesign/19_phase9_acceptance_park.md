# Phase 9: acceptance and parking

## Phase 9a: core additions before acceptance (ruled 2026-09-17, `redesign-2026-09/consults/adr_rulings_2026-09-17.md`)

One implementer unit lands the core additions the ADR discussion ruled, so the single host build carries them and
no second core baseline is retained soon after. Every item changes `BUILD_ID` and keeps `CATALOG_ID`.

- **`record_starsolo.gtf`** (C8; DECISIONS 13): `exports/<ns>/interspersed/full/record_starsolo.gtf`, one exon per
  record, `gene_id` = `transcript_id` = `locus` = record alias, `gene_name` = `rmsk_name`, `gene_type
  "transposable_element"`, the provenance attributes kept; contract with `feature_identity = gene_id` and consumer
  keys STARsolo and cellranger; registration reuses `(record, record_alias)`; roster 24 to 27, payload files 43 to
  46, about 1.616 GB per namespace (`consults/loci_gtf_consult.md` Q5); fixture of five cases (two same-name records
  as two genes; gene–TE overlap allocation; gap-only read; collision preflight against a gene GTF; namespaces and
  one-base endpoints); STAR and cellranger execution gates run when the binaries are on PATH
  (`/workspaces/Meta-Aging/01_modules/te-consumers/env/activate.sh`) and report `unsupported` otherwise.
- **Dfam lineage, rank and clade view** (C10; DECISIONS 15 amended from "a later core view" to this phase): source
  role `dfam_snapshot`, the offline metadata snapshot fetched 2026-09-17 (`redesign-2026-09/taxonomy/
  dfam_interspersed_mm39_snapshot.json.gz` with its provenance), moved into the package as a tracked pinned source
  with a fetch script that documents its production; `tables/taxonomy_dfam.tsv`, one row per `interspersed` name:
  RepeatMasker tokens and canonical labels; `match_status` (`exact`, `part_model_set`, `missing`, `ambiguous`);
  Dfam accessions, names, model versions and lengths (set-valued, `;`-joined) and their sum; the classification
  path and its leaf node; the clade and its lineage; the release; `wicker_code` and the ranks `wicker_class`,
  `wicker_subclass`, `wicker_order`, `wicker_superfamily`, `wicker_family` (the Dfam leaf node) and `subfamily`
  (the name) each with a status `mapped`, `inherited`, `missing`, `inapplicable` or `part_model_set`; the node's
  RepeatMasker type and subtype equivalents. L1 whole-element names map to the set of their `_5end`, `_orf2` and
  `_3end` part models. Acceptance from the census: 1,047 exact, 143 part sets, 30 other misses of which 53 rows in
  total lack a Wicker code, all `Unknown`; a documentation section defines every rank in Wicker's terms with the
  dissertation's five names as an alias table and the label surprises (B1 under `Alu`, `ERVL-MaLR`, hyphenated DNA
  superfamilies, class-less records).
- **Matrix binding** (C9; DECISIONS 14): the OUTPUTS sentence reads `(universe_name, variant, feature_level,
  key_grammar)`; a join fixture over `interspersed` and `all_rmsk` proves that a join on the pair alone doubles.
- **Records, instances and insertions** (DECISIONS 10): an OUTPUTS section stating what a record, an instance and an
  insertion are, that per-locus counts are per record, and the limits of the annotation, with the measured
  numbers (445,649 multi-record instances; 30,569 mixed-name; 23,244 mixed-strand; 8.07% of records overlapping
  another; 722,280 LTR-only instances; 588 L1 records at model base 1); `rmsk_overlap_flag` documented as constant
  false for the mm39 source.
- **IRescue execution check** (DECISIONS 12): `tests/lib/consumers.py` asserts identity joins, roster and molecule
  conservation and unique molecules on their feature, and records the observed allocation (5.5 and 3.5 for the
  4/2/3 fixture) without asserting it.
- **Consumer environment** promoted: the bootstrap and lock from `01_modules/te-consumers/env/` referenced from
  `tests/README` or the runner documentation; `tests/run.sh consumers` documents `activate.sh`.
- **Publication cases**: a failed-build cleanup case (staging left by an interrupted build is removable and never
  installable).
- **Parking handoff**: the RNA qualification limits (TEsingle mates, UMI graph and hard ties; Stellarscope boundary
  and preselection; IRescue's even-start EM), and the host retention budget at about 15.3 GB per build.

Phase 9b is the acceptance, runbook and parking content below, run after 9a with the core and the child rebuilt in
scratch; the milestone review follows 9b.


Deliverables
- `tests/run.sh acceptance` against a full in-container build into `_scratch`: every number in
  phases 1 to 8 re-measured and compared to `tests/expectations/mm39/<universe>/`; fixture tables
  independently authored, never copied from the build under test.
- Host runbook `docs/RUNBOOK.md`: prerequisites and versions, writable host root versus the
  read-only container mount, source cache, `build.sh` invocation for `te_mm39` then
  `te_mm39_gene`, verification, publication, transfer to the CRI root, interruption recovery,
  resolving `current` once per consumer operation.
- Owner runs the host build; the orchestrator verifies the published bytes in-container
  (`release.py verify-current --root /data2/users/shared/refcache --family te_mm39`, which resolves `current`
  once and verifies that archive; `99_verify.py` takes the resolved `archive/<BUILD_ID>` path and refuses the
  selector symlink itself, milestone 7 codex A3) and records the
  `BUILD_ID`s in `docs/_internal/_project/session.md`.
- README truth table updated to delivered and tested; `AGENTS.md` final; `docs/OUTPUTS.md`,
  `docs/PROVENANCE.md`, `docs/RELEASES.md` accurate to the bytes.
- Parking handoff in `docs/_internal/_project/session.md`: what is published, what is tested, what
  is unsupported (tool executables), what is deferred (hg38, transcript context, ERV units, age
  tiers), and the next gates.

Milestone 2 rulings landing here: the `compat_tetranscripts_mm39` membership count equals the 3,799,629 data
lines of the packaged `GRCm39_Ensembl_rmsk_TE.gtf.gz` (md5 `1d6770be131fc1b47402a633f4401cbd`) in the refcache, the
oracle `docs/PROVENANCE.md` joins 1:1 on coordinates (H1; milestone 7 divergent H4 found no legacy SAF on disk); published table digests, `CATALOG_ID` and `BUILD_ID`
equal the in-container `_scratch` build (H6); the runbook seeds the host `TE_TRACKS_SOURCE_CACHE` from
the container's retained source copy, and a checksum mismatch stops for a re-pin decision (L4).

Milestone 5 rulings landing here: the runbook states a measured floor per consumer, projected from a 50,000-row
head of `record.gtf` through Stellarscope's `IntervalTreeAnnotation` and TElocal's `TEindex`, beside the producer's
floor near 6.0 GB resident, measured 5.5 to 6.0 GB across builds (H3); the runbook pins consumer installs to the vendored checkout commits or records the divergence (M4); the
handoff names the barcode-threshold audit as the consumer's (M6); the acceptance record names the oracles the builder
did not produce: the UCSC `rmsk` table (phase 1 qualification), the pinned Dfam snapshot (check 31) and the host
legacy release for the compat count (L4, with H1 corrected: the in-container legacy directories were audit
experiments, moved to `_scratch/te-tracks-audit/legacy_release_experiments/`).

Final review: codex and Opus on the whole release plus a `divergent` pass on the handoff.
Then the umbrella pin bumps and D2 and D3 resume.

Milestone 7 rulings landing here (`reviews/m7_rulings.md`): the runbook verifies the published root with
`release.py verify-current` (codex A3); after host publication the family root and `archive/` are tightened to
owner-only write or the group write is stated as the publisher policy, with the host backup named (divergent M1);
host publication requires `builder_git_dirty` false and a fresh complete `--root` build (M2); when the host build's
ids differ from the in-container build's, a `CATALOG_ID` difference stops for investigation and a `BUILD_ID`
difference with equal `CATALOG_ID` publishes the host build with the in-container build recorded as its content
witness (M5); the handoff names the 14761 ledger's adoption of `te_catalog_id` and `te_build_id` as a consumer gate
(M4); `tests/checks/acceptance/` gains its checks, and the runner exits 2 for a mode without checks (L3).
