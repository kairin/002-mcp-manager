#!/usr/bin/env bash
# Audit script to check for outdated dependencies
# Checks both Python (via uv) and JavaScript (via npm) dependencies
# Exit code: 0 if all dependencies up-to-date, 1 if outdated packages found

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "Checking for outdated dependencies..."

exit_code=0

# Check Python dependencies via uv
echo ""
echo "Checking Python dependencies (uv pip list --outdated)..."
if command -v uv &> /dev/null; then
    outdated_python=$(uv pip list --outdated 2>/dev/null || echo "")
    if [[ -n "$outdated_python" ]]; then
        echo "❌ FAIL: Found outdated Python packages:"
        echo "$outdated_python"
        echo ""
        echo "Resolution: Update pyproject.toml and run 'uv pip sync'"
        exit_code=1
    else
        echo "✅ PASS: All Python packages up-to-date"
    fi
else
    echo "⚠️  WARNING: uv not found, skipping Python dependency check"
fi

# Check JavaScript dependencies via npm
echo ""
echo "Checking JavaScript dependencies (npm outdated)..."
if [[ -f "package.json" ]] && command -v npm &> /dev/null; then
    outdated_npm=$(npm outdated 2>/dev/null || echo "")
    if [[ -n "$outdated_npm" ]]; then
        echo "❌ FAIL: Found outdated npm packages:"
        echo "$outdated_npm"
        echo ""
        echo "Resolution: Update package.json and run 'npm install'"
        exit_code=1
    else
        echo "✅ PASS: All npm packages up-to-date"
    fi
elif [[ ! -f "package.json" ]]; then
    echo "ℹ️  INFO: No package.json found, skipping npm dependency check"
else
    echo "⚠️  WARNING: npm not found, skipping JavaScript dependency check"
fi

if [[ $exit_code -eq 0 ]]; then
    echo ""
    echo "✅ All dependencies are up-to-date"
fi

exit $exit_code
