"""Exception classes for MCP Manager."""


class MCPManagerError(Exception):
    """Base exception for MCP Manager operations."""

    pass


class ServerNotFoundError(MCPManagerError):
    """Raised when a requested MCP server is not found."""

    pass


class ConfigurationError(MCPManagerError):
    """Raised when there's an issue with MCP configuration."""

    pass


class ConnectionError(MCPManagerError):
    """Raised when unable to connect to an MCP server."""

    pass


class ValidationError(MCPManagerError):
    """Raised when configuration validation fails."""

    pass


class UpdateCheckError(MCPManagerError):
    """Raised when unable to check for MCP server updates."""

    pass


class NoUpdateAvailableError(MCPManagerError):
    """Raised when server is already at the latest version."""

    pass


class UpdateFailedError(MCPManagerError):
    """Raised when update check succeeded but applying update failed."""

    pass


class FileSystemError(MCPManagerError):
    """Raised when file system operations fail."""

    pass


class ShellProfileError(MCPManagerError):
    """Raised when unable to update shell profile."""

    pass


class NoServersError(MCPManagerError):
    """Raised when no MCP servers are configured."""

    pass


class InvalidPathError(MCPManagerError):
    """Raised when a provided path is invalid or doesn't exist."""

    pass


class PythonVersionError(MCPManagerError):
    """Python version does not meet requirements (3.13+)."""

    pass


class UVConfigError(MCPManagerError):
    """UV configuration invalid or missing in pyproject.toml."""

    pass


class MCPConfigError(MCPManagerError):
    """MCP server configuration violates UV-First principle."""

    pass


class ConstitutionViolationError(MCPManagerError):
    """Constitution principle violated."""

    pass
