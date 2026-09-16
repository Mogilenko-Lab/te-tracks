# te-tracks phase 6: contig namespaces, aliases, coverage, preflight

You are the implementer for phase 6 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phases 0 to 5 have landed: read
`AGENTS.md`, `tests/run.sh` (checks under `tests/checks/<mode>/`, exit 0 pass, 3 unsupported, other fail;
build dir `$TE_TRACKS_REFROOT/te_mm39/build`), `docs/OUTPUTS.md`, `src/lib/build_exports.py` (the exporter
and its registration), `tests/lib/consumers.py`.

## Read first
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/16_phase6_ensembl_preflight.md` (your phase)
2. `docs/_internal/redesign-2026-09/audit/AUDIT.md` section 6 and
   `docs/_internal/redesign-2026-09/audit/gencode_grcm39_fasta_contigs.tsv` (the measured FASTA contigs)
3. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` entries 3, 5
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding)

## Facts
- `source/mm39.chromAlias.txt`: header `# ucsc assembly ensembl genbank refseq`, 61 data rows; e.g.
  `chr1 1 1 CM000994.3 NC_000067.7`, `chr1_GL456210v1_random MMCHR1_RANDOM_CTG1 GL456210.1 GL456210.1
  NT_166280.1`, `chrM MT MT AY172335.1 NC_005089.1`. `source/mm39.chrom.sizes`: 61 rows.
- The GENCODE FASTA (61 contigs) names chromosomes `chr1` … `chrM` and scaffolds by GenBank accession;
  all 61 lengths equal `chrom.sizes`. Namespace `gencode` = ucsc name when the ucsc name has no `_`,
  otherwise the genbank column. Verify this rule reproduces the 61 FASTA names exactly and report.
- `chr4_JH584295v1_random` and `chrM` carry zero RepeatMasker records.

## Deliverables (exact paths)
1. `src/lib/contigs.py` + `src/35_build_namespaces.sh <build-dir> <config.env>`:
   - `tables/contig_aliases.tsv`: `chrom_ucsc, chrom_ensembl, chrom_gencode, chrom_genbank, chrom_refseq,
     length_bp`; 61 rows; each name column injective; every `chrom` in `rmsk_records` present.
   - `tables/contig_coverage.tsv`: per contig: `chrom_ucsc, length_bp, records_all, records_interspersed,
     has_ensembl, has_gencode, length_agrees` (against the source list).
   - Re-emits every export under `exports/ensembl/interspersed/full/` and `exports/gencode/interspersed/full/`
     (`record.bed, subfamily.bed, family.bed, record.gtf, subfamily.saf, taxonomy_triple.saf`) by renaming
     the contig column of the `ucsc` files through the alias table; rows otherwise byte-identical;
     `rmsk_record_id` and the GTF record alias keep UCSC names inside. Registers the new paths in
     `export_feature_members` and `export_summary` (extend the existing writer; the registration for
     renamed exports repeats the ucsc rows under the new path). Sorted by the renamed contig in C-locale
     order, then start, end, strand, name (consumers read sorted files).
2. `bin/te-tracks-preflight <export> <bam|fai|sizes>` (executable python): reads contig names and lengths
   from a BAM header (pysam), a `.fai`, or a two-column sizes TSV; reads the export's contig set (column 1
   of BED/SAF/GTF, skipping the SAF header); reports `only_in_reference`, `only_in_export`,
   `length_disagreements` (export contigs' lengths come from `contig_aliases.tsv` located relative to the
   export path, two directories above `exports/`... locate it as `<build-dir>/tables/contig_aliases.tsv`
   by walking up from the export path to the directory containing `MANIFEST.json` or `tables/`); exit 0 when
   all three lists are empty, 1 otherwise, printing each list.
3. Checks under `tests/checks/core/`:
   - `60_contig_aliases.py`: 61 rows; injectivity; `chr1_GL456210v1_random` → ensembl `GL456210.1`,
     gencode `GL456210.1`; `chrM` → ensembl `MT`, gencode `chrM`; the gencode column equals the 61 FASTA
     names in `tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv` (copy of the audit file) with equal
     lengths; coverage: `chr4_JH584295v1_random` and `chrM` have zero records.
   - `61_namespace_exports.py`: for each of the six exports, row counts equal across `ucsc`, `ensembl`,
     `gencode`; columns other than the contig column byte-identical row-for-row on a 10,000-row aligned
     sample (sort both by rmsk_record_id or by the GTF alias to align); the contig column maps through
     the alias table.
   - `62_preflight.sh`: preflight of `exports/gencode/.../record.gtf` against the FASTA contig list
     (sizes mode) exits 0; against `exports/ucsc/.../record.gtf` exits 1 listing exactly the 39 scaffolds
     as `only_in_export`/`only_in_reference` pairs; against `exports/ensembl/...` exits 1 listing the 22
     chromosomes; a synthetic BAM header (pysam, contigs `chr1` with a wrong length) reports one length
     disagreement.
4. `docs/OUTPUTS.md`: the alias and coverage tables; the namespace rule (one sentence per namespace); the
   preflight command. `docs/DECISIONS.md` entry 3: the release ships exports in the `ucsc`, `ensembl` and
   `gencode` contig namespaces (edit that one sentence). README truth table: `contig_aliases`,
   `contig_coverage`, the ensembl and gencode export rows, `bin/te-tracks-preflight` to `tested`, phase 6.

## Rules
- Touch only: `src/lib/contigs.py`, `src/35_build_namespaces.sh`, `src/lib/build_exports.py` (only to reuse
  its writers/registration), `bin/te-tracks-preflight`, `tests/checks/core/6*`, `tests/fixtures/contigs/**`,
  `docs/OUTPUTS.md`, `docs/DECISIONS.md` (entry 3, one sentence), `README.md` (truth table).
- No git writes. No installs. No network.
- Report a deviation instead of editing a number or a plan file to fit.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
time bash src/35_build_namespaces.sh "$TE_TRACKS_REFROOT/te_mm39/build" config/mm39.env; echo "exit=$?"
B="$TE_TRACKS_REFROOT/te_mm39/build"
head -3 "$B/tables/contig_aliases.tsv"; grep -E "^chr1_GL456210v1_random|^chrM" "$B/tables/contig_aliases.tsv"
awk -F'\t' '$3==0 || $4==0' "$B/tables/contig_coverage.tsv"
for ns in ucsc ensembl gencode; do wc -l "$B/exports/$ns/interspersed/full/"*; done
head -1 "$B/exports/ensembl/interspersed/full/record.gtf"; head -1 "$B/exports/gencode/interspersed/full/record.gtf"
bin/te-tracks-preflight "$B/exports/gencode/interspersed/full/record.gtf" tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv; echo "exit=$?"
bin/te-tracks-preflight "$B/exports/ucsc/interspersed/full/record.gtf" tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv | tail -3; echo "exit=$?"
tests/run.sh core; echo "exit=$?"
git status --short
```

## Final message
Every file created or changed; acceptance outputs verbatim; confirmation that the gencode rule reproduces
all 61 FASTA names; any deviation.
