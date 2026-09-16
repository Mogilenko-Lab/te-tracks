# te-tracks design synthesis — premises, implications, caveats (2026-09-15)

Inputs: the measured audit (`report/AUDIT.md`), the packaged-GTF reconciliation
(`report/reconcile_stdout.txt`, `report/alias_*.tsv`, `report/conflict_class.tsv`), three
independent codex units (`fanout/A_consumer_contracts.md`, `B_taxonomy_universes.md`,
`C_identity_publication.md`, all gpt-6-astra), and my own reading of the four consumer checkouts.
Where the units disagree I say so and recommend.

## 0. One word that was causing confusion: "fragment"

RepeatMasker calls each row of its output a *fragment*: one aligned match between genome and a
repeat consensus. It is an annotation object. In this project "fragment" is also the Tn5 fragment in
`atac_fragments.tsv.gz`, an experimental object. The two must never share a name. Every place below
that used to say "fragment" for the annotation row now says **record**.

- **Recommended names** (unit B, and I agree): the annotation row is an `rmsk_record` with key
  `record_id`; the RepeatMasker-ID-linked group is an `rm_instance` with key `rm_instance_id`.
  The ledger table the owner called `repeat_fragments` becomes `rmsk_records`. The ATAC object keeps
  `fragment` unqualified.
- Why not `locus`: "locus" promises a biological unit. A record may be a third of one element.
- Why not `insertion`: RepeatMasker's ID grouping is an educated guess that two records derive from
  one element. Calling it an insertion asserts what has not been validated. `insertion_candidate` is
  reserved for a later structural stage that checks it.

## 1. The three identities, in plain terms

te-tracks answers three different "which one?" questions. Each needs its own key, because each has a
different cardinality and a different failure when confused.

### 1a. Which annotation row? → `record_id`

Premise. There are 5,320,771 rows in the mm39 RepeatMasker run. A key must name one row and never
two. Coordinates alone fail: 3 pairs of rows share chrom, start, end and strand with different
names (a B1 SINE and an ORR1B1-int LTR piece annotated over the same bases). The self-describing
string `<repName>|<chrom>:<start>-<end>|<strand>` is unique over all 5.32M rows (measured).

Implication. Keep that string as the key, keep the component columns beside it, and never split
the string to recover coordinates. Rename the column from `locus_id` to `record_id` while nothing
consumes it. Every downstream table that says "this peak overlaps this TE" points at a `record_id`.

Caveat. The key embeds the consensus name, so a future library rename changes identity; that is a
cross-release mapping problem, recorded in the release, never hidden.

### 1b. Which RepeatMasker-linked group? → `rm_instance_id`

Premise. RepeatMasker links records it believes derive from one element that was later split by a
nested insertion or deletion. The link is the ID column of the `.out` file. UCSC's database table
truncates that column to one character, so today's `rmsk_id` column is noise (9 values). From the
`.out`: 4,696,900 groups; 445,649 have two or more records; in the TE classes 437,463 groups hold
1,052,720 records (28%). 30,569 groups mix consensus names; on chr1 the commonest mixtures are
LTR-plus-internal pairs (IAPEz-int with IAPLTR1a_Mm, MERVL-int with MT2_Mm, RLTR10 with RLTR10-int)
and SINE subfamily boundaries (B4 with B4A).

Implication. A record-to-group membership relation costs one small table and gives every RNA or
ATAC analysis the option to treat an ERV provirus as one unit. Stellarscope's `--attribute locus`
groups GTF rows by exactly this kind of shared id, so the group export is a direct consumer need.

Caveat. The group is RepeatMasker's guess, scoped to this annotation release. Its bounding span
includes gaps and nested elements, so any count over a group must use the union of member intervals,
never the span. A count for a group must not be copied onto its members, and a member's count must
not be summed into a group without saying so.

### 1c. Which repeat identity are we counting? → `subfamily` (repName) plus its classification

Premise. `repName` names the consensus sequence a record matched. Biologists call it the subfamily
and it is the unit every RNA quantifier sums over. `repFamily` and `repClass` are curator labels on
that consensus from the Dfam/RepBase library. They should be constant per name and are not: 20 of
1,225 names carry two labels (6,517 records, all DNA-class). Two patterns:

| pattern | example | what it means |
|---|---|---|
| uncertainty suffix | MER99: `hAT` 148 records, `hAT?` 35 | `?` = the curator was unsure of the label for those hits |
| family split | MER63A: `hAT-Tip100` 714, `hAT-Blackjack` 1 | a library reassignment left both labels in the run |

The packaged TEtranscripts GTF already strips the `?` (measured: 60 records), so that normalization
has precedent. None of the 20 names is a retrotransposon.

Implication. Count by `repName`. Keep the raw triple on every record as provenance. Publish a
curated one-row-per-name table (`taxonomy_canonical`) with a `status` column: `resolved`,
`uncertain_source` (label agrees after removing `?`), `unresolved` (competing families, e.g. MER63A-D).
Family and class rollups join through this table, so a count is never duplicated and an unresolved
name lands in an explicit `taxonomy_unresolved` bucket, distinct from RepeatMasker's own `Unknown`.
Unit B rules the same way; my earlier proposal to put the full triple in the count feature name is
withdrawn, because it would split one consensus into two EM features for no biological reason.

Caveat. Majority vote is not curation. MER63A-D stay `unresolved` until a library accession settles
them. The raw dimension `te_dim` keeps one row per triple with no uniqueness claim on name alone
(unit C), and the curated table is the only thing a rollup reads.

## 2. Universes: what each name means and why it exists

RepeatMasker vocabulary. An **interspersed repeat** has copies scattered through the genome, the
signature of past transposition. A **satellite** is organized as tandem arrays, mostly centromeric
and pericentromeric. Simple repeats and low-complexity runs are sequence composition, not ancestry.
The structural-RNA classes (tRNA, rRNA, snRNA, scRNA, srpRNA) are RNA genes and pseudogenes.

| name | records | definition | choose it when | never call it |
|---|---|---|---|---|
| `all_rmsk` | 5,320,771 | every row | you need the complete catalog or masking | "all TEs" |
| `interspersed` | 3,764,949 | classes SINE LTR LINE DNA RC Retroposon Unknown Unspecified DNA?; no satellite; no family exclusion | regulatory questions (default) | "confirmed TEs", "active TEs" |
| `interspersed_plus_satellite` | 3,802,177 | interspersed + Satellite | one interval set for a combined repeat analysis; always stratify | "TE burden" |
| `retrotransposons` | 3,593,857 | LINE SINE LTR Retroposon | RNA-mediated elements only | "active retrotransposons" |
| `satellites` | 37,228 | Satellite only | the heterochromatin/centromere aging axis | "TE expression" |
| `legacy_tetranscripts_mm39` | 3,799,629 | interspersed_plus_satellite minus repFamily `tRNA*` | comparing with 13036-DM / 14839-DM results | the default |

Answers to the questions asked.
- "Interspersed" is RepeatMasker's own word for TEs and their derivatives; satellites are excluded
  because they are tandem arrays, not scattered copies.
- `interspersed_plus_satellite` exists only because today's te-tracks and the packaged file carry
  Satellite inside "TE". It is the comparability bridge, not a biological universe.
- Satellites get their own axis because pericentromeric derepression in aged and senescent cells is a
  real, distinct question, and folding 37k satellite records into "retrotransposon reactivation"
  would mislabel it.
- Unknown/Unspecified/DNA? stay in `interspersed` as provisional candidates; a sensitivity view
  without them is one filter away.
- Structural-RNA classes never enter a TE universe. SINEs stay in by class regardless of their
  ancestral RNA: B2, B4 and ID are tRNA-derived, B1 and human Alu are 7SL-derived.
- IRescue's automatic mm39 annotation is none of these: it drops six classes and keeps snRNA and
  Satellite (3,805,826 records). Custom features are the only way to state the universe.

The tRNA-prefix legacy. `EXCLUDE_FAMILY_PREFIX="tRNA"` drops three ancient conserved SINE families:
LFSINE_Vert 1,235, MamSINE1 925, AmnSINE2 388. They are named for their tRNA ancestry, not for being
tRNA genes. The most likely story is that the packager meant to remove structural RNA and caught the
family names too; the original script is not available, so that is inference. These conserved SINEs
are exactly the kind of sequence that becomes an enhancer, so they belong in `interspersed`. Their
exclusion survives only in the legacy universe.

Does `legacy_tetranscripts_mm39` fully reproduce TEtranscripts? Intervals yes: 3,799,629 records
join 1:1 on coordinates after mapping contig names. Labels no, and the full alias tables now exist
(`report/alias_subfamily.tsv`, `alias_family.tsv`): the packaged file writes `.` for `v` in ID4_v,
LTR33A_v, MER34C_v and RTE-BovB; writes the subfamily name as family wherever rmsk says `Unknown`
(2,851 MurSatRep1 records, 961 YREP_Mm, ...); and strips `?`. The "4 class conflicts of unknown cause"
in PROVENANCE.md are a join artifact of the 3 coordinate-duplicate pairs; there is no real class
disagreement. That closes the open item.

## 3. Which source to pin

Two files from the same RepeatMasker run are served by UCSC. `database/rmsk.txt.gz` is the browser's
table: same 5,320,771 records, but the linkage ID is truncated. `bigZips/mm39.fa.out.gz` is the raw
RepeatMasker output with the real ID column; it is also what IRescue downloads. Pin the `.out.gz` as
the primary record source (md5 to be taken at the authorized host build), keep `rmsk.txt.gz` pinned
as the cross-check, and assert the two agree on every record. Parsing the `.out`: coordinates are
already 1-based, `C` means minus strand, and the consensus columns swap position on the minus strand
with the remaining length in parentheses. Carry raw repStart/repEnd/repLeft and normalized consensus
start/end/remaining.

## 4. Identity of a build, provenance, publication: the simple version

Unit C's design, which I endorse with one flagged trade-off.

- **One id.** `BUILD_ID` is the sha256 over the sorted list of `<md5> <path>` for every delivered
  file plus the manifest. Consumers pin the full id and the md5s of the files they read. No second
  "annotation identity"; adding an export is a new build, and equality of the canonical table across
  builds is a checksum comparison.
- **Manifest, nothing more:** schema_version, assembly, builder_sha, sources with observed md5s
  (`.out.gz`, `rmsk.txt.gz`, chromAlias, FASTA, chrom.sizes, GTF only when a view uses it), the
  universe predicates spelled out, observed counts per universe, outputs with md5s.
- **Layout:** `te_mm39/.staging/<tmp>/` for building, `te_mm39/archive/<BUILD_ID>/` for every
  published build forever, `current -> archive/<BUILD_ID>` as the only mutable thing. Nothing ever
  moves after publication. `INDEX.tsv`, `CURRENT_BUILD.tsv`, date-named snapshots, "reconfirmed" rows
  and the archive-on-supersede step are deleted.
- **Procedure:** build in staging; verify there; recompute every md5 and the id from bytes; verify
  the existing `current` from bytes and abort on any corruption; rename staging to
  `archive/<id>` (fails harmlessly if an identical build already landed); swap `current` by writing a
  temporary symlink and renaming it over. That passes all six tests without a lock.
- **Stop:** building into a dated path, trusting the `BUILD_ID` file, keeping a stale manifest,
  deriving the family from `dirname`, writing the verifier's scratch file into the snapshot.
- **Trade-off for the owner.** Unit C hashes the manifest, and the manifest carries `builder_sha`, so a
  docs-only commit in te-tracks makes an identical rebuild a new `BUILD_ID`. The alternative is to
  exclude `builder_sha` from the hashed content and record it beside the id. Both are simple; the
  first is stricter about "who produced these bytes", the second keeps dedup by content.
- **Expectations** move to `tests/expectations/<source-md5s>/<universe>/` beside a small `shape.env`,
  so a universe change adds a directory instead of editing genome-keyed files.
- **Delete** `LOCUS_ID_FORM`, the ordinal branch and universal `dup_index` (an ordinal belongs to the
  export that needs it), `INTERGENIC_MIN` and `EXPECT_LOCI_NOEXON` until their readers exist, and the
  `rmsk_id` column in favour of the membership table.

## 5. Gene context

The owner's message left this block empty. Both codex units and the ledger design say the same
thing: transcript context is a many-to-many relation (record x transcript) with exon/intron
relation, relative strand and overlap bp, pinned to a gene annotation release. A scalar
`gene_context` per record cannot represent a record that is exonic in one isoform and intronic in
another. Absence before that stage means "not computed", not "intergenic". It is a later stage of
te-tracks, after the canonical table and universes are published. Owner to fill in the intent.

## 6. Consumer contracts (unit A) — see section appended below when the unit lands.

Facts already verified by me from the local checkouts:
- IRescue 1.2.0: custom BED, column 4 = feature name, opaque except `,` and `#`; strand only under
  `--strandedness`; `--locus-level {disabled,fragment,instance}`; README example stale.
- Stellarscope 1.5: GTF; feature = rows sharing `--attribute` (default `locus`); feature_type `exon`;
  stranded modes RF/R/FR; pooling pseudobulk/individual.
- TEsingle 1.0: TE GTF must carry `gene_id`, `transcript_id`, `family_id`, `class_id` or it raises;
  feature identity `transcript:gene:family:class`; `--cutoff` default 1000 UMIs per barcode silently
  drops low-RNA barcodes; `--stranded` default forward.
- MATES 0.1.8: rmsk-style table with `genoName` columns, or BED whose name is `repName#repClass`.
- featureCounts SAF: `GeneID Chr Start End Strand`, 1-based; the lab's legacy GeneID grammar is
  `Subfamily:Family:Class`.

## 7. What this means for te-tracks' scope and richness

The repository stays modality-blind. It publishes: one canonical record table over all rows; one
record-to-instance membership table; one raw taxonomy dimension and one curated canonical map; named
universes with spelled-out predicates; and, per universe actually consumed, the export files the
real parsers were tested against. Everything a downstream stage might ask for later (transcript
context, consensus-coverage structure, promoter calls, mappability) is either carried raw now
(consensus coordinates, scores, divergence) or is a declared later stage with its own relation.

## 6 (appended). Consumer contracts — unit A, verified where I could

Unit A read every parser and lands on **six export files for one universe**, plus a seventh only if
an instance-level IRescue run is wanted. There is no format grid.

| file | name field | consumer |
|---|---|---|
| `subfamily.bed` (BED6) | bare repName | IRescue subfamily run |
| `record.bed` (BED6) | record id | IRescue record run; bedtools |
| `record.gtf` (exon rows) | `transcript_id`=record id, `gene_id`=repName, `family_id`, `class_id`, `locus`=record id, `instance_id`=rm_instance | TEsingle; Stellarscope at record or instance level via `--attribute` |
| `triple_noExon.saf` | `repName:family:class` | the lab's established featureCounts run |
| `record.csv` + `record.bed` (8-column pair) | group in col 4, unique integer index in col 5 | MATES direct reference |
| `instance.bed` (BED6, conditional) | rm_instance id repeated across member blocks | IRescue instance run |

Facts from the parsers that shape te-tracks:
- **IRescue**: commas split names, whitespace truncates, `#` is stripped from the display column only.
  Auto mode downloads `.out.gz` and skips six classes; MATES auto mode for mouse downloads **mm10**,
  so both tools need the custom export for mm39.
- **Stellarscope**: rows sharing the chosen attribute are one feature and neighbours within 1 bp are
  merged; there is a suspected one-base right-boundary overlap in its interval arithmetic that the
  fixture must reproduce before biological use.
- **TEsingle**: requires all four TEtranscripts attributes; the feature is the four-part tuple, so a
  mixed-name rm_instance cannot be one TEsingle feature; `--cutoff 1000` counts distinct raw UR
  strings per barcode before any overlap, so it drops low-RNA nuclei silently unless set explicitly.
- **MATES**: 0-based CSV+BED pair, unique integer index, unstranded counting, model grouping by
  column 7; its stock builder clips records to 1,000 bp and drops `?` and `Unknown` groups.
- **featureCounts (lab driver)**: `%` in a name is interpreted by the cleaner's `printf`.
- **Safe name alphabet** `[A-Za-z0-9_.+/?()-]` with `|` and `:` as the only joiners. Measured on all
  distinct mm39 repName/repFamily/repClass/contig values: none falls outside it (see run log).
- **Exported record alias** for tools whose composite output uses `:` (TEsingle): a colon-free form
  `R|mm39|repName|contig|start|end|strand`, registered back to the canonical `record_id`.
- **te_feature_registration** must hold the export identity, the exact emitted feature id and its
  resolution (`record`, `rm_instance`, `subfamily`, `taxonomy_triple`), one membership edge per
  canonical record with the retained interval blocks, and the run identity. The conservation test:
  a feature with count 7 over three records still totals 7 after a record-level query.
- Every export is authorized only by its known-answer fixture (unit A §4 lists one per tool).
