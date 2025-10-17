# System-Wide MCP Setup - Next Steps

## ✅ Completed So Far

1. **Setup script executed** - Added MCP configuration templates to `~/.profile` and `~/.bashrc`
2. **GitHub token added** - Automatically retrieved and added to `~/.profile`
3. **Configuration files ready** - Claude Code and Gemini CLI configs use environment variable references

## 🔧 Action Required: Add Your API Keys

### Step 1: Edit ~/.profile

Open your profile file:
```bash
nano ~/.profile
```

Find this section (around line 80-95):
```bash
# TODO: Add your Context7 API key here
export CONTEXT7_API_KEY="your-context7-key-here"

# TODO: Add your Hugging Face token here
export HUGGINGFACE_TOKEN="your-huggingface-token-here"

# GitHub token (automatically retrieved)
export GITHUB_PERSONAL_ACCESS_TOKEN="gho_YourGitHubTokenHere"
```

**Replace the placeholder values with your actual new API keys:**

1. **Context7**: Get from https://context7.com/settings
   - Replace `"your-context7-key-here"` with your actual Context7 API key
   - Format: `ctx7sk-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

2. **Hugging Face**: Get from https://huggingface.co/settings/tokens
   - Replace `"your-huggingface-token-here"` with your actual HF token
   - Format: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`

Save and exit (Ctrl+O, Enter, Ctrl+X in nano)

### Step 2: Load Environment Variables

```bash
source ~/.profile
source ~/.bashrc
```

### Step 3: Verify Environment Variables

```bash
# Should show first 20 characters of each key
echo "CONTEXT7_API_KEY: ${CONTEXT7_API_KEY:0:20}..."
echo "HUGGINGFACE_TOKEN: ${HUGGINGFACE_TOKEN:0:20}..."
echo "GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_PERSONAL_ACCESS_TOKEN:0:20}..."
```

Expected output:
```
CONTEXT7_API_KEY: ctx7sk-YourContext7KeyHere...
HUGGINGFACE_TOKEN: hf_YourHuggingFaceTokenHere...
GITHUB_PERSONAL_ACCESS_TOKEN: gho_YourGitHubTokenHere...
```

### Step 4: Test System-Wide Access

Test from any directory (e.g., `/tmp`):

```bash
cd /tmp

# Test Claude Code MCP servers
claude mcp list
# Expected: All 6 servers should show ✓ Connected

# Test Gemini CLI MCP servers
gemini mcp list
# Expected: All servers should connect (stdio servers will work immediately)
```

## 📊 Current Status

### Claude Code (~/.claude.json)
✅ Configuration updated to use environment variables
- context7: `${CONTEXT7_API_KEY}`
- hf-mcp-server: `Bearer ${HUGGINGFACE_TOKEN}`
- github: `Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}`

### Gemini CLI (~/.config/gemini/settings.json)
✅ Configuration updated to use environment variables
- context7: `$CONTEXT7_API_KEY`
- huggingface: `Bearer $HUGGINGFACE_TOKEN`
- github: Uses `gh auth token` inline

### Environment Variables (~/.profile)
- ✅ GITHUB_PERSONAL_ACCESS_TOKEN (auto-added)
- ⏳ CONTEXT7_API_KEY (needs your input)
- ⏳ HUGGINGFACE_TOKEN (needs your input)

## 🎯 Success Criteria

Once you've added your API keys and sourced the files, you should see:

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

## 📖 Reference Documentation

- **Architecture Overview**: `docs/SYSTEM-WIDE-MCP-SETUP.md`
- **Security Guide**: `docs/SECURITY.md`
- **Outstanding Issues**: `OUTSTANDING-ISSUES.md`

## 🆘 Troubleshooting

### Environment variables not loading?
```bash
# Check if they're in ~/.profile
grep "CONTEXT7_API_KEY" ~/.profile

# Manually source
source ~/.profile

# Verify they're set
env | grep -E "CONTEXT7|HUGGINGFACE|GITHUB_PERSONAL"
```

### Claude Code still showing disconnected?
```bash
# Verify config uses env var references (not actual keys)
cat ~/.claude.json | jq '.mcpServers.context7.headers'
# Should show: {"CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"}

# Restart Claude Code after sourcing environment
```

### Gemini CLI HTTP servers timeout?
This is a known issue with Gemini CLI HTTP/SSE servers. stdio servers should work fine. If HTTP servers remain disconnected after adding keys, this may be a Gemini CLI bug.

---

**Setup Script Run**: 2025-10-17 07:41
**Last Updated**: 2025-10-17 07:42
**Status**: Waiting for user to add Context7 and Hugging Face tokens
