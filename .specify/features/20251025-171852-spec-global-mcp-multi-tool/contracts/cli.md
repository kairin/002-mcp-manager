# CLI Contract: mcp-profile

**Generated**: 2025-10-25

This document defines the command-line interface for the `mcp-profile` script.

## Base Command

`mcp-profile [subcommand] [options]`

## Subcommands

| Subcommand | Description | Options | Example |
|---|---|---|---|
| `<profile_name>` | Switches the MCP servers for all supported tools to the specified profile (e.g., `dev`, `ui`, `full`). | `--tool=<tool_name>` | `mcp-profile dev --tool=claude` |
| `status` | Displays the currently active profile for each tool and lists the configured MCP servers. | `--tool=<tool_name>` | `mcp-profile status` |
| `list` | Lists all available profiles from `~/.config/mcp-profiles/`. | | `mcp-profile list` |
| `test` | Runs health checks on the currently configured MCP servers and authentications. | | `mcp-profile test` |
| `backup` | Lists the most recent backups for each supported tool. | `--tool=<tool_name>` | `mcp-profile backup` |
| `help` | Displays the help message. | | `mcp-profile help` |

## Options

- **`--tool=<tool_name>`**: Restricts the operation to a specific tool. If omitted, the command applies to all supported tools.
  - **Supported values**: `claude`, `gemini`, `copilot`, `all`.

## Exit Codes

- **0**: Success.
- **1**: General error (e.g., invalid profile name, script failure).
- **2**: Prerequisite missing (e.g., `jq` not installed).
