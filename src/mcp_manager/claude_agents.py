"""Claude Agent Management for global agent access and deployment."""

from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json
import shutil
import subprocess
from dataclasses import dataclass
from rich.console import Console
from rich import print as rprint

from .exceptions import MCPManagerError


@dataclass
class ClaudeAgent:
    """Represents a Claude agent configuration."""
    name: str
    description: str
    agent_id: str
    department: str
    specialization: str
    file_path: Path
    tools: List[str]
    status: str = "active"


class ClaudeAgentManager:
    """Manages Claude agents globally across all projects."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.home_dir = Path.home()

        # Global agent directories
        self.global_agents_dirs = [
            self.home_dir / "Apps" / "claude-guardian-agents",
            self.home_dir / "Apps" / "deep-research",
            self.home_dir / "Apps" / "DeepResearchAgent"
        ]

        # Global agent registry
        self.agent_registry_path = self.home_dir / ".config" / "mcp-manager" / "claude-agents.json"
        self.agent_registry_path.parent.mkdir(parents=True, exist_ok=True)

    def discover_agents(self) -> Dict[str, ClaudeAgent]:
        """Discover all Claude agents from configured directories."""
        agents = {}

        for agents_dir in self.global_agents_dirs:
            if not agents_dir.exists():
                continue

            # Scan for agent files
            for agent_file in agents_dir.rglob("*-guardian.md"):
                try:
                    agent = self._parse_agent_file(agent_file)
                    if agent:
                        agents[agent.agent_id] = agent
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not parse {agent_file}: {e}[/yellow]")

            # Scan for research agents
            for agent_file in agents_dir.rglob("*-agent.md"):
                try:
                    agent = self._parse_agent_file(agent_file)
                    if agent:
                        agents[agent.agent_id] = agent
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not parse {agent_file}: {e}[/yellow]")

        self._update_agent_registry(agents)
        return agents

    def get_agent_by_id(self, agent_id: str) -> Optional[ClaudeAgent]:
        """Get a specific agent by ID."""
        agents = self.discover_agents()
        return agents.get(agent_id)

    def get_agents_by_department(self, department: str) -> List[ClaudeAgent]:
        """Get all agents from a specific department."""
        agents = self.discover_agents()
        return [agent for agent in agents.values() if agent.department == department]

    def get_agents_by_specialization(self, specialization: str) -> List[ClaudeAgent]:
        """Get all agents with a specific specialization."""
        agents = self.discover_agents()
        return [agent for agent in agents.values() if specialization.lower() in agent.specialization.lower()]

    def deploy_agent_to_project(self, agent_id: str, project_path: Path) -> bool:
        """Deploy a specific agent configuration to a project."""
        try:
            agent = self.get_agent_by_id(agent_id)
            if not agent:
                raise MCPManagerError(f"Agent {agent_id} not found")

            # Create project agents directory
            project_agents_dir = project_path / ".claude-agents"
            project_agents_dir.mkdir(exist_ok=True)

            # Copy agent file to project
            dest_file = project_agents_dir / f"{agent.agent_id}.md"
            shutil.copy2(agent.file_path, dest_file)

            # Update project's agent registry
            project_registry = project_path / ".claude-agents" / "registry.json"
            self._update_project_agent_registry(project_registry, agent)

            return True

        except Exception as e:
            self.console.print(f"[red]Error deploying agent {agent_id}: {e}[/red]")
            return False

    def deploy_department_to_project(self, department: str, project_path: Path) -> Dict[str, bool]:
        """Deploy all agents from a department to a project."""
        agents = self.get_agents_by_department(department)
        results = {}

        for agent in agents:
            results[agent.agent_id] = self.deploy_agent_to_project(agent.agent_id, project_path)

        return results

    def install_global_agent_access(self) -> bool:
        """Install global agent access for Claude Code."""
        try:
            # Create global Claude configuration
            claude_config_path = self.home_dir / ".claude-agents.json"

            agents = self.discover_agents()

            config = {
                "version": "1.0",
                "agent_directories": [str(d) for d in self.global_agents_dirs if d.exists()],
                "agents": {
                    agent_id: {
                        "name": agent.name,
                        "description": agent.description,
                        "department": agent.department,
                        "specialization": agent.specialization,
                        "file_path": str(agent.file_path),
                        "tools": agent.tools,
                        "status": agent.status
                    }
                    for agent_id, agent in agents.items()
                }
            }

            with open(claude_config_path, "w") as f:
                json.dump(config, f, indent=2)

            self.console.print(f"[green]✅ Global agent access installed with {len(agents)} agents[/green]")
            return True

        except Exception as e:
            self.console.print(f"[red]Error installing global agent access: {e}[/red]")
            return False

    def create_agent_quick_access(self) -> bool:
        """Create quick access commands for agents."""
        try:
            # Create bin directory for agent scripts
            bin_dir = self.home_dir / ".local" / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)

            agents = self.discover_agents()

            # Create a universal agent launcher script
            launcher_script = bin_dir / "claude-agent"
            launcher_content = f"""#!/bin/bash
# Claude Agent Universal Launcher
# Auto-generated by MCP Manager

AGENT_REGISTRY="{self.agent_registry_path}"

if [ $# -eq 0 ]; then
    echo "Usage: claude-agent <agent-id> [project-path]"
    echo "Available agents:"
    if [ -f "$AGENT_REGISTRY" ]; then
        jq -r '.agents | keys[]' "$AGENT_REGISTRY" 2>/dev/null || echo "  (registry file not found)"
    fi
    exit 1
fi

AGENT_ID="$1"
PROJECT_PATH="${{2:-.}}"

# Deploy agent to project
mcp-manager agent deploy "$AGENT_ID" "$PROJECT_PATH"
"""

            with open(launcher_script, "w") as f:
                f.write(launcher_content)

            launcher_script.chmod(0o755)

            # Create department-specific shortcuts
            departments = set(agent.department for agent in agents.values())
            for department in departments:
                dept_script = bin_dir / f"claude-{department.replace('-', '_')}"
                dept_content = f"""#!/bin/bash
# Claude {department.title()} Department Agents
# Auto-generated by MCP Manager

mcp-manager agent deploy-department "{department}" "${{1:-.}}"
"""
                with open(dept_script, "w") as f:
                    f.write(dept_content)
                dept_script.chmod(0o755)

            return True

        except Exception as e:
            self.console.print(f"[red]Error creating agent quick access: {e}[/red]")
            return False

    def audit_agent_availability(self) -> Dict[str, Any]:
        """Audit agent availability across the system."""
        audit_results = {
            "total_agents": 0,
            "available_agents": 0,
            "missing_agents": [],
            "departments": {},
            "global_access": False,
            "project_deployments": {}
        }

        try:
            # Check global agent access
            claude_config = self.home_dir / ".claude-agents.json"
            audit_results["global_access"] = claude_config.exists()

            # Discover agents
            agents = self.discover_agents()
            audit_results["total_agents"] = len(agents)
            audit_results["available_agents"] = len([a for a in agents.values() if a.status == "active"])

            # Analyze by department
            for agent in agents.values():
                dept = agent.department
                if dept not in audit_results["departments"]:
                    audit_results["departments"][dept] = {
                        "total": 0,
                        "available": 0,
                        "agents": []
                    }

                audit_results["departments"][dept]["total"] += 1
                audit_results["departments"][dept]["agents"].append(agent.agent_id)

                if agent.status == "active":
                    audit_results["departments"][dept]["available"] += 1

            # Check project deployments
            projects_dir = self.home_dir / "Apps"
            if projects_dir.exists():
                for project_dir in projects_dir.iterdir():
                    if project_dir.is_dir() and (project_dir / ".git").exists():
                        agents_dir = project_dir / ".claude-agents"
                        if agents_dir.exists():
                            deployed_agents = len(list(agents_dir.glob("*.md")))
                            audit_results["project_deployments"][project_dir.name] = deployed_agents

        except Exception as e:
            self.console.print(f"[red]Error auditing agent availability: {e}[/red]")

        return audit_results

    def _parse_agent_file(self, agent_file: Path) -> Optional[ClaudeAgent]:
        """Parse an agent file and extract metadata."""
        try:
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract metadata from frontmatter
            if content.startswith("---"):
                end_frontmatter = content.find("---", 3)
                if end_frontmatter != -1:
                    frontmatter = content[3:end_frontmatter]
                    metadata = {}
                    for line in frontmatter.split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            metadata[key.strip()] = value.strip().strip('"')

                    # Extract from filename if not in frontmatter
                    filename_parts = agent_file.stem.split("-")

                    return ClaudeAgent(
                        name=metadata.get("name", agent_file.stem),
                        description=metadata.get("description", ""),
                        agent_id=metadata.get("agent_id", agent_file.stem),
                        department=metadata.get("department", filename_parts[0] if len(filename_parts) > 1 else "unknown"),
                        specialization=metadata.get("specialization", " ".join(filename_parts[1:-1]) if len(filename_parts) > 2 else ""),
                        file_path=agent_file,
                        tools=metadata.get("tools", "").split(",") if metadata.get("tools") else [],
                        status=metadata.get("status", "active")
                    )

            # Fallback parsing from filename
            filename_parts = agent_file.stem.split("-")
            return ClaudeAgent(
                name=agent_file.stem,
                description="",
                agent_id=agent_file.stem,
                department=filename_parts[0] if len(filename_parts) > 1 else "unknown",
                specialization=" ".join(filename_parts[1:-1]) if len(filename_parts) > 2 else "",
                file_path=agent_file,
                tools=[],
                status="active"
            )

        except Exception:
            return None

    def _update_agent_registry(self, agents: Dict[str, ClaudeAgent]) -> None:
        """Update the global agent registry."""
        registry_data = {
            "version": "1.0",
            "last_updated": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
            "agents": {
                agent_id: {
                    "name": agent.name,
                    "description": agent.description,
                    "department": agent.department,
                    "specialization": agent.specialization,
                    "file_path": str(agent.file_path),
                    "tools": agent.tools,
                    "status": agent.status
                }
                for agent_id, agent in agents.items()
            }
        }

        with open(self.agent_registry_path, "w") as f:
            json.dump(registry_data, f, indent=2)

    def _update_project_agent_registry(self, registry_path: Path, agent: ClaudeAgent) -> None:
        """Update a project's agent registry."""
        if registry_path.exists():
            with open(registry_path, "r") as f:
                registry_data = json.load(f)
        else:
            registry_data = {"agents": {}}

        registry_data["agents"][agent.agent_id] = {
            "name": agent.name,
            "description": agent.description,
            "department": agent.department,
            "specialization": agent.specialization,
            "deployed_at": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip()
        }

        with open(registry_path, "w") as f:
            json.dump(registry_data, f, indent=2)