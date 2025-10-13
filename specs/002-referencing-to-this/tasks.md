# Tasks: MCP Manager Three-Phase Improvements

**Input**: Design documents from `/home/kkk/Apps/002-mcp-manager/specs/002-referencing-to-this/`
**Prerequisites**: plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅
**Feature**: Three-phase enhancement plan (29 functional requirements)

## Execution Flow (main)
```
1. ✅ Loaded plan.md from feature directory
   → Tech stack: Python 3.11+, Typer 0.12+, Rich 13.0+, httpx 0.27+, Pydantic 2.0+
   → Structure: Single Python CLI with src/ layout
2. ✅ Loaded design documents:
   → data-model.md: 4 entities (GeminiCLISettings, UpdateStatus, AuditConfiguration, VersionMetadata)
   → contracts/: 3 contracts (update_server, gemini_sync, audit_with_paths)
   → research.md: 6 research areas with implementation decisions
   → quickstart.md: 8 test scenarios for validation
3. ✅ Generated tasks by priority and phase:
   → Phase 1 (High): MCP updates + Gemini CLI integration (20 tasks)
   → Phase 2 (Medium): Error handling + config paths + docs (15 tasks)
   → Phase 3 (Low): CLI modularization + dynamic versioning (10 tasks)
   → Cross-cutting: Security, quality, documentation (10 tasks)
4. ✅ Applied task rules:
   → Different files = marked [P] for parallel execution
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. ✅ Numbered tasks sequentially (T001-T055)
6. ✅ Generated dependency graph
7. ✅ Created parallel execution examples
8. ✅ Validated task completeness:
   → All 3 contracts have tests ✅
   → All 4 entities have models ✅
   → All CLI commands implemented ✅
9. ✅ READY FOR EXECUTION
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **File paths**: Exact locations in repository structure

## Path Conventions
- **Single project**: `src/mcp_manager/`, `tests/` at repository root
- **CLI structure**: Typer-based command groups
- **Tests**: contract/, integration/, unit/ subdirectories

---

## Phase 3.1: Setup (Tasks 1-5)

### [X] T001: Initialize development environment
**Files**: Repository root
**Dependencies**: None
**Description**: Verify Python 3.11+, uv installed, existing mcp-manager installation functional
**Test**: `python --version`, `uv --version`, `mcp-manager --help`
**Duration**: 2 min

### [X] T002: Install development dependencies
**Files**: pyproject.toml
**Dependencies**: T001
**Description**: Ensure pytest, black, ruff, mypy, coverage installed via uv
**Test**: `uv run pytest --version`, `black --version`, `ruff --version`, `mypy --version`
**Duration**: 3 min

### [X] T003 [P]: Backup existing configuration
**Files**: ~/.claude.json → backup
**Dependencies**: None
**Description**: Create timestamped backup of ~/.claude.json before making any changes
**Test**: Backup file exists with timestamp
**Duration**: 1 min

### [X] T004 [P]: Create test directories
**Files**: tests/contract/, tests/integration/
**Dependencies**: None
**Description**: Ensure test directories exist for contract and integration tests
**Test**: `ls tests/contract/`, `ls tests/integration/`
**Duration**: 1 min

### [X] T005 [P]: Run baseline code quality checks
**Files**: src/mcp_manager/
**Dependencies**: T002
**Description**: Run black, ruff, mypy on existing codebase to establish baseline
**Test**: All checks pass or document existing issues
**Duration**: 3 min

---

## Phase 3.2: Tests First - Phase 1 (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### [X] T006 [P]: Contract test for update_server API
**Files**: tests/contract/test_update_server_contract.py
**Dependencies**: T004
**Description**: Create contract test validating update_server API matches contracts/update_server.yaml specification
**Test**: pytest tests/contract/test_update_server_contract.py (SHOULD FAIL)
**Duration**: 15 min
**Contract Requirements**:
- Input: server_name (string), dry_run (boolean)
- Output: updated (boolean), current_version (string?), latest_version (string?), update_type (enum), changes (string?)
- Errors: ServerNotFoundError, UpdateCheckError, NoUpdateAvailableError, UpdateFailedError

### [X] T007 [P]: Contract test for gemini_sync API
**Files**: tests/contract/test_gemini_sync_contract.py
**Dependencies**: T004
**Description**: Create contract test validating Gemini CLI sync API matches contracts/gemini_sync.yaml
**Test**: pytest tests/contract/test_gemini_sync_contract.py (SHOULD FAIL)
**Duration**: 15 min
**Contract Requirements**:
- Input: force (boolean, default false)
- Output: success (boolean), servers_synced (list[string]), config_path (string), env_var_configured (boolean), shell_profile (string?)
- Errors: ConfigurationError, FileSystemError, ShellProfileError, NoServersError

### [X] T008 [P]: Contract test for audit_with_paths API
**Files**: tests/contract/test_audit_with_paths_contract.py
**Dependencies**: T004
**Description**: Create contract test validating configurable audit paths API matches contracts/audit_with_paths.yaml
**Test**: pytest tests/contract/test_audit_with_paths_contract.py (SHOULD FAIL)
**Duration**: 15 min
**Contract Requirements**:
- Input: search_directories (array[string]?), use_config (boolean), detailed (boolean)
- Output: global_config (object), project_configs (dict), search_paths_used (array[string])
- Errors: InvalidPathError, PermissionError, ConfigurationError

### [X] T009 [P]: Integration test for MCP server update workflow
**Files**: tests/integration/test_mcp_update_workflow.py
**Dependencies**: T004
**Description**: Test end-to-end update workflow: check version → dry-run → actual update → health check
**Test**: pytest tests/integration/test_mcp_update_workflow.py (SHOULD FAIL)
**Duration**: 20 min
**Scenarios**: From quickstart.md Test 1 and Test 2

### [X] T010 [P]: Integration test for Gemini CLI sync workflow
**Files**: tests/integration/test_gemini_sync_workflow.py
**Dependencies**: T004
**Description**: Test end-to-end Gemini sync: read Claude config → create Gemini config → update shell profile → verify
**Test**: pytest tests/integration/test_gemini_sync_workflow.py (SHOULD FAIL)
**Duration**: 20 min
**Scenarios**: From quickstart.md Test 3 and Test 4

### [X] T011 [P]: Integration test for configurable audit paths
**Files**: tests/integration/test_configurable_audit.py
**Dependencies**: T004
**Description**: Test audit with custom paths via CLI flags and config file
**Test**: pytest tests/integration/test_configurable_audit.py (SHOULD FAIL)
**Duration**: 15 min
**Scenarios**: From quickstart.md Test 5

---

## Phase 3.3: Core Implementation - Phase 1 (ONLY after tests are failing)

### [X] T012 [P]: Create UpdateStatus model
**Files**: src/mcp_manager/models.py
**Dependencies**: T006-T011 (tests written)
**Description**: Add UpdateStatus Pydantic model per data-model.md specification
**Test**: Import UpdateStatus successfully, instantiate with valid data
**Duration**: 10 min
**Fields**: server_name, current_version, latest_version, update_available, update_type, dry_run, package_name, check_timestamp

### [X] T013 [P]: Create AuditConfiguration model
**Files**: src/mcp_manager/models.py
**Dependencies**: T006-T011 (tests written)
**Description**: Add AuditConfiguration Pydantic model per data-model.md specification
**Test**: Import AuditConfiguration, validate paths
**Duration**: 10 min
**Fields**: search_directories, default_directories, use_defaults, validate_paths

### [X] T014 [P]: Create GeminiCLISettings model
**Files**: src/mcp_manager/models.py
**Dependencies**: T006-T011 (tests written)
**Description**: Add GeminiCLISettings Pydantic model per data-model.md specification
**Test**: Import GeminiCLISettings, validate mcpServers structure
**Duration**: 10 min
**Fields**: mcpServers, config_path, env_var_configured

### [X] T015 [P]: Create VersionMetadata model
**Files**: src/mcp_manager/models.py
**Dependencies**: T006-T011 (tests written)
**Description**: Add VersionMetadata Pydantic model per data-model.md specification
**Test**: Import VersionMetadata, parse from dict
**Duration**: 10 min
**Fields**: version, python_requirement, mcp_server_count, dependencies, source_file

### [X] T016: Implement check_npm_package_version utility
**Files**: src/mcp_manager/utils.py
**Dependencies**: T012
**Description**: Add subprocess-based npm version checker per research.md decision
**Test**: T006 contract test should start passing for version checks
**Duration**: 15 min
**Implementation**: subprocess.run(['npm', 'view', package, 'version'])

### [X] T017: Implement version comparison utility
**Files**: src/mcp_manager/utils.py
**Dependencies**: T012, T016
**Description**: Add semver comparison using packaging.version per research.md
**Test**: Version("1.2.3") < Version("1.3.0"), categorize as major/minor/patch
**Duration**: 15 min

### [X] T018: Implement update_server method in MCPManager
**Files**: src/mcp_manager/core.py
**Dependencies**: T012, T016, T017
**Description**: Add update_server method to MCPManager class supporting dry-run and actual updates
**Test**: T006 contract test should pass, T009 integration test progress
**Duration**: 30 min
**Logic**: Check version → compare → update args array → save config → health check

### [X] T019: Implement update_all_servers method in MCPManager
**Files**: src/mcp_manager/core.py
**Dependencies**: T018
**Description**: Add update_all_servers to iterate stdio servers and update each
**Test**: Can update multiple servers in sequence
**Duration**: 15 min

### [X] T020 [P]: Create GeminiCLIIntegration class
**Files**: src/mcp_manager/gemini_integration.py (NEW FILE)
**Dependencies**: T014
**Description**: Create new module with GeminiCLIIntegration class per design
**Test**: Import class successfully
**Duration**: 10 min

### [X] T021: Implement sync_from_claude method
**Files**: src/mcp_manager/gemini_integration.py
**Dependencies**: T020
**Description**: Implement Gemini sync logic: read Claude config → merge → write Gemini config → update shell profile
**Test**: T007 contract test should pass, T010 integration test should pass
**Duration**: 40 min
**Logic**: Load ~/.claude.json → create ~/.config/gemini/settings.json → add env var to shell profile

### [X] T022: Implement shell profile detection
**Files**: src/mcp_manager/gemini_integration.py
**Dependencies**: T021
**Description**: Add shell profile detection logic (bashrc → zshrc → profile) per research.md
**Test**: Correctly identifies active shell profile
**Duration**: 15 min

### [X] T023: Add search_directories parameter to audit_configurations
**Files**: src/mcp_manager/core.py
**Dependencies**: T013
**Description**: Modify existing audit_configurations method to accept AuditConfiguration parameter
**Test**: T008 contract test should pass, T011 integration test should pass
**Duration**: 20 min
**Changes**: Remove hardcoded paths, use config.search_directories

### [X] T024: Add 'mcp update' CLI command
**Files**: src/mcp_manager/cli.py
**Dependencies**: T018, T019
**Description**: Add 'mcp-manager mcp update <server>' and 'mcp-manager mcp update --all' commands
**Test**: Commands execute, help text correct, dry-run flag works
**Duration**: 20 min

### [X] T025: Add 'gemini' command group to CLI
**Files**: src/mcp_manager/cli.py
**Dependencies**: T021
**Description**: Add new gemini Typer subcommand group with 'sync' command
**Test**: `mcp-manager gemini sync` executes successfully
**Duration**: 15 min

### [X] T026: Update 'mcp-manager init' to trigger Gemini sync
**Files**: src/mcp_manager/cli.py
**Dependencies**: T025
**Description**: Modify existing init command to call gemini sync after global config creation
**Test**: Init command creates both Claude and Gemini configs
**Duration**: 10 min

### [X] T027: Update 'mcp-manager mcp add/remove' for dual-config sync
**Files**: src/mcp_manager/cli.py
**Dependencies**: T025
**Description**: Modify add/remove commands to sync changes to Gemini CLI config
**Test**: Adding/removing server updates both ~/.claude.json and ~/.config/gemini/settings.json
**Duration**: 15 min

### [X] T028: Add '--search-dir' flag to 'project audit'
**Files**: src/mcp_manager/cli.py
**Dependencies**: T023
**Description**: Add --search-dir CLI flag (repeatable) to project audit command
**Test**: `mcp-manager project audit --search-dir ~/custom` uses custom path
**Duration**: 10 min

---

## Phase 3.4: Tests First - Phase 2 (TDD)

### [X] T029 [P]: Integration test for error handling decorator
**Files**: tests/integration/test_error_handling.py
**Dependencies**: T004
**Description**: Test centralized error decorator with various exception types
**Test**: pytest tests/integration/test_error_handling.py (SHOULD FAIL)
**Duration**: 15 min

---

## Phase 3.5: Core Implementation - Phase 2

### [X] T030 [P]: Create error_handling.py module
**Files**: src/mcp_manager/error_handling.py (NEW FILE)
**Dependencies**: T029
**Description**: Create new module with handle_mcp_errors decorator per research.md
**Test**: T029 should start passing
**Duration**: 20 min
**Implementation**: Decorator using functools.wraps, Rich error display, typer.Exit(1)

### [X] T031: Apply error decorator to all CLI commands
**Files**: src/mcp_manager/cli.py
**Dependencies**: T030
**Description**: Apply @handle_mcp_errors decorator to all command functions (reduce 30+ try/except blocks)
**Test**: All commands still work, errors display consistently
**Duration**: 30 min
**Impact**: Code reduction from 1552 lines (estimated ~100 line reduction)

### [X] T032 [P]: Update README.md Python version requirement
**Files**: README.md
**Dependencies**: None
**Description**: Change Python requirement from "3.13" to ">=3.11" per pyproject.toml
**Test**: grep ">=3.11" README.md
**Duration**: 5 min

### [X] T033 [P]: Expand README.md "One-Command Setup" section
**Files**: README.md
**Dependencies**: T032
**Description**: Add comprehensive setup instructions with all capabilities
**Test**: README reflects actual features
**Duration**: 15 min

### [X] T034 [P]: Update Features.astro to reflect 6 MCP servers
**Files**: website/src/components/Features.astro
**Dependencies**: None
**Description**: Change "5 MCP servers" to "6 MCP servers" (MarkItDown added)
**Test**: grep "6" website/src/components/Features.astro
**Duration**: 5 min

### [X] T035 [P]: Add documentation links to README.md
**Files**: README.md
**Dependencies**: T032
**Description**: Add links to CHANGELOG.md, guides/, and other documentation
**Test**: Links are valid and point to existing files
**Duration**: 10 min

### [X] T036 [P]: Create configuration file support for audit paths
**Files**: src/mcp_manager/config.py
**Dependencies**: T013
**Description**: Add XDG-compliant config file reading for ~/.config/mcp-manager/config.json
**Test**: Config file loaded correctly, defaults used if missing
**Duration**: 20 min

---

## Phase 3.6: Tests First - Phase 3 (TDD)

### [X] T037 [P]: Integration test for CLI modularization
**Files**: tests/integration/test_cli_modules.py
**Dependencies**: T004
**Description**: Test that all existing commands still work after modularization
**Test**: pytest tests/integration/test_cli_modules.py (SHOULD FAIL initially, PASS after T038-T043)
**Duration**: 20 min

---

## Phase 3.7: Core Implementation - Phase 3

### [X] T038 [P]: Create commands/ directory and __init__.py
**Files**: src/mcp_manager/commands/__init__.py (NEW DIRECTORY)
**Dependencies**: T037
**Description**: Create new commands directory for CLI modularization
**Test**: Directory exists, __init__.py created
**Duration**: 2 min

### [X] T039 [P]: Create commands/mcp.py module
**Files**: src/mcp_manager/commands/mcp.py (NEW FILE)
**Dependencies**: T038
**Description**: Extract MCP commands from cli.py to separate module (~300 lines)
**Test**: Import works, commands: audit, init, add, remove, status, update, diagnose, migrate, setup-hf, setup-all
**Duration**: 40 min

### [X] T040 [P]: Create commands/project.py module
**Files**: src/mcp_manager/commands/project.py (NEW FILE)
**Dependencies**: T038
**Description**: Extract project commands from cli.py (~200 lines)
**Test**: Import works, commands: audit, fix, standards
**Duration**: 30 min

### [X] T041 [P]: Create commands/fleet.py module
**Files**: src/mcp_manager/commands/fleet.py (NEW FILE)
**Dependencies**: T038
**Description**: Extract fleet commands from cli.py (~200 lines)
**Test**: Import works, commands: register, status, sync, audit
**Duration**: 30 min

### [X] T042 [P]: Create commands/agent.py module
**Files**: src/mcp_manager/commands/agent.py (NEW FILE)
**Dependencies**: T038
**Description**: Extract agent commands from cli.py (~200 lines)
**Test**: Import works, commands: discover, deploy, deploy-department, install-global, audit
**Duration**: 30 min

### [X] T043 [P]: Create commands/office.py module
**Files**: src/mcp_manager/commands/office.py (NEW FILE)
**Dependencies**: T038
**Description**: Extract office commands from cli.py (~250 lines)
**Test**: Import works, commands: register, list, remove, status, check, deploy, verify, pull, info
**Duration**: 35 min

### [X] T044: Refactor cli.py to use Typer sub-applications
**Files**: src/mcp_manager/cli.py
**Dependencies**: T039-T043
**Description**: Replace extracted commands with app.add_typer() calls, reduce to ~100 lines
**Test**: T037 integration test should pass, all commands still functional
**Duration**: 30 min
**Result**: cli.py: 1552 lines → ~100 lines (orchestration only)

### [X] T045 [P]: Create version_utils.py module
**Files**: src/mcp_manager/version_utils.py (NEW FILE)
**Dependencies**: T015
**Description**: Create new module for pyproject.toml parsing using tomllib (Python 3.11+)
**Test**: Parse pyproject.toml, return VersionMetadata
**Duration**: 20 min

### [X] T046: Install @iarna/toml npm package
**Files**: website/package.json
**Dependencies**: None
**Description**: Add @iarna/toml devDependency for TOML parsing in Astro config
**Test**: npm install succeeds, package appears in package.json
**Duration**: 3 min

### [X] T047: Update astro.config.mjs for dynamic version
**Files**: website/astro.config.mjs
**Dependencies**: T046
**Description**: Read version from pyproject.toml and inject via vite.define per research.md
**Test**: Build succeeds, import.meta.env.PROJECT_VERSION available
**Duration**: 15 min

### [X] T048: Update website pages to use dynamic version
**Files**: website/src/pages/index.astro, website/src/components/Header.astro
**Dependencies**: T047
**Description**: Replace hardcoded version strings with import.meta.env.PROJECT_VERSION
**Test**: Version from pyproject.toml appears in built site
**Duration**: 10 min

---

## Phase 3.8: Integration & Validation

### [X] T049: Run all contract tests
**Files**: tests/contract/
**Dependencies**: T012-T028, T030-T031
**Description**: Execute all contract tests, verify 100% pass rate
**Test**: `pytest tests/contract/ -v` - all pass
**Duration**: 5 min

### [X] T050: Run all integration tests
**Files**: tests/integration/
**Dependencies**: T012-T048
**Description**: Execute all integration tests, verify scenarios from quickstart.md
**Test**: `pytest tests/integration/ -v` - all pass
**Duration**: 10 min

### [X] T051: Run full test suite with coverage
**Files**: tests/
**Dependencies**: T049, T050
**Description**: Run pytest with coverage, ensure >80% coverage requirement met
**Test**: `uv run pytest tests/ --cov=mcp_manager --cov-report=term` - coverage >80%
**Duration**: 10 min

### [X] T052: Execute quickstart validation scenarios
**Files**: specs/002-referencing-to-this/quickstart.md
**Dependencies**: T051
**Description**: Manually execute all 8 test scenarios from quickstart.md
**Test**: All scenarios complete successfully, expected outcomes achieved
**Duration**: 20 min
**Scenarios**: Tests 1-8 from quickstart.md

---

## Phase 3.9: Polish & Quality

### [X] T053: Run code quality checks
**Files**: src/mcp_manager/, tests/
**Dependencies**: T051
**Description**: Execute black, ruff, mypy on entire codebase
**Test**: `black src/ tests/ && ruff check src/ tests/ && mypy src/` - all pass
**Duration**: 5 min

### [X] T054: Build and verify GitHub Pages deployment
**Files**: website/, docs/
**Dependencies**: T048, T053
**Description**: Run `npm run build`, verify docs/ contains all required files
**Test**: docs/index.html exists, version correct, _astro/ present, .nojekyll exists
**Duration**: 5 min

### [X] T055: Update CHANGELOG.md with all improvements
**Files**: docs/CHANGELOG.md
**Dependencies**: T054
**Description**: Create comprehensive changelog entry documenting all 29 functional requirements implemented
**Test**: CHANGELOG reflects all phases, organized by priority
**Duration**: 20 min
**Sections**: Phase 1 (features), Phase 2 (improvements), Phase 3 (refactoring)

---

## Dependencies Graph

```
Setup (T001-T005)
    ↓
Tests Phase 1 (T006-T011) [All parallel]
    ↓
Models (T012-T015) [All parallel]
    ↓
    ├─→ Utils (T016-T017)
    │       ↓
    │   Core Phase 1 (T018-T028)
    │       ↓
    ├─→ Tests Phase 2 (T029)
    │       ↓
    │   Core Phase 2 (T030-T036)
    │       ↓
    ├─→ Tests Phase 3 (T037)
    │       ↓
    │   Core Phase 3 (T038-T048)
    │       ↓
    └─→ Integration & Validation (T049-T052)
            ↓
        Polish (T053-T055)
```

## Parallel Execution Examples

### Phase 3.2: Launch all contract tests together
```bash
# Parallel execution (different files)
Task: "T006: Contract test for update_server API in tests/contract/test_update_server_contract.py"
Task: "T007: Contract test for gemini_sync API in tests/contract/test_gemini_sync_contract.py"
Task: "T008: Contract test for audit_with_paths API in tests/contract/test_audit_with_paths_contract.py"
Task: "T009: Integration test for MCP server update workflow in tests/integration/test_mcp_update_workflow.py"
Task: "T010: Integration test for Gemini CLI sync workflow in tests/integration/test_gemini_sync_workflow.py"
Task: "T011: Integration test for configurable audit paths in tests/integration/test_configurable_audit.py"
```

### Phase 3.3: Launch all model creation tasks together
```bash
# Parallel execution (same file but independent classes)
Task: "T012: Create UpdateStatus model in src/mcp_manager/models.py"
Task: "T013: Create AuditConfiguration model in src/mcp_manager/models.py"
Task: "T014: Create GeminiCLISettings model in src/mcp_manager/models.py"
Task: "T015: Create VersionMetadata model in src/mcp_manager/models.py"
```

### Phase 3.7: Launch all command module extractions together
```bash
# Parallel execution (different files)
Task: "T039: Create commands/mcp.py module"
Task: "T040: Create commands/project.py module"
Task: "T041: Create commands/fleet.py module"
Task: "T042: Create commands/agent.py module"
Task: "T043: Create commands/office.py module"
```

---

## Validation Checklist
*GATE: All items verified before task generation complete*

- [x] All 3 contracts have corresponding tests (T006-T008)
- [x] All 4 entities have model tasks (T012-T015)
- [x] All tests come before implementation (T006-T011 → T012-T048)
- [x] Parallel tasks truly independent (different files or non-conflicting sections)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task in same phase
- [x] TDD order enforced (tests fail first, implementation makes them pass)
- [x] All quickstart scenarios covered (T052)
- [x] Constitutional compliance maintained (T053-T055)

---

## Task Summary

**Total Tasks**: 55
- **Setup**: 5 tasks (T001-T005)
- **Phase 1 Tests**: 6 tasks (T006-T011)
- **Phase 1 Implementation**: 17 tasks (T012-T028)
- **Phase 2 Tests**: 1 task (T029)
- **Phase 2 Implementation**: 7 tasks (T030-T036)
- **Phase 3 Tests**: 1 task (T037)
- **Phase 3 Implementation**: 11 tasks (T038-T048)
- **Integration**: 4 tasks (T049-T052)
- **Polish**: 3 tasks (T053-T055)

**Estimated Duration**: ~12-14 hours (excluding breaks)
- Setup & Testing: ~3 hours
- Phase 1 Implementation: ~5 hours
- Phase 2 Implementation: ~2 hours
- Phase 3 Implementation: ~3 hours
- Integration & Polish: ~1.5 hours

**Parallel Opportunities**: 24 tasks marked [P] (43% can run in parallel)

---

## Notes

- **[P] tasks**: Different files, no dependencies, safe for concurrent execution
- **TDD enforced**: All tests written and failing before implementation
- **Constitutional compliance**: All tasks maintain UV-first, global config, branch preservation principles
- **Backward compatibility**: No breaking changes to existing commands or configurations
- **Code reduction**: cli.py: 1552 → ~100 lines (~93% reduction through modularization)
- **Coverage requirement**: >80% maintained throughout (T051)
- **Documentation accuracy**: All version numbers synchronized (T032-T035, T048)

---

*Based on Constitution v1.1.0 - See `.specify/memory/constitution.md`*
*Ready for /implement command execution*
