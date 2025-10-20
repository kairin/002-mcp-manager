# Implementation Plan: CI/CD Pipeline Improvements

**Branch**: `002-cicd-pipeline-enhancements` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-cicd-pipeline-enhancements/spec.md`

## Summary

Enhance the existing Local CI/CD pipeline (Feature 001) with 11 targeted improvements across 4 priority levels to achieve 100% NFR-003 compliance (5-minute timeout), eliminate silent deployment failures, reduce test phase duration by 40-60% through parallelization, add professional-grade observability (correlation IDs, structured error context), improve TUI UX with real-time progress, and add retry logic for flaky E2E tests. All changes are backwards-compatible enhancements to the existing `scripts/local-ci/run.sh` and `scripts/tui/run.sh` infrastructure.

## Technical Context

**Language/Version**: Bash 4.4+ (existing Feature 001 stack)
**Primary Dependencies**:
- `jq` (JSON processing - existing)
- `bash` builtins (`SECONDS`, `$LINENO`, `${FUNCNAME[@]}`)
- `date` command (for correlation IDs)
- `wait` builtin (parallel job management)
- GitHub Actions (deployment workflow enhancement)

**Storage**:
- JSON log files in `logs/ci-YYYYMMDD_HHMMSS.log` (existing)
- Deployment state tracking in `.github/deployment-state.json` (new)

**Testing**:
- Mocha for unit/integration tests (existing)
- Playwright for E2E tests (existing)
- Shell script syntax validation (`bash -n`)

**Target Platform**: Linux/macOS development environments, GitHub Actions runners
**Project Type**: Enhancement to existing shell-based CI/CD pipeline (single project structure)

**Performance Goals**:
- Pipeline completion: < 300 seconds (hard limit, enforced by FR-001)
- Test phase reduction: 40-60% faster via parallelization (FR-005)
- TUI updates: Minimum every 2 seconds (FR-009)
- Timeout enforcement: Within 1 second of threshold (SC-001)

**Constraints**:
- Backwards compatibility: Existing Feature 001 workflows must continue working
- No new dependencies beyond bash builtins
- Exit code precedence: Test failure (2) takes priority over timeout (5) when both occur
- Serial fallback for resource contention (FR-017)

**Scale/Scope**:
- Existing 9-step pipeline (init, env-check, lint, test-unit, test-integration, test-e2e, build, cleanup, complete)
- ~30 unit tests, ~15 integration tests, ~5 E2E tests (baseline from spec)
- Support for 3 profiles (dev/ui/full) via TUI and CLI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Modular-First Design ✅ PASS

- **Requirement**: Each module (website, TUI, scripts) must be self-contained
  - **Compliance**: All enhancements target existing `scripts/local-ci/` and `scripts/tui/` modules without introducing cross-module dependencies

- **Requirement**: Modules must have clear, well-defined interfaces
  - **Compliance**: TUI continues to call CI/CD script as black box via CLI; CI/CD script logs JSON consumed by TUI parser

- **Requirement**: Changes to one module must not break others
  - **Compliance**: CI/CD enhancements (timeout, parallel tests, logging) are self-contained; TUI enhancements (progress parsing) only add optional JSON parsing of existing logs

- **Requirement**: NO unnecessary files
  - **Compliance**: Only modifying existing files (`run.sh`, `logger.sh`, `.github/workflows/deploy.yml`); adding minimal new files (deployment-state.json for tracking)

- **Requirement**: Directory structure must reflect module boundaries
  - **Compliance**: Existing structure preserved (`scripts/local-ci/`, `scripts/tui/`, `.github/workflows/`)

### Principle II: Local-First CI/CD ✅ PASS

- **Requirement**: Single command to run entire CI/CD pipeline locally
  - **Compliance**: Existing `./scripts/local-ci/run.sh` and TUI remain single-command entry points; enhancements add features without changing invocation

- **Requirement**: Local CI/CD output must be identical to GitHub Actions output
  - **Compliance**: Enhanced JSON logging provides more detail but maintains backwards compatibility; no changes to test output formats

- **Requirement**: Remote repository only executes deployment actions
  - **Compliance**: GitHub Actions workflow enhancements (deployment state tracking with retry) remain deployment-only; no CI/CD moved to remote

- **Requirement**: 100% of checks run locally
  - **Compliance**: All enhancements (timeout enforcement, parallel tests, retry logic) execute locally; only deployment tracking changes affect GitHub Actions

### Principle III: Structured Observability ✅ PASS

- **Requirement**: JSON format for logs
  - **Compliance**: FR-007 adds structured error context (source_file, line_number, function_name) to existing JSON logs; FR-010 adds correlation IDs

- **Requirement**: Clear error messages with actionable guidance
  - **Compliance**: FR-002 specifies timeout error message format; FR-004 specifies deployment failure message format with attempt counts

- **Requirement**: Warnings and errors surfaced immediately
  - **Compliance**: FR-009 TUI real-time progress parsing surfaces failures within 2 seconds; FR-015 constitution check logs warnings immediately (non-blocking)

- **Requirement**: Logs must include timestamps and context
  - **Compliance**: Existing logger.sh timestamps preserved; FR-007 adds source context; FR-010 adds correlation IDs

### Principle IV: Security by Default ✅ PASS

- **Requirement**: Use `.env` files with `.gitignore` patterns
  - **Compliance**: No changes to existing secrets management; enhancements are orthogonal

- **Requirement**: Pre-commit hooks MUST block commits containing secrets
  - **Compliance**: Existing pre-commit hooks unchanged; enhancements do not affect secret validation

- **Requirement**: NO secrets or API keys committed
  - **Compliance**: Deployment state tracking (new file `.github/deployment-state.json`) contains no secrets, only metadata (timestamps, commit SHAs, status)

### Principle V: Test Coverage Completeness ✅ PASS

- **Requirement**: Unit, integration, E2E tests must all pass
  - **Compliance**: FR-005 parallelizes existing test suites without changing test coverage; FR-012 adds E2E retry for flaky tests but preserves failure detection

- **Requirement**: Tests must pass before code can be pushed
  - **Compliance**: FR-001 timeout enforcement makes this stricter (hard fail at 5 minutes); parallel execution speeds up existing requirement

- **Rationale**: FR-016 (integration test regex matchers) improves test quality by replacing brittle `.toContain()` with robust `.toMatch()` assertions

### Performance Standards ✅ PASS WITH ENHANCEMENT

- **Requirement**: Local CI/CD pipeline completion: < 5 minutes
  - **Compliance**: FR-001 enforces this as hard requirement (exit code 5); FR-005 parallel tests reduce duration by 40-60% to help achieve this

### Deployment Standards ✅ PASS WITH ENHANCEMENT

- **Requirement**: Automatic rollback on deployment failure
  - **Compliance**: Existing FR-011 from Feature 001 preserved; FR-003/FR-004 add retry logic before rollback

- **Requirement**: Notification via log file
  - **Compliance**: FR-004 specifies clear error message with attempt counts; existing log file notification preserved

- **Requirement**: Last known good deployment preserved
  - **Compliance**: New `.github/deployment-state.json` tracks currentDeployment and lastKnownGood for manual/automatic rollback reference

### Developer Experience ✅ PASS WITH ENHANCEMENT

- **Requirement**: TUI must provide clear options without flag memorization
  - **Compliance**: Existing TUI preserved; FR-008/FR-009 enhance with real-time progress to eliminate "frozen screen" confusion

### Constitution Gates: ✅ ALL PASS

No violations detected. All enhancements comply with existing constitution principles. No complexity justifications required.

## Project Structure

### Documentation (this feature)

```
specs/002-cicd-pipeline-enhancements/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (entities: Pipeline Run, Deployment State, Log Entry, Test Execution)
├── contracts/           # Phase 1 output (exit codes, JSON log schema, deployment state schema)
│   ├── exit-codes.md    # Pipeline exit code contract (0, 1, 2, 3, 4, 5)
│   ├── log-schema.json  # Enhanced JSON log entry schema with source context and correlation ID
│   └── deployment-state-schema.json  # Deployment state tracking structure
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Structure Decision**: Single project structure (Option 1) - existing Feature 001 layout preserved with targeted enhancements to shell scripts and GitHub Actions workflow.

```
scripts/
├── local-ci/
│   ├── run.sh                    # MODIFY: Add timeout enforcement, parallel tests, correlation ID generation
│   ├── lib/
│   │   ├── logger.sh             # MODIFY: Add structured error context (source_file, line_number, function_name)
│   │   ├── validator.sh          # MODIFY: Add constitution file check (FR-014/FR-015)
│   │   ├── logger.test.sh        # MODIFY: Add tests for new logging features
│   │   └── cleanup-logs.sh       # NO CHANGE: Existing log cleanup logic preserved
│   └── README.md                 # MODIFY: Document new features (timeout, parallel, correlation IDs)
│
└── tui/
    ├── run.sh                    # MODIFY: Add real-time JSON log parsing and progress display
    └── README.md                 # MODIFY: Document real-time progress feature

.github/workflows/
└── deploy.yml                    # MODIFY: Add deployment state tracking with 3-attempt retry logic

web/tests/
├── unit/                         # NO CHANGE: Existing tests run in parallel
├── integration/                  # MODIFY: Refactor .toContain() → .toMatch(/regex/) assertions (FR-016)
└── e2e/                          # NO CHANGE: Existing tests run in parallel with retry (FR-012)

.github/
└── deployment-state.json         # NEW: Track deployment history and last known good state
```

**Files Changed**:
1. `scripts/local-ci/run.sh` - Core pipeline enhancements (timeout, parallel, correlation)
2. `scripts/local-ci/lib/logger.sh` - Structured error context
3. `scripts/local-ci/lib/validator.sh` - Constitution check
4. `scripts/tui/run.sh` - Real-time progress parsing
5. `.github/workflows/deploy.yml` - Deployment state tracking with retry
6. `web/tests/integration/*.test.js` - Regex matcher refactoring

**Files Added**:
1. `.github/deployment-state.json` - Deployment state tracking (created by workflow)

## Complexity Tracking

*No complexity violations - all enhancements comply with constitution*

## Phase 0: Research & Technical Decisions

### Research Tasks

1. **Bash timeout enforcement mechanisms**
   - Decision: Use `$SECONDS` variable with periodic checks in main loop
   - Rationale: Native bash builtin, no external dependencies, microsecond precision sufficient
   - Alternatives: `timeout` command (requires coreutils), signal-based (SIGALRM - complex)

2. **Parallel test execution with failure collection**
   - Decision: Use bash background jobs (`&`) with `wait` builtin and exit code arrays
   - Rationale: Native bash, works on all platforms, simple error aggregation
   - Alternatives: GNU Parallel (external dependency), xargs (limited error handling)

3. **Resource contention detection for serial fallback**
   - Decision: Parse test output for port/lock errors, re-run with dedicated flag
   - Rationale: Pragmatic heuristic-based detection, no complex IPC needed
   - Alternatives: Pre-allocate ports (requires test coordination), retry with backoff (slower)

4. **Bash source context extraction (LINENO, FUNCNAME)**
   - Decision: Use `${BASH_SOURCE[@]}`, `$LINENO`, `${FUNCNAME[@]}` passed to logger wrapper
   - Rationale: Native bash introspection, accurate for direct calls
   - Alternatives: `caller` builtin (limited), stack walking (complex)

5. **Correlation ID generation**
   - Decision: `run-$(date +%Y%m%d-%H%M%S)-$(head /dev/urandom | tr -dc a-z0-9 | head -c 6)`
   - Rationale: Human-readable, sortable, collision-resistant for local runs
   - Alternatives: UUID (requires `uuidgen`), PID-based (not unique across time)

6. **TUI real-time JSON log parsing**
   - Decision: `tail -f` piped to `jq` with line buffering, clear/redraw on update
   - Rationale: Standard Unix tools, works with existing JSON logs, minimal latency
   - Alternatives: `inotify` (Linux-only), polling (higher latency), terminal multiplexer (overkill)

7. **GitHub Actions deployment retry logic**
   - Decision: Bash loop with 3 attempts, exponential backoff, failure on exhaustion
   - Rationale: Simple, predictable, integrates with existing workflow
   - Alternatives: GitHub Actions `retry` action (third-party), manual retries (user burden)

8. **E2E test retry mechanism**
   - Decision: Wrapper around Playwright test step, detect exit code 1, re-run once
   - Rationale: Transparent to tests, preserves genuine failures, simple implementation
   - Alternatives: Playwright built-in retry (per-test, too granular), manual flags (user burden)

### Output: research.md

**File**: `specs/002-cicd-pipeline-enhancements/research.md`

**Contents**:
- Technical decisions for all 8 research areas above
- Code snippets demonstrating bash patterns (timeout check, parallel jobs, source context)
- Trade-off analysis for each decision
- Compatibility matrix (Linux/macOS, bash 4.4+/5.x)

## Phase 1: Design & Contracts

### Data Model

**File**: `specs/002-cicd-pipeline-enhancements/data-model.md`

#### Entity: Pipeline Run
- **run_id** (string, format: "run-YYYYMMDD-HHMMSS-{6char}"): Unique correlation ID
- **start_time** (integer, Unix timestamp): Pipeline start
- **end_time** (integer, Unix timestamp): Pipeline completion
- **duration** (integer, seconds): Total execution time
- **exit_code** (integer, 0-5): Pipeline result code
- **profile** (enum: "dev"|"ui"|"full"): Test profile used
- **triggered_by** (enum: "TUI"|"CLI"): Invocation method
- **steps_completed** (array of strings): Completed step names

**Lifecycle**: Created at init step, updated at each step completion, finalized at complete step

#### Entity: Deployment State Record
- **deployment_id** (string, format: "deploy-{timestamp}"): Unique deployment ID
- **timestamp** (string, ISO 8601): Deployment time
- **commit_sha** (string, 40 chars): Git commit SHA
- **status** (enum: "success"|"failure"|"rolled_back"): Deployment outcome
- **git_operations_attempts** (integer, 1-3): Number of git push attempts
- **error_message** (string, optional): Failure reason if status=failure

**Lifecycle**: Created on deployment start, updated on git operation retry, finalized on success/failure

**Storage**: `.github/deployment-state.json` (structure: `{currentDeployment: {...}, lastKnownGood: {...}, history: [...]}`)

#### Entity: Log Entry
- **timestamp** (string, ISO 8601): Log event time
- **level** (enum: "info"|"warn"|"error"): Severity
- **message** (string): Human-readable message
- **run_id** (string): Correlation ID from Pipeline Run
- **source_file** (string): Relative path to source file (e.g., "lib/logger.sh")
- **line_number** (integer): Line number where log was generated
- **function_name** (string): Function name generating log
- **step_name** (string): Current pipeline step
- **duration_ms** (integer, optional): Step duration if applicable

**Lifecycle**: Generated on each logging call, appended to JSON log file

#### Entity: Test Execution
- **test_type** (enum: "unit"|"integration"|"e2e"): Test suite type
- **attempt_number** (integer, 1-2): Retry attempt (1=first, 2=retry)
- **status** (enum: "passed"|"failed"|"skipped"): Test outcome
- **duration** (integer, seconds): Test execution time
- **failure_count** (integer): Number of failed tests
- **started_at** (integer, Unix timestamp): Test start time
- **completed_at** (integer, Unix timestamp): Test completion time
- **run_in_parallel** (boolean): Whether test ran concurrently with others
- **fallback_to_serial** (boolean): Whether test fell back to serial execution due to resource contention

**Lifecycle**: Created on test step start, updated on completion/retry, logged to JSON

### API Contracts

**Directory**: `specs/002-cicd-pipeline-enhancements/contracts/`

#### Contract: Exit Codes (`exit-codes.md`)

```markdown
# Pipeline Exit Codes

| Code | Meaning | Triggered By |
|------|---------|--------------|
| 0    | Success | All steps passed, duration < 300s |
| 1    | Lint failure | Prettier/linter errors not auto-fixable |
| 2    | Test failure | Unit, integration, or E2E tests failed after retries |
| 3    | Build failure | npm run build failed |
| 4    | Environment validation failure | Missing dependencies (node, npm, jq) |
| 5    | Timeout violation (NFR-003) | Duration ≥ 300 seconds |

**Precedence**: If multiple failures occur, use lowest code except timeout (5) which is overridden by other failures (exit 2 takes precedence over exit 5 per spec User Story 1 scenario 3).
```

#### Contract: Enhanced JSON Log Schema (`log-schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Enhanced Pipeline Log Entry",
  "type": "object",
  "required": ["timestamp", "level", "message", "run_id", "source_file", "line_number", "function_name", "step_name"],
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of log entry"
    },
    "level": {
      "type": "string",
      "enum": ["info", "warn", "error"],
      "description": "Log severity level"
    },
    "message": {
      "type": "string",
      "description": "Human-readable log message"
    },
    "run_id": {
      "type": "string",
      "pattern": "^run-\\d{8}-\\d{6}-[a-z0-9]{6}$",
      "description": "Unique correlation ID for this pipeline run"
    },
    "source_file": {
      "type": "string",
      "description": "Relative path to source file generating log"
    },
    "line_number": {
      "type": "integer",
      "minimum": 1,
      "description": "Line number in source file"
    },
    "function_name": {
      "type": "string",
      "description": "Function name generating log"
    },
    "step_name": {
      "type": "string",
      "description": "Current pipeline step (init, env-check, lint, test-unit, etc.)"
    },
    "duration_ms": {
      "type": "integer",
      "minimum": 0,
      "description": "Optional step duration in milliseconds"
    }
  }
}
```

#### Contract: Deployment State Schema (`deployment-state-schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Deployment State Tracking",
  "type": "object",
  "required": ["currentDeployment", "lastKnownGood"],
  "properties": {
    "currentDeployment": {
      "type": "object",
      "required": ["deployment_id", "timestamp", "commit_sha", "status"],
      "properties": {
        "deployment_id": {"type": "string", "pattern": "^deploy-\\d+$"},
        "timestamp": {"type": "string", "format": "date-time"},
        "commit_sha": {"type": "string", "minLength": 40, "maxLength": 40},
        "status": {"type": "string", "enum": ["success", "failure", "rolled_back"]},
        "git_operations_attempts": {"type": "integer", "minimum": 1, "maximum": 3},
        "error_message": {"type": "string"}
      }
    },
    "lastKnownGood": {
      "type": "object",
      "description": "Reference to last successful deployment for rollback",
      "properties": {
        "deployment_id": {"type": "string"},
        "commit_sha": {"type": "string", "minLength": 40, "maxLength": 40},
        "timestamp": {"type": "string", "format": "date-time"}
      }
    },
    "history": {
      "type": "array",
      "items": {"$ref": "#/properties/currentDeployment"},
      "description": "Optional deployment history (last 10 entries)"
    }
  }
}
```

### Quickstart Guide

**File**: `specs/002-cicd-pipeline-enhancements/quickstart.md`

**Contents**:
1. Prerequisites verification (bash 4.4+, jq installed, existing Feature 001 complete)
2. Quick test of new features:
   - Run pipeline with artificial delay to trigger timeout (exit 5)
   - Run TUI to see real-time progress updates
   - Check JSON logs for correlation IDs and source context
   - Simulate E2E flaky test to verify retry logic
   - Check `.github/deployment-state.json` after GitHub deployment
3. Troubleshooting guide for common issues:
   - Parallel tests hanging: Check for resource contention in logs, verify serial fallback triggered
   - TUI shows blank: Verify JSON log format, check `tail -f` permissions
   - Timeout not enforcing: Verify bash version ≥ 4.4, check `$SECONDS` variable

### Agent Context Update

**Action**: Run `.specify/scripts/bash/update-agent-context.sh claude`

**Expected Updates to `.claude/AGENTS.md` (between markers)**:
- Add bash parallel execution patterns (background jobs, `wait`, exit code arrays)
- Add bash source context introspection (`$LINENO`, `${FUNCNAME[@]}`, `${BASH_SOURCE[@]}`)
- Add correlation ID generation pattern
- Add JSON log schema with structured error context
- Add deployment state tracking schema
- Note: TUI real-time progress parsing using `tail -f | jq`

## Phase 2: Task Generation

**Command**: `/speckit.tasks` (user invokes after Phase 1 complete)

**Expected Task Breakdown** (preview - actual generation by `/speckit.tasks`):
- **Phase 1 (P1 - Critical)**: FR-001/FR-002 timeout enforcement, FR-003/FR-004 deployment retry
- **Phase 2 (P2 - Performance)**: FR-005/FR-006 parallel tests, FR-017 serial fallback
- **Phase 3 (P2 - Observability)**: FR-007 structured logging, FR-010/FR-011 correlation IDs
- **Phase 4 (P2 - UX)**: FR-008/FR-009 TUI real-time progress
- **Phase 5 (P3 - Polish)**: FR-012/FR-013 E2E retry, FR-014/FR-015 constitution check, FR-016 regex matchers

**Dependencies**:
- Phase 2 depends on Phase 1 (parallel tests need timeout enforcement baseline)
- Phase 4 depends on Phase 3 (TUI parsing needs enhanced JSON logs with correlation IDs)
- Phase 5 can run in parallel with Phase 3/4

## Post-Planning Validation

### Constitution Re-Check ✅ PASS

All principles remain compliant after Phase 1 design:
- Modular-First Design: File changes scoped to existing modules
- Local-First CI/CD: All enhancements run locally, deployment tracking only change to GitHub Actions
- Structured Observability: Enhanced JSON logging with source context and correlation IDs
- Security by Default: No changes to secrets management
- Test Coverage: Parallel execution and retry logic improve test reliability

### Unknowns Resolved ✅ COMPLETE

All "NEEDS CLARIFICATION" items from Technical Context resolved in Phase 0 research:
- Timeout mechanism: `$SECONDS` with periodic checks ✓
- Parallel execution: Bash background jobs with `wait` ✓
- Resource contention: Heuristic-based detection with serial fallback ✓
- Source context: `${BASH_SOURCE[@]}`, `$LINENO`, `${FUNCNAME[@]}` ✓
- Correlation IDs: Timestamp + random suffix ✓
- TUI parsing: `tail -f | jq` with terminal redraw ✓
- Deployment retry: Bash loop with exponential backoff ✓
- E2E retry: Wrapper around Playwright step ✓

## Next Steps

1. ✅ **Phase 0 Complete**: Research decisions documented, all technical unknowns resolved
2. ✅ **Phase 1 Complete**: Data model defined, API contracts written, quickstart guide ready
3. **User Action Required**: Run `/speckit.tasks` to generate detailed task breakdown (tasks.md)
4. **User Action Required**: Run `/speckit.analyze` to validate cross-artifact consistency
5. **Implementation Ready**: After tasks.md generation, feature ready for `/speckit.implement`

---

**Planning Status**: ✅ COMPLETE
**Constitution Compliance**: ✅ VERIFIED
**Technical Risks**: ✅ MITIGATED (all research complete, patterns validated)
**Ready for Task Generation**: ✅ YES
