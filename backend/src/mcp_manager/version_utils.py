"""Version utilities for parsing project metadata from pyproject.toml.

This module provides functions to extract version information and metadata
from the project's pyproject.toml file using Python 3.11+ tomllib.
"""

import tomllib
from pathlib import Path

from .models import VersionMetadata


def get_pyproject_path() -> Path:
    """Get the path to pyproject.toml in the project root.

    Returns:
        Path to pyproject.toml file

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found
    """
    # Try relative to this file (src/mcp_manager/)
    current_dir = Path(__file__).parent
    pyproject_path = current_dir.parent.parent / "pyproject.toml"

    if pyproject_path.exists():
        return pyproject_path.resolve()

    # Try current working directory
    cwd_path = Path.cwd() / "pyproject.toml"
    if cwd_path.exists():
        return cwd_path.resolve()

    raise FileNotFoundError(
        "Cannot find pyproject.toml. Please run from project root directory."
    )


def parse_pyproject_toml(pyproject_path: Path | None = None) -> dict:
    """Parse pyproject.toml and return the data structure.

    Args:
        pyproject_path: Optional path to pyproject.toml (auto-detected if None)

    Returns:
        Dictionary containing parsed TOML data

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found
        tomllib.TOMLDecodeError: If pyproject.toml is invalid
    """
    if pyproject_path is None:
        pyproject_path = get_pyproject_path()

    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def get_version_metadata(pyproject_path: Path | None = None) -> VersionMetadata:
    """Get version metadata from pyproject.toml.

    Args:
        pyproject_path: Optional path to pyproject.toml (auto-detected if None)

    Returns:
        VersionMetadata object with project information

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found
        KeyError: If required fields are missing from pyproject.toml
        tomllib.TOMLDecodeError: If pyproject.toml is invalid
    """
    if pyproject_path is None:
        pyproject_path = get_pyproject_path()

    data = parse_pyproject_toml(pyproject_path)

    # Extract project metadata
    project = data.get("project", {})

    # Get version
    version = project.get("version")
    if not version:
        raise KeyError("Missing 'project.version' in pyproject.toml")

    # Get Python requirement
    python_requirement = project.get("requires-python", ">=3.11")

    # Get dependencies
    dependencies_list = project.get("dependencies", [])
    dependencies = {}
    for dep in dependencies_list:
        # Parse dependency strings like "typer>=0.12.0"
        if ">=" in dep:
            name, version_spec = dep.split(">=")
            dependencies[name.strip()] = f">={version_spec.strip()}"
        elif "==" in dep:
            name, version_spec = dep.split("==")
            dependencies[name.strip()] = f"=={version_spec.strip()}"
        else:
            # No version specified
            dependencies[dep.strip()] = "*"

    # MCP server count is hardcoded to 6 (per data-model.md)
    mcp_server_count = 6

    return VersionMetadata(
        version=version,
        python_requirement=python_requirement,
        mcp_server_count=mcp_server_count,
        dependencies=dependencies,
        source_file=pyproject_path,
    )


def get_version_string() -> str:
    """Get the version string from pyproject.toml.

    Returns:
        Version string (e.g., "0.1.0")

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found
        KeyError: If version field is missing
    """
    metadata = get_version_metadata()
    return metadata.version


def get_python_requirement() -> str:
    """Get the Python version requirement from pyproject.toml.

    Returns:
        Python requirement string (e.g., ">=3.11")

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found
    """
    metadata = get_version_metadata()
    return metadata.python_requirement
