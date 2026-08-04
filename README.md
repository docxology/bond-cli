# bond-cli — PROJECT BOND · THE FRONT DOOR

Unified terminal front door for the PROJECT BOND fleet — 27 film packages plus
shared mission infrastructure. It routes verb-first commands to the built
layers and maps their outcomes to exit codes.

**Manuscript identity:** `BOND-CLI` · codename **THE FRONT DOOR** · Layer 4.

This is a **local-only** working tree (no remote, never pushed). `bond-cli`
delegates everything to the sibling layers it depends on and implements none of
their logic.

## What it does

| Command | Delegates to | Action |
|---|---|---|
| `bond list` | `bond_coordinator.registry` | print all 27 films (rank, slug, title, year, codename) |
| `bond brief <film>` | `bond_api` provider | print a film's `MissionBrief` |
| `bond recon <film> [goal]` | `bond_api` provider | print a film's recon findings |
| `bond plan <film>` | `bond_api` provider | print a film's `MissionPlan` steps |
| `bond execute <film>` | `bond_api` provider | execute a plan, print the `MissionOutcome` + provenance |
| `bond debrief <film>` | `bond_api` provider (`run_mission`) | run the full five-stage flow, print the `Debrief` |
| `bond run <mission>` | `bond_orchestrator` | run a canned mission end-to-end, consolidated debrief |
| `bond status` | `bond_coordinator.status` | suite-status snapshot (counts, coverage, blocked) |
| `bond gadgets [film]` | `bond_api.registry.GadgetRegistry` | list gadget-payload names (one film or the fleet) |

## Quick usage

```bash
# From this package directory (installs the four built layers via path sources)
uv sync --extra dev

# The full film roster
uv run python scripts/bond.py list

# A film's lifecycle (reference film is numpy-free and fast)
uv run python scripts/bond.py brief sable
uv run python scripts/bond.py debrief goldfinger

# Run a canned orchestrator mission
uv run python scripts/bond.py run OPERATION_SINGLET

# Suite status + gadget registry
uv run python scripts/bond.py status
uv run python scripts/bond.py gadgets skyfall

# The installed console script is identical
uv run bond list
```

## Dependencies (all built, wired via pyproject `[tool.uv.sources]` path sources)

- `bond-api` (THE PROTOCOL) — frozen `MissionProvider` contract, discovery, `GadgetRegistry`
- `bond-coordinator` (MISSION CONTROL) — registry (`ROSTER`), suite status
- `bond-orchestrator` (DAG 00) — canned missions, `MissionRunner`, film adapters
- `bond-utilities` (Q-BRANCH) — loaded transitively by film providers

## Testing

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Zero mocks; real film providers (the light reference film `sable` for the
lifecycle, a real fleet film for gadgets/missions) plus subprocess smoke of
`scripts/bond.py`. See [`docs/testing_philosophy.md`](docs/testing_philosophy.md).

## Structure

- `src/bond_cli/dispatch.py` — argparse front door + delegation (all logic lives in the layers)
- `src/bond_cli/manuscript_variables.py` — `{{TOKEN}}` map from config + registry
- `scripts/bond.py` — thin sys.path bootstrap wrapper
- `scripts/z_generate_manuscript_variables.py` — manuscript token hydration
