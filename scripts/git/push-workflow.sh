#!/bin/bash
# Complete push workflow for MCP Manager
# Handles everything from branch creation to GitHub Pages deployment

set -e

echo "🚀 MCP Manager Push Workflow"
echo "============================="
echo ""

# Create timestamped branch
DATETIME=$(date +"%Y%m%d-%H%M%S")
echo "Select branch type:"
echo "1) feat    - New feature"
echo "2) fix     - Bug fix"
echo "3) docs    - Documentation"
echo "4) refactor - Code refactoring"
echo "5) test    - Tests"
echo "6) chore   - Maintenance"
read -p "Enter number (1-6): " TYPE_NUM

case $TYPE_NUM in
    1) TYPE="feat";;
    2) TYPE="fix";;
    3) TYPE="docs";;
    4) TYPE="refactor";;
    5) TYPE="test";;
    6) TYPE="chore";;
    *) echo "Invalid selection"; exit 1;;
esac

read -p "Enter short description (lowercase, hyphens): " DESC
BRANCH="${DATETIME}-${TYPE}-${DESC}"

echo "Creating branch: $BRANCH"
git checkout -b "$BRANCH"

# Run local CI
echo ""
echo "Running local CI/CD pipeline..."
./scripts/local-ci.sh

# Stage all changes
echo ""
echo "Staging changes..."
git add -A

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short

# Get commit message
echo ""
read -p "Enter commit message: " COMMIT_MSG

# Commit with co-author
git commit -m "$COMMIT_MSG

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
echo ""
echo "Pushing to remote..."
git push -u origin "$BRANCH"

# Merge to main
echo ""
read -p "Merge to main branch? (y/n): " MERGE
if [ "$MERGE" = "y" ]; then
    git checkout main
    git pull origin main
    git merge "$BRANCH" --no-ff -m "Merge branch '$BRANCH'"
    git push origin main
    echo "✅ Merged to main - GitHub Actions will deploy to GitHub Pages"
else
    echo "📌 Branch pushed. Create a PR when ready."
fi

echo ""
echo "✅ Workflow complete!"
echo ""
echo "📊 Status:"
echo "  - Branch: $BRANCH"
echo "  - Remote: origin/$BRANCH"
if [ "$MERGE" = "y" ]; then
    echo "  - Merged: ✓"
    echo "  - Deploy: https://kairin.github.io/mcp-manager (in progress)"
else
    echo "  - Next: Create PR on GitHub"
fi