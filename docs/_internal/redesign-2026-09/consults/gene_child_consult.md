# Phase 8 design consult: the gene child family (codex gpt-6-astra)

## Summary of recommendations

1. One `te_mm39_gene` family, with immutable snapshots binding one parent, GTF and versioned policy bundle; SAF and eventual context share that scope.
2. Dispatch by family, retain `GENOME=mm39`, verify an exact parent archive, and copy its alias/length table byte-for-byte into the child.
3. Keep `all_exons_unstranded_union_v1`; explicitly retain every positive-length block (`min_retained_block_bp=1`).
4. Keep subtraction and context statuses separate; correct the compat anchor to **3,717,740 blocks from 3,701,642 retained records**.
5. Specify sparse transcript geometry now; ship it in a later snapshot of the same family after its ADR and scaling gate, with phase 8 declaring context `not_computed`.
6. te-tracks owns pinned reference relations; consumers own versioned labels. Add gene-body geometry for the bulk windows and explicit reconciliation of counting annotations.
7. Ship the two SAF groupings in three namespaces; use the core GTF routes for TEtranscripts/TEsingle/TElocal. Admit subtracted BED/GTF through separate consumer fixtures.
8. Pin independently authored geometry and dependency fixtures, plus the measured record/block/base censuses below.

Citations: `T` = `/workspaces/Meta-Aging/01_modules/te-tracks`; paths without a prefix are relative to T. `C` = `T/docs/_internal/redesign-2026-09/consults`; `R` = its sibling `reviews`; `P` = `T/docs/_internal/_project/plans/2026-09-16_te-tracks-redesign`.
`X` = `/workspaces/Meta-Aging/01_modules/.ref`; `K` = `X/14839-DM-cGAS/01_modules/TE-RNAseq-toolkit`; `D` = `/workspaces/Meta-Aging/14761-DM/docs/_internal/_project/plans/2026-09-11_codebase-topology`; `L` = `/workspaces/Meta-Aging/14761-DM/01_modules/scio/skills`. `B` and `G` below denote the exact build and GTF paths in the measurement commands. Proposals below require the owner's ruling; measurements describe these pins only.

## Q1. Topology

**Evidence and options.** ADR 4 adopts core → gene child, and ADR 7 separates catalog identity from build identity (`docs/DECISIONS.md:34-42,66-75`; H5, `R/m2_rulings.md:74-78`). One child snapshot containing both products gives one annotation/policy scope; changing context parameters changes its BUILD_ID even when SAF bytes stay identical. Separate product children allow independent release schedules but require consumers to check matching parent, annotation and mask semantics. Several named views in one snapshot support sensitivity comparisons, at the cost of a policy map, larger inventories and an explicit view pin. These choices are partly orthogonal: two products already constitute named views within one family. The earlier one-core-build proposal was superseded by the two-family resolution (`C/ADR4_consult.md:87-91`; `C/FINAL_REPORT.md:143-150,238`).

**Recommendation and settling measurement.** Choose one family and one annotation per snapshot; use one versioned policy bundle containing mask, normalization, minimum block size, context capability and, when delivered, transcript selection, geometry, sparsity and promoter parameters. Hash the declared values as well as the policy identifier. The scientific tuple `(parent_build_id, GTF digest, policy id)` identifies a recipe; BUILD_ID additionally binds schema, roster and bytes. Copy the parent's catalog identity, giving `CATALOG_ID == parent_catalog_id`; keep both parent pins non-null. A GENCODE bump creates another child archive and preserves the core and ledger keys. Consumers pin child BUILD_ID, parent IDs, export/view path and digest; D2 places child provenance on its context satellite. Settle with tiny mutation fixtures: GTF, policy, capability and roster changes move child BUILD_ID; parent BUILD_ID/CATALOG_ID remain fixed; identical inputs and serializer reproduce bytes (`docs/RELEASES.md:40-88,148-156`).

## Q2. Architecture

**Evidence and options.** `build.sh:48-56,68-93` currently derives family from the config argument and runs every numbered shell stage. `manifest.py` requires four core source roles, local catalog tables and null parents (`src/lib/manifest.py:135-158,239-281,375-431`); `SPECIES` admits `mm39` (`:37`). The family regex already admits `te_mm39_gene` (`src/release.py:24-29`). Choosing `current` repeatedly risks mixed parents; an explicit archive or `(root, family, full BUILD_ID)` resolves one parent. Alias symlinks violate the regular-payload rule (`src/lib/manifest.py:99-108`); a digest-only external lookup needs new preflight plumbing, while an exact small copy works with today's enclosing-directory lookup (`bin/te-tracks-preflight:41-56`). Milestone 7 now explicitly requires dependency availability before install, select and verify-current (`R/m7_rulings.md:20-31`).

**Recommendation.** Add explicit family/config dispatch, preserving the existing core invocation; e.g. a gene-family selection chooses `config/mm39_gene.env` with `GENOME=mm39`, `FAMILY=te_mm39_gene`, `PARENT_FAMILY=te_mm39`, the pinned GTF and policy bundle. Keep family separate from assembly rather than inventing species `mm39_gene`. Require a full parent BUILD_ID plus root, or an explicit verified parent directory for scratch builds; record absolute acquisition paths only as provenance. If `current` is accepted as convenience input, resolve once and check the requested full ID before reading anything. Child stages consume the parent's verified records, taxonomy and universes without rerunning core stages. Copy `universes.json` and `tables/contig_aliases.tsv` by digest; publish child annotation coverage in `tables/gene_annotation_coverage.tsv`, with per-contig gene, transcript and exon row counts and declared coverage semantics. Reuse label construction, sorting, namespace renaming and inventory primitives, parameterized with explicit parent input directory, child output directory, universe, variant, blocks and export roster. `write_registration` hardcodes `full`, the exporter accepts only core sets, and namespace orchestration rebuilds aliases against a core roster (`src/lib/build_exports.py:191-227,303-333`; `src/lib/contigs.py:125-147`); the small `rename_export` primitive is already reusable (`:86-122`). The child owns `tables/exports.tsv`, registration and a complete inventory of its own files, with two registered SAF spellings per retained block and shared registration across namespaces (A1/A2, `R/m5_rulings.md:26-34`).

**Identity/verification and settling measurement.** Introduce a published child manifest schema branch while preserving core schema-1 verification. The child inherits the verified parent's catalog object, assembly, species and taxonomy/universe declarations; its own source roles include the retained GTF with MD5, SHA-256 and bytes, outside `catalog.sources`. Pin copied-input digests and parent family/IDs; do not fabricate local core source entries. Child verification resolves the parent's immutable archive, recomputes both IDs, checks family/assembly and catalog equality, compares inherited/copy declarations and validates child registration against parent records. Give standalone verification an explicit parent-root/directory resolver; publication derives the sibling parent archive from the destination root and requires the dependency there. Extend install/select/verify-current accordingly (`src/release.py:53-100,118-148`); reuse their locking/atomic selection. Verify every archive against its own declared roster and published policy/schema versions, preserving P7's rule and the `build_sources`/catalog boundary (`R/p7_rulings.md:51-70,124-132`). Settle with missing/wrong/corrupt parent, changed `current`, wrong assembly, alias-copy corruption, relocation/transfer, old-core/new-child reselection and repeated child publication fixtures; retain all dependency archives (`docs/RELEASES.md:130-156`).

## Q3. The exon mask

**Evidence and options.** The lab extracts every exon and subtracts without `-s` (`L/te-reference-saf-build/scripts/build_te_saf.sh:95-124`); its gene driver supplies `-f exon -g gene_id`, translated to `-t exon` without `-M` (`K/scripts/runFeatureCounts_TE_and_genes.sh:172-180`; `K/scripts/runFeatureCounts.sh:180-188`). All/basic/canonical/protein-coding exon unions are respectively 160,549,642 / 132,600,517 / 112,655,476 / 75,875,592 bp (independently reverified in `C/gene_context_material.md:227-235,352-356`; all-exon value remeasured below). Narrower masks retain more sequence overlapping the gene pass's annotation; these differences are genome-wide union differences, **not measurements of TE bases or double-counted reads**. TEtranscripts and TElocal index gene exons; TEsingle indexes whole transcripts, and MATES removes whole records overlapping gene bodies (`X/TEtranscripts/bin/TEtranscripts:764`; `X/TElocal/TElocal:605`; `X/TEsingle/TEsingle:107-112`; `X/MATES/build_reference.py:88-89,127-149`). Exon subtraction therefore matches the lab's interval support; it does not emulate every tool's assignment model.

**Recommendation and settling measurement.** Keep all exons, both strands, with alias normalization before union/subtraction; retain blocks of at least one base and record that threshold explicitly. A larger threshold is an additional support filter: it can remove formerly retained records, and conservation must separate `masked_bp` from `length_filtered_bp`. At a 20-bp threshold, 56,863 currently retained compat blocks would be discarded (measurement below); their molecule-count effect is unmeasured. Admit narrower/stranded masks as named policy variants only with a consumer. Settle competing policies by measuring TE-intersection bp, retained records/blocks and threshold-discarded bp under each, then the consumer's counting fixture. Correct G2's guarantee to exon-disjoint support, as adopted in `docs/DECISIONS.md:41-42`; `K/docs/METHODOLOGY.md:168` overclaims molecule exclusivity.

## Q4. Piece registration and status

**Evidence and options.** The registration key already includes both block bounds (`docs/OUTPUTS.md:399-415`; `R/m5_rulings.md:26-28`). A shared per-record table saves a join but couples mask and context policies and release schedules; separate tables keep their different meanings explicit. H3 forbids deriving D2 labels from subtraction status (`R/m2_rulings.md:95-97`). The legacy audit reports **data rows**, whereas plan 18 calls them retained records (`K/docs/_internal/research/2026-06-16-TE-annotation-prep/SAF_on_disk.md:25-40`; `P/18_phase8_gene_child_seam.md:26-29`).

**Recommendation and settling measurement.** Keep `exon_subtraction_status` separately, over the full parent catalog, with status, `n_pieces`, retained and removed bp; scope it by the child's policy. `unchanged`: zero removed bp; `trimmed`: one smaller piece; `split`: multiple pieces; `fully_subtracted`: zero pieces. Register each retained block with its original parent ID; a coordinate-sorted piece index is optional convenience, outside the canonical record identity. Fully subtracted records retain status and universe membership, with zero SAF/registration rows; consumers recover them by left join and distinguish excluded support from an observed zero count. The complete compat calculation gives 3,799,629 input records, **3,701,642 retained records**, **3,717,740 blocks**, 97,987 fully removed, 15,399 split, 52,842 trimmed, and 3,633,401 unchanged; 26,503,064 bp removed and 1,094,973,237 retained. Independent bedtools subtraction reproduces the block/record/base totals. Amend the acceptance anchor's unit; require disjoint contained blocks, zero residual mask overlap, per-record length conservation, key uniqueness and distinct-feature counting after any membership join (`C/ADR4_consult.md:53-55,97`).

## Q5. The context relation

**Evidence and options.** The proposed sparse rule includes every body overlap, promoter overlap and same-contig transcript tied for globally nearest TSS, TES or exon boundary (`C/ADR4_consult.md:13-30`). Nearest-only/canonical-only relations reduce size but discard overlapping hosts and isoform disagreement; a dense cross product has 1,481,137,702,499 pairs before contig filtering. Keep all isoforms, one pair with combined flags, normalized transcript/segment dimensions, exact intersection blocks and a boundary-tie relation. `Ensembl_canonical` is a selectable flag; vM37 has no `MANE_Select` transcripts (`C/gene_context_material.md:218-230`). Exact blocks support D2's sub-peak requirement (`D/02_next_session_agenda.md:35-43`); aggregate overlap bp alone cannot locate an overlap within a peak.

**Geometry recommendation.** Compute on original core records, including fully masked records. For record `[a,b]`, landmark base `p` and transcript sign `s`, use `s*(min(max(p,a),b)-p)`; TSS/TES swap ends on minus strand. For exon cuts use record extent `[a-1,b]`, preserve all nearest cut ties and distinguish touching from base overlap. Introns are gaps in each transcript's merged exons; preserve exon parentage and exact source gene/transcript IDs with version suffixes. Key transcripts by source ID plus locus/strand, validate parentage and bounds, and report missing or unsupported exon structure explicitly. Publish body/exon/intron/promoter overlap bp and `relative_strand=same|opposite|unknown`; these are simultaneous relationships. Promoters contain bases `-U <= s*(x-tss) <= D`, hence U+D+1 bases before contig clipping, with coordinates and `(U,D,promoter_policy_id)` stored. Keep genomic distances; spliced distances require their own definition. These conventions follow `C/ADR4_consult.md:15-30` and need both-strand, one-base and tie fixtures.

**Coverage, size and delivery recommendation.** Keep a separate complete record status relation when context ships: `evaluated` means all required queries completed, including evaluated records with no body overlap; `contig_outside_annotation` means no transcript annotation under the declared coverage policy; `unsupported_structure` means required context is incomplete, with transcript/reason details; `not_computed` means the stage was unavailable. Publish partial geometry only with that incompleteness exposed. Phase 8 should declare capability `not_computed`, permitting consumers to materialize pending status without millions of placeholder rows. Measured: 61 record-bearing contigs, 38 annotated, **23 unannotated contigs carrying 2,638 records**; this corrects the older 59-contig inference (`C/gene_context_material.md:223-235`; current contract `docs/OUTPUTS.md:533-545`).

**Settling measurement.** Exact body-overlap pairs total 14,021,883. A seeded, contig-stratified sample of 11,378 records estimates sparse pair counts of 21.760 million at `(U,D)=(0,0)`, 22.501 million at `(2000,200)`, and 26.817 million at `(10000,2000)`; these are planning estimates, not acceptance counts or adopted promoter windows. At assumed 160–240 text bytes/pair, the middle case is 3.60–5.40 GB; an assumed 72–96 fixed-width bytes/pair with dictionary-coded IDs is 1.62–2.16 GB before dictionaries, compression and auxiliary tables. The 5,320,771 status rows, exact intersections and boundary ties add storage; codec savings remain unmeasured. Implement contig-wise interval/landmark queries and streaming output, avoiding dense joins. Before delivery, measure complete pair/intersection/tie rows, bytes in the chosen serializer, tie multiplicity and peak RSS on chr1, then full mm39. Recommend a later snapshot in the same family, preserving phase 8/9's present delivery boundary (`P/18_phase8_gene_child_seam.md:31-42`; `P/19_phase9_acceptance_park.md:18-20`); shipping context in phase 8 is an owner-approved scope expansion requiring that gate.

## Q6. Where gene_context is computed

**Options and D2 consequences.** (A) te-tracks ships reference geometry; D2 derives `gene_context` under a versioned consumer policy and records context status, child BUILD_ID and label-policy ID on a satellite, exposing the scalar through a joined `te_locus_dim` view. (B) te-tracks also ships a named convenience view; D2 joins its scalar/status and pins that view's version, while retaining access to the relation. This harmonizes labels but makes te-tracks own precedence and window choices. (C) D2 computes against its own GTF; its scalar requires GTF, alias, structure and label-policy pins, plus its own completeness status and tests. This best follows a differing counting reference but duplicates reference derivation. Under every option the current required scalar becomes nullable/pending until computed; retain isoform ambiguity flags rather than silently choosing a transcript (`D/01_consult_codex.md:166,229`; `C/SYNTHESIS.md:180-185`; `C/codex_critique.md:50`).

**Recommendation.** Choose A, with explicitly versioned label precedence and interval scope owned by consumers; consider B once named consumers agree on its semantics. A concrete candidate D2 view exposes exon/intron/body flags and an evaluated-only scalar: `mixed_exon_intron`, `exon_overlap`, `intron_only`, `gene_body_gap`, or `intergenic`, with that precedence; promoter and adjacency flags stay separate. This is a proposed consumer policy for the owner, with the complete relation retained. A changed counting-GTF digest requires normalization and comparison of exon support, transcript/gene spans and relevant identifiers; equal row counts prove no equivalence. Equivalent normalized geometry may be recorded despite different packaging; material differences call for another child against the actual counting reference, or clearly reference-relative labels with the mismatch recorded. Reject G5's unconditional “derive labels … regardless” as a universal reconciliation rule (`C/gene_context_material.md:309-316`; the actual filtered/10x pins remain unverified at `:329-338`).

**Windows and settling measurement.** The bulk requirement is distance from **any gene**, not distance from a promoter (`K/docs/LIMITATIONS.md:125-137`). Preserve the GTF's gene-body table, and derive nearest gene-body distance/ties from it; a transcript-only relation is insufficient. Measured gene union = 1,488,096,243 bp, transcript union = 1,486,451,442 bp; 2,073 records overlap a gene body but no transcript body. Across all_rmsk, substituting transcript spans changes 500 `distance<=10,000` flags and 98 `distance>=20,000` flags. Define gene-body base distance as zero on overlap, otherwise the minimum endpoint separation on the same contig; for evaluated nonoverlapping records, `0<d<=10,000` is adjacent, `d>=20,000` meets the clean-intergenic distance criterion, and `10,000<d<20,000` remains intermediate. Store gene-body geometry even when derived from a declared per-gene transcript envelope for sources lacking gene rows. Pin full-record versus retained-piece label scope; a retained-piece label requires querying the pieces. Settle by comparing labels against actual counting-GTF gene/exon geometry and boundary fixtures at 10,000/10,001/19,999/20,000. Existing grouped counts require recounting for context-stratified abundance (`K/docs/LIMITATIONS.md:130`; `C/ADR4_consult.md:41,97`).

## Q7. Combined-mode counting

**Evidence and options.** The lab driver accepts a path via `-F SAF`, uses `-M` for TEs, counts genes separately and row-binds (`K/scripts/runFeatureCounts_TE_and_genes.sh:117-124,172-189`). Preserve header `GeneID Chr Start End Strand`, 1-based inclusive blocks, original TE strand and repeated group IDs. `subfamily.saf` uses `rmsk_name`; `taxonomy_triple.saf` uses the existing canonical `name:family:class` grammar (`docs/OUTPUTS.md:385-397`). The latter fits the lab's documented three-field label without a rename (`L/annotate-bulk-rnaseq-data/references/te-annotation.md:13-19`); it does not promise byte-identical historical raw labels. The compat universe has 1,225 names and 1,245 raw triples (`B/tables/universe_summary.tsv:3`), while the historical audit reports 1,243 GeneIDs (`K/docs/_internal/research/2026-06-16-TE-annotation-prep/SAF_on_disk.md:25-31`); known packaged-name/family aliases also differ (`C/SYNTHESIS.md:128-134`); validate old-matrix joins separately from accepting the current registered grammar.

**Recommendation.** Deliver the draft interspersed SAF pair in UCSC/Ensembl/GENCODE namespaces, optionally the explicitly requested and inventoried compat pair for legacy membership. Choose the SAF namespace against the actual BAM dictionary and require child preflight; map GTF `chrom_gencode` to canonical before subtraction, including scaffolds. Preflight checks names and lengths and treats reference-only contigs as informational (`bin/te-tracks-preflight:84-101`); prefix stripping alone misses accession mappings (`docs/OUTPUTS.md:526-549`). TEtranscripts and TEsingle accept TE GTFs, and TElocal accepts its own `.locInd`, so a SAF cannot serve all three by renaming (`X/TEtranscripts/bin/TEtranscripts:51-54`; `X/TEsingle/TEsingle:79-82,118`; `X/TElocal/TElocal:109-112`). Keep their core full-GTF/index routes and registered three-/four-part identities (`docs/OUTPUTS.md:368-383,476-478`). Additional subtracted BED/GTF views are feasible but change counting support and require named consumers; repeated GTF rows create individual index entries in the inspected parsers (`X/TEsingle/TEtools/TEindex.py:329-337`; `X/TElocal/TElocal_Toolkit/TEindex.py:419-425`).

**Settling measurement.** Run SAF parser and featureCounts split-block fixtures at both grouping levels, verify emitted IDs against registration and gene IDs against TE IDs before row-binding, and test a paired molecule spanning gene exon/retained TE support in the two separate runs. That measures the molecule-exclusivity limitation rather than assuming it away. Any subtracted GTF promotion must test repeated parent aliases, gap-only reads, length denominators and actual index/count output at the chosen tool version. Existing parser support and absent counting executables remain distinct evidence (`docs/OUTPUTS.md:459-480`); this consult ran no quantifier.

## Q8. Acceptance and fixtures

**Options and recommendation.** Full-build counts alone can reproduce a shared mistake; tiny independently authored interval oracles plus full pinned-input measurements cover geometry and scale. Follow phase 9's independent-oracle rule (`P/19_phase9_acceptance_park.md:3-6`) and extend the tiny publication fixture machinery (`tests/fixtures/publication/build_fixture.py:28-56,59-125`) with an actual core/child dependency. Required fixture answers:

- Record `101..200`, exon `141..160`: pieces `101..140` and `161..200`, same parent ID and group ID; retained/removed = 80/20, status split. Overlapping/antisense exon duplicates change neither union nor answer.
- Record `101..200` wholly in transcript intron `81..220`: unchanged 100/0; context intronic when computed. A matched intergenic control is also unchanged, exercising H3.
- Fully covered record: 0 pieces, fully_subtracted and retained/removed = 0/100; it still appears in the per-record status and context domain.
- Record on a contig without annotation: unchanged support and coverage absence; context stage yields contig_outside_annotation. An unknown or ambiguous GTF alias fails normalization.
- GTF `chr1` mapped through `chrom_gencode` and exported as `1`, plus scaffold `GL456210.1` mapped to `chr1_GL456210v1_random`: the same central-exon split occurs in all namespaces; parent IDs stay fixed. Include an exon on that scaffold, not merely an alias row.
- One-base remainder, touching exon endpoints, a contig-end promoter, both transcript strands, tied landmarks, alternative exon/intron isoforms, unsupported transcript structure, and gene-body gaps between isoforms exercise the future context contract and distance boundaries.

**Numbers and settling measurement.** Pin all measured census fields below by parent/GTF/policy, especially default interspersed: 3,764,949 input records → 3,668,830 retained records / 3,684,934 blocks, 96,119 fully subtracted, retained/removed bp 1,090,369,890 / 26,235,918. At two SAF grammars, registration has 7,369,868 rows across the three namespace exports; compat separately has 7,435,480. Require explicit universe/variant/roster inputs in the fixture, per-record conservation and zero residual overlap; measure final distinct GeneIDs and serializer digests from the implementer's outputs before pinning them. Add dependency/identity evolution cases from Q2 and preserve verification of the current core archive. Acceptance invokes the declared child pipeline and verifies the resolved archive; it never adjusts expected values to a discrepancy (`P/02_orchestration.md:5-9`; `R/m7_rulings.md:32-34`).

## Candidate ADR statements for the owner

1. **G1 — amend, recommended.** One gene family publishes immutable snapshots with one exact parent, annotation and versioned policy bundle; SAF and eventual transcript context are products in that scope, with explicit capability states. BUILD_ID binds the complete declaration and bytes; CATALOG_ID retains the parent's record identity. This prevents mixed-annotation joins and ATAC key churn, while permitting a later context-bearing snapshot (`C/gene_context_material.md:275-281`).
2. **G2 — amend, recommended.** The default mask is every exon on both strands, retaining all positive-length pieces; narrower masks and size filters have named policies. Compat acceptance pins 3,717,740 blocks and 3,701,642 surviving records, with zero residual exon overlap and base conservation. This prevents unmasked annotated-exon support and confusion between piece and record counts; molecule exclusivity stays a counting-run property (`C/gene_context_material.md:283-290`; measurements below).
3. **G3 — amend, recommended.** A sparse record × transcript relation, exact geometry and complete context status support named label derivations; subtraction status remains separate. Scalars may summarize isoform disagreement under a declared rule while the relation retains it. This prevents `unchanged` or missing computation becoming intergenic and prevents a convenience scalar from erasing its evidence (`C/gene_context_material.md:292-298`).
4. **G4 — amend, recommended.** Keep transcript-oriented genomic TSS/TES distances, relative strand, all isoforms/ties and parameterized promoter coordinates; specify exon-cut distances and add gene-body geometry for gene adjacency. This prevents off-by-one boundaries, TSS/TES substitution and treating transcript-union gaps as outside genes (`C/gene_context_material.md:300-307`; Q5–Q6 measurements).
5. **G5 — reject as written; replacement recommended.** te-tracks publishes pinned reference geometry and consumers publish versioned context labels with their actual counting-reference pins. A digest mismatch triggers documented geometry reconciliation or another annotation-pinned child; bulk distance windows query gene-body geometry. This prevents a reference-relative label being presented as the counting annotation's context. A te-tracks convenience view is an **alternative** once its consumer, precedence and validation are agreed (`C/gene_context_material.md:309-316`).
6. **G6 — amend, recommended.** Copy the parent's alias/length table exactly and verify its digest; keep child annotation coverage in a separate inventoried table, defining observed coverage. Normalize all GTF contigs through declared alias columns and fail on unmapped names. This prevents silent scaffold misses, preserves the parent's byte-level alias pin and keeps preflight local to the child (`C/gene_context_material.md:318-323`; `bin/te-tracks-preflight:41-56`).

## Measurements performed

Commands and outputs below are verbatim. The first census independently evaluates the published universe predicates over the parent's parquet, unions 1-based exon intervals after alias mapping, subtracts per record and checks every retained block. The context estimate uses all source transcript rows and exon cuts; it measures candidate-pair cardinality, without certifying transcript structure or producing a context release. The second command independently checks the subtraction with bedtools and compares gene/transcript-body distances. Scratch scripts and BEDs are removed at completion. No builds, counting runs, installs, network calls or git writes were performed.

```bash
export PYTHONDONTWRITEBYTECODE=1
mkdir -p /workspaces/Meta-Aging/_scratch/te-tracks-audit/p8-consult
cat > /workspaces/Meta-Aging/_scratch/te-tracks-audit/p8-consult/measure.py <<'PY'
from pathlib import Path
from collections import defaultdict, Counter
from bisect import bisect_left
import csv, gzip, hashlib, json, re
import numpy as np
import pyarrow.parquet as pq
B = Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build')
G = Path('/data2/users/shared/refcache/mm39/mm39_20260911/gencode.vM37.primary_assembly.annotation.gtf.gz')
for f in ('BUILD_ID', 'CATALOG_ID'): print(f, (B/f).read_text().strip())
for alg in ('md5', 'sha256'):
 with G.open('rb') as h: print('GTF_'+alg, hashlib.file_digest(h, alg).hexdigest())
identity = json.loads((B/'MANIFEST.json').read_text())['identity']
for tag, obj in [('build', identity), ('catalog', identity['catalog'])]:
 raw = json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
 assert hashlib.sha256(('te-tracks-'+tag+'-v1\n').encode()+raw).hexdigest() == (B/(tag.upper()+'_ID')).read_text().strip()
P = B.parent.parent/'pubroot/te_mm39/current'
print('published_identity_equal', json.loads((P/'MANIFEST.json').read_text())['identity'] == identity)
aliases = list(csv.DictReader((B/'tables/contig_aliases.tsv').open(), delimiter='\t'))
amap = {x['chrom_gencode']: x['chrom_ucsc'] for x in aliases}
lengths = {x['chrom_ucsc']: int(x['length_bp']) for x in aliases}
exons, genes, txs, bounds = (defaultdict(list) for _ in range(4))
features, scope, tid = Counter(), set(), {}
with gzip.open(G, 'rt') as h:
 for line in h:
  if line.startswith('#'): continue
  f = line.rstrip().split('\t'); c = amap[f[0]]; a, b = int(f[3]), int(f[4])
  assert 1 <= a <= b <= lengths[c]
  features[f[2]] += 1; scope.add(c)
  if f[2] == 'gene': genes[c].append((a,b))
  if f[2] == 'transcript':
   t = re.search(r'transcript_id "([^"]+)"', f[8])[1]
   assert t not in tid
   tid[t] = (c, len(txs[c])); txs[c].append((a,b,1 if f[6]=='+' else -1))
  if f[2] == 'exon':
   exons[c].append((a,b)); t = re.search(r'transcript_id "([^"]+)"', f[8])[1]
   tc, i = tid[t]; assert tc == c
   bounds[c].extend(((a-1,i),(b,i)))
def merge(rows):
 out = []
 for a,b in sorted(rows):
  if out and a <= out[-1][1]+1: out[-1][1] = max(b,out[-1][1])
  else: out.append([a,b])
 return out
mask = {c: merge(v) for c,v in exons.items()}
ends = {c: [b for a,b in v] for c,v in mask.items()}
print('GTF_counts', json.dumps(dict(sorted(features.items())), sort_keys=True))
print('contigs aliases/annotation', len(aliases), len(scope))
print('exon_union_bp', sum(b-a+1 for rows in mask.values() for a,b in rows))
print('gene_union_equals_transcript_union', all(merge(genes[c]) == merge((a,b) for a,b,s in txs[c]) for c in scope))
D = pq.read_table(B/'tables/rmsk_records.parquet', columns=['chrom','start_1','end_1','rmsk_class','rmsk_family']).to_pandas()
defs = json.loads((B/'universes.json').read_text())['universes']
pred = {x['name']: x['predicate'] for x in defs}
selectors = {'all_rmsk': np.ones(len(D), dtype=bool)}
for u in ('interspersed','compat_tetranscripts_mm39'):
 p = pred[u]; selectors[u] = D.rmsk_class.isin(p['class_in']).to_numpy()
 if 'family_prefix_excluded' in p: selectors[u] &= ~D.rmsk_family.str.startswith(p['family_prefix_excluded']).to_numpy()
counts = {u: Counter() for u in selectors}; residual = 0
for n,(c,a,b) in enumerate(D[['chrom','start_1','end_1']].itertuples(index=False, name=None)):
 rows = mask.get(c, []); j = bisect_left(ends.get(c, []), a); cursor = a; pieces = []
 while j < len(rows) and rows[j][0] <= b:
  x,y = rows[j]
  if cursor < x: pieces.append((cursor, min(b,x-1)))
  cursor = max(cursor,y+1); j += 1
 if cursor <= b: pieces.append((cursor,b))
 kept = sum(y-x+1 for x,y in pieces); removed = b-a+1-kept
 status = 'fully_subtracted' if not pieces else 'unchanged' if not removed else 'split' if len(pieces)>1 else 'trimmed'
 for x,y in pieces:
  k = bisect_left(ends.get(c, []),x); residual += int(k < len(rows) and rows[k][0] <= y)
 for u,selected in selectors.items():
  if selected[n]: counts[u].update({status:1,'records':1,'pieces':len(pieces),'retained_records':int(bool(pieces)),'retained_bp':kept,'removed_bp':removed,'outside_annotation':int(c not in scope),'pieces_lt20':sum(y-x+1<20 for x,y in pieces)})
for u,v in counts.items(): print(u, json.dumps(v,sort_keys=True))
print('residual_piece_overlaps', residual)
print('record_contigs/no_annotation', D.chrom.nunique(), D.loc[~D.chrom.isin(scope),'chrom'].nunique())
rng = np.random.default_rng(20260916); sample_n = 0; estimates = Counter(); exact_body = 0
for c,frame in D.groupby('chrom',sort=True):
 if c not in txs: continue
 t = np.array(txs[c],dtype=np.int64); aa,bb,ss = t.T
 pts = [np.column_stack((np.where(ss==1,aa,bb),np.arange(len(t)))), np.column_stack((np.where(ss==1,bb,aa),np.arange(len(t)))), np.array(bounds[c],dtype=np.int64)]
 pts = [z[np.argsort(z[:,0],kind='stable')] for z in pts]
 ra,rb = frame.start_1.to_numpy(),frame.end_1.to_numpy()
 exact_body += int((np.searchsorted(np.sort(aa),rb,side='right')-np.searchsorted(np.sort(bb),ra,side='left')).sum())
 chosen = rng.choice(len(frame),size=min(len(frame),max(50,round(len(frame)/500))),replace=False); sample_n += len(chosen)
 for j in chosen:
  a,b = int(ra[j]),int(rb[j]); near = set(); body = set(np.flatnonzero((aa<=b)&(bb>=a)))
  for kind,z in enumerate(pts):
   lo,hi = (a-1,b) if kind==2 else (a,b); pos=z[:,0]; l=np.searchsorted(pos,lo); r=np.searchsorted(pos,hi,side='right')
   if l<r: near.update(z[l:r,1].tolist())
   else:
    dist=min(lo-int(pos[l-1]) if l else 10**18,int(pos[r])-hi if r<len(pos) else 10**18)
    for q in (lo-dist,hi+dist): near.update(z[np.searchsorted(pos,q):np.searchsorted(pos,q,side='right'),1].tolist())
  for U,V in ((0,0),(2000,200),(10000,2000)):
   tss=np.where(ss==1,aa,bb); left=np.maximum(1,tss-np.where(ss==1,U,V)); right=np.minimum(lengths[c],tss+np.where(ss==1,V,U))
   promoter=set(np.flatnonzero((left<=b)&(right>=a)))
   estimates[f'U{U}_D{V}'] += len(body|near|promoter)*len(frame)/len(chosen)
print('exact_body_pairs', exact_body)
print('context_sample_records', sample_n)
print('estimated_context_pairs', json.dumps({k:round(v) for k,v in estimates.items()},sort_keys=True))
PY
python3 /workspaces/Meta-Aging/_scratch/te-tracks-audit/p8-consult/measure.py
```
```text
BUILD_ID 0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a
CATALOG_ID 0c0a959dea69e397890b590b640162d5bd45e71a88f6468cadd4b7615022b4a4
GTF_md5 702e27a8727db66cd23e9f66f5aa1d38
GTF_sha256 0d1673f3c0fff7d28ff63f4443a0863fa25f817d391982e465f7ec20f256bcd0
published_identity_equal True
GTF_counts {"CDS": 522521, "Selenocysteine": 64, "UTR": 186133, "exon": 1298921, "gene": 78317, "start_codon": 59738, "stop_codon": 55494, "transcript": 278369}
contigs aliases/annotation 61 38
exon_union_bp 160549642
gene_union_equals_transcript_union False
all_rmsk {"fully_subtracted": 157214, "outside_annotation": 2638, "pieces": 5179754, "pieces_lt20": 129835, "records": 5320771, "removed_bp": 29569849, "retained_bp": 1172003155, "retained_records": 5163557, "split": 15495, "trimmed": 61378, "unchanged": 5086684}
interspersed {"fully_subtracted": 96119, "outside_annotation": 1612, "pieces": 3684934, "pieces_lt20": 55975, "records": 3764949, "removed_bp": 26235918, "retained_bp": 1090369890, "retained_records": 3668830, "split": 15406, "trimmed": 52703, "unchanged": 3600721}
compat_tetranscripts_mm39 {"fully_subtracted": 97987, "outside_annotation": 1754, "pieces": 3717740, "pieces_lt20": 56863, "records": 3799629, "removed_bp": 26503064, "retained_bp": 1094973237, "retained_records": 3701642, "split": 15399, "trimmed": 52842, "unchanged": 3633401}
residual_piece_overlaps 0
record_contigs/no_annotation 61 23
exact_body_pairs 14021883
context_sample_records 11378
estimated_context_pairs {"U0_D0": 21759726, "U10000_D2000": 26816523, "U2000_D200": 22501378}
```

```bash
export PYTHONDONTWRITEBYTECODE=1
cat > /workspaces/Meta-Aging/_scratch/te-tracks-audit/p8-consult/check.py <<'PY'
from pathlib import Path
from collections import defaultdict
import csv, gzip, subprocess
import numpy as np
import pyarrow.parquet as pq
B=Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build')
S=Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/p8-consult')
G=Path('/data2/users/shared/refcache/mm39/mm39_20260911/gencode.vM37.primary_assembly.annotation.gtf.gz')
alias={r['chrom_gencode']:r['chrom_ucsc'] for r in csv.DictReader((B/'tables/contig_aliases.tsv').open(),delimiter='\t')}
rows={k:defaultdict(list) for k in ('gene','transcript','exon')}
with gzip.open(G,'rt') as h:
 for line in h:
  if line.startswith('#'): continue
  f=line.split('\t')
  if f[2] in rows: rows[f[2]][alias[f[0]]].append((int(f[3]),int(f[4])))
def merge(v):
 out=[]
 for a,b in sorted(v):
  if out and a<=out[-1][1]+1: out[-1][1]=max(out[-1][1],b)
  else: out.append([a,b])
 return np.array(out,dtype=np.int64)
rows={k:{c:merge(v) for c,v in d.items()} for k,d in rows.items()}
for k in ('gene','transcript'): print(k+'_union_bp',sum(int((v[:,1]-v[:,0]+1).sum()) for v in rows[k].values()))
D=pq.read_table(B/'tables/rmsk_records.parquet',columns=['chrom','start_1','end_1','rmsk_class','rmsk_family']).to_pandas()
def distance(v,a,b):
 i=np.searchsorted(v[:,1],a); n=len(v)
 right=np.where(i<n,np.maximum(0,v[np.minimum(i,n-1),0]-b),10**18)
 left=np.where(i>0,a-v[np.maximum(i-1,0),1],10**18)
 return np.minimum(left,right)
stat=np.zeros(4,dtype=np.int64)
for c,d in D.groupby('chrom'):
 if c not in rows['gene']: continue
 a,b=d.start_1.to_numpy(),d.end_1.to_numpy()
 g,t=distance(rows['gene'][c],a,b),distance(rows['transcript'][c],a,b)
 stat += [np.sum((g==0)&(t>0)),np.sum(g!=t),np.sum((g<=10000)!=(t<=10000)),np.sum((g>=20000)!=(t>=20000))]
print('gene_vs_transcript body_only/distance_diff/10kb_diff/20kb_diff',stat.tolist())
with (S/'mask.bed').open('w') as h:
 for c,v in sorted(rows['exon'].items()):
  for a,b in v: h.write(f'{c}\t{a-1}\t{b}\n')
classes=['SINE','LTR','LINE','DNA','RC','Retroposon','Unknown','Unspecified','DNA?','Satellite']
compat=D[D.rmsk_class.isin(classes)&~D.rmsk_family.str.startswith('tRNA')]
with (S/'compat.bed').open('w') as h:
 for i,r in enumerate(compat.itertuples()): h.write(f'{r.chrom}\t{r.start_1-1}\t{r.end_1}\t{i}\n')
p=subprocess.Popen(['bedtools','subtract','-a',str(S/'compat.bed'),'-b',str(S/'mask.bed')],stdout=subprocess.PIPE,text=True)
n=retained=bp=0; previous=None
for line in p.stdout:
 c,a,b,key=line.split(); n+=1; bp+=int(b)-int(a); retained+=int(key!=previous); previous=key
assert p.wait()==0
print('bedtools_compat pieces/retained_records/retained_bp',n,retained,bp)
PY
python3 -u /workspaces/Meta-Aging/_scratch/te-tracks-audit/p8-consult/check.py
```
```text
gene_union_bp 1488096243
transcript_union_bp 1486451442
gene_vs_transcript body_only/distance_diff/10kb_diff/20kb_diff [2073, 2073, 500, 98]
bedtools_compat pieces/retained_records/retained_bp 3717740 3701642 1094973237
```

```bash
export PYTHONDONTWRITEBYTECODE=1
python3 - <<'PY'
from pathlib import Path
import shutil
scratch = Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/p8-consult')
shutil.rmtree(scratch)
print('scratch_exists', scratch.exists())
PY
```
```text
scratch_exists False
```

## Open for the owner

Decide whether phase 8 remains the SAF/dependency seam or expands to context, whether the compat SAF pair is a published view, and whether a shared convenience label belongs in te-tracks. For the context ADR, choose promoter `(U,D)`, label precedence/ambiguity handling, full-record versus retained-piece scope and the policy for reconciling the first bulk and 10x counting GTFs. Recommendation: use gene-body distances for the bulk 10/20-kb rules, retaining an explicit intermediate band; the exact thresholds remain consumer policy. Bring the actual counting-GTF digests/filter recipes and the first D2 label/query examples to that discussion. The unverified inputs in `C/gene_context_material.md:325-342` remain open except the compat count, now measured. Owner adoption precedes changes to DECISIONS.md or the implementation prompt (`P/02_orchestration.md:67-74`).
