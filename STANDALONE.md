# STANDALONE.md — bond-cli

`bond-cli` is a standalone local package: it can be run, tested, and verified
entirely from its own directory, given the four built sibling layers available
on path (bond-api, bond-coordinator, bond-orchestrator, bond-utilities).

```bash
cd /Users/4d/Documents/GitHub/template/projects/working/bond/bond-cli
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run python scripts/bond.py list
```

It inspects and drives sibling packages only through their public interfaces
(discovery, registry, missions, status). There is no remote; never push.
