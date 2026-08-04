# Methodology

## Thin dispatch over built layers

`src/bond_cli/dispatch.py` builds an argparse surface whose commands are:

    {{COMMANDS}}

Each handler runs exactly one delegated call. `load_film(slug)` uses the FROZEN `bond_api.discovery.load_provider` contract, searching the fleet directory (`projects/working/bond/<slug>/src`) and bond-api's reference `films/` directory, so a single code path serves both the {{FILM_COUNT}} built films and the reference film. A missing or malformed film raises a `CliError`, which the CLI turns into exit code 1.

## Per-command delegation

- **`list`** — reads the coordinator registry `ROSTER` and prints all {{FILM_COUNT}} films in canonical order (rank, slug, title, year, codename).
- **`brief`/`recon`/`plan`/`execute`/`debrief`** — load the named film's `MissionProvider` and call the corresponding protocol stage. `debrief` runs the full five-stage flow through `bond_api.protocol.run_mission`. `execute`/`debrief` exit 0 iff the outcome reports success.
- **`run`** — resolves a canned mission by name from `bond_orchestrator.missions`, binds each package id to its real film provider via `film_providers.load_film_providers` (falling back to the orchestrator's built-in deterministic provider when a film is not built), executes it with the `MissionRunner`, prints the consolidated debrief, and exits 0 iff every verdict passes.
- **`status`** — reads the aggregate gate manifest written by the fleet gate
  runner (`output/aggregate/gate_manifest.json`) when present, reconciles each
  film's measured status/coverage onto the coordinator registry, and renders
  the suite snapshot (counts by status, coverage summary, blocked packages).
  Without a manifest it falls back to the honest pre-measurement registry.
- **`gadgets`** — builds a `bond_api.GadgetRegistry` by discovering each
  film's gadgets across every fleet convention (`register_gadgets(registry)`,
  zero-arg `register_gadgets()`, module-level `GADGETS` dict or factory, or
  provider-bound registration at construction) and prints the registered
  gadget names (for one film or the whole fleet).
- **`missions`** — lists the orchestrator's canned missions and each mission's
  package chain.
- **`whois <film>`** — prints a film's registry identity (rank, film, year,
  codename, status, coverage, concepts), whether its provider module is built
  on disk, and its measured gate state when the manifest exists.
- **`roster-export`** — exports the fleet roster as key-sorted JSON (the
  measured roster when the manifest exists, else the plain registry), to
  stdout or to a file with `--output`.

## JSON output and color-safe tables

`list`, `status`, `missions`, and `whois` accept `--json` for
machine-readable output; `roster-export` is JSON by construction. Human tables
are rendered by `src/bond_cli/table.py::format_table` with fixed-width column
padding only — never ANSI escape codes — so output is byte-identical in a
terminal, a pipe, a log file, and test capture (the color-safe contract).

## Determinism and exit codes

Film providers are fixed-seed and side-effect free, output ordering is canonical (roster order, sorted result keys), and no command persists wall-clock data. Exit codes: 0 success, 1 command failure (unknown film, non-passing execute/debrief, failed run, empty lookup), 2 argparse misuse.
