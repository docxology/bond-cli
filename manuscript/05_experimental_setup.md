# Experimental Setup

- **Runtime.** Python ≥3.10; the four built layers wired via `[tool.uv.sources]` path sources (bond-api, bond-coordinator, bond-orchestrator, bond-utilities) plus NumPy (film providers load it at import time) and PyYAML.
- **Entry points.** Console script `bond` (`bond = "bond_cli.dispatch:main"`) and the thin `scripts/bond.py` bootstrap — identical dispatch.
- **Film discovery.** `bond_api.discovery.load_provider` over `<slug>/src` (fleet) and `bond-api/films` (reference), FROZEN contract.
- **Mission execution.** `bond_orchestrator.runner.MissionRunner` over real film adapters with deterministic fallback.
- **Toolchain** (dev extras): `pytest`, `pytest-cov`, `ruff`, `mypy`, `types-PyYAML`.
- **Tests.** Real subprocess CLI smoke against the real packages (`python scripts/bond.py list`, etc.) plus in-process dispatch tests against deterministic film providers; zero mocks; ≥90% line+branch coverage on `src/`.
