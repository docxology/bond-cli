# docs/ — Agent-Facing Documentation Hub

Technical guide for `projects/working/bond/bond-cli/docs/` — the operational
rulebook for agents working inside the front door. Every document here is a
hard constraint, not a suggestion.

| File | Purpose |
|---|---|
| `README.md` | Navigation + where each kind of truth lives |
| `AGENTS.md` | This index |
| `agent_instructions.md` | The nine behavioural rules (read-first priority) |
| `architecture.md` | Module-by-module design, registries, reconciliation, gadget harvest, consumed protocol surface, exit codes |
| `testing_philosophy.md` | Zero-mock policy; per-file coverage map; ambient-state pinning; coverage mechanics |
| `_generated/COUNTS.md` | Live measured test count + `src/` coverage % |

## Key conventions

**Read-first protocol.** Read `agent_instructions.md` before modifying any
project file. Agents who skip it tend to implement logic in `dispatch.py`
instead of delegating to the built layers (violating Rule 1), or to reach for a
mock in `tests/` (violating Rule 4).

**Delegation over implementation.** The front door owns arg parsing, provider
loading, output formatting, and exit codes — nothing else. `bond-cli` ships no
`mission.py`; it consumes the frozen `MissionProvider` contract and must never
alter it.

**Zero mocks.** No `unittest.mock`, `MagicMock`, `@patch`, or
`create_autospec` in `tests/`. Real film providers, real tmp film packages,
real gate manifests, real subprocesses.

**No hand-authored numbers.** Any count that appears in the manuscript arrives
as a `{{TOKEN}}` from `src/bond_cli/manuscript_variables.py`; any count in
`data/claim_ledger.yaml` is re-derived from its named source by the suite. When
a doc needs the current test count or coverage %, link `_generated/COUNTS.md`
rather than copying the figure.

**Doc↔code sync.** A new command means four edits: `build_parser()` +
`COMMANDS`, a `cmd_*` handler, `architecture.md`, and the manuscript
methodology/results sections. A new derived quantity means a token, a ledger
row, and a test that re-derives it.

## Reading order

1. `agent_instructions.md` — start here.
2. `architecture.md` — layer boundaries and module responsibilities before
   touching any file.
3. `testing_philosophy.md` — the zero-mock constraint, ambient-state pinning,
   and the coverage gate.
