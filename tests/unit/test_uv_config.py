"""Unit tests for UV configuration management.

Tests:
    - T035: test_validate_uv_config_compliant
    - T036: test_validate_uv_config_non_compliant

References:
    - spec.md: FR-002, FR-003, FR-006
    - data-model.md: UVConfiguration model
    - tasks.md: T035-T036
"""

from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

from mcp_manager.uv_config import (
    check_uv_installed,
    get_uv_config_path,
    validate_uv_config,
)


class TestValidateUvConfig:
    """Test validate_uv_config() compliance checking.

    Tests T035, T036: Compliant vs non-compliant configuration detection.
    """

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='[tool.uv]\npython-downloads = "never"\npython-preference = "only-system"\n')
    def test_validate_uv_config_compliant(self, mock_file, mock_exists):
        """T035: Verify compliant uv.toml detection (downloads=never, preference=only-system)."""
        project_root = Path("/home/user/project")

        # Mock uv.toml exists
        def exists_side_effect(path_self):
            return str(path_self).endswith("uv.toml")

        mock_exists.side_effect = exists_side_effect

        # Mock get_uv_config_path
        with patch("mcp_manager.uv_config.get_uv_config_path", return_value=project_root / "uv.toml"):
            result = validate_uv_config(project_root)

        assert result["python_downloads"] == "never"
        assert result["python_preference"] == "only-system"
        # Should be considered compliant
        assert result.get("python_downloads") in ("never", "manual")

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='[tool.uv]\npython-downloads = "automatic"\npython-preference = "managed"\n')
    def test_validate_uv_config_non_compliant(self, mock_file, mock_exists):
        """T036: Verify violation detection when python-downloads=automatic."""
        project_root = Path("/home/user/project")

        # Mock uv.toml exists
        def exists_side_effect(path_self):
            return str(path_self).endswith("uv.toml")

        mock_exists.side_effect = exists_side_effect

        # Mock get_uv_config_path
        with patch("mcp_manager.uv_config.get_uv_config_path", return_value=project_root / "uv.toml"):
            result = validate_uv_config(project_root)

        assert result["python_downloads"] == "automatic"
        assert result["python_preference"] == "managed"
        # Should be considered non-compliant
        assert result.get("python_downloads") not in ("never", "manual")

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='[tool.uv]\npython-downloads = "manual"\npython-preference = "only-system"\n')
    def test_validate_uv_config_manual_downloads_allowed(self, mock_file, mock_exists):
        """Verify 'manual' downloads setting is considered compliant."""
        project_root = Path("/home/user/project")

        def exists_side_effect(path_self):
            return str(path_self).endswith("uv.toml")

        mock_exists.side_effect = exists_side_effect

        with patch("mcp_manager.uv_config.get_uv_config_path", return_value=project_root / "uv.toml"):
            result = validate_uv_config(project_root)

        assert result["python_downloads"] == "manual"
        assert result["python_preference"] == "only-system"

    @patch("mcp_manager.uv_config.get_uv_config_path", return_value=None)
    def test_validate_uv_config_file_not_found(self, mock_get_path):
        """Verify empty dict returned when UV config file not found."""
        project_root = Path("/home/user/project")

        result = validate_uv_config(project_root)

        assert result == {}

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_validate_uv_config_with_python_version_pin(self, mock_read_text, mock_exists):
        """Verify .python-version file detection."""
        project_root = Path("/home/user/project")

        # Mock .python-version exists
        def exists_side_effect(path_self):
            path_str = str(path_self)
            if path_str.endswith(".python-version"):
                return True
            elif path_str.endswith("uv.toml"):
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        # Mock file contents
        def read_text_side_effect(path_self):
            if str(path_self).endswith(".python-version"):
                return "3.13\n"
            elif str(path_self).endswith("uv.toml"):
                return '[tool.uv]\npython-downloads = "never"\npython-preference = "only-system"\n'
            return ""

        mock_read_text.side_effect = read_text_side_effect

        with patch("mcp_manager.uv_config.get_uv_config_path", return_value=project_root / "uv.toml"):
            result = validate_uv_config(project_root)

        assert result.get("python_version_pinned") == "3.13"


class TestCheckUvInstalled:
    """Test check_uv_installed() PATH verification."""

    @patch("shutil.which", return_value="/home/user/.local/bin/uv")
    def test_check_uv_installed_found(self, mock_which):
        """Verify True returned when UV found in PATH."""
        result = check_uv_installed()

        assert result is True
        mock_which.assert_called_once_with("uv")

    @patch("shutil.which", return_value=None)
    def test_check_uv_installed_not_found(self, mock_which):
        """Verify False returned when UV not in PATH."""
        result = check_uv_installed()

        assert result is False
        mock_which.assert_called_once_with("uv")


class TestGetUvConfigPath:
    """Test get_uv_config_path() configuration file discovery."""

    @patch("pathlib.Path.exists")
    def test_get_uv_config_path_uv_toml(self, mock_exists):
        """Verify uv.toml preferred over pyproject.toml."""
        project_root = Path("/home/user/project")

        # Mock both files exist, should prefer uv.toml
        def exists_side_effect(path_self):
            path_str = str(path_self)
            return path_str.endswith("uv.toml") or path_str.endswith("pyproject.toml")

        mock_exists.side_effect = exists_side_effect

        result = get_uv_config_path(project_root)

        assert result == project_root / "uv.toml"

    @patch("pathlib.Path.exists")
    def test_get_uv_config_path_pyproject_toml(self, mock_exists):
        """Verify pyproject.toml used when uv.toml missing."""
        project_root = Path("/home/user/project")

        # Mock only pyproject.toml exists
        def exists_side_effect(path_self):
            return str(path_self).endswith("pyproject.toml")

        mock_exists.side_effect = exists_side_effect

        result = get_uv_config_path(project_root)

        assert result == project_root / "pyproject.toml"

    @patch("pathlib.Path.exists", return_value=False)
    def test_get_uv_config_path_not_found(self, mock_exists):
        """Verify None returned when no config file found."""
        project_root = Path("/home/user/project")

        result = get_uv_config_path(project_root)

        assert result is None
