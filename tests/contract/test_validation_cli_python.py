"""Contract tests for 'mcp-manager validate python' CLI command."""
import subprocess
import json
import pytest


def test_validate_python_success():
    """Contract: validate python returns exit 0 when Python 3.13+ detected"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "python"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Python version validation: PASS" in result.stdout
    assert "3.13" in result.stdout


def test_validate_python_json_output():
    """Contract: --json flag produces valid JSON"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "python", "--json"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    assert "check_name" in data
    assert "passed" in data
    assert data["check_name"] == "python_version"
