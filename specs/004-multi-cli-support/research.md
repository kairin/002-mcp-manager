# Research: MCP Manager System Health & Multi-Platform Support

**Spec ID**: 004-multi-cli-support (consolidated with 005-we-ve-gone)
**Research Date**: 2025-10-15
**Scope**: Platform compatibility analysis + Project health audit tooling

This research document consolidates findings from two parallel investigations:
1. Multi-platform MCP server configuration compatibility
2. Project health and standardization audit tooling

See the following detailed research documents:
- [Platform Compatibility Research](./research-platform-compatibility.md) - Multi-CLI MCP server configuration analysis
- [Project Health Research](./research-project-health.md) - UV-first development and audit tooling

---

## Research Summary

### Platform Compatibility (from 004)
- **Root Cause**: Configuration format differences between AI CLI platforms (Claude Code, Gemini CLI, Copilot CLI)
- **Key Findings**: 
  - Gemini CLI requires `httpUrl` instead of `url` for HTTP servers
  - Gemini CLI requires `Accept` header for HTTP servers
  - Version staleness risk with fixed package versions

### Project Health (from 005)
- **UV-first Policy**: All Python operations must use `uv` exclusively
- **Dependency Management**: Systematic approach to keeping dependencies current
- **Repository Organization**: Clean separation of backend/frontend concerns

Both research areas inform the comprehensive system health and multi-platform support feature.
