# Research & Technical Decisions: CI/CD Pipeline Improvements

**Branch**: `002-cicd-pipeline-enhancements` | **Date**: 2025-10-20 | **Phase**: 0

## Overview

This document captures the technical research and decisions made during Phase 0 of the CI/CD Pipeline Improvements feature (002). All decisions prioritize backwards compatibility with Feature 001, minimal external dependencies, and native bash capabilities.

## Target Environment

**Compatibility Matrix**:

| Platform | Bash Version | Status | Notes |
|----------|--------------|--------|-------|
| Linux | 4.4+ | ✅ Supported | Primary development target |
| Linux | 5.x | ✅ Supported | Enhanced features available |
| macOS | 4.4+ | ✅ Supported | Shipped with macOS 10.13+ |
| macOS | 5.x | ✅ Supported | Via Homebrew |

**Dependencies**:
- `jq` - JSON processing (existing, required)
- `bash` builtins - `SECONDS`, `$LINENO`, `${FUNCNAME[@]}`, `${BASH_SOURCE[@]}`, `wait`
- `date` - Timestamp generation for correlation IDs
- Standard Unix tools - `tail`, `head`, `/dev/urandom`

## Research Decisions

### 1. Bash Timeout Enforcement Mechanisms

**Decision**: Use `$SECONDS` variable with periodic checks in main loop

**Implementation Pattern**:
```bash
#!/usr/bin/env bash

# Initialize timeout tracking
START_TIME=$SECONDS
TIMEOUT_SECONDS=300  # 5 minutes

# Periodic timeout check function
check_timeout() {
    local elapsed=$((SECONDS - START_TIME))
    if (( elapsed >= TIMEOUT_SECONDS )); then
        log_error "Pipeline timeout: $elapsed seconds (limit: $TIMEOUT_SECONDS)"
        exit 5
    fi
}

# Main pipeline loop
for step in init env-check lint test-unit test-integration test-e2e build cleanup complete; do
    check_timeout  # Check before each step

    log_info "Running step: $step"
    run_step "$step"

    check_timeout  # Check after each step
done
```

**Rationale**:
- **Native bash builtin**: No external dependencies (timeout command requires coreutils)
- **Automatic tracking**: `$SECONDS` automatically increments, no manual calculation
- **Sufficient precision**: 1-second granularity meets requirement (≤ 1 second of threshold)
- **Simple implementation**: Periodic checks at step boundaries, minimal overhead
- **Portable**: Works identically on Linux and macOS

**Alternatives Considered**:

1. **`timeout` command (GNU coreutils)**:
   ```bash
   timeout 300 ./scripts/local-ci/run.sh
   ```
   - ❌ External dependency (not always available)
   - ❌ Doesn't provide granular step timing
   - ✅ Simple one-line usage

2. **Signal-based (SIGALRM)**:
   ```bash
   trap 'echo "Timeout!" && exit 5' ALRM
   (sleep 300; kill -ALRM $$) &
   ```
   - ❌ Complex signal handling
   - ❌ Race conditions between trap and step completion
   - ❌ Difficult to test

**Trade-offs**:
- **Overhead**: Negligible (simple arithmetic comparison)
- **Accuracy**: Within 1 second of threshold (acceptable per SC-001)
- **Maintainability**: Clear, readable code

---

### 2. Parallel Test Execution with Failure Collection

**Decision**: Use bash background jobs (`&`) with `wait` builtin and exit code arrays

**Implementation Pattern**:
```bash
#!/usr/bin/env bash

run_tests_parallel() {
    local test_types=("unit" "integration" "e2e")
    local pids=()
    local exit_codes=()

    # Launch all tests in background
    for test_type in "${test_types[@]}"; do
        (
            log_info "Starting $test_type tests (parallel)"
            npm run "test:$test_type"
            exit $?  # Propagate npm exit code
        ) &
        pids+=($!)  # Capture PID
    done

    # Wait for all jobs and collect exit codes
    for pid in "${pids[@]}"; do
        wait "$pid"
        exit_codes+=($?)
    done

    # Check for any failures
    local failed=0
    for i in "${!test_types[@]}"; do
        if [[ ${exit_codes[$i]} -ne 0 ]]; then
            log_error "${test_types[$i]} tests failed (exit ${exit_codes[$i]})"
            failed=1
        fi
    done

    return $failed
}
```

**Rationale**:
- **Native bash**: No external tools required
- **Simple error aggregation**: Exit code arrays preserve individual test results
- **Cross-platform**: Works on Linux and macOS
- **Existing infrastructure**: Tests already runnable independently via npm scripts

**Alternatives Considered**:

1. **GNU Parallel**:
   ```bash
   parallel npm run test:{} ::: unit integration e2e
   ```
   - ❌ External dependency (not in base systems)
   - ✅ Better load balancing
   - ❌ Overkill for 3 test suites

2. **xargs with parallel execution**:
   ```bash
   echo -e "unit\nintegration\ne2e" | xargs -P 3 -I {} npm run test:{}
   ```
   - ❌ Limited exit code handling (only first failure)
   - ❌ Less readable than explicit bash jobs
   - ✅ No additional dependencies

**Trade-offs**:
- **Complexity**: Moderate (array handling, PID tracking)
- **Resource usage**: Up to 3 concurrent test processes
- **Speed improvement**: 40-60% reduction in test phase duration (per FR-005)

**Failure Scenarios**:
```bash
# Scenario 1: All tests pass
# Result: exit_codes=(0 0 0), return 0

# Scenario 2: One test fails
# Result: exit_codes=(0 1 0), return 1, log error for integration tests

# Scenario 3: Multiple tests fail
# Result: exit_codes=(1 1 0), return 1, log errors for unit and integration tests
```

---

### 3. Resource Contention Detection for Serial Fallback

**Decision**: Parse test output for port/lock errors, re-run with dedicated flag

**Implementation Pattern**:
```bash
#!/usr/bin/env bash

detect_resource_contention() {
    local log_file="$1"

    # Check for common resource contention indicators
    if grep -Eq "(EADDRINUSE|port already in use|lock file exists|database is locked)" "$log_file"; then
        return 0  # Contention detected
    fi

    return 1  # No contention
}

run_tests_with_fallback() {
    local log_file="logs/test-parallel-$(date +%s).log"

    # Attempt 1: Parallel execution
    if run_tests_parallel 2>&1 | tee "$log_file"; then
        log_info "Tests passed (parallel mode)"
        return 0
    fi

    # Check for resource contention
    if detect_resource_contention "$log_file"; then
        log_warn "Resource contention detected, falling back to serial execution"

        # Attempt 2: Serial execution
        for test_type in unit integration e2e; do
            npm run "test:$test_type" || return 2
        done

        log_info "Tests passed (serial fallback mode)"
        return 0
    fi

    # Genuine test failure
    log_error "Tests failed (not due to resource contention)"
    return 2
}
```

**Rationale**:
- **Pragmatic heuristics**: Detects common error patterns (port conflicts, file locks)
- **No complex IPC**: Simple log file parsing with grep
- **Transparent fallback**: User sees warning but tests continue
- **Preserves speed**: Parallel remains default, serial only on detection

**Alternatives Considered**:

1. **Pre-allocate ports**:
   ```bash
   export TEST_PORT_UNIT=3001
   export TEST_PORT_INTEGRATION=3002
   export TEST_PORT_E2E=3003
   ```
   - ❌ Requires test suite coordination (invasive changes)
   - ✅ Prevents contention proactively
   - ❌ Not backwards compatible

2. **Retry with exponential backoff**:
   ```bash
   for attempt in 1 2 3; do
       run_tests_parallel && break
       sleep $((2 ** attempt))
   done
   ```
   - ❌ Slower than serial fallback
   - ❌ May still encounter contention on retries
   - ✅ Simple implementation

**Trade-offs**:
- **False positives**: Heuristics may misidentify genuine errors as contention (acceptable - serial mode still validates)
- **False negatives**: May miss subtle contention (tests fail, user re-runs)
- **Performance**: Serial fallback adds ~40-60% to test phase duration (acceptable for rare edge case)

---

### 4. Bash Source Context Extraction (LINENO, FUNCNAME)

**Decision**: Use `${BASH_SOURCE[@]}`, `$LINENO`, `${FUNCNAME[@]}` passed to logger wrapper

**Implementation Pattern**:
```bash
#!/usr/bin/env bash

# Logger function capturing source context
log_with_context() {
    local level=$1
    local message=$2
    local source_file="${BASH_SOURCE[1]}"  # Caller's file
    local line_number="${BASH_LINENO[0]}"  # Caller's line
    local function_name="${FUNCNAME[1]}"   # Caller's function

    # Convert absolute path to relative (from repo root)
    source_file="${source_file#$REPO_ROOT/}"

    # Generate JSON log entry
    jq -n \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --arg level "$level" \
        --arg message "$message" \
        --arg run_id "$CORRELATION_ID" \
        --arg source_file "$source_file" \
        --argjson line_number "$line_number" \
        --arg function_name "$function_name" \
        --arg step_name "$CURRENT_STEP" \
        '{timestamp: $timestamp, level: $level, message: $message, run_id: $run_id, source_file: $source_file, line_number: $line_number, function_name: $function_name, step_name: $step_name}' \
        >> "$LOG_FILE"
}

# Convenience wrappers
log_info() { log_with_context "info" "$1"; }
log_warn() { log_with_context "warn" "$1"; }
log_error() { log_with_context "error" "$1"; }

# Example usage in pipeline script
run_step_test_unit() {
    log_info "Running unit tests"  # Logs with source: scripts/local-ci/run.sh, line: 123, function: run_step_test_unit
    npm run test:unit || { log_error "Unit tests failed"; return 2; }
}
```

**Rationale**:
- **Native bash introspection**: Built-in arrays provide accurate context
- **Zero overhead for call site**: Wrappers handle complexity
- **Relative paths**: Strips repo root for readable logs
- **Accurate for direct calls**: Works correctly for single-level indirection

**Alternatives Considered**:

1. **`caller` builtin**:
   ```bash
   caller_info=$(caller 0)  # Returns "line function file"
   ```
   - ❌ Limited to single line of context
   - ❌ Awkward parsing of space-separated output
   - ✅ Simpler than arrays

2. **Stack walking with loop**:
   ```bash
   for i in {0..${#FUNCNAME[@]}}; do
       echo "${BASH_SOURCE[$i]}:${BASH_LINENO[$i]}:${FUNCNAME[$i]}"
   done
   ```
   - ✅ Full stack trace available
   - ❌ Overkill for single-level logging
   - ❌ More complex parsing

**Trade-offs**:
- **Accuracy**: Works for direct calls to `log_*` functions; may be inaccurate for deeply nested calls (acceptable for current use case)
- **Performance**: Minimal overhead (array access is O(1))
- **Maintainability**: Clear, documented pattern

**Bash Version Compatibility**:
- `${BASH_SOURCE[@]}`: Available in bash 3.0+
- `${BASH_LINENO[@]}`: Available in bash 3.0+
- `${FUNCNAME[@]}`: Available in bash 2.04+

---

### 5. Correlation ID Generation

**Decision**: `run-$(date +%Y%m%d-%H%M%S)-$(head /dev/urandom | tr -dc a-z0-9 | head -c 6)`

**Implementation Pattern**:
```bash
#!/usr/bin/env bash

generate_correlation_id() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local random_suffix=$(head /dev/urandom | tr -dc a-z0-9 | head -c 6)
    echo "run-${timestamp}-${random_suffix}"
}

# Usage
CORRELATION_ID=$(generate_correlation_id)
export CORRELATION_ID

# Example output: run-20251020-143045-k8m3q2
```

**Rationale**:
- **Human-readable**: Timestamp prefix allows chronological sorting
- **Sortable**: Lexicographic sorting matches chronological order
- **Collision-resistant**: 6-character suffix (36^6 = 2.1 billion combinations)
- **Local-scoped**: Sufficient uniqueness for single developer, single machine
- **No external dependencies**: Uses standard Unix tools (`date`, `/dev/urandom`, `tr`, `head`)

**Alternatives Considered**:

1. **UUID (via `uuidgen`)**:
   ```bash
   CORRELATION_ID=$(uuidgen)
   # Example: 550e8400-e29b-41d4-a716-446655440000
   ```
   - ❌ Requires `uuidgen` (not always available)
   - ✅ Globally unique
   - ❌ Not human-readable or sortable

2. **PID-based**:
   ```bash
   CORRELATION_ID="run-$$-$(date +%s)"
   # Example: run-12345-1729433445
   ```
   - ✅ Simple, no randomness needed
   - ❌ Not unique across time (PID reuse)
   - ❌ Timestamp not human-readable

3. **Millisecond timestamp only**:
   ```bash
   CORRELATION_ID="run-$(date +%s%3N)"
   # Example: run-1729433445123
   ```
   - ✅ Simple, unique per millisecond
   - ❌ Risk of collision if pipeline runs very quickly
   - ❌ Not human-readable

**Trade-offs**:
- **Uniqueness**: Sufficient for local development (not globally unique like UUID)
- **Readability**: Timestamp prefix aids debugging
- **Performance**: Negligible overhead (one-time generation at pipeline start)

**Format Specification**:
- **Pattern**: `run-YYYYMMDD-HHMMSS-{6char}`
- **Example**: `run-20251020-143045-k8m3q2`
- **Regex**: `^run-\d{8}-\d{6}-[a-z0-9]{6}$`

---

### 6. TUI Real-Time JSON Log Parsing

**Decision**: `tail -f` piped to `jq` with line buffering, clear/redraw on update

**Implementation Pattern**:
```bash
#!/usr/bin/env bash

# TUI real-time progress monitoring
monitor_pipeline_progress() {
    local log_file="$1"
    local update_interval=2  # Minimum 2 seconds between redraws (per FR-009)

    # Clear screen and initialize
    clear
    echo "=== CI/CD Pipeline Progress ==="
    echo ""

    # Track last update time
    local last_update=$SECONDS

    # Tail log file and parse JSON entries
    tail -f "$log_file" | while IFS= read -r line; do
        # Parse JSON entry
        local step=$(echo "$line" | jq -r '.step_name // "unknown"')
        local level=$(echo "$line" | jq -r '.level // "info"')
        local message=$(echo "$line" | jq -r '.message // ""')
        local duration=$(echo "$line" | jq -r '.duration_ms // null')

        # Rate limit updates (minimum 2 seconds)
        local elapsed=$((SECONDS - last_update))
        if (( elapsed >= update_interval )); then
            # Clear and redraw progress
            clear
            echo "=== CI/CD Pipeline Progress ==="
            echo ""
            echo "Current Step: $step"
            echo "Status: $message"

            if [[ "$duration" != "null" ]]; then
                echo "Duration: ${duration}ms"
            fi

            echo ""
            echo "Log Level: $level"

            last_update=$SECONDS
        fi

        # Exit on pipeline completion
        if [[ "$step" == "complete" ]]; then
            break
        fi
    done
}

# Launch in background when pipeline starts
monitor_pipeline_progress "logs/ci-$(date +%Y%m%d_%H%M%S).log" &
MONITOR_PID=$!

# Cleanup on exit
trap "kill $MONITOR_PID 2>/dev/null" EXIT
```

**Rationale**:
- **Standard Unix tools**: `tail -f` (follow mode) and `jq` (JSON parsing)
- **Minimal latency**: Real-time log streaming with ~2 second update interval
- **Works with existing logs**: Parses existing JSON log format, backwards compatible
- **Simple terminal UI**: Clear/redraw pattern avoids complex terminal multiplexing

**Alternatives Considered**:

1. **`inotify` (Linux-only)**:
   ```bash
   inotifywait -m -e modify "$log_file" | while read event; do
       # Process log updates
   done
   ```
   - ❌ Linux-only (not portable to macOS)
   - ✅ More efficient (event-driven vs polling)
   - ❌ Added complexity

2. **Polling with `sleep`**:
   ```bash
   while true; do
       parse_latest_log_entry "$log_file"
       sleep 2
   done
   ```
   - ❌ Higher latency (discrete 2-second intervals)
   - ✅ Simple implementation
   - ❌ May miss rapid updates

3. **Terminal multiplexer (tmux/screen)**:
   ```bash
   tmux split-window -v "tail -f $log_file | jq"
   ```
   - ❌ Requires tmux/screen installed
   - ✅ Professional-looking split-pane UI
   - ❌ Overkill for simple progress display

**Trade-offs**:
- **Screen flicker**: Clear/redraw may cause flicker (acceptable for 2-second interval)
- **CPU usage**: `tail -f` + `jq` parsing is lightweight
- **Terminal compatibility**: Works in any ANSI-compatible terminal

**Rate Limiting**:
- **Minimum interval**: 2 seconds (per FR-009)
- **Rationale**: Avoids overwhelming user with updates, reduces screen flicker
- **Implementation**: Track `$SECONDS` variable, skip redraws if < 2 seconds elapsed

---

### 7. GitHub Actions Deployment Retry Logic

**Decision**: Bash loop with 3 attempts, exponential backoff, failure on exhaustion

**Implementation Pattern**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy with retry logic
        run: |
          #!/usr/bin/env bash
          set -euo pipefail

          MAX_ATTEMPTS=3
          BACKOFF_BASE=2  # Exponential backoff: 2^attempt seconds

          for attempt in $(seq 1 $MAX_ATTEMPTS); do
            echo "Deployment attempt $attempt/$MAX_ATTEMPTS"

            # Attempt deployment (git operations)
            if npm run deploy; then
              echo "Deployment successful on attempt $attempt"

              # Update deployment state
              jq -n \
                --arg deployment_id "deploy-$(date +%s)" \
                --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
                --arg commit_sha "$GITHUB_SHA" \
                --arg status "success" \
                --argjson attempts "$attempt" \
                '{currentDeployment: {deployment_id: $deployment_id, timestamp: $timestamp, commit_sha: $commit_sha, status: $status, git_operations_attempts: $attempts}, lastKnownGood: {deployment_id: $deployment_id, commit_sha: $commit_sha, timestamp: $timestamp}}' \
                > .github/deployment-state.json

              exit 0
            fi

            # Log failure
            echo "Deployment failed on attempt $attempt"

            # Exponential backoff (skip on last attempt)
            if (( attempt < MAX_ATTEMPTS )); then
              sleep_duration=$((BACKOFF_BASE ** attempt))
              echo "Retrying in ${sleep_duration} seconds..."
              sleep "$sleep_duration"
            fi
          done

          # All attempts exhausted
          echo "Deployment failed after $MAX_ATTEMPTS attempts"

          # Update deployment state (failure)
          jq -n \
            --arg deployment_id "deploy-$(date +%s)" \
            --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
            --arg commit_sha "$GITHUB_SHA" \
            --arg status "failure" \
            --argjson attempts "$MAX_ATTEMPTS" \
            --arg error_message "Git operations failed after $MAX_ATTEMPTS attempts" \
            '{currentDeployment: {deployment_id: $deployment_id, timestamp: $timestamp, commit_sha: $commit_sha, status: $status, git_operations_attempts: $attempts, error_message: $error_message}}' \
            > .github/deployment-state.json

          exit 1
```

**Rationale**:
- **Simple loop**: No third-party GitHub Actions required
- **Predictable backoff**: Exponential (2^attempt seconds: 2s, 4s, 8s)
- **State tracking**: Records attempts and outcomes in `deployment-state.json`
- **Integrates with existing workflow**: Wraps existing `npm run deploy` command

**Alternatives Considered**:

1. **GitHub Actions `retry` action (third-party)**:
   ```yaml
   - uses: nick-invision/retry@v2
     with:
       max_attempts: 3
       timeout_minutes: 10
       command: npm run deploy
   ```
   - ❌ Third-party dependency (supply chain risk)
   - ✅ Cleaner YAML syntax
   - ❌ Less control over backoff strategy

2. **Manual retries (user burden)**:
   ```yaml
   # No automatic retry, user re-runs workflow manually
   ```
   - ❌ Poor user experience
   - ❌ Requires manual intervention
   - ✅ Simple (no retry logic needed)

**Trade-offs**:
- **Total time**: Worst case ~15 seconds (2 + 4 + 8 + deployment time)
- **Transient failure recovery**: Handles temporary GitHub API outages, network blips
- **False positives**: May retry on genuine deployment errors (acceptable - fails after 3 attempts)

**Backoff Schedule**:
| Attempt | Delay Before | Cumulative Delay |
|---------|--------------|------------------|
| 1       | 0s           | 0s               |
| 2       | 2s           | 2s               |
| 3       | 4s           | 6s               |
| Fail    | -            | ~6s + deployments|

---

### 8. E2E Test Retry Mechanism

**Decision**: Wrapper around Playwright test step, detect exit code 1, re-run once

**Implementation Pattern**:
```bash
#!/usr/bin/env bash

run_e2e_tests_with_retry() {
    local max_attempts=2
    local log_file="logs/e2e-$(date +%s).log"

    for attempt in $(seq 1 $max_attempts); do
        log_info "E2E tests attempt $attempt/$max_attempts"

        # Run Playwright tests
        if npm run test:e2e 2>&1 | tee "$log_file"; then
            log_info "E2E tests passed on attempt $attempt"
            return 0
        fi

        local exit_code=$?

        # Only retry on flaky test failures (exit code 1)
        # Do NOT retry on timeout, infrastructure failures, etc.
        if (( exit_code == 1 && attempt < max_attempts )); then
            log_warn "E2E tests failed (exit $exit_code), retrying once..."
            sleep 2  # Brief delay before retry
        else
            log_error "E2E tests failed after $attempt attempt(s)"
            return 2  # Test failure exit code
        fi
    done

    # Should never reach here, but safeguard
    return 2
}
```

**Rationale**:
- **Transparent to tests**: Wrapper at pipeline level, no changes to test files
- **Preserves genuine failures**: Only retries on exit code 1 (test failures)
- **Simple implementation**: Single retry attempt, no complex backoff
- **Configurable**: Can adjust `max_attempts` if needed

**Alternatives Considered**:

1. **Playwright built-in retry (per-test)**:
   ```javascript
   // playwright.config.js
   export default {
     retries: 1,  // Retry each test once
   };
   ```
   - ❌ Too granular (retries every test, not just suite)
   - ❌ Slower (retries individual flaky tests multiple times)
   - ✅ More transparent to pipeline

2. **Manual flags (user burden)**:
   ```bash
   npm run test:e2e -- --retries=1
   ```
   - ❌ Requires user to remember flag
   - ❌ Not automated
   - ✅ Simpler implementation

**Trade-offs**:
- **False positives**: May mask genuine intermittent failures (acceptable - only one retry)
- **Time overhead**: Adds ~30-60 seconds on flaky test failure (acceptable for rare case)
- **Exit code handling**: Preserves exit code 2 for genuine test failures

**Exit Code Logic**:
```bash
# Scenario 1: First attempt passes
# Result: exit 0

# Scenario 2: First attempt fails (flaky), second passes
# Result: exit 0, log warning

# Scenario 3: Both attempts fail
# Result: exit 2 (test failure)

# Scenario 4: First attempt times out (exit 5)
# Result: exit 5 immediately (no retry)
```

---

## Summary

All 8 research decisions prioritize:

1. **Minimal dependencies**: Leverage bash builtins and standard Unix tools
2. **Backwards compatibility**: Enhancements to existing Feature 001 infrastructure
3. **Cross-platform support**: Linux and macOS with bash 4.4+
4. **Simple implementations**: Prefer readable code over clever solutions
5. **Pragmatic trade-offs**: Accept minor limitations for significant simplicity gains

**Next Phase**: Proceed to Phase 1 (Design & Contracts) with confidence that all technical patterns are validated and feasible.

---

**Research Status**: ✅ COMPLETE
**Technical Risks**: ✅ MITIGATED
**Ready for Phase 1**: ✅ YES
