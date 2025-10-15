# Quickstart: System Python Enforcement

**Feature**: System Python Enforcement (002)
**Date**: 2025-10-15
**Target Audience**: Developers implementing the feature

## Overview

This quickstart guide provides a rapid introduction to implementing the system Python 3.13 enforcement feature for mcp-manager. Follow these steps to understand the architecture, set up your development environment, and begin implementation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     mcp-manager validate                     │
│                    (CLI Command Entry)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              validators.py                                   │
│         validate_python_environment()                        │
│              (Orchestrator)                                  │
└─────┬──────────────────────┬──────────────────────┬─────────┘
      │                      │                      │
      ▼                      ▼                      ▼
┌─────────────┐    ┌──────────────────┐    ┌──────────────┐
│ python_env  │    │   uv_config.py   │    │  models.py   │
│    .py      │    │                  │    │              │
│             │    │                  │    │ Pydantic v2  │
│ - find      │    │ - validate_uv_   │    │  Models:     │
│   _system_  │    │   config()       │    │              │
│   python()  │    │ - check_uv_      │    │ - Python     │
│             │    │   installed()    │    │   Environment│
│ - get       │    │ - get_uv_        │    │ - UV         │
│   _python_  │    │   config_path()  │    │   Config     │
│   version() │    │                  │    │ - Validation │
│             │    │                  │    │   Result     │
│ - detect    │    │                  │    │              │
│   _distro() │    │                  │    │              │
└─────────────┘    └──────────────────┘    └──────────────┘
      │                      │
      │                      │
      ▼                      ▼
┌─────────────────────────────────────┐
│        uv.toml (Project Root)        │
│  python-downloads = "never"         │
│  python-preference = "only-system"  │
└─────────────────────────────────────┘
```

## 5-Minute Setup

### Prerequisites

1. **Python 3.13 Installed**:
   ```bash
   # Ubuntu/Debian
   sudo apt install python3.13

   # macOS (Homebrew)
   brew install python@3.13
   ```

2. **UV Installed**:
   ```bash
   # Install UV
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Verify
   uv --version
   ```

3. **Clone Repository**:
   ```bash
   git clone https://github.com/kairin/mcp-manager.git
   cd mcp-manager
   git checkout 001-system-python-enforcement
   ```

### Quick Configuration

1. **Create `uv.toml`** (project root):
   ```bash
   cat > uv.toml <<'EOF'
   # Prevent automatic Python downloads
   python-downloads = "never"

   # Use only system Python installations
   python-preference = "only-system"
   EOF
   ```

2. **Verify `.python-version`** (should already exist):
   ```bash
   cat .python-version
   # Should output: 3.13
   ```

3. **Install Dependencies**:
   ```bash
   uv sync
   ```

### Verify Setup

```bash
# Check Python detection
python3.13 --version
# Expected: Python 3.13.x

# Check UV uses system Python
uv python find
# Expected: /usr/bin/python3.13 (or /usr/local/bin/python3.13)

# Run existing tests
uv run pytest tests/
```

## Key Modules to Implement

### 1. `backend/src/mcp_manager/python_env.py` (NEW)

**Purpose**: Detect and validate system Python 3.13

**Key Functions**:
```python
def find_system_python() -> Path | None:
    """Search for Python 3.13 in priority order."""
    # Priority: /usr/bin → /usr/local/bin → /opt/homebrew/bin
    pass

def get_python_version(python_path: Path) -> tuple[int, int, int] | None:
    """Get version from Python executable."""
    # Run: python3.13 --version
    # Parse: "Python 3.13.0" → (3, 13, 0)
    pass

def is_python_313(python_path: Path) -> bool:
    """Check if Python is version 3.13.x."""
    pass

def detect_distribution() -> str:
    """Detect OS/distribution for error messages."""
    # macOS vs Linux, read /etc/os-release
    pass

def get_venv_base_python(venv_path: Path) -> Path | None:
    """Get base Python from virtual environment."""
    # Parse pyvenv.cfg: home = /usr/bin
    pass
```

**Testing**:
```bash
# Unit tests
uv run pytest tests/unit/test_python_env.py

# Integration tests
uv run pytest tests/integration/test_python_detection.py
```

### 2. `backend/src/mcp_manager/uv_config.py` (NEW)

**Purpose**: Validate UV configuration compliance

**Key Functions**:
```python
def validate_uv_config(project_root: Path) -> UVConfiguration:
    """Validate UV configuration for compliance."""
    # Read uv.toml or pyproject.toml
    # Check python-downloads, python-preference
    # Check .python-version
    pass

def check_uv_installed() -> bool:
    """Check if UV is available in PATH."""
    pass

def get_uv_config_path(project_root: Path) -> Path | None:
    """Find UV configuration file."""
    # Search: uv.toml → pyproject.toml
    pass
```

**Testing**:
```bash
uv run pytest tests/unit/test_uv_config.py
uv run pytest tests/integration/test_uv_integration.py
```

### 3. `backend/src/mcp_manager/validators.py` (NEW)

**Purpose**: Orchestrate validation and generate results

**Key Functions**:
```python
def validate_python_environment(
    project_root: Path,
    verbose: bool = False
) -> ValidationResult:
    """Main validation orchestrator."""
    # 1. find_system_python()
    # 2. validate_uv_config()
    # 3. Build ValidationResult
    # 4. Return with status (PASS/FAIL/ERROR)
    pass
```

**Testing**:
```bash
uv run pytest tests/unit/test_validators.py
```

### 4. Update `backend/src/mcp_manager/cli.py` (EXISTING)

**Purpose**: Add `validate` command

**Implementation**:
```python
import typer
from pathlib import Path
from mcp_manager.validators import validate_python_environment

app = typer.Typer()

@app.command()
def validate(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Display detailed diagnostic information"
    )
):
    """Validate system Python 3.13 enforcement compliance."""
    result = validate_python_environment(
        project_root=Path.cwd(),
        verbose=verbose
    )

    # Output
    if verbose:
        typer.echo(result.to_verbose())
    else:
        typer.echo(result.to_summary())

    # Exit
    raise typer.Exit(code=result.exit_code)
```

**Testing**:
```bash
uv run pytest tests/contract/test_validation_cli.py
```

## Development Workflow

### Step 1: Implement Models (Day 1)

```bash
# Create models.py with Pydantic v2 models
vim backend/src/mcp_manager/models.py

# Add:
# - PythonEnvironment
# - UVConfiguration
# - ValidationResult

# Test
uv run pytest tests/unit/test_models.py -v
```

### Step 2: Implement Python Detection (Day 2)

```bash
# Create python_env.py
vim backend/src/mcp_manager/python_env.py

# Implement:
# - find_system_python()
# - get_python_version()
# - is_python_313()
# - detect_distribution()

# Test
uv run pytest tests/unit/test_python_env.py -v
uv run pytest tests/integration/test_python_detection.py -v
```

### Step 3: Implement UV Configuration (Day 3)

```bash
# Create uv_config.py
vim backend/src/mcp_manager/uv_config.py

# Implement:
# - validate_uv_config()
# - check_uv_installed()
# - get_uv_config_path()

# Test
uv run pytest tests/unit/test_uv_config.py -v
uv run pytest tests/integration/test_uv_integration.py -v
```

### Step 4: Implement Validation Orchestrator (Day 4)

```bash
# Create validators.py
vim backend/src/mcp_manager/validators.py

# Implement:
# - validate_python_environment()

# Test
uv run pytest tests/unit/test_validators.py -v
```

### Step 5: Add CLI Command (Day 5)

```bash
# Update cli.py
vim backend/src/mcp_manager/cli.py

# Add validate command

# Test
uv run pytest tests/contract/test_validation_cli.py -v

# Manual test
uv run mcp-manager validate
uv run mcp-manager validate --verbose
```

### Step 6: Integration Testing (Day 6)

```bash
# Run full test suite
uv run pytest tests/ -v --cov=mcp_manager

# Check coverage
uv run pytest --cov=mcp_manager --cov-report=html
# Open htmlcov/index.html

# Verify >80% coverage required
```

### Step 7: Code Quality (Day 7)

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# All must pass before commit
```

## Testing Strategy

### Unit Tests (tests/unit/)

- `test_python_env.py`: Python detection logic
- `test_uv_config.py`: UV configuration parsing
- `test_validators.py`: Validation orchestration
- `test_models.py`: Pydantic model validation

### Integration Tests (tests/integration/)

- `test_python_detection.py`: Real Python installation detection
- `test_uv_integration.py`: UV configuration file interaction

### Contract Tests (tests/contract/)

- `test_validation_cli.py`: CLI command behavior and output format

### Run All Tests

```bash
# Quick run
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=mcp_manager --cov-report=term-missing

# Specific module
uv run pytest tests/unit/test_python_env.py::test_find_system_python -v

# Performance test (validate < 2s)
time uv run mcp-manager validate
```

## Common Development Tasks

### Add New Python Search Path

```python
# backend/src/mcp_manager/python_env.py
PYTHON_SEARCH_PATHS = [
    "/usr/bin/python3.13",
    "/usr/local/bin/python3.13",
    "/opt/homebrew/bin/python3.13",
    "/custom/path/python3.13",  # NEW
]
```

### Add New UV Configuration Setting

```python
# backend/src/mcp_manager/models.py
class UVConfiguration(BaseModel):
    # ... existing fields ...
    new_setting: str | None = Field(
        default=None,
        description="New UV setting"
    )
```

### Add New Validation Check

```python
# backend/src/mcp_manager/validators.py
def validate_python_environment(...) -> ValidationResult:
    # ... existing checks ...

    # New check
    if some_condition:
        result.checks_performed.append("New check description")
```

## Debugging Tips

### Debug Python Detection

```bash
# Check which Python UV would use
uv python find

# List all Python installations UV knows about
uv python list

# Manually test Python version
/usr/bin/python3.13 --version
```

### Debug UV Configuration

```bash
# Check current UV config
cat uv.toml

# Test UV sync with system Python
uv sync --python /usr/bin/python3.13 --dry-run

# Verify UV won't download Python
uv python install 3.13  # Should fail with current config
```

### Debug Validation Command

```bash
# Run with verbose output
uv run mcp-manager validate --verbose

# Check exit code
uv run mcp-manager validate; echo $?

# Add debug logging
export LOG_LEVEL=DEBUG
uv run mcp-manager validate --verbose
```

## Next Steps

After completing the quickstart:

1. **Read Detailed Design**:
   - [Data Models](./data-model.md)
   - [CLI Contract](./contracts/validation_cli.md)
   - [Research Findings](./research.md)

2. **Implement Tasks**:
   - Run `/speckit.tasks` to generate task breakdown
   - Follow TDD workflow (tests first)

3. **Submit for Review**:
   - Ensure all tests pass
   - Run code quality checks
   - Create pull request

## Resources

- **Feature Spec**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **UV Documentation**: https://docs.astral.sh/uv/
- **Pydantic v2 Docs**: https://docs.pydantic.dev/latest/
- **CLAUDE.md**: `/CLAUDE.md` (project requirements)

## Support

For questions or issues during implementation:
1. Review research findings in `research.md`
2. Check contracts in `contracts/validation_cli.md`
3. Refer to existing mcp-manager modules for patterns
4. Consult CLAUDE.md for constitutional requirements

---

**Last Updated**: 2025-10-15
**Status**: Ready for Implementation
