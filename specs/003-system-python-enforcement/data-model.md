# Data Model: System Python 3.13 Enforcement

**Feature**: 003-system-python-enforcement
**Date**: 2025-10-14

## Overview

This feature introduces validation entities to enforce Python 3.13 system Python requirements. All models use Pydantic v2 for validation and type safety.

## Core Entities

### 1. PythonVersionInfo

Represents Python version information from system and runtime.

**Fields**:
- `major`: int - Major version number (must be 3)
- `minor`: int - Minor version number (must be >=13)
- `micro`: int - Patch version number
- `releaselevel`: str - Release level ('final', 'alpha', 'beta', 'candidate')
- `serial`: int - Serial number for release level
- `version_string`: str - Full version string (e.g., "3.13.0")
- `executable_path`: Path - Path to Python executable
- `is_system_python`: bool - Whether this is the system Python

**Validation Rules**:
- `major` must equal 3
- `minor` must be >= 13
- `executable_path` must exist and be executable
- `version_string` must match format "X.Y.Z"

**State Transitions**: None (immutable value object)

### 2. UVConfiguration

Represents UV package manager configuration from pyproject.toml.

**Fields**:
- `python_version`: str - Configured Python version (must be "python3.13")
- `config_source`: Path - Path to pyproject.toml
- `is_valid`: bool - Whether configuration meets requirements
- `detected_at`: datetime - When configuration was validated

**Validation Rules**:
- `python_version` must exactly match "python3.13"
- `config_source` must exist and be readable
- `config_source` must be valid TOML format

**State Transitions**: None (snapshot of configuration at validation time)

### 3. MCPServerConfig

Represents a single MCP server configuration.

**Fields**:
- `name`: str - Server name (e.g., "markitdown", "github")
- `type`: Literal["stdio", "http"] - Server connection type
- `command`: Optional[str] - Command for stdio servers
- `args`: List[str] - Arguments for stdio servers
- `url`: Optional[str] - URL for HTTP servers
- `headers`: Dict[str, str] - Headers for HTTP servers
- `uses_uv`: bool - Whether stdio server uses UV (computed)

**Validation Rules**:
- `name` must not be empty
- If `type` == "stdio": `command` and `args` required
- If `type` == "http": `url` required
- `uses_uv` is True only if `command` == "uv" and "run" in `args`

**State Transitions**: None (read-only configuration)

### 4. ValidationResult

Represents the result of a validation check.

**Fields**:
- `check_name`: str - Name of the validation check
- `passed`: bool - Whether validation passed
- `message`: str - Human-readable result message
- `details`: Optional[Dict[str, Any]] - Additional details about validation
- `timestamp`: datetime - When validation was performed
- `severity`: Literal["info", "warning", "error", "critical"] - Result severity

**Validation Rules**:
- `check_name` must not be empty
- `message` must not be empty
- If `passed` is False, `severity` must be "error" or "critical"

**State Transitions**: None (immutable validation result)

### 5. ConstitutionCheckResult

Aggregates multiple validation results for constitution compliance.

**Fields**:
- `principle_number`: int - Constitution principle number (1-9)
- `principle_name`: str - Principle name
- `checks`: List[ValidationResult] - Individual validation results
- `overall_passed`: bool - Whether all checks passed (computed)
- `failed_checks`: List[ValidationResult] - Only failed checks (computed)
- `validation_timestamp`: datetime - When principle was validated

**Validation Rules**:
- `principle_number` must be between 1 and 9
- `checks` must not be empty
- `overall_passed` is True only if all checks passed

**State Transitions**:
```
PENDING → VALIDATING → (PASS | FAIL)
```

### 6. PythonEnforcementStatus

Top-level status object for system Python enforcement.

**Fields**:
- `python_version_valid`: bool - Python 3.13+ check result
- `uv_config_valid`: bool - UV configuration check result
- `mcp_servers_valid`: bool - MCP server configurations check result
- `constitution_compliant`: bool - Overall constitution compliance
- `validation_results`: List[ValidationResult] - All validation results
- `recommendations`: List[str] - Actionable recommendations for failures
- `validated_at`: datetime - Validation timestamp

**Validation Rules**:
- `constitution_compliant` is True only if all three checks valid
- `recommendations` populated only when `constitution_compliant` is False

**State Transitions**:
```
UNKNOWN → CHECKING → (COMPLIANT | NON_COMPLIANT | ERROR)
```

## Entity Relationships

```
PythonEnforcementStatus
├── Contains: List[ValidationResult]
│   └── Each ValidationResult references a specific check
├── Aggregates: PythonVersionInfo validation
├── Aggregates: UVConfiguration validation
└── Aggregates: List[MCPServerConfig] validation

ConstitutionCheckResult
├── Contains: List[ValidationResult]
└── Groups by: Constitution Principle

MCPServerConfig
└── Referenced by: ValidationResult (MCP server validation)
```

## Validation Workflows

### Python Version Validation Workflow
1. Detect runtime Python version (sys.version_info)
2. Detect system Python version (subprocess: python --version)
3. Create PythonVersionInfo entity
4. Validate major >= 3, minor >= 13
5. Return ValidationResult

### UV Configuration Validation Workflow
1. Locate pyproject.toml
2. Parse [tool.uv] section
3. Create UVConfiguration entity
4. Validate python = "python3.13"
5. Return ValidationResult

### MCP Server Validation Workflow
1. Load ~/.claude.json
2. Parse mcpServers section
3. Create List[MCPServerConfig]
4. For each stdio server:
   - Validate command == "uv"
   - Validate "run" in args
5. Aggregate ValidationResult list

### Constitution Compliance Validation Workflow
1. Run all validation workflows
2. Create ConstitutionCheckResult for Principle VII
3. Create PythonEnforcementStatus
4. Generate recommendations for failures
5. Return status

## Persistence

**Note**: This feature does NOT persist validation results to a database. All validation is ephemeral and runs on-demand.

**Rationale**:
- Validation is fast (<200ms total)
- No historical tracking requirements
- Avoids storage complexity
- Simplifies deployment

## Error Handling

**Custom Exceptions** (defined in `exceptions.py`):

```python
class PythonVersionError(MCPManagerError):
    """Python version does not meet requirements"""

class UVConfigError(MCPManagerError):
    """UV configuration invalid or missing"""

class MCPConfigError(MCPManagerError):
    """MCP server configuration violates requirements"""

class ConstitutionViolationError(MCPManagerError):
    """Constitution principle violated"""
```

## Performance Considerations

- **PythonVersionInfo**: <10ms to create (runtime inspection)
- **UVConfiguration**: <50ms to create (file I/O + TOML parsing)
- **MCPServerConfig list**: <100ms to create (JSON parsing + validation)
- **Total validation**: <200ms for complete constitution check

Target: All validation operations complete in <200ms to meet constraint requirements.

---

**Data Model Status**: ✅ **COMPLETE** - All entities defined with validation rules
