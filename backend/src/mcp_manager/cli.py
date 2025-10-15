"""CLI interface for MCP Manager."""

from pathlib import Path

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .core import MCPManager
from .exceptions import MCPManagerError
from .python_env import detect_distribution, get_installation_source, get_python_version
from .uv_config import validate_uv_config

# Initialize CLI app and console
app = typer.Typer(
    name="mcp-manager",
    help="Centralized MCP Server Management for Claude Code",
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def audit(
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


@app.command()
def init(
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


@app.command()
def add(
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


@app.command()
def remove(
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


@app.command()
def status(
    name: str | None = typer.Argument(
        None, help="Check specific server (default: all servers)"
    ),
    timeout: int = typer.Option(5, "--timeout", help="Connection timeout in seconds"),
    show_python: bool = typer.Option(
        True, "--python/--no-python", help="Show Python environment information"
    ),
) -> None:
    """Check MCP server health status."""
    try:
        manager = MCPManager()

        # T056: Display Python version and UV config for quick diagnostics
        if show_python:
            _display_python_environment(manager)
            console.print()  # Add spacing

        if name:
            status_info = manager.check_server_health(name, timeout=timeout)
            _display_single_status(name, status_info)
        else:
            status_results = manager.check_all_servers_health(timeout=timeout)
            _display_status_table(status_results)

    except MCPManagerError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def update(
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


@app.command()
def diagnose(
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


@app.command()
def migrate(
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


def _display_python_environment(manager: MCPManager) -> None:
    """Display Python environment and UV configuration for diagnostics.

    Implements T056: Add Python version and UV config to status output.

    Args:
        manager: MCPManager instance with validated Python environment
    """
    table = Table(title="Python Environment (Constitutional Requirements)")
    table.add_column("Component", style="cyan", width=25)
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow", width=15)

    # Get system Python information
    python_path = manager.get_system_python_path()
    version = get_python_version(python_path)
    source = get_installation_source(python_path)
    distro = detect_distribution()

    # Python version
    if version:
        version_str = f"{version[0]}.{version[1]}.{version[2]}"
        version_status = "✅ Valid" if version[:2] == (3, 13) else "❌ Invalid"
    else:
        version_str = "Unknown"
        version_status = "❌ Error"

    table.add_row("Python Version", version_str, version_status)

    # Python path
    source_display = {
        "package_manager": "Package Manager",
        "manual_install": "Manual Install",
        "unknown": "Unknown",
    }.get(source, source)
    table.add_row("Python Path", str(python_path), f"✅ {source_display}")

    # Distribution
    table.add_row("System", distro, "ℹ️ Detected")

    # UV Configuration
    try:
        uv_config = validate_uv_config(Path.cwd())

        python_downloads = uv_config.get("python_downloads", "not set")
        downloads_status = (
            "✅ Valid" if python_downloads in ("manual", "never") else "❌ Invalid"
        )
        table.add_row("UV Python Downloads", python_downloads, downloads_status)

        python_preference = uv_config.get("python_preference", "not set")
        preference_status = (
            "✅ Valid" if python_preference == "only-system" else "❌ Invalid"
        )
        table.add_row("UV Python Preference", python_preference, preference_status)

    except Exception as e:
        table.add_row("UV Configuration", str(e), "❌ Error")

    console.print(table)


def main() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
