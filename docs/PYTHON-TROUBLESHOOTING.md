# Python Environment Troubleshooting Guide

> 🚨 **CRITICAL**: This guide addresses Python 3.13 and UV configuration issues for mcp-manager constitutional compliance.

## Table of Contents

- [Quick Diagnostic](#quick-diagnostic)
- [Python 3.13 Not Found](#python-313-not-found)
- [UV Configuration Violations](#uv-configuration-violations)
- [Virtual Environment Conflicts](#virtual-environment-conflicts)
- [MCP Server Python Issues](#mcp-server-python-issues)
- [Performance Issues](#performance-issues)
- [Distribution-Specific Guides](#distribution-specific-guides)

## Quick Diagnostic

Run this command to check your Python environment status:

```bash
# Check system Python version
python3.13 --version

# Verify UV configuration
cat uv.toml

# Check mcp-manager Python detection
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli validate
```

## Python 3.13 Not Found

### Symptom

```
PythonEnvironmentError: System Python 3.13 not found.
Constitutional requirement: mcp-manager requires Python 3.13 system installation.
```

### Root Cause

mcp-manager requires **system Python 3.13** - not virtual environments, not pyenv-managed versions, not conda environments. Only a system-wide Python 3.13 installation.

### Solution by Distribution

#### Ubuntu 24.04 / Debian

```bash
# Add deadsnakes PPA for Python 3.13
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.13
sudo apt install python3.13 python3.13-dev python3.13-venv

# Verify installation
python3.13 --version  # Should show: Python 3.13.x

# Verify system location
which python3.13      # Should show: /usr/bin/python3.13
```

#### macOS (Homebrew)

```bash
# Install Python 3.13
brew install python@3.13

# Link to system
brew link python@3.13

# Verify installation
python3.13 --version  # Should show: Python 3.13.x

# Verify system location
which python3.13      # Should show: /opt/homebrew/bin/python3.13
```

#### Arch Linux

```bash
# Install Python 3.13
sudo pacman -S python

# Verify installation
python3.13 --version
```

#### Fedora / RHEL

```bash
# Install Python 3.13
sudo dnf install python3.13

# Verify installation
python3.13 --version
```

### Verification

After installation, verify mcp-manager can detect Python 3.13:

```bash
cd /home/kkk/Apps/002-mcp-manager
PYTHONPATH=backend/src uv run python3 -c "
from mcp_manager.python_env import find_system_python, is_python_313, get_installation_source
python_path = find_system_python()
print(f'Found: {python_path}')
print(f'Is 3.13: {is_python_313(python_path)}')
print(f'Source: {get_installation_source(python_path)}')
"
```

Expected output:
```
Found: /usr/bin/python3.13
Is 3.13: True
Source: apt
```

## UV Configuration Violations

### Symptom

```
PythonEnvironmentError: UV configuration violation: python-downloads=auto.
Constitutional requirement: Must be 'manual' or 'never' to prevent Python downloads.
```

### Root Cause

The project's `uv.toml` enforces constitutional requirements:
- `python-downloads = "never"` - UV must never download Python interpreters
- `python-preference = "only-system"` - UV must only use system Python

### Solution

1. **Check current UV configuration:**

```bash
# Check project uv.toml
cat uv.toml

# Expected content:
[tool.uv]
python-downloads = "never"
python-preference = "only-system"

[tool.uv.pip]
system-site-packages = true
```

2. **Fix global UV configuration (if needed):**

```bash
# Check for conflicting global UV config
cat ~/.config/uv/uv.toml

# If it exists and conflicts, rename it:
mv ~/.config/uv/uv.toml ~/.config/uv/uv.toml.backup

# UV will now use the project uv.toml
```

3. **Verify UV respects project configuration:**

```bash
# This should use system Python 3.13 without downloading
uv run python3 --version
```

### Constitutional Compliance Check

```bash
# Run the UV config validator
PYTHONPATH=backend/src uv run python3 -c "
from mcp_manager.uv_config import validate_uv_config
from pathlib import Path
config = validate_uv_config(Path.cwd())
print(f'Python downloads: {config.get(\"python_downloads\")}')  # Should be: never
print(f'Python preference: {config.get(\"python_preference\")}')  # Should be: only-system
"
```

## Virtual Environment Conflicts

### Symptom

```
PythonEnvironmentError: Found Python at /home/user/.venv/bin/python3.13 but it is not version 3.13.x
```

### Root Cause

mcp-manager detects virtual environment Python instead of system Python. Constitutional requirement: **system Python only**.

### Solution

1. **Deactivate all virtual environments:**

```bash
# If you're in a virtual environment
deactivate

# Verify no virtual env is active
echo $VIRTUAL_ENV  # Should be empty
```

2. **Check Python detection source:**

```bash
PYTHONPATH=backend/src uv run python3 -c "
from mcp_manager.python_env import find_system_python, get_installation_source
python_path = find_system_python()
source = get_installation_source(python_path)
print(f'Path: {python_path}')
print(f'Source: {source}')  # Should be: apt, brew, pacman (NOT venv, conda, pyenv)
"
```

3. **If virtual environment persists:**

```bash
# Remove conflicting virtual environment
rm -rf .venv

# Create fresh UV-managed environment (uses system Python)
uv venv .venv
source .venv/bin/activate

# Install mcp-manager
uv pip install -e .
```

## MCP Server Python Issues

### Symptom

MCP servers fail to launch with Python-related errors:

```
Error: MCP server 'test-server' failed to start
ModuleNotFoundError: No module named 'test_module'
```

### Root Cause

MCP servers configured with direct Python commands instead of UV-managed execution.

### Solution

1. **Check MCP server configuration:**

```bash
# View current MCP servers
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli mcp list

# Check specific server config
cat ~/.claude.json | grep -A 10 "test-server"
```

2. **Fix Python-based MCP server:**

```bash
# Remove misconfigured server
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli mcp remove test-server

# Re-add with UV-managed execution
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli mcp add test-server \
  --type stdio \
  --command python \
  --arg "-m" \
  --arg "test_module"
```

MCPManager will automatically transform this to:
```json
{
  "command": "uv",
  "args": ["run", "/usr/bin/python3.13", "-m", "test_module"]
}
```

3. **Verify MCP server uses system Python:**

```bash
# Check MCP server health
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli mcp health test-server

# View audit log to see Python path used
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli audit
```

## Performance Issues

### Symptom

Slow Python detection or validation commands taking >2 seconds.

### Constitutional Requirement

- Python detection: <100ms (SC-003)
- Validation command: <2s (SC-003)

### Solution

1. **Profile Python detection:**

```bash
PYTHONPATH=backend/src uv run python3 -c "
import time
from mcp_manager.python_env import find_system_python

start = time.time()
python_path = find_system_python()
duration = (time.time() - start) * 1000
print(f'Python detection: {duration:.2f}ms')
print(f'Requirement: <100ms')
print(f'Status: {\"✅ PASS\" if duration < 100 else \"❌ FAIL\"}')"
```

2. **Profile validation command:**

```bash
time PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli validate
# Should complete in <2 seconds
```

3. **Common Performance Issues:**

**Issue**: Slow `find_system_python()` due to many Python installations

**Solution**: The function checks common locations first for fast detection:
```python
# Priority order (fastest to slowest):
1. /usr/bin/python3.13      # System package managers (apt, dnf, pacman)
2. /opt/homebrew/bin/...    # macOS Homebrew
3. /usr/local/bin/...       # Manual installations
4. which python3.13         # PATH search (slowest fallback)
```

**Issue**: Slow UV configuration validation

**Solution**: UV config is cached after first read. Ensure `uv.toml` exists at project root.

## Distribution-Specific Guides

### Ubuntu 24.04 LTS (Recommended)

```bash
# Complete setup
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-dev python3.13-venv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
python3.13 --version
uv --version

# Setup mcp-manager
git clone https://github.com/kairin/mcp-manager.git ~/Apps/mcp-manager
cd ~/Apps/mcp-manager
uv venv .venv
source .venv/bin/activate
uv pip install -e .
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli validate
```

### macOS (Homebrew)

```bash
# Complete setup
brew install python@3.13
brew link python@3.13
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
python3.13 --version
uv --version

# Setup mcp-manager
git clone https://github.com/kairin/mcp-manager.git ~/Apps/mcp-manager
cd ~/Apps/mcp-manager
uv venv .venv
source .venv/bin/activate
uv pip install -e .
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli validate
```

### Arch Linux

```bash
# Complete setup
sudo pacman -S python
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
python3.13 --version
uv --version

# Setup mcp-manager
git clone https://github.com/kairin/mcp-manager.git ~/Apps/mcp-manager
cd ~/Apps/mcp-manager
uv venv .venv
source .venv/bin/activate
uv pip install -e .
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli validate
```

## Common Error Messages

### Error: "python: No such file or directory"

**Cause**: Python 3.13 not installed or not in PATH

**Solution**: Follow [Python 3.13 Not Found](#python-313-not-found) for your distribution

### Error: "uv: command not found"

**Cause**: UV not installed or not in PATH

**Solution**:
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (if needed)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Error: "UV downloaded Python 3.13"

**Cause**: UV configuration allows Python downloads (constitutional violation)

**Solution**: Check `uv.toml` has `python-downloads = "never"` (see [UV Configuration Violations](#uv-configuration-violations))

### Error: "Python 3.13 found but wrong source"

**Cause**: Python from pyenv/conda instead of system package manager

**Solution**:
```bash
# Uninstall pyenv/conda Python
pyenv uninstall 3.13.0  # or
conda env remove -n py313

# Install system Python (see distribution-specific guides above)
```

## Advanced Debugging

### Enable Verbose Logging

```bash
# Set logging level to DEBUG
export LOG_LEVEL=DEBUG

# Run command with detailed logging
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli validate
```

### Inspect Python Environment

```bash
# Complete Python environment diagnostic
PYTHONPATH=backend/src uv run python3 -c "
import sys
import json
from pathlib import Path
from mcp_manager.python_env import find_system_python, is_python_313, get_installation_source

print('=== System Python Info ===')
print(f'Executable: {sys.executable}')
print(f'Version: {sys.version}')
print(f'Prefix: {sys.prefix}')

print('\n=== Detected System Python ===')
python_path = find_system_python()
print(f'Path: {python_path}')
print(f'Is 3.13: {is_python_313(python_path)}')
print(f'Source: {get_installation_source(python_path)}')

print('\n=== UV Configuration ===')
from mcp_manager.uv_config import validate_uv_config
config = validate_uv_config(Path.cwd())
print(json.dumps(config, indent=2))
"
```

### Test MCP Server Launcher

```bash
# Test Python-based MCP server launcher
PYTHONPATH=backend/src uv run python3 -c "
from mcp_manager.core import MCPManager

manager = MCPManager()
system_python = manager.get_system_python_path()
print(f'MCPManager will use: {system_python}')

# Verify it's system Python 3.13
from mcp_manager.python_env import is_python_313, get_installation_source
print(f'Is Python 3.13: {is_python_313(system_python)}')
print(f'Installation source: {get_installation_source(system_python)}')
"
```

## Getting Help

If you encounter issues not covered in this guide:

1. **Check constitutional requirements**: Review `.specify/memory/constitution.md`
2. **Run comprehensive audit**: `PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli audit`
3. **Check logs**: `~/.mcp-manager/logs/`
4. **Open GitHub issue**: https://github.com/kairin/mcp-manager/issues

Include this diagnostic information:
```bash
# Collect diagnostic information
echo "=== System Info ==="
uname -a
python3.13 --version
uv --version

echo "\n=== Python Detection ==="
PYTHONPATH=backend/src uv run python3 -c "
from mcp_manager.python_env import find_system_python, get_installation_source
python_path = find_system_python()
print(f'Path: {python_path}')
print(f'Source: {get_installation_source(python_path)}')
"

echo "\n=== UV Config ==="
cat uv.toml

echo "\n=== Validation ==="
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli validate
```
