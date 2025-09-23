"""Data models for MCP Manager."""

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class ServerType(str, Enum):
    """MCP Server types."""

    HTTP = "http"
    STDIO = "stdio"


class ServerStatus(str, Enum):
    """MCP Server status values."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    NOT_CONFIGURED = "not_configured"


class ServerConfig(BaseModel):
    """MCP Server configuration model."""

    type: ServerType
    url: str | None = None
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    headers: dict[str, str] = Field(default_factory=dict)
    env: dict[str, str] = Field(default_factory=dict)

    def validate_config(self) -> bool:
        """Validate server configuration."""
        if self.type == ServerType.HTTP:
            return self.url is not None
        elif self.type == ServerType.STDIO:
            return self.command is not None
        return False


class MCPServer(BaseModel):
    """MCP Server model with configuration and status."""

    name: str
    config: ServerConfig
    status: ServerStatus = ServerStatus.UNKNOWN
    last_check: str | None = None
    response_time: float | None = None
    error_message: str | None = None

    def is_healthy(self) -> bool:
        """Check if server is healthy."""
        return self.status == ServerStatus.HEALTHY


class GlobalConfig(BaseModel):
    """Global MCP configuration model."""

    version: str = "1.0"
    mcp_servers: dict[str, ServerConfig] = Field(default_factory=dict)
    last_updated: str | None = None

    def add_server(self, name: str, config: ServerConfig) -> None:
        """Add a server to the configuration."""
        self.mcp_servers[name] = config

    def remove_server(self, name: str) -> bool:
        """Remove a server from the configuration."""
        if name in self.mcp_servers:
            del self.mcp_servers[name]
            return True
        return False

    def get_server_config(self, name: str) -> ServerConfig | None:
        """Get configuration for a specific server."""
        return self.mcp_servers.get(name)


class ProjectAuditResult(BaseModel):
    """Result of a project standards audit."""

    project_name: str
    project_path: Path
    compliant: bool
    standards_results: dict[str, dict[str, Any]]
    overall_score: float
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class FleetNode(BaseModel):
    """Fleet node configuration and status."""

    hostname: str
    ip_address: str
    ubuntu_version: str
    python_version: str
    mcp_servers: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    last_sync: str | None = None
    status: Literal["active", "inactive", "unknown"] = "unknown"
