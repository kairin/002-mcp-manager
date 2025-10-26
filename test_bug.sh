#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Test Setup ---
# Create dummy executables
mkdir -p bin
echo '#!/bin/bash' > bin/claude
echo '#!/bin/bash' > bin/gemini
chmod +x bin/claude bin/gemini
export PATH="$(pwd)/bin:$PATH"

# Create dummy profiles
mkdir -p ~/.config/mcp-profiles
cat << EOF > ~/.config/mcp-profiles/dev.json
{ "github": { "command": "github-mcp-server", "type": "stdio" } }
EOF
cat << EOF > ~/.config/mcp-profiles/full.json
{
  "github": { "command": "github-mcp-server", "type": "stdio" },
  "hf-mcp-server": { "url": "http://localhost:3000/mcp", "type": "http" }
}
EOF

# Create dummy configs
project_path=$(pwd)
mkdir -p ~/.config/gemini
# Claude gets the 'dev' profile
claude_servers=$(cat ~/.config/mcp-profiles/dev.json)
cat << EOF > ~/.claude.json
{ "projects": { "$project_path": { "mcpServers": $claude_servers } } }
EOF
# Gemini gets the 'full' profile
gemini_servers=$(cat ~/.config/mcp-profiles/full.json)
cat << EOF > ~/.config/gemini/settings.json
{ "mcpServers": $gemini_servers }
EOF

echo "--- Running Test ---"

# --- Test Assertion ---
# Get the output of the status command for Gemini
output=$(MCP_TOOL=gemini ./scripts/mcp/mcp-profile status)

# Check if the output contains "Active Profile: FULL"
if echo "$output" | grep -q "Active Profile:.*FULL"; then
  echo "✅ PASSED: Gemini status correctly shows 'FULL' profile."
  exit 0
else
  echo "❌ FAILED: Gemini status did not show 'FULL' profile."
  echo "--- Output was: ---"
  echo "$output"
  echo "---------------------"
  exit 1
fi
