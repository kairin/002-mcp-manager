# Local CI/CD Pipeline

This script runs the local CI/CD pipeline with enhanced reliability, performance, and debugging features.

## Usage

To run the local CI/CD script, run the following command from the root of the project:
```bash
./scripts/local-ci/run.sh
```

## Features (Feature 002 Enhancements)

### Timeout Enforcement
- **Hard 300-second (5-minute) timeout** enforcement per NFR-003
- Pipeline exits with **exit code 5** if execution exceeds the timeout
- Prevents runaway pipelines and ensures predictable execution times

### Parallel Test Execution
- **40-60% faster test phase** through concurrent execution
- Unit, integration, and E2E tests run in parallel
- Automatic **serial fallback** on resource contention (port conflicts, file locks)
- Intelligent failure aggregation across parallel tests

### Enhanced Logging with Source Context
- All JSON log entries include **source_file, line_number, function_name**
- Accurate source context from bash call stack for debugging
- Makes troubleshooting pipeline issues significantly faster

### Pipeline Run Correlation IDs
- Unique **run_id** generated for every pipeline execution
- Format: `run-YYYYMMDD-HHMMSS-{6char}`
- Auto-injected into all log entries for cross-run tracing
- Enables easy filtering and correlation across multiple pipeline runs

### E2E Test Retry for Stability
- Automatic retry on first E2E test failure (max 2 attempts)
- Smart retry: only retries test failures (exit code 1), not timeouts
- 2-second delay between retry attempts
- Reduces false failures from timing issues and flaky tests

### Constitution File Validation
- Non-blocking check for `.specify/memory/constitution.md`
- Helpful warnings for SpecKit users with creation hints
- Pipeline continues regardless of file presence

### Deployment State Tracking (GitHub Actions)
- 3-attempt retry with exponential backoff for deployment state persistence
- Hard failure on retry exhaustion (never fails silently)
- Reliable state tracking in `.github/deployment-state.json`

## Exit Codes

- **0**: Success - all checks passed
- **1**: Lint failure
- **2**: Test failure
- **3**: Build failure
- **4**: Environment validation failure
- **5**: Timeout - pipeline exceeded 300 seconds (Feature 002)

## Performance

- **Test Phase**: ~60 seconds with parallel execution (down from ~150s serial)
- **Full Pipeline**: Typically completes in 2-4 minutes
- **Timeout Limit**: Hard 300-second maximum enforced

## Structured Logging

All logs are written in JSON format to `logs/ci-*.log` with:
- `timestamp`: ISO 8601 timestamp
- `level`: info | success | warn | error
- `step_name`: Current pipeline step
- `message`: Human-readable message
- `run_id`: Unique correlation ID for this pipeline run
- `source_file`: Source file that generated the log
- `line_number`: Line number in source file
- `function_name`: Function that generated the log
- `duration_ms`: Step duration in milliseconds (for success logs)
- `exit_code`: Process exit code (for error logs)

## Configuration

No configuration required - all enhancements work out of the box.

## Documentation

- **Specification**: `specs/002-cicd-pipeline-enhancements/spec.md`
- **Implementation Status**: `specs/002-cicd-pipeline-enhancements/IMPLEMENTATION_STATUS.md`
- **Contracts**: `specs/002-cicd-pipeline-enhancements/contracts/`
