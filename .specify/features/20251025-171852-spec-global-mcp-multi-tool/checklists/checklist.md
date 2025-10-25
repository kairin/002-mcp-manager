# Consolidated Checklist: Global MCP Server Installation & Multi-Tool Sync

**Feature Branch**: 20251025-171852-feat-global-mcp-multi-tool-sync

## Pre-flight
- [X] On correct branch: `git branch --show-current | grep -q "20251025-171852-feat-global-mcp-multi-tool-sync"`
- [X] Clean tree: `test -z "$(git status --porcelain)"`
- [X] Constitution exists: `test -f .specify/memory/constitution.md`
- [X] Secret scan clean: `git ls-files | xargs -r grep -l -E "(ghp_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{48})" | wc -l | grep -q '^0$'`

## Specification Quality
- [X] Consolidate duplicated success criteria (SC-001, SC-002) in `spec.md`

## US1: One-click multi-tool profile sync
- [X] Profiles dir exists: `test -d ~/.config/mcp-profiles`
- [X] Switch profile: `scripts/mcp/mcp-profile dev --tool=all`
- [X] Claude keys == profile keys: `jq -r --arg p "$(git rev-parse --show-toplevel)" '(.projects[$p].mcpServers//{})|keys|sort' ~/.claude.json | diff -u - <(jq -r 'keys|sort' ~/.config/mcp-profiles/dev.json)`
- [X] Gemini keys == profile keys: `jq -r '(.mcpServers//{})|keys|sort' ~/.config/gemini/settings.json | diff -u - <(jq -r 'keys|sort' ~/.config/mcp-profiles/dev.json)`

## US2: Claude verification (CLI-first, boxed, real calls)
- [X] Run tests: `scripts/mcp/mcp-profile test`
- [X] Boxed headers present (≈5): `scripts/mcp/mcp-profile test | grep "\xe2\x94\x8c" | wc -l | grep -Eq '^[5-9]$'`
- [X] Real calls present in script (>=5): `grep -c "gh auth status\|gh api\|hf auth whoami\|claude mcp list\|curl.*context7" scripts/mcp/mcp-profile | grep -E '^[5-9]$'`
- [X] Color codes present (>20): `grep -c "\\033\[0;3" scripts/mcp/mcp-profile | grep -E '^[2-9][0-9]$'`
- [X] `verify` helper passes: `scripts/mcp/mcp-profile verify`

## US3: Drift protection
- [X] Local CI guard active: `scripts/local-ci/run.sh --skip-tests`
- [X] Commit policy: Ensure any commit modifying `scripts/mcp/mcp-profile` includes `allow-mcp-profile-update` tag.
- [X] Merge via PR with `--no-ff`; never delete branches.

## Copilot CLI
- [X] Status shows unsupported: `scripts/mcp/mcp-profile status --tool=copilot | grep -qi "unsupported"`
- [X] No write attempts to Copilot; Claude/Gemini unaffected.

## `verify` command (helper)
- [X] If missing, add `verify` command to compare keys across Claude/Gemini vs active profile.

## Backups
- [X] Claude backup created today in `~/.config/claude-code/backups`
- [X] Gemini backup created today in `~/.config/gemini/backups`

## Documentation
- [X] Update README with `--tool=copilot` (unsupported), `verify` command, and drift guard note.
- [X] Link `SPEC-KIT-SAFETY.md` rollback steps from `scripts/mcp/README.md`.

## Exit criteria
- [X] SC-001/002 pass (key equality for Claude/Gemini).
- [X] Test output has boxed sections with CLI-first order.
- [X] Drift guard in place and CI run green.
