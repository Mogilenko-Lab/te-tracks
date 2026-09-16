# Phase 5 re-review (Opus)
Verdict: FAIL

## Blocking

- **[B1] `tests/checks/consumers/11_stellarscope_parser.py:14` — the required Stellarscope parser test never executes.** `checkout_import` resolves `stellarscope.annotation._intervaltree` through `stellarscope/__init__.py:8`, which needs `setuptools_scm` (absent); `intervaltree` is present. Loading `stellarscope/annotation/__init__.py` with `spec_from_file_location(..., submodule_search_locations=...)` and importing `utils`/`_intervaltree` beneath it gives 11 loci by `locus`, 10 by `instance_id`, uniform attribute sets, `{}` for the gap read, and boundary `0,1,1,1`. With a scratch-only `setuptools_scm` shim the **unmodified** check exits 3 with `stellarscope 1.5 right-boundary overlap defect, observed 0,1,1,1 expected 0,1,1,0`, and exits 1 under mutation (edge_100→98 gives `[0,0,1,1]`; `gene_id`→`gene-id` trips the attribute assertion). Agree with codex and the orchestrator. Fix: load the subpackage directly; reserve `unsupported` for `intervaltree`.

- **[B2] `tests/checks/consumers/10_irescue_parser.py:15,24` — `chrcat` is never called, and record-grain identity has no oracle at all.** Beyond codex's B2: I replaced **every** `record.bed` name with `JUNK0…JUNK10` → exit 0; I shifted **every** record coordinate by +500 → exit 0. Line 25 asserts only `len(names) == 11`; the `names == set(EXPECTED["taxonomy"])` identity assertion runs in the `subfamily` branch alone. Codex's own mutation (one subfamily name → `BROKEN`) also tripped a *count* assertion, not an identity one. The check therefore cannot fail on wrong record identities — the milestone's stated property ("feature identity survives every tool"). Fix: assert `names == {record_key(row) for row in ROSTER}` at record grain and exercise real `chrcat`.

- **[B3] `tests/lib/consumers.py:88` — every `ImportError` becomes `unsupported`; four distinct false classes.** Probes through the real `run_check`: `from numpy import definitely_not_a_symbol` → exit 3, `unsupported: probe python module numpy absent`; a checkout-internal `ImportError(name='irescue.map')` → exit 3; a bare `ImportError('no name attribute')` → the message text is printed as the module name; `import pandas` followed by a typo'd `from pandas import DataFramez` → `python module pandas absent`. Observed live, not only synthetically: running check 10 with `src/lib` off `sys.path` printed `unsupported: irescue python module build_exports absent` and the runner still exited 0. Agree with codex; the evidence is broader than reported.

- **[B4] The `chrcat` fix the ruling prescribes cannot run in this container — `gawk` is absent.** `map.py:384` builds the features file with `gawk … gensub(/#.+/,"",1,$1)`. Here `awk` is mawk 1.3.4 (`function gensub never defined`) and `gawk` is not on `PATH`. I ran the real `chrcat` on 11 synthetic intersection rows: `cmd0`/`cmd1` succeed (mappings 11 rows, barcodes written, bedtools groupby fine), `cmd2` writes a 20-byte empty gzip, and `chrcat` raises `SystemExit` via `writerr(..., error=True)`. The fix round must either declare `gawk` a consumers-mode dependency or report that sub-assertion unsupported naming `gawk` — which contradicts `15_phase5_consumer_fixtures.md:11` ("always supported"). Ruling B2 as written is not executable here.

- **[B5] `docs/OUTPUTS.md:451` and `README.md:64` name the wrong blocking module for MATES.** `pyranges` is reached only through `MATES/__init__.py` → `scripts/Ref2csv.py`; no code path the adapter check exercises imports it. `MATES/bam_processor.py:4` imports `pkg_resources` directly, and setuptools 83 no longer ships it — that is the module the adapter itself needs. Confirming codex's MATES claim required three scratch substitutions, not one isolation: package shells for `MATES`/`MATES.scripts`, a `pkg_resources` shim, and binding `start_split_count` onto the shell. With those, the unmodified check passes (exit 0: dotted stem rejected pointing at `record.bed`; filter keeps `{'cell': {'L1': [0,1,2]}}`) and fails (exit 1) when one BED name is broken. So the assertions are sound; calling this "isolate these source imports" understates it, since a `pkg_resources` stub fabricates an absent third-party module.

## Advisory

- **[A1] Nondeterminism is in the checks, not the builder.** Two independent `build_fixture()` runs into different roots produced 45/45 byte-identical files, all equal to the orchestrator's — `records_io.write_tsv` is already deterministic. The 7 differing files are written *by checks*: the five `irescue_*.tsv.gz` use bare `gzip.open(..., "wt")` (MTIME `1789586559` vs `1789586573`, payload md5 identical), and the two `.locInd` embed `TEfeatures.__srcfile` (`TEindex.py:367`) — one differing byte at offset 1930/1324 between roots of equal path length. The fix belongs in `10_irescue_parser.py:29,34,41` (mtime 0), not in the library. Agree with codex; codex's 2,009/1,406 were its own root's sizes — the orchestrator's are 1,993/1,390.
- **[A2] Literal versions — achievable everywhere, from three different sources.** `setup.py` carries TEsingle 1.0, TEtranscripts 2.2.4, TElocal 1.1.3, MATES 0.1.8; irescue 1.2.0 lives in `irescue/_version.py` and `10:18` already asserts it. Stellarscope's `pyproject.toml:18` is `dynamic = ["version"]` with no static string — read `git describe --tags` (HEAD is exactly tag `1.5`) or pin the checkout SHA. Agree with codex.
- **[A3] `UB` and `UR` are identical on every fixture read** (`consumers.py:188`), and `umi_sequences` enforces Hamming ≥ 4, so no correction is ever exercised. TEsingle keys on `UR` (`AlignmentIO.py:44`) and IRescue on `UB`; these fixtures cannot tell the two apart, nor catch a tool reading the wrong tag.
- **[A4] No read carries flag 16, `is_duplicate` or `is_qcfail`**, and featureCounts runs `-s 0`, so read-level strandedness is untested although two roster records are on `-`. TEsingle's `read_in_alignment` skips duplicate/qcfail reads; that filter is never reached.
- **[A5] The MATES check writes into the fixture root.** Under `chdir(FIXTURES)` it creates `samples.txt`, `bam_paths.txt`, `barcodes_paths.txt`, `barcodes.txt`, `record.mates.{csv,bed}`, `count_coverage/` and `MU_Stats/`, mixing consumer outputs into the input directory once B1 lands.
- **[A6] `00_tool_inventory.py` has no oracle** — it cannot fail. Consistent with the contract's reporting sentence; worth stating as reporting-only.
- **[A7] The contract contradicts itself**: parser tests "always supported" against Stellarscope "label the consumer version unsupported until fixed upstream", so acceptance's "every parser test passes" cannot hold while 1.5 is pinned.
- **[A8] Scope**: six phase 6–9 planning files are modified outside phase 5's allowed set. Agree with codex.
- **Prose**: the `docs/OUTPUTS.md` and `README.md` additions are affirmative, carry no contrastive negation, and the check docstrings are one-line intent statements. The only wording defects are factual (B5) and the `README.md:64` gap list, which should read `setuptools_scm`, `pkg_resources`.

## Numbers recomputed

| quantity | contract | observed | command |
|---|---|---|---|
| records / names / instances | 11 / 8 / 10 | 11 / 8 / 10 | own parse of `record.bed`, `record.gtf` attrs |
| exports | seven | 7 (`record/subfamily/family.bed`, `record/subfamily.gtf`, `subfamily/taxonomy_triple.saf`) | `ls exports/ucsc/interspersed/full` |
| families | — | 5 | distinct `family.bed` col 4 |
| TwoLab plurality | 2:1 → `hAT-Tip100` | 2:1, `resolved_plurality`, share 0.667 | `taxonomy_canonical.tsv` |
| BED↔GTF convention | half-open vs 1-based | `bed_start == gtf_start-1`, ends equal, 11/11 | own join |
| boundary reads (0-based) | `[99,100) [100,101) [109,110) [110,111)` | exact, all `1M`, `chrB` | own pysam `get_blocks()` |
| Stellarscope gate | expect `0,1,1,0` | `0,1,1,1` (real source and my reimplementation) | direct subpackage load |
| Edge tree interval | — | `addi(101,111)` vs true `[100,110)`; query `[b_start,b_end+1)` — errors cancel left, compound right | `_intervaltree.py:55,81` |
| BAM alignments/templates/molecules | `expected.json` | all 11 BAMs match exactly | own pysam census |
| `NH:2` multimappers | present | arc 2, ocm/bulk 4, allocation 6/12 | own pysam |
| TEsingle UR cutoff | 999 dropped, 1000 kept | `(init,post)=(2,1)`, boundary 999 F / 1000 T | real `Counters.basic_filtering` |
| fixture files / nondeterministic | — | 53 total, 45 deterministic, 7 not | two full suite runs into two roots |
| consumers suite | — | `checks=11 pass=6 fail=0 unsupported=5`, exit 0 | `tests/run.sh consumers --refroot <scratch>` |

**(g)** Byte-nondeterministic: `irescue_{record,subfamily}_{features,maps}.tsv.gz` and `irescue_comma_maps.tsv.gz` (gzip MTIME header, bytes 4–7; payloads identical) and `record.locInd` / `subfamily.locInd` (absolute GTF path stored in `TEfeatures.__srcfile`). Everything `build_fixture()` writes is reproducible byte-for-byte.

**(h)** The UR-cutoff path executes `TEtools.Counters.basic_filtering(bcumi_dict, cutoff)` from `/workspaces/Meta-Aging/01_modules/.ref/TEsingle/TEtools/Counters.py:244` — the only caller in the tool is `TEsingle:140`. It deletes barcodes where `len(bcumi_dict[cbc]) < cutoff` and returns `(dict, init, post)`, so the `<` gives 999-dropped / 1000-kept. The `1000` default is read by AST from `TEsingle:92`, not executed. The dict it counts is built by `TEtools/AlignmentIO.py:44`, which keys on the **`UR`** tag — that function is not exercised, so "UR" here is documentation of the upstream key rather than a tested property; `basic_filtering` itself is UMI-agnostic.

## Agreement with codex review

- **B1 Stellarscope** — agree; independently reproduced 11/10/`0,1,1,1` and a passing-then-exit-3 run under a scratch shim.
- **B1 MATES** — agree the assertions hold under isolation, disagree with the framing: it needs a `pkg_resources` stub plus two package shells, and `pyranges` blocks nothing the adapter touches (see B5).
- **B2 `chrcat`** — agree, and the gap is larger: record-grain names and coordinates are unchecked (B2). The prescribed fix is blocked by absent `gawk` (B4).
- **B3 ImportError classification** — agree; four false-unsupported classes, one of them observed in a real breakage.
- **A1 fixture nondeterminism** — agree on the 7/53 count and both mechanisms; disagree on locus — `build_fixture` is deterministic, the checks are not, so the fix belongs in `10_irescue_parser.py`.
- **A2 literal versions** — agree, with the caveat that Stellarscope has no static version to read.
- **Scope note (phase 6–9 files)** — agree.

No git write occurred: `reflog -1` is still `3837814 Phase 4`, the 274 tracked-plus-phase-5 file md5s are identical before and after, all nine `.ref` checkouts are clean at their entry SHAs with no new bytecode, and the orchestrator's 53 fixture files are untouched. Scratch under `_scratch/te-tracks-audit/opus-p5/` removed.
