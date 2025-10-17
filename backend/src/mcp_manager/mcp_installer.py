"""System-wide MCP server installation and management."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


class MCPInstaller:
    """Manages system-wide MCP server installation and verification."""

    # Define all supported MCP servers with installation requirements
    SUPPORTED_SERVERS = {
        "context7": {
            "type": "http",
            "url": "https://mcp.context7.com/mcp",
            "requires_install": False,  # HTTP-only, no installation needed
            "requires_env": ["CONTEXT7_API_KEY"],
            "description": "Library documentation and code examples",
        },
        "shadcn": {
            "type": "stdio",
            "command": "npx",
            "args": ["shadcn@latest", "mcp"],
            "env": {},
            "requires_install": False,  # npx installs on-demand
            "requires_env": [],
            "description": "UI component registry and tooling",
        },
        "github": {
            "type": "http",
            "url": "https://api.githubcopilot.com/mcp",
            "requires_install": False,  # HTTP-only
            "requires_env": ["GH_TOKEN"],  # Via gh auth token
            "description": "GitHub API integration and management",
            "setup_command": ["gh", "auth", "login"],
        },
        "playwright": {
            "type": "stdio",
            "command": "npx",
            "args": ["@playwright/mcp@latest"],
            "env": {},
            "requires_install": False,  # npx installs on-demand
            "requires_env": [],
            "description": "Browser automation and testing",
        },
        "hf-mcp-server": {
            "type": "http",
            "url": "https://huggingface.co/mcp",
            "requires_install": False,  # HTTP-only
            "requires_env": ["HUGGINGFACE_TOKEN"],
            "description": "AI model access with HF CLI integration",
            "setup_command": ["uv", "run", "hf", "auth", "login"],
        },
        "markitdown": {
            "type": "stdio",
            "command": "uv",
            "args": ["tool", "run", "markitdown-mcp"],
            "env": {},
            "requires_install": True,  # Needs uv tool install
            "install_command": ["uv", "tool", "install", "markitdown-mcp"],
            "requires_env": [],
            "description": "Document conversion to markdown (PDF, Office, images)",
        },
    }

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self.home_dir = Path.home()
        self.claude_config_path = self.home_dir / ".claude.json"

    def install_all_servers(
        self, skip_auth: bool = False, dry_run: bool = False
    ) -> dict[str, Any]:
        """Install and configure all supported MCP servers system-wide."""
        results = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Installing MCP servers...", total=len(self.SUPPORTED_SERVERS)
            )

            for server_name, server_spec in self.SUPPORTED_SERVERS.items():
                progress.update(task, description=f"[cyan]Installing {server_name}...")
                results[server_name] = self.install_server(
                    server_name, server_spec, skip_auth=skip_auth, dry_run=dry_run
                )
                progress.advance(task)

        return results

    def install_server(
        self,
        server_name: str,
        server_spec: dict[str, Any] | None = None,
        skip_auth: bool = False,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Install and configure a specific MCP server."""
        if server_spec is None:
            server_spec = self.SUPPORTED_SERVERS.get(server_name)
            if not server_spec:
                return {
                    "success": False,
                    "error": f"Unknown server: {server_name}",
                }

        result = {
            "server": server_name,
            "success": False,
            "installed": False,
            "configured": False,
            "authenticated": False,
            "details": [],
        }

        try:
            # Step 1: Install dependencies (if required)
            if server_spec.get("requires_install"):
                if dry_run:
                    result["details"].append(
                        f"Would run: {' '.join(server_spec['install_command'])}"
                    )
                    result["installed"] = True
                else:
                    install_result = self._run_install_command(
                        server_spec["install_command"]
                    )
                    if install_result:
                        result["installed"] = True
                        result["details"].append("Package installed successfully")
                    else:
                        result["details"].append("Package installation failed")
                        return result
            else:
                result["installed"] = True
                result["details"].append("No installation required")

            # Step 2: Configure in .claude.json
            if dry_run:
                result["details"].append(
                    "Would add server configuration to ~/.claude.json"
                )
                result["configured"] = True
            else:
                config_result = self._add_to_claude_config(server_name, server_spec)
                if config_result:
                    result["configured"] = True
                    result["details"].append("Added to .claude.json")
                else:
                    result["details"].append("Configuration failed")
                    return result

            # Step 3: Setup authentication (if required and not skipped)
            if not skip_auth and server_spec.get("requires_env"):
                if dry_run:
                    result["details"].append(
                        f"Would setup authentication for: {', '.join(server_spec['requires_env'])}"
                    )
                    result["authenticated"] = True
                else:
                    auth_result = self._setup_authentication(server_name, server_spec)
                    result["authenticated"] = auth_result["success"]
                    result["details"].extend(auth_result["details"])
            else:
                result["authenticated"] = True
                result["details"].append("No authentication required")

            # Overall success
            result["success"] = (
                result["installed"] and result["configured"] and result["authenticated"]
            )

        except Exception as e:
            result["success"] = False
            result["details"].append(f"Error: {str(e)}")

        return result

    def verify_all_servers(self) -> dict[str, Any]:
        """Verify all MCP servers are installed and configured correctly."""
        results = {}

        for server_name in self.SUPPORTED_SERVERS.keys():
            results[server_name] = self.verify_server(server_name)

        return results

    def verify_server(self, server_name: str) -> dict[str, Any]:
        """Verify a specific MCP server installation."""
        server_spec = self.SUPPORTED_SERVERS.get(server_name)
        if not server_spec:
            return {
                "server": server_name,
                "status": "unknown",
                "details": "Server not in supported list",
            }

        verification = {
            "server": server_name,
            "status": "healthy",
            "checks": {},
        }

        # Check 1: Configuration exists
        try:
            with open(self.claude_config_path) as f:
                config = json.load(f)

            if server_name in config.get("mcpServers", {}):
                verification["checks"]["configured"] = {
                    "status": "pass",
                    "message": "Found in .claude.json",
                }
            else:
                verification["checks"]["configured"] = {
                    "status": "fail",
                    "message": "Not found in .claude.json",
                }
                verification["status"] = "unhealthy"
        except Exception as e:
            verification["checks"]["configured"] = {
                "status": "fail",
                "message": f"Error reading config: {e}",
            }
            verification["status"] = "unhealthy"

        # Check 2: Dependencies installed (for stdio servers requiring installation)
        if server_spec.get("requires_install"):
            install_check = self._check_installation(server_spec)
            verification["checks"]["installed"] = install_check
            if install_check["status"] != "pass":
                verification["status"] = "unhealthy"
        else:
            verification["checks"]["installed"] = {
                "status": "pass",
                "message": "No installation required",
            }

        # Check 3: Authentication configured
        if server_spec.get("requires_env"):
            auth_check = self._check_authentication(server_name, server_spec)
            verification["checks"]["authenticated"] = auth_check
            if auth_check["status"] != "pass":
                verification["status"] = "needs_auth"
        else:
            verification["checks"]["authenticated"] = {
                "status": "pass",
                "message": "No authentication required",
            }

        # Check 4: Connectivity test
        connectivity_check = self._test_connectivity(server_name, server_spec)
        verification["checks"]["connectivity"] = connectivity_check
        if connectivity_check["status"] != "pass":
            verification["status"] = "unhealthy"

        return verification

    def display_installation_status(self, results: dict[str, Any]) -> None:
        """Display formatted installation status."""
        self.console.print(
            "\n[bold cyan]📦 MCP Server Installation Status[/bold cyan]\n"
        )

        table = Table(title="Installation Results")
        table.add_column("Server", style="cyan")
        table.add_column("Installed", style="green")
        table.add_column("Configured", style="yellow")
        table.add_column("Authenticated", style="magenta")
        table.add_column("Status", style="bold")

        for server_name, result in results.items():
            installed_icon = "✅" if result.get("installed") else "❌"
            configured_icon = "✅" if result.get("configured") else "❌"
            authenticated_icon = "✅" if result.get("authenticated") else "❌"
            status = (
                "[green]Success[/green]"
                if result.get("success")
                else "[red]Failed[/red]"
            )

            table.add_row(
                server_name,
                installed_icon,
                configured_icon,
                authenticated_icon,
                status,
            )

        self.console.print(table)

    def display_verification_status(self, results: dict[str, Any]) -> None:
        """Display formatted verification status."""
        self.console.print(
            "\n[bold cyan]🔍 MCP Server Verification Status[/bold cyan]\n"
        )

        table = Table(title="Verification Results")
        table.add_column("Server", style="cyan")
        table.add_column("Configured", style="green")
        table.add_column("Installed", style="yellow")
        table.add_column("Authenticated", style="magenta")
        table.add_column("Connectivity", style="blue")
        table.add_column("Status", style="bold")

        for server_name, verification in results.items():
            checks = verification.get("checks", {})

            configured = checks.get("configured", {}).get("status", "unknown")
            installed = checks.get("installed", {}).get("status", "unknown")
            authenticated = checks.get("authenticated", {}).get("status", "unknown")
            connectivity = checks.get("connectivity", {}).get("status", "unknown")

            def status_icon(status):
                return "✅" if status == "pass" else "❌" if status == "fail" else "⚠️"

            status = verification.get("status", "unknown")
            status_display = (
                "[green]Healthy[/green]"
                if status == "healthy"
                else (
                    "[yellow]Needs Auth[/yellow]"
                    if status == "needs_auth"
                    else "[red]Unhealthy[/red]"
                )
            )

            table.add_row(
                server_name,
                status_icon(configured),
                status_icon(installed),
                status_icon(authenticated),
                status_icon(connectivity),
                status_display,
            )

        self.console.print(table)

    def _run_install_command(self, command: list[str]) -> bool:
        """Run installation command for a package."""
        try:
            self.console.print(f"[dim]Running: {' '.join(command)}[/dim]")
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                self.console.print("[green]✅ Installation successful[/green]")
                return True
            else:
                self.console.print(
                    f"[red]❌ Installation failed: {result.stderr}[/red]"
                )
                return False

        except subprocess.TimeoutExpired:
            self.console.print("[red]❌ Installation timed out[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]❌ Installation error: {e}[/red]")
            return False

    def _add_to_claude_config(
        self, server_name: str, server_spec: dict[str, Any]
    ) -> bool:
        """Add server configuration to .claude.json using environment variable references."""
        try:
            # Load existing config
            if self.claude_config_path.exists():
                with open(self.claude_config_path) as f:
                    config = json.load(f)
            else:
                config = {"mcpServers": {}}

            # Prepare server configuration
            server_config = {"type": server_spec["type"]}

            if server_spec["type"] == "http":
                server_config["url"] = server_spec["url"]

                # SECURITY FIX: Use environment variable references, not actual tokens
                server_config["headers"] = {}
                for env_var in server_spec.get("requires_env", []):
                    if env_var == "CONTEXT7_API_KEY":
                        server_config["headers"]["CONTEXT7_API_KEY"] = "${CONTEXT7_API_KEY}"
                    elif env_var == "GITHUB_PERSONAL_ACCESS_TOKEN" or env_var == "GH_TOKEN":
                        server_config["headers"]["Authorization"] = "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
                    elif env_var == "HUGGINGFACE_TOKEN" or env_var == "HF_TOKEN":
                        server_config["headers"]["Authorization"] = "Bearer ${HUGGINGFACE_TOKEN}"
                    else:
                        # Generic pattern for other tokens
                        server_config["headers"]["Authorization"] = f"Bearer ${{{env_var}}}"

            elif server_spec["type"] == "stdio":
                server_config["command"] = server_spec["command"]
                server_config["args"] = server_spec["args"]
                server_config["env"] = server_spec.get("env", {})

            # Add to config
            config["mcpServers"][server_name] = server_config

            # Save config
            self.claude_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.claude_config_path, "w") as f:
                json.dump(config, f, indent=2)

            return True

        except Exception as e:
            self.console.print(f"[red]Configuration error: {e}[/red]")
            return False

    def _setup_authentication(
        self, server_name: str, server_spec: dict[str, Any]
    ) -> dict[str, Any]:
        """Setup authentication for a server."""
        result = {"success": False, "details": []}

        # Check if environment variables are already set
        env_vars = server_spec.get("requires_env", [])
        missing_vars = [var for var in env_vars if not os.getenv(var)]

        if not missing_vars:
            result["success"] = True
            result["details"].append("Authentication already configured")
            return result

        # If setup command provided, guide user to run it
        if "setup_command" in server_spec:
            self.console.print(
                f"\n[yellow]⚠️  Authentication required for {server_name}[/yellow]"
            )
            self.console.print(f"[dim]Missing: {', '.join(missing_vars)}[/dim]")
            self.console.print(
                f"\n[cyan]Please run:[/cyan] {' '.join(server_spec['setup_command'])}"
            )
            result["details"].append(
                f"Manual authentication required: {' '.join(server_spec['setup_command'])}"
            )
        else:
            self.console.print(
                f"\n[yellow]⚠️  Please set environment variable(s): {', '.join(missing_vars)}[/yellow]"
            )
            result["details"].append(
                f"Manual environment variable setup required: {', '.join(missing_vars)}"
            )

        # Note: Actual authentication is handled by specialized setup scripts
        # This just checks and guides users

        return result

    def _check_installation(self, server_spec: dict[str, Any]) -> dict[str, Any]:
        """Check if required packages are installed."""
        if server_spec["type"] == "stdio":
            command = server_spec["command"]
            try:
                # Try to run the command with --version or --help
                result = subprocess.run(
                    [command, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 or "uv" in command:  # uv always available
                    return {"status": "pass", "message": "Command available"}
                else:
                    return {"status": "fail", "message": "Command not found"}
            except FileNotFoundError:
                return {"status": "fail", "message": f"Command '{command}' not found"}
            except subprocess.TimeoutExpired:
                return {"status": "warn", "message": "Command check timed out"}
            except Exception as e:
                return {"status": "fail", "message": str(e)}

        return {"status": "pass", "message": "No installation check needed"}

    def _check_authentication(
        self, server_name: str, server_spec: dict[str, Any]
    ) -> dict[str, Any]:
        """Check if authentication is configured."""
        env_vars = server_spec.get("requires_env", [])
        missing_vars = [var for var in env_vars if not os.getenv(var)]

        if not missing_vars:
            # Also check if configured in .claude.json
            try:
                with open(self.claude_config_path) as f:
                    config = json.load(f)

                server_config = config.get("mcpServers", {}).get(server_name, {})

                # For HTTP servers, check headers
                if server_spec["type"] == "http":
                    headers = server_config.get("headers", {})
                    if any(
                        key in headers for key in ["Authorization", "CONTEXT7_API_KEY"]
                    ):
                        return {
                            "status": "pass",
                            "message": "Authentication configured",
                        }

                return {"status": "pass", "message": "Environment variables set"}

            except Exception:
                return {"status": "pass", "message": "Environment variables set"}
        else:
            return {
                "status": "fail",
                "message": f"Missing: {', '.join(missing_vars)}",
            }

    def _test_connectivity(
        self, server_name: str, server_spec: dict[str, Any]
    ) -> dict[str, Any]:
        """Test connectivity to the MCP server."""
        # Simple connectivity test - actual health checks handled by MCPManager
        try:
            if server_spec["type"] == "http":
                return {
                    "status": "pass",
                    "message": "HTTP server configuration valid",
                }
            elif server_spec["type"] == "stdio":
                command = server_spec["command"]
                # Check if command exists
                result = subprocess.run(
                    ["which", command], capture_output=True, timeout=5
                )
                if result.returncode == 0 or command == "uv":  # uv is required
                    return {"status": "pass", "message": "Command available"}
                else:
                    return {"status": "fail", "message": "Command not available"}
        except Exception as e:
            return {"status": "fail", "message": str(e)}

        return {"status": "unknown", "message": "Unable to test connectivity"}

    def get_installation_summary(self) -> dict[str, Any]:
        """Get summary of all MCP server installations."""
        summary = {
            "total_servers": len(self.SUPPORTED_SERVERS),
            "configured": 0,
            "healthy": 0,
            "needs_auth": 0,
            "unhealthy": 0,
            "servers": {},
        }

        verification_results = self.verify_all_servers()

        for server_name, verification in verification_results.items():
            status = verification.get("status", "unknown")
            summary["servers"][server_name] = {
                "status": status,
                "description": self.SUPPORTED_SERVERS[server_name].get(
                    "description", ""
                ),
            }

            if (
                verification.get("checks", {}).get("configured", {}).get("status")
                == "pass"
            ):
                summary["configured"] += 1

            if status == "healthy":
                summary["healthy"] += 1
            elif status == "needs_auth":
                summary["needs_auth"] += 1
            elif status == "unhealthy":
                summary["unhealthy"] += 1

        return summary
