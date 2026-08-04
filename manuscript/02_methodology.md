# Methodology

## Thin dispatch over built layers

`src/bond_cli/dispatch.py` builds an argparse surface whose commands are:

    {{COMMANDS}}

Each handler runs exactly one delegated call. `load_film(slug)` uses the FROZEN `bond_api.discovery.load_provider` contract, searching the fleet directory (`projects/working/bond/<slug>/src`) and bond-api's reference `films/` directory, so a single code path serves both the {{FILM_COUNT}} built films and the reference film. A missing or malformed film raises a `CliError`, which the CLI turns into exit code 1.

## Per-command delegation

- **`list`** — reads the coordinator registry `ROSTER` and prints all {{FILM_COUNT}} films in canonical order (rank, slug, title, year, codename).
- **`brief`/`recon`/`plan`/`execute`/`debrief`** — load the named film's `MissionProvider` and call the corresponding protocol stage. `debrief` runs the full five-stage flow through `bond_api.protocol.run_mission`. `execute`/`debrief` exit 0 iff the outcome reports success.
- **`run`** — resolves a canned mission by name from `bond_orchestrator.missions`, binds each package id to its real film provider via `film_providers.load_film_providers` (falling back to the orchestrator's built-in deterministic provider when a film is not built), executes it with the `MissionRunner`, prints the consolidated debrief, and exits 0 iff every verdict passes.
- **`status`** — calls `bond_coordinator.status.build_status` and prints the deterministic suite snapshot (counts by status, coverage summary, blocked packages).
- **`gadgets`** — builds a `bond_api.GadgetRegistry` by discovering each film's `register_gadgets` entry and prints the registered gadget names (for one film or the whole fleet).

## Determinism and exit codes

Film providers are fixed-seed and side-effect free, output ordering is canonical (roster order, sorted result keys), and no command persists wall-clock data. Exit codes: 0 success, 1 command failure (unknown film, non-passing execute/debrief, failed run, empty lookup), 2 argparse misuse.
