# 🏢 Office Setup Guide - MCP Manager Complete System

> **Quick setup guide for cloning and deploying the complete MCP Manager system at your office**

## 🚀 One-Command Setup

When you arrive at the office, run this single command to get the complete system:

```bash
# Clone and setup everything
git clone https://github.com/kairin/mcp-manager.git ~/Apps/mcp-manager && \
cd ~/Apps/mcp-manager && \
uv venv .venv && \
source .venv/bin/activate && \
uv pip install -e . && \
python -m mcp_manager.cli init
```

## 📋 What This Gives You

### ✅ **Comprehensive System Access**

1. **🔧 MCP Server Management**
   - Global access to 5 critical MCP servers
   - Health monitoring and diagnostics
   - Configuration migration tools

2. **📋 Project Standardization**
   - 6 automated standards enforcement
   - Branch strategy: `YYYYMMDD-HHMMSS-type-description`
   - Astro.build + GitHub Pages automation
   - Zero-cost local CI/CD workflows

3. **🤖 Global Claude Agent Access**
   - **174 discovered agents** across your repositories
   - Including the **astro-deploy-specialist** for deployments
   - Department-wide agent orchestration
   - Quick access commands

4. **🌐 Fleet Management**
   - Ubuntu 25.04 consistency enforcement
   - Python 3.13 + uv standardization
   - Multi-node synchronization

## 🎯 Key Commands Available Immediately

### MCP Server Management
```bash
# Check all MCP servers
python -m mcp_manager.cli mcp status

# Audit configurations
python -m mcp_manager.cli mcp audit
```

### Project Standardization
```bash
# Check project compliance
python -m mcp_manager.cli project audit

# Fix specific standards
python -m mcp_manager.cli project fix astro_pages
python -m mcp_manager.cli project fix spec_kit
```

### Claude Agent Access
```bash
# Discover all available agents
python -m mcp_manager.cli agent discover

# Deploy astro specialist to current project
python -m mcp_manager.cli agent deploy astro-deploy-specialist

# Deploy entire engineering department
python -m mcp_manager.cli agent deploy-department engineering
```

### System Status
```bash
# Complete system overview
python -m mcp_manager.cli status
```

## 🔄 Deployment Workflow

When you need to deploy projects (like this one), use the integrated specialist:

```bash
# Deploy current project to GitHub Pages
python -m mcp_manager.cli agent deploy astro-deploy-specialist
```

The system will automatically:
- ✅ Build the Astro project with proper configuration
- ✅ Create .nojekyll for GitHub Pages compatibility
- ✅ Follow branch preservation strategy
- ✅ Push and deploy to GitHub Pages
- ✅ Verify successful deployment

## 🏗️ What's Already Configured

### Global Agent Directories
- `/home/kkk/Apps/claude-guardian-agents` - 52 Guardian Agents
- `/home/kkk/Apps/deep-research` - Research specialists
- `/home/kkk/Apps/DeepResearchAgent` - Advanced research tools
- `/home/kkk/.claude/agents` - Claude Code specialists (like astro-deploy-specialist)

### Project Standards Enforced
1. **Branch Strategy**: YYYYMMDD-HHMMSS-type-description naming
2. **Astro Pages**: Automatic .nojekyll generation for GitHub Pages
3. **Local CI/CD**: Zero-cost workflows before GitHub deployment
4. **UV Python**: Unified Python 3.13+ environment management
5. **Spec-Kit**: AGENTS.md + CLAUDE.md/GEMINI.md symlinks
6. **Design System**: shadcn/ui + Tailwind CSS consistency

### Fleet Management
- Ubuntu 25.04 compliance monitoring
- Python environment standardization
- Multi-node configuration synchronization
- Cost prevention for GitHub operations

## 🎯 Immediate Benefits

1. **🚀 Zero Setup Time**: Everything works immediately after clone
2. **🔧 Consistent Tooling**: Same tools across all environments
3. **💰 Cost Prevention**: Local CI/CD prevents GitHub billing
4. **🤖 AI Workflow**: 174 agents available for any task
5. **📊 Compliance**: Automatic project standardization
6. **🌐 Fleet Scale**: Manage multiple development environments

## 📚 Advanced Usage

### Creating New Projects
```bash
# Create new project with all standards
mkdir ~/Apps/new-project && cd ~/Apps/new-project
python -m mcp_manager.cli project fix spec_kit
python -m mcp_manager.cli project fix astro_pages
python -m mcp_manager.cli project fix uv_python
```

### Managing Multiple Environments
```bash
# Register office machine in fleet
python -m mcp_manager.cli fleet register office-machine 192.168.1.100

# Sync configurations across fleet
python -m mcp_manager.cli fleet sync

# Audit fleet compliance
python -m mcp_manager.cli fleet audit
```

## 🏁 Success Verification

After setup, you should see:
- ✅ 174 agents discovered and accessible
- ✅ 5 MCP servers healthy and globally accessible
- ✅ Local CI/CD workflows operational
- ✅ Project standards ready for enforcement
- ✅ Fleet management operational

This system ensures you have identical, powerful development capabilities wherever you work - home, office, or any new environment.