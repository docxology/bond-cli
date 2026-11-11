# TODO — bond-cli (THE FRONT DOOR)

`bond-cli` is the Layer-4 terminal front door of PROJECT BOND: twelve verb-first
commands that route to the four built sibling layers (`bond-utilities`,
`bond-api`, `bond-coordinator`, `bond-orchestrator`) and map their outcomes to
exit codes. It implements no mission logic and ships no `MissionProvider`.
**Verified state:** the live test count and `src/` coverage figure live in
[`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md), and the last full gate
run is recorded in the Round-2 section at the bottom of this file. The two
headline contracts — exit codes and sorted JSON keys — are
mutation-checked in `tests/test_contracts.py`; the four findings from the
adversarial audit (`output/verify/bond-cli.json`) were all confirmed closed
against the tree while writing this file.

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
with the sandbox disabled if `uv` reports that it failed to initialize its
cache.

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

---

## Round-2 (2026-08-06)

**Baseline (2026-08-05):** 103 passed, 100.00 % line+branch on `src/` (352 stmts /
92 branches); ruff check + format clean; mypy clean.

### Findings (hostile review of my own package)

**F1 — A `TypeError` raised *inside* a one-arg `register_gadgets(registry)` hook
body was misread as a zero-arg hook and re-invoked.** `dispatch.py` caught
`TypeError` around `register(registry)` and fell back to `register()`. When the
hook body itself raised `TypeError`, that fallback re-called the hook with no
argument, escaping a SECOND, misleading `TypeError: missing 1 required
positional argument` that propagated out of `register_film_gadgets` and aborted
the whole-fleet `bond gadgets` sweep while masking the film's real defect.

*Fix:* `_invoke_register_hook` reads the hook's arity from `inspect.signature`
and calls `register(registry)` or `register()` accordingly; a hook-body
exception is caught per-film, diagnosed to stderr, contributes 0, and the sweep
continues. Regression: `test_register_gadgets_hook_body_typeerror_is_contained`
(real tmp film whose one-arg hook body raises `TypeError`) and
`test_register_gadgets_hook_body_error_is_contained` (any exception); both
mutation-verified (revert the signature dispatch → test goes red).

**F2 — Human `bond status` printed `min=None% max=None%` when nothing was
measured.** The JSON path reported `measured:false` + `coverage.*:null`
correctly, but the human table interpolated `None` straight into a `%` string.

*Fix:* min/max render `N/A` (like mean) when unmeasured. Regression:
`test_status_human_none_coverage_does_not_print_none` (asserts `min=N/A`,
`max=N/A`, no `None%`); mutation-verified.

**F3 — gadget failures collapsed three outcomes into one (C1).** An unknown
slug, a built-but-broken film (`die_another_day` needs `scipy`), and a clean
film with no gadgets all printed the same stdout message and exit 1.

*Fix:* `cmd_gadgets` now distinguishes them — unknown slug raises `CliError`
(stderr, exit 1, same "not available" wording as `brief`/`plan`); a built film
whose import raises is diagnosed to stderr naming the exception while still
contributing 0 (fleet sweep never aborts); a clean film keeps the empty-lookup
message. Regression: `test_gadgets_unknown_film_cli_error`.

**F4 — both gadget failure messages went to stdout, not stderr (C2).** A caller
piping `bond gadgets <film>` into a parser received error text as data.

*Fix:* both messages (`no gadgets registered …`, `no film gadgets registered in
the fleet`) now write to stderr; stdout on a failed lookup is empty. Regressions
assert `out == ""` on failure and the message on `err`.

### Verification gaps closed (round 2)

- **V1 — byte-identical repeat runs now bound by a test.** `status --json` and
  `roster-export` are each invoked twice in separate subprocesses and asserted
  byte-identical (`test_status_json_byte_identical_repeat`,
  `test_roster_export_byte_identical_repeat`). A wall-clock field would turn
  these read.
- **V2 — the installed `bond` console script is exercised.** A subprocess test
  asserts the console script's stdout + return code equal `scripts/bond.py` for
  `list`, so a mistyped `pyproject.toml` entry target fails the suite
  (`test_console_script_matches_bootstrapper`).
- **V3 — the layer contract is now a gate.** `test_layer_contract_prohibited_imports_are_gated`
  reads `manuscript/layer_contract.yaml`, requires the three mechanically
  checkable `cross_cutting` rules to be present in the YAML, and asserts the
  `src/` + `scripts/` trees carry no `infrastructure.*`, no wall-clock
  (`import time`/`datetime`/`.now()`), and no terminal-width/environment reads.

### Manuscript improvements

- `03_results.md`: added a live-derived-surface table ({{FILM_COUNT}} /
  {{COMMAND_COUNT}} / {{JSON_COMMAND_COUNT}} / {{LAYER_COUNT}} / {{MISSION_COUNT}},
  each a generated token, regenerated by `scripts/z_generate_manuscript_variables.py`)
  and a full **Limitations and uncertainty** section (coverage-proves-execution,
  best-effort gadget discovery, rectangular `format_table` precondition, gate-is-a-
  snapshot, inherited determinism).
- `02_methodology.md`: documents the three-outcome gadget distinction, the
  `inspect.signature` arity mechanism [@pythoninspect], and the `None%` fix.
- `03_results.md`/`06_reproducibility.md`/`05_experimental_setup.md`: document the
  newly bound repeatability / console-script / layer-contract tests.
- `references.bib` + `99_references.md`: added the `pythoninspect` entry.

### Gates (2026-08-06)

- `uv run pytest tests/ --cov=src --cov-fail-under=90` → **113 passed, 100.00 %**
  (368 stmts / 96 branches, 0 missed, 0 partial).
- `uv run ruff check src/ scripts/ tests/` → clean.
- `uv run ruff format --check src/ scripts/ tests/` → clean (20 files).
- `uv run mypy src/ scripts/` → clean (7 source files).

`docs/_generated/COUNTS.md` updated (113 / 100.00 %, with two new mutation rows for
the F1/F2 fixes and a note on the three round-2 verification bindings).

### Left for a future round

- **E1** — `--json` on `gadgets` and `run` (unchanged from the pre-existing
  backlog above).
- **E2** — shell completion for `bond` (unchanged).

## Workflowz review — 2026-11-10

### Correctness

**W1 — P1 — Make each film's gadget registration atomic when discovery fails.**

*Evidence:* `register_film_gadgets` records only a count before invoking hooks (`src/bond_cli/dispatch.py:586-596`), then returns 0 from the registration-error handler without removing entries already added to the shared registry (`src/bond_cli/dispatch.py:616-624`). `cmd_gadgets` subsequently treats any remaining names as success (`src/bond_cli/dispatch.py:636-645`). Thus a real hook that calls `registry.register(...)` and then raises emits an error diagnostic but can still make the film and its partial gadget set appear successfully registered. Existing failure tests raise before registering anything and therefore cannot expose this state leak (`tests/test_dispatch.py:204-249`). This contradicts the documented contract that a failing film contributes zero and cannot corrupt the fleet sweep (`docs/architecture.md:84-97`).

*Done looks like:* isolate or roll back all mutations for the current slug when any import/registration step raises; preserve entries for other films, retain the stderr diagnostic and best-effort sweep behavior, and add a real tmp-film regression whose hook registers one gadget and then raises. Single-film and fleet output must not expose the partial registration.

*Dependencies/constraints:* use the public `bond_api.registry.GadgetRegistry` surface; do not narrow the intentional broad exception containment or turn a broken film into a fleet-wide abort.

*Demonstrate:*
```bash
uv run pytest tests/test_dispatch.py -k partial_registration -v
# Expected: the new regression passes; the failed slug contributes no registry rows,
# stderr names the original exception, and unrelated films remain registered.
```

**W2 — P1 — Reject non-finite measured coverage before producing JSON.**

*Evidence:* `_measured_coverage` accepts every `int`/`float` other than `bool` and converts it directly to `float` (`src/bond_cli/dispatch.py:289-296`). Python's JSON decoder accepts `NaN`, `Infinity`, and `-Infinity` by default in `_manifest_rows` (`src/bond_cli/dispatch.py:299-313`), and the CLI's default `json.dumps` settings emit those tokens again through measured `whois`, `status`, and `roster-export` payloads (`src/bond_cli/dispatch.py:345-375`, `:454-477`, `:511-525`). Those tokens are not RFC 8259 JSON and can also poison status aggregates. Current edge tests cover zero, strings, and booleans but no non-finite numbers (`tests/test_hardening.py:38-76`).

*Done looks like:* non-finite manifest coverage is treated as unavailable (`None`/JSON `null`), while measured `0.0` remains valid; add parameterized `NaN`/positive-infinity/negative-infinity regressions and parse emitted bytes with a strict JSON decoder that rejects non-standard constants. Prefer strict output encoding as a backstop so future numeric fields cannot silently emit non-RFC JSON.

*Dependencies/constraints:* preserve the existing malformed-manifest degradation and do not reject finite coverage solely for being integer-valued.

*Demonstrate:*
```bash
uv run pytest tests/test_hardening.py tests/test_contracts.py -k 'non_finite or strict_json' -v
# Expected: all three non-finite inputs report null/unknown coverage and every
# emitted status/whois/roster payload is accepted by the strict JSON parser.
```

### Verification

**W3 — P2 — Pin gate manifests in the subprocess determinism tests.**

*Evidence:* the layer contract requires tests to pin `dispatch.GATE_MANIFEST` so ambient fleet state cannot change results (`manuscript/layer_contract.yaml:31-35`; `tests/AGENTS.md:22-26`). The two repeat-run tests instead invoke fresh `scripts/bond.py` subprocesses through `_run_script`, which supplies no isolated manifest (`tests/test_scripts_smoke.py:10-22`, `:65-94`). Both commands read the real workspace manifest by default (`src/bond_cli/dispatch.py:56-63`, `:328-340`, `:506-525`), so a fleet gate writing between the two processes can make the determinism tests fail even though the CLI is deterministic.

*Done looks like:* each subprocess in the byte-identity comparisons uses the same real temporary gate manifest (with explicit absent and present cases as appropriate), while still exercising the actual script entry point and comparing raw stdout bytes. The test must not depend on whether `<bond root>/output/aggregate/gate_manifest.json` exists or changes.

*Dependencies/constraints:* retain separate-process execution and the zero-mock/real-manifest doctrine; do not weaken the assertions to parsed JSON equality or remove the determinism checks.

*Demonstrate:*
```bash
uv run pytest tests/test_scripts_smoke.py -k byte_identical -v
# Expected: both repeat-run tests pass with their temporary manifest pinned;
# inspection of the helpers shows no read of the ambient aggregate manifest.
```

**W4 — P2 — Align the exact development interpreter and regenerate stale lock metadata.**

*Evidence:* the development pin is the unpatched `3.15` (`.python-version:1`), rather than the preferred exact CPython `3.15.2`. The project declares `requires-python = ">=3.11"` (`pyproject.toml:20`), but the generated lock declares `>=3.10` and retains a `python_full_version < '3.11'` resolution branch (`uv.lock:3-7`), including a bond-cli NumPy 2.2.6 dependency for interpreters the project no longer supports (`uv.lock:71-80`). This leaves the checked-in environment metadata inconsistent with the manifest.

*Done looks like:* change `.python-version` from `3.15` to `3.15.2`, regenerate rather than hand-edit `uv.lock` from the current `pyproject.toml`, and confirm the lock's lower bound is `>=3.11` with no bond-cli pre-3.11 dependency fork. Keep the published package floor at `>=3.11`; the README's Python >=3.14 requirement is specifically for the PEP 649 test suite (`README.md:127-132`) and is not evidence for narrowing package runtime support.

*Dependencies/constraints:* requires the four declared sibling path sources and uv; no dependency version refresh is requested beyond what regeneration necessarily records.

*Demonstrate:*
```bash
uv lock --check && uv run python -c 'import platform; assert platform.python_version() == "3.15.2", platform.python_version()'
# Expected: the lock is current and the project interpreter reports exactly 3.15.2.
```

### Documentation

**W5 — P2 — Remove closed Round-2 findings from `Open work`.**

*Evidence:* C1, C2, V1, V2, and V3 are still presented as open defects/gaps (`TODO.md:15-127`), but the same file records C1/C2 as fixed under F3/F4 and V1/V2/V3 as closed with named regression tests (`TODO.md:279-318`). The final future-work list correctly retains only E1 and E2 (`TODO.md:342-346`). The contradictory sections make the backlog unsuitable for choosing remaining work.

*Done looks like:* remove or archive the five closed entries from `Open work`, preserve their Round-2 evidence, and leave genuinely open E1/E2 plus newly reviewed items visible exactly once. Update any stale source-line quotations moved into history rather than presenting them as current defects.

*Dependencies/constraints:* documentation only; do not close E1 or E2 or delete the mutation/regression evidence from Round 2.

*Demonstrate:*
```bash
python - <<'PY'
from pathlib import Path
text = Path('TODO.md').read_text(encoding='utf-8')
open_work = text.split('## Open work', 1)[1].split('## Known limitations', 1)[0]
for item in ('C1', 'C2', 'V1', 'V2', 'V3'):
    assert f'**{item} ' not in open_work, f'{item} is closed but still listed as open'
for item in ('E1', 'E2'):
    assert f'**{item} ' in open_work, f'{item} must remain open'
print('Open work matches the recorded closure state')
PY
# Expected: the probe exits 0 and prints the confirmation line.
```