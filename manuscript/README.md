# Manuscript — bond-cli (THE FRONT DOOR)

Numbered prose sections are `00_abstract.md` … `07_scope_and_related_work.md`
plus `99_references.md`; they use the `{{TOKEN}}` set documented in
[`SYNTAX.md`](SYNTAX.md). Identity (package name + codename) is read from
[`config.yaml`](config.yaml) → `package:`. Fleet counts come from the built
coordinator registry.

Regenerate tokens:

```bash
uv run python scripts/z_generate_manuscript_variables.py
```
