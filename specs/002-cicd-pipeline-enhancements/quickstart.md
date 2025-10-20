# Quickstart Guide: CI/CD Pipeline Improvements

**Branch**: `002-cicd-pipeline-enhancements` | **Date**: 2025-10-20 | **Phase**: 1

## Overview

This quickstart guide helps you verify the CI/CD Pipeline Improvements feature (002) is working correctly after implementation. Follow these steps to test all new features.

## Prerequisites

Before testing the enhancements, verify your environment meets these requirements:

### 1. Check Bash Version

```bash
# Verify bash 4.4 or higher
bash --version

# Expected output (version ≥ 4.4):
# GNU bash, version 4.4.20(1)-release (x86_64-pc-linux-gnu)
# or
# GNU bash, version 5.1.16(1)-release (x86_64-pc-linux-gnu)
```

**If version < 4.4**: Upgrade bash (required for `$SECONDS` variable and array features)

### 2. Verify Dependencies

```bash
# Check jq is installed
which jq && jq --version

# Expected output:
# /usr/bin/jq
# jq-1.6

# Check node and npm
node --version  # Should be ≥ 18.0.0
npm --version   # Should be ≥ 9.0.0

# Check git
git --version   # Should be ≥ 2.0.0
```

**If jq is missing**: Install via package manager
- Ubuntu/Debian: `sudo apt install jq`
- macOS: `brew install jq`

### 3. Verify Feature 001 Complete

```bash
# Check existing CI/CD script exists
test -x ./scripts/local-ci/run.sh && echo "✓ CI/CD script found"

# Check TUI exists
test -x ./scripts/tui/run.sh && echo "✓ TUI script found"

# Check logger library exists
test -f ./scripts/local-ci/lib/logger.sh && echo "✓ Logger library found"
```

**If any check fails**: Complete Feature 001 (Local CI/CD pipeline) first

---

## Quick Test: New Features

### Test 1: Timeout Enforcement (FR-001, FR-002)

**Purpose**: Verify pipeline enforces 5-minute timeout and exits with code 5

**Steps**:

1. **Add artificial delay to trigger timeout**:
   ```bash
   # Edit scripts/local-ci/run.sh temporarily
   # Add this line before test-unit step:
   sleep 301  # Force timeout (301 seconds > 300 second limit)
   ```

2. **Run pipeline**:
   ```bash
   ./scripts/local-ci/run.sh
   ```

3. **Expected behavior**:
   - Pipeline runs for ~301 seconds
   - Timeout error logged: "Pipeline timeout: 301 seconds (limit: 300)"
   - Exit code: 5

4. **Verify exit code**:
   ```bash
   echo $?  # Should print: 5
   ```

5. **Check log file**:
   ```bash
   # Find latest log
   ls -lt logs/ci-*.log | head -1

   # Verify timeout error logged
   jq 'select(.level=="error" and .message | contains("timeout"))' logs/ci-*.log
   ```

6. **Cleanup**: Remove `sleep 301` line

**Expected Output**:
```json
{
  "timestamp": "2025-10-20T14:35:01Z",
  "level": "error",
  "message": "Pipeline timeout: 301 seconds (limit: 300)",
  "run_id": "run-20251020-143045-k8m3q2",
  "source_file": "scripts/local-ci/run.sh",
  "line_number": 85,
  "function_name": "check_timeout",
  "step_name": "test-unit"
}
```

---

### Test 2: Parallel Test Execution (FR-005, FR-006)

**Purpose**: Verify tests run in parallel and complete faster

**Steps**:

1. **Run pipeline with timing**:
   ```bash
   time ./scripts/local-ci/run.sh
   ```

2. **Expected behavior**:
   - Unit, integration, and E2E tests run simultaneously
   - Test phase duration reduced by 40-60% vs serial
   - All test results collected correctly

3. **Verify parallel execution in logs**:
   ```bash
   # Check for overlapping test start times
   jq 'select(.step_name | startswith("test-"))' logs/ci-*.log | jq -s 'sort_by(.timestamp)'
   ```

4. **Expected log pattern** (note overlapping timestamps):
   ```json
   [
     {"timestamp": "2025-10-20T14:30:00Z", "step_name": "test-unit", "message": "Starting unit tests (parallel)"},
     {"timestamp": "2025-10-20T14:30:01Z", "step_name": "test-integration", "message": "Starting integration tests (parallel)"},
     {"timestamp": "2025-10-20T14:30:02Z", "step_name": "test-e2e", "message": "Starting E2E tests (parallel)"}
   ]
   ```

**Baseline Comparison** (Feature 001 serial vs Feature 002 parallel):
- Serial: ~150 seconds (unit: 45s + integration: 55s + e2e: 50s)
- Parallel: ~60 seconds (max of 3 concurrent tests)
- Improvement: 60% faster

---

### Test 3: TUI Real-Time Progress (FR-008, FR-009)

**Purpose**: Verify TUI displays real-time pipeline progress

**Steps**:

1. **Launch TUI**:
   ```bash
   ./scripts/tui/run.sh
   ```

2. **Select a profile** (e.g., "dev")

3. **Expected behavior**:
   - TUI displays current step name
   - Progress updates every ~2 seconds
   - Step durations shown on completion
   - No "frozen screen" (continuous updates)

4. **Manual observation checklist**:
   - [ ] Current step name displayed
   - [ ] Log level shown (info/warn/error)
   - [ ] Duration shown for completed steps
   - [ ] Updates occur smoothly (no flicker)

**Expected TUI Display**:
```
=== CI/CD Pipeline Progress ===

Current Step: test-unit
Status: Running unit tests
Duration: 45000ms

Log Level: info
```

---

### Test 4: Structured Error Context (FR-007)

**Purpose**: Verify log entries include source file, line number, and function name

**Steps**:

1. **Run pipeline normally**:
   ```bash
   ./scripts/local-ci/run.sh
   ```

2. **Inspect log entries**:
   ```bash
   # Check for source context fields
   jq 'select(.source_file and .line_number and .function_name)' logs/ci-*.log | head -5
   ```

3. **Expected log entry structure**:
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

4. **Verify all required fields present**:
   ```bash
   # Count entries missing source context (should be 0)
   jq 'select(.source_file == null or .line_number == null or .function_name == null)' logs/ci-*.log | wc -l
   ```

---

### Test 5: Correlation IDs (FR-010, FR-011)

**Purpose**: Verify each pipeline run has unique correlation ID

**Steps**:

1. **Run pipeline twice**:
   ```bash
   ./scripts/local-ci/run.sh  # Run 1
   ./scripts/local-ci/run.sh  # Run 2
   ```

2. **Extract correlation IDs**:
   ```bash
   # Find latest 2 log files
   ls -lt logs/ci-*.log | head -2

   # Extract run_id from each log
   jq -r '.run_id' logs/ci-20251020_143045.log | head -1
   jq -r '.run_id' logs/ci-20251020_143500.log | head -1
   ```

3. **Expected output** (unique IDs):
   ```
   run-20251020-143045-k8m3q2
   run-20251020-143500-a7b9c1
   ```

4. **Verify format**:
   ```bash
   # Check ID matches pattern: run-YYYYMMDD-HHMMSS-{6char}
   jq -r '.run_id' logs/ci-*.log | head -1 | grep -E '^run-[0-9]{8}-[0-9]{6}-[a-z0-9]{6}$'
   ```

---

### Test 6: E2E Test Retry (FR-012, FR-013)

**Purpose**: Verify flaky E2E tests are retried once

**Steps**:

1. **Simulate flaky E2E test**:
   ```bash
   # Edit web/tests/e2e/example.spec.js temporarily
   # Add random failure:
   if (Math.random() < 0.5) {
     throw new Error('Simulated flaky test failure');
   }
   ```

2. **Run pipeline multiple times**:
   ```bash
   for i in {1..5}; do
     echo "Run $i:"
     ./scripts/local-ci/run.sh
     echo "Exit code: $?"
     echo "---"
   done
   ```

3. **Expected behavior**:
   - Some runs: E2E fails on attempt 1, passes on attempt 2 (exit 0)
   - Some runs: E2E passes on attempt 1 (no retry, exit 0)
   - Rare: E2E fails both attempts (exit 2)

4. **Check logs for retry attempts**:
   ```bash
   # Look for retry log entries
   jq 'select(.step_name=="test-e2e" and (.message | contains("attempt")))' logs/ci-*.log
   ```

5. **Cleanup**: Remove flaky test code

**Expected Log Entry** (retry scenario):
```json
{
  "timestamp": "2025-10-20T14:33:00Z",
  "level": "warn",
  "message": "E2E tests failed (exit 1), retrying once...",
  "run_id": "run-20251020-143045-k8m3q2",
  "source_file": "scripts/local-ci/run.sh",
  "line_number": 230,
  "function_name": "run_e2e_tests_with_retry",
  "step_name": "test-e2e"
}
```

---

### Test 7: Deployment State Tracking (FR-003, FR-004)

**Purpose**: Verify GitHub deployment workflow tracks state and retries

**Note**: This requires GitHub Actions environment. For local testing, inspect workflow file.

**Steps**:

1. **Check workflow file**:
   ```bash
   cat .github/workflows/deploy.yml
   ```

2. **Verify retry logic present**:
   ```bash
   # Look for retry loop with 3 attempts
   grep -A 20 "MAX_ATTEMPTS=3" .github/workflows/deploy.yml
   ```

3. **After successful deployment** (on GitHub):
   ```bash
   # Clone repo and check deployment state
   cat .github/deployment-state.json
   ```

4. **Expected structure**:
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
     }
   }
   ```

---

## Troubleshooting

### Issue: Parallel tests hanging

**Symptoms**: Test step never completes, process hangs

**Diagnosis**:
```bash
# Check for resource contention errors in logs
jq 'select(.message | contains("EADDRINUSE") or contains("port already in use"))' logs/ci-*.log
```

**Solution**:
- Verify serial fallback triggered: Look for "Resource contention detected, falling back to serial execution" in logs
- If not triggered: Check heuristic detection in `run_tests_with_fallback()` function
- Manual workaround: Run tests serially by setting `PARALLEL_TESTS=false` environment variable

---

### Issue: TUI shows blank/frozen screen

**Symptoms**: TUI launches but shows no progress updates

**Diagnosis**:
```bash
# Verify JSON log format
cat logs/ci-*.log | jq '.' | head -5

# Check tail -f permissions
tail -f logs/ci-*.log  # Should stream logs in real-time
```

**Solution**:
- If `jq` parse errors: Verify log entries are valid JSON (one object per line)
- If tail doesn't work: Check file permissions (`chmod 644 logs/ci-*.log`)
- If terminal doesn't clear: Verify ANSI terminal support (`echo $TERM`)

---

### Issue: Timeout not enforcing

**Symptoms**: Pipeline runs longer than 5 minutes without exiting

**Diagnosis**:
```bash
# Verify bash version supports $SECONDS
bash -c 'echo $SECONDS; sleep 2; echo $SECONDS'  # Should print 0, then 2

# Check timeout logic in script
grep -A 10 "check_timeout" scripts/local-ci/run.sh
```

**Solution**:
- If bash < 4.4: Upgrade bash
- If logic missing: Verify `check_timeout()` function called periodically (before and after each step)
- Manual test: Add `echo "Timeout check: $((SECONDS - START_TIME))s"` to debug

---

### Issue: Correlation IDs not unique

**Symptoms**: Multiple pipeline runs have same `run_id`

**Diagnosis**:
```bash
# Check correlation ID generation
bash -c 'source scripts/local-ci/run.sh; generate_correlation_id'  # Should print unique ID

# Verify /dev/urandom readable
head -c 10 /dev/urandom | tr -dc a-z0-9  # Should print random string
```

**Solution**:
- If same ID repeated: Check timestamp precision (`date +%Y%m%d-%H%M%S` should change every second)
- If random suffix same: Verify `/dev/urandom` access (`ls -l /dev/urandom`)
- Manual workaround: Add PID to correlation ID: `run-$(date +%Y%m%d-%H%M%S)-$$`

---

### Issue: E2E retry not working

**Symptoms**: Flaky E2E test fails without retry attempt

**Diagnosis**:
```bash
# Check for retry log entries
jq 'select(.step_name=="test-e2e" and (.message | contains("retry")))' logs/ci-*.log

# Verify retry wrapper called
grep -A 10 "run_e2e_tests_with_retry" scripts/local-ci/run.sh
```

**Solution**:
- If no retry logged: Verify `run_e2e_tests_with_retry()` function wraps `npm run test:e2e`
- If retry on wrong exit code: Check logic only retries on exit code 1 (test failure), not 5 (timeout)
- Manual test: Add `exit 1` before E2E tests to force retry

---

## Validation Checklist

After completing all tests, verify:

- [ ] Timeout enforcement works (exit code 5 on > 300s)
- [ ] Parallel tests complete faster (40-60% reduction)
- [ ] TUI shows real-time progress (updates every ~2s)
- [ ] Log entries include source context (file, line, function)
- [ ] Correlation IDs are unique per run
- [ ] E2E tests retry once on failure
- [ ] Deployment state tracking works (on GitHub)

**All checks passed**: Feature 002 implementation is complete and working correctly.

**Some checks failed**: Review troubleshooting section above or consult `specs/002-cicd-pipeline-enhancements/plan.md` for implementation details.

---

## Next Steps

After successful validation:

1. **Run full pipeline**: `./scripts/local-ci/run.sh` (should complete in < 300s)
2. **Test with TUI**: `./scripts/tui/run.sh` (select profile, verify real-time progress)
3. **Deploy to GitHub Pages**: Commit changes, push to main, verify deployment state tracking
4. **Monitor logs**: Check `logs/ci-*.log` for structured entries with correlation IDs

---

**Quickstart Guide Status**: ✅ COMPLETE
**Test Coverage**: 7 tests (timeout, parallel, TUI, logging, correlation, retry, deployment)
**Troubleshooting Scenarios**: 6 common issues
**Ready for User Testing**: ✅ YES
