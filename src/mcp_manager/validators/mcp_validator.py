"""MCP server configuration validator."""
import json
from pathlib import Path
from typing import List

from ..models.validation_models import MCPServerConfig, ValidationResult


class MCPValidator:
    """Validates MCP server configurations use UV."""

    def __init__(self, claude_config_path: Path = None):
        self.claude_config_path = claude_config_path or (Path.home() / ".claude.json")

    def validate_servers(self) -> ValidationResult:
        """Validate MCP server configurations."""
        try:
            servers = self._load_mcp_servers()

            stdio_servers = [s for s in servers if s.type == "stdio"]
            compliant_servers = [s for s in stdio_servers if s.uses_uv]
            non_compliant = [s for s in stdio_servers if not s.uses_uv]

            if non_compliant:
                failed_names = ", ".join([s.name for s in non_compliant])
                return ValidationResult(
                    check_name="mcp_servers",
                    passed=False,
                    message=f"{len(non_compliant)} stdio servers not using UV: {failed_names}",
                    details={
                        "total_servers": len(servers),
                        "stdio_servers": len(stdio_servers),
                        "compliant": len(compliant_servers),
                        "non_compliant_servers": [s.model_dump() for s in non_compliant],
                    },
                    severity="error",
                )

            return ValidationResult(
                check_name="mcp_servers",
                passed=True,
                message=f"All {len(stdio_servers)} stdio servers using UV",
                details={
                    "total_servers": len(servers),
                    "stdio_servers": len(stdio_servers),
                    "compliant": len(compliant_servers),
                },
                severity="info",
            )
        except Exception as e:
            return ValidationResult(
                check_name="mcp_servers",
                passed=False,
                message=f"MCP server validation failed: {str(e)}",
                severity="error",
            )

    def _load_mcp_servers(self) -> List[MCPServerConfig]:
        """Load MCP server configurations from ~/.claude.json."""
        with self.claude_config_path.open() as f:
            data = json.load(f)

        servers = []
        for name, config in data.get("mcpServers", {}).items():
            servers.append(
                MCPServerConfig(
                    name=name,
                    type=config.get("type", "stdio"),
                    command=config.get("command"),
                    args=config.get("args", []),
                    url=config.get("url"),
                    headers=config.get("headers", {}),
                )
            )

        return servers
