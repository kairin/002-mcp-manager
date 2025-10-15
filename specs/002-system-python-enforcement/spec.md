# Feature Specification: System Python Enforcement

**Feature Branch**: `001-system-python-enforcement`
**Created**: 2025-10-15
**Status**: Draft
**Input**: User description: "System Python enforcement: Ensure mcp-manager always uses Python 3.13 system Python (no additional installations) with UV managing all dependencies and pip operations. Prevent UV from installing additional Python interpreters. All CLI commands, tests, and MCP server configurations must use system Python via UV. Validation checks required for constitution compliance."

## Clarifications

### Session 2025-10-15

- Q: Where and how should mcp-manager store UV configuration to enforce system Python usage? → A: Project-local `.uv/config` or similar in mcp-manager directory (isolated, no system-wide impact)
- Q: What output format should the validation command use to report compliance status? → A: Summary status line with optional verbose flag for detailed diagnostics
- Q: How should the system determine priority when multiple Python 3.13 installations exist? → A: Always prefer package manager installations (check `/usr/bin` first, then `/usr/local/bin`)
- Q: How should mcp-manager behave when executed from within an active Python virtual environment? → A: Allow venv usage but only if the venv itself is based on system Python 3.13
- Q: What should be the canonical name for the constitution compliance validation command? → A: `mcp-manager validate` (concise, can be extended for other validations later)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer runs mcp-manager CLI (Priority: P1)

A developer executes any mcp-manager command on their system that has Python 3.13 installed. The tool must use the system Python 3.13 installation without attempting to download or install additional Python interpreters, regardless of UV's default behavior.

**Why this priority**: This is the core use case - every CLI invocation must respect the system Python mandate. This is the foundation that all other functionality depends on.

**Independent Test**: Can be fully tested by running `mcp-manager status` and verifying (1) the command executes successfully, (2) Python 3.13 system installation is used, and (3) no additional Python downloads/installations occur. Delivers immediate value by ensuring consistent Python environment.

**Acceptance Scenarios**:

1. **Given** a system with Python 3.13 installed and mcp-manager configured, **When** a developer runs `mcp-manager status`, **Then** the command executes using the system Python 3.13 without attempting to install additional Python versions
2. **Given** UV is managing dependencies for mcp-manager, **When** a developer runs `mcp-manager audit`, **Then** all Python operations use system Python 3.13 and UV handles package installations
3. **Given** mcp-manager is installed, **When** a developer checks which Python is being used (e.g., process information), **Then** the output confirms system Python 3.13 is in use

---

### User Story 2 - Developer runs tests (Priority: P2)

A developer runs the mcp-manager test suite to verify functionality. The tests must execute using system Python 3.13 via UV, ensuring test environment consistency with production usage.

**Why this priority**: Testing is critical for development workflow but builds on the foundation of P1. Tests validate that the system Python enforcement works correctly across all mcp-manager operations.

**Independent Test**: Can be fully tested by running `pytest tests/` and verifying (1) tests execute successfully, (2) system Python 3.13 is used for test execution, and (3) test dependencies are managed by UV without additional Python installations. Delivers confidence in code quality.

**Acceptance Scenarios**:

1. **Given** a development environment with mcp-manager source code, **When** a developer runs `pytest tests/`, **Then** all tests execute using system Python 3.13 via UV
2. **Given** test dependencies need installation, **When** UV resolves test requirements, **Then** UV installs packages for system Python 3.13 without installing additional Python interpreters
3. **Given** tests are running, **When** checking the Python executable in test processes, **Then** it points to system Python 3.13

---

### User Story 3 - MCP servers are configured and launched (Priority: P3)

When mcp-manager configures and launches MCP servers (especially stdio-based servers), those servers must operate using system Python 3.13 when applicable, maintaining consistency across the entire mcp-manager ecosystem.

**Why this priority**: This ensures system Python enforcement extends to managed MCP servers. While important for consistency, it's tertiary to core CLI operations and testing.

**Independent Test**: Can be fully tested by running `mcp-manager add <stdio-server>` followed by checking the server process. Verify (1) server launches successfully, (2) stdio servers using Python run with system Python 3.13, and (3) no additional Python installations occur. Delivers consistent Python environment across managed services.

**Acceptance Scenarios**:

1. **Given** an MCP server configuration requiring Python execution, **When** mcp-manager launches the server, **Then** the server process uses system Python 3.13
2. **Given** an MCP server needs Python packages installed, **When** mcp-manager sets up the server environment, **Then** UV manages dependencies using system Python 3.13
3. **Given** multiple MCP servers are running, **When** checking their Python environments, **Then** all Python-based servers use system Python 3.13

---

### User Story 4 - System validates constitution compliance (Priority: P1)

Developers and CI/CD systems need to verify that mcp-manager adheres to the constitutional requirement of using system Python 3.13. A validation command must check and report compliance status.

**Why this priority**: This is P1 because validation is essential for catching violations early and maintaining constitutional compliance. It's a quality gate that prevents drift from requirements.

**Independent Test**: Can be fully tested by running `mcp-manager validate` and verifying (1) command reports current Python configuration, (2) identifies any constitution violations, and (3) provides clear pass/fail status. Delivers immediate compliance verification.

**Acceptance Scenarios**:

1. **Given** mcp-manager is properly configured, **When** a developer runs `mcp-manager validate`, **Then** the command outputs a summary status line showing "PASS" with system Python 3.13 confirmation
2. **Given** a developer wants detailed diagnostics, **When** running `mcp-manager validate --verbose`, **Then** the command displays comprehensive diagnostic information including Python path, UV configuration state, and all validation checks performed
3. **Given** UV configuration might allow additional Python installations, **When** running `mcp-manager validate`, **Then** the summary status shows "FAIL" and identifies the configuration issue
4. **Given** a CI/CD pipeline runs `mcp-manager validate`, **When** mcp-manager is not using system Python 3.13, **Then** the validation fails with clear summary error and non-zero exit code

---

### Edge Cases

- What happens when Python 3.13 is not installed on the system? (System must detect this and provide clear error message requiring Python 3.13 installation)
- How does the system handle UV attempting to install Python despite configuration? (System must prevent this and fail fast with informative error)
- What if a user has multiple Python 3.13 installations (system package manager vs manual install)? (System searches `/usr/bin` first for package manager installation, then `/usr/local/bin` for manual installation, and uses the first Python 3.13 found)
- How does the system behave if UV is not installed? (System must check for UV and provide installation instructions if missing)
- What happens when running mcp-manager in a virtual environment? (System validates that the venv is based on system Python 3.13; allows execution if valid, fails with clear error if venv uses different Python version)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use Python 3.13 system installation for all operations (CLI commands, tests, MCP server configurations)
- **FR-002**: System MUST configure UV via project-local configuration files to manage all Python dependencies and pip operations using system Python 3.13 without impacting system-wide UV settings
- **FR-003**: System MUST prevent UV from installing additional Python interpreters under any circumstances
- **FR-004**: System MUST validate Python version on startup and fail with clear error message if Python 3.13 is not available
- **FR-005**: System MUST provide a `mcp-manager validate` command that outputs a summary status line showing pass/fail compliance status, with an optional `--verbose` flag to display detailed diagnostic information
- **FR-006**: System MUST detect project-local UV configuration that permits Python installation and reject such configurations
- **FR-007**: System MUST ensure all test executions use system Python 3.13 via UV
- **FR-008**: System MUST configure MCP servers (when Python-based) to use system Python 3.13
- **FR-009**: System MUST log the Python executable path being used for auditing purposes
- **FR-010**: System MUST provide clear error messages when system Python 3.13 is not found or UV is misconfigured
- **FR-011**: System MUST search for Python 3.13 in priority order: `/usr/bin/python3.13` first (package manager), then `/usr/local/bin/python3.13` (manual install), using the first installation found
- **FR-012**: System MUST detect when executed within a virtual environment and validate that the venv's base Python is system Python 3.13, failing with clear error if the venv uses a different Python version

### Key Entities

- **Python Environment Configuration**: Represents the detected system Python 3.13 installation, including executable path, version information, and validation status
- **UV Configuration**: Represents project-local UV configuration files (e.g., `.uv/config` in mcp-manager directory) that enforce system Python usage and prevent additional Python installations without affecting system-wide UV settings
- **Validation Result**: Represents the compliance check outcome, including pass/fail status, detected Python version, UV configuration state, and any violations found

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All mcp-manager CLI commands execute using system Python 3.13 with 100% consistency (no exceptions)
- **SC-002**: UV never installs additional Python interpreters during any mcp-manager operation (0 violations)
- **SC-003**: Validation command completes in under 2 seconds and correctly identifies constitution compliance status
- **SC-004**: Test suite executes using system Python 3.13 in 100% of test runs
- **SC-005**: Configuration errors related to Python environment are detected within 1 second of startup
- **SC-006**: Error messages for Python environment issues enable users to resolve problems in under 5 minutes (90% success rate)
- **SC-007**: MCP servers managed by mcp-manager use system Python 3.13 when applicable (100% of Python-based servers)

## Assumptions *(mandatory)*

- Users have Python 3.13 installed via their system package manager (apt, dnf, brew, etc.) or as a system-wide installation
- UV is installed and available in the system PATH
- The term "system Python" refers to Python installed system-wide, not in virtual environments or user-local installations
- Python 3.13 specifically is required (not 3.13+, exactly 3.13.x versions)
- Python 3.13 is located at standard paths: `/usr/bin/python3.13` (package manager) or `/usr/local/bin/python3.13` (manual install)
- Package manager installations at `/usr/bin` are preferred over manual installations at `/usr/local/bin` when multiple Python 3.13 installations exist
- Virtual environments created from system Python 3.13 are acceptable for running mcp-manager; venvs based on other Python versions are rejected
- UV supports project-local configuration files that can override default behavior without affecting system-wide settings
- The validation command will be integrated into CI/CD pipelines for continuous compliance checking

## Constraints *(mandatory)*

- Must work across Linux distributions with different Python installation conventions
- Cannot modify system Python installation or system-wide Python configuration
- Must not interfere with other Python projects or tools on the same system
- UV configuration must be project-local only (e.g., `.uv/config` within mcp-manager directory) and not modify system-wide UV settings or affect other projects
- Solution must be portable across developer machines and CI/CD environments
- Cannot require root/sudo privileges for normal operations (only for initial Python 3.13 installation if needed)

## Dependencies *(optional)*

- Python 3.13 system installation (external dependency - must be pre-installed)
- UV package manager (external dependency - installation instructions should be provided)
- System package manager (apt, dnf, brew) for Python 3.13 installation verification
- pytest for test execution (managed by UV)

## Out of Scope *(optional)*

- Installing Python 3.13 on user systems (users must install this themselves)
- Installing UV on user systems (provide instructions, but not automated installation)
- Supporting Python versions other than 3.13
- Supporting multiple Python versions simultaneously
- Managing Python versions for non-mcp-manager projects
- Creating custom Python distribution or packaging
- Supporting Windows-specific Python installations (focus on Linux/macOS initially)
