"""Unit tests for Python environment detection - FIXED VERSION.

Tests:
    - T028-T034: Python environment functions

References:
    - spec.md: FR-001, FR-011
    - tasks.md: T028-T034
"""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

from mcp_manager.python_env import (
    detect_distribution,
    find_system_python,
    get_installation_source,
    get_python_version,
    get_venv_base_python,
    is_python_313,
)


class TestFindSystemPython:
    """Test find_system_python() priority path search."""

    @patch("mcp_manager.python_env.is_python_313")
    def test_find_system_python_package_manager(self, mock_is_313):
        """T028: Verify /usr/bin/python3.13 is found first."""
        # When is_python_313 is called, return True for correct path
        mock_is_313.return_value = True

        # Create actual Path object that exists on system
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.is_file", return_value=True):
                result = find_system_python()

                # Should return first path in PYTHON_SEARCH_PATHS
                assert result is not None
                assert str(result) == "/usr/bin/python3.13"

    @patch("mcp_manager.python_env.is_python_313")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    def test_find_system_python_fallback_order(self, mock_is_file, mock_exists, mock_is_313):
        """T029: Verify fallback to /usr/local/bin when /usr/bin not found."""
        mock_is_313.return_value = True

        # Only second path exists
        def exists_check(self):
            return str(self) == "/usr/local/bin/python3.13"

        def is_file_check(self):
            return str(self) == "/usr/local/bin/python3.13"

        mock_exists.side_effect = exists_check
        mock_is_file.side_effect = is_file_check

        result = find_system_python()

        assert result is not None
        assert str(result) == "/usr/local/bin/python3.13"


class TestGetPythonVersion:
    """Test get_python_version() subprocess parsing."""

    @patch("subprocess.run")
    @patch("pathlib.Path.exists", return_value=True)
    def test_get_python_version_parsing(self, mock_exists, mock_run):
        """T030: Verify version parsing from subprocess output."""
        mock_run.return_value = Mock(
            stdout="Python 3.13.0\n",
            stderr="",
            returncode=0
        )

        result = get_python_version(Path("/usr/bin/python3.13"))

        assert result == (3, 13, 0)


class TestIsPython313:
    """Test is_python_313() version validation."""

    def test_is_python_313_valid(self):
        """T031: Verify (3, 13, 0) returns True."""
        with patch("mcp_manager.python_env.get_python_version", return_value=(3, 13, 0)):
            result = is_python_313(Path("/usr/bin/python3.13"))
            assert result is True

    def test_is_python_313_invalid(self):
        """T032: Verify (3, 12, 0) returns False."""
        with patch("mcp_manager.python_env.get_python_version", return_value=(3, 12, 0)):
            result = is_python_313(Path("/usr/bin/python3.12"))
            assert result is False


class TestDetectDistribution:
    """Test detect_distribution() OS detection."""

    @patch("pathlib.Path.exists", return_value=True)
    @patch("builtins.open", mock_open(read_data='NAME="Ubuntu"\nVERSION_ID="22.04"\n'))
    def test_detect_distribution_ubuntu(self, mock_exists):
        """T033: Verify Ubuntu detection from /etc/os-release."""
        result = detect_distribution()
        assert "Ubuntu" in result


class TestGetVenvBasePython:
    """Test get_venv_base_python() pyvenv.cfg parsing."""

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("builtins.open", mock_open(read_data="home = /usr/bin\n"))
    @patch("sys.base_prefix", "/usr")
    @patch("sys.prefix", "/home/user/.venv")
    def test_get_venv_base_python(self):
        """T034: Verify pyvenv.cfg parsing extracts base Python path."""
        with patch("mcp_manager.python_env.is_python_313", return_value=True):
            result = get_venv_base_python()

            assert result is not None


class TestGetInstallationSource:
    """Test get_installation_source() path-based source detection."""

    def test_get_installation_source_package_manager(self):
        """Verify 'package_manager' for /usr/bin paths."""
        result = get_installation_source(Path("/usr/bin/python3.13"))
        assert result == "package_manager"

    def test_get_installation_source_homebrew(self):
        """Verify 'package_manager' for Homebrew Apple Silicon paths."""
        result = get_installation_source(Path("/opt/homebrew/bin/python3.13"))
        assert result == "package_manager"

    def test_get_installation_source_manual_install(self):
        """Verify 'manual_install' for /usr/local/bin paths."""
        result = get_installation_source(Path("/usr/local/bin/python3.13"))
        assert result == "manual_install"
