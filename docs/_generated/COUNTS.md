# COUNTS.md — bond-cli live measured evidence

The only place in this package where a measured figure is written down.
Re-measure and update after every gate run; never copy these numbers into
prose elsewhere.

- **Test count:** 83
- **Coverage (src/), line + branch:** 99.55 %

Per-module coverage from the same run:

| Module | Stmts | Miss | Branch | BrPart | Cover |
|---|---|---|---|---|---|
| `src/bond_cli/dispatch.py` | 285 | 0 | 76 | 2 | 99.45 % |
| `src/bond_cli/manuscript_variables.py` | 57 | 0 | 14 | 0 | 100.00 % |
| `src/bond_cli/table.py` | 10 | 0 | 2 | 0 | 100.00 % |
| **TOTAL** | **352** | **0** | **92** | **2** | **99.55 %** |

Remaining partial branches (tracked in `TODO.md`): the "debrief returned no
lessons" path, and the whole-fleet `gadgets` loop exit.

> Measured on 2026-08-04 via
> `uv run pytest tests/ --cov=src --cov-fail-under=90`, after the Phase-5
> documentation-and-hardening pass (measured-coverage reconciliation fixes,
> partial-manifest honesty in `whois`, ambient-state pinning, claim-ledger
> re-derivation, token expansion). `uv run ruff check src/ scripts/ tests/`,
> `uv run ruff format --check src/ scripts/ tests/`, and
> `uv run mypy src/ scripts/` all clean in the same pass.
