# Tasks: CI/CD Pipeline Improvements (Feature 002)

**Input**: Design documents from `/home/kkk/Apps/002-mcp-manager/specs/002-cicd-pipeline-enhancements/`
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story (US1-US9) to enable independent implementation and testing of each story. Tests are NOT included (infrastructure enhancement, not application development).

**Note**: This is an enhancement to Feature 001 (existing Local CI/CD pipeline). All changes maintain backwards compatibility.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US9)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize branch and verify prerequisites

- [X] T001 Create feature branch `002-cicd-pipeline-enhancements` from main
- [X] T002 Verify bash version ≥ 4.4 (`bash --version`)
- [X] T003 Verify `jq` is installed and accessible (`which jq`)
- [X] T004 Create contracts directory `/home/kkk/Apps/002-mcp-manager/specs/002-cicd-pipeline-enhancements/contracts/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core contracts and data structures that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create exit code contract in `/home/kkk/Apps/002-mcp-manager/specs/002-cicd-pipeline-enhancements/contracts/exit-codes.md` with codes 0-5
- [X] T006 [P] Create enhanced JSON log schema in `/home/kkk/Apps/002-mcp-manager/specs/002-cicd-pipeline-enhancements/contracts/log-schema.json`
- [X] T007 [P] Create deployment state schema in `/home/kkk/Apps/002-mcp-manager/specs/002-cicd-pipeline-enhancements/contracts/deployment-state-schema.json`
- [X] T008 Add exit code constant `EXIT_TIMEOUT=5` to `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [X] T009 Add `SECONDS` variable initialization at pipeline start in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Hard Failure on Timeout Violation (Priority: P1) 🎯 MVP

**Goal**: Enforce NFR-003 5-minute timeout with immediate exit code 5

**Independent Test**: Run pipeline with artificial sleep to exceed 300 seconds, verify exit code 5

### Implementation for User Story 1

- [X] T010 [US1] Create timeout check function `check_timeout()` in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh` using `$SECONDS` variable
- [X] T011 [US1] Add timeout check call after each pipeline step in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [X] T012 [US1] Implement timeout failure logic: exit with code 5 and log "Pipeline failed: duration exceeded NFR-003 limit (Xs)" in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [X] T013 [US1] Add exit code precedence logic: test failure (2) overrides timeout (5) when both occur in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [X] T014 [US1] Update help message to include exit code 5 documentation in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`

**Checkpoint**: Pipeline now enforces 300-second hard limit and exits with code 5

---

## Phase 4: User Story 2 - Reliable Deployment State Tracking (Priority: P1)

**Goal**: GitHub Actions deployment with 3-attempt retry and hard failure on exhaustion

**Independent Test**: Simulate git push failure, verify 3 retry attempts and workflow failure

### Implementation for User Story 2

- [X] T015 [US2] Add deployment state tracking step to `.github/workflows/deploy.yml` after successful deployment
- [X] T016 [US2] Create deployment state commit function with retry loop (3 attempts max) in `.github/workflows/deploy.yml`
- [X] T017 [US2] Implement exponential backoff (2^attempt seconds) between retry attempts in `.github/workflows/deploy.yml`
- [X] T018 [US2] Add failure logging "Failed to persist deployment state after 3 attempts" on retry exhaustion in `.github/workflows/deploy.yml`
- [X] T019 [US2] Add success logging "Deployment state persisted (attempt X/3)" in `.github/workflows/deploy.yml`
- [X] T020 [US2] Update deployment state JSON structure in `.github/deployment-state.json` (auto-created by workflow)

**Checkpoint**: Deployment state tracking never fails silently, always retries or fails loudly

---

## Phase 5: User Story 3 - Faster Pipeline Execution via Parallel Tests (Priority: P2)

**Goal**: Run unit, integration, E2E tests in parallel for 40-60% speedup

**Independent Test**: Measure test phase duration before/after, verify 40-60% reduction

**Dependencies**: Requires Phase 3 (US1) complete - timeout must be baseline before parallelization

### Implementation for User Story 3

- [X] T021 [US3] Refactor test execution into functions `run_test_unit()`, `run_test_integration()`, `run_test_e2e()` in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [X] T022 [US3] Implement parallel test execution using background jobs (`&`) in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [X] T023 [US3] Add `wait` builtin to collect parallel job exit codes in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [X] T024 [US3] Implement failure aggregation logic: collect all test failures before reporting in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [X] T025 [US3] Update test logging to indicate parallel execution status in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [X] T026 [US3] Add resource contention detection (port conflicts, file lock timeouts) in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [X] T027 [US3] Implement serial fallback on resource contention with logging in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`

**Checkpoint**: Tests run in parallel, 40-60% faster, with serial fallback on resource contention

---

## Phase 6: User Story 4 - Enhanced Log Context for Debugging (Priority: P2)

**Goal**: Add source_file, line_number, function_name to all JSON log entries

**Independent Test**: Generate logs, verify JSON entries include source context fields

**Dependencies**: Can run in parallel with Phase 5 (US3) - different files

### Implementation for User Story 4

- [ ] T028 [P] [US4] Add source context extraction helper using `${BASH_SOURCE[@]}`, `$LINENO`, `${FUNCNAME[@]}` in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/logger.sh`
- [ ] T029 [P] [US4] Update `log_info()` function to accept and include source context in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/logger.sh`
- [ ] T030 [P] [US4] Update `log_warn()` function to accept and include source context in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/logger.sh`
- [ ] T031 [P] [US4] Update `log_error()` function to accept and include source context in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/logger.sh`
- [ ] T032 [US4] Update all logging calls in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh` to pass source context (calling location)
- [ ] T033 [US4] Update logging calls in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/validator.sh` to pass source context

**Checkpoint**: All logs include accurate source_file, line_number, function_name for debugging

---

## Phase 7: User Story 6 - Pipeline Run Correlation for Tracing (Priority: P3)

**Goal**: Generate unique correlation ID per run, include in all log entries

**Independent Test**: Run multiple pipelines, verify each has unique run_id in all logs

**Dependencies**: Can run in parallel with Phase 6 (US4) - different concerns

### Implementation for User Story 6

- [ ] T034 [P] [US6] Create correlation ID generator function using `date +%Y%m%d-%H%M%S` and `/dev/urandom` in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [ ] T035 [P] [US6] Generate and export `RUN_ID` at pipeline initialization in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [ ] T036 [US6] Update logger functions to include `run_id` field in JSON output in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/logger.sh`
- [ ] T037 [US6] Add run_id to initial pipeline log entry in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`

**Checkpoint**: All log entries include unique run_id for correlation across multiple runs

---

## Phase 8: User Story 5 - Real-Time TUI Progress Updates (Priority: P2)

**Goal**: Parse JSON logs in real-time, display live progress in TUI

**Independent Test**: Launch TUI, verify progress updates every 1-2 seconds showing current step

**Dependencies**: Requires Phase 6 (US4) and Phase 7 (US6) complete - needs enhanced JSON logs with correlation IDs

### Implementation for User Story 5

- [ ] T038 [US5] Create JSON log parser function using `tail -f | jq` in `/home/kkk/Apps/002-mcp-manager/scripts/tui/run.sh`
- [ ] T039 [US5] Implement progress tracking state: current_step, step_count, elapsed_time in `/home/kkk/Apps/002-mcp-manager/scripts/tui/run.sh`
- [ ] T040 [US5] Create progress display function with clear/redraw logic in `/home/kkk/Apps/002-mcp-manager/scripts/tui/run.sh`
- [ ] T041 [US5] Add step completion detection from JSON logs in `/home/kkk/Apps/002-mcp-manager/scripts/tui/run.sh`
- [ ] T042 [US5] Add step status indicators (✓ success, ✗ failure) in `/home/kkk/Apps/002-mcp-manager/scripts/tui/run.sh`
- [ ] T043 [US5] Implement progress update loop (every 1-2 seconds) in `/home/kkk/Apps/002-mcp-manager/scripts/tui/run.sh`
- [ ] T044 [US5] Add error handling for malformed JSON logs in `/home/kkk/Apps/002-mcp-manager/scripts/tui/run.sh`

**Checkpoint**: TUI displays real-time pipeline progress, no more blank screen confusion

---

## Phase 9: User Story 7 - Automatic E2E Test Retry for Stability (Priority: P3)

**Goal**: Retry E2E tests once (2 attempts total) if first attempt fails

**Independent Test**: Create E2E test that fails first run, passes second, verify auto-retry

### Implementation for User Story 7

- [ ] T045 [US7] Create E2E test retry wrapper function in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [ ] T046 [US7] Add attempt counter (1-2) to E2E test execution in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [ ] T047 [US7] Implement retry logic: detect exit code 1, re-run once in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [ ] T048 [US7] Add retry logging "E2E tests failed (attempt 1/2), retrying..." in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [ ] T049 [US7] Add success logging "E2E tests passed (attempt 2/2)" in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [ ] T050 [US7] Add failure logging "E2E tests failed after 2 attempts" and exit code 2 in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`

**Checkpoint**: E2E tests automatically retry once, reducing false failures from timing issues

---

## Phase 10: User Story 8 - Constitution File Validation (Priority: P3)

**Goal**: Check `.specify/memory/constitution.md` exists during env-check, warn if missing

**Independent Test**: Run with/without constitution file, verify warning logged

### Implementation for User Story 8

- [ ] T051 [US8] Add constitution file check function in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/validator.sh`
- [ ] T052 [US8] Integrate check into `validate_environment()` in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/validator.sh`
- [ ] T053 [US8] Add success logging "Constitution file: found ✓" when file exists in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/validator.sh`
- [ ] T054 [US8] Add warning logging "Constitution file missing (optional for SpecKit projects)" when file absent in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/validator.sh`
- [ ] T055 [US8] Add hint message "Run /speckit.constitution to create" to warning in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/validator.sh`
- [ ] T056 [US8] Ensure check is non-blocking (warning only, pipeline continues) in `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/validator.sh`

**Checkpoint**: SpecKit users get early warning if constitution file is missing

---

## Phase 11: User Story 9 - Improved Integration Test Assertions (Priority: P3)

**Goal**: Refactor `.toContain('string')` to `.toMatch(/regex/)` for robust pattern matching

**Independent Test**: Run integration tests, verify patterns match correctly with regex

### Implementation for User Story 9

- [ ] T057 [P] [US9] Refactor assertions in `/home/kkk/Apps/002-mcp-manager/web/tests/integration/Header.integration.test.js` to use `.toMatch(/regex/)`
- [ ] T058 [P] [US9] Refactor assertions in `/home/kkk/Apps/002-mcp-manager/web/tests/integration/modules.integration.test.js` to use `.toMatch(/regex/)`
- [ ] T059 [US9] Run integration tests to verify refactored assertions pass: `cd web && npm run test:integration`
- [ ] T060 [US9] Verify tests now correctly reject malformed output (add test case if needed) in integration test files

**Checkpoint**: Integration tests use robust regex patterns instead of brittle substring matching

---

## Phase 12: Polish & Documentation

**Purpose**: Cross-cutting improvements and documentation updates

- [ ] T061 [P] Update `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/README.md` with new features (timeout, parallel, correlation IDs, retry)
- [ ] T062 [P] Update `/home/kkk/Apps/002-mcp-manager/scripts/tui/README.md` with real-time progress feature
- [ ] T063 [P] Create quickstart guide in `/home/kkk/Apps/002-mcp-manager/specs/002-cicd-pipeline-enhancements/quickstart.md`
- [ ] T064 Verify all exit codes documented in help message of `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh`
- [ ] T065 Run full pipeline end-to-end test with all profiles (dev/ui/full)
- [ ] T066 Test timeout enforcement with artificial delay (verify exit code 5)
- [ ] T067 Test parallel test execution (verify 40-60% speedup)
- [ ] T068 Test TUI real-time progress (verify updates every 1-2 seconds)
- [ ] T069 Test E2E retry logic (verify 2 attempts on failure)
- [ ] T070 Validate JSON log schema compliance with `/home/kkk/Apps/002-mcp-manager/specs/002-cicd-pipeline-enhancements/contracts/log-schema.json`
- [ ] T071 Validate deployment state schema compliance with `/home/kkk/Apps/002-mcp-manager/specs/002-cicd-pipeline-enhancements/contracts/deployment-state-schema.json`
- [ ] T072 Code cleanup: remove debug logging, finalize comments
- [ ] T073 Run quickstart.md validation (if created)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational - P1 priority, must complete first
- **US2 (Phase 4)**: Depends on Foundational - P1 priority, can run parallel with US1 (different files)
- **US3 (Phase 5)**: Depends on US1 completion - needs timeout baseline before parallelization
- **US4 (Phase 6)**: Depends on Foundational - P2 priority, can run parallel with US3 (different files)
- **US6 (Phase 7)**: Depends on Foundational - P3 priority, can run parallel with US4 (different concerns)
- **US5 (Phase 8)**: Depends on US4 AND US6 completion - needs enhanced logs with correlation IDs
- **US7 (Phase 9)**: Depends on Foundational - P3 priority, independent
- **US8 (Phase 10)**: Depends on Foundational - P3 priority, independent
- **US9 (Phase 11)**: Depends on Foundational - P3 priority, independent, can run parallel with US7/US8
- **Polish (Phase 12)**: Depends on all desired user stories being complete

### Critical Path (Sequential Dependencies)

```
Phase 1 (Setup)
  ↓
Phase 2 (Foundational) ← BLOCKS ALL STORIES
  ↓
Phase 3 (US1 - Timeout) ← P1, BLOCKS US3
  ↓
Phase 5 (US3 - Parallel Tests) ← P2, depends on US1
```

### Parallel Opportunities (After Foundational Complete)

```
Parallel Branch 1:
  Phase 3 (US1) → Phase 5 (US3)

Parallel Branch 2:
  Phase 4 (US2) [independent, P1]

Parallel Branch 3:
  Phase 6 (US4) + Phase 7 (US6) → Phase 8 (US5)

Parallel Branch 4:
  Phase 9 (US7) [independent, P3]

Parallel Branch 5:
  Phase 10 (US8) [independent, P3]

Parallel Branch 6:
  Phase 11 (US9) [independent, P3]
```

### Within Each User Story

- P1 stories before P2 stories before P3 stories (priority order)
- US1 must complete before US3 (dependency)
- US4 + US6 must complete before US5 (dependency)
- All other stories are independent after Foundational phase

### Parallel Task Execution (Within Story)

**Phase 2 (Foundational)**:
- T006, T007 can run in parallel (different files)

**Phase 6 (US4)**:
- T028, T029, T030, T031 can run in parallel (all in same file, but different functions)

**Phase 7 (US6)**:
- T034, T035 can run in parallel (different concerns)

**Phase 11 (US9)**:
- T057, T058 can run in parallel (different files)

**Phase 12 (Polish)**:
- T061, T062, T063 can run in parallel (different files)

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US1 (Timeout enforcement)
4. Complete Phase 4: US2 (Deployment state tracking)
5. **STOP and VALIDATE**: Test P1 features independently
6. Deploy if ready - NFR-003 now enforced, deployment tracking reliable

### Incremental Delivery by Priority

1. **P1 Complete** (US1, US2) → Foundation + Compliance ✓
2. **Add P2** (US3, US4, US5) → Performance + Observability ✓
3. **Add P3** (US6, US7, US8, US9) → Polish + Stability ✓

### Parallel Team Strategy

With multiple developers (after Foundational complete):

- **Developer A**: Phase 3 (US1) → Phase 5 (US3)
- **Developer B**: Phase 4 (US2)
- **Developer C**: Phase 6 (US4) + Phase 7 (US6) → Phase 8 (US5)
- **Developer D**: Phase 9 (US7) + Phase 10 (US8) + Phase 11 (US9)

---

## Validation Checkpoints

After each phase, verify:

- **Phase 3 (US1)**: Pipeline exits with code 5 at 300 seconds
- **Phase 4 (US2)**: Deployment workflow retries 3 times and fails on exhaustion
- **Phase 5 (US3)**: Test phase 40-60% faster, serial fallback works
- **Phase 6 (US4)**: All logs include source_file, line_number, function_name
- **Phase 7 (US6)**: All logs include unique run_id
- **Phase 8 (US5)**: TUI updates every 1-2 seconds with live progress
- **Phase 9 (US7)**: E2E tests retry once on failure
- **Phase 10 (US8)**: Constitution check warns if file missing
- **Phase 11 (US9)**: Integration tests use regex matchers

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story (US1-US9)
- Each user story should be independently completable and testable
- No tests included (infrastructure enhancement, not application development)
- All changes maintain backwards compatibility with Feature 001
- Exit code precedence: Test failure (2) > Timeout (5)
- Constitution check is non-blocking (warning only)

---

**Task Count**: 73 tasks across 12 phases
**User Stories**: 9 (2 P1, 3 P2, 4 P3)
**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 5
**Estimated Parallel Execution**: ~60% reduction in wall-clock time with 4 developers
**Status**: Ready for implementation via `/speckit.implement`
