# AGENTS.md — bond-cli (PROJECT BOND · THE FRONT DOOR)

Operational rules for AI agents and developers working inside
`projects/working/bond/bond-cli/`. Read
[`docs/agent_instructions.md`](docs/agent_instructions.md) first, then
[`docs/architecture.md`](docs/architecture.md).

## Layer contract

| Surface | Rule |
|---|---|
| `src/bond_cli/dispatch.py` | Thin argparse front door. **No business logic** — every command delegates to a built layer (bond-api, bond-coordinator, bond-orchestrator). `COMMANDS`, `JSON_COMMANDS`, and `DEPENDENCY_LAYERS` are the single source of every surface count. |
| `src/bond_cli/table.py` | Fixed-width alignment only. Never emit ANSI, never truncate, never probe the terminal. |
| `src/bond_cli/manuscript_variables.py` | Token map from `manuscript/config.yaml` + the coordinator/orchestrator/dispatch registries. Never a literal count. |
| `scripts/` | Thin wrappers (sys.path bootstrap + argv forwarding) only. |
| `tests/` | Zero mocks; real film providers, real tmp film packages, real manifests, real subprocess. |
| `data/claim_ledger.yaml` | Every row names the symbol it is derived from, and the suite re-derives it. |

Cross-cutting rules:

- **Delegation, not duplication.** Never re-implement mission logic, registry
  math, or the protocol here.
- **Never alter the consumed contract.** This package ships no `mission.py`;
  it reads the frozen `MissionProvider` surface and the `GADGETS` conventions.
  Adding a stage or reinterpreting `success` here forks the protocol.
- **Depends on the four built layers** (path sources in pyproject); run
  `uv sync --extra dev` before pytest.
- ≥90% line+branch coverage on `src/`.
- **Pin ambient fleet state.** Any test that depends on the aggregate gate
  manifest must point `dispatch.GATE_MANIFEST` at a `tmp_path`.
- Deterministic: fixed-seed providers, canonical output, sorted JSON keys, no
  wall-clock in persisted artifacts.
- No `infrastructure.*` imports anywhere in `src/` or `scripts/`.
- Exit codes: 0 success, 1 command failure, 2 argparse misuse / unknown mission.
- No leftover exemplar-lineage strings; aim for zero. When referencing the
  lineage in a doc, bracket-split or reword so the doc cannot trip its own
  sweep.

## Build / test / verify

```bash
# One-time (installs bond-utilities, bond-api, bond-coordinator, bond-orchestrator
# from local path sources, plus the dev extras)
uv sync --extra dev

# Gates — all four must be clean before committing
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/

# Regenerate manuscript tokens after any config.yaml or registry change
uv run python scripts/z_generate_manuscript_variables.py

# Smoke the real entry points
uv run python scripts/bond.py status --json
uv run bond list

# Lineage sweep + clean tree
rg -n "template[_]code_project" --glob '!uv.lock' --glob '!.git/**' -g '!output/**' . || echo Clean
git status --short   # clean after commit
```

Measured results (test count, coverage %) belong in
[`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md) — update it when the
gate output changes, and do not copy the figures into other prose.

## Definition of done for a change here

1. Gates above are clean, and you read the output rather than assuming it.
2. New behaviour has a real test (no mock framework, no assertion that cannot
   fail).
3. A new command is in `build_parser()`, `COMMANDS`, `_handlers()`,
   `docs/architecture.md`, `README.md`, and the manuscript methodology/results.
4. A new countable fact is a `{{TOKEN}}`, a `data/claim_ledger.yaml` row, and a
   test that re-derives it.
5. `TODO.md` reflects what is actually left.
