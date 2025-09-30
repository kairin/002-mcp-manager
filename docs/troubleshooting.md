# Troubleshooting Guide

> **Common Issues and Solutions for MCP Manager**

## Quick Diagnostics

### Run Complete Diagnostic Check (Planned)
```bash
mcp-manager diagnose
```

### Manual Quick Check
```bash
# 1. Check all servers
claude mcp list

# 2. Verify configuration exists
test -f ~/.claude.json && echo "✅ Config exists" || echo "❌ Missing config"

# 3. Check environment variables
echo "CONTEXT7_API_KEY: ${CONTEXT7_API_KEY:+SET}"
echo "HUGGINGFACE_TOKEN: ${HUGGINGFACE_TOKEN:+SET}"

# 4. Verify dependencies
which uv gh npx node python3
```

## Common Issues

### 1. ModuleNotFoundError After Installation

**Symptoms**:
```
ModuleNotFoundError: No module named 'markitdown'
```

**Root Cause**: Package installed with pip instead of UV

**Solution** (UV-FIRST MANDATORY):
```bash
# ❌ WRONG - Never use pip
pip install markitdown-mcp

# ✅ CORRECT - Always use UV
uv tool install markitdown-mcp

# Verify UV installation
uv tool list
```

**Prevention**: Always follow [AGENTS.md](../AGENTS.md) UV-first requirements

**Real-World Example**: See [CHANGELOG v1.2.0](../CHANGELOG.md#120---2025-09-25) for MarkItDown case study

### 2. Command Not Found: uv

**Symptoms**:
```
bash: uv: command not found
```

**Solution**:
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc

# Verify installation
uv --version
```

### 3. Command Not Found: gh

**Symptoms**:
```
bash: gh: command not found
```

**Solution**:
```bash
# Linux (Debian/Ubuntu)
sudo apt-get update
sudo apt-get install gh

# Linux (Fedora/RHEL)
sudo dnf install gh

# macOS
brew install gh

# Authenticate
gh auth login

# Verify
gh auth status
```

### 4. GitHub MCP Authentication Failed

**Symptoms**:
```
Error: GitHub MCP server failed to connect
Error: authentication required
```

**Solutions**:

**Check 1: Verify gh CLI authentication**
```bash
# Check auth status
gh auth status

# Should show:
# ✓ Logged in to github.com as username

# If not authenticated
gh auth login
```

**Check 2: Verify token access**
```bash
# Get current token
gh auth token

# Should output: ghp_xxxxxxxxxxxxxxxxxxxx
```

**Check 3: Test GitHub API access**
```bash
# Test API with token
curl -H "Authorization: token $(gh auth token)" https://api.github.com/user
```

**Check 4: Verify ~/.claude.json configuration**
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

### 5. Context7 API Key Not Working

**Symptoms**:
```
Error: HTTP 401 Unauthorized
Error: Invalid API key for context7
```

**Solutions**:

**Check 1: Verify environment variable is set**
```bash
# Check if set
echo $CONTEXT7_API_KEY

# Should output your API key
# If empty, add to shell config
```

**Check 2: Add to shell configuration**
```bash
# Edit ~/.bashrc or ~/.zshrc
nano ~/.bashrc

# Add line:
export CONTEXT7_API_KEY="your-api-key-here"

# Reload
source ~/.bashrc
```

**Check 3: Verify API key format**
```bash
# Context7 keys typically start with specific prefix
# Verify at https://context7.com dashboard
```

**Check 4: Test direct API access**
```bash
curl -H "CONTEXT7_API_KEY: $CONTEXT7_API_KEY" \
     https://mcp.context7.com/mcp/health
```

### 6. Hugging Face Token Invalid

**Symptoms**:
```
Error: HTTP 403 Forbidden
Error: Invalid Hugging Face token
```

**Solutions**:

**Check 1: Verify token format**
```bash
# HF tokens start with 'hf_'
echo $HUGGINGFACE_TOKEN | grep -q '^hf_' && echo "✅ Valid format" || echo "❌ Invalid format"
```

**Check 2: Generate new token**
1. Visit https://huggingface.co/settings/tokens
2. Create new token with read permissions
3. Copy token (starts with `hf_`)
4. Update environment variable

**Check 3: Test token directly**
```bash
curl -H "Authorization: Bearer $HUGGINGFACE_TOKEN" \
     https://huggingface.co/api/whoami
```

### 7. Playwright Browser Not Installed

**Symptoms**:
```
Error: Executable doesn't exist at /path/to/chromium
Error: Please install playwright browsers
```

**Solution**:
```bash
# Install all Playwright browsers
npx playwright install

# Or install specific browser
npx playwright install chromium

# Verify installation
npx playwright --version
```

### 8. Node.js Version Too Old

**Symptoms**:
```
Error: Node.js version 16.x not supported
Error: Please upgrade to Node.js 18+
```

**Solution**:
```bash
# Using nvm (recommended)
nvm install 18
nvm use 18
nvm alias default 18

# Verify version
node --version  # Should show v18.x or higher

# Restart Claude Code
claude restart
```

### 9. Python Version Too Old

**Symptoms**:
```
Error: Python 3.9 not supported
Error: Requires Python 3.11+
```

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install python3.11

# macOS
brew install python@3.11

# Verify version
python3 --version  # Should show 3.11 or higher

# Update UV to use correct Python
uv python install 3.11
```

### 10. JSON Syntax Error in ~/.claude.json

**Symptoms**:
```
Error: Failed to parse ~/.claude.json
Error: Unexpected token } in JSON
```

**Solution**:
```bash
# Validate JSON syntax
python3 -m json.tool ~/.claude.json

# If error, shows line number of issue

# Common issues:
# - Missing comma between objects
# - Trailing comma after last item
# - Unescaped quotes in strings
# - Missing closing braces

# Restore from backup if needed
cp ~/.claude.json.backup ~/.claude.json
```

### 11. Server Connection Timeout

**Symptoms**:
```
Error: Connection timeout after 30 seconds
Error: Failed to connect to server
```

**Solutions**:

**Check 1: Verify network connectivity**
```bash
# Test internet connection
ping -c 3 google.com

# Test specific MCP endpoint
curl -I https://mcp.context7.com/mcp
```

**Check 2: Check firewall settings**
```bash
# Verify no blocking rules
sudo ufw status

# Allow outbound HTTPS if needed
sudo ufw allow out 443/tcp
```

**Check 3: Check proxy settings**
```bash
# If behind corporate proxy
export https_proxy="http://proxy.company.com:8080"
```

**Check 4: Increase timeout (planned feature)**
```json
{
  "mcpServers": {
    "context7": {
      "timeout": 60
    }
  }
}
```

### 12. Multiple Servers Failing

**Symptoms**:
```
$ claude mcp list
context7 (http) - ❌ Disconnected
shadcn (stdio) - ❌ Disconnected
github (stdio) - ❌ Disconnected
```

**Solution - Complete Reset**:
```bash
# 1. Backup current configuration
cp ~/.claude.json ~/.claude.json.backup

# 2. Verify environment variables
cat >> ~/.bashrc << 'EOF'
export CONTEXT7_API_KEY="your-key"
export HUGGINGFACE_TOKEN="hf_your-token"
EOF

# 3. Reload environment
source ~/.bashrc

# 4. Verify dependencies
uv --version
gh auth status
node --version
npx --version

# 5. Restart Claude Code
claude restart

# 6. Test each server individually
claude mcp list
```

## Configuration Issues

### Issue: ~/.claude.json Missing

**Solution**:
```bash
# Create new configuration
mkdir -p ~/.claude
cat > ~/.claude.json << 'EOF'
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
EOF
```

### Issue: Permission Denied on ~/.claude.json

**Solution**:
```bash
# Fix permissions
chmod 600 ~/.claude.json

# Verify
ls -la ~/.claude.json
# Should show: -rw------- (read/write for owner only)
```

### Issue: Configuration Corruption

**Solution**:
```bash
# If backup exists
cp ~/.claude.json.backup ~/.claude.json

# If no backup, recreate from scratch
# See configuration.md for complete examples
```

## Performance Issues

### Issue: Slow Server Response Times

**Symptoms**:
```
Server response taking >5 seconds
Frequent timeout errors
```

**Solutions**:

**Check 1: Network latency**
```bash
# Test API latency
time curl https://mcp.context7.com/mcp
```

**Check 2: Server load**
```bash
# Check system resources
top
htop
```

**Check 3: Clear caches** (planned feature)
```bash
mcp-manager cache clear
```

### Issue: High Memory Usage

**Symptoms**:
```
MCP servers consuming excessive memory
System becoming unresponsive
```

**Solutions**:

**Check 1: Identify resource-heavy servers**
```bash
# Monitor processes
ps aux | grep -E "(mcp|npx|uv)"
```

**Check 2: Restart specific server** (planned)
```bash
mcp-manager restart server-name
```

**Check 3: Adjust resource limits** (planned)
```json
{
  "mcpServers": {
    "playwright": {
      "resourceLimits": {
        "maxMemory": "512M"
      }
    }
  }
}
```

## GitHub Pages Deployment Issues

### Issue: Website Shows 404 Error

**Symptoms**:
- https://kairin.github.io/mcp-manager shows 404
- "There isn't a GitHub Pages site here"

**Root Cause**: Built files missing from docs/ directory

**Solution**:
```bash
# 1. Verify docs/ directory exists
ls -la docs/

# 2. Rebuild website
npm run build

# 3. Verify critical files exist
test -f docs/index.html && echo "✅" || echo "❌ Missing index.html"
test -d docs/_astro && echo "✅" || echo "❌ Missing _astro/"
test -f docs/.nojekyll && echo "✅" || echo "❌ Missing .nojekyll"

# 4. Commit and push
git add docs/
git commit -m "fix: rebuild website for GitHub Pages deployment"
git push origin main

# 5. Wait 2-5 minutes for deployment

# 6. Verify deployment
curl -I https://kairin.github.io/mcp-manager
# Should show: HTTP/2 200
```

**Prevention**: Always run `npm run build` before committing website changes

### Issue: Assets Not Loading (404 on CSS/JS)

**Symptoms**:
- Website loads but no styling
- Console shows 404 errors for /_astro/*.css

**Root Cause**: Incorrect base path configuration

**Solution**:
```javascript
// Verify astro.config.mjs
export default defineConfig({
  site: 'https://kairin.github.io',
  base: '/mcp-manager',  // MUST match repository name
  outDir: './docs',
});
```

## Development Issues

### Issue: Pre-commit Hook Blocking Commit

**Symptoms**:
```
❌ Build failed! Commit blocked.
```

**Solutions**:

**Option 1: Fix build errors**
```bash
# Run build manually to see errors
npm run build

# Fix errors shown
# Retry commit
```

**Option 2: Bypass hook temporarily** (use with caution)
```bash
# Only if absolutely necessary
git commit --no-verify -m "emergency fix"

# Then immediately fix and rebuild
npm run build
git add docs/
git commit -m "fix: rebuild after emergency commit"
```

### Issue: UV Package Not Found

**Symptoms**:
```
Error: Package 'markitdown-mcp' not found
```

**Solution**:
```bash
# List installed UV tools
uv tool list

# Install missing package
uv tool install markitdown-mcp

# Verify installation
uv tool list | grep markitdown
```

### Issue: Import Errors in Python Code

**Symptoms**:
```python
ModuleNotFoundError: No module named 'rich'
```

**Solution**:
```bash
# Install dependencies with UV
uv pip install -r requirements.txt

# Or install specific package
uv pip install rich

# Verify
uv pip list | grep rich
```

## Emergency Recovery

### Complete System Reset

If all else fails, reset to known-good state:

```bash
# 1. Backup everything
cp ~/.claude.json ~/claude.json.emergency.backup
cp ~/.bashrc ~/bashrc.emergency.backup

# 2. Clean installations
rm -rf ~/.local/share/uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Reinstall gh CLI
sudo apt-get remove gh
sudo apt-get install gh
gh auth login

# 4. Reinstall Node.js via nvm
nvm install 18
nvm use 18

# 5. Recreate ~/.claude.json from template
# See configuration.md

# 6. Set environment variables
# Add to ~/.bashrc

# 7. Reload environment
source ~/.bashrc

# 8. Verify everything
claude mcp list
```

## Getting Help

### Collect Diagnostic Information

```bash
# System information
uname -a
python3 --version
node --version
uv --version

# Environment variables (sanitized)
echo "CONTEXT7_API_KEY: ${CONTEXT7_API_KEY:+SET}"
echo "HUGGINGFACE_TOKEN: ${HUGGINGFACE_TOKEN:+SET}"

# Configuration status
test -f ~/.claude.json && echo "Config exists" || echo "Config missing"

# Server status
claude mcp list

# Recent errors (if logs available)
tail -n 50 ~/.claude/logs/mcp-manager.log
```

### Report Issues

When reporting issues, include:

1. **Symptoms**: Exact error messages
2. **Steps to reproduce**: What you did before the error
3. **Environment**: Output from diagnostic collection above
4. **Configuration**: Sanitized ~/.claude.json (remove API keys)
5. **Recent changes**: What changed before issue started

### Useful Resources

- [Configuration Guide](configuration.md) - Setup instructions
- [Server Management Guide](servers.md) - Adding and managing servers
- [API Documentation](api.md) - Python API reference
- [AGENTS.md](../AGENTS.md) - Project requirements
- [CHANGELOG.md](../CHANGELOG.md) - Known issues and fixes

## Preventive Maintenance

### Regular Health Checks

```bash
# Weekly verification
claude mcp list

# Monthly dependency updates
uv tool update markitdown-mcp
npx update-notifier

# Backup configuration
cp ~/.claude.json ~/.claude.json.$(date +%Y%m%d)
```

### Configuration Backups

```bash
# Automated daily backups (add to crontab)
0 0 * * * cp ~/.claude.json ~/.claude.json.backup.$(date +\%Y\%m\%d)

# Keep only last 7 days
0 1 * * * find ~/.claude.json.backup.* -mtime +7 -delete
```

## Known Issues

### Issue: GitHub MCP Slow Performance

**Status**: Investigating
**Workaround**: Use gh CLI directly for complex operations
**Tracking**: N/A

### Issue: MarkItDown PDF Processing Errors

**Status**: Upstream issue
**Workaround**: Pre-process PDFs with poppler-utils
**Tracking**: https://github.com/microsoft/markitdown/issues

## Next Steps

- [Configuration Guide](configuration.md) - Detailed setup
- [Server Management](servers.md) - Managing MCP servers
- [API Documentation](api.md) - Python API reference

---

**Last Updated**: 2025-09-30
**Maintainer**: MCP Manager Project
**Feedback**: Report issues at repository issue tracker