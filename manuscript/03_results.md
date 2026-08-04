# Results

The front door's observable surface, all produced by real delegation to the built layers:

- **`bond list`** prints the full {{FILM_COUNT}}-film roster from the coordinator registry, in canonical order (`--json` for rows).
- **`bond brief <film>`** / **`bond recon <film>`** / **`bond plan <film>`** / **`bond execute <film>`** / **`bond debrief <film>`** exercise a real film provider end-to-end: the brief's identity, the recon's findings, the plan's steps, the executed outcome with provenance, and the debrief's lessons.
- **`bond run <mission>`** executes a canned orchestrator mission over the real film providers (with deterministic fallback) and prints the consolidated debrief; exit 0 iff all verdicts pass.
- **`bond status`** reports the suite snapshot — counts by status, the measured-coverage summary, blocked packages — reconciled against the measured gate manifest when present (`--json` for a key-sorted snapshot).
- **`bond gadgets`** lists which films register gadgets and the gadget names each exposes, across every fleet registration convention.
- **`bond missions`** lists the canned orchestrator missions and their package chains (`--json` for rows).
- **`bond whois <film>`** prints one film's registry identity, built-on-disk state, and measured gate state (`--json` for a payload).
- **`bond roster-export`** emits the fleet roster as key-sorted JSON (stdout or `--output FILE`).

Because every command delegates to a frozen, deterministic layer and prints canonical output, repeated invocations against an unchanged fleet are byte-identical — a live determinism check at the front door.
