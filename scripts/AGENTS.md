# scripts/ — thin wrappers

Thin orchestrators only. `bond.py` bootstraps `src/` and forwards argv to
`bond_cli.dispatch.main`; `z_generate_manuscript_variables.py` delegates to
`bond_cli.manuscript_variables.generate_variables`. No business logic here.

Run (from the package root):

```bash
uv run python scripts/bond.py list
uv run python scripts/bond.py debrief goldfinger
uv run python scripts/bond.py run OPERATION_OMNIBUS
uv run python scripts/bond.py missions
uv run python scripts/bond.py whois goldfinger
```
