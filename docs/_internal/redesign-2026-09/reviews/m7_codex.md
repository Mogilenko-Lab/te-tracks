# Milestone 7 review: publication seam (codex gpt-6-astra)

Verdict: PASS WITH ADVISORIES
## Blocking

- None. The exercised consumer, transfer and roster-evolution routes preserve the published identity and keys.

## Advisory

- [A1] `src/lib/manifest.py:274`, `:281`, `:409`, `src/release.py:56`, `:125`: phase 8 needs family-aware identity and dependency verification. Today identity requires the core family and null parents; the child probe fails with the messages below. Validate both parent IDs as full digests, resolve the exact parent archive, verify its family/assembly and recomputed BUILD_ID/CATALOG_ID against the child pins, and check dependency availability before installation/selection/verify-current. Consumers obtain the parent from the child's declaration; `docs/RELEASES.md:137` already orders parent transfer first. Preserve the published core verification branch. This is scheduled phase 8 work.
- [A2] `src/release.py:24`, `:120`, `build.sh:53`, `src/lib/manifest.py:30`, `:139`, `:161`, `:258`, `:326`, `bin/te-tracks-preflight:36`: publication's regex already admits `te_mm39_gene`, and staging is already per family, but the builder derives family from GENOME; SPECIES admits only assembly `mm39`. Keep family and assembly separate; `GENOME=mm39_gene` currently fails species admission. Phase 8 must parameterize the core source-role set, local catalog-table requirements, record checks and `full` export roster according to the ruled child topology. `release.py` itself has no literal core-family restriction; its verifier needs family/dependency context. Give the child its own direct `.staging/<unique>` and inventoried, parent-pinned `tables/contig_aliases.tsv` (or an explicitly designed pinned lookup); preflight currently walks enclosing directories and cannot discover a sibling parent's aliases. `src/lib/contigs.py:126` also assumes the core UCSC roster and catalog inputs.
- [A3] `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/19_phase9_acceptance_park.md:12`, `src/lib/manifest.py:93`: the planned literal `99_verify.py .../current` invocation refuses the selector symlink as `invalid build directory`. Phase 9's runbook should use `release.py verify-current`, or resolve `current` once and pass that archive path to `99_verify.py`, as the consumer contract at `docs/RELEASES.md:150` specifies. The resolved archive passes under the modified later builder below.

## Evidence

Reviewed branch `redesign-2026-09`, commit `9d165064738d4b121793524da7ab76d2d4389ede`. All Python processes inherited `PYTHONDONTWRITEBYTECODE=1`; git reads used `GIT_OPTIONAL_LOCKS=0`. `$S` below is `/workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex`. Temporary drivers were removed with scratch. Outputs below are verbatim excerpts; successful verifier excerpts retain their final line.

Independent identity driver imported only stdlib, using `json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')`, prefixed separately with `b'te-tracks-build-v1\n'` and `b'te-tracks-catalog-v1\n'`; it compared both ID files including terminal LF. It resolved published `current` once and retained that path for consumer reads. Every differing provenance key is listed.
```text
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/identity.py
build BUILD_ID=0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a CATALOG_ID=0c0a959dea69e397890b590b640162d5bd45e71a88f6468cadd4b7615022b4a4; files_match=True
build manifest_sha256=bde6cb3187bf155f9d13058ec07bda3ae496aad5e23c12bb693212f8989c6cb3
published BUILD_ID=0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a CATALOG_ID=0c0a959dea69e397890b590b640162d5bd45e71a88f6468cadd4b7615022b4a4; files_match=True
published manifest_sha256=13ef2bfc1d0ede041939e1987a75941d25b7d1017012a07e3a97482c58671b36
identity_equal=True
provenance_differing_keys=built_at,invocation_argv,peak_rss_bytes,peak_rss_measurement
```

Fixture driver used `make_build(family)` and `make_build(family, added_export=True)` from `tests/fixtures/publication/build_fixture.py`, with identical default policy notes. The latter adds `all_rmsk/full/record_extra.bed` across namespaces. A tracked-file repository copy under `later-repo` adds that job and its record-BED contract, bumps TAXONOMY_RULE_VERSION to v2, and leaves the published-version tuple at v1. Verification/install/select accept the archived v1 declarations; authoring refuses unpublished v2. A separately rehashed scratch declaration of v2 is refused by verification/install.

Transfer follows `docs/RELEASES.md:130` literally: resolve source, pin ID/raw manifest, create destination staging, explicitly copy contents, compare raw manifest, verify, install, compare installed manifest, select. Both IDs and raw manifest survive. The documented layout and command flags supply everything this fixture transfer needs; no extra implementation knowledge was needed. For the source probes, only one source byte changes: chromAlias byte 1 changes whitespace, and rmsk_out gzip-header byte 4 changes while decompressed records stay equal. Matching source checksum receipts/config pins are updated and the manifest is regenerated; all four canonical table bytes stay unchanged.
```text
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/seam.py
A=972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
B=25bff2bda6d46f1ef18455feb51bcdfbd51eb765b11f1cc368383c5658c5d114
CATALOG=c4528450d0dbd4c1cb0e021e47b01fce7771807c191313e1eb4de544ebcc1f5d; same_catalog=True
export_contracts=24
export_contracts=27
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/release.py install --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward --family te_mm39 --staging /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward/te_mm39/.staging/fixture-276ikggh --select
installed 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
selected 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/release.py install --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward --family te_mm39 --staging /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward/te_mm39/.staging/fixture-tllab5gd --select
installed 25bff2bda6d46f1ef18455feb51bcdfbd51eb765b11f1cc368383c5658c5d114
selected 25bff2bda6d46f1ef18455feb51bcdfbd51eb765b11f1cc368383c5658c5d114
exit=0
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/release.py select --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward --family te_mm39 --build-id 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
selected 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/release.py verify-current --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward --family te_mm39
972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/release.py install --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/reverse --family te_mm39 --staging /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/reverse/te_mm39/.staging/B --select
installed 25bff2bda6d46f1ef18455feb51bcdfbd51eb765b11f1cc368383c5658c5d114
selected 25bff2bda6d46f1ef18455feb51bcdfbd51eb765b11f1cc368383c5658c5d114
exit=0
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/release.py install --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/reverse --family te_mm39 --staging /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/reverse/te_mm39/.staging/A --select
installed 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
selected 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/release.py verify-current --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/reverse --family te_mm39
972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
later-repo: added all_rmsk record_extra.bed; TAXONOMY_RULE_VERSION=taxonomy_rule_v2; PUBLISHED_TAXONOMY_RULE_VERSIONS unchanged
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later-repo/src/99_verify.py /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward/te_mm39/archive/972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
verified 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later-repo/src/99_verify.py /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward/te_mm39/archive/25bff2bda6d46f1ef18455feb51bcdfbd51eb765b11f1cc368383c5658c5d114
verified 25bff2bda6d46f1ef18455feb51bcdfbd51eb765b11f1cc368383c5658c5d114
exit=0
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later-repo/src/release.py verify-current --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward --family te_mm39
972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later-repo/src/release.py select --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward --family te_mm39 --build-id 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
selected 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later-repo/src/release.py install --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later --family te_mm39 --staging /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later/te_mm39/.staging/A --select
installed 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
selected 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later-repo/src/release.py install --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later --family te_mm39 --staging /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later/te_mm39/.staging/B --select
installed 25bff2bda6d46f1ef18455feb51bcdfbd51eb765b11f1cc368383c5658c5d114
selected 25bff2bda6d46f1ef18455feb51bcdfbd51eb765b11f1cc368383c5658c5d114
exit=0
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later-repo/src/90_manifest.py /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/author/te_mm39/.staging/candidate /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward/fixture.env
manifest: unsupported taxonomy_rule_version
exit=1
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later-repo/src/99_verify.py /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/unpublished/te_mm39/.staging/candidate
verify: unsupported taxonomy_rule_version
exit=1
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later-repo/src/release.py install --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/unpublished --family te_mm39 --staging /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/unpublished/te_mm39/.staging/candidate --select
release: unsupported taxonomy_rule_version
exit=1
$ cp -a /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/forward/te_mm39/archive/972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027/. /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/transfer/te_mm39/.staging/incoming
exit=0
staging_raw_manifest_sha256=bfd0eef9d738ad8ce5993d8c2e48a7a750410655e743d7766b67f86551b6dd8a
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/99_verify.py /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/transfer/te_mm39/.staging/incoming
verified 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/release.py install --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/transfer --family te_mm39 --staging /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/transfer/te_mm39/.staging/incoming
installed 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
installed_raw_manifest_matches=True
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/release.py select --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/transfer --family te_mm39 --build-id 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
selected 972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/release.py verify-current --root /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/transfer --family te_mm39
972b2569e8d8fd800c810e35ff0753c20676b176ad241e8d83a07f9de7d4b027
exit=0
transfer_same_BUILD_ID=True transfer_same_CATALOG_ID=True
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/90_manifest.py /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/mutate-chromAlias/te_mm39/.staging/fixture-o590n4mf /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/mutate-chromAlias/fixture.env
exit=0
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/99_verify.py /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/mutate-chromAlias/te_mm39/.staging/fixture-o590n4mf
verified c88fa49aa22819a9255afafdf8ebcbcb1650d6c172e5ecf0246207cbe951a773
exit=0
chromAlias: one_source_byte_changed=True canonical_tables_unchanged=True BUILD_ID_changed=True CATALOG_ID_changed=False
mutated_BUILD_ID=c88fa49aa22819a9255afafdf8ebcbcb1650d6c172e5ecf0246207cbe951a773 mutated_CATALOG_ID=c4528450d0dbd4c1cb0e021e47b01fce7771807c191313e1eb4de544ebcc1f5d
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/90_manifest.py /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/mutate-rmsk_out/te_mm39/.staging/fixture-w8_n2n1c /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/mutate-rmsk_out/fixture.env
exit=0
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/99_verify.py /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/mutate-rmsk_out/te_mm39/.staging/fixture-w8_n2n1c
verified 79123d7e41c3675d2a57d49e349e90f0e34fe56e51c71199846aa4b04fc6914c
exit=0
rmsk_out: one_source_byte_changed=True canonical_tables_unchanged=True BUILD_ID_changed=True CATALOG_ID_changed=True
mutated_BUILD_ID=79123d7e41c3675d2a57d49e349e90f0e34fe56e51c71199846aa4b04fc6914c mutated_CATALOG_ID=92cdc4c643fb557340925ff36e2b5eac2a018d24180b021ad62b56d8235aa583
fixture_seam_complete=True
```

The later verifier also checked the complete published archive. The existing publication regression check ran entirely under `$S/checks-root`.
```text
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/later-repo/src/99_verify.py "$(cat /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/resolved_archive)"
verified 0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a
$ TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/checks-root python3 tests/checks/core/72_publication_cases.py
identical and changed builds, export-roster evolution (4 archives), failed verification, added payload, concurrent installs/selects (6 archives), old IDs, forged ID, corrupt current, selector and root cases, occupied targets, symlinks and 0444/0555 modes pass
```

Consumer driver reads all GENCODE subfamily BED names, passes that published path to vendored IRescue `makeRmsk`, then feeds those exact names through its `index_features`/`parse_maps` using scratch feature/mapping files. It compares the full name set to registration `(interspersed,full,subfamily,rmsk_name)` and the three archived `identity.export_contracts`, then checks every MERVL-int support block against the BED and every returned record ID against the published parquet. This establishes parser identity and membership; quantification remains the consumer's scope.
```text
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/consumer.py
resolved_archive=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive/0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a
$ /workspaces/Meta-Aging/01_modules/te-tracks/bin/te-tracks-preflight /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive/0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a/exports/ucsc/interspersed/full/subfamily.bed /workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv
only_in_reference	["GL456210.1","GL456211.1","GL456212.1","GL456219.1","GL456221.1","GL456233.2","GL456239.1","GL456354.1","GL456359.1","GL456360.1","GL456366.1","GL456367.1","GL456368.1","GL456370.1","GL456372.1","GL456378.1","GL456379.1","GL456381.1","GL456382.1","GL456383.1","GL456385.1","GL456387.1","GL456389.1","GL456390.1","GL456392.1","GL456394.1","GL456396.1","JH584295.1","JH584296.1","JH584297.1","JH584298.1","JH584299.1","JH584300.1","JH584301.1","JH584302.1","JH584303.1","JH584304.1","MU069434.1","MU069435.1","chrM"]
only_in_export	["chr1_GL456210v1_random","chr1_GL456211v1_random","chr1_GL456212v1_random","chr1_GL456221v1_random","chr1_GL456239v1_random","chr1_MU069434v1_random","chr5_GL456354v1_random","chr5_JH584296v1_random","chr5_JH584297v1_random","chr5_JH584298v1_random","chr5_JH584299v1_random","chr7_GL456219v1_random","chrUn_GL456359v1","chrUn_GL456360v1","chrUn_GL456366v1","chrUn_GL456367v1","chrUn_GL456368v1","chrUn_GL456370v1","chrUn_GL456372v1","chrUn_GL456378v1","chrUn_GL456379v1","chrUn_GL456381v1","chrUn_GL456382v1","chrUn_GL456383v1","chrUn_GL456385v1","chrUn_GL456387v1","chrUn_GL456389v1","chrUn_GL456390v1","chrUn_GL456392v1","chrUn_GL456394v1","chrUn_GL456396v1","chrUn_JH584304v1","chrUn_MU069435v1","chrX_GL456233v2_random","chrY_JH584300v1_random","chrY_JH584301v1_random","chrY_JH584302v1_random","chrY_JH584303v1_random"]
length_disagreements	[]
alias_table	"/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive/0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a/tables/contig_aliases.tsv"
exit=2
$ /workspaces/Meta-Aging/01_modules/te-tracks/bin/te-tracks-preflight /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive/0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a/exports/ensembl/interspersed/full/subfamily.bed /workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv
only_in_reference	["JH584295.1","chr1","chr10","chr11","chr12","chr13","chr14","chr15","chr16","chr17","chr18","chr19","chr2","chr3","chr4","chr5","chr6","chr7","chr8","chr9","chrM","chrX","chrY"]
only_in_export	["1","10","11","12","13","14","15","16","17","18","19","2","3","4","5","6","7","8","9","X","Y"]
length_disagreements	[]
alias_table	"/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive/0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a/tables/contig_aliases.tsv"
exit=2
$ /workspaces/Meta-Aging/01_modules/te-tracks/bin/te-tracks-preflight /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive/0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a/exports/gencode/interspersed/full/subfamily.bed /workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv
only_in_reference	["JH584295.1","chrM"]
only_in_export	[]
length_disagreements	[]
alias_table	"/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive/0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a/tables/contig_aliases.tsv"
exit=0
three_manifest_contracts: IRescue=name; name=rmsk_records.rmsk_name; selectable_level=subfamily
irescue_version=1.2.0 checkout=26f36fb391bb031a156ae8f0a77f31c125bfbe15
[2026/09/16 - 20:23:43] Using provided RepeatMasker annotation from /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/archive/0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a/exports/gencode/interspersed/full/subfamily.bed.
IRescue makeRmsk + index_features + parse_maps: 1220 exact published BED names preserved
registration: exact feature set matches=True; key_grammar=rmsk_name; example=MERVL-int; example_registered_records=2066
example_rmsk_record_id=MERVL-int|chr1:5320718-5320755|-
example_member_ids_present_in_published_catalog=True
```

Child probe calls `family_root`, changes GENOME only in a fixture config dictionary, and separately rehashes scratch manifests with nonnull parent IDs under each family spelling. The final command exercises the phase 9 selector-path issue.
```text
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/child.py
family_regex_accepts=te_mm39_gene
GENOME=mm39_gene: species admission required for mm39_gene
family=te_mm39 nonnull_parent_ids: verify: core identity requires null parent ids; exit=1
family=te_mm39_gene nonnull_parent_ids: verify: identity family or species differs; exit=1
$ python3 /workspaces/Meta-Aging/01_modules/te-tracks/src/99_verify.py /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/current
verify: invalid build directory: /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/current
exit=1
```

## Scope check

Only durable write: `docs/_internal/redesign-2026-09/reviews/m7_codex.md`. Temporary drivers, logs, repository copy and fixture outputs lived under `$S` and were removed with Python `shutil`. No git writes, installs or network; owner copies `14839-DM-cGAS` and `sene/` were untouched. Status wrapper ran `git -C <checkout> status --short --untracked-files=all` before and after:
```text
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-codex/scope.py
te-tracks: before=[" M docs/_internal/redesign-2026-09/prompts/m7_codex.md", " M docs/_internal/redesign-2026-09/prompts/m7_divergent.md", " M docs/_internal/redesign-2026-09/prompts/m7_opus.md", " M docs/_internal/redesign-2026-09/prompts/p8_consult.md"] after=[" M docs/_internal/redesign-2026-09/prompts/m7_codex.md", " M docs/_internal/redesign-2026-09/prompts/m7_divergent.md", " M docs/_internal/redesign-2026-09/prompts/m7_opus.md", " M docs/_internal/redesign-2026-09/prompts/p8_consult.md", "?? docs/_internal/redesign-2026-09/reviews/m7_codex.md"]
DfamTEBrowser: before=[] after=[]
irescue: before=[] after=[]
mascarade: before=[] after=[]
MATES: before=[] after=[]
mLLMCelltype: before=[] after=[]
scTE: before=[] after=[]
scTEfinder: before=[] after=[]
stellarscope: before=[] after=[]
TElocal: before=[] after=[]
TEsingle: before=[] after=[]
TEtranscripts: before=[] after=[]
protected_build_and_pubroot: paths/sizes/mtime_ns/modes unchanged; raw manifest hashes unchanged
HEAD_after=9d165064738d4b121793524da7ab76d2d4389ede
scratch_exists_after_cleanup=False
```
