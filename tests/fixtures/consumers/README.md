# Consumer fixtures

- `expected.json` pins roster taxonomy, endpoint answers, BAM alignment/template/molecule totals, raw/corrected UMI counts and flags; consumer checks 10–25 read it through `tests/lib/consumers.py`, and check 00 loads it on import.
- `starsolo_host.gtf` pins a two-exon host gene for alias preflight and combined counting/reference construction; `tests/checks/consumers/17_starsolo_profile.required.py`, `24_starsolo_exec.sh` and `25_cellranger_mkref.sh` read it.
- `starsolo_collision.gtf` pins an exact host gene-ID collision with a TE alias; `tests/checks/consumers/17_starsolo_profile.required.py` reads it.
- `starsolo_reserved.gtf` pins a reserved host gene-ID prefix without an exact TE collision; `tests/checks/consumers/17_starsolo_profile.required.py` reads it.
- `starsolo_molecules.tsv` pins same-name records, reverse strand, instance gap, exon overlap and host-intronic support; `tests/checks/consumers/24_starsolo_exec.sh` reads it.

The collision and reserved-prefix GTFs differ only in `gene_id`; each pins a distinct refusal. ARC/OCM expectation pairs vary alignment counts with mate layout; 4/2 and 3/3 allocation fixtures retain separate asymmetric and symmetric support boundaries.
