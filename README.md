# 🚀 MCP Manager - Complete System Management

<div align="center">
    <h3><em>Comprehensive Project Standardization & Fleet Management System</em></h3>
</div>

<p align="center">
    <strong>A unified management system for MCP servers, project standardization, Claude agents, and Ubuntu 25.04 fleet consistency with zero-cost local CI/CD workflows.</strong>
</p>

<div align="center">
    <img src="docs/images/homepage-hero.png" alt="MCP Manager Homepage" width="800">
    <p><em>Live at: <a href="https://kairin.github.io/mcp-manager/">https://kairin.github.io/mcp-manager/</a></em></p>
</div>

---

## Table of Contents

- [🤔 What is MCP Manager?](#-what-is-mcp-manager)
- [⚡ Get started](#-get-started)
- [🤖 Features](#-features)
- [🔧 Prerequisites](#-prerequisites)
- [📚 Core functionality](#-core-functionality)
- [🌟 Architecture](#-architecture)
- [📖 Learn more](#-learn-more)
- [🔍 Troubleshooting](#-troubleshooting)
- [👥 Maintainers](#-maintainers)
- [💬 Support](#-support)
- [📄 License](#-license)

## 🤔 What is MCP Manager?

MCP Manager is a **comprehensive system management platform** that unifies:

- **🔧 MCP Server Management**: Centralized Model Context Protocol servers for Claude Code
- **📋 Project Standardization**: 6 automated standards enforcement across all repositories
- **🤖 Global Claude Agent Access**: 174+ discovered agents including deployment specialists
- **🌐 Fleet Management**: Ubuntu 25.04 consistency across development environments
- **💰 Zero-Cost Operations**: Local CI/CD workflows preventing GitHub billing

It transforms your development workflow into a standardized, automated system that works identically across home, office, and any new environment.

## ⚡ Get started

### 🚀 One-Command Setup

When you arrive at any new environment, run this single command:

```bash
# Clone and setup everything
git clone https://github.com/kairin/mcp-manager.git ~/Apps/mcp-manager && \
cd ~/Apps/mcp-manager && \
uv venv .venv && \
source .venv/bin/activate && \
uv pip install -e . && \
python -m mcp_manager.cli init
```

### 🎯 Immediate Access

After setup, you'll have:

```bash
# Check comprehensive system status
python -m mcp_manager.cli status

# Verify 5 MCP servers (context7, shadcn, github, playwright, hf-mcp-server)
python -m mcp_manager.cli mcp status

# Access 174+ Claude agents including astro-deploy-specialist
python -m mcp_manager.cli agent discover

# Enforce project standards across repositories
python -m mcp_manager.cli project audit

# Deploy current project to GitHub Pages
python -m mcp_manager.cli agent deploy astro-deploy-specialist
```

### 🌐 Fleet Management

```bash
# Register office machine in fleet
python -m mcp_manager.cli fleet register office-machine 192.168.1.100

# Sync configurations across all environments
python -m mcp_manager.cli fleet sync

# Audit Ubuntu 25.04 + Python 3.13 compliance
python -m mcp_manager.cli fleet audit
```

## 🤖 System Components

<div align="center">
    <img src="docs/images/features-overview.png" alt="MCP Manager Features Overview" width="800">
    <p><em>Complete development environment standardization</em></p>
</div>

### 🔧 MCP Server Management (5 Critical Servers)
| Server | Type | Status | Purpose |
|--------|------|--------|---------|
| [Context7](https://context7.com) | HTTP | ✅ Global + Auth | Library documentation and code examples |
| [shadcn/ui](https://ui.shadcn.com) | stdio | ✅ Global | UI component registry and tooling |
| [GitHub MCP](https://github.com) | HTTP | ✅ Global | GitHub API integration and management |
| [Playwright MCP](https://playwright.dev) | stdio | ✅ Global | Browser automation and testing |
| [Hugging Face MCP](https://huggingface.co) | HTTP | ✅ Global + Auth | AI model access with HF CLI integration |

<div align="center">
    <img src="docs/images/mcp-servers.png" alt="Supported MCP Servers" width="800">
    <p><em>All major Model Context Protocol servers with comprehensive integration</em></p>
</div>

#### 🤗 Hugging Face MCP Setup
```bash
# Quick setup with HF CLI authentication
./hf_quick_setup.sh

# Or use MCP Manager CLI
uv run python -m mcp_manager.cli mcp setup-hf --login

# Setup all MCP servers at once
uv run python -m mcp_manager.cli mcp setup-all
```

### 📋 Project Standardization (6 Automated Standards)
1. **Branch Strategy**: YYYYMMDD-HHMMSS-type-description naming, preserve all branches
2. **Astro Pages**: Automatic .nojekyll generation for GitHub Pages compatibility
3. **Local CI/CD**: Zero-cost workflows executed before GitHub deployment
4. **UV Python**: Python 3.13+ environment management with modern tooling
5. **Spec-Kit**: AGENTS.md integration with CLAUDE.md/GEMINI.md symlinks
6. **Design System**: shadcn/ui + Tailwind CSS consistency

### 🤖 Claude Agent Management (174+ Agents)
- **Guardian Agents**: 52 agents from /home/kkk/Apps/claude-guardian-agents
- **Research Specialists**: Deep research and analysis agents
- **Deployment Specialists**: Including astro-deploy-specialist for GitHub Pages
- **Department Organization**: Engineering, research, security, and more
- **Global Access**: Available across all projects and environments

### 🌐 Fleet Management Features
- **Ubuntu 25.04 Compliance**: Consistent OS version across all nodes
- **Python 3.13 Standardization**: Unified development environment
- **Multi-Node Synchronization**: Configuration sync across environments
- **Cost Prevention**: Local-first workflows prevent GitHub billing overages

## 🔧 Prerequisites

- **Python 3.11+**
- **Claude Code CLI** installed and configured
- **Git** for repository management
- **Node.js 18+** (for stdio-based MCP servers)

## 📚 Core functionality

### Configuration Management
```python
from mcp_manager import MCPManager

# Initialize manager
manager = MCPManager()

# Add HTTP server
manager.add_server(
    name="context7",
    type="http",
    url="https://mcp.context7.com/mcp",
    headers={"CONTEXT7_API_KEY": "your_key"}
)

# Add stdio server
manager.add_server(
    name="shadcn",
    type="stdio",
    command="npx",
    args=["shadcn@latest", "mcp"]
)

# Apply global configuration
manager.apply_global()
```

### Health Monitoring
```python
# Check all servers
status = manager.check_health()

# Check specific server
server_status = manager.check_server("context7")

# Get performance metrics
metrics = manager.get_metrics()
```

## 🌟 Architecture

```
MCP Manager Architecture:
├── Configuration Management
│   ├── Global config storage (.claude.json)
│   ├── Project-specific migration
│   └── Backup and versioning
├── Server Management
│   ├── HTTP server handling
│   ├── stdio server management
│   └── Credential management
├── Monitoring & Health
│   ├── Connectivity testing
│   ├── Performance monitoring
│   └── Error detection
└── CLI Interface
    ├── Interactive commands
    ├── Automation scripts
    └── Integration tools
```

## 📖 Learn more

- **[🏢 Office Setup Guide](https://kairin.github.io/mcp-manager/office-setup/)** - Complete office deployment workflow
- **[Configuration Guide](docs/configuration.md)** - Detailed setup instructions
- **[Server Management](docs/servers.md)** - Adding and managing MCP servers
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[API Reference](docs/api.md)** - Python API documentation

<div align="center">
    <img src="docs/images/office-setup-guide.png" alt="Office Setup Guide" width="600">
    <p><em><a href="https://kairin.github.io/mcp-manager/office-setup/">🏢 Complete Office Setup Guide</a> - One-command deployment for office environments</em></p>
</div>

## 🔍 Troubleshooting

### Common Issues

**MCP servers not connecting:**
```bash
# Check server health
mcp-manager diagnose

# Verify Claude configuration
claude mcp list

# Reset configuration
mcp-manager reset --confirm
```

**Project-specific configurations:**
```bash
# Audit all configurations
mcp-manager audit --detailed

# Migrate to global
mcp-manager migrate --project-to-global
```

## 👥 Maintainers

- Mister K ([@kairin](https://github.com/kairin))

## 💬 Support

For support, please open a [GitHub issue](https://github.com/kairin/mcp-manager/issues/new). We welcome bug reports, feature requests, and questions about MCP server management.

## 📄 License

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) file for the full terms.