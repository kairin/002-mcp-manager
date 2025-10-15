"""Contract tests for 'mcp-manager validate uv' CLI command."""

import json
import subprocess


def test_validate_uv_success():
    """Contract: validate uv returns exit 0 when [tool.uv] configured correctly"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "uv"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "UV configuration validation: PASS" in result.stdout
    assert "3.13" in result.stdout


def test_validate_uv_json_output():
    """Contract: --json flag produces valid JSON"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "uv", "--json"],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert "check_name" in data
    assert data["check_name"] == "uv_configuration"
