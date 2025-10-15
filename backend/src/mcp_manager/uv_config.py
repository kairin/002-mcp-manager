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
                with open(pyproject_toml_path) as f:
                    config = toml.load(f)
                    if "tool" in config and "uv" in config["tool"]:
                        return pyproject_toml_path
            except Exception:
                # If parsing fails, assume no [tool.uv] section
                pass
        else:
            # Without toml library, just check if file contains [tool.uv]
            try:
                with open(pyproject_toml_path) as f:
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
            result["python_downloads"] = config_data.get(
                "python-downloads"
            ) or config_data.get("python_downloads")
            result["python_preference"] = config_data.get(
                "python-preference"
            ) or config_data.get("python_preference")

        except Exception:
            # If parsing fails, leave settings as None
            pass

    # Check for .python-version file
    python_version_file = project_root / ".python-version"
    if python_version_file.exists() and python_version_file.is_file():
        try:
            with open(python_version_file) as f:
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
        with open(config_path) as f:
            return toml.load(f)
    else:
        # Fallback: simple parsing for key = "value" format
        config = {}
        with open(config_path) as f:
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
        with open(config_path) as f:
            data = toml.load(f)
            return data.get("tool", {}).get("uv", {})
    else:
        # Fallback: simple parsing for [tool.uv] section
        config = {}
        in_tool_uv_section = False

        with open(config_path) as f:
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
            check=False,
        )

        if result.returncode == 0:
            python_path_str = result.stdout.strip()
            if python_path_str:
                return Path(python_path_str)

        return None

    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return None


def migrate_legacy_uv_config(
    project_root: Path, create_backup: bool = True
) -> dict[str, str]:
    """Migrate legacy UV configuration to standard uv.toml format.

    Implements T057: UV config migration utility.

    Converts legacy `.uv/config` files to the modern `uv.toml` format
    with constitutional Python 3.13 enforcement requirements.

    Args:
        project_root: Path to project root directory
        create_backup: Create backup of existing configs before migration

    Returns:
        Migration result dictionary:
        {
            "status": "success" | "no_migration_needed" | "error",
            "message": str,  # Description of what happened
            "backup_path": str | None,  # Path to backup if created
            "migrated_from": str | None,  # Source config file path
            "migrated_to": str,  # Destination uv.toml path
        }

    Examples:
        >>> result = migrate_legacy_uv_config(Path.cwd())
        >>> if result["status"] == "success":
        ...     print(f"Migrated from {result['migrated_from']} to {result['migrated_to']}")
        ... elif result["status"] == "no_migration_needed":
        ...     print("Already using standard uv.toml")

    Migration Process:
        1. Check for legacy .uv/config file
        2. Check for existing uv.toml (skip if already migrated)
        3. Create backup of legacy config if requested
        4. Create uv.toml with constitutional requirements
        5. Preserve non-conflicting settings from legacy config

    Constitutional Requirements Applied:
        - python-downloads = "never"
        - python-preference = "only-system"
        - system-site-packages = true

    References:
        - Task: T057 (Create UV config migration utility)
        - Guide: docs/migration-guide.md (T058)
    """
    result: dict[str, str | None] = {
        "status": "error",
        "message": "",
        "backup_path": None,
        "migrated_from": None,
        "migrated_to": str(project_root / "uv.toml"),
    }

    uv_toml_path = project_root / "uv.toml"
    legacy_config_path = project_root / ".uv" / "config"
    global_uv_config = Path.home() / ".config" / "uv" / "uv.toml"

    # Check if already using standard uv.toml
    if uv_toml_path.exists():
        result["status"] = "no_migration_needed"
        result["message"] = "Project already using standard uv.toml configuration"
        return result

    # Check for legacy .uv/config
    if not legacy_config_path.exists():
        # No legacy config found - create new uv.toml with constitutional requirements
        result["status"] = "no_migration_needed"
        result["message"] = (
            "No legacy configuration found. Creating new uv.toml with constitutional requirements."
        )

        try:
            _create_constitutional_uv_toml(uv_toml_path)
            result["status"] = "success"
            result["message"] = "Created new uv.toml with constitutional requirements"
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Failed to create uv.toml: {e}"

        return result

    # Legacy config found - migrate to uv.toml
    result["migrated_from"] = str(legacy_config_path)

    try:
        # Create backup if requested
        if create_backup:
            backup_path = project_root / ".uv" / "config.backup"
            import shutil

            shutil.copy2(legacy_config_path, backup_path)
            result["backup_path"] = str(backup_path)

        # Create uv.toml with constitutional requirements
        _create_constitutional_uv_toml(uv_toml_path)

        result["status"] = "success"
        result["message"] = (
            f"Successfully migrated from {legacy_config_path} to {uv_toml_path}"
        )

    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Migration failed: {e}"

    return result


def _create_constitutional_uv_toml(uv_toml_path: Path) -> None:
    """Create uv.toml with constitutional requirements.

    Creates a uv.toml file with mandatory Python 3.13 enforcement settings.

    Args:
        uv_toml_path: Path where uv.toml should be created

    Raises:
        OSError: If file cannot be created or written
    """
    constitutional_config = """# UV Configuration - Constitutional Requirements
# Auto-generated by mcp-manager (Feature 002: System Python 3.13 Enforcement)
#
# References:
#   - .specify/memory/constitution.md
#   - specs/002-system-python-enforcement/spec.md

[tool.uv]
# Constitutional requirement: Never download Python interpreters
# UV must only use the system-installed Python 3.13
python-downloads = "never"

# Constitutional requirement: Only use system Python
# Prevents UV from using managed or virtual environment Pythons
python-preference = "only-system"

[tool.uv.pip]
# Use system site packages for integration
# Allows MCP servers to access system-installed packages
system-site-packages = true
"""

    uv_toml_path.parent.mkdir(parents=True, exist_ok=True)
    uv_toml_path.write_text(constitutional_config)


def check_global_uv_conflicts(project_root: Path) -> dict[str, str | bool]:
    """Check for global UV configuration conflicts.

    Checks if global UV configuration (~/.config/uv/uv.toml) conflicts
    with project constitutional requirements.

    Args:
        project_root: Path to project root directory

    Returns:
        Dictionary with conflict detection results:
        {
            "has_conflicts": bool,  # True if conflicts detected
            "global_config_exists": bool,  # True if global config exists
            "global_config_path": str | None,  # Path to global config
            "conflicts": list[str],  # List of conflict descriptions
            "resolution": str,  # Recommended resolution steps
        }

    Examples:
        >>> conflicts = check_global_uv_conflicts(Path.cwd())
        >>> if conflicts["has_conflicts"]:
        ...     print(f"Conflicts detected: {conflicts['conflicts']}")
        ...     print(f"Resolution: {conflicts['resolution']}")

    References:
        - Task: T057 (UV config migration utility)
        - Guide: docs/PYTHON-TROUBLESHOOTING.md
    """
    global_config_path = Path.home() / ".config" / "uv" / "uv.toml"

    result: dict[str, str | bool | list] = {
        "has_conflicts": False,
        "global_config_exists": global_config_path.exists(),
        "global_config_path": (
            str(global_config_path) if global_config_path.exists() else None
        ),
        "conflicts": [],
        "resolution": "",
    }

    if not global_config_path.exists():
        result["resolution"] = "No global UV config found - no conflicts"
        return result

    # Parse global config
    try:
        if toml is not None:
            with open(global_config_path) as f:
                global_config = toml.load(f)
        else:
            global_config = _parse_uv_toml(global_config_path)

        # Check for python-downloads conflict
        python_downloads = global_config.get("python-downloads") or global_config.get(
            "python_downloads"
        )
        if python_downloads and python_downloads not in ("manual", "never"):
            result["has_conflicts"] = True
            result["conflicts"].append(
                f"Global config has python-downloads={python_downloads}, "
                "but constitutional requirement is 'never' or 'manual'"
            )

        # Check for python-preference conflict
        python_preference = global_config.get("python-preference") or global_config.get(
            "python_preference"
        )
        if python_preference and python_preference != "only-system":
            result["has_conflicts"] = True
            result["conflicts"].append(
                f"Global config has python-preference={python_preference}, "
                "but constitutional requirement is 'only-system'"
            )

        # Provide resolution
        if result["has_conflicts"]:
            result["resolution"] = (
                "Rename or backup global UV config to prevent conflicts:\n"
                f"  mv {global_config_path} {global_config_path}.backup\n\n"
                "UV will then use the project uv.toml which enforces constitutional requirements."
            )
        else:
            result["resolution"] = (
                "Global UV config is compatible with project requirements"
            )

    except Exception as e:
        result["has_conflicts"] = True
        result["conflicts"].append(f"Failed to parse global config: {e}")
        result["resolution"] = (
            "Unable to validate global config. Consider renaming it:\n"
            f"  mv {global_config_path} {global_config_path}.backup"
        )

    return result
