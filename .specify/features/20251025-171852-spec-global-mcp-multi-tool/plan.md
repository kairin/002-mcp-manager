# Implementation Plan: Global MCP Server Installation & Multi-Tool Sync

Feature Branch: 20251025-171852-spec-global-mcp-multi-tool
Created: 2025-10-25
Status: Planning

## Summary
Ensure the same MCP servers from a single profile JSON are applied to Claude Code (project-scoped), Gemini CLI (global), and Copilot CLI (global if supported), with dynamic JSON reads, XDG-compliant paths, automatic backups, and CLI-first verification; add drift prevention so git push/pull does not revert scripts/mcp/mcp-profile.

## Constitution Check
- No hardcoded values: Read servers exclusively from ~/.config/mcp-profiles/<profile>.json via jq.
- XDG compliance: ~/.local/bin binaries, ~/.config/* configs, backups in ~/.config/*/backups.
- Multi-tool consistency: Same profile JSON drives Claude, Gemini, and Copilot (if supported).
- Security: No secrets committed; run secret scan pre-commit.
- Git strategy: Feature branch, PR/--no-ff merge, never delete branches; add drift guard in CI.

## Architecture & Data Contracts
- Source of Truth: Profile JSON at ~/.config/mcp-profiles/{github|hf|dev|ui|full}.json with per-server blocks (type, command/url).
- Claude Code Target: ~/.claude.json at .projects[<git-root>].mcpServers (object copied verbatim from profile JSON).
- Gemini CLI Target: ~/.config/gemini/settings.json at .mcpServers (object copied verbatim).
- Copilot CLI Target: ~/.config/mcp-config.json (object copied verbatim from profile JSON).

## Phases
- Phase 0: Research & Detection
  - Determine Copilot CLI MCP support and config path; detect installed tools (claude, gemini, gh/copilot).
  - Drift Analysis: Identify any generators/CI steps rewriting scripts/mcp/mcp-profile and propose a guard.
- Phase 1: Contracts & Validation
  - Validate profile JSON schema (keys only, values have required fields); fail fast if invalid.
  - Add health checks for stdio (command exists/executable) and http (url present).
- Phase 2: Implementation
  - Extend mcp-profile to support --tool=copilot and include it in --tool=all, with safe no-op when unsupported.
  - Implement backups: ~/.config/claude-code/backups/claude-backup-TS.json, ~/.config/gemini/backups/gemini-backup-TS.json, and copilot backup if applicable.
  - Preserve current Claude behavior: write .projects[git-root].mcpServers exactly; do not alter other keys.
- Phase 3: Verification
  - Status: Show active profile vs CUSTOM; list servers from live configs.
  - Test: CLI-first boxes (gh, hf), then MCP servers (github, hf-mcp-server, context7) with real outputs.
  - Assertions:
    - jq '.projects["<git-root>"].mcpServers | keys' ~/.claude.json equals jq 'keys' ~/.config/mcp-profiles/<profile>.json
    - jq '.mcpServers | keys' ~/.config/gemini/settings.json equals jq 'keys' ~/.config/mcp-profiles/<profile>.json
- Phase 4: Drift Prevention
  - CI guard: Fail pipeline if scripts/mcp/mcp-profile changes without commit message tag "allow-mcp-profile-update".
  - Enforce PR with --no-ff, protect main; never delete branches.

## Deliverables
- features/<branch>/plan.md (this), research.md (Phase 0), data-model.md (schema), quickstart.md (commands), contracts/* (validation rules), tasks.md via /speckit.tasks.

## Risks & Mitigations
- Copilot CLI MCP unsupported: Implement detection/stub and document; do not block Claude/Gemini.
- Reversion via generators: Add CI guard and audit; document rollback.
- Secrets leakage: Mandatory scans pre-commit.

## Gates & Exit Criteria
- SC-001/002 key equality checks pass for Claude and Gemini after switch.
- Test shows 5 boxed sections, CLI-first, with real outputs.
- CI guard in place; merge via PR/--no-ff.

## Exceptions
- None requested; copilot support guarded by detection.
