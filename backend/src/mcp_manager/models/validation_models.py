"""Pydantic models for Python 3.13 enforcement validation system."""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PythonVersionInfo(BaseModel):
    """Python version information from system and runtime."""

    major: int = Field(..., ge=3, description="Major version (must be 3)")
    minor: int = Field(..., ge=13, description="Minor version (must be >=13)")
    micro: int = Field(..., ge=0, description="Patch version")
    releaselevel: Literal["final", "alpha", "beta", "candidate"] = "final"
    serial: int = 0
    version_string: str = Field(..., pattern=r"^\d+\.\d+\.\d+.*$")
    executable_path: Path
    is_system_python: bool

    @field_validator("minor")
    @classmethod
    def validate_python_version(cls, v: int, info) -> int:
        """Validate Python version meets 3.13+ requirement."""
        if info.data.get("major") == 3 and v < 13:
            raise ValueError("Python 3.13+ required")
        return v

    @field_validator("executable_path")
    @classmethod
    def validate_executable_exists(cls, v: Path) -> Path:
        """Validate Python executable exists."""
        if not v.exists():
            raise ValueError(f"Python executable not found: {v}")
        return v


class UVConfiguration(BaseModel):
    """UV package manager configuration."""

    python_version_file: Optional[Path] = None
    python_version: str
    config_source: Path
    is_valid: bool
    detected_at: datetime = Field(default_factory=datetime.now)

    @field_validator("config_source")
    @classmethod
    def validate_config_exists(cls, v: Path) -> Path:
        """Validate configuration file exists."""
        if not v.exists():
            raise ValueError(f"Config file not found: {v}")
        return v


class MCPServerConfig(BaseModel):
    """MCP server configuration from ~/.claude.json."""

    name: str = Field(..., min_length=1)
    type: Literal["stdio", "http"]
    command: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    uses_uv: bool = Field(default=False)

    @model_validator(mode="after")
    def compute_uses_uv(self) -> "MCPServerConfig":
        """Compute whether stdio server uses UV."""
        if self.type == "stdio":
            self.uses_uv = self.command == "uv" and "run" in self.args
        return self

    @field_validator("command")
    @classmethod
    def validate_stdio_has_command(cls, v: Optional[str], info) -> Optional[str]:
        """Validate stdio servers have command."""
        if info.data.get("type") == "stdio" and not v:
            raise ValueError("stdio servers must specify command")
        return v


class ValidationResult(BaseModel):
    """Result of a validation check."""

    check_name: str = Field(..., min_length=1)
    passed: bool
    message: str = Field(..., min_length=1)
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    severity: Literal["info", "warning", "error", "critical"] = "info"

    @model_validator(mode="after")
    def validate_severity_matches_result(self) -> "ValidationResult":
        """Failed checks must be error or critical."""
        if not self.passed and self.severity not in ["error", "critical"]:
            self.severity = "error"
        return self


class ConstitutionCheckResult(BaseModel):
    """Constitution principle validation result."""

    principle_number: int = Field(..., ge=1, le=9)
    principle_name: str
    checks: List[ValidationResult] = Field(..., min_length=1)
    overall_passed: bool = Field(default=False)
    failed_checks: List[ValidationResult] = Field(default_factory=list)
    validation_timestamp: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def compute_overall_passed(self) -> "ConstitutionCheckResult":
        """All checks must pass for principle to pass."""
        self.overall_passed = all(check.passed for check in self.checks)
        return self

    @model_validator(mode="after")
    def compute_failed_checks(self) -> "ConstitutionCheckResult":
        """Extract only failed checks."""
        self.failed_checks = [check for check in self.checks if not check.passed]
        return self


class PythonEnforcementStatus(BaseModel):
    """Top-level Python 3.13 enforcement status."""

    python_version_valid: bool
    uv_config_valid: bool
    mcp_servers_valid: bool
    constitution_compliant: bool = Field(default=False)
    validation_results: List[ValidationResult]
    recommendations: List[str] = Field(default_factory=list)
    validated_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def compute_constitution_compliant(self) -> "PythonEnforcementStatus":
        """All three checks must pass."""
        self.constitution_compliant = (
            self.python_version_valid
            and self.uv_config_valid
            and self.mcp_servers_valid
        )
        return self

    @model_validator(mode="after")
    def generate_recommendations(self) -> "PythonEnforcementStatus":
        """Generate recommendations for failures."""
        recommendations = []
        if not self.python_version_valid:
            recommendations.append("Upgrade to Python 3.13+ (see TROUBLESHOOTING.md)")
        if not self.uv_config_valid:
            recommendations.append(
                "Create .python-version file with '3.13' content"
            )
        if not self.mcp_servers_valid:
            recommendations.append(
                "Update stdio MCP servers to use UV (see quickstart.md)"
            )
        self.recommendations = recommendations
        return self
