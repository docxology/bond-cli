"""Subprocess smoke tests for the thin scripts/ wrappers (real subprocess)."""

from __future__ import annotations

import json
import subprocess
import sys

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
