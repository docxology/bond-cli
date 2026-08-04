# Architecture — bond-cli

## Shape

`bond-cli` is a thin dispatch front door. The dependency arrow is one-way:

```
scripts/bond.py  →  bond_cli.dispatch.main(argv)  →  built layers
                    (argparse, load_film, format)     (protocol/registry/missions)
```

No logic is owned here except: argument parsing, film-provider loading, output
formatting, and exit-code mapping.

## Modules

| Module | Responsibility |
|---|---|
| `src/bond_cli/dispatch.py` | argparse surface; `main -> int`; per-command handlers; `load_film`; `register_film_gadgets`; `_resolve_provider` |
| `src/bond_cli/manuscript_variables.py` | `{{TOKEN}}` map from `manuscript/config.yaml` + coordinator registry |
| `scripts/bond.py` | sys.path bootstrap → `dispatch.main` |
| `scripts/z_generate_manuscript_variables.py` | token hydration → `output/variables/` |

## Depends-on (all built, path sources)

- **bond-api** — `discovery.load_provider`, `protocol` types + `run_mission`,
  `registry.GadgetRegistry`.
- **bond-coordinator** — `registry.ROSTER`, `status.build_status`,
  `types.PackageStatus`.
- **bond-orchestrator** — `missions.get_mission`/`UnknownMissionError`,
  `runner.MissionRunner`, `film_providers.load_film_providers`,
  `providers.get_provider`.
- **bond-utilities** — loaded transitively by film providers.

## Forbidden patterns

| Forbidden | Instead |
|---|---|
| Import `infrastructure.*` | Don't — the front door is standalone over the four layers |
| Implement mission math in `dispatch.py` | Delegate to a film's provider |
| Dispatch films by re-hardcoding the roster | `bond list` reads the coordinator `ROSTER` |
| Mock a provider in tests | Use a real film (sable/skyfall) or subprocess |

## Adding a command

1. Add the verb to the `sub` parsers in `build_parser()` and to `COMMANDS`.
2. Add a `cmd_<verb>(args) -> int` handler to `_handlers()`.
3. Test it in-process (`dispatch.main([...])` with `capsys`) and, if it's a
   CLI smoke surface, via `scripts/bond.py`.
