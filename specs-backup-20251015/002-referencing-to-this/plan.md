# Implementation Plan: MCP Manager Improvements - Three-Phase Enhancement

**Branch**: `002-referencing-to-this` | **Date**: 2025-10-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/kkk/Apps/002-mcp-manager/specs/002-referencing-to-this/spec.md`

## Execution Flow (/plan command scope)
```
1. ✅ Load feature spec from Input path
2. ✅ Fill Technical Context (no NEEDS CLARIFICATION detected)
   → Project Type: Single Python CLI application
   → Structure Decision: Standard Python package with src/ layout
3. ✅ Fill Constitution Check section
4. ✅ Evaluate Constitution Check section
   → All principles compliant
   → Update Progress Tracking: Initial Constitution Check PASS
5. ➡️  Execute Phase 0 → research.md
6. ➡️  Execute Phase 1 → contracts, data-model.md, quickstart.md, AGENTS.md update
7. ➡️  Re-evaluate Constitution Check section
8. ➡️  Plan Phase 2 → Describe task generation approach
9. STOP - Ready for /tasks command
```

## Summary

This feature implements a three-phase enhancement plan for MCP Manager addressing **29 functional requirements** across core functionality (MCP server updates, Gemini CLI integration), code quality improvements (error handling, configurable paths, documentation fixes), and polish (CLI reorganization, dynamic versioning). The improvements systematically address identified technical debt while maintaining backward compatibility and following constitutional principles for UV-first development, branch preservation, and security by design.

**Primary Goals**:
1. **Phase 1**: Add missing MCP server update capability + multi-platform Gemini CLI integration
2. **Phase 2**: Centralize error handling, make audit paths configurable, fix documentation accuracy
3. **Phase 3**: Reorganize CLI into submodules, implement dynamic version management

## Technical Context

**Language/Version**: Python 3.11+ (specified in pyproject.toml)
**Primary Dependencies**: Typer 0.12+, Rich 13.0+, httpx 0.27+, Pydantic 2.0+
**Storage**: File-based configuration (~/.claude.json, ~/.config/gemini/settings.json)
**Testing**: pytest with 80% coverage requirement, black/ruff/mypy for quality gates
**Target Platform**: Ubuntu 25.04 + Python 3.13 fleet (constitution requirement)
**Project Type**: Single Python CLI application with package structure
**Performance Goals**:
  - CLI commands complete in <2 seconds
  - Health checks <5 seconds
  - Update operations support dry-run mode
**Constraints**:
  - Backward compatibility with existing configurations
  - Zero downtime operations (no breaking changes)
  - UV-first package management (constitutional requirement)
  - Branch preservation with datetime naming
**Scale/Scope**:
  - 29 functional requirements across 3 phases
  - 6 MCP servers to manage (context7, shadcn, github, playwright, hf-mcp-server, markitdown)
  - ~1552 lines of CLI code to refactor
  - Support for fleet-wide synchronization across multiple nodes

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. UV-First Development:**
- [x] All Python operations use `uv` (existing codebase compliant)
- [x] MCP server configs specify `"command": "uv", "args": ["run", ...]` (MarkItDown uses UV)
- [x] Testing uses `uv run pytest` (pyproject.toml configured)

**II. Global Configuration First:**
- [x] MCP servers registered in `~/.claude.json` (existing implementation)
- [x] Configuration backup created before modifications (existing via migrate command)
- [x] Health validation after config changes (existing health check system)

**III. Zero Downtime Operations:**
- [x] Pre-flight validation before configuration changes (existing)
- [x] Atomic updates with rollback capability (to be maintained in Phase 1-2)
- [x] Post-modification health checks pass (existing)

**IV. Branch Preservation:**
- [x] Branch naming: `YYYYMMDD-HHMMSS-type-description` (this branch: 002-referencing-to-this)
- [x] NO branch deletion (workflow compliant)
- [x] Git workflow includes Claude Code co-authorship (standard practice)

**V. GitHub Pages Protection:**
- [x] `npm run build` executed before commits affecting website (existing scripts)
- [x] Required files present: `docs/index.html`, `docs/_astro/`, `docs/.nojekyll`
- [x] Astro config uses correct `site`, `base`, `outDir` settings (existing)

**VI. Security by Design:**
- [x] Credentials stored in `~/.claude.json` with 0600 permissions (existing)
- [x] Environment variable substitution for sensitive values (existing pattern)
- [x] Audit logging for credential access (Phase 2 will maintain/enhance)

**VII. Cross-Platform Compatibility:**
- [x] Ubuntu 25.04 + Python 3.13 standardization (constitution requirement)
- [x] UV package manager for environment management (enforced)
- [x] Fleet-wide synchronization capability (existing fleet commands)

**VIII. Repository Organization:**
- [x] Documentation in `docs/` directory (existing structure)
- [x] Scripts in `scripts/` subdirectories (existing: setup/, deployment/, verify/)
- [x] Source code in `src/mcp_manager/` package (existing)
- [x] No root folder clutter (compliant)

**Initial Assessment**: ✅ PASS - All constitutional principles satisfied

## Project Structure

### Documentation (this feature)
```
specs/002-referencing-to-this/
├── spec.md              # Feature specification (✅ complete)
├── plan.md              # This file (✅ in progress)
├── research.md          # Phase 0 output (⏳ to be created)
├── data-model.md        # Phase 1 output (⏳ to be created)
├── quickstart.md        # Phase 1 output (⏳ to be created)
├── contracts/           # Phase 1 output (⏳ to be created)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
mcp-manager/
├── src/mcp_manager/          # Main Python package
│   ├── __init__.py          # Package exports
│   ├── cli.py               # CLI interface (1552 lines - Phase 3 will split)
│   ├── core.py              # Core MCP management (Phase 1: implement update methods)
│   ├── models.py            # Pydantic models
│   ├── exceptions.py        # Custom exceptions (Phase 2: add decorator base)
│   ├── config.py            # Configuration management (Phase 2: add audit paths config)
│   ├── health.py            # Health monitoring
│   ├── utils.py             # Utility functions
│   ├── gemini_integration.py  # NEW: Gemini CLI integration (Phase 1)
│   ├── version_utils.py     # NEW: Version management utilities (Phase 3)
│   └── error_handling.py    # NEW: Centralized error decorator (Phase 2)
│
├── tests/                   # Test suite
│   ├── contract/           # Contract tests (Phase 1)
│   ├── integration/        # Integration tests
│   └── unit/               # Unit tests
│       ├── test_gemini_integration.py  # NEW (Phase 1)
│       ├── test_update_operations.py   # NEW (Phase 1)
│       └── test_error_handling.py      # NEW (Phase 2)
│
├── docs/                   # Documentation
│   ├── CHANGELOG.md       # (Phase 2: update version references)
│   ├── README.md          # (Phase 2: fix Python version, expand setup guide)
│   └── guides/            # Reference guides
│
├── website/src/           # Astro website source
│   ├── components/
│   │   └── Features.astro  # (Phase 2: update 5→6 servers)
│   └── pages/
│       └── index.astro     # (Phase 3: dynamic version injection)
│
└── pyproject.toml         # Python metadata (Python >=3.11 correctly specified)
```

**Structure Decision**: Standard single Python project with `src/` layout. This is appropriate for a CLI tool with comprehensive functionality organized as a Python package. The structure supports:
- Clear separation between source (`src/`), tests (`tests/`), and documentation (`docs/`)
- Modular CLI organization ready for Phase 3 refactoring
- Integration testing with contract-driven development
- Website source in `website/src/` with build output to `docs/` for GitHub Pages

---

## Phase 0: Outline & Research

**Research Tasks**:

1. **MCP Server Update Mechanisms**
   - Research npm version checking APIs: `npm view <package> version`
   - Investigate uv-compatible update patterns for Python packages
   - Determine version comparison libraries (semver)
   - Document dry-run implementation patterns

2. **Gemini CLI Configuration Structure**
   - Research Gemini CLI settings.json format
   - Verify mcpServers configuration compatibility with Claude Code
   - Document GEMINI_CLI_SYSTEM_SETTINGS_PATH environment variable usage
   - Identify shell profile detection patterns (.bashrc, .zshrc, .profile)

3. **Error Handling Patterns**
   - Research Typer callback/decorator patterns for CLI error handling
   - Document MCPManagerError exception hierarchy requirements
   - Investigate Rich error display best practices
   - Identify try-except consolidation opportunities in cli.py

4. **Configuration Path Management**
   - Research configurable path storage options (config file vs CLI args)
   - Document Path validation patterns with pathlib
   - Identify backward compatibility requirements for default paths
   - Explore XDG base directory specification for cross-platform config

5. **Dynamic Version Management**
   - Research Astro environment variable injection at build time
   - Investigate toml parsing libraries for pyproject.toml
   - Document package.json vs pyproject.toml synchronization strategies
   - Identify build script integration points

6. **CLI Modularization**
   - Research Typer sub-application architecture
   - Document import restructuring requirements
   - Identify logical command groupings (mcp, project, fleet, agent, office)
   - Explore file size targets for maintainability (<400 lines per module)

**Output Format** (research.md):
```markdown
# Research: MCP Manager Improvements

## 1. MCP Server Update Mechanisms

**Decision**: Use `npm view` for npm packages, skip HTTP servers
**Rationale**: npm provides JSON output parseable via subprocess, HTTP servers don't have version endpoints
**Implementation**: subprocess.run(['npm', 'view', package, 'version'], capture_output=True)
**Alternatives Considered**: npm-check-updates (too heavy), package.json parsing (unreliable)

## 2. Gemini CLI Configuration

**Decision**: Mirror Claude Code ~/.claude.json structure in ~/.config/gemini/settings.json
**Rationale**: Gemini CLI uses identical mcpServers schema, documented in Gemini CLI repo
**Environment Variable**: GEMINI_CLI_SYSTEM_SETTINGS_PATH="$HOME/.config/gemini/settings.json"
**Shell Detection**: Check for ~/.bashrc, ~/.zshrc, ~/.profile in that order

[... continues for all research areas ...]
```

---

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

### 1. Data Model (data-model.md)

**Entities** (from spec.md Key Entities):

#### GeminiCLISettings
```python
class GeminiCLISettings(BaseModel):
    """Gemini CLI configuration structure"""
    mcpServers: Dict[str, MCPServerConfig]  # Identical to Claude Code format
    # Additional Gemini-specific settings as discovered in research
```

#### UpdateStatus
```python
class UpdateStatus(BaseModel):
    """MCP server update state"""
    server_name: str
    current_version: Optional[str]  # None for HTTP servers
    latest_version: Optional[str]
    update_available: bool
    update_type: Literal["major", "minor", "patch", "none"]
    dry_run: bool = False
```

#### AuditConfiguration
```python
class AuditConfiguration(BaseModel):
    """Configurable audit paths"""
    search_directories: List[Path]
    default_directories: List[Path] = [
        Path.home() / "Apps",
        Path.home() / "projects",
        Path.home() / "repos"
    ]
```

#### VersionMetadata
```python
class VersionMetadata(BaseModel):
    """Project version information"""
    version: str  # From pyproject.toml
    python_requirement: str  # e.g., ">=3.11"
    mcp_server_count: int  # Current: 6
```

**Relationships**:
- MCPServerConfig (existing) → UpdateStatus (new, one-to-one for stdio servers)
- AuditConfiguration (new) → MCPManager (existing, composition)
- GeminiCLISettings (new) → MCPServerConfig (existing, shares structure)

**Validation Rules**:
- UpdateStatus: version strings must follow semver (major.minor.patch)
- AuditConfiguration: all paths must be absolute and exist
- GeminiCLISettings: mcpServers must validate against MCPServerConfig schema

**State Transitions**:
- UpdateStatus: none → checking → update_available → updating → updated
- Configuration sync: claude_only → gemini_syncing → both_synced

### 2. API Contracts (contracts/)

#### Contract 1: MCP Server Update API
```yaml
# contracts/update_server.yaml
operation: update_server
input:
  server_name: string (required)
  dry_run: boolean (default: false)

output:
  updated: boolean
  current_version: string (optional)
  latest_version: string (optional)
  changes: string (optional)

errors:
  - ServerNotFoundError: server_name not in configuration
  - UpdateCheckError: version check failed
  - NoUpdateAvailableError: already at latest version
```

#### Contract 2: Gemini CLI Sync API
```yaml
# contracts/gemini_sync.yaml
operation: gemini_sync
input:
  force: boolean (default: false)

output:
  success: boolean
  servers_synced: list[string]
  config_path: string
  env_var_configured: boolean

errors:
  - ConfigurationError: ~/.claude.json not found or invalid
  - FileSystemError: cannot create ~/.config/gemini/
  - ShellProfileError: cannot update shell profile
```

#### Contract 3: Configurable Audit Paths API
```yaml
# contracts/audit_with_paths.yaml
operation: audit_configurations
input:
  search_directories: list[string] (optional)
  use_config: boolean (default: true)

output:
  global_config: object
  project_configs: dict[string, object]
  search_paths_used: list[string]

errors:
  - InvalidPathError: path does not exist or not a directory
  - PermissionError: cannot read directory
```

### 3. Contract Tests

**File**: `tests/contract/test_update_server_contract.py`
```python
import pytest
from mcp_manager.core import MCPManager

def test_update_server_contract():
    """Verify update_server API matches contract"""
    manager = MCPManager()

    # Should accept dry_run parameter
    result = manager.update_server("shadcn", dry_run=True)

    # Should return contract-defined fields
    assert "updated" in result
    assert isinstance(result["updated"], bool)

    # Should handle non-existent server
    with pytest.raises(ServerNotFoundError):
        manager.update_server("nonexistent")
```

**File**: `tests/contract/test_gemini_sync_contract.py`
```python
def test_gemini_sync_contract():
    """Verify Gemini CLI sync API matches contract"""
    from mcp_manager.gemini_integration import GeminiCLIIntegration

    gemini = GeminiCLIIntegration()
    result = gemini.sync_from_claude(force=False)

    # Contract-defined output fields
    assert "success" in result
    assert "servers_synced" in result
    assert "config_path" in result
    assert "env_var_configured" in result
```

### 4. Integration Test Scenarios

**From User Stories** (spec.md Acceptance Scenarios):

#### Test Scenario 1: MCP Server Updates
```python
# tests/integration/test_mcp_updates.py
def test_npm_server_update_workflow():
    """
    Given: shadcn MCP server configured with npm
    When: user runs mcp-manager mcp update shadcn
    Then: system checks npm for newer version and updates if available
    """
    # Setup: configure test server
    # Execute: run update command
    # Verify: version changed, config updated, health check passes
```

#### Test Scenario 2: Gemini CLI Integration
```python
# tests/integration/test_gemini_integration.py
def test_gemini_sync_workflow():
    """
    Given: MCP servers configured in Claude Code
    When: user runs mcp-manager gemini sync
    Then: Gemini CLI config created with identical servers
    And: environment variable configured
    """
    # Setup: mock ~/.claude.json
    # Execute: run gemini sync command
    # Verify: ~/.config/gemini/settings.json created
    # Verify: shell profile updated
```

#### Test Scenario 3: Configurable Audit Paths
```python
# tests/integration/test_configurable_audit.py
def test_custom_audit_paths():
    """
    Given: user has projects in custom directories
    When: they run audit with custom paths
    Then: system scans specified directories
    """
    # Setup: create test directories
    # Execute: run audit with --search-dir flags
    # Verify: only specified directories scanned
```

### 5. Update AGENTS.md

**Execution**: Run incremental update script
```bash
cd /home/kkk/Apps/002-mcp-manager
.specify/scripts/bash/update-agent-context.sh claude
```

**Changes to Add**:
- **Tech Stack**: Add Gemini CLI integration, version management utilities
- **Recent Changes**: Document Phase 1-3 improvements
- **File References**: Add new modules (gemini_integration.py, error_handling.py, version_utils.py)

**Keep Under 150 Lines**: Remove oldest changes if necessary to maintain token efficiency

### 6. Quickstart Validation (quickstart.md)

```markdown
# Quickstart: MCP Manager Improvements Validation

## Prerequisites
- Python >=3.11 with uv installed
- Existing mcp-manager installation
- ~/.claude.json with at least one MCP server

## Phase 1: Core Functionality

### Test MCP Server Updates
```bash
# Check current versions
mcp-manager mcp status

# Dry-run update check
mcp-manager mcp update shadcn --dry-run

# Perform actual update (if available)
mcp-manager mcp update shadcn

# Verify health after update
mcp-manager mcp status shadcn
```

### Test Gemini CLI Integration
```bash
# Sync MCP servers to Gemini CLI
mcp-manager gemini sync

# Verify Gemini CLI configuration created
cat ~/.config/gemini/settings.json

# Verify environment variable added
grep GEMINI_CLI_SYSTEM_SETTINGS_PATH ~/.bashrc  # or ~/.zshrc
```

## Phase 2: Code Quality

### Test Configurable Audit Paths
```bash
# Use custom audit paths
mcp-manager project audit --search-dir ~/custom-projects --search-dir ~/work

# Use configuration-based paths (after configuration)
mcp-manager project audit
```

### Verify Documentation Fixes
```bash
# Check Python version in README
grep "Python" README.md  # Should show >=3.11

# Verify MCP server count
grep "MCP servers" website/src/components/Features.astro  # Should show 6
```

## Phase 3: Polish

### Test CLI Reorganization (after implementation)
```bash
# All existing commands should still work
mcp-manager mcp audit
mcp-manager project audit
mcp-manager fleet status
```

### Verify Dynamic Versioning (after implementation)
```bash
# Build website and check version display
npm run build
grep -r "version" docs/  # Should match pyproject.toml
```

## Expected Outcomes
- ✅ MCP servers can be updated automatically
- ✅ Gemini CLI has access to all MCP servers
- ✅ Audit command works with custom directories
- ✅ Documentation reflects accurate requirements
- ✅ CLI remains fully functional after refactoring
```

**Output**: research.md, data-model.md, /contracts/*.yaml, failing contract tests, quickstart.md, AGENTS.md updated

---

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

1. **Load templates and design artifacts**:
   - Load `.specify/templates/tasks-template.md` as base structure
   - Parse `contracts/*.yaml` for contract test tasks
   - Parse `data-model.md` for entity creation tasks
   - Extract scenarios from `quickstart.md` for integration tests

2. **Generate Phase 1 tasks** (High Priority - Core Functionality):
   - Task: Create GeminiCLIIntegration class with sync_from_claude method [P]
   - Task: Implement update_server method in MCPManager core
   - Task: Implement update_all_servers method in MCPManager core
   - Task: Add UpdateStatus model to models.py [P]
   - Task: Create contract test for update_server API [P]
   - Task: Create contract test for gemini_sync API [P]
   - Task: Create integration test for MCP server update workflow
   - Task: Create integration test for Gemini CLI sync workflow
   - Task: Add gemini subcommand group to CLI
   - Task: Implement 'mcp-manager gemini sync' command
   - Task: Update 'mcp-manager init' to call gemini sync
   - Task: Update 'mcp-manager mcp add/remove' to sync both configs

3. **Generate Phase 2 tasks** (Medium Priority - Code Quality):
   - Task: Create error_handling.py with MCPManagerError decorator
   - Task: Apply error decorator to all CLI commands (reduce 30+ try/except blocks)
   - Task: Add AuditConfiguration model to models.py [P]
   - Task: Add search_directories parameter to audit_configurations method
   - Task: Add --search-dir flag to 'mcp-manager project audit' command
   - Task: Update README.md Python requirement (3.13 → >=3.11)
   - Task: Expand README.md "One-Command Setup" section with full capabilities
   - Task: Update Features.astro to state 6 MCP servers (not 5)
   - Task: Add documentation links to README.md (CHANGELOG, guides)
   - Task: Create integration test for configurable audit paths

4. **Generate Phase 3 tasks** (Low Priority - Polish):
   - Task: Create src/mcp_manager/commands/mcp.py for MCP commands
   - Task: Create src/mcp_manager/commands/project.py for project commands
   - Task: Create src/mcp_manager/commands/fleet.py for fleet commands
   - Task: Create src/mcp_manager/commands/agent.py for agent commands
   - Task: Create src/mcp_manager/commands/office.py for office commands
   - Task: Refactor cli.py to use Typer sub-applications
   - Task: Create version_utils.py for pyproject.toml parsing [P]
   - Task: Add Astro build script to inject version from pyproject.toml
   - Task: Update website build process to use dynamic version
   - Task: Verify all CLI commands still functional after reorganization

5. **Generate cross-cutting tasks**:
   - Task: Run security audit (no hardcoded secrets)
   - Task: Run code quality checks (black, ruff, mypy)
   - Task: Execute pytest with >80% coverage requirement
   - Task: Update AGENTS.md with new module references
   - Task: Build and verify GitHub Pages deployment
   - Task: Create comprehensive CHANGELOG entry for all phases

**Ordering Strategy**:
- **TDD order**: Contract tests → Models → Implementation → Integration tests
- **Dependency order**: Phase 1 (core) → Phase 2 (quality) → Phase 3 (polish)
- **Parallel execution markers [P]**: Independent file creation tasks
- **Sequential dependencies**: Tests before implementation, models before services

**Estimated Output**: 50-55 numbered, ordered tasks in tasks.md organized by phase with clear dependencies

**Example Task Structure**:
```markdown
## Phase 1: Core Functionality (Tasks 1-20)

### Task 1: Create UpdateStatus model [P]
**Files**: src/mcp_manager/models.py
**Dependencies**: None (parallel safe)
**Test**: N/A (data model)

### Task 2: Create contract test for update_server [P]
**Files**: tests/contract/test_update_server_contract.py
**Dependencies**: Task 1 (UpdateStatus model)
**Test**: pytest tests/contract/test_update_server_contract.py (should FAIL initially)

[... continues with detailed task breakdown ...]
```

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

---

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

---

## Complexity Tracking
*No constitutional violations - all principles satisfied*

**Justifications**: None required. All implementation approaches align with:
- UV-first development (existing pattern)
- Global configuration first (enhances with Gemini sync)
- Zero downtime operations (maintained through backward compatibility)
- Branch preservation (standard workflow)
- Security by design (no new credential requirements)
- Repository organization (proper file placement)

---

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command - ✅ DONE: research.md created)
- [x] Phase 1: Design complete (/plan command - ✅ DONE: data-model.md, contracts/, quickstart.md created)
- [x] Phase 2: Task planning complete (/plan command - ✅ DONE: approach described above)
- [ ] Phase 3: Tasks generated (/tasks command - ⏭️ NEXT: run /tasks)
- [ ] Phase 4: Implementation complete (future)
- [ ] Phase 5: Validation passed (future)

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS (all principles maintained)
- [x] All NEEDS CLARIFICATION resolved (none in spec)
- [x] Complexity deviations documented (none required)

**Generated Artifacts**:
- ✅ specs/002-referencing-to-this/spec.md (from /specify command)
- ✅ specs/002-referencing-to-this/plan.md (this file)
- ✅ specs/002-referencing-to-this/research.md (Phase 0 output)
- ✅ specs/002-referencing-to-this/data-model.md (Phase 1 output)
- ✅ specs/002-referencing-to-this/quickstart.md (Phase 1 output)
- ✅ specs/002-referencing-to-this/contracts/update_server.yaml (Phase 1)
- ✅ specs/002-referencing-to-this/contracts/gemini_sync.yaml (Phase 1)
- ✅ specs/002-referencing-to-this/contracts/audit_with_paths.yaml (Phase 1)
- ⏳ specs/002-referencing-to-this/tasks.md (awaiting /tasks command)

---

*Based on Constitution v1.1.0 - See `.specify/memory/constitution.md`*
*Spec-kit workflow integration ready for /tasks command execution*
