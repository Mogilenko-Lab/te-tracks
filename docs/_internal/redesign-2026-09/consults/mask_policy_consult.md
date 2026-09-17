# Mask-policy consult (codex gpt-6-astra)

## Summary

Recommend phase 8 ship `all_exons_unstranded_union_v1`, `min_retained_block_bp = 1`. Put `all_exons_stranded_union_v1` beside it in the first later snapshot after a consumer qualifies strand and molecule handling. On `interspersed`, strand-aware subtraction restores **11,125,985 bp across 76,971 records**, including 46,075 records otherwise fully removed. Geometry establishes the available support; the chemistry pilot establishes its counting value.

The 10x reference was present. Its filtered GENCODE vM33 GTF has a **114,032,813-bp exon union**, versus vM37's 160,549,642 bp, and changes unstranded mask geometry for **74,464 interspersed records**. A matching annotation snapshot is warranted. TEsingle models gene/TE competition; IRescue's standard interface models TE ambiguity and accepts no gene GTF. Optional repeat-free intronic/exonic BED views can support the owner's coverage diagnostic in a later child snapshot.

Scope: design and measurements, starting at `redesign-2026-09`, `9c27b14`; no implementation. HEAD advanced externally to `b29e446` during the consult; citations reflect the final on-disk documents. Owner authority: `C/adr_rulings_2026-09-17.md:19-26,33-45,85-89,103-111`. Here `C` = `docs/_internal/redesign-2026-09/consults`, `P` = `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign`, `X` = `/workspaces/Meta-Aging/01_modules/.ref`, `K` = `X/14839-DM-cGAS/01_modules/TE-RNAseq-toolkit`. `B`, `G37`, and `G10` are the exact measurement inputs defined below. GTF line references mean decompressed lines; shortened source paths inherit the checkout named in their sentence/table row.

## Q1. Mask census

All calculations normalize contigs first, use half-open intervals, union overlapping/touching mask intervals, and retain every positive-length piece. Removed bp are **sums over records**; overlapping RepeatMasker records contribute separately, matching the existing acceptance anchor. “Partly cut” includes trimmed and split records and excludes fully removed records. Retained blocks are SAF data rows per grouping, independent of namespace (`docs/OUTPUTS.md:3-5,385-415`).

Policies: **a** = vM37 every exon, unstranded; **b** = every exon, same strand as the TE; **c** = every exon, opposite strand; **d** = exons with `transcript_type "protein_coding"`, unstranded; **e** = exon rows with an exact `tag "basic"`, unstranded; **fU/fS** = G10 every exon, unstranded/same strand. Policy d selects transcript biotype, including UTR portions of its exon rows; it does not select all transcripts of protein-coding genes.

| Policy | Universe | Removed bp | Fully removed records | Partly cut records | Retained records | Retained blocks |
|---|---|---:|---:|---:|---:|---:|
| a | interspersed | 26,235,918 | 96,119 | 68,109 | 3,668,830 | 3,684,934 |
| b | interspersed | 15,109,933 | 50,044 | 38,793 | 3,714,905 | 3,724,927 |
| c | interspersed | 11,480,047 | 47,031 | 32,075 | 3,717,918 | 3,724,485 |
| d | interspersed | 5,979,867 | 25,844 | 7,920 | 3,739,105 | 3,740,842 |
| e | interspersed | 19,798,260 | 65,479 | 54,992 | 3,699,470 | 3,713,346 |
| fU | interspersed | 15,361,040 | 65,841 | 28,122 | 3,699,108 | 3,704,889 |
| fS | interspersed | 8,152,002 | 32,384 | 15,266 | 3,732,565 | 3,736,001 |
| a | compat | 26,503,064 | 97,987 | 68,241 | 3,701,642 | 3,717,740 |
| b | compat | 15,234,899 | 50,716 | 38,888 | 3,748,913 | 3,758,938 |
| c | compat | 11,623,081 | 48,226 | 32,115 | 3,751,403 | 3,757,961 |
| d | compat | 6,100,432 | 26,660 | 7,925 | 3,772,969 | 3,774,694 |
| e | compat | 20,046,977 | 67,208 | 55,085 | 3,732,421 | 3,746,290 |
| fU | compat | 15,508,662 | 66,858 | 28,155 | 3,732,771 | 3,738,539 |
| fS | compat | 8,235,039 | 32,847 | 15,300 | 3,766,782 | 3,770,218 |

`compat` abbreviates `compat_tetranscripts_mm39`. Membership and input length sums are 3,764,949 / 1,116,605,808 bp for interspersed and 3,799,629 / 1,121,476,301 bp for compat (`B/universes.json`; `B/tables/universe_summary.tsv:3-4`).

Define gain per record as `|record ∩ (opposite_exon_union \ same_exon_union)|`: precisely a−b or fU−fS removed bp. Opposite-strand-only **removal c** also removes bases annotated on both strands, so its total differs from the gain.

| Annotation | Universe | Opposite-only gain bp | Records gaining bases | Fully removed → retained |
|---|---|---:|---:|---:|
| vM37 | interspersed | 11,125,985 | 76,971 | 46,075 |
| vM37 | compat | 11,268,165 | 78,207 | 47,271 |
| 10x | interspersed | 7,209,038 | 46,582 | 33,457 |
| 10x | compat | 7,273,623 | 47,136 | 34,011 |

The vM37 both-strand exon intersection accounts for 354,062 interspersed and 354,916 compat record-bp. Protein-coding and basic masks leave respectively **20,256,051 and 6,437,658 interspersed bp** overlapping excluded exon types/tags; their exon unions are 75,875,592 and 132,600,517 bp. These are measured support differences, with read-count effects awaiting a consumer experiment (`C/gene_child_consult.md:31-41` distinguishes these units).

## Q2. What the 10x GTF is

The reference directory containing G10 is `refdata-gex-GRCm39-2024-A`; its `reference.json:10-16` names `gencode.vM33.primary_assembly.annotation.gtf.filtered`, `mkref_version = 8.0.0`, release `2024-A`. `G10:1-5` confirms M33 / Ensembl 110, dated 2023-03-07. `G37:1-5` identifies M37 / Ensembl 114, dated 2025-01-19. G10 stores versionless gene/transcript IDs plus separate version attributes (`G10:6-10`).

| Measured property | vM37 | 10x 2024-A |
|---|---:|---:|
| Gene rows / distinct gene IDs | 78,317 | 33,696 |
| Transcript rows | 278,369 | 125,556 |
| Exon rows | 1,298,921 | 834,423 |
| Unstranded exon union bp | 160,549,642 | 114,032,813 |
| Exon union blocks | 357,216 | 254,763 |
| Transcript-span union bp | 1,486,451,442 | 1,198,967,637 |
| Contigs with annotation | 38 | 35 |

Observed G10 gene-biotype roster: **21,478 protein_coding, 11,521 lncRNA, 697 IG/TR**. The latter comprise `IG_C_gene` 13, `IG_C_pseudogene` 1, `IG_D_gene` 19, `IG_J_gene` 14, `IG_LV_gene` 4, `IG_V_gene` 218, `IG_V_pseudogene` 158, `TR_C_gene` 8, `TR_D_gene` 4, `TR_J_gene` 70, `TR_J_pseudogene` 10, `TR_V_gene` 144, `TR_V_pseudogene` 34. This includes immune pseudogenes and noncoding transcript types within retained protein-coding genes (`G10:7`). The input metadata records a filtered source; the exact filtering command and unfiltered M33 comparison are unavailable here. Release changes and filtering therefore remain combined effects.

**Namespaces.** G10 uses `chr1`–`chr19`, `chrX`, `chrY`, `chrM`, plus 13 accession names: `GL456210.1`, `GL456211.1`, `GL456212.1`, `GL456219.1`, `GL456221.1`, `GL456354.1`, `JH584295.1`, `JH584296.1`, `JH584297.1`, `JH584298.1`, `JH584299.1`, `JH584303.1`, `JH584304.1`. All **35/35 match `chrom_gencode`**; 22 match `chrom_ucsc`, 13 match `chrom_ensembl`/`chrom_genbank`, and zero match `chrom_refseq`. Alias normalization maps all 35 to UCSC with zero unknown names; use the table, including scaffold mappings (`B/tables/contig_aliases.tsv:1-62`; namespace contract `docs/OUTPUTS.md:526-549`).

The G10 annotation covers 35 of the parent's 61 contigs; its 26 unannotated contigs carry 2,825 all_rmsk / 1,749 interspersed / 1,892 compat records. These receive unchanged subtraction geometry with annotation-coverage status kept explicit. The corresponding vM37 figures are 23 contigs and 2,638 / 1,612 / 1,754 records.

G10's exon union is smaller by 46,516,829 bp. Exact set differences are **46,547,211 vM37-only bp and 30,382 G10-only bp**; the masks differ in both directions. A changed record intersects the symmetric difference of the two relevant exon unions, using its strand for b/fS. Comparing exact geometry detects changes even when removed lengths happen to tie; observed changed records with tied lengths: zero.

| Comparison, vM37 → G10 | Universe | Changed records | Less / more removed in G10 | Fully removed → retained | Retained → fully removed | Net retained gain bp |
|---|---|---:|---:|---:|---:|---:|
| a → fU | interspersed | 74,464 | 74,378 / 86 | 30,327 | 49 | 10,874,878 |
| a → fU | compat | 75,416 | 75,328 / 88 | 31,178 | 49 | 10,994,402 |
| b → fS | interspersed | 43,487 | 43,442 / 45 | 17,686 | 26 | 6,957,931 |
| b → fS | compat | 43,760 | 43,714 / 46 | 17,895 | 26 | 6,999,860 |

Across all_rmsk, 97,410 unstranded / 56,444 same-strand outcomes change. Examples in both requested universes: `L1Lx_III|chr1:3143262-3143531|+` loses 56 bp under vM37 and zero under G10; `MIRb|chr1:3437859-3437959|-` loses 101 versus zero; `ORR1F|chr1:63158047-63158145|+` loses zero versus 99. The exact changed-ID set is defined above and fingerprinted below; a record listing would exceed this consult's format.

## Q3. Strand and chemistry

A same-strand mask preserves the TE's RepeatMasker orientation in SAF and assumes the counting run reconstructs **RNA orientation** correctly. Its guarantee is zero same-strand exon overlap. A feature-sense count can use the retained opposite-exon support; an unstranded or TE-antisense count can admit that exon's host RNA. The TE-antisense channel therefore needs its own declared support policy or the conservative all-strand mask. SAF records geometry; it cannot encode the assay's read-to-RNA conversion (`docs/OUTPUTS.md:23,387-389`; `docs/DECISIONS.md:38-42`).

The local toolkit documents featureCounts `-s 0/1/2` as unstranded/forward/reverse and explains why reverse dUTP libraries use `-s 2` for biological sense (`K/docs/BIOLOGY.md:167-189`); its paired pass uses `-p --countReadPairs -B -C` (`K/scripts/runFeatureCounts.sh:171-188`). This bulk convention supplies no 10x chemistry calibration.

**General counter semantics beyond the available local manuals:** for a single mapped cDNA read, featureCounts `-s 1` selects the read/feature same-strand relation and `-s 2` reverses it; STARsolo `--soloStrand Forward`, `Reverse`, and `Unstranded` select the corresponding annotation relation. For paired featureCounts input, the convention is relative to read 1. These recalled API semantics need the consumer's pinned executable/help and synthetic fixture; STAR and featureCounts are absent here, and the checked-in STARsolo recipe omits `--soloStrand` (`X/TEsingle_benchmarking_scripts/software_running/T2T_STARsoloTE.sh:46-64`). The flag governs feature assignment, while the mapper still aligns genomic alternatives.

| Chemistry/layout question | Evidence available locally | Consequence for the pilot |
|---|---|---|
| 10x 3′ / ARC R2-only | The Martirosyan recipe uses R2 as cDNA, R1 as barcode, then TEsingle `forward`, thereby **assuming R2 sense** (`X/TEsingle_Martirosyan_analysis_code/TEsingle/run_STAR_TEsingle.sh:17-24,58-60,92-96`). TEsingle's help broadly calls 10x second-strand (`X/TEsingle/TEsingle:83-87`). The recorded ARC BAM is R2-only (`C/field_practice_synthesis.md:156-165`). | Treat R2-sense as the recipe hypothesis. The accessible evidence does not certify the exact ARC chemistry; measure R2 strand against isolated, unambiguous genes. |
| 10x 5′ PE OCM v3 | The records establish that **both cDNA mates align**, and identify the kit, without establishing which mate is RNA-sense (`C/field_practice_synthesis.md:156-187`). | Measure sense fractions separately for R1 and R2, verify pairing and input order, and calibrate the fragment's orientation. A generic 10x `forward` default cannot settle this kit's mate convention. |

Settle each chemistry with an isolated-exon strand audit on both gene strands, splice-junction support, declared barcode/UMI eligibility, and known-answer same/opposite exon–TE fragments. Compare a/b/fU/fS using identical molecules, reporting gained molecules by host-relative strand, first/last exon and TSS/TES distance, gene/TE ambiguity, and molecule conservation. Measure 5′ RNA-oriented endpoints relative to validated starts before claiming promoter enrichment; interval overlap alone supplies no initiation evidence (`C/field_practice_synthesis.md:183-187`). These are proposed consumer measurements; this consult measured annotation only.

TEsingle applies each BAM record's own `is_reverse` and groups mates as alignment alternatives (`X/TEsingle/TEtools/AlignmentIO.py:4-10,60-76`); anchoring requires exactly one entry (`TEtools/Counters.py:71-72`). Its paired-mate handling needs qualification or an explicit single-mate route before using the OCM comparison. IRescue likewise applies strand to individual BAM-derived blocks (`X/irescue/irescue/map.py:310-332`); its paired representation also belongs in that fixture.

## Q4. The EM-facing route

**Preserve full TE intervals so a consumer can model the candidate origins.** Subtracting exon bases removes TE candidates before EM. The source qualifies the question's premise: a full gene GTF is necessary for the intended joint gene/TE model, while IRescue's standard TE-only model has a different interface.

| Route | Source-confirmed inputs and competition | te-tracks contribution |
|---|---|---|
| TEsingle | Separate gene and TE GTFs; genes indexed from `transcript` rows using `gene_id` (`X/TEsingle/TEsingle:77-87,106-112`; `TEtools/GeneIndex.py:153-189`). Each TE row becomes a candidate with transcript/subfamily/family/class identity (`TEtools/TEindex.py:293-337`). Gene-only molecules bypass EM; TE-containing molecules enter it after gene/TE weighting (`TEtools/Counters.py:19-48,195-201`). | Core `interspersed/full/record.gtf`; the pinned complete gene GTF, including transcript rows, comes from the annotation dependency. |
| IRescue | BAM plus custom TE BED; BED column 4 defines locus/subfamily identity (`X/irescue/irescue/main.py:36-82`; `map.py:61-84`). BED overlaps supply the candidate features (`map.py:310-332`); EM allocates ambiguous UMIs among those features (`count.py:249-297`). No gene-GTF argument is present. | Core full `record.bed` or `subfamily.bed`, according to the declared estimation grain. Gene counts and host context are separate consumer evidence. |
| Recorded STARsolo-TE comparator | Combined gene+TE GTF for the index (`X/TEsingle_benchmarking_scripts/index_generation/T2T_STAR_index_generation.sh:46-62`); `GeneFull` and `--soloMultiMappers EM` at count time (`software_running/T2T_STARsoloTE.sh:48-52`). | Full TE GTF plus full gene annotation in the consumer's combined index. A record-as-gene GTF profile needs the C8 ruling because today's `record.gtf` has `gene_id = subfamily` (`docs/OUTPUTS.md:317,347-376`; `C/adr_rulings_2026-09-17.md:95-97`). |

The IRescue benchmark itself converts intact TE-GTF coordinates directly to locus/subfamily BEDs (`X/TEsingle_benchmarking_scripts/index_generation/T2T_iRescue_BED_generation.sh:8-13`). These parsers can accept changed coordinates; the recommendation for full features preserves the intended hypothesis space rather than claiming a syntactic requirement. The recorded STARsolo command demonstrates multimapper EM; its treatment of a single alignment overlapping both a gene and a TE still needs a known-answer competition fixture. EM assignment itself establishes model allocation, with autonomous transcription remaining a consumer interpretation.

**Child delivery:** phase 8 supplies its pinned gene-source provenance, parent/alias pins and explicit context capability `not_computed`; the core supplies the full TE exports. A later child supplies the record × transcript geometry relation and optional Q5 BEDs. An “EM mask” or another clipped TE export has no demonstrated consumer here. The complete gene annotation must remain recoverable under its digest. This preserves the owner's geometry-only ruling and bulk SAF scope (`C/adr_rulings_2026-09-17.md:19-26`; `C/gene_context_adr_brief.md:132-142`; `P/18_phase8_gene_child_seam.md:31-42`).

## Q5. Intron-retention views

Define, per normalized contig and **unstranded**, `T` = union of transcript spans; `E` = union of every exon row; `I` = union of the gaps between consecutive merged exons **within each transcript**; `R` = union of every all_rmsk record. The two views are `pure_intronic = T \ (E ∪ R)` and `pure_exonic = E \ (I ∪ R)`. Using every transcript's introns excludes bases that are exonic in one isoform and intronic in another, including opposite-strand overlaps. Both GTFs have zero transcript-span versus outer-exon endpoint discrepancies. Thus the first view consists of supported intronic bases after global exon exclusion.

| Annotation | Pure intronic bp | Intronic blocks | Pure exonic bp | Exonic blocks | Evaluated bp | Intronic base fraction |
|---|---:|---:|---:|---:|---:|---:|
| vM37 | 799,877,668 | 2,460,261 | 68,441,203 | 275,053 | 868,318,871 | 0.9211796434630292 |
| 10x | 678,389,216 | 2,005,065 | 61,447,575 | 247,032 | 739,836,791 | 0.9169444183534798 |

Recommend optional later child views named, for example, `pure_intronic_no_rmsk_v1.bed` and `pure_exonic_no_rmsk_v1.bed`: merged BED3 support with the table above as acceptance, a 1-bp minimum, and annotation/parent/alias/policy pins. Each pair has six files across the three namespaces; support sizes and block counts remain namespace-invariant. These views exclude **all_rmsk**, including simple repeats and RNA-repeat classes, independently of the TE counting universe. They introduce geometry and acceptance work without requiring the full context relation first.

Acceptance additionally requires pairwise-disjoint blocks and views, intronic containment in T, exonic containment in E, zero overlap with their respective excluded sets, and exact per-contig base conservation. Measure the complement as well as the retained support. This prevents isoform-dependent exon/intron double membership and repeat coverage from contaminating the diagnostic. The full-genome bedtools/Python agreement below settles the geometry gate; a consumer coverage fixture settles usage.

The **consumer** obtains coverage-depth sums `C_I = Σ depth(x)` on the intronic BED and `C_E` on the exonic BED, and computes the owner's supplied formula:

`U = [C_I / (C_I + C_E)] / [L_I / (L_I + L_E)]`, where `L_I,L_E` are the corresponding BED lengths (`docs/_internal/redesign-2026-09/prompts/mask_consult.md:37-40`).

Pin split-aware aligned-base coverage, paired-overlap treatment, molecule/duplicate treatment, strand policy, multimapper weights, barcode set and sample/cluster pooling. Use both numerator and denominator from the same eligible alignments and regions; zero total coverage gives unavailable U. Coverage sums differ from counts of overlapping reads or summed gene expression. No BAM coverage or U was computed here.

By algebra, U equals intronic mean depth divided by pooled mean depth on these views; zero intronic coverage gives U=0, and equal intronic/exonic mean depths give U=1. Interpreting U as an unspliced fraction requires the coverage model and representative sampling assumed by the paper; capture bias, expression-weighted gene lengths and internal priming can violate it. These limitations are statistical/biological reasoning beyond the supplied implementation. U can exceed 1 under unequal coverage and should retain that diagnostic value rather than be silently clipped.

A higher U indicates more intronic coverage relative to evaluated base availability, strengthening the host pre-mRNA explanation for intronic TE-associated signal. The local records report 55% intronic alignments in a nuclei window versus 20% in a whole-cell window (`C/field_practice_synthesis.md:107-109,200-207`); those percentages are distinct from U. Compare matched annotations, filters and cell types before attributing a nuclei–whole-cell difference to biology. U describes a sample or cell group's background; attribution of an individual TE, or automatic subtraction of U from its count, requires a further model and evidence.

## Q6. Recommended policy set and delivery

| Recommendation | What it prevents | Settling measurement |
|---|---|---|
| Phase 8: `all_exons_unstranded_union_v1`, minimum block 1; all exon rows of the chosen pin. | Residual counted-exon support under an all-exon gene pass; silent length filtering; record/block confusion. | Q1 a and per-record conservation; central-exon split, complete loss and 1-bp fixtures; zero residual exon overlap. Correct plan 18's anchor to 3,701,642 retained compat records / 3,717,740 blocks (`P/18_phase8_gene_child_seam.md:26-29`). |
| First later snapshot: add `all_exons_stranded_union_v1` **alongside the conservative policy**, with minimum block 1 and explicit policy selection. | Premature use of restored antisense-to-exon support with an unqualified strand/mate convention. | Q1 b plus Q3's per-chemistry molecule comparison and same/opposite-strand fixtures; record the measured 11.13-Mb interspersed gain as available support. |
| Keep protein-coding, basic and opposite-only masks as measured alternatives until a named consumer needs them. | An arbitrary biotype cutoff becoming implicit annotation support; broadening the release roster without a counting requirement. | Q1 d/e/c plus a counting comparison against the consumer's actual gene support. scTE's historical `lincRNA` substring illustrates a silently changing biotype rule (`C/sctefinder_scte_notes.md:25-35`). |
| Build a G10-pinned child in phase 9 or immediately after the host build, retaining the same default; require the corresponding snapshot for GEX-2024-A consumers. | A 74,464-record geometry mismatch masquerading as matched gene/TE annotation. | Q1 fU/fS, Q2 IDs/digests, and consumer annotation-pin equality. The GEX GTF establishes neither the ARC GTF's digest nor its equivalence; obtain that pin before the ARC pilot (`C/adr_rulings_2026-09-17.md:103-111`; `C/gene_context_adr_brief.md:104-109`). |
| Keep full core features for EM; add Q5 BEDs as optional later geometry views. | Pre-emptive deletion of EM candidates, or storing assay-specific U/TE-origin labels in the reference. | Tool-specific candidate/UMI fixtures, Q5 interval acceptance and coverage/zero-denominator fixtures in the consumer. |

**Cost of every added mask policy:** one SAF pair (`subfamily`, `taxonomy_triple`) per universe, hence six physical files across UCSC/Ensembl/GENCODE; compat adds another six. Each policy needs the Q1 record/block/base anchors, strand/threshold fixtures, per-record status and block registrations, inventory and namespace checks. For the proposed stranded policy, this is 3,724,927 interspersed or 3,758,938 compat rows **per SAF**, and 7,449,854 or 7,517,876 registration rows for the two groupings; namespaces share registration. A full-catalog status table adds 5,320,771 policy-scoped rows. Serialized bytes and build time remain unmeasured.

Each variant must be selectable in the export path/registration and bind its policy identifier, strand rule, GTF digest and minimum block size. Adding a policy changes the child's declared roster/policy bundle and BUILD_ID; the parent CATALOG_ID and record keys persist. A G10 snapshot separately pins its annotation digest even when some exports happen to agree. This follows the identity model (`docs/DECISIONS.md:34-42,66-76`; `C/gene_child_consult.md:19-29,63-65`). G10 reduces the stranded gain to 7.21 Mb but leaves the chemistry gate and conservative default appropriate. Every mask guarantees interval support; a spliced read or paired fragment can still touch separate gene and TE blocks, so molecule exclusivity belongs to the joint counting run.

## Measurements performed (methods, agreement checks, exact numbers)

Inputs: `B = /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build`; `G37 = /data2/users/shared/refcache/mm39/mm39_20260911/gencode.vM37.primary_assembly.annotation.gtf.gz`; `G10 = /workspaces/Meta-Aging/_scratch/te-tracks-audit/refs/refdata-gex-GRCm39-2024-A/genes/genes.gtf.gz`. All annotation censuses and interval tables above were computed from these files, independently of earlier consult totals.

- Parent BUILD_ID: `9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d`; CATALOG_ID: `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` (`B/BUILD_ID:1`, `B/CATALOG_ID:1`).
- G37 compressed MD5 `702e27a8727db66cd23e9f66f5aa1d38`; SHA-256 `0d1673f3c0fff7d28ff63f4443a0863fa25f817d391982e465f7ec20f256bcd0`; 37,339,119 bytes.
- G10 compressed MD5 `7a998f670d6d0bdf599c046284da051b`; SHA-256 `dfc17ee4c85f3d7665f48fe758f9a1109c3cc4c38a4185943e9e9678fae45fe6`; 35,433,441 bytes. `reference.json:6` also records its own `gtf_hash.gz`; the independently computed hashes here identify the supplied bytes.
- `B/tables/rmsk_records.parquet` SHA-256 `d5deabd4ae015204a2277093bf41ef4bbb597a74313e54d13e0f479eab17f33a`; alias table SHA-256 `4c2c18fdfae512f44789831b3eb2b8716e65e80da7fab41208a36e0053ca50c9`.
- Checked source HEADs: TEsingle `655f127`, IRescue `26f36fb`, benchmarking scripts `6e85f5d`, Martirosyan analysis `f147250`. Toolkit source was read in place; its submodule gitdir is unavailable in this checkout.

**Chr1 gate, completed before genome-wide subtraction:** write all 377,297 chr1 records as BED6, preserving strand and a unique row key. Run `bedtools subtract -a chr1.records.bed -b chr1.policy.raw_exons.bed`, adding `-s` for b/fS or `-S` for c. Bedtools 2.31.1 sees the raw selected exon rows. Independently, Python sorts/merges the masks and sweeps each sorted record, emitting every retained piece. Compare each `(record_key,start0,end0)` tuple, including end-of-stream; all seven comparisons agree exactly, over the complete chr1 catalog and thus both requested subsets.

| Policy | All_rmsk retained blocks compared | Interspersed: removed bp / full / partial / blocks | Compat: removed bp / full / partial / blocks |
|---|---:|---:|---:|
| a | 366,508 | 1,939,430 / 7,359 / 4,745 / 258,373 | 1,947,389 / 7,412 / 4,751 / 260,072 |
| b | 371,952 | 1,052,748 / 3,672 / 2,677 / 261,660 | 1,060,243 / 3,715 / 2,684 / 263,369 |
| c | 371,726 | 906,922 / 3,751 / 2,224 / 261,360 | 907,499 / 3,762 / 2,224 / 263,102 |
| d | 373,916 | 320,087 / 1,690 / 422 / 263,074 | 322,422 / 1,708 / 420 / 264,808 |
| e | 369,585 | 1,454,328 / 5,122 / 3,801 / 260,450 | 1,462,734 / 5,179 / 3,805 / 262,145 |
| fU | 370,148 | 981,837 / 4,537 / 1,668 / 260,465 | 983,773 / 4,553 / 1,667 / 262,201 |
| fS | 373,872 | 491,603 / 2,157 / 860 / 262,695 | 493,610 / 2,172 / 859 / 264,432 |

Chr1 inputs are 264,675 interspersed records / 80,840,586 bp and 266,428 compat records / 81,042,100 bp. For the genome, NumPy binary searches on disjoint mask starts/ends plus cumulative mask lengths evaluate `removed = F(end0) − F(start0)`, where F is covered length below a coordinate. Retained block count is `overlapping_mask_blocks + 1 − first_base_covered − last_base_covered`. This third calculation matched every chr1 record's sweep lengths/block counts before its genome use. Assertions checked that zero blocks correspond exactly to full removal; universe predicates reproduced the input counts and sums.

The default reproduces the prior compat anchor exactly: 3,633,401 unchanged, 52,842 trimmed, 15,399 split, 97,987 fully subtracted; 3,717,740 blocks; 1,094,973,237 retained + 26,503,064 removed = 1,121,476,301 bp (`C/gene_child_consult.md:41`). Interspersed retained bp under a/b/fU/fS are 1,090,369,890 / 1,101,495,875 / 1,101,244,768 / 1,108,453,806.

**Q5 independent genome check:** derive transcript introns before union; form the two exclusions and subtract with Python interval sweeps. Separately run bedtools subtraction on the transcript/exon unions against the appropriate merged excluded sets, comparing every output interval genome-wide; all four views agree. All_rmsk union is 1,192,661,541 bp in 4,036,858 blocks. Intron unions before exclusions are 1,406,892,198 bp (vM37) and 1,129,095,689 bp (G10). Chr1 pure-intronic/pure-exonic checks: vM37 59,127,247 / 4,503,355 bp in 176,400 / 17,703 blocks; G10 49,081,487 / 4,014,984 bp in 139,716 / 15,712 blocks.

Changed-record identity fingerprints: SHA-256 over C-sorted `rmsk_record_id` strings, each followed by one LF. Reconstruct each set with the symmetric-difference intersection predicate in Q2.

| Mask comparison | Universe | Changed-ID SHA-256 |
|---|---|---|
| a → fU | interspersed | `5f19d88e9140085ca4a132368ff6b8d029398586729291ced46c75c96a510303` |
| a → fU | compat | `a4f3a71cd9b8bed492134284226ffe7c1622de62b906af6c7f0faa5dca73f4a6` |
| b → fS | interspersed | `6d98396603e014414d0ed3c99253aabc8b13d37d21992a2b513dc43598903d0e` |
| b → fS | compat | `45654069062cf73c77d9c10bde2e32df15c4c8524ac53fa9cd657bad3cdb42bd` |

All Python runs exported `PYTHONDONTWRITEBYTECODE=1`. Scratch scripts, BEDs, logs and intermediate results were confined to `/workspaces/Meta-Aging/_scratch/te-tracks-audit/mask-consult/` and removed with Python `shutil`. The consult is the sole durable output; sources and checkouts remain inputs. No network, installs or implementation tests were used.

## Open for the owner

1. Adopt the phase 8 default-only roster and schedule the stranded companion in the first later snapshot, conditional on the Q3 pilot; name the consumer responsible for that gate.
2. Schedule the GEX-2024-A child and acquisition of the actual ARC annotation pin. The measured GEX mismatch settles the need for annotation-specific geometry.
3. Decide whether the optional Q5 geometry pair should accompany that snapshot. Its consumer must specify coverage eligibility and pooling before interpreting U.
