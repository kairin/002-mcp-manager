#!/usr/bin/env python3
"""Setup HF MCP server using HF CLI for authentication."""

import json
import subprocess
import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

console = Console()

def get_hf_token_from_cli():
    """Get HF token after CLI login."""
    # Check if logged in
    result = subprocess.run(
        ["uv", "run", "hf", "auth", "whoami"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0 or "Not logged in" in result.stdout:
        console.print("[yellow]Not logged in to Hugging Face[/yellow]")
        console.print("\n[cyan]Please login to Hugging Face to get your token.[/cyan]")
        console.print("You'll be redirected to your browser to authenticate.")

        # Run HF CLI login
        login_result = subprocess.run(["uv", "run", "hf", "auth", "login"])

        if login_result.returncode != 0:
            console.print("[red]Login failed[/red]")
            return None

        console.print("[green]✓ Successfully logged in to Hugging Face[/green]")
    else:
        console.print(f"[green]✓ Already logged in to Hugging Face[/green]")

    # Try to get token from HF cache
    hf_token_path = Path.home() / ".cache" / "huggingface" / "token"

    if hf_token_path.exists():
        with open(hf_token_path, 'r') as f:
            token = f.read().strip()
            if token:
                console.print("[green]✓ Retrieved token from HF CLI cache[/green]")
                return token

    # Alternative: Try environment variable
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if token:
        console.print("[green]✓ Retrieved token from environment[/green]")
        return token

    console.print("[yellow]Warning: Could not retrieve token automatically[/yellow]")
    return None

def update_hf_mcp_server(token=None):
    """Update HF MCP server configuration with token."""
    claude_config_path = Path.home() / ".claude.json"

    # Load existing config
    with open(claude_config_path, "r") as f:
        config = json.load(f)

    # Update HF MCP server
    if "hf-mcp-server" not in config.get("mcpServers", {}):
        config["mcpServers"]["hf-mcp-server"] = {
            "type": "http",
            "url": "https://huggingface.co/mcp"
        }

    if token:
        if "headers" not in config["mcpServers"]["hf-mcp-server"]:
            config["mcpServers"]["hf-mcp-server"]["headers"] = {}

        config["mcpServers"]["hf-mcp-server"]["headers"]["Authorization"] = f"Bearer {token}"
        console.print("[green]✓ Added authentication token to HF MCP server[/green]")
    else:
        console.print("[yellow]⚠️ No token provided, HF MCP server will work with limited access[/yellow]")

    # Save config
    with open(claude_config_path, "w") as f:
        json.dump(config, f, indent=2)

    console.print("[green]✓ HF MCP server configuration updated[/green]")

def main():
    """Main setup flow."""
    console.print("[bold cyan]Setting up Hugging Face MCP Server with CLI Authentication[/bold cyan]\n")

    # Get token from HF CLI
    token = get_hf_token_from_cli()

    if token:
        console.print("\n[green]Token retrieved successfully![/green]")
        if Confirm.ask("Update HF MCP server with this token?"):
            update_hf_mcp_server(token)
            console.print("\n[bold green]✅ Setup complete![/bold green]")
            console.print("HF MCP server is now configured with authentication.")
        else:
            console.print("[yellow]Setup cancelled[/yellow]")
    else:
        console.print("\n[yellow]Could not retrieve token automatically.[/yellow]")
        if Confirm.ask("Configure HF MCP server without authentication?"):
            update_hf_mcp_server(None)
            console.print("\n[yellow]HF MCP server configured without authentication.[/yellow]")
            console.print("You can add authentication later by running this script again.")
        else:
            console.print("[red]Setup cancelled[/red]")

if __name__ == "__main__":
    main()