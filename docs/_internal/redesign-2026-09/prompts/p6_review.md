# te-tracks phase 6 review (codex, read-only)

You are an independent reviewer of phase 6 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`, HEAD `c2a7a43`). The implementer has
finished; you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p6_codex.md`. You change nothing else. No git writes, no installs, no
network. Scratch work goes under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/` and is removed when you
finish; set `PYTHONDONTWRITEBYTECODE=1` for every python invocation. The orchestrator's build at
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` is read-only for you.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/16_phase6_ensembl_preflight.md`
   and the rulings that land in it: `reviews/m2_rulings.md` (M1 preflight exits, M5 namespace-invariant
   registration), `reviews/m5_rulings.md` (codex A2 inventory union; divergent H2 `all_rmsk` record BED).
2. The implementer's prompt: `docs/_internal/redesign-2026-09/prompts/p6_impl.md` (facts and numeric targets).
3. The decisions: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` entries 3, 5.
4. The wording and comment rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".
5. The implementer's changes: `git diff HEAD --stat`, the full diff, and untracked files from `git status --short`.
6. The implementer's own report, pasted below under "Implementer report".

## Judge, with evidence
- **Contract conformance**: every deliverable at the stated path with the stated content; every acceptance command
  re-run by you with its output quoted; any number that differs from the contract named.
- **Alias table**: 61 rows; each name column injective; `chr1_GL456210v1_random` → `GL456210.1` in both `ensembl`
  and `gencode`; `chrM` → `MT` / `chrM`; the gencode column equals the 61 FASTA names with equal lengths; every
  `chrom` in `rmsk_records` present; interspersed coverage zeros exactly on `chr4_JH584295v1_random` and `chrM`,
  whose catalog counts are 2 and 4 (Low_complexity, Simple_repeat, rRNA and tRNA records).
- **Namespace copies**: for each of the seven interspersed exports and the `all_rmsk` BED, the `ensembl` and
  `gencode` files hold the same rows as `ucsc` with the contig column renamed and nothing else changed (align by
  `rmsk_record_id` or the GTF alias on a sample of at least 10,000 rows); each file sorted by its own contig column in
  C-locale byte order, then start and end numerically (`LC_ALL=C sort -c`); the alias and record ids inside keep UCSC
  names.
- **Inventory and registration**: `tables/exports.tsv` has 24 rows whose sha256 values match the files; the seven
  `ucsc` interspersed rows are byte-identical to the milestone 5 inventory (the orchestrator's baseline sha of the
  old file is `55a1eb21…`; compare row by row); the registration holds the 30,119,592 interspersed rows unchanged
  and 5,320,771 `all_rmsk` rows (level `record`, grammar `rmsk_record_id`, one per catalog record, after the
  interspersed rows).
- **Preflight**: run it yourself against the fixture sizes file, a 21-chromosome UCSC-named sizes file and a synthetic
  BAM header you write with pysam, for the interspersed exports and for the `all_rmsk` BED in each namespace. Measured
  fact: the interspersed universe has zero records on `chrM` and `chr4_JH584295v1_random`, so its exports name 59 of
  the 61 contigs while the `all_rmsk` BED names all 61. The implementer compares the export's observed contigs
  literally, so `gencode` interspersed against the GENCODE FASTA exits 2 with the two contigs under
  `only_in_reference`, and the plan's exit 0 holds for the `all_rmsk` BED alone (0; `ucsc` 2 with 39 scaffolds each
  way; `ensembl` 2 with 22 chromosomes each way; 1 against the 21-chromosome file). Judge which exit contract serves
  the handoff gate `te-tracks-preflight <export> <bam> && featureCounts …`: ruling M1 as written, or exit 0 whenever
  every export contig is present in the reference with an agreeing length, reference-only contigs printed for
  information, exit 2 reserved for export contigs the reference lacks (features a counter would drop), exit 1 for a
  length disagreement or an empty intersection. State your recommendation and the hazard each choice leaves open.
- **Builder entry points**: `src/lib/build_exports.py` now has `build_exports()` writing the interspersed set alone
  and `main()` writing both universes; check 42 imports the function and also runs the stage script, and its fixture
  `tests/fixtures/exports/universes.json` declares no `all_rmsk`. Judge whether one entry should define the export
  sets, and state what the fixture needs (expected `all_rmsk` BED rows, registration rows, inventory rows) for check
  42 to exercise the complete-catalog BED.
- **Known deviations**: check 60's zero-record assertion, check 62's expectations and check 42's fixture fail today
  (the implementer's report below). The orchestrator rules on them after your review; state what each check should
  assert.
- **Fixture adequacy**: on scratch copies, break one thing per check 60, 61, 62 and per check 41's extension (a
  renamed contig, a changed length, a dropped `all_rmsk` row) and name the check that fails.
- **Silent assumptions**: anything that will bite phase 7 (the manifest's `export_contracts` and inventory) or phase
  8 (the child exporter's explicit universe, variant and block inputs).
- **Wording rule**: contrastive negation, history or provenance chatter in public files or comments.
- **Scope**: files touched outside the prompt's allowed set; every checkout under `/workspaces/Meta-Aging/01_modules/.ref/`
  clean with no bytecode written.

## Output format (the review file)
```
# Phase 6 review (codex gpt-6-astra)
Verdict: PASS | PASS WITH ADVISORIES | BLOCKING
## Blocking
- [B1] <file:line> <finding> — <evidence> — <what fixes it>
## Advisory
- [A1] ...
## Acceptance re-run
<commands and outputs, verbatim>
## Scope check
<git status / diff --stat summary; checkout status>
```
BLOCKING means a contract deliverable is missing or wrong, an acceptance number differs, or a check cannot fail.
Keep the file under 200 lines. Facts over opinions; every finding cites a path and, where possible, a line.

## Implementer report
Implemented phase 6. Both build stages exit 0; core acceptance reports **13 passed, 3 failed**.

The GENCODE rule reproduces **all 61 FASTA names and lengths exactly**.

Deviations requiring resolution:

- `chr4_JH584295v1_random` and `chrM` contain **2 and 4 total records**, respectively; both contain zero interspersed records. Check 60 retains the requested zero-total assertion and fails.
- Interspersed exports contain 59 contigs. Literal export-contig comparison therefore gives GENCODE preflight exit **2**, listing `JH584295.1` and `chrM` only in the reference. Check 62 exposes the incompatible expectations. The GENCODE `all_rmsk` BED passes against all 61 contigs.
- Check 42’s fixture lacks `all_rmsk` and expects seven exports. Its required updates are outside the allowed paths, so it remains unchanged and fails.
- SAF contigs are read from column 2 (`Chr`), consistent with the existing SAF schema.

Created:

- [src/lib/contigs.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/lib/contigs.py)
- [src/35_build_namespaces.sh](/workspaces/Meta-Aging/01_modules/te-tracks/src/35_build_namespaces.sh)
- [bin/te-tracks-preflight](/workspaces/Meta-Aging/01_modules/te-tracks/bin/te-tracks-preflight)
- [tests/checks/core/60_contig_aliases.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/60_contig_aliases.py)
- [tests/checks/core/61_namespace_exports.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/61_namespace_exports.py)
- [tests/checks/core/62_preflight.sh](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/62_preflight.sh)
- [tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv](/workspaces/Meta-Aging/01_modules/te-tracks/tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv)

Changed:

- [src/lib/build_exports.py](/workspaces/Meta-Aging/01_modules/te-tracks/src/lib/build_exports.py)
- [src/30_build_exports.sh](/workspaces/Meta-Aging/01_modules/te-tracks/src/30_build_exports.sh)
- [tests/checks/core/41_export_registration.py](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/41_export_registration.py)
- [docs/OUTPUTS.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/OUTPUTS.md)
- [docs/DECISIONS.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/DECISIONS.md)
- [README.md](/workspaces/Meta-Aging/01_modules/te-tracks/README.md)

Scratch outputs comprise the 24 exports listed below and `tables/{contig_aliases.tsv,contig_coverage.tsv,exports.tsv,export_feature_members.tsv.gz}`. Prompt-file changes shown by git belong to other work. No git writes, installs, or network access were performed.

Acceptance outputs verbatim, grouped in the requested command order:

```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok src/10_build_records.sh
syntax ok src/15_build_universes.sh
syntax ok src/20_build_taxonomy.sh
syntax ok src/30_build_exports.sh
syntax ok src/35_build_namespaces.sh
syntax ok tests/run.sh
universe=interspersed records=3764949 subfamilies=1220 families=49 taxonomy_triples=1220 instances=3152636 exports=7 registrations=30119592
universe=all_rmsk records=5320771 subfamilies=0 families=0 taxonomy_triples=0 instances=4696900 exports=1 registrations=5320771
[30_build_exports] UCSC exports ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc

real	2m51.083s
user	2m46.951s
sys	0m15.055s
exit=0
namespace=ensembl exports=8
namespace=gencode exports=8
aliases=61 coverage=61 inventory=24
[35_build_namespaces] Contig namespaces ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports

real	1m17.024s
user	1m16.374s
sys	0m31.958s
exit=0
chrom_ucsc	chrom_ensembl	chrom_gencode	chrom_genbank	chrom_refseq	length_bp
chr1	1	chr1	CM000994.3	NC_000067.7	195154279
chr10	10	chr10	CM001003.3	NC_000076.7	130530862
chr1_GL456210v1_random	GL456210.1	GL456210.1	GL456210.1	NT_166280.1	169725
chrM	MT	chrM	AY172335.1	NC_005089.1	16299
chr4_JH584295v1_random	1976	2	0	true	true	true
chrM	16299	4	0	true	true	true
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/family.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/record.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/record.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.gtf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.saf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/taxonomy_triple.saf
   5320771 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/all_rmsk/full/record.bed
  31675416 total
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ensembl/interspersed/full/family.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ensembl/interspersed/full/record.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ensembl/interspersed/full/record.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ensembl/interspersed/full/subfamily.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ensembl/interspersed/full/subfamily.gtf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ensembl/interspersed/full/subfamily.saf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ensembl/interspersed/full/taxonomy_triple.saf
   5320771 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ensembl/all_rmsk/full/record.bed
  31675416 total
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/gencode/interspersed/full/family.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/gencode/interspersed/full/record.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/gencode/interspersed/full/record.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/gencode/interspersed/full/subfamily.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/gencode/interspersed/full/subfamily.gtf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/gencode/interspersed/full/subfamily.saf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/gencode/interspersed/full/taxonomy_triple.saf
   5320771 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/gencode/all_rmsk/full/record.bed
  31675416 total
interspersed 30119592
all_rmsk 5320771
1	te-tracks	exon	3050294	3050775	3667	+	.	gene_id "L1MdA_VI"; transcript_id "R|mm39|L1MdA_VI|chr1|3050294|3050775|+"; locus "R|mm39|L1MdA_VI|chr1|3050294|3050775|+"; family_id "L1"; class_id "LINE"; rmsk_family "L1"; rmsk_class "LINE"; instance_id "I|mm39|1"; rmsk_record_id "L1MdA_VI|chr1:3050294-3050775|+";
GL456210.1	te-tracks	exon	1275	1456	1585	+	.	gene_id "MERVL-int"; transcript_id "R|mm39|MERVL-int|chr1_GL456210v1_random|1275|1456|+"; locus "R|mm39|MERVL-int|chr1_GL456210v1_random|1275|1456|+"; family_id "ERVL"; class_id "LTR"; rmsk_family "ERVL"; rmsk_class "LTR"; instance_id "I|mm39|2174121"; rmsk_record_id "MERVL-int|chr1_GL456210v1_random:1275-1456|+";
only_in_reference	["JH584295.1","chrM"]
only_in_export	[]
length_disagreements	[]
exit=2
only_in_reference	["GL456210.1","GL456211.1","GL456212.1","GL456219.1","GL456221.1","GL456233.2","GL456239.1","GL456354.1","GL456359.1","GL456360.1","GL456366.1","GL456367.1","GL456368.1","GL456370.1","GL456372.1","GL456378.1","GL456379.1","GL456381.1","GL456382.1","GL456383.1","GL456385.1","GL456387.1","GL456389.1","GL456390.1","GL456392.1","GL456394.1","GL456396.1","JH584295.1","JH584296.1","JH584297.1","JH584298.1","JH584299.1","JH584300.1","JH584301.1","JH584302.1","JH584303.1","JH584304.1","MU069434.1","MU069435.1","chrM"]
only_in_export	["chr1_GL456210v1_random","chr1_GL456211v1_random","chr1_GL456212v1_random","chr1_GL456221v1_random","chr1_GL456239v1_random","chr1_MU069434v1_random","chr5_GL456354v1_random","chr5_JH584296v1_random","chr5_JH584297v1_random","chr5_JH584298v1_random","chr5_JH584299v1_random","chr7_GL456219v1_random","chrUn_GL456359v1","chrUn_GL456360v1","chrUn_GL456366v1","chrUn_GL456367v1","chrUn_GL456368v1","chrUn_GL456370v1","chrUn_GL456372v1","chrUn_GL456378v1","chrUn_GL456379v1","chrUn_GL456381v1","chrUn_GL456382v1","chrUn_GL456383v1","chrUn_GL456385v1","chrUn_GL456387v1","chrUn_GL456389v1","chrUn_GL456390v1","chrUn_GL456392v1","chrUn_GL456394v1","chrUn_GL456396v1","chrUn_JH584304v1","chrUn_MU069435v1","chrX_GL456233v2_random","chrY_JH584300v1_random","chrY_JH584301v1_random","chrY_JH584302v1_random","chrY_JH584303v1_random"]
length_disagreements	[]
exit=2
export_path	namespace	rows	sha256
exports/ensembl/all_rmsk/full/record.bed	ensembl	5320771	7c971a972aba99e720466a309e7488b76
exports/ensembl/interspersed/full/family.bed	ensembl	3764949	52c36e4026c06bae74041c579d6e3
exports/ensembl/interspersed/full/record.bed	ensembl	3764949	1d08f7c55c184fcef1b2dca08bd32
exports/ensembl/interspersed/full/record.gtf	ensembl	3764949	362858e6d03f94a3ee4f58a4e18c6
exports/ensembl/interspersed/full/subfamily.bed	ensembl	3764949	b3305f5473460571255f4be2da
exports/ensembl/interspersed/full/subfamily.gtf	ensembl	3764949	15602b3138e1967a077d6e12d9
exports/ensembl/interspersed/full/subfamily.saf	ensembl	3764949	80305f956935ed42703a02cf3b
exports/ensembl/interspersed/full/taxonomy_triple.saf	ensembl	3764949	7d839d473e22bae23725
exports/gencode/all_rmsk/full/record.bed	gencode	5320771	09911e35957fb98bd75164bdc7c8f1318
exports/gencode/interspersed/full/family.bed	gencode	3764949	f9158dde724896a5a0a05f85e07f6
exports/gencode/interspersed/full/record.bed	gencode	3764949	b7a3f9c588843b3f817fcd573a02e
exports/gencode/interspersed/full/record.gtf	gencode	3764949	b6b0668ae526bfc14c49cc8beb45b
exports/gencode/interspersed/full/subfamily.bed	gencode	3764949	a4c17666d6316e7536b5fec934
exports/gencode/interspersed/full/subfamily.gtf	gencode	3764949	7c4f6516514d65742f6c73730f
exports/gencode/interspersed/full/subfamily.saf	gencode	3764949	796de6493a5b908ce265a4e11e
exports/gencode/interspersed/full/taxonomy_triple.saf	gencode	3764949	63862eac97f623d97b5c
exports/ucsc/all_rmsk/full/record.bed	ucsc	5320771	801cc731771cc23e59730dc5828eb4a72f62e64
exports/ucsc/interspersed/full/family.bed	ucsc	3764949	892a1a7a6f842a7c57b1fc7c05448f13c14
exports/ucsc/interspersed/full/record.bed	ucsc	3764949	78afc63310a6cc621ea203df8a58711edc7
exports/ucsc/interspersed/full/record.gtf	ucsc	3764949	859c5f0db4949082fafa08f25cf776c346b
exports/ucsc/interspersed/full/subfamily.bed	ucsc	3764949	7a2311a02931bad5b3af39ff5c01eee1
exports/ucsc/interspersed/full/subfamily.gtf	ucsc	3764949	00a0e6859a9f4200f574ac3f9754130b
exports/ucsc/interspersed/full/subfamily.saf	ucsc	3764949	ef4145d75213662c11844f0c69240cb9
exports/ucsc/interspersed/full/taxonomy_triple.saf	ucsc	3764949	3da80b1449962220e638b1c5ce
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
pass  40_exports_shape.py  seven exports: 3764949 rows each; subfamilies=1220 families=49 taxonomy_triples=1220; coordinates and identifiers pass
pass  41_export_registration.py  registrations: interspersed=30119592 all_rmsk=5320771; eight interspersed ID spellings; instances=3152636; 24 inventory hashes, feature sets and GTF tuple/instance joins pass; three record grammars; count 7 stays 7 at record, subfamily and family levels
Traceback (most recent call last):
  File "/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/42_exports_fixtures.py", line 74, in <module>
    assert completed.returncode == 0, completed.stderr
           ^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: build_exports: undeclared export universe: 'all_rmsk'

fail  42_exports_fixtures.py
Traceback (most recent call last):
  File "/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/60_contig_aliases.py", line 60, in <module>
    assert set(coverage.loc[coverage[column].eq(0), "chrom_ucsc"]) == {"chr4_JH584295v1_random", "chrM"}, (
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ('records_all', {'chr4_JH584295v1_random': 2, 'chrM': 4})
fail  60_contig_aliases.py
pass  61_namespace_exports.py  24 sorted exports and SHA-256 digests; 10000 aligned rows per file; interspersed=3764949 all_rmsk=5320771 per namespace; registrations=30119592+5320771
fail  62_preflight.sh
  preflight contract deviations:
  gencode/record.gtf vs gencode_grcm39_fasta_contigs.tsv: expected exit=0; observed exit=2; report differences={'only_in_reference': {'missing': [], 'extra': ['JH584295.1', 'chrM']}, 'only_in_export': {'missing': [], 'extra': []}, 'length_disagreements': []}; stderr=''
  ucsc/record.gtf vs gencode_grcm39_fasta_contigs.tsv: expected exit=2; observed exit=2; report differences={'only_in_reference': {'missing': [], 'extra': ['chrM']}, 'only_in_export': {'missing': ['chr4_JH584295v1_random'], 'extra': []}, 'length_disagreements': []}; stderr=''
  ensembl/record.gtf vs gencode_grcm39_fasta_contigs.tsv: expected exit=2; observed exit=2; report differences={'only_in_reference': {'missing': [], 'extra': ['JH584295.1']}, 'only_in_export': {'missing': ['MT'], 'extra': []}, 'length_disagreements': []}; stderr=''
checks=16 pass=13 fail=3 unsupported=0
exit=1
 M README.md
 M docs/DECISIONS.md
 M docs/OUTPUTS.md
 M docs/_internal/redesign-2026-09/prompts/p6_impl.md
 M docs/_internal/redesign-2026-09/prompts/p7_impl.md
 M src/30_build_exports.sh
 M src/lib/build_exports.py
 M tests/checks/core/41_export_registration.py
?? bin/
?? docs/_internal/redesign-2026-09/prompts/p6_opus.md
?? docs/_internal/redesign-2026-09/prompts/p6_review.md
?? src/35_build_namespaces.sh
?? src/lib/contigs.py
?? tests/checks/core/60_contig_aliases.py
?? tests/checks/core/61_namespace_exports.py
?? tests/checks/core/62_preflight.sh
?? tests/fixtures/contigs/
```

