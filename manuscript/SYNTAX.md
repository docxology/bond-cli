# Manuscript Syntax — bond-cli

This file documents the token syntax used in the numbered `0*.md` prose
sections. Only the numbered sections are scanned by the live token
cross-reference test (`tests/test_manuscript_variables.py`); guide files (this
file, `AGENTS.md`, `README.md`) may illustrate literal `{{TOKEN}}` without
being gated.

## {{TOKEN}} protocol

Every `{{TOKEN}}` in a numbered section must be produced by
`src/bond_cli/manuscript_variables.py::build_tokens()`. Current token set:

| Token | Source |
|---|---|
| `{{SUITE_NAME}}` | suite constant |
| `{{PACKAGE_NAME}}` | `manuscript/config.yaml` → `package.name` |
| `{{CODENAME}}` | `manuscript/config.yaml` → `package.codename` |
| `{{FILM_COUNT}}` | coordinator registry `ROSTER` length (= 27) |
| `{{COMMANDS}}` | `dispatch.COMMANDS` joined |

Regenerate the token map with:

```bash
uv run python scripts/z_generate_manuscript_variables.py
# writes output/variables/manuscript_variables.json
```

## Notes

No figures or equations are used in this ops/front-door manuscript; all fleet
values come from injected tokens or are described as outputs of `bond`
commands. Citation syntax is Pandoc `[@ref]` against `references.bib`.
