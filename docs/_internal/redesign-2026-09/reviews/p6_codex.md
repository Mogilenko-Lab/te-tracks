# Phase 6 review (codex gpt-6-astra)
Verdict: BLOCKING
## Blocking

- [B1] `tests/checks/core/60_contig_aliases.py:59` asserts zero catalog records on two populated contigs. — Catalog counts are `chr4_JH584295v1_random=2` (Low_complexity, Simple_repeat) and `chrM=4` (those classes plus rRNA and tRNA); interspersed counts are zero on exactly these two contigs. The prompt's zero-total assertion is false; the current phase contract at `16_phase6_ensembl_preflight.md:19` already states the corrected facts. — Assert the two interspersed zeros, catalog counts 2/4, no catalog-zero contigs, and totals 5,320,771/3,764,949; update the check's success message. Preserve the measured tables.
- [B2] `tests/checks/core/62_preflight.sh:54` expects complete-assembly contig sets from the 59-contig interspersed exports. — Against the 61-contig FASTA, GENCODE exits **2 instead of 0**, with only-reference `JH584295.1,chrM`; UCSC has **40/38 instead of 39/39** reference-only/export-only names; Ensembl has **23/21 instead of 22/22**. `bin/te-tracks-preflight:90` faithfully implements M1; the acceptance expectations conflict with the observed universe. — Recommend the counting-gate contract: exit 0 for a nonempty export whose contigs all exist at matching lengths, print reference-only contigs informationally, exit 2 for missing export contigs with an agreeing intersection, and exit 1 for a length mismatch or empty intersection. Revise M1, plan, docs and check 62 together; retain the actual difference lists, test both universes in all namespaces and BED/GTF/SAF plus sizes/FAI/BAM. Strict M1 blocks valid restricted annotations and encourages bypassing the gate; subset acceptance can pass an accidentally incomplete/wrong export and cannot establish assembly identity from shared names/lengths. Inventory verification and pinned reference identity must cover that hazard. Under strict M1, check 62 must instead expect the measured 2 and sets above; its 0/39/22 expectations apply to `all_rmsk` alone.
- [B3] `src/lib/build_exports.py:217` and `:235` define different builds; `tests/checks/core/42_exports_fixtures.py:74` consequently fails before testing any expected output. — The fixture declares no `all_rmsk`. Adding that declaration only in scratch produces 8 inventory rows, 46 registrations and 6 catalog BED rows through the CLI; calling `build_exports()` then leaves 7 inventory rows and 40 registrations beside the existing catalog BED. — Use one build entry with explicit export jobs, called by `main()`; preserve explicit interspersed-only jobs for consumer fixtures. Extend check 42 and its allowed fixture scope: declare `all_rmsk`, hand-author its six sorted BED rows (including `Excluded|chr1:5-9|+`, the one-base record and score clipping), append six `(all_rmsk,full,record,rmsk_record_id)` registrations after the existing 40, expect eight UCSC inventory rows (seven with 5 rows, one with 6; catalog distinct features 6), and require identical function/CLI rebuilds and common validation gates.
## Advisory

- [A1] `src/lib/build_exports.py:20`, `:204` and `src/lib/contigs.py:132`: phase 7 must derive semantic `export_contracts` and inventory from the same explicit export definitions. The current seven-file constant omits the complete-catalog job and namespace stage repeats its own eight-path set. The manifest must cover 24 paths, namespace-invariant IDs/grammars, selected universe and coordinates; the catalog BED supports only `(record,rmsk_record_id)`. The measured registration is 347,526,106 bytes; refresh phase 7's retention estimate.
- [A2] `src/lib/build_exports.py:109`, `:120`, `:124` and `src/lib/contigs.py:126`: phase 8 cannot reuse these orchestration functions unchanged: registration/path variant is fixed to `full`, export sets accept only seven files or record BED, and namespace orchestration requires core catalog inputs and eight UCSC files. Expose universe, variant and block bounds for the child and build its six-file inventory. `bin/te-tracks-preflight:38` also requires local `tables/contig_aliases.tsv`, whereas `prompts/p8_impl.md:41` copies only parent IDs; provide a pinned alias/length source for child preflight and carry these dependencies into the newly required phase 8 design consult and its eventual prompt.
- [A3] `docs/DECISIONS.md:26` still enumerates only interspersed exports and record-level GTF. Expand the delivered-scope sentence to include the complete-catalog record BED and the existing subfamily GTF when the orchestrator rules on ADR 3; `docs/OUTPUTS.md:503` already describes the eight-file matrix accurately.

All requested phase-6 source/CLI/check/fixture/doc paths and 24 artifacts exist; the CLI is executable. Five alias columns are injective over 61 rows; FASTA names/lengths and catalog coverage agree. Checks 41/61 verify full-catalog bounds, score clipping, one registration per record, and 10,000 aligned payload rows per export with UCSC IDs retained. All 24 complete data streams pass `LC_ALL=C sort -c -s` on contig/start/end (SAF header skipped), and their full SHA-256 values match inventory. A HEAD-exporter rebuild reproduces each of the seven original inventory rows (header+rows SHA-256 `55a1eb211f91c9ffb12c89b378aeecb9a538fd97ebeb4a20f85627bda9aef501`) and the unchanged 30,119,592-row registration prefix (including header SHA-256 `314098c5c9c2f0c2e09d54f15360fce1f411f4c677550bd358f04bf051ee3c84`). Isolated stages 30/35 reproduce all 24 exports and four generated tables byte-for-byte.
Independent preflight matrix: all seven interspersed files and the catalog BED in each namespace, each against 61-contig sizes, 21 UCSC chromosomes, pysam BAMs (full GENCODE dictionary and `chr1` length 1), and a five-column FAI: **120 calls** with exact independently computed report lists. Full-dictionary BAM/FAI equal the sizes results above; catalog BED sizes/BAM/FAI exits are UCSC 2 (39/39), Ensembl 2 (22/22), GENCODE 0; 21-chromosome exits are 2/1/2 in both universes; wrong-length BAM exits 1 throughout (Ensembl has an empty intersection). SAF column 2 is correct; the prompt's column-1 instruction needs correction.
Mutation evidence, one change per scratch copy: alias `chr1` length +1 fails check 60 at `:29` before its known failure; Ensembl record-BED contig `1 -> 1_BAD` fails check 61 at `:68`; copied-export alias length +1 makes check 62's previously passing wrong-BAM case report `export_length=195154280`; dropping one `all_rmsk` registration fails check 41 at `:132`. Checks 60/62 already fail baseline; the cited additional failures distinguish mutation detection from those known deviations. No added public prose/comment violates the affirmative wording or intent-only rules.
## Acceptance re-run

The commands below ran from the package root with isolated copies of `source/`, `tables/` and `universes.json`; `--refroot` is essential because `tests/run.sh` overrides the environment default. The orchestrator build remained read-only. Shell statements are joined for space; outputs follow verbatim, including the intentionally truncated inventory display.
```bash
export PYTHONDONTWRITEBYTECODE=1; export GIT_OPTIONAL_LOCKS=0; export TMPDIR=/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/tmp; export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot; export LC_ALL=C
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
time bash src/30_build_exports.sh "$TE_TRACKS_REFROOT/te_mm39/build" config/mm39.env; echo "exit=$?"
time bash src/35_build_namespaces.sh "$TE_TRACKS_REFROOT/te_mm39/build" config/mm39.env; echo "exit=$?"
B="$TE_TRACKS_REFROOT/te_mm39/build"; head -3 "$B/tables/contig_aliases.tsv"; grep -E "^chr1_GL456210v1_random|^chrM" "$B/tables/contig_aliases.tsv"; awk -F'\t' '$3==0 || $4==0' "$B/tables/contig_coverage.tsv"
for ns in ucsc ensembl gencode; do wc -l "$B/exports/$ns/interspersed/full/"* "$B/exports/$ns/all_rmsk/full/"*; done
zcat "$B/tables/export_feature_members.tsv.gz" | awk -F'\t' 'NR>1{n[$1]++} END{for(k in n) print k, n[k]}'
head -1 "$B/exports/ensembl/interspersed/full/record.gtf"; head -1 "$B/exports/gencode/interspersed/full/record.gtf"
bin/te-tracks-preflight "$B/exports/gencode/interspersed/full/record.gtf" tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv; echo "exit=$?"
bin/te-tracks-preflight "$B/exports/ucsc/interspersed/full/record.gtf" tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv | tail -3; echo "exit=${PIPESTATUS[0]}"
cut -f1,2,7,9 "$B/tables/exports.tsv" | cut -c1-90
tests/run.sh core --refroot "$TE_TRACKS_REFROOT"; echo "exit=$?"
git status --short
```
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
[30_build_exports] UCSC exports ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ucsc

real	2m57.499s
user	2m54.569s
sys	0m13.831s
exit=0
namespace=ensembl exports=8
namespace=gencode exports=8
aliases=61 coverage=61 inventory=24
[35_build_namespaces] Contig namespaces ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports

real	1m22.933s
user	1m23.883s
sys	0m31.732s
exit=0
chrom_ucsc	chrom_ensembl	chrom_gencode	chrom_genbank	chrom_refseq	length_bp
chr1	1	chr1	CM000994.3	NC_000067.7	195154279
chr10	10	chr10	CM001003.3	NC_000076.7	130530862
chr1_GL456210v1_random	GL456210.1	GL456210.1	GL456210.1	NT_166280.1	169725
chrM	MT	chrM	AY172335.1	NC_005089.1	16299
chr4_JH584295v1_random	1976	2	0	true	true	true
chrM	16299	4	0	true	true	true
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ucsc/interspersed/full/family.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ucsc/interspersed/full/record.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ucsc/interspersed/full/record.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.gtf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.saf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ucsc/interspersed/full/taxonomy_triple.saf
   5320771 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ucsc/all_rmsk/full/record.bed
  31675416 total
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ensembl/interspersed/full/family.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ensembl/interspersed/full/record.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ensembl/interspersed/full/record.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ensembl/interspersed/full/subfamily.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ensembl/interspersed/full/subfamily.gtf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ensembl/interspersed/full/subfamily.saf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ensembl/interspersed/full/taxonomy_triple.saf
   5320771 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/ensembl/all_rmsk/full/record.bed
  31675416 total
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/gencode/interspersed/full/family.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/gencode/interspersed/full/record.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/gencode/interspersed/full/record.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/gencode/interspersed/full/subfamily.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/gencode/interspersed/full/subfamily.gtf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/gencode/interspersed/full/subfamily.saf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/gencode/interspersed/full/taxonomy_triple.saf
   5320771 /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p6/refroot/te_mm39/build/exports/gencode/all_rmsk/full/record.bed
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
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/02_orchestration.md
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/16_phase6_ensembl_preflight.md
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md
 M docs/_internal/_project/session.md
 M docs/_internal/redesign-2026-09/prompts/p6_impl.md
 M docs/_internal/redesign-2026-09/prompts/p7_impl.md
 M src/30_build_exports.sh
 M src/lib/build_exports.py
 M tests/checks/core/41_export_registration.py
?? bin/
?? docs/_internal/redesign-2026-09/prompts/p6_opus.md
?? docs/_internal/redesign-2026-09/prompts/p6_review.md
?? docs/_internal/redesign-2026-09/reviews/p6_rulings.md
?? src/35_build_namespaces.sh
?? src/lib/contigs.py
?? tests/checks/core/60_contig_aliases.py
?? tests/checks/core/61_namespace_exports.py
?? tests/checks/core/62_preflight.sh
?? tests/fixtures/contigs/
```
## Scope check

Initial `git diff HEAD --stat`: 8 files, 239 insertions, 102 deletions; final: 12 files, 257 insertions, 104 deletions. The status above is verbatim before adding this review. Implementation edits stay within the prompt's allowed paths, including README truth-table changes and the single ADR-3 sentence. Existing `prompts/p6_impl.md`, `p7_impl.md`, `p6_opus.md`, `p6_review.md` are orchestration records; concurrent external changes added plan 02/16/18 and session edits plus `reviews/p6_rulings.md`. Fingerprints of the implementation files stayed identical throughout review; HEAD/reflog remain `c2a7a43`. Reviewer writes are this report and the removed `review-p6/` scratch tree; no installs, network or git mutation commands. The protected build's file set, sizes, mtimes and inodes are unchanged.
The nine original `.ref` checkouts (DfamTEBrowser, MATES, TElocal, TEsingle, TEtranscripts, irescue, mLLMCelltype, mascarade, stellarscope) were clean before and after, with zero `.pyc`, `.pyo` or `__pycache__`. The blanket all-`.ref` condition is now false: an externally created `14839-DM-cGAS/` tree appeared during review, holding 43 `.pyc` files; its nested `13036-DM_DMlab_summer_2025` and `Yasmine_RetroT` repositories report 4 and 514 changed entries, and three copied submodule git links cannot resolve. These paths were untouched by this reviewer; every reviewer Python invocation inherited `PYTHONDONTWRITEBYTECODE=1`.
