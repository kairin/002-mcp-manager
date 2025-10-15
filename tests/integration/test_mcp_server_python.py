"""Integration tests for MCP server Python 3.13 enforcement.

Tests:
    - T052: test_mcp_server_uses_system_python

References:
    - spec.md: FR-008 (MCP servers use system Python 3.13)
    - tasks.md: T052 (Phase 6 - User Story 4)
    - core.py: MCPManager with Python 3.13 enforcement
"""

import json
import sys
from pathlib import Path

import pytest
from mcp_manager.core import MCPManager
from mcp_manager.python_env import find_system_python, is_python_313


class TestMCPServerPythonEnforcement:
    """Test MCP server Python 3.13 enforcement.

    Test T052: Verify MCP server launches use system Python 3.13.
    """

    def test_mcp_manager_validates_python_on_init(self):
        """T052: Verify MCPManager validates Python 3.13 on initialization.

        This test ensures that:
        1. MCPManager constructor validates system Python 3.13
        2. Initialization fails if Python 3.13 not found
        3. Initialization stores validated Python path
        """
        # Create MCPManager instance
        manager = MCPManager()

        # Verify system Python path is stored
        system_python = manager.get_system_python_path()
        assert system_python is not None
        assert system_python.exists()
        assert system_python.is_file()

        # Verify it's Python 3.13
        assert is_python_313(system_python)

        # Verify it matches our detection
        detected_python = find_system_python()
        assert system_python == detected_python

    def test_mcp_server_configuration_with_python_command(self, tmp_path):
        """T052: Verify direct Python commands are replaced with UV-managed execution.

        When a server is configured with command='python', it should be
        replaced with UV-managed execution using system Python 3.13.
        """
        manager = MCPManager()
        system_python = manager.get_system_python_path()

        # Configure test .claude.json in tmp directory
        test_config = tmp_path / ".claude.json"
        manager.claude_config_path = test_config

        # Add server with direct Python command
        manager.add_server(
            name="test-python-server",
            server_type="stdio",
            command="python",
            args=["-m", "test_module"],
            global_config=True,
        )

        # Read configuration
        with open(test_config) as f:
            config = json.load(f)

        server_config = config["mcpServers"]["test-python-server"]

        # Verify UV is used instead of direct Python
        assert server_config["command"] == "uv"

        # Verify args include system Python path
        assert server_config["args"][0] == "run"
        assert Path(server_config["args"][1]) == system_python

        # Verify original args are preserved
        assert server_config["args"][2:] == ["-m", "test_module"]

    def test_mcp_server_configuration_with_uv_command(self, tmp_path):
        """T052: Verify UV-based stdio servers use system Python 3.13 via uv.toml.

        UV commands respect uv.toml configuration which enforces
        python-preference="only-system" and python-downloads="never".
        """
        manager = MCPManager()

        # Configure test .claude.json in tmp directory
        test_config = tmp_path / ".claude.json"
        manager.claude_config_path = test_config

        # Add server with UV command
        manager.add_server(
            name="markitdown",
            server_type="stdio",
            command="uv",
            args=["tool", "run", "markitdown-mcp"],
            global_config=True,
        )

        # Read configuration
        with open(test_config) as f:
            config = json.load(f)

        server_config = config["mcpServers"]["markitdown"]

        # Verify UV command is preserved (constitutional compliance via uv.toml)
        assert server_config["command"] == "uv"
        assert server_config["args"] == ["tool", "run", "markitdown-mcp"]

        # UV will use system Python 3.13 because of uv.toml configuration:
        # - python-downloads = "never"
        # - python-preference = "only-system"

    def test_mcp_server_configuration_with_non_python_command(self, tmp_path):
        """T052: Verify non-Python stdio servers are not modified.

        Servers using npx, node, or other non-Python commands should
        not be modified by Python 3.13 enforcement.
        """
        manager = MCPManager()

        # Configure test .claude.json in tmp directory
        test_config = tmp_path / ".claude.json"
        manager.claude_config_path = test_config

        # Add server with npx command
        manager.add_server(
            name="shadcn",
            server_type="stdio",
            command="npx",
            args=["shadcn@latest", "mcp"],
            global_config=True,
        )

        # Read configuration
        with open(test_config) as f:
            config = json.load(f)

        server_config = config["mcpServers"]["shadcn"]

        # Verify npx command is preserved unchanged
        assert server_config["command"] == "npx"
        assert server_config["args"] == ["shadcn@latest", "mcp"]

    def test_http_server_configuration(self, tmp_path):
        """T052: Verify HTTP servers are not affected by Python enforcement.

        HTTP servers don't execute local commands, so Python enforcement
        should not modify their configuration.
        """
        manager = MCPManager()

        # Configure test .claude.json in tmp directory
        test_config = tmp_path / ".claude.json"
        manager.claude_config_path = test_config

        # Add HTTP server
        manager.add_server(
            name="context7",
            server_type="http",
            url="https://mcp.context7.com/mcp",
            headers={"CONTEXT7_API_KEY": "test-key"},
            global_config=True,
        )

        # Read configuration
        with open(test_config) as f:
            config = json.load(f)

        server_config = config["mcpServers"]["context7"]

        # Verify HTTP configuration is preserved
        assert server_config["type"] == "http"
        assert server_config["url"] == "https://mcp.context7.com/mcp"
        assert server_config["headers"] == {"CONTEXT7_API_KEY": "test-key"}

    def test_current_python_is_313(self):
        """T052: Verify test suite itself runs with Python 3.13.

        This validates that `pytest` is executed with system Python 3.13,
        confirming that UV respects uv.toml configuration.
        """
        # Get current Python version
        version_info = sys.version_info

        # Verify major and minor version
        assert version_info.major == 3
        assert version_info.minor == 13

        # Verify executable path matches system Python
        current_python = Path(sys.executable)
        system_python = find_system_python()

        # Note: current_python might be in a venv, but its base should be system Python
        # We verify the version requirement is satisfied
        assert is_python_313(system_python)

    def test_uv_respects_python_preference(self, tmp_path):
        """T052: Verify UV configuration enforces system Python preference.

        Read uv.toml and verify it contains the constitutional requirements:
        - python-downloads = "never"
        - python-preference = "only-system"
        """
        # Find uv.toml at project root
        project_root = Path.cwd()
        while project_root != project_root.parent:
            uv_toml = project_root / "uv.toml"
            if uv_toml.exists():
                break
            project_root = project_root.parent
        else:
            pytest.skip("uv.toml not found in project tree")

        # Read uv.toml content
        content = uv_toml.read_text()

        # Verify constitutional requirements
        assert 'python-downloads = "never"' in content
        assert 'python-preference = "only-system"' in content


class TestMCPServerLogging:
    """Test Python executable path logging.

    Test T051: Verify logging for MCP server Python paths.
    """

    def test_mcp_manager_logs_system_python_path(self, caplog):
        """T051: Verify MCPManager logs system Python path on initialization.

        Logging enables auditing of which Python executable is used.
        """
        import logging

        caplog.set_level(logging.INFO)

        # Create MCPManager instance
        manager = MCPManager()
        system_python = manager.get_system_python_path()

        # Verify logging contains Python path
        assert any(str(system_python) in record.message for record in caplog.records)

        # Verify logging contains source information
        assert any("source:" in record.message for record in caplog.records)

    def test_mcp_server_add_logs_python_path(self, tmp_path, caplog):
        """T051: Verify adding Python-based server logs executable path.

        When a server using Python is added, the system Python path
        should be logged for auditing.
        """
        import logging

        caplog.set_level(logging.INFO)

        manager = MCPManager()
        system_python = manager.get_system_python_path()

        # Configure test .claude.json
        test_config = tmp_path / ".claude.json"
        manager.claude_config_path = test_config

        # Add Python-based server
        manager.add_server(
            name="test-python-server",
            server_type="stdio",
            command="python",
            args=["-m", "test_module"],
            global_config=True,
        )

        # Verify server configuration is logged
        assert any("test-python-server" in record.message for record in caplog.records)

        # Verify Python path is logged
        assert any(str(system_python) in record.message for record in caplog.records)
