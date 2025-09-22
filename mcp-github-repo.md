# MCP Global Configuration Manager

A universal tool for managing MCP (Model Context Protocol) servers in Claude Code, ensuring all projects have consistent global access to MCP servers.

## 🚀 Quick Start

```bash
# Clone and run
git clone https://github.com/YOUR_USERNAME/mcp-global-manager.git
cd mcp-global-manager
python3 mcp_global_manager.py full
```

## 📋 Prerequisites

- Python 3.6+
- Claude Code installed
- Home directory with `.claude.json` configuration

## 🎯 Purpose

This tool solves the common problem of MCP servers being configured locally in individual projects rather than globally. It ensures:

- ✅ All MCP servers are globally accessible
- ✅ No duplicate configurations
- ✅ Consistent server access across all projects
- ✅ Proper authentication token preservation

## 🤖 LLM Integration Instructions

### For AI Assistants/Agents

When implementing this tool, follow these steps:

1. **Download the script**:
```bash
curl -o mcp_global_manager.py https://raw.githubusercontent.com/YOUR_USERNAME/mcp-global-manager/main/mcp_global_manager.py
```

2. **Run full setup**:
```bash
python3 mcp_global_manager.py full
```

3. **Verify success**:
```bash
claude mcp list
```

### Expected MCP Servers

The tool manages these default MCP servers:

| Server | Type | Purpose |
|--------|------|---------|
| context7 | HTTP | Documentation & library resolution |
| shadcn | stdio | UI component tooling |
| github | HTTP | GitHub API integration |
| playwright | stdio | Browser automation |
| hf-mcp-server | HTTP | Hugging Face integration |

## 📖 Commands

### Full Setup (Recommended)
```bash
python3 mcp_global_manager.py full
```
Runs complete audit, migration, cleanup, and verification.

### Individual Commands

```bash
# Audit current configuration
python3 mcp_global_manager.py audit

# Verify server health
python3 mcp_global_manager.py verify

# Migrate local configs to global
python3 mcp_global_manager.py migrate

# Clean orphaned configurations
python3 mcp_global_manager.py clean

# Add new MCP server
python3 mcp_global_manager.py add \
  --name "server-name" \
  --type http \
  --url "https://example.com/mcp" \
  --headers '{"Authorization": "Bearer TOKEN"}'
```

## 🔧 Configuration File Structure

The tool manages the `~/.claude.json` file with this structure:

```json
{
  "mcpServers": {
    "server-name": {
      "type": "http|stdio",
      "url": "https://...",
      "headers": {},
      "command": "...",
      "args": []
    }
  },
  "projects": {
    "/path/to/project": {
      "mcpServers": {}  // Should be empty after migration
    }
  }
}
```

## 🎓 For Claude Code Agents (Haiku/Sonnet)

### Task Template

```markdown
Task: Ensure all MCP servers are globally configured
Steps:
1. Download the MCP manager tool
2. Run full setup: `python3 mcp_global_manager.py full`
3. Verify all servers show "Connected"
4. Report any issues found
```

### Success Criteria

```python
# Check these conditions:
- [ ] All 5 default MCP servers configured globally
- [ ] No project-specific MCP configurations
- [ ] All servers report "Connected" status
- [ ] No local .mcp.json files found
- [ ] Configuration accessible from any directory
```

## 📊 Sample Output

```
==============================================================
MCP SERVER GLOBAL CONFIGURATION REPORT
==============================================================
Generated: 2024-12-19 10:30:00

📊 GLOBAL CONFIGURATION STATUS:
----------------------------------------
✅ 5 global MCP servers configured:
   • context7 (http)
   • github (http)
   • hf-mcp-server (http)
   • playwright (stdio)
   • shadcn (stdio)

🏥 HEALTH CHECK RESULTS:
----------------------------------------
   ✅ context7: Connected
   ✅ shadcn: Connected
   ✅ github: Connected
   ✅ playwright: Connected
   ✅ hf-mcp-server: Connected

📋 SUMMARY:
----------------------------------------
✅ ALL SYSTEMS OPERATIONAL
All MCP servers are globally configured and healthy.
All projects can access MCP servers from any location.
==============================================================
```

## 🐛 Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Claude configuration file not found" | Ensure Claude Code is installed and initialized |
| "Failed to connect to server" | Check API keys/tokens in configuration |
| "Permission denied" | Run with appropriate permissions or check file ownership |
| Server shows "Failed" status | Verify server URL and authentication credentials |

### Debug Mode

```bash
# Get detailed JSON output
python3 mcp_global_manager.py audit > audit.json
python3 mcp_global_manager.py verify > health.json
```

## 🔑 Environment Variables (Optional)

```bash
# Set custom home directory
export MCP_HOME_DIR="/custom/path"
python3 mcp_global_manager.py full --home-dir $MCP_HOME_DIR
```

## 📝 License

MIT License - Feel free to use, modify, and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 💬 LLM-Friendly Notes

This repository is designed to be easily understood and implemented by AI assistants. The code includes:

- Clear docstrings for all functions
- Type hints for better understanding
- Comprehensive error handling
- Self-documenting command structure
- JSON-based configuration management

### For AI Implementation

When an AI assistant encounters MCP server configuration issues, they can:

1. Reference this repository: `https://github.com/YOUR_USERNAME/mcp-global-manager`
2. Download and execute the tool
3. Parse the JSON/text output for analysis
4. Make decisions based on the audit results
5. Report status back to the user

### Integration Example

```python
# Example for AI agents
import subprocess
import json

def ensure_mcp_global_config():
    # Download tool
    subprocess.run([
        "curl", "-o", "mcp_manager.py",
        "https://raw.githubusercontent.com/YOUR_USERNAME/mcp-global-manager/main/mcp_global_manager.py"
    ])
    
    # Run audit
    result = subprocess.run(
        ["python3", "mcp_manager.py", "audit"],
        capture_output=True,
        text=True
    )
    
    audit = json.loads(result.stdout)
    
    # Check if migration needed
    if audit["projects"] or not audit["global"]:
        # Run full setup
        subprocess.run(["python3", "mcp_manager.py", "full"])
        return "Migration completed"
    
    return "Configuration already optimal"
```

## 📚 Additional Resources

- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [MCP Protocol Specification](https://modelcontextprotocol.org)
- [Claude API Reference](https://docs.claude.com/api)

---

**Repository maintained for AI-assisted development workflows**