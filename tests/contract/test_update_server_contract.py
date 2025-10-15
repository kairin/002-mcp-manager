"""Contract test for update_server API.

Tests that the update_server method matches the API contract defined in
contracts/update_server.yaml
"""

import pytest
from mcp_manager.core import MCPManager
from mcp_manager.exceptions import (
    ServerNotFoundError,
)


class TestUpdateServerContract:
    """Verify update_server API matches contract specification."""

    def test_update_server_accepts_server_name_and_dry_run(self):
        """Test that update_server accepts required and optional parameters."""
        manager = MCPManager()

        # Should accept server_name (required) and dry_run (optional)
        # This will fail until implementation exists
        result = manager.update_server("shadcn", dry_run=True)

        assert result is not None

    def test_update_server_returns_required_fields(self):
        """Test that update_server returns all contract-defined output fields."""
        manager = MCPManager()

        # Attempt dry-run update
        result = manager.update_server("shadcn", dry_run=True)

        # Contract-defined output fields
        assert "updated" in result
        assert isinstance(result["updated"], bool)

        assert "current_version" in result
        # Can be string or None

        assert "latest_version" in result
        # Can be string or None

        assert "update_type" in result
        assert result["update_type"] in ["major", "minor", "patch", "none"]

        assert "changes" in result
        # Can be string or None

    def test_update_server_raises_server_not_found_error(self):
        """Test ServerNotFoundError when server doesn't exist."""
        manager = MCPManager()

        with pytest.raises(ServerNotFoundError):
            manager.update_server("nonexistent_server", dry_run=True)

    def test_update_server_handles_http_servers(self):
        """Test that HTTP servers return update_type='none'."""
        manager = MCPManager()

        # HTTP servers like context7 should not be updatable
        result = manager.update_server("context7", dry_run=True)

        assert result["updated"] is False
        assert result["current_version"] is None
        assert result["latest_version"] is None
        assert result["update_type"] == "none"
        assert "HTTP" in result["changes"] or "not support" in result["changes"]

    def test_update_server_dry_run_does_not_modify_config(self):
        """Test that dry_run=True does not actually update configuration."""
        manager = MCPManager()

        # Get initial config
        initial_config = manager.config.copy()

        # Run dry-run update
        result = manager.update_server("shadcn", dry_run=True)

        # Config should be unchanged
        assert manager.config == initial_config
        assert result["updated"] is False

    def test_update_server_actual_update_modifies_config(self):
        """Test that dry_run=False actually updates configuration if update available."""
        manager = MCPManager()

        # First check if update is available (dry-run)
        check_result = manager.update_server("shadcn", dry_run=True)

        if check_result["update_type"] != "none":
            # Update is available, apply it
            update_result = manager.update_server("shadcn", dry_run=False)

            assert "updated" in update_result
            # Should have modified config if update was applied

    def test_update_server_categorizes_semver_correctly(self):
        """Test that update_type correctly categorizes semantic versions."""
        manager = MCPManager()

        result = manager.update_server("shadcn", dry_run=True)

        # update_type must be one of the enum values
        assert result["update_type"] in ["major", "minor", "patch", "none"]

        # If versions are different, update_type should not be "none"
        if (
            result["current_version"]
            and result["latest_version"]
            and result["current_version"] != result["latest_version"]
        ):
            assert result["update_type"] in ["major", "minor", "patch"]


# Contract examples verification


def test_contract_example_dry_run():
    """Verify example from contract: dry-run update check."""
    manager = MCPManager()

    result = manager.update_server("shadcn", dry_run=True)

    # Should match contract example output structure
    assert isinstance(result["updated"], bool)
    assert result["update_type"] in ["major", "minor", "patch", "none"]


def test_contract_example_no_update_available():
    """Verify example from contract: no update available."""
    manager = MCPManager()

    result = manager.update_server("shadcn", dry_run=True)

    if result["current_version"] == result["latest_version"]:
        assert result["updated"] is False
        assert result["update_type"] == "none"
        assert (
            "latest" in result["changes"].lower()
            or "already" in result["changes"].lower()
        )


def test_contract_example_http_server():
    """Verify example from contract: HTTP server not updatable."""
    manager = MCPManager()

    result = manager.update_server("context7", dry_run=False)

    assert result["updated"] is False
    assert result["current_version"] is None
    assert result["latest_version"] is None
    assert result["update_type"] == "none"
    assert "HTTP" in result["changes"] or "not support" in result["changes"]
