"""CLI interface for MCP Manager - Comprehensive Project Standardization System."""

from pathlib import Path
from typing import Any

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .claude_agents import ClaudeAgentManager
from .core import MCPManager
from .exceptions import MCPManagerError
from .fleet_manager import FleetManager
from .hf_integration import HuggingFaceIntegration
from .office_deployment import OfficeDeploymentManager
from .project_standards import ProjectStandardsManager

# Initialize CLI app and console
app = typer.Typer(
    name="mcp-manager",
    help="🚀 MCP Manager - Comprehensive Project Standardization & Fleet Management System",
    rich_markup_mode="rich",
)
console = Console()

# Create sub-applications for different management areas
mcp_app = typer.Typer(help="🔧 MCP Server Management")
project_app = typer.Typer(help="📋 Project Standardization")
fleet_app = typer.Typer(help="🌐 Fleet Management")
agent_app = typer.Typer(help="🤖 Claude Agent Management")
office_app = typer.Typer(help="🏢 Office Deployment Management")

app.add_typer(mcp_app, name="mcp")
app.add_typer(project_app, name="project")
app.add_typer(fleet_app, name="fleet")
app.add_typer(agent_app, name="agent")
app.add_typer(office_app, name="office")


# =============================================================================
# MCP SERVER MANAGEMENT COMMANDS
# =============================================================================


@mcp_app.command("audit")
def mcp_audit(
    detailed: bool = typer.Option(
        False, "--detailed", help="Show detailed configuration analysis"
    ),
    format: str = typer.Option(
        "table", "--format", help="Output format: table, json, yaml"
    ),
) -> None:
    """Audit all MCP server configurations across projects."""
    try:
        manager = MCPManager()
        results = manager.audit_configurations(detailed=detailed)

        if format == "table":
            _display_audit_table(results)
        elif format == "json":
            import json

            console.print_json(json.dumps(results, indent=2))
        else:
            rprint(f"[red]Unsupported format: {format}[/red]")
            raise typer.Exit(1)

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@mcp_app.command("init")
def mcp_init(
    global_config: bool = typer.Option(
        False, "--global", help="Initialize global configuration"
    ),
    force: bool = typer.Option(
        False, "--force", help="Force initialization even if config exists"
    ),
) -> None:
    """Initialize MCP Manager configuration."""
    try:
        manager = MCPManager()

        if global_config:
            manager.init_global_config(force=force)
            rprint(
                "[green]✅ Global MCP configuration initialized successfully[/green]"
            )
        else:
            manager.init_project_config(force=force)
            rprint(
                "[green]✅ Project MCP configuration initialized successfully[/green]"
            )

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@mcp_app.command("add")
def mcp_add(
    name: str = typer.Argument(..., help="MCP server name"),
    type: str = typer.Option(..., "--type", "-t", help="Server type: http or stdio"),
    url: str | None = typer.Option(
        None, "--url", help="Server URL (for HTTP servers)"
    ),
    command: str | None = typer.Option(
        None, "--command", help="Command to run (for stdio servers)"
    ),
    args: list[str] | None = typer.Option(
        None, "--arg", help="Command arguments (can be used multiple times)"
    ),
    header: list[str] | None = typer.Option(
        None, "--header", "-H", help="HTTP headers (format: 'Key: Value')"
    ),
    env: list[str] | None = typer.Option(
        None, "--env", help="Environment variables (format: 'KEY=value')"
    ),
    global_config: bool = typer.Option(
        True, "--global/--local", help="Add to global or local configuration"
    ),
) -> None:
    """Add a new MCP server."""
    try:
        manager = MCPManager()

        # Parse headers
        headers = {}
        if header:
            for h in header:
                if ":" in h:
                    key, value = h.split(":", 1)
                    headers[key.strip()] = value.strip()
                else:
                    rprint(f"[red]Invalid header format: {h}. Use 'Key: Value'[/red]")
                    raise typer.Exit(1)

        # Parse environment variables
        env_vars = {}
        if env:
            for e in env:
                if "=" in e:
                    key, value = e.split("=", 1)
                    env_vars[key.strip()] = value.strip()
                else:
                    rprint(f"[red]Invalid env format: {e}. Use 'KEY=value'[/red]")
                    raise typer.Exit(1)

        manager.add_server(
            name=name,
            server_type=type,
            url=url,
            command=command,
            args=args or [],
            headers=headers,
            env=env_vars,
            global_config=global_config,
        )

        scope = "global" if global_config else "local"
        rprint(f"[green]✅ MCP server '{name}' added to {scope} configuration[/green]")

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@mcp_app.command("remove")
def mcp_remove(
    name: str = typer.Argument(..., help="MCP server name to remove"),
    global_config: bool = typer.Option(
        True, "--global/--local", help="Remove from global or local configuration"
    ),
    force: bool = typer.Option(
        False, "--force", help="Force removal without confirmation"
    ),
) -> None:
    """Remove an MCP server."""
    try:
        manager = MCPManager()

        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to remove MCP server '{name}'?"
            )
            if not confirm:
                rprint("[yellow]Operation cancelled[/yellow]")
                raise typer.Exit(0)

        manager.remove_server(name, global_config=global_config)

        scope = "global" if global_config else "local"
        rprint(
            f"[green]✅ MCP server '{name}' removed from {scope} configuration[/green]"
        )

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@mcp_app.command("status")
def mcp_status(
    name: str | None = typer.Argument(
        None, help="Check specific server (default: all servers)"
    ),
    timeout: int = typer.Option(5, "--timeout", help="Connection timeout in seconds"),
) -> None:
    """Check MCP server health status."""
    try:
        manager = MCPManager()

        if name:
            status_info = manager.check_server_health(name, timeout=timeout)
            _display_single_status(name, status_info)
        else:
            status_results = manager.check_all_servers_health(timeout=timeout)
            _display_status_table(status_results)

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@mcp_app.command("update")
def mcp_update(
    name: str | None = typer.Argument(
        None, help="Update specific server (default: all servers)"
    ),
    all_servers: bool = typer.Option(False, "--all", help="Update all servers"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be updated without making changes"
    ),
) -> None:
    """Update MCP servers."""
    try:
        manager = MCPManager()

        if name and all_servers:
            rprint("[red]Error: Cannot specify both server name and --all[/red]")
            raise typer.Exit(1)

        if name:
            result = manager.update_server(name, dry_run=dry_run)
            _display_update_result(name, result, dry_run)
        else:
            results = manager.update_all_servers(dry_run=dry_run)
            _display_update_results(results, dry_run)

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@mcp_app.command("diagnose")
def mcp_diagnose(
    name: str | None = typer.Argument(
        None, help="Diagnose specific server (default: all servers)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed diagnostic information"
    ),
) -> None:
    """Diagnose MCP server issues."""
    try:
        manager = MCPManager()

        if name:
            diagnosis = manager.diagnose_server(name, verbose=verbose)
            _display_single_diagnosis(name, diagnosis)
        else:
            diagnoses = manager.diagnose_all_servers(verbose=verbose)
            _display_diagnosis_results(diagnoses)

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@mcp_app.command("migrate")
def mcp_migrate(
    project_to_global: bool = typer.Option(
        False, "--project-to-global", help="Migrate project configs to global"
    ),
    backup: bool = typer.Option(
        True, "--backup/--no-backup", help="Create backup before migration"
    ),
    force: bool = typer.Option(
        False, "--force", help="Force migration without confirmation"
    ),
) -> None:
    """Migrate MCP server configurations."""
    try:
        manager = MCPManager()

        if project_to_global:
            if not force:
                confirm = typer.confirm(
                    "Migrate all project-specific MCP configurations to global?"
                )
                if not confirm:
                    rprint("[yellow]Operation cancelled[/yellow]")
                    raise typer.Exit(0)

            results = manager.migrate_project_to_global(create_backup=backup)
            _display_migration_results(results)
        else:
            rprint(
                "[red]Error: No migration type specified. Use --project-to-global[/red]"
            )
            raise typer.Exit(1)

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@mcp_app.command("setup-hf")
def mcp_setup_hf(
    login: bool = typer.Option(False, "--login", help="Login with HF CLI"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Setup Hugging Face MCP server with authentication."""
    try:
        hf_integration = HuggingFaceIntegration()

        # Check current HF login status
        user = hf_integration.get_current_hf_user()
        if user:
            rprint(f"[green]✓ Already logged in as: {user}[/green]")
        elif login:
            if not hf_integration.login_with_hf_cli():
                rprint(
                    "[yellow]Warning: HF CLI login failed, continuing with manual token entry[/yellow]"
                )

        # Configure HF MCP server
        if hf_integration.update_claude_config(dry_run=dry_run):
            rprint("[green]✅ HF MCP server configured successfully[/green]")
        else:
            rprint("[red]❌ Failed to configure HF MCP server[/red]")
            raise typer.Exit(1)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@mcp_app.command("setup-all")
def mcp_setup_all(
    force: bool = typer.Option(
        False, "--force", help="Force setup even if servers exist"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Setup all required MCP servers (GitHub, shadcn, HF) globally."""
    try:
        manager = MCPManager()
        hf_integration = HuggingFaceIntegration()

        rprint("[bold cyan]Setting up all required MCP servers globally[/bold cyan]\n")

        servers_to_add = []

        # Check existing servers
        existing = manager.get_global_servers()

        # GitHub MCP server
        if "github" not in existing or force:
            servers_to_add.append(
                {
                    "name": "github",
                    "type": "http",
                    "url": "https://github.com/mcp",
                    "headers": {},
                }
            )
            rprint("[yellow]• Will add GitHub MCP server[/yellow]")
        else:
            rprint("[green]✓ GitHub MCP server already configured[/green]")

        # shadcn MCP server
        if "shadcn" not in existing or force:
            servers_to_add.append(
                {
                    "name": "shadcn",
                    "type": "stdio",
                    "command": "npx",
                    "args": ["shadcn@latest", "mcp"],
                    "env": {},
                }
            )
            rprint("[yellow]• Will add shadcn MCP server[/yellow]")
        else:
            rprint("[green]✓ shadcn MCP server already configured[/green]")

        # HF MCP server (handled separately)
        if "hf-mcp-server" not in existing or force:
            rprint("[yellow]• Will add HF MCP server with authentication[/yellow]")
        else:
            rprint("[green]✓ HF MCP server already configured[/green]")

        if dry_run:
            rprint("\n[bold yellow]Dry run mode - no changes made[/bold yellow]")
            return

        # Add servers
        for server in servers_to_add:
            try:
                manager.add_server(
                    name=server["name"],
                    server_type=server["type"],
                    url=server.get("url"),
                    command=server.get("command"),
                    args=server.get("args", []),
                    headers=server.get("headers", {}),
                    env=server.get("env", {}),
                    global_config=True,
                )
                rprint(f"[green]✅ Added {server['name']} MCP server[/green]")
            except Exception as e:
                rprint(f"[red]❌ Failed to add {server['name']}: {e}[/red]")

        # Setup HF MCP server with authentication
        if "hf-mcp-server" not in existing or force:
            if hf_integration.update_claude_config(dry_run=False):
                rprint("[green]✅ HF MCP server configured with authentication[/green]")
            else:
                rprint(
                    "[yellow]⚠️ HF MCP server configuration needs manual attention[/yellow]"
                )

        # Final verification
        rprint("\n[bold cyan]Verifying all MCP servers...[/bold cyan]")
        final_servers = manager.get_global_servers()
        required = ["context7", "playwright", "github", "shadcn", "hf-mcp-server", "markitdown"]

        all_present = all(s in final_servers for s in required)
        if all_present:
            rprint(
                f"[green]✅ All {len(required)} required MCP servers are now configured globally![/green]"
            )
            for server in required:
                rprint(f"   • {server}")
        else:
            missing = [s for s in required if s not in final_servers]
            rprint(f"[yellow]⚠️ Missing servers: {', '.join(missing)}[/yellow]")

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _display_audit_table(results: dict) -> None:
    """Display audit results in a table format."""
    table = Table(title="MCP Configuration Audit")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")

    # Add rows based on audit results
    for component, info in results.items():
        status = "✅ OK" if info.get("status") == "ok" else "❌ Issues"
        details = str(info.get("details", ""))
        table.add_row(component, status, details)

    console.print(table)


def _display_single_status(name: str, status_info: dict) -> None:
    """Display status for a single server."""
    status = status_info.get("status", "unknown")
    if status == "healthy":
        rprint(f"[green]✅ {name}: Healthy[/green]")
    elif status == "unhealthy":
        rprint(f"[red]❌ {name}: Unhealthy[/red]")
    else:
        rprint(f"[yellow]⚠️ {name}: {status}[/yellow]")

    if "details" in status_info:
        console.print(f"   Details: {status_info['details']}")


def _display_status_table(status_results: dict) -> None:
    """Display status results in a table format."""
    table = Table(title="MCP Server Health Status")
    table.add_column("Server", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Response Time", style="yellow")
    table.add_column("Details", style="dim")

    for name, info in status_results.items():
        status = info.get("status", "unknown")
        response_time = f"{info.get('response_time', 0):.2f}s"
        details = info.get("details", "")

        status_icon = {"healthy": "✅", "unhealthy": "❌", "unknown": "⚠️"}.get(
            status, "❓"
        )

        table.add_row(name, f"{status_icon} {status}", response_time, details)

    console.print(table)


def _display_update_result(name: str, result: dict, dry_run: bool) -> None:
    """Display update result for a single server."""
    action = "Would update" if dry_run else "Updated"
    if result.get("updated"):
        rprint(f"[green]✅ {action} {name}[/green]")
    else:
        rprint(f"[yellow]ℹ️ {name} is already up to date[/yellow]")


def _display_update_results(results: dict, dry_run: bool) -> None:
    """Display update results for multiple servers."""
    action = "Update Preview" if dry_run else "Update Results"
    table = Table(title=action)
    table.add_column("Server", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")

    for name, result in results.items():
        status = "✅ Updated" if result.get("updated") else "ℹ️ Up to date"
        details = result.get("details", "")
        table.add_row(name, status, details)

    console.print(table)


def _display_single_diagnosis(name: str, diagnosis: dict) -> None:
    """Display diagnosis for a single server."""
    console.print(f"\n[bold cyan]Diagnosis for {name}[/bold cyan]")

    for check, result in diagnosis.items():
        status = result.get("status", "unknown")
        if status == "pass":
            rprint(f"[green]✅ {check}[/green]")
        elif status == "fail":
            rprint(f"[red]❌ {check}[/red]")
        else:
            rprint(f"[yellow]⚠️ {check}[/yellow]")

        if "details" in result:
            console.print(f"   {result['details']}")


def _display_diagnosis_results(diagnoses: dict) -> None:
    """Display diagnosis results for multiple servers."""
    for name, diagnosis in diagnoses.items():
        _display_single_diagnosis(name, diagnosis)
        console.print()  # Add spacing between servers


def _display_migration_results(results: dict) -> None:
    """Display migration results."""
    table = Table(title="Migration Results")
    table.add_column("Project", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Servers Migrated", style="yellow")

    for project, result in results.items():
        status = "✅ Success" if result.get("success") else "❌ Failed"
        servers = ", ".join(result.get("servers", []))
        table.add_row(project, status, servers)

    console.print(table)


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
            rprint(
                "[cyan]💡 Use 'mcp-manager office register' to add machines[/cyan]"
            )
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
            rprint("[cyan]🚀 Deploying MCP configuration to all office machines...[/cyan]")
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
            rprint(f"\n[cyan]Deployment complete: {successful}/{total} successful[/cyan]")

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
                rprint(
                    "[cyan]💡 Run 'mcp-manager office deploy' to synchronize[/cyan]"
                )

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
