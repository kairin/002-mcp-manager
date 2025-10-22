#!/bin/bash
# .github/scripts/validate-workflow.sh
# Pre-commit validation for GitHub Actions workflows
# Prevents syntax errors from reaching production

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo "🔍 Validating GitHub Actions Workflows..."
echo ""

# Test 1: YAML Syntax Validation
echo "📝 Test 1: YAML Syntax Validation"
if ! command -v yamllint &> /dev/null; then
  echo "${YELLOW}⚠️  yamllint not installed (optional but recommended)${NC}"
  WARNINGS=$((WARNINGS + 1))
else
  if yamllint .github/workflows/*.yml 2>&1; then
    echo "${GREEN}✅ All workflow files have valid YAML syntax${NC}"
  else
    echo "${RED}❌ YAML syntax errors found${NC}"
    ERRORS=$((ERRORS + 1))
  fi
fi
echo ""

# Test 2: jq/Shell Escaping Check
echo "📝 Test 2: jq/Shell Variable Escaping Check"
ESCAPING_ISSUES=0

for file in .github/workflows/*.yml; do
  # Check for problematic patterns: $(( inside jq calls
  if grep -E 'jq.*--arg.*\$\(\(' "$file" &>/dev/null; then
    echo "${RED}❌ Found potential jq escaping issue in $file:${NC}"
    grep -n 'jq.*--arg.*\$\(\(' "$file" || true
    ESCAPING_ISSUES=$((ESCAPING_ISSUES + 1))
  fi
  
  # Check for unescaped ${{ in jq context
  if grep -E "jq.*\\\$\{\{" "$file" &>/dev/null; then
    echo "${RED}❌ Found potential GitHub context escaping issue in $file:${NC}"
    grep -n "jq.*\${{" "$file" || true
    ESCAPING_ISSUES=$((ESCAPING_ISSUES + 1))
  fi
done

if [ $ESCAPING_ISSUES -eq 0 ]; then
  echo "${GREEN}✅ No jq/shell escaping issues detected${NC}"
else
  echo "${RED}❌ Found $ESCAPING_ISSUES escaping issues${NC}"
  ERRORS=$((ERRORS + 1))
fi
echo ""

# Test 3: Shell Script Syntax Check
echo "📝 Test 3: Shell Script Syntax Validation"
SHELL_ERRORS=0

find .github/scripts -name "*.sh" -type f 2>/dev/null | while read -r script; do
  if ! bash -n "$script" 2>/dev/null; then
    echo "${RED}❌ Shell syntax error in $script:${NC}"
    bash -n "$script" || true
    SHELL_ERRORS=$((SHELL_ERRORS + 1))
  fi
done

if [ $SHELL_ERRORS -eq 0 ]; then
  echo "${GREEN}✅ All shell scripts have valid syntax${NC}"
else
  echo "${RED}❌ Found $SHELL_ERRORS shell syntax errors${NC}"
  ERRORS=$((ERRORS + 1))
fi
echo ""

# Test 4: Common Mistake Detection
echo "📝 Test 4: Common Workflow Mistakes"
MISTAKES=0

for file in .github/workflows/*.yml; do
  # Check for missing 'if: success()' after important steps
  if grep -q "needs:" "$file" && ! grep -q "if: success()" "$file"; then
    echo "${YELLOW}⚠️  $file uses 'needs:' but no 'if: success()' checks${NC}"
    WARNINGS=$((WARNINGS + 1))
  fi
  
  # Check for hardcoded absolute paths (should use workspace)
  if grep -E "run:.*\/home\/|run:.*\/root\/" "$file" &>/dev/null; then
    echo "${RED}❌ Found hardcoded absolute paths in $file${NC}"
    MISTAKES=$((MISTAKES + 1))
  fi
  
  # Check for missing set -euo pipefail in multi-line scripts
  if grep -A2 "run: |" "$file" | grep -v "set -euo pipefail" &>/dev/null; then
    echo "${YELLOW}⚠️  Multi-line script in $file should start with 'set -euo pipefail'${NC}"
    WARNINGS=$((WARNINGS + 1))
  fi
done

if [ $MISTAKES -eq 0 ]; then
  echo "${GREEN}✅ No common workflow mistakes detected${NC}"
else
  echo "${RED}❌ Found $MISTAKES common mistakes${NC}"
  ERRORS=$((ERRORS + 1))
fi
echo ""

# Test 5: Variable Consistency Check
echo "📝 Test 5: Variable Reference Consistency"
VAR_ISSUES=0

for file in .github/workflows/*.yml; do
  # Check that ${{ }} is used for GitHub context
  if grep -E "github\.[a-z_]+\)" "$file" &>/dev/null; then
    echo "${YELLOW}⚠️  $file accesses github.* without \${{ }} - may not work in shell${NC}"
    VAR_ISSUES=$((VAR_ISSUES + 1))
  fi
done

if [ $VAR_ISSUES -eq 0 ]; then
  echo "${GREEN}✅ All variable references look correct${NC}"
else
  echo "${YELLOW}⚠️  Found $VAR_ISSUES potential variable reference issues${NC}"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Validation Summary:"
echo "   Errors:   $ERRORS"
echo "   Warnings: $WARNINGS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ERRORS -eq 0 ]; then
  echo "${GREEN}✅ All validation tests passed!${NC}"
  exit 0
else
  echo "${RED}❌ Validation failed with $ERRORS errors${NC}"
  echo "Please fix the issues above before committing."
  exit 1
fi
