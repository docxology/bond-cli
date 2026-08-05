# COUNTS.md — bond-cli live measured evidence

The only place in this package where a measured figure is written down.
Re-measure and update after every gate run; never copy these numbers into
prose elsewhere.

- **Test count:** 103
- **Coverage (src/), line + branch:** 100.00 %

Per-module coverage from the same run:

| Module | Stmts | Miss | Branch | BrPart | Cover |
|---|---|---|---|---|---|
| `src/bond_cli/dispatch.py` | 285 | 0 | 76 | 0 | 100.00 % |
| `src/bond_cli/manuscript_variables.py` | 57 | 0 | 14 | 0 | 100.00 % |
| `src/bond_cli/table.py` | 10 | 0 | 2 | 0 | 100.00 % |
| **TOTAL** | **352** | **0** | **92** | **0** | **100.00 %** |

Remaining partial branches: none — `BrPart` is 0 in every row above. The two
that stood at the previous measurement are both closed by
`tests/test_contracts.py`:

- `dispatch.py:240->243` — the "debrief returned no lessons" path, reached by a
  real film package whose `Debrief.lessons` is empty;
- `dispatch.py:588->590` — the `register_film_gadgets` fall-through for a
  module-level `GADGETS` that is neither a `GadgetRegistry` nor a `dict`. This
  is a conditional fall-through, **not** a loop exit and not fleet-wide; the
  note previously in this file mislabelled it as "the whole-fleet `gadgets`
  loop exit", and an agent following that description would have written the
  wrong test.

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

> Measured on 2026-08-05 via
> `uv run pytest tests/ --cov=src --cov-fail-under=90`, after the exit-code and
> sorted-keys contract pass. `uv run ruff check src/ scripts/ tests/`,
> `uv run ruff format --check src/ scripts/ tests/`, and
> `uv run mypy src/ scripts/` all clean in the same pass.
