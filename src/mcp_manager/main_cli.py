"""CLI interface for MCP Manager - Comprehensive Project Standardization System."""

from pathlib import Path
from typing import Any

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .claude_agents import ClaudeAgentManager
from .cli.gemini_commands import gemini_app
from .cli.mcp_commands import mcp_app
from .cli.validate_commands import app as validate_app
from .cli_utils import set_verbose_mode
from .core import MCPManager
from .exceptions import MCPManagerError
from .fleet_manager import FleetManager
from .office_deployment import OfficeDeploymentManager
from .project_standards import ProjectStandardsManager

# Initialize CLI app and console
app = typer.Typer(
    name="mcp-manager",
    help="🚀 MCP Manager - Comprehensive Project Standardization & Fleet Management System",
    rich_markup_mode="rich",
)
console = Console()


# Global verbose flag callback
@app.callback()
def global_options(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output with debug information",
    ),
) -> None:
    """Global options for MCP Manager.

    Args:
        ctx: Typer context
        verbose: Enable verbose mode
    """
    set_verbose_mode(verbose)
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


# Create sub-applications for different management areas
# Note: mcp_app and gemini_app are imported from .cli module
project_app = typer.Typer(help="📋 Project Standardization")
fleet_app = typer.Typer(help="🌐 Fleet Management")
agent_app = typer.Typer(help="🤖 Claude Agent Management")
office_app = typer.Typer(help="🏢 Office Deployment Management")

app.add_typer(mcp_app, name="mcp")
app.add_typer(project_app, name="project")
app.add_typer(fleet_app, name="fleet")
app.add_typer(agent_app, name="agent")
app.add_typer(office_app, name="office")
app.add_typer(gemini_app, name="gemini")
app.add_typer(validate_app, name="validate")


def main() -> None:
    """Main CLI entry point."""
    app()


# =============================================================================
# PROJECT STANDARDIZATION COMMANDS
# =============================================================================


@project_app.command("audit")
def project_audit(
    project_path: str | None = typer.Argument(
        None, help="Project path (default: current directory)"
    ),
    all_projects: bool = typer.Option(
        False, "--all", help="Audit all projects in home directory"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", help="Show detailed compliance information"
    ),
) -> None:
    """Audit project compliance with standardization requirements."""
    try:
        standards_manager = ProjectStandardsManager(console)

        if all_projects:
            results = standards_manager.audit_all_projects()
            summary = standards_manager.get_compliance_summary(results)
            _display_compliance_summary(summary)
            _display_project_audit_results(results, detailed)
        else:
            project_dir = Path(project_path or ".")
            results = standards_manager.audit_project(project_dir)
            _display_single_project_audit(project_dir.name, results, detailed)

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@project_app.command("fix")
def project_fix(
    standard: str = typer.Argument(
        ..., help="Standard to fix (e.g., branch_strategy, astro_pages)"
    ),
    project_path: str | None = typer.Argument(
        None, help="Project path (default: current directory)"
    ),
    all_projects: bool = typer.Option(
        False, "--all", help="Fix standard for all projects"
    ),
) -> None:
    """Fix a specific standard for a project or all projects."""
    try:
        standards_manager = ProjectStandardsManager(console)

        if all_projects:
            # Find all projects and fix the standard
            scan_dirs = [
                Path.home() / "Apps",
                Path.home() / "projects",
                Path.home() / "repos",
            ]
            for scan_dir in scan_dirs:
                if scan_dir.exists():
                    for project_dir in scan_dir.iterdir():
                        if project_dir.is_dir() and (project_dir / ".git").exists():
                            success = standards_manager.fix_project_standard(
                                project_dir, standard
                            )
                            status = "✅" if success else "❌"
                            rprint(f"{status} {project_dir.name}: {standard}")
        else:
            project_dir = Path(project_path or ".")
            success = standards_manager.fix_project_standard(project_dir, standard)
            if success:
                rprint(f"[green]✅ Fixed {standard} for {project_dir.name}[/green]")
            else:
                rprint(f"[red]❌ Failed to fix {standard} for {project_dir.name}[/red]")

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@project_app.command("standards")
def project_standards() -> None:
    """List all available project standards."""
    standards_manager = ProjectStandardsManager(console)

    table = Table(title="Project Standardization Requirements")
    table.add_column("Standard", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Fix Command", style="yellow")

    for standard_id, standard in standards_manager.standards.items():
        table.add_row(standard_id, standard.description, standard.fix_command)

    console.print(table)


# =============================================================================
# FLEET MANAGEMENT COMMANDS
# =============================================================================


@fleet_app.command("register")
def fleet_register(
    hostname: str = typer.Argument(..., help="Hostname of the node"),
    ip_address: str = typer.Argument(..., help="IP address of the node"),
) -> None:
    """Register a new node in the fleet."""
    try:
        fleet_manager = FleetManager(console)
        success = fleet_manager.register_node(hostname, ip_address)

        if success:
            rprint(f"[green]✅ Node {hostname} registered successfully[/green]")
        else:
            rprint(f"[red]❌ Failed to register node {hostname}[/red]")

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@fleet_app.command("status")
def fleet_status() -> None:
    """Get status of all fleet nodes."""
    try:
        fleet_manager = FleetManager(console)
        status = fleet_manager.get_fleet_status()

        table = Table(title="Fleet Status")
        table.add_column("Node", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Projects", style="yellow")
        table.add_column("MCP Servers", style="magenta")
        table.add_column("Last Sync", style="dim")

        for hostname, node_info in status["nodes"].items():
            status_icon = "🟢" if node_info["status"] == "active" else "🔴"
            table.add_row(
                hostname,
                f"{status_icon} {node_info['status']}",
                str(node_info["projects"]),
                str(node_info["mcp_servers"]),
                node_info.get("last_sync", "Never") or "Never",
            )

        console.print(table)
        rprint(
            f"\n[cyan]Total: {status['total_nodes']} nodes ({status['active_nodes']} active, {status['inactive_nodes']} inactive)[/cyan]"
        )

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@fleet_app.command("sync")
def fleet_sync() -> None:
    """Synchronize configuration across all fleet nodes."""
    try:
        fleet_manager = FleetManager(console)
        results = fleet_manager.sync_fleet_configuration()

        table = Table(title="Fleet Synchronization Results")
        table.add_column("Node", style="cyan")
        table.add_column("MCP Servers", style="green")
        table.add_column("Project Standards", style="yellow")
        table.add_column("Claude Agents", style="magenta")
        table.add_column("Python Env", style="blue")

        for hostname, result in results.items():
            table.add_row(
                hostname,
                "✅" if result["mcp_servers"] else "❌",
                "✅" if result["project_standards"] else "❌",
                "✅" if result["claude_agents"] else "❌",
                "✅" if result["python_environment"] else "❌",
            )

        console.print(table)

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@fleet_app.command("audit")
def fleet_audit() -> None:
    """Audit compliance across all fleet nodes."""
    try:
        fleet_manager = FleetManager(console)
        results = fleet_manager.audit_fleet_compliance()

        table = Table(title="Fleet Compliance Audit")
        table.add_column("Node", style="cyan")
        table.add_column("Ubuntu 25.04", style="green")
        table.add_column("Python 3.13", style="yellow")
        table.add_column("MCP Servers", style="magenta")
        table.add_column("Tools", style="blue")
        table.add_column("Overall", style="bold")

        for hostname, compliance in results.items():
            table.add_row(
                hostname,
                "✅" if compliance["ubuntu_version"] else "❌",
                "✅" if compliance["python_version"] else "❌",
                "✅" if compliance["mcp_servers"] else "❌",
                "✅" if compliance["tools_installed"] else "❌",
                (
                    "✅ Compliant"
                    if compliance["overall_compliance"]
                    else "❌ Non-compliant"
                ),
            )

        console.print(table)

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


# =============================================================================
# CLAUDE AGENT MANAGEMENT COMMANDS
# =============================================================================


@agent_app.command("discover")
def agent_discover() -> None:
    """Discover all available Claude agents."""
    try:
        agent_manager = ClaudeAgentManager(console)
        agents = agent_manager.discover_agents()

        table = Table(title="Available Claude Agents")
        table.add_column("Agent ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Department", style="yellow")
        table.add_column("Specialization", style="magenta")
        table.add_column("Status", style="blue")

        for agent_id, agent in agents.items():
            table.add_row(
                agent_id,
                agent.name,
                agent.department,
                agent.specialization,
                agent.status,
            )

        console.print(table)
        rprint(f"\n[cyan]Total: {len(agents)} agents discovered[/cyan]")

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@agent_app.command("deploy")
def agent_deploy(
    agent_id: str = typer.Argument(..., help="Agent ID to deploy"),
    project_path: str | None = typer.Argument(
        None, help="Project path (default: current directory)"
    ),
) -> None:
    """Deploy a specific agent to a project."""
    try:
        agent_manager = ClaudeAgentManager(console)
        project_dir = Path(project_path or ".")

        success = agent_manager.deploy_agent_to_project(agent_id, project_dir)

        if success:
            rprint(f"[green]✅ Agent {agent_id} deployed to {project_dir.name}[/green]")
        else:
            rprint(f"[red]❌ Failed to deploy agent {agent_id}[/red]")

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@agent_app.command("deploy-department")
def agent_deploy_department(
    department: str = typer.Argument(
        ..., help="Department to deploy (e.g., product, engineering)"
    ),
    project_path: str | None = typer.Argument(
        None, help="Project path (default: current directory)"
    ),
) -> None:
    """Deploy all agents from a department to a project."""
    try:
        agent_manager = ClaudeAgentManager(console)
        project_dir = Path(project_path or ".")

        results = agent_manager.deploy_department_to_project(department, project_dir)

        table = Table(title=f"Department {department.title()} Deployment Results")
        table.add_column("Agent ID", style="cyan")
        table.add_column("Status", style="green")

        for agent_id, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            table.add_row(agent_id, status)

        console.print(table)

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@agent_app.command("install-global")
def agent_install_global() -> None:
    """Install global agent access for Claude Code."""
    try:
        agent_manager = ClaudeAgentManager(console)
        success = agent_manager.install_global_agent_access()

        if success:
            # Also create quick access commands
            agent_manager.create_agent_quick_access()

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@agent_app.command("audit")
def agent_audit() -> None:
    """Audit agent availability across the system."""
    try:
        agent_manager = ClaudeAgentManager(console)
        audit_results = agent_manager.audit_agent_availability()

        # Display summary
        rprint("[cyan]Agent Availability Summary[/cyan]")
        rprint(f"Total Agents: {audit_results['total_agents']}")
        rprint(f"Available Agents: {audit_results['available_agents']}")
        rprint(
            f"Global Access: {'✅ Enabled' if audit_results['global_access'] else '❌ Disabled'}"
        )

        # Display by department
        if audit_results["departments"]:
            table = Table(title="Agents by Department")
            table.add_column("Department", style="cyan")
            table.add_column("Total", style="green")
            table.add_column("Available", style="yellow")
            table.add_column("Agents", style="dim")

            for dept, info in audit_results["departments"].items():
                agents_list = ", ".join(info["agents"][:3])  # Show first 3
                if len(info["agents"]) > 3:
                    agents_list += f" (+{len(info['agents']) - 3} more)"

                table.add_row(
                    dept, str(info["total"]), str(info["available"]), agents_list
                )

            console.print(table)

        # Display project deployments
        if audit_results["project_deployments"]:
            rprint("\n[cyan]Project Deployments[/cyan]")
            for project, count in audit_results["project_deployments"].items():
                rprint(f"  {project}: {count} agents")

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


# =============================================================================
# TOP-LEVEL COMMANDS
# =============================================================================


@app.command()
def init() -> None:
    """Initialize MCP Manager with full project standardization setup."""
    try:
        rprint(
            "[cyan]🚀 Initializing MCP Manager - Comprehensive Project Standardization System[/cyan]"
        )

        # Initialize MCP configuration
        rprint("[yellow]1. Setting up MCP server management...[/yellow]")
        manager = MCPManager()
        manager.init_global_config(force=False)

        # Initialize project standards
        rprint("[yellow]2. Setting up project standardization...[/yellow]")
        standards_manager = ProjectStandardsManager(console)

        # Initialize fleet management
        rprint("[yellow]3. Setting up fleet management...[/yellow]")
        fleet_manager = FleetManager(console)
        import socket

        hostname = socket.gethostname()
        ip_address = "127.0.0.1"  # Local node
        fleet_manager.register_node(hostname, ip_address)

        # Initialize Claude agents
        rprint("[yellow]4. Setting up Claude agent management...[/yellow]")
        agent_manager = ClaudeAgentManager(console)
        agent_manager.install_global_agent_access()

        rprint("[green]✅ MCP Manager initialization complete![/green]")
        rprint("\n[cyan]Available commands:[/cyan]")
        rprint("  • [yellow]mcp-manager mcp[/yellow] - MCP server management")
        rprint("  • [yellow]mcp-manager project[/yellow] - Project standardization")
        rprint("  • [yellow]mcp-manager fleet[/yellow] - Fleet management")
        rprint("  • [yellow]mcp-manager agent[/yellow] - Claude agent management")

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Show overall system status."""
    try:
        rprint("[cyan]🌐 MCP Manager System Status[/cyan]\n")

        # MCP Status
        rprint("[yellow]MCP Servers:[/yellow]")
        manager = MCPManager()
        mcp_status = manager.check_all_servers_health(timeout=3)
        for name, info in mcp_status.items():
            status_icon = "✅" if info.get("status") == "healthy" else "❌"
            rprint(f"  {status_icon} {name}: {info.get('status', 'unknown')}")

        # Project Standards Status
        rprint("\n[yellow]Project Standards:[/yellow]")
        standards_manager = ProjectStandardsManager(console)
        all_results = standards_manager.audit_all_projects()
        summary = standards_manager.get_compliance_summary(all_results)
        rprint(
            f"  📊 {summary['compliant_projects']}/{summary['total_projects']} projects compliant ({summary['compliance_percentage']:.1f}%)"
        )

        # Fleet Status
        rprint("\n[yellow]Fleet Management:[/yellow]")
        fleet_manager = FleetManager(console)
        fleet_status = fleet_manager.get_fleet_status()
        rprint(
            f"  🌐 {fleet_status['active_nodes']}/{fleet_status['total_nodes']} nodes active"
        )

        # Claude Agents Status
        rprint("\n[yellow]Claude Agents:[/yellow]")
        agent_manager = ClaudeAgentManager(console)
        agent_audit = agent_manager.audit_agent_availability()
        rprint(
            f"  🤖 {agent_audit['available_agents']}/{agent_audit['total_agents']} agents available"
        )
        rprint(
            f"  🔧 Global access: {'✅ Enabled' if agent_audit['global_access'] else '❌ Disabled'}"
        )

    except Exception as e:
        rprint(f"[red]Error getting system status: {e}[/red]")
        raise typer.Exit(1)


# =============================================================================
# HELPER FUNCTIONS FOR DISPLAY
# =============================================================================


def _display_compliance_summary(summary: dict[str, Any]) -> None:
    """Display project compliance summary."""
    table = Table(title="Project Compliance Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Projects", str(summary["total_projects"]))
    table.add_row("Compliant Projects", str(summary["compliant_projects"]))
    table.add_row("Compliance Percentage", f"{summary['compliance_percentage']:.1f}%")

    console.print(table)


def _display_project_audit_results(
    results: dict[str, dict[str, Any]], detailed: bool
) -> None:
    """Display project audit results."""
    for project_name, project_results in results.items():
        _display_single_project_audit(project_name, project_results, detailed)
        console.print()


def _display_single_project_audit(
    project_name: str, results: dict[str, Any], detailed: bool
) -> None:
    """Display audit results for a single project."""
    table = Table(title=f"Project Audit: {project_name}")
    table.add_column("Standard", style="cyan")
    table.add_column("Status", style="green")

    if detailed:
        table.add_column("Issues", style="red")
        table.add_column("Recommendations", style="yellow")

    for standard_id, result in results.items():
        status = "✅ Compliant" if result["compliant"] else "❌ Non-compliant"

        if detailed:
            issues = "; ".join(result.get("issues", []))
            recommendations = "; ".join(result.get("recommendations", []))
            table.add_row(standard_id, status, issues, recommendations)
        else:
            table.add_row(standard_id, status)

    console.print(table)


# =============================================================================
# OFFICE DEPLOYMENT MANAGEMENT COMMANDS
# =============================================================================


@office_app.command("register")
def office_register(
    hostname: str = typer.Argument(..., help="Hostname of the office machine"),
    ip_address: str = typer.Argument(..., help="IP address of the machine"),
    ssh_user: str = typer.Option(..., "--user", "-u", help="SSH username"),
    ssh_key: str | None = typer.Option(
        None, "--key", "-k", help="Path to SSH private key"
    ),
) -> None:
    """Register a new office machine for MCP deployment."""
    try:
        office_manager = OfficeDeploymentManager(console)
        success = office_manager.register_office_node(
            hostname, ip_address, ssh_user, ssh_key
        )

        if success:
            rprint(
                f"[green]✅ Registered office machine: {hostname} ({ip_address})[/green]"
            )
            rprint(
                "[cyan]💡 Tip: Run 'mcp-manager office status' to check connectivity[/cyan]"
            )
        else:
            rprint(f"[red]❌ Failed to register machine {hostname}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@office_app.command("list")
def office_list() -> None:
    """List all registered office machines."""
    try:
        office_manager = OfficeDeploymentManager(console)
        nodes = office_manager.list_office_nodes()

        if not nodes:
            rprint("[yellow]No office machines registered yet.[/yellow]")
            rprint("[cyan]💡 Use 'mcp-manager office register' to add machines[/cyan]")
            return

        table = Table(title="Registered Office Machines")
        table.add_column("Hostname", style="cyan")
        table.add_column("IP Address", style="green")
        table.add_column("SSH User", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Last Sync", style="dim")

        for hostname, node in nodes.items():
            status_icon = {
                "active": "🟢 Active",
                "unreachable": "🔴 Unreachable",
                "unknown": "⚪ Unknown",
            }.get(node.get("status", "unknown"), "⚪ Unknown")

            table.add_row(
                hostname,
                node["ip_address"],
                node["ssh_user"],
                status_icon,
                node.get("last_sync", "Never") or "Never",
            )

        console.print(table)
        rprint(f"\n[cyan]Total: {len(nodes)} office machines[/cyan]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@office_app.command("remove")
def office_remove(
    hostname: str = typer.Argument(..., help="Hostname to remove"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation"),
) -> None:
    """Remove an office machine from management."""
    try:
        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to remove office machine '{hostname}'?"
            )
            if not confirm:
                rprint("[yellow]Operation cancelled[/yellow]")
                raise typer.Exit(0)

        office_manager = OfficeDeploymentManager(console)
        success = office_manager.remove_office_node(hostname)

        if not success:
            raise typer.Exit(1)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@office_app.command("status")
def office_status() -> None:
    """Show deployment status for all office machines."""
    try:
        office_manager = OfficeDeploymentManager(console)
        office_manager.display_office_status()

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@office_app.command("check")
def office_check(
    hostname: str = typer.Argument(..., help="Hostname to check connectivity"),
) -> None:
    """Check SSH connectivity to an office machine."""
    try:
        office_manager = OfficeDeploymentManager(console)

        rprint(f"[cyan]🔍 Checking connectivity to {hostname}...[/cyan]")
        is_reachable = office_manager.check_node_connectivity(hostname)

        if is_reachable:
            rprint(f"[green]✅ {hostname} is reachable via SSH[/green]")
        else:
            rprint(f"[red]❌ {hostname} is unreachable[/red]")
            rprint(
                "[yellow]💡 Check SSH configuration, firewall, and network connectivity[/yellow]"
            )
            raise typer.Exit(1)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@office_app.command("deploy")
def office_deploy(
    hostname: str | None = typer.Argument(
        None, help="Deploy to specific machine (default: all machines)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be deployed without making changes"
    ),
) -> None:
    """Deploy MCP configuration to office machine(s)."""
    try:
        office_manager = OfficeDeploymentManager(console)

        if hostname:
            # Deploy to specific machine
            rprint(f"[cyan]🚀 Deploying MCP configuration to {hostname}...[/cyan]")
            success = office_manager.deploy_to_node(hostname, dry_run=dry_run)

            if not success:
                raise typer.Exit(1)

        else:
            # Deploy to all machines
            rprint(
                "[cyan]🚀 Deploying MCP configuration to all office machines...[/cyan]"
            )
            results = office_manager.deploy_to_all_nodes(dry_run=dry_run)

            # Display results
            table = Table(title="Deployment Results")
            table.add_column("Hostname", style="cyan")
            table.add_column("Status", style="green")

            for node_hostname, success in results.items():
                status = "✅ Success" if success else "❌ Failed"
                table.add_row(node_hostname, status)

            console.print(table)

            # Summary
            successful = sum(1 for s in results.values() if s)
            total = len(results)
            rprint(
                f"\n[cyan]Deployment complete: {successful}/{total} successful[/cyan]"
            )

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@office_app.command("verify")
def office_verify(
    hostname: str | None = typer.Argument(
        None, help="Verify specific machine (default: all machines)"
    ),
) -> None:
    """Verify MCP configuration matches across machines."""
    try:
        office_manager = OfficeDeploymentManager(console)

        if hostname:
            # Verify specific machine
            rprint(f"[cyan]🔍 Verifying {hostname}...[/cyan]")
            result = office_manager.verify_node_configuration(hostname)

            if result["status"] == "unreachable":
                rprint(f"[red]❌ {result['message']}[/red]")
                raise typer.Exit(1)
            elif result["status"] == "error":
                rprint(f"[red]❌ {result['message']}[/red]")
                raise typer.Exit(1)
            elif result["match"]:
                rprint(
                    f"[green]✅ Configuration matches ({result['local_servers']} servers)[/green]"
                )
            else:
                rprint("[yellow]⚠️ Configuration mismatch detected[/yellow]")
                rprint(
                    f"   Local servers: {result['local_servers']}, Remote servers: {result['remote_servers']}"
                )
                rprint("[cyan]💡 Run 'mcp-manager office deploy' to synchronize[/cyan]")

        else:
            # Verify all machines
            rprint("[cyan]🔍 Verifying all office machines...[/cyan]")
            results = office_manager.verify_all_nodes()

            table = Table(title="Configuration Verification")
            table.add_column("Hostname", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Servers (Local/Remote)", style="yellow")
            table.add_column("Match", style="magenta")

            for node_hostname, result in results.items():
                if result["status"] == "unreachable":
                    status = "🔴 Unreachable"
                    servers = "N/A"
                    match = "N/A"
                elif result["status"] == "error":
                    status = "❌ Error"
                    servers = "N/A"
                    match = "N/A"
                else:
                    status = "🟢 OK"
                    servers = f"{result['local_servers']}/{result['remote_servers']}"
                    match = "✅ Match" if result["match"] else "❌ Mismatch"

                table.add_row(node_hostname, status, servers, match)

            console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@office_app.command("pull")
def office_pull(
    hostname: str = typer.Argument(..., help="Pull configuration from this machine"),
) -> None:
    """Pull MCP configuration from a remote office machine (reverse sync)."""
    try:
        office_manager = OfficeDeploymentManager(console)

        rprint(f"[cyan]📥 Pulling MCP configuration from {hostname}...[/cyan]")
        rprint("[yellow]⚠️ This will overwrite your local .claude.json[/yellow]")

        confirm = typer.confirm("Continue?")
        if not confirm:
            rprint("[yellow]Operation cancelled[/yellow]")
            raise typer.Exit(0)

        success = office_manager.sync_from_node(hostname)

        if not success:
            raise typer.Exit(1)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@office_app.command("info")
def office_info() -> None:
    """Show information about the current machine."""
    try:
        office_manager = OfficeDeploymentManager(console)
        info = office_manager.get_current_machine_info()

        table = Table(title="Current Machine Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Hostname", info["hostname"])
        table.add_row("IP Address", info["ip_address"])
        table.add_row("SSH User", info["user"])

        console.print(table)

        rprint(
            "\n[cyan]💡 Use these values when registering from another machine:[/cyan]"
        )
        rprint(
            f"   [yellow]mcp-manager office register {info['hostname']} {info['ip_address']} --user {info['user']}[/yellow]"
        )

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    main()
