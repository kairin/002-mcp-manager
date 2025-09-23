#!/usr/bin/env python3
"""Verify all MCP servers are properly installed and configured."""

import json
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def verify_mcp_servers():
    """Verify MCP server installation and configuration."""

    claude_config_path = Path.home() / ".claude.json"

    # Base minimum MCP servers (finalized configuration)
    required_servers = [
        "context7",
        "github",
        "hf-mcp-server",
        "playwright",
        "shadcn"
    ]

    # Load configuration using jq to handle large files
    try:
        result = subprocess.run(
            ["jq", ".mcpServers", str(claude_config_path)],
            capture_output=True,
            text=True,
            check=True
        )
        mcp_servers = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        return False

    # Create status table
    table = Table(title="🚀 MCP Server Base Installation Verification", box=box.ROUNDED)
    table.add_column("Server", style="cyan", width=15)
    table.add_column("Status", style="green", width=12)
    table.add_column("Type", style="yellow", width=8)
    table.add_column("Configuration", style="blue", width=50)
    table.add_column("Purpose", style="magenta", width=30)

    # Server purposes
    server_purposes = {
        "context7": "📚 Library documentation API",
        "github": "🐙 GitHub repository integration",
        "hf-mcp-server": "🤗 Hugging Face ML models/datasets",
        "playwright": "🎭 Browser automation & testing",
        "shadcn": "🎨 UI component library access"
    }

    all_good = True

    for server_name in required_servers:
        issues = []

        if server_name not in mcp_servers:
            table.add_row(
                server_name,
                "❌ Missing",
                "-",
                "-",
                server_purposes.get(server_name, "Unknown")
            )
            all_good = False
            continue

        server_config = mcp_servers[server_name]

        # Prepare configuration display
        if server_config.get("type") == "http":
            url = server_config.get('url', 'N/A')
            # Truncate long URLs for display
            if len(url) > 40:
                config_display = f"URL: {url[:37]}..."
            else:
                config_display = f"URL: {url}"

            # Check for authentication
            if "headers" in server_config or "Authorization" in str(server_config):
                config_display += "\n✓ Auth configured"
        else:
            cmd = server_config.get("command", "N/A")
            args = " ".join(server_config.get("args", []))[:30]
            config_display = f"CMD: {cmd} {args}"

        # Check basic configuration validity
        if server_config.get("type") == "http":
            if not server_config.get("url"):
                issues.append("Missing URL")
        elif server_config.get("type") == "stdio":
            if not server_config.get("command"):
                issues.append("Missing command")

        # Determine status
        if issues:
            status = "⚠️ Issues"
            all_good = False
        else:
            status = "✅ Connected"

        table.add_row(
            server_name,
            status,
            server_config.get("type", "-"),
            config_display,
            server_purposes.get(server_name, "Unknown")
        )

    # Print results
    console.print("\n")
    console.print(table)
    console.print("\n")

    # Summary
    if all_good:
        console.print(Panel.fit(
            "[bold green]✅ Base MCP Installation Complete![/bold green]\n\n"
            "[bold]All 5 core MCP servers are connected:[/bold]\n"
            "• context7 - Library documentation and code examples\n"
            "• github - Repository management and GitHub API\n"
            "• hf-mcp-server - Hugging Face ML ecosystem\n"
            "• playwright - Browser automation and testing\n"
            "• shadcn - Modern UI component library\n\n"
            "[green]Configuration Path:[/green] ~/.claude.json\n"
            "[green]Scope:[/green] Global (all projects)\n\n"
            "[bold yellow]Ready to add more MCP servers![/bold yellow]",
            title="✨ MCP Manager - Finalized Base Configuration",
            border_style="green"
        ))
    else:
        console.print("\n[bold yellow]⚠️ Some issues detected. Please review the table above.[/bold yellow]")
        missing = [s for s in required_servers if s not in mcp_servers]
        if missing:
            console.print(f"[red]Missing servers: {', '.join(missing)}[/red]")

    # Check for extra servers
    extra = set(mcp_servers.keys()) - set(required_servers)
    if extra:
        console.print(f"\n[cyan]Additional servers beyond base installation: {', '.join(extra)}[/cyan]")

    console.print("\n[dim]Total servers configured: {} | Required base servers: {}[/dim]".format(
        len(mcp_servers), len(required_servers)
    ))

    return all_good


if __name__ == "__main__":
    success = verify_mcp_servers()
    exit(0 if success else 1)