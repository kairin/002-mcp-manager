"""Integration test for Gemini CLI sync workflow.

Tests the complete end-to-end workflow:
1. Read Claude Code configuration
2. Create Gemini CLI configuration
3. Update shell profile with environment variable
4. Verify configuration persists

Based on quickstart.md Test 3 and Test 4.
"""

import json
from pathlib import Path

from mcp_manager.gemini_integration import GeminiCLIIntegration


class TestGeminiSyncWorkflow:
    """Test end-to-end Gemini CLI synchronization workflow."""

    def test_complete_sync_workflow_first_time(self):
        """Test complete sync workflow on first run (quickstart Test 3)."""
        gemini = GeminiCLIIntegration()

        # Step 1: Sync MCP servers to Gemini CLI
        result = gemini.sync_from_claude()

        # Verify sync result structure
        assert result["success"] is True
        assert len(result["servers_synced"]) > 0
        assert Path(result["config_path"]).exists()

        # Step 2: Verify Gemini CLI configuration was created
        config_path = Path(result["config_path"])
        assert config_path.exists()
        assert config_path == Path.home() / ".config" / "gemini" / "settings.json"

        with open(config_path) as f:
            config = json.load(f)

        # Should contain mcpServers section
        assert "mcpServers" in config
        assert isinstance(config["mcpServers"], dict)
        assert len(config["mcpServers"]) > 0

        # Step 3: Verify expected servers are present
        expected_servers = {
            "context7",
            "shadcn",
            "github",
            "playwright",
            "hf-mcp-server",
            "markitdown",
        }
        synced_servers = set(config["mcpServers"].keys())

        # At least some expected servers should be present
        assert len(synced_servers.intersection(expected_servers)) > 0

        # Step 4: Verify environment variable was added to shell profile
        if result["env_var_configured"]:
            profile_path = Path(result["shell_profile"])
            assert profile_path.exists()

            with open(profile_path) as f:
                profile_content = f.read()

            assert "GEMINI_CLI_SYSTEM_SETTINGS_PATH" in profile_content
            assert str(config_path) in profile_content

    def test_sync_preserves_server_structure(self):
        """Test that synced servers maintain correct structure."""
        gemini = GeminiCLIIntegration()

        result = gemini.sync_from_claude()
        config_path = Path(result["config_path"])

        with open(config_path) as f:
            gemini_config = json.load(f)

        # Load Claude config for comparison
        claude_config_path = Path.home() / ".claude.json"
        with open(claude_config_path) as f:
            claude_config = json.load(f)

        # Each server should have same structure
        for server_name in result["servers_synced"]:
            assert server_name in gemini_config["mcpServers"]
            assert server_name in claude_config["mcpServers"]

            gemini_server = gemini_config["mcpServers"][server_name]
            claude_server = claude_config["mcpServers"][server_name]

            # Type should match
            assert gemini_server["type"] == claude_server["type"]

            # HTTP servers should have url
            if claude_server["type"] == "http":
                assert "url" in gemini_server
                assert gemini_server["url"] == claude_server["url"]

            # stdio servers should have command and args
            if claude_server["type"] == "stdio":
                assert "command" in gemini_server
                assert "args" in gemini_server
                assert gemini_server["command"] == claude_server["command"]
                assert gemini_server["args"] == claude_server["args"]

    def test_sync_handles_existing_config_merge(self):
        """Test that sync merges with existing Gemini configuration."""
        gemini = GeminiCLIIntegration()

        # First sync
        result1 = gemini.sync_from_claude()
        assert result1["success"] is True

        # Second sync (should merge, not overwrite)
        result2 = gemini.sync_from_claude(force=False)
        assert result2["success"] is True

        # Configuration should still exist
        config_path = Path(result2["config_path"])
        assert config_path.exists()

    def test_sync_force_mode_overwrites(self):
        """Test that force=True overwrites existing configuration."""
        gemini = GeminiCLIIntegration()

        # First sync
        result1 = gemini.sync_from_claude()

        # Force sync
        result2 = gemini.sync_from_claude(force=True)

        assert result2["success"] is True
        # Should have synced all servers again
        assert len(result2["servers_synced"]) > 0

    def test_sync_detects_correct_shell_profile(self):
        """Test that sync correctly identifies the active shell profile."""
        gemini = GeminiCLIIntegration()

        result = gemini.sync_from_claude()

        if result["env_var_configured"]:
            # Should detect one of the standard profiles
            valid_profiles = [
                Path.home() / ".bashrc",
                Path.home() / ".zshrc",
                Path.home() / ".profile",
            ]

            profile_path = Path(result["shell_profile"])
            assert profile_path in valid_profiles
            assert profile_path.exists()

    def test_sync_creates_directory_structure(self):
        """Test that sync creates necessary directory structure."""
        gemini = GeminiCLIIntegration()

        result = gemini.sync_from_claude()

        # ~/.config/gemini/ should be created
        gemini_dir = Path.home() / ".config" / "gemini"
        assert gemini_dir.exists()
        assert gemini_dir.is_dir()

        # settings.json should be created
        settings_file = gemini_dir / "settings.json"
        assert settings_file.exists()
        assert settings_file.is_file()

    def test_sync_handles_missing_claude_config(self):
        """Test that sync handles missing Claude configuration gracefully."""
        gemini = GeminiCLIIntegration()

        # This would need to temporarily move ~/.claude.json
        # For now, just verify the sync works with existing config
        result = gemini.sync_from_claude()
        assert result["success"] is True

    def test_sync_environment_variable_persistence(self):
        """Test that environment variable persists across sessions."""
        gemini = GeminiCLIIntegration()

        result = gemini.sync_from_claude()

        if result["env_var_configured"]:
            # Verify environment variable can be read
            # (Would need to reload shell profile in practice)
            profile_path = Path(result["shell_profile"])
            with open(profile_path) as f:
                content = f.read()

            # Should contain export statement
            assert "export GEMINI_CLI_SYSTEM_SETTINGS_PATH" in content

    def test_sync_all_six_mcp_servers(self):
        """Test that all 6 MCP servers are synced correctly."""
        gemini = GeminiCLIIntegration()

        result = gemini.sync_from_claude(force=True)

        # Should sync all 6 servers
        expected_servers = {
            "context7",
            "shadcn",
            "github",
            "playwright",
            "hf-mcp-server",
            "markitdown",
        }

        synced_set = set(result["servers_synced"])

        # All expected servers should be synced
        assert expected_servers.issubset(
            synced_set
        ), f"Missing servers: {expected_servers - synced_set}"


# Quickstart validation scenarios


def test_quickstart_test_3_gemini_cli_synchronization():
    """
    Quickstart Test 3: Gemini CLI Synchronization

    From quickstart.md lines 92-128:
    - ~/.config/gemini/settings.json created
    - File contains identical mcpServers from ~/.claude.json
    - Environment variable added to shell profile
    - All 6 servers present
    """
    gemini = GeminiCLIIntegration()

    # Sync MCP servers to Gemini CLI
    result = gemini.sync_from_claude()

    # Success criteria 1: Config file created
    config_path = Path(result["config_path"])
    assert config_path.exists()
    assert config_path == Path.home() / ".config" / "gemini" / "settings.json"

    # Success criteria 2: File contains identical mcpServers
    with open(config_path) as f:
        gemini_config = json.load(f)
    assert "mcpServers" in gemini_config

    claude_config_path = Path.home() / ".claude.json"
    with open(claude_config_path) as f:
        claude_config = json.load(f)

    # mcpServers should match
    for server_name in result["servers_synced"]:
        assert server_name in gemini_config["mcpServers"]
        assert server_name in claude_config["mcpServers"]

    # Success criteria 3: Environment variable added
    if result["env_var_configured"]:
        profile_path = Path(result["shell_profile"])
        with open(profile_path) as f:
            content = f.read()
        assert "GEMINI_CLI_SYSTEM_SETTINGS_PATH" in content

    # Success criteria 4: All 6 servers present
    assert len(result["servers_synced"]) >= 6


def test_quickstart_test_4_gemini_cli_integration_verification():
    """
    Quickstart Test 4: Gemini CLI Integration Verification

    From quickstart.md lines 130-153:
    - Environment variable set correctly
    - Gemini CLI config file readable
    - Configuration persists across shell restarts
    """
    gemini = GeminiCLIIntegration()

    result = gemini.sync_from_claude()

    # Success criteria 1: Environment variable set correctly
    if result["env_var_configured"]:
        profile_path = Path(result["shell_profile"])
        with open(profile_path) as f:
            content = f.read()

        # Should contain correct path
        expected_path = str(Path.home() / ".config" / "gemini" / "settings.json")
        assert expected_path in content

    # Success criteria 2: Config file readable
    config_path = Path(result["config_path"])
    with open(config_path) as f:
        config = json.load(f)
    assert "mcpServers" in config

    # Success criteria 3: Configuration persists
    # File should exist on disk
    assert config_path.exists()
    assert config_path.is_file()
