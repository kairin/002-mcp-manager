#!/bin/bash
# Branch naming convention checker for MCP Manager
# Format: YYYYMMDD-HHMMSS-type-short-description

BRANCH=$(git branch --show-current)

# Skip check for main branch
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    exit 0
fi

# Pattern: YYYYMMDD-HHMMSS-type-description
PATTERN="^[0-9]{8}-[0-9]{6}-(feat|fix|docs|refactor|test|chore|style|perf)-[a-z0-9-]+$"

if ! echo "$BRANCH" | grep -qE "$PATTERN"; then
    echo "❌ Branch name '$BRANCH' doesn't match required format!"
    echo ""
    echo "Required format: YYYYMMDD-HHMMSS-type-short-description"
    echo "Examples:"
    echo "  20250923-143000-feat-mcp-server-manager"
    echo "  20250923-143515-fix-configuration-audit"
    echo "  20250923-144030-docs-api-reference"
    echo ""
    echo "Types: feat, fix, docs, refactor, test, chore, style, perf"
    exit 1
fi

echo "✅ Branch name '$BRANCH' is valid"