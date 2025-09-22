#!/bin/bash

# GitHub CLI-based local workflow simulation for MCP Manager
# This script provides zero-cost local CI/CD capabilities

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
LOG_DIR="$SCRIPT_DIR/../logs"
CONFIG_DIR="$SCRIPT_DIR/../config"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color=""

    case "$level" in
        "ERROR") color="$RED" ;;
        "SUCCESS") color="$GREEN" ;;
        "WARNING") color="$YELLOW" ;;
        "INFO") color="$BLUE" ;;
        "STEP") color="$CYAN" ;;
    esac

    echo -e "${color}[$timestamp] [$level] $message${NC}"
    echo "[$timestamp] [$level] $message" >> "$LOG_DIR/workflow-$(date +%s).log"
}

# Performance timing
start_timer() {
    TIMER_START=$(date +%s)
}

end_timer() {
    local operation="$1"
    if [ -n "$TIMER_START" ]; then
        local duration=$(($(date +%s) - TIMER_START))
        log "INFO" "⏱️ $operation completed in ${duration}s"
        echo "{\"timestamp\":\"$(date -Iseconds)\",\"operation\":\"$operation\",\"duration\":\"${duration}s\"}" >> "$LOG_DIR/performance-$(date +%s).json"
        unset TIMER_START
    fi
}

# Python environment validation
validate_python_env() {
    log "STEP" "🐍 Validating Python environment..."
    start_timer

    # Check for uv
    if command -v uv >/dev/null 2>&1; then
        log "SUCCESS" "✅ uv package manager found"
    else
        log "ERROR" "❌ uv package manager not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        end_timer "Python environment validation"
        return 1
    fi

    # Check for virtual environment
    if [ -d "$REPO_DIR/.venv" ]; then
        log "SUCCESS" "✅ Virtual environment found"

        # Activate and check Python version
        source "$REPO_DIR/.venv/bin/activate"
        local python_version=$(python --version 2>&1)
        log "INFO" "📊 Python version: $python_version"

        # Check if mcp-manager is installed
        if python -c "import mcp_manager" 2>/dev/null; then
            log "SUCCESS" "✅ mcp-manager package installed"
        else
            log "WARNING" "⚠️ mcp-manager package not installed. Run: uv pip install -e ."
        fi
    else
        log "WARNING" "⚠️ Virtual environment not found. Run: uv venv"
    fi

    end_timer "Python environment validation"
}

# Code quality checks
run_code_quality() {
    log "STEP" "🔍 Running code quality checks..."
    start_timer

    cd "$REPO_DIR"
    source .venv/bin/activate 2>/dev/null || true

    local quality_issues=0

    # Black formatting check
    if command -v black >/dev/null 2>&1; then
        log "INFO" "🖤 Running Black formatter check..."
        if black --check src/ tests/ 2>/dev/null; then
            log "SUCCESS" "✅ Black formatting passed"
        else
            log "WARNING" "⚠️ Black formatting issues found. Run: black src/ tests/"
            ((quality_issues++))
        fi
    else
        log "WARNING" "⚠️ Black not found. Install dev dependencies: uv pip install -e '.[dev]'"
    fi

    # Ruff linting
    if command -v ruff >/dev/null 2>&1; then
        log "INFO" "🔍 Running Ruff linter..."
        if ruff check src/ tests/ 2>/dev/null; then
            log "SUCCESS" "✅ Ruff linting passed"
        else
            log "WARNING" "⚠️ Ruff linting issues found. Run: ruff check src/ tests/"
            ((quality_issues++))
        fi
    else
        log "WARNING" "⚠️ Ruff not found. Install dev dependencies: uv pip install -e '.[dev]'"
    fi

    # MyPy type checking
    if command -v mypy >/dev/null 2>&1; then
        log "INFO" "🔍 Running MyPy type checker..."
        if mypy src/ 2>/dev/null; then
            log "SUCCESS" "✅ MyPy type checking passed"
        else
            log "WARNING" "⚠️ MyPy type checking issues found. Run: mypy src/"
            ((quality_issues++))
        fi
    else
        log "WARNING" "⚠️ MyPy not found. Install dev dependencies: uv pip install -e '.[dev]'"
    fi

    if [ $quality_issues -eq 0 ]; then
        log "SUCCESS" "✅ All code quality checks passed"
    else
        log "WARNING" "⚠️ Found $quality_issues code quality issues"
    fi

    end_timer "Code quality checks"
    return $quality_issues
}

# Test execution
run_tests() {
    log "STEP" "🧪 Running test suite..."
    start_timer

    cd "$REPO_DIR"
    source .venv/bin/activate 2>/dev/null || true

    if command -v pytest >/dev/null 2>&1; then
        log "INFO" "🧪 Running pytest with coverage..."
        if pytest tests/ --cov=mcp_manager --cov-report=html --cov-report=term 2>&1 | tee "$LOG_DIR/test-results-$(date +%s).log"; then
            log "SUCCESS" "✅ Test suite passed"
        else
            log "ERROR" "❌ Test suite failed"
            end_timer "Test execution"
            return 1
        fi
    else
        log "WARNING" "⚠️ pytest not found. Install dev dependencies: uv pip install -e '.[dev]'"
        log "INFO" "ℹ️ Running basic import test..."
        if python -c "import mcp_manager; print('✅ Package imports successfully')"; then
            log "SUCCESS" "✅ Basic import test passed"
        else
            log "ERROR" "❌ Basic import test failed"
            return 1
        fi
    fi

    end_timer "Test execution"
}

# Astro build validation
validate_astro_build() {
    log "STEP" "🏗️ Validating Astro build..."
    start_timer

    cd "$REPO_DIR"

    # Check if Node.js is available
    if ! command -v node >/dev/null 2>&1; then
        log "ERROR" "❌ Node.js not found. Install Node.js >=18"
        end_timer "Astro build validation"
        return 1
    fi

    # Check Node.js version
    local node_version=$(node --version)
    log "INFO" "📊 Node.js version: $node_version"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log "INFO" "📦 Installing npm dependencies..."
        npm install
    fi

    # Run Astro check
    if npm run check 2>/dev/null; then
        log "SUCCESS" "✅ Astro check passed"
    else
        log "WARNING" "⚠️ Astro check issues found"
    fi

    # Build Astro site
    log "INFO" "🏗️ Building Astro site..."
    if npm run build 2>&1 | tee "$LOG_DIR/astro-build-$(date +%s).log"; then
        log "SUCCESS" "✅ Astro build completed"

        # Verify build output
        if [ -f "$REPO_DIR/docs/index.html" ]; then
            log "SUCCESS" "✅ Build output verified"
        else
            log "ERROR" "❌ Build output not found"
            return 1
        fi

        # Verify .nojekyll file
        if [ -f "$REPO_DIR/docs/.nojekyll" ]; then
            log "SUCCESS" "✅ .nojekyll file created (CRITICAL for GitHub Pages)"
        else
            log "ERROR" "❌ .nojekyll file missing (WILL BREAK GitHub Pages)"
            return 1
        fi

    else
        log "ERROR" "❌ Astro build failed"
        end_timer "Astro build validation"
        return 1
    fi

    end_timer "Astro build validation"
}

# GitHub Pages simulation
simulate_pages() {
    log "STEP" "📄 Simulating GitHub Pages deployment..."
    start_timer

    if [ -f "$SCRIPT_DIR/gh-pages-setup.sh" ]; then
        "$SCRIPT_DIR/gh-pages-setup.sh"
    else
        log "INFO" "ℹ️ GitHub Pages setup script not found, creating it..."
        "$0" init
        "$SCRIPT_DIR/gh-pages-setup.sh"
    fi

    end_timer "GitHub Pages simulation"
}

# GitHub status check
check_github_status() {
    log "STEP" "🐙 Checking GitHub status..."
    start_timer

    if command -v gh >/dev/null 2>&1; then
        if gh auth status >/dev/null 2>&1; then
            log "SUCCESS" "✅ GitHub CLI authenticated"

            # Check recent workflow runs
            local recent_runs
            recent_runs=$(gh run list --limit 5 --json status,conclusion,name,createdAt 2>/dev/null || echo "[]")
            echo "$recent_runs" > "$LOG_DIR/github-runs-$(date +%s).json"

            local run_count
            run_count=$(echo "$recent_runs" | jq length 2>/dev/null || echo "0")
            log "INFO" "📊 Found $run_count recent workflow runs"
        else
            log "WARNING" "⚠️ GitHub CLI not authenticated"
        fi
    else
        log "WARNING" "⚠️ GitHub CLI not available"
    fi

    end_timer "GitHub status check"
}

# Billing check
check_billing() {
    log "STEP" "💰 Checking GitHub Actions billing..."
    start_timer

    if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
        local billing_info
        billing_info=$(gh api user/settings/billing/actions 2>/dev/null || echo "{}")
        echo "$billing_info" > "$LOG_DIR/billing-$(date +%s).json"

        local minutes_used_raw
        local included_minutes_raw
        minutes_used_raw=$(echo "$billing_info" | jq -r '.total_minutes_used // empty' 2>/dev/null || true)
        included_minutes_raw=$(echo "$billing_info" | jq -r '.included_minutes // empty' 2>/dev/null || true)

        local minutes_used="${minutes_used_raw:-unknown}"
        local included_minutes="${included_minutes_raw:-unknown}"

        log "INFO" "📊 GitHub Actions usage: $minutes_used / $included_minutes minutes"

        if [[ "$minutes_used" =~ ^[0-9]+$ ]] && [[ "$included_minutes" =~ ^[0-9]+$ ]] && [ "$included_minutes" -ne 0 ]; then
            local usage_percent=$((minutes_used * 100 / included_minutes))
            if [ $usage_percent -gt 80 ]; then
                log "WARNING" "⚠️ High GitHub Actions usage: ${usage_percent}%"
            else
                log "SUCCESS" "✅ GitHub Actions usage within limits: ${usage_percent}%"
            fi
        fi
    else
        log "WARNING" "⚠️ Cannot check billing - GitHub CLI not available or not authenticated"
    fi

    end_timer "Billing check"
}

# Complete local workflow
run_complete_workflow() {
    log "INFO" "🚀 Starting complete MCP Manager local workflow..."

    local overall_start=$(date +%s)
    local failed_steps=0

    # Run all workflow steps
    validate_python_env || ((failed_steps++))
    run_code_quality || ((failed_steps++))
    run_tests || ((failed_steps++))
    validate_astro_build || ((failed_steps++))
    check_github_status || ((failed_steps++))
    check_billing || ((failed_steps++))
    simulate_pages || ((failed_steps++))

    local overall_duration=$(($(date +%s) - overall_start))

    if [ $failed_steps -eq 0 ]; then
        log "SUCCESS" "🎉 Complete workflow successful in ${overall_duration}s"
        echo "{\"timestamp\":\"$(date -Iseconds)\",\"workflow\":\"complete\",\"duration\":\"${overall_duration}s\",\"status\":\"success\",\"failed_steps\":$failed_steps}" >> "$LOG_DIR/workflow-summary-$(date +%s).json"
        return 0
    else
        log "WARNING" "⚠️ Workflow completed with $failed_steps failed steps in ${overall_duration}s"
        echo "{\"timestamp\":\"$(date -Iseconds)\",\"workflow\":\"complete\",\"duration\":\"${overall_duration}s\",\"status\":\"partial\",\"failed_steps\":$failed_steps}" >> "$LOG_DIR/workflow-summary-$(date +%s).json"
        return 1
    fi
}

# Initialize local CI/CD infrastructure
init_infrastructure() {
    log "STEP" "🏗️ Initializing MCP Manager local CI/CD infrastructure..."

    # Create necessary directories
    mkdir -p "$LOG_DIR" "$CONFIG_DIR/workflows" "$CONFIG_DIR/test-suites"

    # Create GitHub Pages setup script
    if [ ! -f "$SCRIPT_DIR/gh-pages-setup.sh" ]; then
        log "INFO" "📄 Creating Astro GitHub Pages setup script..."
        cat > "$SCRIPT_DIR/gh-pages-setup.sh" << 'EOF'
#!/bin/bash
# Astro GitHub Pages setup for MCP Manager
echo "📄 Setting up zero-cost GitHub Pages with Astro..."

REPO_DIR="$(dirname "$(dirname "$(dirname "$0")")")"

setup_github_pages() {
    echo "🔧 Configuring Astro for GitHub Pages deployment..."

    # Ensure Astro build output directory exists
    if [ ! -d "$REPO_DIR/docs" ]; then
        echo "❌ docs/ directory not found. Running Astro build..."
        cd "$REPO_DIR" && npm run build
        if [ $? -ne 0 ]; then
            echo "❌ Astro build failed. Check astro.config.mjs configuration."
            return 1
        fi
    fi

    # Verify Astro build output
    if [ -f "$REPO_DIR/docs/index.html" ]; then
        echo "✅ Astro build output verified in docs/"
    else
        echo "❌ No index.html found in docs/. Run: npm run build"
        return 1
    fi

    # CRITICAL: Verify .nojekyll file exists
    if [ -f "$REPO_DIR/docs/.nojekyll" ]; then
        echo "✅ .nojekyll file confirmed (CRITICAL for GitHub Pages)"
    else
        echo "❌ .nojekyll file missing. Creating it now..."
        touch "$REPO_DIR/docs/.nojekyll"
        echo "✅ .nojekyll file created"
    fi

    # Configure GitHub Pages to serve from docs/ folder
    if command -v gh >/dev/null 2>&1; then
        echo "🔧 Configuring GitHub Pages deployment..."
        gh api repos/:owner/:repo --method PATCH \
            --field source[branch]=main \
            --field source[path]="/docs" 2>/dev/null && \
            echo "✅ GitHub Pages configured to serve from docs/ folder" || \
            echo "ℹ️ GitHub CLI configuration may require manual setup"
    else
        echo "ℹ️ GitHub CLI not available, configure Pages manually:"
        echo "   Settings → Pages → Source: Deploy from a branch → main → /docs"
    fi

    echo "✅ Astro GitHub Pages setup complete"
}

setup_github_pages
EOF
        chmod +x "$SCRIPT_DIR/gh-pages-setup.sh"
        log "SUCCESS" "✅ Astro GitHub Pages setup script created"
    fi

    # Create MCP-specific performance monitor
    if [ ! -f "$SCRIPT_DIR/mcp-performance-monitor.sh" ]; then
        log "INFO" "📊 Creating MCP performance monitor script..."
        cat > "$SCRIPT_DIR/mcp-performance-monitor.sh" << 'EOF'
#!/bin/bash
# Performance monitoring for MCP Manager
echo "📊 Monitoring MCP Manager performance..."

monitor_mcp_performance() {
    local test_mode="$1"
    local log_dir="$(dirname "$0")/../logs"
    local repo_dir="$(dirname "$(dirname "$(dirname "$0")")")"

    # Python package performance
    if [ -f "$repo_dir/.venv/bin/activate" ]; then
        source "$repo_dir/.venv/bin/activate"

        # CLI startup time
        local cli_startup_time
        cli_startup_time=$(time (mcp-manager --help >/dev/null 2>&1) 2>&1 | grep real | awk '{print $2}' || echo "0m0.000s")

        # Import time
        local import_time
        import_time=$(time (python -c "import mcp_manager" 2>/dev/null) 2>&1 | grep real | awk '{print $2}' || echo "0m0.000s")

        # Store results
        cat > "$log_dir/mcp-performance-$(date +%s).json" << EOL
{
    "timestamp": "$(date -Iseconds)",
    "cli_startup_time": "$cli_startup_time",
    "import_time": "$import_time",
    "test_mode": "$test_mode",
    "python_version": "$(python --version 2>&1)",
    "package_installed": $(python -c "import mcp_manager; print('true')" 2>/dev/null || echo "false")
}
EOL
        echo "✅ MCP Manager performance data collected"
    else
        echo "⚠️ Virtual environment not found for performance testing"
    fi
}

case "$1" in
    --test) monitor_mcp_performance "test" ;;
    --baseline) monitor_mcp_performance "baseline" ;;
    --compare) monitor_mcp_performance "compare" ;;
    *) monitor_mcp_performance "default" ;;
esac
EOF
        chmod +x "$SCRIPT_DIR/mcp-performance-monitor.sh"
        log "SUCCESS" "✅ MCP performance monitor created"
    fi

    log "SUCCESS" "✅ MCP Manager local CI/CD infrastructure initialized"
}

# Show help
show_help() {
    echo "MCP Manager Local GitHub Workflow Simulation"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  init        Initialize local CI/CD infrastructure"
    echo "  local       Run complete local workflow simulation"
    echo "  python      Validate Python environment and dependencies"
    echo "  quality     Run code quality checks (black, ruff, mypy)"
    echo "  test        Run test suite with coverage"
    echo "  build       Build Astro site and validate output"
    echo "  status      Check GitHub Actions status"
    echo "  billing     Check GitHub Actions billing"
    echo "  pages       Setup and validate GitHub Pages deployment"
    echo "  all         Run complete workflow (python + quality + test + build + status + billing + pages)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 init     # Initialize local CI/CD infrastructure"
    echo "  $0 all      # Run complete local workflow"
    echo "  $0 quality  # Only run code quality checks"
    echo "  $0 build    # Only build and validate Astro site"
    echo ""
}

# Main execution
main() {
    case "${1:-help}" in
        "init")
            init_infrastructure
            ;;
        "local"|"workflow")
            run_complete_workflow
            ;;
        "python"|"py")
            validate_python_env
            ;;
        "quality"|"lint")
            run_code_quality
            ;;
        "test"|"tests")
            run_tests
            ;;
        "build"|"astro")
            validate_astro_build
            ;;
        "status")
            check_github_status
            ;;
        "billing")
            check_billing
            ;;
        "pages")
            simulate_pages
            ;;
        "all")
            run_complete_workflow
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            echo "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi