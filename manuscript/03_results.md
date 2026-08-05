# Results

## The delivered surface

{{PACKAGE_NAME}} exposes {{COMMAND_COUNT}} commands over the {{LAYER_COUNT}} built layers, all produced by real delegation:

- **`bond list`** prints the full {{FILM_COUNT}}-film roster from the coordinator registry, in canonical order (`--json` for rows).
- **`bond brief <film>`** / **`bond recon <film>`** / **`bond plan <film>`** / **`bond execute <film>`** / **`bond debrief <film>`** exercise a real film provider end-to-end: the brief's identity, the recon's findings, the plan's steps, the executed outcome with provenance, and the debrief's lessons.
- **`bond run <mission>`** executes any of the {{MISSION_COUNT}} canned orchestrator missions ({{MISSION_NAMES}}) over the real film providers, with deterministic fallback for films not yet built, and prints the consolidated debrief; exit 0 iff all verdicts pass.
- **`bond status`** reports the suite snapshot — counts by status, the coverage summary, blocked packages — reconciled against the measured gate manifest when present (`--json` for a key-sorted snapshot).
- **`bond gadgets`** lists which films register gadgets and the gadget names each exposes, across every fleet registration convention.
- **`bond missions`** lists the canned missions and their package chains (`--json` for rows).
- **`bond whois <film>`** prints one film's registry identity, built-on-disk state, and measured gate state (`--json` for a payload).
- **`bond roster-export`** emits the fleet roster as key-sorted JSON (stdout or `--output FILE`).

Of these, {{JSON_COMMAND_COUNT}} accept `--json` ({{JSON_COMMANDS}}); `roster-export` is JSON by construction.

## Measurement is distinguishable from declaration

The reconciliation results are worth stating separately, because they are the front door's only non-trivial computation. Against a full manifest, every film reports its gate verdict and measured coverage. Against a *partial* manifest, films with rows report measurements and films without rows report `measured: null` while retaining their declared registry status — the two are never conflated. Against a malformed or absent manifest, every command still succeeds and reports the registry view, flagged `measured: false`. A gate row of `0.0` coverage survives as `0.0`, not as "unknown": a package measured at zero has been measured.

## Determinism

Because every command delegates to a frozen, deterministic layer and prints canonical output — roster order, sorted JSON keys, no wall-clock field anywhere — repeated invocations against an unchanged fleet are byte-identical. That property is a live determinism check on the layers beneath: if a film provider ever became seed-dependent, the front door's own output would stop reproducing.

## Verification

The suite is zero-mock: real providers, real importable film packages written to temporary directories, real gate manifests, and real subprocess invocations of the `scripts/` entry points. The live test count and the measured `src/` coverage percentage are recorded in `docs/_generated/COUNTS.md` and re-measured by the gate `uv run pytest tests/ --cov=src --cov-fail-under=90`; this manuscript deliberately quotes neither figure, so no prose here can go stale against the measurement. Every count it does quote — commands, JSON commands, layers, films, missions — is injected from the registry that defines it, and `data/claim_ledger.yaml` records the same values with their sources, re-derived on every test run.
