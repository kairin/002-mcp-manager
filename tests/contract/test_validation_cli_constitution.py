"""Contract tests for 'mcp-manager validate constitution' CLI command."""
import subprocess
import json
import pytest


def test_validate_constitution_all_principles():
    """Contract: validate constitution checks all 9 principles"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "constitution"],
        capture_output=True,
        text=True
    )
    assert "Constitution validation:" in result.stdout
    assert "Principles validated:" in result.stdout


def test_validate_constitution_specific_principle():
    """Contract: --principle flag validates single principle"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "constitution", "--principle", "7"],
        capture_output=True,
        text=True
    )
    assert ("7. Cross-Platform Compatibility" in result.stdout or
            "VII. Cross-Platform Compatibility" in result.stdout or
            "Principle VII" in result.stdout)


def test_validate_constitution_json_output():
    """Contract: --json flag produces valid JSON"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "constitution", "--json"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    assert "check_name" in data
    assert "principle_results" in data or "principles_validated" in data
