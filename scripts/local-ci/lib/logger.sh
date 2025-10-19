#!/usr/bin/env bash
# JSON Logging Library for Local CI/CD Pipeline
# Uses jq for guaranteed valid JSON output
# See: specs/001-local-cicd-astro-site/data-model.md Entity 1

set -euo pipefail

# Check jq is installed
if ! command -v jq &> /dev/null; then
    echo '{"timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")'","level":"error","step":"init","message":"jq is not installed - required for JSON logging"}' >&2
    exit 4
fi

# log_json: Output structured JSON log entry
# Args:
#   $1 - level: info|success|warn|error
#   $2 - step: init|env-check|lint|test-unit|test-integration|test-e2e|build|cleanup|complete
#   $3 - message: Human-readable description
#   $4 - duration (optional): Seconds (float)
#   $5 - exitCode (optional): Command exit code
#   $6 - error (optional): JSON string with error details
log_json() {
    local level="$1"
    local step="$2"
    local message="$3"
    local duration="${4:-}"
    local exit_code="${5:-}"
    local error="${6:-}"

    # Generate ISO 8601 timestamp with milliseconds
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

    # Build JSON using jq to guarantee valid output
    jq -n \
        --arg timestamp "$timestamp" \
        --arg level "$level" \
        --arg step "$step" \
        --arg message "$message" \
        --arg duration "$duration" \
        --arg exitCode "$exit_code" \
        --arg error "$error" \
        '{
            timestamp: $timestamp,
            level: $level,
            step: $step,
            message: $message
        } +
        (if $duration != "" then {duration: ($duration | tonumber)} else {} end) +
        (if $exitCode != "" then {exitCode: ($exitCode | tonumber)} else {} end) +
        (if $error != "" then {error: ($error | fromjson)} else {} end)'
}

# log_info: Convenience function for info level
log_info() {
    log_json "info" "$1" "$2" "${3:-}" "${4:-}" "${5:-}"
}

# log_success: Convenience function for success level
log_success() {
    log_json "success" "$1" "$2" "${3:-}" "${4:-}" "${5:-}"
}

# log_warn: Convenience function for warn level
log_warn() {
    log_json "warn" "$1" "$2" "${3:-}" "${4:-}" "${5:-}"
}

# log_error: Convenience function for error level
log_error() {
    log_json "error" "$1" "$2" "${3:-}" "${4:-}" "${5:-}"
}

# get_duration: Calculate duration between two timestamps
# Args:
#   $1 - start time (seconds since epoch)
#   $2 - end time (seconds since epoch, defaults to now)
# Returns: Duration in seconds (float)
get_duration() {
    local start="$1"
    local end="${2:-$(date +%s.%N)}"
    echo "$end - $start" | bc -l | awk '{printf "%.1f", $0}'
}

# Export functions for use in other scripts
export -f log_json
export -f log_info
export -f log_success
export -f log_warn
export -f log_error
export -f get_duration
