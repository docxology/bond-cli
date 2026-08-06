"""Subprocess smoke tests for the thin scripts/ wrappers (real subprocess)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import PROJECT_ROOT


def _run_script(name, *args):
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / name), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )


def test_bond_list_smoke():
    result = _run_script("bond.py", "list")
    assert result.returncode == 0, result.stderr
    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    assert len(lines) == 27  # the full film roster


def test_bond_status_smoke():
    result = _run_script("bond.py", "status")
    assert result.returncode == 0, result.stderr
    assert "total films: 27" in result.stdout


def test_bond_missions_smoke():
    result = _run_script("bond.py", "missions")
    assert result.returncode == 0, result.stderr
    assert "OPERATION_OMNIBUS" in result.stdout


def test_bond_whois_smoke():
    result = _run_script("bond.py", "whois", "goldfinger")
    assert result.returncode == 0, result.stderr
    assert "GRAND SLAM" in result.stdout


def test_bond_roster_export_smoke():
    result = _run_script("bond.py", "roster-export")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["total"] == 27


def test_z_generate_manuscript_variables_smoke():
    result = _run_script("z_generate_manuscript_variables.py")
    assert result.returncode == 0, result.stderr
    out_path = PROJECT_ROOT / "output" / "variables" / "manuscript_variables.json"
    assert out_path.exists()
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["CODENAME"] == "THE FRONT DOOR"


# --------------------------------------------------------------------------- #
# V1 — byte-identical repeat runs (the determinism claim in the manuscript)
# --------------------------------------------------------------------------- #
# Two invocations against an unchanged fleet are byte-identical.  Run each in
# a fresh subprocess so a wall-clock field that *happened* to land on the same
# value within one process cannot hide; separate processes are milliseconds
# apart, so any ``generated_at: time.time()`` makes them differ.


def _run_two_scripts_byte_identical(name, *args):
    first = _run_script(name, *args)
    second = _run_script(name, *args)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout, (
        f"{' '.join((name, *args))} not byte-identical"
    )
    return first


def test_status_json_byte_identical_repeat():
    first = _run_two_scripts_byte_identical("bond.py", "status", "--json")
    assert json.loads(first.stdout)["schema_version"] == 1


def test_roster_export_byte_identical_repeat():
    first = _run_two_scripts_byte_identical("bond.py", "roster-export")
    assert json.loads(first.stdout)["total"] == 27


# --------------------------------------------------------------------------- #
# V2 — the installed ``bond`` console script is exercised (not just scripts/)
# --------------------------------------------------------------------------- #


def _run_console(*args):
    exe = Path(sys.executable)
    console = exe.with_name("bond")
    return subprocess.run(
        [str(console), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )


def test_console_script_matches_bootstrapper():
    """``pyproject.toml: [project.scripts] bond = \"bond_cli.dispatch:main\"``
    is a real entry point: the installed ``bond`` console script must exist and
    produce the same stdout + returncode as ``scripts/bond.py`` for the same
    argv (README: "both returning the same exit codes").
    """
    console = _run_console("list")
    assert console.returncode == 0, console.stderr
    bootstrap = _run_script("bond.py", "list")
    assert bootstrap.returncode == 0, bootstrap.stderr
    assert console.stdout == bootstrap.stdout
    assert console.returncode == bootstrap.returncode
