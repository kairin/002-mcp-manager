"""UV configuration validator."""
from pathlib import Path

from ..models.validation_models import UVConfiguration, ValidationResult


class UVValidator:
    """Validates UV package manager configuration."""

    def __init__(self, python_version_file: Path = None):
        self.python_version_file = python_version_file or Path(".python-version")
        self.pyproject_path = Path("pyproject.toml")

    def validate_configuration(self) -> ValidationResult:
        """Validate UV configuration via .python-version file."""
        try:
            config = self._load_uv_config()

            if not config.is_valid:
                return ValidationResult(
                    check_name="uv_configuration",
                    passed=False,
                    message=f"UV configuration invalid: .python-version contains '{config.python_version}' (expected '3.13')",
                    details={"config": config.model_dump()},
                    severity="error",
                )

            return ValidationResult(
                check_name="uv_configuration",
                passed=True,
                message=f'UV configured correctly: .python-version = "{config.python_version}"',
                details={"config": config.model_dump()},
                severity="info",
            )
        except FileNotFoundError:
            return ValidationResult(
                check_name="uv_configuration",
                passed=False,
                message=f".python-version file not found at {self.python_version_file}",
                severity="error",
            )
        except Exception as e:
            return ValidationResult(
                check_name="uv_configuration",
                passed=False,
                message=f"UV config validation failed: {str(e)}",
                severity="error",
            )

    def _load_uv_config(self) -> UVConfiguration:
        """Load and parse UV configuration from .python-version file."""
        # Read .python-version file
        with self.python_version_file.open() as f:
            python_version = f.read().strip()

        # Check if version starts with "3.13"
        is_valid = python_version.startswith("3.13")

        return UVConfiguration(
            python_version_file=self.python_version_file,
            python_version=python_version if python_version else "NOT_CONFIGURED",
            config_source=self.pyproject_path,
            is_valid=is_valid,
        )
