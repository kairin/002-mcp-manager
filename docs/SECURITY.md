# 🔒 MCP Manager Security Guide

> **CRITICAL**: This document outlines security best practices for MCP server configuration and API key management.

## 🚨 Security Issue Resolution (2025-10-17)

### Issue Identified
Previous implementation stored API keys and tokens **directly in configuration files** (`~/.claude.json`), which is a critical security vulnerability:

```json
// ❌ WRONG - Hardcoded tokens (VULNERABLE)
{
  "mcpServers": {
    "context7": {
      "headers": {
        "CONTEXT7_API_KEY": "ctx7sk-actual-key-here"
      }
    }
  }
}
```

### Impact
- API keys exposed in configuration files
- Credentials could be accidentally committed to git
- Tokens could be shared when syncing configs across machines
- No token rotation or expiration management

### Resolution
**✅ FIXED**: Updated implementation uses environment variable references:

```json
// ✅ CORRECT - Environment variable reference (SECURE)
{
  "mcpServers": {
    "context7": {
      "headers": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    }
  }
}
```

## 🛡️ Secure Configuration Pattern

### Environment Variable Setup

1. **Create `.env` file** (excluded from git):
```bash
# Copy template
cp .env.example .env

# Edit with your actual tokens
nano .env
```

2. **Add your tokens to `.env`**:
```bash
# MCP Server API Keys
CONTEXT7_API_KEY=ctx7sk-your-actual-key
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your-actual-token
HUGGINGFACE_TOKEN=hf_your-actual-token
```

3. **Load environment variables**:
```bash
# Option 1: Source before running
source .env

# Option 2: Add to ~/.bashrc or ~/.zshrc
cat >> ~/.bashrc << 'EOF'
# MCP Manager environment variables
if [ -f ~/Apps/mcp-manager/.env ]; then
    source ~/Apps/mcp-manager/.env
fi
EOF

# Option 3: Use direnv (recommended)
echo "source_env" > .envrc
direnv allow
```

### MCP Server Configuration

**Context7**:
```json
{
  "type": "http",
  "url": "https://mcp.context7.com/mcp",
  "headers": {
    "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
  }
}
```

**GitHub**:
```json
{
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp",
  "headers": {
    "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
  }
}
```

**Hugging Face**:
```json
{
  "type": "http",
  "url": "https://huggingface.co/mcp",
  "headers": {
    "Authorization": "Bearer ${HUGGINGFACE_TOKEN}"
  }
}
```

## 🔄 Migrating from Insecure Configuration

If you have an existing configuration with hardcoded tokens:

### Step 1: Run Migration Script
```bash
cd ~/Apps/mcp-manager
uv run python scripts/security/migrate-to-env-vars.py
```

The script will:
- ✅ Backup your current configuration
- ✅ Extract hardcoded tokens
- ✅ Create `.env` file with tokens
- ✅ Update configuration to use environment variable references

### Step 2: Revoke Exposed Tokens

**⚠️ CRITICAL**: If your API keys were exposed, you **MUST** revoke them immediately:

**Context7**:
1. Visit: https://context7.com/settings
2. Revoke old key
3. Generate new key
4. Update `.env` file

**GitHub**:
1. Visit: https://github.com/settings/tokens
2. Delete exposed token
3. Generate new token with same scopes
4. Update `.env` file

**Hugging Face**:
1. Visit: https://huggingface.co/settings/tokens
2. Revoke old token
3. Create new token
4. Update `.env` file

### Step 3: Verify Configuration
```bash
# Source environment variables
source .env

# Verify tokens are loaded
echo $CONTEXT7_API_KEY | head -c 10  # Should show first 10 chars

# Test MCP servers
claude mcp list
```

## 🔐 Security Best Practices

### 1. Never Commit Secrets
```bash
# Verify .gitignore protects sensitive files
cat .gitignore | grep -E "\.env|\.claude\.json|\.gemini"

# Check git history for accidentally committed secrets
git log --all --full-history -- "*.json" | grep -i "bearer\|api_key"
```

### 2. Use Secure File Permissions
```bash
# Protect .env file
chmod 600 .env

# Protect configuration files
chmod 600 ~/.claude.json
chmod 600 ~/.config/gemini/settings.json
```

### 3. Token Rotation
```bash
# Rotate tokens every 90 days
# Set reminder:
echo "Rotate MCP API tokens" | at now + 90 days
```

### 4. Audit Configuration
```bash
# Check for hardcoded tokens
uv run python -m mcp_manager.cli audit --security
```

## 📋 Security Checklist

Before deploying or sharing your configuration:

- [ ] All API keys stored in environment variables
- [ ] `.env` file excluded from git (in `.gitignore`)
- [ ] `.claude.json` excluded from git
- [ ] No hardcoded tokens in configuration files
- [ ] File permissions set to `600` for sensitive files
- [ ] Token rotation schedule established
- [ ] Exposed tokens revoked and regenerated
- [ ] Security audit passed

## 🚨 If You've Exposed Credentials

### Immediate Actions
1. **Revoke all exposed tokens immediately**
2. **Check git history for committed secrets**:
   ```bash
   git log --all --full-history -S "your-token-prefix" --source --all
   ```
3. **Remove from git history if committed**:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .claude.json" \
     --prune-empty --tag-name-filter cat -- --all
   ```
4. **Generate new tokens**
5. **Update `.env` file**
6. **Force push cleaned history** (if repository is not public)

### Preventive Measures
- Enable GitHub secret scanning
- Use pre-commit hooks to detect secrets
- Set up git-secrets or similar tools

## 🔗 Related Resources

- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## 📞 Security Contacts

If you discover a security vulnerability:
- **DO NOT** create a public GitHub issue
- Email: security@[your-domain].com (if available)
- Or create a private security advisory on GitHub

---

**Last Updated**: 2025-10-17
**Security Standard**: OAuth 2.0 Best Practices + MCP Specification 2025-03-26
