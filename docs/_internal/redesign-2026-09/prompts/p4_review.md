# te-tracks phase 4 review (codex, read-only)

You are an independent reviewer of phase 4 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p4_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md`
2. The decisions: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md`
3. The wording and comment rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments"
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD --stat` and the full
   diff, plus untracked files from `git status --short`.
5. The implementer's own report, pasted below under "Implementer report".

## Judge, with evidence
- **Contract conformance**: every deliverable in the phase file present at the stated path with the stated
  content; every acceptance command re-run by you with its output quoted; any number that differs from the
  contract named.
- **Fixture adequacy**: do the fixtures and checks fail when they should? Try to break one (read-only: reason
  from the code, or run it against a modified copy under /tmp).
- **Silent assumptions**: anything the code or docs assume that the contract leaves open; anything that will
  bite phase 5.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 4 review (codex gpt-6-astra)
Verdict: PASS | PASS WITH ADVISORIES | BLOCKING
## Blocking
- [B1] <file:line> <finding> — <evidence> — <what fixes it>
## Advisory
- [A1] ...
## Acceptance re-run
<commands and outputs, verbatim>
## Scope check
<git status / diff --stat summary>
```
BLOCKING means a contract deliverable is missing or wrong, an acceptance number differs, or a check cannot fail.
Keep the file under 200 lines. Facts over opinions; every finding cites a path and, where possible, a line.

## Orchestrator notes (check these in addition)
- The plan file carries the milestone 2 rulings (`reviews/m2_rulings.md`, "Phase 4") and the phase 3 tokens
  (`reviews/p3_rulings.md`, H5): seven exports including `subfamily.gtf`; `export_feature_members` keyed by
  `(universe_name, variant, feature_level)` with both id spellings at level `record`; `tables/exports.tsv` as the
  inventory; component alphabet `[A-Za-z0-9_.+/?()-]+` with `|` and `:` as separators; unresolved ranks spelled
  `unresolved_class_<name>` / `unresolved_family_<name>`; membership read from `universe_members.tsv.gz`.
- Run the export stage yourself into your own directory
  (`/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p4/build/` with `tables/` and `universes.json` symlinked
  from the orchestrator's build under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/`,
  read-only) and compare the sha256 of every export and of `export_feature_members.tsv.gz` and `exports.tsv` with the
  orchestrator's. Remove your directory when done.
- Recompute with your own code from the parquet and `universe_members.tsv.gz`: 3,764,949 `interspersed` records;
  1,220 names; BED start = start_1 - 1 on every row; GTF and SAF coordinates equal the table; `taxonomy_triple.saf`
  distinct GeneIDs 1,220; `family.bed` distinct names equal the distinct canonical pairs over the universe's names;
  `subfamily.gtf` `transcript_id == gene_id` on every row.
- Parse a 1,000-row sample of each GTF with the three vendored readers under `/workspaces/Meta-Aging/01_modules/.ref/`
  (`TEtranscripts/TEToolkit/TEindex.py`, `TEsingle/TEtools/TEindex.py`, `TElocal/TElocal_Toolkit/TEindex.py`) and
  Stellarscope's `annotation/utils.py`, as the milestone 2 codex review did, and state the feature tuple each
  produces from `record.gtf` and from `subfamily.gtf`.
- Fixture adequacy: on scratch copies, break the alphabet validation, the BED offset, the attribute order, the
  registration conservation and the `exports.tsv` sha256 one at a time; name the check that fails each time.
- Wording: every sentence and comment in `src/lib/build_exports.py`, `src/30_build_exports.sh`, the three checks,
  the `docs/OUTPUTS.md` diff and the README diff.

- The implementer reports README's narrative still says "six files" while the truth table lists seven exports;
  judge every README and OUTPUTS.md sentence that counts or lists the exports.

## Implementer report
Implemented phase 4. All **13 core checks pass**. Observed `family.bed` distinct-name count: **49**.

Created or changed these 24 repository files:

```text
README.md
docs/OUTPUTS.md
src/30_build_exports.sh
src/lib/build_exports.py
src/lib/build_records.py
tests/checks/core/23_records_fixtures.py
tests/checks/core/40_exports_shape.py
tests/checks/core/41_export_registration.py
tests/checks/core/42_exports_fixtures.py
tests/fixtures/records/slash_name.out
tests/fixtures/records/slash_name.tsv
tests/fixtures/exports/README.md
tests/fixtures/exports/records.tsv
tests/fixtures/exports/taxonomy.tsv
tests/fixtures/exports/universe_members.tsv
tests/fixtures/exports/universes.json
tests/fixtures/exports/expected/export_feature_members.tsv
tests/fixtures/exports/expected/family.bed
tests/fixtures/exports/expected/record.bed
tests/fixtures/exports/expected/record.gtf
tests/fixtures/exports/expected/subfamily.bed
tests/fixtures/exports/expected/subfamily.gtf
tests/fixtures/exports/expected/subfamily.saf
tests/fixtures/exports/expected/taxonomy_triple.saf
```

Generated nine artifacts under the [scratch build directory](/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build):

```text
exports/ucsc/interspersed/full/record.bed
exports/ucsc/interspersed/full/subfamily.bed
exports/ucsc/interspersed/full/family.bed
exports/ucsc/interspersed/full/record.gtf
exports/ucsc/interspersed/full/subfamily.gtf
exports/ucsc/interspersed/full/subfamily.saf
exports/ucsc/interspersed/full/taxonomy_triple.saf
tables/export_feature_members.tsv.gz
tables/exports.tsv
```

Acceptance outputs, verbatim:

```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/05_qualify_source.sh
syntax ok src/10_build_records.sh
syntax ok src/15_build_universes.sh
syntax ok src/20_build_taxonomy.sh
syntax ok src/30_build_exports.sh
syntax ok tests/run.sh
universe=interspersed records=3764949 subfamilies=1220 families=49 taxonomy_triples=1220 exports=7 registrations=18824745
[30_build_exports] UCSC exports ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full

real	1m35.049s
user	1m33.454s
sys	0m12.151s
exit=0
```

```text
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/family.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/record.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/record.gtf
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.bed
   3764949 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.gtf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.saf
   3764950 /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/taxonomy_triple.saf
  26354645 total
==> /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/record.bed <==
chr1	3050293	3050775	L1MdA_VI|chr1:3050294-3050775|+	1000	+
chr1	3051044	3051146	ID2|chr1:3051045-3051146|-	242	-

==> /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.bed <==
chr1	3050293	3050775	L1MdA_VI	1000	+
chr1	3051044	3051146	ID2	242	-

==> /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/family.bed <==
chr1	3050293	3050775	LINE/L1	1000	+
chr1	3051044	3051146	SINE/ID	242	-

==> /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/record.gtf <==
chr1	te-tracks	exon	3050294	3050775	3667	+	.	gene_id "L1MdA_VI"; transcript_id "R|mm39|L1MdA_VI|chr1|3050294|3050775|+"; locus "R|mm39|L1MdA_VI|chr1|3050294|3050775|+"; family_id "L1"; class_id "LINE"; rmsk_family "L1"; rmsk_class "LINE"; instance_id "I|mm39|1"; rmsk_record_id "L1MdA_VI|chr1:3050294-3050775|+";
chr1	te-tracks	exon	3051045	3051146	242	-	.	gene_id "ID2"; transcript_id "R|mm39|ID2|chr1|3051045|3051146|-"; locus "R|mm39|ID2|chr1|3051045|3051146|-"; family_id "ID"; class_id "SINE"; rmsk_family "ID"; rmsk_class "SINE"; instance_id "I|mm39|2"; rmsk_record_id "ID2|chr1:3051045-3051146|-";

==> /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.gtf <==
chr1	te-tracks	exon	3050294	3050775	3667	+	.	gene_id "L1MdA_VI"; transcript_id "L1MdA_VI"; locus "L1MdA_VI"; family_id "L1"; class_id "LINE"; rmsk_family "L1"; rmsk_class "LINE";
chr1	te-tracks	exon	3051045	3051146	242	-	.	gene_id "ID2"; transcript_id "ID2"; locus "ID2"; family_id "ID"; class_id "SINE"; rmsk_family "ID"; rmsk_class "SINE";

==> /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/subfamily.saf <==
GeneID	Chr	Start	End	Strand
L1MdA_VI	chr1	3050294	3050775	+

==> /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/exports/ucsc/interspersed/full/taxonomy_triple.saf <==
GeneID	Chr	Start	End	Strand
L1MdA_VI:L1:LINE	chr1	3050294	3050775	+
1220
49
1220
export_path	namespace	universe_name	variant	feature_level	format	rows	distinct_features	sha256
exports/ucsc/interspersed/full/family.bed	ucsc	interspersed	full	family	bed	3764949	49	892a1a7a6f842a7c57b1fc7c05448f13c14173ce8c8e1f3c4333d3afee0d4108
exports/ucsc/interspersed/full/record.bed	ucsc	interspersed	full	record	bed	3764949	3764949	78afc63310a6cc621ea203df8a58711edc7d27842615e79a2237db432bca67de
exports/ucsc/interspersed/full/record.gtf	ucsc	interspersed	full	record	gtf	3764949	3764949	859c5f0db4949082fafa08f25cf776c346b6290fe23d4147e5e108ff5ba5f38d
exports/ucsc/interspersed/full/subfamily.bed	ucsc	interspersed	full	subfamily	bed	3764949	1220	7a2311a02931bad5b3af39ff5c01eee13fa0d4ab4070db91618aae74cebb7f3f
exports/ucsc/interspersed/full/subfamily.gtf	ucsc	interspersed	full	subfamily	gtf	3764949	1220	00a0e6859a9f4200f574ac3f9754130b4113b6ad10fbd1c0bf31090eb9c4e0ed
exports/ucsc/interspersed/full/subfamily.saf	ucsc	interspersed	full	subfamily	saf	3764949	1220	ef4145d75213662c11844f0c69240cb99bba31c968057f26fe73ea3853ac12d9
exports/ucsc/interspersed/full/taxonomy_triple.saf	ucsc	interspersed	full	taxonomy_triple	saf	3764949	1220	3da80b1449962220e638b1c5ce9f33a0ffdcb11f50dedc29a864a62fee14ce0b
3764949 family
7529898 record
3764949 subfamily
3764949 taxonomy_triple
```

```text
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
pass  41_export_registration.py  registrations=18824745; five ID spellings cover every record once; seven inventory hashes and feature sets pass; count 7 stays 7 at record, subfamily and family levels
pass  42_exports_fixtures.py  hand-authored export bytes, membership selection, unresolved ranks, coordinate duplicates, shared instances, deterministic rebuild and identifier gates pass
checks=13 pass=13 fail=0 unsupported=0
exit=0
```

```text
 M README.md
 M docs/OUTPUTS.md
 M docs/_internal/redesign-2026-09/prompts/p5_impl.md
 M src/lib/build_records.py
 M tests/checks/core/23_records_fixtures.py
?? src/30_build_exports.sh
?? src/lib/build_exports.py
?? tests/checks/core/40_exports_shape.py
?? tests/checks/core/41_export_registration.py
?? tests/checks/core/42_exports_fixtures.py
?? tests/fixtures/exports/
?? tests/fixtures/records/slash_name.out
?? tests/fixtures/records/slash_name.tsv
```

No implementation deviations. Scope notes: README’s existing narrative still says “six files”; its edits were restricted to the truth table. The concurrent `p5_impl.md` modification was untouched by me. No git writes, installs or network access were performed.
