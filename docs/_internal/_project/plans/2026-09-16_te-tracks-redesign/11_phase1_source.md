# Phase 1: source layer

Goal: one pinned RepeatMasker `.out` parsed under a declared profile, with the UCSC table used once
to qualify it.

Deliverables
- `config/mm39.env` revised: `RMSK_OUT_URL` = `bigZips/mm39.fa.out.gz`, `RMSK_OUT_MD5` =
  `ffc8399d05f3388d80b78c93482a5b95`; `RMSK_TABLE_URL`/`MD5` kept for qualification;
  `CHROM_SIZES_URL` added and pinned at fetch; `GENOME_FA_MD5` kept as declared; declared run
  identity fields `RM_VERSION="open-4.0.8"`, `RM_LIBRARY="RepBase 20181026; Dfam_Consensus 20181026"`,
  `RM_RUN_EVIDENCE=<UCSC README URL>`; `LOCUS_ID_FORM`, `INTERGENIC_MIN`, `EXPECT_LOCI_NOEXON`,
  `EXCLUDE_FAMILY_PREFIX`, `TE_CLASSES` removed (universes replace the last two). Gene GTF moves to
  the child family config (phase 8).
- `src/00_fetch_sources.sh`: fetches `.out.gz`, `chromAlias.txt`, `chrom.sizes`; verifies pins.
- `src/lib/rmsk_out.py`: parser profile `rm_out_v1`: 15 whitespace fields plus optional `*`;
  header recognition; parentheses stripped only from numeric fields; `C` mapped to `-` with raw
  strand kept; consensus fields normalized (`+`: start,end,left; `C`: left,end,start); raw
  class/family token kept and split once at `/`; `source_row_number` assigned; malformed row fails
  with line number.
- `tools/qualify_source.py`: field-level multiset comparison of `.out` against the UCSC table
  (coordinates 0/1-based, tenths-of-percent conversion, negative-left convention, class-only tokens
  duplicated into family by UCSC). Writes `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md`.

Acceptance (measured 2026-09-15, must reproduce)
- records parsed: 5,320,771; distinct instance ids: 4,696,900; ids never span two contigs.
- qualification: 5,320,771 rows match on (chrom, start_1, end_1, strand, name); class/family
  agrees after the class-only projection rule; consensus and score fields agree under the stated
  conversions; UCSC `id` excluded.
- `ID2 chr1:3051045-3051146 -` parses to consensus start 5, end 104, left 48.
- Fixtures under `tests/fixtures/source/`: plus and minus rows, `(TGCT)n`, a starred row, a
  class-only token, a malformed row.

Review focus: every parsed field traceable to a source column; no silent absolute values.
