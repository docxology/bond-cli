# bond-cli

`bond-cli` installs the `bond` command for the PROJECT BOND film-software
suite. It reads the shared roster and delegates to the vendored layers. The
distribution is `bond-cli`; the Python package is `bond_cli`.

From the repository root with [uv](https://docs.astral.sh/uv/) installed,
use the checkout’s Python version and locked, local dependencies.

```sh
uv sync --locked
uv run --no-sync bond --help
uv run --no-sync bond list --json
```

The roster can include entries for film packages absent from the checkout.
Status reports show measured values when an aggregate gate manifest is
present. See [installation and verification](docs/standalone.md) for those
inputs and the contributor checks.

- [Documentation index](docs/README.md)
- [Command reference](docs/usage.md)
- [Source map](docs/reference/source.md) and [contributor guidance](AGENTS.md)
- [Software manuscript](docs/manuscript/README.md)
