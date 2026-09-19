# Claim validation: narrative (codex gpt-6-astra)

Verdict: FALSE CLAIMS PRESENT

## Tally

Counted complete prose sentences and one factual unit per table/deferral row; README includes 22 table rows. Fenced command examples and eight procedural directives in AGENTS are excluded from the sentence denominator and commands are assessed below. A contradicted clause makes its sentence false; an unavailable required observation makes it unverifiable. Admission requirements are evaluated as recorded conditions, not as claims that a pilot has completed.

| File | Fact-asserting sentences | Verified true | False | Unverifiable |
|---|---:|---:|---:|---:|
| README.md | 69 | 58 | 2 | 9 |
| AGENTS.md | 27 | 25 | 0 | 2 |
| docs/DECISIONS.md | 74 | 60 | 10 | 4 |
| Total | 170 | 143 | 12 | 15 |

## False claims

- [F1] README.md:6 “An annotation change between analyses silently makes their counts incomparable.” — A changed annotation can retain identical counting support: core check 81 removes duplicate GTF rows and requires byte-identical SAFs and registration; the independent copied-GTF probe also preserves the mask. — Corrected: “Annotation changes can alter feature definitions; pinned builds make those definitions explicit.”
- [F2] README.md:105 “The qualified test surface has 26 core passes, 11 fresh-build acceptance passes, 11 acceptance rerun passes, and 15 consumer passes plus one unsupported Stellarscope boundary check; all four commands exit 0.” — The on-disk core roster contains 28 checks. Current run outcomes are recorded below; a fresh build was excluded by this review. — Corrected: “The current surface contains 28 core checks, 11 required acceptance checks and 16 consumer checks; activated consumers report 15 passes and one unsupported Stellarscope boundary check.”
- [F3] docs/DECISIONS.md:39 “Consumers match the snapshot's annotation digest to their counting annotation: the first snapshot pins GENCODE vM37 and the second pins the 10x 2024-A annotation (GENCODE vM33 filtered) used for the current single-cell counts; a mismatch requires documented geometry reconciliation or another snapshot.” — Every retained child manifest pins GENCODE vM37; the 10x child is deferred in README.md:73. — Corrected: “The delivered child pins GENCODE vM37; the 10x 2024-A child awaits its annotation digest and geometry reconciliation.”
- [F4] docs/DECISIONS.md:98 “te-tracks publishes a sparse record-by-transcript geometry relation with per-pair status and a per-record roll-up, carrying exon, intron and UTR overlap, relative strand, and signed closest-base distance to each transcript's start and end, with gene-body distance beside transcript distance so consumers can derive their own labels.” — Every child declares context_capability=not_computed, and no retained inventory or table contains this relation. — Corrected: “The deferred transcript-context relation has the geometry defined here and requires chr1 then whole-mm39 scaling evidence.”
- [F5] docs/DECISIONS.md:102 “Rows cover body overlaps, the nearest start, end and exon edge on the record's contig with ties kept, and records overlapping a window from 10 kb upstream to 2 kb downstream of an annotated transcript start; narrower promoter policies are consumer filters on the stored distance.” — The declared 10 kb/2 kb envelope and nearest-edge rows describe an absent context product. — Corrected: “The proposed relation covers body overlaps, tied nearest edges and a 10 kb upstream to 2 kb downstream transcript-start envelope.”
- [F6] docs/DECISIONS.md:105 “Each transcript carries `Ensembl_canonical` and `mRNA_start_NF` flags so consumers can exclude incomplete starts.” — There is no published per-transcript context table. In the retained GTF, only 78,317 of 278,369 transcript rows carry Ensembl_canonical and 7,247 carry mRNA_start_NF. — Corrected: “The proposed relation records Ensembl_canonical and mRNA_start_NF status for each transcript.”
- [F7] docs/DECISIONS.md:125 “Candidate core snapshots contain geometry computed solely from catalog columns under declared parameters: the block union of an instance's records with gaps preserved, record 5′ windows with model-prefix eligibility, LTR–internal candidate pairs by family, strand and gap with per-pair status, and divergence bins with pinned thresholds.” — The complete retained core inventories contain no instance-union, record-window, LTR–internal-pair or divergence-bin view. — Corrected: “The deferred core candidate views require declared geometry parameters, a host build and a named consumer.”
- [F8] docs/DECISIONS.md:129 “Views carry neutral names, support and candidate status.” — Those candidate views and their status columns are absent. — Corrected: “The proposed candidate-view contract uses neutral names, support and candidate status.”
- [F9] docs/DECISIONS.md:160 “A run's matrix binds to a registration through the full key `(universe_name, variant, feature_level, key_grammar)` because registration holds each record under multiple universes and joining on level and grammar alone doubles counts.” — Doubling is specific to shared record/rmsk_record_id keys; 5,320,771 minus 3,764,949 = 1,555,822 catalog records occur only in all_rmsk. The full registration scan finds record/record_alias only in interspersed: R|mm39|L1MdA_VI|chr1|3050294|3050775|+ has one registration; its rmsk_record_id spelling has two. — Corrected: “Matrices bind through universe, variant, feature level and key grammar; omitting universe duplicates record keys shared by interspersed and all_rmsk.”
- [F10] docs/DECISIONS.md:182 “Each decision states the chosen behaviour and its reason in two to four brief affirmative sentences.” — The 16 numbered sections contain 4,4,3,4,4,3,4,4,6,4,4,5,4,2,6,3 sentences; sections 9 and 15 have six and section 12 has five. — Corrected: “Each decision records its chosen behaviour and supporting rationale.”
- [F11] docs/DECISIONS.md:144 “The consumer environment is delivered by reference to the consuming module in [RUNBOOK.md](RUNBOOK.md#consumer-environment), with source pins, installed versions and execution evidence.” — The linked runbook points to /workspaces/Meta-Aging/01_modules/te-consumers/env/, whose parent module is absent. The recipe and five named records exist under /workspaces/Meta-Aging/01_modules/te-quant/env/. The installed .venv/te-consumers activation path does exist. — Corrected: “The consuming recipe lives at /workspaces/Meta-Aging/01_modules/te-quant/env/; the installed environment activates through /workspaces/Meta-Aging/.venv/te-consumers/activate.sh.”
- [F12] docs/DECISIONS.md:70 “The UCSC browser table is compared once at source qualification and the report is retained.” — Stage 05 compares source fields and stage 10 independently checks one-to-one browser keys and class/family agreement; both comparison paths refuse the copied family-disagreement fixture. — Corrected: “Source qualification compares the browser table and retains its report; canonical-record construction also checks source keys and class/family agreement.”

## Unverifiable claims

- [U1] README.md:3 “Transposable-element annotation is fiddly and goes stale; keeping it current by hand gave each project a different annotation.” — The causal history of hand-maintained annotations across projects has no compared per-project build receipts in the reviewed artifacts. — Settled by: Dated project annotations and their generation histories.
- [U2] README.md:47 “| `full/record_starsolo.gtf` | `interspersed` | STARsolo and cellranger: record counts through record-as-gene grammar |” — STARsolo counting is exercised, but cellranger qualification runs mkgtf/mkref and supplies no cellranger count matrix. — Settled by: A cellranger count fixture demonstrating record identities and molecule conservation.
- [U3] README.md:82 “`./build.sh --genome mm39 --build-dir <dir>` runs the stages, writes the manifest and IDs, and verifies the directory in place.” — A full build command was not rerun because this review forbids rebuilding; retained invocation provenance and component tests supply partial evidence. — Settled by: An authorized complete run against a fresh writable scratch directory with the cached pins and qualified toolchain.
- [U4] README.md:83 “`./build.sh --genome mm39 --root <refroot>` builds and verifies in unique staging, installs at `te_mm39/archive/<BUILD_ID>/` and atomically selects the relative `current` symlink; `--no-select` preserves the existing selection.” — This review forbids publication. Tiny publication cases demonstrate staging/install/selection semantics, not a fresh complete build through this command. — Settled by: An authorized full scratch publication with an empty destination and cached sources.
- [U5] README.md:84 “`./build.sh --genome mm39 --family gene --root <refroot> --parent-build-id <full-parent-id>` publishes the GENCODE vM37 child for `interspersed` and `compat_tetranscripts_mm39`.” — This review forbids rebuilding/publication; the delivered child and component/dependency tests were checked. — Settled by: An authorized complete child publication against a verified parent archive and pinned GTF.
- [U6] README.md:89 “Scripts use `LC_ALL=C`; `TE_TRACKS_SOURCE_CACHE` reuses checksum-matching sources, and host builds compare recorded toolchain versions.” — Locale and checksum-cache behavior are demonstrated; execution of the host toolchain-comparison procedure is unavailable here. — Settled by: The owner’s host preflight/version log from the qualified image.
- [U7] README.md:102 “`acceptance --build` requires an empty `$TE_TRACKS_REFROOT/acceptance/` and publishes a fresh core/child pair there; `acceptance` checks that pair again, with development archives retained.” — The occupied-root guard and acceptance replay are exercised; fresh pair construction is prohibited for this review. — Settled by: An authorized acceptance --build run with an empty acceptance directory and matching cached pins.
- [U8] README.md:112 “mm39 builds and publishes through `build.sh --genome mm39 --root <refroot>`; a genome config requires its `SPECIES` entry in `src/lib/manifest.py`.” — The species admission condition is present; the full build/publication command was not rerun under the no-build constraint. — Settled by: An authorized complete scratch publication using the declared species entry.
- [U9] AGENTS.md:9 “Production builds, publication, directory/ACL policy, backup and CRI transfer run on the host in the qualified devcontainer image with writable destination mounts.” — The mount is read-only here and the runbook prescribes these host operations; completed host builds, ACL qualification, backup and CRI transfer are unavailable for verification. — Settled by: Host execution, filesystem/ACL qualification and verified destination receipts.
- [U10] AGENTS.md:34 “That check verifies cached source pins, requires an empty `$TE_TRACKS_REFROOT/acceptance/`, and builds `te_mm39` followed by `te_mm39_gene` there.” — Source-pin refusal and the empty-root guard are demonstrated; constructing and publishing the pair is prohibited. — Settled by: An authorized fresh acceptance build with cached pins and writable scratch storage.
- [U11] docs/DECISIONS.md:6 “The canonical tables publish four feature levels—record, instance, subfamily and canonical family—and every quantification records its assigned and reported levels.” — The feature identities are present, but the package contains no population of consuming quantifications proving that every run records both levels. — Settled by: Consuming quantification ledgers with assigned-level and reported-level fields.
- [U12] docs/DECISIONS.md:47 “Peaks, motif databases and TF inference are the ATAC framework's own pinned inputs; motif content on TE consensus sequences belongs to another child family.” — This names ownership and actual pins in an external ATAC framework; this package’s artifacts do not establish those consumers’ inputs. — Settled by: The consuming ATAC reference manifests and their digests.
- [U13] docs/DECISIONS.md:59 “Consuming projects keep their quantification ledger in their own tables, `peak_record_overlaps` and `te_feature_registration`, keyed to `rmsk_records`, with `feature_level` as the measurement grain column.” — The named consuming-project ledger tables and their populated key/measurement columns are absent from this package. — Settled by: The consuming projects’ schemas and populated ledger artifacts.
- [U14] docs/DECISIONS.md:108 “Consuming ledgers key on `te_catalog_id` and `te_build_id`.” — These are proposed consumer keys here; actual adopting ledgers are outside the artifacts verified. — Settled by: A populated consuming ledger carrying both identifiers.
- [U15] README.md:88 “Every published build stays on disk; consumers resolve `current` once and pin the full ID and file digests.” — Archive retention and resolve-once CLI behavior are demonstrated; actual consumers retaining full build and file-digest pins are not established by these package artifacts. — Settled by: Consuming run manifests carrying the resolved BUILD_ID and each consumed file digest.

## Numbers recomputed

In the replay commands, `P="$TE_TRACKS_REFROOT/te_mm39/build"` and `C="$TE_TRACKS_REFROOT/te_mm39_gene/build"`; direct Python uses `PYTHONDONTWRITEBYTECODE=1`. Counts came from artifact rows or individual result lines, not check-summary literals.

| Claim | Stated | Observed | Command / independent calculation |
|---|---|---|---|
| README:4 raw Alu family | 558,808 | 558,808 | `python3 -c 'import gzip,sys; print(sum(len(r)>10 and r[0].isdigit() and r[10].partition("/")[2]=="Alu" for r in map(str.split,gzip.open(sys.argv[1],"rt"))))' "$P/source/mm39.fa.out.gz"` |
| README:4 SINE/B1 | 0 | 0 | `python3 -c 'import gzip,sys; print(sum(len(r)>10 and r[0].isdigit() and r[10]=="SINE/B1" for r in map(str.split,gzip.open(sys.argv[1],"rt"))))' "$P/source/mm39.fa.out.gz"`; original independent scan covered 5,320,771 rows. |
| README:4 tokens; :31 universes; :40 suffix rows | 3; 6; 7 | 3 source name/class/family columns; 6 universe objects; first 7 of 9 output rows are suffixes | Read raw record fields, json.load(universes.json), and expand README table paths against exports. |
| README:105 suite results | 26 core; 11 fresh; 11 replay; 15 consumer + 1 unsupported | 28 core; 11 acceptance replay; 15 consumer + 1 unsupported; all three exits 0. Fresh construction unverified. | Count individual ^pass/^fail/^unsupported lines and check files, independently of runner summaries; fresh construction excluded. |
| AGENTS:22 modes; :37 required checks | 4 invocations; 11 required checks | core, consumers, acceptance, acceptance --build; 11/11 acceptance filenames required | Enumerate tests/checks and invoke all four forms; --build exercised through guarded refusal. |
| AGENTS:45 root hash | First 12 SHA-256 digits | 930ad69d7ac3 | hashlib.sha256(str(Path(REFROOT).resolve()).encode()).hexdigest()[:12] |
| DECISIONS:70 browser comparison | Once at source qualification | Comparison in stage 05 and key/class/family comparisons in stage 10 | Run qualifier and record-builder refusal paths on independent fixture copies; reproduce full qualification report. |
| DECISIONS:86 minimum retained block | 1 bp | 775 one-base blocks; zero nonpositive blocks among 3,684,934 interspersed SAF rows | Stream child exports/ucsc/interspersed/exon_subtracted/subfamily.saf; End-Start+1. |
| README:55 / DECISIONS:86 exon-disjoint guarantee | Zero exon overlap | 0 overlapping blocks in both complete SAFs (3,684,934 and 3,717,740 blocks) | Merge every retained GTF exon by contig; bisect the independent interval union for each inclusive SAF interval in both universes. |
| DECISIONS:102 context envelope | 10 kb upstream / 2 kb downstream | Proposed parameters; zero delivered context tables | Enumerate actual payload paths and every retained identity.inventory; see F5. |
| DECISIONS:160 duplication | Doubling | Two registrations for the shared record key; one for its record alias | Stream all export_feature_members.tsv.gz rows, group by universe/variant/level/grammar and count each exact example key; see F9. |
| DECISIONS:173 rank aliases; :182 sentences | 5 aliases; 2–4 sentences each | 5 aliases; sections 9/15=6 and 12=5 | Count OUTPUTS rank-alias rows and sentence boundaries after shielding inline code and links. |
| README:86 / DECISIONS:74 build hash | sha256 prefix plus canonical identity | All 10 stored IDs match independent recomputation | hashlib.sha256(b"te-tracks-build-v1\n" + json.dumps(identity,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()) |
| Catalog identity and child inheritance | Decompressed canonical tables, same parent catalog | 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e throughout | Independently hash canonical identity.catalog with te-tracks-catalog-v1 prefix; core 70 and closing verifiers check payload digests. |

GENCODE vM37 was read from the retained GTF header (version M37 / Ensembl 114). The rank-rule version was read from manifests and the implementation. All six parser checkout HEADs equal their pins; direct executable probes report IRescue 1.2.0, featureCounts 2.1.1, STAR 2.7.11b and cellranger 10.1.0. Scope contains no payload-byte, duration or resident-memory literals.

## Capabilities demonstrated

| Claim | How demonstrated | Outcome |
|---|---|---|
| Core contracts and full development artifacts | tests/run.sh core; complete stdout/stderr and exit captured | 28 pass, zero fail/unsupported; exit 0. |
| Activated consumer qualification, offline | source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh; TENX_DISABLE_TELEMETRY=1 tests/run.sh consumers | 15 pass, one unsupported (Stellarscope boundary); exit 0. Cellranger evidence covers reference construction. |
| Existing acceptance pair | tests/run.sh acceptance, unchanged reviewed expectation files | 11 pass, zero fail/unsupported; exit 0. |
| acceptance --build guards | Real runner against occupied private root; then repeat with a byte-flipped independent copy of cached mm39.fa.out.gz | Occupied root: one fail + ten required unsupported, runner exit 1. Corrupt source copy: checksum refusal, exit 1. Neither case started a build. |
| Runner exits and required suffixes | Copied runner/common.sh; non-executable shell and Python checks returning 0, 3 and 7; test both .required.sh and .required.py; missing/empty directories and bad usage | Check 0→pass/runner 0; optional 3→unsupported/runner 0; both required suffixes with 3→runner 1; check 7→fail/runner 1; each usage/missing/empty-directory case→2. Non-executable .sh/.py files ran in name order. |
| Missing versus damaged selected archives | Real runner against an absent private root; then copied BUILD_ID/CATALOG_ID/MANIFEST.json in both selected family layouts, deleting each copy in turn | Absent pair: eleven required unsupported, exit 1. Each of six identity-file deletions: eleven failures, exit 1, with the missing file named. |
| Root override, locale, bytecode and build flag | Copied runner with a relative --refroot; inspect check environments and execution order; core 01 exercises private fixture sharing/cleanup and retained override | Relative root exported as an absolute path; LC_ALL=C and PYTHONDONTWRITEBYTECODE=1 observed; --build flag=1 reaches the first check; fixture lifecycle self-test passed. |
| Scratch lifecycle | TMPDIR under the required private scratch root; two common.scratch contexts plus consumer_floor.py against retained GTF | Both unique task directories were removed on context exit; the consumer floor used the documented root-hash path and removed its task directory; exit 0. |
| Absent executable convention | Run IRescue, featureCounts, STAR and cellranger executable checks without activation | Each of four actual executable checks returned 3 with its absent binary named. |
| Source parsing, qualification, universes, canonical taxonomy and rank metadata | Core 10–34 against full artifacts plus authored negative fixtures; independently counted opening source figures | Core 10–34 passed: every canonical row was recomputed from the rule; the external canonical-taxonomy oracle covers the 20 multi-label names; the Dfam view checks its complete selected-name scope. Fresh full-source qualification exited 0 and reproduced the retained report byte for byte; both source-comparison paths rejected family disagreement. |
| Export identity, coordinates, namespaces and preflight | Core 40–43 and 60–62; full-data shape/registration and named fixture refusals | All cited full-data and fixture checks passed; acceptance reproduced those results. |
| Exon-disjoint support and parent dependency | Core 80–83; acceptance child/oracle checks; independent inclusive-interval union plus bisect scan of every retained SAF block; independently hashed alias copies | All cited checks passed; independent complete SAF scans found zero exon-overlapping blocks in both universes. |
| Annotation changes may preserve support | Core 81 duplicate-row invariance and independently changed copied GTFs | Core duplicate-row invariance passed; independent 24-row→23-row annotation change preserved the complete mask. |
| Default mask versus deferred mask admission | validate_policy on declared default plus stranded/protein-coding/basic substitutions | The retained default passed; all three alternative policy substitutions were refused as unsupported. |
| Publication identity and retention | Core 70–73 and child publication fixtures; inspect archive modes and relative current targets; earlier full archives verified at closing | All publication fixtures passed; eight archive directory/file trees have 0555/0444 modes and exact declared payload rosters; closing results below. |
| README links and target descriptions | Resolve all nine README links and anchors; inspect promised source, schema/status/map, decisions, runbook, release and expectation sections | All resolve and match their pointer descriptions. |
| README output-table concordance | Rows 44→OUTPUTS 15–16, 45→17, 46→18, 47→19, 48→20, 49→21–22, 50→23–25, 51→26, 52→30; inspect every expanded artifact path | All nine rows agree; qualification limits remain those of the long map. |

Decision-state audit: 1–3, 5–8 and 12–15 have delivered schema/export/fixture evidence, subject to the external-consumer uncertainties and the matrix overstatement above. Decision 4 delivers the vM37 child. Decision 9 delivers the not_computed declaration. Decision 10 delivers records and source instances; insertion reconstruction remains a condition for candidate admission. Decision 11 has a proposed contract and no delivered candidate view. Decision 16 has the sentence-count contradiction above.

Deferral audit: inspected both development builds, eight complete retained archive inventories and their directory rosters, configs and implementation entry points. hg38, transcript context, ERV reconstruction, age tiers, stranded mask, 10x child, instance STARsolo profile, TES context envelope and cross-build correspondence remain absent. Instance membership, consensus coordinates, Dfam clades and divergence are available precursors. Consumer pilots remain external evidence gates. Protein-coding/basic masks have retained consult measurements and conditional admission; the production policy accepts the all-exon unstranded mask.

## Cross-scope contradictions

| Your path | Other path | Contradiction |
|---|---|---|
| docs/DECISIONS.md:98 | docs/OUTPUTS.md:549, :884, :939 | DECISIONS describes published context rows and flags; OUTPUTS declares context not_computed and defers the relation. |
| docs/DECISIONS.md:160 | docs/OUTPUTS.md:714 | DECISIONS generalizes doubling to a run’s matrix; OUTPUTS identifies the narrower 1,000-shared-record demonstration. |
| docs/DECISIONS.md:144 | docs/RUNBOOK.md:42 | DECISIONS claims environment delivery through the runbook; its recipe path is absent. F11 records the observed te-quant path for the publication validator. |

README’s nine-row short consumer map has no row-level disagreement with OUTPUTS. The second-child contradiction is also internal to this scope: DECISIONS:39 versus README:73.

## Closing verification

Final artifact checks ran after all suites and mutation probes. Paths below are relative to `TE_TRACKS_REFROOT`.

`python3 src/99_verify.py <directory>` was run for each build. The development child also received `--parent-dir "$TE_TRACKS_REFROOT/te_mm39/build"`; archived children resolved their retained parents.

| Build directory | Exit |
|---|---:|
| `te_mm39/build` | 0 |
| `te_mm39_gene/build` | 0 |
| `pubroot/te_mm39/archive/5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813` | 0 |
| `pubroot/te_mm39/archive/763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c` | 0 |
| `pubroot/te_mm39/archive/9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d` | 0 |
| `pubroot/te_mm39_gene/archive/1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b` | 0 |
| `pubroot/te_mm39_gene/archive/198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1` | 0 |
| `pubroot/te_mm39_gene/archive/693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0` | 0 |
| `acceptance/te_mm39/archive/5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813` | 0 |
| `acceptance/te_mm39_gene/archive/198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1` | 0 |

`python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/<root>" --family <family>`:

| Root | Family | Exit |
|---|---|---:|
| `pubroot` | `te_mm39` | 0 |
| `pubroot` | `te_mm39_gene` | 0 |
| `acceptance` | `te_mm39` | 0 |
| `acceptance` | `te_mm39_gene` | 0 |

Both roots resolve core `5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813` and child `198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1`. All ten build-verifier and four verify-current exits are 0.

All work used the stipulated environment and private TMPDIR, with real copied files for mutations. Full builds, production publication, installs, network and git writes were excluded. Complete command logs were captured in the private scratch directory; the private scratch directory was removed with Python shutil.rmtree after the results were transcribed. The three scoped files retained their starting SHA-256 digests. Only this review is written in the package.
