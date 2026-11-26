# src/

Importable front-door package (THE FRONT DOOR):

- `bond_cli/__init__.py` — package identity; sets `__version__` before the
  submodule imports (it is the `PACKAGE_VERSION` token's fallback).
- `bond_cli/dispatch.py` — the `bond` argparse CLI: command registries, the
  twelve command handlers, film loading, gate-manifest reconciliation, and the
  tolerant gadget harvest. Delegates every computation to the fleet layers.
- `bond_cli/table.py` — color-safe aligned table rendering (fixed width, no ANSI).
- `bond_cli/manuscript_variables.py` — manuscript token map (config identity +
  live registry counts).

`src/__init__.py` is a plain source-layout marker. Run the CLI via
`scripts/bond.py` or the installed `bond` console script. Design detail:
`../docs/architecture.md`.
