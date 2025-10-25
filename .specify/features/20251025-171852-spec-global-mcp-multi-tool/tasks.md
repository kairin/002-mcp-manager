# Tasks: Global MCP Server Installation & Multi-Tool Sync

Input: spec.md + plan.md
Generated: 2025-10-25T09:21:56.926Z

## Phase 1: Setup (Shared Infrastructure)
- [ ] T001 [P] Create global profiles dir if missing: ~/.config/mcp-profiles/
- [ ] T002 [P] Ensure XDG dirs exist: ~/.config/claude-code/backups, ~/.config/gemini/backups
- [ ] T003 [P] Add README note: scripts/mcp/README.md about global profile source-of-truth

## Phase 2: Foundational (Blocking)
- [ ] T010 Validate profile JSON schema via jq before writes (keys only + per-server fields)
- [ ] T011 [P] Add health checks in check_profile_health() for stdio exec and http url (already present - verify only)
- [ ] T012 Add --tool=copilot arg parsing stub (no-op if unsupported)
- [ ] T013 Add safe detection for Copilot CLI MCP capability (research path, print "unsupported" if absent)

## Phase 3: US1 - One-click multi-tool profile sync (P1)
- [ ] T020 [US1] Update switch_profile() to include copilot branch (guarded by detection)
- [ ] T021 [US1] Back up copilot config if supported to ~/.config/github-copilot/backups/copilot-backup-TS.json
- [ ] T022 [US1] Write copilot config from profile if supported (exact server object copy)
- [ ] T023 [US1] Keep Claude per-project write using .projects[$git_root].mcpServers (no changes)
- [ ] T024 [US1] Keep Gemini global write to .mcpServers (no changes)
- [ ] T025 [US1] Status/list reflect copilot state: supported/unsupported

## Phase 4: US2 - Claude Code verification (P1)
- [ ] T030 [US2] Add jq assertion helper: compare ~/.claude.json project servers vs profile keys
- [ ] T031 [US2] Ensure test_api_keys shows 5 boxed sections with CLI-first order (verify greps from SPEC-KIT-SAFETY)
- [ ] T032 [US2] Add docs snippet to README: verification commands for Claude vs profile

## Phase 5: US3 - Drift protection on push/pull (P2)
- [ ] T040 [US3] Add local-ci guard: fail if scripts/mcp/mcp-profile changed without "allow-mcp-profile-update" in commit message
- [ ] T041 [US3] Document merge strategy (PR/--no-ff) in SPEC-KIT-SAFETY.md and README.md
- [ ] T042 [US3] Add emergency rollback snippet (reference SPEC-KIT-SAFETY.md) to scripts/mcp/README.md

## Phase 6: Polish & Cross-Cutting
- [ ] T050 [P] Update README examples for --tool=all and copilot detection
- [ ] T051 [P] Add quickstart.md under feature dir with commands to validate Claude/Gemini key equality
- [ ] T052 [P] Run secret scan before commit on feature branch

## Notes
- Keep no hardcoded servers; always read ~/.config/mcp-profiles/<profile>.json
- XDG compliance mandatory; do not use ~/bin or /usr/bin for user scripts
- Copilot support must be a no-op if unsupported; do not break Claude/Gemini
