#!/usr/bin/env python3
"""
Audit script to check MCP server configurations for cross-platform issues
Validates MCP config files for known problematic patterns
Exit code: 0 if all configs valid, 1 if issues found
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple


def find_mcp_config_files(repo_root: Path) -> List[Path]:
    """Find all MCP configuration files in the repository"""
    config_files = []

    # Common MCP config locations
    possible_paths = [
        repo_root / ".claude.json",
        repo_root / "config" / "mcp_servers.json",
        repo_root / ".config" / "mcp" / "servers.json",
    ]

    for path in possible_paths:
        if path.exists():
            config_files.append(path)

    # Also search for any .json files in config directories
    for config_dir in [repo_root / "config", repo_root / ".config"]:
        if config_dir.exists():
            for json_file in config_dir.rglob("*.json"):
                if "mcp" in json_file.name.lower() and json_file not in config_files:
                    config_files.append(json_file)

    return config_files


def check_stdio_server_paths(config: dict) -> List[Tuple[str, str]]:
    """Check stdio server configurations for cross-platform path issues"""
    issues = []

    mcp_servers = config.get("mcpServers", {})

    for server_name, server_config in mcp_servers.items():
        if server_config.get("type") == "stdio":
            command = server_config.get("command", "")
            args = server_config.get("args", [])

            # Check for hardcoded absolute paths
            if command.startswith("/") or command.startswith("C:\\"):
                issues.append((
                    server_name,
                    f"Hardcoded absolute path in command: {command}. "
                    f"Use relative paths or environment variables."
                ))

            # Check for Windows-specific paths in args
            for arg in args:
                if isinstance(arg, str) and ("\\" in arg or arg.startswith("C:")):
                    issues.append((
                        server_name,
                        f"Windows-specific path in args: {arg}. "
                        f"Use forward slashes for cross-platform compatibility."
                    ))

            # Check for missing command
            if not command:
                issues.append((
                    server_name,
                    "stdio server missing 'command' field"
                ))

    return issues


def check_environment_variables(config: dict) -> List[Tuple[str, str]]:
    """Check for environment variable usage and documentation"""
    issues = []

    mcp_servers = config.get("mcpServers", {})

    for server_name, server_config in mcp_servers.items():
        env = server_config.get("env", {})
        headers = server_config.get("headers", {})

        # Check for hardcoded secrets
        for key, value in {**env, **headers}.items():
            if isinstance(value, str):
                # Check for patterns that look like hardcoded secrets
                if len(value) > 20 and not value.startswith("${"):
                    # Likely hardcoded value
                    if any(secret_key in key.lower() for secret_key in ["key", "token", "secret", "password"]):
                        issues.append((
                            server_name,
                            f"Possible hardcoded secret in '{key}'. "
                            f"Use environment variable placeholders like ${{ENV_VAR_NAME}}"
                        ))

    return issues


def main() -> int:
    """Main audit function"""
    print("Checking MCP configuration files...")

    repo_root = Path(__file__).parent.parent.parent
    config_files = find_mcp_config_files(repo_root)

    if not config_files:
        print("ℹ️  INFO: No MCP configuration files found")
        return 0

    print(f"Found {len(config_files)} MCP config file(s): {', '.join(str(f.relative_to(repo_root)) for f in config_files)}")

    all_issues = []

    for config_file in config_files:
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ FAIL: Invalid JSON in {config_file}: {e}")
            return 1
        except Exception as e:
            print(f"❌ FAIL: Error reading {config_file}: {e}")
            return 1

        # Run all checks
        issues = []
        issues.extend(check_stdio_server_paths(config))
        issues.extend(check_environment_variables(config))

        if issues:
            all_issues.append((config_file, issues))

    if all_issues:
        print("\n❌ FAIL: Found configuration issues:\n")
        for config_file, issues in all_issues:
            print(f"In {config_file.relative_to(repo_root)}:")
            for server_name, issue in issues:
                print(f"  - [{server_name}] {issue}")
        print("\nResolution: Fix the configuration issues listed above")
        return 1

    print("✅ PASS: All MCP configurations are valid and cross-platform compatible")
    return 0


if __name__ == "__main__":
    sys.exit(main())
