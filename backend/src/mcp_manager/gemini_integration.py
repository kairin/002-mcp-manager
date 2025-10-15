"""Gemini CLI integration for MCP server synchronization.

Manages synchronization of MCP server configurations from Claude Code
to Google Gemini CLI, including configuration file management and
shell profile environment variable setup.
"""

import json
import os
from pathlib import Path
from typing import Any

from .exceptions import ConfigurationError, FileSystemError, ShellProfileError


class GeminiCLIIntegration:
    """Manages Gemini CLI configuration synchronization with Claude Code.

    Handles:
    - Reading Claude Code's ~/.claude.json configuration
    - Writing Gemini CLI's settings.json with identical structure
    - Detecting and updating shell profile for GEMINI_CLI_SYSTEM_SETTINGS_PATH
    - Preserving server configurations during sync operations
    """

    def __init__(
        self,
        claude_config_path: Path | None = None,
        gemini_config_path: Path | None = None,
    ):
        """Initialize Gemini CLI integration.

        Args:
            claude_config_path: Path to Claude Code config (default: ~/.claude.json)
            gemini_config_path: Path to Gemini CLI config (default: ~/.config/gemini/settings.json)
        """
        self.claude_config_path = claude_config_path or (Path.home() / ".claude.json")
        self.gemini_config_path = gemini_config_path or (
            Path.home() / ".config" / "gemini" / "settings.json"
        )

    def sync_from_claude(self, force: bool = False) -> dict[str, Any]:
        """Synchronize MCP servers from Claude Code to Gemini CLI.

        Reads Claude Code configuration and writes identical structure to
        Gemini CLI configuration file. Updates shell profile if needed.

        Args:
            force: Force overwrite existing Gemini configuration

        Returns:
            Dictionary with sync results:
            - success: bool
            - servers_synced: list[str]
            - config_path: str
            - env_var_configured: bool
            - shell_profile: str | None

        Raises:
            ConfigurationError: If Claude config is invalid or missing
            FileSystemError: If unable to write Gemini config
            ShellProfileError: If unable to update shell profile
        """
        # Read Claude Code configuration
        claude_config = self._read_claude_config()
        mcp_servers = claude_config.get("mcpServers", {})

        if not mcp_servers:
            return {
                "success": False,
                "servers_synced": [],
                "config_path": str(self.gemini_config_path),
                "env_var_configured": False,
                "shell_profile": None,
            }

        # Check if Gemini config exists and force flag
        if self.gemini_config_path.exists() and not force:
            # Merge existing Gemini config with Claude config
            try:
                with open(self.gemini_config_path) as f:
                    existing_config = json.load(f)
                # Preserve existing Gemini servers, add/update from Claude
                existing_servers = existing_config.get("mcpServers", {})
                existing_servers.update(mcp_servers)
                mcp_servers = existing_servers
            except Exception:
                # If can't read existing config, just use Claude config
                pass

        # Write Gemini configuration
        try:
            config_path = self._write_gemini_config(mcp_servers)
        except Exception as e:
            raise FileSystemError(
                f"Failed to write Gemini CLI configuration: {e}"
            ) from e

        # Detect and update shell profile
        shell_profile_path = self._detect_shell_profile()
        profile_updated = False

        if shell_profile_path:
            try:
                profile_updated = self._update_shell_profile(shell_profile_path)
            except Exception as e:
                raise ShellProfileError(f"Failed to update shell profile: {e}") from e

        # Only report shell_profile if we actually updated it
        shell_profile_str = (
            str(shell_profile_path)
            if (shell_profile_path and profile_updated)
            else None
        )

        return {
            "success": True,
            "servers_synced": list(mcp_servers.keys()),
            "config_path": str(config_path),
            "env_var_configured": profile_updated or self._is_env_var_configured(),
            "shell_profile": shell_profile_str,
        }

    def _read_claude_config(self) -> dict[str, Any]:
        """Read Claude Code configuration from ~/.claude.json.

        Returns:
            Dictionary with Claude Code configuration

        Raises:
            ConfigurationError: If config file doesn't exist or is invalid
        """
        if not self.claude_config_path.exists():
            raise ConfigurationError(
                f"Claude Code configuration not found at {self.claude_config_path}"
            )

        try:
            with open(self.claude_config_path) as f:
                config = json.load(f)

            if "mcpServers" not in config:
                raise ConfigurationError(
                    "Invalid Claude Code configuration: missing 'mcpServers' key"
                )

            return config

        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in Claude Code configuration: {e}"
            ) from e

    def _write_gemini_config(self, servers: dict[str, Any]) -> Path:
        """Write Gemini CLI configuration to settings.json.

        Args:
            servers: Dictionary of server name to server configuration

        Returns:
            Path to written configuration file

        Raises:
            FileSystemError: If unable to create directory or write file
        """
        try:
            # Ensure directory exists
            self.gemini_config_path.parent.mkdir(parents=True, exist_ok=True)

            # Create Gemini CLI configuration with identical structure to Claude
            gemini_config = {"mcpServers": servers}

            # Write configuration file
            with open(self.gemini_config_path, "w") as f:
                json.dump(gemini_config, f, indent=2)

            return self.gemini_config_path

        except PermissionError as e:
            raise FileSystemError(
                f"Permission denied writing to {self.gemini_config_path}"
            ) from e
        except OSError as e:
            raise FileSystemError(f"OS error writing Gemini configuration: {e}") from e

    def _detect_shell_profile(self) -> Path | None:
        """Detect the active shell profile file.

        Checks for common shell profiles in order:
        1. ~/.zshrc (Zsh)
        2. ~/.bashrc (Bash)
        3. ~/.bash_profile (Bash)
        4. ~/.profile (Generic)

        Returns:
            Path to detected shell profile or None if not found
        """
        home = Path.home()
        profiles = [
            home / ".zshrc",
            home / ".bashrc",
            home / ".bash_profile",
            home / ".profile",
        ]

        for profile in profiles:
            if profile.exists():
                return profile

        return None

    def _update_shell_profile(self, profile_path: Path) -> bool:
        """Update shell profile with GEMINI_CLI_SYSTEM_SETTINGS_PATH.

        Adds export statement to shell profile if not already present:
        export GEMINI_CLI_SYSTEM_SETTINGS_PATH="~/.config/gemini/settings.json"

        Args:
            profile_path: Path to shell profile file

        Returns:
            True if profile was updated, False if already configured

        Raises:
            ShellProfileError: If unable to read or write profile
        """
        export_line = 'export GEMINI_CLI_SYSTEM_SETTINGS_PATH="$HOME/.config/gemini/settings.json"'
        marker_comment = "# MCP Manager - Gemini CLI configuration"

        try:
            # Read existing profile
            with open(profile_path) as f:
                content = f.read()

            # Check if already configured
            if "GEMINI_CLI_SYSTEM_SETTINGS_PATH" in content:
                return False  # Already configured

            # Add export statement with marker comment
            with open(profile_path, "a") as f:
                f.write(f"\n{marker_comment}\n{export_line}\n")

            return True  # Profile updated

        except PermissionError as e:
            raise ShellProfileError(
                f"Permission denied updating shell profile: {profile_path}"
            ) from e
        except OSError as e:
            raise ShellProfileError(f"OS error updating shell profile: {e}") from e

    def _is_env_var_configured(self) -> bool:
        """Check if GEMINI_CLI_SYSTEM_SETTINGS_PATH environment variable is set.

        Returns:
            True if environment variable is set in current shell
        """
        return "GEMINI_CLI_SYSTEM_SETTINGS_PATH" in os.environ

    def get_status(self) -> dict[str, Any]:
        """Get current Gemini CLI integration status.

        Returns:
            Dictionary with status information:
            - claude_config_exists: bool
            - gemini_config_exists: bool
            - env_var_configured: bool
            - servers_count: int
        """
        servers_count = 0
        if self.gemini_config_path.exists():
            try:
                with open(self.gemini_config_path) as f:
                    config = json.load(f)
                    servers_count = len(config.get("mcpServers", {}))
            except Exception:
                pass

        return {
            "claude_config_exists": self.claude_config_path.exists(),
            "gemini_config_exists": self.gemini_config_path.exists(),
            "env_var_configured": self._is_env_var_configured(),
            "servers_count": servers_count,
        }
