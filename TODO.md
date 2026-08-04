# bond-cli TODO

Forward-only backlog for the terminal front door (PROJECT BOND · THE FRONT
DOOR). No closed-out archaeology; keep it pointed.

## Phase-3 scope (this build)

- [x] `src/bond_cli/dispatch.py` — verb-first argparse front door: `list`,
      `brief`, `recon`, `plan`, `execute`, `debrief`, `run`, `status`,
      `gadgets`; thin delegation to the four built layers.
- [x] `scripts/bond.py` + console script `bond` — thin entry points.
- [x] `src/bond_cli/manuscript_variables.py` — identity + registry tokens.
- [x] Deterministic zero-mock suite (real film providers + subprocess smoke) at
      ≥90% coverage.

## Integration points / notes

- **Real-film mission binding.** `bond run` binds each mission package to its
  real film adapter via `bond_orchestrator.film_providers.load_film_providers`
  and falls back to the orchestrator's built-in deterministic provider when a
  film is not built. As the fleet's remaining films land, `run` uses them with
  no front-door change.
- **Gadget discovery is best-effort.** `bond gadgets` imports each film's
  `mission` module and calls `register_gadgets` if present; films without the
  hook (or that fail to import) contribute 0. 14/27 films currently register.
- **Not a scope item.** The front door does not implement the protocol, the
  DAG runner, the registry, or Q-branch primitives — those stay in their own
  packages.

## Quality gates (current evidence)

- Tests + coverage: `uv run pytest tests/ --cov=src --cov-fail-under=90`.
  Live count + coverage % in `docs/_generated/COUNTS.md`.
- Lint/type: `uv run ruff check src/ scripts/ tests/` and
  `uv run mypy src/ scripts/` clean.
- Lineage: zero exemplar-lineage hits outside allowed docs.
