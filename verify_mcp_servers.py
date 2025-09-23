#!/usr/bin/env python3
"""Verify all MCP servers are properly installed and configured."""

import json
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def verify_mcp_servers():
    """Verify MCP server installation and configuration."""

    claude_config_path = Path.home() / ".claude.json"

    # Required servers
    required_servers = [
        "context7",
        "playwright",
        "github",
        "shadcn",
        "hf-mcp-server"
    ]

    # Expected configurations
    expected_configs = {
        "context7": {
            "type": "http",
            "url": "https://mcp.context7.com/mcp"
        },
        "playwright": {
            "type": "stdio",
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        },
        "github": {
            "type": "http",
            "url": "https://github.com/mcp"
        },
        "shadcn": {
            "type": "stdio",
            "command": "npx",
            "args": ["shadcn@latest", "mcp"]
        },
        "hf-mcp-server": {
            "type": "http",
            "url": "https://huggingface.co/mcp"
        }
    }

    # Load configuration
    with open(claude_config_path, "r") as f:
        config = json.load(f)

    mcp_servers = config.get("mcpServers", {})

    # Create status table
    table = Table(title="MCP Server Verification Report", box=box.ROUNDED)
    table.add_column("Server", style="cyan", width=15)
    table.add_column("Status", style="green", width=12)
    table.add_column("Type", style="yellow", width=8)
    table.add_column("Configuration", style="blue", width=50)
    table.add_column("Issues", style="red", width=30)

    all_good = True

    for server_name in required_servers:
        issues = []

        if server_name not in mcp_servers:
            table.add_row(
                server_name,
                "❌ Missing",
                "-",
                "-",
                "Server not configured"
            )
            all_good = False
            continue

        server_config = mcp_servers[server_name]
        expected = expected_configs[server_name]

        # Check type
        if server_config.get("type") != expected["type"]:
            issues.append(f"Wrong type: {server_config.get('type')}")

        # Check URL for HTTP servers
        if expected["type"] == "http":
            if server_config.get("url") != expected.get("url"):
                issues.append(f"Wrong URL: {server_config.get('url')}")

        # Check command for stdio servers
        if expected["type"] == "stdio":
            if server_config.get("command") != expected.get("command"):
                issues.append(f"Wrong command: {server_config.get('command')}")

            # Check args
            actual_args = server_config.get("args", [])
            expected_args = expected.get("args", [])
            if actual_args != expected_args:
                issues.append(f"Wrong args: {actual_args}")

        # Prepare configuration display
        if server_config.get("type") == "http":
            config_display = f"URL: {server_config.get('url', 'N/A')}"
            if server_name == "context7" and "headers" in server_config:
                if "CONTEXT7_API_KEY" in server_config["headers"]:
                    config_display += "\n✓ API Key configured"
            elif server_name == "hf-mcp-server" and "headers" in server_config:
                if server_config["headers"].get("Authorization"):
                    config_display += "\n✓ Auth token configured"
                else:
                    config_display += "\n⚠️ No auth token"
                    issues.append("No authentication token")
        else:
            cmd = server_config.get("command", "N/A")
            args = " ".join(server_config.get("args", []))
            config_display = f"Command: {cmd} {args}"

        # Determine status
        if issues:
            status = "⚠️ Issues"
            all_good = False
        else:
            status = "✅ OK"

        table.add_row(
            server_name,
            status,
            server_config.get("type", "-"),
            config_display,
            "\n".join(issues) if issues else "None"
        )

    # Print results
    console.print("\n")
    console.print(table)
    console.print("\n")

    # Summary
    console.print("[bold]Summary:[/bold]")
    console.print(f"Total servers configured: {len(mcp_servers)}")
    console.print(f"Required servers: {len(required_servers)}")

    if all_good:
        console.print("\n[bold green]✅ All MCP servers are properly installed and configured![/bold green]")
        console.print("[green]All Claude Code projects can now use these servers globally.[/green]")
    else:
        console.print("\n[bold yellow]⚠️ Some issues detected. Please review the table above.[/bold yellow]")
        missing = [s for s in required_servers if s not in mcp_servers]
        if missing:
            console.print(f"[red]Missing servers: {', '.join(missing)}[/red]")

    # Check for extra servers
    extra = set(mcp_servers.keys()) - set(required_servers)
    if extra:
        console.print(f"\n[cyan]Additional servers configured: {', '.join(extra)}[/cyan]")

    return all_good


if __name__ == "__main__":
    verify_mcp_servers()