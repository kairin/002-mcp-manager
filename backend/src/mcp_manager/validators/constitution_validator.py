"""Constitution compliance validator."""
from typing import List, Optional

from ..models.validation_models import (
    ConstitutionCheckResult,
    PythonEnforcementStatus,
    ValidationResult,
)
from .mcp_validator import MCPValidator
from .python_validator import PythonValidator
from .uv_validator import UVValidator


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
            self.mcp_validator.validate_servers(),
        ]

        return ConstitutionCheckResult(
            principle_number=7,
            principle_name="Cross-Platform Compatibility (Python 3.13)",
            checks=checks,
        )

    def validate_all_principles(
        self, principle_filter: Optional[int] = None
    ) -> List[ConstitutionCheckResult]:
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
            validation_results=[python_result, uv_result, mcp_result],
        )
