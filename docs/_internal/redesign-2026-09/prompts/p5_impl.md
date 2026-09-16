# te-tracks phase 5: consumer fixtures

You are the implementer for phase 5 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phases 0 to 4 have landed: read
`AGENTS.md`, `tests/run.sh` (checks are `tests/checks/<mode>/*.sh` and `*.py`, run by name order through `bash`
or `python3`; exit 0 pass, 3 unsupported, other fail; `tests/lib/records.py` supplies `BUILD`, `require` and a
typed TSV reader), `docs/OUTPUTS.md` (export formats and the GTF attribute mapping), `src/lib/build_exports.py`,
`src/lib/build_taxonomy.py` (`resolve`, the rule the fixture's canonical labels come from).

## Read first
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/15_phase5_consumer_fixtures.md` (your phase) and
   the phase 5 rulings in `docs/_internal/redesign-2026-09/reviews/m2_rulings.md` (A4 TElocal index, H2 grain)
2. `docs/_internal/redesign-2026-09/consults/A_consumer_contracts.md` (every parser fact below with its
   source line) and `docs/_internal/redesign-2026-09/audit/AUDIT.md` F9 (IRescue facts)
3. The local read-only consumer checkouts under `/workspaces/Meta-Aging/01_modules/.ref/`:
   `irescue` (v1.2.0), `stellarscope` (1.5), `TEsingle`, `TEtranscripts` (2.2.4), `TElocal` (1.1.3),
   `MATES` (v0.1.8). Read their parsers; write nothing there. Key sites: `irescue/irescue/map.py` lines
   61–84 (custom BED) and 115–133 (auto skip list), `irescue/count.py` 57–84 (name splitting);
   `stellarscope/stellarscope/annotation/_intervaltree.py` 34–60 (grouping, merge, boundary),
   `annotation/utils.py` 60–115 (attribute regex, sentinel); `TEsingle/TEsingle` 92–93 (UR cutoff), 110–135
   (gene index on `transcript` rows), `TEsingle/TEtools/TEindex.py` 287–335 (four-attribute tuple);
   `TEtranscripts/TEToolkit/TEindex.py` 436–437 (`gene_id:family_id:class_id`);
   `TElocal/TElocal` around line 627 (`.locInd` loaded as a pickle) and `TElocal/TElocal_Toolkit/TEindex.py`
   367–420 (the index built from GTF text; four-part feature);
   `MATES/MATES/bam_processor.py` 17–18 (`ref_path.split('.')[0]+'.bed'`), `MATES/scripts/calculate_MU.py`
   271–295 (`?`/`Unknown` groups dropped).
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding)

## Environment facts
Available in-container: python3 with pysam 0.24, pandas, pyarrow, numpy, pytest; `bedtools`, `samtools`.
Absent: `irescue`, `featureCounts`, `stellarscope`, `TEsingle`, `TEcount`, `TElocal`, `duckdb`. The
`/tmp` filesystem is noexec; scratch for generated fixtures is `$TE_TRACKS_REFROOT/fixtures/` (create it).
Parser-level tests import modules from the checkouts by injecting the checkout path into `sys.path`; when an
import fails because a dependency is missing, the check exits 3 naming the module, so "supported" stays
honest. Execution-level tests exit 3 naming the missing executable.

## Deliverables (exact paths)
1. `tests/lib/consumers.py`: tool discovery (`which` plus `--version` capture for irescue, featureCounts,
   stellarscope, TEsingle, TEcount, TElocal, bedtools, samtools), checkout import helper, synthetic data
   builders: a FASTA with two contigs (`chrA` 5,000 bp, `chrB` 3,000 bp, deterministic sequence from a
   fixed seed), a records table with: two records of one subfamily `SubA` (`chrA:1001-1200 +`,
   `chrA:2001-2200 -`), one two-record instance `SubB` + `SubB-int` sharing `.out` ID 7 (`chrA:3001-3100`,
   `chrA:3201-3400`), a missing-family name `NoFam` (raw token `DNA`), a two-label name `TwoLab` (three records:
   two `DNA/hAT-Tip100` on distinct instances and one `DNA/hAT-Blackjack`, so `resolve` elects `hAT-Tip100` by
   plurality 2:1), the boundary record `chrB:101-110 +` named `Edge`, and the coordinate-duplicate pair `DupX`
   and `DupY` (equal coordinates on `chrB`, distinct names). Roster: 11 records, 8 names, 10 instances
   (`SubB` and `SubB-int` share one; `TwoLab`'s three records sit on three). The fixture's `taxonomy_canonical`
   comes from `build_taxonomy.resolve` over the fixture's raw labels with instance counts, and the exports,
   including `subfamily.gtf`, from `src/lib/build_exports.py` on those tables (so the real rule and exporter are
   under test), written under `$TE_TRACKS_REFROOT/fixtures/consumers/`.
   Synthetic BAMs via pysam, sorted and indexed: `arc_3prime.bam` (single cDNA read per molecule, tags `CB`,
   `UB`), `ocm_5prime_pe.bam` (paired mates, `CB`, `UB`), `bulk_pe.bam` (paired, no cell tags). Molecules:
   unique to one record; duplicated (same CB+UB twice); multimapping (two alignments, `NH:2`, one primary);
   gap-only (inside the instance gap `chrA:3101-3200`); boundary-adjacent reads on `chrB` covering
   `[99,100)`, `[100,101)`, `[109,110)`, `[110,111)` in 0-based half-open coordinates against `Edge`
   (GTF `101..110`).
2. Checks under `tests/checks/consumers/` (each prints a first line `supported <tool> <version>` or
   `unsupported: <reason>`):
   - `00_tool_inventory.py`: prints every tool with its version or `absent`; always exit 0.
   - `10_irescue_parser.py`: from the checkout, drive the custom-BED reader with `record.bed` and
     `subfamily.bed` and assert feature counts (11 record features; 8 subfamily names counting `SubB` and
     `SubB-int` separately); assert a name containing `,` splits (documenting the hazard) and that our
     exporter rejects it (import `build_exports` validation).
   - `11_stellarscope_parser.py`: group `record.gtf` by `locus` (11 features) and by `instance_id`
     (10 features: the two-record instance merges); boundary gate on `Edge` with the four reads: expected
     overlaps `0,1,1,0`; when the checkout yields `0,1,1,1` exit 3 with
     `unsupported: stellarscope 1.5 right-boundary overlap defect, observed 0,1,1,1 expected 0,1,1,0`;
     any other result exits 1. Also assert the attribute regex accepts every line of `record.gtf`.
   - `12_tesingle_parser.py`: build the four-attribute tuple through the checkout's TEindex from `record.gtf`
     (record grain: `TwoLab`'s three records give three distinct tuples `<alias>:TwoLab:hAT-Tip100:DNA`, the raw
     labels living in `rmsk_family`; 11 tuples over the fixture) and from `subfamily.gtf` (subfamily grain: one
     tuple `TwoLab:TwoLab:hAT-Tip100:DNA`; 8 tuples over the fixture); assert the UR cutoff semantics on a synthetic
     per-barcode UR count (999 dropped, 1,000 kept) by reading the exact comparison in `TEsingle` lines 92–93.
   - `13_tetranscripts_telocal_parser.py`: TEtranscripts grain `gene_id:family_id:class_id` from
     `record.gtf` yields 8 groups (`TwoLab` one group); TElocal's `.locInd` is built from `record.gtf` through
     the checkout's `TEindex`, written as the pickle TElocal loads, read back through that loader, and yields
     11 four-part features (one per fixture record); the same path over `subfamily.gtf` yields 8.
   - `14_mates_parser.py` (optional adapter): parse an eight-column CSV+BED pair written by a small
     fixture writer in `tests/lib/consumers.py`; assert the stem rule (`record_mates.csv` →
     `record_mates.bed`; `record.mates.csv` breaks) and that `?`/`Unknown` groups are dropped by the model
     preparation code.
   - `20_irescue_exec.sh`: exit 3 `unsupported: irescue absent` when missing; otherwise the subfamily run
     gives `SubA`=2 molecules, the record run 1+1, and the 4/2 versus 3/3 allocation fixture (two records,
     four unique-to-A molecules, two unique-to-B, three shared) yields A=4+x, B=2+(3-x) with EM x reported.
   - `21_featurecounts_exec.sh`: exit 3 when absent; otherwise one SAF feature with two molecules counts 2;
     a one-base feature counts an exactly overlapping read.
   - `22_bedtools_exec.sh`: supported here: `bedtools intersect -wa -wb` of a query against `record.bed`
     for the coordinate-duplicate fixture pair `DupX` and `DupY` preserves both names; a right-adjacent query
     has no hit; `-s`/`-S` strand.
   - `23_samtools_fixture_integrity.sh`: supported: every fixture BAM indexes and `samtools view -c` matches
     the molecule counts the builder intended.
3. `tests/run.sh consumers` output summarises supported/unsupported per tool (the runner already prints
   the first line of each check).
4. `docs/OUTPUTS.md`: a "Consumer contracts" section: one row per consumer with the export it reads (both GTFs
   where a tool's grain follows `transcript_id`), the attribute or column that carries feature identity, the
   fixture that proves it, and its support status in-container; the TElocal row states that its index is built
   from `record.gtf` by TElocal's own indexer. README truth table: fixtures row `tested`, phase 5, with the
   unsupported executables named.

## Rules
- Touch only: `tests/lib/**`, `tests/checks/consumers/**`, `tests/fixtures/consumers/**` (hand-authored
  expected values only; generated data goes under `$TE_TRACKS_REFROOT/fixtures/`), `docs/OUTPUTS.md`,
  `README.md` (truth table). Nothing under `src/` except reading it; nothing under `01_modules/.ref/`.
- No git writes anywhere (the checkouts are git repositories too). No installs. No network.
- Never edit an expected value to match an observed one. Report every deviation.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
for f in tests/run.sh tests/checks/consumers/*.sh; do bash -n "$f" && echo "syntax ok $f"; done
tests/run.sh consumers; echo "exit=$?"     # expect: parser checks pass or unsupported with a named module; bedtools and samtools pass; irescue/featureCounts unsupported; stellarscope boundary gate unsupported with the defect message; exit 0
tests/run.sh core; echo "exit=$?"          # unchanged, pass
ls -la "$TE_TRACKS_REFROOT/fixtures/consumers/"
git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short
for d in irescue stellarscope TEsingle MATES TEtranscripts TElocal; do git -C /workspaces/Meta-Aging/01_modules/.ref/$d status --short | head -3; done   # expect empty
```

## Final message
Every file created or changed; acceptance outputs verbatim; the support matrix (tool → supported/unsupported
→ reason); any deviation.
