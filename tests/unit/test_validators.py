"""Unit tests for validation orchestrator.

Tests:
    - T037: test_validation_result_exit_codes

References:
    - spec.md: FR-005
    - data-model.md: ValidationResult model
    - contracts/validation_cli.md: Exit codes 0/1/2
    - tasks.md: T037
"""

from datetime import datetime
from pathlib import Path

import pytest

from mcp_manager.models.python_enforcement import (
    PythonEnvironment,
    UVConfiguration,
    ValidationResult,
)


class TestValidationResultExitCodes:
    """Test ValidationResult.exit_code property.

    Test T037: Verify exit_code property returns 0/1/2 correctly.
    """

    def test_validation_result_exit_code_pass(self):
        """T037: Verify exit_code=0 for PASS status."""
        result = ValidationResult(
            status="PASS",
            python_environment=None,
            uv_configuration=None,
            errors=[],
            warnings=[],
            checks_performed=["Test check"],
            timestamp=datetime.now()
        )

        assert result.exit_code == 0

    def test_validation_result_exit_code_fail(self):
        """T037: Verify exit_code=1 for FAIL status."""
        result = ValidationResult(
            status="FAIL",
            python_environment=None,
            uv_configuration=None,
            errors=[],
            warnings=[],
            checks_performed=["Test check"],
            timestamp=datetime.now()
        )

        assert result.exit_code == 1

    def test_validation_result_exit_code_error(self):
        """T037: Verify exit_code=2 for ERROR status."""
        result = ValidationResult(
            status="ERROR",
            python_environment=None,
            uv_configuration=None,
            errors=["Python 3.13 not found"],
            warnings=[],
            checks_performed=["Test check"],
            timestamp=datetime.now()
        )

        assert result.exit_code == 2

    def test_validation_result_has_violations_true(self):
        """Verify has_violations property returns True for FAIL status."""
        # Create non-compliant UV config
        uv_config = UVConfiguration(
            config_file_path=Path("/tmp/uv.toml"),
            python_downloads="automatic",
            python_preference="managed",
            is_compliant=False,
            compliance_violations=["UV allows Python downloads"]
        )

        result = ValidationResult(
            status="FAIL",
            python_environment=None,
            uv_configuration=uv_config,
            errors=[],
            warnings=[],
            checks_performed=["Test check"],
            timestamp=datetime.now()
        )

        assert result.has_violations is True

    def test_validation_result_has_violations_false(self):
        """Verify has_violations property returns False for PASS status."""
        # Create compliant UV config
        uv_config = UVConfiguration(
            config_file_path=Path("/tmp/uv.toml"),
            python_downloads="never",
            python_preference="only-system",
            is_compliant=True,
            compliance_violations=[]
        )

        result = ValidationResult(
            status="PASS",
            python_environment=None,
            uv_configuration=uv_config,
            errors=[],
            warnings=[],
            checks_performed=["Test check"],
            timestamp=datetime.now()
        )

        assert result.has_violations is False

    def test_validation_result_to_summary_pass(self):
        """Verify to_summary() output for PASS status."""
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
            config_file_path=Path("/tmp/uv.toml"),
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
            checks_performed=["Test check"],
            timestamp=datetime.now()
        )

        summary = result.to_summary()

        assert "✓ PASS" in summary
        assert "/usr/bin/python3.13" in summary
        assert "3.13.0" in summary
        assert "Compliant" in summary

    def test_validation_result_to_summary_fail(self):
        """Verify to_summary() output for FAIL status."""
        uv_config = UVConfiguration(
            config_file_path=Path("/tmp/uv.toml"),
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
            checks_performed=["Test check"],
            timestamp=datetime.now()
        )

        summary = result.to_summary()

        assert "✗ FAIL" in summary
        assert "Constitution violations detected" in summary
        assert "python-downloads=automatic" in summary
        assert "python-preference=managed" in summary

    def test_validation_result_to_summary_error(self):
        """Verify to_summary() output for ERROR status."""
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

        summary = result.to_summary()

        assert "✗ ERROR" in summary
        assert "Validation could not complete" in summary
        assert "Python 3.13 not found" in summary

    def test_validation_result_to_verbose_contains_all_sections(self):
        """Verify to_verbose() includes all required sections."""
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
            config_file_path=Path("/tmp/uv.toml"),
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

        verbose = result.to_verbose()

        # Verify all required sections present
        assert "System Python Enforcement Validation Report" in verbose
        assert "Python Environment:" in verbose
        assert "UV Configuration:" in verbose
        assert "Validation Checks:" in verbose
        assert "Result: PASS" in verbose
        assert "Timestamp:" in verbose
        # Verify specific details
        assert "/usr/bin/python3.13" in verbose
        assert "3.13.0" in verbose
        assert "Package Manager" in verbose
        assert "Ubuntu" in verbose
        assert "only-system" in verbose
        assert "never" in verbose
