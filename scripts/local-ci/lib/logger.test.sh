#!/usr/bin/env bash
# Unit Tests for logger.sh
# Run: bash logger.test.sh

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Source the logger library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/logger.sh"

# assert_equals: Compare expected and actual values
assert_equals() {
    local expected="$1"
    local actual="$2"
    local test_name="$3"

    TESTS_RUN=$((TESTS_RUN + 1))

    if [ "$expected" = "$actual" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✓${NC} $test_name"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  ${YELLOW}Expected:${NC} $expected"
        echo -e "  ${YELLOW}Actual:${NC} $actual"
        return 1
    fi
}

# assert_json_valid: Check if output is valid JSON
assert_json_valid() {
    local json="$1"
    local test_name="$2"

    TESTS_RUN=$((TESTS_RUN + 1))

    if echo "$json" | jq . > /dev/null 2>&1; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✓${NC} $test_name"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  ${YELLOW}Invalid JSON:${NC} $json"
        return 1
    fi
}

# assert_json_field: Check if JSON has expected field value
assert_json_field() {
    local json="$1"
    local field="$2"
    local expected="$3"
    local test_name="$4"

    TESTS_RUN=$((TESTS_RUN + 1))

    local actual
    actual=$(echo "$json" | jq -r ".$field")

    if [ "$actual" = "$expected" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✓${NC} $test_name"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  ${YELLOW}Expected ${field}:${NC} $expected"
        echo -e "  ${YELLOW}Actual ${field}:${NC} $actual"
        return 1
    fi
}

echo "======================================"
echo "Logger Library Unit Tests"
echo "======================================"
echo

# Test 1: log_json produces valid JSON
echo "Test 1: Basic log_json output"
OUTPUT=$(log_json "info" "test-step" "test message")
assert_json_valid "$OUTPUT" "log_json produces valid JSON"

# Test 2: Required fields are present
assert_json_field "$OUTPUT" "level" "info" "log_json includes 'level' field"
assert_json_field "$OUTPUT" "step" "test-step" "log_json includes 'step' field"
assert_json_field "$OUTPUT" "message" "test message" "log_json includes 'message' field"

# Test 3: Timestamp format (ISO 8601)
TIMESTAMP=$(echo "$OUTPUT" | jq -r '.timestamp')
if [[ "$TIMESTAMP" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$ ]]; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}✓${NC} Timestamp follows ISO 8601 format"
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}✗${NC} Timestamp follows ISO 8601 format"
    echo -e "  ${YELLOW}Actual:${NC} $TIMESTAMP"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Test 4: Optional duration field
OUTPUT_WITH_DURATION=$(log_json "success" "build" "Build complete" "123.5")
assert_json_field "$OUTPUT_WITH_DURATION" "duration" "123.5" "log_json includes optional 'duration' field"

# Test 5: Optional exitCode field
OUTPUT_WITH_EXIT=$(log_json "error" "lint" "Lint failed" "" "1")
assert_json_field "$OUTPUT_WITH_EXIT" "exitCode" "1" "log_json includes optional 'exitCode' field"

# Test 6: Special characters are escaped properly
OUTPUT_SPECIAL=$(log_json "info" "test" 'Message with "quotes" and \backslash')
assert_json_valid "$OUTPUT_SPECIAL" "log_json escapes special characters correctly"

# Test 7: Convenience function log_info
OUTPUT_INFO=$(log_info "init" "Starting pipeline")
assert_json_field "$OUTPUT_INFO" "level" "info" "log_info sets level to 'info'"

# Test 8: Convenience function log_success
OUTPUT_SUCCESS=$(log_success "complete" "All tests passed")
assert_json_field "$OUTPUT_SUCCESS" "level" "success" "log_success sets level to 'success'"

# Test 9: Convenience function log_warn
OUTPUT_WARN=$(log_warn "build" "Build slower than expected")
assert_json_field "$OUTPUT_WARN" "level" "warn" "log_warn sets level to 'warn'"

# Test 10: Convenience function log_error
OUTPUT_ERROR=$(log_error "test-e2e" "Playwright tests failed")
assert_json_field "$OUTPUT_ERROR" "level" "error" "log_error sets level to 'error'"

# Test 11: get_duration calculates correctly
START_TIME=$(date +%s.%N)
sleep 0.1
DURATION=$(get_duration "$START_TIME")
# Check if duration is approximately 0.1 seconds (allow 0.05-0.2 range)
if awk "BEGIN {exit !($DURATION >= 0.05 && $DURATION <= 0.3)}"; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}✓${NC} get_duration calculates duration correctly (${DURATION}s)"
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}✗${NC} get_duration calculates duration correctly"
    echo -e "  ${YELLOW}Expected range:${NC} 0.05-0.3s"
    echo -e "  ${YELLOW}Actual:${NC} ${DURATION}s"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Summary
echo
echo "======================================"
echo "Test Summary"
echo "======================================"
echo "Tests run: $TESTS_RUN"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"
    exit 1
else
    echo "All tests passed!"
    exit 0
fi
