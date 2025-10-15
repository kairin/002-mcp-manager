# Research: System Python Enforcement

**Date**: 2025-10-15
**Feature**: System Python Enforcement (001)
**Purpose**: Technology research and decision documentation for enforcing Python 3.13 system usage

## Overview

This document consolidates research findings for implementing system Python 3.13 enforcement across mcp-manager, preventing UV from installing additional Python interpreters.

## 1. UV Configuration Mechanism

### Decision: Use `uv.toml` for project-local configuration

**Rationale**:
- `uv.toml` takes precedence over `pyproject.toml` sections
- Dedicated UV configuration file improves clarity
- Separates UV-specific settings from Python package metadata
- Already have `.python-version` file (pinned to `3.13`)

**Location**: `/home/kkk/Apps/002-mcp-manager/uv.toml` (project root)

**Configuration Precedence** (highest to lowest):
1. Command-line arguments
2. Environment variables
3. **Project-level config** (`uv.toml` or `pyproject.toml` with `[tool.uv]`)
4. User-level config (`~/.config/uv/uv.toml` on Linux/macOS)
5. System-level config (`/etc/uv/uv.toml` on Linux/macOS)

**Alternatives Considered**:
- `pyproject.toml` with `[tool.uv]` section: Less clear separation, lower precedence
- Environment variables only: Not portable, requires shell configuration
- `.uv/config` directory: Not standard UV format (UV uses `uv.toml`)

## 2. Python Detection Strategy

### Decision: Multi-path search with priority order

**Rationale**:
- Different package managers use different paths
- Need predictable resolution for multiple installations
- Must work across Linux distributions and macOS

**Implementation Strategy**:

```python
PYTHON_SEARCH_PATHS = [
    "/usr/bin/python3.13",           # Package manager (Debian, Ubuntu, Fedora, RHEL)
    "/usr/local/bin/python3.13",     # Manual install (Linux) or Homebrew (older macOS)
    "/opt/homebrew/bin/python3.13",  # Homebrew (Apple Silicon macOS)
]

def find_system_python() -> Path | None:
    """Search for Python 3.13 in priority order."""
    for path in PYTHON_SEARCH_PATHS:
        if Path(path).exists() and is_valid_python_313(path):
            return Path(path)
    return None
```

**Version Verification Method**: Use `subprocess` to run `python3.13 --version` and parse output
- More reliable than `sys.version_info` (which reflects current interpreter)
- Works for validating external Python installations
- Example: `"Python 3.13.0"` → extract `(3, 13, 0)`

**Virtual Environment Detection**:
- Read `pyvenv.cfg` file in venv directory
- Parse `home = /path/to/base/python` line
- Verify base Python points to system Python 3.13 path

**Alternatives Considered**:
- `sys.version_info`: Only works for current interpreter, not external validation
- PATH-based search: Unreliable due to user PATH modifications
- `which python3.13`: Subject to PATH manipulation, less predictable

## 3. UV Python Enforcement

### Decision: Use `python-preference = "only-system"` + `python-downloads = "never"`

**Rationale**:
- `only-system` forces UV to use system Python exclusively
- `never` completely prevents Python downloads
- Combined settings ensure constitutional compliance (FR-002, FR-003)

**Configuration** (`uv.toml`):

```toml
# Prevent automatic Python downloads (FR-003)
python-downloads = "never"

# Force UV to use only system Python installations (FR-002)
python-preference = "only-system"
```

**Additional Enforcement**:
- `.python-version` file with `3.13` content (already exists)
- `requires-python = ">=3.11"` in `pyproject.toml` (already exists)

**Error Handling**:
- UV will error if system Python 3.13 not found → meets FR-004 requirement
- Explicit error messages guide users to install Python 3.13
- No silent fallbacks or automatic downloads

**Alternatives Considered**:
- `python-preference = "system"`: Still allows managed Python as fallback
- `python-downloads = "manual"`: Allows downloads during explicit `uv python install`
- Environment variables only: Not persistent, requires shell configuration

## 4. Validation Command Best Practices

### Decision: Summary output with optional `--verbose` flag

**Rationale**:
- Aligns with clarification answer (Question 2)
- Supports both human operators and CI/CD automation
- Follows Unix philosophy (silent success, informative failure)

**Exit Code Convention**:
- `0`: Validation passed (system Python 3.13 in use, UV configured correctly)
- `1`: Validation failed (constitutional violation detected)
- `2`: Validation error (unable to complete checks, e.g., UV not installed)

**Output Format**:

**Summary Mode** (default):
```
✓ PASS: System Python 3.13 enforcement validated
  Python: /usr/bin/python3.13 (3.13.0)
  UV Config: Compliant (only-system, downloads=never)
```

**Verbose Mode** (`--verbose`):
```
System Python Enforcement Validation Report
============================================

Python Environment:
  Executable: /usr/bin/python3.13
  Version: 3.13.0
  Source: Package manager (apt)
  Virtual Env: None

UV Configuration:
  Config File: /home/user/project/uv.toml
  python-preference: only-system ✓
  python-downloads: never ✓
  .python-version: 3.13 ✓

Validation Checks:
  ✓ Python 3.13 detected
  ✓ Python from approved path (/usr/bin)
  ✓ UV prevents Python downloads
  ✓ UV uses system Python only
  ✓ No virtual environment conflicts

Result: PASS
```

**CI/CD Integration**:
- Exit code 0 for success allows `mcp-manager validate || exit 1` in scripts
- Summary output provides quick pass/fail indication
- Verbose mode aids debugging on CI/CD failures

**Alternatives Considered**:
- JSON output: Over-engineered for current needs, can add later if needed
- Always verbose: Too noisy for CI/CD logs
- Exit code only: Insufficient feedback for debugging

## 5. Cross-Distribution Compatibility

### Decision: Path priority list with distribution detection

**Rationale**:
- Different package managers install to different locations
- Priority order ensures predictable selection (package manager > manual)
- Distribution detection helps provide specific error messages

**Python Path Mapping**:

| Distribution | Package Manager | Python 3.13 Path |
|--------------|----------------|------------------|
| Debian/Ubuntu | apt | `/usr/bin/python3.13` |
| Fedora/RHEL | dnf/yum | `/usr/bin/python3.13` |
| Arch Linux | pacman | `/usr/bin/python3.13` |
| macOS (Intel) | Homebrew | `/usr/local/bin/python3.13` |
| macOS (Apple Silicon) | Homebrew | `/opt/homebrew/bin/python3.13` |
| Manual install (Linux) | N/A | `/usr/local/bin/python3.13` |

**Distribution Detection** (for error messages):

```python
def detect_distribution() -> str:
    """Detect Linux distribution or macOS."""
    if sys.platform == "darwin":
        # Detect Homebrew architecture
        if Path("/opt/homebrew").exists():
            return "macOS (Apple Silicon)"
        return "macOS (Intel)"

    # Read /etc/os-release on Linux
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("ID="):
                    dist_id = line.split("=")[1].strip().strip('"')
                    return {
                        "ubuntu": "Ubuntu",
                        "debian": "Debian",
                        "fedora": "Fedora",
                        "rhel": "RHEL",
                        "arch": "Arch Linux"
                    }.get(dist_id, dist_id.capitalize())
    except FileNotFoundError:
        pass

    return "Linux (unknown)"
```

**Error Message Example**:
```
ERROR: Python 3.13 not found on your system.

Detected OS: Ubuntu
Installation command: sudo apt install python3.13

Expected location: /usr/bin/python3.13
Searched locations:
  ✗ /usr/bin/python3.13
  ✗ /usr/local/bin/python3.13
  ✗ /opt/homebrew/bin/python3.13
```

**Alternatives Considered**:
- Single hardcoded path: Breaks on different distributions
- PATH-based search: Unreliable due to user customization
- Require manual configuration: Poor UX, violates FR-011

## 6. Additional Research Findings

### Python Version Parsing

**Method**: `subprocess` + regex parsing

```python
import subprocess
import re
from pathlib import Path

def get_python_version(python_path: Path) -> tuple[int, int, int] | None:
    """Get Python version from executable."""
    try:
        result = subprocess.run(
            [str(python_path), "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Output: "Python 3.13.0" or "Python 3.13.0rc2"
        match = re.match(r"Python (\d+)\.(\d+)\.(\d+)", result.stdout)
        if match:
            return tuple(map(int, match.groups()))
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass
    return None

def is_python_313(python_path: Path) -> bool:
    """Check if Python executable is version 3.13.x."""
    version = get_python_version(python_path)
    return version is not None and version[:2] == (3, 13)
```

### Virtual Environment Base Python Detection

**Method**: Parse `pyvenv.cfg` file

```python
def get_venv_base_python(venv_path: Path) -> Path | None:
    """Get base Python from virtual environment."""
    pyvenv_cfg = venv_path / "pyvenv.cfg"
    if not pyvenv_cfg.exists():
        return None

    try:
        with open(pyvenv_cfg) as f:
            for line in f:
                if line.startswith("home = "):
                    # home = /usr/bin
                    bin_dir = Path(line.split("=", 1)[1].strip())
                    # Return full path: /usr/bin/python3.13
                    return bin_dir / "python3.13"
    except (IOError, ValueError):
        pass

    return None

def is_venv_based_on_system_python(venv_path: Path, system_python: Path) -> bool:
    """Check if venv uses system Python 3.13."""
    base_python = get_venv_base_python(venv_path)
    return base_python == system_python
```

### UV Configuration Validation

**Method**: Parse `uv.toml` or `pyproject.toml`

```python
import tomllib  # Python 3.11+
from pathlib import Path

def validate_uv_config(project_root: Path) -> dict[str, bool]:
    """Validate UV configuration for compliance."""
    results = {
        "python_downloads_disabled": False,
        "python_preference_system_only": False,
        "python_version_pinned": False
    }

    # Check uv.toml (takes precedence)
    uv_toml = project_root / "uv.toml"
    if uv_toml.exists():
        with open(uv_toml, "rb") as f:
            config = tomllib.load(f)
            results["python_downloads_disabled"] = (
                config.get("python-downloads") in ("never", "manual")
            )
            results["python_preference_system_only"] = (
                config.get("python-preference") == "only-system"
            )

    # Check .python-version
    python_version_file = project_root / ".python-version"
    if python_version_file.exists():
        content = python_version_file.read_text().strip()
        results["python_version_pinned"] = content == "3.13"

    return results
```

## 7. Implementation Recommendations

### Phase 1 Deliverables

1. **Create `uv.toml`** with enforcement configuration
2. **Implement `src/mcp_manager/python_env.py`**:
   - `find_system_python()`: Multi-path search
   - `get_python_version()`: Version validation
   - `is_python_313()`: Version check
   - `detect_distribution()`: OS/distro detection
   - `get_venv_base_python()`: Venv validation

3. **Implement `src/mcp_manager/uv_config.py`**:
   - `validate_uv_config()`: Config compliance check
   - `get_uv_config_path()`: Config file location
   - `check_uv_installed()`: UV availability check

4. **Implement `src/mcp_manager/validators.py`**:
   - `validate_python_environment()`: Main validation orchestrator
   - CLI command handler for `mcp-manager validate`

### Phase 2 Test Coverage

1. **Unit Tests**:
   - Python version parsing (various formats)
   - Path priority resolution
   - Virtual environment detection
   - UV configuration parsing

2. **Integration Tests**:
   - Python detection across distributions (mocked paths)
   - UV configuration enforcement (temporary config files)
   - Virtual environment validation (created test venvs)

3. **Contract Tests**:
   - Validation command exit codes
   - Summary vs verbose output format
   - Error message clarity

## 8. Open Questions / Future Considerations

### Resolved
- ✅ UV configuration format: `uv.toml` selected
- ✅ Python path priority: Package manager first, then manual
- ✅ Validation output format: Summary with optional `--verbose`
- ✅ Virtual environment handling: Validate base Python

### Deferred (Out of Scope)
- Windows support: Explicitly out of scope per spec
- Python 3.14 forward compatibility: Will address when Python 3.14 released
- Custom Python paths: Not needed given search strategy
- Multiple Python version support: Explicitly excluded per spec

## Summary

All research questions resolved. Ready to proceed to Phase 1 design (data models, contracts, quickstart).

**Key Decisions**:
1. **UV Config**: `uv.toml` with `python-preference="only-system"` + `python-downloads="never"`
2. **Python Detection**: Priority-ordered path search (`/usr/bin` → `/usr/local/bin` → `/opt/homebrew/bin`)
3. **Validation Command**: Summary output (default) + `--verbose` flag for diagnostics
4. **Cross-Platform**: Distribution detection for targeted error messages
5. **Venv Handling**: Validate base Python from `pyvenv.cfg` file

**Next Steps**: Create data models, API contracts, and quickstart guide (Phase 1).
