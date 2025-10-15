"""Gemini CLI Integration commands."""

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from ..cli_utils import handle_cli_errors
from ..gemini_integration import GeminiCLIIntegration

# Create console for output
console = Console()

# Create Gemini command group
gemini_app = typer.Typer(help="💎 Gemini CLI Integration")


@gemini_app.command("sync")
@handle_cli_errors
def gemini_sync(
    force: bool = typer.Option(
        False, "--force", help="Force overwrite existing Gemini configuration"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview changes without applying"
    ),
) -> None:
    """Sync MCP configuration from Claude to Gemini."""
    gemini = GeminiCLIIntegration()

    rprint("[cyan]🔄 Syncing MCP configuration to Gemini CLI...[/cyan]\n")

    # Get current status
    status = gemini.get_status()

    rprint(f"Source: ~/.claude.json ({status.get('claude_servers', 0)} servers)")
    rprint("Target: ~/.gemini/config.json")

    if dry_run:
        rprint("\n[yellow]Dry run mode - no changes will be made[/yellow]")
        return

    # Perform sync
    result = gemini.sync_from_claude(force=force)

    if result.get("success"):
        synced = result.get("servers_synced", [])
        rprint(f"\n[green]✅ Synchronized {len(synced)} servers to Gemini CLI[/green]")
        for server in synced:
            rprint(f"   • {server}")
    else:
        error = result.get("error", "Unknown error")
        rprint(f"\n[red]❌ Sync failed: {error}[/red]")
        raise typer.Exit(1)


@gemini_app.command("status")
@handle_cli_errors
def gemini_status() -> None:
    """Check Gemini CLI integration status."""
    gemini = GeminiCLIIntegration()

    rprint("[cyan]💎 Gemini CLI Integration Status[/cyan]\n")

    # Get status
    status = gemini.get_status()

    # Display status table
    table = Table(title="Configuration Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")

    # Claude configuration
    claude_status = "✅ Exists" if status["claude_config_exists"] else "❌ Missing"
    claude_details = f"{status.get('claude_servers', 0)} servers configured"
    table.add_row("Claude Configuration", claude_status, claude_details)

    # Gemini configuration
    gemini_status_str = "✅ Exists" if status["gemini_config_exists"] else "❌ Missing"
    gemini_details = f"{status.get('gemini_servers', 0)} servers configured"
    table.add_row("Gemini Configuration", gemini_status_str, gemini_details)

    # Sync status
    if status.get("in_sync"):
        sync_status = "✅ In sync"
        sync_details = "Configurations match"
    else:
        sync_status = "❌ Out of sync"
        sync_details = "Run 'mcp-manager gemini sync' to synchronize"

    table.add_row("Sync Status", sync_status, sync_details)

    console.print(table)

    # Additional information
    if status.get("last_sync"):
        rprint(f"\n[dim]Last sync: {status['last_sync']}[/dim]")

    if not status.get("in_sync"):
        rprint(
            "\n[cyan]💡 Tip: Run 'mcp-manager gemini sync' to synchronize configurations[/cyan]"
        )
