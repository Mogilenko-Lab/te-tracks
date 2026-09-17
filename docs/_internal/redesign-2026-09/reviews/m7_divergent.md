# Milestone 7 review: unstated assumptions (divergent)

Read at `9d16506`: plan `00_INDEX.md` and `16_` to `19_`; `reviews/{m2_divergent,m5_divergent,m5_rulings,p6_rulings,p7_rulings}.md`;
`consults/{owner_context_2026-09-15,ADR67_consult,ADR38_consult,gene_context_material}.md`; `README.md`, `docs/{DECISIONS,OUTPUTS,RELEASES,PROVENANCE}.md`;
`14761-DM/AGENTS.md` and its D2/D3 plan; `build.sh`, `src/release.py`, `src/lib/{manifest,build_exports,records_io,build_records}.py`,
`bin/te-tracks-preflight`, `tests/run.sh`. Measurements are read-only passes over the build, `pubroot`,
`/data2/users/shared/refcache` and `/proc/mounts`; verifier mutations ran from copies of `src/` in a scratchpad outside
every repo. Plan `19_` moved in the working tree; citations are to `9d16506`.

## High

- [H1] **The verifier judges an archive against its own declaration, so earlier archives stay verifiable
  (`DECISIONS.md:74-75`).** Failure: four builder constants still gate a published archive, each the defect codex B1
  named. Measured against the published archive (baseline exit 0): `SCHEMA_VERSION = "te-tracks-manifest-2"` →
  `MANIFEST.json: unsupported schema_version`; the mm39 `SPECIES` entry extended with `assembly_accession` →
  `identity family or species differs`; `FEATURE_LEVELS` renaming `taxonomy_triple` → `unsupported export
  selectable_levels: exports/ensembl/interspersed/full/record.gtf`; one field added to `verify_export_contracts`'s
  `keys` → `export contract fields differ`. Adding a genome or a level passes. `taxonomy_rule_version` and the predicate
  schema became growing tuples (`manifest.py:27-28`) while `SCHEMA_VERSION` (`:26,375`), `SPECIES` (`:37,410`),
  `FEATURE_LEVELS` (`build_exports.py:32`, read `manifest.py:213,215`) and `keys` (`:198-204`) stayed single-valued, and
  the fix's independence probe varied exactly the two that were converted (`p7_rulings.md`, "Verifier independence").
  The SPECIES edit is already asked for: `identity.assembly` is `{"ucsc":"mm39","name":"GRCm39"}`, 31 canonical bytes
  with no accession, and `ADR67_consult.md:33` requires "assembly accession/version". Cost high: `verify-current`,
  `select` and `install --select` all fail. Phase 8 or 9.
- [H2] **`export_contracts` describes files, so hashing it is hashing the payload.** Failure: editing a reader label
  mints a second 10.46 GB archive for byte-identical data. Measured on the published manifest: `export_contracts` is
  15,271 of 25,019 canonical identity bytes (61.0%), the inventory 6,063 (24.2%), and the field carries tool names and
  key grammars for six executables that have never run here (`README.md:70`). It happened once: p7 ruling A4 removed
  `14761 ATAC` from one `consumer_keys` entry and records the consequence, "This changes `export_contracts` and
  therefore `BUILD_ID`"; the id moved `d9e6c18c…` → `0e053139…` with "the 43 payload files byte-identical to the
  reviewed build", and retention keeps both at 10,461,884,289 bytes each (`RELEASES.md:156`). Check 70 asserts
  `len(export_contracts) == 24` and mutates the field in neither direction. Phase 9: state which identity fields a later
  release may correct without a new archive.
- [H3] **`CATALOG_ID` protects ledger continuity across rebuilds.** Failure: it binds serialization bytes, so a library
  upgrade re-keys a catalog that did not move. Three of its four table digests are compressed streams —
  `rmsk_records.parquet` 378,232,086 B (snappy, `build_records.py:122`), `rmsk_records.tsv.gz` 246,337,861 and
  `rmsk_instance_members.tsv.gz` 63,215,760 (`gzip.GzipFile(mtime=0, compresslevel=6)`, `records_io.py:37`) — and the
  parquet footer carries its writer verbatim: `created_by: parquet-cpp-arrow version 25.0.0`, measured. A pyarrow bump
  changes `CATALOG_ID` for identical records, so the ledger key `(te_catalog_id, rmsk_record_id)` (`DECISIONS.md:70`)
  changes value for 5,320,771 records, and id equality is the only published test for "same catalog". The defence is
  prose: `RELEASES.md:36-37` has host publication "compare against the recorded Python, pandas, pyarrow and zlib
  versions", and no check executes it. Cost high; this is the churn `CATALOG_ID` exists to prevent. Phase 9, or a
  deferral naming the comparison as manual.
- [H4] **Phase 9 reconciles the compat universe against the published legacy `te_subfamily.saf` (plan `19_:22-23`).**
  Failure: that file exists nowhere. `/data2/users/shared/refcache/mm39/mm39_20260911/` holds four entries — the GENCODE
  GTF, the genome FASTA, `GRCm39_Ensembl_rmsk_TE.gtf.gz`, `MANIFEST.json` — and a search of the refcache and the audit
  scratch finds no `*subfamily*.saf`. The nearest candidates are the two disqualified audit experiments, whose
  `te_dim.tsv` `n_loci` sum to 3,800,864 and 3,762,401 against the compat membership 3,799,629
  (`universe_summary.tsv`), so an orchestrator hunting the named artifact reproduces the false 1,235-record discrepancy
  `m5_rulings.md` rejected on its premise. The oracle that works is on the host and already reconciled:
  `GRCm39_Ensembl_rmsk_TE.gtf.gz` (md5 `1d6770be…`) carries exactly 3,799,629 data lines, measured in-container in
  1.8 s, and `PROVENANCE.md:31-37` records the 1:1 coordinate join. Cost high: the release's one external oracle.
  Phase 9: name the packaged GTF.
- [H5] **The gene child is "built by the same `build.sh`" (plan `18_:16`) and its manifest pins the parent.** Failure:
  the identity layer is core-only in six places and the phase 8 consult agenda names none of them. `manifest.py:258`
  requires `mm39_gene` in `SPECIES`; `:158` requires the four parent canonical tables inside the child's own inventory;
  `:139` requires `SOURCES.json` to declare exactly `rmsk_out`, `rmsk_table`, `chromAlias`, `chrom_sizes`, with no role
  for a gene GTF; `:411` requires a null `parent_build_id`; `:170` hardcodes `full` in the expected export path, so
  `exon_subtracted` is inexpressible; `:240-247` demands `GENOME_FA_*` and all four source URL/MD5 pairs from a child
  config that plan `18_:14` gives as `PARENT_FAMILY`, `GENE_GTF_URL`, `GENE_GTF_MD5`, `EXON_MASK_POLICY`. And
  `build.sh:68` globs every `src/[0-9][0-9]_*.sh` with no family selection, so one driver re-runs fetch, records and all
  24 parent exports into the child staging. p7 ruling codex A3 defers "family-specific identity, parent validation" in
  one sentence; the seven consult questions (plan `18_:5-11`, `gene_context_material.md:237-272`) are about gene-context
  topology. Cost high: the next phase meets an identity refactor after the publication seam closed. Phase 8, into the
  consult agenda before the implementation prompt.

## Medium

- [M1] **`umask 002` and mode 2775 protect published bytes.** Failure: any member of the shared group unmakes a release
  outside the lock. Measured: the refcache root is `0755 devuser:devgroup` (uid 788715489, this container's own uid, so
  the owner alone creates the family), the existing `mm39/` family 2775, and `release.py:37-43` creates the new family
  0775 and `archive/` 2775. Payload modes hold (0 exceptions off 0444/0555 in `pubroot`); both writable entries sit
  above them, so `mv archive/<id> /tmp` or `ln -sfn` on `current` needs group write alone, takes no `flock`, and leaves
  the selector dangling or naming an unverified tree. `verify-current` reports the fault; the bytes and the consumer pin
  are gone, and retention (`RELEASES.md:156`) is a sentence with no mechanism and no second copy. Phase 9 runbook.
- [M2] **The complete file inventory binds the payload.** Failure: it is derived from disk, so an unintended file is
  declared rather than caught. `manifest.py:90-123` hashes what it walks and only `exports/` carries a roster
  (`:181,226`), so an extra `tables/*.tmp` enters the inventory, enters `BUILD_ID` and verifies forever. The producing
  revision cannot arbitrate: the published archive records `builder_git_sha 99bf646…` with `builder_git_dirty: true`,
  and `ADR67_consult.md:52` ("a recoverable clean producing revision for publication") was adopted with the two-section
  manifest minus that clause. Concretely: an interrupted build leaves staging for inspection (`RELEASES.md:141`), the
  owner re-runs a stage into it, and the partial file publishes under a dirty SHA. Phase 9: fresh staging per attempt
  plus a clean-revision gate or an explicit deferral.
- [M3] **The raw `MANIFEST.json` SHA-256 is a consumer pin (`RELEASES.md:151`).** Failure: it is a property of one copy.
  Measured today, one `BUILD_ID` and one `CATALOG_ID` over two manifests: `13ef2bfc…` in `pubroot/te_mm39/current`,
  `bde6cb31…` in `te_mm39/build`. A consumer pinning the sha it was handed, then re-resolving through a root where the
  build converged onto a first manifest (`RELEASES.md:87-88,134`), fails an integrity check on an identical release.
  Phase 9: scope that sha to transfer, where `:130-136` already uses it.
- [M4] **The two-id pin contract reaches the consuming ledger.** Failure: the consumer has not adopted it. Grep over
  `14761-DM/AGENTS.md` (252 lines) returns no `te-tracks`, `RepeatMasker`, `TE`, `catalog` or `te_release` hit, and D2
  keeps one release column: `te` and `te_locus_dim` are PK `(te_release, locus_id)`
  (`.../2026-09-11_codebase-topology/01_consult_codex.md:165-166`), with `te_catalog_id` and `te_build_id` absent from
  the repo. So `te_release` binds the published `BUILD_ID` and H2's label edit re-keys `te_locus_dim` plus every
  `peak_te_overlaps` row. `m5_rulings.md` M1 landed as a te-tracks documentation change. Phase 9 handoff: name the
  column change as a consumer gate.
- [M5] **"The host build runs inside the same image" (`m2_rulings.md`, Phase 7 H6) makes the two builds comparable.**
  Failure: the claim is unverifiable and sits against the package's own execution note, which puts the build on the host
  because the refcache is read-only inside the container (`AGENTS.md`). `image_identity()` (`manifest.py:285-294`)
  records `/etc/os-release` and one line, `serial: 20260627`, and reports "container image digest unavailable"; the
  substitute is four version strings compared by prose (`RELEASES.md:36-38`). Failure path: the host pyarrow differs by
  a patch, the parquet footer differs (H3), both ids diverge, and phase 9's gate — published digests, `CATALOG_ID` and
  `BUILD_ID` equal to the `_scratch` build (`m2_rulings.md`, Phase 9 H6) — fails with no recorded branch. Phase 9:
  state the remedy for an id mismatch.

## Low

- [L1] **Preflight's alias table belongs to the export's build.** Failure: it belongs to whatever encloses the path.
  Demonstrated: three BED rows copied from the published archive into a scratch tree carrying its own
  `tables/contig_aliases.tsv` were judged against that table, exiting 1 on a fabricated 1,000 bp `chr1` disagreement
  with the `alias_table` line as the only trace. The walk-up is unbounded (`bin/te-tracks-preflight:44-45`) and
  published (`OUTPUTS.md:561-563`); an export carries no build identity to bind it. Phase 8 or 9.
- [L2] **Preflight reports every input fault as its named one-line error.** Failure: `TypeError` escapes. A short row in
  the alias table makes `csv.DictReader` yield `None` and `int(row["length_bp"])` raise a traceback, since the handler
  at `:102` catches `(ValueError, KeyError, OSError, ImportError)` where `release.py:176` and `99_verify.py:19` include
  `TypeError`. Exit stays 1. Phase 9.
- [L3] **`tests/run.sh acceptance` is the phase 9 gate.** Failure: `tests/checks/acceptance/` is empty, so the run
  prints `checks=0 pass=0 fail=0 unsupported=0` and `no checks registered for mode acceptance` and exits 0, measured;
  `README.md:37` publishes the invocation, and a script reads the exit code. Phase 9.
- [L4] **`universes.schema_version` owns predicate grammar (rulings A2, A3).** Failure: the version constrains nothing
  about the keys. `PUBLISHED_PREDICATE_SCHEMAS` grows while the key whitelist at `manifest.py:424` is one global set, so
  widening it for a schema-2 key also legalizes that key inside a schema-1 archive. Phase 8 or 9.
- [L5] **Prompt files are the record (`02_orchestration.md:48`).** Raised at m2 (L3) and m5 (L5), ruled process both
  times; at `9d16506` the three `m7_*` prompts and `p8_consult.md` are modified in the working tree, so the brief
  governing this review is untracked while the review lands committed. Orchestration.

## Defended already

- Relative `current` across machines: measured relative (`archive/<id>`), the host `mm39/current` likewise, the refcache at one absolute path inside and out — `RELEASES.md:23-24`, `release.py:74-77`.
- `flock`, rename atomicity and one-filesystem staging: both roots are local ext4 (`/dev/sda1`, `/dev/sdb1` in `/proc/mounts`) under one kernel, and `install` enforces `st_dev` equality — `release.py:140-141`.
- Consumer traversal and ACLs: payload 0444/0555 and world-readable, 0 exceptions measured; the scratch's default ACLs are clamped by the mask `chmod` sets, and the host refcache carries none (`drwxr-xr-x`, no `+`).
- Readers holding an archive across a selector swap: every archive stays resolvable and consumers resolve once — `RELEASES.md:150-154`.
- `CATALOG_ID` narrowed to `rmsk_out`: a `chromAlias` or `chrom.sizes` refresh cannot silently move records, since `rmsk_record_id` embeds `chrom:start-end` and bounds verify against the build's own sizes file (`manifest.py:332-351`) — `p7_rulings.md` Opus A2.
- The child pinning `parent_build_id` in a root whose `current` moves: the pin is an immutable id resolved at `archive/<id>`, and parents transfer and verify before a child is selected — `ADR67_consult.md:95`, `RELEASES.md:137`.
- Verifier purity on a read-only snapshot, bytes and mtimes unchanged — `RELEASES.md:100-103`, `p7_rulings.md`.
- The gene-context ADR the owner has yet to hold: `gene_context` waits for it and D2 populates nothing from the status table — `m2_rulings.md` Phase 8 H3, plan `18_:39-42`; mask alternatives measured at `gene_context_material.md:212-236`, the consumer-GTF mismatch carried as open question 7 at `:265-272`.
- The host floor: 6.0 GB resident and about 10.46 GB per build against 1.13 TB free on `/dev/sdb1`, measured — `RELEASES.md:161-166`.
- Reviewers reading the orchestrator's build and expectations descending from it — `m5_rulings.md` L4, plan `19_:28-32`.
- `99_verify.py` refusing the `current` symlink: corrected in the working tree to `release.py verify-current` (milestone 7 codex A3).

Predicted first bite: H5 — phase 8 opens next, and the manifest module cannot describe a child build in six independent
places while the consult agenda asks about exon masks.
