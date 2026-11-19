<!-- vendored-sha: 9f98079b2de0c10d60e9447c6c534abbc8d659b0 -->
# Vendored `bond-api`

This directory is a **copy, not a fork**: every file here is byte-identical to its upstream path at
the commit below, and `scripts/vendor.py --check` fails the moment that stops being true.

| | |
| --- | --- |
| Upstream | `docxology/bond-api` |
| Commit | `9f98079b2de0c10d60e9447c6c534abbc8d659b0` |
| Copied | 10 files — `src/bond_api/**` plus `LICENSE`, `README.md`, `pyproject.toml` |
| Not copied | upstream `tests/`, `docs/`, `uv.lock`, and CI configuration |

**Why it is here.** The package is not installable from an index, and the primary consumer of this
repository clones it *alone* — Dependabot's update jobs run in a single-repository checkout — so a
suite-relative path cannot resolve there.

**Refreshing.** Re-copy from a clean upstream checkout and re-record:

```bash
scripts/vendor.py --refresh --from <path to a bond-api checkout> [--sha <commit>]
```

Edits belong upstream. A change made here is caught by `scripts/vendor.py --check`, which
`tests/test_vendor_provenance.py` runs inside this package's own gate.
