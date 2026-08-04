# src/ — bond-cli front door

Importable package logic lives here. `dispatch.py` builds the argparse surface
and delegates to the built layers; `manuscript_variables.py` builds the token
map. The package deliberately owns **no mission logic**.

## Modules

- `bond_cli/dispatch.py` — `main(argv) -> int`, command handlers, `load_film`,
  `register_film_gadgets`, `_resolve_provider`.
- `bond_cli/manuscript_variables.py` — `{{TOKEN}}` map from
  `manuscript/config.yaml` + coordinator registry.

## Rules

- Delegate to `bond_api` / `bond_coordinator` / `bond_orchestrator`; never
  re-implement their logic.
- No `infrastructure.*` imports.
- Deterministic output; no wall-clock in persisted artifacts.
