"""Integration tests for real system Python detection.

Tests:
    - T038: test_python_detection_real_system

References:
    - spec.md: FR-001, FR-011
    - tasks.md: T038
"""

import subprocess
import sys
from pathlib import Path

import pytest

from mcp_manager.python_env import (
    detect_distribution,
    find_system_python,
    get_python_version,
    is_python_313,
)


class TestPythonDetectionRealSystem:
    """Integration tests using real system Python (not mocked).

    Test T038: Real system Python 3.13 detection.
    """

    def test_python_detection_real_system(self):
        """T038: Verify real system Python 3.13 detection (not mocked)."""
        # This test uses actual system calls - no mocking
        python_path = find_system_python()

        # System Python 3.13 should be found
        assert python_path is not None, "System Python 3.13 not found. Is it installed?"
        assert python_path.exists(), f"Python path {python_path} does not exist"
        assert python_path.is_file(), f"Python path {python_path} is not a file"

        # Verify it's in expected priority locations
        expected_dirs = ["/usr/bin", "/usr/local/bin", "/opt/homebrew/bin"]
        assert any(str(python_path.parent) == dir for dir in expected_dirs), \
            f"Python not in expected locations: {python_path}"

    def test_get_python_version_real(self):
        """Verify get_python_version() works with real Python executable."""
        python_path = find_system_python()
        pytest.skip if python_path is None else None

        version = get_python_version(python_path)

        assert version is not None, f"Could not get version from {python_path}"
        assert len(version) == 3, f"Version should be (major, minor, patch): {version}"
        assert all(isinstance(v, int) for v in version), f"Version parts must be integers: {version}"

    def test_is_python_313_real(self):
        """Verify is_python_313() correctly identifies system Python."""
        python_path = find_system_python()
        pytest.skip if python_path is None else None

        result = is_python_313(python_path)

        assert result is True, f"Python at {python_path} is not 3.13.x"

        # Also verify version directly
        version = get_python_version(python_path)
        assert version[0] == 3, f"Major version should be 3: {version}"
        assert version[1] == 13, f"Minor version should be 13: {version}"

    def test_detect_distribution_real(self):
        """Verify detect_distribution() returns valid distribution name."""
        distribution = detect_distribution()

        assert distribution is not None
        assert isinstance(distribution, str)
        assert len(distribution) > 0

        # Should contain one of the expected patterns
        valid_patterns = [
            "Ubuntu", "Debian", "Fedora", "Red Hat", "CentOS",
            "macOS", "Linux"
        ]
        assert any(pattern in distribution for pattern in valid_patterns), \
            f"Distribution '{distribution}' doesn't match expected patterns"

    def test_python_executable_runs(self):
        """Verify found Python executable actually runs."""
        python_path = find_system_python()
        pytest.skip if python_path is None else None

        # Try running a simple command
        result = subprocess.run(
            [str(python_path), "-c", "print('test')"],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0, f"Python execution failed: {result.stderr}"
        assert "test" in result.stdout

    def test_current_interpreter_is_313(self):
        """Verify the current test interpreter is Python 3.13."""
        # This test validates the test environment itself
        current_version = sys.version_info

        assert current_version.major == 3, f"Not Python 3: {current_version}"
        assert current_version.minor == 13, f"Not Python 3.13: {current_version}"

    @pytest.mark.slow
    def test_python_can_import_stdlib(self):
        """Verify system Python can import standard library modules."""
        python_path = find_system_python()
        pytest.skip if python_path is None else None

        # Test importing various stdlib modules
        test_imports = [
            "import sys",
            "import pathlib",
            "import subprocess",
            "import json",
            "import re"
        ]

        for import_stmt in test_imports:
            result = subprocess.run(
                [str(python_path), "-c", import_stmt],
                capture_output=True,
                text=True,
                timeout=5
            )

            assert result.returncode == 0, \
                f"Failed to import: {import_stmt}\n{result.stderr}"
