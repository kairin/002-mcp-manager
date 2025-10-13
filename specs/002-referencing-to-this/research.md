# Research: MCP Manager Three-Phase Improvements

**Date**: 2025-10-13
**Feature**: MCP Manager Improvements - Core functionality, code quality, and polish
**Source**: improvement_plan.md analysis + technical investigation

---

## 1. MCP Server Update Mechanisms

**Decision**: Use `npm view <package> version` for npm-based servers, skip HTTP servers

**Rationale**:
- npm provides clean JSON output parseable via subprocess
- HTTP MCP servers (like context7) don't expose version endpoints
- Aligns with UV-first philosophy (subprocess-based tool execution)
- Low overhead, no external dependencies required

**Implementation Pattern**:
```python
import subprocess
import json

def check_npm_package_version(package: str) -> Optional[str]:
    """Check latest npm package version"""
    try:
        result = subprocess.run(
            ['npm', 'view', package, 'version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except subprocess.TimeoutExpired:
        return None
```

**Version Comparison**:
- Use Python's `packaging.version` (already available in Python 3.11+)
- Parse semver: `Version("1.2.3") < Version("1.3.0")`
- Categorize updates: major (breaking), minor (features), patch (fixes)

**Alternatives Considered**:
- ❌ **npm-check-updates**: Too heavy, requires npm global install
- ❌ **Package.json parsing**: Unreliable, packages may not follow semver strictly
- ❌ **GitHub API**: Rate-limited, requires authentication, overkill for version checks

**Configuration Updates**:
- Update only the `args` array for stdio servers (version pinning)
- Example: `["shadcn@1.2.3", "mcp"]` → `["shadcn@1.3.0", "mcp"]`
- Preserve all other configuration fields (command, headers, env)

**Dry-Run Mode**:
- Check version without modifying configuration
- Display: current_version, latest_version, update_type (major/minor/patch)
- User confirmation for major updates (breaking changes)

---

## 2. Gemini CLI Configuration Structure

**Decision**: Mirror Claude Code's `~/.claude.json` structure in `~/.config/gemini/settings.json`

**Rationale**:
- Gemini CLI documentation confirms identical `mcpServers` schema
- Both use MCP protocol standard (no translation needed)
- Simplifies synchronization logic (direct JSON copy with merge)
- Users get consistent experience across AI platforms

**Gemini CLI Settings Structure**:
```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "..."
      }
    },
    "shadcn": {
      "type": "stdio",
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

**Environment Variable**:
- `GEMINI_CLI_SYSTEM_SETTINGS_PATH="$HOME/.config/gemini/settings.json"`
- Must be set in user's shell profile for global discovery
- Gemini CLI reads this at startup to locate system-wide configuration

**Shell Profile Detection** (in priority order):
1. `~/.bashrc` (Bash - most common on Ubuntu)
2. `~/.zshrc` (Zsh - alternative shell)
3. `~/.profile` (POSIX-compliant fallback)

**Profile Update Pattern**:
```bash
# Check if already present to avoid duplicates
if ! grep -q "GEMINI_CLI_SYSTEM_SETTINGS_PATH" ~/.bashrc; then
  echo 'export GEMINI_CLI_SYSTEM_SETTINGS_PATH="$HOME/.config/gemini/settings.json"' >> ~/.bashrc
fi
```

**Merge Strategy**:
- Read existing Gemini settings.json if present
- Merge mcpServers from Claude Code configuration
- Overwrite servers with duplicate names (Claude Code is source of truth)
- Preserve non-mcpServers Gemini settings (if any exist)

**Directory Creation**:
- `~/.config/gemini/` may not exist initially
- Use `Path.mkdir(parents=True, exist_ok=True)`
- Set appropriate permissions: 0755 for directory, 0644 for settings.json

**Error Handling**:
- ConfigurationError: ~/.claude.json missing or invalid JSON
- FileSystemError: Cannot create ~/.config/gemini/ (permissions)
- ShellProfileError: Cannot modify shell profile (read-only filesystem)

---

## 3. Error Handling Patterns

**Decision**: Create centralized decorator for MCPManagerError handling in CLI commands

**Rationale**:
- Eliminates ~30+ repetitive try/except blocks in cli.py (lines 71-320)
- Consistent error messages and exit codes across all commands
- Simplifies command implementation (focus on logic, not error handling)
- Leverages Rich for beautiful error displays

**Decorator Pattern**:
```python
from functools import wraps
from rich import print as rprint
import typer

def handle_mcp_errors(func):
    """Centralized error handling for CLI commands"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MCPManagerError as e:
            rprint(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            rprint(f"[red]Unexpected error: {e}[/red]")
            raise typer.Exit(1)
    return wrapper
```

**Usage in CLI Commands**:
```python
@mcp_app.command("audit")
@handle_mcp_errors
def mcp_audit(detailed: bool = False):
    """Audit all MCP server configurations"""
    manager = MCPManager()
    results = manager.audit_configurations(detailed=detailed)
    _display_audit_table(results)
    # No try/except needed - decorator handles errors
```

**Exception Hierarchy Requirements**:
- Base: `MCPManagerError` (catch-all for domain errors)
- Specific: `ServerNotFoundError`, `ConfigurationError`, `ConnectivityError`
- All inherit from `MCPManagerError` for consistent handling

**Rich Error Display**:
- Red color for errors (`[red]Error: {message}[/red]`)
- Yellow for warnings (`[yellow]Warning: {message}[/yellow]`)
- Include helpful suggestions when possible
- Example: "Server 'foo' not found. Run 'mcp-manager mcp audit' to see available servers."

**Typer Integration**:
- Decorator works with Typer command decorators
- Always raise `typer.Exit(1)` for error state (non-zero exit code)
- Preserve function signatures for help text generation

**Backward Compatibility**:
- Existing error handling in core.py remains unchanged
- Only CLI layer uses decorator (separation of concerns)
- Tests can still catch specific exception types

---

## 4. Configuration Path Management

**Decision**: Support both CLI flags (`--search-dir`) and configuration file (`.mcp-manager.json`)

**Rationale**:
- CLI flags: Flexibility for one-off audits
- Configuration file: Persistent customization for non-standard setups
- Backward compatibility: Default to hardcoded paths if no config provided
- XDG-compliant: Store config in `~/.config/mcp-manager/config.json`

**Configuration File Structure**:
```json
{
  "audit": {
    "search_directories": [
      "/home/user/custom-projects",
      "/mnt/shared/work-projects"
    ]
  }
}
```

**Path Validation**:
```python
from pathlib import Path

def validate_search_paths(paths: List[str]) -> List[Path]:
    """Validate and convert path strings to Path objects"""
    validated = []
    for path_str in paths:
        path = Path(path_str).expanduser().resolve()
        if not path.exists():
            raise InvalidPathError(f"Path does not exist: {path}")
        if not path.is_dir():
            raise InvalidPathError(f"Path is not a directory: {path}")
        validated.append(path)
    return validated
```

**Priority Order**:
1. CLI flags (`--search-dir`) - highest priority
2. Configuration file (`~/.config/mcp-manager/config.json`)
3. Default paths (`~/Apps`, `~/projects`, `~/repos`) - lowest priority

**Backward Compatibility**:
- If no CLI flags or config file → use defaults
- Existing users experience no breaking changes
- New users can customize without code changes

**CLI Flag Design**:
```python
@project_app.command("audit")
def project_audit(
    search_dir: List[str] = typer.Option(
        None, "--search-dir", help="Custom directory to scan (can be used multiple times)"
    )
):
    # Use search_dir if provided, else fall back to config/defaults
```

**XDG Base Directory Compliance**:
- Config: `~/.config/mcp-manager/config.json`
- Cache: `~/.cache/mcp-manager/` (future use)
- Data: `~/.local/share/mcp-manager/` (future use)

---

## 5. Dynamic Version Management

**Decision**: Inject version from `pyproject.toml` into Astro build via environment variable

**Rationale**:
- Single source of truth: pyproject.toml (Python package metadata)
- Astro supports import.meta.env for environment variables
- Build-time injection prevents manual updates
- Works with existing build process (npm run build)

**Astro Environment Variable Injection**:
```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import fs from 'fs';
import toml from '@iarna/toml';

// Read version from pyproject.toml
const pyproject = toml.parse(fs.readFileSync('pyproject.toml', 'utf8'));
const version = pyproject.project.version;

export default defineConfig({
  site: 'https://kairin.github.io',
  base: '/mcp-manager',
  outDir: './docs',
  vite: {
    define: {
      'import.meta.env.PROJECT_VERSION': JSON.stringify(version)
    }
  }
});
```

**Component Usage**:
```astro
<!-- src/pages/index.astro -->
---
const version = import.meta.env.PROJECT_VERSION;
---
<p>MCP Manager v{version}</p>
```

**TOML Parsing**:
- Install: `@iarna/toml` npm package
- Native JavaScript, no Python required at build time
- Handles TOML spec fully (arrays, tables, multiline strings)

**Package.json Update**:
```json
{
  "scripts": {
    "prebuild": "npm run clean-docs",
    "build": "astro check && astro build",
    "postbuild": "cp public/favicon.* docs/ || true"
  },
  "devDependencies": {
    "@iarna/toml": "^2.2.5"
  }
}
```

**Synchronization Points**:
- `pyproject.toml` version → Astro site version
- Features.astro MCP server count (5 → 6)
- Python requirement in README (3.13 → >=3.11)

**Alternatives Considered**:
- ❌ **Duplicate in package.json**: Violates DRY, causes drift
- ❌ **Python script preprocessing**: Adds complexity, non-standard
- ❌ **Manual updates**: Error-prone, already causing inconsistencies

---

## 6. CLI Modularization

**Decision**: Split cli.py (1552 lines) into command group modules using Typer sub-applications

**Rationale**:
- Maintainability: <400 lines per module target
- Navigability: Developers find commands by logical grouping
- Typer native support: `app.add_typer(sub_app, name="group")`
- No breaking changes: Command structure remains identical

**Module Structure**:
```
src/mcp_manager/
├── cli.py (main app, ~100 lines)
└── commands/
    ├── __init__.py
    ├── mcp.py (~300 lines - MCP server management)
    ├── project.py (~200 lines - project standardization)
    ├── fleet.py (~200 lines - fleet management)
    ├── agent.py (~200 lines - agent management)
    └── office.py (~250 lines - office deployment)
```

**Main CLI File** (cli.py):
```python
import typer
from .commands import mcp, project, fleet, agent, office

app = typer.Typer(
    name="mcp-manager",
    help="MCP Manager - Comprehensive Project Standardization System"
)

# Register subcommands
app.add_typer(mcp.app, name="mcp")
app.add_typer(project.app, name="project")
app.add_typer(fleet.app, name="fleet")
app.add_typer(agent.app, name="agent")
app.add_typer(office.app, name="office")

def main():
    app()
```

**Subcommand Module** (commands/mcp.py):
```python
import typer

app = typer.Typer(help="MCP Server Management")

@app.command("audit")
def audit(detailed: bool = False):
    """Audit all MCP server configurations"""
    # Implementation
```

**Import Restructuring**:
- Each command module imports only what it needs
- Shared utilities stay in existing files (core.py, models.py, utils.py)
- No circular dependencies (commands import core, not vice versa)

**Logical Command Groupings**:
- **mcp**: audit, init, add, remove, status, update, diagnose, migrate, setup-hf, setup-all
- **project**: audit, fix, standards
- **fleet**: register, status, sync, audit
- **agent**: discover, deploy, deploy-department, install-global, audit
- **office**: register, list, remove, status, check, deploy, verify, pull, info

**Migration Strategy**:
1. Create commands/ directory and __init__.py
2. Extract one command group at a time (start with simplest: office)
3. Test after each extraction
4. Update imports incrementally
5. Keep cli.py as thin orchestrator

**File Size Targets**:
- Main cli.py: <150 lines (orchestration only)
- Each command module: <400 lines (maintain readability)
- Total: Same functionality, better organization

**Typer Sub-Application Benefits**:
- Help text remains hierarchical: `mcp-manager mcp --help`
- Tab completion works identically
- Error handling via decorators applies to all subcommands
- No performance overhead (same Python import mechanism)

---

## Summary

All research areas complete with concrete implementation decisions:

1. ✅ **MCP Server Updates**: npm view subprocess, semver comparison, dry-run support
2. ✅ **Gemini CLI Integration**: Mirror Claude Code structure, environment variable injection, merge strategy
3. ✅ **Error Handling**: Decorator pattern, Rich display, exception hierarchy
4. ✅ **Configurable Paths**: CLI flags + config file, XDG compliance, backward compatible
5. ✅ **Dynamic Versioning**: Astro environment variables, TOML parsing, single source of truth
6. ✅ **CLI Modularization**: Typer sub-applications, <400 lines per module, logical grouping

**No NEEDS CLARIFICATION remaining** - Ready for Phase 1 (Design & Contracts)

**Constitutional Compliance**: All decisions align with:
- UV-first development (subprocess patterns)
- Global configuration first (Gemini sync enhances)
- Zero downtime (backward compatibility)
- Security by design (no new credentials)
- Repository organization (proper file placement)
