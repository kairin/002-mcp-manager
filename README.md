# MCP Profile Switcher

A simple shell script to switch between different MCP (Model Context Protocol) server configurations for Claude Code.

## What It Does

Claude Code supports multiple MCP servers, but loading all of them consumes significant context tokens (~85K). This script lets you quickly switch between different profile configurations based on your current needs:

- **dev** (7K tokens) - Minimal profile for basic coding (github, markitdown)
- **ui** (12K tokens) - UI/Design work (github, shadcn-ui, shadcn, markitdown)
- **full** (85K tokens) - All servers for complex tasks (github, shadcn-ui, context7, shadcn, playwright, markitdown, hf-mcp-server)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/kairin/mcp-manager.git ~/Apps/002-mcp-manager
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

## Usage

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

# Create manual backup
mcp-profile backup

# Show help
mcp-profile help
```

## Important Notes

- **Must restart Claude Code** after switching profiles for changes to take effect
- Automatic backups are created in `~/.config/claude-code/backups/` before each switch
- Original configuration files are in `~/.config/claude-code/profiles/`

## Profile Details

### dev (Minimal - 7K tokens)
Best for: Basic coding, git operations, document processing
```
- github (Git operations, PR management)
- markitdown (Document conversion)
```

### ui (UI/Design - 12K tokens)
Best for: Frontend development, component work
```
- github (Git operations)
- shadcn-ui (Component registry)
- shadcn (UI tooling)
- markitdown (Document conversion)
```

### full (All Servers - 85K tokens)
Best for: Complex tasks requiring all capabilities
```
- github (Git operations)
- shadcn-ui (Component registry)
- context7 (Library documentation)
- shadcn (UI tooling)
- playwright (Browser automation)
- markitdown (Document conversion)
- hf-mcp-server (Hugging Face models)
```

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
├── mcp_servers.json          # Active configuration
├── profiles/
│   ├── mcp-servers-dev.json  # Minimal profile
│   ├── mcp-servers-ui.json   # UI profile
│   └── mcp-servers-full.json # Full profile
└── backups/
    └── mcp-servers-backup-YYYYMMDD_HHMMSS.json
```

## Requirements

- Claude Code CLI installed
- Bash or Zsh shell
- MCP servers configured in `~/.config/claude-code/profiles/`

## Troubleshooting

### Profile not switching
- Make sure to restart Claude Code after switching profiles
- Check that profile files exist in `~/.config/claude-code/profiles/`

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
