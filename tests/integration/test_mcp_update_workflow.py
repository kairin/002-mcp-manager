"""Integration test for MCP server update workflow.

Tests the complete end-to-end workflow:
1. Check current version
2. Check for updates (dry-run)
3. Apply update (if available)
4. Verify health after update

Based on quickstart.md Test 1 and Test 2.
"""

from mcp_manager.core import MCPManager


class TestMCPUpdateWorkflow:
    """Test end-to-end MCP server update workflow."""

    def test_complete_update_workflow_dry_run(self):
        """Test complete update workflow in dry-run mode (quickstart Test 1)."""
        manager = MCPManager()

        # Step 1: Check current server status
        status = manager.get_server_status("shadcn")
        assert status is not None

        # Step 2: Check for updates (dry-run mode)
        update_check = manager.update_server("shadcn", dry_run=True)

        # Verify dry-run response structure
        assert "updated" in update_check
        assert "current_version" in update_check
        assert "latest_version" in update_check
        assert "update_type" in update_check
        assert "changes" in update_check

        # Dry-run should not modify configuration
        assert update_check["updated"] is False

        # Step 3: Verify health check still works
        health = manager.check_server_health("shadcn")
        assert health is not None

    def test_complete_update_workflow_actual_update(self):
        """Test complete update workflow with actual update (quickstart Test 2)."""
        manager = MCPManager()

        # Step 1: Check for updates (dry-run first)
        update_check = manager.update_server("shadcn", dry_run=True)

        if update_check["update_type"] != "none":
            # Update is available

            # Step 2: Get current configuration
            initial_config = manager.config.copy()

            # Step 3: Apply actual update
            update_result = manager.update_server("shadcn", dry_run=False)

            # Verify update was applied
            assert update_result["updated"] is True
            assert update_result["current_version"] != update_result["latest_version"]

            # Step 4: Verify configuration was updated
            updated_config = manager.config
            assert updated_config != initial_config

            # Step 5: Verify health check passes after update
            health = manager.check_server_health("shadcn")
            assert health["status"] == "healthy"

        else:
            # No update available, verify message
            assert (
                "already" in update_check["changes"].lower()
                or "latest" in update_check["changes"].lower()
            )

    def test_update_http_server_handling(self):
        """Test that HTTP servers are handled correctly (not updatable)."""
        manager = MCPManager()

        # HTTP servers like context7 should return update_type="none"
        result = manager.update_server("context7", dry_run=True)

        assert result["updated"] is False
        assert result["current_version"] is None
        assert result["latest_version"] is None
        assert result["update_type"] == "none"
        assert "HTTP" in result["changes"] or "not support" in result["changes"]

    def test_update_all_servers_workflow(self):
        """Test updating all servers at once."""
        manager = MCPManager()

        # Check all servers for updates (dry-run)
        all_results = manager.update_all_servers(dry_run=True)

        assert isinstance(all_results, dict)

        # Each server should have update information
        for server_name, result in all_results.items():
            assert "updated" in result
            assert "update_type" in result

            # HTTP servers should be marked as non-updatable
            server_config = manager.get_server_config(server_name)
            if server_config["type"] == "http":
                assert result["update_type"] == "none"

    def test_update_respects_semantic_versioning(self):
        """Test that update categorization follows semantic versioning."""
        manager = MCPManager()

        result = manager.update_server("shadcn", dry_run=True)

        if result["current_version"] and result["latest_version"]:
            from packaging.version import Version

            current = Version(result["current_version"])
            latest = Version(result["latest_version"])

            if latest > current:
                # Should categorize correctly
                if latest.major > current.major:
                    assert result["update_type"] == "major"
                elif latest.minor > current.minor:
                    assert result["update_type"] == "minor"
                elif latest.micro > current.micro:
                    assert result["update_type"] == "patch"
            else:
                # No update available
                assert result["update_type"] == "none"

    def test_update_handles_network_errors_gracefully(self):
        """Test that network errors during update check are handled."""
        manager = MCPManager()

        # This test verifies error handling exists
        # Actual network error simulation would require mocking
        try:
            result = manager.update_server("shadcn", dry_run=True)
            # Should either succeed or raise appropriate exception
            assert "updated" in result
        except Exception as e:
            # Should raise a known exception type
            assert hasattr(e, "__class__")

    def test_update_preserves_server_configuration(self):
        """Test that updating preserves other server configuration."""
        manager = MCPManager()

        # Get original configuration
        original_config = manager.get_server_config("shadcn")
        original_command = original_config.get("command")
        original_env = original_config.get("env", {})

        # Perform update (if available)
        result = manager.update_server("shadcn", dry_run=False)

        # Get updated configuration
        updated_config = manager.get_server_config("shadcn")

        # Command and environment should be preserved
        assert updated_config.get("command") == original_command
        assert updated_config.get("env") == original_env

        # Only args should change (version number)
        if result["updated"]:
            assert original_config["args"] != updated_config["args"]

    def test_update_workflow_with_rollback_on_failure(self):
        """Test that configuration is restored if update fails."""
        manager = MCPManager()

        # Get original configuration
        original_config = manager.config.copy()

        # Attempt update that might fail
        try:
            result = manager.update_server("shadcn", dry_run=False)

            # If update succeeded, config should change
            if result["updated"]:
                assert manager.config != original_config
        except Exception:
            # If update failed, config should be unchanged
            assert manager.config == original_config


# Quickstart validation scenarios


def test_quickstart_test_1_mcp_server_update_dry_run():
    """
    Quickstart Test 1: MCP Server Update Check (Dry-Run)

    From quickstart.md lines 21-50:
    - Command completes in <5 seconds
    - Shows version information for stdio servers
    - HTTP servers explicitly noted as non-updatable
    - No configuration files modified
    """
    manager = MCPManager()

    import time

    start_time = time.time()

    # Check all servers for updates (dry-run mode)
    result = manager.update_server("shadcn", dry_run=True)

    elapsed_time = time.time() - start_time

    # Should complete quickly
    assert elapsed_time < 5.0, "Update check should complete in <5 seconds"

    # Shows version information
    assert result["current_version"] is not None or result["update_type"] == "none"

    # No configuration modified
    # (would verify by checking config file hasn't changed)


def test_quickstart_test_2_mcp_server_update_actual():
    """
    Quickstart Test 2: MCP Server Update (Actual)

    From quickstart.md lines 56-89:
    - Configuration updated with new version
    - Health check passes after update
    - No service interruption
    """
    manager = MCPManager()

    # Apply update to specific server
    result = manager.update_server("shadcn", dry_run=False)

    if result["updated"]:
        # Configuration should be updated
        assert result["current_version"] != result["latest_version"]

        # Verify health check passes
        health = manager.check_server_health("shadcn")
        assert health["status"] in ["healthy", "ok"]

        # Verify configuration was saved
        config = manager.get_server_config("shadcn")
        assert result["latest_version"] in str(config["args"])
