#!/usr/bin/env python3
"""
Hugging Face MCP Server Integration Module

This module provides integration between Hugging Face CLI authentication
and MCP server configuration, allowing automatic token management.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()


class HuggingFaceIntegration:
    """Manages Hugging Face token integration with MCP servers."""

    def __init__(self) -> None:
        self.hf_token_path = Path.home() / ".cache" / "huggingface" / "token"
        self.claude_config_path = Path.home() / ".claude.json"

    def get_hf_token_from_env(self) -> str | None:
        """Get Hugging Face token from environment variables."""
        return os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")

    def get_hf_token_from_cache(self) -> str | None:
        """Get Hugging Face token from local cache file."""
        if self.hf_token_path.exists():
            try:
                with open(self.hf_token_path) as f:
                    token = f.read().strip()
                    if token:
                        return token
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Could not read HF token from cache: {e}[/yellow]"
                )
        return None

    def prompt_for_hf_token(self) -> str | None:
        """Prompt user for Hugging Face token."""
        console.print("\n[bold cyan]Hugging Face MCP Server Setup[/bold cyan]")
        console.print(
            "To use the Hugging Face MCP server, you need a Hugging Face API token."
        )
        console.print("You can get one from: https://huggingface.co/settings/tokens")

        token = Prompt.ask(
            "\n[green]Enter your Hugging Face token[/green]", password=True
        )

        if token and Confirm.ask("Save token locally for future use?"):
            self.save_hf_token_to_cache(token)

        return token

    def save_hf_token_to_cache(self, token: str) -> bool:
        """Save Hugging Face token to local cache."""
        try:
            self.hf_token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.hf_token_path, "w") as f:
                f.write(token)
            self.hf_token_path.chmod(0o600)  # Secure file permissions
            console.print("[green]✓ Token saved to local cache[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to save token: {e}[/red]")
            return False

    def get_or_prompt_token(self) -> str | None:
        """Get HF token from various sources or prompt for it."""
        # Try environment variable first
        token = self.get_hf_token_from_env()
        if token:
            console.print("[green]✓ Using HF token from environment variable[/green]")
            return token

        # Try cached token
        token = self.get_hf_token_from_cache()
        if token:
            console.print("[green]✓ Using HF token from local cache[/green]")
            return token

        # Try to login with HF CLI
        console.print("[yellow]No token found. Attempting HF CLI login...[/yellow]")
        if self.login_with_hf_cli():
            # Try to get token after login
            token = self.get_hf_token_from_cache()
            if token:
                console.print("[green]✓ Retrieved token from HF CLI[/green]")
                return token

        # Prompt for token as last resort
        return self.prompt_for_hf_token()

    def configure_hf_mcp_server(self, token: str | None = None) -> dict[str, Any]:
        """Configure the Hugging Face MCP server with authentication."""
        if not token:
            token = self.get_or_prompt_token()

        if not token:
            console.print(
                "[yellow]Warning: No HF token provided. Server may have limited functionality.[/yellow]"
            )

        return {
            "type": "http",
            "url": "https://huggingface.co/mcp",
            "headers": {"Authorization": f"Bearer {token}" if token else None},
        }

    def update_claude_config(self, dry_run: bool = False) -> bool:
        """Update Claude configuration with HF MCP server."""
        try:
            # Load existing config
            config = {}
            if self.claude_config_path.exists():
                with open(self.claude_config_path) as f:
                    config = json.load(f)

            # Ensure mcpServers section exists
            if "mcpServers" not in config:
                config["mcpServers"] = {}

            # Check if hf-mcp-server already configured
            existing_hf = config["mcpServers"].get("hf-mcp-server", {})
            existing_token = existing_hf.get("headers", {}).get("Authorization")

            if existing_token and existing_token != "None":
                console.print(
                    "[cyan]HF MCP server already configured with token[/cyan]"
                )
                if not Confirm.ask("Update with new token?"):
                    return True

            # Configure HF MCP server
            hf_config = self.configure_hf_mcp_server()

            if dry_run:
                console.print("\n[bold]Dry run - would add to configuration:[/bold]")
                console.print(json.dumps({"hf-mcp-server": hf_config}, indent=2))
                return True

            # Update configuration
            config["mcpServers"]["hf-mcp-server"] = hf_config

            # Save configuration
            with open(self.claude_config_path, "w") as f:
                json.dump(config, f, indent=2)

            console.print("[green]✓ Successfully configured HF MCP server[/green]")
            return True

        except Exception as e:
            console.print(f"[red]Failed to update configuration: {e}[/red]")
            return False

    def verify_hf_cli_installation(self) -> bool:
        """Check if huggingface-hub CLI is installed."""
        try:
            # Check using uv run
            result = subprocess.run(
                ["uv", "run", "hf", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                console.print(
                    f"[green]✓ huggingface-hub CLI available: {result.stdout.strip()}[/green]"
                )
                return True
        except:
            pass

        # Try direct Python import
        try:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-c",
                    "import huggingface_hub; print(huggingface_hub.__version__)",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                console.print(
                    f"[green]✓ huggingface-hub version {result.stdout.strip()} installed[/green]"
                )
                console.print(
                    "[yellow]Note: Use 'uv run hf' to run CLI commands[/yellow]"
                )
                return True
        except:
            pass

        console.print("[yellow]huggingface-hub CLI not installed[/yellow]")
        console.print("Install with: uv sync (already in pyproject.toml dependencies)")
        return False

    def login_with_hf_cli(self) -> bool:
        """Use HF CLI to login and store token."""
        try:
            console.print("[cyan]Launching HF CLI login...[/cyan]")
            result = subprocess.run(["uv", "run", "hf", "auth", "login"], text=True)
            if result.returncode == 0:
                console.print("[green]✓ Successfully logged in with HF CLI[/green]")
                return True
        except Exception as e:
            console.print(f"[red]HF CLI login failed: {e}[/red]")
        return False

    def get_current_hf_user(self) -> str | None:
        """Get current logged-in HF user."""
        try:
            result = subprocess.run(
                ["uv", "run", "hf", "auth", "whoami"], capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        return None


def main() -> None:
    """Main entry point for HF integration setup."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Configure Hugging Face MCP server integration"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify HF CLI installation"
    )
    parser.add_argument("--login", action="store_true", help="Login with HF CLI")
    parser.add_argument("--whoami", action="store_true", help="Show current HF user")
    parser.add_argument(
        "--setup", action="store_true", help="Complete setup with MCP server"
    )
    args = parser.parse_args()

    integration = HuggingFaceIntegration()

    if args.verify:
        integration.verify_hf_cli_installation()
        return

    if args.login:
        if integration.login_with_hf_cli():
            # After successful login, offer to configure MCP server
            if Confirm.ask("\n[cyan]Configure HF MCP server now?[/cyan]"):
                integration.update_claude_config()
        return

    if args.whoami:
        user = integration.get_current_hf_user()
        if user:
            console.print(f"[green]Logged in as: {user}[/green]")
        else:
            console.print("[yellow]Not logged in to Hugging Face[/yellow]")
            console.print(
                "Use: uv run python src/mcp_manager/hf_integration.py --login"
            )
        return

    if args.setup or not any(vars(args).values()):
        console.print(
            "[bold cyan]Setting up Hugging Face MCP Server Integration[/bold cyan]"
        )

        # Check if already logged in
        user = integration.get_current_hf_user()
        if user:
            console.print(f"[green]✓ Already logged in as: {user}[/green]")
        else:
            console.print("[yellow]Not logged in to Hugging Face[/yellow]")
            if Confirm.ask("Login now?"):
                if not integration.login_with_hf_cli():
                    console.print(
                        "[red]Login failed. Continuing with manual token entry...[/red]"
                    )

        # Update Claude configuration
        if integration.update_claude_config(dry_run=args.dry_run):
            console.print("\n[green]✓ Setup complete![/green]")
            console.print("The HF MCP server is now configured with authentication.")
        else:
            console.print(
                "\n[red]Setup failed. Please check the error messages above.[/red]"
            )


if __name__ == "__main__":
    main()
