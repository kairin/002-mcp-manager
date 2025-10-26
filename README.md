# MCP Profile Switcher and Local CI/CD Pipeline

This repository contains a suite of tools designed to streamline development workflows. It includes a powerful MCP (Model Context Protocol) Profile Switcher for managing AI tool configurations and a complete local CI/CD pipeline for running validation, testing, and builds in a local environment.

## Features

- **MCP Profile Switcher**: A script to switch between different MCP server configurations for Claude Code, Gemini CLI, and other supported tools.
- **Local CI/CD Pipeline**: A robust CI/CD pipeline that runs linting, testing, and build steps with detailed JSON logging.
- **Interactive TUI**: A user-friendly terminal interface for executing CI/CD tasks without needing to memorize commands.
- **Comprehensive Validation**: Scripts to validate your environment, dependencies, and to detect secrets.

## MCP Profile Switcher

### What It Does

AI tools like Claude Code and Gemini CLI support multiple MCP servers, but loading all of them can consume significant context tokens. The `mcp-profile` script lets you quickly switch between different profile configurations based on your current needs:

- **dev** (~7K tokens) - Minimal profile for basic coding
- **ui** (~12K tokens) - UI/Design work
- **full** (~85K tokens) - All servers for complex tasks

Server lists are dynamically read from profile files and may vary based on your setup.

### How It Works

The `mcp-profile` script manages MCP server configurations in:
- Claude Code's terminal CLI config (`~/.claude.json`) on a per-project basis.
- Gemini CLI's global config (`~/.config/gemini/settings.json`).

When you switch profiles, the script:

1. Creates a timestamped backup of your current configurations.
2. Updates the `mcpServers` section in the relevant configuration files for the specified tools.
3. Displays the new active configuration to confirm the switch.

**Important:** Changes for Claude Code are project-specific, while changes for Gemini CLI are global.

## Installation

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/kairin/002-mcp-manager.git ~/Apps/002-mcp-manager
    cd ~/Apps/002-mcp-manager
    ```

2.  **Add Scripts to Your PATH**

    Add the following lines to your `~/.zshrc` or `~/.bashrc` file to make the scripts accessible from anywhere in your terminal:

    ```bash
    export PATH="$HOME/Apps/002-mcp-manager/scripts/mcp:$PATH"
    export PATH="$HOME/Apps/002-mcp-manager/scripts/tui:$PATH"
    export PATH="$HOME/Apps/002-mcp-manager/scripts/local-ci:$PATH"
    ```

3.  **Reload Your Shell**

    ```bash
    source ~/.zshrc  # or source ~/.bashrc
    ```

4.  **Verify Installation**

    You can verify that the `mcp-profile` script is installed correctly by running:

    ```bash
    mcp-profile status
    ```

The script will automatically create profile files if they don't exist. Default profiles include:
- **dev**: github, markitdown
- **ui**: github, markitdown, playwright, shadcn, shadcn-ui
- **full**: all 6 servers (adds hf-mcp-server)

## MCP Profile Switcher Usage

### Interactive Mode (Default)

For an easy-to-use interface, run the `mcp-profile` command without any arguments:

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
<br>

## Local CI/CD Pipeline and TUI

This repository also includes a powerful local CI/CD pipeline that allows you to run linting, tests, and builds on your local machine. This is particularly useful for validating changes before pushing them to a remote repository.

### Interactive TUI

The easiest way to use the CI/CD pipeline is through the interactive TUI. To launch it, run:

```bash
run.sh
```

This will open a menu where you can:

-   Run the full CI/CD pipeline.
-   Run the pipeline with tests skipped for a faster execution.
-   Run in verbose mode for detailed output.
-   View recent logs.
-   Check your environment for required dependencies.
-   Clean up old log files.

### Direct CLI Usage

You can also run the CI/CD pipeline directly from the command line:

```bash
# Run the full pipeline
run.sh

# Run without tests
run.sh --skip-tests

# Run with verbose output
run.sh --verbose

# Run without auto-fixing lint errors
run.sh --no-fix

# Show the help message
run.sh --help
```
