# Results

The front door's observable surface, all produced by real delegation to the built layers:

- **`bond list`** prints the full {{FILM_COUNT}}-film roster from the coordinator registry, in canonical order.
- **`bond brief <film>`** / **`bond recon <film>`** / **`bond plan <film>`** / **`bond execute <film>`** / **`bond debrief <film>`** exercise a real film provider end-to-end: the brief's identity, the recon's findings, the plan's steps, the executed outcome with provenance, and the debrief's lessons.
- **`bond run <mission>`** executes a canned orchestrator mission over the real film providers (with deterministic fallback) and prints the consolidated debrief; exit 0 iff all verdicts pass.
- **`bond status`** reports the coordinator's suite snapshot: counts by package status and the measured-coverage summary.
- **`bond gadgets`** lists which films register gadgets and the gadget names each exposes.

Because every command delegates to a frozen, deterministic layer and prints canonical output, repeated invocations against an unchanged fleet are byte-identical — a live determinism check at the front door.
