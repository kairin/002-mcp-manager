# API Documentation

> **Python API Reference for MCP Manager**

## Overview

MCP Manager provides a Python API for programmatic management of Model Context Protocol servers. This reference covers all public classes, methods, and utilities.

**Status**: 🚧 **Planned** - API design in progress

## Installation

```bash
# UV-first installation (MANDATORY)
uv pip install mcp-manager

# Verify installation
uv run mcp-manager --version
```

## Quick Start

```python
from mcp_manager import MCPManager, ServerConfig

# Initialize manager
manager = MCPManager()

# List all servers
servers = manager.list_servers()
for server in servers:
    print(f"{server.name}: {server.status}")

# Check server health
health = manager.check_health("context7")
print(f"Status: {health.status}")
print(f"Response time: {health.response_time_ms}ms")
```

## Core Classes

### MCPManager

Main class for managing MCP servers.

```python
class MCPManager:
    """
    Central manager for MCP server operations.

    Attributes:
        config_path (Path): Path to global configuration file
        servers (Dict[str, ServerConfig]): Loaded server configurations
    """

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize MCP Manager.

        Args:
            config_path: Custom configuration path (default: ~/.claude.json)
        """
        ...

    def list_servers(self) -> List[ServerInfo]:
        """
        List all configured MCP servers.

        Returns:
            List of ServerInfo objects with name, type, and status

        Example:
            >>> manager = MCPManager()
            >>> servers = manager.list_servers()
            >>> for server in servers:
            ...     print(f"{server.name}: {server.type}")
        """
        ...

    def add_server(
        self,
        name: str,
        config: ServerConfig
    ) -> bool:
        """
        Add new MCP server to configuration.

        Args:
            name: Unique server identifier
            config: Server configuration object

        Returns:
            True if added successfully

        Raises:
            ServerExistsError: Server name already exists
            ValidationError: Invalid server configuration

        Example:
            >>> from mcp_manager import ServerConfig, ServerType
            >>> config = ServerConfig(
            ...     type=ServerType.HTTP,
            ...     url="https://api.example.com/mcp",
            ...     headers={"API-Key": "..."}
            ... )
            >>> manager.add_server("example", config)
            True
        """
        ...

    def remove_server(self, name: str) -> bool:
        """
        Remove MCP server from configuration.

        Args:
            name: Server identifier to remove

        Returns:
            True if removed successfully

        Raises:
            ServerNotFoundError: Server does not exist

        Example:
            >>> manager.remove_server("old-server")
            True
        """
        ...

    def update_server(
        self,
        name: str,
        config: ServerConfig
    ) -> bool:
        """
        Update existing server configuration.

        Args:
            name: Server identifier to update
            config: New server configuration

        Returns:
            True if updated successfully

        Raises:
            ServerNotFoundError: Server does not exist
            ValidationError: Invalid configuration

        Example:
            >>> config = manager.get_server("example")
            >>> config.url = "https://new.example.com/mcp"
            >>> manager.update_server("example", config)
            True
        """
        ...

    def get_server(self, name: str) -> ServerConfig:
        """
        Get server configuration by name.

        Args:
            name: Server identifier

        Returns:
            ServerConfig object

        Raises:
            ServerNotFoundError: Server does not exist

        Example:
            >>> config = manager.get_server("context7")
            >>> print(config.url)
            'https://mcp.context7.com/mcp'
        """
        ...

    def check_health(self, name: str) -> HealthStatus:
        """
        Check server health and connectivity.

        Args:
            name: Server identifier to check

        Returns:
            HealthStatus object with status and metrics

        Raises:
            ServerNotFoundError: Server does not exist

        Example:
            >>> health = manager.check_health("context7")
            >>> if health.is_healthy:
            ...     print(f"Server OK ({health.response_time_ms}ms)")
        """
        ...

    def check_all_health(self) -> Dict[str, HealthStatus]:
        """
        Check health of all configured servers.

        Returns:
            Dictionary mapping server names to HealthStatus objects

        Example:
            >>> results = manager.check_all_health()
            >>> healthy = [name for name, status in results.items()
            ...            if status.is_healthy]
            >>> print(f"{len(healthy)}/{len(results)} servers healthy")
        """
        ...

    def backup_config(self, backup_path: Optional[Path] = None) -> Path:
        """
        Create backup of current configuration.

        Args:
            backup_path: Custom backup location (default: ~/.claude.json.backup)

        Returns:
            Path to backup file

        Example:
            >>> backup = manager.backup_config()
            >>> print(f"Backup saved to {backup}")
        """
        ...

    def restore_config(self, backup_path: Path) -> bool:
        """
        Restore configuration from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            True if restored successfully

        Raises:
            FileNotFoundError: Backup file does not exist
            ValidationError: Invalid backup file format

        Example:
            >>> manager.restore_config(Path("~/.claude.json.backup"))
            True
        """
        ...
```

### ServerConfig

Configuration model for MCP servers.

```python
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field

class ServerType(str, Enum):
    """MCP server connection type."""
    HTTP = "http"
    STDIO = "stdio"

class ServerConfig(BaseModel):
    """
    MCP server configuration model.

    Attributes:
        type: Server connection type (http or stdio)
        url: API endpoint URL (HTTP servers only)
        command: Executable command (stdio servers only)
        args: Command-line arguments (stdio servers only)
        headers: HTTP headers with API keys (HTTP servers only)
        env: Environment variables for server process
        timeout: Connection timeout in seconds (default: 30)
    """

    type: ServerType
    url: Optional[str] = None
    command: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    headers: Dict[str, str] = Field(default_factory=dict)
    env: Dict[str, str] = Field(default_factory=dict)
    timeout: int = 30

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    def validate(self) -> None:
        """
        Validate configuration consistency.

        Raises:
            ValidationError: Configuration is invalid

        Example:
            >>> config = ServerConfig(type=ServerType.HTTP)
            >>> config.validate()  # Raises: HTTP server requires url
        """
        ...

# Example configurations
http_config = ServerConfig(
    type=ServerType.HTTP,
    url="https://mcp.context7.com/mcp",
    headers={"CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"},
    timeout=45
)

stdio_config = ServerConfig(
    type=ServerType.STDIO,
    command="npx",
    args=["shadcn@latest", "mcp"],
    env={}
)
```

### HealthStatus

Server health check result model.

```python
from datetime import datetime
from enum import Enum

class ServerStatus(str, Enum):
    """Server health status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    UNKNOWN = "unknown"

class HealthStatus(BaseModel):
    """
    Server health check result.

    Attributes:
        server_name: Server identifier
        status: Current health status
        is_healthy: Convenience boolean for status == CONNECTED
        response_time_ms: Response time in milliseconds
        last_check: Timestamp of health check
        error_message: Error details if status == ERROR
    """

    server_name: str
    status: ServerStatus
    response_time_ms: Optional[float] = None
    last_check: datetime
    error_message: Optional[str] = None

    @property
    def is_healthy(self) -> bool:
        """Check if server is healthy."""
        return self.status == ServerStatus.CONNECTED

    def __str__(self) -> str:
        """Human-readable status string."""
        if self.is_healthy:
            return f"✅ {self.server_name} ({self.response_time_ms}ms)"
        return f"❌ {self.server_name}: {self.error_message}"

# Example usage
health = HealthStatus(
    server_name="context7",
    status=ServerStatus.CONNECTED,
    response_time_ms=125.5,
    last_check=datetime.now()
)
print(health.is_healthy)  # True
print(health)  # ✅ context7 (125.5ms)
```

### ServerInfo

Server information summary model.

```python
class ServerInfo(BaseModel):
    """
    Server information summary.

    Attributes:
        name: Server identifier
        type: Server connection type
        status: Current health status
        url: API endpoint (HTTP servers only)
        command: Executable command (stdio servers only)
    """

    name: str
    type: ServerType
    status: ServerStatus
    url: Optional[str] = None
    command: Optional[str] = None

    def __str__(self) -> str:
        """Human-readable server info."""
        status_icon = "✅" if self.status == ServerStatus.CONNECTED else "❌"
        return f"{status_icon} {self.name} ({self.type.value})"

# Example
info = ServerInfo(
    name="context7",
    type=ServerType.HTTP,
    status=ServerStatus.CONNECTED,
    url="https://mcp.context7.com/mcp"
)
print(info)  # ✅ context7 (http)
```

## Utility Functions

### Configuration Management

```python
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: Path = Path.home() / ".claude.json") -> Dict[str, Any]:
    """
    Load MCP configuration from file.

    Args:
        config_path: Path to configuration file

    Returns:
        Parsed configuration dictionary

    Raises:
        FileNotFoundError: Configuration file does not exist
        JSONDecodeError: Invalid JSON format

    Example:
        >>> config = load_config()
        >>> servers = config["mcpServers"]
    """
    ...

def save_config(
    config: Dict[str, Any],
    config_path: Path = Path.home() / ".claude.json"
) -> None:
    """
    Save MCP configuration to file.

    Args:
        config: Configuration dictionary to save
        config_path: Path to configuration file

    Raises:
        PermissionError: Cannot write to configuration file
        ValidationError: Invalid configuration format

    Example:
        >>> config = load_config()
        >>> config["mcpServers"]["new-server"] = {...}
        >>> save_config(config)
    """
    ...

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure.

    Args:
        config: Configuration dictionary to validate

    Returns:
        True if valid

    Raises:
        ValidationError: Configuration is invalid

    Example:
        >>> config = load_config()
        >>> validate_config(config)
        True
    """
    ...
```

### Environment Variables

```python
import os
from typing import Dict, Optional

def expand_env_vars(value: str) -> str:
    """
    Expand ${VAR_NAME} patterns in string.

    Args:
        value: String with potential environment variables

    Returns:
        String with expanded variables

    Example:
        >>> os.environ["API_KEY"] = "secret"
        >>> expand_env_vars("Key: ${API_KEY}")
        'Key: secret'
    """
    ...

def load_env_file(env_file: Path) -> Dict[str, str]:
    """
    Load environment variables from .env file.

    Args:
        env_file: Path to .env file

    Returns:
        Dictionary of environment variables

    Example:
        >>> env = load_env_file(Path(".env"))
        >>> os.environ.update(env)
    """
    ...

def get_required_env(var_name: str) -> str:
    """
    Get required environment variable.

    Args:
        var_name: Environment variable name

    Returns:
        Environment variable value

    Raises:
        EnvironmentError: Variable not set

    Example:
        >>> api_key = get_required_env("CONTEXT7_API_KEY")
    """
    ...
```

## Exceptions

```python
class MCPManagerError(Exception):
    """Base exception for MCP Manager."""
    pass

class ServerNotFoundError(MCPManagerError):
    """Server not found in configuration."""

    def __init__(self, server_name: str):
        super().__init__(f"Server '{server_name}' not found")
        self.server_name = server_name

class ServerExistsError(MCPManagerError):
    """Server name already exists."""

    def __init__(self, server_name: str):
        super().__init__(f"Server '{server_name}' already exists")
        self.server_name = server_name

class ConfigurationError(MCPManagerError):
    """Invalid configuration detected."""
    pass

class ConnectivityError(MCPManagerError):
    """Unable to connect to MCP server."""

    def __init__(self, server_name: str, reason: str):
        super().__init__(f"Cannot connect to '{server_name}': {reason}")
        self.server_name = server_name
        self.reason = reason

class ValidationError(MCPManagerError):
    """Configuration validation failed."""
    pass

# Example exception handling
try:
    manager.get_server("nonexistent")
except ServerNotFoundError as e:
    print(f"Error: {e}")
    print(f"Available servers: {[s.name for s in manager.list_servers()]}")
```

## CLI Integration

### Command-Line Interface

```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def list_servers():
    """List all configured MCP servers."""
    manager = MCPManager()
    servers = manager.list_servers()

    for server in servers:
        console.print(server)

@app.command()
def add(
    name: str,
    type: str = typer.Option(..., help="Server type (http/stdio)"),
    url: Optional[str] = typer.Option(None, help="API endpoint URL"),
    command: Optional[str] = typer.Option(None, help="Executable command")
):
    """Add new MCP server."""
    manager = MCPManager()

    config = ServerConfig(
        type=ServerType(type),
        url=url,
        command=command
    )

    try:
        manager.add_server(name, config)
        console.print(f"✅ Added server '{name}'")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)

@app.command()
def status(name: Optional[str] = None):
    """Check server health status."""
    manager = MCPManager()

    if name:
        health = manager.check_health(name)
        console.print(health)
    else:
        results = manager.check_all_health()
        for health in results.values():
            console.print(health)

if __name__ == "__main__":
    app()
```

## Advanced Usage

### Custom Health Checks

```python
from typing import Callable

class MCPManager:
    def register_health_check(
        self,
        server_name: str,
        check_func: Callable[[ServerConfig], bool]
    ) -> None:
        """
        Register custom health check function.

        Args:
            server_name: Server to register check for
            check_func: Function that returns True if healthy

        Example:
            >>> def custom_check(config: ServerConfig) -> bool:
            ...     response = requests.get(config.url)
            ...     return response.status_code == 200
            >>>
            >>> manager.register_health_check("context7", custom_check)
        """
        ...
```

### Configuration Migration

```python
def migrate_project_config(
    project_path: Path,
    global_config: Path = Path.home() / ".claude.json"
) -> bool:
    """
    Migrate project-specific config to global.

    Args:
        project_path: Path to project directory
        global_config: Path to global configuration

    Returns:
        True if migration successful

    Example:
        >>> migrate_project_config(Path("./my-project"))
        True
    """
    ...
```

### Monitoring and Metrics

```python
from typing import Iterator
import time

class MCPMonitor:
    """Real-time MCP server monitoring."""

    def __init__(self, manager: MCPManager):
        self.manager = manager

    def monitor(self, interval: int = 5) -> Iterator[Dict[str, HealthStatus]]:
        """
        Continuously monitor server health.

        Args:
            interval: Check interval in seconds

        Yields:
            Health status for all servers

        Example:
            >>> monitor = MCPMonitor(manager)
            >>> for status in monitor.monitor(interval=10):
            ...     for name, health in status.items():
            ...         print(f"{name}: {health.status}")
            ...     time.sleep(1)
        """
        while True:
            yield self.manager.check_all_health()
            time.sleep(interval)
```

## Testing

### Unit Tests

```python
import pytest
from mcp_manager import MCPManager, ServerConfig, ServerType

def test_add_server():
    """Test adding new server."""
    manager = MCPManager()
    config = ServerConfig(
        type=ServerType.HTTP,
        url="https://test.example.com/mcp"
    )

    assert manager.add_server("test", config)
    assert "test" in [s.name for s in manager.list_servers()]

def test_server_not_found():
    """Test server not found error."""
    manager = MCPManager()

    with pytest.raises(ServerNotFoundError):
        manager.get_server("nonexistent")
```

### Integration Tests

```python
@pytest.mark.integration
def test_http_server_connectivity():
    """Test actual HTTP server connection."""
    manager = MCPManager()
    health = manager.check_health("context7")

    assert health.is_healthy
    assert health.response_time_ms < 1000
```

## Next Steps

- [Configuration Guide](configuration.md) - Setup instructions
- [Server Management](servers.md) - Managing MCP servers
- [Troubleshooting](troubleshooting.md) - Common issues

## Contributing

For contributing to the API:

1. Follow [AGENTS.md](../AGENTS.md) standards
2. Use UV for all Python operations
3. Add type annotations to all functions
4. Write comprehensive docstrings
5. Include usage examples
6. Add unit tests for new features

---

**Status**: 🚧 Planned - API design in progress
**Target**: Python 3.11+
**Dependencies**: Pydantic v2, Rich, Typer
**License**: MIT