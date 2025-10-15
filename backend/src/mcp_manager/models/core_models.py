"""Data models for MCP Manager."""

from datetime import datetime
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


# Phase 1 Models: Three-Phase Enhancement Plan


class UpdateStatus(BaseModel):
    """MCP server update state and version information.

    Tracks version information for npm-based MCP servers and categorizes
    updates according to semantic versioning.

    Fields from data-model.md specification.
    """

    server_name: str = Field(..., description="MCP server identifier")
    current_version: str | None = Field(
        None, description="Installed version (None for HTTP servers)"
    )
    latest_version: str | None = Field(
        None, description="Available version from registry"
    )
    update_available: bool = Field(..., description="Whether update is available")
    update_type: Literal["major", "minor", "patch", "none"] = Field(
        ..., description="Semantic version category"
    )
    dry_run: bool = Field(default=False, description="Whether this is a simulation")
    package_name: str | None = Field(
        None, description="npm package name (for stdio servers)"
    )
    check_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When version check was performed",
    )


class AuditConfiguration(BaseModel):
    """Configurable project directory paths for audit operations.

    Supports custom search directories for project .claude.json files,
    with fallback to default locations.

    Fields from data-model.md specification.
    """

    search_directories: list[Path] | None = Field(
        None, description="User-specified directories to scan"
    )
    default_directories: list[Path] = Field(
        default_factory=lambda: [
            Path.home() / "Apps",
            Path.home() / "projects",
            Path.home() / "repos",
        ],
        description="Built-in default paths",
    )
    use_defaults: bool = Field(
        default=True,
        description="Whether to include defaults if no custom paths provided",
    )
    validate_paths: bool = Field(
        default=True,
        description="Whether to check path existence before scanning",
    )

    def get_paths_to_scan(self) -> list[Path]:
        """Get the final list of paths to scan based on configuration."""
        if self.search_directories:
            return self.search_directories
        elif self.use_defaults:
            return self.default_directories
        else:
            return []


class GeminiCLISettings(BaseModel):
    """Gemini CLI configuration structure for MCP server synchronization.

    Mirrors Claude Code configuration structure and manages sync state.

    Fields from data-model.md specification.
    """

    mcpServers: dict[str, ServerConfig] = Field(
        default_factory=dict,
        description="MCP server definitions (identical to Claude Code format)",
    )
    config_path: Path = Field(
        ...,
        description="Location of settings.json file (~/.config/gemini/settings.json)",
    )
    env_var_configured: bool = Field(
        default=False,
        description="Whether GEMINI_CLI_SYSTEM_SETTINGS_PATH is set in shell profile",
    )


class VersionMetadata(BaseModel):
    """Project version information from pyproject.toml for consistency checks.

    Used for dynamic version injection and documentation synchronization.

    Fields from data-model.md specification.
    """

    version: str = Field(..., description='Project version (e.g., "0.1.0")')
    python_requirement: str = Field(
        ..., description='Required Python version (e.g., ">=3.11")'
    )
    mcp_server_count: int = Field(
        ..., description="Number of supported MCP servers (current: 6)"
    )
    dependencies: dict[str, str] = Field(
        default_factory=dict, description="Key dependencies and versions"
    )
    source_file: Path = Field(..., description="Location of pyproject.toml")
