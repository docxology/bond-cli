---
name: bond-cli
description: Maintain the PROJECT BOND terminal front door (THE FRONT DOOR): dispatch, delegation, exit codes.
version: 1.0.0
author: activeinference.institute
license: MIT
tags: [project-bond, front-door, thin-orchestrator, mission-orchestration]
---

# bond-cli

Project-scoped skill for the in-repo terminal front door in this repository
(PROJECT BOND Layer 4 · codename **THE FRONT DOOR**). Load when working inside
the package.

## When to Use

- Maintaining `bond-cli`: the verb-first `bond` CLI (`list`, `brief`, `recon`,
  `plan`, `execute`, `debrief`, `run`, `status`, `gadgets`, `missions`,
  `whois`, `roster-export`), its `--json` output, and its color-safe tables.
- Verifying the package against the shared guardrail preamble (≥90% coverage,
  no mocks, thin orchestrators, delegation, no lineage residue).

## Quick Reference

```bash
cd <bond root>/bond-cli
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90

# ops-style verification
uv run python scripts/bond.py list
uv run python scripts/bond.py debrief goldfinger
uv run python scripts/bond.py run OPERATION_SINGLET
uv run python scripts/bond.py status
uv run python scripts/bond.py gadgets skyfall
```

## Architecture

- Depends on the FOUR built layers via `[tool.uv.sources]` path sources:
  bond-api (protocol/discovery/registry), bond-coordinator (registry/status),
  bond-orchestrator (missions/runner/adapters), bond-utilities (transitive).
- `src/bond_cli/dispatch.py` — argparse surface + delegation; no business logic.
  `COMMANDS` / `JSON_COMMANDS` / `DEPENDENCY_LAYERS` are the single source of
  every surface count.
- `src/bond_cli/table.py` — color-safe aligned tables (fixed width, no ANSI).
- `src/bond_cli/manuscript_variables.py` — `{{TOKEN}}` map.
- `scripts/bond.py` — thin bootstrap; console script `bond` is identical.

## Pitfalls

- **Delegate, don't duplicate.** The front door implements no mission logic;
  route to the layers.
- **No mocks.** Use real film providers — reference `sable` (numpy-free, fast)
  for the lifecycle, a real fleet film (`skyfall` has `register_gadgets`) for
  gadgets; real subprocess for `scripts/bond.py` smoke.
- **Search paths must exist.** `bond_api` validates that every provided search
  path is a directory — filter `_film_search_paths` to existing dirs (sable
  lives only under `bond-api/films`).
- **Exit codes:** 0 success, 1 command failure, 2 argparse misuse.
- **Pin the gate manifest.** The fleet's `output/aggregate/gate_manifest.json`
  lives outside this package and comes and goes; any test that depends on it
  must point `dispatch.GATE_MANIFEST` at a `tmp_path`, or the suite's result
  and branch coverage move with the workspace.
- **Report measurement honestly.** A film absent from a partial manifest must
  report `measured: null` — never its declared registry status dressed up as an
  observation. A measured `0.0` coverage is a measurement, not "unknown".
- **No hand-authored numbers.** Counts go in `build_tokens()` and
  `data/claim_ledger.yaml`, both re-derived by the suite.
- **Lineage / no-mock self-referential greps:** bracket-split or reword so your
  own docs and tests can't trip the fleet gates.
- **mypy:** the four layers ship without `py.typed` — the
  `[[tool.mypy.overrides]]` for `bond_*.*` silences import-untyped.

## Cross-refs

- Shared guardrail preamble + suite map:
  `software-development/bond-suite-package-development` skill.
- FROZEN protocol: `bond-api` (`docs/protocol.md` / `bond-api-phase1` reference).
- Official CLI + docs: `scripts/`, `docs/`.
