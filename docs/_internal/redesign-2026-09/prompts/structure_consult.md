# te-tracks structure consult: host-promoter windows, instance views, record-end windows, LTR–internal pairs and divergence bins (codex, read-only)

You are consulted on design; you measure and recommend, you implement nothing. Working directory
`/workspaces/Meta-Aging/01_modules/te-tracks`, branch `redesign-2026-09`, commit `9c27b14`. You write exactly one
file: `docs/_internal/redesign-2026-09/consults/structural_views_consult.md`. You change nothing else. No git writes
anywhere (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too; `14839-DM-cGAS` and
`sene/` are the owner's directories, read the first, leave both alone), no installs, no network. Export
`PYTHONDONTWRITEBYTECODE=1`. Scratch only under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/structure-consult/`,
removed when you finish (Python `shutil`; `/tmp` is noexec). pandas, pyarrow, numpy and bedtools 2.31.1 are available.

Read-only inputs: the core build `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` (tables
`rmsk_records.parquet` with 24 columns including `rmsk_instance_id`, `consensus_start_1`, `consensus_end_1`,
`consensus_left_bp`, `divergence_pct`, `length_bp`, `strand`; `rmsk_instance_members.tsv.gz`, `rmsk_taxonomy.tsv`,
`contig_aliases.tsv`); GENCODE vM37 at
`/data2/users/shared/refcache/mm39/mm39_20260911/gencode.vM37.primary_assembly.annotation.gtf.gz`; the Dfam census
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/field/dfam_census_1220.tsv` if complete (columns include
`classification`; read it, do not write it).

## Read first, in order
1. `docs/_internal/redesign-2026-09/consults/adr_rulings_2026-09-17.md` (the owner's rulings; C4 and C11 are your
   subject; motif mapping is ruled downstream).
2. `consults/gene_context_adr_brief.md` (C4, C11), `consults/field_practice_consult.md` Q5, Q6 and M2, M3,
   `consults/field_practice_synthesis.md` sections 2, 5 and 9, `../reviews/field_divergent.md` H3, H4, H5, L2,
   `consults/gene_child_consult.md` Q5 and Q6 (the relation's geometry and the promoter window estimates 21.8 M /
   22.5 M / 26.8 M pairs for (0,0) / (2000,200) / (10000,2000)).
3. `docs/OUTPUTS.md` (records schema, instances, universes and predicate grammar), `docs/DECISIONS.md` (the deferrals
   of ERV units and age tiers).

## The owner's words (verbatim, 2026-09-17)
On C4: "I don't fully get the idea with the windows, but have a layman concern that promoter position might be
annotation-biology sensitive, or would a unified DB suffice, but then what DB, where do motifs map in this
endeavour or is this downstream concern?"
On C11: "I don't fully understand, and would need a little bit more explanation, and explanation in simpler terms."

Write your Summary in plain language for the owner first: what a RepeatMasker record is against an insertion, why
the two ends of a provirus and its middle are separate records, what a solo LTR is, why a full-length L1 keeps its
promoter at its 5′ end and most copies have lost it, and what each proposed view lets a consumer ask. Then the
technical sections.

## Questions
1. **Host-promoter windows.** Define the transcript start and end used by the context relation (GTF transcript
   rows; `Ensembl_canonical` tag; `MANE_Select` absent in mouse). Explain how a stored window `(U, D)` around each
   start selects which record × transcript pairs exist for records outside gene bodies, and how any narrower window
   is derived afterwards from the signed distance. Measure exactly on chr1, then extrapolate, the pair counts for
   (0,0), (1000,100), (2000,200), (10000,2000), (20000,2000). Name the alternative TSS sources (FANTOM5 CAGE, EPDnew,
   ENCODE cCRE promoter-like signatures) as later pinned inputs of another snapshot, with what each would add and
   its licence and mouse coverage as far as you know (say so). State the interface to motif scanning: te-tracks gives
   intervals and identities; sequence and motif databases (cisTarget in the refcache, JASPAR, CisBP) belong to the
   ATAC framework.
2. **Instance block-union view.** Define one feature per `rmsk_instance_id`: union of member blocks per contig and
   strand, gaps preserved, `mixed_name`, `mixed_strand` and `member_count` status. Measure for the interspersed
   selection: features, multi-block features, total gap bases, the largest gap, and how many instances span more
   than 50 kb (a sign of unrelated fragments sharing an id). Propose its export forms (BED12, GTF multi-exon
   transcript) and registration grammar `(instance, instance_alias)`; state what it prevents and what it cannot
   claim.
3. **Record-end windows.** Define `record_5prime_N`: for record `[a,b]`, `[a, min(b, a+N-1)]` on `+` and
   `[max(a, b-N+1), b]` on `-`; eligibility `consensus_start_1 - 1 <= tolerance`. Measure counts of eligible records
   and windows for N in {100, 300, 500, 1000} and tolerance in {0, 10, 100} for `LINE/L1`, for the young L1 names
   (`L1MdA_*`, `L1MdGf_*`, `L1MdTf_*`), for class `LTR` and for `LTR` records whose name contains `LTR`. Explain what
   a 5′ library consumer asks with it (does the molecule's RNA-oriented 5′ end fall inside) and why interval overlap
   answers a different question; name the failure it prevents (a truncation boundary called a promoter) and the
   one it cannot prevent.
4. **LTR–internal candidate pairs.** Beyond same-instance pairing (25,055 LTR-named records in 17,947 instances share
   an instance with an `-int` record; 103,526 instances are internal-only; 722,280 are LTR-only), measure an
   adjacency rule: an LTR-named record and an internal record of the same `rmsk_family`, same strand, within X bp
   (X in {100, 1000, 5000}), in LTR–internal or internal–LTR order; count LTR records gaining a partner, internal-only
   instances gaining a flanking LTR, and full `LTR–internal–LTR` triplets. State the false-pair risk from nested
   insertions and how a status vocabulary (`same_instance`, `adjacent_same_family`, `unpaired`, `ambiguous`) records
   it. Name "One code to find them all" (Bailly-Bechet 2014) as the field algorithm and what it adds.
5. **Divergence bins.** From `divergence_pct` (468,810 records at exactly 0; B1_Mus1 median 8.9 with 5–95% 4.1–21.8;
   B3 median 23.1): propose bin edges and names (`divergence_le_5pct`, ...), measure record and instance counts per
   bin for L1, ERVK, ERVL-MaLR, B1 and B2, and state what a bin is (a sequence-distance stratum under this
   RepeatMasker run) and is not (an age or an activity claim). Say how a universe predicate schema would need to
   grow to express a bin.
6. **Ordering and cost.** For each view: size (rows, bytes estimated from the record exports), whether it changes
   `BUILD_ID` only or also the catalog, and the consequence for the one host build at phase 9 (10.5 GB per build in
   the retention window). Recommend before or after the host build, given the owner's pilot order (14761 RNA first,
   ATAC direct counts, no ATAC EM at first).

## Output format
```
# Structural views consult (codex gpt-6-astra)
## Summary in plain language
## Q1 .. Q6
## Measurements performed (methods, exact numbers)
## Open for the owner
```
Under 250 lines. Facts over opinions; cite paths and lines; where you rely on knowledge beyond the inputs, say so
in the sentence. Recommend; do not implement.
