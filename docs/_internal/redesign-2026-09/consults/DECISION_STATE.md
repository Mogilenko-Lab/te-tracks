# te-tracks decision state under review (2026-09-15)

Read alongside: `../../report/AUDIT.md` (measured facts), `../SYNTHESIS.md` (current synthesis),
`../fanout/{A_consumer_contracts,B_taxonomy_universes,C_identity_publication}.md` (earlier consults),
`../fanout/owner_context_2026-09-15.md` (owner intent), and the repository `01_modules/te-tracks/`.
Local read-only consumer checkouts: `01_modules/.ref/{irescue,stellarscope,TEsingle,MATES}`.

Owner's stated goal: park a durable, tested state of te-tracks that serves snRNA (3' ARC), scRNA
(5' PE OCM), snATAC (ARC) and external bulk RNA-seq, for mouse now and human next, with other
species possible. The repository carries no knowledge of what the annotation is used for. Namespace
clarity and simplicity are first-class. Public wording is brief and affirmative.

## Measured facts that constrain every ADR
- mm39 RepeatMasker run: 5,320,771 records; identical record set in UCSC `rmsk.txt.gz` and
  `bigZips/mm39.fa.out.gz`; the `.out` carries the true instance ID (4,696,900 ids), the table
  truncates it to one character.
- Self-describing key `repName|chrom:start-end|strand` unique over all records; coordinate-only key
  collides 3 times.
- 20 repNames carry two (family,class) triples (6,517 records, all DNA-class): `X` vs `X?` and
  family splits (MER63A-D hAT-Tip100 vs hAT-Blackjack). Packaged TEtranscripts GTF strips `?`.
- Universe sizes: all_rmsk 5,320,771; interspersed 3,764,949; +satellite 3,802,177;
  retrotransposons 3,593,857; satellites 37,228; legacy_tetranscripts_mm39 3,799,629.
- Tool universes: IRescue auto skips six classes, keeps Satellite+snRNA (3,805,826); MATES TE mode
  keeps DNA LTR RC Retroposon SINE LINE, downloads mm10; TEtranscripts/TEsingle GTF = legacy set;
  Telescope/Stellarscope retro.hg38.v1 = curated HERV + full-length L1, human only.
- Consumer name grammar: IRescue reserves `,` and `#` (display column), whitespace; TEsingle needs
  four GTF attributes and builds `transcript:gene:family:class`; Stellarscope groups GTF rows by
  `--attribute` (default `locus`); MATES needs CSV+BED pair with integer index; lab featureCounts
  cleaner interprets `%`. All mm39 names fit `[A-Za-z0-9_.+/?()-]`.
- RepeatMasker run identity for mm39, from UCSC bigZips/README.txt: RepeatMasker open-4.0.8
  (Feb 2017) run with -s, library RepBase RELEASE 20181026 + Dfam_Consensus RELEASE 20181026. The
  `.out` file itself carries no version metadata (header and tail checked). This is a declared, not
  computed, fact and belongs in the manifest as such.
- Publication defects confirmed by test: same-day rebuild overwrites live `current`; release.sh trusts
  the BUILD_ID file.

## Current recommendations (what you are asked to stress-test)

ADR-1 Counting unit at subfamily level = repName (the consensus). Raw triple kept per record;
  `taxonomy_canonical` gives one row per name with status resolved | uncertain_source | unresolved;
  rollups read only that table. te-tracks publishes record, instance and subfamily levels; each
  analysis run chooses one and records it.
ADR-2 Six universes: all_rmsk, interspersed (default: SINE LTR LINE DNA RC Retroposon Unknown
  Unspecified DNA?), interspersed_plus_satellite, retrotransposons, satellites,
  legacy_tetranscripts_<genome>. Satellites are a universe, not a class inside the default.
ADR-3 First deliverable = canonical tables + instance membership + taxonomy tables + six
  `interspersed` exports (subfamily.bed, record.bed, record.gtf with record/taxonomy/instance
  attributes, subfamily.noExon.saf, MATES csv+bed, conditional instance.bed), each with a
  known-answer parser fixture.
ADR-4 Transcript context = a later stage producing a record x transcript relation (exon/intron,
  relative strand, overlap bp) keyed by (BUILD_ID, gene-annotation md5); species handled by one
  `config/<genome>.env` per assembly; universe names global, membership per genome.
ADR-5 Namespace: entities record | instance | subfamily | family | class | universe | build;
  qualifier `rmsk_` = as asserted by RepeatMasker; tables rmsk_records, rm_instance_members,
  taxonomy_rmsk, taxonomy_canonical, universes.json, MANIFEST.json; exports
  `<universe>/<level>.<format>`; ledger tables rmsk_records, peak_record_overlaps,
  te_feature_registration.
ADR-6 Primary source `bigZips/<genome>.fa.out.gz` (md5 pinned), `rmsk.txt.gz` pinned as cross-check.
ADR-7 One BUILD_ID over delivered bytes; staging -> verify -> rename into archive/<BUILD_ID>/ ->
  atomic `current` symlink swap; builder sha in manifest but outside the hash; INDEX.tsv,
  CURRENT_BUILD.tsv, dated snapshots and archive-on-supersede deleted. Gene GTF md5 in manifest;
  a GENCODE bump = new build.
ADR-8 ADR wording: brief, affirmative, no contrastive negation.
Deferred: young/old age tiers (perc_div per record exists; per-subfamily median divergence cheap;
  curated evolutionary ages and full-length/ORF status are a later structural stage).
