"""Core MCP server management with system Python 3.13 enforcement.

This module implements Tasks T049-T051 from Phase 6 (User Story 4):
- T049: Update MCP server launcher to use system Python 3.13 path
- T050: Add Python environment validation for MCP server launches
- T051: Add logging for MCP server Python executable path

References:
    - spec.md: FR-008 (MCP servers use system Python 3.13)
    - tasks.md: Phase 6 - User Story 4
    - CLAUDE.md: MCP server management requirements
"""

import json
import logging
from pathlib import Path
from typing import Any

from .exceptions import (
    ConfigurationError,
    PythonEnvironmentError,
    ServerNotFoundError,
)
from .python_env import (
    detect_distribution,
    find_system_python,
    get_installation_instructions,
    get_installation_source,
    is_python_313,
)
from .uv_config import validate_uv_config

# Setup logging
logger = logging.getLogger(__name__)


class MCPManager:
    """Manages MCP servers with system Python 3.13 enforcement.

    Implements FR-008: Ensure MCP servers use system Python 3.13 when applicable.

    Constitutional Requirements:
    - All stdio servers using Python must use system Python 3.13
    - No additional Python interpreters may be downloaded or installed
    - UV configuration must enforce python-preference="only-system"
    """

    def __init__(self):
        """Initialize MCP Manager with Python environment validation.

        Raises:
            PythonEnvironmentError: If system Python 3.13 not found or UV misconfigured
        """
        self.home_dir = Path.home()
        self.claude_config_path = self.home_dir / ".claude.json"

        # T050: Validate Python environment on initialization
        self._validate_python_environment()

    def _validate_python_environment(self) -> None:
        """Validate system Python 3.13 and UV configuration.

        Implements T050: Python environment validation for MCP server launches.

        Raises:
            PythonEnvironmentError: If validation fails
        """
        # Find system Python 3.13
        python_path = find_system_python()

        if python_path is None:
            distro = detect_distribution()
            instructions = get_installation_instructions()
            raise PythonEnvironmentError(
                f"System Python 3.13 not found on {distro}.\n"
                f"Constitutional requirement: mcp-manager requires Python 3.13 system installation.\n"
                f"{instructions}"
            )

        if not is_python_313(python_path):
            distro = detect_distribution()
            instructions = get_installation_instructions()
            raise PythonEnvironmentError(
                f"Found Python at {python_path} but it is not version 3.13.x.\n"
                f"Constitutional requirement: Only Python 3.13 is allowed.\n"
                f"Detected system: {distro}\n"
                f"{instructions}"
            )

        # T051: Log Python executable path for auditing
        source = get_installation_source(python_path)
        logger.info(
            f"MCP Manager using system Python 3.13: {python_path} (source: {source})"
        )

        # Store validated Python path
        self._system_python_path = python_path

        # Validate UV configuration
        project_root = Path.cwd()
        uv_config = validate_uv_config(project_root)

        if uv_config.get("python_downloads") not in ("manual", "never"):
            raise PythonEnvironmentError(
                f"UV configuration violation: python-downloads={uv_config.get('python_downloads')}.\n"
                f"Constitutional requirement: Must be 'manual' or 'never' to prevent Python downloads.\n\n"
                f"To fix, ensure uv.toml contains:\n"
                f"    [tool.uv]\n"
                f'    python-downloads = "never"\n\n'
                f"Then remove any global UV config conflicts:\n"
                f"    mv ~/.config/uv/uv.toml ~/.config/uv/uv.toml.backup\n\n"
                f"Troubleshooting guide: docs/PYTHON-TROUBLESHOOTING.md"
            )

        if uv_config.get("python_preference") != "only-system":
            raise PythonEnvironmentError(
                f"UV configuration violation: python-preference={uv_config.get('python_preference')}.\n"
                f"Constitutional requirement: Must be 'only-system' to enforce system Python usage.\n\n"
                f"To fix, ensure uv.toml contains:\n"
                f"    [tool.uv]\n"
                f'    python-preference = "only-system"\n\n'
                f"Then remove any global UV config conflicts:\n"
                f"    mv ~/.config/uv/uv.toml ~/.config/uv/uv.toml.backup\n\n"
                f"Troubleshooting guide: docs/PYTHON-TROUBLESHOOTING.md"
            )

    def get_system_python_path(self) -> Path:
        """Get validated system Python 3.13 path.

        Returns:
            Path to system Python 3.13 executable

        Implements T049: Provide system Python path for MCP server launchers.
        """
        return self._system_python_path

    def init_global_config(self, force: bool = False) -> None:
        """Initialize global MCP configuration.

        Args:
            force: Overwrite existing configuration if True

        Raises:
            ConfigurationError: If config exists and force=False
        """
        if self.claude_config_path.exists() and not force:
            raise ConfigurationError(
                f"Configuration already exists at {self.claude_config_path}. "
                "Use force=True to overwrite."
            )

        # Create default configuration
        config = {"mcpServers": {}}

        self.claude_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.claude_config_path, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(
            f"Initialized global MCP configuration at {self.claude_config_path}"
        )

    def init_project_config(self, force: bool = False) -> None:
        """Initialize project-local MCP configuration.

        Args:
            force: Overwrite existing configuration if True

        Raises:
            ConfigurationError: If config exists and force=False
        """
        project_config_path = Path.cwd() / ".claude" / "config.json"

        if project_config_path.exists() and not force:
            raise ConfigurationError(
                f"Project configuration already exists at {project_config_path}. "
                "Use force=True to overwrite."
            )

        # Create default configuration
        config = {"mcpServers": {}}

        project_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(project_config_path, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Initialized project MCP configuration at {project_config_path}")

    def add_server(
        self,
        name: str,
        server_type: str,
        url: str | None = None,
        command: str | None = None,
        args: list[str] | None = None,
        headers: dict[str, str] | None = None,
        env: dict[str, str] | None = None,
        global_config: bool = True,
    ) -> None:
        """Add MCP server with Python 3.13 enforcement.

        Implements T049: For stdio servers using Python, configure UV to use system Python 3.13.

        Args:
            name: Server name
            server_type: 'http' or 'stdio'
            url: Server URL (for HTTP servers)
            command: Command to run (for stdio servers)
            args: Command arguments
            headers: HTTP headers
            env: Environment variables
            global_config: Use global config if True, project config if False

        Raises:
            ConfigurationError: If invalid server configuration
        """
        if server_type not in ("http", "stdio"):
            raise ConfigurationError(
                f"Invalid server type: {server_type}. Must be 'http' or 'stdio'."
            )

        # Load existing config
        config_path = (
            self.claude_config_path
            if global_config
            else Path.cwd() / ".claude" / "config.json"
        )

        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
        else:
            config = {"mcpServers": {}}

        # Build server configuration
        server_config: dict[str, Any] = {"type": server_type}

        if server_type == "http":
            if not url:
                raise ConfigurationError("HTTP servers require 'url' parameter")
            server_config["url"] = url
            server_config["headers"] = headers or {}

        elif server_type == "stdio":
            if not command:
                raise ConfigurationError("stdio servers require 'command' parameter")

            # T049: For Python-based stdio servers, use UV with system Python 3.13
            # UV respects uv.toml configuration (python-preference="only-system")
            if command in ("python", "python3", "python3.13"):
                # Replace direct Python command with UV-managed execution
                # This ensures constitutional compliance (system Python 3.13 only)
                logger.warning(
                    f"Server '{name}' uses direct Python command. "
                    f"Replacing with UV-managed execution for constitutional compliance."
                )
                server_config["command"] = "uv"
                server_config["args"] = ["run", str(self._system_python_path)] + (
                    args or []
                )

                # T051: Log Python executable path
                logger.info(
                    f"MCP server '{name}' configured to use system Python 3.13: {self._system_python_path}"
                )
            else:
                server_config["command"] = command
                server_config["args"] = args or []

                # Log non-Python stdio servers
                logger.info(
                    f"MCP server '{name}' uses command '{command}' (non-Python stdio server)"
                )

            server_config["env"] = env or {}

        # Add server to config
        config["mcpServers"][name] = server_config

        # Save config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        scope = "global" if global_config else "project"
        logger.info(f"Added MCP server '{name}' to {scope} configuration")

    def remove_server(self, name: str, global_config: bool = True) -> None:
        """Remove MCP server from configuration.

        Args:
            name: Server name to remove
            global_config: Use global config if True, project config if False

        Raises:
            ServerNotFoundError: If server not found in configuration
        """
        config_path = (
            self.claude_config_path
            if global_config
            else Path.cwd() / ".claude" / "config.json"
        )

        if not config_path.exists():
            raise ServerNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path) as f:
            config = json.load(f)

        if name not in config.get("mcpServers", {}):
            raise ServerNotFoundError(f"Server '{name}' not found in configuration")

        del config["mcpServers"][name]

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        scope = "global" if global_config else "project"
        logger.info(f"Removed MCP server '{name}' from {scope} configuration")

    def get_global_servers(self) -> dict[str, Any]:
        """Get all global MCP servers.

        Returns:
            Dictionary of server configurations
        """
        if not self.claude_config_path.exists():
            return {}

        with open(self.claude_config_path) as f:
            config = json.load(f)

        return config.get("mcpServers", {})

    def audit_configurations(self, detailed: bool = False) -> dict[str, Any]:
        """Audit MCP configurations (placeholder).

        Args:
            detailed: Include detailed analysis if True

        Returns:
            Audit results dictionary
        """
        # Placeholder implementation
        return {"status": "ok", "details": "Audit not yet implemented"}

    def check_server_health(self, name: str, timeout: int = 5) -> dict[str, Any]:
        """Check MCP server health (placeholder).

        Args:
            name: Server name
            timeout: Connection timeout in seconds

        Returns:
            Health status dictionary
        """
        # Placeholder implementation
        return {"status": "unknown", "details": "Health check not yet implemented"}

    def check_all_servers_health(self, timeout: int = 5) -> dict[str, Any]:
        """Check health of all MCP servers (placeholder).

        Args:
            timeout: Connection timeout in seconds

        Returns:
            Dictionary of health statuses by server name
        """
        servers = self.get_global_servers()
        return {
            name: self.check_server_health(name, timeout) for name in servers.keys()
        }

    def update_server(self, name: str, dry_run: bool = False) -> dict[str, Any]:
        """Update MCP server (placeholder).

        Args:
            name: Server name
            dry_run: Show what would be updated without making changes

        Returns:
            Update result dictionary
        """
        # Placeholder implementation
        return {"updated": False, "details": "Update not yet implemented"}

    def update_all_servers(self, dry_run: bool = False) -> dict[str, Any]:
        """Update all MCP servers (placeholder).

        Args:
            dry_run: Show what would be updated without making changes

        Returns:
            Dictionary of update results by server name
        """
        servers = self.get_global_servers()
        return {name: self.update_server(name, dry_run) for name in servers.keys()}

    def diagnose_server(self, name: str, verbose: bool = False) -> dict[str, Any]:
        """Diagnose MCP server issues (placeholder).

        Args:
            name: Server name
            verbose: Include verbose diagnostics if True

        Returns:
            Diagnosis results dictionary
        """
        # Placeholder implementation
        return {"status": "unknown", "details": "Diagnosis not yet implemented"}

    def diagnose_all_servers(self, verbose: bool = False) -> dict[str, Any]:
        """Diagnose all MCP servers (placeholder).

        Args:
            verbose: Include verbose diagnostics if True

        Returns:
            Dictionary of diagnosis results by server name
        """
        servers = self.get_global_servers()
        return {name: self.diagnose_server(name, verbose) for name in servers.keys()}

    def migrate_project_to_global(self, create_backup: bool = True) -> dict[str, Any]:
        """Migrate project MCP configurations to global (placeholder).

        Args:
            create_backup: Create backup before migration if True

        Returns:
            Migration results dictionary
        """
        # Placeholder implementation
        return {"success": False, "details": "Migration not yet implemented"}
