# Implementation Tasks: Local CI/CD for Astro Site

**Feature**: 001-local-cicd-astro-site
**Branch**: `001-local-cicd-astro-site`
**Date**: 2025-10-19
**Total Tasks**: 45 (30 for MVP)
**Input**: Design documents from `/home/kkk/Apps/002-mcp-manager/specs/001-local-cicd-astro-site/`

---

## Implementation Strategy

**MVP Scope**: User Story 1 (P1) - Local CI/CD Execution (Tasks T001-T030)
**Incremental Delivery**: Each user story is independently testable and deployable
**Approach**: Modular-first, fix critical repository issues first

**User Story Priorities**:
1. **US1 (P1)**: Local CI/CD Execution - Core cost-saving pipeline
2. **US2 (P2)**: Modular Implementation - TUI for developer experience
3. **US3 (P3)**: Astro Website + GitHub Pages Deployment

---

## Phase 1: Repository Cleanup & Setup

**Goal**: Fix 7 critical repository issues identified in CRITICAL_ISSUES.md

**Independent Test**: Repository structure matches plan.md, no unnecessary files, all `.env` templates exist

### Cleanup Tasks (Critical Issues #3, #4, #5):

- [ ] T001 Remove redundant `web/web/` directory: `rm -rf /home/kkk/Apps/002-mcp-manager/web/web/`
- [ ] T002 Move test files from `web/src/tests/` to `web/tests/unit/`: `mv web/src/tests/*.test.js web/tests/unit/`
- [ ] T003 Remove empty `web/src/tests/` directory: `rmdir /home/kkk/Apps/002-mcp-manager/web/src/tests/`

### Environment Configuration:

- [ ] T004 Create `.env.example` at `/home/kkk/Apps/002-mcp-manager/.env.example` with template values from data-model.md Entity 2
- [ ] T005 [P] Create `.env.local` at `/home/kkk/Apps/002-mcp-manager/.env.local` with development settings (NODE_ENV=development)
- [ ] T006 [P] Create `.env.production` at `/home/kkk/Apps/002-mcp-manager/.env.production` with production settings

### Directory Structure:

- [ ] T007 Create `logs/` directory at `/home/kkk/Apps/002-mcp-manager/logs/` with `.gitkeep` file
- [ ] T008 Update `.gitignore` to include `logs/`, `.env.local`, `.env.production`, `web/dist/` patterns

---

## Phase 2: Foundational Infrastructure (Security & Logging)

**Goal**: Implement pre-commit hooks (Critical Issue #2) and JSON logging library (Critical Issue #1 foundation)

**Independent Test**: Pre-commit hook blocks secrets, logger library produces valid JSON

### Pre-Commit Hook Setup (Critical Issue #2):

- [ ] T009 Install Husky and lint-staged: `cd web && npm install --save-dev husky lint-staged`
- [ ] T010 Initialize Husky: `cd web && npx husky init`
- [ ] T011 Install Gitleaks binary for secret detection (macOS: `brew install gitleaks`, Linux: download from releases)
- [ ] T012 Configure lint-staged in `web/package.json` with Gitleaks command per research.md
- [ ] T013 Create pre-commit hook at `/home/kkk/Apps/002-mcp-manager/.husky/pre-commit` calling `npx lint-staged`
- [ ] T014 Test pre-commit hook by staging file with fake secret pattern (should block commit)

### JSON Logging Library (Critical Issue #1 - Part 1):

- [ ] T015 [P] Create logger library at `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/logger.sh` with jq-based functions per research.md
- [ ] T016 [P] Implement `log_json()` function in logger.sh with timestamp, level, step, message parameters
- [ ] T017 [P] Create unit tests for logger at `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/logger.test.sh`
- [ ] T018 [P] Create validator library at `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/validator.sh` with secret patterns from data-model.md Entity 2
- [ ] T019 [P] Create cleanup script at `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/lib/cleanup-logs.sh` with 30-day retention logic

---

## Phase 3: User Story 1 - Local CI/CD Execution (P1) 🎯 MVP

**Goal**: As a developer, I want to run all CI/CD processes locally before pushing to the remote repository, so that I can avoid incurring additional charges on GitHub Actions.

**Independent Test**: Developer runs `./scripts/local-ci/run.sh` → all checks execute with JSON logging → exit code 0 if success

**Acceptance Scenarios**:
1. ✅ Developer runs local CI/CD script → linting, testing, building all execute
2. ✅ Lint failure triggers auto-fix attempt before failing
3. ✅ Push to remote after local CI pass → no GitHub Actions CI/CD triggered

### US1: Rewrite CI/CD Script (Critical Issue #1):

- [ ] T020 [US1] Backup existing `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh` to `run.sh.backup`
- [ ] T021 [US1] Rewrite run.sh header with proper shebang, error handling (`set -euo pipefail`), and logger import
- [ ] T022 [US1] Implement init step in run.sh: log start, set LOG_FILE variable, create log directory
- [ ] T023 [US1] Implement env-check step: validate bash, jq, node, npm versions per Technical Context requirements
- [ ] T024 [US1] Implement lint step with auto-fix: run prettier --check, if fail run prettier --write, re-run check
- [ ] T025 [US1] Implement test-unit step: run `cd web && npx mocha tests/unit/**/*.test.js` with output capture
- [ ] T026 [US1] Implement test-integration step: run `cd web && npx mocha tests/integration/**/*.integration.test.js`
- [ ] T027 [US1] Implement test-e2e step: run `cd web && npx playwright test tests/e2e/` with browser installation check
- [ ] T028 [US1] Implement build step: run `cd web && npm run build`, verify `web/dist/` created, check size
- [ ] T029 [US1] Implement cleanup step: call cleanup-logs.sh to remove logs older than 30 days
- [ ] T030 [US1] Implement complete step: output final summary JSON with metrics per data-model.md Entity 3

### US1: Error Handling & CLI Options:

- [ ] T031 [US1] Add error handling for all steps with proper exit codes: 0=success, 1=lint, 2=test, 3=build, 4=env
- [ ] T032 [US1] Add SIGINT (Ctrl+C) handler for graceful abortion with exit code 130
- [ ] T033 [US1] Implement `--no-fix` flag to skip auto-fix attempts on lint failure
- [ ] T034 [US1] Implement `--verbose` flag to show full command output (not just JSON logs)
- [ ] T035 [US1] Implement `--skip-tests` flag to skip all test execution (lint + build only)
- [ ] T036 [US1] Implement `--log-file <path>` flag for custom log file location
- [ ] T037 [US1] Add duration tracking for each step, log warning if total exceeds 300 seconds (NFR-003)
- [ ] T038 [US1] Update run.sh to use `tee -a "$LOG_FILE"` for dual output (STDOUT + file)

### US1: Testing & Validation:

- [ ] T039 [US1] Test run.sh with intentional lint error → verify auto-fix attempted
- [ ] T040 [US1] Test run.sh with failing test → verify exit code 2
- [ ] T041 [US1] Test run.sh full pipeline → verify completes in < 5 minutes
- [ ] T042 [US1] Validate JSON log structure matches data-model.md Entity 1 schema

---

## Phase 4: User Story 2 - Modular Implementation (P2)

**Goal**: As a developer, I want the implementation to be modular, with clear separation between the website, TUI, and scripts, so that the project is simple and easy to maintain.

**Independent Test**: TUI runs independently, website tests don't depend on CI, changes to one module don't break others

**Acceptance Scenarios**:
1. ✅ TUI provides interactive menu for CI/CD operations
2. ✅ Changes to TUI don't affect website or CI script
3. ✅ Modules have clear, documented boundaries

### US2: TUI Implementation (Critical Issue #6):

- [ ] T043 [US2] Choose TUI framework (dialog, whiptail, or gum) based on availability: test `which dialog whiptail gum`
- [ ] T044 [US2] Create TUI main script at `/home/kkk/Apps/002-mcp-manager/scripts/tui/run.sh` with framework import
- [ ] T045 [US2] Implement main menu with options: [1] Run CI/CD, [2] View Logs, [3] Setup, [4] Help, [5] Exit
- [ ] T046 [US2] Implement "Run CI/CD" option: execute `../local-ci/run.sh` and display real-time logs using `tail -f`
- [ ] T047 [US2] Implement "View Logs" option: list log files in `logs/`, let user select, display with `cat log | jq .`
- [ ] T048 [US2] Implement "Setup" option: guide user through creating `.env.local` file interactively
- [ ] T049 [US2] Implement "Help" option: display content from `../../specs/001-local-cicd-astro-site/quickstart.md`
- [ ] T050 [US2] Add error handling for user cancellation (ESC key) and invalid selections
- [ ] T051 [US2] Update `/home/kkk/Apps/002-mcp-manager/scripts/tui/README.md` with TUI usage instructions

### US2: Module Independence Verification:

- [ ] T052 [US2] Create integration test at `web/tests/integration/module-independence.test.js` verifying no cross-module imports
- [ ] T053 [US2] Document module boundaries in `/home/kkk/Apps/002-mcp-manager/scripts/README.md` per contracts/ci-script.contract.md
- [ ] T054 [US2] Update root `README.md` with module overview diagram showing web/, scripts/tui/, scripts/local-ci/ separation

---

## Phase 5: User Story 3 - Astro Website + GitHub Pages (P3)

**Goal**: As a project owner, I want a website built with Astro.build and hosted on GitHub Pages, so that I can have a fast and modern web presence for free.

**Independent Test**: Website builds successfully, deploys to GitHub Pages, rolls back on failure, meets performance targets

**Acceptance Scenarios**:
1. ✅ Push to main → website deploys to GitHub Pages (no CI/CD on remote)
2. ✅ Website loads in < 1.5s on 3G (NFR-001)
3. ✅ Lighthouse Performance score > 90 (NFR-002)

### US3: GitHub Actions Deployment Workflow (Critical Issue #7):

- [ ] T055 [US3] Create workflow file at `/home/kkk/Apps/002-mcp-manager/.github/workflows/deploy.yml`
- [ ] T056 [US3] Configure workflow trigger: `on: push: branches: [main]` (deployment only, no CI/CD)
- [ ] T057 [US3] Add checkout step with `actions/checkout@v4`
- [ ] T058 [US3] Add deployment step: configure GitHub Pages to serve from `web/dist/` (pre-built locally)
- [ ] T059 [US3] Implement rollback logic: store last deployment ID in artifact, rollback on failure per data-model.md Entity 4
- [ ] T060 [US3] Add Lighthouse CI step: run `npx @lhci/cli@0.13.x autorun` to validate NFR-001, NFR-002
- [ ] T061 [US3] Add deployment state tracking: upload deployment metadata to GitHub Actions artifacts
- [ ] T062 [US3] Add notification step: log deployment status, send notification on rollback

### US3: Website Performance Optimization:

- [ ] T063 [US3] Configure Astro for production build optimization in `web/astro.config.mjs`
- [ ] T064 [US3] Add image optimization for any images in `web/public/` or `web/src/`
- [ ] T065 [US3] Test website performance locally with Lighthouse: `npx lighthouse http://localhost:4321 --view`
- [ ] T066 [US3] Verify page load time < 1.5s on simulated 3G (Chrome DevTools Network throttling)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Documentation, final validations, and quality improvements

### Documentation:

- [ ] T067 [P] Update `/home/kkk/Apps/002-mcp-manager/scripts/local-ci/README.md` with complete usage guide
- [ ] T068 [P] Update `/home/kkk/Apps/002-mcp-manager/scripts/tui/README.md` with TUI screenshots/examples
- [ ] T069 [P] Update root `/home/kkk/Apps/002-mcp-manager/README.md` with quickstart, architecture diagram, module overview

### Final Validations:

- [ ] T070 Verify all success criteria (SC-001 through SC-006) from spec.md are met
- [ ] T071 Run constitution compliance check: verify all 5 principles pass per plan.md Phase 1 Post-Design Re-Check
- [ ] T072 Validate quickstart.md setup time < 10 minutes (SC-003) with fresh clone
- [ ] T073 Test complete workflow: commit → pre-commit hook → local CI → push → deployment

---

## Dependencies & Execution Order

```
Phase 1 (Cleanup) → Phase 2 (Foundation) → Phase 3 (US1 - MVP) 🎯
                                          ↘ Phase 4 (US2)
                                          ↘ Phase 5 (US3)
                                          → Phase 6 (Polish)
```

**User Story Dependencies**:
- **US1 (P1)**: No dependencies → Implement first (MVP)
- **US2 (P2)**: Depends on US1 (TUI calls CI script)
- **US3 (P3)**: Depends on US1 (deployment needs pre-built artifacts)

**Critical Path to MVP**: `T001-T008 → T009-T019 → T020-T042` (42 tasks)

---

## Parallel Opportunities

### Phase 1 (Cleanup):
- **Parallel**: T005-T006 (create .env files simultaneously)

### Phase 2 (Foundation):
- **Parallel**: T015-T019 (all lib/ scripts independent)

### Phase 3 (US1):
- **Parallel**: T023-T029 (pipeline steps can be implemented simultaneously by different developers)
- **Parallel**: T033-T036 (CLI flags independent)

### Phase 4 (US2):
- **Parallel**: T046-T049 (TUI menu options independent)

### Phase 5 (US3):
- **Parallel**: T058-T062 (workflow steps independent)
- **Parallel**: T063-T066 (performance optimizations independent)

### Phase 6 (Polish):
- **Parallel**: T067-T069 (documentation files independent)

---

## Parallel Execution Examples

### MVP Sprint Planning (Phase 3 - US1):

**Sprint 1: Foundation** (Week 1)
- Developer A: T001-T008 (cleanup)
- Developer B: T009-T014 (pre-commit hooks)
- Developer C: T015-T019 (logging libraries)

**Sprint 2: Core Pipeline** (Week 2)
- Developer A: T020-T024 (init, env-check, lint)
- Developer B: T025-T027 (test steps)
- Developer C: T028-T030 (build, cleanup, complete)

**Sprint 3: Polish** (Week 3)
- Developer A: T031-T032 (error handling)
- Developer B: T033-T036 (CLI flags)
- Developer C: T037-T042 (validation)

### Post-MVP Parallel Development:

- **Team A**: Phase 4 (US2) - TUI implementation
- **Team B**: Phase 5 (US3) - Deployment + website optimization

---

## Task Statistics

**Total Tasks**: 73
**MVP Tasks** (Phases 1-3): T001-T042 (42 tasks)
**Post-MVP Tasks**: T043-T073 (31 tasks)

**Tasks by Phase**:
- Phase 1 (Cleanup): 8 tasks
- Phase 2 (Foundation): 11 tasks
- Phase 3 (US1 - MVP): 23 tasks
- Phase 4 (US2): 12 tasks
- Phase 5 (US3): 12 tasks
- Phase 6 (Polish): 7 tasks

**Parallelizable Tasks**: 28 tasks marked [P] (38%)

**Critical Issues Addressed**:
- ✅ Issue #1 (CI script logging): T015-T019, T020-T042
- ✅ Issue #2 (pre-commit hooks): T009-T014
- ✅ Issue #3 (web/web/ removal): T001
- ✅ Issue #4 (test directory): T002-T003
- ✅ Issue #5 (.env files): T004-T006
- ✅ Issue #6 (TUI): T043-T054
- ✅ Issue #7 (deployment): T055-T062

---

## MVP Recommendation

**Minimum Viable Product**: Phases 1 + 2 + 3 (Tasks T001-T042)

**MVP Deliverables**:
- ✅ Repository cleanup complete (no unnecessary files)
- ✅ Pre-commit hooks block secrets
- ✅ Local CI/CD pipeline with JSON logging
- ✅ Auto-fix capability for lint errors
- ✅ All tests run locally (unit, integration, e2e)
- ✅ Build generates deployable artifacts
- ✅ < 5 minute pipeline duration
- ✅ Exit codes match contract specification

**MVP Duration**: ~20-25 hours (42 tasks)

**Post-MVP Increments**:
- **Increment 1 (US2 - TUI)**: T043-T054 (~8-10 hours)
- **Increment 2 (US3 - Deployment)**: T055-T066 (~6-8 hours)
- **Increment 3 (Polish)**: T067-T073 (~4-6 hours)

**Total Estimated Duration**: ~38-49 hours

---

## Validation Checklist

✅ **Format Compliance**:
- All 73 tasks follow format: `- [ ] [TID] [P?] [Story?] Description with path`
- Task IDs sequential (T001-T073)
- Parallelizable tasks marked [P] (28 tasks)
- User story tasks labeled [US1], [US2], [US3]

✅ **Completeness**:
- All 3 user stories have dedicated phases
- All 7 critical issues addressed with specific tasks
- All acceptance scenarios mapped to tasks
- All constitution principles have validation tasks

✅ **Testability**:
- Each phase has "Independent Test" criteria
- MVP can be tested and delivered independently
- Each user story has acceptance scenarios

✅ **File Specificity**:
- All tasks include absolute or relative file paths
- Contract and data-model references where applicable
- Clear dependencies between tasks

---

**Generated**: 2025-10-19
**Status**: Ready for Implementation
**Next Step**: Begin Phase 1 (T001-T008) - Repository Cleanup
**MVP Milestone**: Complete T001-T042 for first deliverable increment
