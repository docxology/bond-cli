# tests/ — front-door test suite

Zero mocks. Real film providers (reference `sable` + a real fleet film) and
real subprocess smoke of `scripts/bond.py`. Persistent cases are covered
in-process (`dispatch.main` + `capsys`) so they count toward the `src/` gate.

## Files

| File | Covers |
|---|---|
| `test_dispatch.py` | in-process command routing, provider lifecycle, gadgets, exit codes, measured status |
| `test_deepening.py` | `missions`/`whois`/`roster-export`, `--json`, color-safe tables, gadget-convention tolerance (tmp fake films) |
| `test_manuscript_variables.py` | `{{TOKEN}}` map + live manuscript cross-reference |
| `test_scripts_smoke.py` | subprocess `scripts/bond.py` + token hydration |

Gate: `uv run pytest tests/ --cov=src --cov-fail-under=90`.
