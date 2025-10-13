# Research: System Python 3.13 Enforcement

**Feature**: 003-system-python-enforcement
**Date**: 2025-10-14
**Status**: Complete

## Executive Summary

All technical decisions are clear based on constitution v1.2.0 updates and existing project architecture. No research unknowns exist - implementation is straightforward extension of existing validators with constitutional enforcement.

## Research Areas

### 1. UV Python Interpreter Pinning

**Decision**: Use `[tool.uv] python = "python3.13"` in pyproject.toml

**Rationale**:
- UV respects explicit `python` configuration in `[tool.uv]` section
- Prevents auto-discovery of alternative Python versions
- Blocks UV from downloading additional interpreters
- Already implemented in constitution amendment

**Alternatives considered**:
- Environment variables (`UV_PYTHON`): Less permanent, requires shell configuration
- `.python-version` file: UV may still auto-discover if misconfigured
- Hard-coded paths: Not portable across fleet nodes

**References**:
- UV documentation: https://docs.astral.sh/uv/concepts/python-versions/
- Constitution v1.2.0 Principle I (UV-First Development)

### 2. Python Version Detection Strategy

**Decision**: Use `sys.version_info` for runtime checks, `python --version` for system validation

**Rationale**:
- `sys.version_info` provides structured version tuple for comparisons
- Subprocess call to `python --version` verifies system Python path
- Combination ensures both runtime and system Python match expectations

**Alternatives considered**:
- `platform.python_version()`: Less structured, string parsing required
- Only runtime checks: Misses system Python misconfiguration
- Only system checks: Misses active interpreter issues

**Implementation**:
```python
import sys
import subprocess

def validate_python_version():
    # Runtime check
    if sys.version_info < (3, 13):
        raise PythonVersionError(f"Python 3.13+ required, found {sys.version}")

    # System Python check
    result = subprocess.run(["python", "--version"], capture_output=True, text=True)
    # Parse and validate matches runtime version
```

### 3. UV Configuration Validation

**Decision**: Parse pyproject.toml and validate `[tool.uv]` section exists with correct `python` value

**Rationale**:
- TOML parsing via built-in `tomllib` (Python 3.11+)
- Validates both presence and correctness of configuration
- Can detect misconfigurations before they cause issues

**Alternatives considered**:
- UV CLI inspection: No direct UV command to show config
- File system search for UV cache: Fragile, implementation-dependent
- Runtime UV behavior test: Too slow for pre-flight validation

**Implementation**:
```python
import tomllib
from pathlib import Path

def validate_uv_config():
    pyproject_path = Path("pyproject.toml")
    with pyproject_path.open("rb") as f:
        config = tomllib.load(f)

    uv_config = config.get("tool", {}).get("uv", {})
    python_config = uv_config.get("python")

    if python_config != "python3.13":
        raise UVConfigError(f"Expected python3.13, found {python_config}")
```

### 4. MCP Server Configuration Validation

**Decision**: Parse `~/.claude.json` and validate stdio servers use UV command pattern

**Rationale**:
- MCP configurations already centralized in `~/.claude.json`
- stdio servers that don't use UV bypass system Python enforcement
- Validation ensures all servers comply with Principle I (UV-First)

**Alternatives considered**:
- Runtime server inspection: Too late (server already misconfigured)
- Process monitoring: Complex, requires active servers
- Configuration backup validation: Reactive, not preventive

**Implementation**:
```python
def validate_mcp_servers():
    claude_config = Path.home() / ".claude.json"
    with claude_config.open() as f:
        config = json.load(f)

    for name, server in config.get("mcpServers", {}).items():
        if server.get("type") == "stdio":
            command = server.get("command")
            if command != "uv":
                raise MCPConfigError(f"Server {name} does not use UV: {command}")
```

### 5. Pre-commit Hook Integration

**Decision**: Add pre-commit hook that runs Python/UV validation before commits

**Rationale**:
- Constitutional requirement (Principle VIII: file placement validation in pre-commit)
- Prevents commits that violate Python 3.13 requirement
- Fast validation (<200ms total) doesn't slow down workflow

**Alternatives considered**:
- CI-only validation: Too late (code already committed locally)
- Manual validation: Error-prone, not enforceable
- Git hooks without pre-commit framework: Harder to maintain/distribute

**Implementation**:
```yaml
# .pre-commit-config.yaml addition
- repo: local
  hooks:
    - id: validate-python-enforcement
      name: Validate Python 3.13 Enforcement
      entry: uv run python -m mcp_manager.validators.constitution_validator
      language: system
      pass_filenames: false
      always_run: true
```

### 6. Constitution Compliance Validation

**Decision**: Create `constitution_validator.py` that checks all 9 principles programmatically

**Rationale**:
- Automates manual constitution checks
- Provides actionable failure messages
- Can be run via CLI or pre-commit hook
- Validates Principle VII enforcement specifically

**Alternatives considered**:
- Manual checklists: Not enforceable, human error
- Linting-only approach: Can't validate runtime behavior
- External tools: None exist for custom constitutional requirements

**Implementation**:
```python
class ConstitutionValidator:
    def validate_principle_vii(self):
        """Validate Cross-Platform Compatibility (Python 3.13)"""
        checks = [
            self._check_python_version(),
            self._check_uv_config(),
            self._check_pyproject_requirements(),
        ]
        return all(checks)
```

## Implementation Path

Based on research, implementation follows this sequence:

1. **Core Validators** (independent, parallel):
   - `python_validator.py`: Python version checks
   - `uv_validator.py`: UV configuration checks
   - `constitution_validator.py`: Orchestrates all checks

2. **Data Models**:
   - `validation_models.py`: Pydantic models for validation results

3. **CLI Integration**:
   - `validate_commands.py`: Typer commands for manual validation

4. **Pre-commit Integration**:
   - Update `.pre-commit-config.yaml` with validation hook

5. **Testing** (TDD approach):
   - Contract tests define validator interfaces
   - Unit tests for each validator
   - Integration tests for end-to-end validation

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| UV behavior changes in future versions | Medium | Pin UV version in dependencies, document UV version requirements |
| System Python not available on node | High | Fail-fast with clear error message, document Ubuntu 25.04 requirement |
| Performance overhead from validation | Low | Validation <200ms, only runs on init/pre-commit, not every CLI call |
| False positives in validation | Medium | Comprehensive test suite, dry-run mode for validation |

## Success Criteria

- ✅ All 15 functional requirements (FR-001 to FR-015) satisfied
- ✅ Constitution v1.2.0 Principle VII enforced programmatically
- ✅ Zero additional Python installations on any fleet node
- ✅ Pre-commit validation blocks non-compliant commits
- ✅ CLI validation commands provide actionable feedback
- ✅ Integration tests verify end-to-end enforcement

## References

- Constitution v1.2.0: `.specify/memory/constitution.md`
- Feature Specification: `./spec.md`
- UV Documentation: https://docs.astral.sh/uv/
- Python sys module: https://docs.python.org/3/library/sys.html
- pyproject.toml format: https://peps.python.org/pep-0621/

---

**Research Status**: ✅ **COMPLETE** - All decisions made, no unknowns remain
