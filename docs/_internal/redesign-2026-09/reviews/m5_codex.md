# Milestone 5 review: consumer seam (codex gpt-6-astra)
Verdict: BLOCKING

## Blocking

- [B1] `src/lib/build_exports.py:158` registers five input-ID spellings per record, omitting the actual TEsingle/TElocal output tuples and Stellarscope instance aliases. `docs/OUTPUTS.md:387` promises exact emitted IDs; the ADR consult explicitly requires exact tuples (`docs/_internal/redesign-2026-09/consults/ADR5_consult.md:122`). — On 1,000 evenly spaced mm39 rows, both tuple parsers produce 1,000 record keys and 285 subfamily keys with **zero exact registration matches**; Stellarscope produces 1,000 instance keys with zero matches. The count-7 join consequently loses the feature. BED, `locus`, SAF and TEtranscripts triple keys resolve. `tests/checks/core/41_export_registration.py:133` checks only GTF `locus`; its conservation fixture supplies a separate authored `F` membership (`:20`), bypassing this seam. — Before phase 6/7, extend `export_feature_members` with `(record, R:name:family:class)`, `(subfamily, name:name:family:class)` and `(instance, I|mm39|id)` memberships over the selected records; retain existing IDs and the seven export filenames/attributes. Extend the closed level/count assertions at `41_export_registration.py:84` and `:95`, expected registration bytes, and parser-to-registration joins. These additional rows fit the existing columns; the published registration contents and level contract need correction.

## Advisory

- [A1] `docs/OUTPUTS.md:392` promises one row per feature–record pair; phase 8 requires several retained blocks per pair (`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md:12`). — A real bedtools subtraction produces two pieces with the same feature and parent record, distinguished by `(10,12)` and `(16,20)`. — In phase 8, scope the one-row promise to `full` and define membership-row uniqueness using the existing block columns. The four-column feature key remains unchanged; child identity pins the parent catalog/build, and fully subtracted records belong in the planned status table.
- [A2] `src/lib/build_exports.py:44`, `:106`, `:159`, `:173` hardcode `interspersed`, `ucsc` and `full`; `:128` and `:178` replace the registration/inventory. `tests/checks/core/40_exports_shape.py:17` and `41_export_registration.py:104` require exactly the UCSC paths; `tests/lib/consumers.py:380` selects that path too. — Phase 6 must rename only contig columns, preserve embedded UCSC identities and registration bytes, append namespace inventory rows and extend namespace checks. Phase 8 needs explicit universe/variant/block inputs, including its planned compat-universe acceptance run. Parameterize or add dedicated stages before those phases; reusing the current writer unchanged would overwrite the inventory. Sampled Ensembl copies retain every tested key.
- [A3] `docs/OUTPUTS.md:404` / `src/lib/build_exports.py:172` provide phase 7's file-identity inventory seed: path, namespace, universe, variant, default level, format and digest. They do not encode the selectable GTF feature spaces: TEtranscripts reads either GTF at registered `taxonomy_triple` level, while their inventory levels are `record`/`subfamily`; Stellarscope's instance choice is also absent. — In phase 7, encode attribute mappings, output-key construction, coordinate conventions and selectable levels in manifest `export_contracts`, as specified by `docs/_internal/redesign-2026-09/consults/ADR5_consult.md:124`. The existing inventory columns suffice for file identity; the manifest must supply these semantic contracts.

## Evidence

Reviewed branch `redesign-2026-09`, HEAD `9ac66fbbb97fafb27de6cc686080243e7fe18b6d`, against the requested phase plans, rulings, consults, public contracts, code, fixtures and phase reviews. Prior rulings govern the earlier reviews' findings. This review assesses consumer identities; it does not repeat the full numerical/fixture audit.

Exact keys: let `n` be `rmsk_name`, `f/c` the canonical or positional unresolved family/class tokens, `K` the canonical record ID, `R` its colon-free record alias, and `I` its `I|mm39|<rmsk_instance_id>` alias.

| Reader and export | Actual key | Registration level / result |
|---|---|---|
| IRescue and bedtools, record/subfamily/family BED | `K`, `n`, `c/f` | record/subfamily/family; resolve |
| Stellarscope, record GTF `locus` / `instance_id` | `R` / `I` | record resolves / instance missing |
| Stellarscope, subfamily GTF `locus` | `n` | subfamily; resolves |
| TEtranscripts, either GTF | `n:f:c` | taxonomy_triple; resolves |
| TEsingle and TElocal, record GTF | `R:n:f:c` | record; missing |
| TEsingle and TElocal, subfamily GTF | `n:n:f:c` | subfamily; missing |
| SAF reader, subfamily / taxonomy-triple SAF | `n` / `n:f:c` | subfamily/taxonomy_triple; resolve |

Within a pinned build, `(universe_name, variant, feature_level, emitted_feature_id)` identifies the feature; `rmsk_record_id` and the block bounds describe its support. Namespace copies reuse this feature key and membership. Split pieces reuse the feature and record IDs with distinct existing block bounds.

The two GTFs have the same fixed columns and shared taxonomy attributes; only `transcript_id`, `locus` and record-only `instance_id`/`rmsk_record_id` differ. All three TE parsers find their four required attributes in both files. Selecting `instance_id` on subfamily GTF yields no Stellarscope groups, consistent with the documented record-GTF-only choice (`docs/OUTPUTS.md:335`, `:347`, `:361`, `:429`). No GTF attribute or filename change is needed.

`probe.py` read 1,000 positions `i*(rows-1)//999` from each mm39 export, ran checkout `makeRmsk`, `index_features`, `parse_maps`, the three real `TEfeatures.build` parsers, TElocal's actual pickle-loader branch and Stellarscope's isolated `IntervalTreeAnnotation`; bedtools read the sampled BEDs. SAF used `csv.DictReader`, since featureCounts is absent. It scanned the full registration, retained sample-record edges, joined those records to parquet and canonical taxonomy, and checked bounds. `pairs.py` compared every sampled parser-key/record edge with that registration. `count7` assigns a synthetic count to one exact measured feature, selects distinct measured IDs after the record/subfamily/family joins, and sums once. A zero below means an unmatched key, never an inferred biological zero. IRescue `chrcat` and featureCounts execution remain unverified here.

The commands below used `GIT_OPTIONAL_LOCKS=0`, `PYTHONDONTWRITEBYTECODE=1`, and `TMPDIR=/workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex/tmp`; consumer/support probes used the separate scratch refroot. Probe scripts and logs were removed at completion. Outputs are verbatim.

```text
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex/probe.py
sample: 1000 evenly spaced rows from each mm39 export; first/last included
GTF difference: transcript_id,locus,instance_id,rmsk_record_id only; other columns/attributes equal=True
Stellarscope/subfamily/instance_id: groups=0 (attribute absent; unsupported choice)
registration scan: rows=18824745; sample record/block joins=5000; canonical records=1000
IRescue/record: keys=1000 registered=1000 count7(record/subfamily/family)=7/7/7 first=AmnL2-1|chr17:78151932-78152001|+
bedtools/record: keys=1000 registered=1000 count7(record/subfamily/family)=7/7/7 first=AmnL2-1|chr17:78151932-78152001|+
IRescue/subfamily: keys=285 registered=285 count7(record/subfamily/family)=7/7/7 first=AmnL2-1
bedtools/subfamily: keys=285 registered=285 count7(record/subfamily/family)=7/7/7 first=AmnL2-1
IRescue/family: keys=23 registered=23 count7(record/subfamily/family)=7/7/7 first=DNA/DNA
bedtools/family: keys=23 registered=23 count7(record/subfamily/family)=7/7/7 first=DNA/DNA
Stellarscope/record/locus: keys=1000 registered=1000 count7(record/subfamily/family)=7/7/7 first=R|mm39|AmnL2-1|chr17|78151932|78152001|+
Stellarscope/subfamily/locus: keys=285 registered=285 count7(record/subfamily/family)=7/7/7 first=AmnL2-1
Stellarscope/record/instance_id: keys=1000 registered=0 count7(record/subfamily/family)=0/0/0 first=I|mm39|1
TEtranscripts/record: keys=285 registered=285 count7(record/subfamily/family)=7/7/7 first=AmnL2-1:L2:LINE
TEtranscripts/subfamily: keys=285 registered=285 count7(record/subfamily/family)=7/7/7 first=AmnL2-1:L2:LINE
TEsingle/record: keys=1000 registered=0 count7(record/subfamily/family)=0/0/0 first=R|mm39|AmnL2-1|chr17|78151932|78152001|+:AmnL2-1:L2:LINE
TEsingle/subfamily: keys=285 registered=0 count7(record/subfamily/family)=0/0/0 first=AmnL2-1:AmnL2-1:L2:LINE
TElocal/record: keys=1000 registered=0 count7(record/subfamily/family)=0/0/0 first=R|mm39|AmnL2-1|chr17|78151932|78152001|+:AmnL2-1:L2:LINE
TElocal/subfamily: keys=285 registered=0 count7(record/subfamily/family)=0/0/0 first=AmnL2-1:AmnL2-1:L2:LINE
SAF-reader/subfamily: keys=285 registered=285 count7(record/subfamily/family)=7/7/7 first=AmnL2-1
SAF-reader/taxonomy_triple: keys=285 registered=285 count7(record/subfamily/family)=7/7/7 first=AmnL2-1:L2:LINE
registration levels=family,record,subfamily,taxonomy_triple
inventory columns=export_path,namespace,universe_name,variant,feature_level,format,rows,distinct_features,sha256
featureCounts executable absent: SAF-reader results certify format/key only
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex/pairs.py
IRescue/record: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
bedtools/record: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
IRescue/subfamily: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
bedtools/subfamily: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
IRescue/family: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
bedtools/family: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
Stellarscope/record/locus: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
Stellarscope/subfamily/locus: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
Stellarscope/record/instance_id: exact sample key-record edges=0/1000; per-key distinct-feature count7 outcomes=[0]
TEtranscripts/record: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
TEtranscripts/subfamily: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
TEsingle/record: exact sample key-record edges=0/1000; per-key distinct-feature count7 outcomes=[0]
TEsingle/subfamily: exact sample key-record edges=0/1000; per-key distinct-feature count7 outcomes=[0]
TElocal/record: exact sample key-record edges=0/1000; per-key distinct-feature count7 outcomes=[0]
TElocal/subfamily: exact sample key-record edges=0/1000; per-key distinct-feature count7 outcomes=[0]
SAF-reader/subfamily: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
SAF-reader/taxonomy_triple: exact sample key-record edges=1000/1000; per-key distinct-feature count7 outcomes=[7]
```

Conservation means selecting distinct measured features over supporting records (`ADR5_consult.md:144`), as the current check implements; sums of per-record or per-subfamily marginal selections are not allocations. The existing `F=7` fixture passes while its three record-target totals sum to 21. The consumer fixture's mixed instance spans `SubB` and `SubB-int`: copying its count into both subfamilies sums to 14. Even after B1, that instance requires an explicit allocation for additive subfamily counts. Record, subfamily, family and split-block selections can conserve the original feature count without inventing such an allocation.

Unresolved fixture values retain `_` literally through the TE parsers, Stellarscope's quoted-value regex, IRescue's feature/map readers and bedtools. `/` separates exactly two family-BED positions; `:` separates three TEtranscripts/SAF or four TEsingle/TElocal positions. Neither unresolved token contains those separators (`src/lib/build_exports.py:19`, `:85`). The SAF format reader preserves GeneID; executable featureCounts acceptance of these tokens remains unmeasured. `seams.py` also renamed only the sampled contig columns using the pinned chromAlias Ensembl column and subtracted a central interval with real bedtools.

```text
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex/conservation.py
existing conservation(registration): PASS; measured key=F; total=7 at record/subfamily/family
existing per-record target totals sum=21; distinct measured-feature selection=7
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex/seams.py
unresolved TEsingle/record: R|mm39|Opaque|chr10|9|12|-:Opaque:unresolved_family_Opaque:unresolved_class_Opaque
unresolved TEsingle/subfamily: Opaque:Opaque:unresolved_family_Opaque:unresolved_class_Opaque
unresolved TEtranscripts/record: Opaque:unresolved_family_Opaque:unresolved_class_Opaque
unresolved TEtranscripts/subfamily: Opaque:unresolved_family_Opaque:unresolved_class_Opaque
unresolved TElocal/record: R|mm39|Opaque|chr10|9|12|-:Opaque:unresolved_family_Opaque:unresolved_class_Opaque
unresolved TElocal/subfamily: Opaque:Opaque:unresolved_family_Opaque:unresolved_class_Opaque
unresolved Stellarscope/record: unresolved_family_Opaque / unresolved_class_Opaque
unresolved Stellarscope/subfamily: unresolved_family_Opaque / unresolved_class_Opaque
unresolved IRescue/bedtools family.bed: unresolved_class_Opaque/unresolved_family_Opaque
unresolved SAF-reader: Opaque:unresolved_family_Opaque:unresolved_class_Opaque
namespace probe: seven sampled Ensembl copies; all BED/SAF keys and TE/Stellarscope parser keys unchanged
split probe: [('interspersed', 'exon_subtracted', 'subfamily', 'A', 'A|chr2:10-20|+', 10, 12), ('interspersed', 'exon_subtracted', 'subfamily', 'A', 'A|chr2:10-20|+', 16, 20)]
split uniqueness: feature-record=1; including existing block columns=2; distinct-feature count7=7
mixed instance I|mm39|7: subfamilies=['SubB', 'SubB-int']; distinct-feature selection=7; sum of unallocated per-subfamily copies=14
existing conservation fact=[{'emitted_feature_id': 'F', 'count': 7}]
```

Support reporting is honest for the exercised paths: absent executables and external modules exit 3 with names; missing symbols/internal imports fail; the observed Stellarscope boundary defect exits 3 with the version and observed/expected vectors (`tests/lib/consumers.py:116`, `:129`; `tests/checks/consumers/11_stellarscope_parser.py:43`). Executable discovery dispatches the four existing execution checks automatically (`tests/lib/consumers.py:536`); installing `gawk` enables check 15 and installing DuckDB enables check 30 against an available build. Inventory entries for Stellarscope/TEsingle/TEcount/TElocal are availability reports, with their source-parser checks separate. Installing those tools does not create additional execution checks. MATES is explicitly a fixture-only adapter using a documented resource-function stand-in, not a delivered mm39 export (`docs/OUTPUTS.md:436`). featureCounts' enabled checks cover subfamily and one-base SAF (`tests/lib/consumers.py:483`); the triple SAF still needs an executable identity check when available.

```text
$ tests/run.sh consumers --refroot /workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex/refroot
pass  00_tool_inventory.py  supported tool_inventory reporting-only; irescue=absent; featureCounts=absent; stellarscope=absent; TEsingle=absent; TEcount=absent; TElocal=absent; bedtools=bedtools v2.31.1; samtools=samtools 1.21
pass  10_irescue_parser.py  supported irescue 1.2.0 checkout parser; record=11, subfamily=8; comma splits one name and exporter rejects it
unsupported  11_stellarscope_parser.py  unsupported: stellarscope 1.5 right-boundary overlap defect, observed 0,1,1,1 expected 0,1,1,0
pass  12_tesingle_parser.py  supported TEsingle 1.0 checkout parser; record=11, subfamily=8; 999 distinct UR dropped, 1000 kept; duplicate/QC-fail reads skipped
pass  13_tetranscripts_telocal_parser.py  supported TEtranscripts/TElocal 2.2.4/1.1.3 checkout parsers; TEtranscripts=8 groups; TElocal locInd record=11, subfamily=8
pass  14_mates_parser.py  supported MATES 0.1.8 checkout adapter; eight-column pair; underscore stem; ?/Unknown model groups dropped
unsupported  15_irescue_chrcat.py  unsupported: irescue system tool gawk absent
unsupported  20_irescue_exec.sh  unsupported: irescue absent
unsupported  21_featurecounts_exec.sh  unsupported: featureCounts absent
pass  22_bedtools_exec.sh  supported bedtools v2.31.1; duplicate names, half-open boundaries and -s/-S pass
pass  23_samtools_fixture_integrity.sh  supported samtools 1.21; 11 sorted, indexed BAMs; ARC=13 OCM=26 bulk=26 alignments, 11 molecules each; tagged main UB=11 UR=12; reverse strands and duplicate/QC-fail flags pass
unsupported  30_registration_duckdb.py  unsupported: python module duckdb absent
checks=12 pass=7 fail=0 unsupported=5
exit=0
$ python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex/support.py
unsupported: stellarscope python module intervaltree absent
simulated absent parser dependency exit=3
missing-symbol: exit=1; failed missing-symbol: cannot import name missing
checkout-internal: exit=1; failed checkout-internal: No module named 'irescue.absent'
mocked executable discovery irescue: check dispatched=True
mocked executable discovery featureCounts: check dispatched=True
mocked executable discovery bedtools: check dispatched=True
mocked executable discovery samtools: check dispatched=True
```

The dependency probe simulated absence of installed `intervaltree` at import and discovery, then ran the unchanged Stellarscope check. The dispatch probes mocked discovery and check bodies only; their outputs establish automatic dispatch, not executable correctness.

## Scope check

Entry snapshot: Python subprocess calls to `git -C <repo> rev-parse HEAD` and `git -C <repo> status --short --untracked-files=all` for te-tracks and every `.git` under `/workspaces/Meta-Aging/01_modules/.ref`. Each line below is the captured repository name, HEAD and `repr(status)`; `''` means empty status.

```text
te-tracks 9ac66fbbb97fafb27de6cc686080243e7fe18b6d ' M docs/_internal/redesign-2026-09/prompts/m5_codex.md\n M docs/_internal/redesign-2026-09/prompts/m5_divergent.md\n M docs/_internal/redesign-2026-09/prompts/m5_opus.md\n'
DfamTEBrowser a57c5866a681838cae431009d5c156fbf817af56 ''
MATES 87c1218603a26fc9cfa8ab36ef6f730d72d127af ''
TElocal 1a168c299714fc55df7dd93359f553759b95c810 ''
TEsingle 655f1274de0fe5f3241219afc2ecb1c2e0830ae9 ''
TEtranscripts e7f9b93f8c351b1b582cf0882aed49ffd1f0d1e9 ''
irescue 26f36fb391bb031a156ae8f0a77f31c125bfbe15 ''
mLLMCelltype 322f41e3ed8ebff810154d1a815e3c5294691e83 ''
mascarade 2e40e365aa297b089df53009914ac1d4d3dc4f0e ''
stellarscope 0e0d594047212afe81e3754732119975a0d2aa6f ''
```

After writing this review, the same commands were repeated:

```text
$ GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1 python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex/scope.py
te-tracks 9ac66fbbb97fafb27de6cc686080243e7fe18b6d ' M docs/_internal/redesign-2026-09/prompts/m5_codex.md\n M docs/_internal/redesign-2026-09/prompts/m5_divergent.md\n M docs/_internal/redesign-2026-09/prompts/m5_opus.md\n?? docs/_internal/redesign-2026-09/reviews/m5_codex.md\n'
DfamTEBrowser a57c5866a681838cae431009d5c156fbf817af56 ''
MATES 87c1218603a26fc9cfa8ab36ef6f730d72d127af ''
TElocal 1a168c299714fc55df7dd93359f553759b95c810 ''
TEsingle 655f1274de0fe5f3241219afc2ecb1c2e0830ae9 ''
TEtranscripts e7f9b93f8c351b1b582cf0882aed49ffd1f0d1e9 ''
irescue 26f36fb391bb031a156ae8f0a77f31c125bfbe15 ''
mLLMCelltype 322f41e3ed8ebff810154d1a815e3c5294691e83 ''
mascarade 2e40e365aa297b089df53009914ac1d4d3dc4f0e ''
stellarscope 0e0d594047212afe81e3754732119975a0d2aa6f ''
orchestrator build file sizes/mtimes unchanged=True
```

The sole repository file written is `docs/_internal/redesign-2026-09/reviews/m5_codex.md`. The three prompt modifications predate this review. All scratch scripts, samples, fixtures, pickles, logs and temporary files were confined to `/workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex/`, then removed. The orchestrator's build was read only. No Git write commands, installs or network calls were made.

Cleanup: `shutil.rmtree(Path("/workspaces/Meta-Aging/_scratch/te-tracks-audit/m5-codex"))`, followed by `print("scratch_exists=" + str(scratch.exists()))`:

```text
scratch_exists=False
```
