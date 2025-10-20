#!/usr/bin/env bash
# TUI for Local CI/CD Pipeline
# Interactive menu interface for scripts/local-ci/run.sh
# See: specs/001-local-cicd-astro-site/spec.md FR-006

set -euo pipefail

# Get script directory (works even if called from elsewhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CI_SCRIPT="$PROJECT_ROOT/scripts/local-ci/run.sh"
LOGS_DIR="$PROJECT_ROOT/logs"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if CI script exists
if [ ! -f "$CI_SCRIPT" ]; then
    echo -e "${RED}Error: CI/CD script not found at $CI_SCRIPT${NC}"
    exit 1
fi

# Main menu loop
main_menu() {
    while true; do
        clear
        echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}║${NC}  ${BLUE}Local CI/CD Pipeline - Interactive Menu${NC}                      ${CYAN}║${NC}"
        echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${GREEN}CI/CD Operations:${NC}"
        echo "  1) Run Full CI/CD Pipeline (lint + tests + build)"
        echo "  2) Run CI/CD (Skip Tests - faster)"
        echo "  3) Run CI/CD (Verbose Mode)"
        echo "  4) Run CI/CD (No Auto-Fix)"
        echo ""
        echo -e "${GREEN}Monitoring & Maintenance:${NC}"
        echo "  5) View Recent Logs"
        echo "  6) Check Environment"
        echo "  7) Clean Old Logs"
        echo ""
        echo -e "${GREEN}Help & Info:${NC}"
        echo "  8) Help & Documentation"
        echo "  9) Exit"
        echo ""
        echo -e "${CYAN}────────────────────────────────────────────────────────────────${NC}"

        read -p "$(echo -e ${BLUE}Select an option [1-9]: ${NC})" choice

        case $choice in
            1)
                run_full_pipeline
                ;;
            2)
                run_skip_tests
                ;;
            3)
                run_verbose
                ;;
            4)
                run_no_fix
                ;;
            5)
                view_logs
                ;;
            6)
                check_environment
                ;;
            7)
                clean_logs
                ;;
            8)
                show_help
                ;;
            9)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please select 1-9.${NC}"
                sleep 2
                ;;
        esac
    done
}

# Option 1: Run Full CI/CD Pipeline
run_full_pipeline() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}Running Full CI/CD Pipeline${NC}                                  ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}This will run: lint → unit tests → integration tests → e2e tests → build${NC}"
    echo ""

    "$CI_SCRIPT"
    exit_code=$?

    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ CI/CD Pipeline completed successfully!${NC}"
    else
        echo -e "${RED}✗ CI/CD Pipeline failed with exit code: $exit_code${NC}"
        case $exit_code in
            1)
                echo -e "${YELLOW}  Lint errors detected. Check logs for details.${NC}"
                ;;
            2)
                echo -e "${YELLOW}  Test failures detected. Check logs for details.${NC}"
                ;;
            3)
                echo -e "${YELLOW}  Build failed. Check logs for details.${NC}"
                ;;
            4)
                echo -e "${YELLOW}  Environment validation failed. Run option 6 to check.${NC}"
                ;;
        esac
    fi

    pause
}

# Option 2: Run CI/CD (Skip Tests)
run_skip_tests() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}Running CI/CD (Skip Tests)${NC}                                    ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}This will run: lint → build (skipping tests)${NC}"
    echo ""

    "$CI_SCRIPT" --skip-tests
    exit_code=$?

    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ CI/CD completed successfully (tests skipped)!${NC}"
    else
        echo -e "${RED}✗ CI/CD failed with exit code: $exit_code${NC}"
    fi

    pause
}

# Option 3: Run CI/CD (Verbose Mode)
run_verbose() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}Running CI/CD (Verbose Mode)${NC}                                  ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}This will show detailed output for all steps${NC}"
    echo ""

    "$CI_SCRIPT" --verbose
    exit_code=$?

    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ CI/CD completed successfully!${NC}"
    else
        echo -e "${RED}✗ CI/CD failed with exit code: $exit_code${NC}"
    fi

    pause
}

# Option 4: Run CI/CD (No Auto-Fix)
run_no_fix() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}Running CI/CD (No Auto-Fix)${NC}                                   ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}This will NOT auto-fix lint errors${NC}"
    echo ""

    "$CI_SCRIPT" --no-fix
    exit_code=$?

    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ CI/CD completed successfully!${NC}"
    else
        echo -e "${RED}✗ CI/CD failed with exit code: $exit_code${NC}"
        if [ $exit_code -eq 1 ]; then
            echo -e "${YELLOW}  Lint errors detected. Run option 1 to auto-fix.${NC}"
        fi
    fi

    pause
}

# Option 5: View Recent Logs
view_logs() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}Recent CI/CD Logs${NC}                                             ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ ! -d "$LOGS_DIR" ] || [ -z "$(ls -A "$LOGS_DIR" 2>/dev/null)" ]; then
        echo -e "${YELLOW}No logs found in $LOGS_DIR${NC}"
        pause
        return
    fi

    echo -e "${GREEN}Recent log files (newest first):${NC}"
    echo ""
    ls -lht "$LOGS_DIR"/*.json 2>/dev/null | head -10 | while read -r line; do
        echo "  $line"
    done
    echo ""

    read -p "$(echo -e ${BLUE}View a log file? [y/N]: ${NC})" view_choice

    if [[ "$view_choice" =~ ^[Yy]$ ]]; then
        latest_log=$(ls -t "$LOGS_DIR"/*.json 2>/dev/null | head -1)
        if [ -n "$latest_log" ]; then
            echo -e "${GREEN}Showing: $latest_log${NC}"
            echo ""
            if command -v jq &> /dev/null; then
                cat "$latest_log" | jq '.'
            else
                cat "$latest_log"
            fi
        fi
    fi

    pause
}

# Option 6: Check Environment
check_environment() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}Environment Check${NC}                                             ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Source validator to check dependencies
    if [ -f "$PROJECT_ROOT/scripts/local-ci/lib/validator.sh" ]; then
        source "$PROJECT_ROOT/scripts/local-ci/lib/validator.sh"

        echo -e "${GREEN}Checking dependencies...${NC}"
        echo ""

        deps=(
            "bash:5.0:Bash Shell"
            "jq:1.6:JSON Processor"
            "node:18.0:Node.js"
            "npm:9.0:NPM"
        )

        all_ok=true
        for dep in "${deps[@]}"; do
            IFS=':' read -r cmd min_ver name <<< "$dep"
            printf "  %-20s" "$name:"

            if validate_dependency "$cmd" "$min_ver" 2>/dev/null; then
                version=$($cmd --version 2>&1 | grep -oP '\d+\.\d+(\.\d+)?' | head -1)
                echo -e "${GREEN}✓${NC} $version"
            else
                echo -e "${RED}✗${NC} Not found or version < $min_ver"
                all_ok=false
            fi
        done

        echo ""
        if $all_ok; then
            echo -e "${GREEN}✓ All dependencies satisfied!${NC}"
        else
            echo -e "${YELLOW}⚠ Some dependencies need attention${NC}"
        fi
    else
        echo -e "${YELLOW}Validator script not found. Running basic checks...${NC}"
        echo ""

        for cmd in bash jq node npm; do
            printf "  %-20s" "$cmd:"
            if command -v "$cmd" &> /dev/null; then
                version=$($cmd --version 2>&1 | head -1)
                echo -e "${GREEN}✓${NC} $version"
            else
                echo -e "${RED}✗${NC} Not installed"
            fi
        done
    fi

    pause
}

# Option 7: Clean Old Logs
clean_logs() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}Clean Old Logs${NC}                                                ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ ! -d "$LOGS_DIR" ]; then
        echo -e "${YELLOW}No logs directory found${NC}"
        pause
        return
    fi

    # Count current logs
    current_count=$(find "$LOGS_DIR" -name "*.json" -type f | wc -l)
    echo -e "${GREEN}Current log files: $current_count${NC}"
    echo ""

    # Run cleanup script
    cleanup_script="$PROJECT_ROOT/scripts/local-ci/lib/cleanup-logs.sh"
    if [ -f "$cleanup_script" ]; then
        echo -e "${YELLOW}Running cleanup (keeps last 30 days)...${NC}"
        bash "$cleanup_script"

        new_count=$(find "$LOGS_DIR" -name "*.json" -type f | wc -l)
        removed=$((current_count - new_count))

        echo ""
        if [ $removed -gt 0 ]; then
            echo -e "${GREEN}✓ Removed $removed old log file(s)${NC}"
        else
            echo -e "${GREEN}✓ No logs older than 30 days${NC}"
        fi
    else
        echo -e "${RED}Cleanup script not found at $cleanup_script${NC}"
    fi

    pause
}

# Option 8: Help & Documentation
show_help() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}Help & Documentation${NC}                                          ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    echo -e "${GREEN}About:${NC}"
    echo "  This TUI provides an interactive interface for the local CI/CD"
    echo "  pipeline. It helps you run CI/CD tasks without memorizing flags."
    echo ""

    echo -e "${GREEN}Menu Options:${NC}"
    echo "  1-4: CI/CD operations with different configurations"
    echo "  5-7: Monitoring and maintenance tasks"
    echo "  8:   This help screen"
    echo "  9:   Exit the TUI"
    echo ""

    echo -e "${GREEN}Exit Codes (when running CI/CD):${NC}"
    echo "  0: Success - all checks passed"
    echo "  1: Lint failure"
    echo "  2: Test failure"
    echo "  3: Build failure"
    echo "  4: Environment validation failure"
    echo ""

    echo -e "${GREEN}Direct CLI Usage (alternative to TUI):${NC}"
    echo "  $CI_SCRIPT"
    echo "  $CI_SCRIPT --skip-tests"
    echo "  $CI_SCRIPT --verbose"
    echo "  $CI_SCRIPT --no-fix"
    echo "  $CI_SCRIPT --help"
    echo ""

    echo -e "${GREEN}Documentation:${NC}"
    echo "  README: $PROJECT_ROOT/README.md"
    echo "  Spec:   $PROJECT_ROOT/specs/001-local-cicd-astro-site/spec.md"
    echo "  Tasks:  $PROJECT_ROOT/specs/001-local-cicd-astro-site/tasks.md"
    echo ""

    pause
}

# Helper function: pause until user presses Enter
pause() {
    echo ""
    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
}

# Run main menu
main_menu
