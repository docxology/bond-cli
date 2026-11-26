# Render and validate the manuscript

## Generate the manuscript variables

From the standalone project root:

```sh
uv sync --locked
uv run --no-sync python scripts/z_generate_manuscript_variables.py
```

The script reads [the manuscript configuration](manuscript/config.yaml)
and derives the token map from the CLI and vendored registries. It writes
`output/variables/manuscript_variables.json`. The numbered source sections,
LaTeX preamble, bibliography, and layer contract live in
[docs/manuscript/](manuscript/README.md).

## Render with the pinned template

The render uses Git, uv, Pandoc 3.1.11.1, matching
[pandoc-crossref](https://github.com/lierdakil/pandoc-crossref/releases/tag/v0.3.17.0c),
XeLaTeX, and the TeX Live packages in the
[template run guide](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/RUN_GUIDE.md).
Run these commands from the bond-cli checkout. The runner executes the
project hydrator in a detached worktree under its own `projects/working/`
directory.

```sh
bond_cli_source="$PWD"
git clone https://github.com/docxology/template.git ../bond-cli-renderer
cd ../bond-cli-renderer
git checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
uv sync --locked --no-dev
mkdir -p projects/working
bond_cli_checkout="$PWD/projects/working/bond-cli"
git -C "$bond_cli_source" worktree add --detach "$bond_cli_checkout" HEAD
(
  cd "$bond_cli_checkout"
  uv sync --locked
  uv run --no-sync python scripts/z_generate_manuscript_variables.py
)

uv run --no-sync python - "$bond_cli_checkout" <<'PY'
import json
import sys
from pathlib import Path

from infrastructure.rendering.manuscript_injection import write_resolved_manuscript_tree

project = Path(sys.argv[1])
variables = project / "output" / "variables" / "manuscript_variables.json"
write_resolved_manuscript_tree(project, json.loads(variables.read_text(encoding="utf-8")))
PY

uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/bond-cli
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/bond-cli
```

The renderer resolves numbered source sections from `docs/manuscript/` and
uses their hydrated copies in `output/manuscript/`. Stage 04 checks the
[project evaluation plan](../experiment_plan.yaml) and needs the
committed source in Git's index for provenance.

The project writes its combined PDF to `output/pdf/` and HTML to
`output/web/index.html`. Validation and provenance reports go to
`output/reports/`. Verify the section order, resolved registry counts, and
bibliography in the combined output. This manuscript uses prose and tables.
