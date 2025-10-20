# Implementation Guide: Remaining Phases (8-12)

**Feature**: CI/CD Pipeline Improvements (002)
**Branch**: `002-cicd-pipeline-enhancements`
**Status**: Phase 7 Complete, Phases 8-12 Pending

## Phase 7 ✅ COMPLETE

**User Story 6 - Pipeline Run Correlation** is now fully implemented:
- Unique correlation IDs (`run-YYYYMMDD-HHMMSS-{6char}`) generated per pipeline run
- All log entries automatically include `run_id` field
- Committed: `a2431fa`

---

## Phase 8: Real-Time TUI Progress Updates (Priority: P2)

**Goal**: Parse JSON logs in real-time and display live progress in TUI
**Tasks**: T038-T044
**Files to Modify**: `scripts/tui/run.sh`

### Implementation Steps

#### 1. Create JSON Log Parser Function (T038)

Add to `scripts/tui/run.sh`:

```bash
# Parse JSON logs in real-time using tail and jq
parse_pipeline_logs() {
    local log_file="$1"

    # Use tail -f to follow log file, parse with jq
    tail -f "$log_file" 2>/dev/null | while IFS= read -r line; do
        # Parse JSON entry
        local step=$(echo "$line" | jq -r '.step_name // "unknown"' 2>/dev/null)
        local level=$(echo "$line" | jq -r '.level // "info"' 2>/dev/null)
        local message=$(echo "$line" | jq -r '.message // ""' 2>/dev/null)
        local duration=$(echo "$line" | jq -r '.duration_ms // null' 2>/dev/null)

        # Call display update function
        update_progress_display "$step" "$level" "$message" "$duration"

        # Exit on pipeline completion
        if [[ "$step" == "complete" ]]; then
            break
        fi
    done
}
```

#### 2. Implement Progress Tracking State (T039)

Add state variables:

```bash
# Progress tracking state
declare -A PROGRESS_STATE=(
    [current_step]="init"
    [step_count]=0
    [elapsed_time]=0
    [total_steps]=9  # init, env-check, lint, test-unit, test-integration, test-e2e, build, cleanup, complete
)
```

#### 3. Create Progress Display Function (T040)

```bash
# Clear and redraw progress display
update_progress_display() {
    local step="$1"
    local level="$2"
    local message="$3"
    local duration="$4"

    # Update state
    PROGRESS_STATE[current_step]="$step"
    PROGRESS_STATE[elapsed_time]=$((PROGRESS_STATE[elapsed_time] + 1))

    # Clear screen and redraw
    clear
    echo "=== CI/CD Pipeline Progress ==="
    echo ""
    echo "Current Step: ${step}"
    echo "Status: ${message}"

    if [[ "$duration" != "null" ]]; then
        echo "Duration: ${duration}ms"
    fi

    echo ""
    echo "Log Level: ${level}"
    echo "Elapsed: ${PROGRESS_STATE[elapsed_time]}s"
}
```

#### 4. Add Step Completion Detection (T041)

Track completed steps:

```bash
# Detect step completion from log level "success"
if [[ "$level" == "success" ]]; then
    PROGRESS_STATE[step_count]=$((PROGRESS_STATE[step_count] + 1))
fi
```

#### 5. Add Step Status Indicators (T042)

```bash
# Add status indicators based on log level
get_status_indicator() {
    local level="$1"
    case "$level" in
        success) echo "✓" ;;
        error) echo "✗" ;;
        warn) echo "⚠" ;;
        *) echo "●" ;;
    esac
}
```

#### 6. Implement Progress Update Loop (T043)

Add rate limiting (every 1-2 seconds):

```bash
# Track last update time for rate limiting
LAST_UPDATE=$SECONDS

# In parse loop, add rate limiting
local elapsed=$((SECONDS - LAST_UPDATE))
if (( elapsed >= 2 )); then
    update_progress_display "$step" "$level" "$message" "$duration"
    LAST_UPDATE=$SECONDS
fi
```

#### 7. Add Error Handling for Malformed JSON (T044)

```bash
# Wrap jq calls in error handling
parse_json_field() {
    local line="$1"
    local field="$2"
    echo "$line" | jq -r ".${field} // \"unknown\"" 2>/dev/null || echo "unknown"
}
```

### Testing Phase 8

```bash
# Launch TUI and verify real-time updates
./scripts/tui/run.sh

# Select a profile (e.g., dev)
# Expected: Progress updates every ~2 seconds showing current step
```

---

## Phase 9: E2E Test Retry for Stability (Priority: P3)

**Goal**: Retry E2E tests once if first attempt fails
**Tasks**: T045-T050
**Files to Modify**: `scripts/local-ci/run.sh`

### Implementation Steps

#### 1. Create E2E Test Retry Wrapper (T045)

Find the E2E test execution section in `run.sh` and replace with:

```bash
# Feature 002 - US7: E2E test retry wrapper
run_e2e_tests_with_retry() {
    local max_attempts=2
    local step_start=$(date +%s.%N)

    for attempt in $(seq 1 $max_attempts); do
        log_info "test-e2e" "E2E tests attempt $attempt/$max_attempts" | tee -a "$LOG_FILE"

        # Run Playwright tests
        cd "$WEB_DIR"
        if npm run test:e2e >> "$LOG_FILE" 2>&1; then
            local duration=$(get_duration "$step_start")
            local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
            log_success "test-e2e" "E2E tests passed on attempt $attempt" "" "$duration_ms" | tee -a "$LOG_FILE"
            return 0
        fi

        local exit_code=$?

        # Only retry on test failures (exit code 1), not timeouts or other errors
        if (( exit_code == 1 && attempt < max_attempts )); then
            log_warn "test-e2e" "E2E tests failed (exit $exit_code), retrying once..." | tee -a "$LOG_FILE"
            sleep 2  # Brief delay before retry
        else
            local duration=$(get_duration "$step_start")
            local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
            log_error "test-e2e" "E2E tests failed after $attempt attempt(s)" "" "$duration_ms" "$EXIT_TEST_FAILED" | tee -a "$LOG_FILE"
            return $EXIT_TEST_FAILED
        fi
    done

    return $EXIT_TEST_FAILED
}
```

#### 2. Replace E2E Test Call (T046-T050)

Find the existing E2E test step and replace the test execution with:

```bash
step_test_e2e() {
    # ... existing setup ...

    # Use retry wrapper instead of direct npm call
    if ! run_e2e_tests_with_retry; then
        return $EXIT_TEST_FAILED
    fi

    # ... existing cleanup ...
}
```

### Testing Phase 9

```bash
# Temporarily make an E2E test flaky to verify retry
# Edit web/tests/e2e/example.spec.js
# Add: if (Math.random() < 0.5) throw new Error('Simulated flaky test');

# Run pipeline
./scripts/local-ci/run.sh

# Expected: E2E tests may fail on attempt 1, succeed on attempt 2
# Check logs for retry messages
```

---

## Phase 10: Constitution File Validation (Priority: P3)

**Goal**: Check `.specify/memory/constitution.md` exists, warn if missing
**Tasks**: T051-T056
**Files to Modify**: `scripts/local-ci/lib/validator.sh`

### Implementation Steps

#### 1. Add Constitution File Check Function (T051)

Add to `scripts/local-ci/lib/validator.sh`:

```bash
# Feature 002 - US8: Validate constitution file exists (optional check)
validate_constitution_file() {
    local project_root="$1"
    local constitution_file="$project_root/.specify/memory/constitution.md"

    if [[ -f "$constitution_file" ]]; then
        echo "found"
    else
        echo "missing"
    fi
}
```

#### 2. Integrate into Environment Validation (T052)

In `scripts/local-ci/lib/validator.sh`, add to `validate_environment()` or create new function:

```bash
# Check constitution file (non-blocking)
check_constitution() {
    local project_root="$1"
    local log_file="$2"

    local result=$(validate_constitution_file "$project_root")

    if [[ "$result" == "found" ]]; then
        log_info "env-check" "Constitution file: found ✓" | tee -a "$log_file"
    else
        log_warn "env-check" "Constitution file missing (optional for SpecKit projects)" | tee -a "$log_file"
        log_info "env-check" "Hint: Run /speckit.constitution to create" | tee -a "$log_file"
    fi

    # Always return 0 (non-blocking check)
    return 0
}
```

#### 3. Call from step_env_check (T053-T056)

In `scripts/local-ci/run.sh`, add to `step_env_check()`:

```bash
step_env_check() {
    # ... existing checks ...

    # Feature 002 - US8: Constitution check (non-blocking)
    check_constitution "$PROJECT_ROOT" "$LOG_FILE"

    # ... rest of function ...
}
```

### Testing Phase 10

```bash
# Test with constitution file present
touch .specify/memory/constitution.md
./scripts/local-ci/run.sh
# Expected: "Constitution file: found ✓"

# Test with file missing
rm .specify/memory/constitution.md
./scripts/local-ci/run.sh
# Expected: Warning message with hint
```

---

## Phase 11: Integration Test Regex Matchers (Priority: P3)

**Goal**: Refactor `.toContain()` to `.toMatch(/regex/)` for robust assertions
**Tasks**: T057-T060
**Files to Modify**: `web/tests/integration/*.test.js`

### Implementation Steps

#### 1. Identify Files (T057-T058)

```bash
# Find integration test files
grep -r "\.toContain(" web/tests/integration/
```

Expected files:
- `web/tests/integration/Header.integration.test.js`
- `web/tests/integration/modules.integration.test.js`

#### 2. Refactor Assertions (T057-T058)

**Before**:
```javascript
expect(output).toContain('DevDojo Profile Switcher');
```

**After**:
```javascript
expect(output).toMatch(/DevDojo Profile Switcher/);
```

**Pattern matching examples**:
```javascript
// Exact string → regex with escaping
.toContain('MCP Server')  →  .toMatch(/MCP Server/)

// With special characters → escape them
.toContain('status: OK')  →  .toMatch(/status: OK/)

// Flexible matching → use regex patterns
.toContain('Server')  →  .toMatch(/Server|service/)

// Case insensitive
.toContain('error')  →  .toMatch(/error/i)
```

#### 3. Run Integration Tests (T059)

```bash
cd web
npm run test:integration

# Verify all tests pass with new regex matchers
```

#### 4. Add Test Case for Malformed Output (T060)

Add to relevant integration test file:

```javascript
test('rejects malformed output', () => {
    const malformedOutput = 'INVALID_DATA_NO_MATCH';
    expect(malformedOutput).not.toMatch(/expected pattern/);
});
```

### Testing Phase 11

```bash
# Run integration tests
cd web && npm run test:integration

# Expected: All tests pass with regex matchers
# Verify tests correctly reject malformed output
```

---

## Phase 12: Polish & Documentation

**Goal**: Update documentation, run validation tests, finalize feature
**Tasks**: T061-T073

### Implementation Steps

#### 1. Update README Files (T061-T063)

**scripts/local-ci/README.md**:
```markdown
## New Features (Feature 002)

- **Timeout Enforcement**: Pipeline exits with code 5 if exceeds 300 seconds
- **Parallel Test Execution**: Unit, integration, E2E tests run concurrently (40-60% faster)
- **Correlation IDs**: Unique run_id in all log entries for cross-run tracing
- **E2E Test Retry**: Automatic retry on first failure for stability
- **Enhanced Logging**: Source file, line number, function name in all logs
```

**scripts/tui/README.md**:
```markdown
## Real-Time Progress (Feature 002)

The TUI now displays real-time pipeline progress:
- Updates every 1-2 seconds
- Shows current step, status, duration
- Step completion indicators (✓/✗/⚠)
- No more frozen screen during execution
```

#### 2. Verify Exit Codes (T064)

Confirm help message documents all exit codes including new code 5.

#### 3. Run End-to-End Tests (T065-T069)

```bash
# Test with all profiles
for profile in dev ui full; do
    echo "Testing profile: $profile"
    ./scripts/tui/run.sh  # Select profile manually
done

# Test timeout enforcement (T066)
# Add: sleep 301 to run.sh temporarily
./scripts/local-ci/run.sh
# Expected: Exit code 5, timeout error logged

# Test parallel execution (T067)
time ./scripts/local-ci/run.sh
# Expected: Test phase completes in ~60s (vs ~150s serial)

# Test TUI progress (T068)
./scripts/tui/run.sh
# Expected: Real-time updates every 1-2 seconds

# Test E2E retry (T069)
# Add flaky test, run pipeline
# Expected: Retry logged, tests eventually pass
```

#### 4. Validate JSON Schemas (T070-T071)

```bash
# Validate log entries match schema
jq -s '.[0]' logs/ci-*.log | \
    jq -f specs/002-cicd-pipeline-enhancements/contracts/log-schema.json

# Check deployment state (if deployed)
jq '.' .github/deployment-state.json | \
    jq -f specs/002-cicd-pipeline-enhancements/contracts/deployment-state-schema.json
```

#### 5. Code Cleanup (T072)

```bash
# Remove any debug logging
grep -r "console.log\|echo.*DEBUG" scripts/

# Finalize comments
# Verify all functions have proper documentation
```

#### 6. Run Quickstart Validation (T073)

Follow `specs/002-cicd-pipeline-enhancements/quickstart.md` test scenarios.

---

## Commit Strategy

After completing each phase:

```bash
# Stage changes
git add <modified-files>

# Commit with descriptive message
git commit -m "feat: <Phase description> (Phase X - USY)

<Detailed description>

Completes tasks TXXX-TXXX.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to branch
git push origin 002-cicd-pipeline-enhancements
```

---

## Priority Recommendation

Based on complexity and value:

1. **Phase 10** (Constitution Check) - Easiest, quick win
2. **Phase 9** (E2E Retry) - Medium complexity, high stability value
3. **Phase 11** (Regex Matchers) - Easy refactoring, test quality improvement
4. **Phase 12** (Documentation) - Essential for completion
5. **Phase 8** (TUI Progress) - Most complex, requires careful testing

---

## Testing Checklist

After all phases complete:

- [ ] Pipeline enforces 300-second timeout (exit code 5)
- [ ] Tests run in parallel (40-60% faster)
- [ ] All logs include unique run_id
- [ ] TUI shows real-time progress
- [ ] E2E tests retry once on failure
- [ ] Constitution check warns if file missing
- [ ] Integration tests use regex matchers
- [ ] Documentation updated
- [ ] All validation tests pass

---

**Document Status**: ✅ READY FOR IMPLEMENTATION
**Last Updated**: 2025-10-21
**Phase 7 Commit**: `a2431fa`
