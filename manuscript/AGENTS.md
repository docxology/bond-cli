---
title: "Manuscript directory: bond-cli"
type: "manuscript_guide"
version: "3.0.0"
---

# Manuscript (`projects/working/bond/bond-cli/manuscript/`)

Agent rules for this package live in [`../docs/agent_instructions.md`](../docs/agent_instructions.md).
This file covers manuscript-specific editing: the `{{TOKEN}}` protocol and the
section inventory.

## File inventory

| File | Role |
|---|---|
| `00_abstract.md` | Abstract; front-door role summary |
| `01_introduction.md` | Fleet context; {{PACKAGE_NAME}} role |
| `02_methodology.md` | Dispatch design + per-command delegation |
| `03_results.md` | Observable surface of the `bond` commands |
| `04_conclusion.md` | Thinness, correctness, determinism |
| `05_experimental_setup.md` | Runtime + deps + entry points + toolchain |
| `06_reproducibility.md` | Determinism contract |
| `07_scope_and_related_work.md` | Scope + relationship to the four layers |
| `99_references.md` | Bibliography |
| `config.yaml` | Identity (`package.name`/`package.codename`) + authors + publication |
| `preamble.md` | LaTeX injections (PDF render) |
| `references.bib` | BibTeX entries |
| `SYNTAX.md` | Token/citation syntax |
| `README.md` | Human quick reference |

## {{TOKEN}} protocol

Fleet values are injected tokens (`{{FILM_COUNT}}`, `{{COMMANDS}}`, …) or
described as *measured* outputs of `bond` commands — never hand-authored. To
add a token: add a key to `build_tokens()` in
`src/bond_cli/manuscript_variables.py`, use it in a numbered section, and the
live cross-reference test will confirm it resolves.

Run `uv run python scripts/z_generate_manuscript_variables.py` after any
`config.yaml` identity change to regenerate
`output/variables/manuscript_variables.json`.
