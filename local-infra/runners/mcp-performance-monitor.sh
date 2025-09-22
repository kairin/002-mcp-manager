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
