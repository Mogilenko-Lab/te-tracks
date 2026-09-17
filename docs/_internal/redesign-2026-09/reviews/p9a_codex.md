# Phase 9a review (codex gpt-6-astra)
Verdict: BLOCKING

## Blocking

- [B1] `tests/lib/consumers.py:558-562` silently discards matrix rows and duplicate feature IDs before checking conservation — replaying the real IRescue outputs with an extra 100-count matrix row passed; adding a duplicate registered feature row with 100 counts also passed because `dict(zip(...))` overwrites it. Wrong identity and a +1 change to an existing count correctly failed. This misses deliverable 6's roster/molecule conservation — assert both matrix dimensions against unique feature/barcode rosters and check the original matrix total before constructing the dictionary; add these negative cases.
- [B2] `tests/lib/consumers.py:751-768` permits STARsolo support on a TE absent from the overlap molecules — replaying the real Gene output as HostGene=1.5, SubB=1.2, Edge=0.3 passed, although `tests/fixtures/consumers/starsolo_molecules.tsv:5-7` supports only HostGene/SubB. Removing 0.3 without redistributing it failed. This misses deliverable 2's support guarantee — require zero EM support outside the case's allowed genes and conserve the total within that set, keeping the host/TE split observational.

## Advisory

- [A1] `tests/checks/core/33_taxonomy_dfam_view.py:137-147` checks codes and the aggregate class-status census, but omits coded rows' derived rank values/statuses — changing AmnHarb1's materialized `wicker_class` to `WRONG CLASS` in a scratch copy still returned 0. My independent derivation matches the current tables. Compare every derived rank/status per name and add a materialized-table mutation case before 9b.
- [A2] `src/lib/manifest.py:600-611` admits more source layouts than the reported legacy/new cases — a resealed fixture retaining `dfam_snapshot` while removing `rmsk_out` from `identity.build_sources` verified with four roles; removing `chromAlias` failed. This hybrid omits one of the new build's five promised roles. The primary bytes remain bound through `catalog.sources`, so this is an admission-policy advisory: enumerate the supported legacy and tracked-source layouts explicitly. D2's actual three-role archive and five-role build both verify.
- [A3] `docs/OUTPUTS.md:81` describes the LTR-only predicate without naming `all_rmsk`; `docs/OUTPUTS.md:605` still labels consumer registration by `(feature_level, key_grammar)` without a table-wide universe/variant default. The 722,280 result happens to agree in both universes. Add the universe to that measurement and full scope/default to the consumer table. The matrix-binding sentence at line 567 is correct; I found no other public sentence prescribing a pair-only matrix join.
- [A4] `src/lib/contigs.py:134` says “eight UCSC inventory entries”; the effective roster contains nine. D6 is a pre-existing, reported diagnostic defect outside the touch list; correct the message in a separately scoped change.

## Acceptance re-run

- Profile and binding: independent recomputation used scratch Python/DuckDB code without production derivation helpers. For every namespace, all 3,764,949 GTF rows, distinct aliases, 59 contigs, exon features, twelve ordered attributes, fixed fields and catalog coordinate round-trips matched; full outer joins to `(interspersed, full, record, record_alias)` registration had zero unmatched rows and no duplicates. Bytes were UCSC 1,616,329,134; Ensembl 1,604,983,782; GENCODE 1,616,260,404. Core checks 40/61 cover every emitted catalog-derived field; the archive verifier alone checks hashes rather than that semantic equality. Independent binding joins gave 2,000 rows/1,001,000 counts versus 1,000/500,500.
- Dfam: independent reconstruction matched every name and every projected column: exact/parts/missing 1,047/147/26; records 2,797,852/928,528/38,569; part sizes 3/2/1 = 30/9/108; L2a/L2b/L2c/L2d/L2d2/L3b; models/nodes/coded nodes 1,263/300/193; multi-clade models 9; primate models/names 33/31; exact leaf/inherited/missing codes 884/110/53. Companions exactly reconstruct selected models/clades in both directions; the 26 model-less names require a left join, and 252 complete-tree nodes have no direct model assignment. Line counts are quoted below. D1 follows authoritative plan 19: all five Wicker ranks are missing for the 53 Unknown names. D3 is justified: the fetch census totals 3,760,582, short 4,367 across exactly 20 multi-label names; published weights equal catalog counts. A repository-wide search found only metadata summaries and checks using `model_length_sum_bp`, with no full-length denominator.
- Records and instances: independent catalog grouping/interval sweeps reproduced D4: `all_rmsk` multi-record instances 445,649, overlapping records 429,440/5,320,771 = 8.07101076%, LTR-only instances 722,280; `interspersed` multi-record/mixed-name/mixed-strand instances 434,707/30,569/23,244, overlapping records 394,785/3,764,949 = 10.48579941%; complete-catalog mixed-name/mixed-strand instances 30,699/23,245; raw LINE/L1 model-base-1 records 588; true overlap flags 0. OUTPUTS defines records, instances, insertions, per-record locus counts and annotation limits. Scope clarification is A3.
- Source, identity and prose: the tracked-input candidate is eligible through `.gitignore:21`; its bytes and retained source copy match the config SHA-256 `ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f`. Independently hashing the domain-prefixed canonical identity JSON reproduced both reported BUILD_IDs and CATALOG_ID; scratch/archive identities agree, catalog sources contain only `rmsk_out`, inventories/contracts are 51/27 and legacy 43/24. All deliverable paths are present. Child CATALOG_ID and the previous child's subtraction summary are byte-identical. Size totals match the report. Public additions/comments contain no gratuitous contrastive negation or implementation-history chatter.
- Consumers and remaining deviations: independent reads of the generated matrices reproduced IRescue 5.5/3.5 and 4.5/4.5 in both layouts; STAR Gene 1.5/1.5 and GeneFull 2.98266/0.0173415, two separate same-name genes, zero gap TE support and intronic Gene/GeneFull support. Cellranger retained 11 alias genes plus the host and a 10,441-byte STAR Genome file. Required parser check 17 and absent-binary exits are confirmed below. D8 is justified: my additional `mkref --memgb=2` attempt exited 1 with “STAR requires at least 3 GB of memory when aligning reads to your reference.”; the 3 GB gate passed. D7 is judged from the frozen rerun below; the reported transient live-edit failure leaves no reproduced runner defect. The interrupted-staging refusal/removal fixture is present at `tests/checks/core/72_publication_cases.py:96-106`. Rebuild/publication commands were excluded by this review's explicit read-only instruction; all applicable acceptance commands were rerun.
```text
$ export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1; B="$TE_TRACKS_REFROOT/te_mm39/build"; C="$TE_TRACKS_REFROOT/te_mm39_gene/build"; for f in build.sh lib/common.sh src/*.sh src/gene/*.sh tests/run.sh tests/checks/consumers/*.sh; do bash -n "$f" && echo "syntax ok $f"; done; sha256sum data/dfam/dfam_interspersed_mm39_snapshot.json.gz; cat "$B/BUILD_ID" "$B/CATALOG_ID"; python3 -c "import json;i=json.load(open('$B/MANIFEST.json'))['identity'];print(len(i['inventory']),len(i['export_contracts']),sorted(i['build_sources']))"
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok src/10_build_records.sh
syntax ok src/15_build_universes.sh
syntax ok src/20_build_taxonomy.sh
syntax ok src/25_build_dfam.sh
syntax ok src/30_build_exports.sh
syntax ok src/35_build_namespaces.sh
syntax ok src/gene/00_fetch_gene_sources.sh
syntax ok src/gene/10_copy_parent_inputs.sh
syntax ok src/gene/50_build_exon_subtracted.sh
syntax ok tests/run.sh
syntax ok tests/checks/consumers/20_irescue_exec.sh
syntax ok tests/checks/consumers/21_featurecounts_exec.sh
syntax ok tests/checks/consumers/22_bedtools_exec.required.sh
syntax ok tests/checks/consumers/23_samtools_fixture_integrity.required.sh
syntax ok tests/checks/consumers/24_starsolo_exec.sh
syntax ok tests/checks/consumers/25_cellranger_mkref.sh
ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f  data/dfam/dfam_interspersed_mm39_snapshot.json.gz
763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
51 27 ['chromAlias', 'chrom_sizes', 'dfam_snapshot', 'rmsk_out', 'rmsk_table']
$ wc -l "$B"/exports/*/interspersed/full/record_starsolo.gtf; cut -f1 "$B/exports/ucsc/interspersed/full/record_starsolo.gtf" | sort -u | wc -l; head -2 "$B/exports/ucsc/interspersed/full/record_starsolo.gtf"; head -3 "$B/tables/taxonomy_dfam.tsv" | cut -c1-400; wc -l "$B"/tables/taxonomy_dfam*.tsv "$B"/tables/dfam_*.tsv; cut -f7 "$B/tables/taxonomy_dfam.tsv" | tail -n +2 | sort | uniq -c
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ensembl/interspersed/full/record_starsolo.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/gencode/interspersed/full/record_starsolo.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/record_starsolo.gtf
  11294847 total
59
chr1	te-tracks	exon	3050294	3050775	3667	+	.	gene_id "R|mm39|L1MdA_VI|chr1|3050294|3050775|+"; transcript_id "R|mm39|L1MdA_VI|chr1|3050294|3050775|+"; gene_name "L1MdA_VI"; gene_type "transposable_element"; locus "R|mm39|L1MdA_VI|chr1|3050294|3050775|+"; rmsk_name "L1MdA_VI"; family_id "L1"; class_id "LINE"; rmsk_family "L1"; rmsk_class "LINE"; instance_id "I|mm39|1"; rmsk_record_id "L1MdA_VI|chr1:3050294-3050775|+";
chr1	te-tracks	exon	3051045	3051146	242	-	.	gene_id "R|mm39|ID2|chr1|3051045|3051146|-"; transcript_id "R|mm39|ID2|chr1|3051045|3051146|-"; gene_name "ID2"; gene_type "transposable_element"; locus "R|mm39|ID2|chr1|3051045|3051146|-"; rmsk_name "ID2"; family_id "ID"; class_id "SINE"; rmsk_family "ID"; rmsk_class "SINE"; instance_id "I|mm39|2"; rmsk_record_id "ID2|chr1:3051045-3051146|-";
rmsk_name	rmsk_class	rmsk_family	canonical_class	canonical_family	record_count	match_status	dfam_accessions	dfam_model_names	dfam_model_versions	dfam_model_lengths_bp	available_part_count	part_roles_present	model_length_sum_bp	classification_path	classification_leaf	clades	clade_leaves	clade_compatibility	dfam_release	wicker_code	wicker_code_uncertain	wicker_class	wicker_class_status	wicker_subcla
AmnHarb1	DNA	PIF-Harbinger	DNA	PIF-Harbinger	115	exact	DF000001731	AmnHarb1	1	1444	0		1444	root;Interspersed_Repeat;Transposable_Element;Class_II_DNA_Transposition;Transposase;PIF-Harbinger;Harbinger	Harbinger	root;cellular organisms;Eukaryota;Opisthokonta;Metazoa;Eumetazoa;Bilateria;Deuterostomia;Chordata;Craniata;Vertebrata;Gnathostomata;Teleostomi;Euteleostomi;Sarcopterygii;Dipnotetrapodomorpha
AmnL2-1	LINE	L2	LINE	L2	1311	exact	DF000001732	AmnL2-1	1	2613	0		2613	root;Interspersed_Repeat;Transposable_Element;Class_I_Retrotransposition;LINE;Group-II;Group-2;R1-like;CR1-group;L2-group;L2	L2	root;cellular organisms;Eukaryota;Opisthokonta;Metazoa;Eumetazoa;Bilateria;Deuterostomia;Chordata;Craniata;Vertebrata;Gnathostomata;Teleostomi;Euteleostomi;Sarcopterygii;Dipnotetrapodomorpha;Tetrapoda;A
   1264 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_dfam_models.tsv
   1221 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/taxonomy_dfam.tsv
    301 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/dfam_lineage_nodes.tsv
   1279 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/dfam_model_clades.tsv
   4065 total
   1047 exact
     26 missing
    147 part_model_set
$ cat "$C/tables/exon_subtraction_summary.tsv"; cmp "$C/CATALOG_ID" "$B/CATALOG_ID" && echo 'child CATALOG_ID equal'; cmp "$C/tables/exon_subtraction_summary.tsv" "$TE_TRACKS_REFROOT/pubroot/te_mm39_gene/archive/1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b/tables/exon_subtraction_summary.tsv" && echo 'child exon-subtraction summary unchanged'; ls "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive" "$TE_TRACKS_REFROOT/pubroot/te_mm39_gene/archive"; du -sb "$B"; python3 -c "import json;inv=json.load(open('$B/MANIFEST.json'))['identity']['inventory'];print('payload files',len(inv),'bytes',sum(e['bytes'] for e in inv))"
universe_name	records	unchanged	trimmed	split	fully_subtracted	retained_records	blocks	retained_bp	removed_bp	records_on_unannotated_contigs
all_rmsk	5320771	5086684	61378	15495	157214	5163557	5179754	1172003155	29569849	2638
interspersed	3764949	3600721	52703	15406	96119	3668830	3684934	1090369890	26235918	1612
compat_tetranscripts_mm39	3799629	3633401	52842	15399	97987	3701642	3717740	1094973237	26503064	1754
child CATALOG_ID equal
child exon-subtraction summary unchanged
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive:
763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d

/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39_gene/archive:
1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b
693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
15301655992	/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build
payload files 51 bytes 15301535164
$ python3 src/99_verify.py "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive/9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d"; echo "exit=$?"
ok build paths: regular files and directories
ok inventory: 43 files, exact paths, bytes and sha256
ok BUILD_ID: 9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d
ok CATALOG_ID: 90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e
ok catalog, source_run scope, assembly, contig digest and taxonomy rule
ok universe definitions and predicate grammar
ok export contracts: 24 namespace paths
ok export rows and sha256: exports/ensembl/all_rmsk/full/record.bed
ok export rows and sha256: exports/ensembl/interspersed/full/family.bed
ok export rows and sha256: exports/ensembl/interspersed/full/record.bed
ok export rows and sha256: exports/ensembl/interspersed/full/record.gtf
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.bed
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/ensembl/interspersed/full/subfamily.saf
ok export rows and sha256: exports/ensembl/interspersed/full/taxonomy_triple.saf
ok export rows and sha256: exports/gencode/all_rmsk/full/record.bed
ok export rows and sha256: exports/gencode/interspersed/full/family.bed
ok export rows and sha256: exports/gencode/interspersed/full/record.bed
ok export rows and sha256: exports/gencode/interspersed/full/record.gtf
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.bed
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/gencode/interspersed/full/subfamily.saf
ok export rows and sha256: exports/gencode/interspersed/full/taxonomy_triple.saf
ok export rows and sha256: exports/ucsc/all_rmsk/full/record.bed
ok export rows and sha256: exports/ucsc/interspersed/full/family.bed
ok export rows and sha256: exports/ucsc/interspersed/full/record.bed
ok export rows and sha256: exports/ucsc/interspersed/full/record.gtf
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.bed
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.gtf
ok export rows and sha256: exports/ucsc/interspersed/full/subfamily.saf
ok export rows and sha256: exports/ucsc/interspersed/full/taxonomy_triple.saf
ok records schema: 24 required typed columns
ok record identities: 5320771 unique keys and text instance ids
ok record bounds: source/mm39.chrom.sizes
ok universe_summary all_rmsk: 5320771 records
verified 9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d
exit=0
$ python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39; echo "exit=$?"; python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39_gene; echo "exit=$?"
763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c
exit=0
693ba1aa15e85d13b9dafd046962e6f07a0b3aad476b82041e4eabc10e1a65e0
exit=0
$ export TMPDIR=/workspaces/Meta-Aging/_scratch/te-tracks-audit/p9a-review/tmp TE_TRACKS_CONSUMER_FIXTURES=/workspaces/Meta-Aging/_scratch/te-tracks-audit/p9a-review/consumers; tests/run.sh core; echo "exit=$?"
pass  01_runner_selftest.sh  runner statuses, required checks, diagnostics, dangling symlinks and usage exits pass
pass  10_rmsk_out_parser.py  6 expected records; plain/gzip, signed consensus, ID tokens, malformed/unreadable input and ID statistics pass
pass  11_source_qualification.sh  13 summary metrics and 10 field disagreements verified; reports identical; four source md5s and declared assembly match config pins
pass  20_records_schema.py  5320771 records; 24 typed columns; all typed rows equal; identities and bounds pass
pass  21_instances.py  4696900 instances; one instance per record; single contig; sizes 1=4251251 2=338697 3+=106952
pass  22_universes.py  six universe summaries and every membership match; 17 classes; 3 collision pairs; 20 multi-label names / 6517 records
pass  23_records_fixtures.py  hand-authored records, collisions, text IDs, signed fields, instances, bounds, joins, class sets and tRNA-family rules pass
pass  30_taxonomy_canonical.py  18484 names; all 15 columns recomputed exactly; 20 report rows equal the multi-label subset; census matches; minimum plurality share 0.840 MER63C
pass  31_taxonomy_dfam_agreement.py  report names missing from snapshot: []
pass  32_taxonomy_rule_fixtures.py  31 rule cases; permutations, rank shares, instance weighting, rounded median, deterministic builds, input gates and canonical rollups pass
pass  33_taxonomy_dfam_view.py  Dfam census and catalog joins pass; {"coded_nodes": 193, "exact_names": 1047, "exact_records": 2797852, "exact_wicker_inherited": 110, "exact_wicker_mapped": 884, "exact_wicker_missing": 53, "l2_cr1_part_sets": 6, "lineage_nodes": 300, "missing_names": 26, "missing_records": 38569, "model_rows": 1263, "multi_clade_models": 9, "names": 1220, "part_model_set_names": 147, "part_model_set_records": 928528, "part_sets_1": 108, "part_sets_2": 9, "part_sets_3": 30, "primate_branch_models": 33, "primate_branch_names": 31, "records": 3764949}
pass  34_dfam_rule_fixtures.py  14 authored Dfam cases: codes, inherited ranks, uncertainty, subclasses, parts, clades and named disagreement pass
pass  40_exports_shape.py  eight exports: 3764949 rows each; subfamilies=1220 families=49 taxonomy_triples=1220; coordinates and identifiers pass
pass  41_export_registration.py  registrations: interspersed=30119592 all_rmsk=5320771; eight interspersed ID spellings; instances=3152636; 27 inventory hashes, feature sets and GTF tuple/instance joins pass; three record grammars; count 7 stays 7 at record, subfamily and family levels
pass  42_exports_fixtures.py  nine hand-authored exports and 46 registration rows; eight-export/40-row interspersed job; membership selection, unresolved ranks, coordinate duplicates, shared instances, deterministic rebuild, universe and identifier gates pass
pass  43_matrix_binding.py  1000 shared records: pair-only join=2000 rows/1001000 counts; four-field join=1000 rows/500500 counts
pass  60_contig_aliases.py  61 injective aliases and FASTA names/lengths; catalog=5320771 interspersed=3764949; all contigs carry catalog records; chr4_JH584295v1_random and chrM carry 2 and 4 catalog records, zero interspersed records
pass  61_namespace_exports.py  27 sorted exports and SHA-256 digests; 18 complete renamed files regenerated; interspersed=3764949 all_rmsk=5320771 per namespace; registrations=30119592+5320771
pass  62_preflight.sh  104 preflight cases; both universes, three namespaces, BED/GTF/SAF and sizes/FAI/BAM; covered=0, export-only=2, empty/shared-length/input errors=1; exact reports and enclosing build aliases pass
pass  70_manifest_identity.py  BUILD_ID=763815187e47d13bd397475e4cb8de99c3a793a2039d1d36506de805c3fddd1c CATALOG_ID=90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e; 51 payloads; identity mutations pass
pass  71_verify_build.py  real build verifies unchanged; fixture stray authoring payload, flipped byte, extra file, unpublished taxonomy rule and export roster mismatch fail with named discrepancies; fixture cases=3.563s
pass  72_publication_cases.py  identical and changed builds, export-roster evolution (4 archives), failed verification and interrupted staging cleanup, concurrent installs/selects (5 archives), old IDs, forged ID, corrupt current, selector and root cases, occupied targets, symlinks and 0444/0555 modes pass
pass  80_exon_subtraction.py  5320771 records conserve bases; registered blocks ordered, disjoint and contained; 200000-record sample exon-disjoint; summary census, 14805348 registrations, 12 SAF row multisets and sort orders, independent GTF coverage 38/61 with 2638 unannotated records pass
pass  81_exon_subtraction_fixtures.py  15 geometry cases, 12 SAFs, 96 registrations, annotation coverage, duplicate invariance and named refusals pass
pass  82_child_identity.py  child identity fields, inherited pins, all policy/GTF/roster/parent mutations, dependency and payload refusals, SAF content and order refusals, parent/build-dir symlink refusals with trailing slashes, CLI usage gates pass
pass  83_child_publication_cases.sh  child install/select/verify-current require present, verified parent; repeated publication converges; archive resolution, preserved selection, immutable modes and earlier core selection pass
checks=26 pass=26 fail=0 unsupported=0
exit=0
$ tests/run.sh consumers; echo "exit=$?"
pass  00_tool_inventory.required.py  supported tool_inventory reporting-only; irescue=absent; featureCounts=absent; stellarscope=absent; TEsingle=absent; TEcount=absent; TElocal=absent; bedtools=bedtools v2.31.1; samtools=samtools 1.21; STAR=absent; cellranger=absent
pass  10_irescue_parser.required.py  supported irescue 1.2.0 (v1.2.0-20-g26f36fb) checkout parser; record=11, subfamily=8; comma splits one name and exporter rejects it
unsupported  11_stellarscope_parser.py  unsupported: stellarscope right-boundary overlap defect, observed 0,1,1,1 expected 0,1,1,0; stellarscope 1.5 (1.5) checkout parser
pass  12_tesingle_parser.required.py  supported TEsingle 1.0 (1.0-8-g655f127) checkout parser; record=11, subfamily=8; 999 distinct UR dropped, 1000 kept; duplicate/QC-fail reads skipped
pass  13_tetranscripts_telocal_parser.required.py  supported TEtranscripts/TElocal 2.2.4 (2.2.4-13-ge7f9b93)/1.1.3 (1.1.3-4-g1a168c2) checkout parsers; TEtranscripts=8 groups; TElocal locInd record=11, subfamily=8
pass  14_mates_parser.required.py  supported MATES 0.1.8 (v0.1.8-9-g87c1218) checkout adapter; eight-column pair; underscore stem; ?/Unknown model groups dropped
pass  15_irescue_chrcat.py  supported irescue 1.2.0 (v1.2.0-20-g26f36fb) checkout chrcat; chrcat emitted record=11, subfamily=8 identities; mappings and feature index agree
pass  16_family_triple_readers.required.py  supported family/triple readers bedtools v2.31.1; Python SAF column reader; family buckets and 8 SAF GeneIDs registered; three TwoLab rows share one triple
pass  17_starsolo_profile.required.py  supported STARsolo/cellranger record profile parser; 12 ordered attributes; 11 record genes; same-name separation, registration, namespaces, one-base endpoints and host collisions pass
unsupported  20_irescue_exec.sh  unsupported: irescue absent
unsupported  21_featurecounts_exec.sh  unsupported: featureCounts absent
pass  22_bedtools_exec.required.sh  supported bedtools v2.31.1; duplicate names, half-open boundaries and -s/-S pass
pass  23_samtools_fixture_integrity.required.sh  supported samtools 1.21; 11 sorted, indexed BAMs; ARC=13 OCM=26 bulk=26 alignments, 11 molecules each; tagged main UB=11 UR=12; reverse strands and duplicate/QC-fail flags pass
unsupported  24_starsolo_exec.sh  unsupported: STAR absent
unsupported  25_cellranger_mkref.sh  unsupported: cellranger absent
pass  30_registration_duckdb.py  DuckDB registration targets and hand-computed totals pass; count 7 stays 7 at record, subfamily and family levels
checks=16 pass=11 fail=0 unsupported=5
exit=0
$ source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh; tests/run.sh consumers; echo "exit=$?"
pass  00_tool_inventory.required.py  supported tool_inventory reporting-only; irescue=IRescue 1.2.0; featureCounts=featureCounts v2.1.1; stellarscope=1.5; TEsingle=TEsingle 1.0; TEcount=TEcount 2.2.4; TElocal=TElocal 1.1.3; bedtools=bedtools v2.31.1; samtools=samtools 1.21; STAR=2.7.11b; cellranger=cellranger 10.1.0
pass  10_irescue_parser.required.py  supported irescue 1.2.0 (v1.2.0-20-g26f36fb) checkout parser; record=11, subfamily=8; comma splits one name and exporter rejects it
unsupported  11_stellarscope_parser.py  unsupported: stellarscope right-boundary overlap defect, observed 0,1,1,1 expected 0,1,1,0; stellarscope 1.5 (1.5) checkout parser
pass  12_tesingle_parser.required.py  supported TEsingle 1.0 (1.0-8-g655f127) checkout parser; record=11, subfamily=8; 999 distinct UR dropped, 1000 kept; duplicate/QC-fail reads skipped
pass  13_tetranscripts_telocal_parser.required.py  supported TEtranscripts/TElocal 2.2.4 (2.2.4-13-ge7f9b93)/1.1.3 (1.1.3-4-g1a168c2) checkout parsers; TEtranscripts=8 groups; TElocal locInd record=11, subfamily=8
pass  14_mates_parser.required.py  supported MATES 0.1.8 (v0.1.8-9-g87c1218) checkout adapter; eight-column pair; underscore stem; ?/Unknown model groups dropped
pass  15_irescue_chrcat.py  supported irescue 1.2.0 (v1.2.0-20-g26f36fb) checkout chrcat; chrcat emitted record=11, subfamily=8 identities; mappings and feature index agree
pass  16_family_triple_readers.required.py  supported family/triple readers bedtools v2.31.1; Python SAF column reader; family buckets and 8 SAF GeneIDs registered; three TwoLab rows share one triple
pass  17_starsolo_profile.required.py  supported STARsolo/cellranger record profile parser; 12 ordered attributes; 11 record genes; same-name separation, registration, namespaces, one-base endpoints and host collisions pass
pass  20_irescue_exec.sh  supported irescue IRescue 1.2.0; SubA=2, records=1+1; {"arc_3_3": {"A": 4.5, "B": 4.5, "EM_x": 1.5}, "arc_4_2": {"A": 5.5, "B": 3.5, "EM_x": 1.5}, "ocm_3_3": {"A": 4.5, "B": 4.5, "EM_x": 1.5}, "ocm_4_2": {"A": 5.5, "B": 3.5, "EM_x": 1.5}}
pass  21_featurecounts_exec.sh  supported featureCounts v2.1.1; -s 0; two fragments per subfamily and triple SAF feature; inclusive one-base overlap
pass  22_bedtools_exec.required.sh  supported bedtools v2.31.1; duplicate names, half-open boundaries and -s/-S pass
pass  23_samtools_fixture_integrity.required.sh  supported samtools 1.21; 11 sorted, indexed BAMs; ARC=13 OCM=26 bulk=26 alignments, 11 molecules each; tagged main UB=11 UR=12; reverse strands and duplicate/QC-fail flags pass
pass  24_starsolo_exec.sh  supported STAR 2.7.11b; record gene identities and molecule conservation pass; {"gap": {"Gene": {"EM": {}, "unique": {}}, "GeneFull": {"EM": {"HostGene": 1.0}, "unique": {"HostGene": 1.0}}}, "intronic": {"Gene": {"EM": {"R|mm39|SubB-int|chrA|3201|3400|+": 1.0}, "unique": {"R|mm39|SubB-int|chrA|3201|3400|+": 1.0}}, "GeneFull": {"EM": {"HostGene": 0.5, "R|mm39|SubB-int|chrA|3201|3400|+": 0.5}, "unique": {}}}, "overlap": {"Gene": {"EM": {"HostGene": 1.5, "R|mm39|SubB|chrA|3001|3100|+": 1.5}, "unique": {"HostGene": 1.0, "R|mm39|SubB|chrA|3001|3100|+": 1.0}}, "GeneFull": {"EM": {"HostGene": 2.98266, "R|mm39|SubB|chrA|3001|3100|+": 0.0173415}, "unique": {"HostGene": 1.0}}}, "same_name": {"Gene": {"EM": {"R|mm39|SubA|chrA|1001|1200|+": 1.0, "R|mm39|SubA|chrA|2001|2200|-": 1.0}, "unique": {"R|mm39|SubA|chrA|1001|1200|+": 1.0, "R|mm39|SubA|chrA|2001|2200|-": 1.0}}, "GeneFull": {"EM": {"R|mm39|SubA|chrA|1001|1200|+": 1.0, "R|mm39|SubA|chrA|2001|2200|-": 1.0}, "unique": {"R|mm39|SubA|chrA|1001|1200|+": 1.0, "R|mm39|SubA|chrA|2001|2200|-": 1.0}}}}
pass  25_cellranger_mkref.sh  supported cellranger 10.1.0; mkgtf retains TE and host biotypes; mkref keeps 11 alias genes and its STAR index
pass  30_registration_duckdb.py  DuckDB registration targets and hand-computed totals pass; count 7 stays 7 at record, subfamily and family levels
checks=16 pass=15 fail=0 unsupported=1
exit=0
```

## Scope check

Implementation baseline: `git status --short` has 38 entries; expanding `data/` gives 40 implementation files (22 modified, 18 untracked). `git diff HEAD --stat`: 22 files changed, 689 insertions(+), 90 deletions(-). Branch `redesign-2026-09`; `git diff --check` passed. The 40 input-file digests stayed unchanged during final review assembly.
D5 is justified: `tests/checks/consumers/17_starsolo_profile.required.py` is the sole addition outside the enumerated touch list and is explicitly required by prompt deliverable 2. DECISIONS edits are confined to section 15; every other implementation change is allowed. This review is the only repository file written by this reviewer; temporary review artifacts were removed with `shutil.rmtree`.
