"""Unit tests for Python environment detection.

Tests:
    - T028: test_find_system_python_package_manager
    - T029: test_find_system_python_manual_install
    - T030: test_get_python_version_parsing
    - T031: test_is_python_313_valid
    - T032: test_is_python_313_invalid
    - T033: test_detect_distribution_ubuntu
    - T034: test_get_venv_base_python

References:
    - spec.md: FR-001, FR-011
    - data-model.md: PythonEnvironment model
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
    """Test find_system_python() priority path search.

    Tests T028, T029: Priority order /usr/bin → /usr/local/bin → /opt/homebrew/bin
    """

    @patch("mcp_manager.python_env.is_python_313", return_value=True)
    @patch("mcp_manager.python_env.Path")
    def test_find_system_python_package_manager(self, mock_path_class, mock_is_313):
        """T028: Verify /usr/bin/python3.13 is found first (package manager priority)."""
        # Mock: /usr/bin/python3.13 exists and is file
        def path_constructor(path_str):
            mock_path = Mock()
            mock_path.exists.return_value = (path_str == "/usr/bin/python3.13")
            mock_path.is_file.return_value = (path_str == "/usr/bin/python3.13")
            mock_path.__str__ = lambda self: path_str
            mock_path.__eq__ = lambda self, other: str(self) == str(other)
            return mock_path

        mock_path_class.side_effect = path_constructor

        result = find_system_python()

        assert str(result) == "/usr/bin/python3.13"

    @patch("pathlib.Path.exists")
    def test_find_system_python_manual_install(self, mock_exists):
        """T029: Verify /usr/local/bin fallback when /usr/bin not found."""
        # Mock: /usr/bin doesn't exist, but /usr/local/bin does
        def exists_side_effect(path_self):
            path_str = str(path_self)
            if path_str == "/usr/bin/python3.13":
                return False
            elif path_str == "/usr/local/bin/python3.13":
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        result = find_system_python()

        assert result == Path("/usr/local/bin/python3.13")

    @patch("pathlib.Path.exists")
    def test_find_system_python_homebrew_fallback(self, mock_exists):
        """Verify /opt/homebrew/bin fallback (macOS Apple Silicon)."""
        # Mock: Only Homebrew path exists
        def exists_side_effect(path_self):
            return str(path_self) == "/opt/homebrew/bin/python3.13"

        mock_exists.side_effect = exists_side_effect

        result = find_system_python()

        assert result == Path("/opt/homebrew/bin/python3.13")

    @patch("pathlib.Path.exists", return_value=False)
    def test_find_system_python_not_found(self, mock_exists):
        """Verify None returned when Python 3.13 not found anywhere."""
        result = find_system_python()

        assert result is None


class TestGetPythonVersion:
    """Test get_python_version() subprocess parsing.

    Test T030: Version parsing from subprocess output.
    """

    @patch("subprocess.run")
    def test_get_python_version_parsing(self, mock_run):
        """T030: Verify version parsing from 'Python 3.13.0' output."""
        # Mock subprocess output
        mock_run.return_value = Mock(
            stdout="Python 3.13.0\n",
            stderr="",
            returncode=0
        )

        python_path = Path("/usr/bin/python3.13")
        result = get_python_version(python_path)

        assert result == (3, 13, 0)
        mock_run.assert_called_once_with(
            [str(python_path), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )

    @patch("subprocess.run")
    def test_get_python_version_with_suffix(self, mock_run):
        """Verify version parsing with release candidate suffix."""
        mock_run.return_value = Mock(
            stdout="Python 3.13.1rc2\n",
            returncode=0
        )

        result = get_python_version(Path("/usr/bin/python3.13"))

        assert result == (3, 13, 1)

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "cmd"))
    def test_get_python_version_command_fails(self, mock_run):
        """Verify None returned when --version command fails."""
        result = get_python_version(Path("/usr/bin/python3.13"))

        assert result is None

    @patch("subprocess.run")
    def test_get_python_version_invalid_format(self, mock_run):
        """Verify None returned when version output format is invalid."""
        mock_run.return_value = Mock(
            stdout="Invalid version string\n",
            returncode=0
        )

        result = get_python_version(Path("/usr/bin/python3.13"))

        assert result is None


class TestIsPython313:
    """Test is_python_313() version validation.

    Tests T031, T032: True for 3.13.x, False otherwise.
    """

    def test_is_python_313_valid(self):
        """T031: Verify (3, 13, 0) returns True."""
        python_path = Path("/usr/bin/python3.13")

        with patch("mcp_manager.python_env.get_python_version", return_value=(3, 13, 0)):
            result = is_python_313(python_path)

        assert result is True

    def test_is_python_313_invalid(self):
        """T032: Verify (3, 12, 0) returns False."""
        python_path = Path("/usr/bin/python3.12")

        with patch("mcp_manager.python_env.get_python_version", return_value=(3, 12, 0)):
            result = is_python_313(python_path)

        assert result is False

    def test_is_python_313_patch_version(self):
        """Verify 3.13.5 returns True (any patch version OK)."""
        python_path = Path("/usr/bin/python3.13")

        with patch("mcp_manager.python_env.get_python_version", return_value=(3, 13, 5)):
            result = is_python_313(python_path)

        assert result is True

    def test_is_python_313_wrong_major(self):
        """Verify 2.7.x returns False."""
        python_path = Path("/usr/bin/python2.7")

        with patch("mcp_manager.python_env.get_python_version", return_value=(2, 7, 18)):
            result = is_python_313(python_path)

        assert result is False

    def test_is_python_313_future_version(self):
        """Verify 3.14.x returns False (must be exactly 3.13)."""
        python_path = Path("/usr/bin/python3.14")

        with patch("mcp_manager.python_env.get_python_version", return_value=(3, 14, 0)):
            result = is_python_313(python_path)

        assert result is False


class TestDetectDistribution:
    """Test detect_distribution() OS detection.

    Test T033: Ubuntu detection from /etc/os-release.
    """

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='NAME="Ubuntu"\nVERSION="22.04 LTS (Jammy Jellyfish)"\n')
    def test_detect_distribution_ubuntu(self, mock_file, mock_exists):
        """T033: Verify Ubuntu detection from /etc/os-release."""
        # Mock /etc/os-release exists
        def exists_side_effect(path_self):
            return str(path_self) == "/etc/os-release"

        mock_exists.side_effect = exists_side_effect

        result = detect_distribution()

        assert "Ubuntu" in result
        mock_file.assert_called_once_with(Path("/etc/os-release"), "r")

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='NAME="Fedora Linux"\nVERSION="38 (Workstation Edition)"\n')
    def test_detect_distribution_fedora(self, mock_file, mock_exists):
        """Verify Fedora detection from /etc/os-release."""
        def exists_side_effect(path_self):
            return str(path_self) == "/etc/os-release"

        mock_exists.side_effect = exists_side_effect

        result = detect_distribution()

        assert "Fedora" in result

    @patch("pathlib.Path.exists", return_value=False)
    @patch("platform.system", return_value="Darwin")
    @patch("platform.machine", return_value="arm64")
    def test_detect_distribution_macos_apple_silicon(self, mock_machine, mock_system, mock_exists):
        """Verify macOS Apple Silicon detection."""
        result = detect_distribution()

        assert result == "macOS (Apple Silicon)"

    @patch("pathlib.Path.exists", return_value=False)
    @patch("platform.system", return_value="Darwin")
    @patch("platform.machine", return_value="x86_64")
    def test_detect_distribution_macos_intel(self, mock_machine, mock_system, mock_exists):
        """Verify macOS Intel detection."""
        result = detect_distribution()

        assert result == "macOS (Intel)"

    @patch("pathlib.Path.exists", return_value=False)
    @patch("platform.system", return_value="Linux")
    def test_detect_distribution_unknown_linux(self, mock_system, mock_exists):
        """Verify fallback for unknown Linux distribution."""
        result = detect_distribution()

        assert result == "Linux"


class TestGetVenvBasePython:
    """Test get_venv_base_python() pyvenv.cfg parsing.

    Test T034: pyvenv.cfg parsing for base Python path.
    """

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="home = /usr/bin\ninclude-system-site-packages = false\nversion = 3.13.0\n")
    @patch.dict("os.environ", {"VIRTUAL_ENV": "/home/user/.venv"})
    def test_get_venv_base_python(self, mock_file, mock_exists):
        """T034: Verify pyvenv.cfg parsing extracts base Python path."""
        # Mock pyvenv.cfg exists
        def exists_side_effect(path_self):
            return str(path_self).endswith("pyvenv.cfg")

        mock_exists.side_effect = exists_side_effect

        result = get_venv_base_python()

        assert result == Path("/usr/bin/python3.13")

    def test_get_venv_base_python_not_in_venv(self):
        """Verify None returned when not in virtual environment."""
        # Mock sys to simulate NOT being in venv (base_prefix == prefix)
        import sys
        with patch.object(sys, "base_prefix", "/usr"), \
             patch.object(sys, "prefix", "/usr"):
            result = get_venv_base_python()

            assert result is None

    @patch("pathlib.Path.exists", return_value=False)
    @patch.dict("os.environ", {"VIRTUAL_ENV": "/home/user/.venv"})
    def test_get_venv_base_python_missing_config(self, mock_exists):
        """Verify None returned when pyvenv.cfg missing."""
        result = get_venv_base_python()

        assert result is None

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="include-system-site-packages = false\nversion = 3.13.0\n")
    @patch.dict("os.environ", {"VIRTUAL_ENV": "/home/user/.venv"})
    def test_get_venv_base_python_missing_home(self, mock_file, mock_exists):
        """Verify None returned when 'home' key missing in pyvenv.cfg."""
        def exists_side_effect(path_self):
            return str(path_self).endswith("pyvenv.cfg")

        mock_exists.side_effect = exists_side_effect

        result = get_venv_base_python()

        assert result is None


class TestGetInstallationSource:
    """Test get_installation_source() path-based source detection."""

    def test_get_installation_source_package_manager(self):
        """Verify 'package_manager' for /usr/bin paths."""
        result = get_installation_source(Path("/usr/bin/python3.13"))

        assert result == "package_manager"

    def test_get_installation_source_manual_install(self):
        """Verify 'manual_install' for /usr/local/bin paths."""
        result = get_installation_source(Path("/usr/local/bin/python3.13"))

        assert result == "manual_install"

    def test_get_installation_source_homebrew(self):
        """Verify 'package_manager' for Homebrew paths."""
        result = get_installation_source(Path("/opt/homebrew/bin/python3.13"))

        assert result == "package_manager"

    def test_get_installation_source_unknown(self):
        """Verify 'unknown' for unrecognized paths."""
        result = get_installation_source(Path("/home/user/.local/bin/python3.13"))

        assert result == "unknown"
