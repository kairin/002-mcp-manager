"""Office-wide deployment and synchronization for MCP Manager."""

import json
import socket
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .exceptions import MCPManagerError


@dataclass
class OfficeNode:
    """Represents a machine in the office network."""

    hostname: str
    ip_address: str
    ssh_user: str
    ssh_key_path: str | None = None
    status: str = "unknown"  # unknown, active, unreachable
    last_sync: datetime | None = None
    mcp_config_hash: str | None = None


class OfficeDeploymentManager:
    """Manages MCP configuration deployment across office machines."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".config" / "mcp-manager"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.office_config_path = self.config_dir / "office-nodes.json"
        self.claude_config_path = self.home_dir / ".claude.json"

    def register_office_node(
        self,
        hostname: str,
        ip_address: str,
        ssh_user: str,
        ssh_key_path: str | None = None,
    ) -> bool:
        """Register a new office machine for deployment."""
        try:
            nodes = self._load_office_nodes()

            # Add or update node
            nodes[hostname] = {
                "hostname": hostname,
                "ip_address": ip_address,
                "ssh_user": ssh_user,
                "ssh_key_path": ssh_key_path,
                "status": "unknown",
                "last_sync": None,
                "mcp_config_hash": None,
            }

            self._save_office_nodes(nodes)
            self.console.print(
                f"[green]✅ Registered office node: {hostname} ({ip_address})[/green]"
            )
            return True

        except Exception as e:
            self.console.print(f"[red]❌ Failed to register node: {e}[/red]")
            return False

    def list_office_nodes(self) -> dict[str, dict[str, Any]]:
        """List all registered office nodes."""
        return self._load_office_nodes()

    def remove_office_node(self, hostname: str) -> bool:
        """Remove an office node from management."""
        try:
            nodes = self._load_office_nodes()

            if hostname not in nodes:
                self.console.print(
                    f"[yellow]⚠️ Node {hostname} not found in registry[/yellow]"
                )
                return False

            del nodes[hostname]
            self._save_office_nodes(nodes)
            self.console.print(
                f"[green]✅ Removed office node: {hostname}[/green]"
            )
            return True

        except Exception as e:
            self.console.print(f"[red]❌ Failed to remove node: {e}[/red]")
            return False

    def check_node_connectivity(self, hostname: str) -> bool:
        """Check if an office node is reachable via SSH."""
        nodes = self._load_office_nodes()

        if hostname not in nodes:
            raise MCPManagerError(f"Node {hostname} not registered")

        node = nodes[hostname]
        try:
            # Build SSH command
            ssh_cmd = ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes"]

            if node.get("ssh_key_path"):
                ssh_cmd.extend(["-i", node["ssh_key_path"]])

            ssh_cmd.extend([f"{node['ssh_user']}@{node['ip_address']}", "echo", "ok"])

            # Test connection
            result = subprocess.run(
                ssh_cmd, capture_output=True, text=True, timeout=10
            )

            is_reachable = result.returncode == 0

            # Update node status
            node["status"] = "active" if is_reachable else "unreachable"
            nodes[hostname] = node
            self._save_office_nodes(nodes)

            return is_reachable

        except subprocess.TimeoutExpired:
            node["status"] = "unreachable"
            nodes[hostname] = node
            self._save_office_nodes(nodes)
            return False
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Connectivity check failed: {e}[/yellow]")
            return False

    def deploy_to_node(self, hostname: str, dry_run: bool = False) -> bool:
        """Deploy MCP configuration to a specific office node."""
        nodes = self._load_office_nodes()

        if hostname not in nodes:
            raise MCPManagerError(f"Node {hostname} not registered")

        node = nodes[hostname]

        # Check connectivity first
        if not self.check_node_connectivity(hostname):
            self.console.print(
                f"[red]❌ Cannot reach node {hostname}. Deployment aborted.[/red]"
            )
            return False

        try:
            # Read local MCP configuration
            if not self.claude_config_path.exists():
                raise MCPManagerError(
                    "Local .claude.json not found. Cannot deploy."
                )

            with open(self.claude_config_path) as f:
                local_config = json.load(f)

            if dry_run:
                self.console.print(
                    f"[yellow]🔍 Dry run - would deploy to {hostname}[/yellow]"
                )
                self.console.print(
                    f"   MCP Servers: {len(local_config.get('mcpServers', {}))}"
                )
                return True

            # Copy configuration to remote node
            ssh_cmd_base = ["ssh"]
            if node.get("ssh_key_path"):
                ssh_cmd_base.extend(["-i", node["ssh_key_path"]])
            ssh_cmd_base.append(f"{node['ssh_user']}@{node['ip_address']}")

            # Create backup on remote node
            backup_cmd = ssh_cmd_base + [
                "cp",
                "~/.claude.json",
                f"~/.claude.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "||",
                "true",
            ]
            subprocess.run(backup_cmd, capture_output=True, timeout=10)

            # Transfer configuration file
            scp_cmd = ["scp"]
            if node.get("ssh_key_path"):
                scp_cmd.extend(["-i", node["ssh_key_path"]])
            scp_cmd.extend(
                [
                    str(self.claude_config_path),
                    f"{node['ssh_user']}@{node['ip_address']}:~/.claude.json",
                ]
            )

            result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                raise MCPManagerError(f"SCP transfer failed: {result.stderr}")

            # Update node metadata
            node["last_sync"] = datetime.now().isoformat()
            node["mcp_config_hash"] = self._calculate_config_hash(local_config)
            node["status"] = "active"
            nodes[hostname] = node
            self._save_office_nodes(nodes)

            self.console.print(
                f"[green]✅ Successfully deployed MCP configuration to {hostname}[/green]"
            )
            return True

        except Exception as e:
            self.console.print(f"[red]❌ Deployment failed: {e}[/red]")
            return False

    def deploy_to_all_nodes(self, dry_run: bool = False) -> dict[str, bool]:
        """Deploy MCP configuration to all registered office nodes."""
        nodes = self._load_office_nodes()
        results = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Deploying to office nodes...", total=len(nodes)
            )

            for hostname in nodes.keys():
                progress.update(
                    task, description=f"[cyan]Deploying to {hostname}..."
                )
                results[hostname] = self.deploy_to_node(hostname, dry_run=dry_run)
                progress.advance(task)

        return results

    def verify_node_configuration(self, hostname: str) -> dict[str, Any]:
        """Verify MCP configuration on a remote node matches local."""
        nodes = self._load_office_nodes()

        if hostname not in nodes:
            raise MCPManagerError(f"Node {hostname} not registered")

        node = nodes[hostname]

        if not self.check_node_connectivity(hostname):
            return {
                "status": "unreachable",
                "message": f"Cannot reach node {hostname}",
                "match": False,
            }

        try:
            # Fetch remote configuration
            ssh_cmd = ["ssh"]
            if node.get("ssh_key_path"):
                ssh_cmd.extend(["-i", node["ssh_key_path"]])
            ssh_cmd.extend(
                [
                    f"{node['ssh_user']}@{node['ip_address']}",
                    "cat",
                    "~/.claude.json",
                ]
            )

            result = subprocess.run(
                ssh_cmd, capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": "Failed to read remote configuration",
                    "match": False,
                }

            remote_config = json.loads(result.stdout)

            # Read local configuration
            with open(self.claude_config_path) as f:
                local_config = json.load(f)

            # Compare configurations
            local_hash = self._calculate_config_hash(local_config)
            remote_hash = self._calculate_config_hash(remote_config)

            match = local_hash == remote_hash

            return {
                "status": "ok",
                "match": match,
                "local_servers": len(local_config.get("mcpServers", {})),
                "remote_servers": len(remote_config.get("mcpServers", {})),
                "local_hash": local_hash,
                "remote_hash": remote_hash,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "match": False,
            }

    def verify_all_nodes(self) -> dict[str, dict[str, Any]]:
        """Verify MCP configuration across all office nodes."""
        nodes = self._load_office_nodes()
        results = {}

        for hostname in nodes.keys():
            results[hostname] = self.verify_node_configuration(hostname)

        return results

    def sync_from_node(self, hostname: str) -> bool:
        """Pull MCP configuration from a remote node (reverse sync)."""
        nodes = self._load_office_nodes()

        if hostname not in nodes:
            raise MCPManagerError(f"Node {hostname} not registered")

        node = nodes[hostname]

        if not self.check_node_connectivity(hostname):
            self.console.print(
                f"[red]❌ Cannot reach node {hostname}. Sync aborted.[/red]"
            )
            return False

        try:
            # Create local backup
            if self.claude_config_path.exists():
                backup_path = self.claude_config_path.with_suffix(
                    f".json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                subprocess.run(
                    ["cp", str(self.claude_config_path), str(backup_path)],
                    check=True,
                )
                self.console.print(
                    f"[yellow]📋 Local backup created: {backup_path.name}[/yellow]"
                )

            # Pull configuration from remote
            scp_cmd = ["scp"]
            if node.get("ssh_key_path"):
                scp_cmd.extend(["-i", node["ssh_key_path"]])
            scp_cmd.extend(
                [
                    f"{node['ssh_user']}@{node['ip_address']}:~/.claude.json",
                    str(self.claude_config_path),
                ]
            )

            result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                raise MCPManagerError(f"SCP transfer failed: {result.stderr}")

            self.console.print(
                f"[green]✅ Successfully pulled MCP configuration from {hostname}[/green]"
            )
            return True

        except Exception as e:
            self.console.print(f"[red]❌ Sync failed: {e}[/red]")
            return False

    def get_deployment_status(self) -> dict[str, Any]:
        """Get comprehensive deployment status for all office nodes."""
        nodes = self._load_office_nodes()

        status = {
            "total_nodes": len(nodes),
            "active_nodes": 0,
            "unreachable_nodes": 0,
            "synced_nodes": 0,
            "out_of_sync_nodes": 0,
            "nodes_detail": {},
        }

        for hostname, node in nodes.items():
            # Check connectivity
            is_reachable = self.check_node_connectivity(hostname)

            if is_reachable:
                status["active_nodes"] += 1

                # Verify configuration
                verification = self.verify_node_configuration(hostname)

                node_status = {
                    "reachable": True,
                    "config_match": verification.get("match", False),
                    "last_sync": node.get("last_sync", "Never"),
                    "local_servers": verification.get("local_servers", 0),
                    "remote_servers": verification.get("remote_servers", 0),
                }

                if verification.get("match"):
                    status["synced_nodes"] += 1
                else:
                    status["out_of_sync_nodes"] += 1

            else:
                status["unreachable_nodes"] += 1
                node_status = {
                    "reachable": False,
                    "config_match": False,
                    "last_sync": node.get("last_sync", "Never"),
                }

            status["nodes_detail"][hostname] = node_status

        return status

    def display_office_status(self) -> None:
        """Display formatted office deployment status."""
        status = self.get_deployment_status()

        # Summary table
        self.console.print("\n[bold cyan]🏢 Office Deployment Status[/bold cyan]\n")

        summary_table = Table(title="Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", style="green")

        summary_table.add_row("Total Nodes", str(status["total_nodes"]))
        summary_table.add_row("Active Nodes", str(status["active_nodes"]))
        summary_table.add_row("Unreachable Nodes", str(status["unreachable_nodes"]))
        summary_table.add_row("Synced Nodes", str(status["synced_nodes"]))
        summary_table.add_row("Out of Sync", str(status["out_of_sync_nodes"]))

        self.console.print(summary_table)

        # Node details table
        details_table = Table(title="Node Details")
        details_table.add_column("Hostname", style="cyan")
        details_table.add_column("Status", style="green")
        details_table.add_column("Config Match", style="yellow")
        details_table.add_column("Servers (Local/Remote)", style="magenta")
        details_table.add_column("Last Sync", style="dim")

        for hostname, node_info in status["nodes_detail"].items():
            status_icon = "🟢 Active" if node_info["reachable"] else "🔴 Unreachable"
            match_icon = "✅ Synced" if node_info["config_match"] else "❌ Out of Sync"
            servers = (
                f"{node_info.get('local_servers', 0)}/{node_info.get('remote_servers', 0)}"
                if node_info["reachable"]
                else "N/A"
            )

            details_table.add_row(
                hostname,
                status_icon,
                match_icon,
                servers,
                node_info.get("last_sync", "Never"),
            )

        self.console.print(details_table)

    def _load_office_nodes(self) -> dict[str, dict[str, Any]]:
        """Load office nodes configuration from disk."""
        if not self.office_config_path.exists():
            return {}

        try:
            with open(self.office_config_path) as f:
                return json.load(f)
        except Exception as e:
            self.console.print(
                f"[yellow]⚠️ Failed to load office nodes: {e}[/yellow]"
            )
            return {}

    def _save_office_nodes(self, nodes: dict[str, dict[str, Any]]) -> None:
        """Save office nodes configuration to disk."""
        with open(self.office_config_path, "w") as f:
            json.dump(nodes, f, indent=2)

    def _calculate_config_hash(self, config: dict[str, Any]) -> str:
        """Calculate a hash of the MCP server configuration."""
        import hashlib

        # Extract only mcpServers for comparison
        servers = config.get("mcpServers", {})
        config_str = json.dumps(servers, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]

    def get_current_machine_info(self) -> dict[str, str]:
        """Get information about the current machine."""
        hostname = socket.gethostname()

        try:
            # Try to get IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
        except Exception:
            ip_address = "127.0.0.1"

        return {
            "hostname": hostname,
            "ip_address": ip_address,
            "user": subprocess.run(
                ["whoami"], capture_output=True, text=True
            ).stdout.strip(),
        }
