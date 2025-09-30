#!/bin/bash
# Quick setup script for HF MCP server with CLI authentication

echo "🤗 Hugging Face MCP Server Setup"
echo "================================"
echo ""
echo "This will:"
echo "1. Login to Hugging Face CLI (opens browser)"
echo "2. Retrieve your HF token automatically"
echo "3. Configure the HF MCP server with authentication"
echo ""

# Run the Python script
uv run python setup_hf_with_cli.py