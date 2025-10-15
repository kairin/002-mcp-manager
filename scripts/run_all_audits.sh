#!/usr/bin/env bash
# Orchestrator script to run all project health audits
# Executes all modular audit scripts in sequence
# Fails immediately if any audit fails

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_DIR="$SCRIPT_DIR/audit"

echo "========================================="
echo "   MCP Manager - Project Health Audit"
echo "========================================="
echo ""

# Track overall status
all_passed=true

# Function to run an audit and handle its result
run_audit() {
    local audit_script="$1"
    local audit_name="$2"

    echo "----------------------------------------"
    echo "Running: $audit_name"
    echo "----------------------------------------"

    if bash "$audit_script"; then
        echo ""
    else
        echo ""
        echo "❌ AUDIT FAILED: $audit_name"
        echo "Fix the issues above before proceeding."
        echo ""
        all_passed=false
        return 1
    fi
}

# Run all audits in sequence
# Order matters: fundamental checks first, then higher-level checks

echo "Phase 1: Python Package Management"
run_audit "$AUDIT_DIR/check_pip_usage.sh" "UV-First Policy Check" || true

echo ""
echo "Phase 2: Dependency Health"
run_audit "$AUDIT_DIR/check_outdated.sh" "Outdated Dependencies Check" || true

echo ""
echo "Phase 3: Repository Organization"
run_audit "$AUDIT_DIR/find_root_files.sh" "Root Directory Cleanliness" || true

echo ""
echo "Phase 4: MCP Configuration"
# Run Python script if it exists
if [[ -f "$AUDIT_DIR/check_mcp_configs.py" ]]; then
    echo "----------------------------------------"
    echo "Running: MCP Config Cross-Platform Check"
    echo "----------------------------------------"
    if python3 "$AUDIT_DIR/check_mcp_configs.py"; then
        echo ""
    else
        echo ""
        echo "❌ AUDIT FAILED: MCP Config Cross-Platform Check"
        echo "Fix the issues above before proceeding."
        echo ""
        all_passed=false
    fi
fi

echo "========================================="
if $all_passed; then
    echo "✅ All audits PASSED"
    echo "========================================="
    exit 0
else
    echo "❌ Some audits FAILED"
    echo "========================================="
    echo ""
    echo "Please fix the issues reported above and try again."
    exit 1
fi
