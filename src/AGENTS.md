# src/ — bond-cli front door

Importable package logic lives here. `dispatch.py` builds the argparse surface
and delegates to the built layers; `table.py` renders; `manuscript_variables.py`
builds the token map. The package deliberately owns **no mission logic** and
ships **no `MissionProvider`** — it is the fleet's protocol consumer.

## Modules

- `bond_cli/dispatch.py` — `main(argv) -> int`; the `COMMANDS` /
  `JSON_COMMANDS` / `DEPENDENCY_LAYERS` registries; twelve `cmd_*` handlers;
  `load_film`; `register_film_gadgets`; `_resolve_provider`; and the
  reconciliation trio `_manifest_rows` / `_measured_coverage` / `_reconcile`
  composed by `_measured_roster`.
- `bond_cli/table.py` — color-safe aligned table rendering (no ANSI, no
  truncation, no terminal probing).
- `bond_cli/manuscript_variables.py` — token map from `manuscript/config.yaml`
  (identity + paper version) and the coordinator/orchestrator/dispatch
  registries; writes `output/variables/manuscript_variables.json`.

## Rules

- Delegate to `bond_api` / `bond_coordinator` / `bond_orchestrator`; never
  re-implement their logic, and never extend the frozen protocol here.
- No `infrastructure.*` imports.
- Deterministic output; sorted JSON keys; no wall-clock in persisted artifacts.
- Never write a literal count: derive it from the registry that owns it and
  expose it as a manuscript token plus a `data/claim_ledger.yaml` row.
- A measurement that is absent must be reported as absent — never substitute a
  declared registry value for an observed one.
