# AGENTS.md — bond-cli (PROJECT BOND · THE FRONT DOOR)

Operational rules for AI agents and developers working inside
`projects/working/bond/bond-cli/`. Read `docs/agent_instructions.md` first.

## Layer contract

| Surface | Rule |
|---|---|
| `src/bond_cli/dispatch.py` | Thin argparse front door. **No business logic** — every command delegates to a built layer (bond-api, bond-coordinator, bond-orchestrator). |
| `src/bond_cli/manuscript_variables.py` | Token map from `manuscript/config.yaml` + coordinator registry. |
| `scripts/` | Thin wrappers (sys.path bootstrap + argv forwarding) only. |
| `tests/` | Zero mocks; real film providers + real subprocess. |

Cross-cutting rules:

- **Delegation, not duplication.** Never re-implement mission logic, registry
  math, or the protocol here.
- **Depends on the four built layers** (path sources in pyproject); run
  `uv sync --extra dev` before pytest.
- ≥90% line+branch coverage on `src/`:
  `uv run pytest tests/ --cov=src --cov-fail-under=90`.
- Deterministic: fixed-seed providers, canonical output, no wall-clock in
  persisted artifacts.
- No `infrastructure.*` imports anywhere in `src/` or `scripts/`.
- Exit codes: 0 success, 1 command failure, 2 argparse misuse.
- No leftover exemplar-lineage strings; aim for zero. When referencing the
  lineage in this doc, bracket-split or reword so the doc cannot trip its own
  sweep.

## Verification commands

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" --glob '!uv.lock' --glob '!.git/**' -g '!output/**' . || echo Clean
git status --short   # clean after commit
```
