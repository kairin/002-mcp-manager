# 🚨 Outstanding Issues & Resolution Guide

**Date**: 2025-10-17
**Status**: Code Fixed ✅ | User Actions Required ⏳

---

## Summary

Your MCP Manager implementation had **security vulnerabilities** and **configuration issues** that have now been fixed in the code. However, you need to take immediate action to:

1. Migrate configurations to secure pattern
2. Revoke exposed API keys
3. Fix Gemini CLI MCP server connectivity

---

## 🔐 Issue #1: API Keys Exposed in Configuration Files

### Problem
Both Claude Code and Gemini CLI configurations contained **hardcoded API tokens**:

**Claude Code (`~/.claude.json`)**:
- Context7: `ctx7sk-YourContext7KeyHere` ❌
- GitHub: `gho_YourGitHubTokenHere` ❌
- Hugging Face: `hf_YourHuggingFaceTokenHere` ❌

**Gemini CLI (`~/.gemini/settings.json`)**:
- Context7: `ctx7sk-YourContext7KeyHere` ❌ (same key!)
- Hugging Face: Uses `$HF_TOKEN` ⚠️ (wrong syntax, should be `${HUGGINGFACE_TOKEN}`)

### Solution Implemented ✅
- Updated `mcp_installer.py` to use environment variable references
- Updated `hf_integration.py` for secure token handling
- Added `.claude.json` and Gemini configs to `.gitignore`
- Created migration scripts for both Claude and Gemini

### Your Action Required ⏳

#### Step 1: Run Migration Scripts

**For Claude Code**:
```bash
cd ~/Apps/mcp-manager
uv run python scripts/security/migrate-to-env-vars.py
```

**For Gemini CLI**:
```bash
cd ~/Apps/mcp-manager
uv run python scripts/security/migrate-gemini-to-env-vars.py
```

#### Step 2: Revoke Exposed API Keys

⚠️ **CRITICAL**: These keys were exposed in configuration files:

**Context7**: https://context7.com/settings
1. Login to your account
2. Navigate to API Keys
3. Find key: `ctx7sk-YourContext7KeyHere`
4. Click "Revoke" or "Delete"
5. Generate new key
6. Update `.env`: `CONTEXT7_API_KEY=new_key_here`

**GitHub**: https://github.com/settings/tokens
1. Go to Personal Access Tokens
2. Find token: `gho_OsDEAm1J...`
3. Click "Delete"
4. Generate new token (scopes: `repo`, `workflow`, `admin:org`)
5. Update `.env`: `GITHUB_PERSONAL_ACCESS_TOKEN=new_token_here`

**Hugging Face**: https://huggingface.co/settings/tokens
1. Go to Access Tokens
2. Find token: `hf_zJIJiIho...`
3. Click "Delete token"
4. Create new token
5. Update `.env`: `HUGGINGFACE_TOKEN=new_token_here`

#### Step 3: Load Environment Variables
```bash
# Source the .env file
source .env

# Or add to ~/.bashrc for automatic loading
cat >> ~/.bashrc << 'EOF'
# MCP Manager environment variables
if [ -f ~/Apps/mcp-manager/.env ]; then
    source ~/Apps/mcp-manager/.env
fi
EOF
source ~/.bashrc
```

#### Step 4: Verify Configuration
```bash
# Claude Code
claude mcp list  # All 6 servers should be connected

# Gemini CLI
gemini mcp list  # Check if all servers connect now
```

---

## ❌ Issue #2: Gemini CLI - Hugging Face MCP Disconnected

### Problem
```
gemini mcp list
✓ context7 - Connected
✗ huggingface - Disconnected  ← THIS ONE
✓ playwright - Connected
✓ shadcn - Connected
✓ markitdown - Connected
✓ github - Connected
```

### Root Causes
1. **Wrong environment variable syntax**: Uses `$HF_TOKEN` instead of `${HUGGINGFACE_TOKEN}`
2. **Environment variable not set**: `$HF_TOKEN` or `$HUGGINGFACE_TOKEN` might not be exported
3. **Configuration mismatch**: Gemini config format differs from Claude format

### Solution Implemented ✅
- Created `migrate-gemini-to-env-vars.py` script
- Standardizes to `${HUGGINGFACE_TOKEN}` syntax
- Converts Gemini's custom format to standard MCP format

### Your Action Required ⏳

#### Run Gemini Migration Script:
```bash
cd ~/Apps/mcp-manager
uv run python scripts/security/migrate-gemini-to-env-vars.py
```

This will:
- ✅ Backup your Gemini configs
- ✅ Fix the `$HF_TOKEN` → `${HUGGINGFACE_TOKEN}` syntax
- ✅ Standardize Context7 configuration
- ✅ Update `.env` with extracted tokens

#### Verify Fix:
```bash
# Ensure environment variable is set
source .env
echo $HUGGINGFACE_TOKEN  # Should show your token

# Test Gemini MCP servers
gemini mcp list  # huggingface should now show ✓ Connected
```

---

## ⚠️ Issue #3: Import Error in CLI

### Problem
```
ImportError: cannot import name 'InvalidPathError' from 'mcp_manager.exceptions'
```

### Solution Implemented ✅
- Added `InvalidPathError` exception class to `exceptions.py`
- Added `UpdateCheckError` exception class to `exceptions.py`
- CLI commands should now work without import errors

### Your Action Required ⏳
None - this is already fixed in the code. Just verify CLI works:
```bash
uv run python -m mcp_manager.cli --help  # Should work now
```

---

## 📋 Complete Action Checklist

### Immediate Actions (Do First):
- [ ] Run Claude migration script: `uv run python scripts/security/migrate-to-env-vars.py`
- [ ] Run Gemini migration script: `uv run python scripts/security/migrate-gemini-to-env-vars.py`
- [ ] **Revoke exposed Context7 API key** (highest priority)
- [ ] **Revoke exposed GitHub token** (highest priority)
- [ ] **Revoke exposed Hugging Face token** (highest priority)

### Configuration Updates:
- [ ] Generate new Context7 API key
- [ ] Generate new GitHub personal access token
- [ ] Generate new Hugging Face token
- [ ] Update `.env` file with all new tokens
- [ ] Set secure file permissions: `chmod 600 .env`

### Verification:
- [ ] Source environment variables: `source .env`
- [ ] Verify Claude MCP servers: `claude mcp list` (all 6 should be ✓)
- [ ] Verify Gemini MCP servers: `gemini mcp list` (all should be ✓)
- [ ] Test Context7 connection
- [ ] Test Hugging Face connection
- [ ] Test GitHub connection

### Security Hygiene:
- [ ] Verify `.claude.json` is in `.gitignore`
- [ ] Verify `.gemini/` is in `.gitignore`
- [ ] Verify `.env` is in `.gitignore`
- [ ] Check git history for accidentally committed secrets
- [ ] Run: `git log --all -S "ctx7sk-" --source --all` (should be empty)

---

## 🎯 Quick Fix Commands

### One-Line Migration:
```bash
cd ~/Apps/mcp-manager && \
uv run python scripts/security/migrate-to-env-vars.py && \
uv run python scripts/security/migrate-gemini-to-env-vars.py && \
source .env && \
echo "✅ Migration complete! Now revoke old API keys and update .env"
```

### Verify Everything Works:
```bash
# Load environment variables
source ~/Apps/mcp-manager/.env

# Test both CLIs
claude mcp list && echo "\n---\n" && gemini mcp list
```

---

## 📚 Reference Documentation

- **Security Guide**: `docs/SECURITY.md`
- **Claude Migration**: `SECURITY-FIX-SUMMARY.md`
- **Environment Template**: `.env.example`
- **Gemini Migration Script**: `scripts/security/migrate-gemini-to-env-vars.py`
- **Claude Migration Script**: `scripts/security/migrate-to-env-vars.py`

---

## 🆘 If You Need Help

### Hugging Face Still Disconnected?
```bash
# Check if token is set
echo $HUGGINGFACE_TOKEN | head -c 10

# Manually test Hugging Face API
curl -H "Authorization: Bearer $HUGGINGFACE_TOKEN" https://huggingface.co/api/whoami

# Re-run Gemini migration
uv run python scripts/security/migrate-gemini-to-env-vars.py --force
```

### Claude MCP Servers Not Working?
```bash
# Check configuration format
cat ~/.claude.json | jq '.mcpServers.context7.headers'
# Should show: {"CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"}

# Re-run Claude migration
uv run python scripts/security/migrate-to-env-vars.py
```

### Environment Variables Not Loading?
```bash
# Check if .env exists and has correct permissions
ls -la ~/Apps/mcp-manager/.env

# Manually source
source ~/Apps/mcp-manager/.env

# Add to shell profile (permanent fix)
echo 'source ~/Apps/mcp-manager/.env' >> ~/.bashrc
source ~/.bashrc
```

---

## ✅ Success Criteria

When everything is fixed, you should see:

**Claude Code**:
```
$ claude mcp list
✓ context7 - Connected
✓ github - Connected
✓ hf-mcp-server - Connected
✓ shadcn - Connected
✓ playwright - Connected
✓ markitdown - Connected
```

**Gemini CLI**:
```
$ gemini mcp list
✓ context7 - Connected
✓ huggingface - Connected
✓ playwright - Connected
✓ shadcn - Connected
✓ markitdown - Connected
✓ github - Connected
```

**Security**:
- Old API keys revoked ✓
- New API keys in `.env` file ✓
- Configuration files use `${VAR}` syntax ✓
- No secrets in git history ✓

---

**Last Updated**: 2025-10-17
**Priority**: 🔴 **CRITICAL** - Complete immediately to secure your credentials
