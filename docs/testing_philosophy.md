# Testing Philosophy — bond-cli

`bond-cli` is tested with **zero mocks** against **real** layers and real film
providers.

## Zero-mock policy

No `unittest.mock`, `MagicMock`, `@patch`, or `create_autospec` in `tests/`.
A mock-free front door matters: it proves the delegation wiring actually
reaches the real providers, the real registry, and the real runner — not a
stubbed facsimile.

## What the suite exercises

- **In-process dispatch** (`bond_cli.dispatch.main([...])` with `capsys`):
  - `list` returns the {{FILM_COUNT}}-film roster from the coordinator registry.
  - `brief`/`recon`/`plan`/`execute`/`debrief` against the reference film
    `sable` (numpy-free, fast) and a real fleet film (`goldfinger`) for the
    NumPy-backed path.
  - `run` a canned mission over real film adapters, plus a fallback path when
    a real film cannot be bound (real `FilmProviderError`).
  - `status` summary and the blocked-packages branch (real `build_status` over
    a custom roster with a RED package).
  - `gadgets` for a real registering film (`skyfall`), a non-registering film
    (`sable`), and the whole-fleet path; best-effort gadget discovery.
  - Exit-code paths: unknown film → 1, unknown mission → 2, argparse misuse → 2.
- **Subprocess smoke** (`scripts/bond.py list`, `status`, and
  `z_generate_manuscript_variables.py`) via `sys.executable` with
  `cwd=project_root`, exercising the real entry points.

## Coverage

The gate is `uv run pytest tests/ --cov=src --cov-fail-under=90` (line +
branch, ≥90%). Live count + coverage % are in
[`docs/_generated/COUNTS.md`](_generated/COUNTS.md). Subprocess smoke does not
count toward `src/` coverage; the persistent cases are covered in-process.

## Determinism

Fixed-seed providers and canonical ordering make repeated runs byte-stable.
Tests assert presence/values of real outputs, never wall-clock.
