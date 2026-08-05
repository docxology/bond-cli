---
title: "Manuscript directory: bond-cli"
type: "manuscript_guide"
version: "3.0.0"
---

# Manuscript (`projects/working/bond/bond-cli/manuscript/`)

Agent rules for this package live in [`../docs/agent_instructions.md`](../docs/agent_instructions.md).
This file covers manuscript-specific editing: the section inventory, the
`{{TOKEN}}` protocol, and the citation bar.

## File inventory

| File | Role |
|---|---|
| `00_abstract.md` | Abstract: front-door role, command surface, what the deepened layer adds |
| `01_introduction.md` | Fleet context, the interface problem the front door solves, the two design commitments |
| `02_methodology.md` | Dispatch design, per-command delegation, gate-manifest reconciliation, JSON + color-safe tables, determinism/exit codes |
| `03_results.md` | The delivered surface, measurement-vs-declaration behaviour, determinism, verification |
| `04_conclusion.md` | Thinness, honesty about measurement, why a boring front door is the right one |
| `05_experimental_setup.md` | Runtime, entry points, discovery, measured state, toolchain, gates |
| `06_reproducibility.md` | Determinism contract, the no-hand-authored-numbers rule, clean-checkout recipe |
| `07_scope_and_related_work.md` | Scope and non-scope, relationship to the built layers, external related work |
| `99_references.md` | In-suite packages + external cited sources |
| `config.yaml` | Identity (`package:`), paper metadata (`paper:`), authors, keywords, render targets |
| `preamble.md` | LaTeX injections (PDF render) |
| `references.bib` | BibTeX entries — real, checkable sources only |
| `SYNTAX.md` | Token table + citation syntax |
| `README.md` | Human quick reference |
| `layer_contract.yaml` | Module boundary rules mirrored from `../docs/architecture.md` |

## {{TOKEN}} protocol

Fleet and surface values are injected tokens — never hand-authored. To add one:
add a key to `build_tokens()` in `src/bond_cli/manuscript_variables.py`, derive
it from the symbol that owns the fact (never a literal), use it in a numbered
section, and let the live cross-reference test confirm it resolves. If the new
value is countable, add a row to `data/claim_ledger.yaml` too; the suite
re-derives every ledger row from its named source.

Volatile measurements (test count, coverage %) must **not** become tokens. They
belong in `../docs/_generated/COUNTS.md`; prose names the gate that produces
them.

Run `uv run python scripts/z_generate_manuscript_variables.py` after any
`config.yaml` identity/version change to regenerate
`output/variables/manuscript_variables.json`.

## Citation bar

Pandoc `[@key]` against `references.bib`. Every entry must be a real,
verifiable publication or standard that this package actually follows — PEP
389 and the argparse docs for the sub-command grammar, POSIX Chapter 12 and
Raymond for the exit-code/plain-output conventions, RFC 8259 for `--json`,
SemVer for the version string. If you cannot verify an entry exists, delete it
rather than ship it.
