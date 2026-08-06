# Methodology

## Thin dispatch over built layers

`src/bond_cli/dispatch.py` builds an argparse surface whose {{COMMAND_COUNT}} commands are:

    {{COMMANDS}}

That tuple, `COMMANDS`, is the single source of the command surface: it drives help ordering, the manuscript token above, and the ledger row that the test suite re-derives. Two sibling tuples do the same job for the rest of the surface — `JSON_COMMANDS` ({{JSON_COMMANDS}}) names the commands accepting `--json`, and `DEPENDENCY_LAYERS` names the {{LAYER_COUNT}} built siblings ({{LAYER_NAMES}}) in dependency order. No count in this manuscript is written by hand; each is derived from the tuple or registry it describes.

`load_film(slug)` uses the FROZEN `bond_api.discovery.load_provider` contract, searching the fleet directory (`projects/working/bond/<slug>/src`) and bond-api's reference `films/` directory, so a single code path serves both the {{FILM_COUNT}} built films and the reference film. Only directories that exist are passed to discovery, because the contract validates every search path it is given. A missing or malformed film raises a `CliError`, which the CLI turns into exit code 1.

## Per-command delegation

- **`list`** — reads the coordinator registry `ROSTER` and prints all {{FILM_COUNT}} films in canonical order (rank, slug, title, year, codename).
- **`brief`/`recon`/`plan`/`execute`/`debrief`** — load the named film's `MissionProvider` and call the corresponding protocol stage. `debrief` runs the full five-stage flow through `bond_api.protocol.run_mission`. `execute`/`debrief` exit 0 iff the outcome reports success.
- **`run`** — resolves a canned mission by name from `bond_orchestrator.missions` (there are {{MISSION_COUNT}}: {{MISSION_NAMES}}), binds each package id to its real film provider via `film_providers.load_film_providers` (falling back to the orchestrator's built-in deterministic provider when a film is not built), executes it with the `MissionRunner`, prints the consolidated debrief, and exits 0 iff every verdict passes.
- **`status`** — reads the aggregate gate manifest written by the fleet gate runner (`output/aggregate/gate_manifest.json`) when present, reconciles each film's measured status/coverage onto the coordinator registry, and renders the suite snapshot (counts by status, coverage summary, blocked packages). Without a manifest it falls back to the honest pre-measurement registry.
- **`gadgets`** — builds a `bond_api.GadgetRegistry` by discovering each film's
  gadgets across every fleet convention (`register_gadgets(registry)`, zero-arg
  `register_gadgets()`, module-level `GADGETS` dict or factory, a module-level
  `GadgetRegistry`, or provider-bound registration at construction), and prints
  the registered gadget names, for one film or the whole fleet. The three
  single-film outcomes are now distinguished: an **unknown slug** raises a
  `CliError` (stderr, exit 1) with the same "not available" wording as
  `brief`/`plan`; a **built film whose import or hook raises** is diagnosed to
  stderr (naming the exception) while still contributing `0` so a whole-fleet
  sweep never aborts; and a **clean film with no gadgets** keeps the
  empty-lookup message. All failure text goes to **stderr**, so a caller piping
  stdout into a parser never receives error text as data.
- **`missions`** — lists the orchestrator's {{MISSION_COUNT}} canned missions and each mission's package chain.
- **`whois <film>`** — prints a film's registry identity (rank, film, year, codename, status, coverage, concepts), whether its provider module is built on disk, and its measured gate state when the manifest carries a row for it.
- **`roster-export`** — exports the fleet roster as key-sorted JSON (the measured roster when the manifest exists, else the plain registry), to stdout or to a file with `--output`.

## Reconciling measurement onto the registry

The registry records what each film package *declares*; the aggregate gate manifest records what the fleet gate *measured*. Three functions keep the two apart and then combine them honestly.

`_manifest_rows()` reads the manifest into rows keyed by slug and returns nothing at all when the file is absent, unreadable, or malformed — a broken manifest degrades the front door to registry-only reporting rather than failing a command. `_measured_coverage(row)` extracts a coverage percentage, treating a measured `0.0` as a real measurement (only a missing or non-numeric value is unknown; booleans are rejected, since `bool` subclasses `int` in Python). `_reconcile(record, row)` overlays one row onto one registry record, marking the package ready iff its gate returned `0` and red otherwise.

Composing these over the roster gives the measured view. A film with no row keeps its registry record untouched, because a manifest may cover only part of the fleet — and `whois` reports a measurement for such a film as `null` rather than echoing the registry's declared status as though it had been observed. The distinction matters: a front door that reports intentions as measurements is worse than one that reports nothing.

## JSON output and color-safe tables

{{JSON_COMMANDS}} accept `--json` for machine-readable output; `roster-export` is JSON by construction and therefore takes no flag. All JSON is emitted with sorted keys and contains no wall-clock field, so two runs against an unchanged fleet are byte-identical.

Human tables are rendered by `src/bond_cli/table.py::format_table` with fixed-width column padding only — never ANSI escape codes. That is the color-safe contract: identical bytes in a terminal, a pipe, a log file, and test capture, and no escape sequences leaking into anything a downstream tool parses. Widths derive from the header and cell text; no cell is truncated or wrapped, so no information is lost to formatting.

## Determinism and exit codes

Film providers are fixed-seed and side-effect free, output ordering is canonical (roster order, sorted result keys), and no command persists wall-clock data. Exit codes: 0 success, 1 command failure (unknown film, non-passing execute/debrief/run, empty or broken gadget lookup), 2 argparse misuse and unknown mission name. `main()` catches only its own `CliError`; any other exception is a genuine defect and propagates rather than being flattened into a misleading exit code.

Gadget-hook arity is read from `inspect.signature` [@pythoninspect] rather than guessed by catching `TypeError` on a registry call. That closes a subtle failure mode: a `register_gadgets(registry)` hook whose *body* raised `TypeError` was previously re-invoked as a zero-arg hook, escaping a second, misleading `TypeError: missing 1 required positional argument` that aborted the whole-fleet sweep and masked the film's real defect. With arity from the signature, a hook-body exception is caught per-film, diagnosed to stderr, and the sweep continues.
