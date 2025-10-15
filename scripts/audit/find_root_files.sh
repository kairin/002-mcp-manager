#!/usr/bin/env bash
# Audit script to check for misplaced files in repository root
# Identifies files that should be organized into subdirectories
# Exit code: 0 if root is clean, 1 if misplaced files found

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "Checking for misplaced files in repository root..."

# Define allowed files in root directory
allowed_files=(
    ".gitignore"
    ".git"
    "README.md"
    "LICENSE"
    "pyproject.toml"
    "package.json"
    "package-lock.json"
    "astro.config.mjs"
    "tsconfig.json"
    ".python-version"
    "uv.toml"
    ".pre-commit-config.yaml"
    "CLAUDE.md"
    "IMPLEMENTATION-ORDER.md"
    "RENAMING-PLAN.md"
)

# Define allowed directories in root
allowed_dirs=(
    "src"
    "backend"
    "frontend"
    "tests"
    "docs"
    "specs"
    "scripts"
    "public"
    "node_modules"
    ".git"
    ".specify"
    ".github"
    ".venv"
    "venv"
    "dist"
    "build"
    "specs-backup-20251015"
)

# Find all items in root (excluding hidden files except those in allowed list)
misplaced_files=()

for item in *; do
    if [[ -f "$item" ]]; then
        # Check if file is in allowed list
        if [[ ! " ${allowed_files[@]} " =~ " ${item} " ]]; then
            # Check if it's a markdown file that might belong in docs/
            if [[ "$item" =~ \.md$ ]]; then
                misplaced_files+=("$item (should be in docs/ or docs/archive/)")
            else
                misplaced_files+=("$item")
            fi
        fi
    elif [[ -d "$item" ]]; then
        # Check if directory is in allowed list
        if [[ ! " ${allowed_dirs[@]} " =~ " ${item} " ]]; then
            misplaced_files+=("$item/ (unexpected directory)")
        fi
    fi
done

if [[ ${#misplaced_files[@]} -gt 0 ]]; then
    echo "❌ FAIL: Found misplaced files/directories in root:"
    printf '  - %s\n' "${misplaced_files[@]}"
    echo ""
    echo "Resolution: Move files to appropriate subdirectories:"
    echo "  - *.md files (status/completion) → docs/archive/"
    echo "  - Configuration files → maintain or document in README.md"
    echo "  - Temporary directories → add to .gitignore or remove"
    exit 1
fi

echo "✅ PASS: Repository root is clean and organized"
exit 0
