# TODO — bond-cli (THE FRONT DOOR)

`bond-cli` is the Layer-4 terminal front door of PROJECT BOND: twelve verb-first
commands that route to the four built sibling layers (`bond-utilities`,
`bond-api`, `bond-coordinator`, `bond-orchestrator`) and map their outcomes to
exit codes. It implements no mission logic and ships no `MissionProvider`.
**Verified state today (2026-08-05, commit `b0e811a`, clean tree):**
`uv run pytest tests/ --cov=src --cov-fail-under=90` → **103 passed,
100.00 % line+branch coverage on `src/`** (352 statements, 92 branches, 0 missed,
0 partial). The two headline contracts — exit codes and sorted JSON keys — are
mutation-checked in `tests/test_contracts.py`; the four findings from the
adversarial audit (`output/verify/bond-cli.json`) were all confirmed closed
against the current tree while writing this file, and
`output/verify/bond-cli.unresolved.json` records nothing unresolved.

## Open work

### Correctness

**C1 — `bond gadgets <film>` collapses three different outcomes into one
message and one exit code.**

`register_film_gadgets` swallows every import exception
(`src/bond_cli/dispatch.py:550-553`, `except Exception: return 0`) and
`cmd_gadgets` reports any empty result identically
(`src/bond_cli/dispatch.py:618-622`). Measured today, all three of these print
`no gadgets registered for film '<slug>'` and exit 1:

| Invocation | Actual condition |
|---|---|
| `gadgets definitely_not_a_film` | the film does not exist |
| `gadgets die_another_day` | film exists, `import die_another_day.mission` raises `ModuleNotFoundError: No module named 'scipy'` |
| `gadgets sable` | film imports cleanly and genuinely registers no gadgets |

The same blindness hides in the fleet sweep: a bare `bond gadgets` lists 22 of
28 slugs, and nothing distinguishes the five films with no gadgets from
`die_another_day`, which is broken in this package's environment. An operator
cannot tell a missing dependency from an empty shelf.

*Done looks like:* an unknown slug raises `CliError` (exit 1, message on stderr,
same wording as `brief`/`plan`); an import failure emits a diagnostic on stderr
naming the exception while still contributing 0 so the fleet sweep never aborts
(the existing tolerance contract, unchanged); a clean film with no gadgets keeps
today's message. Update the exit-code line in `README.md:44-46` and
`manuscript/02_methodology.md:40` if the wording changes, and add a test that
distinguishes the three cases.

*Demonstrate:*
```bash
uv run python scripts/bond.py gadgets definitely_not_a_film   # "not available", stderr, rc 1
uv run python scripts/bond.py gadgets die_another_day 2>&1 >/dev/null   # names scipy
uv run python scripts/bond.py gadgets sable                   # unchanged, rc 1
uv run python scripts/bond.py gadgets >/dev/null              # rc 0, stdout unchanged
```

**C2 — the two `gadgets` failure messages go to stdout, not stderr.**

`src/bond_cli/dispatch.py:621` and `:628` `print(...)` to stdout. Every other
failure path in the package writes to stderr — the `CliError` handler at
`:707`, the unknown-mission path at `:258`. A caller piping `bond gadgets
<film>` into a parser receives the error text as if it were data.

*Done looks like:* both messages carry `file=sys.stderr`; stdout on a failed
gadget lookup is empty.

*Demonstrate:* `uv run python scripts/bond.py gadgets sable 2>/dev/null` prints
nothing and exits 1.

### Verification

**V1 — the "byte-identical repeat run" claim is not bound by any test.**

`manuscript/02_methodology.md:34` ("two runs against an unchanged fleet are
byte-identical"), `manuscript/03_results.md:24`, and
`manuscript/06_reproducibility.md:11` all assert it. I confirmed it holds by
hand today (`roster-export` twice and `status --json` twice, `cmp` clean both
times), but no test asserts it. Adding a `"generated_at": time.time()` field to
any JSON payload would keep the entire suite green and coverage at 100 %,
because the new line is *executed* — coverage measures execution, not
falsifiability. This is the same class of hollow gate the audit found in the
sorted-keys contract.

*Done looks like:* a test in `tests/test_contracts.py` that invokes at least
`status --json` and `roster-export` twice in separate subprocesses (pinning
`GATE_MANIFEST` so ambient fleet state cannot move) and asserts the raw bytes
are equal — verified by mutation: inject a wall-clock field into a payload and
watch the test go red, then record the mutation in
`docs/_generated/COUNTS.md`'s mutation table alongside the two already there.

*Demonstrate:* `uv run pytest tests/test_contracts.py -k byte_identical -v`

**V2 — the `bond` console-script entry point is never exercised.**

`pyproject.toml:38-39` declares `bond = "bond_cli.dispatch:main"`.
`README.md:93-94`, `AGENTS.md:57`, and `manuscript/05_experimental_setup.md:4`
all claim it is identical to the `scripts/bond.py` bootstrap and returns the
same exit codes. `tests/test_scripts_smoke.py` invokes only `scripts/bond.py`
(six tests, all via `_run_script`). Renaming `main`, or mistyping the target
string in `pyproject.toml`, breaks the installed CLI and fails nothing.

*Done looks like:* a smoke test that runs the installed `bond` console script
in a subprocess for at least one command and asserts its stdout and returncode
match `scripts/bond.py` for the same argv.

*Demonstrate:* `uv run pytest tests/test_scripts_smoke.py -k console -v`

**V3 — `manuscript/layer_contract.yaml` is prose, not a gate.**

Several of its `cross_cutting:` rules are genuinely enforced by tests (sorted
JSON keys, no ANSI, exit codes, the re-derived claim ledger). Three are not
enforced anywhere and are true today only by inspection:

- "No `infrastructure.*` imports anywhere in `src/` or `scripts/`"
  (also `AGENTS.md:33`, `src/AGENTS.md:25`) — verified clean today by
  `grep -rn infrastructure src/ scripts/`, which matches only the prose rule
  itself.
- "Never emits a wall-clock value" (`dispatch.py` and
  `manuscript_variables.py` rows) — verified clean today by
  `grep -rn "import time|datetime|\.now\(\)" src/ scripts/` → no matches.
- "No terminal-width probing and no environment reads" (`table.py` row) — same
  grep, no `os.environ` / `getenv` / `shutil.get_terminal_size` in `src/`.

*Done looks like:* one test that reads `manuscript/layer_contract.yaml` and
asserts these three mechanically checkable rules against the `src/` and
`scripts/` sources, so adding `import datetime` to `dispatch.py` fails the
suite instead of silently falsifying the manuscript.

*Demonstrate:* `uv run pytest tests/test_hardening.py -k layer_contract -v`

### Documentation

None open. Checked: every measured figure in the package lives only in
`docs/_generated/COUNTS.md` (`grep -rn "99\.55|partial branch|103|100 %"` across
`docs/`, `manuscript/`, `README.md`, `AGENTS.md`, `tests/AGENTS.md`,
`src/AGENTS.md` finds no figure quoted elsewhere); COUNTS.md's numbers match the
run recorded above; the "next steps" prose in `README.md:137`, `AGENTS.md:77`,
and `docs/README.md:25` are pointers to this file rather than duplicated
backlogs; and the four documentation defects the audit raised (the singular-vs-
two partial branch contradiction and the mislabelled `dispatch.py:588` branch)
are corrected in the current COUNTS.md.

### Extension

**E1 — `--json` on `gadgets` and `run`.**

`JSON_COMMANDS` (`src/bond_cli/dispatch.py:82`) is `("list", "status",
"missions", "whois")`; `gadgets` and `run` print human text only. `run`'s
consolidated debrief *does* already name each package's verdict
(`goldfinger: PASS — …`), so the gap is machine-readability, not visibility: a
script cannot get per-package verdicts without parsing prose. Work is
mechanical — parser flag, `JSON_COMMANDS` entry, handler branch, test — and the
`{{JSON_COMMANDS}}` / `{{JSON_COMMAND_COUNT}}` manuscript tokens and the
`json_command_count` row in `data/claim_ledger.yaml` re-derive themselves.
`tests/test_hardening.py::test_json_commands_claim_is_enforced_by_the_parser`
already asserts both halves of the claim, so a flag added without updating
`JSON_COMMANDS` fails the suite.

*Done looks like:* `bond gadgets --json` emits film → gadget-name rows and
`bond run <mission> --json` emits per-package verdicts plus the consolidated
debrief, both key-sorted, with a raw-text key-order assertion in
`tests/test_contracts.py` matching the existing five.

*Demonstrate:*
`uv run python scripts/bond.py run OPERATION_SINGLET --json | python -c 'import json,sys; json.load(sys.stdin)'`
and `uv run pytest tests/ --cov=src --cov-fail-under=90`.

**E2 — shell completion.**

No `bash`/`zsh` completion ships (`grep -rn "completion|argcomplete" src/
scripts/ pyproject.toml` → no matches). Generating it from `COMMANDS` plus the
coordinator roster for the `<film>` argument keeps completion in sync with the
registry by construction, which is the only version worth shipping here.

*Done looks like:* a `bond completion bash|zsh` subcommand (or a generated
script under `scripts/`) whose command list is read from `dispatch.COMMANDS`,
with a test asserting every entry of `COMMANDS` appears in the generated text.

*Demonstrate:* `uv run python scripts/bond.py completion zsh | grep -c roster-export`

## Known limitations (not bugs)

- **Coverage cannot see a conditional expression.** `return 0 if ok else 1`
  emits no branch arc, so 100 % line+branch coverage says nothing about whether
  the non-zero path is exercised — this is exactly how the audit found both
  headline contracts fully "covered" and entirely unverified. Every exit-code
  and key-ordering claim is therefore pinned explicitly in
  `tests/test_contracts.py`, each checked by mutating `dispatch.py` and watching
  it go red (mutation table in `docs/_generated/COUNTS.md`). Any new
  `return 0 if … else 1`, and any new JSON payload, needs a paired
  falsifiable test; the coverage gate will not catch it for you.
- **Gadget discovery is best-effort by contract.** `register_film_gadgets`
  tolerates every registration convention the fleet uses and returns 0 for a
  film that fails to import, so one broken film cannot abort a fleet sweep. Do
  not narrow this to "raise on import error" — the whole-fleet sweep depends on
  it. C1 above adds a *diagnostic*, not an abort.
- **The fleet sweep imports every film module, and that is fine.** A bare
  `bond gadgets` imports all 27 roster films plus the reference film; measured
  today at **0.34 s wall** (`time uv run python scripts/bond.py gadgets`). A
  previous revision of this file called it "seconds" and proposed a `--fast`
  mode; the measurement does not support that work. Do not "fix" it by caching
  results to disk — that would introduce state the front door deliberately has
  none of.
- **`die_another_day` cannot be imported from this package's environment.** It
  requires `scipy`, which `bond-cli` does not install. That is correct: the
  front door depends only on the four built layers and must not grow a
  film's scientific dependencies. C1 is about *reporting* the condition, not
  removing it.
- **`format_table` assumes rectangular input.** A row shorter than `headers`
  raises `IndexError` (`src/bond_cli/table.py:39-42`). Every call site builds
  rows of matched width by construction and no public surface accepts
  user-supplied rows, so this is an unvalidated internal precondition rather
  than a reachable defect. Do not add per-cell padding without a caller that
  needs it.
- **Not a scope item.** The front door does not implement the protocol, the DAG
  runner, the registry, or Q-branch primitives — those stay in their own
  packages. It also does not do interactive/TUI modes, persistent state, or
  network access. `bond run` binds each mission package to its real film adapter
  via `bond_orchestrator.film_providers.load_film_providers` and falls back to
  the orchestrator's built-in deterministic provider when a film is not built,
  so newly landed films work with no front-door change.

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90   # 103 passed, 100.00 % (2026-08-05)
uv run ruff check src/ scripts/ tests/               # clean
uv run ruff format --check src/ scripts/ tests/      # clean
uv run mypy src/ scripts/                            # clean
```

Sandbox note: `uv` cannot write its cache under the default sandbox — re-run
with the sandbox disabled if you see
`Failed to initialize cache at /Users/4d/.cache/uv`.

Smoke the real entry points and the determinism property by hand:

```bash
uv run python scripts/bond.py status --json
uv run bond list                                     # the console script (unbound — see V2)
uv run python scripts/bond.py roster-export > /tmp/r1.json
uv run python scripts/bond.py roster-export > /tmp/r2.json
cmp /tmp/r1.json /tmp/r2.json                        # byte-identical (unbound — see V1)
```

Live test count and measured `src/` coverage belong in
`docs/_generated/COUNTS.md` and nowhere else. Derived counts (commands, JSON
commands, layers, films, missions) live in `data/claim_ledger.yaml` and are
re-derived from their named source symbols by
`tests/test_hardening.py::test_claim_ledger_matches_its_sources`.
