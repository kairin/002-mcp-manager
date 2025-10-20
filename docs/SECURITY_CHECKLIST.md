# Security Checklist - MCP Profile Manager

## ✅ Security Verification Completed

**Date**: 2025-10-20
**Status**: SECURE ✓

## What Was Fixed

### Before (INSECURE ❌)
```json
{
  "context7": {
    "type": "http",
    "url": "https://mcp.context7.com/mcp",
    "headers": {
      "CONTEXT7_API_KEY": "ctx7sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    }
  }
}
```
**Problem:** API key hardcoded in config files → would be committed to git

### After (SECURE ✅)
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
**Solution:** API key stored in environment variable → config files safe to commit

## Files Updated

### 1. Shell Profile (`~/.zshrc`)
```bash
# Context7 MCP API Key
export CONTEXT7_API_KEY='ctx7sk-your-api-key-here'
```
**Location:** `~/.zshrc` (line appended)
**Purpose:** Store API key securely in environment
**Scope:** User-level, not committed to git

### 2. Profile Files (All Profiles)
Updated files:
- `~/.config/claude-code/profiles/dev.json` ✅
- `~/.config/claude-code/profiles/ui.json` ✅
- `~/.config/claude-code/profiles/full.json` ✅

**Change:** Added context7 server with `${CONTEXT7_API_KEY}` reference
**Safe to commit:** YES ✅

### 3. Main Config (`~/.claude.json`)
**Change:** Replaced hardcoded key with `${CONTEXT7_API_KEY}`
**Current project:** `/home/kkk/Apps/002-mcp-manager`
**Safe to commit:** NO (contains conversation history)
**Note:** This file is user-specific and shouldn't be in git anyway

## Verification Results

### ✅ Environment Variable Check
```bash
$ echo $CONTEXT7_API_KEY
ctx7sk-your-api-key-here
```
Status: **PASSED** ✓

### ✅ Profile Switching Check
```bash
$ mcp-profile dev
Active Profile: DEV
Servers (3): context7, github, markitdown

$ mcp-profile ui
Active Profile: UI
Servers (6): context7, github, markitdown, playwright, shadcn, shadcn-ui

$ mcp-profile full
Active Profile: FULL
Servers (7): context7, github, hf-mcp-server, markitdown, playwright, shadcn, shadcn-ui
```
Status: **PASSED** ✓ (context7 in all profiles)

### ✅ Security Scan
```bash
$ grep -r "ctx7sk-" ~/.config/claude-code/profiles/
(no results - only env var references found)
```
Status: **PASSED** ✓ (no hardcoded keys in config files)

### ✅ Environment Variable References
```bash
$ grep -r "\${CONTEXT7_API_KEY}" ~/.config/claude-code/profiles/ ~/.claude.json | wc -l
4
```
Status: **PASSED** ✓ (all configs use env var)

## Security Compliance

### AGENTS.md Requirements
- [✅] No API keys in version control
- [✅] No hardcoded secrets
- [✅] Environment variables for sensitive data
- [✅] Privacy-protected information only
- [✅] Security scan passes

### Git Safety
- [✅] Profile files safe to commit
- [✅] No secrets in tracked files
- [✅] `.gitignore` covers sensitive files
- [✅] Single source of truth (env var)

## Profile Configuration Summary

| Profile | Servers | Context | Includes Context7 |
|---------|---------|---------|-------------------|
| dev     | 3       | ~8K     | ✅ YES            |
| ui      | 6       | ~13K    | ✅ YES            |
| full    | 7       | ~86K    | ✅ YES            |

**Note:** Context7 adds ~1K token overhead per profile

## Quick Reference

### Check API Key is Set
```bash
echo "CONTEXT7_API_KEY=${CONTEXT7_API_KEY:0:10}..."
```

### Verify Config Uses Env Var
```bash
cat ~/.config/claude-code/profiles/dev.json | jq '.context7.headers'
# Should show: { "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}" }
```

### Switch Profiles
```bash
mcp-profile dev    # Minimal with context7
mcp-profile ui     # Design work with context7
mcp-profile full   # All servers with context7
```

### Restart Claude Code
```bash
# Exit current session (Ctrl+D)
claude
# Context7 should appear in /mcp listing
```

## Security Best Practices Applied

1. **Environment Variables** - API keys stored outside config files
2. **Variable Expansion** - `${VAR_NAME}` syntax for runtime resolution
3. **Single Source of Truth** - Key defined once, referenced everywhere
4. **Git Safety** - Config files contain references only, not actual keys
5. **Documentation** - Security approach documented for team

## Next Steps

### For New Team Members
1. Get Context7 API key from https://context7.com
2. Add to shell profile: `export CONTEXT7_API_KEY='your-key'`
3. Reload shell: `source ~/.zshrc`
4. Switch to desired profile: `mcp-profile dev`
5. Restart Claude Code

### For Key Rotation
1. Generate new key from Context7 dashboard
2. Update shell profile: `export CONTEXT7_API_KEY='new-key'`
3. Reload shell: `source ~/.zshrc`
4. Restart Claude Code (no config changes needed!)

## Documentation Links

- **Setup Guide**: [docs/context7-mcp-setup.md](context7-mcp-setup.md)
- **Security Section**: [README.md#security-api-keys-and-secrets](../README.md#security-api-keys-and-secrets)
- **GitHub MCP Setup**: [docs/github-mcp-setup.md](github-mcp-setup.md)

## Verification Command

Run this to verify your setup:
```bash
# 1. Check env var is set
[ -n "$CONTEXT7_API_KEY" ] && echo "✅ API key set" || echo "❌ API key missing"

# 2. Check config uses env var (not hardcoded key)
grep -q "\${CONTEXT7_API_KEY}" ~/.config/claude-code/profiles/dev.json && \
  echo "✅ Config secure" || echo "❌ Config has hardcoded key"

# 3. Test profile switching
mcp-profile status | grep -q "context7" && \
  echo "✅ Context7 available" || echo "❌ Context7 missing"
```

## Audit Trail

- **2025-10-20 10:05** - Environment variable setup completed
- **2025-10-20 10:05** - All profile files updated with env var
- **2025-10-20 10:05** - Main config updated with env var
- **2025-10-20 10:05** - Security documentation created
- **2025-10-20 10:05** - Profile switching verified
- **2025-10-20 10:05** - Security scan PASSED

## Maintainer Notes

**If you add a new MCP server requiring authentication:**

1. Add API key to `~/.zshrc`: `export NEW_SERVER_API_KEY='value'`
2. Use `${NEW_SERVER_API_KEY}` in profile JSON files
3. Document in `docs/new-server-mcp-setup.md`
4. Update README security section
5. Run security scan before committing
6. Never commit actual API keys!

---

**Security Status**: ✅ SECURE
**Last Audit**: 2025-10-20
**Auditor**: Claude Code (automated)
**Compliance**: AGENTS.md security requirements PASSED
