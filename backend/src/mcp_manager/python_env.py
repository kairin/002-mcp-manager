"""Python environment detection and validation for System Python Enforcement.

This module provides functions to detect, validate, and analyze Python 3.13
installations on the system. It supports package manager installations (apt, brew)
and manual installations across Linux and macOS platforms.

References:
    - Spec: specs/002-system-python-enforcement/spec.md
    - Research: specs/002-system-python-enforcement/research.md
    - Tasks: T008, T009, T010, T011, T012
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Literal

# Priority-ordered search paths for Python 3.13 (per research.md lines 46-59)
PYTHON_SEARCH_PATHS = [
    "/usr/bin/python3.13",          # Debian/Ubuntu/Fedora package manager
    "/usr/local/bin/python3.13",    # Manual install or macOS Homebrew (Intel)
    "/opt/homebrew/bin/python3.13",  # macOS Homebrew (Apple Silicon)
]


def find_system_python() -> Path | None:
    """Search for Python 3.13 in priority order.

    Searches standard system locations for a Python 3.13 executable in priority
    order. Package manager installations are preferred over manual installations.

    Search Priority:
        1. /usr/bin/python3.13 (package manager - Debian/Ubuntu/Fedora)
        2. /usr/local/bin/python3.13 (manual install or macOS Homebrew Intel)
        3. /opt/homebrew/bin/python3.13 (macOS Homebrew Apple Silicon)

    Returns:
        Path to Python 3.13 executable if found, None otherwise

    Examples:
        >>> python_path = find_system_python()
        >>> if python_path:
        ...     print(f"Found Python at {python_path}")
        ... else:
        ...     print("Python 3.13 not found")

    References:
        - Research: research.md lines 46-59
        - Task: T008
    """
    for python_path_str in PYTHON_SEARCH_PATHS:
        python_path = Path(python_path_str)
        if python_path.exists() and python_path.is_file():
            # Verify it's actually Python 3.13 before returning
            if is_python_313(python_path):
                return python_path

    return None


def get_python_version(python_path: Path) -> tuple[int, int, int] | None:
    """Get version from Python executable.

    Runs the Python executable with --version flag and parses the output
    to extract the version tuple (major, minor, micro).

    Args:
        python_path: Path to Python executable

    Returns:
        Version tuple (major, minor, micro) if successful, None on error

    Examples:
        >>> version = get_python_version(Path("/usr/bin/python3.13"))
        >>> if version:
        ...     print(f"Python {version[0]}.{version[1]}.{version[2]}")

    References:
        - Research: research.md lines 245-265
        - Task: T009
    """
    if not python_path.exists():
        return None

    try:
        # Run python3.13 --version (output format: "Python 3.13.0")
        result = subprocess.run(
            [str(python_path), "--version"],
            capture_output=True,
            text=True,
            timeout=5,  # Prevent hanging on broken installations
            check=False
        )

        # Version may be in stdout or stderr depending on Python version
        output = result.stdout.strip() or result.stderr.strip()

        if not output:
            return None

        # Parse "Python 3.13.0" → (3, 13, 0)
        # Handle cases like "Python 3.13.0rc1" or "Python 3.13.0+"
        if output.startswith("Python "):
            version_str = output.split()[1]  # Get "3.13.0" part

            # Split on '.' and take first 3 components
            # Handle suffixes like "rc1", "+", etc.
            parts = version_str.split(".")
            if len(parts) >= 3:
                # Extract numeric part from third component (e.g., "0rc1" → "0")
                micro_str = ""
                for char in parts[2]:
                    if char.isdigit():
                        micro_str += char
                    else:
                        break

                if micro_str:
                    return (int(parts[0]), int(parts[1]), int(micro_str))

        return None

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError, IndexError):
        return None


def is_python_313(python_path: Path) -> bool:
    """Check if Python is version 3.13.x.

    Validates that the Python executable is specifically version 3.13.x
    (not 3.12, not 3.14, exactly 3.13).

    Args:
        python_path: Path to Python executable

    Returns:
        True if Python version is 3.13.x, False otherwise

    Examples:
        >>> is_valid = is_python_313(Path("/usr/bin/python3.13"))
        >>> print(f"Valid Python 3.13: {is_valid}")

    References:
        - Research: research.md lines 267-270
        - Task: T010
    """
    version = get_python_version(python_path)
    if version is None:
        return False

    # Must be exactly 3.13.x (not 3.12 or 3.14)
    return version[:2] == (3, 13)


def detect_distribution() -> str:
    """Detect OS/distribution for error messages.

    Detects the operating system and distribution to provide
    targeted error messages and installation instructions.

    Returns:
        Distribution name as string (e.g., "Ubuntu 22.04", "macOS (Apple Silicon)")

    Platforms Detected:
        - macOS (Intel)
        - macOS (Apple Silicon)
        - Ubuntu (with version)
        - Debian (with version)
        - Fedora (with version)
        - CentOS/RHEL (with version)
        - Generic Linux (fallback)

    Examples:
        >>> distro = detect_distribution()
        >>> print(f"Running on {distro}")

    References:
        - Research: research.md lines 192-217
        - Task: T011
    """
    system = platform.system()

    if system == "Darwin":
        # macOS detection
        machine = platform.machine()
        if machine == "arm64":
            return "macOS (Apple Silicon)"
        else:
            return "macOS (Intel)"

    elif system == "Linux":
        # Linux distribution detection via /etc/os-release
        os_release_path = Path("/etc/os-release")

        if os_release_path.exists():
            try:
                os_release = {}
                with open(os_release_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line:
                            key, value = line.split("=", 1)
                            # Remove quotes from value
                            value = value.strip('"')
                            os_release[key] = value

                # Extract distribution name and version
                name = os_release.get("NAME", "Linux")
                version = os_release.get("VERSION_ID", "")

                if version:
                    return f"{name} {version}"
                else:
                    return name

            except (IOError, OSError):
                pass

        # Fallback for Linux without /etc/os-release
        return "Linux"

    else:
        # Fallback for other systems (Windows, BSD, etc.)
        return system


def get_venv_base_python(venv_path: Path | None = None) -> Path | None:
    """Get base Python from virtual environment.

    Parses the pyvenv.cfg file from a virtual environment to extract
    the base Python installation path. If no venv_path is provided,
    checks if current Python is running in a venv.

    Args:
        venv_path: Path to virtual environment directory (optional)
                  If None, checks if current Python is in venv via sys.prefix

    Returns:
        Path to base Python executable if in venv, None otherwise

    Examples:
        >>> # Check if current Python is in venv
        >>> base = get_venv_base_python()
        >>> if base:
        ...     print(f"Virtual env base Python: {base}")

        >>> # Check specific venv
        >>> base = get_venv_base_python(Path("/path/to/venv"))

    Virtual Environment Detection:
        - Looks for pyvenv.cfg in venv directory
        - Parses "home = /usr/bin" to get Python location
        - Combines home path with "python3.13" to get full path

    References:
        - Research: research.md lines 277-295
        - Task: T012
    """
    # If no venv path provided, check if current Python is in venv
    if venv_path is None:
        # Check if running in virtual environment
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            venv_path = Path(sys.prefix)
        else:
            # Not in a virtual environment
            return None

    # Look for pyvenv.cfg
    pyvenv_cfg_path = venv_path / "pyvenv.cfg"

    if not pyvenv_cfg_path.exists():
        return None

    try:
        # Parse pyvenv.cfg to find home directory
        home_dir = None
        with open(pyvenv_cfg_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("home = "):
                    home_dir = line.split("=", 1)[1].strip()
                    break

        if home_dir is None:
            return None

        # Construct path to Python executable
        # The home directory typically points to the bin directory containing Python
        base_python_path = Path(home_dir) / "python3.13"

        if base_python_path.exists() and base_python_path.is_file():
            return base_python_path
        else:
            # Try without version suffix
            base_python_path = Path(home_dir) / "python3"
            if base_python_path.exists() and base_python_path.is_file():
                # Verify it's actually 3.13
                if is_python_313(base_python_path):
                    return base_python_path

        return None

    except (IOError, OSError):
        return None


def get_installation_source(python_path: Path) -> Literal["package_manager", "manual_install", "unknown"]:
    """Determine Python installation source based on path.

    Classifies Python installation as package manager, manual install,
    or unknown based on the executable path location.

    Args:
        python_path: Path to Python executable

    Returns:
        Installation source classification

    Classification Rules:
        - /usr/bin/* → package_manager
        - /opt/homebrew/bin/* → package_manager (macOS Homebrew)
        - /usr/local/bin/* → manual_install (or Intel Homebrew)
        - Other paths → unknown

    Examples:
        >>> source = get_installation_source(Path("/usr/bin/python3.13"))
        >>> print(source)  # "package_manager"
    """
    python_str = str(python_path)

    # Package manager installations
    if python_str.startswith("/usr/bin/"):
        return "package_manager"
    if python_str.startswith("/opt/homebrew/bin/"):  # macOS Homebrew Apple Silicon
        return "package_manager"

    # Manual installations (or Intel Homebrew which uses /usr/local)
    if python_str.startswith("/usr/local/bin/"):
        return "manual_install"

    # Unknown/other installations
    return "unknown"
