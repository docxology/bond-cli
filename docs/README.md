# docs/ — bond-cli (THE FRONT DOOR)

Documentation for the PROJECT BOND terminal front door: Layer 4, a thin
dispatch surface over the four built layers (`bond-utilities`, `bond-api`,
`bond-coordinator`, `bond-orchestrator`). This directory holds the operational
rulebook and the design record; `../manuscript/` holds the publishable
narrative, and `../README.md` holds the operator quick-start.

## Contents

| File | Read it for |
|---|---|
| [`agent_instructions.md`](agent_instructions.md) | **Read first.** The hard rules for changing anything in this package, each with the consequence of breaking it. |
| [`architecture.md`](architecture.md) | Module-by-module design: what `dispatch.py`, `table.py`, and `manuscript_variables.py` each compute; the command/JSON/layer registries; gate-manifest reconciliation; the tolerant gadget harvest; how the CLI consumes (never implements) the frozen `MissionProvider` contract; the exit-code contract. |
| [`testing_philosophy.md`](testing_philosophy.md) | The zero-mock / real-data / determinism doctrine as it applies to a CLI: what each test file covers, why ambient fleet state must be pinned, and the coverage gate. |
| [`AGENTS.md`](AGENTS.md) | Index + conventions for agents working inside `docs/`. |
| [`_generated/COUNTS.md`](_generated/COUNTS.md) | Live measured evidence — test count and `src/` coverage % from the last gate run. Never quote a figure in prose; point here. |

## Where the other truth lives

| Question | Authority |
|---|---|
| What does a command do? | `src/bond_cli/dispatch.py` docstrings, then `../README.md` |
| What number may prose state? | `src/bond_cli/manuscript_variables.py` → a `{{TOKEN}}` (and `../data/claim_ledger.yaml`, re-derived by the suite) |
| What is still open? | `../TODO.md` |
| What is the fleet-wide contract? | `vendor/bond-api/` (the frozen protocol) |
