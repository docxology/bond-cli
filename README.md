# bond-cli — PROJECT BOND · THE FRONT DOOR

The unified terminal front door for the PROJECT BOND fleet: 27 film packages
plus shared mission infrastructure. It routes verb-first commands to the built
layers and maps their outcomes to exit codes.

**Manuscript identity:** `BOND-CLI` · codename **THE FRONT DOOR** · Layer 4 ·
version 3.0.0.

This is a **local-only** working tree (no remote, never pushed). `bond-cli`
delegates everything to the sibling layers it depends on and implements none of
their logic — it ships no `MissionProvider` and no mission mathematics.

## The film/concept mapping

Every other package in the suite maps a *film* to software. This one maps the
*franchise's operational frame*: an operator receives a briefing, walks a
mission through its stages, runs a multi-part operation, and gets a status
board back. `bond-cli` is the desk that grammar happens at — one verb, one
target, one exit code — for all 27 films at once. Its own concept is the front
door itself: uniform access to heterogeneous capability, which is exactly what
a fleet of standalone packages otherwise lacks.

## Commands

| Command | Delegates to | Action |
|---|---|---|
| `bond list [--json]` | `bond_coordinator.registry` | print all 27 films (rank, slug, title, year, codename) |
| `bond brief <film>` | `bond_api` provider | print a film's `MissionBrief` |
| `bond recon <film> [goal]` | `bond_api` provider | print a film's recon findings |
| `bond plan <film>` | `bond_api` provider | print a film's `MissionPlan` steps |
| `bond execute <film>` | `bond_api` provider | execute a plan, print the `MissionOutcome` + provenance |
| `bond debrief <film>` | `bond_api` provider (`run_mission`) | run the full five-stage flow, print the `Debrief` |
| `bond run <mission>` | `bond_orchestrator` | run a canned mission end-to-end, consolidated debrief |
| `bond status [--json]` | `bond_coordinator.status` + gate manifest | suite-status snapshot (measured coverage when gated) |
| `bond gadgets [film]` | `bond_api.registry.GadgetRegistry` | list gadget-payload names (one film or the fleet) |
| `bond missions [--json]` | `bond_orchestrator.missions` | list canned missions + package chains |
| `bond whois <film> [--json]` | `bond_coordinator.registry` + gate manifest | registry identity, built-on-disk, measured state |
| `bond roster-export [--output PATH]` | `bond_coordinator.registry` + gate manifest | fleet roster as key-sorted JSON |

`list`/`status`/`missions`/`whois` accept `--json`; `roster-export` is JSON by
construction. Human tables are color-safe (fixed-width alignment, no ANSI).

**Exit codes:** `0` success · `1` command failure (unknown/broken film, non-passing
execute/debrief/run, empty or broken gadget lookup) · `2` argparse misuse or unknown
mission. All failure text goes to **stderr** — stdout on a failed command carries
only data. In particular `bond gadgets <film>` distinguishes three outcomes: an
unknown slug raises the same "not available" `CliError` as `brief`/`plan`, a
built-but-broken film is diagnosed to stderr (naming the exception) while still
contributing 0 so a whole-fleet sweep never aborts, and a clean film with no
gadgets keeps the empty-lookup message.

## The MissionProvider surface it consumes

`bond-cli` is the fleet's pure *consumer* of the frozen `bond-api` contract. It
reads exactly these members and never extends them:

| Stage | Call | Fields read |
|---|---|---|
| brief | `provider.brief()` | `film`, `codename`, `objectives`, optional `assets`, `constraints` |
| recon | `provider.recon(ReconRequest(goal=...))` | `findings[].label`, `.detail` |
| plan | `provider.plan(brief)` | `steps[].name`, `.action` |
| execute | `provider.execute(plan)` | `success`, `results`, `provenance` |
| debrief | `bond_api.protocol.run_mission(provider, request)` | `outcome`, `lessons` |
| gadgets | `bond_api.registry.GadgetRegistry` | `register`, `lookup`, `gadgets_for`, `films` |

Films are located through `bond_api.discovery.load_provider` over
`<bond root>/<slug>/src` and `<bond root>/bond-api/films`. Gadget discovery
tolerates every registration convention the fleet uses (hook arities, a module
`GADGETS` dict or factory, a module-level `GadgetRegistry`, provider-bound
registration); a film that fails to import contributes zero rather than
aborting a fleet-wide sweep.

## Install and run

```bash
# From this package directory (installs the four built layers via path sources)
uv sync --extra dev

# The full film roster
uv run python scripts/bond.py list

# A film's lifecycle (the reference film is numpy-free and fast)
uv run python scripts/bond.py brief sable
uv run python scripts/bond.py debrief goldfinger

# Run a canned orchestrator mission
uv run python scripts/bond.py run OPERATION_SINGLET

# Suite status, gadget registry, and the deepened surface
uv run python scripts/bond.py status
uv run python scripts/bond.py status --json
uv run python scripts/bond.py gadgets skyfall
uv run python scripts/bond.py missions
uv run python scripts/bond.py whois goldfinger --json
uv run python scripts/bond.py roster-export --output /tmp/roster.json

# The installed console script is identical
uv run bond list
```

## Modules

| Path | Description |
|---|---|
| `src/bond_cli/__init__.py` | Package identity; assigns `__version__` before submodule import (the `{{PACKAGE_VERSION}}` fallback) |
| `src/bond_cli/dispatch.py` | The front door: command registries, twelve `cmd_*` handlers, film loading, gate-manifest reconciliation, tolerant gadget harvest, argparse surface, `main() -> int` |
| `src/bond_cli/table.py` | `format_table` — fixed-width, ANSI-free, byte-stable table rendering |
| `src/bond_cli/manuscript_variables.py` | `{{TOKEN}}` map from `manuscript/config.yaml` + the coordinator/orchestrator/dispatch registries; persists `output/variables/manuscript_variables.json` |
| `scripts/bond.py` | Thin `sys.path` bootstrap → `dispatch.main` |
| `scripts/z_generate_manuscript_variables.py` | Thin orchestrator → `manuscript_variables.generate_variables` |

## Dependencies (all built, wired via pyproject `[tool.uv.sources]` path sources)

- `bond-utilities` (Q-BRANCH) — ciphers, codenames, clocks, deterministic RNG; loaded transitively by film providers
- `bond-api` (THE PROTOCOL) — frozen `MissionProvider` contract, discovery, `GadgetRegistry`
- `bond-coordinator` (MISSION CONTROL) — the roster (`ROSTER`) and suite status
- `bond-orchestrator` (DAG 00) — canned missions, `MissionRunner`, film adapters

## Testing

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90     # line + branch, ≥90% gate
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

Zero mocks: real film providers (`sable`, `goldfinger`, `skyfall`), real
importable film packages written to `tmp_path`, real gate manifests, and real
subprocess invocations of `scripts/`. The measured test count and coverage %
live in [`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md) — this README
names the gate rather than quoting a figure that would go stale. See
[`docs/testing_philosophy.md`](docs/testing_philosophy.md).

## Documentation

- [`docs/agent_instructions.md`](docs/agent_instructions.md) — the hard rules (read first)
- [`docs/architecture.md`](docs/architecture.md) — module-by-module design and the consumed protocol surface
- [`docs/testing_philosophy.md`](docs/testing_philosophy.md) — zero-mock doctrine, ambient-state pinning
- [`manuscript/`](manuscript/) — the publishable narrative; every number is an injected `{{TOKEN}}`
- [`TODO.md`](TODO.md) — the remaining work
