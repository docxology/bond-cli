# Scope and Related Work

## Scope

{{PACKAGE_NAME}} covers the **front-door** surface only: routing verbs to films, missions, status, and gadgets. It does **not** implement the `MissionProvider` protocol (bond-api), the mission DAG/checkpoint machinery (bond-orchestrator), the registry/ledger/situation room (bond-coordinator), or Q-branch primitives (bond-utilities). A film is never executed outside its own frozen provider; a mission is never orchestrated outside the runner.

## Relationship to the built layers

- **bond-api (THE PROTOCOL)** — the FROZEN `MissionProvider` contract + discovery + `GadgetRegistry` that the front door consumes for `brief`/`recon`/`plan`/`execute`/`debrief` and `gadgets`.
- **bond-coordinator (MISSION CONTROL)** — source of the {{FILM_COUNT}}-film `ROSTER` for `list` and of the `build_status` snapshot for `status`.
- **bond-orchestrator (DAG 00)** — source of canned missions and the `MissionRunner` for `run`.
- **bond-utilities (Q-BRANCH)** — transitively loaded by film providers; provenance is recorded by the orchestrator, not duplicated here.

## Related surface

`bond list` and `bond run` overlap conceptually with the orchestrator's own `list`/`run` CLI; the front door re-exposes them under one grammar rather than relocating the logic.
