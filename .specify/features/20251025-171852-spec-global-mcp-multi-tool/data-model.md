# Data Model: MCP Profile Switcher

**Generated**: 2025-10-25

This document defines the key data entities for the MCP Profile Switcher feature, based on the feature specification.

## 1. Profile JSON

This entity is the source of truth for all MCP server configurations. It is a JSON file located at `~/.config/mcp-profiles/<profile-name>.json`.

- **Type**: JSON Object
- **Description**: A map where each key is a server name and the value is the server's configuration object.

### Schema

The structure for each server configuration within the JSON file is as follows:

```json
{
  "server-name": {
    "type": "stdio" | "http",
    "command": ["string"],
    "url": "string",
    "description": "string"
  }
}
```

### Fields

- **`server-name`** (string, key): The unique identifier for the MCP server.
- **`type`** (string, required): The type of server. Must be either `stdio` or `http`.
- **`command`** (array of strings): The command and its arguments to start the server. Required if `type` is `stdio`.
- **`url`** (string): The URL for the MCP server. Required if `type` is `http`.
- **`description`** (string, optional): A brief description of the server's purpose.

### Validation Rules

- Each server entry MUST have a `type` field.
- If `type` is `stdio`, the `command` field is required.
- If `type` is `http`, the `url` field is required.

## 2. Tool Configurations

This entity represents the target configuration files for each supported AI tool that the `mcp-profile` script modifies.

### 2.1 Claude Code

- **Path**: `~/.claude.json`
- **Target Key**: `.projects["<git-root>"].mcpServers`
- **Behavior**: The `mcpServers` object is a direct copy of the selected Profile JSON content.

### 2.2 Gemini CLI

- **Path**: `~/.config/gemini/settings.json`
- **Target Key**: `.mcpServers`
- **Behavior**: The `mcpServers` object is a direct copy of the selected Profile JSON content.

### 2.3 GitHub Copilot CLI

- **Path**: `~/.config/mcp-config.json`
- **Target Key**: The root of the file is the MCP server map.
- **Behavior**: The entire file content is a direct copy of the selected Profile JSON content.
