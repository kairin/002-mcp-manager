# MCP Profile Switcher

A simple shell script to switch between different MCP (Model Context Protocol) server configurations for Claude Code.

## What It Does

Claude Code supports multiple MCP servers, but loading all of them consumes significant context tokens (~85K). This script lets you quickly switch between different profile configurations based on your current needs:

- **dev** (7K tokens) - Minimal profile for basic coding
- **ui** (12K tokens) - UI/Design work
- **full** (85K tokens) - All servers for complex tasks

Server lists are dynamically read from configuration files and may vary based on your setup.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/kairin/002-mcp-manager.git ~/Apps/002-mcp-manager
```

### 2. Add to your PATH
Add this to your `~/.zshrc` or `~/.bashrc`:
```bash
export PATH="$HOME/Apps/002-mcp-manager/scripts/mcp:$PATH"
```

### 3. Reload your shell
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### 4. Create profile configurations (if needed)

If you don't already have MCP profile configs, you need to create them in `~/.config/claude-code/`:

- `mcp-servers-dev.json` - Minimal servers (github, markitdown)
- `mcp-servers-ui.json` - UI work servers (github, shadcn, markitdown)
- `mcp-servers-full.json` - All servers

**Note:** The script requires these three profile files to exist. You can customize the servers in each profile based on your needs.

## Usage

### Interactive Mode (Default)

Simply run the command without arguments to launch an interactive menu:

```bash
mcp-profile
```

This displays a numbered menu where you can:
1. Switch to DEV profile (Minimal, ~7K tokens)
2. Switch to UI profile (Design work, ~12K tokens)
3. Switch to FULL profile (All servers, ~85K tokens)
4. Show detailed status
5. Show recent backups
6. Quit

### Command Line Mode

You can also use direct commands:

```bash
# Switch to minimal profile (7K tokens)
mcp-profile dev

# Switch to UI profile (12K tokens)
mcp-profile ui

# Switch to full profile (85K tokens)
mcp-profile full

# Check current profile
mcp-profile status

# List all available profiles
mcp-profile list

# Show recent backups
mcp-profile backup

# Show help
mcp-profile help
```

## Important Notes

- **Must restart Claude Code** after switching profiles for changes to take effect
- Automatic backups are created in `~/.config/claude-code/backups/` before each switch
- Profile configuration files are stored in `~/.config/claude-code/`

## Profile Details

The server lists shown below are examples. Use `mcp-profile status` to see the actual servers in each profile.

### dev (Minimal - 7K tokens)
**Best for:** Basic coding, git operations, document processing

**Typical servers:** github, markitdown

### ui (UI/Design - 12K tokens)
**Best for:** Frontend development, component work

**Typical servers:** github, shadcn, markitdown

### full (All Servers - 85K tokens)
**Best for:** Complex tasks requiring all capabilities

**Typical servers:** context7, github, hf-mcp-server, markitdown, playwright, shadcn, shadcn-ui

## How It Works

The script manages three configuration files in `~/.config/claude-code/`:
- `mcp-servers-dev.json` - Minimal configuration
- `mcp-servers-ui.json` - UI-focused configuration
- `mcp-servers-full.json` - Complete configuration

When you switch profiles, the script:
1. Creates a timestamped backup of your current configuration
2. Copies the selected profile to `mcp_servers.json`
3. Shows the new active configuration

## Configuration Location

MCP server configurations are stored in:
```
~/.config/claude-code/
├── mcp-servers.json          # Active configuration
├── mcp-servers-dev.json      # Minimal profile
├── mcp-servers-ui.json       # UI profile
├── mcp-servers-full.json     # Full profile
└── backups/
    └── mcp-servers-backup-YYYYMMDD_HHMMSS.json
```

## Requirements

- **Claude Code** - The CLI must be installed
- **Bash or Zsh** - Shell environment
- **jq** - JSON processor for reading server lists
  - Ubuntu/Debian: `sudo apt install jq`
  - macOS: `brew install jq`
- **MCP profile configs** - Must exist in `~/.config/claude-code/`
  - `mcp-servers-dev.json`
  - `mcp-servers-ui.json`
  - `mcp-servers-full.json`

## Troubleshooting

### Profile not switching
- Make sure to restart Claude Code after switching profiles
- Check that profile files exist in `~/.config/claude-code/`
  - `mcp-servers-dev.json`
  - `mcp-servers-ui.json`
  - `mcp-servers-full.json`

### Script not found
- Verify the script is in your PATH: `echo $PATH`
- Make sure the script is executable: `chmod +x scripts/mcp/mcp-profile`

### Backups
- Backups are automatically created before each switch
- Located in `~/.config/claude-code/backups/`
- Named with timestamp: `mcp-servers-backup-YYYYMMDD_HHMMSS.json`

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Mister K ([@kairin](https://github.com/kairin))
