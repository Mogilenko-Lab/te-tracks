# Structural views consult (codex gpt-6-astra)

## Summary in plain language

A RepeatMasker **record** is one annotated stretch matching a repeat model. An **insertion** is the DNA left by one insertion event. Several records can describe parts of that insertion; a later insertion inside it can separate those parts. The source instance ID links records that RepeatMasker grouped together. It provides a useful starting group, with biological reconstruction still to establish its meaning (`docs/OUTPUTS.md:14-35,59-63`; `../reviews/field_divergent.md:24-43`).

In general TE biology, beyond the supplied annotations, a provirus has an LTR at each end and an internal region between them. Repeat libraries represent the LTR and internal sequence with different models, so RepeatMasker can report three records for one provirus and further records for fragmented matches. A **solo LTR** can remain after recombination between the two ends removes the intervening sequence. An LTR with no recorded internal partner is therefore an unresolved structural candidate; missing annotation or a different instance ID can also explain the missing partner.

In general L1 biology, beyond the supplied annotations, the promoter lies in the RNA-oriented 5′ region. A full-length L1 retains that region; reverse transcription often stops before copying the RNA's 5′ end, so most inserted copies have lost it. The observed boundary of a shortened copy can consequently be far inside the original element. Here, only 588 of 877,139 L1 records start at consensus base 1; this measures model-prefix coverage, with functional promoter status still unassessed (Q3).

Your promoter concern is well founded: a gene can use different starts in different cells, and an annotation records a particular set of transcript models. One pinned GENCODE snapshot gives a consistent coordinate reference. Tissue-specific start evidence can enter a later snapshot. A window is a declared distance around a recorded start; its width controls which candidate relationships we retain. It does not establish the promoter used in the experiment (Q1).

Each proposed view serves a different question:

- **Host-start windows:** which gene transcript starts are near this repeat, and at what signed distance?
- **Instance block unions:** which annotated pieces belong to this source group, while preserving the sequence gaps between them?
- **Record-end windows:** does a molecule's RNA-oriented 5′ end fall near the annotated repeat end that retains the model prefix?
- **LTR–internal pairs:** which nearby repeat components could form one element, and which have competing partners?
- **Divergence bins:** how does support vary across measured sequence distance from the repeat models?

Recommend the current phase-9 host build first, then annotation-matched context and simple divergence queries for 14761, followed by consumer-qualified instance/end views and structural reconstruction. Motif scanning belongs to the ATAC framework under the owner's ruling (`C/adr_rulings_2026-09-17.md:10-25,33-50`). These are design recommendations; implementation remains unchanged.

Path shorthand: `T` = `/workspaces/Meta-Aging/01_modules/te-tracks`; repository paths are relative to T. `C` = `docs/_internal/redesign-2026-09/consults`; `B` = `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build`; `G` = `/data2/users/shared/refcache/mm39/mm39_20260911/gencode.vM37.primary_assembly.annotation.gtf.gz`; `D` = `/workspaces/Meta-Aging/_scratch/te-tracks-audit/field/dfam_census_1220.tsv`. Binary/compressed input citations identify tables and columns; exact measurements and methods are below.

## Q1. Host-promoter windows

Use **GTF transcript rows**, preserving versioned transcript and gene IDs. For transcript `[s,e]`, TSS/TES are `s/e` on `+` and `e/s` on `−`. Normalize contigs with `B/tables/contig_aliases.tsv` (`chrom_gencode → chrom_ucsc`). G contains 278,369 transcripts, 78,317 tagged `Ensembl_canonical`, and zero `MANE_Select` tags on transcript rows. Canonical is a selectable flag; retaining all isoforms preserves alternative starts (`C/gene_context_adr_brief.md:60-69`; `C/gene_child_consult.md:43-51`).

For record `[a,b]`, landmark `p`, and transcript strand sign `s`, signed closest-base distance is `d = s*(min(max(p,a),b)-p)`: negative upstream, zero covering the landmark, positive downstream. A stored TSS window contains bases satisfying `−U ≤ s*(x−TSS) ≤ D`, clipped to contig bounds, hence U+D+1 bases before clipping. `(0,0)` contains the TSS base.

The measured sparse relation is the **union** of transcript-body overlaps, TSS-window overlaps, and transcripts tied for globally nearest same-contig TSS, TES or exon cut, with one row per record × transcript. Nearest queries are independent of TE strand; relative strand remains an attribute. A record outside all gene bodies still gets nearest-landmark candidates. Increasing the window adds any additional transcript whose window overlaps that record; it also adds candidates for records inside other genes. Gene-body distance remains separate, including the previously measured gene/transcript-span differences (`C/gene_child_consult.md:45-59`).

For any narrower `(u,dn)` with `u≤U` and `dn≤D`, filtering the stored pairs by `−u ≤ distance_to_TSS ≤ dn` exactly recovers that narrower window's overlaps. Body/nearest pairs remain available for their own queries. A wider window requires a new pair enumeration; a missing pair beyond the declared scope means unevaluated proximity.

Exact chr1 counts use all 377,297 records, 18,081 transcripts and 4,990 genes. Of these records, 160,278 overlap no gene body. The extrapolation multiplies by `5,318,133 / 377,297 = 14.0953492872`, excluding the 2,638 records on unannotated contigs.

| Stored (U,D), bp | Exact chr1 pairs | Added over (0,0) | Pairs for records outside all gene bodies | Of additions, outside gene bodies | mm39 extrapolation |
|---|---:|---:|---:|---:|---:|
| (0,0) | 1,412,484 | 0 | 252,481 | 0 | 19,909,455 |
| (1,000,100) | 1,431,274 | 18,790 | 257,036 | 4,555 | 20,174,307 |
| (2,000,200) | 1,455,699 | 43,215 | 263,657 | 11,176 | 20,518,586 |
| (10,000,2,000) | 1,714,112 | 301,628 | 332,093 | 79,612 | 24,161,007 |
| (20,000,2,000) | 2,073,944 | 661,460 | 436,337 | 183,856 | 29,232,965 |

These are exact chr1 cardinalities and **chr1-density extrapolations**, not exact genome totals. The earlier contig-stratified sample estimated 21,759,726 / 22,501,378 / 26,816,523 at (0,0) / (2000,200) / (10000,2000), respectively (`C/gene_child_consult.md:172-216`). The chr1 extrapolations are about 8.5–9.9% lower at those widths; genomic heterogeneity remains a sizing uncertainty. Keep the prior higher figures in capacity planning until full-mm39 enumeration.

Recommend `(10000,2000)` as the first deferred context snapshot's **candidate search envelope**, permitting narrower 1-kb/2-kb queries afterwards. This is a storage/reuse choice; consumers name their biological promoter policy. The 20-kb gene-adjacency question uses gene-body distance separately, as the owner's toolkit specifies (`/workspaces/Meta-Aging/01_modules/.ref/14839-DM-cGAS/01_modules/TE-RNAseq-toolkit/docs/LIMITATIONS.md:125-137`). The snapshot must match the consumer's gene annotation (`C/adr_rulings_2026-09-17.md:103-111`).

The following source descriptions and licence recollections are **general knowledge beyond the local inputs, unverified offline**; current release terms, assembly and tissue inventories need checking at admission.

| Later pinned TSS input | Added evidence and mouse coverage known to me | Licence knowledge / admission requirement |
|---|---|---|
| FANTOM5 CAGE | Experimentally observed capped RNA starts and tissue/cell usage, including mouse; coverage depends on sampled tissues. Familiar mouse releases use older assemblies, so mm39 availability or a pinned lift-over must be established. | I recall FANTOM5 data under CC BY 4.0; verify the exact downloaded release's terms and attribution. |
| EPDnew | Curated experimentally supported promoter/TSS collection, including mouse; familiar mouse releases include mm10. It provides a selected high-confidence start set; exact mm39 coverage is unverified here. | Openly downloadable to my knowledge; I cannot establish the exact redistribution licence from these inputs. Pin it before redistribution. |
| ENCODE cCRE promoter-like signatures | Accessible regions with promoter-associated chromatin evidence, including mouse resources familiar on mm10; these are candidate regulatory intervals rather than directly measured transcript starts. Assay/tissue and mm39 coverage need pinning. | ENCODE's open data-use policy is familiar; verify release-specific terms, attribution and any third-party restrictions. |

Each alternative belongs in another input-pinned snapshot with source ID, assembly, evidence and mapping status preserved. te-tracks supplies intervals, strands and record/instance identities. The ATAC framework obtains sequence from its pinned assembly FASTA and scans against separately pinned motif resources, including cisTarget in `/data2/users/shared/refcache/cistarget`, JASPAR and CisBP; motif matches and motif-to-TF interpretations remain downstream (`C/adr_rulings_2026-09-17.md:10-17`).

## Q2. Instance block-union view

Define one logical feature per text `rmsk_instance_id`, with member intervals unioned **within each contig and strand**. Merge overlap and touching bases; retain positive gaps. Keep selected `member_count`, `mixed_name`, `mixed_strand`, partition count, block count and span. Selection is the published raw-class `interspersed` predicate; membership/status refers to that selection (`docs/OUTPUTS.md:59-94`).

| Exact interspersed measurement | Value |
|---|---:|
| Selected member records | 3,764,949 |
| Logical instance features | 3,152,636 |
| Multi-record instances | 434,707 |
| Multi-block features, counting all strand partitions | 398,980 |
| Contig × strand partitions | 3,175,880 |
| Union blocks | 3,688,115 |
| Mixed-name instances | 30,569 |
| Mixed-strand instances | 23,244 |
| Gap bases, summed within strand partitions | 263,926,042 |
| Largest within-partition gap, bp | 24,679 |
| Instances with overall span >50 kb | 0 |
| Largest overall span, bp | 31,513 |

Every selected instance is on one contig. The largest gap lies in minus-strand `L1_Mur3` instance `4299283`, between chrX:8,344,835 and 8,369,515, leaving 24,679 intervening bases. The >50-kb screen finds zero cases; this limited negative screen leaves source-group validity unestablished. Gap sums are per feature/strand partition, with possible overlap between different instances.

**Exports:** BED12 expresses the discontiguous blocks; a GTF multi-exon transcript uses `gene_id = transcript_id = instance_alias` and one exon per union block. Single-strand export eligibility is **3,129,392 features / 3,636,088 exon blocks**, including 375,736 multi-block features. The 23,244 mixed-strand instances remain in the complete feature/block tables with explicit unsupported-transcript status. A single BED12/GTF transcript cannot faithfully encode both strands; a future partition export would need component IDs linked back to the parent, with its own consumer contract.

Use `(feature_level, key_grammar) = (instance, instance_alias)`, `I|mm39|<rmsk_instance_id>`, and bind the matrix through the full `(universe, variant, feature_level, key_grammar)`. Existing full instance registration already connects each member record; union blocks require an explicit block-to-member mapping wherever consumers need block provenance. Mixed-name features retain all source names and need consumer allocation for subfamily summaries (`docs/OUTPUTS.md:399-441`; C9 at `C/adr_rulings_2026-09-17.md:52`).

A block-aware consumer avoids counting a gap as repeat sequence and avoids adding overlapping member bases twice within a feature. A span-only reader, including an exon-to-gene-span conversion, loses that guarantee. The view establishes source-group support; it cannot certify one biological insertion, eliminate overlaps between different instances, or make each molecule belong to only one feature. Qualify gap-only reads, mixed strands, and actual parser grouping before publication (`C/field_practice_consult.md:94-98`; `../reviews/field_divergent.md:24-36`).

## Q3. Record-end windows

Define `record_5prime_N([a,b],+) = [a,min(b,a+N−1)]` and `record_5prime_N([a,b],−) = [max(a,b−N+1),b]`. Require valid forward-model extents (`1≤consensus_start_1≤consensus_end_1`, positive `consensus_end_1+consensus_left_bp`) and `consensus_start_1−1≤tolerance`. Thus tolerance 10 admits starts through 11. The two invalid L1 rows already documented at `docs/OUTPUTS.md:44-46` fail validity and fall outside every tested prefix threshold; raw prefix-only counts here are identical.

Selections: LINE/L1 = 877,139 records; young-name subset `^L1Md(A|Gf|Tf)_` = 70,628 records across 12 names; class LTR = 1,105,064; class LTR with literal `LTR` anywhere in its name = 306,411. That last screen includes 27,830 `-int` records and therefore expresses a name filter, with component role still unresolved.

Every eligible record produces one positive-length window for **each** N, clipped to record length. The eligible column is consequently also the window count at N=100, 300, 500 and 1000. The four right columns count windows reaching the full requested N; remaining windows are shorter.

| Selection | Tolerance bp | Eligible records = windows at each N | Full 100 | Full 300 | Full 500 | Full 1000 |
|---|---:|---:|---:|---:|---:|---:|
| LINE/L1 | 0 | 588 | 548 | 369 | 285 | 174 |
| LINE/L1 | 10 | 2,342 | 2,186 | 1,119 | 872 | 575 |
| LINE/L1 | 100 | 11,226 | 10,346 | 7,088 | 6,050 | 4,945 |
| Young L1 names | 0 | 146 | 145 | 138 | 136 | 132 |
| Young L1 names | 10 | 686 | 683 | 358 | 351 | 339 |
| Young L1 names | 100 | 3,601 | 3,579 | 3,231 | 3,212 | 3,184 |
| LTR class | 0 | 284,044 | 268,839 | 212,144 | 50,799 | 8,548 |
| LTR class | 10 | 410,467 | 385,460 | 290,736 | 67,552 | 12,434 |
| LTR class | 100 | 552,142 | 510,677 | 353,861 | 76,718 | 13,983 |
| LTR in name | 0 | 81,868 | 78,774 | 67,227 | 23,905 | 1,567 |
| LTR in name | 10 | 103,826 | 99,410 | 82,522 | 29,782 | 2,025 |
| LTR in name | 100 | 129,948 | 121,755 | 94,996 | 33,069 | 2,319 |

A 5′ library consumer reconstructs the molecule's **RNA-oriented 5′ aligned endpoint**, with mate, strand, clipping and splice handling, and asks whether that point lies inside an eligible window. Interval overlap instead asks whether any aligned sequence touches the window; its 5′ endpoint can be elsewhere (`C/field_practice_consult.md:100-110`; `C/field_practice_synthesis.md:183-195`). Preserve full competing gene/TE support for the primary RNA estimator; an end-support assay is separately declared.

The prefix screen prevents calling a clearly internal truncation boundary a model's 5′ promoter boundary. It cannot prevent host read-through being interpreted as autonomous TE transcription. Prefix coverage also leaves promoter sequence integrity, correct model choice, 5′ versus 3′ LTR role and mapping ambiguity unresolved. Consensus extents provide no base-level indel map; row-implied lengths vary within 145/149 L1 names (`C/field_practice_consult.md:128-135,187-203`). Publish N, tolerance, validity and eligibility as explicit reference properties; choose biological evidence thresholds in the consumer. Register each clipped block to its parent record alias under a parameter-specific variant, for example `record_5prime_300_prefix_le_100bp`, with the original record identity retained.

## Q4. LTR–internal candidate pairs

**Denominator correction:** the supplied 25,055 / 17,947 baseline uses class-LTR records with names **not ending `-int`**, rather than literal `LTR` names. Reproduced: 176,698 `-int` records in 121,473 instances; 928,366 other class-LTR records; 17,947 shared instances, 103,526 internal-only and 722,280 non-internal-only instances. Literal `LTR` plus exclusion of `-int` leaves 278,581 candidates, of which 17,995 records in 13,084 instances share an instance with a strict `-int` record. The prior 21,733 literal-name partners additionally used `_I$|-I_` as internal patterns (`C/field_practice_consult.md:201-203`). These definitions answer different screens.

The measured adjacency rule requires same contig, raw `rmsk_family`, and strand; disjoint records in either genomic order; and **0≤gap≤X**, where `gap = right.start_1−left.end_1−1`. Both LTR–internal and internal–LTR orders qualify; TE-oriented left/right reverses on minus strand. Enumerate every qualifying pair, allowing intervening annotations; this is a distance candidate relation. A triplet is one internal **record**, one candidate entirely on each side, with each gap≤X. Count every distinct Cartesian combination of left and right candidates, retaining alternative partners.

| Candidate naming | X bp | Pair rows | LTR records with adjacent partner | Newly partnered LTR records | Of 103,526 internal-only instances, gaining a flank | Triplet combinations | Internal records at triplet centers |
|---|---:|---:|---:|---:|---:|---:|---:|
| All non-`-int` | 100 | 37,834 | 34,468 | 12,833 | 7,415 | 4,226 | 4,012 |
| All non-`-int` | 1,000 | 93,660 | 58,755 | 34,194 | 20,072 | 21,853 | 12,518 |
| All non-`-int` | 5,000 | 237,375 | 116,533 | 91,540 | 45,783 | 132,938 | 43,480 |
| Literal `LTR`, non-`-int` | 100 | 24,877 | 22,652 | 6,233 | 2,637 | 3,322 | 3,153 |
| Literal `LTR`, non-`-int` | 1,000 | 48,668 | 28,811 | 10,993 | 5,919 | 9,880 | 5,883 |
| Literal `LTR`, non-`-int` | 5,000 | 101,834 | 37,818 | 19,849 | 9,513 | 56,412 | 25,454 |

“Newly partnered” excludes LTR records already sharing an instance with any strict internal record, regardless of distance. Both naming rows use the **same original 103,526 internal-only-instance denominator**. Broad-rule triplet centers occupy 3,607 / 9,337 / 24,270 distinct instances at X=100 / 1000 / 5000; they are candidate configurations, with fragmentation and repeated centers retained. At 5 kb, 181,443 of 237,375 broad pair rows cross instance IDs; 54,834 LTR records have multiple internal partners, and only 16,440 of 43,480 center records have exactly one candidate on each side.

Nested insertions and neighboring same-family copies can supply plausible but unrelated flanks; broad families such as ERVK do not establish compatible LTR/internal model pairs. Increasing X increases both recovery and this false-pair opportunity; the table measures yield, with precision unmeasured. Preserve `same_instance`, `adjacent_same_family`, `unpaired`, `ambiguous`; ambiguity includes competing flanks and conflicting structure. Keep edge evidence beside any overall `ambiguous` status so source-instance support remains visible. `unpaired` leaves solo-LTR status unassessed.

**One code to find them all** (Bailly-Bechet et al., 2014, *Mobile DNA* 5:13) is the field reconstruction target: the local review describes assembling full LTR–internal–LTR candidates before falling back to solo/internal pieces (`../reviews/field_bioinf.md:13,32`). From general algorithm knowledge beyond these inputs, its LTR/internal correspondence handling and fragment assembly add model compatibility and copy reconstruction to a proximity screen. Its precise options and behavior were uninspected here; it was not run. Admission should compare its reconstruction with these candidates and sequence-supported examples before adopting ERV units (`docs/DECISIONS.md:88-92`).

## Q5. Divergence bins

Recommend five disjoint **record-level sequence-distance strata under this pinned RepeatMasker run**: `divergence_le_5pct` [0,5], `divergence_gt_5_le_10pct` (5,10], `divergence_gt_10_le_20pct` (10,20], `divergence_gt_20_le_30pct` (20,30], and `divergence_gt_30pct` (30,∞). Biological age and activity remain unassessed. In general biological knowledge beyond these inputs, model choice and substitution-rate variation affect divergence; low divergence alone establishes neither recent insertion nor transcription.

Each entry below is **records / distinct source instances represented by those records**. Records partition into bins; one instance can appear in several bins, so instance columns must not be summed into an exclusive insertion count.

| Selection | [0,5]% | (5,10]% | (10,20]% | (20,30]% | >30% | Total records / instances |
|---|---:|---:|---:|---:|---:|---:|
| L1 | 114,620 / 92,330 | 126,951 / 102,038 | 215,551 / 166,412 | 326,832 / 235,100 | 93,185 / 77,299 | 877,139 / 610,410 |
| ERVK | 25,913 / 16,814 | 40,113 / 30,624 | 149,062 / 115,819 | 116,606 / 98,352 | 38,337 / 33,535 | 370,031 / 271,188 |
| ERVL-MaLR | 17,707 / 13,736 | 25,476 / 22,265 | 122,220 / 101,061 | 256,841 / 213,277 | 111,867 / 98,393 | 534,111 / 418,708 |
| B1 | 41,093 / 40,783 | 96,428 / 94,951 | 137,760 / 135,081 | 119,674 / 117,372 | 21,746 / 21,395 | 416,701 / 409,304 |
| B2 | 18,341 / 17,974 | 63,142 / 61,081 | 82,758 / 79,715 | 172,621 / 162,442 | 33,432 / 31,516 | 370,294 / 350,925 |

L1 selects raw LINE/L1; ERVK and ERVL-MaLR select raw class LTR with that family; **B1 selects the ten SINE names starting `B1`**; B2 selects raw SINE/B2 and includes B3/B3A. The raw Alu bucket additionally includes five PB1 names, totaling 558,808 records / 549,330 instances. For the broader B1+PB1 interpretation its five bin counts are 41,160/40,850; 97,478/95,993; 158,193/155,250; 212,868/209,327; 49,109/48,451 (records/instances). A raw family filter `B1` returns zero (`B/tables/rmsk_taxonomy.tsv`; `C/field_practice_synthesis.md:55-66`).

Reproduced all-catalog zero divergence = **468,810**; B1_Mus1 p05/median/p95 = **4.1/8.9/21.8%**; B3 = **15.7/23.1/31.5%**. All 5,320,771 divergence values are finite and nonnegative. These spreads motivate keeping the measured value per record; a name median discards within-name variation (`../reviews/field_divergent.md:119-122`). An exclusive instance bin would need a separate declared summary, such as a member-weighting policy, and another census.

`universes.json` schema 1 supports only class inclusion and family-prefix exclusion (`docs/OUTPUTS.md:74-94,125-126`). A proposed schema 2 could add typed `divergence_pct_range: {lower: 5, lower_inclusive: false, upper: 10, upper_inclusive: true}` combined by AND with the base class selection, `upper: null` for an unbounded upper limit, and percent units. Negative/nonfinite values fail validation; reject unknown keys and malformed bounds and pin edge inclusion and conservation fixtures. Exact-family and explicit-name-set predicates are additional extensions if the five biological selections themselves become named universes. Numeric bins alone require neither a new RepeatMasker run nor a new catalog.

## Q6. Ordering and cost

Measured UCSC interspersed exports: BED6 **235,909,236 bytes / 3,764,949 rows = 62.659 bytes/row**; record GTF **1,216,878,580 bytes = 323.213 bytes/row**. The following are uncompressed **planning estimates**, in decimal MB/GB, per namespace where applicable. They exclude new metadata, registration growth, indexes, serializer differences and compression; three namespace exports cost approximately three times the interval-file estimate.

| View | Rows/features and estimated payload | Identity effect | Recommended timing |
|---|---|---|---|
| Host-start/context relation | At recommended (10000,2000), 24.161 M pairs by chr1 scaling, 26.817 M by the earlier genome sample. At 160–240 bytes/pair, budget about 3.87–6.44 GB; 5.321 M record statuses, exact intersection blocks and boundary ties add storage. | New gene-child BUILD_ID; parent core and CATALOG_ID retained. | After host build; first larger reference task for annotation-matched 14761 context. |
| Instance block union | Complete table: 3.153 M features / 3.688 M blocks. Single-strand export: 3.129 M BED12 rows ≈328 MB; 3.636 M exon rows ≈1.175 GB GTF. | New core BUILD_ID; same CATALOG_ID. | After host build, with a named block-aware consumer. |
| Record-end windows | One N at tolerance 100 for L1+all LTR: 563,368 rows ≈35.3 MB BED / 182.1 MB GTF. All 4 N × 3 tolerances: 5,043,236 rows ≈316.0 MB BED / 1.630 GB GTF. Young/literal subsets overlap these selections. | New core BUILD_ID for published views; same CATALOG_ID. | After host build, before a qualified 5′-library end-support analysis. |
| LTR–internal candidates | Broad X=5 kb: 237,375 pair rows ≈29.7 MB at twice the BED-row budget; 132,938 triplet rows ≈25.0 MB at three times that budget; complete component status adds 1,105,064 rows (about 69.2 MB at the BED-row budget). | New core BUILD_ID for derived candidate tables; same CATALOG_ID. | After host build and end/instance qualification; validated units need a further evidence gate. |
| Divergence bins | Binning all interspersed records adds 3,764,949 memberships across five disjoint bins. If BED/GTF exports are duplicated by bin, their combined rows equal the baseline: ≈235.9 MB BED / 1.217 GB GTF per namespace; memberships and summary-only views are smaller but unmeasured. | New core BUILD_ID/schema for published universes; same CATALOG_ID. A consumer query over existing values needs no build. | Query during the pilot; publish after host build with a named need. |

BED12 budgeting uses `(62.659+40) × 3,129,392 + 14 × (3,636,088−3,129,392)` bytes to allow fixed BED12 fields and extra block lists. GTF uses the existing record-row average conservatively; a dedicated instance attribute grammar could be smaller. Pair/triplet budgets scale existing record identifiers and geometry, with extra evidence fields still to size. Context uses the earlier 160–240-byte row assumption because its geometry is richer (`C/gene_child_consult.md:51`). These are estimates of payload shape, with final serializer costs still unmeasured.

All identity conclusions assume **derived companion tables/exports**, preserving the canonical record, membership and taxonomy bytes. Changing source group membership or canonical records would also change CATALOG_ID. New export contracts, predicates, parameters and inventories change BUILD_ID (`docs/RELEASES.md:42-71`; `docs/DECISIONS.md:68-76`).

The existing core payload is 10,461,884,289 bytes, about **10.5 GB per retained build**. A later core build retains another full baseline plus its additions under the current archive model; all five views in separate builds would repeatedly incur that baseline. The gene child pins an existing parent and adds its own payload, with dependency closure retained (`docs/RELEASES.md:160-176`). Preserve the single phase-9 host build; batch subsequently justified core views into one later snapshot. This follows the ruled 14761 RNA-first pilot and direct ATAC counts without initial ATAC EM (`C/adr_rulings_2026-09-17.md:33-50`). The cardinality experiments here leave serialization, complete geometry, consumer fixtures and full-mm39 context qualification outstanding.

## Measurements performed (methods, exact numbers)

**Scope and pins.** Started on `redesign-2026-09` at `9c27b14`; another process advanced HEAD to `b29e446` and completed the Dfam census during this consult. I performed no git writes. Re-read the updated rulings; their C4/C11 assignments and motif boundary remain as cited. Only this consult is a durable write; Python measurement scratch was confined to `/workspaces/Meta-Aging/_scratch/te-tracks-audit/structure-consult/` and removed with `shutil.rmtree`. Every shell invocation exported `PYTHONDONTWRITEBYTECODE=1`; no builds, installs, network requests or quantifiers ran. The owner's `14839-DM-cGAS` documentation was read; `sene/` was untouched.

- `B/BUILD_ID`: `9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d`.
- `B/CATALOG_ID`: `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e`.
- `B/tables/rmsk_records.parquet` SHA-256: `d5deabd4ae015204a2277093bf41ef4bbb597a74313e54d13e0f479eab17f33a`; 24 columns, 5,320,771 rows.
- Compressed G SHA-256: `0d1673f3c0fff7d28ff63f4443a0863fa25f817d391982e465f7ec20f256bcd0`.
- Complete D SHA-256: `b3bee1d921f8b221df4f3d982961562787aa8d034ac009f75d32528e0799e832`; 1,220 unique names exactly equal the interspersed name set, 1,047 exact hits with classification and 173 misses. Read and left unchanged. Its initial 661-row partial state was excluded from conclusions.

**Input census.** Streamed `rmsk_instance_members.tsv.gz`: 5,320,771 rows / 4,696,900 distinct text instance tokens. Read `rmsk_taxonomy.tsv`: 18,504 triples / 18,484 names. Used the published class predicate, never a reconstructed class list. D's lineages confirm B1_Mus1 and PB1 on the Alu branch (lines 19,792), B3 on B2 (24), and IAPEz-int/IAPLTR1a_Mm on the same ERV2 lineage (193,195); this supplies ancestry, with individual component pairing unresolved. L1MdA_I has no exact hit and lists part-model alternatives (305). No Dfam sequence or promoter projection was admitted.

**Q1 enumeration.** Parsed GTF transcript/gene/exon rows and alias-normalized contigs. chr1 body pairs = **921,233**. For each of TSS, TES and exon cuts, selected every contained point, otherwise all tied nearest points; exon cuts use `[a−1,b]`. Deduplicated nearest pairs = **921,242**. Used bedtools `intersect -wa -wb` between records and the interval union of each transcript body with its TSS window, then unioned encoded `(record,transcript)` keys with nearest pairs. Body-or-window counts at the five widths are **921,233 / 956,624 / 996,203 / 1,335,805 / 1,739,096**; Q1 gives the final deduplicated relation sizes. The cardinality process took 12.01 s and peaked at 1,453,332 KiB RSS here; this excludes complete context serialization. An independent brute-force point/distance calculation on 1,000 seeded chr1 records (`seed=20260917`) agreed across all 5,000 window/pair-set comparisons.

**Q2–Q3 calculations.** Sorted selected records by text instance, contig, strand, start and end; compared each start with the running maximum end. Positive gaps are `max(0,start−previous_union_end−1)`; a separate Python streaming merge reproduced **3,688,115 blocks / 263,926,042 gap bp / 24,679 maximum gap**. Overall spans use `max(end)−min(start)+1` per instance. For each Q3 selection, applied extent validity and prefix tolerance, counted eligible rows and `length_bp≥N`, and summed `min(length_bp,N)`. Example window-base sums for tolerance 100 and N=100/300/500/1000: L1 **1,098,905 / 2,780,941 / 4,080,110 / 6,801,862 bp**; all LTR **53,999,489 / 140,263,127 / 176,478,423 / 193,574,977 bp**. Overlaps between records remain in these sums.

**Q4–Q5 calculations.** Grouped LTR candidates by contig/family/strand; binary-searched sorted starts/ends to enumerate disjoint pairs through gap 5,000, then filtered for 100 and 1,000. Independent bedtools `window -w 5001 -sm`, followed by equal-family, disjointness and explicit gap filtering, reproduced the entire **237,375-edge** set. Triplets use `left_candidate_count × right_candidate_count` per internal record. New-partner and internal-only gains use distinct record/instance sets as defined in Q4. Divergence bins use the exact raw numeric inequalities, with pandas distinct text-ID counts within each bin. Software: pandas 2.2.3, numpy 1.26.4, pyarrow reader, bedtools 2.31.1. These are reference measurements, with biological sensitivity/precision still unmeasured.

## Open for the owner

1. Choose the first context search envelope: recommend **(10000,2000)** in the deferred, annotation-matched child; narrower biological promoter rules remain consumer policy. Alternative experimental TSS inputs can follow a concrete tissue question.
2. Confirm that instance/end/pair products publish **support and candidate status**, with single-strand instance export eligibility and unresolved solo/promoter status explicit. Name the first consumer before qualifying an adapter.
3. Confirm **after-host-build** ordering and batch later core changes. Divergence queries can serve the 14761 pilot immediately from existing columns; 5′ end-support qualification follows the whole-cell RNA use case. No candidate decision or implementation was adopted by this consult.
