#!/usr/bin/env bash
# Validator Library for Local CI/CD Pipeline
# Provides validation functions for environment, dependencies, and secrets
# See: specs/001-local-cicd-astro-site/data-model.md Entity 2

set -euo pipefail

# validate_dependency: Check if a command exists and meets version requirements
# Args:
#   $1 - command name
#   $2 - minimum version (optional, format: "X.Y" or "X.Y.Z")
# Returns: 0 if valid, 1 if invalid
validate_dependency() {
    local cmd="$1"
    local min_version="${2:-}"

    if ! command -v "$cmd" &> /dev/null; then
        echo "ERROR: $cmd is not installed" >&2
        return 1
    fi

    if [ -n "$min_version" ]; then
        local current_version
        case "$cmd" in
            node)
                current_version=$(node --version | sed 's/v//')
                ;;
            npm)
                current_version=$(npm --version)
                ;;
            jq)
                current_version=$(jq --version | sed 's/jq-//')
                ;;
            bash)
                current_version=$(bash --version | head -1 | grep -oP '\d+\.\d+\.\d+')
                ;;
            *)
                # Generic version extraction
                current_version=$($cmd --version 2>&1 | grep -oP '\d+\.\d+(\.\d+)?' | head -1)
                ;;
        esac

        if ! version_compare "$current_version" "$min_version"; then
            echo "ERROR: $cmd version $current_version < $min_version (required)" >&2
            return 1
        fi
    fi

    return 0
}

# version_compare: Compare two version strings
# Args:
#   $1 - current version (e.g., "18.16.0")
#   $2 - minimum version (e.g., "18.0")
# Returns: 0 if current >= minimum, 1 otherwise
version_compare() {
    local current="$1"
    local minimum="$2"

    # Normalize versions to same length
    IFS='.' read -ra current_parts <<< "$current"
    IFS='.' read -ra minimum_parts <<< "$minimum"

    # Compare each part
    for i in "${!minimum_parts[@]}"; do
        local curr_part="${current_parts[$i]:-0}"
        local min_part="${minimum_parts[$i]}"

        if [ "$curr_part" -lt "$min_part" ]; then
            return 1
        elif [ "$curr_part" -gt "$min_part" ]; then
            return 0
        fi
    done

    return 0
}

# validate_env: Check if required environment variables are set
# Args:
#   $1 - variable name
#   $2 - allowed values (comma-separated, optional)
# Returns: 0 if valid, 1 if invalid
validate_env() {
    local var_name="$1"
    local allowed_values="${2:-}"

    if [ -z "${!var_name:-}" ]; then
        echo "ERROR: Environment variable $var_name is not set" >&2
        return 1
    fi

    if [ -n "$allowed_values" ]; then
        local value="${!var_name}"
        if [[ ! ",$allowed_values," =~ ",$value," ]]; then
            echo "ERROR: $var_name='$value' not in allowed values: $allowed_values" >&2
            return 1
        fi
    fi

    return 0
}

# validate_file_exists: Check if file exists
# Args:
#   $1 - file path
# Returns: 0 if exists, 1 if not
validate_file_exists() {
    local file_path="$1"

    if [ ! -f "$file_path" ]; then
        echo "ERROR: File not found: $file_path" >&2
        return 1
    fi

    return 0
}

# validate_directory_exists: Check if directory exists
# Args:
#   $1 - directory path
# Returns: 0 if exists, 1 if not
validate_directory_exists() {
    local dir_path="$1"

    if [ ! -d "$dir_path" ]; then
        echo "ERROR: Directory not found: $dir_path" >&2
        return 1
    fi

    return 0
}

# Secret detection patterns from data-model.md Entity 2
# These are basic patterns - Gitleaks provides comprehensive detection

# detect_github_token: Check for GitHub token patterns
# Args:
#   $1 - string to check
# Returns: 0 if no token found, 1 if token detected
detect_github_token() {
    local text="$1"

    if echo "$text" | grep -qE 'gh[ps]_[A-Za-z0-9]{36,}'; then
        echo "WARNING: GitHub token pattern detected" >&2
        return 1
    fi

    return 0
}

# detect_api_key: Check for generic API key patterns
# Args:
#   $1 - string to check
# Returns: 0 if no key found, 1 if key detected
detect_api_key() {
    local text="$1"

    if echo "$text" | grep -qE 'sk_live_[A-Za-z0-9]{24,}'; then
        echo "WARNING: API key pattern detected" >&2
        return 1
    fi

    return 0
}

# detect_aws_key: Check for AWS secret key patterns
# Args:
#   $1 - string to check
# Returns: 0 if no key found, 1 if key detected
detect_aws_key() {
    local text="$1"

    if echo "$text" | grep -qE 'AWS_SECRET_ACCESS_KEY.*[A-Za-z0-9/+=]{40}'; then
        echo "WARNING: AWS secret key pattern detected" >&2
        return 1
    fi

    return 0
}

# detect_private_key: Check for private key patterns
# Args:
#   $1 - string to check
# Returns: 0 if no key found, 1 if key detected
detect_private_key() {
    local text="$1"

    if echo "$text" | grep -qE 'BEGIN.*PRIVATE KEY'; then
        echo "WARNING: Private key pattern detected" >&2
        return 1
    fi

    return 0
}

# validate_no_secrets: Run all secret detection checks
# Args:
#   $1 - string to check
# Returns: 0 if no secrets found, 1 if secrets detected
validate_no_secrets() {
    local text="$1"
    local secrets_found=0

    detect_github_token "$text" || secrets_found=1
    detect_api_key "$text" || secrets_found=1
    detect_aws_key "$text" || secrets_found=1
    detect_private_key "$text" || secrets_found=1

    return $secrets_found
}

# Feature 002 - US8: Validate constitution file exists (T051)
# Check if .specify/memory/constitution.md exists (optional check for SpecKit projects)
# Args:
#   $1 - project root path
# Returns: 0 always (non-blocking check), prints status to stdout
validate_constitution_file() {
    local project_root="$1"
    local constitution_file="$project_root/.specify/memory/constitution.md"

    if [[ -f "$constitution_file" ]]; then
        echo "found"
    else
        echo "missing"
    fi

    return 0
}

# Guard: block unintended changes to scripts/mcp/mcp-profile unless commit message opts-in
# Returns 0 if allowed or not applicable, 1 if blocked
validate_mcp_profile_update_guard() {
    local project_root="${1:-$(pwd)}"
    if ! git -C "$project_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo "not-a-git-repo"
        return 0
    fi
    # If no commits yet, allow
    if ! git -C "$project_root" rev-parse HEAD >/dev/null 2>&1; then
        return 0
    fi
    local last_msg
    last_msg=$(git -C "$project_root" log -1 --pretty=%B 2>/dev/null || echo "")
    local changed
    changed=$(git -C "$project_root" diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null | grep -E '^scripts/mcp/mcp-profile$' || true)
    if [ -n "$changed" ]; then
        if ! grep -qi "allow-mcp-profile-update" <<<"$last_msg"; then
            return 1
        fi
    fi
    return 0
}

# Export functions for use in other scripts
export -f validate_dependency
export -f version_compare
export -f validate_env
export -f validate_file_exists
export -f validate_directory_exists
export -f detect_github_token
export -f detect_api_key
export -f detect_aws_key
export -f detect_private_key
export -f validate_no_secrets
export -f validate_constitution_file
export -f validate_mcp_profile_update_guard
