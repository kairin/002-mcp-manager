#!/usr/bin/env bash
# Validator Library for Local CI/CD Pipeline
# Provides validation functions for environment, dependencies, and secrets
# See: specs/001-local-cicd-astro-site/data-model.md Entity 2

set -euo pipefail

# --- Functions ---

# Function: validate_dependency
# Purpose: Checks if a command exists and meets a minimum version requirement.
# Arguments:
#   $1 - command_name: The name of the command to validate.
#   $2 - minimum_version (optional): The minimum required version (e.g., "18.0").
# Returns: 0 if the dependency is valid, 1 otherwise.
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

# Function: version_compare
# Purpose: Compares two version strings to see if the current version meets the minimum requirement.
# Arguments:
#   $1 - current_version: The version to check (e.g., "18.16.0").
#   $2 - minimum_version: The minimum required version (e.g., "18.0").
# Returns: 0 if the current version is greater than or equal to the minimum, 1 otherwise.
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

# Function: validate_env
# Purpose: Checks if a required environment variable is set and optionally validates its value.
# Arguments:
#   $1 - variable_name: The name of the environment variable.
#   $2 - allowed_values (optional): A comma-separated string of allowed values.
# Returns: 0 if the environment variable is valid, 1 otherwise.
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

# Function: validate_file_exists
# Purpose: Checks if a file exists at the given path.
# Arguments:
#   $1 - file_path: The path to the file.
# Returns: 0 if the file exists, 1 otherwise.
validate_file_exists() {
    local file_path="$1"

    if [ ! -f "$file_path" ]; then
        echo "ERROR: File not found: $file_path" >&2
        return 1
    fi

    return 0
}

# Function: validate_directory_exists
# Purpose: Checks if a directory exists at the given path.
# Arguments:
#   $1 - directory_path: The path to the directory.
# Returns: 0 if the directory exists, 1 otherwise.
validate_directory_exists() {
    local dir_path="$1"

    if [ ! -d "$dir_path" ]; then
        echo "ERROR: Directory not found: $dir_path" >&2
        return 1
    fi

    return 0
}

# --- Secret Detection Functions ---
# These functions provide basic secret detection. For comprehensive scanning,
# a dedicated tool like Gitleaks is recommended.

# Function: detect_github_token
# Purpose: Checks for a GitHub token pattern in a given string.
# Arguments:
#   $1 - text: The string to check.
# Returns: 0 if no token is found, 1 otherwise.
detect_github_token() {
    local text="$1"

    if echo "$text" | grep -qE 'gh[ps]_[A-Za-z0-9]{36,}'; then
        echo "WARNING: GitHub token pattern detected" >&2
        return 1
    fi

    return 0
}

# Function: detect_api_key
# Purpose: Checks for a generic API key pattern in a given string.
# Arguments:
#   $1 - text: The string to check.
# Returns: 0 if no key is found, 1 otherwise.
detect_api_key() {
    local text="$1"

    if echo "$text" | grep -qE 'sk_live_[A-Za-z0-9]{24,}'; then
        echo "WARNING: API key pattern detected" >&2
        return 1
    fi

    return 0
}

# Function: detect_aws_key
# Purpose: Checks for an AWS secret key pattern in a given string.
# Arguments:
#   $1 - text: The string to check.
# Returns: 0 if no key is found, 1 otherwise.
detect_aws_key() {
    local text="$1"

    if echo "$text" | grep -qE 'AWS_SECRET_ACCESS_KEY.*[A-Za-z0-9/+=]{40}'; then
        echo "WARNING: AWS secret key pattern detected" >&2
        return 1
    fi

    return 0
}

# Function: detect_private_key
# Purpose: Checks for a private key pattern in a given string.
# Arguments:
#   $1 - text: The string to check.
# Returns: 0 if no key is found, 1 otherwise.
detect_private_key() {
    local text="$1"

    if echo "$text" | grep -qE 'BEGIN.*PRIVATE KEY'; then
        echo "WARNING: Private key pattern detected" >&2
        return 1
    fi

    return 0
}

# Function: validate_no_secrets
# Purpose: Runs all secret detection checks on a given string.
# Arguments:
#   $1 - text: The string to check.
# Returns: 0 if no secrets are found, 1 otherwise.
validate_no_secrets() {
    local text="$1"
    local secrets_found=0

    detect_github_token "$text" || secrets_found=1
    detect_api_key "$text" || secrets_found=1
    detect_aws_key "$text" || secrets_found=1
    detect_private_key "$text" || secrets_found=1

    return $secrets_found
}

# --- Project-Specific Validations ---

# Function: validate_constitution_file
# Purpose: Checks for the existence of the constitution.md file in SpecKit projects.
#          This is an optional, non-blocking check.
# Arguments:
#   $1 - project_root: The root directory of the project.
# Returns: 0 always. Prints "found" or "missing" to stdout.
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

# Function: validate_mcp_profile_update_guard
# Purpose: Prevents unintended changes to the mcp-profile script unless
#          the commit message includes a specific opt-in flag.
# Returns: 0 if the update is allowed, 1 if it is blocked.
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

# --- Exports ---
# Export functions for use in other scripts.
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
