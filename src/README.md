# src/

Importable front-door package (THEN FRONT DOOR):

- `bond_cli/dispatch.py` — the `bond` argparse CLI, delegating to the fleet layers.
- `bond_cli/manuscript_variables.py` — manuscript token map.

`src/__init__.py` is a plain source-layout marker. Run the CLI via
`scripts/bond.py` or the installed `bond` console script.
