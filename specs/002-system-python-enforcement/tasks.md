# Tasks: System Python Enforcement

**Feature**: 002-system-python-enforcement
**Input**: Design documents from `/specs/002-system-python-enforcement/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/validation_cli.md ✓, quickstart.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions
- **Current Structure**: `backend/src/mcp_manager/`, `tests/` at repository root
- **Note**: Paths reflect current project structure after Feature 001 restructure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and UV configuration for system Python 3.13 enforcement

- [x] T001 Create `uv.toml` at project root with `python-downloads = "never"` and `python-preference = "only-system"` per research.md
- [x] T002 [P] Verify `.python-version` file contains `3.13` (should already exist)
- [x] T003 [P] Update `pyproject.toml` to set `requires-python = ">=3.13"` for constitutional compliance
- [x] T004 [P] Verify system Python 3.13 installed and UV available before proceeding

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and Python environment detection that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Create Pydantic v2 `PythonEnvironment` model in `backend/src/mcp_manager/models/python_enforcement.py` with fields: executable_path, version, source, distribution, is_valid, in_virtualenv, venv_base_python (see data-model.md lines 22-92)
- [x] T006 [P] Create Pydantic v2 `UVConfiguration` model in `backend/src/mcp_manager/models/python_enforcement.py` with fields: config_file_path, python_downloads, python_preference, python_version_pinned, is_compliant, compliance_violations (see data-model.md lines 112-201)
- [x] T007 [P] Create Pydantic v2 `ValidationResult` model in `backend/src/mcp_manager/models/python_enforcement.py` with fields: status, python_environment, uv_configuration, errors, warnings, checks_performed, timestamp (see data-model.md lines 222-377)
- [x] T008 [P] Implement `find_system_python()` in `backend/src/mcp_manager/python_env.py` to search priority paths: /usr/bin/python3.13 → /usr/local/bin/python3.13 → /opt/homebrew/bin/python3.13 (see research.md lines 46-59)
- [x] T009 [P] Implement `get_python_version()` in `backend/src/mcp_manager/python_env.py` using subprocess to parse `python3.13 --version` output (see research.md lines 245-265)
- [x] T010 [P] Implement `is_python_313()` in `backend/src/mcp_manager/python_env.py` to validate version is (3, 13, x) (see research.md lines 267-270)
- [x] T011 [P] Implement `detect_distribution()` in `backend/src/mcp_manager/python_env.py` to detect OS from /etc/os-release or macOS architecture (see research.md lines 192-217)
- [x] T012 [P] Implement `get_venv_base_python()` in `backend/src/mcp_manager/python_env.py` to parse pyvenv.cfg and extract base Python path (see research.md lines 277-295)
- [x] T013 [P] Implement `validate_uv_config()` in `backend/src/mcp_manager/uv_config.py` to parse uv.toml and check python-downloads/python-preference settings (see research.md lines 306-337)
- [x] T014 [P] Implement `check_uv_installed()` in `backend/src/mcp_manager/uv_config.py` to verify UV availability in PATH
- [x] T015 [P] Implement `get_uv_config_path()` in `backend/src/mcp_manager/uv_config.py` to locate uv.toml or pyproject.toml with [tool.uv] section

**Checkpoint**: Foundation ready - all Python detection and UV configuration infrastructure available

---

## Phase 3: User Story 1 - Developer runs mcp-manager CLI (Priority: P1) 🎯 MVP

**Goal**: Ensure all mcp-manager CLI commands execute using system Python 3.13 without downloading additional Python interpreters

**Independent Test**: Run `mcp-manager status` and verify (1) command executes successfully, (2) Python 3.13 system installation is used via `import sys; print(sys.executable)`, (3) no additional Python downloads occur during execution

**Functional Requirements**: FR-001 (system Python 3.13 for all operations), FR-002 (UV project-local config), FR-003 (prevent Python installation), FR-004 (validate Python on startup)

### Implementation for User Story 1

- [x] T016 [US1] Add Python version validation on CLI startup in `backend/src/mcp_manager/cli.py` before any command execution using `find_system_python()` and `is_python_313()`
- [x] T017 [US1] Add UV configuration validation on CLI startup in `backend/src/mcp_manager/cli.py` to verify `uv.toml` compliance using `validate_uv_config()`
- [x] T018 [US1] Implement clear error message in `backend/src/mcp_manager/cli.py` when system Python 3.13 not found, including distribution-specific installation instructions (FR-010)
- [x] T019 [US1] Implement clear error message in `backend/src/mcp_manager/cli.py` when UV configuration allows Python downloads, suggesting fix (FR-010)
- [x] T020 [US1] Add Python executable path logging in `backend/src/mcp_manager/cli.py` for auditing purposes (FR-009)

**Checkpoint**: At this point, all CLI commands should enforce system Python 3.13 and prevent UV Python downloads

---

## Phase 4: User Story 2 - System validates constitution compliance (Priority: P1)

**Goal**: Provide `mcp-manager validate` command that checks and reports Python 3.13 enforcement compliance with summary and verbose output modes

**Independent Test**: Run `mcp-manager validate` and verify (1) command reports current Python configuration, (2) identifies constitution violations if any, (3) provides clear pass/fail status with exit codes 0=PASS, 1=FAIL, 2=ERROR

**Functional Requirements**: FR-005 (validate command with --verbose), FR-006 (detect non-compliant UV config), FR-011 (priority path search), FR-012 (venv validation)

### Implementation for User Story 2

- [x] T021 [P] [US2] Implement `validate_python_environment()` orchestrator in `backend/src/mcp_manager/validators.py` that calls `find_system_python()`, `validate_uv_config()`, builds `ValidationResult` model (see data-model.md lines 378-389)
- [x] T022 [P] [US2] Implement `ValidationResult.to_summary()` method in `backend/src/mcp_manager/models/python_enforcement.py` to generate summary status line per contract (see contracts/validation_cli.md lines 56-88)
- [x] T023 [P] [US2] Implement `ValidationResult.to_verbose()` method in `backend/src/mcp_manager/models/python_enforcement.py` to generate detailed diagnostic report per contract (see contracts/validation_cli.md lines 90-128)
- [x] T024 [US2] Add `validate` command to `backend/src/mcp_manager/cli.py` with optional `--verbose` flag using Typer (see contracts/validation_cli.md lines 18-28)
- [x] T025 [US2] Implement exit code logic in validate command: 0=PASS, 1=FAIL, 2=ERROR per contract (see contracts/validation_cli.md lines 30-37)
- [x] T026 [US2] Add virtual environment detection and base Python validation in `validate_python_environment()` (FR-012)
- [x] T027 [US2] Implement performance optimization to ensure validation completes in <2 seconds (SC-003)

**Checkpoint**: At this point, `mcp-manager validate` command should be fully functional with both summary and verbose output modes

---

## Phase 5: User Story 3 - Developer runs tests (Priority: P2)

**Goal**: Ensure test suite executes using system Python 3.13 via UV, validating system Python enforcement works correctly

**Independent Test**: Run `pytest tests/` and verify (1) tests execute successfully, (2) system Python 3.13 is used for test execution via `sys.executable`, (3) test dependencies managed by UV without additional Python installations

**Functional Requirements**: FR-007 (tests use system Python 3.13)

**Note**: Tests validate that the system Python enforcement implementation is working correctly

### Unit Tests for User Story 3

- [x] T028 [P] [US3] Create unit test `test_find_system_python_package_manager()` in `tests/unit/test_python_env.py` to verify /usr/bin/python3.13 is found first (mocked paths)
- [x] T029 [P] [US3] Create unit test `test_find_system_python_manual_install()` in `tests/unit/test_python_env.py` to verify /usr/local/bin fallback (mocked paths)
- [x] T030 [P] [US3] Create unit test `test_get_python_version_parsing()` in `tests/unit/test_python_env.py` to verify version parsing from "Python 3.13.0" output
- [x] T031 [P] [US3] Create unit test `test_is_python_313_valid()` in `tests/unit/test_python_env.py` to verify (3, 13, 0) returns True
- [x] T032 [P] [US3] Create unit test `test_is_python_313_invalid()` in `tests/unit/test_python_env.py` to verify (3, 12, 0) returns False
- [x] T033 [P] [US3] Create unit test `test_detect_distribution_ubuntu()` in `tests/unit/test_python_env.py` to verify Ubuntu detection from /etc/os-release
- [x] T034 [P] [US3] Create unit test `test_get_venv_base_python()` in `tests/unit/test_python_env.py` to verify pyvenv.cfg parsing
- [x] T035 [P] [US3] Create unit test `test_validate_uv_config_compliant()` in `tests/unit/test_uv_config.py` to verify compliant uv.toml detection
- [x] T036 [P] [US3] Create unit test `test_validate_uv_config_non_compliant()` in `tests/unit/test_uv_config.py` to verify violation detection when python-downloads=automatic
- [x] T037 [P] [US3] Create unit test `test_validation_result_exit_codes()` in `tests/unit/test_validators.py` to verify exit_code property returns 0/1/2 correctly

### Integration Tests for User Story 3

- [x] T038 [P] [US3] Create integration test `test_python_detection_real_system()` in `tests/integration/test_python_detection.py` to verify real system Python 3.13 detection (not mocked)
- [x] T039 [P] [US3] Create integration test `test_uv_config_parsing_real_file()` in `tests/integration/test_uv_integration.py` to verify parsing actual uv.toml file
- [x] T040 [P] [US3] Create integration test `test_uv_python_find_matches_detection()` in `tests/integration/test_uv_integration.py` to verify `uv python find` matches our detection

### Contract Tests for User Story 3

- [x] T041 [P] [US3] Create contract test `test_validate_success_summary_output()` in `tests/contract/test_validation_cli.py` to verify summary format on PASS (see contracts/validation_cli.md lines 213-218)
- [x] T042 [P] [US3] Create contract test `test_validate_failure_violations_listed()` in `tests/contract/test_validation_cli.py` to verify failure output lists violations (see contracts/validation_cli.md lines 220-226)
- [x] T043 [P] [US3] Create contract test `test_validate_error_python_not_found()` in `tests/contract/test_validation_cli.py` to verify error output when Python 3.13 missing (see contracts/validation_cli.md lines 228-233)
- [x] T044 [P] [US3] Create contract test `test_validate_verbose_complete_report()` in `tests/contract/test_validation_cli.py` to verify verbose output includes all sections (see contracts/validation_cli.md lines 235-241)
- [x] T045 [P] [US3] Create contract test `test_validate_venv_base_python_check()` in `tests/contract/test_validation_cli.py` to verify venv base Python validation (see contracts/validation_cli.md lines 243-247)
- [x] T046 [P] [US3] Create contract test `test_validate_performance_within_limits()` in `tests/contract/test_validation_cli.py` to verify execution <2 seconds (see contracts/validation_cli.md lines 249-253)

### Test Configuration for User Story 3

- [x] T047 [US3] Configure pytest in `pyproject.toml` to use system Python 3.13 via UV with coverage plugin
- [ ] T048 [US3] Verify test coverage >80% for python_env.py, uv_config.py, validators.py modules

**Checkpoint**: At this point, comprehensive test suite validates system Python 3.13 enforcement across all modules

---

## Phase 6: User Story 4 - MCP servers configured and launched (Priority: P3)

**Goal**: Ensure MCP servers managed by mcp-manager use system Python 3.13 when applicable, maintaining consistency

**Independent Test**: Run `mcp-manager add <stdio-server>` and verify (1) server launches successfully, (2) stdio servers using Python run with system Python 3.13, (3) no additional Python installations occur

**Functional Requirements**: FR-008 (MCP servers use system Python 3.13)

### Implementation for User Story 4

- [x] T049 [US4] Update MCP server launcher in `backend/src/mcp_manager/core.py` to use system Python 3.13 path from `find_system_python()` for stdio Python servers
- [x] T050 [US4] Add Python environment validation for MCP server launches in `backend/src/mcp_manager/core.py` to verify system Python is used
- [x] T051 [US4] Add logging for MCP server Python executable path in `backend/src/mcp_manager/core.py` for auditing (FR-009)
- [x] T052 [P] [US4] Create integration test `test_mcp_server_uses_system_python()` in `tests/integration/test_mcp_server_python.py` to verify server process Python version

**Checkpoint**: All MCP servers launched by mcp-manager use system Python 3.13 consistently ✅ COMPLETE

---

## Phase 7: Polish & Cross-Cutting Concerns ✅ COMPLETE

**Purpose**: Documentation, error messages, and performance improvements affecting multiple user stories

- [x] T053 [P] Update README.md with system Python 3.13 requirements and UV configuration instructions
- [x] T054 [P] Create troubleshooting section in docs/ for common Python environment issues (Python not found, UV misconfigured, venv conflicts)
- [x] T055 [P] Enhance error messages across all modules to include actionable resolution steps per distribution (Ubuntu: apt install, macOS: brew install)
- [x] T056 [P] Add Python version and UV config to `mcp-manager status` output for quick diagnostics
- [x] T057 [P] Create UV config migration utility in `backend/src/mcp_manager/uv_config.py` to migrate legacy `.uv/config` to standard `uv.toml` format
- [x] T058 [P] Document UV config migration process for existing users in docs/migration-guide.md with step-by-step instructions and backup recommendations
- [x] T059 Run all code quality checks: black, ruff, mypy on src/ and tests/
- [x] T060 Verify quickstart.md workflow (5-minute setup, verify commands work as documented)
- [x] T061 [P] Performance profiling: ensure Python detection <100ms, validation command <2s (SC-003)
- [x] T062 Final integration test: verify all user stories work together (CLI commands, validate, tests, MCP servers)

**Checkpoint**: All documentation, error messages, migration utilities, and quality checks complete ✅

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - Uses validators.py which depends on foundational modules
  - User Story 3 (P2): Can start after User Stories 1 & 2 complete - Tests validate their implementations
  - User Story 4 (P3): Can start after Foundational - Independent from other stories but benefits from validation
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation → US1 (independent)
- **User Story 2 (P1)**: Foundation → US2 (uses validators.py which uses python_env + uv_config from foundation)
- **User Story 3 (P2)**: Foundation → US1 + US2 → US3 (tests validate US1 & US2 implementations)
- **User Story 4 (P3)**: Foundation → US4 (independent but uses python_env from foundation)

### Critical Path

```
Setup (Phase 1)
    ↓
Foundational (Phase 2) ← BLOCKING
    ↓
    ├─→ User Story 1 (P1) ─┐
    ├─→ User Story 2 (P1) ─┤
    └─→ User Story 4 (P3) ─┼─→ User Story 3 (P2) → Polish (Phase 7)
                           └──────────────────────────┘
```

**MVP Path** (minimum viable product):
1. Setup (Phase 1)
2. Foundational (Phase 2)
3. User Story 1 (P1) - CLI enforcement
4. User Story 2 (P1) - Validation command
5. **STOP** - Deploy MVP with core enforcement and validation

**Full Feature Path**:
Continue from MVP → User Story 3 (P2) tests → User Story 4 (P3) MCP servers → Polish

### Within Each User Story

- Models before services (foundational models in Phase 2)
- Services before CLI commands (validators before validate command)
- Core implementation before tests (US1, US2, US4 before US3)
- Tests must validate existing implementations

### Parallel Opportunities

**Phase 1 - Setup** (all can run in parallel):
- T002, T003, T004 (different files)

**Phase 2 - Foundational** (models and modules in parallel):
- T005, T006, T007 (different models in same file - sequential)
- T008, T009, T010, T011, T012 (python_env.py - sequential within file)
- T013, T014, T015 (uv_config.py - sequential within file)
- python_env.py + uv_config.py + models.py can be worked on in parallel (different files)

**Phase 4 - User Story 2**:
- T021, T022, T023 (different files/methods - can parallelize)

**Phase 5 - User Story 3** (all tests can run in parallel):
- T028-T037 (unit tests - all different test functions)
- T038-T040 (integration tests - all different test functions)
- T041-T046 (contract tests - all different test functions)

**Phase 7 - Polish**:
- T053, T054, T055, T056, T057, T058, T061 (documentation, migration, and optimization - different files)

**Cross-Story Parallelization** (if team capacity allows):
- After Phase 2 completes: US1, US2, and US4 can proceed in parallel (different files/commands)

---

## Parallel Example: User Story 2 (Validation Command)

```bash
# These tasks can be launched together (different files):
Task T021: "Implement validate_python_environment() orchestrator in backend/src/mcp_manager/validators.py"
Task T022: "Implement ValidationResult.to_summary() method in backend/src/mcp_manager/models/python_enforcement.py"
Task T023: "Implement ValidationResult.to_verbose() method in backend/src/mcp_manager/models/python_enforcement.py"

# After T021-T023 complete, these can proceed sequentially:
Task T024: "Add validate command to backend/src/mcp_manager/cli.py"
Task T025: "Implement exit code logic in validate command"
```

---

## Parallel Example: User Story 3 (Tests)

```bash
# All unit tests can be launched together (different test functions):
Task T028-T037: All unit tests for python_env, uv_config, validators

# All integration tests can be launched together:
Task T038-T040: All integration tests

# All contract tests can be launched together:
Task T041-T046: All contract tests for validation CLI
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. **Complete Phase 1**: Setup (T001-T004) - 4 tasks
2. **Complete Phase 2**: Foundational (T005-T015) - 11 tasks
3. **Complete Phase 3**: User Story 1 (T016-T020) - 5 tasks
4. **Complete Phase 4**: User Story 2 (T021-T027) - 7 tasks
5. **STOP and VALIDATE**: Test CLI commands and validate command independently
6. **Deploy/Demo**: MVP with core Python enforcement + validation ready

**MVP Total**: 27 tasks
**MVP Value**: Complete Python 3.13 enforcement + compliance validation

### Incremental Delivery

1. **Foundation** (Phase 1-2): Setup + Foundational → 15 tasks → Core infrastructure ready
2. **MVP** (Phase 3-4): Add US1 + US2 → 27 tasks total → Test independently → Deploy/Demo
3. **Quality** (Phase 5): Add US3 tests → 48 tasks total → Comprehensive test coverage
4. **Complete** (Phase 6-7): Add US4 + Polish → 62 tasks total → Full feature with MCP server support and migration utilities

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

1. **All developers**: Complete Setup + Foundational together (Phase 1-2)
2. **Once Phase 2 done**:
   - **Developer A**: User Story 1 (CLI enforcement) - T016-T020
   - **Developer B**: User Story 2 (Validation command) - T021-T027
   - **Developer C**: User Story 4 (MCP servers) - T049-T052
3. **After US1, US2, US4 complete**:
   - **All developers**: User Story 3 (Tests) - T028-T048 (can split test files)
4. **Final**: Polish together (Phase 7)

---

## Task Summary

**Total Tasks**: 62 tasks across 7 phases

**Tasks per User Story**:
- Setup (Phase 1): 4 tasks
- Foundational (Phase 2): 11 tasks
- User Story 1 - CLI (P1): 5 tasks
- User Story 2 - Validation (P1): 7 tasks
- User Story 3 - Tests (P2): 21 tasks
- User Story 4 - MCP Servers (P3): 4 tasks
- Polish (Phase 7): 10 tasks (includes UV config migration T057-T058)

**Parallel Opportunities**: 36 tasks marked [P] can run in parallel within their phases

**MVP Scope**: 27 tasks (Phases 1-4: Setup + Foundational + US1 + US2)

**Independent Test Criteria**:
- US1: Run `mcp-manager status` - verifies CLI uses system Python 3.13
- US2: Run `mcp-manager validate` - verifies validation command works
- US3: Run `pytest tests/` - verifies test suite validates enforcement
- US4: Run `mcp-manager add <server>` - verifies MCP servers use system Python

---

## Notes

- [P] tasks = different files/functions, no sequential dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate story independently
- Code quality checks (black, ruff, mypy) required before marking Phase 7 complete
- All file paths reflect current project structure (backend/src/mcp_manager/)
