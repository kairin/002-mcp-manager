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

# Feature 002: Get repository root for relative paths
get_repo_root() {
    git rev-parse --show-toplevel 2>/dev/null || echo "$HOME/Apps/002-mcp-manager"
}

# Feature 002: Extract source context from bash call stack
# Returns: source_file|line_number|function_name
get_source_context() {
    local repo_root
    repo_root=$(get_repo_root)

    # Call stack: caller_script → log_info/log_error/etc → log_json → get_source_context
    # From log_json perspective:
    #   BASH_SOURCE[0] = logger.sh (get_source_context)
    #   BASH_SOURCE[1] = logger.sh (log_json)
    #   BASH_SOURCE[2] = logger.sh (log_info/log_error/etc convenience function)
    #   BASH_SOURCE[3] = run.sh/validator.sh (actual caller we want)
    # From convenience function perspective:
    #   BASH_SOURCE[0] = logger.sh (get_source_context)
    #   BASH_SOURCE[1] = logger.sh (log_json)
    #   BASH_SOURCE[2] = logger.sh (convenience function)
    #   BASH_SOURCE[3] = run.sh (actual caller)
    #   BASH_LINENO[2] = line in run.sh that called log_info
    #   FUNCNAME[3] = function in run.sh

    local source_file="${BASH_SOURCE[3]:-unknown}"
    local line_number="${BASH_LINENO[2]:-0}"
    local function_name="${FUNCNAME[3]:-main}"

    # Convert absolute path to relative path from repo root
    if [[ "$source_file" == "$repo_root"* ]]; then
        source_file="${source_file#$repo_root/}"
    fi

    echo "${source_file}|${line_number}|${function_name}"
}

# log_json: Output structured JSON log entry with source context (Feature 002: US4)
# Args:
#   $1 - level: info|success|warn|error
#   $2 - step_name: init|env-check|lint|test-unit|test-integration|test-e2e|build|cleanup|complete
#   $3 - message: Human-readable description
#   $4 - run_id (optional): Correlation ID (format: run-YYYYMMDD-HHMMSS-{6char})
#   $5 - duration_ms (optional): Duration in milliseconds
#   $6 - exitCode (optional): Command exit code
#   $7 - error (optional): JSON string with error details
log_json() {
    local level="$1"
    local step_name="$2"
    local message="$3"
    local run_id="${4:-}"
    local duration_ms="${5:-}"
    local exit_code="${6:-}"
    local error="${7:-}"

    # Feature 002: Extract source context (T029)
    local context
    context=$(get_source_context)
    IFS='|' read -r source_file line_number function_name <<< "$context"

    # Generate ISO 8601 timestamp with milliseconds
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

    # Build JSON using jq to guarantee valid output (Feature 002: Enhanced schema)
    jq -n \
        --arg timestamp "$timestamp" \
        --arg level "$level" \
        --arg message "$message" \
        --arg run_id "$run_id" \
        --arg source_file "$source_file" \
        --argjson line_number "$line_number" \
        --arg function_name "$function_name" \
        --arg step_name "$step_name" \
        --arg duration_ms "$duration_ms" \
        --arg exitCode "$exit_code" \
        --arg error "$error" \
        '{
            timestamp: $timestamp,
            level: $level,
            message: $message,
            source_file: $source_file,
            line_number: $line_number,
            function_name: $function_name,
            step_name: $step_name
        } +
        (if $run_id != "" then {run_id: $run_id} else {} end) +
        (if $duration_ms != "" then {duration_ms: ($duration_ms | tonumber)} else {} end) +
        (if $exitCode != "" then {exitCode: ($exitCode | tonumber)} else {} end) +
        (if $error != "" then {error: ($error | fromjson)} else {} end)'
}

# log_info: Convenience function for info level (Feature 002: US6 - Auto-inject RUN_ID)
# Args: $1=step_name, $2=message, $3=run_id (opt, defaults to $RUN_ID), $4=duration_ms (opt), $5=exitCode (opt), $6=error (opt)
log_info() {
    log_json "info" "$1" "$2" "${3:-${RUN_ID:-}}" "${4:-}" "${5:-}" "${6:-}"
}

# log_success: Convenience function for success level (Feature 002: US6 - Auto-inject RUN_ID)
# Args: $1=step_name, $2=message, $3=run_id (opt, defaults to $RUN_ID), $4=duration_ms (opt), $5=exitCode (opt), $6=error (opt)
log_success() {
    log_json "success" "$1" "$2" "${3:-${RUN_ID:-}}" "${4:-}" "${5:-}" "${6:-}"
}

# log_warn: Convenience function for warn level (Feature 002: US6 - Auto-inject RUN_ID)
# Args: $1=step_name, $2=message, $3=run_id (opt, defaults to $RUN_ID), $4=duration_ms (opt), $5=exitCode (opt), $6=error (opt)
log_warn() {
    log_json "warn" "$1" "$2" "${3:-${RUN_ID:-}}" "${4:-}" "${5:-}" "${6:-}"
}

# log_error: Convenience function for error level (Feature 002: US6 - Auto-inject RUN_ID)
# Args: $1=step_name, $2=message, $3=run_id (opt, defaults to $RUN_ID), $4=duration_ms (opt), $5=exitCode (opt), $6=error (opt)
log_error() {
    log_json "error" "$1" "$2" "${3:-${RUN_ID:-}}" "${4:-}" "${5:-}" "${6:-}"
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

# Export functions for use in other scripts (Feature 002: Added new functions)
export -f get_repo_root
export -f get_source_context
export -f log_json
export -f log_info
export -f log_success
export -f log_warn
export -f log_error
export -f get_duration
