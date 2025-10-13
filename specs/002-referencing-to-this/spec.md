# Feature Specification: MCP Manager Improvements - Three-Phase Enhancement Plan

**Feature Branch**: `002-referencing-to-this`
**Created**: 2025-10-13
**Status**: Draft
**Input**: User description: "referencing to this document /home/kkk/Apps/002-mcp-manager/improvement_plan.md - help me to determine how best to implement improvements organized into three phases prioritized by criticality and dependencies"

## Execution Flow (main)
```
1. Parse user description from Input
   → Feature request is for systematic implementation of documented improvements
2. Extract key concepts from description
   → Actors: Developers, maintainers, end-users of mcp-manager
   → Actions: Update code, refactor, configure integrations, fix documentation
   → Data: MCP server configurations, version metadata, audit paths
   → Constraints: Maintain backward compatibility, follow AGENTS.md standards
3. For each unclear aspect:
   → All aspects clarified via improvement_plan.md reference document
4. Fill User Scenarios & Testing section
   → User flows identified for each phase
5. Generate Functional Requirements
   → Each requirement derived from improvement plan criticality ratings
6. Identify Key Entities
   → MCP server configurations, Gemini CLI settings, version metadata
7. Run Review Checklist
   → All requirements testable and implementation-agnostic
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a developer maintaining the mcp-manager tool, I need to systematically address identified code quality issues, missing functionality, and configuration limitations to improve maintainability, extend platform support, and provide a better user experience for all mcp-manager users.

### Acceptance Scenarios - Phase 1: High-Priority Core Functionality

1. **MCP Server Updates**
   - **Given** an MCP server configuration exists with an npm-based package
   - **When** a user runs the update command
   - **Then** the system checks for newer versions and updates the configuration if available

2. **Gemini CLI Integration**
   - **Given** MCP servers are configured in Claude Code's configuration
   - **When** a user runs the Gemini sync command
   - **Then** the system creates/updates Gemini CLI configuration with identical server definitions
   - **And** the system configures environment variables for system-wide Gemini CLI access

### Acceptance Scenarios - Phase 2: Code Quality & Maintainability

3. **Error Handling Consistency**
   - **Given** any CLI command encounters an error
   - **When** the error is an MCPManagerError
   - **Then** the system handles it consistently without code duplication

4. **Configurable Audit Paths**
   - **Given** a user has projects in non-standard directories
   - **When** they run the audit command with custom paths
   - **Then** the system scans the specified directories instead of hardcoded defaults

5. **Documentation Accuracy**
   - **Given** a new contributor reads the README
   - **When** they check version requirements
   - **Then** they see Python >=3.11 matching pyproject.toml (not Python 3.13)

### Acceptance Scenarios - Phase 3: Polish & Organization

6. **CLI Code Organization**
   - **Given** the CLI codebase is large and monolithic
   - **When** maintainers need to find specific command logic
   - **Then** they can navigate to dedicated submodules (mcp.py, project.py, etc.)

7. **Dynamic Version Display**
   - **Given** the website displays version information
   - **When** the version is updated in pyproject.toml
   - **Then** the website automatically reflects the new version without manual edits

### Edge Cases
- What happens when Gemini CLI configuration already exists with conflicting server definitions?
  - System should intelligently merge, overwriting duplicates by name
- How does the system handle update checks for non-npm-based servers (HTTP servers)?
  - System should skip version checks for HTTP servers or provide appropriate messaging
- What if audit command is run with paths that don't exist?
  - System should validate paths and provide clear error messages
- How does error handling decorator interact with existing error handling?
  - Decorator should be applied consistently without breaking existing functionality

---

## Requirements *(mandatory)*

### Functional Requirements - Phase 1 (High Priority)

#### MCP Server Update Capability
- **FR-001**: System MUST check for newer versions of npm-based MCP servers
- **FR-002**: System MUST update MCP server configurations when newer versions are available
- **FR-003**: System MUST provide dry-run mode for update operations showing what would change
- **FR-004**: System MUST distinguish between HTTP and stdio server types for update operations
- **FR-005**: Update operations MUST preserve existing server configurations except version information

#### Gemini CLI Integration
- **FR-006**: System MUST create Gemini CLI configuration file at `~/.config/gemini/settings.json`
- **FR-007**: System MUST synchronize MCP server configurations from Claude Code to Gemini CLI
- **FR-008**: System MUST merge configurations intelligently, overwriting servers with duplicate names
- **FR-009**: System MUST configure environment variables for system-wide Gemini CLI discovery
- **FR-010**: Gemini sync command MUST create directories and files if they don't exist
- **FR-011**: System MUST maintain both Claude Code and Gemini CLI configurations in sync during add/remove operations
- **FR-012**: Init command MUST configure Gemini CLI integration as part of initial setup

### Functional Requirements - Phase 2 (Medium Priority)

#### Error Handling Consistency
- **FR-013**: System MUST handle MCPManagerError exceptions consistently across all CLI commands
- **FR-014**: Error handling MUST reduce code duplication in CLI implementation
- **FR-015**: Error messages MUST be consistent in format and helpfulness

#### Configurable Audit Paths
- **FR-016**: System MUST allow users to specify custom project directories for audit operations
- **FR-017**: System MUST support both configuration-based and command-line path specification
- **FR-018**: Audit command MUST validate provided paths before scanning
- **FR-019**: System MUST preserve backward compatibility with default paths

#### Documentation Accuracy
- **FR-020**: README MUST reflect actual Python version requirement (>=3.11) from pyproject.toml
- **FR-021**: README MUST accurately describe one-command setup capabilities
- **FR-022**: Frontend MUST accurately state the number of supported MCP servers (6, not 5)
- **FR-023**: README MUST link to valuable documentation in the docs directory

### Functional Requirements - Phase 3 (Low Priority)

#### CLI Code Organization
- **FR-024**: CLI codebase MUST be organized into logical submodules by command group
- **FR-025**: Submodule organization MUST maintain all existing CLI functionality
- **FR-026**: Import structure MUST remain clean and maintainable

#### Dynamic Version Management
- **FR-027**: Frontend MUST display version information dynamically from pyproject.toml
- **FR-028**: Version updates MUST not require manual frontend file edits
- **FR-029**: Build process MUST extract and inject version information automatically

### Key Entities *(include if feature involves data)*

- **MCP Server Configuration**: Represents server connection details including type (http/stdio), URL/command, arguments, headers, and environment variables
- **Gemini CLI Settings**: Parallel configuration structure for Gemini CLI with mcpServers section identical to Claude Code format
- **Audit Configuration**: User-specified or configured project directory paths for scanning
- **Version Metadata**: Project version information from pyproject.toml used throughout documentation and frontend
- **Update Status**: State information about available updates for MCP servers including current and latest versions

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded (three phases with priority levels)
- [x] Dependencies and assumptions identified (improvement_plan.md as source)

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked (none - all clarified via improvement_plan.md)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---

## Phase Prioritization Summary

**Phase 1 (High Priority)**: Core functionality gaps - server updates and Gemini CLI integration are critical missing features that extend platform support and maintain server currency.

**Phase 2 (Medium Priority)**: Code quality and maintainability improvements reduce technical debt, improve developer experience, and align documentation with reality.

**Phase 3 (Low Priority)**: Polish and organization improvements enhance code navigability and automate version management, but don't impact core functionality.

## Success Metrics

- Phase 1: MCP servers can be updated automatically, Gemini CLI users have access to all MCP servers
- Phase 2: Code duplication reduced by ~30+ try/except blocks, audit command works with any project structure
- Phase 3: CLI codebase organized into <400 line files, version displayed consistently without manual updates

## Dependencies and Assumptions

- Assumes npm-based servers support version checking via `npm view <package> version`
- Assumes Gemini CLI configuration structure mirrors Claude Code's format
- Assumes backward compatibility must be maintained for existing users
- Assumes all improvements must follow AGENTS.md standards for branch management and commits
