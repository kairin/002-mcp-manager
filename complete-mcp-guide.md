# Complete MCP Global Configuration Management Guide

## 📋 Table of Contents
1. [Problem Statement](#problem-statement)
2. [Solution Overview](#solution-overview)
3. [The MCP Global Manager Tool](#the-mcp-global-manager-tool)
4. [Implementation Methods](#implementation-methods)
5. [GitHub Repository Setup](#github-repository-setup)
6. [Usage Instructions](#usage-instructions)
7. [LLM Integration Guide](#llm-integration-guide)
8. [Success Verification](#success-verification)
9. [Troubleshooting](#troubleshooting)
10. [Reference Commands](#reference-commands)

---

## Problem Statement

The goal is to ensure that:
- ✅ All apps created in the home directory can access ALL installed MCP servers
- ✅ All MCP servers are installed in a global configuration
- ✅ Any Claude Code instances in any project location can access the same MCP servers
- ✅ No project-specific MCP configurations override global settings
- ✅ MCP servers consistently verify as connected and functional

### Initial Situation
- Multiple projects had their own MCP server configurations
- Some MCP servers were only available in specific projects
- Inconsistent access to MCP servers across different directories
- The Hugging Face MCP server was configured locally instead of globally

---

## Solution Overview

A Python-based tool that:
1. **Audits** all MCP configurations (global and project-specific)
2. **Migrates** local configurations to global
3. **Verifies** MCP server health
4. **Cleans** orphaned configurations
5. **Manages** addition of new MCP servers globally

---

## The MCP Global Manager Tool

### Core Features
- **Comprehensive Audit**: Scans all configurations and identifies issues
- **Automatic Migration**: Moves all local configs to global
- **Health Verification**: Tests connectivity for all MCP servers
- **Clean Management**: Removes duplicate and orphaned configurations
- **Preserves Authentication**: Maintains API keys and tokens during migration

### Required MCP Servers
The tool ensures these 5 servers are globally configured:

| Server | Type | Purpose | Authentication |
|--------|------|---------|----------------|
| context7 | HTTP | Documentation & library resolution | X-API-Key required |
| shadcn | stdio | UI component tooling | None |
| github | HTTP | GitHub API integration | None |
| playwright | stdio | Browser automation | None |
| hf-mcp-server | HTTP | Hugging Face integration | Bearer token required |

### Python Script Structure
```python
class MCPGlobalManager:
    - audit_configurations()    # Check all configs
    - verify_mcp_health()       # Test server connectivity
    - migrate_to_global()       # Move local to global
    - add_mcp_server()          # Add new servers
    - clean_orphaned_configs()  # Remove duplicates
    - generate_report()         # Create status report
    - run_full_setup()          # Execute complete setup
```

---

## Implementation Methods

### Method 1: Quick Local Setup

```bash
# 1. Create the script file
cd ~
mkdir -p tools/mcp-manager
cd tools/mcp-manager

# 2. Create the Python script (copy from artifact #1)
cat > mcp_global_manager.py << 'EOF'
[INSERT FULL SCRIPT FROM ARTIFACT #1]
EOF

# 3. Make executable and run
chmod +x mcp_global_manager.py
python3 mcp_global_manager.py full
```

### Method 2: Direct Download (if hosted)

```bash
# One-line setup
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/mcp-global-manager/main/mcp_global_manager.py
python3 mcp_global_manager.py full
```

### Method 3: GitHub Repository (Recommended)

See [GitHub Repository Setup](#github-repository-setup) section below.

---

## GitHub Repository Setup

### Step 1: Create Repository Structure

```bash
# Run this script to create complete repo structure
#!/bin/bash

REPO_NAME="mcp-global-manager"
mkdir -p $REPO_NAME
cd $REPO_NAME

# Initialize git
git init

# Create all necessary files:
# - mcp_global_manager.py (main script)
# - README.md (documentation)
# - requirements.txt (no external deps)
# - LICENSE (MIT)
# - .gitignore
# - LLM_INSTRUCTIONS.md (for AI agents)
# - test_mcp.py (validation script)
# - examples/claude.json.example

# [Use the setup script from artifact #3]
```

### Step 2: Push to GitHub

```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/mcp-global-manager.git
git branch -M main
git push -u origin main
```

### Step 3: Make It LLM-Accessible

Update README with:
- Clear installation instructions
- Success criteria
- JSON output examples
- Integration code samples

---

## Usage Instructions

### Basic Commands

```bash
# Full setup (recommended first run)
python3 mcp_global_manager.py full

# Individual operations
python3 mcp_global_manager.py audit    # Check configurations
python3 mcp_global_manager.py verify   # Test server health
python3 mcp_global_manager.py migrate  # Move local to global
python3 mcp_global_manager.py clean    # Remove orphaned configs

# Add new MCP server
python3 mcp_global_manager.py add \
  --name "custom-server" \
  --type http \
  --url "https://example.com/mcp" \
  --headers '{"Authorization": "Bearer TOKEN"}'
```

### Adding Hugging Face MCP Server

```bash
# With OAuth (follow prompts)
claude mcp add hf-mcp-server -t http https://huggingface.co/mcp?login

# With HF Token (direct)
claude mcp add hf-mcp-server \
  -t http https://huggingface.co/mcp \
  -H "Authorization: Bearer YOUR_HF_TOKEN"

# Then migrate to global
python3 mcp_global_manager.py migrate
```

### Verification Commands

```bash
# Check MCP server status
claude mcp list

# Test from different directories
cd ~/Apps && claude mcp list
cd ~/Desktop && claude mcp list

# Get detailed audit
python3 mcp_global_manager.py audit | jq '.'
```

---

## LLM Integration Guide

### For Claude Code Agents (Haiku/Sonnet)

#### Task Template for LLMs
```markdown
Task: Ensure all MCP servers are globally configured
Repository: https://github.com/YOUR_USERNAME/mcp-global-manager

Steps:
1. Download the MCP manager tool
2. Run full setup: `python3 mcp_global_manager.py full`
3. Verify all servers show "Connected"
4. Report any issues found

Success Criteria:
- [ ] 5 MCP servers configured globally
- [ ] All servers report "Connected" status
- [ ] No project-specific configurations remain
- [ ] Same MCP list from any directory
```

#### Python Integration Code for LLMs

```python
import subprocess
import json
import sys

def ensure_mcp_global_configuration():
    """Ensure all MCP servers are globally configured"""
    
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
    
    # Check if action needed
    if audit["issues"] or len(audit["global"]) < 5:
        # Run full setup
        subprocess.run(["python3", "mcp_manager.py", "full"])
        
        # Verify success
        verify = subprocess.run(
            ["python3", "mcp_manager.py", "verify"],
            capture_output=True,
            text=True
        )
        health = json.loads(verify.stdout)
        
        if health["all_healthy"]:
            return "✅ Configuration complete - all servers healthy"
        else:
            return f"⚠️ Configuration updated but some servers unhealthy: {health['servers']}"
    
    return "✅ Configuration already optimal"

# Execute
result = ensure_mcp_global_configuration()
print(result)
```

### Prompt for Any LLM

```
I need you to ensure all my MCP servers are globally configured for Claude Code.
Use the tool from https://github.com/YOUR_USERNAME/mcp-global-manager

Requirements:
1. All projects in my home directory should access the same MCP servers
2. These servers must be available: context7, shadcn, github, playwright, hf-mcp-server
3. No project-specific configurations should remain
4. All servers must verify as connected

Please:
1. Download the tool
2. Run the full setup
3. Verify all servers are healthy
4. Report the results with specific status for each server
```

---

## Success Verification

### Expected Successful Output

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

### Verification Checklist

```bash
# 1. Check global configuration exists
cat ~/.claude.json | jq '.mcpServers | keys'
# Expected: ["context7", "github", "hf-mcp-server", "playwright", "shadcn"]

# 2. Verify no project-specific configs
cat ~/.claude.json | jq '.projects[].mcpServers'
# Expected: {} or null for all projects

# 3. Test from multiple directories
for dir in ~ ~/Apps ~/Desktop; do
  echo "Testing from $dir:"
  cd $dir && claude mcp list | grep "Connected" | wc -l
done
# Expected: 5 connected servers from each directory

# 4. No local .mcp.json files
find ~ -name ".mcp.json" 2>/dev/null
# Expected: No results
```

---

## Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Claude configuration file not found" | Claude Code not initialized | Run `claude` once to create config |
| "Server shows Failed status" | Missing/invalid authentication | Check API keys and tokens |
| "Different servers in different directories" | Project-specific configs remain | Run `python3 mcp_global_manager.py migrate` |
| "Permission denied" | Incorrect file permissions | `chmod 644 ~/.claude.json` |
| "hf-mcp-server not showing" | Added locally not globally | Run full migration |

### Debug Commands

```bash
# Get detailed configuration
cat ~/.claude.json | jq '.'

# Check specific project configs
cat ~/.claude.json | jq '.projects["PROJECT_PATH"].mcpServers'

# Test specific server
claude mcp test context7

# Get verbose output
python3 mcp_global_manager.py audit > debug.json
cat debug.json | jq '.issues'

# Manual cleanup if needed
cat ~/.claude.json | jq 'del(.projects[].mcpServers) | .mcpServers = .mcpServers' > ~/.claude.json.new
mv ~/.claude.json.new ~/.claude.json
```

---

## Reference Commands

### Complete Workflow

```bash
# 1. Initial audit
python3 mcp_global_manager.py audit

# 2. Full setup if issues found
python3 mcp_global_manager.py full

# 3. Verify success
claude mcp list

# 4. Test from project directory
cd ~/my-project && claude mcp list

# 5. Generate report
python3 mcp_global_manager.py full > ~/mcp_report.txt
```

### Adding Custom MCP Servers

```bash
# HTTP server with authentication
python3 mcp_global_manager.py add \
  --name "my-api" \
  --type http \
  --url "https://api.example.com/mcp" \
  --headers '{"X-API-Key": "secret-key"}'

# Stdio server with command
python3 mcp_global_manager.py add \
  --name "my-tool" \
  --type stdio \
  --command "npx" \
  --args "my-tool@latest" "serve"
```

### Configuration Backup

```bash
# Backup before changes
cp ~/.claude.json ~/.claude.json.backup

# Restore if needed
cp ~/.claude.json.backup ~/.claude.json
```

---

## Summary

This complete guide provides:

1. **A Python tool** that manages MCP server configurations
2. **Multiple implementation methods** for different use cases
3. **GitHub repository structure** for LLM reference
4. **Clear success criteria** for verification
5. **Troubleshooting guide** for common issues
6. **LLM integration code** for automation

The end goal is achieved when:
- ✅ All 5 MCP servers are globally configured
- ✅ No project-specific configurations exist
- ✅ All servers verify as connected
- ✅ Any project in the home directory can access all MCP servers
- ✅ The configuration is consistent across all locations

This solution ensures that Claude Code agents (Haiku or otherwise) can reliably access all MCP servers from any project location, providing consistent functionality across the entire development environment.