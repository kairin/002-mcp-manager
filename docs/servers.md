# Server Management Guide

> **Adding, Configuring, and Managing MCP Servers**

## Overview

MCP Manager provides tools for managing Model Context Protocol servers across all Claude Code sessions. This guide covers adding new servers, updating configurations, and maintaining server health.

## Quick Reference

### Essential Commands

```bash
# List all configured servers
claude mcp list

# Add new server (planned)
mcp-manager add <server-name> --type <http|stdio>

# Remove server (planned)
mcp-manager remove <server-name>

# Check server health (planned)
mcp-manager status

# Update server configuration (planned)
mcp-manager update <server-name>
```

## Adding New Servers

### HTTP Server Example

To add a new HTTP-based MCP server:

1. **Obtain API credentials** from the service provider
2. **Set environment variable**:
   ```bash
   export SERVICE_API_KEY="your-api-key"
   ```

3. **Add to ~/.claude.json**:
   ```json
   {
     "mcpServers": {
       "service-name": {
         "type": "http",
         "url": "https://api.example.com/mcp",
         "headers": {
           "Authorization": "Bearer ${SERVICE_API_KEY}"
         }
       }
     }
   }
   ```

4. **Verify connectivity**:
   ```bash
   claude mcp list
   ```

### stdio Server Example

To add a new stdio-based MCP server:

1. **Install required package**:
   ```bash
   # For Node.js packages
   npx install-package@latest

   # For Python packages (UV-first only)
   uv tool install package-name
   ```

2. **Add to ~/.claude.json**:
   ```json
   {
     "mcpServers": {
       "service-name": {
         "type": "stdio",
         "command": "npx",
         "args": ["package-name@latest"],
         "env": {}
       }
     }
   }
   ```

3. **Test execution**:
   ```bash
   npx package-name@latest --help
   ```

## Current Server Inventory

### Production Servers (6 Active)

#### 1. Context7 (HTTP)
- **Purpose**: Library documentation and code examples
- **Type**: HTTP
- **URL**: https://mcp.context7.com/mcp
- **Authentication**: CONTEXT7_API_KEY
- **Status**: ✅ Connected
- **Use Cases**:
  - Fetching library documentation
  - Finding code examples
  - Resolving package versions

#### 2. Hugging Face MCP (HTTP)
- **Purpose**: AI model search and access
- **Type**: HTTP
- **URL**: https://huggingface.co/mcp
- **Authentication**: HUGGINGFACE_TOKEN
- **Status**: ✅ Connected
- **Use Cases**:
  - Searching ML models
  - Finding datasets
  - Accessing model documentation

#### 3. GitHub MCP (stdio)
- **Purpose**: GitHub API integration
- **Type**: stdio
- **Command**: `sh -c "GH_TOKEN=$(gh auth token) npx @modelcontextprotocol/server-github"`
- **Authentication**: GitHub CLI (gh)
- **Status**: ✅ Connected
- **Use Cases**:
  - Repository management
  - Pull request operations
  - Issue tracking
  - Workflow management

#### 4. shadcn/ui MCP (stdio)
- **Purpose**: UI component registry access
- **Type**: stdio
- **Command**: `npx shadcn@latest mcp`
- **Authentication**: None required
- **Status**: ✅ Connected
- **Use Cases**:
  - Component search
  - Installation commands
  - Configuration examples

#### 5. Playwright MCP (stdio)
- **Purpose**: Browser automation and testing
- **Type**: stdio
- **Command**: `npx @playwright/mcp@latest`
- **Authentication**: None required
- **Status**: ✅ Connected
- **Use Cases**:
  - Web scraping
  - Browser automation
  - Testing workflows

#### 6. MarkItDown (stdio)
- **Purpose**: Document conversion to markdown
- **Type**: stdio
- **Command**: `uv run markitdown-mcp`
- **Authentication**: None required
- **Status**: ✅ Connected
- **Use Cases**:
  - PDF to markdown conversion
  - Office document processing
  - Image text extraction

## Server Configuration Patterns

### Pattern 1: Simple HTTP Server
```json
{
  "type": "http",
  "url": "https://api.example.com/mcp",
  "headers": {
    "API-Key": "${ENV_VAR_NAME}"
  }
}
```

### Pattern 2: HTTP Server with Bearer Token
```json
{
  "type": "http",
  "url": "https://api.example.com/mcp",
  "headers": {
    "Authorization": "Bearer ${TOKEN_ENV_VAR}"
  }
}
```

### Pattern 3: Simple stdio Server (npx)
```json
{
  "type": "stdio",
  "command": "npx",
  "args": ["package-name@latest"],
  "env": {}
}
```

### Pattern 4: stdio Server with Shell Command
```json
{
  "type": "stdio",
  "command": "sh",
  "args": ["-c", "ENV_VAR=$(command) npx package-name"],
  "env": {}
}
```

### Pattern 5: Python stdio Server (UV-first)
```json
{
  "type": "stdio",
  "command": "uv",
  "args": ["run", "package-name"],
  "env": {}
}
```

### Pattern 6: Binary Executable
```json
{
  "type": "stdio",
  "command": "/absolute/path/to/binary",
  "args": ["--flag", "value"],
  "env": {
    "CUSTOM_ENV": "value"
  }
}
```

## Updating Server Configurations

### Updating HTTP Server URL
```bash
# 1. Backup current configuration
cp ~/.claude.json ~/.claude.json.backup

# 2. Edit configuration
nano ~/.claude.json

# 3. Update URL
# Change: "url": "https://old.example.com/mcp"
# To: "url": "https://new.example.com/mcp"

# 4. Verify connectivity
claude mcp list
```

### Updating stdio Server Command
```bash
# 1. Test new command works
npx new-package@latest --help

# 2. Update ~/.claude.json
# Change args array to use new package

# 3. Restart Claude Code
claude restart

# 4. Verify server loads
claude mcp list
```

## Removing Servers

### Manual Removal
```bash
# 1. Backup configuration
cp ~/.claude.json ~/.claude.json.backup

# 2. Edit ~/.claude.json
nano ~/.claude.json

# 3. Remove server block entirely
# Delete the entire "server-name": { ... } block

# 4. Verify removal
claude mcp list
```

### Automated Removal (Planned)
```bash
# Future MCP Manager command
mcp-manager remove server-name
```

## Health Monitoring

### Check All Servers
```bash
# List all servers with status
claude mcp list

# Expected output shows:
# ✅ Connected servers
# ❌ Disconnected servers
# ⚠️  Warning status
```

### Manual Health Check

#### HTTP Server Health Check
```bash
# Test direct API access
curl -H "API-Key: $ENV_VAR" https://api.example.com/mcp/health

# Expected: HTTP 200 OK
```

#### stdio Server Health Check
```bash
# Test command execution
npx package-name@latest --version

# Expected: Version output
```

### Automated Health Monitoring (Planned)
```bash
# Future MCP Manager commands
mcp-manager status              # Check all servers
mcp-manager status server-name  # Check specific server
mcp-manager monitor             # Real-time monitoring
```

## Troubleshooting Server Issues

### Server Not Showing in List

**Symptoms**:
```
$ claude mcp list
context7 (http) - Connected
# Missing server not shown
```

**Solution**:
1. Verify ~/.claude.json contains server definition
2. Check JSON syntax is valid:
   ```bash
   python3 -m json.tool ~/.claude.json
   ```
3. Restart Claude Code:
   ```bash
   claude restart
   ```

### Server Shows as Disconnected

**Symptoms**:
```
context7 (http) - ❌ Disconnected
```

**Solutions**:

For HTTP servers:
1. Check environment variable is set:
   ```bash
   echo $CONTEXT7_API_KEY
   ```
2. Verify API endpoint is accessible:
   ```bash
   curl https://mcp.context7.com/mcp
   ```
3. Check API key is valid (try in browser/Postman)

For stdio servers:
1. Test command runs directly:
   ```bash
   npx shadcn@latest mcp --help
   ```
2. Check Node.js/Python version requirements
3. Verify package is installed globally

### Command Not Found Error

**Symptoms**:
```
Error: command not found: uv
```

**Solutions**:
1. Install missing dependency:
   ```bash
   # UV
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # gh CLI
   sudo apt-get install gh

   # Node.js/npx
   nvm install 18
   ```
2. Add to PATH:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
3. Verify installation:
   ```bash
   which uv
   uv --version
   ```

## Server Security

### Environment Variable Security

✅ **DO**:
- Store secrets in environment variables
- Use ${VAR_NAME} syntax in ~/.claude.json
- Keep ~/.claude.json local only
- Add ~/.claude.json to .gitignore

❌ **DO NOT**:
- Hardcode API keys in ~/.claude.json
- Commit ~/.claude.json to repositories
- Share API keys in documentation
- Use production keys in examples

### API Key Rotation

When rotating API keys:

1. **Generate new key** from service provider
2. **Update environment variable**:
   ```bash
   # In ~/.bashrc or ~/.zshrc
   export CONTEXT7_API_KEY="new-key-here"
   ```
3. **Reload shell configuration**:
   ```bash
   source ~/.bashrc
   ```
4. **Verify new key works**:
   ```bash
   claude mcp list
   ```
5. **Revoke old key** from service provider

## Performance Optimization

### Caching Strategies

For HTTP servers:
- Context7: Caches documentation for 15 minutes
- Hugging Face: Caches model metadata for 1 hour

For stdio servers:
- Playwright: Browser instances persist across calls
- MarkItDown: Processes files on-demand only

### Connection Pooling

HTTP servers maintain persistent connections:
- Maximum 10 concurrent connections per server
- Connection timeout: 30 seconds
- Retry attempts: 3 with exponential backoff

## Future Enhancements

### Planned MCP Manager Features

- **Automatic Discovery**: Scan and suggest popular MCP servers
- **One-Command Installation**: `mcp-manager add github`
- **Health Dashboard**: Real-time monitoring interface
- **Performance Metrics**: Response time tracking
- **Configuration Migration**: Import from project configs
- **Backup/Restore**: Automated configuration backups

### Community Server Registry

Planned integration with community MCP server registry:
- Search available servers
- View server ratings and reviews
- Install with verified configurations
- Share custom server configurations

## Next Steps

- [Configuration Guide](configuration.md) - Detailed setup instructions
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [API Documentation](api.md) - Python API reference

## Related Resources

- [AGENTS.md](../AGENTS.md) - Project requirements and standards
- [CHANGELOG.md](../CHANGELOG.md) - Server connectivity history
- [README.md](../README.md) - Project overview