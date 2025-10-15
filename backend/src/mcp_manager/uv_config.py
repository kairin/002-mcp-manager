"""UV configuration validation for System Python Enforcement.

This module provides functions to validate UV package manager configuration
and ensure constitutional compliance with system Python 3.13 enforcement.

References:
    - Spec: specs/002-system-python-enforcement/spec.md
    - Research: specs/002-system-python-enforcement/research.md
    - Tasks: T013, T014, T015
"""

import shutil
import subprocess
from pathlib import Path
from typing import Literal

try:
    import toml
except ImportError:
    # Fallback for systems without toml library
    toml = None  # type: ignore


def check_uv_installed() -> bool:
    """Check if UV is available in PATH.

    Verifies that the UV package manager is installed and accessible
    by checking if the `uv` command is available in the system PATH.

    Returns:
        True if UV is installed and accessible, False otherwise

    Examples:
        >>> if check_uv_installed():
        ...     print("UV is installed")
        ... else:
        ...     print("UV not found - please install: https://astral.sh/uv")

    References:
        - Task: T014
    """
    return shutil.which("uv") is not None


def get_uv_config_path(project_root: Path) -> Path | None:
    """Find UV configuration file.

    Searches for UV configuration in the project, checking both uv.toml
    (UV-specific config) and pyproject.toml (with [tool.uv] section).

    Search Order:
        1. uv.toml in project root
        2. pyproject.toml in project root (if it has [tool.uv] section)

    Args:
        project_root: Path to project root directory

    Returns:
        Path to UV configuration file if found, None otherwise

    Examples:
        >>> config_path = get_uv_config_path(Path.cwd())
        >>> if config_path:
        ...     print(f"Found UV config: {config_path}")

    References:
        - Research: research.md lines 306-337
        - Task: T015
    """
    # Check for uv.toml first (UV-specific config file)
    uv_toml_path = project_root / "uv.toml"
    if uv_toml_path.exists() and uv_toml_path.is_file():
        return uv_toml_path

    # Check for pyproject.toml with [tool.uv] section
    pyproject_toml_path = project_root / "pyproject.toml"
    if pyproject_toml_path.exists() and pyproject_toml_path.is_file():
        # Try to parse and check for [tool.uv] section
        if toml is not None:
            try:
                with open(pyproject_toml_path, "r") as f:
                    config = toml.load(f)
                    if "tool" in config and "uv" in config["tool"]:
                        return pyproject_toml_path
            except Exception:
                # If parsing fails, assume no [tool.uv] section
                pass
        else:
            # Without toml library, just check if file contains [tool.uv]
            try:
                with open(pyproject_toml_path, "r") as f:
                    content = f.read()
                    if "[tool.uv]" in content:
                        return pyproject_toml_path
            except Exception:
                pass

    return None


def validate_uv_config(project_root: Path) -> dict[str, str | None]:
    """Validate UV configuration for compliance.

    Parses UV configuration file and extracts settings relevant to
    system Python enforcement (python-downloads, python-preference).
    Also checks for .python-version file.

    Args:
        project_root: Path to project root directory

    Returns:
        Dictionary with configuration settings:
        {
            "config_file": str | None,  # Path to config file
            "python_downloads": str | None,  # "automatic" | "manual" | "never"
            "python_preference": str | None,  # "only-managed" | "managed" | "system" | "only-system"
            "python_version_pinned": str | None,  # Content of .python-version
        }

    Examples:
        >>> config = validate_uv_config(Path.cwd())
        >>> if config["python_downloads"] == "never":
        ...     print("✓ Python downloads disabled")
        >>> if config["python_preference"] == "only-system":
        ...     print("✓ Using only system Python")

    Constitutional Requirements:
        - FR-002: python-preference must be "only-system"
        - FR-003: python-downloads must be "manual" or "never"
        - Recommended: .python-version should contain "3.13"

    References:
        - Research: research.md lines 306-337
        - Task: T013
    """
    result: dict[str, str | None] = {
        "config_file": None,
        "python_downloads": None,
        "python_preference": None,
        "python_version_pinned": None,
    }

    # Find UV configuration file
    config_path = get_uv_config_path(project_root)
    if config_path:
        result["config_file"] = str(config_path)

        # Parse configuration file
        try:
            if config_path.name == "uv.toml":
                # Parse uv.toml (direct settings, no [tool.uv] prefix)
                config_data = _parse_uv_toml(config_path)
            else:
                # Parse pyproject.toml [tool.uv] section
                config_data = _parse_pyproject_toml(config_path)

            # Extract relevant settings
            result["python_downloads"] = config_data.get("python-downloads") or config_data.get("python_downloads")
            result["python_preference"] = config_data.get("python-preference") or config_data.get("python_preference")

        except Exception:
            # If parsing fails, leave settings as None
            pass

    # Check for .python-version file
    python_version_file = project_root / ".python-version"
    if python_version_file.exists() and python_version_file.is_file():
        try:
            with open(python_version_file, "r") as f:
                version_content = f.read().strip()
                if version_content:
                    result["python_version_pinned"] = version_content
        except Exception:
            pass

    return result


def _parse_uv_toml(config_path: Path) -> dict[str, str]:
    """Parse uv.toml configuration file.

    Args:
        config_path: Path to uv.toml file

    Returns:
        Dictionary with configuration settings
    """
    if toml is not None:
        # Use toml library if available
        with open(config_path, "r") as f:
            return toml.load(f)
    else:
        # Fallback: simple parsing for key = "value" format
        config = {}
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Parse key = value
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    config[key] = value
        return config


def _parse_pyproject_toml(config_path: Path) -> dict[str, str]:
    """Parse pyproject.toml [tool.uv] section.

    Args:
        config_path: Path to pyproject.toml file

    Returns:
        Dictionary with UV configuration settings from [tool.uv] section
    """
    if toml is not None:
        # Use toml library if available
        with open(config_path, "r") as f:
            data = toml.load(f)
            return data.get("tool", {}).get("uv", {})
    else:
        # Fallback: simple parsing for [tool.uv] section
        config = {}
        in_tool_uv_section = False

        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()

                # Check for [tool.uv] section start
                if line == "[tool.uv]":
                    in_tool_uv_section = True
                    continue

                # Check for next section (exit [tool.uv])
                if in_tool_uv_section and line.startswith("["):
                    break

                # Parse key = value in [tool.uv] section
                if in_tool_uv_section and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    config[key] = value

        return config


def get_uv_python_path() -> Path | None:
    """Get Python path that UV would use.

    Queries UV to determine which Python executable it would use
    based on current configuration.

    Returns:
        Path to Python executable UV would use, or None on error

    Examples:
        >>> uv_python = get_uv_python_path()
        >>> if uv_python:
        ...     print(f"UV would use: {uv_python}")

    Note:
        Requires UV to be installed (check with check_uv_installed() first)
    """
    if not check_uv_installed():
        return None

    try:
        # Run 'uv python find' to get the Python path UV would use
        result = subprocess.run(
            ["uv", "python", "find"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )

        if result.returncode == 0:
            python_path_str = result.stdout.strip()
            if python_path_str:
                return Path(python_path_str)

        return None

    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return None
