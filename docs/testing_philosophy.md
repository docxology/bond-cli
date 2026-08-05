# Testing Philosophy — bond-cli (THE FRONT DOOR)

`bond-cli` is tested with **zero mocks** against **real** layers, real film
providers, real files, and real subprocesses.

## Why a CLI in particular must not be mocked

The front door's entire job is wiring. Its value is the claim "this verb really
reaches that layer and really returns that exit code". A mocked provider or a
stubbed registry would test the wiring against a facsimile of itself — the
test would pass at exactly the moment the wiring broke. So every test drives
`bond_cli.dispatch.main(argv)` (or a real subprocess) and lets the call travel
all the way into `bond_api`, `bond_coordinator`, and `bond_orchestrator`.

## Zero-mock policy

Prohibited anywhere in `tests/`: `unittest.mock`, `MagicMock`, `@patch`,
`create_autospec`, or any other mocking framework.

Permitted, and used deliberately: `monkeypatch.setattr` on **this package's own
module constants** — `dispatch.BOND_ROOT`, `dispatch.GATE_MANIFEST`,
`dispatch.GADGET_FILM_SLUGS`. That is environment isolation, not dependency
replacement: it redirects real filesystem reads at real files this test wrote.
Two tests also monkeypatch a sibling layer's function to raise its **own real
exception type** (`FilmProviderError`, and a real `build_status` over a real
custom roster) to reach an error branch that cannot otherwise be provoked
locally; the objects on both sides remain real.

## Real substitutes for mocks

| Instead of a mock | The suite uses |
|---|---|
| a stub provider | the reference film `sable` (numpy-free, fast) and real fleet films `goldfinger` / `skyfall` |
| a fake film package | a real `<slug>/src/<slug>/mission.py` written into `tmp_path` and genuinely imported |
| a fake gate manifest | a real JSON file on disk, with `GATE_MANIFEST` pointed at it |
| a patched CLI entry | `subprocess.run([sys.executable, "scripts/bond.py", ...])` |
| a fabricated coverage number | the measured value in `_generated/COUNTS.md` |

## What each test file covers

| File | Focus |
|---|---|
| `test_dispatch.py` | The command surface end-to-end: the full roster from `list`, the five protocol stages against `sable` and `goldfinger`, `run` over real film adapters plus the real-`FilmProviderError` fallback, `status` (plain, blocked, measured, unmeasured, malformed manifest), `gadgets` for registering and non-registering films, and every exit-code path. |
| `test_deepening.py` | The Phase-4 surface: `missions`, `whois`, `roster-export`, the `--json` variants, color-safe table behaviour, and each gadget-registration convention driven through a real tmp film package. |
| `test_hardening.py` | The Phase-5 edges: measured `0.0` coverage preserved, non-numeric/boolean coverage rejected, partial manifests (unmeasured films keep registry records and report `measured: null`), malformed and package-key-less manifests, the unmeasured `roster-export` branch, a film that raises on import, optional `MissionBrief` sections, the token↔registry contract, and the claim ledger re-derived from its named sources. |
| `test_manuscript_variables.py` | Token hydration: identity from config, defaults when config is absent or malformed, persistence round-trip, and a sweep asserting every `{{TOKEN}}` used in the numbered manuscript sections resolves. |
| `test_scripts_smoke.py` | The thin `scripts/` wrappers as real subprocesses, proving the operator-facing entry points work outside the pytest process. |

## Pin ambient state

The fleet's aggregate gate manifest lives outside this package
(`<bond root>/output/aggregate/gate_manifest.json`) and appears or disappears
as the fleet gate runs. Any test whose outcome depends on it points
`dispatch.GATE_MANIFEST` at a `tmp_path` — present for the measured branches,
deliberately absent for the unmeasured ones. Without that pin, the suite's
branch coverage moves with whoever last ran the fleet gate. This is the
package's own scar: the unmeasured `roster-export` branch went uncovered for a
whole phase purely because a manifest happened to exist in the workspace.

## Determinism

Fixed-seed providers, canonical ordering (roster order, sorted JSON keys), and
no wall-clock in any persisted artifact make repeated runs byte-stable. Tests
assert real values, never timestamps; `test_status_json` asserts that no
`generated_at` key exists.

## Coverage

The gate is:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

line + branch, ≥90% on `src/`. Live test count and coverage % live in
[`_generated/COUNTS.md`](_generated/COUNTS.md) — the only place a figure is
written down. Subprocess smoke does not contribute to `src/` coverage by
design; every persistent behaviour it touches is also covered in-process.
