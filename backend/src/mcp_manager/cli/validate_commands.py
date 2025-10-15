"""Validation CLI commands for Python 3.13 enforcement."""
import json as json_module

import typer
from rich.console import Console

from ..validators.constitution_validator import ConstitutionValidator
from ..validators.mcp_validator import MCPValidator
from ..validators.python_validator import PythonValidator
from ..validators.uv_validator import UVValidator

app = typer.Typer(help="Validation commands for Python 3.13 enforcement")
console = Console()


@app.command("python")
def validate_python(
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed information"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Validate Python 3.13 system Python enforcement."""
    validator = PythonValidator()
    result = validator.validate_version()

    if json:
        console.print_json(data=result.model_dump(mode='json'))
    else:
        status = "✅" if result.passed else "❌"
        console.print(
            f"{status} Python version validation: {'PASS' if result.passed else 'FAIL'}"
        )
        console.print(result.message)

        if verbose and result.details:
            console.print("\nDetails:", style="bold")
            for key, value in result.details.items():
                console.print(f"  {key}: {value}")

    raise typer.Exit(0 if result.passed else 1)


@app.command("uv")
def validate_uv(
    verbose: bool = typer.Option(False, "--verbose"),
    json: bool = typer.Option(False, "--json"),
):
    """Validate UV package manager configuration."""
    validator = UVValidator()
    result = validator.validate_configuration()

    if json:
        console.print_json(data=result.model_dump(mode='json'))
    else:
        status = "✅" if result.passed else "❌"
        console.print(
            f"{status} UV configuration validation: {'PASS' if result.passed else 'FAIL'}"
        )
        console.print(result.message)

    raise typer.Exit(0 if result.passed else 1)


@app.command("mcp-servers")
def validate_mcp_servers(
    verbose: bool = typer.Option(False, "--verbose"),
    json: bool = typer.Option(False, "--json"),
):
    """Validate MCP server configurations use UV."""
    validator = MCPValidator()
    result = validator.validate_servers()

    if json:
        console.print_json(data=result.model_dump(mode='json'))
    else:
        status = "✅" if result.passed else "❌"
        console.print(
            f"{status} MCP server validation: {'PASS' if result.passed else 'FAIL'}"
        )
        console.print(result.message)

        if verbose and result.details:
            console.print("\nServer details:", style="bold")
            console.print(f"  Total servers: {result.details.get('total_servers')}")
            console.print(f"  Stdio servers: {result.details.get('stdio_servers')}")
            console.print(f"  UV compliant: {result.details.get('compliant')}")

    raise typer.Exit(0 if result.passed else 1)


@app.command("constitution")
def validate_constitution(
    principle: int = typer.Option(
        None, "--principle", help="Validate specific principle (1-9)"
    ),
    verbose: bool = typer.Option(False, "--verbose"),
    json: bool = typer.Option(False, "--json"),
):
    """Validate complete constitution compliance."""
    validator = ConstitutionValidator()

    if principle:
        results = validator.validate_all_principles(principle_filter=principle)
    else:
        results = validator.validate_all_principles()

    all_passed = all(r.overall_passed for r in results)

    if json:
        console.print_json(
            data={
                "check_name": "constitution_compliance",
                "passed": all_passed,
                "principles_validated": len(results),
                "principle_results": [r.model_dump(mode='json') for r in results],
            }
        )
    else:
        status = "✅" if all_passed else "❌"
        console.print(
            f"{status} Constitution validation: {'PASS' if all_passed else 'FAIL'}"
        )
        console.print(f"- Principles validated: {len(results)}")

        for result in results:
            principle_status = "✓" if result.overall_passed else "✗"
            console.print(
                f"  {principle_status} {result.principle_number}. {result.principle_name}"
            )

    raise typer.Exit(0 if all_passed else 1)


@app.command("all")
def validate_all(
    verbose: bool = typer.Option(False, "--verbose"),
    json: bool = typer.Option(False, "--json"),
):
    """Run all validation checks (Python, UV, MCP servers, Constitution)."""
    python_validator = PythonValidator()
    uv_validator = UVValidator()
    mcp_validator = MCPValidator()
    constitution_validator = ConstitutionValidator()

    # Run all validations
    python_result = python_validator.validate_version()
    uv_result = uv_validator.validate_configuration()
    mcp_result = mcp_validator.validate_servers()
    constitution_results = constitution_validator.validate_all_principles()

    # Determine overall status
    all_passed = (
        python_result.passed
        and uv_result.passed
        and mcp_result.passed
        and all(r.overall_passed for r in constitution_results)
    )

    if json:
        console.print_json(
            data={
                "check_name": "comprehensive_validation",
                "passed": all_passed,
                "python": python_result.model_dump(mode='json'),
                "uv": uv_result.model_dump(mode='json'),
                "mcp_servers": mcp_result.model_dump(mode='json'),
                "constitution": [r.model_dump(mode='json') for r in constitution_results],
            }
        )
    else:
        console.print("=== Python 3.13 System Enforcement Validation ===\n")

        # Python validation
        status = "✅" if python_result.passed else "❌"
        console.print(f"{status} Python: {python_result.message}")

        # UV validation
        status = "✅" if uv_result.passed else "❌"
        console.print(f"{status} UV: {uv_result.message}")

        # MCP validation
        status = "✅" if mcp_result.passed else "❌"
        console.print(f"{status} MCP Servers: {mcp_result.message}")

        # Constitution validation
        constitution_passed = all(r.overall_passed for r in constitution_results)
        status = "✅" if constitution_passed else "❌"
        console.print(f"{status} Constitution: {len(constitution_results)} principles")

        console.print(f"\n{'='*50}")
        final_status = "✅ ALL CHECKS PASSED" if all_passed else "❌ SOME CHECKS FAILED"
        console.print(final_status)

    raise typer.Exit(0 if all_passed else 1)
