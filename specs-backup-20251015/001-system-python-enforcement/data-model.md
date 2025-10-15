# Data Model: System Python Enforcement

**Date**: 2025-10-15
**Feature**: System Python Enforcement (001)
**Purpose**: Define data structures for Python environment detection, UV configuration, and validation results

## Overview

This document defines the Pydantic v2 models used throughout the system Python enforcement feature.

## Core Entities

### 1. PythonEnvironment

Represents a detected Python 3.13 installation with validation status.

```python
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class PythonEnvironment(BaseModel):
    """System Python 3.13 environment configuration."""

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
        """Ensure version is Python 3.13.x."""
        if v[:2] != (3, 13):
            raise ValueError(f"Python version must be 3.13.x, got {v[0]}.{v[1]}.{v[2]}")
        return v

    @field_validator("executable_path")
    @classmethod
    def validate_path_exists(cls, v: Path) -> Path:
        """Ensure Python executable exists."""
        if not v.exists():
            raise ValueError(f"Python executable not found: {v}")
        if not v.is_file():
            raise ValueError(f"Python path is not a file: {v}")
        return v

    @property
    def version_string(self) -> str:
        """Format version as string (e.g., '3.13.0')."""
        return f"{self.version[0]}.{self.version[1]}.{self.version[2]}"

    @property
    def is_package_manager_install(self) -> bool:
        """Check if Python from package manager."""
        return self.source == "package_manager"

    model_config = {
        "frozen": True,  # Immutable after creation
        "str_strip_whitespace": True
    }
```

**Relationships**:
- Referenced by `ValidationResult` to store detected Python environment
- Used by `UVConfiguration` to verify Python path matches configured Python

**Lifecycle**:
1. **Detection**: Created by `find_system_python()` in `python_env.py`
2. **Validation**: `is_valid` field set based on version and path checks
3. **Storage**: Passed to validation command for reporting

### 2. UVConfiguration

Represents UV's project-local configuration with compliance status.

```python
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class UVConfiguration(BaseModel):
    """UV package manager configuration for Python enforcement."""

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
        """Ensure config file exists."""
        if not v.exists():
            raise ValueError(f"UV config file not found: {v}")
        return v

    @property
    def prevents_python_downloads(self) -> bool:
        """Check if Python downloads are disabled."""
        return self.python_downloads in ("manual", "never")

    @property
    def uses_only_system_python(self) -> bool:
        """Check if UV is configured to use only system Python."""
        return self.python_preference == "only-system"

    @property
    def has_python_version_pin(self) -> bool:
        """Check if .python-version file exists."""
        return self.python_version_pinned is not None

    def check_compliance(self) -> None:
        """Validate compliance and populate violations list."""
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
```

**Relationships**:
- Referenced by `ValidationResult` to store UV configuration status
- Depends on `PythonEnvironment` for verifying configured Python path

**Lifecycle**:
1. **Discovery**: Created by `validate_uv_config()` in `uv_config.py`
2. **Parsing**: Reads `uv.toml` or `pyproject.toml` to extract settings
3. **Compliance Check**: `check_compliance()` populates violations
4. **Reporting**: Passed to validation command for output

### 3. ValidationResult

Represents the complete constitution compliance validation outcome.

```python
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal

class ValidationResult(BaseModel):
    """Constitution compliance validation result."""

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
        """Get exit code for validation command."""
        return {
            "PASS": 0,   # Success
            "FAIL": 1,   # Validation failed (constitutional violation)
            "ERROR": 2   # Error during validation (e.g., UV not installed)
        }[self.status]

    @property
    def has_violations(self) -> bool:
        """Check if any compliance violations found."""
        return (
            self.status == "FAIL"
            or (self.uv_configuration and not self.uv_configuration.is_compliant)
        )

    def to_summary(self) -> str:
        """Generate summary output (default validation output)."""
        if self.status == "PASS":
            assert self.python_environment is not None
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
        """Generate verbose output (--verbose flag)."""
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
```

**Relationships**:
- Aggregates `PythonEnvironment` and `UVConfiguration`
- Returned by `validate_python_environment()` main orchestrator
- Consumed by CLI command handler for output generation

**Lifecycle**:
1. **Creation**: Built by validation orchestrator after all checks
2. **Population**: Fields set based on detection and validation results
3. **Output**: Converted to summary or verbose string for display
4. **Exit**: `exit_code` property used for command exit status

## Entity Relationship Diagram

```
ValidationResult
├── python_environment: PythonEnvironment?
│   ├── executable_path: Path
│   ├── version: (int, int, int)
│   ├── source: "package_manager" | "manual_install" | "unknown"
│   ├── distribution: str
│   ├── is_valid: bool
│   ├── in_virtualenv: bool
│   └── venv_base_python: Path?
│
├── uv_configuration: UVConfiguration?
│   ├── config_file_path: Path
│   ├── python_downloads: "automatic" | "manual" | "never" | None
│   ├── python_preference: "only-managed" | "managed" | "system" | "only-system" | None
│   ├── python_version_pinned: str?
│   ├── is_compliant: bool
│   └── compliance_violations: list[str]
│
├── status: "PASS" | "FAIL" | "ERROR"
├── errors: list[str]
├── warnings: list[str]
├── checks_performed: list[str]
└── timestamp: datetime
```

## Validation Rules

### PythonEnvironment Validation

| Rule | Field | Validation | Error Message |
|------|-------|------------|---------------|
| VR-001 | `version` | Must be (3, 13, x) | "Python version must be 3.13.x, got {version}" |
| VR-002 | `executable_path` | Must exist as file | "Python executable not found: {path}" |
| VR-003 | `source` | Derived from path | N/A (auto-determined) |
| VR-004 | `venv_base_python` | Must match system Python if in venv | "Virtual environment uses different Python version" |

### UVConfiguration Validation

| Rule | Field | Validation | Error Message |
|------|-------|------------|---------------|
| VR-101 | `python_downloads` | Must be "manual" or "never" | "UV allows Python downloads (python-downloads={value}). Must be 'manual' or 'never'." |
| VR-102 | `python_preference` | Must be "only-system" | "UV not configured for system-only Python (python-preference={value}). Must be 'only-system'." |
| VR-103 | `python_version_pinned` | Recommended to be "3.13" | "Missing .python-version file to pin Python 3.13" |
| VR-104 | `config_file_path` | Must exist | "UV config file not found: {path}" |

### ValidationResult Status Determination

| Condition | Status | Exit Code |
|-----------|--------|-----------|
| All checks pass, no violations | PASS | 0 |
| Python detected but violations found | FAIL | 1 |
| Python not found or UV not installed | ERROR | 2 |
| Critical error during validation | ERROR | 2 |

## State Transitions

### PythonEnvironment Lifecycle

```
[Detection] → [Created with is_valid=False]
              ↓
          [Version Check]
              ↓
          is_valid=True if version=(3,13,x)
              ↓
          [Immutable - frozen model]
```

### UVConfiguration Lifecycle

```
[Discovery] → [Created with is_compliant=False]
              ↓
          [Parse Config Files]
              ↓
          [check_compliance()]
              ↓
          is_compliant=True if no violations
              ↓
          [Mutable - allows field updates]
```

### ValidationResult Lifecycle

```
[Orchestrator Start]
    ↓
[Detect Python] → python_environment=PythonEnvironment
    ↓
[Check UV Config] → uv_configuration=UVConfiguration
    ↓
[Evaluate Status] → status = PASS | FAIL | ERROR
    ↓
[Generate Output] → to_summary() or to_verbose()
    ↓
[Exit with Code] → exit_code property
```

## Usage Examples

### Creating PythonEnvironment

```python
from pathlib import Path
from mcp_manager.models import PythonEnvironment

# Valid Python 3.13 from package manager
env = PythonEnvironment(
    executable_path=Path("/usr/bin/python3.13"),
    version=(3, 13, 0),
    source="package_manager",
    distribution="Ubuntu",
    is_valid=True,
    in_virtualenv=False,
    venv_base_python=None
)

print(env.version_string)  # "3.13.0"
print(env.is_package_manager_install)  # True
```

### Creating UVConfiguration

```python
from pathlib import Path
from mcp_manager.models import UVConfiguration

# Non-compliant UV config
config = UVConfiguration(
    config_file_path=Path("/home/user/project/uv.toml"),
    python_downloads="automatic",  # Violation!
    python_preference="managed",    # Violation!
    python_version_pinned="3.13",
    is_compliant=False,
    compliance_violations=[]
)

config.check_compliance()  # Populates violations
print(config.is_compliant)  # False
print(config.compliance_violations)  # ["UV allows Python downloads...", "UV not configured for system-only Python..."]
```

### Creating ValidationResult

```python
from mcp_manager.models import ValidationResult, PythonEnvironment, UVConfiguration

result = ValidationResult(
    status="PASS",
    python_environment=env,
    uv_configuration=config,
    checks_performed=[
        "Python 3.13 detected",
        "UV configuration validated",
        "No virtual environment conflicts"
    ]
)

print(result.exit_code)  # 0
print(result.to_summary())  # "✓ PASS: System Python 3.13 enforcement validated..."
```

## Summary

Three core Pydantic v2 models defined:
1. **PythonEnvironment**: Immutable Python installation representation
2. **UVConfiguration**: Mutable UV config with compliance checking
3. **ValidationResult**: Aggregated validation outcome with formatted output

All models include:
- Full type annotations
- Field validation via Pydantic validators
- Property methods for computed fields
- Clear state transition lifecycles
- Comprehensive error messages

Next: Define API contracts for validation command (Phase 1 continuation).
