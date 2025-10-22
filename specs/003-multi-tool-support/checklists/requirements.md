# Specification Quality Checklist: Multi-Tool MCP Profile Management

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2025-10-23
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Implementation Verification Checklist

**Purpose**: Verify the implementation is complete and functional (not placeholder code)

**Instructions**: Run each verification step and mark [x] when passing. Document failures in Notes section.

### VR-001: File I/O Operations

- [ ] Run `mcp-profile dev` and check modification time of `~/.claude.json`: `stat -c %Y ~/.claude.json`
- [ ] Wait 2 seconds, run `mcp-profile ui`, verify timestamp changed
- [ ] Verify actual file content changed: `jq '.projects[].mcpServers | keys' ~/.claude.json`

**Expected**: Timestamps update after each profile switch, server lists match profile

### VR-002: JSON Parsing with jq

- [ ] Verify `jq` is used (not string manipulation): `grep -n "jq" ~/Apps/002-mcp-manager/scripts/mcp/mcp-profile`
- [ ] Check script doesn't use sed/awk for JSON: `grep -E "sed|awk.*json" ~/Apps/002-mcp-manager/scripts/mcp/mcp-profile`

**Expected**: Script contains `jq` commands, no sed/awk JSON manipulation

### VR-003: Tool Detection with Binary Checks

- [ ] Verify tool detection logic: `grep -A 5 "which\|command -v" ~/Apps/002-mcp-manager/scripts/mcp/mcp-profile`
- [ ] Test detection with missing tool: Temporarily remove claude from PATH, run `mcp-profile status`

**Expected**: Script uses `which` or `command -v`, gracefully handles missing tools

### VR-004: Backup Creation

- [ ] Run `mcp-profile full` and check for new backup: `ls -lt ~/.config/claude-code/backups/ | head -5`
- [ ] Verify backup contains actual config: `jq . ~/.config/claude-code/backups/claude-backup-*.json | head -20`

**Expected**: New timestamped backup file exists, contains valid JSON config

### VR-005: Configuration Updates Verification

- [ ] Switch to dev profile: `mcp-profile dev`
- [ ] Read Claude config: `jq '.projects[].mcpServers | keys' ~/.claude.json`
- [ ] Read Gemini config (if installed): `jq '.mcpServers | keys' ~/.config/gemini/settings.json`
- [ ] Compare with profile source: `jq 'keys' ~/.config/mcp-profiles/dev.json`

**Expected**: Config files match profile JSON exactly

### VR-006: Symlink Verification

- [ ] Check CLAUDE.md is symlink: `test -L CLAUDE.md && echo "✓ Symlink" || echo "✗ Not a symlink"`
- [ ] Check GEMINI.md is symlink: `test -L GEMINI.md && echo "✓ Symlink" || echo "✗ Not a symlink"`
- [ ] Verify targets: `ls -la CLAUDE.md GEMINI.md | grep "-> AGENTS.md"`
- [ ] Check relative path: `readlink CLAUDE.md` (should show "AGENTS.md", not absolute path)

**Expected**: Both are symlinks with relative paths to AGENTS.md

### VR-007: Error Message Quality

- [ ] Test invalid profile: `mcp-profile nonexistent-profile 2>&1 | grep -i "available\|valid"`
- [ ] Test invalid tool flag: `mcp-profile dev --tool=invalid 2>&1 | grep -i "claude\|gemini"`
- [ ] Test missing jq: Temporarily rename jq, run script, check error message

**Expected**: Specific, actionable error messages (not generic "failed")

### VR-008: Idempotency

- [ ] Switch to dev profile: `mcp-profile dev`
- [ ] Record config checksum: `md5sum ~/.claude.json > /tmp/config1.md5`
- [ ] Switch to dev again: `mcp-profile dev`
- [ ] Compare checksum: `md5sum ~/.claude.json > /tmp/config2.md5 && diff /tmp/config1.md5 /tmp/config2.md5`

**Expected**: Second switch produces identical config (checksum match)

### VR-009: Status Reads Actual Configs

- [ ] Manually edit `~/.claude.json` to add a fake server
- [ ] Run `mcp-profile status`
- [ ] Verify status output includes the fake server

**Expected**: Status reflects actual file content (not cached state)

### VR-010: Feature Test Coverage

- [ ] Verify all 3 user stories have acceptance scenarios: `grep -c "Given.*When.*Then" specs/003-multi-tool-support/spec.md`
- [ ] Check verification requirements exist in user stories: `grep -c "Verification Requirements:" specs/003-multi-tool-support/spec.md`

**Expected**: At least 8 acceptance scenarios, 3 verification requirement sections

### Functional Requirement Verification

#### FR-001: Tool Detection

- [ ] Run with Claude installed: `which claude && mcp-profile status | grep -i claude`
- [ ] Run with Gemini installed: `which gemini && mcp-profile status | grep -i gemini`

#### FR-002: Simultaneous Profile Switching

- [ ] Run `mcp-profile dev` (no --tool flag)
- [ ] Verify both configs updated: Check timestamps on both `~/.claude.json` and `~/.config/gemini/settings.json`

#### FR-003: Individual Tool Switching

- [ ] Run `mcp-profile ui --tool=claude`
- [ ] Verify only Claude config timestamp changed (Gemini unchanged)

#### FR-004: Environment Variable Support

- [ ] Run `MCP_TOOL=gemini mcp-profile full`
- [ ] Verify only Gemini config changed

#### FR-005: Backup Creation

- [ ] Count backups before: `ls ~/.config/claude-code/backups/ | wc -l`
- [ ] Run `mcp-profile dev`
- [ ] Count backups after: Verify count increased by 1

#### FR-011-012: Symlinks

- [ ] Verify CLAUDE.md and GEMINI.md are symlinks with relative paths (see VR-006)

#### FR-013: Philosophy Documentation

- [ ] Check AGENTS.md mentions deployment: `grep -i "deployment\|30 minutes" AGENTS.md`
- [ ] Verify minimalism removed: `grep -i "minimal\|minimalism" AGENTS.md` (should find deployment context, not restriction)

#### FR-014: Multi-Tool Documentation

- [ ] Check README has multi-tool examples: `grep -c "\-\-tool=" README.md`

#### FR-015: JSON Validation

- [ ] Create malformed profile JSON: `echo "{invalid json" > /tmp/test-profile.json`
- [ ] Try to use it (expect clear error)

### Success Criteria Verification

#### SC-001: Speed (< 5 seconds)

- [ ] Time profile switch: `time mcp-profile dev`

**Expected**: Total time < 5 seconds

#### SC-002: Success Rate (100%)

- [ ] Run 5 consecutive switches, verify all succeed with no errors

#### SC-003: Backup Retention

- [ ] Check oldest backup: `ls -lt ~/.config/claude-code/backups/ | tail -5`

**Expected**: Backups from at least 30 days ago still exist (if system that old)

#### SC-005: Symlink Git Operations

- [ ] Clone repo to /tmp: `git clone ~/Apps/002-mcp-manager /tmp/test-mcp`
- [ ] Check symlinks: `cd /tmp/test-mcp && test -L CLAUDE.md && test -L GEMINI.md`
- [ ] Cleanup: `rm -rf /tmp/test-mcp`

**Expected**: Symlinks work after clone

#### SC-007: Verification Time (< 10 minutes)

- [ ] Time this entire checklist execution

**Expected**: All checks complete in under 10 minutes

## Notes

### Verification Run: [DATE]

**Tester**: [Name]
**System**: [OS, versions]

**Failures**:
- [Document any failed checks with specific errors]

**Observations**:
- [Note any unexpected behavior, edge cases found, suggestions]

**Overall Status**: [ ] PASS / [ ] FAIL

---

## Specification Quality: COMPLETE ✓

All specification quality checks passed. The spec is ready for `/speckit.plan` phase.
