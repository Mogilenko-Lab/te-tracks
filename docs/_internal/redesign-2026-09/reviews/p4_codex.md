# Phase 4 review (codex gpt-6-astra)
Verdict: BLOCKING

## Blocking

- [B1] `tests/checks/core/41_export_registration.py:17` The phase's required DuckDB conservation query is absent — `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md:43` requires that query; the delivered fixture uses pandas exclusively. The implementation follows `docs/_internal/redesign-2026-09/prompts/p4_impl.md:80`, which explicitly requests pandas, so this is an unreconciled contract/prompt discrepancy. Both the DuckDB module and executable are absent here — supply and validate the required query in a supported environment, or record a ruling accepting pandas and synchronize the authoritative phase contract.

## Advisory

- [A1] `README.md:126` The guarantee says six files and lists GTF only at record level — seven files exist, including `subfamily.gtf`; README's three namespace inventories and `docs/OUTPUTS.md:252`, `:281`, `:421` consistently specify seven. The prompt confined README edits to truth-table rows — update this guarantee to seven and include subfamily GTF when resolving the prose scope.
- [A2] `tests/checks/core/41_export_registration.py:24` The conservation fixture leaves `target` unused: lines 29–30 select only distinct measured-feature IDs. Replacing all nine targets with `WRONG` still exits 0; removing deduplication fails with a one-to-one merge error — retain the useful duplication guard and assert the intended target relationships/results before citing this fixture as proof of rollups at three grains. The full-build membership checks at lines 54–71 independently verify the actual registrations.
- [A3] `src/lib/build_exports.py:90` Unresolved tokens assume a reserved namespace that validation does not enforce — a scratch taxonomy with unresolved family for `U` and a resolved family literally named `unresolved_family_U` for `Other`, both class `DNA`, accepts both as `DNA/unresolved_family_U`. This pools two meanings under one family ID; mm39 has zero unresolved ranks — reserve the unresolved prefixes or reject collisions between resolved labels and generated tokens, with a fixture.

## Acceptance re-run

All seven exports, both output tables, the shell/Python builders, three checks, fixture files, slash-name gate and required documentation sections are present. Every numerical acceptance value matches: 3,764,949 selected records, 1,220 names/triples, 49 canonical class/family pairs, and 18,824,745 registrations. B1 is the outstanding acceptance deliverable.

Applied the current phase contract's component alphabet `[A-Za-z0-9_.+?()-]+` and separators `|`, `:`, `/`, as amended by `reviews/p3_rulings.md` (re-review A3); the review prompt's slash-permitting component alphabet is stale. Inspected every sentence/docstring/comment in both new source files, all three checks, and both public-document diffs: no added contrastive negation or incidental history/provenance chatter. The requested legacy-grouping terminology is retained.

Rebuild inputs were individual symlinks inside a local `tables/`, plus a `universes.json` symlink. This kept both generated tables local and the orchestrator's inputs read-only. The acceptance build command used the requested reviewer directory; remaining acceptance commands read the orchestrator's build.

```bash
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export LC_ALL=C
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
time bash src/30_build_exports.sh /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p4/build config/mm39.env; echo "exit=$?"
E="$TE_TRACKS_REFROOT/te_mm39/build/exports/ucsc/interspersed/full"
wc -l "$E"/*
head -2 "$E"/record.bed "$E"/subfamily.bed "$E"/family.bed "$E"/record.gtf "$E"/subfamily.gtf "$E"/subfamily.saf "$E"/taxonomy_triple.saf
cut -f4 "$E"/subfamily.bed | sort -u | wc -l
cut -f4 "$E"/family.bed | sort -u | wc -l
tail -n +2 "$E"/taxonomy_triple.saf | cut -f1 | sort -u | wc -l
cat "$TE_TRACKS_REFROOT/te_mm39/build/tables/exports.tsv"
zcat "$TE_TRACKS_REFROOT/te_mm39/build/tables/export_feature_members.tsv.gz" | tail -n +2 | cut -f3 | sort | uniq -c
tests/run.sh core; echo "exit=$?"
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
syntax ok tests/run.sh
universe=interspersed records=3764949 subfamilies=1220 families=49 taxonomy_triples=1220 exports=7 registrations=18824745
[30_build_exports] UCSC exports ready in /workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p4/build/exports/ucsc/interspersed/full

real	1m39.363s
user	1m37.856s
sys	0m12.149s
exit=0
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

Independent scratch code used parquet records selected by gzip membership, canonical pairs derived over those names, and Python CSV/regex parsing of every export row; it imported neither the exporter nor its checks. SHA-256 comparisons cover all nine generated artifacts. Reader samples use 1,000 evenly spaced rows per GTF and the actual vendored `TEindex.TEfeatures.build` and Stellarscope `parse_gtf`. TE readers also retain the full internal tuple with a trailing strand; the reporting feature tuples below exclude that strand. These are parser checks; phase 5 owns counting and overlap behaviour.

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 /tmp/te-tracks-p4-codex/independent.py
independent: records=3764949 names=1220 canonical_pairs=49 taxonomy_GeneIDs=1220
independent: every BED start=start_1-1; every GTF/SAF bound, identifier, strand and score match; subfamily transcript_id=gene_id on all rows
sha256 MATCH 892a1a7a6f842a7c57b1fc7c05448f13c14173ce8c8e1f3c4333d3afee0d4108 exports/ucsc/interspersed/full/family.bed
sha256 MATCH 78afc63310a6cc621ea203df8a58711edc7d27842615e79a2237db432bca67de exports/ucsc/interspersed/full/record.bed
sha256 MATCH 859c5f0db4949082fafa08f25cf776c346b6290fe23d4147e5e108ff5ba5f38d exports/ucsc/interspersed/full/record.gtf
sha256 MATCH 7a2311a02931bad5b3af39ff5c01eee13fa0d4ab4070db91618aae74cebb7f3f exports/ucsc/interspersed/full/subfamily.bed
sha256 MATCH 00a0e6859a9f4200f574ac3f9754130b4113b6ad10fbd1c0bf31090eb9c4e0ed exports/ucsc/interspersed/full/subfamily.gtf
sha256 MATCH ef4145d75213662c11844f0c69240cb99bba31c968057f26fe73ea3853ac12d9 exports/ucsc/interspersed/full/subfamily.saf
sha256 MATCH 3da80b1449962220e638b1c5ce9f33a0ffdcb11f50dedc29a864a62fee14ce0b exports/ucsc/interspersed/full/taxonomy_triple.saf
sha256 MATCH 9a5a530254d49d3aea5ceb5cb4cdd35f718b1cd6dfcef77e4bd91aae87724f4f tables/export_feature_members.tsv.gz
sha256 MATCH 55a1eb211f91c9ffb12c89b378aeecb9a538fd97ebeb4a20f85627bda9aef501 tables/exports.tsv
$ PYTHONDONTWRITEBYTECODE=1 python3 /tmp/te-tracks-p4-codex/readers.py
TEtranscripts record.gtf: rows=1000 groups=285 first_feature=L1MdA_VI:L1:LINE
TEsingle record.gtf: rows=1000 groups=1000 first_feature=R|mm39|L1MdA_VI|chr1|3050294|3050775|+:L1MdA_VI:L1:LINE
TElocal record.gtf: rows=1000 groups=1000 first_feature=R|mm39|L1MdA_VI|chr1|3050294|3050775|+:L1MdA_VI:L1:LINE
Stellarscope record.gtf: rows=1000 locus_groups=1000 first_locus=R|mm39|L1MdA_VI|chr1|3050294|3050775|+
TEtranscripts subfamily.gtf: rows=1000 groups=285 first_feature=L1MdA_VI:L1:LINE
TEsingle subfamily.gtf: rows=1000 groups=285 first_feature=L1MdA_VI:L1MdA_VI:L1:LINE
TElocal subfamily.gtf: rows=1000 groups=285 first_feature=L1MdA_VI:L1MdA_VI:L1:LINE
Stellarscope subfamily.gtf: rows=1000 locus_groups=285 first_locus=L1MdA_VI
```

Mutation probes ran unchanged check 42 against copied code/fixtures, changing one builder behaviour at a time. Check 41's conservation function was invoked separately from its scratch copy. Alphabet removal fails the required offending-file diagnostic; BED/order/registration mutations fail expected bytes; SHA mutation fails the measured digest assertion.

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 /tmp/te-tracks-p4-codex/mutations.py
baseline: 42_exports_fixtures.py exit=0; hand-authored export bytes, membership selection, unresolved ranks, coordinate duplicates, shared instances, deterministic rebuild and identifier gates pass
alphabet validation disabled: 42_exports_fixtures.py exit=1; AssertionError: ('subfamily.bed', "taxonomy_canonical missing exported name: 'Bad Name'")
BED offset removed: 42_exports_fixtures.py exit=1; AssertionError: record.bed
GTF attribute order swapped: 42_exports_fixtures.py exit=1; AssertionError: record.gtf
registration family support omitted: 42_exports_fixtures.py exit=1; AssertionError
exports.tsv sha256 zeroed: 42_exports_fixtures.py exit=1; AssertionError
conservation baseline (41_export_registration.py): conservation.py exit=0; (no diagnostic)
conservation distinct-feature guard removed (41_export_registration.py): conservation.py exit=1; pandas.errors.MergeError: Merge keys are not unique in left dataset; not a one-to-one merge
conservation all nine targets replaced by WRONG (41_export_registration.py): conservation.py exit=0; (no diagnostic)
```

## Scope check

On branch `redesign-2026-09`, the 24 reported implementation files fit `prompts/p4_impl.md:100`–102, including the narrowly allowed record-validator/fixture changes and README truth-table additions. The initial tracked diff was 6 files, 332 insertions, 54 deletions. `prompts/p4_review.md` and `prompts/p5_impl.md` were already modified at entry. The phase 7 plan change and three milestone-5 prompt files appeared during review; these are outside phase 4's allowed set and were left untouched. Git status alone cannot attribute their authorship. Hash comparison confirms the reviewed implementation bytes stayed unchanged.

```text
$ git status --short
 M README.md
 M docs/OUTPUTS.md
 M docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/17_phase7_publication.md
 M docs/_internal/redesign-2026-09/prompts/p4_review.md
 M docs/_internal/redesign-2026-09/prompts/p5_impl.md
 M src/lib/build_records.py
 M tests/checks/core/23_records_fixtures.py
?? docs/_internal/redesign-2026-09/prompts/m5_codex.md
?? docs/_internal/redesign-2026-09/prompts/m5_divergent.md
?? docs/_internal/redesign-2026-09/prompts/m5_opus.md
?? src/30_build_exports.sh
?? src/lib/build_exports.py
?? tests/checks/core/40_exports_shape.py
?? tests/checks/core/41_export_registration.py
?? tests/checks/core/42_exports_fixtures.py
?? tests/fixtures/exports/
?? tests/fixtures/records/slash_name.out
?? tests/fixtures/records/slash_name.tsv
$ git diff HEAD --stat
 README.md                                          |  22 +--
 docs/OUTPUTS.md                                    | 146 ++++++++++++++++---
 .../17_phase7_publication.md                       |   4 +-
 .../redesign-2026-09/prompts/p4_review.md          | 158 ++++++++++++++++++++-
 docs/_internal/redesign-2026-09/prompts/p5_impl.md |  57 +++++---
 src/lib/build_records.py                           |   2 +-
 tests/checks/core/23_records_fixtures.py           |   1 +
 7 files changed, 335 insertions(+), 55 deletions(-)
```

Reviewer scratch under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p4/` and `/tmp/te-tracks-p4-codex/` was removed after verification. The sole repository write is this review. No git writes, installs or network access occurred.
