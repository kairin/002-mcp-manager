#!/bin/bash
##
## System-Wide MCP Configuration Setup
## Configures Claude Code, Gemini CLI, and Copilot CLI to use shared environment variables
##

set -e

echo "========================================="
echo "System-Wide MCP Configuration Setup"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if API keys are already in environment
check_env_vars() {
    echo "Checking current environment variables..."

    if [ -n "$CONTEXT7_API_KEY" ]; then
        echo -e "${GREEN}✓${NC} CONTEXT7_API_KEY is set"
        HAS_CONTEXT7=1
    else
        echo -e "${YELLOW}⚠${NC} CONTEXT7_API_KEY not found in environment"
        HAS_CONTEXT7=0
    fi

    if [ -n "$HUGGINGFACE_TOKEN" ]; then
        echo -e "${GREEN}✓${NC} HUGGINGFACE_TOKEN is set"
        HAS_HF=1
    else
        echo -e "${YELLOW}⚠${NC} HUGGINGFACE_TOKEN not found in environment"
        HAS_HF=0
    fi

    if [ -n "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
        echo -e "${GREEN}✓${NC} GITHUB_PERSONAL_ACCESS_TOKEN is set"
        HAS_GITHUB=1
    else
        echo -e "${YELLOW}⚠${NC} GITHUB_PERSONAL_ACCESS_TOKEN not found in environment"
        HAS_GITHUB=0
    fi

    echo ""
}

# Add environment variables to ~/.profile if not already there
setup_profile() {
    echo "Setting up ~/.profile..."

    if grep -q "# MCP Manager - Shared API Keys" ~/.profile 2>/dev/null; then
        echo -e "${YELLOW}⚠${NC} MCP environment variables already in ~/.profile"
        echo "   Edit ~/.profile manually to update keys"
    else
        echo -e "${GREEN}→${NC} Adding MCP environment variable section to ~/.profile"

        cat >> ~/.profile << 'EOF'

# ============================================
# MCP Manager - Shared API Keys
# Used by: Claude Code, Gemini CLI, Copilot CLI
# ============================================

# TODO: Replace these with your actual API keys
export CONTEXT7_API_KEY="your-context7-key-here"
export HUGGINGFACE_TOKEN="your-huggingface-token-here"
export GITHUB_PERSONAL_ACCESS_TOKEN="your-github-token-here"

# Alternative names for compatibility
export HF_TOKEN="$HUGGINGFACE_TOKEN"
export GH_TOKEN="$GITHUB_PERSONAL_ACCESS_TOKEN"

EOF

        echo -e "${GREEN}✓${NC} Added to ~/.profile"
        echo -e "${YELLOW}⚠${NC} IMPORTANT: Edit ~/.profile and add your actual API keys!"
    fi

    echo ""
}

# Configure Gemini CLI system-wide setting
setup_gemini_env() {
    echo "Setting up Gemini CLI system-wide configuration..."

    if grep -q "GEMINI_CLI_SYSTEM_SETTINGS_PATH" ~/.bashrc 2>/dev/null; then
        echo -e "${YELLOW}⚠${NC} GEMINI_CLI_SYSTEM_SETTINGS_PATH already in ~/.bashrc"
    else
        echo -e "${GREEN}→${NC} Adding GEMINI_CLI_SYSTEM_SETTINGS_PATH to ~/.bashrc"

        cat >> ~/.bashrc << 'EOF'

# MCP Manager - Gemini CLI system-wide configuration
export GEMINI_CLI_SYSTEM_SETTINGS_PATH="$HOME/.config/gemini/settings.json"

EOF

        echo -e "${GREEN}✓${NC} Added to ~/.bashrc"
    fi

    echo ""
}

# Show next steps
show_next_steps() {
    echo "========================================="
    echo "Setup Complete!"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. ${YELLOW}Edit ~/.profile${NC} and add your actual API keys:"
    echo "   nano ~/.profile"
    echo ""
    echo "2. ${YELLOW}Reload your shell configuration:${NC}"
    echo "   source ~/.profile"
    echo "   source ~/.bashrc"
    echo ""
    echo "3. ${YELLOW}Verify environment variables are set:${NC}"
    echo "   echo \$CONTEXT7_API_KEY | head -c 10"
    echo "   echo \$HUGGINGFACE_TOKEN | head -c 10"
    echo ""
    echo "4. ${YELLOW}Test MCP servers:${NC}"
    echo "   claude mcp list"
    echo "   gemini mcp list"
    echo ""
    echo "📖 For detailed information, see:"
    echo "   ~/Apps/002-mcp-manager/docs/SYSTEM-WIDE-MCP-SETUP.md"
    echo ""
}

# Main execution
main() {
    check_env_vars
    setup_profile
    setup_gemini_env
    show_next_steps
}

main
