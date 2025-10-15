# CLI Contract: `mcp-manager validate`

**Version**: 1.0.0
**Date**: 2025-10-15
**Feature**: System Python Enforcement (002)
**Command**: `mcp-manager validate`

## Overview

The `mcp-manager validate` command verifies constitution compliance regarding system Python 3.13 usage. It checks that:
1. System Python 3.13 is installed and accessible
2. UV is configured to use only system Python
3. UV is prevented from installing additional Python interpreters
4. Virtual environments (if present) are based on system Python 3.13

## Command Signature

```bash
mcp-manager validate [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--verbose` | flag | false | Display detailed diagnostic information |
| `--help` | flag | N/A | Show help message and exit |

### Exit Codes

| Code | Status | Meaning |
|------|--------|---------|
| 0 | PASS | Validation successful, all checks passed |
| 1 | FAIL | Validation failed, constitutional violations detected |
| 2 | ERROR | Validation error, unable to complete checks |

## Input Contracts

### Preconditions

- **P1**: Command executed from mcp-manager project root or subdirectory
- **P2**: User has read access to UV configuration files
- **P3**: User has permission to execute Python binary

### Environment Dependencies

- System Python 3.13 installation (optional - will validate presence)
- UV package manager (optional - will validate presence)
- UV configuration files: `uv.toml` or `pyproject.toml` (optional)
- `.python-version` file (optional)

## Output Contracts

### Summary Mode (Default)

**Success Output** (exit code 0):
```
✓ PASS: System Python 3.13 enforcement validated
  Python: /usr/bin/python3.13 (3.13.0)
  UV Config: Compliant (only-system, downloads=never)
```

**Format**:
- Line 1: Status indicator (`✓ PASS` or `✗ FAIL` or `✗ ERROR`)
- Line 2: Python information (path and version)
- Line 3: UV configuration summary

**Failure Output** (exit code 1):
```
✗ FAIL: Constitution violations detected
  UV allows Python downloads (python-downloads=automatic). Must be 'manual' or 'never'.
  UV not configured for system-only Python (python-preference=managed). Must be 'only-system'.
```

**Format**:
- Line 1: Status indicator with failure message
- Lines 2+: Individual violation messages (indented)

**Error Output** (exit code 2):
```
✗ ERROR: Validation could not complete
  Python 3.13 not found on system
  Searched locations: /usr/bin/python3.13, /usr/local/bin/python3.13, /opt/homebrew/bin/python3.13
```

**Format**:
- Line 1: Status indicator with error message
- Lines 2+: Specific error details (indented)

### Verbose Mode (`--verbose`)

**Success Output** (exit code 0):
```
System Python Enforcement Validation Report
============================================

Python Environment:
  Executable: /usr/bin/python3.13
  Version: 3.13.0
  Source: Package Manager
  Distribution: Ubuntu
  Virtual Env: None

UV Configuration:
  Config File: /home/user/project/uv.toml
  python-preference: only-system ✓
  python-downloads: never ✓
  .python-version: 3.13 ✓

Validation Checks:
  ✓ Python 3.13 detected
  ✓ Python from approved path (/usr/bin)
  ✓ UV prevents Python downloads
  ✓ UV uses system Python only
  ✓ No virtual environment conflicts

Result: PASS
Timestamp: 2025-10-15T14:30:00.123456
```

**Sections**:
1. **Header**: Report title with separator line
2. **Python Environment**: Detected Python details
3. **UV Configuration**: Config file and settings with checkmarks
4. **Validation Checks**: List of executed checks with results
5. **Warnings** (if any): Non-critical issues
6. **Errors** (if any): Critical problems
7. **Footer**: Final result and timestamp

## Behavior Contracts

### BC-001: Python Detection

**Given**: System has Python 3.13 at `/usr/bin/python3.13`
**When**: User runs `mcp-manager validate`
**Then**: Command detects Python and reports path and version

**Given**: System has no Python 3.13 installation
**When**: User runs `mcp-manager validate`
**Then**: Command exits with code 2 and lists searched paths

### BC-002: UV Configuration Validation

**Given**: `uv.toml` exists with `python-downloads = "never"` and `python-preference = "only-system"`
**When**: User runs `mcp-manager validate`
**Then**: Command reports "UV Config: Compliant"

**Given**: `uv.toml` has `python-downloads = "automatic"`
**When**: User runs `mcp-manager validate`
**Then**: Command exits with code 1 and reports violation

### BC-003: Virtual Environment Handling

**Given**: Running in venv created from system Python 3.13
**When**: User runs `mcp-manager validate`
**Then**: Command validates base Python and passes

**Given**: Running in venv created from Python 3.12
**When**: User runs `mcp-manager validate`
**Then**: Command exits with code 1 and reports venv violation

### BC-004: Multiple Python Installations

**Given**: Both `/usr/bin/python3.13` and `/usr/local/bin/python3.13` exist
**When**: User runs `mcp-manager validate`
**Then**: Command uses `/usr/bin/python3.13` (package manager priority)

### BC-005: Verbose Output

**Given**: Valid Python environment
**When**: User runs `mcp-manager validate --verbose`
**Then**: Command displays full diagnostic report including:
- Python path, version, source, distribution
- UV config file path and all settings
- Complete list of validation checks performed
- Timestamp of validation

### BC-006: Error Handling

**Given**: UV is not installed
**When**: User runs `mcp-manager validate`
**Then**: Command exits with code 2 (ERROR) and displays:
```
✗ ERROR: Validation could not complete
  UV package manager not found in PATH
  Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Given**: Permission denied reading UV config
**When**: User runs `mcp-manager validate`
**Then**: Command exits with code 2 (ERROR) and error: "Cannot read UV configuration"

## Performance Contracts

| Contract | Requirement | Measurement |
|----------|-------------|-------------|
| PC-001 | Total execution time | < 2 seconds (SC-003) |
| PC-002 | Python detection time | < 100ms |
| PC-003 | UV config parsing time | < 50ms |
| PC-004 | Output generation time | < 10ms |

## Security Contracts

| Contract | Requirement |
|----------|-------------|
| SC-001 | No privilege escalation required (normal user permissions) |
| SC-002 | Read-only operations (no file modifications) |
| SC-003 | No sensitive data logged to stdout/stderr |
| SC-004 | Path traversal prevention (validate config file paths) |

## Testing Contracts

### Unit Test Coverage

```python
# test_validation_cli.py (contract tests)

def test_validate_success_summary_output():
    """Verify summary output format on success."""
    # Setup: Valid Python 3.13, compliant UV config
    # Execute: mcp-manager validate
    # Assert: Exit code 0, output matches format

def test_validate_failure_violations_listed():
    """Verify failure output lists all violations."""
    # Setup: Python 3.13 exists, UV config non-compliant
    # Execute: mcp-manager validate
    # Assert: Exit code 1, violations in output

def test_validate_error_python_not_found():
    """Verify error output when Python 3.13 missing."""
    # Setup: No Python 3.13 installation
    # Execute: mcp-manager validate
    # Assert: Exit code 2, searched paths listed

def test_validate_verbose_complete_report():
    """Verify verbose output includes all sections."""
    # Setup: Valid environment
    # Execute: mcp-manager validate --verbose
    # Assert: Output contains all required sections

def test_validate_venv_base_python_check():
    """Verify venv base Python validation."""
    # Setup: Venv based on system Python 3.13
    # Execute: mcp-manager validate
    # Assert: Exit code 0, venv info in verbose output

def test_validate_performance_within_limits():
    """Verify execution completes within 2 seconds."""
    # Setup: Valid environment
    # Execute: time mcp-manager validate
    # Assert: Duration < 2000ms
```

### Integration Test Scenarios

```python
# test_validation_integration.py

def test_validate_with_real_uv_config():
    """Test validation against actual UV configuration."""
    # Setup: Create temporary uv.toml with test settings
    # Execute: mcp-manager validate
    # Cleanup: Remove temporary config
    # Assert: Correct detection of settings

def test_validate_python_path_priority():
    """Test Python path search priority order."""
    # Setup: Mock multiple Python installations
    # Execute: mcp-manager validate
    # Assert: Selects /usr/bin before /usr/local/bin

def test_validate_cross_distribution_paths():
    """Test Python detection across distributions."""
    # Setup: Mock different distribution environments
    # Execute: mcp-manager validate
    # Assert: Correct path selection per distribution
```

## Compatibility Contracts

| Platform | Minimum Version | Status |
|----------|----------------|--------|
| Linux (Debian/Ubuntu) | Ubuntu 20.04+ | Supported |
| Linux (Fedora/RHEL) | Fedora 35+ | Supported |
| macOS (Intel) | macOS 12+ | Supported |
| macOS (Apple Silicon) | macOS 12+ | Supported |
| Windows | N/A | Not Supported (out of scope) |

## Example Usage

### Basic Validation

```bash
$ mcp-manager validate
✓ PASS: System Python 3.13 enforcement validated
  Python: /usr/bin/python3.13 (3.13.0)
  UV Config: Compliant (only-system, downloads=never)

$ echo $?
0
```

### Verbose Validation

```bash
$ mcp-manager validate --verbose
System Python Enforcement Validation Report
============================================
[... full report ...]
Result: PASS

$ echo $?
0
```

### Failed Validation

```bash
$ mcp-manager validate
✗ FAIL: Constitution violations detected
  UV allows Python downloads (python-downloads=automatic). Must be 'manual' or 'never'.

$ echo $?
1
```

### CI/CD Integration

```bash
#!/bin/bash
# pre-commit hook or CI/CD step

if ! mcp-manager validate; then
    echo "ERROR: Python environment validation failed"
    exit 1
fi

echo "Python environment validated successfully"
```

```yaml
# GitHub Actions example
- name: Validate Python Environment
  run: |
    mcp-manager validate --verbose
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-15 | Initial contract definition |

## References

- Feature Specification: `../spec.md`
- Data Models: `../data-model.md`
- Research: `../research.md`
- Functional Requirements: FR-005 (validation command), FR-009 (logging), FR-010 (error messages)
- Success Criteria: SC-003 (< 2 second execution), SC-006 (error resolution time)
