# Configuration Guide

> **Complete MCP Server Setup Instructions**

## Overview

MCP Manager uses a global configuration approach to ensure all MCP servers are consistently available across all Claude Code sessions. This guide covers installation, configuration, and testing.

## Configuration Location

Global MCP configuration is stored in:
```
~/.claude.json
```

This file is managed by Claude Code and should contain all MCP server definitions.

## Supported Server Types

### HTTP Servers
HTTP servers connect via REST API endpoints:
- **context7**: Documentation and code examples
- **hf-mcp-server**: Hugging Face model access

### stdio Servers
stdio servers run as local processes:
- **github**: GitHub API integration
- **shadcn**: UI component registry
- **playwright**: Browser automation
- **markitdown**: Document conversion

## Server-Specific Configuration

### Context7 (HTTP)

**Requirements**:
- Context7 API key from https://context7.com
- Environment variable: `CONTEXT7_API_KEY`

**Configuration**:
```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    }
  }
}
```

**Setup**:
```bash
# Add to ~/.bashrc or ~/.zshrc
export CONTEXT7_API_KEY="your-api-key-here"
```

### Hugging Face MCP (HTTP)

**Requirements**:
- Hugging Face account and token from https://huggingface.co/settings/tokens
- Environment variable: `HUGGINGFACE_TOKEN`
- gh CLI installed: `sudo apt-get install gh` or `brew install gh`

**Configuration**:
```json
{
  "mcpServers": {
    "hf-mcp-server": {
      "type": "http",
      "url": "https://huggingface.co/mcp",
      "headers": {
        "Authorization": "Bearer ${HUGGINGFACE_TOKEN}"
      }
    }
  }
}
```

**Setup**:
```bash
# Add to ~/.bashrc or ~/.zshrc
export HUGGINGFACE_TOKEN="hf_xxxxxxxxxxxxxxxxxxxx"

# Verify CLI access
gh auth login
```

### GitHub MCP (stdio)

**Requirements**:
- GitHub account with authentication
- gh CLI installed and authenticated
- Node.js 18+ and npx

**Configuration**:
```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "sh",
      "args": ["-c", "GH_TOKEN=$(gh auth token) npx @modelcontextprotocol/server-github"],
      "env": {}
    }
  }
}
```

**Setup**:
```bash
# Install gh CLI
sudo apt-get install gh  # Linux
brew install gh          # macOS

# Authenticate
gh auth login

# Verify token access
gh auth token
```

### shadcn/ui MCP (stdio)

**Requirements**:
- Node.js 18+ and npx
- No authentication required

**Configuration**:
```json
{
  "mcpServers": {
    "shadcn": {
      "type": "stdio",
      "command": "npx",
      "args": ["shadcn@latest", "mcp"],
      "env": {}
    }
  }
}
```

**Setup**:
```bash
# Verify Node.js version
node --version  # Should be 18+

# Test npx access
npx --version
```

### Playwright MCP (stdio)

**Requirements**:
- Node.js 18+ and npx
- Playwright browsers (installed automatically)

**Configuration**:
```json
{
  "mcpServers": {
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {}
    }
  }
}
```

**Setup**:
```bash
# Install Playwright browsers (if prompted)
npx playwright install
```

### MarkItDown (stdio)

**Requirements**:
- Python 3.11+
- UV package manager (required - no pip allowed)

**Configuration**:
```json
{
  "mcpServers": {
    "markitdown": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "markitdown-mcp"],
      "env": {}
    }
  }
}
```

**Setup**:
```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify UV installation
uv --version

# Install markitdown-mcp
uv tool install markitdown-mcp

# Verify installation
uv run markitdown-mcp --version
```

## Testing Connectivity

### Verify All Servers

```bash
# List all configured MCP servers
claude mcp list

# Expected output:
# context7 (http) - Connected
# playwright (stdio) - Connected
# github (stdio) - Connected
# shadcn (stdio) - Connected
# hf-mcp-server (http) - Connected
# markitdown (stdio) - Connected
```

### Test Individual Servers

```bash
# Test HTTP server
curl -H "CONTEXT7_API_KEY: $CONTEXT7_API_KEY" https://mcp.context7.com/mcp/health

# Test stdio server
npx shadcn@latest mcp --help
```

## Environment Variables

All environment variables should be set in your shell configuration file:

**For Bash** (`~/.bashrc`):
```bash
export CONTEXT7_API_KEY="your-context7-api-key"
export HUGGINGFACE_TOKEN="hf_xxxxxxxxxxxxxxxxxxxx"
```

**For Zsh** (`~/.zshrc`):
```bash
export CONTEXT7_API_KEY="your-context7-api-key"
export HUGGINGFACE_TOKEN="hf_xxxxxxxxxxxxxxxxxxxx"
```

**Reload Configuration**:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

## Troubleshooting

### Server Not Found
```
Error: Server 'context7' not found in configuration
```

**Solution**: Verify ~/.claude.json contains the server definition.

### Authentication Failed
```
Error: HTTP 401 Unauthorized
```

**Solution**: Check environment variable is set correctly:
```bash
echo $CONTEXT7_API_KEY
```

### Command Not Found
```
Error: command not found: uv
```

**Solution**: Install required dependencies:
```bash
# For UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# For gh CLI
sudo apt-get install gh
```

### Connection Timeout
```
Error: Connection timeout after 30s
```

**Solution**: Check network connectivity and firewall settings.

## Complete Example Configuration

Here's a complete ~/.claude.json example with all 6 servers:

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
      "type": "stdio",
      "command": "sh",
      "args": ["-c", "GH_TOKEN=$(gh auth token) npx @modelcontextprotocol/server-github"],
      "env": {}
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
      "args": ["run", "markitdown-mcp"],
      "env": {}
    }
  }
}
```

## Next Steps

- [Server Management Guide](servers.md) - Adding and managing MCP servers
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [API Documentation](api.md) - Python API reference

## Security Notes

⚠️ **Never commit actual API keys to repository**
- Use environment variables for all secrets
- Keep ~/.claude.json local only
- Use templates in documentation

## Related Resources

- [AGENTS.md](../AGENTS.md) - Complete project instructions
- [FOLLOWING-INSTRUCTIONS.md](FOLLOWING-INSTRUCTIONS.md) - Why compliance matters
- [CHANGELOG.md](../CHANGELOG.md) - Historical configuration examples