# Milestone 9 seam review (codex gpt-6-astra)
Verdict: BLOCKING

Reviewed `redesign-2026-09` at `204ee66`. The records, exports and child compose coherently; two operational handoff defects prevent the documented stranger workflow. This review used targeted probes and existing archives, with no rebuild, publication, installation, network access or git write. The four complete suite modes were not repeated. Internal `reviews/` and `prompts/` citations are under `docs/_internal/redesign-2026-09/`; numbered plans are under `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/`.

## The one thing the first consumer will hit

**Recreating the advertised consumer environment does not recreate the sources its required qualification checks actually load.** `docs/RUNBOOK.md:42` points to `te-consumers/env/bootstrap.sh`, then activation and `tests/run.sh consumers`. Those checks load six separate sibling `.ref` checkouts (`tests/lib/consumers.py:22`), whose location and restoration procedure appear in no public setup instructions. The bootstrap installs packages and executable shims, not those checkouts. An activated-environment probe with only the checkout root redirected to an absent private directory made required IRescue check 10 exit **1**, at `git describe` with exit **128**, before any fixture was built. An otherwise successful installation therefore leads to source hunting and reverse engineering of the test harness on a fresh host. The full commits in the runbook are useful, but cannot replace the missing repository/path/restore instructions. This is B1.

## Blocking

- [B1] `docs/RUNBOOK.md:42`, `docs/RUNBOOK.md:320`, `tests/lib/consumers.py:22,73,98`: required parser-source prerequisites have no public reconstruction procedure — the six paths are `01_modules/.ref/{irescue,stellarscope,TEsingle,TEtranscripts,TElocal,MATES}`; the umbrella ignores `.ref`, and the referenced bootstrap creates none of them. The activated missing-checkout probe above fails deterministically — publish all six source URLs, destination paths and full commits with restoration commands, or qualify against reconstructible installed sources. Calling these checkouts “vendored” also misstates their packaging.
- [B2] `docs/RUNBOOK.md:186–190,200–204`: failed clean-builder checks fall through to selection — the documented caller is `bash -l` (`:100`), with neither `set -e` nor `|| exit` around either Python assertion. A harmless exact-structure probe printed `AssertionError`, then `SELECT_WOULD_RUN`, and returned **0**. `src/release.py:53–65,84–101` accepts valid dirty manifests; convergence preserves the first manifest — explicitly terminate on each failed gate and make the publication sequence fail-fast before selection. The claimed protection against selecting dirty host provenance is currently unenforced by the written commands.

## Advisory

- [A1] `docs/RUNBOOK.md:42–45`: “reproducible environment” exceeds the referenced recipe — sibling `te-consumers/env/bootstrap.sh:22,25,29,47` upgrades packaging tools without pins, installs top-level Git requirements without consuming `pip-freeze.txt`, and extracts downloads without enforcing the recorded hashes. Current source commits match all five installed Python tools — narrow the reproducibility claim or consume a dependency lock and verify downloads.
- [A2] `docs/DECISIONS.md:202–203`: consumer-environment promotion is still listed as deferred to phase 9 — promotion by reference is delivered at `docs/RUNBOOK.md:42–68`, consistent with plan 19:54–55 and the owner's sibling-package ruling — replace that stale deferral with its delivered owner and the remaining pilot gates.
- [A3] `tests/expectations/mm39/README.md:6,16`: the “Independent authoring evidence” heading conflates correctness oracles with reproduction pins — `identity.tsv` hashes came from the earlier development build, even though the phase-9b prompt quoted them before acceptance. They establish reproduction, not biological correctness — label that distinction explicitly; retain the pins and fatal discrepancy check.
- [A4] `tests/expectations/mm39/gene_oracle.tsv:2–12`: incomplete metric pinning obscures available independent evidence — there are **11 literals**, including `annotation_rows`, so only **10 of the 18 printed metrics** are pinned, rather than the prompt's twelve. Unpinned: chr18 `input_records`, `exon_rows`, `union_bp`; chr19 `exon_rows`; `chr1_MU069434v1_random` `exon_rows`, `union_intervals`, `union_bp`, `retained_bp`. Add independently supported anchors. Exact bedtools/SAF block-multiset equality still makes the oracle substantive.

I agree with `reviews/m7_rulings.md` M2: the clean-host gate belongs in the runbook; B2 is a defect in that assigned gate. I agree with `reviews/m2_rulings.md:127–128`: the historical universe expectations earned acceptance through three independent derivations. I agree with `reviews/m5_rulings.md:97–98`: MATES is an explicitly fixture-only adapter.

Deferral audit: hg38, transcript context, structural/ERV reconstruction views, age tiers, the stranded mask, TES-side context, instance STARsolo, cross-build correspondence and the 10x annotation child are absent from the shipped inventories and applicable config. Every retained child uses vM37, the unstranded exon union, minimum block 1 and `not_computed`. Dfam clades/divergence and source instances are delivered evidence for later decisions; they do not constitute those deferred products. A2 is the stale shipped-as-deferred item. The annotation sequence in `DECISIONS.md:39–41` is clarified as future work by README's explicit 10x deferral.

## Runbook walk

| Step | Executed or read | Outcome |
|---|---|---|
| Gene parent resolution and publication, lines 8–21 | Read; verification executed in closing | Existing-parent precondition is explicit. Commands select `config/mm39_gene.env` through `--family gene`; no unsupported `--config` appears. |
| Scratch child build and core suite, lines 23–38 | Read | Parent/child paths and flags exist. Build and suite deliberately omitted under this review's constraints. |
| Consumer setup/activation, lines 42–74 | Activation and missing-checkout probe executed; bootstrap/suite read | Activation exists. Required qualification has the undocumented B1 prerequisite. No installs or complete suite run. |
| Host image launch, lines 79–101 | Read | Compose names `scdock-r-dev:v0.5.15`; no Docker socket here. Image digest, writable mount and fresh-container behavior remain host-only. |
| Producer versions, lines 103–132 | Executed | Python 3.11.15, pyarrow 25.0.0, pandas 2.2.3, numpy 1.26.4, pysam 0.24.0, zlib 1.2.11/1.2.11, bash 5.1.16, coreutils 8.32 and bedtools 2.31.1 match; exits 0. |
| Source-cache seed, lines 134–164 | Read-only hash-validation portion executed | All seven pins match. Destination creation/copy omitted; retained cache exists here. A new host must receive that retained cache as stated. |
| Clean tree/build/install, lines 166–183 | Read | Dispatch is correct; no build/install executed. Acceptance and development identities match. |
| Clean manifest/select, lines 185–208 | Read; harmless failure probe executed | B2: failed Python assertion does not terminate the calling shell. |
| Directory/ACL/backup policy, lines 210–216 | Read | Owner-only policy and CRI mirror named. Effective ACLs and destination availability cannot be qualified here. |
| Transfer/recovery/fault cases, lines 218–246 | Read | Parent-first transfer, raw-manifest integrity and private staging are specified. Site transport, disk exhaustion, interrupted copy, filesystem rename and host access remain host tests. |
| Consumer resolution/pins, lines 248–267 | Read; dependency refusals and closing verification executed | Pins identify immutable paths and the child's own parent. Missing parent and an older same-catalog parent both fail. |
| Namespace preflight, lines 37–38 | Executed | Three core namespace BEDs and child UCSC SAF each exit 0 against dictionaries generated from the retained aliases; this checks the command/namespace seam, not an independent sequencing reference. |
| Manual annotation floor, lines 299–318 | Executed through `--reader` on a private 50,000-row head | Both readers exit 0. Stellarscope: 132,988,928 annotation bytes/3.808 s; TElocal: 51,314,688/24.962 s. Historical timing anchors remain historical. The default driver uses `p9b`; private-head invocation kept all scratch inside `m9-review`. |
| Consumer pins/pilots, lines 320–337 | Read; six checkout versions and five installed commits checked | Current pins match. Barcode, chemistry, mate/UMI and bulk strand policy remain consuming-project gates. |

The frozen runner passed `bash -n` and **22 isolated cases** using real copies of the runner/common shell library: five exit 0, three exit 1, fourteen exit 2. Cases covered both option orders, absolute normalization, duplicate/unknown/missing/empty options, `--build` outside acceptance, missing/empty check directories, failing and dangling checks, and optional/required unsupported checks. The live-edit parse-error report leaves no reproduced defect in the frozen runner (`tests/run.sh:14–47,61–117`).

All **27 core and 12 child exports** have named readers. Documentation supplies their grains and namespace choice (`docs/OUTPUTS.md:9–34,654–666`); all 39 were checked at the traced coordinates against actual bytes. In the table, `<ns>` is the alignment-matching `ucsc`, `ensembl` or `gencode`; full paths follow the documented export template.

| Consumer | File, universe/variant and measured identity |
|---|---|
| Bulk featureCounts | Child `<ns>/interspersed/exon_subtracted/subfamily.saf` or `taxonomy_triple.saf`; GeneID is name or canonical name:family:class. Child compatibility pair explicitly uses `compat_tetranscripts_mm39`. |
| TEsingle / TElocal | Core `<ns>/interspersed/full/record.gtf` plus full counting gene annotation; record four-tuple. TElocal builds its own `.locInd`. `subfamily.gtf` supplies the named sensitivity grain. |
| TEtranscripts | Same unmasked GTFs and full gene annotation; canonical taxonomy triple, not a locus result merely because the filename is `record.gtf`. |
| Stellarscope | Same GTFs; `locus` gives record alias or subfamily; `record.gtf` with `instance_id` gives source instance. Right-boundary gate remains explicitly unsupported. |
| STARsolo / cellranger | Core `<ns>/interspersed/full/record_starsolo.gtf` plus full gene annotation; record alias in `gene_id`. Cellranger qualification covers reference construction; counting recipe remains downstream. |
| IRescue | Core `<ns>/interspersed/full/{record,subfamily}.bed`; BED column 4 is record ID or name. |
| Other released routes | featureCounts reads full SAFs for sensitivity; bedtools reads record/family BEDs; 14761 reads `<ns>/all_rmsk/full/record.bed`. Tables/source/manifest readers are named at `OUTPUTS.md:27–34`. |
| Fixture readers | MATES has `record_mates.csv`/`.bed`, fixture ordinal and name grouping; samtools reads fixture BAMs; SAF and DuckDB readers bind the documented columns/registration. Their limited scope is explicit. |

The documented pinning contract for every published counting route requires `BUILD_ID`, `CATALOG_ID`, export digest, namespace, universe, variant, feature level and key grammar. Child routes additionally pin parent and annotation digest; EM/combined routes pin the full counting annotation (`RUNBOOK.md:258–267`). No released export is orphaned, and no named reader lacks a file or an explicit fixture-only boundary.

## One record, one subfamily, one instance, followed end to end

Here `C` is the development core and `G` its child under `$TE_TRACKS_REFROOT/{te_mm39,te_mm39_gene}/build`; their identities equal the acceptance archives. Both carry CATALOG_ID `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e`. Line numbers for `.gz` files refer to decompressed text.

Take `R = L1MdFanc_I|chr1:8951646-8956913|+`, name `N = L1MdFanc_I`, record alias `A = R|mm39|L1MdFanc_I|chr1|8951646|8956913|+`, instance alias `I|mm39|8118`.

| Hop | Observed values and join |
|---|---|
| Primary source | `C/source/mm39.fa.out.gz:10043`, annotation ordinal **10040**: score 32349; divergence/deletion/insertion **7.0/2.4/0.8**; chr1 **8951646–8956913**, `+`; name N; `LINE/L1`; consensus **218–5586**, left **987**; query-left **186197366**; instance **8118**; no star. |
| Canonical record | `rmsk_records` keyed by R retains those fields, length **5268**, raw `LINE`/`L1`, UCSC consensus fields **218/5586/−987**, overlap flag false and source ordinal 10040. The documented five-field coordinate/name key and ordinal locate the source without guesswork (`OUTPUTS.md:54–86`). |
| Universes | Explicit member rows at **1608373,5380217,9173339,12920089** put R in compatibility, interspersed, interspersed-plus-satellites and retrotransposon-derived, all nonprovisional. `all_rmsk` membership is implicit; satellite membership is absent. |
| Raw/canonical name | `C/tables/rmsk_taxonomy.tsv:17521` and `taxonomy_canonical.tsv:17514`: N → **LINE/L1**, one label, concordant ranks, shares 1.0; **11,630 records**, **8,704 instances**, **9,315,041 bp**, median divergence **5.7%**. All 11,630 source rows independently matched the Parquet records on coordinates, strand, name, instance, score and divergence/deletion/insertion. |
| Dfam models | N → `taxonomy_dfam_models.tsv:342–344`: **5end DF000001828 (v1), 1255 bp; orf2 DF000001832 (v1), 4681 bp; 3end DF000001827 (v1), 987 bp**. Part-model set, sum **6923 bp**, Dfam **4.0**. This metadata sum has no implied whole-element coordinate projection. |
| Dfam lineage/ranks | `dfam_lineage_nodes.tsv:217`: `root;Interspersed_Repeat;Transposable_Element;Class_I_Retrotransposition;LINE;Group-II;Group-1;L1-like;L1-group;L1`, depth **9**, code **R/I (LINE)/L (L1)**. `Class I (retrotransposons)`, order LINE, superfamily/family L1 have `part_model_set`; subclass empty/`inapplicable`; subfamily N/`mapped`; code uncertainty false. |
| Dfam clades | Accessions join `dfam_model_clades.tsv:826,827,831`; each has the same complete path ending **Muridae;Murinae;Mus**, hence one distinct clade and `compatible`. Join by accession, not the display `clades` string (`OUTPUTS.md:384–390`). |
| Namespaces | `contig_aliases.tsv:2`: UCSC **chr1**, Ensembl **1**, GENCODE **chr1**, GenBank **CM000994.3**, RefSeq **NC_000067.7**, length **195154279**. Only interval contig changes; R and A keep `chr1`. |
| Core registration | `C/tables/export_feature_members.tsv.gz:60450–60457` registers the eight spellings below with block **8951646–8956913**; row **30129633** adds the all-rmsk record spelling. STARsolo reuses the record-alias registration. |
| Child mask | `G/source/gencode.vM37.primary_assembly.annotation.gtf.gz:2486,2533`: two Sntg1 transcript exon rows share **8952385–8952438**, on **minus** strand. Unstranded union removes their **54 bp once** from this plus-strand TE. |
| Child status/blocks | Status row **10041** is split, **2** blocks, retained **5214**, removed **54**. Blocks **8951646–8952384** and **8952439–8956913** appear at interspersed SAF/registration rows **7428–7429**, and in both feature groupings, both child universes and all three namespaces. |

The eight registration spellings are R; A; `A:L1MdFanc_I:L1:LINE`; N; `L1MdFanc_I:L1MdFanc_I:L1:LINE`; `LINE/L1`; `L1MdFanc_I:L1:LINE`; `I|mm39|8118`, in the documented level/grammar order (`OUTPUTS.md:598–607`). BED uses **8951645–8956913**, score **1000**, and R/N/`LINE/L1`; GTF/SAF use inclusive bounds and GTF score **32349**. `record.gtf` has gene N and transcript/locus A; `record_starsolo.gtf` has gene/transcript/locus A, gene name N and TE biotype; `subfamily.gtf` has gene/transcript/locus N. SAF GeneIDs are N or its taxonomy triple. These values match all namespace files, including the all-rmsk BED.

For the **whole subfamily**, every core registration spelling has **11,630** supporting rows, all five applicable universes retain the same records, and the name occupies **32 contigs**. Child status is **11,436 unchanged + 70 trimmed + 36 split + 88 fully subtracted = 11,630**; **11,586 blocks**, **9,245,181 retained bp + 69,860 removed bp = 9,315,041**. Each child universe/grouping has 11,586 supporting registrations. Canonical name → Dfam model is one-to-three here; summing a name-level count after that join triples it.

For **instance 8118**, `rmsk_instance_members.tsv.gz:5084875–5084876` contains R and `L1MdFanc_I|chr1:8956915-8957897|+` (source ordinal **10041**). The second record has length **983**, score **7617**, divergence **6.2%**, consensus **5588–6564**, left **9**; it shares the name, universes, taxonomy and Dfam joins above. Its child status is unchanged, one block **8956915–8957897**. The instance preserves the one-base genomic gap **8956914**, has **6251 bp** parent support and **6197 bp** child support across three blocks. Its grammar is available through record GTF instance attributes; no instance STARsolo or child instance-count export is claimed.

Joins need no undocumented identity knowledge. A naive record-ID registration join doubles R across `all_rmsk`/`interspersed`; a scoped instance-count join doubles across its two members; the selected split record contributes two child support rows; a subfamily-count join repeats a count over all 11,630 parent records or 11,586 child blocks. These are support relations, not allocation weights. `OUTPUTS.md:614–620` supplies the full scope and distinct-measured-feature rule. Dfam models/clades also require aggregation before counts are joined.

Identity probes used **real copied files with different inodes**, never linked copies. Changing the gzip timestamp of `rmsk_records.tsv.gz` changed recomputed BUILD_ID to `1197c077da3b1d64bad681abc43c2a70f77f96630d2f6605a0b269efe80f0a0c` while retaining CATALOG_ID. Changing canonical record score **3667→3668** changed both hashes, with catalog `8529ccf5a53e4c4d29cbc1116ee827c29008618a7d5fafa545ca5bff26f32ac4`. Appending LF to copied qualification or alias bytes changed BUILD_ID alone. These exercised the real inventory digests/catalog function without authoring or publishing a build. No canonical-record change that preserved catalog identity, or inventoried-byte change that preserved build identity, was found.

There **is** a published-byte exception to a literal “everything changes BUILD_ID”: changing only raw MANIFEST provenance leaves both IDs fixed. Actual acceptance/development manifests likewise differ with identical identity sections. This is explicitly specified at `RELEASES.md:101–104`, not a newly discovered identity failure. `m7_rulings.md` H3 and `p9a_rulings.md`'s verifier threat-model ruling remain sound: canonical text binds the catalog; serializers and metadata have their declared boundaries; the verifier is not an authenticity oracle for a deliberately re-authored manifest.

Dependency probes through `src/99_verify.py` exited **1** for an absent parent and **1** for the earlier valid `9ddf3622…` parent sharing the same catalog (`parent BUILD_ID differs`). Earlier-archive selection passed the real current/candidate verification path in `release.select_locked`; only the three filesystem-changing calls were intercepted, so no selector changed. Closing verification below checks the actual earlier archives again.

Acceptance manifests record **51c016243c8991b27f0da112a00d90a815ead929**, dirty **true**. `git diff` of `build.sh`, `src/`, `lib/`, `config/` and `data/dfam/` from phase-9a `d28336f` to both that revision and HEAD is empty. Acceptance/development identity sections are exactly equal. This confirms the reported source/config and identity continuity; B2 prevents confirming the claimed dirty-host exclusion.

The export peak spread is **1,871,175,680 bytes**, about **1.87 GB / 38% of the smaller observation**. Equal output hashes do not guarantee equal allocation or RSS. The recorded **16 GB single-producer reservation** has headroom over both 4.94/6.81 GB stage observations and the historical complete peak near 9 GB; two observations cannot establish an upper bound. `RUNBOOK.md:284–286` correctly asks for a complete host measurement. The manual floor utility's location under acceptance `lib/` is defensible: timing/RSS are reported planning observations, and no suite check pretends to assert them.

## Claims checked

A counted claim is a distinct assertion, with repeated public statements counted once. Table checks establish agreement with retained artifacts; raw-record measurements used independent SQL, and the targeted geometry probe used bedtools. Historical measurements are not promises of future runtime.

| Claims checked | Wrong | Where / evidence |
|---|---:|---|
| 25 sizes, inventory/contract/source counts | 0 | `RELEASES.md:185–214`, `PROVENANCE.md:183–185`; stat and manifests. |
| 24 universe metrics; 17 class counts | 0 | `PROVENANCE.md:46–84`; six summaries and raw-taxonomy sums. |
| 13 canonical-taxonomy; 22 Dfam metrics | 0 | `PROVENANCE.md:98–128`; canonical and normalized tables. |
| 16 child coverage/geometry metrics | 0 | `PROVENANCE.md:133–137`, `OUTPUTS.md:803–836`; summaries/coverage, with registration totals also traced. |
| 9 input hashes | 0 | Seven cache/package pins, legacy GTF MD5 and decompressed Dfam SHA-256. |
| 33 runtime/tool/source-version assertions | 0 | Runbook versions, OS/image evidence, six describe/commit pairs and five installed source commits. |
| 20 additional raw-record measurements | 0 | `PROVENANCE.md:38–59`, `OUTPUTS.md:79–117,494`; independent Parquet SQL, including 429,440 overlapping records. |
| 105 explicit README truth-table paths | 0 | `README.md:78–167`; brace-expanded, family-resolved: 33 repository, 55 core and 17 child paths. |
| 58 fixture facts | 0 | `OUTPUTS.md:654–718`; retained roster/FASTA/BAMs, featureCounts results, IRescue/STAR allocation JSON and cellranger reference. |
| 12 historical resource-carrier assertions; 12 floor arithmetic assertions | 0 | Acceptance manifests; `prompts/p9a_review.md:171,339`; `p9a_rulings.md:162–163`; `p7_rulings.md`; arithmetic allows separate rounding. |
| 18 three-contig oracle metrics | 0 | `PROVENANCE.md:147–149`; targeted bedtools comparison reproduced all eighteen. |
| 39 export-to-reader bindings | 0 | `OUTPUTS.md:15–26`; registered roster and the all-namespace byte trace above. |
| 10 deferral-status assertions | 1 | Nine absent products; delivered consumer environment still deferred (A2). |
| 3 operational handoff capabilities | 3 | Checkout reconstruction (B1), stopping failed clean checks (B2), exact environment reproduction (A1). |
| 1 expectation-provenance characterization | Overbroad | Independent-correctness wording applied to development-build hashes (A3). |
| **437 checked** | **4 false/incomplete operational or status claims; 1 overbroad characterization** | **423 quantitative/path/binding assertions matched.** |

Nine raw historical observations lack an independent surviving carrier in the inspected material: initial export RSS **6,807,732,224**; initial child RSS/time **874,917,888/152.012**; and the two reader triples at `RUNBOOK.md:312–313`. Original phase-9b build/floor logs were not retained under `p9b/`; original four suite exits likewise could not be re-established from their invocation logs. Later orchestrator logs corroborate suite counts. These are **unverified historical claims**, not demonstrated wrong values; the nine observations and four original exits are excluded from the checked total. Preserve their raw logs or a durable measurement witness. The final acceptance manifests do independently retain **4,936,556,544**, **881,565,696** and **154.376**.

## Acceptance suite: what would have to break

`core_checks()` (`tests/checks/acceptance/lib/common.py:79–94`) aliases acceptance archives as private `build` paths and requires every selected core subprocess to exit 0. This is useful full-scale contract replay, not fresh independent authoring. No acceptance check is incapable of failure.

| Check | What it would catch; fresh measurement versus replay | Independently authored |
|---|---|---|
| 10 source | Fresh seven source digests, report metric/equality/PASS checks, retained Dfam timestamp (`areas.py:21–39`). Any pin, metric or report drift fails. Source comparison itself is retained qualification evidence. | External source pins and prior independently checked report; no core replay. |
| 20 records/universes | Core 20/21/22 replay: schema, complete TSV/Parquet equality, keys/bounds, instances and every membership; fresh twelve record/instance metrics (`:42–77`). | Prior census/fixture anchors; fresh census does not author its own expected numbers. |
| 30 canonical taxonomy | Entirely core 30/31/32 replay: table/census drift, Dfam disagreement or violated authored rule/rollup cases fail (`:80–84`). | External 20-name Dfam and authored fixtures/census. All-row expected labels also use production `resolve`, so that leg alone is not an independent oracle. |
| 35 Dfam | Core 33/34 replay plus fresh four-table row counts (`:87–93`); metadata, rank-cell, clade/model or fixture drift fails. | External snapshot, prior census and authored rank edge cases. |
| 40 exports | Core 40/41/43 replay plus literal 27 exports, 49 families, namespace/file bytes (`:96–113`); changed coordinates, grammar, registration/conservation or matrix scope fails. | Fixture/census anchors; file-size literals are prior-output reproduction checks. |
| 45 record profile | Fresh complete streams in all namespaces (`:116–145`); malformed attributes, inconsistent record alias, duplicate gene or wrong 3,764,949/59 census fails. | Authored grammar and prior catalog census; no replay. |
| 60 namespaces | Entirely core 60/61/62 replay (`:148–150`); wrong alias/length, renamed bytes/order or preflight classification fails. | External FASTA lengths, separately implemented awk/sort projection and authored preflight cases. |
| 70 publication | Fresh identity encoding, expected IDs, rosters, modes, selectors, staging and reproduction comparison, plus production verification (`:153–209`). | IDs are development-output pins; hash procedure/rosters are authored. **Any BUILD_ID discrepancy fails `assert not discrepancies` at :208.** |
| 80 child | Core 80 replay plus fresh chunked status aggregation with restated predicates (`:212–238`); census, conservation, coverage, registration or SAF inconsistency fails. | Prior independent geometry/census; summaries partly derive from child status and need the independent geometry leg. |
| 85 bedtools oracle | Fresh GTF→merge→subtract versus exact SAF block multisets (`oracles.py:15–89`); any missing/extra block or pinned metric fails. Targeted run here exits 0 and reproduces all eighteen printed measurements. | External bedtools, retained pinned inputs and earlier reviewer anchors; A4 records omissions. |
| 90 legacy reconciliation | Fresh pinned packaged-GTF full coordinate/strand multiset (`oracles.py:92–148`); wrong MD5, count or either directional difference fails. | External legacy GTF and fixed 3,799,629 census; names intentionally excluded from this geometry oracle. |

Taxonomy and namespaces have **no fresh acceptance algorithm**. Their external fixtures/reference evidence keeps their acceptance claims meaningful; replay alone adds scale coverage, not independence. Build-derived intermediate expectations also occur in core 30:58–78 (labels/counts/medians), 40:143 (family count), 41:134,168–170,226 (instance and export metadata), 61:107–111 (renamed files/features), and 80:37–40,139–165 (status/block/feature counts). These are consistency checks. Independently pinned censuses, fixtures and external geometry prevent them from being tautological suite-wide evidence. I agree with the distinction already recorded in `reviews/m5_rulings.md:115–117`.

| Expectation table | Earlier derivation; could only the judged build supply it? |
|---|---|
| `source_pins.tsv` | Reviewed configs, phase-1 pins and `p9a_rulings.md:299`; external input hashes. **No.** |
| `source_qualification.tsv` | Audit report:25–52 and independent `m2_opus.md:65–93`; all 23 metrics predate acceptance. **No.** |
| `class_census.tsv` | Independent source parser in `m2_opus.md:73`, audit census. **No.** |
| `universe_summary.tsv` | `p2_impl.md:31–36`, independent `m2_opus.md:75–80`, authoritative m2 acceptance ruling. **No.** |
| `taxonomy_census.tsv` | Plan 13:109–116 for rank statuses; `reviews/p3_codex2.md:102–105` supplies the 14/6 multilabel class partition. **No.** |
| `dfam_census.tsv` | All 21 values in plan 19:35–39, with external metadata and catalog weights. **No.** |
| `record_census.tsv` | `p9a_codex.md:20`, `m5_rulings.md:18–23`, `m7_opus.md:50–51`, `m2_rulings.md:124–126`. **No.** |
| `exon_subtraction_summary.tsv` | Plan 18:118–125 and independent `p8_codex.md:180–182`. **No.** |
| `gene_oracle.tsv` | Prior bedtools derivation in `p8_codex.md:178–179`, `p8_rulings.md:19–22,40–42`. **No.** |
| `identity.tsv` | Prior development hashes in `p9b_impl.md:28–31`; roster counts are contract-derived. **Build-derived hashes, preserved before the judged acceptance build; reproduction evidence.** |

No new acceptance output was found copied into a census oracle. Prior plans can preserve a build observation without turning it into an independent correctness derivation: this qualification applies to identity/file-size fingerprints. Commit `204ee66` added **five expectation TSVs plus README.md**, not six new tables; ten expectation TSVs now exist. The default manual `consumer_floor.py` driver is outside the eleven checks and reports rather than gates timing deviations.

## Closing verification

Closing commands ran after all probes and mutation-copy cleanup. The actual roster is **eight physical archive directories and two development build directories**. Paths below are relative to `$TE_TRACKS_REFROOT`.

Each directory used `python3 src/99_verify.py <directory>`; archives supplied their corresponding `--root`, and the development child supplied `--parent-dir "$TE_TRACKS_REFROOT/te_mm39/build"`.

| Build directory or archive | Verifier exit |
|---|---:|
| `acceptance/te_mm39/archive/5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813` | 0 |
| `acceptance/te_mm39_gene/archive/198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1` | 0 |
| `pubroot/te_mm39/archive/5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813` | 0 |
| `pubroot/te_mm39/archive/763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c` | 0 |
| `pubroot/te_mm39/archive/9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d` | 0 |
| `pubroot/te_mm39_gene/archive/1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b` | 0 |
| `pubroot/te_mm39_gene/archive/198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1` | 0 |
| `pubroot/te_mm39_gene/archive/693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0` | 0 |
| `te_mm39/build` | 0 |
| `te_mm39_gene/build` | 0 |

| `python3 src/release.py verify-current --root <root> --family <family>` | Exit |
|---|---:|
| `acceptance` / `te_mm39` | 0 |
| `acceptance` / `te_mm39_gene` | 0 |
| `pubroot` / `te_mm39` | 0 |
| `pubroot` / `te_mm39_gene` | 0 |

The current core has **52 inventory entries, 27 contracts and 15,301,538,537 payload bytes**; the current child has **21, 12 and 2,157,717,760**. Their BUILD_IDs are the full `5e2a1563…` and `198f39f0…` archive names above; both have the catalog identity recorded in the trace.

All **14 completed commands exited 0**. Complete command output and exits were captured during execution. The before/after comparison found **zero changes across 579 retained paths**, checking sizes, modification times, modes and symlink targets. The entire private `m9-review/` scratch directory, including transient logs, was removed with Python `shutil.rmtree`. The sole repository write is this review; retained builds, archives and selectors remain in place.
