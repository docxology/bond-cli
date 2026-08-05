# Architecture — bond-cli (THE FRONT DOOR)

`bond-cli` is Layer 4 of PROJECT BOND: the single terminal surface an operator
talks to. It owns four things and nothing else — **argument shaping**,
**provider/registry loading**, **output formatting**, and **exit-code
mapping**. Every substantive computation happens in a built sibling layer.

## Shape

```
scripts/bond.py ─┐
                 ├─→ bond_cli.dispatch.main(argv) ─→ handler ─→ built layer ─→ int
console `bond` ──┘        │                             │
                          │                             ├─ bond_api         (protocol, discovery, GadgetRegistry)
                          ├─ build_parser()              ├─ bond_coordinator (ROSTER, build_status)
                          ├─ _handlers()                 └─ bond_orchestrator (missions, MissionRunner)
                          └─ CliError → stderr, exit 1
```

The arrow is strictly one-way. No layer imports `bond_cli`; `bond_cli` imports
no `infrastructure.*`.

## Modules in `src/bond_cli/`

| Module | What it computes |
|---|---|
| `__init__.py` | Package identity. Assigns `__version__` **before** importing submodules, because `manuscript_variables` reads it as the `{{PACKAGE_VERSION}}` fallback during package init. Re-exports `dispatch` and `manuscript_variables`. |
| `dispatch.py` | The whole front door: the command registries, twelve `cmd_*` handlers, film loading, gate-manifest reconciliation, tolerant gadget harvesting, the argparse surface, and `main() -> int`. |
| `table.py` | `format_table(headers, rows) -> str` — fixed-width column alignment with **no ANSI**. Widths derive from header + cell text; columns join on two spaces; nothing is truncated or wrapped. Byte-identical for identical input (no terminal probing, no environment reads). |
| `manuscript_variables.py` | The `{{TOKEN}}` map: identity from `manuscript/config.yaml`, fleet counts from the coordinator/orchestrator registries, surface counts from `dispatch`'s own tuples. Persists to `output/variables/manuscript_variables.json` (sorted keys). |

### `dispatch.py` in detail

**Registries — the single source of every surface number.**

| Constant | Contents | Feeds |
|---|---|---|
| `COMMANDS` | the twelve verbs, in help order | `--help` ordering, `{{COMMANDS}}`, `{{COMMAND_COUNT}}` |
| `JSON_COMMANDS` | verbs that accept `--json` (`roster-export` is JSON by construction, so it is deliberately absent) | `{{JSON_COMMANDS}}`, `{{JSON_COMMAND_COUNT}}` |
| `DEPENDENCY_LAYERS` | the built siblings, Layer 0 → Layer 3 | `{{LAYER_NAMES}}`, `{{LAYER_COUNT}}` |
| `GADGET_FILM_SLUGS` | override hook for the whole-fleet gadget sweep (empty ⇒ roster + reference film) | fast deterministic tests |
| `BOND_ROOT` / `GATE_MANIFEST` | fleet workspace root; the aggregate gate-manifest path | `status` / `whois` / `roster-export` |

**Film loading.** `_film_search_paths(slug)` returns only *existing* directories
— `<BOND_ROOT>/<slug>/src` (fleet layout) and `<BOND_ROOT>/bond-api/films`
(reference layout) — because `bond_api.discovery` validates every path it is
given. `load_film(slug)` calls the frozen `load_provider` and converts a
`DiscoveryError` into `CliError` (exit 1).

**Gate-manifest reconciliation** — three small functions, each independently
tested:

1. `_manifest_rows()` → `{slug: row}` or `None`. Absent, unreadable, or
   malformed manifest ⇒ `None`. It never raises; a broken manifest degrades the
   front door to registry-only reporting rather than failing a command.
2. `_measured_coverage(row)` → `float | None`. A measured `0.0` is a real
   measurement and is preserved; only a missing or non-numeric value (booleans
   included, since `bool` is an `int` subclass) becomes `None`.
3. `_reconcile(record, row)` → a `replace()`d registry record whose status is
   `READY` iff `rc == 0`, else `RED`.

`_measured_roster()` composes them over the whole `ROSTER`, leaving records
untouched where the manifest has no row. `cmd_whois` reports `measured` **only**
for a film that actually has a row — a film missing from a partial manifest
reports `null`, never registry defaults dressed up as a measurement.

**Tolerant gadget harvest.** `register_film_gadgets(registry, slug)` imports
`<slug>.mission` with the film's `src/` temporarily on `sys.path` (always
removed in a `finally`) and accepts every convention the fleet actually uses:

| Convention | Handling |
|---|---|
| `register_gadgets(registry)` | called with the registry |
| `register_gadgets()` (zero-arg) | `TypeError` retry, then the module-level `GADGETS` is harvested |
| module `GADGETS` dict | registered directly |
| module `GADGETS` callable factory | invoked, then registered |
| module `GADGETS` = `bond_api.GadgetRegistry` | copied entry-by-entry via `lookup` |
| gadgets bound in `MissionProvider.__init__` | provider constructed when the shelf looks empty, then the module re-read |

A film that raises on import contributes `0`. That broad `except Exception` is
deliberate and is the documented contract: a whole-fleet `bond gadgets` sweep
must never be aborted by one unbuilt or broken film. It is bounded — it wraps
the import only, and the "broken film contributes 0" path is asserted by a test
against a real module that raises on import.

## Relationship to the frozen `MissionProvider` contract

**bond-cli ships no `mission.py` and implements no `MissionProvider`.** It is
the fleet's pure *consumer* of that protocol; the providers live in the film
packages and in bond-api's reference film. The front door touches the frozen
surface at exactly these points:

| Command | Frozen surface used |
|---|---|
| `brief` | `provider.brief() -> MissionBrief` (`film`, `codename`, `objectives`, optional `assets`/`constraints`) |
| `recon` | `provider.recon(ReconRequest(goal=...)) -> ReconReport` (`findings`) |
| `plan` | `provider.plan(brief) -> MissionPlan` (`steps`) |
| `execute` | `provider.execute(plan) -> MissionOutcome` (`success`, `results`, `provenance`) |
| `debrief` | `bond_api.protocol.run_mission(provider, request) -> Debrief` (all five stages) |
| `gadgets` | `bond_api.registry.GadgetRegistry` (`register`, `lookup`, `gadgets_for`, `films`) |

Because the CLI reads only these fields, a film package may deepen its internals
freely and the front door needs no change. Conversely, **the front door must
never add a stage, rename a field, or reinterpret `success`** — that would fork
the protocol for the whole fleet.

`bond run` is the one command that does not touch a provider directly: it
resolves a mission from `bond_orchestrator.missions`, binds each package id to
its real film adapter via `film_providers.load_film_providers`, falls back to
the orchestrator's built-in deterministic provider when a film is not built on
disk, and hands the whole set to `MissionRunner`.

## Exit-code contract

| Code | Meaning |
|---|---|
| `0` | command succeeded |
| `1` | command failure — unknown/malformed film (`CliError`), a non-passing `execute`/`debrief`/`run`, an empty gadget lookup |
| `2` | argparse misuse, and an unknown mission name for `bond run` |

`main()` catches only `CliError`; anything else is a genuine bug and propagates
with a traceback rather than being swallowed into a misleading exit code.

## Forbidden patterns

| Forbidden | Instead |
|---|---|
| Import `infrastructure.*` | The front door is standalone over the four layers |
| Implement mission math in `dispatch.py` | Delegate to a film's provider |
| Re-hardcode the roster | Read `bond_coordinator.registry.ROSTER` |
| Hand-author a count in prose or in `data/claim_ledger.yaml` | Derive it from a registry and expose it as a `{{TOKEN}}` |
| Emit ANSI colour | `table.format_table` — the color-safe contract |
| Mock a provider in tests | Use a real film (`sable`/`goldfinger`/`skyfall`) or a real tmp package |

## Adding a command

1. Add the verb to `build_parser()` **and** to `COMMANDS` (and to
   `JSON_COMMANDS` if it takes `--json`).
2. Add `cmd_<verb>(args) -> int` and wire it into `_handlers()`.
3. Test in-process (`dispatch.main([...])` + `capsys`); add subprocess smoke if
   it is an operator-facing entry point.
4. If it introduces a countable fact, add the derivation to
   `manuscript_variables.build_tokens` and a row to `data/claim_ledger.yaml` —
   `tests/test_hardening.py` re-derives every ledger row from its named source,
   so a stale number fails the suite instead of shipping.
