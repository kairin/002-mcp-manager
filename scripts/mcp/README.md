# MCP Profile Management Scripts

Scripts for managing MCP (Model Context Protocol) server configurations for Claude Code.

## Scripts

### mcp-profile

Switches between different MCP server profiles to optimize context token usage.

**Location:** `/home/kkk/Apps/002-mcp-manager/scripts/mcp/mcp-profile`

**Usage:**
```bash
mcp-profile [command]
```

**Commands:**
- `dev` - Switch to minimal development profile (~7K tokens)
  - Servers: github, markitdown (dynamically read from profile)
- `ui` - Switch to UI work profile (~12K tokens)
  - Servers: github, markitdown, playwright, shadcn, shadcn-ui (dynamically read from profile)
- `full` - Switch to full profile (~85K tokens)
  - Servers: All 7 servers including hf-mcp-server and context7 (dynamically read from profile)
- `status` - Show current active profile (default)
- `list` - List all available profiles with their server configurations
- `test` - Test API keys for active MCP servers (GitHub, HuggingFace, Context7)
- `backup` - Show recent backups
- `help` - Show help message

**Note:** Server lists are dynamically read from profile files and may vary based on your setup.

**Examples:**
```bash
# Switch to minimal profile for development
mcp-profile dev

# Check current profile
mcp-profile status

# List available profiles with server details
mcp-profile list

# Test API keys for active servers
mcp-profile test

# View recent backups
mcp-profile backup
```

**Important Notes:**
- You **must restart Claude Code** after switching profiles for changes to take effect
- Claude Code reads the config at startup from `~/.claude.json`
- Changes are project-specific (detected via git root or current directory)
- Each profile switch automatically creates a timestamped backup
- Backups are stored in `~/.config/claude-code/backups/`

## Installation

The script is automatically available via PATH. Two methods are configured:

1. **Direct PATH** (recommended):
   - Added to `~/.zshrc`: `export PATH="$HOME/Apps/002-mcp-manager/scripts/mcp:$PATH"`
   - Reload shell: `source ~/.zshrc` or restart terminal

2. **Symlink** (backwards compatibility):
   - Symlink exists at: `~/bin/mcp-profile`
   - Links to the main script

## Configuration Files

MCP configurations are managed in the following locations:

```
~/.claude.json                          # Claude Code main config (active)
~/.config/claude-code/
├── profiles/                           # Profile definitions
│   ├── dev.json                        # Minimal profile
│   ├── ui.json                         # UI profile
│   └── full.json                       # Full profile
└── backups/                            # Automatic backups
    └── claude-backup-YYYYMMDD_HHMMSS.json
```

The `~/.claude.json` file contains project-specific MCP server configurations. The script updates the `mcpServers` section for the current project when switching profiles.

## Workflow

Typical workflow for switching profiles:

```bash
# Before starting work
mcp-profile dev              # Switch to minimal profile

# Start Claude Code
claude-code                  # Loads dev profile

# ... do your work ...

# Exit Claude Code
exit

# Switch back to full profile
mcp-profile full

# Start Claude Code again
claude-code                  # Now loads full profile
```

## Token Usage Guide

Choose your profile based on your task:

- **DEV (7K tokens)**: Basic coding, file editing, git operations
- **UI (12K tokens)**: Frontend work, component development, shadcn usage
- **FULL (85K tokens)**: Complex tasks requiring all tools, browser automation, etc.

## Troubleshooting

**Script not found after installation:**
```bash
# Reload your shell configuration
source ~/.zshrc

# Or check if the PATH was added
echo $PATH | grep "002-mcp-manager"
```

**Changes not taking effect:**
- Make sure you **fully exit** Claude Code (not just switch to another window)
- Verify the profile switched: `mcp-profile status`
- Check the active config: `cat ~/.claude.json | jq '.projects'`

**Need to restore a backup:**
```bash
# View backups
mcp-profile backup

# Manually restore (replace TIMESTAMP)
cp ~/.config/claude-code/backups/claude-backup-YYYYMMDD_HHMMSS.json \
   ~/.claude.json
```

**Testing API Keys:**
```bash
# Test all active server authentication
mcp-profile test

# This will test:
# - GitHub API authentication (via gh CLI)
# - HuggingFace MCP OAuth (via Claude Code MCP connection)
# - HuggingFace CLI token (via hf auth whoami)
# - Context7 API key (via direct API call)
```
