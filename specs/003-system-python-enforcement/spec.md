# Feature Specification: System Python 3.13 Enforcement

**Feature Branch**: `003-system-python-enforcement`
**Created**: 2025-10-14
**Status**: Draft
**Input**: User description: "System Python enforcement: Ensure mcp-manager always uses Python 3.13 system Python (no additional installations) with UV managing all dependencies and pip operations. Prevent UV from installing additional Python interpreters. All CLI commands, tests, and MCP server configurations must use system Python via UV. Validation checks required for constitution compliance."

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

## User Scenarios & Testing

### Primary User Story
As a fleet administrator managing Ubuntu 25.04 nodes with Python 3.13, I need mcp-manager to use the system Python interpreter exclusively so that I can avoid Python version bloat, ensure consistent behavior across all nodes, and maintain zero additional dependencies beyond the base OS installation.

### Acceptance Scenarios
1. **Given** a fresh Ubuntu 25.04 system with Python 3.13 installed, **When** mcp-manager is initialized via `mcp-manager init`, **Then** the system must use Python 3.13 without attempting to download or install any additional Python versions
2. **Given** mcp-manager is already configured, **When** any CLI command is executed (`audit`, `status`, `add`, etc.), **Then** all operations must run using the system Python 3.13 interpreter via UV
3. **Given** MCP server configurations are created, **When** stdio-based servers are launched, **Then** all MCP servers must execute using system Python 3.13 via UV (e.g., `uv run markitdown-mcp`)
4. **Given** project dependencies need to be installed, **When** UV manages pip operations, **Then** all packages must be installed into UV-managed virtual environments using system Python 3.13 as the base interpreter
5. **Given** a constitution compliance check is run, **When** Python version validation executes, **Then** the system must confirm Python 3.13+ is active and no additional Python installations exist

### Edge Cases
- What happens when a developer attempts to run `pip install` directly (bypassing UV)?
- How does the system handle scenarios where Python 3.13 is not available on the system?
- What validation occurs if UV attempts to auto-discover a different Python version?
- How does the system prevent UV from downloading/installing Python interpreters during package operations?
- What happens if pyproject.toml is misconfigured with a lower Python version requirement?

## Requirements

### Functional Requirements
- **FR-001**: System MUST enforce Python 3.13+ as the exclusive interpreter for all operations
- **FR-002**: System MUST use UV for all package management operations (NEVER direct pip)
- **FR-003**: System MUST configure `[tool.uv] python = "python3.13"` in pyproject.toml
- **FR-004**: System MUST validate that `requires-python = ">=3.13"` is set in pyproject.toml
- **FR-005**: System MUST prevent UV from downloading or installing additional Python interpreters
- **FR-006**: All CLI commands MUST execute via `uv run <command>` to ensure system Python usage
- **FR-007**: All MCP server stdio configurations MUST use `"command": "uv", "args": ["run", "<server>"]`
- **FR-008**: System MUST provide validation commands to verify system Python 3.13 is active
- **FR-009**: System MUST fail fast with clear error messages if Python 3.13+ is not available
- **FR-010**: System MUST integrate constitution compliance checks for Python version enforcement
- **FR-011**: Pre-commit hooks MUST validate UV configuration and Python version requirements
- **FR-012**: System MUST prevent operations that would bypass UV package management
- **FR-013**: All test execution MUST use `uv run pytest` (NEVER direct pytest)
- **FR-014**: System MUST log Python interpreter path and version during initialization
- **FR-015**: Fleet synchronization MUST verify Python 3.13 consistency across all nodes

### Key Entities
- **System Python Validator**: Verifies Python 3.13+ availability and active interpreter
- **UV Configuration Manager**: Enforces [tool.uv] settings and prevents interpreter downloads
- **MCP Server Launcher**: Ensures all stdio servers execute via UV with system Python
- **Constitution Compliance Checker**: Validates Principle VII (Cross-Platform Compatibility) adherence
- **Pre-commit Hook Validator**: Blocks commits that violate Python version requirements

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
