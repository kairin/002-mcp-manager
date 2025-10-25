# Checklist: Global MCP Server Installation & Multi-Tool Sync (Checked)

Generated: 20251025-103755Z
Feature Branch: 20251025-171852-spec-global-mcp-multi-tool

## Pre-flight
- [x] On correct branch (20251025-171852-spec-global-mcp-multi-tool)
- [ ] Clean tree
- [x] Constitution exists (.specify/memory/constitution.md)
- [ ] Secret scan clean (run suggested command)

## US1: One-click multi-tool profile sync
- [ ] Profiles dir exists (~/.config/mcp-profiles)
- [ ] Switch profile (scripts/mcp/mcp-profile dev --tool=all)
- [ ] Claude keys == profile keys (run jq/diff)
- [ ] Gemini keys == profile keys (run jq/diff)

## US2: Claude verification (CLI-first, boxed, real calls)
- [ ] Run tests: scripts/mcp/mcp-profile test
- [ ] Boxed headers present (≈5) (run suggested grep)
- [x] Real calls present in script (>=5) [count=9]
- [ ] Color codes present (>20) [count=5]
- [ ] Verify helper passes (scripts/mcp/mcp-profile verify)

## US3: Drift protection
- [x] Local CI guard present (validate_mcp_profile_update_guard)
- [ ] Commit policy (include allow-mcp-profile-update on mcp-profile changes)
- [ ] Merge via PR with --no-ff; never delete branches

## Copilot CLI
- [x] Status shows unsupported (implemented)
- [x] No write attempts to Copilot; Claude/Gemini unaffected (by design)

## Backups
- [ ] Claude backup created today
- [ ] Gemini backup created today

## Documentation
- [ ] Update README with --tool=copilot, verify, drift guard
- [ ] Link SPEC-KIT-SAFETY.md rollback steps from scripts/mcp/README.md

## Exit criteria
- [ ] SC-001/002 pass (key equality for Claude/Gemini)
- [ ] Test output has boxed sections with CLI-first order
- [ ] Drift guard in place and CI run green
