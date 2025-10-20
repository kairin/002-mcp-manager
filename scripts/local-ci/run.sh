#!/usr/bin/env bash
# Local CI/CD Pipeline Script
# Runs linting, testing, and build steps with JSON logging
# See: specs/001-local-cicd-astro-site/spec.md

set -euo pipefail

# Get script directory (works even if called from elsewhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WEB_DIR="$PROJECT_ROOT/web"

# Source libraries
source "$SCRIPT_DIR/lib/logger.sh"
source "$SCRIPT_DIR/lib/validator.sh"

# Exit codes
readonly EXIT_SUCCESS=0
readonly EXIT_LINT_FAILED=1
readonly EXIT_TEST_FAILED=2
readonly EXIT_BUILD_FAILED=3
readonly EXIT_ENV_FAILED=4
readonly EXIT_TIMEOUT=5  # Feature 002: NFR-003 timeout enforcement

# Default options
NO_FIX=false
VERBOSE=false
SKIP_TESTS=false
LOG_FILE=""
PIPELINE_START=$(date +%s.%N)

# Feature 002: Timeout enforcement (NFR-003)
START_TIME=$SECONDS  # Bash builtin for elapsed time tracking
TIMEOUT_SECONDS=300  # 5-minute hard limit

# Feature 002: Pipeline Run Correlation (US6)
RUN_ID=""  # Will be generated in step_init

# Parse command-line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-fix)
                NO_FIX=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --log-file)
                LOG_FILE="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                show_help
                exit 1
                ;;
        esac
    done
}

# Show help message
show_help() {
    cat <<EOF
Local CI/CD Pipeline Script

Usage: $0 [OPTIONS]

Options:
  --no-fix         Skip auto-fix for linting errors
  --verbose        Show detailed output for each step
  --skip-tests     Skip all test steps (unit, integration, e2e)
  --log-file PATH  Write logs to specified file (default: logs/ci-TIMESTAMP.log)
  -h, --help       Show this help message

Exit codes:
  0 - Success
  1 - Lint failed
  2 - Tests failed
  3 - Build failed
  4 - Environment validation failed
  5 - Timeout violation (pipeline exceeded 5 minutes)

Examples:
  $0                      # Run full pipeline
  $0 --verbose            # Run with detailed output
  $0 --no-fix             # Run without auto-fixing lint errors
  $0 --skip-tests         # Run only lint and build
EOF
}

# Feature 002 - US6: Generate unique correlation ID for this pipeline run
# Format: run-YYYYMMDD-HHMMSS-{6char}
# Example: run-20251021-143045-k8m3q2
generate_correlation_id() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local random_suffix=$(head -c 100 /dev/urandom | tr -dc 'a-z0-9' | head -c 6)
    echo "run-${timestamp}-${random_suffix}"
}

# Step 1: Initialize
step_init() {
    local step_start=$(date +%s.%N)

    # Feature 002 - US6: Generate and export correlation ID
    RUN_ID=$(generate_correlation_id)
    export RUN_ID

    # Set up log file
    if [ -z "$LOG_FILE" ]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        LOG_FILE="$PROJECT_ROOT/logs/ci-$timestamp.log"
    fi

    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"

    # Log initialization (with run_id)
    log_info "init" "Starting local CI/CD pipeline" | tee -a "$LOG_FILE"
    log_info "init" "Run ID: $RUN_ID" | tee -a "$LOG_FILE"
    log_info "init" "Project root: $PROJECT_ROOT" | tee -a "$LOG_FILE"
    log_info "init" "Web directory: $WEB_DIR" | tee -a "$LOG_FILE"
    log_info "init" "Log file: $LOG_FILE" | tee -a "$LOG_FILE"

    local duration=$(get_duration "$step_start")
    local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
    log_success "init" "Initialization complete" "" "$duration_ms" | tee -a "$LOG_FILE"
}

# Step 2: Environment validation
step_env_check() {
    local step_start=$(date +%s.%N)

    log_info "env-check" "Validating environment and dependencies" | tee -a "$LOG_FILE"

    local failed=0

    # Check Bash version (>= 5.0)
    if ! validate_dependency "bash" "5.0"; then
        log_error "env-check" "Bash version check failed" | tee -a "$LOG_FILE"
        failed=1
    fi

    # Check jq (>= 1.6)
    if ! validate_dependency "jq" "1.6"; then
        log_error "env-check" "jq version check failed" | tee -a "$LOG_FILE"
        failed=1
    fi

    # Check Node.js (>= 18.0)
    if ! validate_dependency "node" "18.0"; then
        log_error "env-check" "Node.js version check failed" | tee -a "$LOG_FILE"
        failed=1
    fi

    # Check npm (>= 9.0)
    if ! validate_dependency "npm" "9.0"; then
        log_error "env-check" "npm version check failed" | tee -a "$LOG_FILE"
        failed=1
    fi

    # Check web directory exists
    if ! validate_directory_exists "$WEB_DIR"; then
        log_error "env-check" "Web directory not found: $WEB_DIR" | tee -a "$LOG_FILE"
        failed=1
    fi

    local duration=$(get_duration "$step_start")
    local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')

    if [ $failed -eq 0 ]; then
        log_success "env-check" "Environment validation passed" "" "$duration_ms" | tee -a "$LOG_FILE"
        return 0
    else
        log_error "env-check" "Environment validation failed" "" "$duration_ms" "$EXIT_ENV_FAILED" | tee -a "$LOG_FILE"
        return $EXIT_ENV_FAILED
    fi
}

# Step 3: Lint
step_lint() {
    local step_start=$(date +%s.%N)

    log_info "lint" "Running Prettier linter" | tee -a "$LOG_FILE"

    cd "$WEB_DIR"

    # First check
    if npx prettier --check . >> "$LOG_FILE" 2>&1; then
        local duration=$(get_duration "$step_start")
        local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
        log_success "lint" "Linting passed" "" "$duration_ms" | tee -a "$LOG_FILE"
        return 0
    fi

    # If check failed and auto-fix is disabled
    if [ "$NO_FIX" = true ]; then
        local duration=$(get_duration "$step_start")
        local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
        log_error "lint" "Linting failed (auto-fix disabled)" "" "$duration_ms" "$EXIT_LINT_FAILED" | tee -a "$LOG_FILE"
        return $EXIT_LINT_FAILED
    fi

    # Auto-fix
    log_info "lint" "Auto-fixing linting errors" | tee -a "$LOG_FILE"
    if npx prettier --write . >> "$LOG_FILE" 2>&1; then
        # Re-check after fix
        if npx prettier --check . >> "$LOG_FILE" 2>&1; then
            local duration=$(get_duration "$step_start")
            local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
            log_success "lint" "Linting passed after auto-fix" "" "$duration_ms" | tee -a "$LOG_FILE"
            return 0
        fi
    fi

    # Failed even after auto-fix
    local duration=$(get_duration "$step_start")
    local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
    log_error "lint" "Linting failed after auto-fix" "" "$duration_ms" "$EXIT_LINT_FAILED" | tee -a "$LOG_FILE"
    return $EXIT_LINT_FAILED
}

# Step 4: Unit tests
step_test_unit() {
    local step_start=$(date +%s.%N)

    if [ "$SKIP_TESTS" = true ]; then
        log_info "test-unit" "Skipping unit tests (--skip-tests flag)" | tee -a "$LOG_FILE"
        return 0
    fi

    log_info "test-unit" "Running unit tests" | tee -a "$LOG_FILE"

    cd "$WEB_DIR"

    if npx mocha tests/unit/**/*.test.js >> "$LOG_FILE" 2>&1; then
        local duration=$(get_duration "$step_start")
        local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
        log_success "test-unit" "Unit tests passed" "" "$duration_ms" | tee -a "$LOG_FILE"
        return 0
    else
        local exit_code=$?
        local duration=$(get_duration "$step_start")
        local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
        log_error "test-unit" "Unit tests failed" "" "$duration_ms" "$exit_code" | tee -a "$LOG_FILE"
        return $EXIT_TEST_FAILED
    fi
}

# Step 5: Integration tests
step_test_integration() {
    local step_start=$(date +%s.%N)

    if [ "$SKIP_TESTS" = true ]; then
        log_info "test-integration" "Skipping integration tests (--skip-tests flag)" | tee -a "$LOG_FILE"
        return 0
    fi

    log_info "test-integration" "Running integration tests" | tee -a "$LOG_FILE"

    cd "$WEB_DIR"

    if npx mocha tests/integration/**/*.test.js >> "$LOG_FILE" 2>&1; then
        local duration=$(get_duration "$step_start")
        local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
        log_success "test-integration" "Integration tests passed" "" "$duration_ms" | tee -a "$LOG_FILE"
        return 0
    else
        local exit_code=$?
        local duration=$(get_duration "$step_start")
        local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
        log_error "test-integration" "Integration tests failed" "" "$duration_ms" "$exit_code" | tee -a "$LOG_FILE"
        return $EXIT_TEST_FAILED
    fi
}

# Step 6: E2E tests
step_test_e2e() {
    local step_start=$(date +%s.%N)

    if [ "$SKIP_TESTS" = true ]; then
        log_info "test-e2e" "Skipping E2E tests (--skip-tests flag)" | tee -a "$LOG_FILE"
        return 0
    fi

    log_info "test-e2e" "Running E2E tests with Playwright" | tee -a "$LOG_FILE"

    cd "$WEB_DIR"

    if npx playwright test >> "$LOG_FILE" 2>&1; then
        local duration=$(get_duration "$step_start")
        local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
        log_success "test-e2e" "E2E tests passed" "" "$duration_ms" | tee -a "$LOG_FILE"
        return 0
    else
        local exit_code=$?
        local duration=$(get_duration "$step_start")
        local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
        log_error "test-e2e" "E2E tests failed" "" "$duration_ms" "$exit_code" | tee -a "$LOG_FILE"
        return $EXIT_TEST_FAILED
    fi
}

# Step 7: Build
step_build() {
    local step_start=$(date +%s.%N)

    log_info "build" "Building project" | tee -a "$LOG_FILE"

    cd "$WEB_DIR"

    # Run build
    if npm run build >> "$LOG_FILE" 2>&1; then
        # Verify dist/ was created
        if [ -d "$WEB_DIR/dist" ]; then
            local duration=$(get_duration "$step_start")
            local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
            log_success "build" "Build completed successfully" "" "$duration_ms" | tee -a "$LOG_FILE"
            return 0
        else
            local duration=$(get_duration "$step_start")
            local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
            log_error "build" "Build succeeded but dist/ directory not found" "" "$duration_ms" "$EXIT_BUILD_FAILED" | tee -a "$LOG_FILE"
            return $EXIT_BUILD_FAILED
        fi
    else
        local exit_code=$?
        local duration=$(get_duration "$step_start")
        local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
        log_error "build" "Build failed" "" "$duration_ms" "$exit_code" | tee -a "$LOG_FILE"
        return $EXIT_BUILD_FAILED
    fi
}

# Step 8: Cleanup
step_cleanup() {
    local step_start=$(date +%s.%N)

    log_info "cleanup" "Running cleanup tasks" | tee -a "$LOG_FILE"

    # Run cleanup script if it exists
    if [ -f "$SCRIPT_DIR/lib/cleanup-logs.sh" ]; then
        if bash "$SCRIPT_DIR/lib/cleanup-logs.sh" >> "$LOG_FILE" 2>&1; then
            local duration=$(get_duration "$step_start")
            local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
            log_success "cleanup" "Cleanup completed" "" "$duration_ms" | tee -a "$LOG_FILE"
        else
            local duration=$(get_duration "$step_start")
            local duration_ms=$(echo "$duration * 1000" | bc | awk '{printf "%.0f", $0}')
            log_warn "cleanup" "Cleanup script failed (non-critical)" "" "$duration_ms" | tee -a "$LOG_FILE"
        fi
    else
        log_info "cleanup" "No cleanup script found, skipping" | tee -a "$LOG_FILE"
    fi
}

# Feature 002: Timeout check function (US1 - FR-001, FR-002)
check_timeout() {
    local elapsed=$((SECONDS - START_TIME))
    if (( elapsed >= TIMEOUT_SECONDS )); then
        local error_msg="Pipeline failed: duration exceeded NFR-003 limit (${elapsed}s > ${TIMEOUT_SECONDS}s)"
        local elapsed_ms=$((elapsed * 1000))
        log_error "timeout" "$error_msg" "" "$elapsed_ms" "$EXIT_TIMEOUT" | tee -a "$LOG_FILE"
        exit $EXIT_TIMEOUT
    fi
}

# Feature 002: Parallel test execution (US3 - FR-005, FR-006)
run_tests_parallel() {
    if [ "$SKIP_TESTS" = true ]; then
        log_info "test-parallel" "Skipping all tests (--skip-tests flag)" | tee -a "$LOG_FILE"
        return 0
    fi

    log_info "test-parallel" "Running tests in parallel (unit, integration, e2e)" | tee -a "$LOG_FILE"

    local test_types=("unit" "integration" "e2e")
    local pids=()
    local exit_codes=()
    local temp_logs=()

    # Launch all tests in background with separate log files
    for test_type in "${test_types[@]}"; do
        local temp_log="/tmp/ci-test-${test_type}-$$.log"
        temp_logs+=("$temp_log")

        (
            cd "$WEB_DIR"
            case "$test_type" in
                "unit")
                    npx mocha tests/unit/**/*.test.js >> "$temp_log" 2>&1
                    ;;
                "integration")
                    npx mocha tests/integration/**/*.test.js >> "$temp_log" 2>&1
                    ;;
                "e2e")
                    npx playwright test >> "$temp_log" 2>&1
                    ;;
            esac
        ) &
        pids+=($!)
    done

    # Wait for all jobs and collect exit codes
    for i in "${!pids[@]}"; do
        wait "${pids[$i]}"
        exit_codes+=($?)
    done

    # Aggregate logs into main log file
    for i in "${!test_types[@]}"; do
        cat "${temp_logs[$i]}" >> "$LOG_FILE"
        rm -f "${temp_logs[$i]}"
    done

    # Check for resource contention indicators
    local contention_detected=false
    for temp_log in "${temp_logs[@]}"; do
        if [ -f "$temp_log" ]; then
            if grep -Eq "(EADDRINUSE|port already in use|lock file exists|database is locked)" "$temp_log" 2>/dev/null; then
                contention_detected=true
                break
            fi
        fi
    done

    # Check for failures
    local failed_tests=()
    for i in "${!test_types[@]}"; do
        if [[ ${exit_codes[$i]} -ne 0 ]]; then
            failed_tests+=("${test_types[$i]}")
        fi
    done

    # If resource contention detected and tests failed, fall back to serial
    if [ "$contention_detected" = true ] && [ ${#failed_tests[@]} -gt 0 ]; then
        log_warn "test-parallel" "Resource contention detected, falling back to serial execution" | tee -a "$LOG_FILE"
        return 1  # Signal to run serial fallback
    fi

    # Report results
    if [ ${#failed_tests[@]} -eq 0 ]; then
        log_success "test-parallel" "All parallel tests passed (unit, integration, e2e)" | tee -a "$LOG_FILE"
        return 0
    else
        log_error "test-parallel" "Tests failed: ${failed_tests[*]}" | tee -a "$LOG_FILE"
        return $EXIT_TEST_FAILED
    fi
}

# Feature 002: Serial test fallback (US3 - FR-017)
run_tests_serial() {
    log_info "test-serial" "Running tests in serial mode" | tee -a "$LOG_FILE"

    # Run tests sequentially
    step_test_unit || return $?
    step_test_integration || return $?
    step_test_e2e || return $?

    log_success "test-serial" "All serial tests passed" | tee -a "$LOG_FILE"
    return 0
}

# Step 9: Complete
step_complete() {
    local pipeline_end=$(date +%s.%N)
    local total_duration=$(get_duration "$PIPELINE_START" "$pipeline_end")

    # Feature 002: Hard check for timeout violation (this shouldn't be reached if check_timeout works)
    local total_duration_ms=$(echo "$total_duration * 1000" | bc | awk '{printf "%.0f", $0}')
    if (( $(echo "$total_duration > 300" | bc -l) )); then
        log_error "complete" "Pipeline failed: duration exceeded NFR-003 limit" "" "$total_duration_ms" "$EXIT_TIMEOUT" | tee -a "$LOG_FILE"
        exit $EXIT_TIMEOUT
    else
        log_success "complete" "Pipeline completed successfully" "" "$total_duration_ms" | tee -a "$LOG_FILE"
    fi

    # Output final summary
    jq -n \
        --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")" \
        --arg duration "$total_duration" \
        --arg logFile "$LOG_FILE" \
        '{
            timestamp: $timestamp,
            level: "info",
            step: "complete",
            message: "CI/CD pipeline finished",
            duration: ($duration | tonumber),
            logFile: $logFile,
            summary: {
                status: "success",
                totalDuration: ($duration | tonumber)
            }
        }' | tee -a "$LOG_FILE"
}

# Main execution
main() {
    parse_args "$@"

    # Feature 002: Run pipeline steps with timeout checks (US1)
    step_init || exit $?
    check_timeout

    step_env_check || exit $?
    check_timeout

    step_lint || exit $?
    check_timeout

    # Feature 002: Parallel test execution with serial fallback (US3)
    if ! run_tests_parallel; then
        # If return code is 1, try serial fallback (resource contention)
        # If return code is EXIT_TEST_FAILED (2), tests genuinely failed
        if [ $? -eq 1 ]; then
            run_tests_serial || exit $?
        else
            exit $EXIT_TEST_FAILED
        fi
    fi
    check_timeout

    step_build || exit $?
    check_timeout

    step_cleanup
    check_timeout

    step_complete
    # Final check happens in step_complete

    exit $EXIT_SUCCESS
}

# Run main function with all arguments
main "$@"
