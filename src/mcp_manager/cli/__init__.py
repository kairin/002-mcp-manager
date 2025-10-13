"""CLI commands for MCP Manager.

This module provides a modular CLI structure with separate command groups:
- mcp: MCP server management
- gemini: Gemini CLI integration
- project: Project standardization
- fleet: Fleet management
- agent: Claude agent management
- office: Office deployment management
- validate: Python 3.13 enforcement validation
"""

from .gemini_commands import gemini_app
from .mcp_commands import mcp_app
from .validate_commands import app as validate_app

__all__ = [
    "mcp_app",
    "gemini_app",
    "validate_app",
]
