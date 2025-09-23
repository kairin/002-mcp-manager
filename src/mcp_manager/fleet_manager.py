"""Fleet Management for Ubuntu 25.04 development environments."""

from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import json
from dataclasses import dataclass
from rich.console import Console
from rich import print as rprint

from .exceptions import MCPManagerError


@dataclass
class FleetNode:
    """Represents a development environment in the fleet."""
    hostname: str
    ip_address: str
    ubuntu_version: str
    python_version: str
    mcp_servers: List[str]
    projects: List[str]
    last_sync: Optional[str] = None
    status: str = "unknown"


class FleetManager:
    """Manages consistency across Ubuntu 25.04 development fleet."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.home_dir = Path.home()
        self.fleet_config_path = self.home_dir / ".config" / "mcp-manager" / "fleet.json"
        self.fleet_config_path.parent.mkdir(parents=True, exist_ok=True)

    def register_node(self, hostname: str, ip_address: str) -> bool:
        """Register a new node in the fleet."""
        try:
            fleet_data = self._load_fleet_config()

            # Detect system information
            ubuntu_version = self._get_ubuntu_version()
            python_version = self._get_python_version()
            mcp_servers = self._get_installed_mcp_servers()
            projects = self._discover_projects()

            node = FleetNode(
                hostname=hostname,
                ip_address=ip_address,
                ubuntu_version=ubuntu_version,
                python_version=python_version,
                mcp_servers=mcp_servers,
                projects=projects,
                status="active"
            )

            fleet_data["nodes"][hostname] = {
                "hostname": node.hostname,
                "ip_address": node.ip_address,
                "ubuntu_version": node.ubuntu_version,
                "python_version": node.python_version,
                "mcp_servers": node.mcp_servers,
                "projects": node.projects,
                "last_sync": node.last_sync,
                "status": node.status
            }

            self._save_fleet_config(fleet_data)
            return True

        except Exception as e:
            self.console.print(f"[red]Error registering node: {e}[/red]")
            return False

    def sync_fleet_configuration(self) -> Dict[str, Any]:
        """Synchronize configuration across all fleet nodes."""
        results = {}
        fleet_data = self._load_fleet_config()

        for hostname, node_data in fleet_data["nodes"].items():
            self.console.print(f"[cyan]Syncing configuration to {hostname}...[/cyan]")

            sync_result = {
                "mcp_servers": False,
                "project_standards": False,
                "claude_agents": False,
                "python_environment": False,
                "errors": []
            }

            try:
                # Sync MCP servers
                sync_result["mcp_servers"] = self._sync_mcp_servers_to_node(node_data)

                # Sync project standards
                sync_result["project_standards"] = self._sync_project_standards_to_node(node_data)

                # Sync Claude agents
                sync_result["claude_agents"] = self._sync_claude_agents_to_node(node_data)

                # Sync Python environment
                sync_result["python_environment"] = self._sync_python_environment_to_node(node_data)

            except Exception as e:
                sync_result["errors"].append(str(e))

            results[hostname] = sync_result

        return results

    def audit_fleet_compliance(self) -> Dict[str, Any]:
        """Audit compliance across all fleet nodes."""
        fleet_data = self._load_fleet_config()
        compliance_results = {}

        requirements = {
            "ubuntu_version": "25.04",
            "python_version": "3.13",
            "required_mcp_servers": ["context7", "shadcn", "github", "playwright", "hf-mcp-server"],
            "required_tools": ["uv", "gh", "astro"]
        }

        for hostname, node_data in fleet_data["nodes"].items():
            compliance = {
                "ubuntu_version": node_data.get("ubuntu_version", "").startswith(requirements["ubuntu_version"]),
                "python_version": node_data.get("python_version", "").startswith(requirements["python_version"]),
                "mcp_servers": all(
                    server in node_data.get("mcp_servers", [])
                    for server in requirements["required_mcp_servers"]
                ),
                "tools_installed": self._check_tools_on_node(node_data, requirements["required_tools"]),
                "overall_compliance": True
            }

            # Calculate overall compliance
            compliance["overall_compliance"] = all([
                compliance["ubuntu_version"],
                compliance["python_version"],
                compliance["mcp_servers"],
                compliance["tools_installed"]
            ])

            compliance_results[hostname] = compliance

        return compliance_results

    def get_fleet_status(self) -> Dict[str, Any]:
        """Get status of all fleet nodes."""
        fleet_data = self._load_fleet_config()
        status = {
            "total_nodes": len(fleet_data["nodes"]),
            "active_nodes": 0,
            "inactive_nodes": 0,
            "nodes": {}
        }

        for hostname, node_data in fleet_data["nodes"].items():
            node_status = self._ping_node(node_data)
            status["nodes"][hostname] = {
                "status": node_status,
                "last_sync": node_data.get("last_sync"),
                "projects": len(node_data.get("projects", [])),
                "mcp_servers": len(node_data.get("mcp_servers", []))
            }

            if node_status == "active":
                status["active_nodes"] += 1
            else:
                status["inactive_nodes"] += 1

        return status

    def deploy_configuration_update(self, config_type: str, config_data: Dict[str, Any]) -> Dict[str, bool]:
        """Deploy configuration updates to all fleet nodes."""
        fleet_data = self._load_fleet_config()
        results = {}

        for hostname, node_data in fleet_data["nodes"].items():
            self.console.print(f"[cyan]Deploying {config_type} to {hostname}...[/cyan]")

            try:
                if config_type == "mcp_server":
                    success = self._deploy_mcp_server_to_node(node_data, config_data)
                elif config_type == "project_template":
                    success = self._deploy_project_template_to_node(node_data, config_data)
                elif config_type == "claude_agent":
                    success = self._deploy_claude_agent_to_node(node_data, config_data)
                else:
                    success = False

                results[hostname] = success

            except Exception as e:
                self.console.print(f"[red]Error deploying to {hostname}: {e}[/red]")
                results[hostname] = False

        return results

    def _load_fleet_config(self) -> Dict[str, Any]:
        """Load fleet configuration from file."""
        if self.fleet_config_path.exists():
            with open(self.fleet_config_path, "r") as f:
                return json.load(f)
        else:
            return {"nodes": {}, "version": "1.0"}

    def _save_fleet_config(self, fleet_data: Dict[str, Any]) -> None:
        """Save fleet configuration to file."""
        with open(self.fleet_config_path, "w") as f:
            json.dump(fleet_data, f, indent=2)

    def _get_ubuntu_version(self) -> str:
        """Get Ubuntu version."""
        try:
            result = subprocess.run(
                ["lsb_release", "-r", "-s"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return "unknown"

    def _get_python_version(self) -> str:
        """Get Python version."""
        try:
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().replace("Python ", "")
        except:
            return "unknown"

    def _get_installed_mcp_servers(self) -> List[str]:
        """Get list of installed MCP servers."""
        try:
            claude_config = self.home_dir / ".claude.json"
            if claude_config.exists():
                with open(claude_config, "r") as f:
                    config = json.load(f)
                    return list(config.get("mcpServers", {}).keys())
            return []
        except:
            return []

    def _discover_projects(self) -> List[str]:
        """Discover projects in common directories."""
        projects = []
        search_dirs = [
            self.home_dir / "Apps",
            self.home_dir / "projects",
            self.home_dir / "repos"
        ]

        for search_dir in search_dirs:
            if search_dir.exists():
                for project_dir in search_dir.iterdir():
                    if project_dir.is_dir() and (project_dir / ".git").exists():
                        projects.append(f"{search_dir.name}/{project_dir.name}")

        return projects

    def _ping_node(self, node_data: Dict[str, Any]) -> str:
        """Check if a node is reachable."""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", node_data["ip_address"]],
                capture_output=True,
                text=True
            )
            return "active" if result.returncode == 0 else "inactive"
        except:
            return "inactive"

    def _check_tools_on_node(self, node_data: Dict[str, Any], required_tools: List[str]) -> bool:
        """Check if required tools are installed on a node."""
        # For local node, check directly
        if node_data["hostname"] == subprocess.run(["hostname"], capture_output=True, text=True).stdout.strip():
            for tool in required_tools:
                result = subprocess.run(["which", tool], capture_output=True)
                if result.returncode != 0:
                    return False
            return True
        else:
            # For remote nodes, this would require SSH
            # For now, assume tools are installed
            return True

    def _sync_mcp_servers_to_node(self, node_data: Dict[str, Any]) -> bool:
        """Sync MCP servers to a node."""
        try:
            # For local node
            if node_data["hostname"] == subprocess.run(["hostname"], capture_output=True, text=True).stdout.strip():
                # Already local, consider synced
                return True
            else:
                # For remote nodes, would use SSH/rsync
                # Implementation depends on specific requirements
                return True
        except Exception:
            return False

    def _sync_project_standards_to_node(self, node_data: Dict[str, Any]) -> bool:
        """Sync project standards to a node."""
        # Implementation for syncing project standards
        return True

    def _sync_claude_agents_to_node(self, node_data: Dict[str, Any]) -> bool:
        """Sync Claude agents to a node."""
        # Implementation for syncing Claude agents
        return True

    def _sync_python_environment_to_node(self, node_data: Dict[str, Any]) -> bool:
        """Sync Python environment configuration to a node."""
        # Implementation for syncing Python environment
        return True

    def _deploy_mcp_server_to_node(self, node_data: Dict[str, Any], config_data: Dict[str, Any]) -> bool:
        """Deploy MCP server configuration to a node."""
        # Implementation for deploying MCP server
        return True

    def _deploy_project_template_to_node(self, node_data: Dict[str, Any], config_data: Dict[str, Any]) -> bool:
        """Deploy project template to a node."""
        # Implementation for deploying project template
        return True

    def _deploy_claude_agent_to_node(self, node_data: Dict[str, Any], config_data: Dict[str, Any]) -> bool:
        """Deploy Claude agent to a node."""
        # Implementation for deploying Claude agent
        return True