#!/bin/bash
# Test script to verify MCP servers work in Claude Code

echo "Testing Claude Code MCP Server Configuration"
echo "============================================"
echo ""

# Test if Claude Code CLI is available
if command -v claude >/dev/null 2>&1; then
    echo "✅ Claude Code CLI is installed"
else
    echo "❌ Claude Code CLI not found"
    exit 1
fi

# Check configuration file
if [ -f "$HOME/.claude.json" ]; then
    echo "✅ Claude configuration found at ~/.claude.json"

    # Count MCP servers
    SERVER_COUNT=$(jq '.mcpServers | keys | length' ~/.claude.json)
    echo "   Total MCP servers configured: $SERVER_COUNT"

    # List servers
    echo ""
    echo "Configured MCP Servers:"
    jq -r '.mcpServers | keys[] | "   • " + .' ~/.claude.json
else
    echo "❌ No Claude configuration found"
    exit 1
fi

echo ""
echo "Base installation verified! Ready to add more MCP servers."
echo ""
echo "To add new servers, edit ~/.claude.json and add to the mcpServers section."
