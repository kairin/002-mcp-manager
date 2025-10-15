"""Validation orchestrator for System Python Enforcement.

This module provides the main validation orchestrator that coordinates
Python environment detection, UV configuration validation, and result
reporting for the `mcp-manager validate` command.

References:
    - Spec: specs/002-system-python-enforcement/spec.md
    - Contract: specs/002-system-python-enforcement/contracts/validation_cli.md
    - Tasks: T021, T026
"""

from pathlib import Path

from ..models.python_enforcement import (
    PythonEnvironment,
    UVConfiguration,
    ValidationResult,
)
from ..python_env import (
    detect_distribution,
    find_system_python,
    get_installation_source,
    get_python_version,
    get_venv_base_python,
    is_python_313,
)
from ..uv_config import check_uv_installed, get_uv_config_path, validate_uv_config


def validate_python_environment(project_root: Path | None = None) -> ValidationResult:
    """Validate complete Python 3.13 and UV configuration compliance.

    This orchestrator performs comprehensive validation:
    1. Detects system Python 3.13 installation
    2. Validates UV configuration compliance
    3. Checks virtual environment compatibility (if applicable)
    4. Builds complete ValidationResult with all findings

    Implements T021: Validation orchestrator that calls find_system_python(),
    validate_uv_config(), and builds ValidationResult model.

    Implements T026: Virtual environment detection and base Python validation.

    Args:
        project_root: Project root directory for UV config lookup.
                     Defaults to current working directory if None.

    Returns:
        ValidationResult: Complete validation outcome with status, environment
                         details, UV configuration, errors, and warnings.

    Exit Status (via ValidationResult.exit_code property):
        0 (PASS): All validation checks passed
        1 (FAIL): Validation failed, constitutional violations detected
        2 (ERROR): Validation error, unable to complete checks

    Examples:
        >>> result = validate_python_environment()
        >>> print(result.to_summary())
        ✓ PASS: System Python 3.13 enforcement validated
          Python: /usr/bin/python3.13 (3.13.0)
          UV Config: Compliant (only-system, downloads=never)

        >>> # In CI/CD
        >>> result = validate_python_environment()
        >>> sys.exit(result.exit_code)

    References:
        - Contract: validation_cli.md lines 130-187 (behavior contracts)
        - Data Model: data-model.md lines 378-389 (ValidationResult lifecycle)
        - Task: T021 (orchestrator implementation)
        - Task: T026 (venv detection)
    """
    if project_root is None:
        project_root = Path.cwd()

    checks_performed = []
    errors = []
    warnings = []

    # Step 1: Detect system Python 3.13 (T021)
    python_path = find_system_python()
    checks_performed.append("Searched for system Python 3.13")

    if python_path is None:
        errors.append("Python 3.13 not found on system")
        errors.append(
            "Searched locations: /usr/bin/python3.13, /usr/local/bin/python3.13, "
            "/opt/homebrew/bin/python3.13"
        )
        return ValidationResult(
            status="ERROR",
            python_environment=None,
            uv_configuration=None,
            errors=errors,
            warnings=warnings,
            checks_performed=checks_performed,
        )

    # Verify it's actually Python 3.13
    if not is_python_313(python_path):
        version = get_python_version(python_path)
        version_str = f"{version[0]}.{version[1]}.{version[2]}" if version else "unknown"
        errors.append(
            f"Python at {python_path} is version {version_str}, not 3.13.x as required"
        )
        return ValidationResult(
            status="ERROR",
            python_environment=None,
            uv_configuration=None,
            errors=errors,
            warnings=warnings,
            checks_performed=checks_performed,
        )

    checks_performed.append("Python 3.13 detected")

    # Get Python version and installation details
    version = get_python_version(python_path)
    if version is None:
        errors.append(f"Could not determine version for Python at {python_path}")
        return ValidationResult(
            status="ERROR",
            python_environment=None,
            uv_configuration=None,
            errors=errors,
            warnings=warnings,
            checks_performed=checks_performed,
        )

    distribution = detect_distribution()
    source = get_installation_source(python_path)

    # Step 2: Virtual environment detection (T026)
    venv_base_python = get_venv_base_python()
    in_virtualenv = venv_base_python is not None
    checks_performed.append("Checked for virtual environment")

    if in_virtualenv:
        # Validate that venv is based on system Python 3.13
        if venv_base_python and not is_python_313(venv_base_python):
            base_version = get_python_version(venv_base_python)
            base_version_str = (
                f"{base_version[0]}.{base_version[1]}.{base_version[2]}"
                if base_version
                else "unknown"
            )
            errors.append(
                f"Virtual environment uses Python {base_version_str}, "
                f"not system Python 3.13 (base: {venv_base_python})"
            )
            # Create PythonEnvironment anyway for reporting
            python_environment = PythonEnvironment(
                executable_path=python_path,
                version=version,
                source=source,
                distribution=distribution,
                is_valid=False,
                in_virtualenv=in_virtualenv,
                venv_base_python=venv_base_python,
            )
            return ValidationResult(
                status="FAIL",
                python_environment=python_environment,
                uv_configuration=None,
                errors=errors,
                warnings=warnings,
                checks_performed=checks_performed,
            )
        else:
            checks_performed.append(
                "Virtual environment based on system Python 3.13 (valid)"
            )

    # Create PythonEnvironment model
    python_environment = PythonEnvironment(
        executable_path=python_path,
        version=version,
        source=source,
        distribution=distribution,
        is_valid=True,
        in_virtualenv=in_virtualenv,
        venv_base_python=venv_base_python,
    )
    checks_performed.append(f"Python from approved path ({python_path.parent})")

    # Step 3: Check UV installation
    if not check_uv_installed():
        errors.append("UV package manager not found in PATH")
        return ValidationResult(
            status="ERROR",
            python_environment=python_environment,
            uv_configuration=None,
            errors=errors,
            warnings=warnings,
            checks_performed=checks_performed,
        )

    checks_performed.append("UV package manager detected")

    # Step 4: Validate UV configuration (T021)
    uv_config_dict = validate_uv_config(project_root)
    checks_performed.append("Validated UV configuration")

    config_file_path = get_uv_config_path(project_root)
    if config_file_path is None:
        warnings.append("No UV configuration file found (uv.toml or pyproject.toml)")
        # Create minimal UVConfiguration
        uv_configuration = UVConfiguration(
            config_file_path=project_root / "uv.toml",  # Expected location
            python_downloads=None,
            python_preference=None,
            python_version_pinned=uv_config_dict.get("python_version_pinned"),
            is_compliant=False,
            compliance_violations=["UV configuration file not found"],
        )
    else:
        # Create UVConfiguration model
        uv_configuration = UVConfiguration(
            config_file_path=config_file_path,
            python_downloads=uv_config_dict.get("python_downloads"),
            python_preference=uv_config_dict.get("python_preference"),
            python_version_pinned=uv_config_dict.get("python_version_pinned"),
            is_compliant=False,  # Will be set by check_compliance()
            compliance_violations=[],
        )

        # Run compliance check
        uv_configuration.check_compliance()
        checks_performed.append("UV compliance check completed")

    # Step 5: Determine final status
    if uv_configuration.is_compliant:
        checks_performed.append("UV prevents Python downloads")
        checks_performed.append("UV uses system Python only")
        if not in_virtualenv:
            checks_performed.append("No virtual environment conflicts")

        return ValidationResult(
            status="PASS",
            python_environment=python_environment,
            uv_configuration=uv_configuration,
            errors=[],
            warnings=warnings,
            checks_performed=checks_performed,
        )
    else:
        # Validation failed due to UV configuration violations
        return ValidationResult(
            status="FAIL",
            python_environment=python_environment,
            uv_configuration=uv_configuration,
            errors=[],
            warnings=warnings,
            checks_performed=checks_performed,
        )
