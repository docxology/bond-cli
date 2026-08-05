# Manuscript — bond-cli (THE FRONT DOOR)

The publishable narrative for the PROJECT BOND terminal front door.

## Sections

`00_abstract.md`, `01_introduction.md`, `02_methodology.md`, `03_results.md`,
`04_conclusion.md`, `05_experimental_setup.md`, `06_reproducibility.md`,
`07_scope_and_related_work.md`, `99_references.md` — plus `preamble.md` (LaTeX
injections), `config.yaml` (identity, authors, render targets),
`references.bib` (real external sources), `SYNTAX.md` (token + citation rules),
`AGENTS.md` (editing rules), and `layer_contract.yaml` (module boundaries).

## The rule that governs every edit

**No number describing this package or the fleet is typed into prose.** Each
arrives as a `{{TOKEN}}` produced by
`src/bond_cli/manuscript_variables.py::build_tokens()` from the symbol that
owns it: `dispatch.COMMANDS` / `JSON_COMMANDS` / `DEPENDENCY_LAYERS`, the
coordinator `ROSTER`, the orchestrator's `MISSION_NAMES`, and
`config.yaml`'s `package:` / `paper:` blocks. The full table is in
[`SYNTAX.md`](SYNTAX.md), and
`tests/test_manuscript_variables.py` fails if any token used here is not
generated.

Volatile measurements (test count, coverage %) are deliberately **not** tokens
— they live only in `../docs/_generated/COUNTS.md`, and the prose names the
gate command instead.

## Regenerate tokens

```bash
uv run python scripts/z_generate_manuscript_variables.py
# → output/variables/manuscript_variables.json (sorted keys, deterministic)
```
