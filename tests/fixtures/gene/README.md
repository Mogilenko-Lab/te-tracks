# Gene child fixtures

- `annotation.gtf` pins exon unions with central cuts, introns, adjacent/overlapping/nested/duplicate exons, opposite strands and scaffold aliases; `tests/checks/core/81_exon_subtraction_fixtures.py` reads it.
- `contig_aliases.tsv` pins primary/scaffold name normalization and an unannotated contig; `tests/checks/core/81_exon_subtraction_fixtures.py` reads it.
- `coverage.tsv` pins gene/transcript/exon counts, exon-union bases and unannotated status; `tests/checks/core/81_exon_subtraction_fixtures.py` reads it.
- `geometry.json` pins 15 hand-authored block/status/conservation answers, including one retained base and four retained blocks; `tests/checks/core/81_exon_subtraction_fixtures.py` reads it.
- `publication_cases.py` pins child dependency closure, convergence, corruption refusals, selection and immutable modes; `tests/checks/core/83_child_publication_cases.sh` executes it.

Intronic, intergenic, touching and unannotated records share unchanged support and pin distinct geometries. Central, adjacent, opposite-strand, duplicate, nested and scaffold cases share block sizes while pinning separate union, strand and alias boundaries.
