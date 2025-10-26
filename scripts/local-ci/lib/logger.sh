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

# --- Functions ---

# Function: get_repo_root
# Purpose: Gets the root directory of the Git repository.
# Returns: The absolute path to the repository root.
get_repo_root() {
    git rev-parse --show-toplevel 2>/dev/null || echo "$HOME/Apps/002-mcp-manager"
}

# Function: get_source_context
# Purpose: Extracts the source file, line number, and function name from the Bash call stack.
#          This provides context for log messages.
# Returns: A string in the format "source_file|line_number|function_name".
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

# Function: log_json
# Purpose: Outputs a structured JSON log entry. This is the core logging function.
# Arguments:
#   $1 - level: The log level (info, success, warn, error).
#   $2 - step_name: The name of the pipeline step.
#   $3 - message: A human-readable log message.
#   $4 - run_id (optional): The unique ID for the pipeline run.
#   $5 - duration_ms (optional): The duration of the step in milliseconds.
#   $6 - exitCode (optional): The exit code of a command.
#   $7 - error (optional): A JSON string with error details.
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

# Function: log_info
# Purpose: A convenience function for logging informational messages.
# Arguments: See log_json for argument details.
log_info() {
    log_json "info" "$1" "$2" "${3:-${RUN_ID:-}}" "${4:-}" "${5:-}" "${6:-}"
}

# Function: log_success
# Purpose: A convenience function for logging success messages.
# Arguments: See log_json for argument details.
log_success() {
    log_json "success" "$1" "$2" "${3:-${RUN_ID:-}}" "${4:-}" "${5:-}" "${6:-}"
}

# Function: log_warn
# Purpose: A convenience function for logging warning messages.
# Arguments: See log_json for argument details.
log_warn() {
    log_json "warn" "$1" "$2" "${3:-${RUN_ID:-}}" "${4:-}" "${5:-}" "${6:-}"
}

# Function: log_error
# Purpose: A convenience function for logging error messages.
# Arguments: See log_json for argument details.
log_error() {
    log_json "error" "$1" "$2" "${3:-${RUN_ID:-}}" "${4:-}" "${5:-}" "${6:-}"
}

# Function: get_duration
# Purpose: Calculates the duration between two timestamps.
# Arguments:
#   $1 - start_time: The start time in seconds since the epoch.
#   $2 - end_time (optional): The end time in seconds since the epoch. Defaults to the current time.
# Returns: The duration in seconds as a float.
get_duration() {
    local start="$1"
    local end="${2:-$(date +%s.%N)}"
    echo "$end - $start" | bc -l | awk '{printf "%.1f", $0}'
}

# --- Exports ---
# Export functions for use in other scripts.
export -f get_repo_root
export -f get_source_context
export -f log_json
export -f log_info
export -f log_success
export -f log_warn
export -f log_error
export -f get_duration
