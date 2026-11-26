# Install and verify bond-cli

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run
from the project root:

```sh
uv sync --locked
uv run --no-sync bond list
uv run --no-sync bond status --json
```

The lockfile installs the four dependencies from the copies in `vendor/`.
The package supports Python 3.11 or later. The checkout selects Python 3.15.
The full native test run requires Python 3.14 or later for generated
provider annotations.

## Reference provider

The SABLE fixture in [bond-api](https://github.com/docxology/bond-api) is a
deterministic protocol contract demonstration. It can be placed at
`../bond-api/films/sable/mission.py` relative to the bond-cli checkout.
With SABLE present, `uv run --no-sync bond brief sable` prints the
reference provider's description.

Without an aggregate gate manifest, the status commands show registry
declarations and missing measured values. The tests for measured status
use temporary manifests.

## Verify the package

From the bond-cli checkout, verify documentation-related behavior and the CLI’s registry and status surfaces:

```sh
uv sync --locked --extra dev
uv run --no-sync pytest --no-cov tests/test_manuscript_variables.py tests/test_hardening.py \
  tests/test_scripts_smoke.py tests/test_vendor_provenance.py
uv run --no-sync ruff check src/ scripts/ tests/
uv run --no-sync ruff format --check src/ scripts/ tests/
uv run --no-sync mypy src/ scripts/
uv run --no-sync python scripts/vendor.py --check
```

See [the coverage archive](_generated/COUNTS.md) and the
[testing philosophy](testing_philosophy.md). The
[rendering guide](rendering.md) describes the separate paper build.
