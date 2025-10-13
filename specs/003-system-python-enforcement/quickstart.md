# Quickstart: System Python 3.13 Enforcement

**Feature**: 003-system-python-enforcement
**Date**: 2025-10-14
**Estimated time**: 5 minutes

## Prerequisites

- Ubuntu 25.04 with Python 3.13 installed
- UV package manager installed
- mcp-manager installed via UV
- Access to ~/.claude.json configuration

## Quick Start Steps

### Step 1: Verify System Python (30 seconds)

```bash
# Check system Python version
python --version
# Expected output: Python 3.13.0 or higher

# Verify UV is installed
uv --version
# Expected output: uv X.Y.Z or higher
```

**Success criteria**: Python 3.13+ and UV both available

### Step 2: Run Python Validation (30 seconds)

```bash
# Validate Python 3.13 enforcement
uv run mcp-manager validate python
```

**Expected output**:
```
✅ Python version validation: PASS
- System Python: 3.13.0
- Runtime Python: 3.13.0
- Executable: /usr/bin/python3.13
- Constitution v1.2.0 Principle VII: COMPLIANT
```

**Success criteria**: Validation passes with green checkmark

### Step 3: Verify UV Configuration (30 seconds)

```bash
# Validate UV configuration
uv run mcp-manager validate uv
```

**Expected output**:
```
✅ UV configuration validation: PASS
- Config source: /path/to/pyproject.toml
- Python version: python3.13
- Constitution v1.2.0 Principle I: COMPLIANT
```

**Success criteria**: UV configured to use python3.13

### Step 4: Validate MCP Servers (1 minute)

```bash
# Validate MCP server configurations
uv run mcp-manager validate mcp-servers
```

**Expected output**:
```
✅ MCP server validation: PASS
- Validated servers: 3 stdio, 2 HTTP
- UV compliance: 3/3 stdio servers
- Constitution v1.2.0 Principle I: COMPLIANT

Servers validated:
  ✓ markitdown (stdio via uv)
  ✓ github (stdio via uv)
  ✓ playwright (stdio via uv)
  ✓ context7 (HTTP)
  ✓ hf-mcp-server (HTTP)
```

**Success criteria**: All stdio servers use UV

### Step 5: Run Full Constitution Check (1 minute)

```bash
# Validate complete constitution compliance
uv run mcp-manager validate constitution
```

**Expected output**:
```
✅ Constitution validation: PASS
- Constitution version: 1.2.0
- Principles validated: 9/9
- Python 3.13 enforcement: ACTIVE
- Fleet compliance: READY

Principle status:
  ✓ I.   UV-First Development
  ✓ II.  Global Configuration First
  ✓ III. Zero Downtime Operations
  ✓ IV.  Branch Preservation
  ✓ V.   GitHub Pages Protection
  ✓ VI.  Security by Design
  ✓ VII. Cross-Platform Compatibility (Python 3.13)
  ✓ VIII. Repository Organization
  ✓ IX.  Multi-Agent Support
```

**Success criteria**: All principles pass validation

### Step 6: Test Pre-commit Integration (2 minutes)

```bash
# Test pre-commit hook validation
git add .
git commit -m "test: verify Python 3.13 enforcement"
```

**Expected behavior**:
- Pre-commit hook runs validation
- Commit proceeds if validation passes
- Commit blocks if validation fails

**Success criteria**: Pre-commit hook validates Python enforcement

## Troubleshooting

### Issue: Python version < 3.13

**Symptom**:
```
❌ Python version validation: FAIL
- System Python: 3.11.5
- Required: 3.13+
```

**Solution**:
```bash
# Upgrade system Python (Ubuntu 25.04)
sudo apt update
sudo apt install python3.13 python3.13-venv

# Verify upgrade
python --version
```

### Issue: UV configuration missing

**Symptom**:
```
❌ UV configuration validation: FAIL
- Python version: NOT CONFIGURED
```

**Solution**:
```toml
# Add to pyproject.toml
[tool.uv]
python = "python3.13"
```

Then rebuild:
```bash
uv sync
```

### Issue: MCP server not using UV

**Symptom**:
```
❌ MCP server validation: FAIL
Failed servers:
  ✗ markitdown: uses direct python
```

**Solution**:
```bash
# Edit ~/.claude.json
nano ~/.claude.json
```

Update server configuration:
```json
{
  "mcpServers": {
    "markitdown": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "markitdown-mcp"]
    }
  }
}
```

Restart Claude Code to apply changes.

## Acceptance Test Scenarios

These scenarios validate the feature specification acceptance criteria:

### Scenario 1: Fresh System Initialization

**Given**: Fresh Ubuntu 25.04 system with Python 3.13
**When**: `mcp-manager init` is executed
**Then**: System uses Python 3.13 without additional installations

**Test**:
```bash
uv run mcp-manager init --global
uv run mcp-manager validate python
# Must pass without downloading additional Python
```

### Scenario 2: CLI Command Execution

**Given**: mcp-manager configured
**When**: Any CLI command executed (audit, status, add, etc.)
**Then**: Operations run using system Python 3.13 via UV

**Test**:
```bash
uv run mcp-manager status
uv run mcp-manager audit
# Verify via: ps aux | grep python (should show python3.13)
```

### Scenario 3: MCP Server Launch

**Given**: MCP server configurations exist
**When**: stdio-based servers launched
**Then**: All servers execute using system Python 3.13 via UV

**Test**:
```bash
uv run mcp-manager validate mcp-servers
# All stdio servers must show "command": "uv"
```

### Scenario 4: Package Installation

**Given**: Project dependencies need installation
**When**: UV manages pip operations
**Then**: Packages installed using system Python 3.13

**Test**:
```bash
uv pip install pytest
uv run python -c "import sys; print(sys.version)"
# Must output Python 3.13.x
```

### Scenario 5: Constitution Compliance

**Given**: Constitution compliance check executed
**When**: Python version validation runs
**Then**: System confirms Python 3.13+ active, no additional installs

**Test**:
```bash
uv run mcp-manager validate constitution --principle 7
# Must pass Principle VII validation
```

## Success Verification

All quickstart steps completed successfully when:

1. ✅ `python --version` shows 3.13+
2. ✅ `uv run mcp-manager validate python` passes
3. ✅ `uv run mcp-manager validate uv` passes
4. ✅ `uv run mcp-manager validate mcp-servers` passes
5. ✅ `uv run mcp-manager validate constitution` passes
6. ✅ Pre-commit hook blocks invalid commits
7. ✅ No additional Python installations exist on system

## Next Steps

After quickstart completion:

1. Deploy to additional fleet nodes
2. Run fleet-wide validation: `mcp-manager fleet audit`
3. Configure CI/CD to run validation on PRs
4. Review constitution compliance regularly

## Documentation References

- Full specification: `./spec.md`
- Data model: `./data-model.md`
- CLI contracts: `./contracts/validation_cli.md`
- Constitution: `.specify/memory/constitution.md`

---

**Quickstart Status**: ✅ **COMPLETE** - All steps defined with success criteria
