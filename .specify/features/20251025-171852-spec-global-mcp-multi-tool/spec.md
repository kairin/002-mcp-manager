# Feature Specification: Global MCP Server Installation & Multi-Tool Sync (Claude, Gemini, Copilot)

**Feature Branch**: 20251025-171852-spec-global-mcp-multi-tool
**Created**: 2025-10-25
**Status**: Draft
**Input**: User description: "Also, the same MCP servers should also be installed for use globally by Copilot CLI, Gemini CLI and Claude Code. Help to verify the implementation for Claude Code so far is correct. It seems every time we git push and pull the implementation keep reverting to a broken version."

## User Scenarios & Testing (mandatory)

### User Story 1 - One-click multi-tool profile sync (Priority: P1)
- As a developer, I can run one command to apply the same MCP servers from a profile JSON across Claude Code (project-scoped), Gemini CLI (global), and Copilot CLI (global, if supported), with backups created first.
- Independent Test: Run `mcp-profile dev --tool=all` then verify Claude project's ~/.claude.json and ~/.config/gemini/settings.json have identical server keys to `~/.config/mcp-profiles/dev.json`.
- Acceptance:
  1. Given valid profile JSON, When switching to `dev`, Then Claude and Gemini reflect the profile servers exactly.
  2. Given tools not installed, When switching profile, Then graceful skips with warnings and exit code 0.

### User Story 2 - Claude Code verification (Priority: P1)
- As a developer, I can verify Claude Code's current project's MCP servers match the selected profile and pass CLI-first tests.
- Independent Test: Run `mcp-profile test` and see boxed, colored CLI tests (gh, hf), then MCP servers (github, hf-mcp-server, context7) with real outputs.
- Acceptance:
  1. Given active profile, When running test, Then 5 boxed sections appear with real API/CLI outputs.
  2. Given mismatched config, When running status, Then profile shows as CUSTOM and lists actual servers.

### User Story 3 - Drift protection on git pull/push (Priority: P2)
- As a maintainer, I want feature branches and merge strategy to prevent regressions where `scripts/mcp/mcp-profile` gets reverted.
- Independent Test: Create feature branch, commit changes, push, merge with `--no-ff` to main, pull; file remains correct.
- Acceptance:
  1. Given feature branch, When merged `--no-ff`, Then history preserved and no branch deletions.
  2. Given CI, When running, Then it must not regenerate/overwrite mcp-profile unless an explicit task says so.

### Edge Cases
- Tools missing (claude, gemini, copilot): skip with warnings and continue for installed tools.
- Profile JSON missing keys or invalid: show clear errors; do not write partial configs.
- Copilot CLI MCP unsupported: detect and report status as "not supported yet" without failing other tools.

## Requirements (mandatory)

### Functional Requirements
- FR-001: System MUST use a single source of truth profile JSON at `~/.config/mcp-profiles/<profile>.json` (dynamic, no hardcoding).
- FR-002: System MUST update Claude Code's `~/.claude.json` under `.projects[<git-root>].mcpServers` from the profile (with backup).
- FR-003: System MUST update Gemini CLI `~/.config/gemini/settings.json` `.mcpServers` globally from the profile (with backup).
- FR-004: System SHOULD detect Copilot CLI MCP capabilities; if supported, MUST sync globally; else, MUST report unsupported status clearly.
- FR-005: System MUST provide `status`, `list`, `test`, and `backup` commands reflecting multi-tool state.
- FR-006: Tests MUST be CLI-first with boxed, colored output and real API calls (gh, hf, context7, claude mcp list).
- FR-007: Backups MUST be timestamped in XDG-compliant paths and listed by `backup`.

### Key Entities
- Profile JSON: Map of MCP server configs (stdio/http), used by all tools.
- Tool Configs: Claude project-scoped ~/.claude.json, Gemini global ~/.config/gemini/settings.json, Copilot global (TBD/Detect).

## Success Criteria (mandatory)
- SC-001: `jq '.projects["<git-root>"].mcpServers | keys' ~/.claude.json` equals `jq 'keys' ~/.config/mcp-profiles/dev.json` after switch.
- SC-002: `jq '.mcpServers | keys' ~/.config/gemini/settings.json` equals `jq 'keys' ~/.config/mcp-profiles/dev.json` after switch.
- SC-003: `mcp-profile test` shows 5 boxed sections with real outputs and appropriate colors; order is CLI-first.
- SC-004: After merge with `--no-ff`, pulling main does not revert `scripts/mcp/mcp-profile`.

## Constitution Check
- Aligns with AGENTS.md: No hardcoded values; XDG paths; multi-tool consistency; backups; CLI-first tests; branch preservation; security scans.

