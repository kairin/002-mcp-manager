#!/bin/bash
# Local CI/CD Pipeline for MCP Manager
# Runs all checks and builds before allowing push to remote

set -e  # Exit on error

echo "🚀 MCP Manager Local CI/CD Pipeline"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step counter
STEP=0
TOTAL_STEPS=8

function run_step() {
    STEP=$((STEP + 1))
    echo -e "${YELLOW}[$STEP/$TOTAL_STEPS]${NC} $1"
}

function success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check branch naming
run_step "Checking branch naming convention..."
./scripts/check-branch-name.sh || error "Branch naming check failed"
success "Branch name valid"

# Python formatting
run_step "Running Python formatter (black)..."
black src/ tests/ --check || {
    echo "Auto-formatting code..."
    black src/ tests/
    success "Code formatted"
}

# Python linting
run_step "Running Python linter (ruff)..."
ruff check src/ tests/ || error "Linting failed"
success "Linting passed"

# Python type checking
run_step "Running type checker (mypy)..."
mypy src/ || error "Type checking failed"
success "Type checking passed"

# Python tests
run_step "Running Python tests..."
python -m pytest tests/ --cov=mcp_manager --cov-fail-under=80 || error "Tests failed or coverage below 80%"
success "Tests passed with coverage >80%"

# Astro type checking
run_step "Running Astro type checking..."
npm run check || error "Astro type checking failed"
success "Astro types valid"

# Build Astro site
run_step "Building Astro website..."
npm run build || error "Astro build failed"
success "Website built to ./docs"

# Verify build outputs
run_step "Verifying build outputs..."
if [ ! -d "./docs" ]; then
    error "docs directory not found"
fi

if [ ! -f "./docs/.nojekyll" ]; then
    error ".nojekyll file not created"
fi

if [ ! -d "./docs/_astro" ]; then
    error "_astro assets directory not found"
fi

FILE_COUNT=$(find ./docs -type f | wc -l)
success "Build verified: $FILE_COUNT files in docs/"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ All checks passed! Ready to push.${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "1. git add -A"
echo "2. git commit -m 'Your message'"
echo "3. git push origin <branch>"
echo "4. GitHub Actions will deploy to GitHub Pages"