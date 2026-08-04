# docs/ — Agent-Facing Documentation Hub

Technical guide for `projects/working/bond/bond-cli/docs/` — the operational
rulebook for agents working inside the front door. Every document here is a
hard constraint, not a suggestion.

| File | Purpose |
|---|---|
| `README.md` | Navigation + audience entry points |
| `AGENTS.md` | This index |
| `agent_instructions.md` | Behavioral rules (read-first priority) |
| `architecture.md` | Dispatch surface + layer boundaries |
| `testing_philosophy.md` | Zero-mock policy; coverage mechanics; live counts in `_generated/COUNTS.md` |

## Key conventions

**Read-first protocol.** AI agents must read `agent_instructions.md` before
modifying any project file. Skipping it is the most common source of errors —
agents who skip it tend to implement logic in `dispatch.py` instead of
delegating to the built layers (violating Rule 1 of `architecture.md`), or
mocks in tests.

**Delegation over implementation.** The front door owns arg parsing, provider
loading, output formatting, and exit codes — nothing else.

**Zero mocks.** No `unittest.mock`, `MagicMock`, `@patch`, or `create_autospec`
in `tests/`. Real film providers (the light reference film `sable`, a real
fleet film for gadgets/missions) plus real subprocess smoke.

## Reading order

1. `agent_instructions.md` — start here.
2. `architecture.md` — layer boundaries before touching any file.
3. `testing_philosophy.md` — zero-mock constraint + coverage mechanics.
