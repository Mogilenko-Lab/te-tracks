# Releases

Every build carries a `BUILD_ID`. Projects cite it and get exactly those bytes.

## BUILD_ID

```
BUILD_ID = sha256( sorted list of "<md5>  <relative path>" for every delivered output )
```

It covers the delivered tracks. `source/`, `MANIFEST.json` and `BUILD_ID` itself stay outside the
fingerprint, so a re-download or a fresh timestamp leaves it unchanged.

The id names the content. Two builds from the same sources and the same logic carry the same
`BUILD_ID`, and a build that changes any output carries a new one.

## What a build does on publication

**The id matches `current`.** The published snapshot stays where it is, the redundant directory is
removed, and `INDEX.tsv` gains a `reconfirmed` row. A re-run is a no-op with a receipt.

**The id differs.** The previous snapshot moves to `archive/<snapshot>__<build_id_short>`, `current`
moves onto the new snapshot, and `INDEX.tsv` gains an `archived` row and a `current` row.

Earlier builds stay on disk and stay complete, so a result produced against an earlier annotation
stays reproducible against the bytes that produced it.

## Layout

```
<refroot>/te_mm39/
├── current -> te_mm39_<date>        the published build
├── CURRENT_BUILD.tsv                build_id, snapshot, built_at, builder — one file to read
├── INDEX.tsv                        every build ever, with status
├── te_mm39_<date>/                  the published snapshot
│   ├── BUILD_ID
│   ├── MANIFEST.json
│   └── ... tracks ...
└── archive/
    └── te_mm39_<date>__<id12>/      superseded builds, complete
```

## Citing a build

A project records the `build_id` from `CURRENT_BUILD.tsv` at the time it ran.

```
build_id   3e75dad5f3a8f077d132a33c3325641ced7c3f5afc393bafe2a4c17babe13566
snapshot   te_mm39_20260914
```

`INDEX.tsv` resolves that id to a path, whether the build is current or archived.

## Verifying a snapshot

```
src/99_verify.sh <snapshot-dir> config/<genome>.env
```

It recomputes every output md5 against `MANIFEST.json` and re-asserts the declared shape. Run it
after a build and after any transfer between reference roots.

## Reference roots

```
/data2/users/shared/refcache          workstation, and mounted read-only into the Meta-Aging container at the same path
/gpfs/data/rathmell-lab/data/refdata  CRI
```

Build once on the workstation, transfer the snapshot, and verify it at the destination. One build
plus a checksum keeps both roots holding the same `BUILD_ID`.
