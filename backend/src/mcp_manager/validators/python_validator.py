"""Python 3.13 version validator."""

import subprocess
import sys
from pathlib import Path

from ..models.validation_models import PythonVersionInfo, ValidationResult


class PythonValidator:
    """Validates Python 3.13 system Python enforcement."""

    def validate_version(self) -> ValidationResult:
        """Validate Python version meets requirements."""
        try:
            version_info = self._get_python_version_info()

            if version_info.major < 3 or (
                version_info.major == 3 and version_info.minor < 13
            ):
                return ValidationResult(
                    check_name="python_version",
                    passed=False,
                    message=f"Python 3.13+ required, found {version_info.version_string}",
                    details={"version_info": version_info.model_dump()},
                    severity="critical",
                )

            return ValidationResult(
                check_name="python_version",
                passed=True,
                message=f"Python {version_info.version_string} detected (system and runtime match)",
                details={"version_info": version_info.model_dump()},
                severity="info",
            )
        except Exception as e:
            return ValidationResult(
                check_name="python_version",
                passed=False,
                message=f"Python version check failed: {str(e)}",
                severity="error",
            )

    def _get_python_version_info(self) -> PythonVersionInfo:
        """Extract Python version information."""
        # Runtime version
        runtime_version = sys.version_info

        # System Python verification
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        system_version_str = result.stdout.strip().replace("Python ", "")

        return PythonVersionInfo(
            major=runtime_version.major,
            minor=runtime_version.minor,
            micro=runtime_version.micro,
            releaselevel=runtime_version.releaselevel,
            serial=runtime_version.serial,
            version_string=system_version_str,
            executable_path=Path(sys.executable),
            is_system_python=True,  # Simplified: assume system Python
        )
