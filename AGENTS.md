# MCP Manager - Claude Code Integration

> 🤖 **CRITICAL**: This file contains NON-NEGOTIABLE requirements that ALL AI assistants (Claude, Gemini, ChatGPT, etc.) working on this repository MUST follow at ALL times.

## 🎯 Project Overview

**MCP Manager** is a centralized management system for Model Context Protocol (MCP) servers used by Claude Code. It automates installation, configuration, and maintenance of MCP servers, ensuring consistent availability across all projects while providing monitoring, auditing, and troubleshooting capabilities.

**Repository**: https://github.com/kairin/mcp-manager
**Integration**: Prepared for [spec-kit](https://github.com/kairin/spec-kit) workflow

## ⚡ NON-NEGOTIABLE REQUIREMENTS

### 🚨 CRITICAL: Branch Management & Git Strategy (MANDATORY)

#### Branch Preservation (MANDATORY)
- **NEVER DELETE BRANCHES** without explicit user permission
- **ALL BRANCHES** contain valuable development history
- **NO** automatic cleanup with `git branch -d`
- **YES** to automatic merge to main branch, preserving dedicated branch

#### Branch Naming (MANDATORY SCHEMA)
**Format**: `YYYYMMDD-HHMMSS-type-short-description`

Examples:
- `20250923-143000-feat-mcp-server-manager`
- `20250923-143515-fix-configuration-audit`
- `20250923-144030-docs-api-reference`

#### GitHub Safety Strategy (MANDATORY)
```bash
# MANDATORY: Every commit must use this workflow
DATETIME=$(date +"%Y%m%d-%H%M%S")
BRANCH_NAME="${DATETIME}-feat-description"
git checkout -b "$BRANCH_NAME"
git add .
git commit -m "Descriptive commit message

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>"
git push -u origin "$BRANCH_NAME"
git checkout main
git merge "$BRANCH_NAME" --no-ff
git push origin main
# NEVER: git branch -d "$BRANCH_NAME"
```

### 🚨 CRITICAL: Python Development Standards (MANDATORY)

#### Python Version & Dependencies
- **Python 3.11+**: Minimum required version
- **Modern Type Hints**: Full type annotations required
- **Pydantic v2**: For configuration and data validation
- **Rich**: For CLI output and progress indicators
- **Typer**: For CLI interface with modern features

#### Code Quality (NON-NEGOTIABLE)
```bash
# MANDATORY: Code quality checks before every commit
black src/ tests/                    # Code formatting
ruff check src/ tests/               # Linting and imports
mypy src/                           # Type checking
pytest tests/ --cov=mcp_manager     # Testing with coverage >80%
```

#### Project Structure (MANDATORY)
```
mcp-manager/
├── src/mcp_manager/           # Main package
│   ├── __init__.py           # Package exports
│   ├── cli.py                # CLI interface
│   ├── core.py               # Core MCP management
│   ├── models.py             # Pydantic models
│   ├── exceptions.py         # Custom exceptions
│   ├── config.py             # Configuration management
│   ├── health.py             # Health monitoring
│   └── utils.py              # Utility functions
├── tests/                    # Test suite
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
├── pyproject.toml            # Project configuration
├── README.md                 # Project documentation
├── CLAUDE.md                 # This file - AI instructions
└── LICENSE                   # MIT License
```

### 🚨 CRITICAL: Spec-Kit Integration (MANDATORY)

#### Spec-Kit Workflow Commands
This project is prepared for [spec-kit](https://github.com/kairin/spec-kit) integration with the following workflow:

1. **`/constitution`** - Establish project principles
2. **`/specify`** - Define MCP management requirements
3. **`/plan`** - Create technical implementation plan
4. **`/tasks`** - Generate actionable task breakdown
5. **`/implement`** - Execute implementation

#### Constitutional Principles (MANDATORY)
- **Global Configuration First**: All MCP servers managed globally by default
- **Zero Downtime Operations**: Configuration changes must not break existing setups
- **Security by Design**: Secure credential storage and rotation
- **Performance Monitoring**: Health checks and performance tracking
- **User-Centric Design**: Intuitive CLI with helpful error messages

### 🚨 CRITICAL: MCP Server Management (MANDATORY)

#### Supported MCP Server Types
| Server | Type | Implementation | Priority |
|--------|------|----------------|----------|
| context7 | HTTP | ✅ Required | High |
| shadcn | stdio | ✅ Required | High |
| github | HTTP | ✅ Required | High |
| playwright | stdio | ✅ Required | High |
| hf-mcp-server | HTTP | ✅ Required | High |

#### Configuration Management (MANDATORY)
```python
# Global configuration structure (MANDATORY)
{
    "mcpServers": {
        "context7": {
            "type": "http",
            "url": "https://mcp.context7.com/mcp",
            "headers": {"CONTEXT7_API_KEY": "..."}
        },
        "shadcn": {
            "type": "stdio",
            "command": "npx",
            "args": ["shadcn@latest", "mcp"],
            "env": {}
        }
        # ... other servers
    }
}
```

#### Health Monitoring (MANDATORY)
- **Connectivity Tests**: Regular HTTP/stdio connectivity validation
- **Performance Metrics**: Response time and reliability tracking
- **Error Detection**: Automatic issue identification and reporting
- **Recovery Actions**: Automated recovery for common issues

## 🏗️ Development Standards

### CLI Interface (MANDATORY)
```bash
# Primary commands (REQUIRED)
mcp-manager audit              # Audit all MCP configurations
mcp-manager init --global      # Initialize global configuration
mcp-manager add <name> [opts]  # Add new MCP server
mcp-manager remove <name>      # Remove MCP server
mcp-manager status             # Check server health
mcp-manager update [--all]     # Update servers
mcp-manager diagnose          # Troubleshoot issues
mcp-manager migrate           # Migrate project configs to global

# Configuration commands
mcp-manager config show       # Show current configuration
mcp-manager config backup     # Create configuration backup
mcp-manager config restore    # Restore from backup

# Monitoring commands
mcp-manager monitor           # Real-time health monitoring
mcp-manager metrics           # Performance metrics
mcp-manager logs             # View operation logs
```

### Testing Requirements (MANDATORY)
- **Unit Tests**: >80% code coverage required
- **Integration Tests**: Real MCP server interaction tests
- **CLI Tests**: Command-line interface testing
- **Performance Tests**: Response time and resource usage
- **Error Handling**: Comprehensive error scenario testing

### Documentation (MANDATORY)
- **API Documentation**: Complete Python API reference
- **CLI Documentation**: Comprehensive command reference
- **Configuration Guide**: Setup and configuration instructions
- **Troubleshooting Guide**: Common issues and solutions
- **Contributing Guide**: Development setup and contribution process

## 🔧 Implementation Guidelines

### Error Handling (MANDATORY)
```python
# Custom exception hierarchy (REQUIRED)
class MCPManagerError(Exception):
    """Base exception for MCP Manager."""

class ServerNotFoundError(MCPManagerError):
    """Server not found in configuration."""

class ConfigurationError(MCPManagerError):
    """Invalid configuration detected."""

class ConnectivityError(MCPManagerError):
    """Unable to connect to MCP server."""
```

### Logging (MANDATORY)
```python
import logging
from rich.logging import RichHandler

# Rich-based logging configuration (REQUIRED)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
```

### Configuration Management (MANDATORY)
```python
from pathlib import Path
from pydantic import BaseModel
import json

class MCPServerConfig(BaseModel):
    """MCP server configuration model."""
    type: Literal["http", "stdio"]
    url: Optional[str] = None
    command: Optional[str] = None
    args: List[str] = []
    headers: Dict[str, str] = {}
    env: Dict[str, str] = {}

# Global configuration location (MANDATORY)
CLAUDE_CONFIG_PATH = Path.home() / ".claude.json"
```

## 🚨 ABSOLUTE PROHIBITIONS

### DO NOT
- Delete branches without explicit user permission
- Break existing MCP server configurations
- Store credentials in plain text without encryption
- Skip type annotations in new code
- Ignore test coverage requirements
- Bypass code quality checks (black, ruff, mypy)
- Commit without proper branch naming strategy
- Remove or modify global MCP configurations without backup

### DO NOT BYPASS
- Branch preservation requirements
- Code quality standards (black, ruff, mypy, pytest)
- Type annotation requirements
- Configuration backup before changes
- Health check validation
- Error handling requirements

## ✅ MANDATORY ACTIONS

### Before Every Commit
1. **Code Quality**: Run `black`, `ruff`, `mypy` checks
2. **Testing**: Execute `pytest` with >80% coverage
3. **Branch Creation**: Use datetime-based branch naming
4. **Configuration Backup**: Backup configs before changes
5. **Health Validation**: Verify MCP server connectivity
6. **Documentation**: Update relevant docs if adding features

### Quality Gates
- All tests pass with >80% coverage
- Type checking passes without errors
- Code formatting matches black standards
- Linting passes ruff validation
- MCP servers remain functional after changes
- Documentation is updated for new features

## 🎯 Success Criteria

### Functionality Metrics
- **Configuration Audit**: 100% accurate detection of project vs global configs
- **Migration Success**: >99% successful project-to-global migrations
- **Health Monitoring**: <5 second server health check completion
- **Error Recovery**: Automatic recovery for >90% of common issues

### Code Quality Metrics
- **Test Coverage**: >80% line coverage maintained
- **Type Coverage**: 100% type annotation compliance
- **Performance**: CLI commands complete in <2 seconds
- **Reliability**: >99.9% uptime for monitoring operations

### User Experience Metrics
- **Setup Time**: <5 minutes for initial global configuration
- **Learning Curve**: Intuitive CLI requiring minimal documentation
- **Error Messages**: Clear, actionable error descriptions
- **Recovery Time**: <1 minute average issue resolution

## 📚 Resources & Integration

### Spec-Kit Integration
This project is prepared for spec-kit workflow integration:
- **Repository**: https://github.com/kairin/spec-kit
- **Workflow**: Constitution → Specify → Plan → Tasks → Implement
- **Commands**: `/constitution`, `/specify`, `/plan`, `/tasks`, `/implement`

### Related Projects
- **ghostty-config-files**: https://github.com/kairin/ghostty-config-files
- **Claude Code**: https://claude.ai/code
- **Context7 MCP**: https://context7.com

### Documentation
- **README.md**: Project overview and quick start
- **API Documentation**: Python API reference (planned)
- **CLI Reference**: Command-line interface guide (planned)
- **Contributing Guide**: Development setup and workflow (planned)

---

**CRITICAL**: These requirements are NON-NEGOTIABLE. All AI assistants must follow these guidelines exactly. Failure to comply may result in configuration corruption, broken MCP setups, or security vulnerabilities.

**Version**: 1.0-2025
**Last Updated**: 2025-09-23
**Status**: ACTIVE - MANDATORY COMPLIANCE
**Target**: Python 3.11+ with modern development practices
**Review**: Required before any major implementation changes