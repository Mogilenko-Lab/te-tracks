# Milestone 7 rulings

Reviewed state: branch `redesign-2026-09`, commit `9d16506` ("Phase 7: identity and publication");
build `BUILD_ID` `0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a`, `CATALOG_ID`
`0c0a959dea69e397890b590b640162d5bd45e71a88f6468cadd4b7615022b4a4`. Three read-only reviewers ran in
parallel: codex on the publication seam (`m7_codex.md`), Opus on numbers, checks and the rulings
audit (`m7_opus.md`), divergent on unstated assumptions (`m7_divergent.md`).

## Codex (`m7_codex.md`, verdict PASS WITH ADVISORIES)

Codex reproduced both identities with a stdlib encoder in both roots, drove the roster-evolution
case in both orders and under a later builder (bumped taxonomy constant, extended roster,
published tuple unchanged), followed the `docs/RELEASES.md` transfer procedure literally on a
fixture with the same `BUILD_ID` and raw manifest at the destination, confirmed `CATALOG_ID` holds
under a one-byte `chromAlias` change and moves under a one-byte `rmsk_out` change, ran IRescue's
`makeRmsk`, `index_features` and `parse_maps` over the published GENCODE subfamily BED with all
1,220 names preserved and resolved through the registration to catalog records, and ran preflight
on one export per namespace from the published archive. No blocking finding. Rulings:

- **A1 accepted as phase 8 scope.** Family-aware identity and dependency verification (both
  parent ids as digests, exact parent archive resolution, parent family and assembly and recomputed
  ids checked against the child pins, dependency availability before install, select and
  verify-current) is the child seam's work; the core verification branch stays as published. The
  phase 8 consult prompt asks this under its architecture question, and the finding is handed to
  the consult as input.
- **A2 accepted as phase 8 scope, with one design input recorded now:** family and assembly stay
  separate identities, so `SPECIES` admits assemblies and the family carries its own name; the
  child gets its own direct `.staging/<unique>` and an inventoried, parent-pinned
  `tables/contig_aliases.tsv` or an explicitly designed pinned lookup, since preflight walks
  enclosing directories and cannot see a sibling parent's aliases. `src/lib/contigs.py` assumes
  the core UCSC roster and catalog inputs and needs the parameter the consult rules on.
- **A3 accepted; fixed in plan 19 now.** The runbook's literal `99_verify.py .../current` refuses
  the selector symlink; the plan states `release.py verify-current`, or resolving `current` once
  and verifying that archive path, as `docs/RELEASES.md` specifies for consumers.

## Divergent (`m7_divergent.md`)

Every measured claim the orchestrator re-checked reproduces: the four single-valued verifier gates
(`manifest.py:204,213-215,375,410`), the parquet footer `created_by: parquet-cpp-arrow version 25.0.0`
inside a `CATALOG_ID` table, the absence of any `*subfamily*.saf` under the refcache against a packaged
`GRCm39_Ensembl_rmsk_TE.gtf.gz` of exactly 3,799,629 records, `export_contracts` at 15,271 of 25,019
canonical identity bytes with `consumer_keys` at 1,782, `tests/run.sh acceptance` exiting 0 with zero
checks, and the preflight handler at line 102. Rulings:

- **H1 accepted in part; the milestone fix converts two gates.** `SPECIES` admission compares the
  declared `name` and `taxon_id` to the admitted entry and ignores further keys on either side, so an
  accession added later leaves earlier archives verifiable; export contract fields are a required
  set that a declared contract may extend (`keys <= set(contract)`), so a later field leaves earlier
  archives verifiable. `SCHEMA_VERSION` stays single-valued by design: a new manifest schema adds a
  verifier branch. `FEATURE_LEVELS` only grows; renaming a level is a contract break by design and
  stays refused. The record here states both.
- **H2 accepted.** Identity binds what a consumer's bytes and semantics depend on; a reader label is
  documentation. The manifest's export contracts drop `consumer_keys`; the code table
  `EXPORT_CONTRACTS` keeps it for the consumer checks and OUTPUTS.md's route table keeps the prose.
  Check 70 asserts the manifest contracts carry the ten identity fields and no `consumer_keys`.
  The answer to "which identity fields may a later release correct without a new archive" is none,
  which is why documentation leaves the identity. `BUILD_ID` changes once more before the host
  publication.
- **H3 accepted as a contract amendment (owner may overturn with the other `CATALOG_ID` rulings).**
  `catalog.tables` binds content, so its digests are taken over the decompressed bytes of
  `rmsk_records.tsv.gz` and `rmsk_instance_members.tsv.gz` and the plain bytes of `rmsk_taxonomy.tsv`;
  `rmsk_records.parquet` leaves the catalog and stays in the inventory (`BUILD_ID`). The canonical
  text tables are written by the package's own writer, so a pyarrow or zlib change leaves
  `CATALOG_ID` in place while `BUILD_ID` records the serialization. `catalog_from_payload` and the
  verifier decompress to hash (about 310 MB of text); check 70 gains a mutation on a parquet digest
  (`BUILD_ID` alone) and the docs state the rule.
- **H4 accepted; plan 19 corrected now.** The compat oracle is the packaged
  `GRCm39_Ensembl_rmsk_TE.gtf.gz` (md5 `1d6770be131fc1b47402a633f4401cbd`, 3,799,629 data lines,
  the 1:1 coordinate join in `docs/PROVENANCE.md`); the "legacy `te_subfamily.saf`" wording leaves
  the plan and the milestone 2 H1 record is read as that GTF.
- **H5 accepted; checked against the consult.** The six core-only places (`SPECIES` admission by
  `GENOME`, catalog tables required in the child inventory, the fixed source-role set, null parent
  ids, the `full` variant in expected paths, the config keys) and `build.sh`'s stage glob without
  family selection are the child's identity refactor. The phase 8 consult (`consults/gene_child_consult.md`)
  was read against this list: its Q2 addresses all six places and the stage glob (family dispatch
  with `GENOME=mm39` and `FAMILY=te_mm39_gene`, the GTF as a child source role outside
  `catalog.sources`, non-null parent pins with the parent's catalog inherited, an explicit variant in
  the exporter and registration, child config keys, and child stages consuming the verified parent
  without rerunning core stages), so no addendum is needed; the phase 8 implementation prompt names
  all of them.
- **M1 deferred to the phase 9 runbook:** after host publication the family root and `archive/`
  are tightened to owner-only write (0755 and 2755) or the group write is stated as the cooperative
  publisher policy; retention becomes a stated policy with the host's backup named.
- **M2 accepted in two parts.** Authoring gains a core payload roster: the non-export inventory paths
  must equal the expected `source/` and `tables/` set, so a stray file fails the build instead of
  entering `BUILD_ID`. The clean-revision gate is the phase 9 runbook's: host publication requires
  `builder_git_dirty` false, and publication proceeds only from a fresh complete `--root` build,
  never from a resumed staging; `docs/RELEASES.md` states the second sentence now.
- **M3 accepted.** The raw `MANIFEST.json` SHA-256 is a transfer-integrity check; consumer pins are
  `BUILD_ID`, `CATALOG_ID` and file digests. `docs/RELEASES.md` consumer pins are restated.
- **M4 accepted as a consumer gate for the phase 9 handoff:** the 14761 ledger adopts
  `te_catalog_id` and `te_build_id` in place of a single `te_release`; recorded for the owner, whose
  repository it is.
- **M5 accepted into plan 19:** if the host build's ids differ from the in-container build's, the
  runbook compares the recorded toolchain versions; with H3 in place a `CATALOG_ID` difference means
  the catalog content differs and stops, while a `BUILD_ID` difference with equal `CATALOG_ID` is a
  serialization difference and the host build publishes as the release with the in-container build
  recorded as its content witness.
- **L1 accepted.** Preflight resolves the alias table from the build root that contains
  `MANIFEST.json` above the export path and refuses an export with no such root; the walk stops
  there. Check 62 covers the refusal.
- **L2 accepted:** the preflight handler adds `TypeError`; check 62 adds a short alias row.
- **L3 accepted:** a mode with no registered checks exits 2; check 01 asserts it.
- **L4 accepted:** predicate keys are published per schema (`{1: {"class_in", "family_prefix_excluded"}}`).
- **L5 process, as at milestones 2 and 5;** the prompts are committed with the milestone.

## Opus (`m7_opus.md`, verdict PASS WITH ADVISORIES)

Opus reproduced every published number of phases 6 and 7 by an independent route (both ids in both
roots, 86/86 digests and sizes, the five retention figures, the alias table and its GENCODE rule, the
registration digests and row counts, the preflight legs), failed each of checks 60, 61, 62, 70, 71, 72
and consumer check 10 with one mutation, audited every accepted ruling of phases 6 and 7 to a file,
line and observed behaviour, and re-manifested the payload with the committed tree to the same
identity. Rulings:

- **A1 accepted (milestone fix):** README's core-suite sentence names contigs (60 to 62) and
  identity and publication (70 to 72).
- **A2 accepted.** The phase 7 codex A4 ruling listed check 14 and omitted 11; the assertions sit in
  10, 11, 12, 13 and 16, which is the intended set, and this record corrects the list. The declared
  `featureCounts` key on both SAF files gains its assertion in check 16 beside the SAF column
  reader, since check 21 stays unsupported here.
- **A3 accepted as an observation with a phase 9 rule.** Both scratch manifests record the phase 6
  commit with `builder_git_dirty` true because the payload was built before the phase 7 commit; the
  committed builder reproduces the identity exactly. Host publication requires a clean committed
  tree (divergent M2, plan 19). After the milestone fix is committed, the orchestrator republishes
  the scratch root from the clean tree so the scratch archive itself records a clean revision.
- **A4 accepted; plan 17 marks the figures.** The three superseded manifests' peak values and the
  stage 35 figure are historical measurements with no surviving carrier; plan 17 says so beside them,
  and public prose carries only the range and the per-build provenance field.

## Fix loop and orchestrator verification

Unit `te-tracks-m7-fix` (`prompts/m7_fix.md`) implemented the twelve items, re-manifested the build and
republished the scratch root; its report named two deviations, both accepted: the decompressed canonical
text tables measure 1,078,253,278 bytes (the prompt's "about 310 MB" was the compressed size), and the
verifier's streamed digests add about 6 s to a full verification (29.6 s against 23.3 s). Two checks then
failed because the new payload-roster gate refused the publication fixture, which wrote a `policy.txt`
payload and no `source/qualification.md`; the gate is right and the fixture conformed in unit
`te-tracks-m7-fix2` (`prompts/m7_fix2.md`): the note now lives in `source/qualification.md`, the
added-payload case left check 72 since a stray payload fails authoring and check 71 covers it, and the
archive counts read 1, 2, 4 and 5.

Orchestrator verification (`_scratch/te-tracks-audit/p7_verify/verify_c.log`):

- New identities: `BUILD_ID` `9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d`,
  `CATALOG_ID` `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e`; both recompute with
  an independent encoder in the build directory and in `pubroot/te_mm39/current`; identity sections equal;
  the 43 payload digests unchanged from the reviewed build (`exports.tsv` digest column equal across roots).
- Identity layout: contracts carry the ten identity fields and no `consumer_keys`; `catalog.tables` holds
  `rmsk_records.tsv`, `rmsk_instance_members.tsv`, `rmsk_taxonomy.tsv` and the digests reproduce from the
  decompressed bytes (862,169,033 / 215,225,351 / 858,894); the parquet is out of the catalog; `species`
  carries `name` and `taxon_id`.
- Verifier independence: a scratch builder with taxonomy rule v2, an extended roster and a `SPECIES`
  entry extended with `assembly_accession` verifies the archive and `verify-current` exits 0.
- Installed archive: 0 files off 0444, 0 directories off 0555, `archive/` 2775, one archive, relative
  `current`, empty `.staging`; `verify-current` exit 0; the verifier leaves the build unchanged.
- Runner: `tests/run.sh acceptance` exits 2 with zero checks. Preflight: an export under a tree without
  `MANIFEST.json` is refused with the named message; a marked tree resolves and exits 0.
- Public files carry no superseded figure or phrase; `docs/DECISIONS.md` entry 7 has four sentences.
- `tests/run.sh core` 19 pass in 12 min 38 s; `tests/run.sh consumers` 8 pass, 5 unsupported, exit 0.
- Git: HEAD `9d16506` before the commit, no git writes by any unit; the fourteen checkouts under `.ref`
  (now including `TEsingle_benchmarking_scripts`, `TEsingle_Martirosyan_analysis_code` and `Thesis_2023`)
  are clean; `14839-DM-cGAS` and `sene/` are plain directories.
- Leftovers: `pubtest` and publication `.staging` empty; unit scratch removed.

After this commit the orchestrator resets the scratch root and republishes from the clean tree so the
scratch archive records a clean builder revision (Opus A3), then bumps the umbrella pin.

Committed as "Milestone 7: identity hardening after the publication review".
