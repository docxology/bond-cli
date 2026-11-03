<!-- vendored-sha: 1954d0f7fab994c20b86543c2e91daf6caed0c13 -->
# Vendored `bond-orchestrator`

This directory is a **copy, not a fork**: every file here is byte-identical to its upstream path at
the commit below, and `scripts/vendor.py --check` fails the moment that stops being true.

| | |
| --- | --- |
| Upstream | `docxology/bond-orchestrator` |
| Commit | `1954d0f7fab994c20b86543c2e91daf6caed0c13` |
| Copied | 15 files — `src/bond_orchestrator/**` plus `LICENSE`, `README.md`, `pyproject.toml` |
| Not copied | upstream `tests/`, `docs/`, `uv.lock`, and CI configuration |

**Why it is here.** The package is not installable from an index, and the primary consumer of this
repository clones it *alone* — Dependabot's update jobs run in a single-repository checkout — so a
suite-relative path cannot resolve there.

**Refreshing.** Re-copy from a clean upstream checkout and re-record:

```bash
scripts/vendor.py --refresh --from <path to a bond-orchestrator checkout> [--sha <commit>]
```

Edits belong upstream. A change made here is caught by `scripts/vendor.py --check`, which
`tests/test_vendor_provenance.py` runs inside this package's own gate.
