# Context7 MCP Server Setup Guide

## Overview

Context7 is an MCP server that provides up-to-date documentation for libraries and frameworks. This guide shows how to securely configure it with the MCP Profile Switcher.

## What is Context7?

Context7 provides Claude with access to current library documentation through two key tools:
- `resolve-library-id`: Find the Context7 library ID from a package name
- `get-library-docs`: Fetch documentation for a specific library

## Secure Setup

### Step 1: Get Your API Key

1. Visit https://context7.com
2. Sign up for an account
3. Generate an API key from your dashboard
4. Copy the key (format: `ctx7sk-xxxxx...`)

### Step 2: Add Environment Variable

**IMPORTANT:** Never hardcode API keys in config files!

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Context7 MCP API Key
export CONTEXT7_API_KEY='your-actual-api-key-here'
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Step 3: Verify Environment Variable

```bash
# Should show your key (first 10 chars only for security)
echo "CONTEXT7_API_KEY=${CONTEXT7_API_KEY:0:10}..."
```

### Step 4: Profile Files Use Environment Variable

The profile files already use the secure environment variable syntax:

**~/.config/claude-code/profiles/dev.json**:
```json
{
  "context7": {
    "type": "http",
    "url": "https://mcp.context7.com/mcp",
    "headers": {
      "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
    }
  },
  "github": { ... },
  "markitdown": { ... }
}
```

The `${CONTEXT7_API_KEY}` syntax tells Claude Code to:
1. Look for an environment variable named `CONTEXT7_API_KEY`
2. Expand it to the actual value at runtime
3. Include it in the HTTP headers

### Step 5: Switch to a Profile with Context7

```bash
# Context7 is available in all profiles
mcp-profile dev   # or ui, or full
```

### Step 6: Restart Claude Code

```bash
# Exit current session (Ctrl+D or type 'exit')
# Start new session
claude
```

### Step 7: Verify Context7 is Working

In Claude Code, check MCP servers:
```
/mcp
```

You should see `context7` listed with authentication successful.

## Usage Examples

Once configured, you can ask Claude to use Context7:

```
"Get the latest Next.js documentation about server components"
"Find React hooks documentation"
"Show me how to use Supabase authentication"
```

Claude will:
1. Use `resolve-library-id` to find the library
2. Use `get-library-docs` to fetch current documentation
3. Answer based on up-to-date information

## Security Best Practices

### ✅ DO:
- Store API keys in environment variables
- Use `${VAR_NAME}` syntax in configs
- Add sensitive files to `.gitignore`
- Rotate keys regularly
- Keep shell profile files secure (`chmod 600 ~/.zshrc`)

### ❌ DON'T:
- Hardcode API keys in JSON files
- Commit keys to git
- Share keys in documentation
- Use the same key across multiple services
- Leave keys in command history

## Profiles with Context7

Context7 is now included in all profiles:

- **dev** (~8K tokens) - github, markitdown, **context7**
- **ui** (~13K tokens) - github, markitdown, playwright, shadcn, shadcn-ui, **context7**
- **full** (~86K tokens) - all 7 servers including **context7**

The small context overhead (~1K tokens) is worth having documentation access across all profiles.

## Troubleshooting

### "Authentication failed" error

1. Verify environment variable is set:
   ```bash
   echo $CONTEXT7_API_KEY
   ```

2. Reload shell profile:
   ```bash
   source ~/.zshrc
   ```

3. Restart Claude Code (must be a fresh session)

### "Failed to reconnect to context7"

This can happen if:
- SSE connection timed out (normal, will retry)
- API key expired (generate new key)
- Network issues (check internet connection)

### Environment variable not expanding

Make sure you're using:
- Correct syntax: `"${CONTEXT7_API_KEY}"` (with quotes and braces)
- Claude Code v1.0.18 or later (supports variable expansion)

### Key visible in config files

If you see the actual key (not `${CONTEXT7_API_KEY}`) in:
- `~/.claude.json`
- `~/.config/claude-code/profiles/*.json`

You have a security issue! Run:
```bash
# Replace hardcoded key with environment variable reference
# In all profile files and ~/.claude.json
```

## Rotating API Keys

To change your Context7 API key:

1. Generate new key from Context7 dashboard
2. Update environment variable in shell profile:
   ```bash
   export CONTEXT7_API_KEY='new-api-key-here'
   ```
3. Reload shell: `source ~/.zshrc`
4. Restart Claude Code

No need to modify any config files - they already use the environment variable!

## Why This Approach?

**Single Source of Truth:**
- API key stored in ONE place (environment variable)
- All configs reference the variable
- Change once, updates everywhere

**Git Safety:**
- Profile files contain `${CONTEXT7_API_KEY}` (safe to commit)
- Actual key never appears in git-tracked files
- Repository remains secure

**Compliance:**
- Follows AGENTS.md security requirements
- Passes security scans
- No secrets in version control

## See Also

- [GitHub MCP Setup](github-mcp-setup.md)
- [HuggingFace MCP Setup](hf-mcp-setup.md)
- [Profile Customization Guide](../README.md#customizing-profiles)
- [Security Best Practices](../README.md#security-api-keys-and-secrets)

## Support

- Context7 Documentation: https://docs.context7.com
- MCP Profile Switcher Issues: https://github.com/kairin/002-mcp-manager/issues
- Claude Code Documentation: https://docs.claude.com/en/docs/claude-code/mcp
