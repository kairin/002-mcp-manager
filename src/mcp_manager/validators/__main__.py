"""Pre-commit hook entry point for constitution validation."""
import sys

from .constitution_validator import ConstitutionValidator


def main() -> None:
    """Run constitution validation and exit with appropriate code."""
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
