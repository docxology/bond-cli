# STANDALONE.md — bond-cli

`bond-cli` is a standalone local package: it can be run and verified from its
own directory, given the four built layers it carries under `vendor/`
(bond-api, bond-coordinator, bond-orchestrator, bond-utilities).

```bash
cd <this package root>    # the four built layers travel in vendor/
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run python scripts/bond.py list
```

Running the full test suite additionally requires the real fleet: six of its
tests import fleet film packages, with their runtime dependencies, and read the
fleet's aggregate gate manifest. In a lone clone those six fail rather than
skip, so run them where the fleet is importable.

It inspects and drives the built layers only through their public interfaces
(discovery, registry, missions, status).
