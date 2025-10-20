# HuggingFace MCP Server Setup

## Configuration

The HuggingFace MCP server has been configured for use in the **full** profile.

### Current Configuration

**Location**: `~/.config/claude-code/mcp-servers-full.json`

```json
"hf-mcp-server": {
  "type": "http",
  "url": "https://huggingface.co/mcp?login",
  "description": "Hugging Face Hub - Models, datasets, spaces, and papers"
}
```

### Setup Instructions

The HuggingFace MCP server was added using the official configuration:

```bash
claude mcp add hf-mcp-server -t http "https://huggingface.co/mcp?login"
```

After adding, you need to:
1. Restart Claude Code
2. Follow the OAuth login flow when prompted
3. The server will then connect automatically

### Features

The HuggingFace MCP server provides access to:
- **Models**: Browse and search Hugging Face models
- **Datasets**: Access and explore datasets
- **Spaces**: Interact with Hugging Face Spaces
- **Papers**: Search research papers

### Usage with MCP Profile Switcher

The `hf-mcp-server` is included in the **full** profile (~85K tokens) and excluded from the **dev** and **ui** profiles to conserve context tokens.

```bash
# Switch to full profile to access HuggingFace
mcp-profile full

# Restart Claude Code
# The hf-mcp-server will now be available

# Switch back to dev profile when not needed
mcp-profile dev
```

### Troubleshooting

**Connection Issues:**
- Ensure you've completed the OAuth authentication flow
- Try removing and re-adding the server:
  ```bash
  claude mcp remove hf-mcp-server
  claude mcp add hf-mcp-server -t http "https://huggingface.co/mcp?login"
  ```
- Restart Claude Code after any configuration changes

**Token Usage:**
- The HuggingFace server contributes to the ~85K token usage in the full profile
- Use `mcp-profile dev` or `mcp-profile ui` when you don't need HuggingFace features

### References

- Official setup: https://huggingface.co/settings/mcp
- HuggingFace MCP docs: https://huggingface.co/docs/hub/en/hf-mcp-server

---

**Last Updated**: 2025-10-20
**Status**: Active in full profile
