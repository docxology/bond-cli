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

The reconciliation results are worth stating separately, because they are the front door's only non-trivial computation. Against a full manifest, every film reports its gate verdict and measured coverage. Against a *partial* manifest, films with rows report measurements and films without rows report `measured: null` while retaining their declared registry status — the two are never conflated. Against a malformed or absent manifest, every command still succeeds and reports the registry view, flagged `measured: false`; the human status prints `min=N/A max=N/A mean=N/A` rather than a literal `None%`. A gate row of `0.0` coverage survives as `0.0`, not as "unknown": a package measured at zero has been measured.

## Determinism

Because every command delegates to a frozen, deterministic layer and prints canonical output — roster order, sorted JSON keys, no wall-clock field anywhere — repeated invocations against an unchanged fleet are byte-identical. That property is a live determinism check on the layers beneath: if a film provider ever became seed-dependent, the front door's own output would stop reproducing.

## Verification

The suite is zero-mock: real providers, real importable film packages written to temporary directories, real gate manifests, and real subprocess invocations of the `scripts/` entry points. The live test count and the measured `src/` coverage percentage are recorded in `docs/_generated/COUNTS.md` and re-measured by the gate `uv run pytest tests/ --cov=src --cov-fail-under=90`; this manuscript deliberately quotes neither figure, so no prose here can go stale against the measurement. Every count it does quote — commands, JSON commands, layers, films, missions — is injected from the registry that defines it, and `data/claim_ledger.yaml` records the same values with their sources, re-derived on every test run.

Two of the claims above are not established by coverage and are therefore pinned by dedicated mutation-checked tests. The exit-code contract (0 iff the underlying execute/debrief/run passed) is implemented as a conditional expression, for which coverage.py emits no branch arc: replacing all three with an unconditional `return 0` left the entire suite green, because no test drove a *failing* mission. It is now driven by real film packages whose `execute` genuinely reports failure, each paired with a passing positive control. The sorted-JSON-keys contract was similarly invisible, since every assertion parsed the output back into a dictionary and discarded key order; it is now asserted against the raw emitted text with each handler's literal construction order pinned, so the assertion cannot pass by coincidence. Both tests were validated by applying the corresponding mutation to `dispatch.py` and confirming they go red; the mutation table is recorded alongside the measurement in `docs/_generated/COUNTS.md`.

A third class of claim is bound by *repeatability* rather than coverage: the determinism guarantees in `06_reproducibility.md`. `status --json` and `roster-export` are invoked twice in separate subprocesses and asserted byte-identical, so a `generated_at: time.time()` field — executed, fully covered, and invisible to coverage — turns the suite read as a determinism regression. The installed `bond` console script (declared in `pyproject.toml`) is exercised in a subprocess and its stdout/exit code asserted equal to the `scripts/bond.py` bootstrap, so a mistyped entry-point target in `pyproject.toml` fails the suite. And the three mechanically checkable `cross_cutting` rules in `manuscript/layer_contract.yaml` — no `infrastructure.*` imports, no wall-clock calls, no terminal-width/environment reads — are asserted against the `src/` and `scripts/` trees, so adding `import time` to `dispatch.py` fails the suite instead of silently falsifying the manuscript.

## The derived surface (bound to the live token map)

The counts this front door reports are never hand-typed into prose. Every one is produced from the registry or tuple that owns it by `src/bond_cli/manuscript_variables.py`, persisted to `output/variables/manuscript_variables.json` by `scripts/z_generate_manuscript_variables.py`, and re-derived on every test run:

| Quantity | Live value |
|---|---|
| Films in the coordinator roster | {{FILM_COUNT}} |
| Front-door subcommands | {{COMMAND_COUNT}} |
| Subcommands accepting `--json` | {{JSON_COMMAND_COUNT}} |
| Built sibling layers delegated to | {{LAYER_COUNT}} |
| Canned orchestrator missions | {{MISSION_COUNT}} |

Each placeholder in the table above is regenerated from the live coordinator `ROSTER`, the orchestrator `MISSION_NAMES`, and `dispatch.COMMANDS` / `JSON_COMMANDS` / `DEPENDENCY_LAYERS`; the values cannot drift from the engines they count. `data/claim_ledger.yaml` records the same five quantities against the same five source symbols, and `tests/test_hardening.py::test_claim_ledger_matches_its_sources` re-derives them.

## Limitations and uncertainty

- **Coverage proves execution, not verification.** A conditional expression (`return 0 if ok else 1`) emits no branch arc, so high line+branch coverage can coexist with a completely unverified non-zero path — that is exactly how both headline contracts were once fully "covered" and entirely unbound. The mitigation is zero-mock contract tests that drive the *failing* path and are mutation-validated (see above), not the coverage number itself.
- **Gadget discovery is best-effort by contract.** A film that fails to import, or whose hook body raises, contributes `0` and emits a diagnostic to stderr — the whole-fleet `bond gadgets` sweep must never be aborted by one broken film. The cost is that gadget coverage for the fleet is only as healthy as the individual films' hooks; the front door reports the exception, it does not repair the film. This package does not install a film's scientific dependencies (e.g. `die_another_day` needs `scipy` and is not importable here), which is correct — the front door depends only on the four built layers — even though it means one film realistically shows as gadget-broken in this environment.
- **`format_table` assumes rectangular input.** A row shorter than the header raises `IndexError`; a row longer is silently truncated to the header width. Every call site builds matched-width rows by construction and no public surface accepts user-supplied rows, so this is an unvalidated internal precondition rather than a reachable defect — but it would be the right place to add a guard if the front door ever grew a free-format command.
- **The measured gate is a snapshot, not a promise.** `status`, `whois`, and `roster-export` report the aggregate gate manifest as last written by the fleet runner. A stale or absent manifest degrades to the declared registry view, flagged `measured: false`; the front door reports the manifest honestly and does not try to re-measure the fleet itself.
- **Determinism is inherited, not re-derived.** The byte-identical repeat runs pass because the layers beneath are deterministic and the front door introduces no randomness, wall-clock, or unordered output. If a film provider ever became seed-dependent, the front door's output would stop reproducing and the determinism tests above would turn red — but they would flag the *symptom*, not pinpoint the film.
