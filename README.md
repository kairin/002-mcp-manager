# MCP Profile Switcher

A simple shell script to switch between different MCP (Model Context Protocol) server configurations for Claude Code, Gemini CLI, and other supported tools.

## What It Does

AI tools like Claude Code and Gemini CLI support multiple MCP servers, but loading all of them can consume significant context tokens. This script lets you quickly switch between different profile configurations based on your current needs:

- **dev** (~7K tokens) - Minimal profile for basic coding
- **ui** (~12K tokens) - UI/Design work
- **full** (~85K tokens) - All servers for complex tasks

Server lists are dynamically read from profile files and may vary based on your setup.

## How It Works

The script manages MCP server configurations in:
- Claude Code's terminal CLI config (`~/.claude.json`) on a per-project basis.
- Gemini CLI's global config (`~/.config/gemini/settings.json`).

When you switch profiles:

1. Creates a timestamped backup of your configs.
2. Updates the `mcpServers` section for the specified tools.
3. Shows the new active configuration.

**Important:** Changes for Claude Code are project-specific, while changes for Gemini CLI are global.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/kairin/002-mcp-manager.git ~/Apps/002-mcp-manager
cd ~/Apps/002-mcp-manager
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

### 4. Verify installation
```bash
mcp-profile status
```

The script will automatically create profile files if they don't exist. Default profiles include:
- **dev**: github, markitdown
- **ui**: github, markitdown, playwright, shadcn, shadcn-ui
- **full**: all 6 servers (adds hf-mcp-server)

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
5. Test API keys
6. Show recent backups
7. Quit

**UI Features:**
- **Unified Table Display**: All tables use consistent 85-character width for perfect alignment
- **Color-Coded Status**: Visual indicators for server health (✓ Ready, ⚠ Warning, ✗ Error, ● Active)
- **ANSI-Aware Formatting**: Smart text centering that properly handles color codes
- **Visual Profile Selection**: Clean tabular display showing profile details, server count, token usage, and health status

### Command Line Mode

You can also use direct commands:

```bash
# Switch both Claude and Gemini to the minimal profile
mcp-profile dev

# Switch only Claude to the UI profile
mcp-profile ui --tool=claude

# Switch only Gemini to the full profile
mcp-profile full --tool=gemini

# Check current profile status for all tools
mcp-profile status

# List all available profiles with server details
mcp-profile list

# Test API keys for active MCP servers
mcp-profile test

# Verify that tool configs match the active profile
mcp-profile verify

# Show recent backups
mcp-profile backup

# Show help
mcp-profile help
```

## Important Notes

- **Must restart tools** (Claude Code, Gemini CLI) after switching profiles for changes to take effect.
- Automatic backups are created in `~/.config/claude-code/backups/` and `~/.config/gemini/backups/` before each switch.
- Profile files are stored in `~/.config/mcp-profiles/`.

## Profile Details

### dev (Minimal - ~7K tokens)
**Best for:** Basic coding, git operations, document processing

**Servers:**
- `github` - GitHub API integration
- `markitdown` - Document to markdown conversion

### ui (UI/Design - ~12K tokens)
**Best for:** Frontend development, component work, browser testing

**Servers:**
- `github` - GitHub API integration
- `markitdown` - Document conversion
- `playwright` - Browser automation
- `shadcn` - shadcn/ui CLI
- `shadcn-ui` - shadcn/ui components server

### full (All Servers - ~85K tokens)
**Best for:** Complex tasks requiring all capabilities

**Servers:** All 6 servers (dev + ui + hf-mcp-server)
- `github` - GitHub API
- `markitdown` - Document conversion
- `playwright` - Browser automation
- `shadcn` - shadcn/ui CLI
- `shadcn-ui` - shadcn/ui components
- `hf-mcp-server` - HuggingFace Hub integration

Use `mcp-profile status` to see the actual servers in each profile for your installation.

## Configuration Structure

```
~/.claude.json                          # Claude Code terminal CLI config
~/.config/gemini/settings.json          # Gemini CLI global config
~/.config/mcp-profiles/
├── dev.json                        # Minimal profile
├── ui.json                         # UI profile
└── full.json                       # Full profile
~/.config/claude-code/backups/          # Claude backups
~/.config/gemini/backups/               # Gemini backups
```

## Customizing Profiles

You can edit profile files directly:

```bash
# Edit dev profile
vim ~/.config/mcp-profiles/dev.json
```

Each profile is a JSON object containing MCP server configurations. Example:

```json
{
  "github": {
    "type": "stdio",
    "command": "/home/user/.local/bin/github-mcp-wrapper.sh",
    "args": [],
    "env": {}
  }
}
```

After editing, switch to the profile to apply changes:
```bash
mcp-profile dev
```

## Security: API Keys and Secrets

**CRITICAL:** Never commit API keys or secrets to your repository!

Use environment variables for sensitive data. See the `mcp-profile help` command for more details.

### Testing API Keys

To verify that your API keys are properly configured and working, use the `test` command:

```bash
mcp-profile test
```

This command will test credentials for services like GitHub, HuggingFace, and Context7.

## Requirements

- **Claude Code** or **Gemini CLI**
- **Bash or Zsh** - Shell environment
- **jq** - JSON processor (REQUIRED)
  - Ubuntu/Debian: `sudo apt install jq`
  - macOS: `brew install jq`

## Troubleshooting

### "jq not found" error
```bash
# Ubuntu/Debian
sudo apt install jq

# macOS
brew install jq
```

### Profile not switching
1. Make sure to restart your AI tools after switching profiles.
2. Verify you're in the correct project directory for Claude Code changes.
3. Check that profile files exist:
   ```bash
   ls -la ~/.config/mcp-profiles/
   ```

### Script not found
1. Verify the script is in your PATH: `echo $PATH`
2. Make sure the script is executable:
   ```bash
   chmod +x ~/Apps/002-mcp-manager/scripts/mcp/mcp-profile
   ```

### View current configuration
```bash
# See current project's MCP servers for Claude
cat ~/.claude.json | jq '.projects["/path/to/project"].mcpServers'

# See global MCP servers for Gemini
cat ~/.config/gemini/settings.json | jq '.mcpServers'

# Or use the script
mcp-profile status
```

### Restore from backup
Backups are stored in `~/.config/claude-code/backups/` and `~/.config/gemini/backups/`:
```bash
# List backups
mcp-profile backup

# Restore manually
cp <backup_file> <config_file>
```

## Local CI/CD for Astro Site

This project includes a complete local CI/CD pipeline for the Astro.build website, allowing you to run all checks locally before pushing to GitHub (reducing GitHub Actions costs).

See `mcp-profile help` for more details on the local CI/CD pipeline.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Mister K ([@kairin](https://github.com/kairin))

## Project Links

- **Repository**: https://github.com/kairin/002-mcp-manager
- **Issues**: https://github.com/kairin/002-mcp-manager/issues
