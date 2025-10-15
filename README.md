# 🤖 MCP Manager

<div align="center">
    <h3><em>Centralized MCP Server Management for Claude Code</em></h3>
</div>

<p align="center">
    <strong>A comprehensive tool for managing Model Context Protocol (MCP) servers globally across all Claude Code projects with automated configuration, monitoring, and maintenance capabilities.</strong>
</p>

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

MCP Manager is a **centralized management system** for Model Context Protocol (MCP) servers used by Claude Code. It automates the installation, configuration, and maintenance of MCP servers, ensuring consistent availability across all your projects while providing monitoring, auditing, and troubleshooting capabilities.

## ⚡ Get started

### 1. Install MCP Manager

```bash
# Clone the repository
git clone https://github.com/kairin/mcp-manager.git
cd mcp-manager

# Install using uv
uv pip install -e .

# Or install from PyPI (coming soon)
uv pip install mcp-manager
```

### 2. Initialize MCP configuration

```bash
# Audit current MCP setup
mcp-manager audit

# Initialize global configuration
mcp-manager init --global

# Add MCP servers
mcp-manager add context7 --type http --url https://mcp.context7.com/mcp --header "CONTEXT7_API_KEY: your_key"
mcp-manager add shadcn --type stdio --command "npx shadcn@latest mcp"
```

### 3. Monitor and maintain

```bash
# Check server health
mcp-manager status

# Update servers
mcp-manager update --all

# Troubleshoot issues
mcp-manager diagnose
```

## 🤖 Features

### MCP Server Management
- **Global Configuration**: Centralized MCP server setup for all Claude Code projects
- **Health Monitoring**: Real-time status checking and connectivity validation
- **Automated Updates**: Intelligent updating of MCP servers and dependencies
- **Configuration Audit**: Complete analysis of project-specific vs global configurations

### Integration Support
| MCP Server | Type | Support | Notes |
|------------|------|---------|-------|
| [Context7](https://context7.com) | HTTP | ✅ | Library documentation and code examples |
| [shadcn/ui](https://ui.shadcn.com) | stdio | ✅ | UI component registry and tooling |
| [GitHub Copilot MCP](https://github.com) | HTTP | ✅ | GitHub API integration |
| [Playwright MCP](https://playwright.dev) | stdio | ✅ | Browser automation testing |
| [Hugging Face MCP](https://huggingface.co) | HTTP | ✅ | AI model access and inference |

### Management Features
- **Conflict Resolution**: Automatic migration from project-specific to global configs
- **Backup & Recovery**: Configuration backup and rollback capabilities
- **Security Management**: Secure credential storage and rotation
- **Performance Monitoring**: Server response time and reliability tracking

## 🔧 Prerequisites

- **Python 3.13** (enforced via UV)
- **UV package manager** for Python dependency management
- **Claude Code CLI** installed and configured
- **Git** for repository management
- **Node.js 18+** (for stdio-based MCP servers)

## 🛡️ Project Health & Quality

This project uses **automated health checks** enforced on every commit via pre-commit hooks:

### Automated Audits
- **UV-First Policy**: Ensures all Python package management uses `uv` (not `pip`)
- **Dependency Health**: Checks for outdated Python and JavaScript dependencies
- **Repository Organization**: Validates clean root directory structure
- **MCP Config Validation**: Cross-platform compatibility checks for MCP server configurations

### Running Audits Manually
```bash
# Run all project health audits
./scripts/run_all_audits.sh

# Run individual audits
./scripts/audit/check_pip_usage.sh        # UV-first policy
./scripts/audit/check_outdated.sh         # Dependency health
./scripts/audit/find_root_files.sh        # Repository organization
./scripts/audit/check_mcp_configs.py      # MCP config validation
```

### Pre-Commit Integration
The project uses [pre-commit hooks](https://pre-commit.com/) to automatically run:
- Project health audits
- Code formatting (Black)
- Linting (Ruff)
- Type checking (mypy)
- File validation (trailing whitespace, YAML, JSON)

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

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

- **[Configuration Guide](docs/configuration.md)** - Detailed setup instructions
- **[Server Management](docs/servers.md)** - Adding and managing MCP servers
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[API Reference](docs/api.md)** - Python API documentation

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