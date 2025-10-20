# GitHub MCP Server Setup

## Overview

This document explains how the GitHub MCP (Model Context Protocol) server is configured for this project to work with Claude Code using the GitHub CLI (`gh`) for authentication.

## Problem

The GitHub MCP server requires a GitHub Personal Access Token via the `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable. Instead of hardcoding tokens (security risk), we use the `gh` CLI's authentication.

## Solution

### 1. Wrapper Script

Created: `/home/kkk/.local/bin/github-mcp-wrapper.sh`

```bash
#!/usr/bin/env bash
# GitHub MCP Server Wrapper
# Automatically fetches GitHub token from gh CLI and starts the MCP server

set -euo pipefail

# Get token from gh CLI
export GITHUB_PERSONAL_ACCESS_TOKEN=$(gh auth token)

# Start the GitHub MCP server
exec /home/kkk/.local/bin/github-mcp-server stdio
```

**Why a wrapper?**
- Cleaner than inline `bash -c` commands
- Easier to debug and maintain
- Follows XDG Base Directory standards
- More reliable for Claude Code to execute

### 2. Configuration

All MCP profile configurations updated:
- `~/.config/claude-code/mcp-servers.json` (active profile)
- `~/.config/claude-code/mcp-servers-dev.json`
- `~/.config/claude-code/mcp-servers-ui.json`
- `~/.config/claude-code/mcp-servers-full.json`

**Configuration format:**
```json
{
  "mcpServers": {
    "github": {
      "command": "/home/kkk/.local/bin/github-mcp-wrapper.sh",
      "description": "GitHub API integration for repositories, issues, PRs, and CI/CD"
    }
  }
}
```

## Prerequisites

1. **GitHub CLI (`gh`)** - Must be installed and authenticated
   ```bash
   gh auth login
   gh auth status  # Verify authentication
   ```

2. **GitHub MCP Server Binary** - Must be installed at `/home/kkk/.local/bin/github-mcp-server`
   ```bash
   # Install via npm (if needed)
   npm install -g @modelcontextprotocol/server-github
   ```

3. **Required Scopes** - GitHub token must have:
   - `repo` - Full control of private repositories
   - `workflow` - Update GitHub Action workflows
   - `read:org` - Read org and team membership
   - `admin:repo_hook` - Full control of repository hooks
   - `gist` - Create gists
   - `write:packages` - Upload packages

## Verification

### Test GitHub CLI Authentication
```bash
gh auth status
```

Expected output:
```
github.com
  ✓ Logged in to github.com account <username>
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'admin:repo_hook', 'gist', 'read:org', 'repo', 'workflow', 'write:packages'
```

### Test Wrapper Script
```bash
timeout 2 /home/kkk/.local/bin/github-mcp-wrapper.sh
```

Expected output:
```
time=... level=INFO msg="starting server" version=0.16.0 ...
GitHub MCP Server running on stdio
time=... level=INFO msg="shutting down server" signal="context done"
```

### Test in Claude Code

1. Restart Claude Code (or reload window in VS Code)
2. Check if GitHub MCP tools are available
3. Try a GitHub-related command

## Troubleshooting

### Issue: "Parse error" when testing manually

**Normal behavior** - The server expects JSON-RPC formatted input on stdin. When run manually without a proper MCP client, it shows parse errors. This doesn't indicate a problem.

### Issue: Server won't connect

1. **Check gh authentication:**
   ```bash
   gh auth status
   ```

2. **Verify wrapper is executable:**
   ```bash
   ls -la /home/kkk/.local/bin/github-mcp-wrapper.sh
   ```
   Should show `-rwxr-xr-x` (executable permissions)

3. **Test token retrieval:**
   ```bash
   gh auth token
   ```
   Should output your GitHub token

4. **Check binary exists:**
   ```bash
   ls -la /home/kkk/.local/bin/github-mcp-server
   ```

5. **Restart Claude Code completely**

### Issue: Token expires

GitHub CLI handles token refresh automatically. If authentication expires:
```bash
gh auth login --web
```

## Architecture Alignment

This setup follows the project's architectural principles:

✅ **Modular-First Design** - Wrapper script is independent, reusable
✅ **Security by Default** - No hardcoded tokens, dynamic token retrieval
✅ **XDG Standards** - Follows `~/.local/bin/` and `~/.config/` conventions
✅ **Minimal Complexity** - Simple bash script, no unnecessary dependencies
✅ **Maintainability** - Clear separation, easy to debug and update

## Related Files

- Wrapper: `/home/kkk/.local/bin/github-mcp-wrapper.sh`
- Binary: `/home/kkk/.local/bin/github-mcp-server`
- Active config: `~/.config/claude-code/mcp-servers.json`
- Dev profile: `~/.config/claude-code/mcp-servers-dev.json`
- UI profile: `~/.config/claude-code/mcp-servers-ui.json`
- Full profile: `~/.config/claude-code/mcp-servers-full.json`

## References

- [GitHub MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [GitHub CLI Authentication](https://cli.github.com/manual/gh_auth_login)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)

---

**Last Updated**: 2025-10-20
**Status**: ✅ Configured and tested
