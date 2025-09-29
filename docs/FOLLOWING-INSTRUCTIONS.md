# Following Instructions: Why AGENTS.md Compliance Matters

## Introduction

Strict adherence to AGENTS.md requirements is critical for MCP Manager's reliability and consistency. This guide explains why compliance prevents failures and provides real-world case studies demonstrating the impact of following (or ignoring) constitutional principles.

**Key Principle**: Every instruction in AGENTS.md exists for a documented, evidence-based reason. Deviating from established workflows causes preventable failures that waste development time.

## Constitutional Foundation

All requirements in AGENTS.md align with [Constitution v1.0.0](../.specify/memory/constitution.md). The seven core principles provide the governance framework:

1. **UV-First Development** (Principle I) - Mandatory UV package manager usage
2. **Global Configuration First** (Principle II) - Centralized MCP server management
3. **Zero Downtime Operations** (Principle III) - Configuration changes never break existing setups
4. **Branch Preservation** (Principle IV) - Never delete branches, preserve all history
5. **GitHub Pages Protection** (Principle V) - Website must remain functional at all times
6. **Security by Design** (Principle VI) - Secure credential storage and rotation
7. **Cross-Platform Compatibility** (Principle VII) - Identical operation across Ubuntu 25.04 + Python 3.13 fleet

## Case Study 1: MarkItDown MCP Integration (v1.2.1)

### Background

MarkItDown MCP server integration in version 1.2.1 demonstrated the critical importance of UV-first development compliance (Constitution Principle I).

### The Problem

Initial integration attempts violated Principle I by using standard `pip` and direct executables. See [CHANGELOG.md v1.2.0-1.2.1](../CHANGELOG.md#120---2025-09-25) for complete failure timeline.

### The Solution

Strict UV-first compliance resolved 100% of issues using `uv pip install` and `uv run` commands.

## Case Study 2: GitHub MCP Configuration Evolution (v1.2.3)

### Background

GitHub MCP server was incorrectly documented as "HTTP" type, causing Claude Code integration failures.

### The Problem - Why HTTP Configuration Failed

1. **Connection Failures**: Claude Code couldn't establish HTTP connection to non-existent server endpoint
2. **Missing URL**: HTTP type requires `url` and `headers` fields, not `command` and `args`
3. **Server Not Found**: Claude Code reported "GitHub MCP server not available"
4. **Authentication Errors**: Attempted HTTP headers caused authentication failures
5. **Timeout Issues**: HTTP client waited for server response that never came

**Root Cause**: GitHub MCP Server v0.16.0 at `/home/kkk/bin/github-mcp-server` is a **stdio-based CLI tool**, not an HTTP API server.

### The Solution

Corrected documentation with accurate stdio configuration. See [CHANGELOG.md v1.2.3](../CHANGELOG.md#123---2025-09-30) for detailed failure analysis.

## Best Practices

1. **Always Follow UV-First** - Use `uv pip install` and `uv run` commands
2. **Verify Server Type** - Check if stdio (binary) or HTTP (service) before configuring
3. **Test in Fresh Environment** - Validate setup works from clean state
4. **Reference Constitutional Principles** - Cite specific version numbers

## Troubleshooting

See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for comprehensive diagnostic procedures.

---

**Version:** 1.0.0 | **Last Updated:** 2025-09-30 | **Constitution Reference:** v1.0.0
