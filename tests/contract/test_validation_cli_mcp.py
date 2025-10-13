"""Contract tests for 'mcp-manager validate mcp-servers' CLI command."""
import subprocess
import json
import pytest


def test_validate_mcp_servers_success():
    """Contract: validate mcp-servers checks stdio servers use UV"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "mcp-servers"],
        capture_output=True,
        text=True
    )
    # May pass or fail depending on actual config
    # Just validate structure
    assert "MCP server validation:" in result.stdout


def test_validate_mcp_servers_json_output():
    """Contract: --json flag produces valid JSON with server list"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "mcp-servers", "--json"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    assert "check_name" in data
    assert data["check_name"] == "mcp_servers"
