# Scope and Related Work

## Scope

{{PACKAGE_NAME}} covers the **front-door** surface only: routing verbs to films, missions, status, gadgets, and roster export. It does **not** implement the `MissionProvider` protocol (bond-api), the mission DAG and checkpoint machinery (bond-orchestrator), the registry/ledger/situation room (bond-coordinator), or Q-branch primitives (bond-utilities). A film is never executed outside its own frozen provider; a mission is never orchestrated outside the runner. The one computation the front door does own — overlaying the measured gate manifest onto the registry — is presentational: it changes what is reported, never what is executed.

Explicitly out of scope: interactive or TUI modes, persistent CLI state, network access, credential handling, and any writing to another package's tree. The only file the CLI writes is the roster export the operator asks for with `--output`, plus its own manuscript token map.

## Relationship to the built layers

- **bond-api (THE PROTOCOL)** — the FROZEN `MissionProvider` contract + discovery + `GadgetRegistry` that the front door consumes for `brief`/`recon`/`plan`/`execute`/`debrief` and `gadgets`.
- **bond-coordinator (MISSION CONTROL)** — source of the {{FILM_COUNT}}-film `ROSTER` for `list`/`whois`/`roster-export` and of the `build_status` snapshot for `status`.
- **bond-orchestrator (DAG 00)** — source of the {{MISSION_COUNT}} canned missions and the `MissionRunner` for `run`.
- **bond-utilities (Q-BRANCH)** — transitively loaded by film providers; provenance is recorded by the orchestrator and merely displayed here, never recomputed.

## Related work

The design is conventional by intent. The verb-first grammar and one-verb-per-subparser structure follow the standard-library `argparse` sub-command model [@bethard2009argparse; @pythonargparse]; the exit-code discipline (0 success, non-zero failure, distinct code for usage error) and the commitment to plain, pipeable output follow long-standing Unix utility conventions [@posix2018; @raymond2003unix]. Machine-readable output is JSON per RFC 8259 [@rfc8259], key-sorted for byte-stability. The package version follows Semantic Versioning [@semver2].

The color-safe table is the one place the front door deviates from common practice: many modern CLIs auto-detect a TTY and emit ANSI colour. This one never does. Uniform bytes across a terminal, a pipe, a log file, and test capture are worth more to a fleet whose output is read by other programs than colour is to a human reader — and a table that renders identically everywhere is a table whose tests mean something.

## Related surface within the suite

`bond list` and `bond run` overlap conceptually with the orchestrator's own `list`/`run` CLI; the front door re-exposes them under one grammar rather than relocating the logic. Where the two disagree, the orchestrator is authoritative — it holds the implementation.
