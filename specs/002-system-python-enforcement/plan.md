# Implementation Plan: System Python Enforcement

**Branch**: `001-system-python-enforcement` | **Date**: 2025-10-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-system-python-enforcement/spec.md`

**Note**: This plan addresses the constitutional requirement to enforce system Python 3.13 usage across all mcp-manager operations, preventing UV from installing additional Python interpreters.

## Summary

This feature enforces strict usage of system Python 3.13 across the entire mcp-manager project by:
1. Detecting and validating system Python 3.13 installation at startup
2. Configuring UV via project-local settings to use system Python exclusively
3. Preventing UV from downloading or installing additional Python interpreters
4. Providing a `mcp-manager validate` command for constitution compliance verification
5. Supporting virtual environments created from system Python 3.13 while rejecting others

**Technical Approach**: Python environment detection module + UV configuration management + startup validation hooks + CLI validation command with summary/verbose output modes.

## Technical Context

**Language/Version**: Python 3.13 (system installation required)
**Primary Dependencies**:
- UV (package manager - external, user-installed)
- typer (CLI framework - managed by UV)
- pydantic v2 (configuration validation - managed by UV)
- rich (CLI output formatting - managed by UV)
- pytest (testing - managed by UV)

**Storage**: File-based (project-local UV configuration at `.uv/config` or `uv.toml`)
**Testing**: pytest with contract tests for validation command, integration tests for UV behavior, unit tests for Python detection
**Target Platform**: Linux (primary), macOS (secondary) - focus on package manager Python installations
**Project Type**: Single project (CLI tool)

**Performance Goals**:
- Python detection: <100ms on startup
- Validation command: <2 seconds total execution
- Configuration validation: <1 second

**Constraints**:
- Must use exactly Python 3.13 (not 3.13+)
- Project-local UV configuration only (no system-wide modification)
- No root/sudo required for normal operations
- Must not interfere with other UV-managed projects
- Cross-distribution compatibility (apt, dnf, brew package managers)

**Scale/Scope**:
- Single mcp-manager project
- 12 functional requirements (FR-001 through FR-012)
- 4 priority user stories
- 5 edge cases to handle

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Status**: Template constitution not yet ratified - using CLAUDE.md requirements as reference

**CLAUDE.md Compliance**:
✅ **Python 3.11+ Requirement**: Feature enforces Python 3.13 (exceeds minimum)
✅ **Modern Type Hints**: All detection/validation code will use full type annotations
✅ **Pydantic v2**: Configuration models will use Pydantic v2
✅ **Rich CLI Output**: Validation command uses Rich for formatted output
✅ **Typer CLI**: Validation command implemented via Typer
✅ **Code Quality**: black, ruff, mypy, pytest required before commits
✅ **Branch Preservation**: Feature branch `001-system-python-enforcement` preserved
✅ **Test Coverage**: >80% coverage required for all Python detection/validation modules

**No Constitution Violations**: All requirements align with CLAUDE.md mandates.

## Project Structure

### Documentation (this feature)

```
specs/002-system-python-enforcement/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (completed)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── validation_cli.md  # Validation command contract
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created yet)
```

### Source Code (repository root)

```
src/mcp_manager/
├── __init__.py          # Package exports
├── cli.py               # CLI interface (existing)
├── core.py              # Core MCP management (existing)
├── models.py            # Pydantic models (existing)
├── exceptions.py        # Custom exceptions (existing)
├── config.py            # Configuration management (existing)
├── health.py            # Health monitoring (existing)
├── utils.py             # Utility functions (existing)
├── python_env.py        # NEW: Python environment detection
├── uv_config.py         # NEW: UV configuration management
└── validators.py        # NEW: Validation command implementation

tests/
├── contract/
│   └── test_validation_cli.py  # NEW: Validation command contract tests
├── integration/
│   ├── test_uv_integration.py  # NEW: UV behavior integration tests
│   └── test_python_detection.py # NEW: Python detection integration tests
└── unit/
    ├── test_python_env.py      # NEW: Python env unit tests
    ├── test_uv_config.py       # NEW: UV config unit tests
    └── test_validators.py      # NEW: Validators unit tests

.uv/
└── config               # NEW: Project-local UV configuration (or uv.toml at root)
```

**Structure Decision**: Single project structure is appropriate for mcp-manager CLI tool. New modules added to existing `src/mcp_manager/` package to maintain cohesion. UV configuration stored project-locally to avoid system-wide impacts per FR-002.

## Complexity Tracking

*No complexity violations detected - all requirements align with constitution principles.*

## Phase 0: Research & Technology Decisions

### Research Questions

Based on Technical Context unknowns and feature requirements:

1. **UV Configuration Mechanism**: How does UV support project-local Python enforcement?
   - Research UV's configuration file format (`.uv/config` vs `uv.toml`)
   - Identify specific settings to prevent Python installation
   - Verify project-local vs system-wide configuration precedence

2. **Python Detection Strategy**: Best practices for detecting system Python 3.13
   - Standard paths across distributions (Debian/Ubuntu, Fedora/RHEL, macOS/Homebrew)
   - Version verification methods (parsing `--version` output vs `sys.version_info`)
   - Virtual environment base Python detection (reading pyvenv.cfg)

3. **UV Python Enforcement**: How to configure UV to strictly use specific Python
   - UV's `--python` flag vs configuration file settings
   - Preventing automatic Python downloads/installations
   - Error handling when configured Python unavailable

4. **Validation Command Best Practices**: CLI validation command patterns
   - Exit code conventions (0=pass, non-zero=fail)
   - Structured output formats (summary vs verbose)
   - Integration with CI/CD systems (machine-readable output options)

5. **Cross-Distribution Compatibility**: Package manager Python path differences
   - Debian/Ubuntu: `/usr/bin/python3.13`
   - Fedora/RHEL: `/usr/bin/python3.13`
   - macOS Homebrew: `/usr/local/bin/python3.13` or `/opt/homebrew/bin/python3.13`
   - Manual installs: `/usr/local/bin/python3.13`

### Research Completion

✅ **All research questions resolved**. See [research.md](research.md) for complete findings.

**Key Decisions Made**:
1. **UV Configuration**: Use `uv.toml` with `python-preference="only-system"` + `python-downloads="never"`
2. **Python Detection**: Priority-ordered path search (`/usr/bin` → `/usr/local/bin` → `/opt/homebrew/bin`)
3. **Validation Output**: Summary mode (default) + optional `--verbose` flag
4. **Venv Handling**: Parse `pyvenv.cfg` to validate base Python
5. **Cross-Platform**: Distribution detection for targeted error messages

## Phase 1: Design & Contracts

### Data Model (Completed)

✅ **Created** [data-model.md](data-model.md)

**Pydantic v2 Models Defined**:
1. **PythonEnvironment**: Immutable system Python 3.13 representation
   - Fields: executable_path, version, source, distribution, is_valid, in_virtualenv, venv_base_python
   - Validators: Version must be (3, 13, x), path must exist
   - Properties: version_string, is_package_manager_install

2. **UVConfiguration**: Mutable UV config with compliance checking
   - Fields: config_file_path, python_downloads, python_preference, python_version_pinned, is_compliant, compliance_violations
   - Methods: check_compliance(), prevents_python_downloads, uses_only_system_python
   - Validators: Config file must exist

3. **ValidationResult**: Aggregated validation outcome
   - Fields: status (PASS/FAIL/ERROR), python_environment, uv_configuration, errors, warnings, checks_performed, timestamp
   - Methods: to_summary(), to_verbose()
   - Properties: exit_code, has_violations

### API Contracts (Completed)

✅ **Created** [contracts/validation_cli.md](contracts/validation_cli.md)

**Command**: `mcp-manager validate [--verbose]`

**Exit Codes**:
- 0: PASS (all checks passed)
- 1: FAIL (constitutional violations detected)
- 2: ERROR (unable to complete validation)

**Output Modes**:
- **Summary** (default): Single-line status with Python path and UV config summary
- **Verbose** (`--verbose`): Full diagnostic report with all checks, timestamps, detailed info

**Behavior Contracts**: 6 contracts defined (BC-001 through BC-006)
**Performance Contracts**: < 2 seconds total execution (SC-003)
**Security Contracts**: Read-only, no privilege escalation, path traversal prevention

### Quickstart Guide (Completed)

✅ **Created** [quickstart.md](quickstart.md)

**Contents**:
- Architecture overview with component diagram
- 5-minute setup instructions
- Key modules implementation guide (python_env.py, uv_config.py, validators.py, cli.py)
- 7-day development workflow
- Testing strategy (unit, integration, contract tests)
- Debugging tips and common tasks

### Agent Context Update (Completed)

✅ **Updated** `/CLAUDE.md` with feature technologies:
- Language: Python 3.13 (system installation required)
- Storage: File-based (project-local UV configuration)
- Project Type: Single project (CLI tool)

## Phase 1 Completion Summary

**Artifacts Created**:
- ✅ [research.md](research.md) - Technology research and decisions
- ✅ [data-model.md](data-model.md) - Pydantic v2 model specifications
- ✅ [contracts/validation_cli.md](contracts/validation_cli.md) - CLI command contract
- ✅ [quickstart.md](quickstart.md) - Developer implementation guide
- ✅ CLAUDE.md - Agent context updated

**Constitution Check (Post-Design)**:

Re-evaluating against CLAUDE.md requirements:

✅ **Python 3.13 Enforcement**: Aligns with Python 3.11+ requirement (exceeds minimum)
✅ **Pydantic v2 Models**: All models use Pydantic v2 (PythonEnvironment, UVConfiguration, ValidationResult)
✅ **Type Annotations**: Full type hints in all model definitions and function signatures
✅ **Rich CLI Output**: ValidationResult provides formatted output (summary + verbose modes)
✅ **Testing Strategy**: Unit, integration, and contract tests defined with >80% coverage target
✅ **Code Quality Gates**: black, ruff, mypy checks required before commits
✅ **UV Integration**: Project-local configuration prevents system-wide impacts (FR-002)

**No New Violations**: Design maintains full constitutional compliance.

## Next Steps

This planning phase is complete. To continue with implementation:

```bash
# Generate task breakdown
/speckit.tasks

# Begin implementation
/speckit.implement
```

The `/speckit.tasks` command will create `tasks.md` with actionable task breakdown based on this plan, data models, and contracts.

