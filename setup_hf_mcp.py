#!/usr/bin/env python3
"""Quick setup script for HF MCP server without authentication."""

import json
from pathlib import Path

def add_hf_mcp_server():
    """Add HF MCP server to global configuration without authentication."""

    claude_config_path = Path.home() / ".claude.json"

    # Load existing config
    with open(claude_config_path, "r") as f:
        config = json.load(f)

    # Add HF MCP server (without auth for now)
    config["mcpServers"]["hf-mcp-server"] = {
        "type": "http",
        "url": "https://huggingface.co/mcp",
        "headers": {}
    }

    # Save config
    with open(claude_config_path, "w") as f:
        json.dump(config, f, indent=2)

    print("✅ HF MCP server added (without authentication)")
    print("To add authentication later, run: uv run python src/mcp_manager/hf_integration.py --login")

if __name__ == "__main__":
    add_hf_mcp_server()