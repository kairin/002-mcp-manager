# System-Wide MCP Configuration Guide

**Architecture**: Shared API keys, CLI-specific configurations

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│  Shared Environment Variables           │
│  ~/.profile or ~/.bashrc                │
│  - CONTEXT7_API_KEY                     │
│  - HUGGINGFACE_TOKEN                    │
│  - GITHUB_PERSONAL_ACCESS_TOKEN         │
└─────────────────────────────────────────┘
              ↓
    ┌─────────┴─────────┬─────────────────┐
    ↓                   ↓                 ↓
┌─────────┐      ┌──────────┐    ┌─────────────┐
│ Claude  │      │ Gemini   │    │ Copilot     │
│ Code    │      │ CLI      │    │ CLI         │
└─────────┘      └──────────┘    └─────────────┘
    ↓                   ↓                 ↓
~/.claude.json   ~/.config/gemini/  ~/.copilot/
                 settings.json       mcp-config.json
```

---

## Step 1: Shared Environment Variables

### Location: `~/.profile` (system-wide, loaded for all shells)

```bash
# Add to ~/.profile (recommended) or ~/.bashrc
cat >> ~/.profile << 'EOF'

# ============================================
# MCP Manager - Shared API Keys
# Used by: Claude Code, Gemini CLI, Copilot CLI
# ============================================

export CONTEXT7_API_KEY="your-context7-key-here"
export HUGGINGFACE_TOKEN="your-huggingface-token-here"
export GITHUB_PERSONAL_ACCESS_TOKEN="your-github-token-here"

# Alternative names for compatibility
export HF_TOKEN="$HUGGINGFACE_TOKEN"
export GH_TOKEN="$GITHUB_PERSONAL_ACCESS_TOKEN"

EOF

# Reload
source ~/.profile
```

### Verify:
```bash
echo "CONTEXT7_API_KEY: ${CONTEXT7_API_KEY:0:10}..."
echo "HUGGINGFACE_TOKEN: ${HUGGINGFACE_TOKEN:0:10}..."
echo "GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_PERSONAL_ACCESS_TOKEN:0:10}..."
```

---

## Step 2: Claude Code Configuration

### Location: `~/.claude.json` (system-wide, all projects)

**Pattern**: Use `env` section to reference system environment variables

```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    },
    "hf-mcp-server": {
      "type": "http",
      "url": "https://huggingface.co/mcp",
      "headers": {
        "Authorization": "Bearer ${HUGGINGFACE_TOKEN}"
      }
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    },
    "shadcn": {
      "type": "stdio",
      "command": "npx",
      "args": ["shadcn@latest", "mcp"],
      "env": {}
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {}
    },
    "markitdown": {
      "type": "stdio",
      "command": "uv",
      "args": ["tool", "run", "markitdown-mcp"],
      "env": {}
    }
  }
}
```

**Note**: Claude Code reads environment variables from the shell that launched it.

### Verify:
```bash
claude mcp list
# All servers should show ✓ Connected
```

---

## Step 3: Gemini CLI Configuration

### Location: `~/.config/gemini/settings.json` (system-wide)

**Pattern**: Use `$VAR` syntax (not `${VAR}`) in headers

```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "$CONTEXT7_API_KEY"
      }
    },
    "hf-mcp-server": {
      "type": "http",
      "url": "https://huggingface.co/mcp",
      "headers": {
        "Authorization": "Bearer $HUGGINGFACE_TOKEN"
      }
    },
    "github": {
      "type": "stdio",
      "command": "bash",
      "args": ["-c", "GITHUB_PERSONAL_ACCESS_TOKEN=$(gh auth token) /home/kkk/bin/github-mcp-server stdio"],
      "env": {}
    },
    "shadcn": {
      "type": "stdio",
      "command": "npx",
      "args": ["shadcn@3.4.0", "mcp"],
      "env": {}
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {}
    },
    "markitdown": {
      "type": "stdio",
      "command": "uvx",
      "args": ["markitdown-mcp"]
    }
  }
}
```

### Enable System-Wide Config:
```bash
# Add to ~/.bashrc or ~/.zshrc
export GEMINI_CLI_SYSTEM_SETTINGS_PATH="$HOME/.config/gemini/settings.json"
```

### Verify:
```bash
source ~/.bashrc
gemini mcp list
# All servers should show ✓ Connected
```

---

## Step 4: GitHub Copilot CLI Configuration

### Location: `~/.copilot/mcp-config.json` (system-wide)

**Pattern**: Standard MCP server configuration with env vars

### Using Interactive Mode:
```bash
copilot
> /mcp add context7
# Follow prompts to add HTTP server with Authorization header
```

### Or Manually Edit:
```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    },
    "github": {
      "type": "stdio",
      "command": "gh-mcp-server",
      "args": ["stdio"]
    }
  }
}
```

### Verify:
```bash
copilot
> /mcp show
# Should list all configured MCP servers
```

---

## 🔐 Security Best Practices

### 1. File Permissions
```bash
chmod 600 ~/.profile       # Protect environment variables
chmod 600 ~/.claude.json   # Protect Claude config
chmod 600 ~/.config/gemini/settings.json  # Protect Gemini config
chmod 600 ~/.copilot/mcp-config.json      # Protect Copilot config
```

### 2. Git Ignore (Per Project)
```bash
# Add to .gitignore in each project
echo ".claude.json" >> .gitignore
echo ".gemini/" >> .gitignore
echo ".env*" >> .gitignore
```

### 3. Never Commit
- ❌ `~/.profile` with actual keys
- ❌ `~/.claude.json` with hardcoded tokens
- ❌ Any file containing actual API keys

### 4. Use Templates
- ✅ Commit `.env.example` with placeholders
- ✅ Document required environment variables
- ✅ Use `${VAR}` or `$VAR` references in configs

---

## 📋 Verification Checklist

### Environment Variables Set:
```bash
✓ CONTEXT7_API_KEY exported in ~/.profile
✓ HUGGINGFACE_TOKEN exported in ~/.profile
✓ GITHUB_PERSONAL_ACCESS_TOKEN exported in ~/.profile
```

### CLI Configurations:
```bash
✓ ~/.claude.json uses ${VAR} syntax
✓ ~/.config/gemini/settings.json uses $VAR syntax
✓ ~/.copilot/mcp-config.json configured
✓ GEMINI_CLI_SYSTEM_SETTINGS_PATH exported
```

### System-Wide Access:
```bash
# Test from any directory
cd /tmp
claude mcp list    # ✓ All servers connected
gemini mcp list    # ✓ All servers connected
copilot            # ✓ Can access /mcp commands
```

---

## 🔧 Troubleshooting

### Claude Code: "Missing environment variables"
```bash
# Check if environment variables are accessible
env | grep -E "CONTEXT7|HUGGINGFACE|GITHUB_PERSONAL"

# Ensure they're in ~/.profile, not just ~/.bashrc
# Claude Code may not source ~/.bashrc
```

### Gemini CLI: HTTP servers disconnected
```bash
# Gemini uses $VAR not ${VAR}
# Check config:
cat ~/.config/gemini/settings.json | jq '.mcpServers.context7.headers'
# Should show: {"CONTEXT7_API_KEY": "$CONTEXT7_API_KEY"}
```

### Copilot CLI: MCP servers not found
```bash
# Check config location
ls -la ~/.copilot/mcp-config.json
# Or alternative location
ls -la ~/.config/mcp-config.json
```

---

## 🎯 Summary

| CLI | Config Location | Env Var Syntax | Scope |
|-----|-----------------|----------------|-------|
| **Claude Code** | `~/.claude.json` | `${VAR}` | System-wide |
| **Gemini CLI** | `~/.config/gemini/settings.json` | `$VAR` | System-wide |
| **Copilot CLI** | `~/.copilot/mcp-config.json` | `${VAR}` | System-wide |

**Shared API Keys**: `~/.profile`
- Single source of truth
- Exported to all shells
- Referenced by all CLIs

---

**Last Updated**: 2025-10-17
**Compatibility**: Claude Code 2.x, Gemini CLI 1.x, GitHub Copilot CLI
