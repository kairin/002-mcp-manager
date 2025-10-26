# Quickstart: Multi-Tool MCP Profile Management

**Date**: 2025-10-26
**Author**: Gemini

This guide provides a quick overview of how to use the `mcp-profile` command.

## 1. Prerequisites

- `mcp-manager` installed.
- `jq` installed (the script will attempt to auto-install it if missing).
- At least one supported AI tool installed (Claude Code or Gemini CLI).
- MCP profiles defined as JSON files in `~/.config/mcp-profiles/`.

## 2. Basic Usage

### Interactive Mode

Running the script without any arguments will launch an interactive TUI.

```bash
# Launch the interactive TUI
mcp-profile
```

From the TUI, you can:
- Switch profiles for all tools.
- View the current status.
- Manage profiles (create, edit, delete).

### Command-Line Mode

#### Switch Profiles for All Tools

To switch the profile for all installed AI tools simultaneously, provide the profile name as an argument.

```bash
# Switch all tools to the 'dev' profile
mcp-profile dev

# Switch all tools to the 'full' profile
mcp-profile full
```

#### Check Status

To see the currently active profile for each tool.

```bash
# Show the status for all tools
mcp-profile status
```

## 3. Advanced Usage

### Tool-Specific Switching

You can switch the profile for a single tool using the `--tool` flag or the `MCP_TOOL` environment variable.

```bash
# Switch only Claude Code to the 'ui' profile
mcp-profile ui --tool=claude

# Switch only Gemini CLI to the 'full' profile
mcp-profile full --tool=gemini

# Equivalent to the above using an environment variable
MCP_TOOL=gemini mcp-profile full
```

### List Available Profiles

To see a list of all the profiles available in your `~/.config/mcp-profiles/` directory.

```bash
# List all available profiles
mcp-profile list
```

### Backups

The script automatically creates timestamped, redacted backups of your configuration files before making any changes. You can find them in the respective tool's backup directory (e.g., `~/.config/claude-code/backups/`).

### Help

For a full list of commands and options.

```bash
# Show the help message
mcp-profile help
```
