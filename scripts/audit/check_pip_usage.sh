#!/usr/bin/env bash
# Audit script to enforce uv-first policy for Python package management
# This script checks for any usage of 'pip' commands in the codebase
# Exit code: 0 if no violations found, 1 if pip usage detected

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "Checking for pip usage in codebase..."

# Search for standalone pip commands (not "uv pip") in files
# Excluding this audit script itself and node_modules
# Use negative lookbehind to exclude "uv pip" but catch standalone "pip"
violations=$(grep -rE '\bpip (install|freeze|list|show|uninstall|download)\b' \
    --include="*.py" \
    --include="*.sh" \
    --include="*.md" \
    --exclude-dir="node_modules" \
    --exclude-dir=".git" \
    --exclude-dir=".venv" \
    --exclude-dir="venv" \
    --exclude="check_pip_usage.sh" \
    . 2>/dev/null | grep -v "uv pip" || true)

if [[ -n "$violations" ]]; then
    echo "❌ FAIL: Found pip usage in the following locations:"
    echo "$violations"
    echo ""
    echo "Resolution: Replace 'pip' commands with 'uv pip' equivalents:"
    echo "  pip install <package>  →  uv pip install <package>"
    echo "  pip freeze             →  uv pip freeze"
    echo "  pip list               →  uv pip list"
    exit 1
fi

echo "✅ PASS: No pip usage found. All Python package management uses uv."
exit 0
