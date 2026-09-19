# Publication fixtures

- `build_fixture.py` supplies complete tiny core/child builds, text instance 007, pinned sources and an extended export roster for identity, corruption and publication contracts; `tests/checks/core/71_verify_build.py`, `72_publication_cases.py`, `73_clean_publication.py` and `82_child_identity.py` import it, and `83_child_publication_cases.sh` reaches it through `tests/fixtures/gene/publication_cases.py`.

Build notes vary one retained source value to pin distinct build identities; `record_extra.bed` exercises archive evolution through all three namespaces. Generated outputs stay in scratch; authored expectations stay in this tree.
