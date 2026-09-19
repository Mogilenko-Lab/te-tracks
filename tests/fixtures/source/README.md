# Source parser fixtures

- `records.out` pins headers, blank lines, both strands, class-only and multi-slash labels, a shared instance, an overlap star and signed consensus fields; `tests/checks/core/10_rmsk_out_parser.py` reads it.
- `expected.tsv` pins every typed field and source-row ordinal for `records.out`; `tests/checks/core/10_rmsk_out_parser.py` reads it.
- `unparenthesized_reverse_left.out` pins the reverse-strand consensus-left parentheses requirement and line-4 diagnostic; `tests/checks/core/10_rmsk_out_parser.py` reads it.
