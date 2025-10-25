# Research: GitHub Copilot CLI MCP Support

**Generated**: 2025-10-25

## 1. Unknown: Copilot CLI MCP Support and Configuration Path

- **Task**: Research if and how the GitHub Copilot CLI supports custom MCP (Model Context Protocol) servers.
- **Finding**: The GitHub Copilot CLI **does** support custom MCP servers.

## 2. Decision & Rationale

- **Decision**: The `mcp-profile` script will officially support managing the GitHub Copilot CLI's MCP configuration.
- **Configuration Path**: The target configuration file is `~/.config/mcp-config.json`.
- **Rationale**: Official GitHub documentation confirms that the Copilot CLI uses this XDG-compliant path for its global MCP server configuration. This aligns perfectly with the project's constitutional principles of multi-tool consistency and XDG compliance. The script can therefore treat Copilot CLI as a first-class citizen alongside Gemini CLI for global profile synchronization.

## 3. Alternatives Considered

- **Repository-Specific Config**: The VS Code extension for Copilot supports repository-level configuration via `.vscode/mcp.json`. This was considered but is out of scope for the current feature, which focuses on synchronizing a user's global tool setup across multiple machines.
- **No Support**: The initial plan allowed for the possibility of no support. This has been disproven by the research.
