# Claim validation: outputs (codex gpt-6-astra)
Verdict: FALSE CLAIMS PRESENT

## Tally

| file | fact-asserting sentences | verified true | false | unverifiable |
|---|---:|---:|---:|---:|
| `docs/OUTPUTS.md` | 636 | 614 | 12 | 10 |

Counting convention: 348 wrapped prose sentences, 283 table rows, four numbered rule steps and one standalone command. Each table row is one composite assertion, including its paths, grain, namespace and coordinates; a false component makes the row false. Headings and table headers are excluded. Commands count as assertions of executable capability. Findings below account for every false or unverifiable unit.

The inspected core is `5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813`; the child is `198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1`. Their development directories and both `pubroot` and `acceptance` selectors declare identical identities. Historical archives were included in closing verification. Spatial checks cover all 27 core exports and all 12 child exports, every published universe and all three namespaces. Nonspatial tables have no coordinate convention. Both retained legacy experiment directories were inspected.

## False claims

The first seven findings quote artifact cells. Line 11 explicitly makes core paths relative to the archive root; the bare filenames below exist under `tables/`, and are absent at the stated root paths.

- [F1] `docs/OUTPUTS.md:27` “`tables/rmsk_records.{tsv.gz,parquet}`, `rmsk_instance_members.tsv.gz`, `rmsk_taxonomy.tsv`” — Both companion paths omit `tables/`. — Corrected: “The catalog tables are `tables/rmsk_records.{tsv.gz,parquet}`, `tables/rmsk_instance_members.tsv.gz` and `tables/rmsk_taxonomy.tsv`.”
- [F2] `docs/OUTPUTS.md:28` “`universes.json`, `tables/universe_members.tsv.gz`, `universe_summary.tsv`” — The summary is under `tables/`. — Corrected: “Universe definitions and census occupy `universes.json`, `tables/universe_members.tsv.gz` and `tables/universe_summary.tsv`.”
- [F3] `docs/OUTPUTS.md:29` “`tables/taxonomy_canonical.tsv`, `taxonomy_resolution_report.tsv`” — The report is under `tables/`. — Corrected: “Canonical rollups use `tables/taxonomy_canonical.tsv` and `tables/taxonomy_resolution_report.tsv`.”
- [F4] `docs/OUTPUTS.md:30` “`tables/taxonomy_dfam.tsv`, `taxonomy_dfam_models.tsv`, `dfam_lineage_nodes.tsv`, `dfam_model_clades.tsv`” — All three companions are under `tables/`. — Corrected: “Dfam annotations occupy `tables/taxonomy_dfam.tsv`, `tables/taxonomy_dfam_models.tsv`, `tables/dfam_lineage_nodes.tsv` and `tables/dfam_model_clades.tsv`.”
- [F5] `docs/OUTPUTS.md:31` “`tables/export_feature_members.tsv.gz`, `exports.tsv` in each family” — Both families inventory exports at `tables/exports.tsv`. — Corrected: “Each family publishes registration in `tables/export_feature_members.tsv.gz` and inventory in `tables/exports.tsv`.”
- [F6] `docs/OUTPUTS.md:32` “`tables/contig_aliases.tsv`, core `contig_coverage.tsv`” — Core coverage is under `tables/`. — Corrected: “Contig identity and coverage use `tables/contig_aliases.tsv` and core `tables/contig_coverage.tsv`.”
- [F7] `docs/OUTPUTS.md:33` “Child `tables/exon_subtraction_status.tsv`, `exon_subtraction_summary.tsv`, `gene_annotation_coverage.tsv`” — Both companions are under the child's `tables/`. — Corrected: “The child audit tables are `tables/exon_subtraction_status.tsv`, `tables/exon_subtraction_summary.tsv` and `tables/gene_annotation_coverage.tsv`.”
- [F8] `docs/OUTPUTS.md:195` “Every per-locus count measures a record.” — Installed Stellarscope builds 11 loci with `locus`, 10 with `instance_id`, and eight from subfamily GTF; its locus unit follows the selected attribute. — Corrected: “Record-grain counts measure individual records; instance-grain counts measure source groupings.”
- [F9] `docs/OUTPUTS.md:312` “`canonical_family` is unique within `canonical_class`.” — The column pair repeats across names: `LINE/L1` occurs in 149 canonical rows and `LTR/ERVK` in 285. The pair identifies a family shared by several rows. — Corrected: “Canonical family identity is `(canonical_class, canonical_family)`; several names share a family.”
- [F10] `docs/OUTPUTS.md:741` “Generated inputs live under `$TE_TRACKS_REFROOT/fixtures/consumers/`.” — `tests/run.sh` now selects a private temporary directory, or the explicit retained override; this run used `p11_outputs/consumers`. The stated location remains the direct-check fallback. — Corrected: “Consumer suite runs share a private temporary fixture directory; `TE_TRACKS_CONSUMER_FIXTURES` selects a retained directory.”
- [F11] `docs/OUTPUTS.md:792` “MATES works in `$TE_TRACKS_REFROOT/fixtures/consumers_scratch/mates/` and removes that directory.” — The adapter derives its workspace from `FIXTURES.parent`, which follows the private suite directory or override. This run used `p11_outputs/consumers_scratch/mates/` and removed it. — Corrected: “MATES uses `consumers_scratch/mates/` beside the selected fixture directory and removes that workspace.”

- [F12] `docs/OUTPUTS.md:564` “Provisional status is a class property recoverable by joining names to `rmsk_taxonomy` or records to `universe_members`.” — Six names have both `DNA` and `DNA?` raw labels: Eulor5B, Eulor6A, Eutr16, MER124, MER131 and UCON2. MER124 has 247 `DNA` records and two `DNA?` records; the inspected membership rows carry `false` and `true` respectively. A name-only join returns both provisional states and cannot recover an individual record's flag. — Corrected: “Interspersed provisional flags follow each record's raw class and are keyed by `(universe_name, rmsk_record_id)` in `tables/universe_members.tsv.gz`.”

## Unverifiable claims

- [U1] `docs/OUTPUTS.md:39` “The three single-cell and single-nucleus pilots qualify those choices in the consuming toolkit; the bulk pilot qualifies its featureCounts recipe.” — Synthetic fixtures demonstrate the stated test behavior; four completed assay pilots were not demonstrated in this package audit. — Settlement: the consuming toolkit's four pinned pilot runs and qualification records.
- [U2] `docs/OUTPUTS.md:300` “R arrow” reader row, including “`read_delim_arrow(path, delim="\t", col_types=types, quote="", escape_double=FALSE, escape_backslash=FALSE, na=character(), as_data_frame=FALSE)`” and “`read_parquet(path, as_data_frame=FALSE)` retains the embedded typed schema.” — R is installed, but `requireNamespace("arrow", quietly=TRUE)` is false; installs are forbidden. — Settlement: execute both readers with the stated schema in an R Arrow environment. pandas, DuckDB and R data.table were demonstrated on every canonical record.
- [U3] `docs/OUTPUTS.md:304` “Identical input produces byte-identical tables and universe definitions under the same builder and serialization libraries.” — Fixture reproducibility and equal retained inventories provide narrower evidence; a new complete build was forbidden. — Settlement: two independent complete builds with identical inputs and toolchain, followed by byte comparisons.
- [U4] `docs/OUTPUTS.md:444` “Wicker families use the 80-80-80 sequence-similarity convention; this view takes the curated Dfam leaf name as its family label.” — The leaf mapping is verified. The numerical biological convention has no retained primary publication or sequence qualification here, and network access is forbidden. — Settlement: the cited Wicker definition; the table does not measure sequence similarity.
- [U5] `docs/OUTPUTS.md:759` “Adapter supported in isolation; installed package depends on `pkg_resources` (setuptools below 82), absent here” — The pinned MATES adapter works in isolation. The activated environment has no installed MATES distribution and no `pkg_resources`; setuptools is 84.0.0. This does not establish the stated version cutoff or full-package import. — Settlement: qualification with installed MATES and the relevant setuptools versions.
- [U6] `docs/OUTPUTS.md:879` “Verified staging builds install once into `archive/<BUILD_ID>/`; an atomic replacement selects the single `current` symlink.” — Existing selectors and immutable archives were checked; installation and selection were not executed because publication is forbidden. — Settlement: the publication/concurrency fixture or a qualified host publication with an observed atomic replacement.
- [U7] `docs/OUTPUTS.md:944` “`tests/run.sh acceptance --build` builds both families into `$TE_TRACKS_REFROOT/acceptance/`; `tests/run.sh acceptance` checks those archives again.” — The second command was executed; the first is prohibited by this task. — Settlement: an empty acceptance destination, matching cached source pins and a permitted fresh-build run.

- [U8] `docs/OUTPUTS.md:18` “`exports/<ns>/interspersed/full/record.gtf` | `interspersed / full` | TEsingle, TElocal; TEtranscripts; Stellarscope after its boundary gate” — The complete installed TElocal record-index build was stopped while still reading the annotation; its growing feature list makes each new record expensive to insert. Its eleven-record parser/index round trip passes. TEsingle and TEtranscripts completed full-record reads, and Stellarscope's documented boundary gate remains unsupported. — Settlement: a completed TElocal index build from this full record GTF, followed by the installed loader and identity join.

- [U9] `docs/OUTPUTS.md:402` “The census TSV's `rmsk_name` column contains each selected name once; `census_sha256` and `taxonomy_sha256` record the respective input file digests.” — The selected-name census and its retained digest agree. The retained provenance lacks `taxonomy_sha256`; the current fetch implementation writes that additional key, but a live refresh was prohibited. — Settlement: run the current refresh script and independently compare both recorded digests with its exact inputs.

- [U10] `docs/OUTPUTS.md:19` “`exports/<ns>/interspersed/full/record_starsolo.gtf` | `interspersed / full` | STARsolo, cellranger” — Both installed tools consumed the eleven-record profile with a host gene, and every full-export row was independently checked. A complete production profile combined with the full gene annotation was not consumed by these tools in this pass. — Settlement: complete installed STARsolo and cellranger reference construction using the published profile and pinned full gene annotation.

## Numbers recomputed

`C=$TE_TRACKS_REFROOT/te_mm39/build`; `G=$TE_TRACKS_REFROOT/te_mm39_gene/build`. SQL used the record Parquet as `r`, its published interspersed predicate as `i`, instance membership as `m`, and explicit TSV schemas. Counts below come from independent source/table/Matrix Market reads, rather than test summary lines. Headers and declared scalar types were checked in every dictionary, including both legacy schemas. Independent audit programs ran as `python3 "$S/recompute.py"`, `python3 "$S/extra_numbers.py"`, `python3 "$S/export_counts.py"`, `python3 "$S/source_rows.py"`, `python3 "$S/fixture_numbers.py"`, `python3 "$S/geometry.py"` and `python3 "$S/geometry_compare.py"`, with explicit-reader runs `python3 "$S/python_readers.py"` and `Rscript "$S/readers.R"`. Here `S` is the prescribed `p11_outputs` scratch directory; the command column records each computation. The scratch programs and complete logs were removed after recording results, as requested.

| claim | stated | observed | command |
|---|---|---|---|
| Record schema and catalog | 24 columns; 5,320,771 records | exact; both serializations equal | `pq.read_schema`; explicit pandas/DuckDB/R reads; compare all typed rows |
| Primary/browser source mapping | one-to-one, retained source fields | 5,320,771 rows; zero field differences in each source comparison | Stream `.out` against records ordered by `source_row_number`; full join UCSC on five key fields |
| Complete memberships | one per record; single contig | 5,320,771 rows; 4,696,900 instances; zero differences | `EXCEPT ALL` both directions between `m` and record ID pairs; group contigs by instance |
| Multi-record instances, all/interspersed | 445,649 / 434,707 | exact | Join `r` to `m`; `GROUP BY rmsk_instance_id HAVING count(*)>1` |
| Interspersed mixed-name instances / members | 30,569 / 95,830 | exact | Per-instance distinct-name count; sum member counts where greater than one |
| Interspersed mixed-strand instances | 23,244 | exact | `GROUP BY rmsk_instance_id HAVING count(DISTINCT strand)>1` |
| Overlapping records | 429,440 / 5,320,771; 8.0710% | 429,440; 8.0710107614% | Per-contig preceding maximum end and following start |
| LTR-only source groups | 722,280 | exact; all members of these groups are LTR | Group by membership ID; require LTR non-`-int`, exclude any `-int` member |
| LINE/L1 consensus-start 1 | 588 | exact | `count(*) WHERE rmsk_class='LINE' AND rmsk_family='L1' AND consensus_start_1=1` |
| Inverted consensus bounds / overlap flags | two named records / constant false | exact named IDs; 5,320,771 false flags | `WHERE consensus_start_1>consensus_end_1`; group by overlap flag |
| Universe totals | six; compat 3,799,629 | all six summaries match independently evaluated predicates | For each predicate, count records/names/raw triples and sum `length_bp` |
| Canonical taxonomy | 15 columns; 20 double-label interspersed names | exact; family identity repeats (F9) | Read header; recompute resolver votes/medians; group raw labels by name |
| Dfam match census: names / records | exact 1,047 / 2,797,852; parts 147 / 928,528; missing 26 / 38,569 | exact | Group `taxonomy_dfam` by `match_status`; sum record counts joined to `i` |
| Part sets; L2/CR1 sets | 30 three-part, nine two-part, 108 one-part; six named sets | exact, including L2a/L2b/L2c/L2d/L2d2/L3b | Group part counts; select raw families L2/CR1 |
| Exact Dfam codes | 884 leaf, 110 inherited, 53 missing | exact | Join classification paths to coded ancestors; group exact-name statuses |
| Dfam companions and clades | 1,263 models; 300 nodes; 193 coded; 1,278 clade rows; nine multiclade models; 33 primate models / 31 names | exact | Count table rows, nonempty codes and distinct accession/path pairs |
| Class-less / missing ranks | 53 `Unknown` leaves; UCON4 inherits `D` and class II | exact; all five Wicker statuses missing for 53; UCON4 family `Kolobok` mapped, class inherited | Filter `taxonomy_dfam` by leaf/name and inspect every rank/status |
| Core payload and exports | 52 payload files; 27 exports; nine per namespace | exact | Enumerate physical files, excluding three identity controls; read every export |
| Record gene profile | 3,764,949 rows and genes; 59 contigs per namespace | exact in all three | Parse every GTF; count rows, distinct `gene_id`, distinct column 1 |
| BED score clipping | 1,224,713 above 1,000; 32.5% | 1,224,713; 32.5293383788% | `count(*) FILTER(WHERE sw_score>1000)` over `i`; compare BED scores |
| Core registration | 30,119,592 interspersed; 3,152,636 instance aliases; 5,320,771 all-rmsk | exact | Group complete registration TSV by universe/level/grammar; distinct instance aliases |
| Scoped matrix demonstration | 1,000 shared records; 2,000 versus 1,000 joins | exact; totals 1,001,000 versus 500,500 | Independently join 1,000 selected IDs to registration at both scopes |
| Alias/coverage census | 61 aliases; 59 interspersed contigs; zero-interspersed contigs have two/four records | exact | Group `r`/`i` by contig; join aliases and source lengths |
| Child SAFs and registration | 12 files; 3,684,934 / 3,717,740 blocks; 7,369,868 / 7,435,480 registrations | exact in every namespace and both universes | Count every SAF; group complete child registration |
| Child coverage | 38/61 contigs; 23 unannotated; 2,638 unaffected records | exact | Parse retained GTF, normalize aliases, join catalog and statuses |
| Gene/transcript/exon rows; exon union | 78,317 / 278,369 / 1,298,921; 160,549,642 bp | exact; 357,216 merged intervals | Count GTF feature column; `sort`, `bedtools merge`, sum end-start |
| Child status census and conservation | all three summary rows; retained + removed = length | every field matches; zero failures across 5,320,771 records | Independently aggregate statuses by raw universe predicate; complete bedtools subtraction |
| Fixture roster and taxonomy | 11 records, eight names, ten instances; TwoLab vote 2:1 | exact | Count generated records/members; group raw instance votes |
| Fixture FASTA/BAMs | seed 1729; 5,000/3,000 bp; 13/26/26 alignments; 11 molecules; UB/UR 11/12 | exact, including flagged reads and one barcode | Reproduce seeded sequence; inspect every BAM record/tag with pysam |
| IRescue allocations | 2 versus 1+1; 5.5/3.5 and 4.5/4.5; total nine | exact in ARC and OCM | Read fresh executable Matrix Market outputs and feature rosters |
| featureCounts fixture | two fragments per shared feature; one one-base read | exact | Read fresh count TSVs for subfamily, triple and one-base SAFs |
| STARsolo allocations | same-name 1+1; gap 0 TE; overlap 1.5/1.5 and 2.98266/0.0173415; intronic 1 and 0.5/0.5 | exact | Read each fresh `matrix.mtx` and `UniqueAndMult-EM.mtx`, joined to features |
| cellranger and parser gzip | 11 TE genes + host; 3 GB argument; five deterministic gzip headers | exact | Read generated reference GTF and command log; decode gzip MTIME/FNAME bits |
| Legacy dictionary | 15 locus columns; five dimension columns; one-character UCSC IDs | exact in both retained experiments | Read both headers/types; check all lengths and raw ID string lengths |

All 39 measured export digests equal their inventories. BUILD_ID was independently recomputed with canonical JSON; both families retain CATALOG_ID `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e`. Dfam 4.0 comes from the retained snapshot; GENCODE M37 comes from the retained GTF header. The pinned 2018 library identity comes from retained source metadata. Consumer versions and checkout commits were read from executables and pinned checkouts.

## Capabilities demonstrated

| claim | how demonstrated | outcome |
|---|---|---|
| IRescue reads record/subfamily BED | Installed 1.2.0 executable on both fixture profiles; installed `makeRmsk` on both complete UCSC exports; pinned parser and `chrcat` | Both grammars read; fixture identities and allocation match |
| TEsingle reads record/subfamily GTF | Installed `TEtools.TEindex.TEfeatures.build` on both complete exports; pinned parser/filter fixture | 3,764,949 record tuples or 1,220 subfamily tuples; raw-UMI threshold and filters pass |
| TEtranscripts reads both GTFs | Installed `TEToolkit` parser on both complete exports; checkout grouping fixture | 1,220 canonical triples from either production GTF; eight fixture groups |
| TElocal reads GTF-derived index | Installed `TElocal_Toolkit` on fixture GTFs and full subfamily GTF; upstream index/pickle-loader fixture | Fixture round trip preserves 11/eight identities; full record-index completion remains unverified (U8) |
| Stellarscope reads both GTFs and instance attributes | Installed annotation parser plus pinned endpoint fixture | 11 record / ten instance / eight subfamily loci; right-boundary defect reproduces `0,1,1,1`; check exit 3 |
| STARsolo record-as-gene profile | Installed 2.7.11b index and Gene/GeneFull fixture runs | Both matrices, aliases, same-name separation, gap and EM observations reproduced; complete GTF contracts checked separately; full production binding unverified (U10) |
| cellranger profile | Installed 10.1.0 `mkgtf` and `mkref --nthreads=1 --memgb=3` | All 11 TE aliases plus host retained; STAR index created for fixture; full production binding unverified (U10) |
| MATES adapter | Pinned 0.1.8 source functions, eight-column paired files, filters and companion-name cases | Isolated adapter passes; **no installed MATES package** for full-tool demonstration (U5) |
| featureCounts SAF binding | Installed 2.1.1 with `-F SAF -s 0` on all six core and all 12 child SAFs, each with a matching-namespace probe BAM; counting fixtures | All 18 production reads exit 0; fixture feature identity and inclusive endpoint counts pass |
| bedtools binding | Installed 2.31.1 intersects complete UCSC record/family/catalog BEDs; fixture boundary/strand checks | Names retained; half-open and strand behavior pass |
| 14761 ATAC route / SAF column reader | Complete catalog BED and registrations checked; generic bedtools read; SAF rows and joins parsed | Artifact contracts demonstrated; the ATAC route is a consuming project, with no standalone executable to qualify here |
| samtools | Installed 1.21 fixture integrity checks; independent pysam inspection | Sort/index, alignment counts, strands, names and tags agree |
| pandas / DuckDB / R data.table | Documented explicit-schema reads of all 5,320,771 records | All succeed; text instance IDs and declared numeric/boolean types preserved; R Arrow unavailable (U2) |
| Exon subtraction | Independently parse every retained GTF exon; full-catalog `bedtools merge` and `subtract`; compare all statuses and four UCSC SAF multisets | Zero differences; all 5,179,754 catalog blocks checked; minimum retained length one; namespace comparisons cover all 12 SAFs |
| Input and policy refusals | Supplemental parser, record, taxonomy, export, gene-geometry and child-identity fixtures in private scratch | Checks 10, 23, 42, 71, 81 and 82 all exit 0; malformed identities, reserved tokens, unmapped contigs, incompatible policy values and changed SAF content/order are refused |
| Preflight and verifier content gates | Complete acceptance contracts, including BAM/FAI/sizes cases, namespace identity and child registration-to-SAF checks | All eleven acceptance checks pass; suite exit 0 |
| Source refresh CLI | CLI options and retained census digest checked; fetch implementation inspected | CLI arguments exposed; retained census digest agrees; refreshed provenance-writing behavior remains unverified (U9) |

The activated consumer suite exited 0: 15 checks passed and the documented Stellarscope boundary check was unsupported. Complete annotation reads above are separate from fixture counting evidence. Whole-genome STAR/cellranger counting and assay pilot outcomes were not inferred from tiny fixtures.

## Cross-scope contradictions

| your path | other path | the contradiction |
|---|---|---|
| `docs/OUTPUTS.md:741`, `:792` | `README.md:107` | OUTPUTS names fixed reference-root fixture/work directories; README describes private suite fixtures and the retained override, matching the runner. |
| `docs/OUTPUTS.md:886`, `:939` | `docs/DECISIONS.md:98` | OUTPUTS declares context `not_computed` with a scaling gate; DECISIONS says the package presently publishes the transcript relation. The current child has no such relation. DECISIONS later also states the deferral. |

## Closing verification

These were the last artifact checks. Targets below are relative to `$TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`.

Each build ran `python3 src/99_verify.py <build-directory>`. Archives supplied `--root <pubroot-or-acceptance-root>`; the development child supplied `--parent-dir "$TE_TRACKS_REFROOT/te_mm39/build"`. Each selector ran `python3 src/release.py verify-current --root <publication-root> --family <family>`.

| command | target under reference root | exit |
|---|---|---:|
| `99_verify.py` | `acceptance/te_mm39/archive/5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813` | 0 |
| `99_verify.py` | `acceptance/te_mm39_gene/archive/198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1` | 0 |
| `99_verify.py` | `pubroot/te_mm39/archive/5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813` | 0 |
| `99_verify.py` | `pubroot/te_mm39/archive/763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c` | 0 |
| `99_verify.py` | `pubroot/te_mm39/archive/9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d` | 0 |
| `99_verify.py` | `pubroot/te_mm39_gene/archive/1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b` | 0 |
| `99_verify.py` | `pubroot/te_mm39_gene/archive/198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1` | 0 |
| `99_verify.py` | `pubroot/te_mm39_gene/archive/693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0` | 0 |
| `99_verify.py` | `te_mm39/build` | 0 |
| `99_verify.py` | `te_mm39_gene/build` | 0 |
| `release.py verify-current` | `pubroot/te_mm39` | 0 |
| `release.py verify-current` | `pubroot/te_mm39_gene` | 0 |
| `release.py verify-current` | `acceptance/te_mm39` | 0 |
| `release.py verify-current` | `acceptance/te_mm39_gene` | 0 |

All ten build verifiers and all four current-selector checks exited 0. Complete stdout/stderr and exit statuses were captured before cleanup. The prescribed private scratch directory was removed with Python `shutil.rmtree`. This validation wrote only the requested review in the package; it performed no rebuild, publication, installation, network access or git write.
