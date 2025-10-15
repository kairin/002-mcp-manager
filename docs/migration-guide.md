# UV Configuration Migration Guide

> 🔄 **Migration to Constitutional Python 3.13 Enforcement**
>
> This guide helps existing mcp-manager users migrate to the new constitutional UV configuration requirements introduced in Feature 002: System Python 3.13 Enforcement.

## Table of Contents

- [Who Needs to Migrate?](#who-needs-to-migrate)
- [What Changed?](#what-changed)
- [Before You Start](#before-you-start)
- [Automatic Migration](#automatic-migration)
- [Manual Migration](#manual-migration)
- [Verifying Migration](#verifying-migration)
- [Troubleshooting](#troubleshooting)
- [Rollback Procedure](#rollback-procedure)

## Who Needs to Migrate?

You need to migrate if you meet ANY of these criteria:

✅ **You have legacy `.uv/config` files** in your project
✅ **Your `uv.toml` lacks constitutional requirements** (`python-downloads`, `python-preference`)
✅ **You have global UV config** at `~/.config/uv/uv.toml` that conflicts with project requirements
✅ **You're upgrading** from mcp-manager versions before Feature 002

You do NOT need to migrate if:

❌ You're setting up mcp-manager for the first time
❌ Your project already has compliant `uv.toml`
❌ You don't use UV package manager

## What Changed?

### Old Approach (Pre-Feature 002)

```bash
# Multiple configuration locations
.uv/config                  # Legacy UV config
~/.config/uv/uv.toml       # Global UV config (may conflict)
pyproject.toml             # Mixed Python config

# No Python enforcement
python-downloads = "automatic"  # ❌ UV could download Pythons
python-preference = "managed"    # ❌ UV used managed Pythons
```

### New Approach (Feature 002: Constitutional Requirements)

```toml
# Single source of truth: uv.toml
# Location: <project-root>/uv.toml

[tool.uv]
# Constitutional requirement: Never download Python interpreters
python-downloads = "never"

# Constitutional requirement: Only use system Python 3.13
python-preference = "only-system"

[tool.uv.pip]
# Use system site packages for MCP server integration
system-site-packages = true
```

**Key Differences**:

| Setting | Old | New (Constitutional) |
|---------|-----|---------------------|
| **Python Source** | UV downloads | System Python 3.13 only |
| **Config Location** | `.uv/config`, global | `uv.toml` (project-local) |
| **Python Downloads** | Allowed | **Forbidden** |
| **Version Enforcement** | None | Python 3.13 **mandatory** |
| **MCP Server Python** | Varies | System Python 3.13 |

## Before You Start

### Prerequisites

1. **System Python 3.13 installed** (see [Python Troubleshooting Guide](PYTHON-TROUBLESHOOTING.md#python-313-not-found))
2. **UV package manager** installed (`uv --version` works)
3. **Backup current configuration** (migration creates backups automatically, but better safe)

### Quick Pre-Migration Check

```bash
# Check current UV configuration status
PYTHONPATH=backend/src uv run python3 -c "
from mcp_manager.uv_config import check_global_uv_conflicts, get_uv_config_path
from pathlib import Path

# Check for legacy config
project_root = Path.cwd()
legacy_config = project_root / '.uv' / 'config'
if legacy_config.exists():
    print('⚠️  Legacy .uv/config found - migration needed')

# Check for global conflicts
conflicts = check_global_uv_conflicts(project_root)
if conflicts['has_conflicts']:
    print('⚠️  Global UV config conflicts detected')
    print(conflicts['resolution'])

# Check current project config
config_path = get_uv_config_path(project_root)
if config_path:
    print(f'✅ Current config: {config_path}')
else:
    print('⚠️  No UV config found - will create uv.toml')
"
```

## Automatic Migration

The recommended migration approach using the built-in migration utility.

### Step 1: Run Migration Utility

```bash
# From mcp-manager project root
PYTHONPATH=backend/src uv run python3 -c "
from mcp_manager.uv_config import migrate_legacy_uv_config
from pathlib import Path

result = migrate_legacy_uv_config(Path.cwd(), create_backup=True)

print(f'Status: {result[\"status\"]}')
print(f'Message: {result[\"message\"]}')

if result['backup_path']:
    print(f'Backup created: {result[\"backup_path\"]}')

if result['migrated_from']:
    print(f'Migrated from: {result[\"migrated_from\"]}')

print(f'Configuration: {result[\"migrated_to\"]}')
"
```

### Step 2: Check for Global Conflicts

```bash
# Identify and resolve global UV config conflicts
PYTHONPATH=backend/src uv run python3 -c "
from mcp_manager.uv_config import check_global_uv_conflicts
from pathlib import Path

conflicts = check_global_uv_conflicts(Path.cwd())

if conflicts['has_conflicts']:
    print('⚠️  CONFLICTS DETECTED')
    for conflict in conflicts['conflicts']:
        print(f'  - {conflict}')
    print()
    print('Resolution:')
    print(conflicts['resolution'])
else:
    print('✅ No global config conflicts')
"
```

### Step 3: Resolve Global Conflicts (If Needed)

If conflicts detected in Step 2:

```bash
# Backup global UV config
mv ~/.config/uv/uv.toml ~/.config/uv/uv.toml.backup

# UV will now use project uv.toml exclusively
```

### Step 4: Verify Migration

```bash
# Verify UV uses system Python 3.13
uv python find  # Should show: /usr/bin/python3.13 or /opt/homebrew/bin/python3.13

# Verify mcp-manager validates successfully
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli status --python

# Should show:
# Python Environment (Constitutional Requirements)
# ┌─────────────────────┬───────────────────────────┬────────────────┐
# │ Component           │ Value                     │ Status         │
# ├─────────────────────┼───────────────────────────┼────────────────┤
# │ Python Version      │ 3.13.x                    │ ✅ Valid       │
# │ Python Path         │ /usr/bin/python3.13       │ ✅ Package Mgr │
# │ UV Python Downloads │ never                     │ ✅ Valid       │
# │ UV Python Preference│ only-system               │ ✅ Valid       │
# └─────────────────────┴───────────────────────────┴────────────────┘
```

## Manual Migration

For advanced users who prefer manual migration or troubleshooting.

### Step 1: Create Backup

```bash
# Backup legacy config (if exists)
if [ -f .uv/config ]; then
    cp .uv/config .uv/config.backup
    echo "✅ Backed up .uv/config"
fi

# Backup global config (if exists)
if [ -f ~/.config/uv/uv.toml ]; then
    cp ~/.config/uv/uv.toml ~/.config/uv/uv.toml.backup
    echo "✅ Backed up global UV config"
fi
```

### Step 2: Create uv.toml

```bash
# Create uv.toml with constitutional requirements
cat > uv.toml << 'EOF'
# UV Configuration - Constitutional Requirements
# Feature 002: System Python 3.13 Enforcement

[tool.uv]
# Constitutional requirement: Never download Python interpreters
python-downloads = "never"

# Constitutional requirement: Only use system Python
python-preference = "only-system"

[tool.uv.pip]
# Use system site packages for integration
system-site-packages = true
EOF

echo "✅ Created uv.toml"
```

### Step 3: Remove Conflicting Configs

```bash
# Remove or rename global UV config
if [ -f ~/.config/uv/uv.toml ]; then
    mv ~/.config/uv/uv.toml ~/.config/uv/uv.toml.disabled
    echo "✅ Disabled global UV config"
fi

# Optionally remove legacy .uv/config (backup exists)
# rm .uv/config
```

### Step 4: Verify Configuration

```bash
# Check UV configuration
cat uv.toml

# Verify UV respects configuration
uv python find  # Should use system Python 3.13
```

## Verifying Migration

### Verification Checklist

Run these checks to ensure migration succeeded:

#### 1. UV Configuration Check

```bash
# Verify uv.toml exists and is valid
cat uv.toml | grep -E "python-downloads|python-preference"

# Expected output:
# python-downloads = "never"
# python-preference = "only-system"
```

#### 2. Python Detection Check

```bash
# Verify UV finds system Python 3.13
uv python find

# Expected output:
# /usr/bin/python3.13  (Ubuntu/Debian)
# /opt/homebrew/bin/python3.13  (macOS Apple Silicon)
# /usr/local/bin/python3.13  (macOS Intel)
```

#### 3. MCPManager Validation Check

```bash
# Verify mcp-manager initialization works
PYTHONPATH=backend/src uv run python3 -c "
from mcp_manager.core import MCPManager

manager = MCPManager()
python_path = manager.get_system_python_path()
print(f'✅ MCPManager using: {python_path}')
"

# Expected output:
# ✅ MCPManager using: /usr/bin/python3.13
```

#### 4. MCP Server Configuration Check

```bash
# Verify MCP servers will use system Python
cat ~/.claude.json | python3 -m json.tool | grep -A 5 '"command"'

# Python-based servers should show:
# "command": "uv",
# "args": ["run", "/usr/bin/python3.13", "-m", "module_name"]
```

#### 5. Full Status Check

```bash
# Comprehensive environment status
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli status --python

# All checks should show ✅ Valid
```

## Troubleshooting

### Migration Failed: "System Python 3.13 not found"

**Problem**: Migration utility cannot find Python 3.13

**Solution**: Install Python 3.13 first (see [Python Troubleshooting Guide](PYTHON-TROUBLESHOOTING.md#python-313-not-found))

```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13

# macOS
brew install python@3.13

# Then retry migration
```

### UV Still Downloading Python

**Problem**: UV downloads Python despite `python-downloads = "never"`

**Solution**: Global UV config is overriding project config

```bash
# Check for global config
cat ~/.config/uv/uv.toml

# If it exists and conflicts, rename it
mv ~/.config/uv/uv.toml ~/.config/uv/uv.toml.disabled

# Verify UV now respects project config
uv python find  # Should use system Python
```

### MCP Servers Failing After Migration

**Problem**: MCP servers fail to start after migration

**Solution**: Re-add MCP servers to regenerate configurations with UV-managed execution

```bash
# Remove misconfigured server
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli mcp remove server-name

# Re-add with correct configuration
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli mcp add server-name \
  --type stdio \
  --command python \
  --arg "-m" \
  --arg "module_name"

# MCPManager will automatically configure UV-managed execution
```

### pyproject.toml vs uv.toml Confusion

**Problem**: Not sure whether to use `pyproject.toml` or `uv.toml`

**Solution**: Use `uv.toml` for clarity and constitutional compliance

| File | Purpose | Recommended |
|------|---------|-------------|
| `uv.toml` | UV-specific config | ✅ **Use this** |
| `pyproject.toml` | Python project metadata | ⚠️ Can include `[tool.uv]` but not recommended |

**Why `uv.toml`?**
- Clear separation of concerns
- No risk of conflicting with other Python tools
- Easier to audit for constitutional compliance
- Explicit UV configuration location

## Rollback Procedure

If migration causes issues, you can rollback to previous configuration.

### Rollback to Legacy Config

```bash
# 1. Restore legacy .uv/config (if backup exists)
if [ -f .uv/config.backup ]; then
    cp .uv/config.backup .uv/config
    echo "✅ Restored .uv/config"
fi

# 2. Remove uv.toml
rm uv.toml

# 3. Restore global UV config (if backup exists)
if [ -f ~/.config/uv/uv.toml.backup ]; then
    cp ~/.config/uv/uv.toml.backup ~/.config/uv/uv.toml
    echo "✅ Restored global UV config"
fi

# 4. Verify rollback
uv python find
```

### Rollback to Pre-Migration State

```bash
# Complete rollback script
#!/bin/bash
set -e

echo "Rolling back UV configuration migration..."

# Restore legacy config
if [ -f .uv/config.backup ]; then
    cp .uv/config.backup .uv/config
    echo "✅ Restored .uv/config"
fi

# Remove new uv.toml
if [ -f uv.toml ]; then
    mv uv.toml uv.toml.rollback
    echo "✅ Removed uv.toml (saved as uv.toml.rollback)"
fi

# Restore global config
if [ -f ~/.config/uv/uv.toml.backup ]; then
    cp ~/.config/uv/uv.toml.backup ~/.config/uv/uv.toml
    echo "✅ Restored global UV config"
elif [ -f ~/.config/uv/uv.toml.disabled ]; then
    mv ~/.config/uv/uv.toml.disabled ~/.config/uv/uv.toml
    echo "✅ Re-enabled global UV config"
fi

echo ""
echo "Rollback complete. Verify UV configuration:"
echo "  uv python find"
```

## Post-Migration Best Practices

After successful migration:

### 1. Update Documentation

If you have project-specific setup docs, update them to reference `uv.toml` instead of `.uv/config`.

### 2. Update CI/CD Pipelines

If you have automated workflows, ensure they:
- Install Python 3.13 explicitly
- Don't attempt to install UV-managed Pythons
- Respect `uv.toml` configuration

### 3. Team Communication

Notify team members about:
- New constitutional requirements
- Migration procedure (link to this guide)
- Troubleshooting resources (link to [Python Troubleshooting Guide](PYTHON-TROUBLESHOOTING.md))

### 4. Monitor MCP Server Health

```bash
# Regular health checks after migration
PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli mcp health --all

# Verify all servers use system Python 3.13
cat ~/.claude.json | grep -A 3 '"command"'
```

## Additional Resources

- **[Python Troubleshooting Guide](PYTHON-TROUBLESHOOTING.md)** - Comprehensive Python 3.13 setup and troubleshooting
- **[README.md](../README.md#prerequisites)** - System requirements and UV configuration
- **[Constitutional Requirements](.specify/memory/constitution.md)** - Project governance and principles
- **[Feature 002 Specification](../specs/002-system-python-enforcement/spec.md)** - Technical specification for System Python 3.13 Enforcement

## Getting Help

If you encounter migration issues not covered in this guide:

1. **Check diagnostics**: `PYTHONPATH=backend/src uv run python3 -m mcp_manager.cli status --python`
2. **Review troubleshooting**: [Python Troubleshooting Guide](PYTHON-TROUBLESHOOTING.md)
3. **Open GitHub issue**: https://github.com/kairin/mcp-manager/issues
4. **Include diagnostic output** from the verification checks above

---

**Migration Guide Version**: 1.0
**Feature**: 002 - System Python 3.13 Enforcement
**Last Updated**: 2025-10-16
**Status**: ACTIVE
