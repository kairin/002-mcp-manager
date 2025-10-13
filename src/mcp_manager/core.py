"""Core MCP Manager functionality."""

import json
import subprocess
import time
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console

from .exceptions import (
    ConfigurationError,
    InvalidPathError,
    MCPManagerError,
    ServerNotFoundError,
    UpdateCheckError,
)
from .models import AuditConfiguration
from .utils import (
    check_npm_package_version,
    compare_versions,
    extract_package_name_from_args,
    extract_version_from_args,
    update_args_with_version,
)


class MCPManager:
    """Core MCP Manager for server configuration and health monitoring."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self.home_dir = Path.home()
        self.claude_config_path = self.home_dir / ".claude.json"
        self._config_cache: dict[str, Any] | None = None

    @property
    def config(self) -> dict[str, Any]:
        """Get current global configuration."""
        if not self.claude_config_path.exists():
            return {"mcpServers": {}, "version": "1.0"}

        with open(self.claude_config_path) as f:
            return json.load(f)

    def get_server_config(self, name: str) -> dict[str, Any]:
        """Get configuration for a specific server."""
        servers = self.config.get("mcpServers", {})
        if name not in servers:
            raise ServerNotFoundError(f"Server '{name}' not found in configuration")
        return servers[name]

    def get_server_status(self, name: str) -> dict[str, Any]:
        """Get status information for a specific server."""
        return self.check_server_health(name)

    def init_global_config(self, force: bool = False) -> None:
        """Initialize global MCP configuration."""
        if self.claude_config_path.exists() and not force:
            self.console.print(
                "[yellow]Global configuration already exists. Use --force to overwrite.[/yellow]"
            )
            return

        # Create basic configuration structure
        config = {"mcpServers": {}, "version": "1.0"}

        # Ensure directory exists
        self.claude_config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.claude_config_path, "w") as f:
            json.dump(config, f, indent=2)

        self.console.print(
            f"[green]✅ Global configuration initialized at {self.claude_config_path}[/green]"
        )

    def init_project_config(self, force: bool = False) -> None:
        """Initialize project-specific MCP configuration."""
        project_config_path = Path.cwd() / ".claude.json"

        if project_config_path.exists() and not force:
            self.console.print(
                "[yellow]Project configuration already exists. Use --force to overwrite.[/yellow]"
            )
            return

        config = {"mcpServers": {}, "version": "1.0"}

        with open(project_config_path, "w") as f:
            json.dump(config, f, indent=2)

        self.console.print(
            f"[green]✅ Project configuration initialized at {project_config_path}[/green]"
        )

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
        """Add a new MCP server configuration."""
        try:
            # Validate server type
            if server_type not in ["http", "stdio"]:
                raise ConfigurationError(f"Invalid server type: {server_type}")

            # Create server configuration
            server_config = {"type": server_type}

            if server_type == "http":
                if not url:
                    raise ConfigurationError("URL is required for HTTP servers")
                server_config["url"] = url
                if headers:
                    server_config["headers"] = headers

            elif server_type == "stdio":
                if not command:
                    raise ConfigurationError("Command is required for stdio servers")
                server_config["command"] = command
                if args:
                    server_config["args"] = args

            if env:
                server_config["env"] = env

            # Choose configuration file
            config_path = (
                self.claude_config_path
                if global_config
                else Path.cwd() / ".claude.json"
            )

            # Load existing configuration
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
            else:
                config = {"mcpServers": {}, "version": "1.0"}

            # Add server
            config["mcpServers"][name] = server_config

            # Save configuration
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            raise MCPManagerError(f"Failed to add server {name}: {e}")

    def remove_server(self, name: str, global_config: bool = True) -> None:
        """Remove an MCP server configuration."""
        config_path = (
            self.claude_config_path if global_config else Path.cwd() / ".claude.json"
        )

        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")

        with open(config_path) as f:
            config = json.load(f)

        if name not in config.get("mcpServers", {}):
            raise ServerNotFoundError(f"Server '{name}' not found in configuration")

        del config["mcpServers"][name]

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    def list_servers(self, global_config: bool = True) -> dict[str, Any]:
        """List all configured MCP servers."""
        config_path = (
            self.claude_config_path if global_config else Path.cwd() / ".claude.json"
        )

        if not config_path.exists():
            return {}

        with open(config_path) as f:
            config = json.load(f)

        return config.get("mcpServers", {})

    def get_global_servers(self) -> dict[str, Any]:
        """Get all globally configured MCP servers."""
        return self.list_servers(global_config=True)

    def check_server_health(self, name: str, timeout: int = 5) -> dict[str, Any]:
        """Check health of a specific MCP server."""
        servers = self.list_servers()
        if name not in servers:
            raise ServerNotFoundError(f"Server '{name}' not found")

        server_config = servers[name]
        server_type = server_config.get("type")

        result = {
            "name": name,
            "status": "unknown",
            "response_time": None,
            "details": "",
        }

        try:
            start_time = time.time()

            if server_type == "http":
                url = server_config.get("url")
                headers = server_config.get("headers", {})

                response = httpx.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()

                result["status"] = "healthy"
                result["details"] = f"HTTP {response.status_code}"

            elif server_type == "stdio":
                command = server_config.get("command")
                args = server_config.get("args", [])
                env = server_config.get("env", {})

                # Test if command exists
                process = subprocess.run(
                    [command] + args,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env={**subprocess.os.environ, **env},
                )

                result["status"] = "healthy" if process.returncode == 0 else "unhealthy"
                result["details"] = f"Exit code: {process.returncode}"

            result["response_time"] = time.time() - start_time

        except Exception as e:
            result["status"] = "unhealthy"
            result["details"] = str(e)

        return result

    def check_all_servers_health(self, timeout: int = 5) -> dict[str, Any]:
        """Check health of all configured MCP servers."""
        servers = self.list_servers()
        results = {}

        for name in servers.keys():
            try:
                results[name] = self.check_server_health(name, timeout)
            except Exception as e:
                results[name] = {
                    "name": name,
                    "status": "unhealthy",
                    "response_time": None,
                    "details": str(e),
                }

        return results

    def audit_configurations(
        self, config: AuditConfiguration | None = None, detailed: bool = False
    ) -> dict[str, Any]:
        """Audit MCP configurations across projects.

        Args:
            config: AuditConfiguration with custom search paths (optional)
            detailed: Include detailed information about each project

        Returns:
            Dictionary with audit results including search_paths_used
        """
        # Use provided config or create default
        if config is None:
            config = AuditConfiguration()

        # Get paths to scan
        search_dirs = config.get_paths_to_scan()

        # Validate custom paths if requested (only validate if custom paths provided)
        if config.validate_paths and config.search_directories is not None:
            validated_dirs = []
            for search_dir in search_dirs:
                if not search_dir.exists():
                    raise InvalidPathError(
                        f"Search directory does not exist: {search_dir}"
                    )
                validated_dirs.append(search_dir)
            search_dirs = validated_dirs

        # For default paths, just filter out non-existent ones (don't raise errors)
        elif config.search_directories is None:
            search_dirs = [d for d in search_dirs if d.exists()]

        audit_results = {
            "global_config": {
                "exists": self.claude_config_path.exists(),
                "servers": (
                    len(self.list_servers()) if self.claude_config_path.exists() else 0
                ),
                "status": "ok" if self.claude_config_path.exists() else "missing",
            },
            "project_configs": {},
            "search_paths_used": [str(p) for p in search_dirs],
        }

        # Find project-specific configurations
        for search_dir in search_dirs:
            if search_dir.exists():
                for project_dir in search_dir.iterdir():
                    if project_dir.is_dir():
                        project_config = project_dir / ".claude.json"
                        if project_config.exists():
                            try:
                                with open(project_config) as f:
                                    config = json.load(f)

                                project_name = f"{search_dir.name}/{project_dir.name}"
                                audit_results["project_configs"][project_name] = {
                                    "servers": len(config.get("mcpServers", {})),
                                    "path": str(project_config),
                                    "status": (
                                        "needs_migration"
                                        if config.get("mcpServers")
                                        else "empty"
                                    ),
                                }
                            except Exception as e:
                                audit_results["project_configs"][project_dir.name] = {
                                    "servers": 0,
                                    "path": str(project_config),
                                    "status": f"error: {e}",
                                }

        return audit_results

    def update_server(self, name: str, dry_run: bool = False) -> dict[str, Any]:
        """Update a specific MCP server.

        Checks for updates to npm-based MCP servers and optionally applies them.
        HTTP servers are not updatable and will return update_type="none".

        Args:
            name: Server name to update
            dry_run: If True, check for updates without applying (default: False)

        Returns:
            Dict with update status matching update_server.yaml contract:
            {
                "updated": bool,
                "current_version": str | None,
                "latest_version": str | None,
                "update_type": "major" | "minor" | "patch" | "none",
                "changes": str | None
            }

        Raises:
            ServerNotFoundError: If server doesn't exist
            UpdateCheckError: If version check fails

        Implementation for T018.
        """
        # Get server configuration
        server_config = self.get_server_config(name)
        server_type = server_config.get("type")

        # HTTP servers are not updatable
        if server_type == "http":
            return {
                "updated": False,
                "current_version": None,
                "latest_version": None,
                "update_type": "none",
                "changes": "HTTP servers do not support version updates",
            }

        # stdio servers - check for npm package updates
        if server_type == "stdio":
            command = server_config.get("command")
            args = server_config.get("args", [])

            # Only npm-based servers are updatable
            if command not in ["npx", "npm"]:
                return {
                    "updated": False,
                    "current_version": None,
                    "latest_version": None,
                    "update_type": "none",
                    "changes": f"Only npm-based servers are updatable (command: {command})",
                }

            # Extract package name and current version
            package_name = extract_package_name_from_args(args)
            if not package_name:
                return {
                    "updated": False,
                    "current_version": None,
                    "latest_version": None,
                    "update_type": "none",
                    "changes": "Could not extract package name from args",
                }

            current_version = extract_version_from_args(args)

            # Check if using a tag like "@latest"
            using_tag = False
            if not current_version:
                # Check if args contain a tag like "@latest", "@next", etc.
                for arg in args:
                    if "@" in arg and not arg.startswith("@"):
                        parts = arg.split("@")
                        if len(parts) == 2 and not parts[1][0].isdigit():
                            using_tag = True
                            break

            # Check for latest version
            try:
                latest_version = check_npm_package_version(package_name)
            except UpdateCheckError as e:
                raise UpdateCheckError(f"Failed to check updates for {name}: {e}")

            if not latest_version:
                return {
                    "updated": False,
                    "current_version": current_version,
                    "latest_version": None,
                    "update_type": "none",
                    "changes": f"Package {package_name} not found in npm registry",
                }

            # Compare versions
            if current_version:
                update_available, update_type = compare_versions(
                    current_version, latest_version
                )
            elif using_tag:
                # Using a tag like @latest - pin to specific version
                update_available = True
                update_type = "minor"  # Conservative default
                current_version = (
                    "latest"  # Set current_version to "latest" for display
                )
            else:
                # No version specified at all - treat as update available
                update_available = True
                update_type = "minor"  # Conservative default

            # If no update available
            if not update_available:
                return {
                    "updated": False,
                    "current_version": current_version,
                    "latest_version": latest_version,
                    "update_type": "none",
                    "changes": "Already at latest version",
                }

            # Dry-run mode - report what would be updated
            if dry_run:
                return {
                    "updated": False,
                    "current_version": current_version,
                    "latest_version": latest_version,
                    "update_type": update_type,
                    "changes": "New version available (dry-run mode)",
                }

            # Apply update
            try:
                # Update args with new version
                new_args = update_args_with_version(args, latest_version)

                # Load configuration
                config = self.config.copy()

                # Update server configuration
                config["mcpServers"][name]["args"] = new_args

                # Save updated configuration
                with open(self.claude_config_path, "w") as f:
                    json.dump(config, f, indent=2)

                # Verify health after update
                try:
                    health = self.check_server_health(name, timeout=10)
                    if health["status"] != "healthy":
                        # Rollback on health check failure
                        with open(self.claude_config_path, "w") as f:
                            json.dump(self.config, f, indent=2)

                        return {
                            "updated": False,
                            "current_version": current_version,
                            "latest_version": latest_version,
                            "update_type": update_type,
                            "changes": f"Update failed health check, rolled back: {health['details']}",
                        }
                except Exception:
                    # Health check failed, but update was applied
                    pass

                return {
                    "updated": True,
                    "current_version": current_version,
                    "latest_version": latest_version,
                    "update_type": update_type,
                    "changes": f"Updated from {current_version} to {latest_version}",
                }

            except Exception as e:
                raise MCPManagerError(f"Failed to apply update for {name}: {e}")

        # Unknown server type
        return {
            "updated": False,
            "current_version": None,
            "latest_version": None,
            "update_type": "none",
            "changes": f"Unknown server type: {server_type}",
        }

    def update_all_servers(self, dry_run: bool = False) -> dict[str, Any]:
        """Update all MCP servers.

        Iterates through all configured servers and checks/applies updates.
        Only stdio servers with npm command are updatable.

        Args:
            dry_run: If True, check for updates without applying (default: False)

        Returns:
            Dict mapping server names to their update status:
            {
                "server1": {"updated": bool, "current_version": str, ...},
                "server2": {...},
                ...
            }

        Implementation for T019.
        """
        servers = self.list_servers()
        results = {}

        for name in servers.keys():
            try:
                results[name] = self.update_server(name, dry_run)
            except Exception as e:
                results[name] = {
                    "updated": False,
                    "current_version": None,
                    "latest_version": None,
                    "update_type": "none",
                    "changes": f"Error checking updates: {e}",
                }

        return results

    def diagnose_server(self, name: str, verbose: bool = False) -> dict[str, Any]:
        """Diagnose issues with a specific MCP server."""
        diagnosis = {}

        try:
            # Check if server exists in configuration
            servers = self.list_servers()
            if name not in servers:
                diagnosis["configuration"] = {
                    "status": "fail",
                    "details": "Server not found in configuration",
                }
                return diagnosis

            server_config = servers[name]
            diagnosis["configuration"] = {
                "status": "pass",
                "details": "Server found in configuration",
            }

            # Check configuration validity
            server_type = server_config.get("type")
            if server_type == "http":
                if "url" in server_config:
                    diagnosis["url_check"] = {
                        "status": "pass",
                        "details": f"URL configured: {server_config['url']}",
                    }
                else:
                    diagnosis["url_check"] = {
                        "status": "fail",
                        "details": "URL not configured for HTTP server",
                    }
            elif server_type == "stdio":
                if "command" in server_config:
                    diagnosis["command_check"] = {
                        "status": "pass",
                        "details": f"Command configured: {server_config['command']}",
                    }
                else:
                    diagnosis["command_check"] = {
                        "status": "fail",
                        "details": "Command not configured for stdio server",
                    }

            # Check connectivity
            health_result = self.check_server_health(name)
            diagnosis["connectivity"] = {
                "status": "pass" if health_result["status"] == "healthy" else "fail",
                "details": health_result["details"],
            }

        except Exception as e:
            diagnosis["error"] = {"status": "fail", "details": str(e)}

        return diagnosis

    def diagnose_all_servers(self, verbose: bool = False) -> dict[str, Any]:
        """Diagnose all configured MCP servers."""
        servers = self.list_servers()
        results = {}

        for name in servers.keys():
            results[name] = self.diagnose_server(name, verbose)

        return results

    def migrate_project_to_global(self, create_backup: bool = True) -> dict[str, Any]:
        """Migrate project-specific MCP configurations to global."""
        migration_results = {}

        search_dirs = [
            self.home_dir / "Apps",
            self.home_dir / "projects",
            self.home_dir / "repos",
        ]

        # Load global configuration
        global_config = {}
        if self.claude_config_path.exists():
            with open(self.claude_config_path) as f:
                global_config = json.load(f)
        else:
            global_config = {"mcpServers": {}, "version": "1.0"}

        for search_dir in search_dirs:
            if search_dir.exists():
                for project_dir in search_dir.iterdir():
                    if project_dir.is_dir():
                        project_config_path = project_dir / ".claude.json"
                        if project_config_path.exists():
                            try:
                                with open(project_config_path) as f:
                                    project_config = json.load(f)

                                project_servers = project_config.get("mcpServers", {})
                                if project_servers:
                                    # Create backup if requested
                                    if create_backup:
                                        backup_path = project_config_path.with_suffix(
                                            ".json.backup"
                                        )
                                        with open(backup_path, "w") as f:
                                            json.dump(project_config, f, indent=2)

                                    # Migrate servers to global configuration
                                    migrated_servers = []
                                    for (
                                        server_name,
                                        server_config,
                                    ) in project_servers.items():
                                        global_config["mcpServers"][
                                            server_name
                                        ] = server_config
                                        migrated_servers.append(server_name)

                                    # Clear project configuration
                                    project_config["mcpServers"] = {}
                                    with open(project_config_path, "w") as f:
                                        json.dump(project_config, f, indent=2)

                                    project_name = (
                                        f"{search_dir.name}/{project_dir.name}"
                                    )
                                    migration_results[project_name] = {
                                        "success": True,
                                        "servers": migrated_servers,
                                        "backup_created": create_backup,
                                    }

                            except Exception as e:
                                project_name = f"{search_dir.name}/{project_dir.name}"
                                migration_results[project_name] = {
                                    "success": False,
                                    "error": str(e),
                                }

        # Save updated global configuration
        with open(self.claude_config_path, "w") as f:
            json.dump(global_config, f, indent=2)

        return migration_results
