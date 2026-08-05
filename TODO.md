# bond-cli TODO

Forward-only backlog for the terminal front door (PROJECT BOND · THE FRONT
DOOR). Delivered work is described in `README.md` and the manuscript, not
archived here — this file holds only what is genuinely still open.

## Open work

- [ ] **`--json` on the remaining commands.** `gadgets` and `run` still print
      human text only. `gadgets --json` (film → gadget names) and
      `run --json` (per-package verdicts + consolidated debrief) would make the
      whole surface machine-readable. Adding either means: parser flag,
      `JSON_COMMANDS` entry, handler branch, test, and the
      `{{JSON_COMMANDS}}`/`{{JSON_COMMAND_COUNT}}` tokens update themselves.
- [ ] **Debrief with no lessons.** `cmd_debrief`'s "no lessons" branch is the
      one partial branch left uncovered — every real provider currently returns
      at least one lesson. Cover it when a film ships a lesson-free debrief, or
      by driving `run_mission` over a real minimal provider.
- [ ] **Fleet-wide `gadgets` cost.** The default sweep imports every film's
      mission module (NumPy-backed films included), so a bare `bond gadgets`
      takes seconds. Consider a `--fast` mode that reads only films already
      imported, or parallel import. Do not "fix" it by caching results to disk —
      that would introduce state the front door deliberately has none of.
- [ ] **Shell completion.** No `bash`/`zsh` completion is shipped. Generating
      it from `COMMANDS` (plus the roster for the `<film>` argument) is
      mechanical and would keep completion in sync with the registry by
      construction.
- [ ] **Exit-code documentation for `run` sub-failures.** A mission whose
      verdicts partly fail returns 1 with no indication of which package
      failed beyond the consolidated debrief text. A structured summary line
      (or the `run --json` above) would make scripting against it practical.

## Integration points / notes

- **Real-film mission binding.** `bond run` binds each mission package to its
  real film adapter via `bond_orchestrator.film_providers.load_film_providers`
  and falls back to the orchestrator's built-in deterministic provider when a
  film is not built. As the fleet's remaining films land, `run` uses them with
  no front-door change.
- **Gadget discovery is best-effort by contract.** `register_film_gadgets`
  tolerates every registration convention and returns 0 for a film that fails
  to import, so one broken film cannot abort a fleet sweep. Do not narrow this
  to "raise on import error" — the whole-fleet sweep depends on it. To see how
  many films currently register, run `uv run python scripts/bond.py gadgets`
  and count the lines; the figure moves as the fleet is built, so it is not
  written down here.
- **Not a scope item.** The front door does not implement the protocol, the
  DAG runner, the registry, or Q-branch primitives — those stay in their own
  packages. It also does not do interactive/TUI modes, persistent state, or
  network access.

## Quality gates (how to check, not what the numbers were)

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

Live test count and measured `src/` coverage: `docs/_generated/COUNTS.md`.
Derived counts (commands, JSON commands, layers, films, missions):
`data/claim_ledger.yaml`, re-derived from their named sources by
`tests/test_hardening.py::test_claim_ledger_matches_its_sources`.
