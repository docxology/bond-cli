# tests/ — front-door test suite

Zero mocks. Real film providers (reference `sable` plus real fleet films),
real importable film packages under `tmp_path`, real gate manifests, and real
subprocess smoke of `scripts/`. Persistent cases are covered in-process
(`dispatch.main` + `capsys`) so they count toward the `src/` gate.

## Files

| File | Covers |
|---|---|
| `test_dispatch.py` | in-process command routing, provider lifecycle, gadgets, exit codes, measured status |
| `test_deepening.py` | `missions`/`whois`/`roster-export`, `--json`, color-safe tables, gadget-convention tolerance (real tmp films) |
| `test_contracts.py` | exit-code contract (real failing film packages through `execute`/`debrief`/`run`, each with a passing control) and sorted-JSON-keys contract (raw-text key order, construction order pinned); both mutation-verified |
| `test_hardening.py` | manifest edges (measured `0.0`, non-numeric, partial, malformed, key-less), unmeasured export branch, broken-film tolerance, optional brief sections, token↔registry contract, claim-ledger re-derivation |
| `test_manuscript_variables.py` | token map + live manuscript cross-reference |
| `test_scripts_smoke.py` | subprocess `scripts/bond.py` + token hydration |

## Rules

- No mocking framework, ever. `monkeypatch.setattr` on this package's own
  constants (`BOND_ROOT`, `GATE_MANIFEST`, `GADGET_FILM_SLUGS`) is environment
  isolation and is allowed; replacing a dependency's behaviour with a stand-in
  is not.
- **Pin ambient state.** Any test that depends on the fleet's aggregate gate
  manifest must point `dispatch.GATE_MANIFEST` at a `tmp_path` — present or
  deliberately absent. The real manifest comes and goes as the fleet gate runs.
- Every assertion must be able to fail. No tautologies, no `assert result` on a
  value that is always truthy.
- **Coverage does not prove a claim is bound.** A conditional expression
  (`return 0 if ok else 1`) emits no branch arc, and `json.loads` discards key
  order — both of this package's headline contracts were 100 %-covered and
  unverified. When a claim matters, mutate the code that implements it and
  confirm the test goes red before believing it.

Gate: `uv run pytest tests/ --cov=src --cov-fail-under=90`.
