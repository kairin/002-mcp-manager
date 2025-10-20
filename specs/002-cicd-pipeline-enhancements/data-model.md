# Data Model: CI/CD Pipeline Improvements

**Branch**: `002-cicd-pipeline-enhancements` | **Date**: 2025-10-20 | **Phase**: 1

## Overview

This document defines the core data entities and their relationships for the CI/CD Pipeline Improvements feature (002). All entities are stored in JSON format for structured observability and programmatic access.

## Entities

### 1. Pipeline Run

**Purpose**: Track a single execution of the CI/CD pipeline from start to completion.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `run_id` | string | ✅ | Unique correlation ID (format: `run-YYYYMMDD-HHMMSS-{6char}`) |
| `start_time` | integer | ✅ | Pipeline start timestamp (Unix epoch seconds) |
| `end_time` | integer | ✅ | Pipeline completion timestamp (Unix epoch seconds) |
| `duration` | integer | ✅ | Total execution time in seconds |
| `exit_code` | integer | ✅ | Pipeline result code (0-5, see exit code contract) |
| `profile` | string | ✅ | Test profile used (`dev`, `ui`, or `full`) |
| `triggered_by` | string | ✅ | Invocation method (`TUI` or `CLI`) |
| `steps_completed` | array[string] | ✅ | List of completed step names in execution order |

**Example**:
```json
{
  "run_id": "run-20251020-143045-k8m3q2",
  "start_time": 1729433445,
  "end_time": 1729433623,
  "duration": 178,
  "exit_code": 0,
  "profile": "dev",
  "triggered_by": "TUI",
  "steps_completed": [
    "init",
    "env-check",
    "lint",
    "test-unit",
    "test-integration",
    "test-e2e",
    "build",
    "cleanup",
    "complete"
  ]
}
```

**Lifecycle**:
1. **Created**: At `init` step, assigned correlation ID
2. **Updated**: After each step completion, append to `steps_completed`
3. **Finalized**: At `complete` step, set `end_time`, calculate `duration`, set `exit_code`

**Storage**: Embedded in log entries (each log entry contains `run_id` for correlation)

**Relationships**:
- **Has many**: Log Entries (via `run_id`)
- **Has many**: Test Executions (via `run_id`)

---

### 2. Deployment State Record

**Purpose**: Track deployment history and maintain reference to last known good deployment for rollback.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `deployment_id` | string | ✅ | Unique deployment identifier (format: `deploy-{timestamp}`) |
| `timestamp` | string | ✅ | Deployment time in ISO 8601 format (e.g., `2025-10-20T14:30:45Z`) |
| `commit_sha` | string | ✅ | Git commit SHA (40 characters) |
| `status` | string | ✅ | Deployment outcome: `success`, `failure`, or `rolled_back` |
| `git_operations_attempts` | integer | ✅ | Number of git push attempts (1-3) |
| `error_message` | string | ❌ | Failure reason (only present if `status=failure`) |

**Example (Success)**:
```json
{
  "deployment_id": "deploy-1729433445",
  "timestamp": "2025-10-20T14:30:45Z",
  "commit_sha": "5c04b60a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e",
  "status": "success",
  "git_operations_attempts": 1
}
```

**Example (Failure)**:
```json
{
  "deployment_id": "deploy-1729433500",
  "timestamp": "2025-10-20T14:31:40Z",
  "commit_sha": "7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b",
  "status": "failure",
  "git_operations_attempts": 3,
  "error_message": "Git operations failed after 3 attempts: remote rejected push"
}
```

**Lifecycle**:
1. **Created**: On deployment start in GitHub Actions workflow
2. **Updated**: After each git push retry attempt, increment `git_operations_attempts`
3. **Finalized**: On success/failure, set `status` and optionally `error_message`

**Storage**: `.github/deployment-state.json` (structure below)

**File Structure**:
```json
{
  "currentDeployment": {
    "deployment_id": "deploy-1729433445",
    "timestamp": "2025-10-20T14:30:45Z",
    "commit_sha": "5c04b60a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e",
    "status": "success",
    "git_operations_attempts": 1
  },
  "lastKnownGood": {
    "deployment_id": "deploy-1729433445",
    "commit_sha": "5c04b60a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e",
    "timestamp": "2025-10-20T14:30:45Z"
  },
  "history": [
    {
      "deployment_id": "deploy-1729433400",
      "timestamp": "2025-10-20T14:30:00Z",
      "commit_sha": "3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f",
      "status": "success",
      "git_operations_attempts": 2
    }
  ]
}
```

**Relationships**:
- **References**: Git commit (via `commit_sha`)
- **Tracks**: Deployment attempts over time (via `history` array)

---

### 3. Log Entry

**Purpose**: Structured JSON log entry for pipeline events with source context and correlation.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `timestamp` | string | ✅ | Log event time in ISO 8601 format (e.g., `2025-10-20T14:30:45Z`) |
| `level` | string | ✅ | Severity level: `info`, `warn`, or `error` |
| `message` | string | ✅ | Human-readable log message |
| `run_id` | string | ✅ | Correlation ID from Pipeline Run |
| `source_file` | string | ✅ | Relative path to source file (e.g., `scripts/local-ci/lib/logger.sh`) |
| `line_number` | integer | ✅ | Line number where log was generated (≥1) |
| `function_name` | string | ✅ | Function name generating log |
| `step_name` | string | ✅ | Current pipeline step (`init`, `env-check`, `lint`, etc.) |
| `duration_ms` | integer | ❌ | Step duration in milliseconds (only present for step completion logs) |

**Example (Info)**:
```json
{
  "timestamp": "2025-10-20T14:30:45Z",
  "level": "info",
  "message": "Running unit tests",
  "run_id": "run-20251020-143045-k8m3q2",
  "source_file": "scripts/local-ci/run.sh",
  "line_number": 123,
  "function_name": "run_step_test_unit",
  "step_name": "test-unit"
}
```

**Example (Error with Duration)**:
```json
{
  "timestamp": "2025-10-20T14:32:15Z",
  "level": "error",
  "message": "Unit tests failed: 3 test suites failed",
  "run_id": "run-20251020-143045-k8m3q2",
  "source_file": "scripts/local-ci/run.sh",
  "line_number": 127,
  "function_name": "run_step_test_unit",
  "step_name": "test-unit",
  "duration_ms": 90000
}
```

**Lifecycle**:
1. **Generated**: On each logging call (`log_info`, `log_warn`, `log_error`)
2. **Appended**: To JSON log file (`logs/ci-YYYYMMDD_HHMMSS.log`)
3. **Persisted**: Until log cleanup (per Feature 001 retention policy)

**Storage**: JSON Lines format (one JSON object per line) in `logs/ci-YYYYMMDD_HHMMSS.log`

**Relationships**:
- **Belongs to**: Pipeline Run (via `run_id`)
- **References**: Source code file and function (via `source_file`, `line_number`, `function_name`)

**JSON Schema**: See `contracts/log-schema.json`

---

### 4. Test Execution

**Purpose**: Track individual test suite execution with retry and parallelization metadata.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `test_type` | string | ✅ | Test suite type: `unit`, `integration`, or `e2e` |
| `attempt_number` | integer | ✅ | Retry attempt (1=first attempt, 2=retry after failure) |
| `status` | string | ✅ | Test outcome: `passed`, `failed`, or `skipped` |
| `duration` | integer | ✅ | Test execution time in seconds |
| `failure_count` | integer | ✅ | Number of failed tests (0 if `status=passed`) |
| `started_at` | integer | ✅ | Test start time (Unix epoch seconds) |
| `completed_at` | integer | ✅ | Test completion time (Unix epoch seconds) |
| `run_in_parallel` | boolean | ✅ | Whether test ran concurrently with other test suites |
| `fallback_to_serial` | boolean | ✅ | Whether test fell back to serial execution due to resource contention |

**Example (Parallel Success)**:
```json
{
  "test_type": "unit",
  "attempt_number": 1,
  "status": "passed",
  "duration": 45,
  "failure_count": 0,
  "started_at": 1729433445,
  "completed_at": 1729433490,
  "run_in_parallel": true,
  "fallback_to_serial": false
}
```

**Example (E2E Retry Success)**:
```json
{
  "test_type": "e2e",
  "attempt_number": 2,
  "status": "passed",
  "duration": 60,
  "failure_count": 0,
  "started_at": 1729433550,
  "completed_at": 1729433610,
  "run_in_parallel": true,
  "fallback_to_serial": false
}
```

**Example (Serial Fallback)**:
```json
{
  "test_type": "integration",
  "attempt_number": 2,
  "status": "passed",
  "duration": 55,
  "failure_count": 0,
  "started_at": 1729433500,
  "completed_at": 1729433555,
  "run_in_parallel": false,
  "fallback_to_serial": true
}
```

**Lifecycle**:
1. **Created**: On test step start, set `test_type`, `started_at`, `run_in_parallel`
2. **Updated**: On retry, increment `attempt_number`, update timestamps
3. **Finalized**: On completion, set `status`, `duration`, `failure_count`, `completed_at`, `fallback_to_serial`
4. **Logged**: As JSON log entry with `step_name=test-{type}`

**Storage**: Embedded in Log Entries (logged at test completion)

**Relationships**:
- **Belongs to**: Pipeline Run (via shared `run_id` in log entries)
- **Groups**: Multiple Test Executions per Pipeline Run (3 test types × up to 2 attempts)

---

## Entity Relationships

```
Pipeline Run (1)
    ├─── has many ───> Log Entry (N)
    │                      └─ references: source_file, line_number, function_name
    │
    └─── has many ───> Test Execution (3-6)
                           └─ embedded in Log Entries

Deployment State Record (standalone)
    ├─── currentDeployment
    ├─── lastKnownGood
    └─── history (array)

Git Commit (external)
    └─── referenced by ───> Deployment State Record (commit_sha)
```

---

## Storage Summary

| Entity | Storage Location | Format | Lifecycle |
|--------|------------------|--------|-----------|
| Pipeline Run | Embedded in Log Entries | JSON (via `run_id`) | Per pipeline execution |
| Deployment State Record | `.github/deployment-state.json` | JSON object | Persistent (updated per deployment) |
| Log Entry | `logs/ci-YYYYMMDD_HHMMSS.log` | JSON Lines (NDJSON) | Per pipeline execution, cleaned up by retention policy |
| Test Execution | Embedded in Log Entries | JSON (at test step completion) | Per test suite execution |

---

## Data Flow

### Pipeline Execution Flow

1. **Pipeline Start**:
   - Generate `run_id` (correlation ID)
   - Create initial Log Entry (level=info, step_name=init)
   - Set `start_time`

2. **Each Pipeline Step**:
   - Log step start (with `run_id`, `source_file`, `line_number`, `function_name`)
   - Execute step logic
   - Log step completion (with `duration_ms`)
   - Update `steps_completed` array

3. **Test Execution**:
   - Create Test Execution entry (set `test_type`, `started_at`, `run_in_parallel`)
   - Run tests (parallel or serial)
   - On completion: Log Test Execution with final status
   - On failure: Optionally retry (increment `attempt_number`)

4. **Pipeline Completion**:
   - Set `end_time`
   - Calculate `duration`
   - Set `exit_code`
   - Log final entry (step_name=complete)

### Deployment Flow

1. **Deployment Start** (GitHub Actions):
   - Create new `currentDeployment` entry
   - Set `deployment_id`, `timestamp`, `commit_sha`
   - Set `git_operations_attempts=1`

2. **Deployment Retry**:
   - Increment `git_operations_attempts`
   - Exponential backoff (2^attempt seconds)

3. **Deployment Success**:
   - Set `status=success`
   - Update `lastKnownGood` with current deployment
   - Append to `history` array (keep last 10)

4. **Deployment Failure**:
   - Set `status=failure`
   - Set `error_message` with failure reason
   - Preserve previous `lastKnownGood` for rollback reference

---

## JSON Schema References

All entities have corresponding JSON schemas for validation:

- **Log Entry**: `specs/002-cicd-pipeline-enhancements/contracts/log-schema.json`
- **Deployment State Record**: `specs/002-cicd-pipeline-enhancements/contracts/deployment-state-schema.json`
- **Exit Codes**: `specs/002-cicd-pipeline-enhancements/contracts/exit-codes.md`

---

**Data Model Status**: ✅ COMPLETE
**Entities Defined**: 4 (Pipeline Run, Deployment State Record, Log Entry, Test Execution)
**Ready for Implementation**: ✅ YES
