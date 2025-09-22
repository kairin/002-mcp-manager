"""MCP Manager - Centralized MCP Server Management for Claude Code.

This package provides comprehensive tools for managing Model Context Protocol (MCP)
servers across all Claude Code projects with automated configuration, monitoring,
and maintenance capabilities.
"""

__version__ = "0.1.0"
__author__ = "Mister K"
__email__ = "678459+kairin@users.noreply.github.com"

from .core import MCPManager
from .models import MCPServer, ServerConfig, ServerStatus
from .exceptions import MCPManagerError, ServerNotFoundError, ConfigurationError

__all__ = [
    "MCPManager",
    "MCPServer",
    "ServerConfig",
    "ServerStatus",
    "MCPManagerError",
    "ServerNotFoundError",
    "ConfigurationError",
]