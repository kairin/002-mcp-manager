#!/usr/bin/env python3
"""
Gemini CLI Secure Configuration Migration Script

This script migrates Gemini CLI MCP server configurations from hardcoded API keys
to environment variable references, fixing the security vulnerability.

CRITICAL SECURITY FIX: Addresses hardcoded tokens in ~/.gemini/settings.json
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()


def backup_config(config_path: Path) -> Path:
    """Create a backup of the configuration file."""
    backup_path = config_path.with_suffix(f"{config_path.suffix}.backup")
    backup_path.write_text(config_path.read_text())
    console.print(f"[green]✓ Backup created: {backup_path}[/green]")
    return backup_path


def extract_tokens(config: dict[str, Any]) -> dict[str, str]:
    """Extract API tokens from Gemini configuration."""
    tokens = {}

    mcp_servers = config.get("mcpServers", {})

    # Context7
    if "context7" in mcp_servers:
        headers = mcp_servers["context7"].get("headers", {})
        if api_key := headers.get("CONTEXT7_API_KEY"):
            if not api_key.startswith("${"):
                tokens["CONTEXT7_API_KEY"] = api_key

    # Hugging Face - check for various token patterns
    if "huggingface" in mcp_servers:
        headers = mcp_servers["huggingface"].get("headers", {})
        if auth := headers.get("Authorization"):
            # Handle "Bearer $HF_TOKEN", "Bearer ${HF_TOKEN}", or hardcoded tokens
            if auth.startswith("Bearer "):
                token_part = auth.replace("Bearer ", "")
                if not token_part.startswith("$"):
                    # It's a hardcoded token
                    tokens["HUGGINGFACE_TOKEN"] = token_part
                elif token_part in ["$HF_TOKEN", "${HF_TOKEN}"]:
                    # Already using env var, just needs standardization
                    console.print(
                        "[yellow]Note: Hugging Face already uses env var, will standardize to ${HUGGINGFACE_TOKEN}[/yellow]"
                    )

    return tokens


def migrate_to_env_vars(config: dict[str, Any]) -> dict[str, Any]:
    """Migrate Gemini configuration to use environment variable references."""
    mcp_servers = config.get("mcpServers", {})

    # Context7 - convert from "http" format to stdio format if needed
    if "context7" in mcp_servers:
        context7 = mcp_servers["context7"]
        if "httpUrl" in context7:
            # Convert to standard http format
            mcp_servers["context7"] = {
                "type": "http",
                "url": context7.get("httpUrl", "https://mcp.context7.com/mcp"),
                "headers": {"CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"},
            }
        else:
            # Already in standard format, just fix headers
            if "headers" not in context7:
                context7["headers"] = {}
            context7["headers"]["CONTEXT7_API_KEY"] = "${CONTEXT7_API_KEY}"

    # Hugging Face
    if "huggingface" in mcp_servers:
        hf_config = mcp_servers["huggingface"]
        if "httpUrl" in hf_config:
            # Convert to standard format
            mcp_servers["huggingface"] = {
                "type": "http",
                "url": hf_config.get("httpUrl", "https://huggingface.co/mcp"),
                "headers": {"Authorization": "Bearer ${HUGGINGFACE_TOKEN}"},
            }
        else:
            # Fix headers only
            if "headers" not in hf_config:
                hf_config["headers"] = {}
            hf_config["headers"]["Authorization"] = "Bearer ${HUGGINGFACE_TOKEN}"

    return config


def create_env_file(tokens: dict[str, str], env_path: Path) -> None:
    """Create or update .env file with extracted tokens."""
    existing_tokens = {}

    # Read existing .env if it exists
    if env_path.exists():
        console.print(f"[cyan]Reading existing {env_path}...[/cyan]")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing_tokens[key.strip()] = value.strip()

    # Merge with new tokens (new tokens take precedence)
    existing_tokens.update(tokens)

    # Write updated .env
    env_content = "# MCP Manager Environment Variables\n"
    env_content += "# Updated by Gemini migration script\n\n"

    for key, value in existing_tokens.items():
        env_content += f"{key}={value}\n"

    env_path.write_text(env_content)
    env_path.chmod(0o600)  # Secure file permissions
    console.print(f"[green]✓ Updated {env_path} with secure permissions (0600)[/green]")


def display_security_summary(tokens: dict[str, str], config_paths: list[Path]) -> None:
    """Display security issues found and actions to take."""
    console.print(
        Panel.fit(
            "[bold red]🚨 SECURITY ISSUES DETECTED IN GEMINI CLI[/bold red]\n\n"
            f"Found [bold]{len(tokens)}[/bold] hardcoded API keys in Gemini configuration.\n"
            f"Affected files: [cyan]{', '.join(str(p) for p in config_paths)}[/cyan]\n\n"
            "[yellow]Immediate Actions Required:[/yellow]\n"
            "1. ✅ Migrate config to use environment variables (this script)\n"
            "2. 🔄 Revoke exposed API keys and generate new ones\n"
            "3. 📝 Update .env file with new keys\n"
            "4. 🔒 Verify Gemini config files are secure\n"
            "5. 🧪 Test Gemini CLI: `gemini mcp list`",
            title="Gemini CLI Security Alert",
        )
    )


def main() -> int:
    """Main migration workflow."""
    console.print(
        "[bold cyan]Gemini CLI Security Migration[/bold cyan]\n", style="bold"
    )

    # Check for both Gemini config locations
    gemini_home_config = Path.home() / ".gemini" / "settings.json"
    gemini_system_config = Path.home() / ".config" / "gemini" / "settings.json"

    configs_to_migrate = []
    if gemini_home_config.exists():
        configs_to_migrate.append(gemini_home_config)
    if gemini_system_config.exists():
        configs_to_migrate.append(gemini_system_config)

    if not configs_to_migrate:
        console.print("[yellow]No Gemini CLI configuration files found.[/yellow]")
        console.print(
            "[dim]Checked: ~/.gemini/settings.json and ~/.config/gemini/settings.json[/dim]"
        )
        return 0

    console.print(f"[cyan]Found {len(configs_to_migrate)} Gemini config file(s):[/cyan]")
    for path in configs_to_migrate:
        console.print(f"  • {path}")

    all_tokens = {}

    try:
        # Extract tokens from all configs
        for config_path in configs_to_migrate:
            console.print(f"\n[cyan]Analyzing {config_path}...[/cyan]")
            with open(config_path) as f:
                config = json.load(f)

            tokens = extract_tokens(config)
            all_tokens.update(tokens)

        if not all_tokens:
            console.print(
                "\n[green]✓ All Gemini configurations already use environment variables![/green]"
            )
            console.print(
                "[yellow]Note: Checking if environment variable format is correct...[/yellow]"
            )

            # Still migrate to standardize format (e.g., $HF_TOKEN → ${HUGGINGFACE_TOKEN})
            if not Confirm.ask("\nStandardize environment variable format?"):
                return 0

        else:
            # Display security summary
            display_security_summary(all_tokens, configs_to_migrate)

            console.print(f"\n[bold]Found hardcoded tokens:[/bold]")
            for key in all_tokens.keys():
                console.print(f"  • {key}")

        console.print()
        if not Confirm.ask("[bold]Proceed with migration?[/bold]"):
            console.print("[yellow]Migration cancelled[/yellow]")
            return 1

        # Migrate all configs
        for config_path in configs_to_migrate:
            console.print(f"\n[cyan]Migrating {config_path}...[/cyan]")

            # Create backup
            backup_path = backup_config(config_path)

            # Load and migrate
            with open(config_path) as f:
                config = json.load(f)

            migrated_config = migrate_to_env_vars(config)

            # Save migrated configuration
            with open(config_path, "w") as f:
                json.dump(migrated_config, f, indent=2)

            console.print(f"[green]✓ Migrated {config_path}[/green]")

        # Create/update .env file
        if all_tokens:
            env_path = Path.cwd() / ".env"
            if Confirm.ask(f"\nUpdate {env_path} with extracted tokens?"):
                create_env_file(all_tokens, env_path)

        # Success message
        console.print(
            Panel.fit(
                "[bold green]✅ Gemini CLI Migration Complete![/bold green]\n\n"
                "[yellow]Next Steps:[/yellow]\n"
                "1. Source environment variables: [cyan]source .env[/cyan]\n"
                "2. Verify Gemini MCP servers work: [cyan]gemini mcp list[/cyan]\n"
                "3. [bold red]CRITICAL:[/bold red] Revoke old API keys:\n"
                "   • Context7: https://context7.com/settings\n"
                "   • Hugging Face: https://huggingface.co/settings/tokens\n"
                "4. Restart Gemini CLI for changes to take effect",
                title="Success",
            )
        )

        return 0

    except Exception as e:
        console.print(f"[red]❌ Migration failed: {e}[/red]")
        import traceback

        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
