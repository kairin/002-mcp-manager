"""Pydantic v2 models for System Python 3.13 Enforcement (Feature 002).

This module defines the core data models for Python environment detection,
UV configuration validation, and constitution compliance validation.

References:
    - Spec: specs/002-system-python-enforcement/spec.md
    - Data Model: specs/002-system-python-enforcement/data-model.md
    - Tasks: T005, T006, T007
"""

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PythonEnvironment(BaseModel):
    """System Python 3.13 environment configuration.

    Represents a detected Python 3.13 installation with validation status.
    This model is immutable (frozen) after creation.

    Attributes:
        executable_path: Absolute path to Python 3.13 executable
        version: Python version as (major, minor, micro) tuple
        source: Installation source (package_manager, manual_install, unknown)
        distribution: OS distribution name (e.g., 'Ubuntu', 'macOS (Apple Silicon)')
        is_valid: True if Python is 3.13.x and executable exists
        in_virtualenv: True if currently running in virtual environment
        venv_base_python: Base Python path if in venv, None otherwise

    Examples:
        >>> env = PythonEnvironment(
        ...     executable_path=Path("/usr/bin/python3.13"),
        ...     version=(3, 13, 0),
        ...     source="package_manager",
        ...     distribution="Ubuntu",
        ...     is_valid=True,
        ...     in_virtualenv=False,
        ...     venv_base_python=None
        ... )
        >>> env.version_string
        '3.13.0'
        >>> env.is_package_manager_install
        True
    """

    executable_path: Path = Field(
        ...,
        description="Absolute path to Python 3.13 executable"
    )

    version: tuple[int, int, int] = Field(
        ...,
        description="Python version as (major, minor, micro) tuple"
    )

    source: Literal["package_manager", "manual_install", "unknown"] = Field(
        ...,
        description="Installation source based on path location"
    )

    distribution: str = Field(
        ...,
        description="OS distribution (e.g., 'Ubuntu', 'macOS (Apple Silicon)')"
    )

    is_valid: bool = Field(
        ...,
        description="True if Python is 3.13.x and executable"
    )

    in_virtualenv: bool = Field(
        default=False,
        description="True if currently running in virtual environment"
    )

    venv_base_python: Path | None = Field(
        default=None,
        description="Base Python path if in venv, None otherwise"
    )

    @field_validator("version")
    @classmethod
    def validate_version_313(cls, v: tuple[int, int, int]) -> tuple[int, int, int]:
        """Ensure version is Python 3.13.x.

        Args:
            v: Version tuple (major, minor, micro)

        Returns:
            Validated version tuple

        Raises:
            ValueError: If version is not 3.13.x
        """
        if v[:2] != (3, 13):
            raise ValueError(f"Python version must be 3.13.x, got {v[0]}.{v[1]}.{v[2]}")
        return v

    @field_validator("executable_path")
    @classmethod
    def validate_path_exists(cls, v: Path) -> Path:
        """Ensure Python executable exists.

        Args:
            v: Path to Python executable

        Returns:
            Validated path

        Raises:
            ValueError: If path doesn't exist or is not a file
        """
        if not v.exists():
            raise ValueError(f"Python executable not found: {v}")
        if not v.is_file():
            raise ValueError(f"Python path is not a file: {v}")
        return v

    @property
    def version_string(self) -> str:
        """Format version as string (e.g., '3.13.0').

        Returns:
            Version string in format 'major.minor.micro'
        """
        return f"{self.version[0]}.{self.version[1]}.{self.version[2]}"

    @property
    def is_package_manager_install(self) -> bool:
        """Check if Python from package manager.

        Returns:
            True if source is 'package_manager'
        """
        return self.source == "package_manager"

    model_config = {
        "frozen": True,  # Immutable after creation
        "str_strip_whitespace": True
    }


class UVConfiguration(BaseModel):
    """UV package manager configuration for Python enforcement.

    Represents UV's project-local configuration with constitutional compliance status.
    This model is mutable and can be updated as configuration changes are detected.

    Attributes:
        config_file_path: Path to uv.toml or pyproject.toml config file
        python_downloads: Python download policy from config
        python_preference: Python preference setting from config
        python_version_pinned: Content of .python-version file if exists
        is_compliant: True if configuration meets constitutional requirements
        compliance_violations: List of compliance violations (empty if compliant)

    Examples:
        >>> config = UVConfiguration(
        ...     config_file_path=Path("/home/user/project/uv.toml"),
        ...     python_downloads="never",
        ...     python_preference="only-system",
        ...     python_version_pinned="3.13",
        ...     is_compliant=False,
        ...     compliance_violations=[]
        ... )
        >>> config.check_compliance()
        >>> config.is_compliant
        True
    """

    config_file_path: Path = Field(
        ...,
        description="Path to uv.toml or pyproject.toml config file"
    )

    python_downloads: Literal["automatic", "manual", "never", None] = Field(
        default=None,
        description="Python download policy from config"
    )

    python_preference: Literal[
        "only-managed", "managed", "system", "only-system", None
    ] = Field(
        default=None,
        description="Python preference setting from config"
    )

    python_version_pinned: str | None = Field(
        default=None,
        description="Content of .python-version file if exists"
    )

    is_compliant: bool = Field(
        ...,
        description="True if configuration meets constitutional requirements"
    )

    compliance_violations: list[str] = Field(
        default_factory=list,
        description="List of compliance violations (empty if compliant)"
    )

    @field_validator("config_file_path")
    @classmethod
    def validate_config_exists(cls, v: Path) -> Path:
        """Ensure config file exists.

        Args:
            v: Path to config file

        Returns:
            Validated path

        Raises:
            ValueError: If config file doesn't exist
        """
        if not v.exists():
            raise ValueError(f"UV config file not found: {v}")
        return v

    @property
    def prevents_python_downloads(self) -> bool:
        """Check if Python downloads are disabled.

        Returns:
            True if python_downloads is 'manual' or 'never'
        """
        return self.python_downloads in ("manual", "never")

    @property
    def uses_only_system_python(self) -> bool:
        """Check if UV is configured to use only system Python.

        Returns:
            True if python_preference is 'only-system'
        """
        return self.python_preference == "only-system"

    @property
    def has_python_version_pin(self) -> bool:
        """Check if .python-version file exists.

        Returns:
            True if python_version_pinned is not None
        """
        return self.python_version_pinned is not None

    def check_compliance(self) -> None:
        """Validate compliance and populate violations list.

        Checks constitutional requirements (FR-002, FR-003) and updates
        is_compliant and compliance_violations fields accordingly.

        Side Effects:
            - Updates self.compliance_violations with any violations found
            - Updates self.is_compliant based on violations count
        """
        violations = []

        # FR-003: Must prevent Python installation
        if not self.prevents_python_downloads:
            violations.append(
                f"UV allows Python downloads (python-downloads={self.python_downloads}). "
                f"Must be 'manual' or 'never'."
            )

        # FR-002: Must use only system Python
        if not self.uses_only_system_python:
            violations.append(
                f"UV not configured for system-only Python "
                f"(python-preference={self.python_preference}). "
                f"Must be 'only-system'."
            )

        # Recommended: .python-version file
        if not self.has_python_version_pin:
            violations.append(
                "Missing .python-version file to pin Python 3.13"
            )

        self.compliance_violations = violations
        self.is_compliant = len(violations) == 0

    model_config = {
        "validate_assignment": True  # Re-validate on field updates
    }


class ValidationResult(BaseModel):
    """Constitution compliance validation result.

    Represents the complete outcome of a constitution compliance validation,
    aggregating Python environment detection and UV configuration validation.

    Attributes:
        status: Overall validation status (PASS, FAIL, or ERROR)
        python_environment: Detected Python environment (None if detection failed)
        uv_configuration: UV configuration status (None if UV not found/configured)
        errors: Critical errors that prevented validation
        warnings: Non-critical issues found during validation
        checks_performed: List of validation checks executed
        timestamp: When validation was performed

    Examples:
        >>> result = ValidationResult(
        ...     status="PASS",
        ...     python_environment=env,
        ...     uv_configuration=config,
        ...     checks_performed=[
        ...         "Python 3.13 detected",
        ...         "UV configuration validated"
        ...     ]
        ... )
        >>> result.exit_code
        0
        >>> print(result.to_summary())
        ✓ PASS: System Python 3.13 enforcement validated...
    """

    status: Literal["PASS", "FAIL", "ERROR"] = Field(
        ...,
        description="Overall validation status"
    )

    python_environment: PythonEnvironment | None = Field(
        default=None,
        description="Detected Python environment (None if detection failed)"
    )

    uv_configuration: UVConfiguration | None = Field(
        default=None,
        description="UV configuration status (None if UV not found/configured)"
    )

    errors: list[str] = Field(
        default_factory=list,
        description="Critical errors that prevented validation"
    )

    warnings: list[str] = Field(
        default_factory=list,
        description="Non-critical issues found during validation"
    )

    checks_performed: list[str] = Field(
        default_factory=list,
        description="List of validation checks executed"
    )

    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When validation was performed"
    )

    @property
    def exit_code(self) -> int:
        """Get exit code for validation command.

        Returns:
            0 for PASS, 1 for FAIL, 2 for ERROR
        """
        return {
            "PASS": 0,   # Success
            "FAIL": 1,   # Validation failed (constitutional violation)
            "ERROR": 2   # Error during validation (e.g., UV not installed)
        }[self.status]

    @property
    def has_violations(self) -> bool:
        """Check if any compliance violations found.

        Returns:
            True if status is FAIL or UV configuration has violations
        """
        return (
            self.status == "FAIL"
            or (self.uv_configuration and not self.uv_configuration.is_compliant)
        )

    def to_summary(self) -> str:
        """Generate summary output (default validation output).

        Provides a concise single-line or few-line summary of the validation result.
        This is the default output format shown to users.

        Returns:
            Formatted summary string
        """
        if self.status == "PASS":
            assert self.python_environment is not None
            assert self.uv_configuration is not None
            return (
                f"✓ PASS: System Python 3.13 enforcement validated\n"
                f"  Python: {self.python_environment.executable_path} "
                f"({self.python_environment.version_string})\n"
                f"  UV Config: Compliant "
                f"(only-system, downloads={self.uv_configuration.python_downloads})"
            )
        elif self.status == "FAIL":
            violations = []
            if self.uv_configuration:
                violations.extend(self.uv_configuration.compliance_violations)
            violations_str = "\n  ".join(violations)
            return (
                f"✗ FAIL: Constitution violations detected\n"
                f"  {violations_str}"
            )
        else:  # ERROR
            errors_str = "\n  ".join(self.errors)
            return (
                f"✗ ERROR: Validation could not complete\n"
                f"  {errors_str}"
            )

    def to_verbose(self) -> str:
        """Generate verbose output (--verbose flag).

        Provides a detailed multi-section report including Python environment details,
        UV configuration, validation checks performed, warnings, and errors.

        Returns:
            Formatted verbose report string
        """
        lines = [
            "System Python Enforcement Validation Report",
            "=" * 44,
            ""
        ]

        # Python Environment section
        lines.append("Python Environment:")
        if self.python_environment:
            env = self.python_environment
            lines.append(f"  Executable: {env.executable_path}")
            lines.append(f"  Version: {env.version_string}")
            lines.append(f"  Source: {env.source.replace('_', ' ').title()}")
            lines.append(f"  Distribution: {env.distribution}")
            if env.in_virtualenv:
                lines.append(f"  Virtual Env: Yes (base: {env.venv_base_python})")
            else:
                lines.append("  Virtual Env: None")
        else:
            lines.append("  ✗ Python 3.13 not detected")

        lines.append("")

        # UV Configuration section
        lines.append("UV Configuration:")
        if self.uv_configuration:
            cfg = self.uv_configuration
            lines.append(f"  Config File: {cfg.config_file_path}")
            lines.append(
                f"  python-preference: {cfg.python_preference} "
                f"{'✓' if cfg.uses_only_system_python else '✗'}"
            )
            lines.append(
                f"  python-downloads: {cfg.python_downloads} "
                f"{'✓' if cfg.prevents_python_downloads else '✗'}"
            )
            lines.append(
                f"  .python-version: {cfg.python_version_pinned} "
                f"{'✓' if cfg.has_python_version_pin else '✗'}"
            )
        else:
            lines.append("  ✗ UV configuration not found")

        lines.append("")

        # Validation Checks section
        lines.append("Validation Checks:")
        for check in self.checks_performed:
            lines.append(f"  ✓ {check}")

        if self.warnings:
            lines.append("")
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  ⚠ {warning}")

        if self.errors:
            lines.append("")
            lines.append("Errors:")
            for error in self.errors:
                lines.append(f"  ✗ {error}")

        lines.append("")
        lines.append(f"Result: {self.status}")
        lines.append(f"Timestamp: {self.timestamp.isoformat()}")

        return "\n".join(lines)

    model_config = {
        "arbitrary_types_allowed": True  # For datetime
    }
