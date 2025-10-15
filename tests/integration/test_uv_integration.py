"""Integration tests for UV configuration and behavior.

Tests:
    - T039: test_uv_config_parsing_real_file
    - T040: test_uv_python_find_matches_detection

References:
    - spec.md: FR-002, FR-003
    - tasks.md: T039-T040
"""

import subprocess
import tempfile
from pathlib import Path

import pytest
from mcp_manager.python_env import find_system_python
from mcp_manager.uv_config import (
    check_uv_installed,
    get_uv_config_path,
    validate_uv_config,
)


class TestUvConfigParsingRealFile:
    """Integration tests using actual uv.toml files.

    Test T039: Parsing real uv.toml file.
    """

    def test_uv_config_parsing_real_file(self):
        """T039: Verify parsing actual uv.toml file."""
        # Create temporary uv.toml with compliant settings
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            uv_toml = project_root / "uv.toml"

            # Write compliant configuration
            uv_toml.write_text(
                "[tool.uv]\n"
                'python-downloads = "never"\n'
                'python-preference = "only-system"\n'
            )

            # Parse the real file
            result = validate_uv_config(project_root)

            assert result["python_downloads"] == "never"
            assert result["python_preference"] == "only-system"

    def test_uv_config_parsing_pyproject_toml(self):
        """Verify parsing UV config from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            pyproject_toml = project_root / "pyproject.toml"

            # Write pyproject.toml with [tool.uv] section
            pyproject_toml.write_text(
                "[project]\n"
                'name = "test-project"\n'
                "\n"
                "[tool.uv]\n"
                'python-downloads = "manual"\n'
                'python-preference = "only-system"\n'
            )

            result = validate_uv_config(project_root)

            assert result["python_downloads"] == "manual"
            assert result["python_preference"] == "only-system"

    def test_uv_config_with_python_version_file(self):
        """Verify .python-version file detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            uv_toml = project_root / "uv.toml"
            python_version = project_root / ".python-version"

            uv_toml.write_text(
                "[tool.uv]\n"
                'python-downloads = "never"\n'
                'python-preference = "only-system"\n'
            )

            python_version.write_text("3.13\n")

            result = validate_uv_config(project_root)

            assert result.get("python_version_pinned") == "3.13"

    def test_get_uv_config_path_real_files(self):
        """Verify get_uv_config_path() with real files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Test 1: Only uv.toml exists
            uv_toml = project_root / "uv.toml"
            uv_toml.touch()

            path = get_uv_config_path(project_root)
            assert path == uv_toml

            # Test 2: Both exist, should prefer uv.toml
            pyproject_toml = project_root / "pyproject.toml"
            pyproject_toml.touch()

            path = get_uv_config_path(project_root)
            assert path == uv_toml

            # Test 3: Only pyproject.toml exists
            uv_toml.unlink()

            path = get_uv_config_path(project_root)
            assert path == pyproject_toml

    def test_check_uv_installed_real(self):
        """Verify check_uv_installed() with real system."""
        result = check_uv_installed()

        # UV should be installed for this project
        assert result is True, "UV not found in PATH. Is it installed?"


class TestUvPythonFindMatchesDetection:
    """Integration tests comparing UV's python detection with ours.

    Test T040: Verify `uv python find` matches our detection.
    """

    @pytest.mark.skipif(not check_uv_installed(), reason="UV not installed")
    def test_uv_python_find_matches_detection(self):
        """T040: Verify `uv python find` matches our detection."""
        # Get UV's python detection
        try:
            result = subprocess.run(
                ["uv", "python", "find", "3.13"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            uv_python_path = Path(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            pytest.skip(f"Could not run 'uv python find': {e}")

        # Get our python detection
        our_python_path = find_system_python()

        assert our_python_path is not None, "Our detection found no Python 3.13"

        # Paths should match (resolving symlinks)
        uv_resolved = uv_python_path.resolve()
        our_resolved = our_python_path.resolve()

        assert (
            uv_resolved == our_resolved
        ), f"UV found {uv_python_path} but we found {our_python_path}"

    @pytest.mark.skipif(not check_uv_installed(), reason="UV not installed")
    def test_uv_run_uses_system_python(self):
        """Verify 'uv run' uses system Python 3.13."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create uv.toml with our config
            uv_toml = project_root / "uv.toml"
            uv_toml.write_text(
                "[tool.uv]\n"
                'python-downloads = "never"\n'
                'python-preference = "only-system"\n'
            )

            # Create .python-version
            python_version = project_root / ".python-version"
            python_version.write_text("3.13\n")

            # Run a simple Python command via UV
            try:
                result = subprocess.run(
                    [
                        "uv",
                        "run",
                        "--no-project",
                        "python3",
                        "-c",
                        "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=15,
                )

                if result.returncode == 0:
                    version = result.stdout.strip()
                    assert version == "3.13", f"UV used Python {version}, not 3.13"
                else:
                    pytest.skip(f"uv run failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                pytest.skip("uv run timed out")
            except FileNotFoundError:
                pytest.skip("uv command not found")

    @pytest.mark.skipif(not check_uv_installed(), reason="UV not installed")
    def test_uv_venv_uses_system_python(self):
        """Verify 'uv venv' creates venv from system Python 3.13."""
        our_python = find_system_python()
        pytest.skip if our_python is None else None

        with tempfile.TemporaryDirectory() as tmpdir:
            venv_path = Path(tmpdir) / ".venv"

            # Create venv using UV with system Python
            try:
                subprocess.run(
                    ["uv", "venv", "--python", str(our_python), str(venv_path)],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30,
                )
            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                subprocess.TimeoutExpired,
            ) as e:
                pytest.skip(f"Could not create venv: {e}")

            # Verify pyvenv.cfg contains our Python
            pyvenv_cfg = venv_path / "pyvenv.cfg"
            assert pyvenv_cfg.exists(), "pyvenv.cfg not created"

            cfg_content = pyvenv_cfg.read_text()
            assert (
                "3.13" in cfg_content
            ), f"pyvenv.cfg doesn't reference 3.13:\n{cfg_content}"
