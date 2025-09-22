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