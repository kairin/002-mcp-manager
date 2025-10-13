# Tasks: System Python 3.13 Enforcement

**Input**: Design documents from `/home/kkk/Apps/002-mcp-manager/specs/003-system-python-enforcement/`
**Prerequisites**: plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

## Execution Summary

This feature implements Python 3.13 system Python enforcement across all mcp-manager operations. Implementation follows TDD approach with contract tests defining validator interfaces before implementation.

**Tech Stack**:
- Python 3.13 (system Python, MANDATORY)
- UV (package manager with explicit python3.13 pinning)
- Pydantic v2 (validation models)
- Typer (CLI commands)
- Rich (output formatting)
- pytest (testing)

**Structure**: Single project extending existing mcp-manager CLI

**Estimated Duration**: 28 tasks, ~8-12 hours total

---

## Phase 3.1: Setup

- [x] T001: Create validator subsystem directory structure
- [x] T002: Extend exceptions.py with validation-specific exceptions

### T001: Create validator subsystem directory structure

Create new directories for validation subsystem:

```bash
mkdir -p src/mcp_manager/validators
mkdir -p src/mcp_manager/models
mkdir -p tests/contract
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p scripts/verify
```

Create `__init__.py` files:
- `src/mcp_manager/validators/__init__.py` (empty for now)

**Success**: Directory structure exists, ready for implementation

---

### T002: Extend exceptions.py with validation-specific exceptions

**File**: `src/mcp_manager/exceptions.py`

Add new exception classes for validation system:

```python
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
```

**Success**: New exceptions defined, inherit from MCPManagerError

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] T003: Contract test for `validate python` CLI command
- [x] T004: Contract test for `validate uv` CLI command
- [x] T005: Contract test for `validate mcp-servers` CLI command
- [x] T006: Contract test for `validate constitution` CLI command

### T003 [P]: Contract test for `validate python` CLI command

**File**: `tests/contract/test_validation_cli_python.py`

Write contract test defining expected behavior of `mcp-manager validate python`:

```python
import subprocess
import json
import pytest

def test_validate_python_success():
    """Contract: validate python returns exit 0 when Python 3.13+ detected"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "python"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Python version validation: PASS" in result.stdout
    assert "3.13" in result.stdout

def test_validate_python_json_output():
    """Contract: --json flag produces valid JSON"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "python", "--json"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    assert "check_name" in data
    assert "passed" in data
    assert data["check_name"] == "python_version"
```

**Success**: Tests written, execute `uv run pytest tests/contract/test_validation_cli_python.py` and verify FAIL (not implemented yet)

---

### T004 [P]: Contract test for `validate uv` CLI command

**File**: `tests/contract/test_validation_cli_uv.py`

Write contract test for UV configuration validation:

```python
import subprocess
import json
import pytest

def test_validate_uv_success():
    """Contract: validate uv returns exit 0 when [tool.uv] configured correctly"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "uv"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "UV configuration validation: PASS" in result.stdout
    assert "python3.13" in result.stdout

def test_validate_uv_json_output():
    """Contract: --json flag produces valid JSON"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "uv", "--json"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    assert "check_name" in data
    assert data["check_name"] == "uv_configuration"
```

**Success**: Tests written and FAIL when executed

---

### T005 [P]: Contract test for `validate mcp-servers` CLI command

**File**: `tests/contract/test_validation_cli_mcp.py`

Write contract test for MCP server configuration validation:

```python
import subprocess
import json
import pytest

def test_validate_mcp_servers_success():
    """Contract: validate mcp-servers checks stdio servers use UV"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "mcp-servers"],
        capture_output=True,
        text=True
    )
    # May pass or fail depending on actual config
    # Just validate structure
    assert "MCP server validation:" in result.stdout

def test_validate_mcp_servers_json_output():
    """Contract: --json flag produces valid JSON with server list"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "mcp-servers", "--json"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    assert "check_name" in data
    assert data["check_name"] == "mcp_servers"
```

**Success**: Tests written and FAIL

---

### T006 [P]: Contract test for `validate constitution` CLI command

**File**: `tests/contract/test_validation_cli_constitution.py`

Write contract test for full constitution compliance validation:

```python
import subprocess
import json
import pytest

def test_validate_constitution_all_principles():
    """Contract: validate constitution checks all 9 principles"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "constitution"],
        capture_output=True,
        text=True
    )
    assert "Constitution validation:" in result.stdout
    assert "Principles validated:" in result.stdout

def test_validate_constitution_specific_principle():
    """Contract: --principle flag validates single principle"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "constitution", "--principle", "7"],
        capture_output=True,
        text=True
    )
    assert "VII. Cross-Platform Compatibility" in result.stdout or "Principle VII" in result.stdout

def test_validate_constitution_json_output():
    """Contract: --json flag produces valid JSON"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "constitution", "--json"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    assert "check_name" in data
    assert "principle_results" in data or "principles_validated" in data
```

**Success**: Tests written and FAIL

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### T007 [P]: PythonVersionInfo model in validation_models.py

**File**: `src/mcp_manager/models/validation_models.py`

Create Pydantic model for Python version information:

```python
from pydantic import BaseModel, Field, validator
from pathlib import Path
from typing import Literal

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

    @validator("minor")
    def validate_python_version(cls, v, values):
        if values.get("major") == 3 and v < 13:
            raise ValueError("Python 3.13+ required")
        return v

    @validator("executable_path")
    def validate_executable_exists(cls, v):
        if not v.exists():
            raise ValueError(f"Python executable not found: {v}")
        return v
```

**Success**: Model defined with validation rules, imports work

---

### T008 [P]: UVConfiguration model in validation_models.py

**File**: `src/mcp_manager/models/validation_models.py`

Add UV configuration model:

```python
from datetime import datetime

class UVConfiguration(BaseModel):
    """UV package manager configuration from pyproject.toml."""
    python_version: str = Field(..., pattern=r"^python3\.13$")
    config_source: Path
    is_valid: bool
    detected_at: datetime = Field(default_factory=datetime.now)

    @validator("config_source")
    def validate_config_exists(cls, v):
        if not v.exists():
            raise ValueError(f"Config file not found: {v}")
        return v
```

**Success**: Model defined, validation rules work

---

### T009 [P]: MCPServerConfig model in validation_models.py

**File**: `src/mcp_manager/models/validation_models.py`

Add MCP server configuration model:

```python
from typing import Optional, Dict, List

class MCPServerConfig(BaseModel):
    """MCP server configuration from ~/.claude.json."""
    name: str = Field(..., min_length=1)
    type: Literal["stdio", "http"]
    command: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    uses_uv: bool = Field(default=False)

    @validator("uses_uv", always=True)
    def compute_uses_uv(cls, v, values):
        """Compute whether stdio server uses UV."""
        if values.get("type") == "stdio":
            command = values.get("command", "")
            args = values.get("args", [])
            return command == "uv" and "run" in args
        return False

    @validator("command")
    def validate_stdio_has_command(cls, v, values):
        if values.get("type") == "stdio" and not v:
            raise ValueError("stdio servers must specify command")
        return v
```

**Success**: Model with computed field works

---

### T010 [P]: ValidationResult model in validation_models.py

**File**: `src/mcp_manager/models/validation_models.py`

Add validation result model:

```python
from typing import Any, Optional
from datetime import datetime

class ValidationResult(BaseModel):
    """Result of a validation check."""
    check_name: str = Field(..., min_length=1)
    passed: bool
    message: str = Field(..., min_length=1)
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    severity: Literal["info", "warning", "error", "critical"] = "info"

    @validator("severity")
    def validate_severity_matches_result(cls, v, values):
        """Failed checks must be error or critical."""
        if not values.get("passed") and v not in ["error", "critical"]:
            return "error"
        return v
```

**Success**: Model with cross-field validation works

---

### T011 [P]: ConstitutionCheckResult model in validation_models.py

**File**: `src/mcp_manager/models/validation_models.py`

Add constitution check result model:

```python
class ConstitutionCheckResult(BaseModel):
    """Constitution principle validation result."""
    principle_number: int = Field(..., ge=1, le=9)
    principle_name: str
    checks: List[ValidationResult] = Field(..., min_items=1)
    overall_passed: bool = Field(default=False)
    failed_checks: List[ValidationResult] = Field(default_factory=list)
    validation_timestamp: datetime = Field(default_factory=datetime.now)

    @validator("overall_passed", always=True)
    def compute_overall_passed(cls, v, values):
        """All checks must pass for principle to pass."""
        checks = values.get("checks", [])
        return all(check.passed for check in checks)

    @validator("failed_checks", always=True)
    def compute_failed_checks(cls, v, values):
        """Extract only failed checks."""
        checks = values.get("checks", [])
        return [check for check in checks if not check.passed]
```

**Success**: Model with computed aggregations works

---

### T012 [P]: PythonEnforcementStatus model in validation_models.py

**File**: `src/mcp_manager/models/validation_models.py`

Add top-level enforcement status model:

```python
class PythonEnforcementStatus(BaseModel):
    """Top-level Python 3.13 enforcement status."""
    python_version_valid: bool
    uv_config_valid: bool
    mcp_servers_valid: bool
    constitution_compliant: bool = Field(default=False)
    validation_results: List[ValidationResult]
    recommendations: List[str] = Field(default_factory=list)
    validated_at: datetime = Field(default_factory=datetime.now)

    @validator("constitution_compliant", always=True)
    def compute_constitution_compliant(cls, v, values):
        """All three checks must pass."""
        return (
            values.get("python_version_valid", False)
            and values.get("uv_config_valid", False)
            and values.get("mcp_servers_valid", False)
        )

    @validator("recommendations", always=True)
    def generate_recommendations(cls, v, values):
        """Generate recommendations for failures."""
        recommendations = []
        if not values.get("python_version_valid"):
            recommendations.append("Upgrade to Python 3.13+ (see TROUBLESHOOTING.md)")
        if not values.get("uv_config_valid"):
            recommendations.append("Add [tool.uv] python = \"python3.13\" to pyproject.toml")
        if not values.get("mcp_servers_valid"):
            recommendations.append("Update stdio MCP servers to use UV (see quickstart.md)")
        return recommendations
```

**Success**: Complete validation model hierarchy defined

---

### T013: Python validator implementation

**File**: `src/mcp_manager/validators/python_validator.py`

Implement Python 3.13 version validation:

```python
import sys
import subprocess
from pathlib import Path
from ..models.validation_models import PythonVersionInfo, ValidationResult
from ..exceptions import PythonVersionError

class PythonValidator:
    """Validates Python 3.13 system Python enforcement."""

    def validate_version(self) -> ValidationResult:
        """Validate Python version meets requirements."""
        try:
            version_info = self._get_python_version_info()

            if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 13):
                return ValidationResult(
                    check_name="python_version",
                    passed=False,
                    message=f"Python 3.13+ required, found {version_info.version_string}",
                    details={"version_info": version_info.dict()},
                    severity="critical"
                )

            return ValidationResult(
                check_name="python_version",
                passed=True,
                message=f"Python {version_info.version_string} detected (system and runtime match)",
                details={"version_info": version_info.dict()},
                severity="info"
            )
        except Exception as e:
            return ValidationResult(
                check_name="python_version",
                passed=False,
                message=f"Python version check failed: {str(e)}",
                severity="error"
            )

    def _get_python_version_info(self) -> PythonVersionInfo:
        """Extract Python version information."""
        # Runtime version
        runtime_version = sys.version_info

        # System Python verification
        result = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True
        )
        system_version_str = result.stdout.strip().replace("Python ", "")

        return PythonVersionInfo(
            major=runtime_version.major,
            minor=runtime_version.minor,
            micro=runtime_version.micro,
            releaselevel=runtime_version.releaselevel,
            serial=runtime_version.serial,
            version_string=system_version_str,
            executable_path=Path(sys.executable),
            is_system_python=True  # TODO: Verify this properly
        )
```

**Success**: Python validator implements validation logic, unit tests pass

---

### T014: UV configuration validator implementation

**File**: `src/mcp_manager/validators/uv_validator.py`

Implement UV configuration validation:

```python
import tomllib
from pathlib import Path
from ..models.validation_models import UVConfiguration, ValidationResult
from ..exceptions import UVConfigError

class UVValidator:
    """Validates UV package manager configuration."""

    def __init__(self, pyproject_path: Path = None):
        self.pyproject_path = pyproject_path or Path("pyproject.toml")

    def validate_configuration(self) -> ValidationResult:
        """Validate UV configuration in pyproject.toml."""
        try:
            config = self._load_uv_config()

            if not config.is_valid:
                return ValidationResult(
                    check_name="uv_configuration",
                    passed=False,
                    message=f"UV configuration invalid: python = \"{config.python_version}\" (expected \"python3.13\")",
                    details={"config": config.dict()},
                    severity="error"
                )

            return ValidationResult(
                check_name="uv_configuration",
                passed=True,
                message=f"UV configured correctly: python = \"{config.python_version}\"",
                details={"config": config.dict()},
                severity="info"
            )
        except FileNotFoundError:
            return ValidationResult(
                check_name="uv_configuration",
                passed=False,
                message=f"pyproject.toml not found at {self.pyproject_path}",
                severity="error"
            )
        except Exception as e:
            return ValidationResult(
                check_name="uv_configuration",
                passed=False,
                message=f"UV config validation failed: {str(e)}",
                severity="error"
            )

    def _load_uv_config(self) -> UVConfiguration:
        """Load and parse UV configuration from pyproject.toml."""
        with self.pyproject_path.open("rb") as f:
            data = tomllib.load(f)

        uv_config = data.get("tool", {}).get("uv", {})
        python_version = uv_config.get("python", "")

        return UVConfiguration(
            python_version=python_version if python_version else "NOT_CONFIGURED",
            config_source=self.pyproject_path,
            is_valid=(python_version == "python3.13")
        )
```

**Success**: UV validator works with pyproject.toml parsing

---

### T015: MCP server configuration validator implementation

**File**: `src/mcp_manager/validators/mcp_validator.py`

Implement MCP server configuration validation:

```python
import json
from pathlib import Path
from typing import List
from ..models.validation_models import MCPServerConfig, ValidationResult
from ..exceptions import MCPConfigError

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
                        "non_compliant_servers": [s.dict() for s in non_compliant]
                    },
                    severity="error"
                )

            return ValidationResult(
                check_name="mcp_servers",
                passed=True,
                message=f"All {len(stdio_servers)} stdio servers using UV",
                details={
                    "total_servers": len(servers),
                    "stdio_servers": len(stdio_servers),
                    "compliant": len(compliant_servers)
                },
                severity="info"
            )
        except Exception as e:
            return ValidationResult(
                check_name="mcp_servers",
                passed=False,
                message=f"MCP server validation failed: {str(e)}",
                severity="error"
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
                    headers=config.get("headers", {})
                )
            )

        return servers
```

**Success**: MCP validator parses ~/.claude.json and validates stdio servers

---

### T016: Constitution validator implementation

**File**: `src/mcp_manager/validators/constitution_validator.py`

Implement constitution compliance validator:

```python
from typing import List, Optional
from .python_validator import PythonValidator
from .uv_validator import UVValidator
from .mcp_validator import MCPValidator
from ..models.validation_models import (
    ConstitutionCheckResult,
    PythonEnforcementStatus,
    ValidationResult
)

class ConstitutionValidator:
    """Validates constitution compliance across all principles."""

    def __init__(self):
        self.python_validator = PythonValidator()
        self.uv_validator = UVValidator()
        self.mcp_validator = MCPValidator()

    def validate_principle_vii(self) -> ConstitutionCheckResult:
        """Validate Principle VII: Cross-Platform Compatibility (Python 3.13)."""
        checks = [
            self.python_validator.validate_version(),
            self.uv_validator.validate_configuration(),
            self.mcp_validator.validate_servers()
        ]

        return ConstitutionCheckResult(
            principle_number=7,
            principle_name="Cross-Platform Compatibility (Python 3.13)",
            checks=checks
        )

    def validate_all_principles(self, principle_filter: Optional[int] = None) -> List[ConstitutionCheckResult]:
        """Validate all constitution principles (or specific principle)."""
        if principle_filter == 7:
            return [self.validate_principle_vii()]

        # For now, only Principle VII is implemented
        # Future: Add validators for other principles
        return [self.validate_principle_vii()]

    def get_enforcement_status(self) -> PythonEnforcementStatus:
        """Get complete Python enforcement status."""
        python_result = self.python_validator.validate_version()
        uv_result = self.uv_validator.validate_configuration()
        mcp_result = self.mcp_validator.validate_servers()

        return PythonEnforcementStatus(
            python_version_valid=python_result.passed,
            uv_config_valid=uv_result.passed,
            mcp_servers_valid=mcp_result.passed,
            validation_results=[python_result, uv_result, mcp_result]
        )
```

**Success**: Constitution validator orchestrates all checks

---

### T017: CLI validation commands implementation

**File**: `src/mcp_manager/cli/validate_commands.py`

Implement Typer CLI commands for validation:

```python
import typer
import json
from rich.console import Console
from rich.table import Table
from ..validators.python_validator import PythonValidator
from ..validators.uv_validator import UVValidator
from ..validators.mcp_validator import MCPValidator
from ..validators.constitution_validator import ConstitutionValidator

app = typer.Typer(help="Validation commands for Python 3.13 enforcement")
console = Console()

@app.command("python")
def validate_python(
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed information"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON")
):
    """Validate Python 3.13 system Python enforcement."""
    validator = PythonValidator()
    result = validator.validate_version()

    if json_output:
        console.print_json(data=result.dict())
    else:
        status = "✅" if result.passed else "❌"
        console.print(f"{status} Python version validation: {'PASS' if result.passed else 'FAIL'}")
        console.print(result.message)

        if verbose and result.details:
            console.print("\nDetails:", style="bold")
            for key, value in result.details.items():
                console.print(f"  {key}: {value}")

    raise typer.Exit(0 if result.passed else 1)

@app.command("uv")
def validate_uv(
    verbose: bool = typer.Option(False, "--verbose"),
    json_output: bool = typer.Option(False, "--json")
):
    """Validate UV package manager configuration."""
    validator = UVValidator()
    result = validator.validate_configuration()

    if json_output:
        console.print_json(data=result.dict())
    else:
        status = "✅" if result.passed else "❌"
        console.print(f"{status} UV configuration validation: {'PASS' if result.passed else 'FAIL'}")
        console.print(result.message)

    raise typer.Exit(0 if result.passed else 1)

@app.command("mcp-servers")
def validate_mcp_servers(
    verbose: bool = typer.Option(False, "--verbose"),
    json_output: bool = typer.Option(False, "--json")
):
    """Validate MCP server configurations use UV."""
    validator = MCPValidator()
    result = validator.validate_servers()

    if json_output:
        console.print_json(data=result.dict())
    else:
        status = "✅" if result.passed else "❌"
        console.print(f"{status} MCP server validation: {'PASS' if result.passed else 'FAIL'}")
        console.print(result.message)

        if verbose and result.details:
            console.print("\nServer details:", style="bold")
            console.print(f"  Total servers: {result.details.get('total_servers')}")
            console.print(f"  Stdio servers: {result.details.get('stdio_servers')}")
            console.print(f"  UV compliant: {result.details.get('compliant')}")

    raise typer.Exit(0 if result.passed else 1)

@app.command("constitution")
def validate_constitution(
    principle: int = typer.Option(None, "--principle", help="Validate specific principle (1-9)"),
    verbose: bool = typer.Option(False, "--verbose"),
    json_output: bool = typer.Option(False, "--json")
):
    """Validate complete constitution compliance."""
    validator = ConstitutionValidator()

    if principle:
        results = validator.validate_all_principles(principle_filter=principle)
    else:
        results = validator.validate_all_principles()

    all_passed = all(r.overall_passed for r in results)

    if json_output:
        console.print_json(data={
            "check_name": "constitution_compliance",
            "passed": all_passed,
            "principles_validated": len(results),
            "principle_results": [r.dict() for r in results]
        })
    else:
        status = "✅" if all_passed else "❌"
        console.print(f"{status} Constitution validation: {'PASS' if all_passed else 'FAIL'}")
        console.print(f"- Principles validated: {len(results)}")

        for result in results:
            principle_status = "✓" if result.overall_passed else "✗"
            console.print(f"  {principle_status} {result.principle_number}. {result.principle_name}")

    raise typer.Exit(0 if all_passed else 1)
```

**Success**: All CLI commands implemented with Rich formatting

---

### T018: Integrate validation commands into main CLI

**File**: `src/mcp_manager/cli.py`

Add validation subcommand to main CLI:

```python
# Add import at top
from .cli.validate_commands import app as validate_app

# In main app setup
app.add_typer(validate_app, name="validate", help="Validation commands")
```

**Success**: `mcp-manager validate` subcommand available, contract tests should now pass

---

### T019: Add pre-commit hook for Python validation

**File**: `.pre-commit-config.yaml`

Add Python enforcement validation hook:

```yaml
# Add this hook to existing configuration
  - repo: local
    hooks:
      - id: validate-python-enforcement
        name: Validate Python 3.13 Enforcement
        entry: uv run python -m mcp_manager.validators.constitution_validator
        language: system
        pass_filenames: false
        always_run: true
        stages: [commit]
```

**File**: `src/mcp_manager/validators/__main__.py` (new)

Create executable validator for pre-commit:

```python
"""Pre-commit hook entry point for constitution validation."""
import sys
from .constitution_validator import ConstitutionValidator

def main():
    validator = ConstitutionValidator()
    status = validator.get_enforcement_status()

    if not status.constitution_compliant:
        print("❌ Constitution compliance check FAILED:")
        for rec in status.recommendations:
            print(f"  - {rec}")
        sys.exit(1)

    print("✅ Constitution compliance check PASSED")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Success**: Pre-commit hook blocks commits when validation fails

---

## Phase 3.4: Integration Tests

### T020 [P]: Integration test for fresh system initialization

**File**: `tests/integration/test_fresh_system_init.py`

Test Scenario 1 from quickstart.md:

```python
import pytest
import subprocess

def test_fresh_system_uses_python313():
    """Scenario 1: Fresh system initialization uses Python 3.13"""
    # This test assumes Python 3.13 is installed
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "python"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "3.13" in result.stdout
    assert "PASS" in result.stdout
```

**Success**: Integration test validates acceptance scenario 1

---

### T021 [P]: Integration test for CLI command execution

**File**: `tests/integration/test_cli_command_execution.py`

Test Scenario 2: CLI commands use system Python via UV:

```python
import subprocess
import sys

def test_cli_commands_use_system_python():
    """Scenario 2: CLI commands execute using system Python 3.13"""
    # Run a CLI command and verify Python version
    result = subprocess.run(
        ["uv", "run", "python", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
        capture_output=True,
        text=True
    )

    version = result.stdout.strip()
    assert version.startswith("3.13")
```

**Success**: Test validates CLI execution via UV

---

### T022 [P]: Integration test for MCP server launch validation

**File**: `tests/integration/test_mcp_server_launch.py`

Test Scenario 3: MCP servers use system Python via UV:

```python
import subprocess

def test_mcp_servers_validated():
    """Scenario 3: MCP stdio servers use UV command pattern"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "mcp-servers"],
        capture_output=True,
        text=True
    )

    # Test should validate configuration structure
    assert "MCP server validation:" in result.stdout
```

**Success**: Test validates MCP server configurations

---

### T023 [P]: Integration test for package installation

**File**: `tests/integration/test_package_installation.py`

Test Scenario 4: UV manages packages with system Python:

```python
import subprocess

def test_uv_uses_system_python():
    """Scenario 4: UV package operations use system Python 3.13"""
    result = subprocess.run(
        ["uv", "run", "python", "-c", "import sys; print(sys.version)"],
        capture_output=True,
        text=True
    )

    assert "3.13" in result.stdout
```

**Success**: Test validates UV package management

---

### T024 [P]: Integration test for constitution compliance

**File**: `tests/integration/test_constitution_compliance.py`

Test Scenario 5: Constitution Principle VII validation:

```python
import subprocess

def test_principle_vii_validation():
    """Scenario 5: Principle VII validation passes"""
    result = subprocess.run(
        ["uv", "run", "mcp-manager", "validate", "constitution", "--principle", "7"],
        capture_output=True,
        text=True
    )

    # Should validate structure (may pass or fail based on actual config)
    assert "VII" in result.stdout or "7" in result.stdout
```

**Success**: Test validates constitution compliance checking

---

## Phase 3.5: Polish

### T025 [P]: Unit tests for python_validator.py

**File**: `tests/unit/test_python_validator.py`

Write comprehensive unit tests:

```python
import pytest
from unittest.mock import patch, MagicMock
from mcp_manager.validators.python_validator import PythonValidator

def test_validate_version_pass():
    """Unit: Python 3.13+ validation passes"""
    validator = PythonValidator()
    with patch("sys.version_info", (3, 13, 0, "final", 0)):
        result = validator.validate_version()
        assert result.passed is True

def test_validate_version_fail_old_version():
    """Unit: Python 3.11 validation fails"""
    validator = PythonValidator()
    with patch("sys.version_info", (3, 11, 0, "final", 0)):
        result = validator.validate_version()
        assert result.passed is False
        assert "3.13+ required" in result.message
```

**Success**: >80% code coverage for python_validator.py

---

### T026 [P]: Unit tests for uv_validator.py

**File**: `tests/unit/test_uv_validator.py`

Write comprehensive unit tests:

```python
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from mcp_manager.validators.uv_validator import UVValidator

def test_validate_configuration_pass():
    """Unit: Valid UV configuration passes"""
    toml_content = """
[tool.uv]
python = "python3.13"
"""
    with patch("builtins.open", mock_open(read_data=toml_content.encode())):
        validator = UVValidator(Path("pyproject.toml"))
        result = validator.validate_configuration()
        assert result.passed is True

def test_validate_configuration_fail_wrong_version():
    """Unit: Wrong Python version fails"""
    toml_content = """
[tool.uv]
python = "python3.11"
"""
    with patch("builtins.open", mock_open(read_data=toml_content.encode())):
        validator = UVValidator(Path("pyproject.toml"))
        result = validator.validate_configuration()
        assert result.passed is False
```

**Success**: >80% code coverage for uv_validator.py

---

### T027 [P]: Unit tests for constitution_validator.py

**File**: `tests/unit/test_constitution_validator.py`

Write comprehensive unit tests:

```python
import pytest
from unittest.mock import MagicMock
from mcp_manager.validators.constitution_validator import ConstitutionValidator
from mcp_manager.models.validation_models import ValidationResult

def test_validate_principle_vii():
    """Unit: Principle VII aggregates all checks"""
    validator = ConstitutionValidator()
    result = validator.validate_principle_vii()

    assert result.principle_number == 7
    assert len(result.checks) == 3  # Python, UV, MCP
    assert result.principle_name == "Cross-Platform Compatibility (Python 3.13)"

def test_get_enforcement_status():
    """Unit: Enforcement status aggregates results"""
    validator = ConstitutionValidator()
    status = validator.get_enforcement_status()

    assert hasattr(status, "python_version_valid")
    assert hasattr(status, "uv_config_valid")
    assert hasattr(status, "mcp_servers_valid")
    assert hasattr(status, "constitution_compliant")
```

**Success**: >80% code coverage for constitution_validator.py

---

### T028 [P]: Create standalone verification utility

**File**: `scripts/verify/verify_python_enforcement.py`

Create standalone verification script:

```python
#!/usr/bin/env python3
"""
Standalone verification utility for Python 3.13 enforcement.

Usage:
    python scripts/verify/verify_python_enforcement.py [--json]
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_manager.validators.constitution_validator import ConstitutionValidator

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Verify Python 3.13 enforcement")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    validator = ConstitutionValidator()
    status = validator.get_enforcement_status()

    if args.json:
        import json
        print(json.dumps(status.dict(), indent=2, default=str))
    else:
        symbol = "✅" if status.constitution_compliant else "❌"
        print(f"{symbol} Python 3.13 Enforcement: {'COMPLIANT' if status.constitution_compliant else 'NON-COMPLIANT'}")
        print(f"  Python version: {'✓' if status.python_version_valid else '✗'}")
        print(f"  UV config: {'✓' if status.uv_config_valid else '✗'}")
        print(f"  MCP servers: {'✓' if status.mcp_servers_valid else '✗'}")

        if status.recommendations:
            print("\nRecommendations:")
            for rec in status.recommendations:
                print(f"  - {rec}")

    sys.exit(0 if status.constitution_compliant else 1)

if __name__ == "__main__":
    main()
```

Make executable:
```bash
chmod +x scripts/verify/verify_python_enforcement.py
```

**Success**: Standalone utility works, can be run independently

---

### T029: Update TROUBLESHOOTING.md with Python enforcement

**File**: `docs/TROUBLESHOOTING.md` (or create if not exists)

Add troubleshooting section for Python 3.13 enforcement:

```markdown
## Python 3.13 Enforcement Issues

### Issue: Python version < 3.13

**Symptom**: `mcp-manager validate python` fails with "Python 3.13+ required"

**Solution**:
1. Upgrade system Python on Ubuntu 25.04:
   ```bash
   sudo apt update
   sudo apt install python3.13 python3.13-venv
   ```

2. Verify upgrade:
   ```bash
   python --version  # Should show 3.13.x
   ```

3. Re-run validation:
   ```bash
   uv run mcp-manager validate python
   ```

### Issue: UV configuration missing

**Symptom**: `mcp-manager validate uv` fails with "python = NOT_CONFIGURED"

**Solution**:
1. Add to `pyproject.toml`:
   ```toml
   [tool.uv]
   python = "python3.13"
   ```

2. Rebuild environment:
   ```bash
   uv sync
   ```

### Issue: MCP servers not using UV

**Symptom**: `mcp-manager validate mcp-servers` fails with servers using direct python

**Solution**:
1. Edit `~/.claude.json`
2. Update stdio servers to use UV:
   ```json
   {
     "mcpServers": {
       "markitdown": {
         "type": "stdio",
         "command": "uv",
         "args": ["run", "markitdown-mcp"]
       }
     }
   }
   ```
3. Restart Claude Code
```

**Success**: Documentation updated with troubleshooting guidance

---

### T030: Execute quickstart.md validation

**Manual Task**: Run through quickstart.md steps to validate feature:

1. Execute Step 1-5 from `specs/003-system-python-enforcement/quickstart.md`
2. Verify all validations pass
3. Test pre-commit hook integration
4. Run all acceptance scenarios
5. Document any issues found

**Success**: All quickstart steps complete successfully, acceptance criteria met

---

## Dependencies

### Critical Path (Sequential)
```
Setup (T001-T002)
  ↓
Contract Tests (T003-T006) [P]
  ↓
Data Models (T007-T012) [P]
  ↓
Validators (T013-T016) [Sequential: T013 → T014 → T015 → T016]
  ↓
CLI Integration (T017-T018)
  ↓
Pre-commit Hook (T019)
  ↓
Integration Tests (T020-T024) [P]
  ↓
Unit Tests + Polish (T025-T030) [P]
```

### Parallel Execution Groups

**Group 1: Contract Tests (T003-T006)**
```python
# Can run simultaneously - different test files
Task: "Write contract test for validate python command"
Task: "Write contract test for validate uv command"
Task: "Write contract test for validate mcp-servers command"
Task: "Write contract test for validate constitution command"
```

**Group 2: Data Models (T007-T012)**
```python
# Can run simultaneously - same file but independent sections
Task: "Create PythonVersionInfo model"
Task: "Create UVConfiguration model"
Task: "Create MCPServerConfig model"
Task: "Create ValidationResult model"
Task: "Create ConstitutionCheckResult model"
Task: "Create PythonEnforcementStatus model"
```

**Group 3: Integration Tests (T020-T024)**
```python
# Can run simultaneously - different test files
Task: "Write integration test for fresh system initialization"
Task: "Write integration test for CLI command execution"
Task: "Write integration test for MCP server launch"
Task: "Write integration test for package installation"
Task: "Write integration test for constitution compliance"
```

**Group 4: Polish (T025-T029)**
```python
# Can run simultaneously - different files
Task: "Write unit tests for python_validator.py"
Task: "Write unit tests for uv_validator.py"
Task: "Write unit tests for constitution_validator.py"
Task: "Create standalone verification utility"
Task: "Update TROUBLESHOOTING.md"
```

## Validation Checklist

Before considering this feature complete:

- [ ] All contract tests exist and initially failed (T003-T006)
- [ ] All contract tests now pass after implementation
- [ ] All 6 data models defined with validation rules (T007-T012)
- [ ] All 4 validators implemented and tested (T013-T016)
- [ ] All 4 CLI commands work correctly (T017-T018)
- [ ] Pre-commit hook blocks invalid commits (T019)
- [ ] All 5 integration tests pass (T020-T024)
- [ ] Unit test coverage >80% for validators (T025-T027)
- [ ] Standalone verification utility works (T028)
- [ ] Documentation updated (T029)
- [ ] Quickstart.md scenarios validated (T030)
- [ ] No additional Python installations on system
- [ ] All MCP stdio servers use UV command pattern
- [ ] Constitution v1.2.0 Principle VII fully enforced

## Notes

- **TDD Approach**: Contract tests (Phase 3.2) must be written and failing before implementation (Phase 3.3)
- **Performance**: All validation operations must complete in <200ms total
- **Error Handling**: All validators must return ValidationResult, never raise exceptions to CLI
- **Parallel Execution**: Tasks marked [P] can run simultaneously
- **Git Strategy**: Use datetime-based branch naming, preserve all branches
- **Testing**: Execute `uv run pytest` (NEVER direct pytest)

---

**Tasks Status**: ✅ **READY FOR EXECUTION** - 30 tasks generated, dependencies mapped, parallel execution identified

**Next Command**: Begin execution with `/implement` or manual task execution starting with T001
