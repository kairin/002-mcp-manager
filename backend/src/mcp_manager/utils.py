"""Utility functions for MCP Manager."""

import subprocess

from packaging.version import InvalidVersion, Version

from .exceptions import UpdateCheckError


def check_npm_package_version(package: str, timeout: int = 10) -> str | None:
    """Check latest npm package version.

    Uses npm view command via subprocess to query npm registry.

    Args:
        package: npm package name (e.g., "shadcn", "@modelcontextprotocol/server-github")
        timeout: Command timeout in seconds (default: 10)

    Returns:
        Latest version string (e.g., "1.3.0") or None if package not found

    Raises:
        UpdateCheckError: If npm command fails or times out

    Implementation from research.md decision.
    """
    try:
        result = subprocess.run(
            ["npm", "view", package, "version"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        if result.returncode == 0:
            version = result.stdout.strip()
            return version if version else None

        # Non-zero exit code
        if "404" in result.stderr or "E404" in result.stderr:
            # Package not found
            return None

        raise UpdateCheckError(
            f"npm view failed for package '{package}': {result.stderr}"
        )

    except subprocess.TimeoutExpired as e:
        raise UpdateCheckError(
            f"npm view command timed out after {timeout}s for package '{package}'"
        ) from e
    except FileNotFoundError as e:
        raise UpdateCheckError(
            "npm command not found. Please install npm to check for updates."
        ) from e
    except Exception as e:
        raise UpdateCheckError(
            f"Unexpected error checking npm package '{package}': {e}"
        ) from e


def compare_versions(current: str, latest: str) -> tuple[bool, str]:
    """Compare semantic versions and categorize update type.

    Uses packaging.version for semver comparison following research.md decision.

    Args:
        current: Current version string (e.g., "1.2.3")
        latest: Latest version string (e.g., "1.3.0")

    Returns:
        Tuple of (update_available, update_type):
        - update_available: True if latest > current
        - update_type: "major", "minor", "patch", or "none"

    Examples:
        >>> compare_versions("1.2.3", "2.0.0")
        (True, "major")
        >>> compare_versions("1.2.3", "1.3.0")
        (True, "minor")
        >>> compare_versions("1.2.3", "1.2.4")
        (True, "patch")
        >>> compare_versions("1.3.0", "1.3.0")
        (False, "none")
    """
    try:
        curr = Version(current)
        new = Version(latest)

        if new > curr:
            # Update available - categorize by semver
            if new.major > curr.major:
                return (True, "major")
            elif new.minor > curr.minor:
                return (True, "minor")
            elif new.micro > curr.micro:
                return (True, "patch")
            else:
                # Edge case: pre-release or build metadata changed
                return (True, "patch")
        else:
            # No update or downgrade
            return (False, "none")

    except InvalidVersion:
        # If versions can't be parsed as semver, treat as no update
        return (False, "none")


def extract_version_from_args(args: list[str]) -> str | None:
    """Extract version number from npm package args.

    Args:
        args: Command args list (e.g., ["shadcn@1.2.3", "mcp"])

    Returns:
        Version string (e.g., "1.2.3") or None if not found

    Examples:
        >>> extract_version_from_args(["shadcn@1.2.3", "mcp"])
        "1.2.3"
        >>> extract_version_from_args(["shadcn", "mcp"])
        None
    """
    for arg in args:
        if "@" in arg:
            # Format: package@version
            parts = arg.split("@")
            if len(parts) == 2:
                package, version = parts
                # Verify it looks like a version (starts with digit)
                if version and version[0].isdigit():
                    return version
            elif len(parts) > 2:
                # Scoped package: @scope/package@version
                version = parts[-1]
                if version and version[0].isdigit():
                    return version
    return None


def extract_package_name_from_args(args: list[str]) -> str | None:
    """Extract package name from npm package args.

    Args:
        args: Command args list (e.g., ["shadcn@1.2.3", "mcp"])

    Returns:
        Package name (e.g., "shadcn") or None if not found

    Examples:
        >>> extract_package_name_from_args(["shadcn@1.2.3", "mcp"])
        "shadcn"
        >>> extract_package_name_from_args(["@scope/package@1.0.0", "mcp"])
        "@scope/package"
    """
    for arg in args:
        if "@" in arg:
            # Handle scoped packages: @scope/package@version
            if arg.startswith("@"):
                # Scoped package
                parts = arg.rsplit("@", 1)  # Split from right to get last @
                if len(parts) == 2:
                    return parts[0]
            else:
                # Regular package
                parts = arg.split("@")
                if len(parts) >= 2:
                    return parts[0]

    # Fallback: return first arg if no @ found
    return args[0] if args else None


def update_args_with_version(args: list[str], new_version: str) -> list[str]:
    """Update args list with new version number.

    Handles both specific versions (e.g., "1.2.3") and tags (e.g., "latest", "next").
    Tags are replaced with the specific version number.

    Args:
        args: Original args list (e.g., ["shadcn@1.2.3", "mcp"] or ["shadcn@latest", "mcp"])
        new_version: New version to use (e.g., "1.3.0")

    Returns:
        Updated args list (e.g., ["shadcn@1.3.0", "mcp"])

    Examples:
        >>> update_args_with_version(["shadcn@1.2.3", "mcp"], "1.3.0")
        ["shadcn@1.3.0", "mcp"]
        >>> update_args_with_version(["shadcn@latest", "mcp"], "1.3.0")
        ["shadcn@1.3.0", "mcp"]
    """
    updated_args = []

    for arg in args:
        if "@" in arg:
            # Found package with version or tag
            if arg.startswith("@"):
                # Scoped package: @scope/package@version
                parts = arg.rsplit("@", 1)
                if len(parts) == 2:
                    # Replace version or tag
                    updated_args.append(f"{parts[0]}@{new_version}")
                else:
                    updated_args.append(arg)
            else:
                # Regular package: package@version or package@tag
                parts = arg.split("@")
                if len(parts) == 2:
                    # Replace version or tag (including "latest", "next", etc.)
                    updated_args.append(f"{parts[0]}@{new_version}")
                else:
                    updated_args.append(arg)
        else:
            # No @ symbol, keep as-is
            updated_args.append(arg)

    return updated_args
