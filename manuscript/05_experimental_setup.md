# Experimental Setup

- **Runtime.** Python ≥3.10; the {{LAYER_COUNT}} built layers ({{LAYER_NAMES}}) wired via `[tool.uv.sources]` path sources, plus NumPy (film providers load it at import time) and PyYAML (manuscript config).
- **Entry points.** Console script `bond` (`bond = "bond_cli.dispatch:main"`) and the thin `scripts/bond.py` bootstrap — identical dispatch, both returning the same exit codes.
- **Film discovery.** `bond_api.discovery.load_provider` over `<slug>/src` (fleet layout) and `bond-api/films` (reference layout), FROZEN contract; only existing directories are offered to it.
- **Mission execution.** `bond_orchestrator.runner.MissionRunner` over real film adapters, with the orchestrator's built-in deterministic provider as fallback for films not yet built on disk.
- **Measured fleet state.** The aggregate gate manifest at `<bond root>/output/aggregate/gate_manifest.json`, written by the fleet gate runner. Absent, unreadable, or malformed ⇒ registry-only reporting; the tests pin this path at a temporary file so no result depends on whether the workspace currently holds a manifest.
- **Output layer.** `src/bond_cli/table.py::format_table` for color-safe aligned tables (no ANSI); JSON output follows RFC 8259 [@rfc8259], is key-sorted, and never embeds wall-clock values.
- **Token hydration.** `scripts/z_generate_manuscript_variables.py` → `src/bond_cli/manuscript_variables.py` → `output/variables/manuscript_variables.json`; identity from `manuscript/config.yaml`, counts from the live registries.
- **Toolchain** (dev extras): `pytest`, `pytest-cov`, `ruff`, `mypy`, `types-PyYAML`.
- **Gates.** `uv run pytest tests/ --cov=src --cov-fail-under=90` (line + branch), `uv run ruff check src/ scripts/ tests/`, `uv run ruff format --check src/ scripts/ tests/`, `uv run mypy src/ scripts/`. Measured results are recorded in `docs/_generated/COUNTS.md`, not in this prose.
- **Tests.** Real subprocess CLI smoke against the real packages plus in-process dispatch tests against real deterministic film providers and real temporary film packages; zero mocks.
