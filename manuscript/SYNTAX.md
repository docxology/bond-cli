# Manuscript Syntax — bond-cli

This file documents the token syntax used in the numbered prose sections
(`00`–`07`, `99`). Only numbered sections are scanned by the live token
cross-reference test (`tests/test_manuscript_variables.py::test_all_manuscript_
tokens_generated`); guide files (this file, `AGENTS.md`, `README.md`) may
illustrate a literal `{{TOKEN}}` without being gated.

## {{TOKEN}} protocol

Every `{{TOKEN}}` in a numbered section must be produced by
`src/bond_cli/manuscript_variables.py::build_tokens()`. **No numeral that
describes this package or the fleet may be typed into prose** — it is written
once, in the function below, derived from the symbol that owns it.

| Token | Source |
|---|---|
| `{{SUITE_NAME}}` | `dispatch.SUITE_NAME` |
| `{{PACKAGE_NAME}}` | `manuscript/config.yaml` → `package.name` |
| `{{CODENAME}}` | `manuscript/config.yaml` → `package.codename` |
| `{{PACKAGE_VERSION}}` | `manuscript/config.yaml` → `paper.version` (falls back to `bond_cli.__version__`) |
| `{{FILM_COUNT}}` | length of the coordinator registry `ROSTER` |
| `{{COMMANDS}}` | `dispatch.COMMANDS`, joined |
| `{{COMMAND_COUNT}}` | length of `dispatch.COMMANDS` |
| `{{JSON_COMMANDS}}` | `dispatch.JSON_COMMANDS`, joined |
| `{{JSON_COMMAND_COUNT}}` | length of `dispatch.JSON_COMMANDS` |
| `{{LAYER_NAMES}}` | `dispatch.DEPENDENCY_LAYERS`, joined (Layer 0 → Layer 3) |
| `{{LAYER_COUNT}}` | length of `dispatch.DEPENDENCY_LAYERS` |
| `{{MISSION_NAMES}}` | `bond_orchestrator.missions.MISSION_NAMES`, joined |
| `{{MISSION_COUNT}}` | length of `MISSION_NAMES` |

Regenerate the token map with:

```bash
uv run python scripts/z_generate_manuscript_variables.py
# writes output/variables/manuscript_variables.json (sorted keys)
```

## What is deliberately NOT a token

Test count and measured coverage % change with every gate run. They live only
in `docs/_generated/COUNTS.md` and are never quoted in manuscript prose — a
frozen token would be a stale measurement dressed as a current one. The
manuscript instead names the gate command that produces them.

## Citations

Pandoc syntax against `references.bib`: `@key` narrative, `[@key]`
parenthetical, `[@key1; @key2]` for several. Every entry in `references.bib` is
a real, checkable source for something this package implements — the argparse
sub-command model, POSIX utility/exit-code conventions, RFC 8259 JSON, and
Semantic Versioning. Do not add an entry you have not verified exists.

## Notes

No figures or equations are used in this ops/front-door manuscript; all fleet
values come from injected tokens or are described as outputs of `bond`
commands.
