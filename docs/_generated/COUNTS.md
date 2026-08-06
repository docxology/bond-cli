# COUNTS.md — bond-cli live measured evidence

The only place in this package where a measured figure is written down.
Re-measure and update after every gate run; never copy these numbers into
prose elsewhere.

- **Test count:** 113
- **Coverage (src/), line + branch:** 100.00 %

Per-module coverage from the same run:

| Module | Stmts | Miss | Branch | BrPart | Cover |
|---|---|---|---|---|---|
| `src/bond_cli/dispatch.py` | 301 | 0 | 80 | 0 | 100.00 % |
| `src/bond_cli/manuscript_variables.py` | 57 | 0 | 14 | 0 | 100.00 % |
| `src/bond_cli/table.py` | 10 | 0 | 2 | 0 | 100.00 % |
| **TOTAL** | **368** | **0** | **96** | **0** | **100.00 %** |

Remaining partial branches: none — `BrPart` is 0 in every row above.

## What this number does and does not prove

100 % line + branch coverage on `src/` means every statement and every
`if`/`elif`/loop arc is executed by the suite. It does **not** by itself mean
every documented behaviour is pinned. Coverage.py emits no arc for a
conditional expression (`return 0 if ok else 1`), and parsing JSON back into a
dict discards key order — so both the exit-code contract and the sorted-keys
contract were fully "covered" at 99.55 % while remaining entirely unverified,
until `tests/test_contracts.py` bound them. Each of those tests was checked by
mutation: flipping the guarded behaviour in `dispatch.py` turns them red.

| Mutation applied to `src/bond_cli/dispatch.py` | Result |
|---|---|
| all three `return 0 if <predicate> else 1` → `return 0` | 3 failures (`test_execute_failing_film_exits_1`, `test_debrief_failing_film_exits_1`, `test_run_mission_with_failing_film_exits_1`) |
| all six `sort_keys=True` → `sort_keys=False` | 7 failures (the four `--json` surfaces, `roster-export` to stdout and to `--output`, and `_fmt_value`) |
| human `status`: `min={minimum} max={maximum}` → `min={coverage.minimum}%` | 1 failure (`test_status_human_none_coverage_does_not_print_none`) — a literal `None%` prints to human status |
| `_invoke_register_hook(register, registry)` → `except TypeError: register()` fallback | 1 failure (`test_register_gadgets_hook_body_typeerror_is_contained`) — a body `TypeError` is re-invoked as a zero-arg hook and escapes a misleading `TypeError: missing 1 required positional argument` |

Each round-2 mutation was applied to `dispatch.py`, the named test turned red, and the change was reverted before the next run.

> Measured on 2026-08-06 via
> `uv run pytest tests/ --cov=src --cov-fail-under=90` (113 passed, 100.00 %).
> `uv run ruff check src/ scripts/ tests/`, `uv run ruff format --check src/
> scripts/ tests/`, and `uv run mypy src/ scripts/` all clean in the same pass.
> Round 2 also bound three repeatability/verify claims the coverage gate cannot
> see: `status --json` and `roster-export` asserted byte-identical across two
> subprocesses, the installed `bond` console script asserted equal to the
> `scripts/bond.py` bootstrap, and the `cross_cutting` layer-contract rules
> (no `infrastructure.*`, no wall-clock, no terminal/environment reads) asserted
> against the `src/` + `scripts/` trees.
