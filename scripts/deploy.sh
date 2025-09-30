#!/bin/bash
# MCP Manager - Local Deployment Script
# Complete local CI/CD workflow before pushing to GitHub

set -e

echo "🚀 MCP Manager Local Deployment Workflow"
echo "=========================================="

# Step 1: Clean and build
echo ""
echo "📦 Step 1: Building website..."
npm run build

# Step 2: Verify build
echo ""
echo "🔍 Step 2: Verifying build artifacts..."
test -f docs/index.html || { echo "❌ Missing docs/index.html"; exit 1; }
test -d docs/_astro || { echo "❌ Missing docs/_astro/"; exit 1; }
test -f docs/.nojekyll || { echo "❌ Missing docs/.nojekyll"; exit 1; }
echo "✅ All critical files verified"

# Step 3: Check git status
echo ""
echo "📊 Step 3: Checking git status..."
if [[ -z $(git status -s) ]]; then
    echo "✅ No changes to commit"
    exit 0
fi

git status -s

# Step 4: Stage changes
echo ""
echo "📝 Step 4: Staging changes..."
read -p "Stage all changes? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add .
    echo "✅ Changes staged"
else
    echo "⏭️  Skipping staging"
    exit 0
fi

# Step 5: Create commit
echo ""
echo "💾 Step 5: Creating commit..."
DATETIME=$(date +"%Y%m%d-%H%M%S")
read -p "Enter commit type (docs/feat/fix): " COMMIT_TYPE
read -p "Enter short description: " DESCRIPTION
BRANCH_NAME="${DATETIME}-${COMMIT_TYPE}-${DESCRIPTION}"

echo ""
echo "Branch: $BRANCH_NAME"
read -p "Enter commit message: " COMMIT_MSG

git checkout -b "$BRANCH_NAME"
git commit -m "$COMMIT_MSG

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ Commit created"

# Step 6: Push to remote
echo ""
echo "📤 Step 6: Pushing to remote..."
read -p "Push branch to remote? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push -u origin "$BRANCH_NAME"
    echo "✅ Branch pushed to remote"
else
    echo "⏭️  Skipping push - branch remains local"
    exit 0
fi

# Step 7: Merge to main
echo ""
echo "🔀 Step 7: Merging to main..."
read -p "Merge to main? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git checkout main
    git merge "$BRANCH_NAME" --no-ff -m "Merge branch '$BRANCH_NAME' into main"
    echo "✅ Merged to main (branch preserved)"
else
    echo "⏭️  Skipping merge - staying on feature branch"
    exit 0
fi

# Step 8: Push main
echo ""
echo "📤 Step 8: Pushing main to remote..."
read -p "Push main to remote? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    echo "✅ Main pushed to remote"

    # Wait for GitHub Pages
    echo ""
    echo "⏳ Waiting 30s for GitHub Pages deployment..."
    sleep 30

    # Verify deployment
    echo ""
    echo "🔍 Verifying GitHub Pages deployment..."
    HTTP_STATUS=$(curl -I https://kairin.github.io/mcp-manager/ 2>/dev/null | head -1 | awk '{print $2}')
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ GitHub Pages deployed successfully!"
        echo "🌐 Live at: https://kairin.github.io/mcp-manager/"
    else
        echo "⚠️  GitHub Pages status: HTTP $HTTP_STATUS"
        echo "💡 May need a few more minutes to deploy"
    fi
else
    echo "⏭️  Skipping push - main remains local"
fi

echo ""
echo "🎉 Deployment workflow complete!"
echo "=========================================="