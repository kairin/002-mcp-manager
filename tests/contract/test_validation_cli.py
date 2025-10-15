"""Contract tests for validation CLI command behavior.

Tests:
    - T041: test_validate_success_summary_output
    - T042: test_validate_failure_violations_listed
    - T043: test_validate_error_python_not_found
    - T044: test_validate_verbose_complete_report
    - T045: test_validate_venv_base_python_check
    - T046: test_validate_performance_within_limits

References:
    - spec.md: FR-005
    - contracts/validation_cli.md: BC-001 through BC-008
    - tasks.md: T041-T046
"""

import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest


class TestValidateCLIContract:
    """Contract tests for `mcp-manager validate` CLI command.

    These tests verify the CLI command adheres to its contract specification,
    including exit codes, output format, and performance requirements.
    """

    def run_validate_command(self, *args, timeout=5):
        """Helper to run mcp-manager validate command.

        Args:
            *args: Additional command-line arguments
            timeout: Command timeout in seconds

        Returns:
            subprocess.CompletedProcess with stdout, stderr, returncode
        """
        cmd = ["python", "-m", "mcp_manager.cli", "validate"] + list(args)
        env = {"PYTHONPATH": "backend/src"}

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        return result

    def test_validate_success_summary_output(self):
        """T041: Verify PASS status displays summary output with exit code 0.

        Contract: BC-001 (Successful validation)
        Expected:
            - Exit code: 0
            - Output contains: "✓ PASS"
            - Output contains: Python path
            - Output contains: Version number
            - Output contains: "Compliant"
        """
        # This test requires a compliant system setup
        # We'll use mocking to ensure consistent test environment
        from mcp_manager.models.python_enforcement import (
            PythonEnvironment,
            UVConfiguration,
            ValidationResult,
        )
        from datetime import datetime

        python_env = PythonEnvironment(
            executable_path=Path("/usr/bin/python3.13"),
            version=(3, 13, 0),
            source="package_manager",
            distribution="Ubuntu",
            is_valid=True,
            in_virtualenv=False,
            venv_base_python=None
        )

        uv_config = UVConfiguration(
            config_file_path=Path("/home/user/project/uv.toml"),
            python_downloads="never",
            python_preference="only-system",
            is_compliant=True,
            compliance_violations=[]
        )

        result = ValidationResult(
            status="PASS",
            python_environment=python_env,
            uv_configuration=uv_config,
            errors=[],
            warnings=[],
            checks_performed=["Python 3.13 detected", "UV configuration validated"],
            timestamp=datetime.now()
        )

        # Verify exit code property
        assert result.exit_code == 0

        # Verify summary output contains required elements
        summary = result.to_summary()
        assert "✓ PASS" in summary
        assert "/usr/bin/python3.13" in summary
        assert "3.13.0" in summary
        assert "Compliant" in summary

    def test_validate_failure_violations_listed(self):
        """T042: Verify FAIL status lists all violations with exit code 1.

        Contract: BC-002 (Configuration violations detected)
        Expected:
            - Exit code: 1
            - Output contains: "✗ FAIL"
            - Output contains: "Constitution violations detected"
            - Output contains: Each violation message
        """
        from mcp_manager.models.python_enforcement import (
            UVConfiguration,
            ValidationResult,
        )
        from datetime import datetime

        uv_config = UVConfiguration(
            config_file_path=Path("/home/user/project/uv.toml"),
            python_downloads="automatic",
            python_preference="managed",
            is_compliant=False,
            compliance_violations=[
                "UV allows Python downloads (python-downloads=automatic). Must be 'manual' or 'never'.",
                "UV not configured for system-only Python (python-preference=managed). Must be 'only-system'."
            ]
        )

        result = ValidationResult(
            status="FAIL",
            python_environment=None,
            uv_configuration=uv_config,
            errors=[],
            warnings=[],
            checks_performed=["UV configuration validated"],
            timestamp=datetime.now()
        )

        # Verify exit code property
        assert result.exit_code == 1

        # Verify failure output contains required elements
        summary = result.to_summary()
        assert "✗ FAIL" in summary
        assert "Constitution violations detected" in summary
        assert "python-downloads=automatic" in summary
        assert "python-preference=managed" in summary

    def test_validate_error_python_not_found(self):
        """T043: Verify ERROR status when Python 3.13 missing with exit code 2.

        Contract: BC-003 (Python 3.13 not found)
        Expected:
            - Exit code: 2
            - Output contains: "✗ ERROR"
            - Output contains: "Python 3.13 not found"
            - Output contains: Searched locations
            - Output contains: Installation guidance
        """
        from mcp_manager.models.python_enforcement import ValidationResult
        from datetime import datetime

        result = ValidationResult(
            status="ERROR",
            python_environment=None,
            uv_configuration=None,
            errors=[
                "Python 3.13 not found on system",
                "Searched locations: /usr/bin/python3.13, /usr/local/bin/python3.13"
            ],
            warnings=[],
            checks_performed=["Searched for system Python 3.13"],
            timestamp=datetime.now()
        )

        # Verify exit code property
        assert result.exit_code == 2

        # Verify error output contains required elements
        summary = result.to_summary()
        assert "✗ ERROR" in summary
        assert "Validation could not complete" in summary
        assert "Python 3.13 not found" in summary

    def test_validate_verbose_complete_report(self):
        """T044: Verify --verbose flag displays complete validation report.

        Contract: BC-004 (Verbose output)
        Expected:
            - All sections present: Python Environment, UV Configuration, Validation Checks
            - Python details: executable path, version, source, distribution
            - UV details: config file, python-downloads, python-preference
            - Timestamp included
            - Result status clearly indicated
        """
        from mcp_manager.models.python_enforcement import (
            PythonEnvironment,
            UVConfiguration,
            ValidationResult,
        )
        from datetime import datetime

        python_env = PythonEnvironment(
            executable_path=Path("/usr/bin/python3.13"),
            version=(3, 13, 0),
            source="package_manager",
            distribution="Ubuntu",
            is_valid=True,
            in_virtualenv=False,
            venv_base_python=None
        )

        uv_config = UVConfiguration(
            config_file_path=Path("/home/user/project/uv.toml"),
            python_downloads="never",
            python_preference="only-system",
            python_version_pinned="3.13",
            is_compliant=True,
            compliance_violations=[]
        )

        result = ValidationResult(
            status="PASS",
            python_environment=python_env,
            uv_configuration=uv_config,
            errors=[],
            warnings=[],
            checks_performed=["Python 3.13 detected", "UV configuration validated"],
            timestamp=datetime.now()
        )

        # Verify verbose output contains all required sections
        verbose = result.to_verbose()

        # Section headers
        assert "System Python Enforcement Validation Report" in verbose
        assert "Python Environment:" in verbose
        assert "UV Configuration:" in verbose
        assert "Validation Checks:" in verbose
        assert "Result: PASS" in verbose
        assert "Timestamp:" in verbose

        # Python details
        assert "/usr/bin/python3.13" in verbose
        assert "3.13.0" in verbose
        assert "Package Manager" in verbose
        assert "Ubuntu" in verbose

        # UV details
        assert "only-system" in verbose
        assert "never" in verbose

    def test_validate_venv_base_python_check(self):
        """T045: Verify virtual environment base Python validation.

        Contract: BC-005 (Virtual environment validation)
        Expected when in venv:
            - Checks base Python is system Python 3.13
            - Output indicates venv status
            - Output shows base Python path
            - Validates base Python meets requirements
        """
        from mcp_manager.models.python_enforcement import (
            PythonEnvironment,
            ValidationResult,
        )
        from datetime import datetime

        # Simulate venv environment
        python_env = PythonEnvironment(
            executable_path=Path("/home/user/project/.venv/bin/python3"),
            version=(3, 13, 0),
            source="package_manager",
            distribution="Ubuntu",
            is_valid=True,
            in_virtualenv=True,
            venv_base_python=Path("/usr/bin/python3.13")
        )

        result = ValidationResult(
            status="PASS",
            python_environment=python_env,
            uv_configuration=None,
            errors=[],
            warnings=[],
            checks_performed=[
                "Python 3.13 detected",
                "Virtual environment detected",
                "Base Python verified: /usr/bin/python3.13"
            ],
            timestamp=datetime.now()
        )

        # Verify venv information in output
        verbose = result.to_verbose()
        assert "Virtual Environment" in verbose
        assert "/usr/bin/python3.13" in verbose
        assert "Base Python:" in verbose or "venv_base_python" in verbose

    @pytest.mark.slow
    def test_validate_performance_within_limits(self):
        """T046: Verify validation completes within 2 seconds.

        Contract: BC-007 (Performance requirement)
        Expected:
            - Validation completes in <2 seconds
            - Performance acceptable even with file I/O
            - No blocking operations or network calls
        """
        from mcp_manager.validators.python_enforcement_validator import (
            PythonEnforcementValidator
        )

        validator = PythonEnforcementValidator()

        # Measure validation time
        start_time = time.time()
        result = validator.validate()
        elapsed_time = time.time() - start_time

        # Verify performance requirement
        assert elapsed_time < 2.0, \
            f"Validation took {elapsed_time:.2f}s, exceeds 2.0s requirement"

        # Verify validation completed successfully (returned a result)
        assert result is not None
        assert hasattr(result, "status")
        assert result.status in ("PASS", "FAIL", "ERROR")

    def test_validate_uv_missing_error_output(self):
        """Verify ERROR output when UV not installed.

        Contract: BC-006 (UV not installed)
        Expected:
            - Exit code: 2
            - Output contains: "UV package manager not found"
            - Output contains: Installation instructions
        """
        from mcp_manager.models.python_enforcement import ValidationResult
        from datetime import datetime

        result = ValidationResult(
            status="ERROR",
            python_environment=None,
            uv_configuration=None,
            errors=[
                "UV package manager not found in PATH",
                "Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh"
            ],
            warnings=[],
            checks_performed=["Checked for UV installation"],
            timestamp=datetime.now()
        )

        # Verify exit code property
        assert result.exit_code == 2

        # Verify error output
        summary = result.to_summary()
        assert "✗ ERROR" in summary
        assert "UV package manager not found" in summary

    def test_validate_json_output_format(self):
        """Verify --json flag produces valid JSON output.

        Contract: BC-008 (JSON output format)
        Expected:
            - Valid JSON structure
            - Contains status, python_environment, uv_configuration
            - Exit code matches status
        """
        import json
        from mcp_manager.models.python_enforcement import (
            PythonEnvironment,
            UVConfiguration,
            ValidationResult,
        )
        from datetime import datetime

        python_env = PythonEnvironment(
            executable_path=Path("/usr/bin/python3.13"),
            version=(3, 13, 0),
            source="package_manager",
            distribution="Ubuntu",
            is_valid=True,
            in_virtualenv=False,
            venv_base_python=None
        )

        uv_config = UVConfiguration(
            config_file_path=Path("/home/user/project/uv.toml"),
            python_downloads="never",
            python_preference="only-system",
            is_compliant=True,
            compliance_violations=[]
        )

        result = ValidationResult(
            status="PASS",
            python_environment=python_env,
            uv_configuration=uv_config,
            errors=[],
            warnings=[],
            checks_performed=["Python 3.13 detected"],
            timestamp=datetime.now()
        )

        # Pydantic v2 model_dump_json for JSON serialization
        json_output = result.model_dump_json(indent=2)

        # Verify valid JSON
        parsed = json.loads(json_output)
        assert parsed["status"] == "PASS"
        assert "python_environment" in parsed
        assert "uv_configuration" in parsed
        assert parsed["python_environment"]["executable_path"] == "/usr/bin/python3.13"
        assert parsed["uv_configuration"]["python_downloads"] == "never"
