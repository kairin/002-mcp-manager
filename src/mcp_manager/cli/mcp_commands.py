"""MCP Server Management commands."""


import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from ..cli_utils import handle_cli_errors
from ..core import MCPManager
from ..hf_integration import HuggingFaceIntegration
from ..mcp_installer import MCPInstaller

# Create console for output
console = Console()

# Create MCP command group
mcp_app = typer.Typer(help="🔧 MCP Server Management")


@mcp_app.command("audit")
@handle_cli_errors
def mcp_audit(
    detailed: bool = typer.Option(
        False, "--detailed", help="Show detailed configuration analysis"
    ),
    format: str = typer.Option(
        "table", "--format", help="Output format: table, json, yaml"
    ),
) -> None:
    """Audit all MCP server configurations across projects."""
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


@mcp_app.command("init")
@handle_cli_errors
def mcp_init(
    global_config: bool = typer.Option(
        False, "--global", help="Initialize global configuration"
    ),
    force: bool = typer.Option(
        False, "--force", help="Force initialization even if config exists"
    ),
) -> None:
    """Initialize MCP Manager configuration."""
    manager = MCPManager()

    if global_config:
        manager.init_global_config(force=force)
        rprint("[green]✅ Global MCP configuration initialized successfully[/green]")
    else:
        manager.init_project_config(force=force)
        rprint("[green]✅ Project MCP configuration initialized successfully[/green]")


@mcp_app.command("add")
@handle_cli_errors
def mcp_add(
    name: str = typer.Argument(..., help="MCP server name"),
    type: str = typer.Option(..., "--type", "-t", help="Server type: http or stdio"),
    url: str | None = typer.Option(None, "--url", help="Server URL (for HTTP servers)"),
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


@mcp_app.command("remove")
@handle_cli_errors
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
    manager = MCPManager()

    if not force:
        confirm = typer.confirm(f"Are you sure you want to remove MCP server '{name}'?")
        if not confirm:
            rprint("[yellow]Operation cancelled[/yellow]")
            raise typer.Exit(0)

    manager.remove_server(name, global_config=global_config)

    scope = "global" if global_config else "local"
    rprint(f"[green]✅ MCP server '{name}' removed from {scope} configuration[/green]")


@mcp_app.command("status")
@handle_cli_errors
def mcp_status(
    name: str | None = typer.Argument(
        None, help="Check specific server (default: all servers)"
    ),
    timeout: int = typer.Option(5, "--timeout", help="Connection timeout in seconds"),
) -> None:
    """Check MCP server health status."""
    manager = MCPManager()

    if name:
        status_info = manager.check_server_health(name, timeout=timeout)
        _display_single_status(name, status_info)
    else:
        status_results = manager.check_all_servers_health(timeout=timeout)
        _display_status_table(status_results)


@mcp_app.command("update")
@handle_cli_errors
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


@mcp_app.command("diagnose")
@handle_cli_errors
def mcp_diagnose(
    name: str | None = typer.Argument(
        None, help="Diagnose specific server (default: all servers)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed diagnostic information"
    ),
) -> None:
    """Diagnose MCP server issues."""
    manager = MCPManager()

    if name:
        diagnosis = manager.diagnose_server(name, verbose=verbose)
        _display_single_diagnosis(name, diagnosis)
    else:
        diagnoses = manager.diagnose_all_servers(verbose=verbose)
        _display_diagnosis_results(diagnoses)


@mcp_app.command("migrate")
@handle_cli_errors
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
        rprint("[red]Error: No migration type specified. Use --project-to-global[/red]")
        raise typer.Exit(1)


@mcp_app.command("setup-hf")
@handle_cli_errors
def mcp_setup_hf(
    login: bool = typer.Option(False, "--login", help="Login with HF CLI"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Setup Hugging Face MCP server with authentication."""
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


@mcp_app.command("setup-all")
@handle_cli_errors
def mcp_setup_all(
    force: bool = typer.Option(
        False, "--force", help="Force setup even if servers exist"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Setup all required MCP servers (GitHub, shadcn, HF) globally."""
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
    required = [
        "context7",
        "playwright",
        "github",
        "shadcn",
        "hf-mcp-server",
        "markitdown",
    ]

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


@mcp_app.command("install-all")
@handle_cli_errors
def mcp_install_all(
    skip_auth: bool = typer.Option(
        False, "--skip-auth", help="Skip authentication setup"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be installed without making changes"
    ),
) -> None:
    """Install and configure all 6 MCP servers system-wide (includes MarkItDown)."""
    installer = MCPInstaller(console)

    rprint("[bold cyan]📦 Installing All MCP Servers System-Wide[/bold cyan]\n")
    rprint(
        "[dim]This ensures all servers are available globally, not just in this repo[/dim]\n"
    )

    # Install all servers
    results = installer.install_all_servers(skip_auth=skip_auth, dry_run=dry_run)

    # Display results
    installer.display_installation_status(results)

    if not dry_run:
        # Get summary
        summary = installer.get_installation_summary()

        rprint("\n[bold cyan]📊 Installation Summary[/bold cyan]")
        rprint(f"   Total Servers: {summary['total_servers']}")
        rprint(f"   Configured: {summary['configured']}")
        rprint(f"   Healthy: {summary['healthy']}")
        rprint(f"   Needs Auth: {summary['needs_auth']}")
        rprint(f"   Unhealthy: {summary['unhealthy']}")

        if summary["healthy"] == summary["total_servers"]:
            rprint(
                "\n[green]✅ All MCP servers installed and operational system-wide![/green]"
            )
        elif summary["needs_auth"] > 0:
            rprint(
                f"\n[yellow]⚠️ {summary['needs_auth']} server(s) need authentication setup[/yellow]"
            )
            rprint(
                "[cyan]💡 Run the suggested commands shown above to complete setup[/cyan]"
            )
        else:
            rprint(
                f"\n[red]❌ {summary['unhealthy']} server(s) failed to install[/red]"
            )


@mcp_app.command("verify-all")
@handle_cli_errors
def mcp_verify_all() -> None:
    """Verify all MCP servers are installed and working system-wide."""
    installer = MCPInstaller(console)

    rprint("[bold cyan]🔍 Verifying All MCP Servers[/bold cyan]\n")

    # Verify all servers
    results = installer.verify_all_servers()

    # Display results
    installer.display_verification_status(results)

    # Count healthy servers
    healthy_count = sum(1 for v in results.values() if v.get("status") == "healthy")
    total_count = len(results)

    if healthy_count == total_count:
        rprint(
            f"\n[green]✅ All {total_count} MCP servers are healthy and operational![/green]"
        )
        rprint("[dim]Servers are configured globally and available system-wide[/dim]")
    else:
        rprint(
            f"\n[yellow]⚠️ {total_count - healthy_count}/{total_count} server(s) need attention[/yellow]"
        )
        rprint("[cyan]💡 Run 'mcp-manager mcp install-all' to fix issues[/cyan]")


@mcp_app.command("install")
@handle_cli_errors
def mcp_install(
    server_name: str = typer.Argument(..., help="MCP server name to install"),
    skip_auth: bool = typer.Option(
        False, "--skip-auth", help="Skip authentication setup"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be installed without making changes"
    ),
) -> None:
    """Install a specific MCP server system-wide."""
    installer = MCPInstaller(console)

    rprint(f"[bold cyan]📦 Installing {server_name} MCP Server[/bold cyan]\n")

    # Install specific server
    result = installer.install_server(server_name, skip_auth=skip_auth, dry_run=dry_run)

    # Display result
    if result.get("success"):
        rprint(f"[green]✅ {server_name} installed successfully![/green]")
        for detail in result.get("details", []):
            rprint(f"   • {detail}")
    else:
        rprint(f"[red]❌ {server_name} installation failed[/red]")
        for detail in result.get("details", []):
            rprint(f"   • {detail}")
        raise typer.Exit(1)


# =============================================================================
# HELPER FUNCTIONS FOR DISPLAY
# =============================================================================


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
