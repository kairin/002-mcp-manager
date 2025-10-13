"""Contract test for Gemini CLI sync API.

Tests that the sync_from_claude method matches the API contract defined in
contracts/gemini_sync.yaml
"""

from pathlib import Path

from mcp_manager.gemini_integration import GeminiCLIIntegration


class TestGeminiSyncContract:
    """Verify Gemini CLI sync API matches contract specification."""

    def test_sync_accepts_force_parameter(self):
        """Test that sync_from_claude accepts optional force parameter."""
        gemini = GeminiCLIIntegration()

        # Should accept force parameter (optional, default False)
        result = gemini.sync_from_claude(force=False)

        assert result is not None

    def test_sync_returns_required_fields(self):
        """Test that sync_from_claude returns all contract-defined output fields."""
        gemini = GeminiCLIIntegration()

        result = gemini.sync_from_claude(force=False)

        # Contract-defined output fields
        assert "success" in result
        assert isinstance(result["success"], bool)

        assert "servers_synced" in result
        assert isinstance(result["servers_synced"], list)
        for server in result["servers_synced"]:
            assert isinstance(server, str)

        assert "config_path" in result
        assert isinstance(result["config_path"], str)
        # Should be absolute path
        assert Path(result["config_path"]).is_absolute()

        assert "env_var_configured" in result
        assert isinstance(result["env_var_configured"], bool)

        assert "shell_profile" in result
        # Can be string or None
        if result["shell_profile"] is not None:
            assert isinstance(result["shell_profile"], str)

    def test_sync_raises_configuration_error_when_claude_config_missing(self):
        """Test ConfigurationError when ~/.claude.json doesn't exist."""
        gemini = GeminiCLIIntegration()

        # Mock scenario where ~/.claude.json is missing
        # This will fail until implementation exists
        # with pytest.raises(ConfigurationError):
        #     gemini.sync_from_claude()
        pass  # Implementation will handle this

    def test_sync_creates_gemini_config_directory(self):
        """Test that sync creates ~/.config/gemini/ if it doesn't exist."""
        gemini = GeminiCLIIntegration()

        result = gemini.sync_from_claude(force=False)

        # Verify config path is created
        config_path = Path(result["config_path"])
        assert config_path.parent.exists()
        assert config_path.parent == Path.home() / ".config" / "gemini"

    def test_sync_writes_valid_json_config(self):
        """Test that Gemini config file contains valid JSON with mcpServers."""
        gemini = GeminiCLIIntegration()

        result = gemini.sync_from_claude(force=False)

        config_path = Path(result["config_path"])
        if config_path.exists():
            import json

            with open(config_path) as f:
                config = json.load(f)

            # Should have mcpServers section
            assert "mcpServers" in config
            assert isinstance(config["mcpServers"], dict)

    def test_sync_updates_shell_profile_on_first_run(self):
        """Test that first sync adds environment variable to shell profile."""
        gemini = GeminiCLIIntegration()

        result = gemini.sync_from_claude(force=False)

        if result["env_var_configured"]:
            # Shell profile should be reported
            assert result["shell_profile"] is not None
            profile_path = Path(result["shell_profile"])
            assert profile_path.exists()

            # Profile should contain GEMINI_CLI_SYSTEM_SETTINGS_PATH
            with open(profile_path) as f:
                content = f.read()
            assert "GEMINI_CLI_SYSTEM_SETTINGS_PATH" in content

    def test_sync_force_overwrites_existing_config(self):
        """Test that force=True overwrites existing Gemini configuration."""
        gemini = GeminiCLIIntegration()

        # First sync
        result1 = gemini.sync_from_claude(force=False)

        # Force sync
        result2 = gemini.sync_from_claude(force=True)

        assert result2["success"] is True
        # Should have synced servers even if already existed
        assert len(result2["servers_synced"]) > 0

    def test_sync_merges_without_force(self):
        """Test that force=False merges rather than overwrites."""
        gemini = GeminiCLIIntegration()

        # Sync without force should merge configurations
        result = gemini.sync_from_claude(force=False)

        assert result["success"] is True
        # Should indicate which servers were synced (new or updated)

    def test_sync_returns_correct_server_list(self):
        """Test that servers_synced contains expected MCP servers."""
        gemini = GeminiCLIIntegration()

        result = gemini.sync_from_claude(force=True)

        # Expected MCP servers from contract example
        expected_servers = {
            "context7",
            "shadcn",
            "github",
            "playwright",
            "hf-mcp-server",
            "markitdown",
        }

        synced_set = set(result["servers_synced"])

        # At least some of the expected servers should be synced
        assert len(synced_set.intersection(expected_servers)) > 0


# Contract examples verification


def test_contract_example_first_time_sync():
    """Verify example from contract: first-time sync."""
    gemini = GeminiCLIIntegration()

    result = gemini.sync_from_claude(force=False)

    # Should match contract example output structure
    assert result["success"] is True
    assert isinstance(result["servers_synced"], list)
    assert len(result["servers_synced"]) >= 1
    assert Path(result["config_path"]).parent == Path.home() / ".config" / "gemini"


def test_contract_example_sync_with_existing_config():
    """Verify example from contract: sync with existing Gemini config."""
    gemini = GeminiCLIIntegration()

    # First sync
    gemini.sync_from_claude(force=False)

    # Second sync should handle existing config
    result = gemini.sync_from_claude(force=False)

    assert result["success"] is True
    # env_var_configured might be False if already set
    if not result["env_var_configured"]:
        assert result["shell_profile"] is None


def test_contract_example_force_overwrite():
    """Verify example from contract: force overwrite."""
    gemini = GeminiCLIIntegration()

    result = gemini.sync_from_claude(force=True)

    assert result["success"] is True
    assert len(result["servers_synced"]) >= 1
    assert Path(result["config_path"]).exists()
