# Data Model: Multi-Tool MCP Profile Management

**Date**: 2025-10-26
**Author**: Gemini

This document outlines the key data entities for the MCP Profile Management feature, based on the feature specification.

## 1. MCP Profile

Represents a named collection of MCP server configurations. Profiles are stored as tool-agnostic JSON files.

- **Storage**: `~/.config/mcp-profiles/{profile-name}.json`
- **Format**: JSON

**Attributes**:

| Attribute | Type | Description |
|---|---|---|
| `$schema_version` | String | The version of the profile schema (e.g., "1.0"). |
| `name` | String | The unique name of the profile (e.g., "dev", "ui"). |
| `servers` | Array[Object] | A list of MCP server configurations. |
| `token_count_estimate` | Integer | An estimated token count for the profile. |

**Example (`dev.json`)**:

```json
{
  "$schema_version": "1.0",
  "name": "dev",
  "token_count_estimate": 7000,
  "servers": {
    "github": {},
    "markitdown": {}
  }
}
```

## 2. Tool Configuration

Represents the AI tool-specific configuration file that contains the active MCP server list.

### Claude Code
- **Storage**: `~/.claude.json`
- **Scope**: Project-specific. The file contains a dictionary of projects, and the MCP servers are configured per project.

### Gemini CLI
- **Storage**: `~/.config/gemini/settings.json`
- **Scope**: Global. The file contains a single `mcp_servers` section.

## 3. Configuration Backup

A timestamped snapshot of a tool's configuration file, created before any modifications.

- **Storage**: Tool-specific backup directories (e.g., `~/.config/claude-code/backups/`, `~/.config/gemini/backups/`).
- **Format**: JSON (redacted).

**Attributes**:

| Attribute | Description |
|---|---|
| `timestamp` | The timestamp of the backup, included in the filename (e.g., `claude.json.20251026-084515.backup`). |
| `content` | The original content of the configuration file, with sensitive values like API keys redacted. |
| `tool_name` | The name of the tool the backup belongs to (e.g., "claude", "gemini"). |

## 4. AI Instruction Document

Represents the set of files used to provide consistent instructions to AI assistants.

- **`AGENTS.md`**: The master instruction file, acting as the single source of truth.
- **`CLAUDE.md`**: A symlink to `AGENTS.md`.
- **`GEMINI.md`**: A symlink to `AGENTS.md`.
