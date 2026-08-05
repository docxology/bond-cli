# tests/

Zero mocks; real providers, real files, real subprocesses.

- `test_dispatch.py` — in-process command routing, the five protocol stages,
  `run`, `status`, `gadgets`, exit codes.
- `test_deepening.py` — `missions`/`whois`/`roster-export`, `--json`,
  color-safe tables, every gadget-registration convention via real tmp films.
- `test_contracts.py` — the exit-code contract (real failing film packages
  driven through `execute`/`debrief`/`run`, each with a passing control) and
  the sorted-JSON-keys contract (asserted on raw emitted text); both verified
  by mutation.
- `test_hardening.py` — manifest-reconciliation edges (measured `0.0`, partial
  and malformed manifests), the unmeasured export branch, a film that raises on
  import, optional brief sections, the token↔registry contract, the claim ledger.
- `test_manuscript_variables.py` — token map + live manuscript cross-reference.
- `test_scripts_smoke.py` — subprocess smoke of the `scripts/` entry points.

Gate: `uv run pytest tests/ --cov=src --cov-fail-under=90`. Doctrine:
`../docs/testing_philosophy.md`.
