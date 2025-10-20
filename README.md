# MCP Profile Switcher

A simple shell script to switch between different MCP (Model Context Protocol) server configurations for Claude Code terminal CLI.

## What It Does

Claude Code supports multiple MCP servers, but loading all of them consumes significant context tokens (~85K). This script lets you quickly switch between different profile configurations based on your current needs:

- **dev** (~7K tokens) - Minimal profile for basic coding
- **ui** (~12K tokens) - UI/Design work
- **full** (~85K tokens) - All servers for complex tasks

Server lists are dynamically read from profile files and may vary based on your setup.

## How It Works

The script manages MCP server configurations in Claude Code's terminal CLI config (`~/.claude.json`). When you switch profiles:

1. Creates a timestamped backup of your entire Claude config
2. Updates the `mcpServers` section for the current project
3. Shows the new active configuration

**Important:** Changes are project-specific. The script automatically detects your current project directory.

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

### Command Line Mode

You can also use direct commands:

```bash
# Switch to minimal profile (~7K tokens)
mcp-profile dev

# Switch to UI profile (~12K tokens)
mcp-profile ui

# Switch to full profile (~85K tokens)
mcp-profile full

# Check current profile
mcp-profile status

# List all available profiles with server details
mcp-profile list

# Test API keys for active MCP servers
mcp-profile test

# Show recent backups
mcp-profile backup

# Show help
mcp-profile help
```

## Important Notes

- **Must restart Claude Code** after switching profiles for changes to take effect
- Automatic backups are created in `~/.config/claude-code/backups/` before each switch
- Changes apply only to the current project directory
- Profile files are stored in `~/.config/claude-code/profiles/`

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
~/.config/claude-code/
├── profiles/                           # Profile definitions
│   ├── dev.json                        # Minimal profile
│   ├── ui.json                         # UI profile
│   └── full.json                       # Full profile
└── backups/                            # Automatic backups
    └── claude-backup-YYYYMMDD_HHMMSS.json
```

## Customizing Profiles

You can edit profile files directly:

```bash
# Edit dev profile
vim ~/.config/claude-code/profiles/dev.json

# Edit ui profile
vim ~/.config/claude-code/profiles/ui.json

# Edit full profile
vim ~/.config/claude-code/profiles/full.json
```

Each profile is a JSON object containing MCP server configurations. Example:

```json
{
  "github": {
    "type": "stdio",
    "command": "/home/user/.local/bin/github-mcp-wrapper.sh",
    "args": [],
    "env": {}
  },
  "markitdown": {
    "type": "stdio",
    "command": "uvx",
    "args": ["markitdown-mcp"],
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

### Environment Variables for Sensitive Data

Some MCP servers (like `context7`) require API keys. These should NEVER be hardcoded in configuration files. Instead, use environment variables:

**Example: Context7 API Key**

1. Add to your shell profile (`~/.zshrc` or `~/.bashrc`):
   ```bash
   export CONTEXT7_API_KEY='your-api-key-here'
   ```

2. Use environment variable syntax in profile files:
   ```json
   {
     "context7": {
       "type": "http",
       "url": "https://mcp.context7.com/mcp",
       "headers": {
         "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
       }
     }
   }
   ```

3. Reload your shell:
   ```bash
   source ~/.zshrc  # or source ~/.bashrc
   ```

**Why This Matters:**
- ✅ Profile files can be safely committed to git
- ✅ API keys remain private and secure
- ✅ Claude Code automatically expands `${VAR_NAME}` at runtime
- ✅ Easy to rotate keys without touching config files

**Other Examples:**
- `shadcn-ui` already uses this pattern: `$(gh auth token)`
- Any MCP server with authentication should follow this approach

See `docs/context7-mcp-setup.md` for detailed Context7 setup instructions.

### Testing API Keys

To verify that your API keys are properly configured and working, use the `test` command:

```bash
mcp-profile test
```

This command will:
- Automatically detect which MCP servers in your active profile require API keys
- Test each credential with the actual service (GitHub, HuggingFace, Context7)
- Show real API responses and authentication status
- Display rate limits and account information where available

**Example Output:**
```
=== MCP API Key Testing ===

Project: /home/user/Apps/my-project
Active servers (7): github, markitdown, playwright, shadcn, shadcn-ui, hf-mcp-server, context7

Testing API keys for servers that require authentication...

Testing GitHub API...
✓ GitHub authentication successful
  ✓ Logged in to github.com account myuser
  - Token scopes: 'repo', 'workflow', 'write:packages'
  Rate limit: Limit: 5000/hour | Used: 10 | Remaining: 4990

Testing HuggingFace MCP Server (OAuth)...
✓ HuggingFace MCP OAuth session active
  Status: Connected via Claude Code
  OAuth authentication verified through MCP

Testing HuggingFace CLI Token...
✓ HuggingFace CLI token valid
  Username: myuser
  Organizations: 2 (org1, org2)
  Token source: Environment variable (HF_TOKEN)

Token can be used for:
  ✓ hf CLI commands (model/dataset download, upload)
  ✓ Python transformers/datasets libraries
  ✓ Direct API access in scripts

Testing Context7 API...
✓ Context7 API key valid
  HTTP Status: 200 OK
  Connection: Successful

Test Summary:
  Profile servers tested: 4
  Servers not requiring API keys are working automatically
```

**When to use:**
- After setting up new API keys in your `.profile` or `.bashrc`
- To verify credentials before starting work
- To troubleshoot MCP server connection issues
- To check rate limits on GitHub API
- To verify HuggingFace authentication for both MCP OAuth and CLI token

**Note:** The test command shows real API responses, not hardcoded messages. Servers like `markitdown`, `playwright`, and `shadcn` don't require external API keys and work automatically.

### Setting up HuggingFace Authentication

The `hf-mcp-server` uses OAuth authentication through Claude Code, but you may also want to set up CLI token authentication for direct HuggingFace CLI usage:

**Option 1: Login via CLI (Recommended)**
```bash
# Install the HuggingFace CLI
pip install -U huggingface_hub[cli]

# Login interactively
hf auth login

# Token will be stored in ~/.cache/huggingface/token
```

**Option 2: Environment Variable**

Add to your `~/.zshrc` or `~/.bashrc`:
```bash
export HF_TOKEN='hf_your_token_here'
```

Then reload your shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

**Get your token:**
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with at least read permissions
3. Use it in either method above

**Test your setup:**
```bash
# Test with the modern CLI command
hf auth whoami

# Or use the mcp-profile test command
mcp-profile test
```

## Requirements

- **Claude Code** - Terminal CLI must be installed
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
1. Make sure to restart Claude Code after switching profiles
2. Verify you're in the correct project directory
3. Check that profile files exist:
   ```bash
   ls -la ~/.config/claude-code/profiles/
   ```

### Script not found
1. Verify the script is in your PATH: `echo $PATH`
2. Make sure the script is executable:
   ```bash
   chmod +x ~/Apps/002-mcp-manager/scripts/mcp/mcp-profile
   ```

### View current configuration
```bash
# See current project's MCP servers
cat ~/.claude.json | jq '.projects["/path/to/project"].mcpServers'

# Or use the script
mcp-profile status
```

### Restore from backup
Backups are stored in `~/.config/claude-code/backups/`:
```bash
# List backups
mcp-profile backup

# Restore manually
cp ~/.config/claude-code/backups/claude-backup-YYYYMMDD_HHMMSS.json ~/.claude.json
```

## Migration from Old Version

If you were using the old version with `~/.config/claude-code/mcp-servers*.json`, those files are no longer needed. The new version uses:
- `~/.claude.json` for active configuration
- `~/.config/claude-code/profiles/` for profile storage

The script automatically creates profile files on first use.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Mister K ([@kairin](https://github.com/kairin))

## Project Links

- **Repository**: https://github.com/kairin/002-mcp-manager
- **Issues**: https://github.com/kairin/002-mcp-manager/issues
