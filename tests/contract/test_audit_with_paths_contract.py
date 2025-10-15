"""Contract test for configurable audit paths API.

Tests that the audit_configurations method matches the API contract defined in
contracts/audit_with_paths.yaml
"""

from pathlib import Path

import pytest
from mcp_manager.core import MCPManager
from mcp_manager.exceptions import InvalidPathError
from mcp_manager.models import AuditConfiguration


class TestAuditWithPathsContract:
    """Verify audit_configurations API matches contract specification."""

    def test_audit_accepts_search_directories_parameter(self):
        """Test that audit_configurations accepts optional search_directories."""
        manager = MCPManager()

        # Should accept search_directories (optional array)
        config = AuditConfiguration(
            search_directories=[Path.home() / "Apps"],
            use_defaults=False,
        )
        result = manager.audit_configurations(config=config)

        assert result is not None

    def test_audit_accepts_use_config_parameter(self):
        """Test that audit_configurations accepts use_config parameter."""
        manager = MCPManager()

        config = AuditConfiguration(
            search_directories=None,
            use_defaults=True,
        )
        result = manager.audit_configurations(config=config)

        assert result is not None

    def test_audit_accepts_detailed_parameter(self):
        """Test that audit_configurations accepts detailed parameter."""
        manager = MCPManager()

        config = AuditConfiguration(
            search_directories=None,
            use_defaults=True,
        )
        # detailed parameter in method call
        result = manager.audit_configurations(config=config, detailed=False)

        assert result is not None

    def test_audit_returns_required_fields(self):
        """Test that audit_configurations returns all contract-defined output fields."""
        manager = MCPManager()

        config = AuditConfiguration(
            search_directories=[Path.home() / "Apps"],
            use_defaults=False,
        )
        result = manager.audit_configurations(config=config)

        # Contract-defined output fields
        assert "global_config" in result
        assert isinstance(result["global_config"], dict)

        # global_config should have required fields
        gc = result["global_config"]
        assert "exists" in gc
        assert isinstance(gc["exists"], bool)
        assert "servers" in gc
        assert isinstance(gc["servers"], int)
        assert "status" in gc
        assert gc["status"] in ["ok", "missing", "invalid"]

        assert "project_configs" in result
        assert isinstance(result["project_configs"], dict)

        assert "search_paths_used" in result
        assert isinstance(result["search_paths_used"], list)
        for path in result["search_paths_used"]:
            assert isinstance(path, str)

    def test_audit_raises_invalid_path_error_for_nonexistent_path(self):
        """Test InvalidPathError when provided path doesn't exist."""
        manager = MCPManager()

        with pytest.raises(InvalidPathError):
            config = AuditConfiguration(
                search_directories=[Path("/nonexistent/path")],
                use_defaults=False,
                validate_paths=True,
            )
            manager.audit_configurations(config=config)

    def test_audit_uses_custom_paths_when_provided(self):
        """Test that custom search_directories are used instead of defaults."""
        manager = MCPManager()

        custom_path = Path.home() / "Apps"
        config = AuditConfiguration(
            search_directories=[custom_path],
            use_defaults=False,
        )
        result = manager.audit_configurations(config=config)

        # Should report the custom path as used
        assert str(custom_path) in result["search_paths_used"]

    def test_audit_uses_defaults_when_no_custom_paths(self):
        """Test that default paths are used when no custom paths provided."""
        manager = MCPManager()

        config = AuditConfiguration(
            search_directories=None,
            use_defaults=True,
        )
        result = manager.audit_configurations(config=config)

        # Should use default paths
        assert len(result["search_paths_used"]) > 0

        # Default paths from contract
        default_paths = [
            str(Path.home() / "Apps"),
            str(Path.home() / "projects"),
            str(Path.home() / "repos"),
        ]

        # At least one default path should be in search_paths_used
        used_paths = set(result["search_paths_used"])
        defaults = set(default_paths)
        assert len(used_paths.intersection(defaults)) > 0

    def test_audit_reports_global_config_status(self):
        """Test that global_config status is correctly reported."""
        manager = MCPManager()

        config = AuditConfiguration(
            search_directories=[Path.home()],
            use_defaults=False,
        )
        result = manager.audit_configurations(config=config)

        gc = result["global_config"]

        # If ~/.claude.json exists, status should be "ok"
        claude_config = Path.home() / ".claude.json"
        if claude_config.exists():
            assert gc["exists"] is True
            assert gc["status"] in ["ok", "invalid"]
            assert gc["servers"] >= 0

    def test_audit_finds_project_configs(self):
        """Test that audit finds project-level .claude.json files."""
        manager = MCPManager()

        config = AuditConfiguration(
            search_directories=[Path.home() / "Apps"],
            use_defaults=False,
        )
        result = manager.audit_configurations(config=config)

        # project_configs is a dict of project_name -> config_info
        assert isinstance(result["project_configs"], dict)

        # Each project config should have required fields
        for project_name, project_info in result["project_configs"].items():
            assert isinstance(project_info, dict)
            assert "servers" in project_info
            assert "path" in project_info
            assert "status" in project_info


# Contract examples verification


def test_contract_example_audit_with_custom_paths():
    """Verify example from contract: audit with custom paths."""
    manager = MCPManager()

    custom_paths = [Path.home() / "Apps"]
    config = AuditConfiguration(
        search_directories=custom_paths,
        use_defaults=False,
    )
    result = manager.audit_configurations(config=config)

    # Should match contract example output structure
    assert "global_config" in result
    assert "project_configs" in result
    assert "search_paths_used" in result

    # Verify custom paths were used
    assert str(custom_paths[0]) in result["search_paths_used"]


def test_contract_example_audit_with_defaults():
    """Verify example from contract: audit with defaults."""
    manager = MCPManager()

    config = AuditConfiguration(
        search_directories=None,
        use_defaults=True,
    )
    result = manager.audit_configurations(config=config)

    # Should use default search paths
    assert len(result["search_paths_used"]) > 0

    # Global config should be reported
    assert result["global_config"]["exists"] in [True, False]


def test_contract_example_no_projects_found():
    """Verify example from contract: no projects found."""
    manager = MCPManager()

    # Use an empty directory
    empty_dir = Path("/tmp/mcp_test_empty")
    empty_dir.mkdir(exist_ok=True)

    config = AuditConfiguration(
        search_directories=[empty_dir],
        use_defaults=False,
    )
    result = manager.audit_configurations(config=config)

    # Should return empty project_configs
    # (unless the directory happens to have .claude.json files)
    assert isinstance(result["project_configs"], dict)
    assert len(result["search_paths_used"]) == 1
    assert str(empty_dir) in result["search_paths_used"]

    # Cleanup
    empty_dir.rmdir()
