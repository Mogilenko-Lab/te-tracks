# Milestone 2 review: schema and identity (codex gpt-6-astra)
Verdict: PASS WITH ADVISORIES

Reviewed `redesign-2026-09` at `c28caea8fe9908bb801e79827216de2e00f974ba`. Citations: `P/` = `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/`; `C/` = `docs/_internal/redesign-2026-09/consults/`; `R/` = `/workspaces/Meta-Aging/01_modules/.ref/`. The six phase reviews were read as historical evidence; current code and public contracts determine this verdict.

## Blocking

- None. Phases 3–9 and the consuming ledger can retain the published mm39 keys, columns and filenames. Deferred hg38 shards and structural ERV units require their own admission contracts.

## Advisory

- [A1] `docs/OUTPUTS.md:27,55`, `src/00_fetch_sources.sh:51` Instance scope is implicit in the public contract and absent from source metadata — the complete token and single-contig invariant are documented; the explicit source-wide/run-scoped restriction appears in `C/ADR5_consult.md:28,34`. `SOURCES.json` identifies one pinned `.out`, while `MANIFEST.json` is deferred. Restarting per-contig IDs fail `src/lib/build_records.py:78`; independently numbered runs on the same contig could merge undetected. Publish the single source-wide run requirement and build-scoped instance key in phase 7 identity metadata; qualify source partitions and their membership keys before hg38 admission. Preserve existing mm39 tokens. Text supports `I|mm39|007` directly; phase 7 hashes the serialized table through its inventory, so tokens need no numeric conversion.
- [A2] `src/lib/build_universes.py:66`, `docs/OUTPUTS.md:68` The committed grammar has two operators and implicit AND; **`or` is rejected**, despite the review prompt and historical phase-2 review describing it. Version 1 documents these semantics and unknown keys fail closed. Raw class sets and family-prefix exclusions cover all scheduled universes; a validated ERV unit set needs structural membership and a versioned extension, even if OR were added (`docs/DECISIONS.md:89`). In phases 4/7, dispatch by the published version and read the selected build's JSON/membership; freeze a version-change rule for new predicate semantics. The Python dict is acceptable: one authored object is serialized, parsed and evaluated (`src/lib/build_universes.py:98,105`); an external JSON authoring file is optional.
- [A3] `src/lib/build_universes.py:98,121`, `P/17_phase7_publication.md:4` Freeze universe bytes and identity canonicalization in phase 7 — current literal insertion order, `indent=2`, `ensure_ascii=False`, UTF-8 and final LF are deterministic on modern insertion-ordered Python for this string/integer/list object. The measured file equals the current writer. There is no key sorting; changing object order or indentation changes the inventory digest even if `canonical_json(identity)` normalizes the embedded predicates. Today's ASCII-only object gives equal text under both ASCII settings. `schema_version=1` can cover grammar semantics; specify that ownership and the byte profile before release. Cross-version execution was not tested; the public byte guarantee already limits reproduction to the same builder/libraries (`docs/OUTPUTS.md:110`).
- [A4] `P/15_phase5_consumer_fixtures.md:15`, `docs/OUTPUTS.md:168` TElocal's `.locInd` handoff needs an indexing step — `R/TElocal/TElocal:627` loads a pickle, whereas its `TElocal_Toolkit/TEindex.py:383` parses GTF when building an index. Directly renaming `record.gtf` to `.locInd` cannot satisfy that reader. Phase 5 should build and validate an index from the registered GTF and correct this wording; the canonical filename/key stays intact. Phase 4/7 contracts should also specify alias versus exact output-tuple registration: TEtranscripts emits `gene:family:class`, TEsingle and TElocal include the transcript alias (`C/ADR5_consult.md:122,124`). Existing membership columns can express these mappings.
- [A5] `docs/OUTPUTS.md:104`, `tests/lib/records.py:37` Serialization is sufficient with explicit reader options; default inference is outside the contract — numeric-looking instance IDs need text, all declared int64 fields need signed 64-bit types, and readers must retain empty strings/literal labels and disable TSV quoting as the writer does (`src/lib/records_io.py:51`). Phase 7 should publish the ordered types/nullability and reader settings for DuckDB, R Arrow/data.table and pandas. Pandas and data.table probes preserve `007`, `-1847` and `false`; DuckDB and R Arrow are unavailable here. Before introducing nullable companion fields, enforce the reserved `\N` token or define a literal representation: the current text gate checks only tabs/line endings (`src/lib/build_records.py:103`). The live signed consensus contract supersedes the consult's original nonnegative wording (`C/ADR5_consult.md:58`; `docs/OUTPUTS.md:35`).

## Evidence

**Record/export/ledger judgment.** `src/lib/build_records.py:68,81` rejects name pipes/whitespace and contig pipes/colons/whitespace, making the constructed key reversible through its pipe-delimited components. All measured names fit the phase-4 alphabet: outside characters = empty; full-catalog punctuation is `()-._`, and interspersed punctuation is `-_`. None of those characters is an attribute delimiter in the inspected GTF readers. GTF uses the planned colon-free alias, rather than inserting the canonical colon-bearing ID into colon-delimited tuples (`P/14_phase4_exports.md:9`). TEtranscripts/TEsingle/TElocal split attributes on semicolons and remove quotes (`R/TEtranscripts/TEToolkit/TEindex.py:407,436`; `R/TEsingle/TEtools/TEindex.py:299,329`; `R/TElocal/TElocal_Toolkit/TEindex.py:389,419`); Stellarscope captures quoted values and groups them unchanged (`R/stellarscope/stellarscope/annotation/utils.py:61`; `annotation/_intervaltree.py:49`). The local name probes below test parsing only.

`record.bed` carries the canonical ID unchanged; IRescue transports the BED name and later splits comma-separated feature lists, with `#` display handling (`R/irescue/irescue/map.py:332,384`). Those delimiters are absent and forbidden by phase 4. SAF exports carry names or canonical triples, not record IDs (`docs/OUTPUTS.md:198`); no escaping is needed for the measured names. featureCounts execution remains unverified here. The lab SAF-result cleaner interprets `%` through `printf $1` (`/workspaces/Meta-Aging/01_modules/scio/skills/te-gene-featurecounts/scripts/runFeatureCounts_TE_and_genes.sh:135`); `%` is absent and excluded by the export alphabet. `export_feature_members` and the ledger carry opaque text FKs, with components authoritative for coordinates (`C/ADR5_consult.md:34,134`). Ingestion adds `te_build_id`; the registration relation's measured feature key and distinct-feature/existence join preserve the specified count-7/three-member conservation rule (`C/ADR5_consult.md:136,144`). No escaping or re-keying follows from those relations.

**Taxonomy judgment.** `rmsk_taxonomy` supplies every input to the voting rule: raw class/family labels, uncertainty suffixes and per-label record counts (`src/lib/build_records.py:114`; `P/13_phase3_taxonomy.md:11`). Class-only tokens become equal class/family labels and therefore abstain under rule step 2 (`src/lib/rmsk_out.py:84`). It cannot distinguish a class-only token from an explicit `X/X`; the rule intentionally treats both identically. Exact spelling remains in records' `rmsk_class_family`. The phase-3 output additionally needs per-record `divergence_pct` to calculate its median; the aggregate taxonomy table cannot supply that statistic, and the phase explicitly reads records for it (`P/13_phase3_taxonomy.md:43`). No voting input or column addition is missing.

**Universe/namespace/child judgment.** Within a pinned build, a universe name selects its JSON definition and membership; `all_rmsk` resolves to the complete catalog (`docs/OUTPUTS.md:90`). Phases 4/6/8 can reuse that name without recoding predicates; across builds the name needs the build pin, and the child pins its parent (`P/18_phase8_gene_child_seam.md:8`). `tests/checks/core/20_records_schema.py:35` does assume canonical `chrom` equals the ID component, correctly for source tables. Phase 6 renames export contigs only (`P/16_phase6_ensembl_preflight.md:12`), so its checks must use the alias relation rather than reapply that canonical-table assertion. Child blocks retain parent record IDs and parent build scope; subtraction changes registered support, with full-record coordinates retained. No canonical schema change is needed.

**Legacy judgment.** The compatibility predicate is exactly the legacy whitelist plus the case-sensitive `^tRNA` family exclusion (`docs/PROVENANCE.md:10`; `src/lib/build_universes.py:54`; `6ff3ee9:config/mm39.env:35,43`). Class-list order differs; selected records do not. This establishes selection compatibility. Canonical taxonomy-triple exports intentionally have a different grouping from legacy raw triples (`docs/OUTPUTS.md:199,201`).

The following commands and outputs are verbatim. Probes use the existing build read-only and synthetic data only; the numbers/fixture review remains with the other reviewers.

```bash
python3 -B - <<'PY'
import csv, hashlib, importlib.util, io, json, re, shutil, subprocess, sys
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
sys.path.insert(0, 'src/lib')
from build_records import load_out, load_sizes, validate_records
from build_universes import DEFINITIONS, evaluate_predicate
b = Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build')
t = list(csv.DictReader((b/'tables/rmsk_taxonomy.tsv').open(), delimiter='\t'))
classes = DEFINITIONS['universes'][1]['predicate']['class_in']
for label, rows in [('all_rmsk', t), ('interspersed', [r for r in t if r['rmsk_class'] in classes])]:
    names = {r['rmsk_name'] for r in rows}
    chars = set(''.join(names))
    print(label, 'names=', len(names), 'outside=', sorted(c for c in chars if not re.fullmatch(r'[A-Za-z0-9_.+/?()|:-]', c)), 'punctuation=', ''.join(sorted(c for c in chars if not c.isalnum())))
print('taxonomy_columns=', list(t[0]))
print('Eulor5B_labels=', [(r['rmsk_class'], r['rmsk_family'], r['record_count']) for r in t if r['rmsk_name']=='Eulor5B'])
print('taxonomy_colons=', any(':' in r[k] for r in t for k in ('rmsk_name','rmsk_family','rmsk_class')))
j = (b/'universes.json').read_bytes()
print('json_bytes=', len(j), 'writer_equal=', j==(json.dumps(DEFINITIONS, indent=2, ensure_ascii=False)+'\n').encode(), 'sha256=', hashlib.sha256(j).hexdigest())
print('json_predicate_keys=', sorted({k for u in json.loads(j)['universes'] for k in u['predicate']}))
print('ascii_flags_equal=', json.dumps(DEFINITIONS, ensure_ascii=False)==json.dumps(DEFINITIONS, ensure_ascii=True))
print('sorted_keys_change_bytes=', j!=(json.dumps(DEFINITIONS, indent=2, ensure_ascii=False, sort_keys=True)+'\n').encode())
try:
    evaluate_predicate(pd.DataFrame({'rmsk_class':['LTR'], 'rmsk_family':['ERV1']}), {'or':[{'class_in':['LTR']}]})
except ValueError as e:
    print('or_probe=', str(e))
meta = json.loads((b/'source/SOURCES.json').read_text())
print('source_metadata_keys=', sorted(meta), 'manifest_exists=', (b/'MANIFEST.json').exists())
f = Path('tests/fixtures/records')
try:
    validate_records(load_out(f/'spanning_instance.out'), load_sizes(f/'chrom.sizes'))
except ValueError as e:
    print('restarting_id_probe=', str(e))
schema = pq.read_schema(b/'tables/rmsk_records.parquet')
print('selected_types=', [(k, str(schema.field(k).type), schema.field(k).nullable) for k in ('rmsk_instance_id','consensus_left_bp','rmsk_overlap_flag')])
payload = 'rmsk_instance_id\tconsensus_left_bp\trmsk_overlap_flag\n007\t-1847\tfalse\n'
frame = pd.read_csv(io.StringIO(payload), sep='\t', dtype={'rmsk_instance_id':str, 'consensus_left_bp':'int64', 'rmsk_overlap_flag':bool}, na_filter=False, quoting=3)
print('pandas_typed_probe=', frame.iloc[0].to_dict(), 'instance_alias=', 'I|mm39|'+frame.iloc[0]['rmsk_instance_id'])
legacy = subprocess.check_output(['git','show','6ff3ee9:config/mm39.env'], text=True)
old_classes = re.search(r'^TE_CLASSES="([^"]+)"', legacy, re.M)[1].split()
old_prefix = re.search(r'^EXCLUDE_FAMILY_PREFIX="([^"]+)"', legacy, re.M)[1]
p = next(u['predicate'] for u in DEFINITIONS['universes'] if u['name']=='compat_tetranscripts_mm39')
print('legacy_class_symmetric_difference=', sorted(set(old_classes)^set(p['class_in'])), 'legacy_prefix=', old_prefix, 'new_prefix=', p['family_prefix_excluded'])
print('available=', {k: bool(shutil.which(k)) for k in ('featureCounts','Rscript','duckdb')}, 'duckdb_python=', importlib.util.find_spec('duckdb') is not None)
print('python=', sys.version.split()[0], 'pandas=', pd.__version__)
PY
```
```text
all_rmsk names= 18484 outside= [] punctuation= ()-._
interspersed names= 1220 outside= [] punctuation= -_
taxonomy_columns= ['rmsk_name', 'rmsk_family', 'rmsk_class', 'record_count', 'record_length_sum_bp']
Eulor5B_labels= [('DNA', 'Crypton-A', '34'), ('DNA?', 'DNA?', '1')]
taxonomy_colons= False
json_bytes= 2351 writer_equal= True sha256= 617feb99e7711f413df3e7935e532abcc12d4ecf7cfbcc4009a6cf31f2cb1b4c
json_predicate_keys= ['class_in', 'family_prefix_excluded']
ascii_flags_equal= True
sorted_keys_change_bytes= True
or_probe= unknown universe predicate keys: ['or']
source_metadata_keys= ['assembly', 'genome', 'rm_library', 'rm_run_evidence', 'rm_version', 'rmsk_out_profile', 'sources'] manifest_exists= False
restarting_id_probe= instance spans multiple contigs: {'rmsk_instance_id': '007', 'chrom': 'chr10'}
selected_types= [('rmsk_instance_id', 'string', False), ('consensus_left_bp', 'int64', False), ('rmsk_overlap_flag', 'bool', False)]
pandas_typed_probe= {'rmsk_instance_id': '007', 'consensus_left_bp': -1847, 'rmsk_overlap_flag': False} instance_alias= I|mm39|007
legacy_class_symmetric_difference= [] legacy_prefix= tRNA new_prefix= tRNA
available= {'featureCounts': False, 'Rscript': True, 'duckdb': False} duckdb_python= False
python= 3.11.15 pandas= 2.2.3
```

```bash
python3 -B - <<'PY'
import csv, importlib.util, sys
from pathlib import Path
ref = Path('/workspaces/Meta-Aging/01_modules/.ref')
s = Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/m2-codex')
tax = Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_taxonomy.tsv')
names = {r['rmsk_name'] for r in csv.DictReader(tax.open(), delimiter='\t')}
chosen = sorted({min((n for n in names if c in n), key=lambda n:(len(n), n)) for c in '().-_'})
rows, aliases = [], []
for i, name in enumerate(chosen):
    start, end = 101+i*20, 110+i*20
    alias = f'R|mm39|{name}|chr1|{start}|{end}|+'
    aliases.append(alias)
    attrs = f'gene_id "{name}"; transcript_id "{alias}"; family_id "F"; class_id "C"; locus "{alias}"; instance_id "I|mm39|007";'
    rows.append(f'chr1\trmsk\texon\t{start}\t{end}\t.\t+\t.\t{attrs}\n')
path = s/'names.gtf'
path.write_text(''.join(rows))
print('measured_name_samples=', chosen)
sys.path.insert(0, str(ref/'TEtranscripts'))
for tool, rel in [('TEsingle','TEsingle/TEtools/TEindex.py'), ('TEtranscripts','TEtranscripts/TEToolkit/TEindex.py'), ('TElocal','TElocal/TElocal_Toolkit/TEindex.py')]:
    spec = importlib.util.spec_from_file_location('probe_'+tool, ref/rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    obj = mod.TEfeatures()
    obj.build(str(path))
    wanted = [f'{a}:{n}:F:C:+' for a,n in zip(aliases, chosen)]
    print(tool, 'exact_attribute_tuple=', obj._nameIDmap==wanted)
try:
    spec = importlib.util.spec_from_file_location('probe_stellar', ref/'stellarscope/stellarscope/annotation/utils.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print('Stellarscope exact_locus=', all(mod.GTFFeature(r).attributes['locus']==a for r,a in zip(rows,aliases)))
except ImportError as e:
    print('Stellarscope parser unavailable:', e)
PY
```
```text
measured_name_samples= ['(A)n', '4.5SRNA', 'A-rich', 'B1_Mm']
TEsingle exact_attribute_tuple= True
TEtranscripts exact_attribute_tuple= True
TElocal exact_attribute_tuple= True
Stellarscope exact_locus= True
```

```bash
Rscript --vanilla - <<'RS'
suppressPackageStartupMessages(library(data.table))
x <- fread(text="rmsk_instance_id\tconsensus_left_bp\trmsk_overlap_flag\n007\t-1847\tfalse\n", quote="", na.strings=NULL, colClasses=list(character="rmsk_instance_id", integer64="consensus_left_bp", logical="rmsk_overlap_flag"))
cat("data.table", as.character(packageVersion("data.table")), "id=", x$rmsk_instance_id, "left=", as.character(x$consensus_left_bp), "left_class=", class(x$consensus_left_bp), "flag=", x$rmsk_overlap_flag, "\n")
cat("R_arrow_available=", requireNamespace("arrow", quietly=TRUE), "\n")
RS
```
```text
data.table 1.18.4 id= 007 left= -1847 left_class= integer64 flag= FALSE 
R_arrow_available= FALSE 
```

## Scope check

Before, from the opening commands:
```text
$ git status --short
 M docs/_internal/redesign-2026-09/prompts/m2_codex.md
 M docs/_internal/redesign-2026-09/prompts/m2_divergent.md
 M docs/_internal/redesign-2026-09/prompts/m2_opus.md
$ git branch --show-current
redesign-2026-09
$ git rev-parse HEAD
c28caea8fe9908bb801e79827216de2e00f974ba
```

After:
```text
$ git --no-optional-locks status --short
 M docs/_internal/redesign-2026-09/prompts/m2_codex.md
 M docs/_internal/redesign-2026-09/prompts/m2_divergent.md
 M docs/_internal/redesign-2026-09/prompts/m2_opus.md
?? docs/_internal/redesign-2026-09/reviews/m2_codex.md
```
```bash
python3 -B - <<'PY'
from pathlib import Path
import shutil
s = Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/m2-codex')
shutil.rmtree(s)
print('scratch_exists=', s.exists())
PY
```
```text
scratch_exists= False
```
The sole durable write is `docs/_internal/redesign-2026-09/reviews/m2_codex.md`. Scratch writes were `repo_before.json`, `build_before.json` and `names.gtf` under the directory removed above. The three prompt changes predated this review. No git writes, installations or network access occurred; the orchestrator's build was opened only for reading.
