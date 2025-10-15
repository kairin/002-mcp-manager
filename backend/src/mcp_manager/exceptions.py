"""Custom exceptions for MCP Manager.

References:
    - CLAUDE.md: Error handling requirements
    - tasks.md: T049-T052 (Phase 6 implementation)
"""


class MCPManagerError(Exception):
    """Base exception for MCP Manager operations."""

    pass


class ServerNotFoundError(MCPManagerError):
    """Server not found in configuration."""

    pass


class ConfigurationError(MCPManagerError):
    """Invalid configuration detected."""

    pass


class ConnectivityError(MCPManagerError):
    """Unable to connect to MCP server."""

    pass


class PythonEnvironmentError(MCPManagerError):
    """Python environment validation failed.

    Raised when:
    - System Python 3.13 not found
    - UV configuration violates constitutional requirements
    - MCP server cannot use system Python 3.13
    """

    pass


class FileSystemError(MCPManagerError):
    """File system operation failed.

    Raised when:
    - Unable to create directories
    - Permission denied writing configuration files
    - OS errors during file operations
    """

    pass


class ShellProfileError(MCPManagerError):
    """Shell profile update failed.

    Raised when:
    - Unable to read shell profile
    - Permission denied writing to shell profile
    - OS errors updating shell configuration
    """

    pass
