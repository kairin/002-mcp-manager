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

# Default options
NO_FIX=false
VERBOSE=false
SKIP_TESTS=false
LOG_FILE=""
PIPELINE_START=$(date +%s.%N)

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

Examples:
  $0                      # Run full pipeline
  $0 --verbose            # Run with detailed output
  $0 --no-fix             # Run without auto-fixing lint errors
  $0 --skip-tests         # Run only lint and build
EOF
}

# Step 1: Initialize
step_init() {
    local step_start=$(date +%s.%N)

    # Set up log file
    if [ -z "$LOG_FILE" ]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        LOG_FILE="$PROJECT_ROOT/logs/ci-$timestamp.log"
    fi

    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"

    # Log initialization
    log_info "init" "Starting local CI/CD pipeline" | tee -a "$LOG_FILE"
    log_info "init" "Project root: $PROJECT_ROOT" | tee -a "$LOG_FILE"
    log_info "init" "Web directory: $WEB_DIR" | tee -a "$LOG_FILE"
    log_info "init" "Log file: $LOG_FILE" | tee -a "$LOG_FILE"

    local duration=$(get_duration "$step_start")
    log_success "init" "Initialization complete" "$duration" | tee -a "$LOG_FILE"
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

    if [ $failed -eq 0 ]; then
        log_success "env-check" "Environment validation passed" "$duration" | tee -a "$LOG_FILE"
        return 0
    else
        log_error "env-check" "Environment validation failed" "$duration" "$EXIT_ENV_FAILED" | tee -a "$LOG_FILE"
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
        log_success "lint" "Linting passed" "$duration" | tee -a "$LOG_FILE"
        return 0
    fi

    # If check failed and auto-fix is disabled
    if [ "$NO_FIX" = true ]; then
        local duration=$(get_duration "$step_start")
        log_error "lint" "Linting failed (auto-fix disabled)" "$duration" "$EXIT_LINT_FAILED" | tee -a "$LOG_FILE"
        return $EXIT_LINT_FAILED
    fi

    # Auto-fix
    log_info "lint" "Auto-fixing linting errors" | tee -a "$LOG_FILE"
    if npx prettier --write . >> "$LOG_FILE" 2>&1; then
        # Re-check after fix
        if npx prettier --check . >> "$LOG_FILE" 2>&1; then
            local duration=$(get_duration "$step_start")
            log_success "lint" "Linting passed after auto-fix" "$duration" | tee -a "$LOG_FILE"
            return 0
        fi
    fi

    # Failed even after auto-fix
    local duration=$(get_duration "$step_start")
    log_error "lint" "Linting failed after auto-fix" "$duration" "$EXIT_LINT_FAILED" | tee -a "$LOG_FILE"
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
        log_success "test-unit" "Unit tests passed" "$duration" | tee -a "$LOG_FILE"
        return 0
    else
        local exit_code=$?
        local duration=$(get_duration "$step_start")
        log_error "test-unit" "Unit tests failed" "$duration" "$exit_code" | tee -a "$LOG_FILE"
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
        log_success "test-integration" "Integration tests passed" "$duration" | tee -a "$LOG_FILE"
        return 0
    else
        local exit_code=$?
        local duration=$(get_duration "$step_start")
        log_error "test-integration" "Integration tests failed" "$duration" "$exit_code" | tee -a "$LOG_FILE"
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
        log_success "test-e2e" "E2E tests passed" "$duration" | tee -a "$LOG_FILE"
        return 0
    else
        local exit_code=$?
        local duration=$(get_duration "$step_start")
        log_error "test-e2e" "E2E tests failed" "$duration" "$exit_code" | tee -a "$LOG_FILE"
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
            log_success "build" "Build completed successfully" "$duration" | tee -a "$LOG_FILE"
            return 0
        else
            local duration=$(get_duration "$step_start")
            log_error "build" "Build succeeded but dist/ directory not found" "$duration" "$EXIT_BUILD_FAILED" | tee -a "$LOG_FILE"
            return $EXIT_BUILD_FAILED
        fi
    else
        local exit_code=$?
        local duration=$(get_duration "$step_start")
        log_error "build" "Build failed" "$duration" "$exit_code" | tee -a "$LOG_FILE"
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
            log_success "cleanup" "Cleanup completed" "$duration" | tee -a "$LOG_FILE"
        else
            local duration=$(get_duration "$step_start")
            log_warn "cleanup" "Cleanup script failed (non-critical)" "$duration" | tee -a "$LOG_FILE"
        fi
    else
        log_info "cleanup" "No cleanup script found, skipping" | tee -a "$LOG_FILE"
    fi
}

# Step 9: Complete
step_complete() {
    local pipeline_end=$(date +%s.%N)
    local total_duration=$(get_duration "$PIPELINE_START" "$pipeline_end")

    # Check if duration exceeds 5 minutes (300 seconds)
    if (( $(echo "$total_duration > 300" | bc -l) )); then
        log_warn "complete" "Pipeline completed but took longer than 5 minutes" "$total_duration" | tee -a "$LOG_FILE"
    else
        log_success "complete" "Pipeline completed successfully" "$total_duration" | tee -a "$LOG_FILE"
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

    # Run pipeline steps
    step_init || exit $?
    step_env_check || exit $?
    step_lint || exit $?
    step_test_unit || exit $?
    step_test_integration || exit $?
    step_test_e2e || exit $?
    step_build || exit $?
    step_cleanup
    step_complete

    exit $EXIT_SUCCESS
}

# Run main function with all arguments
main "$@"
