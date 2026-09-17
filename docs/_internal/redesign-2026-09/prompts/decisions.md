# te-tracks decisions record (unit `te-tracks-decisions`)

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks` (branch `redesign-2026-09`, tree clean at the
commit that carries this prompt). You write the owner's rulings from the gene-context ADR discussion into
`docs/DECISIONS.md`. The rulings are final text decisions by the repository owner; your job is to express them in
the file's established form. You change no other file.

## Read first
1. `docs/DECISIONS.md` in full: the form is a numbered section per decision, two to four brief affirmative
   sentences stating the chosen behaviour and its reason, then "Recorded deferrals" as bullets that name the
   evidence the next decision needs.
2. `docs/_internal/redesign-2026-09/consults/adr_rulings_2026-09-17.md` in full (all rounds; the third round at the
   end carries the final rulings and the owner's boundaries).
3. `docs/_internal/redesign-2026-09/consults/open_questions_premises_2026-09-17.md` (the premises and the
   biology the entries rest on; section 1 "Records, insertions and instances" is the basis of item 4 below).
4. `docs/_internal/redesign-2026-09/consults/gene_context_adr_brief.md` (candidate texts C1 to C11).
5. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments"; `AGENTS.md` of this repository.

## Environment and rules
- `export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot PYTHONDONTWRITEBYTECODE=1`.
  Scratch, if you need any, under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/decisions/`, removed with
  Python `shutil` when you finish (`/tmp` is noexec).
- No git writes anywhere (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too),
  no installs, no network, no edits outside `docs/DECISIONS.md`.
- Prose is affirmative and brief: state what a thing is. A "not" clause stays only where the contrast is
  logically load-bearing; list every remaining one in your report with its reason. No numbers in the entries
  beyond what a reader needs to act; measured figures live in OUTPUTS.md and the internal records.
- Every entry cites nothing and names no reviewer, session or date; history lives in the internal records.
- Where an existing section already covers part of a ruling, amend that section in place; add new sections
  after 7 and before "Wording", renumbering "Wording" last. Keep section 8 "Wording" as the final numbered
  section.

## Entries to write (content, one section each unless stated)

1. **Amend section 4 "Gene-dependent views" into "Gene annotation snapshots".** The family `te_<assembly>_gene`
   publishes immutable snapshots; each pins one parent core build by full `BUILD_ID`, one gene annotation by
   digest and one versioned policy bundle (mask policy, minimum retained block, context capability, later the
   context envelope); `CATALOG_ID` stays the parent's. A consumer counts against the snapshot whose annotation
   digest equals its counting annotation's; the first snapshot pins GENCODE vM37 and a second pins the 10x
   2024-A gene annotation (GENCODE vM33 filtered) the current single-cell datasets were counted with; a digest
   mismatch triggers documented geometry reconciliation or another snapshot. The child carries an exact copy of
   the parent's contig alias and length table verified by digest, normalizes annotation contigs through it, and
   fails on an unmapped contig. The compat universe's exon-subtracted pair stays a published view of the family
   for legacy reproduction. Peaks, motif databases and TF inference are the ATAC framework's own pinned inputs;
   any motif content on TE consensus would be another child family.
2. **New section "Exon mask policy".** The default mask is the unstranded union of every exon row of the pinned
   annotation with every positive-length block retained (`all_exons_unstranded_union_v1`,
   `min_retained_block_bp = 1`), because an all-exon gene pass counts every exon row and the guarantee is
   exon-disjoint sequence support. A same-strand mask (`all_exons_stranded_union_v1`) joins beside it in a later
   snapshot once a chemistry pilot has established which mate is RNA-sense; protein-coding and basic masks are
   measured alternatives that enter with a named consumer. EM routes take the unmasked record exports with the
   full gene annotation; molecule exclusivity is a property of the joint counting run.
3. **New section "Transcript context is geometry".** te-tracks publishes geometry and consumers derive labels:
   the context product is a sparse record-by-transcript relation with per-pair status and a per-record roll-up,
   carrying exon, intron and UTR overlap, relative strand, and signed closest-base distance to each transcript's
   start and end, with gene-body distance beside transcript distance. Rows exist for body overlaps, for the
   nearest start, end and exon edge on the record's contig, and for records inside a window 10 kb upstream to
   2 kb downstream of an annotated transcript start; narrower promoter policies are filters on the stored
   distance and are the consumer's. Each transcript carries its `Ensembl_canonical` and `mRNA_start_NF` flags so
   incomplete starts can be excluded. The first child snapshot declares context `not_computed`; the relation
   arrives in a later snapshot after a scaling gate; consuming ledgers key on `te_catalog_id` and `te_build_id`.
4. **New section "Records, instances and insertions".** A record is one RepeatMasker alignment of a genome
   stretch to a consensus model and is the unit of every export and every per-locus count. An instance id is
   RepeatMasker's grouping hypothesis for records descended from one element; it is carried on every record and
   registered as its own feature level, and it errs in both directions, so it is a starting group rather than a
   biological insertion. Insertion-level units (full-length copies, proviruses, solo LTRs) are reconstructions
   with declared parameters and evidence, published later as candidate views. The documentation states these
   limits of the annotation: records are alignments to a pinned library, fragmentation and nesting split
   elements, consensus coordinates are model-relative, records overlap one another, and genic context depends
   on the annotation pin.
5. **New section "Structural candidate views".** Later core snapshots publish geometry that is a pure function
   of catalog columns under declared parameters: the block union of an instance's records with gaps preserved,
   record 5′ windows with model-prefix eligibility, LTR–internal candidate pairs by family, strand and gap with a
   status per pair, and divergence bins with pinned thresholds. Every view carries neutral names, support and
   candidate status, and enters after the host build, batched, when a consumer names the need. Biological
   verdicts (promoter-intact, solo LTR, young) belong to the consuming analysis.
6. **New section "Consumer boundary and qualification".** te-tracks ships registered intervals and identities and
   verifies consumer tools against fixtures at two levels: parser checks run a tool's own reading code on the
   exports, execution checks run the pinned binary on a fixture and assert identity joins, roster and molecule
   conservation, and unique molecules landing on their feature, recording each tool's allocation of ambiguous
   molecules without asserting it. Alignment parameters, estimator choice, forks and allocation behaviour belong
   to the consuming toolkit; te-tracks documents the qualification limits it has observed. Execution checks run
   against a pinned, reproducible tool environment recorded with the repository and report `unsupported` where a
   binary is absent.
7. **New section "STARsolo record profile".** The export `record_starsolo.gtf` makes one record one gene and one
   single-exon transcript (`gene_id`, `transcript_id` and `locus` equal to the record alias, `gene_name` the
   RepeatMasker name, `gene_type` `transposable_element`, provenance attributes kept) so that gene-level counters
   count loci; the existing `record.gtf` keeps the subfamily grammar TEsingle and TElocal consume. Registration
   reuses the record alias membership; the profile enters with its contract and fixture; an instance-level
   profile waits behind mixed-name, mixed-strand, gap and junction tests.
8. **New section "Matrix binding".** A run's matrix binds to a registration through the full key
   `(universe_name, variant, feature_level, key_grammar)`, because the registration holds each record under more
   than one universe and a join on the level and grammar alone doubles counts; a join fixture over both universes
   proves the rule.
9. **New section "Rank vocabulary and Dfam".** Raw and canonical RepeatMasker labels stay as they are. A later core
   view stores, for the `interspersed` names first, the Dfam lineage, accession, model version, model length,
   clade and release as truth, and derives a named rank scheme with a status per rank (`mapped`, `inherited`,
   `missing`, `inapplicable`, `part_model_set`); L1 whole-element names map to the set of their Dfam part models.
   The rank vocabulary is named at admission, with Wicker's ranks recommended and the dissertation's five names
   kept as a documented alias table. The documentation states the label surprises a consumer must know.
10. **Recorded deferrals: update.** Young versus old tiers now name Dfam clade assignment beside divergence as
    the evidence; ERV units name the LTR–internal candidate view as the precursor; the transcript-context bullet
    is replaced by a reference to the new context section and its scaling gate; add bullets for the stranded
    mask companion (after the chemistry pilot), the TES-side window (if the 3′ pilot needs it), the
    instance-level STARsolo profile (behind its tests), and the promotion of the consumer environment into the
    package (phase 9).

## Acceptance
- `docs/DECISIONS.md` is the only changed file (`git status --short` shows exactly that line).
- Every numbered section keeps the form: two to four sentences, affirmative, behaviour plus reason. Section
  numbering is contiguous and "Wording" is the last numbered section; its own text updates its sentence count
  claim if you change it.
- `grep -nE "\b(not|never|neither|nor|rather than|instead of|cannot)\b|n't" docs/DECISIONS.md` lists only
  load-bearing contrasts; report each remaining line with its reason.
- `tests/run.sh core --refroot "$TE_TRACKS_REFROOT"` exits 0 (about 13 minutes; the build is in place).
- Scratch removed; no git write anywhere.

## Report
End with: the sections added or amended (numbers and titles), the negation lines kept with reasons, the runner
result, and any place where the rulings left you a choice and what you chose.
