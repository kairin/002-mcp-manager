# CLI Contract: Validation Commands

**Feature**: 003-system-python-enforcement
**Date**: 2025-10-14
**Type**: Command-Line Interface

## Command: `mcp-manager validate python`

Validates system Python version meets requirements.

### Signature
```bash
mcp-manager validate python [--verbose] [--json]
```

### Options
- `--verbose`: Show detailed validation information
- `--json`: Output results in JSON format

### Success Output (exit code 0)
```
✅ Python version validation: PASS
- System Python: 3.13.0
- Runtime Python: 3.13.0
- Executable: /usr/bin/python3.13
- Constitution v1.2.0 Principle VII: COMPLIANT
```

### Failure Output (exit code 1)
```
❌ Python version validation: FAIL
- System Python: 3.11.5
- Required: 3.13+
- Constitution v1.2.0 Principle VII: VIOLATION

Recommendations:
  1. Upgrade to Python 3.13+ on Ubuntu 25.04
  2. Verify system Python with: python --version
  3. See docs/TROUBLESHOOTING.md for migration guide
```

### JSON Output (--json flag)
```json
{
  "check_name": "python_version",
  "passed": true,
  "message": "Python 3.13.0 detected (system and runtime match)",
  "details": {
    "system_version": "3.13.0",
    "runtime_version": "3.13.0",
    "executable_path": "/usr/bin/python3.13",
    "is_system_python": true
  },
  "timestamp": "2025-10-14T10:30:00Z",
  "severity": "info"
}
```

---

## Command: `mcp-manager validate uv`

Validates UV configuration meets requirements.

### Signature
```bash
mcp-manager validate uv [--verbose] [--json]
```

### Options
- `--verbose`: Show detailed UV configuration
- `--json`: Output results in JSON format

### Success Output (exit code 0)
```
✅ UV configuration validation: PASS
- Config source: /home/kkk/Apps/002-mcp-manager/pyproject.toml
- Python version: python3.13
- Constitution v1.2.0 Principle I: COMPLIANT
```

### Failure Output (exit code 1)
```
❌ UV configuration validation: FAIL
- Config source: /home/kkk/Apps/002-mcp-manager/pyproject.toml
- Python version: NOT CONFIGURED
- Required: [tool.uv] python = "python3.13"

Recommendations:
  1. Add [tool.uv] section to pyproject.toml
  2. Set python = "python3.13"
  3. Run: uv sync to rebuild environment
```

---

## Command: `mcp-manager validate mcp-servers`

Validates MCP server configurations use UV.

### Signature
```bash
mcp-manager validate mcp-servers [--verbose] [--json]
```

### Options
- `--verbose`: Show all MCP server configurations
- `--json`: Output results in JSON format

### Success Output (exit code 0)
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

### Failure Output (exit code 1)
```
❌ MCP server validation: FAIL
- Validated servers: 3 stdio, 2 HTTP
- UV compliance: 2/3 stdio servers
- Constitution v1.2.0 Principle I: VIOLATION

Failed servers:
  ✗ markitdown: uses direct python (should be uv run)

Recommendations:
  1. Update ~/.claude.json:
     "markitdown": {
       "type": "stdio",
       "command": "uv",
       "args": ["run", "markitdown-mcp"]
     }
  2. Restart Claude Code to apply changes
```

---

## Command: `mcp-manager validate constitution`

Validates complete constitution compliance (all principles).

### Signature
```bash
mcp-manager validate constitution [--principle PRINCIPLE] [--verbose] [--json]
```

### Options
- `--principle PRINCIPLE`: Validate specific principle (1-9, default: all)
- `--verbose`: Show detailed compliance information
- `--json`: Output results in JSON format

### Success Output (exit code 0)
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

### Failure Output (exit code 1)
```
❌ Constitution validation: FAIL
- Constitution version: 1.2.0
- Principles validated: 8/9 PASS
- Python 3.13 enforcement: VIOLATION
- Fleet compliance: NOT READY

Failed principles:
  ✗ VII. Cross-Platform Compatibility
    - Python version: 3.11.5 (requires 3.13+)
    - UV configuration: MISSING [tool.uv] section

Recommendations:
  1. Run: mcp-manager validate python --verbose
  2. Run: mcp-manager validate uv --verbose
  3. See: .specify/memory/constitution.md for requirements
```

---

## Contract Tests

Each command must have corresponding contract tests in `tests/contract/test_validation_api.py`:

### Test Structure
```python
def test_validate_python_success():
    """Contract: validate python returns exit 0 when Python 3.13+ detected"""
    result = subprocess.run(["uv", "run", "mcp-manager", "validate", "python"], ...)
    assert result.returncode == 0
    assert "Python version validation: PASS" in result.stdout

def test_validate_python_failure():
    """Contract: validate python returns exit 1 when Python < 3.13"""
    # Mock sys.version_info to return (3, 11, 5)
    ...

def test_validate_python_json_output():
    """Contract: --json flag produces valid JSON"""
    result = subprocess.run(["uv", "run", "mcp-manager", "validate", "python", "--json"], ...)
    data = json.loads(result.stdout)
    assert "check_name" in data
    assert "passed" in data
```

---

**Contract Status**: ✅ **COMPLETE** - All CLI commands defined with success/failure modes
