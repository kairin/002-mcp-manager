# Quickstart: MCP Manager Improvements Validation

**Date**: 2025-10-13
**Purpose**: Validate three-phase enhancement implementation
**Duration**: ~15-20 minutes

---

## Prerequisites

- ✅ Python >=3.11 with uv installed
- ✅ Existing mcp-manager installation (`uv pip install -e .`)
- ✅ `~/.claude.json` with at least one MCP server configured
- ✅ npm installed (for stdio server updates)
- ✅ Terminal access with Bash or Zsh

---

## Phase 1: Core Functionality Validation

### Test 1: MCP Server Update Check (Dry-Run)

**Objective**: Verify version checking works without modifying configuration

```bash
# Check all servers for updates (dry-run mode)
mcp-manager mcp update --all --dry-run

# Expected Output:
# ✓ shadcn: 1.2.3 → 1.3.0 (minor update available)
# ℹ github: Already at latest version
# ℹ context7: HTTP servers do not support updates

# Check specific server
mcp-manager mcp update shadcn --dry-run

# Expected Output:
# Server: shadcn
# Current: 1.2.3
# Latest: 1.3.0
# Update Type: minor
# Would update: Yes (use without --dry-run to apply)
```

**✅ Success Criteria**:
- Command completes in <5 seconds
- Shows version information for stdio servers
- HTTP servers explicitly noted as non-updatable
- No configuration files modified

**❌ Failure Indicators**:
- ServerNotFoundError: Check `mcp-manager mcp status` for available servers
- UpdateCheckError: Verify npm is installed and accessible

---

### Test 2: MCP Server Update (Actual)

**Objective**: Apply available updates to MCP server

```bash
# Apply update to specific server
mcp-manager mcp update shadcn

# Expected Output:
# ✓ Updated shadcn from 1.2.3 to 1.3.0
# ✓ Configuration saved
# ✓ Health check passed

# Verify update applied
mcp-manager mcp status shadcn

# Expected Output:
# ✅ shadcn: Healthy
# Type: stdio
# Command: npx
# Args: ['shadcn@1.3.0', 'mcp']  # <-- Version updated
# Response time: <1s
```

**✅ Success Criteria**:
- Configuration updated with new version
- Health check passes after update
- No service interruption

**❌ Failure Indicators**:
- UpdateFailedError: Rollback triggered, check logs
- Connectivity issues: Verify npm registry access

---

### Test 3: Gemini CLI Synchronization

**Objective**: Sync MCP servers from Claude Code to Gemini CLI

```bash
# Sync MCP servers to Gemini CLI
mcp-manager gemini sync

# Expected Output:
# ✓ Synced 6 servers to Gemini CLI:
#   - context7
#   - shadcn
#   - github
#   - playwright
#   - hf-mcp-server
#   - markitdown
# ✓ Created ~/.config/gemini/settings.json
# ✓ Added GEMINI_CLI_SYSTEM_SETTINGS_PATH to ~/.bashrc
# ℹ Restart your shell or run: source ~/.bashrc

# Verify Gemini CLI configuration created
cat ~/.config/gemini/settings.json

# Expected Output: (JSON with mcpServers section)
```

**✅ Success Criteria**:
- `~/.config/gemini/settings.json` created
- File contains identical mcpServers from `~/.claude.json`
- Environment variable added to shell profile
- All 6 servers present

**❌ Failure Indicators**:
- ConfigurationError: Check `~/.claude.json` exists and is valid JSON
- FileSystemError: Verify write permissions for `~/.config/`
- ShellProfileError: Manually add `export GEMINI_CLI_SYSTEM_SETTINGS_PATH="$HOME/.config/gemini/settings.json"`

---

### Test 4: Gemini CLI Integration Verification

**Objective**: Confirm Gemini CLI can discover MCP servers

```bash
# Reload shell environment
source ~/.bashrc  # or ~/.zshrc

# Verify environment variable set
echo $GEMINI_CLI_SYSTEM_SETTINGS_PATH
# Expected: /home/user/.config/gemini/settings.json

# If Gemini CLI is installed, verify it sees the servers
# (This step assumes Gemini CLI is installed - skip if not)
gemini --version  # Verify Gemini CLI available
# ... MCP server discovery test (depends on Gemini CLI implementation) ...
```

**✅ Success Criteria**:
- Environment variable set correctly
- Gemini CLI config file readable
- Configuration persists across shell restarts

---

## Phase 2: Code Quality & Configuration

### Test 5: Configurable Audit Paths

**Objective**: Audit projects in custom directories

```bash
# Create test directory structure
mkdir -p ~/test-audit/project-a
mkdir -p ~/test-audit/project-b

# Add test .claude.json to one project
echo '{"mcpServers": {"test": {"type": "http", "url": "http://test"}}}' > ~/test-audit/project-a/.claude.json

# Audit with custom paths
mcp-manager project audit --search-dir ~/test-audit

# Expected Output:
# Global Config: ✅ OK (6 servers)
# Project Configs:
#   test-audit/project-a: ⚠️ Needs migration (1 server)
#   Search paths: ['/home/user/test-audit']

# Audit with multiple custom paths
mcp-manager project audit --search-dir ~/test-audit --search-dir ~/Apps

# Expected Output:
# Search paths: ['/home/user/test-audit', '/home/user/Apps']
# (Combined results from both directories)

# Clean up
rm -rf ~/test-audit
```

**✅ Success Criteria**:
- Custom directories scanned instead of defaults
- Multiple `--search-dir` flags supported
- Results show actual paths used

**❌ Failure Indicators**:
- InvalidPathError: Path must exist before auditing
- PermissionError: Check directory read permissions

---

### Test 6: Documentation Accuracy

**Objective**: Verify documentation reflects actual requirements

```bash
# Check Python version in README
grep -i "python" README.md | grep "3.11"
# Expected: Should find "Python >=3.11" (NOT "Python 3.13")

# Check MCP server count in Features component
grep -i "MCP server" website/src/components/Features.astro
# Expected: Should mention "6" servers (NOT "5")

# Verify documentation links exist
grep -i "CHANGELOG" README.md
grep -i "guide" README.md
# Expected: Links to docs/CHANGELOG.md and guides
```

**✅ Success Criteria**:
- README shows correct Python version (>=3.11)
- Features.astro shows 6 MCP servers
- Documentation links present

**⚠️ If tests fail**: Run documentation fixes from Phase 2 tasks

---

## Phase 3: Polish & Organization

### Test 7: CLI Reorganization (Post-Implementation)

**Objective**: Verify CLI functionality after modularization

```bash
# Test all command groups still work
mcp-manager mcp status          # MCP commands
mcp-manager project audit       # Project commands
mcp-manager fleet status        # Fleet commands
mcp-manager agent discover      # Agent commands
mcp-manager office info         # Office commands

# Verify help text remains clear
mcp-manager --help
mcp-manager mcp --help
mcp-manager project --help

# Check command discovery (tab completion should work)
```

**✅ Success Criteria**:
- All existing commands functional
- Help text clear and organized
- No import errors
- Performance unchanged (<2s per command)

---

### Test 8: Dynamic Version Management (Post-Implementation)

**Objective**: Verify version automatically updates in website

```bash
# Check current version in pyproject.toml
grep "version = " pyproject.toml
# Example: version = "0.1.0"

# Build website
npm run build

# Verify version in built website
grep -r "0.1.0" docs/ | head -n 3
# Expected: Version appears in index.html and other pages

# Change version in pyproject.toml (test only)
sed -i 's/version = "0.1.0"/version = "0.2.0"/' pyproject.toml

# Rebuild
npm run build

# Verify new version appears
grep -r "0.2.0" docs/ | head -n 3
# Expected: New version automatically injected

# Restore original version
git checkout pyproject.toml
```

**✅ Success Criteria**:
- Version from pyproject.toml appears in built website
- Changing pyproject.toml version updates website after rebuild
- No manual file edits required

---

## Expected Outcomes Summary

After completing all tests, you should have:

### Phase 1 Outcomes:
- ✅ MCP servers can be updated automatically via `mcp-manager mcp update`
- ✅ Gemini CLI has access to all 6 MCP servers via `~/.config/gemini/settings.json`
- ✅ Environment variable configured for system-wide Gemini CLI discovery

### Phase 2 Outcomes:
- ✅ Audit command works with custom directories via `--search-dir` flag
- ✅ Documentation reflects accurate requirements (Python >=3.11, 6 servers)
- ✅ Error handling consistent across all CLI commands

### Phase 3 Outcomes:
- ✅ CLI codebase organized into modules (<400 lines each)
- ✅ Version displayed consistently without manual updates
- ✅ All functionality preserved after refactoring

---

## Troubleshooting

### Common Issues

**Issue**: `mcp-manager: command not found`
- **Solution**: Run `uv pip install -e .` from repository root

**Issue**: `ServerNotFoundError` during update
- **Solution**: Run `mcp-manager mcp status` to see available servers
- **Check**: Verify server name spelling

**Issue**: Gemini sync fails with FileSystemError
- **Solution**: Check `~/.config/` directory permissions
- **Workaround**: Manually create: `mkdir -p ~/.config/gemini`

**Issue**: Environment variable not persisting
- **Solution**: Check correct shell profile was updated (bash vs zsh)
- **Manual**: Add to appropriate profile file

**Issue**: Update check fails for npm servers
- **Solution**: Verify npm is installed: `npm --version`
- **Solution**: Check network connectivity to npm registry

---

## Next Steps

After validation:
1. Review any failed tests and file issues
2. Run full test suite: `uv run pytest tests/ --cov=mcp_manager`
3. Verify code quality: `black src/ tests/ && ruff check src/ tests/ && mypy src/`
4. Update CHANGELOG.md with all improvements
5. Commit changes with proper branch naming: `YYYYMMDD-HHMMSS-feat-improvements`

---

**Total Validation Time**: ~15-20 minutes
**Prerequisites Check**: 5 minutes
**Phase 1 Tests**: 5 minutes
**Phase 2 Tests**: 3 minutes
**Phase 3 Tests**: 5 minutes
**Troubleshooting Buffer**: 2 minutes
