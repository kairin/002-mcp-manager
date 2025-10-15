# Data Model: MCP Manager Improvements

**Date**: 2025-10-13
**Feature**: Three-Phase Enhancement Plan
**Based on**: spec.md Key Entities + research.md decisions

---

## Entity Definitions

### 1. GeminiCLISettings

**Purpose**: Represents Gemini CLI configuration structure for MCP server synchronization

**Fields**:
- `mcpServers`: Dict[str, MCPServerConfig] - MCP server definitions (identical to Claude Code format)
- `config_path`: Path - Location of settings.json file (~/.config/gemini/settings.json)
- `env_var_configured`: bool - Whether GEMINI_CLI_SYSTEM_SETTINGS_PATH is set in shell profile

**Validation Rules**:
- `mcpServers` must validate against MCPServerConfig schema (existing)
- `config_path` must be absolute path
- Each server in `mcpServers` must have required fields based on type:
  - HTTP: `type`, `url`
  - stdio: `type`, `command`, `args`

**Relationships**:
- **Shares structure with**: Claude Code configuration (~/.claude.json)
- **Contains**: MCPServerConfig instances (existing model)
- **Managed by**: GeminiCLIIntegration class (new)

**State Transitions**:
```
not_configured → syncing → synced
                   ↓
                 error
```

**Example**:
```python
{
    "mcpServers": {
        "context7": {
            "type": "http",
            "url": "https://mcp.context7.com/mcp",
            "headers": {"CONTEXT7_API_KEY": "..."}
        },
        "shadcn": {
            "type": "stdio",
            "command": "npx",
            "args": ["shadcn@latest", "mcp"]
        }
    },
    "config_path": Path("/home/user/.config/gemini/settings.json"),
    "env_var_configured": True
}
```

---

### 2. UpdateStatus

**Purpose**: Tracks MCP server update state and version information

**Fields**:
- `server_name`: str - MCP server identifier
- `current_version`: Optional[str] - Installed version (None for HTTP servers)
- `latest_version`: Optional[str] - Available version from registry
- `update_available`: bool - Whether update is available
- `update_type`: Literal["major", "minor", "patch", "none"] - Semantic version category
- `dry_run`: bool - Whether this is a simulation (default: False)
- `package_name`: Optional[str] - npm package name (for stdio servers)
- `check_timestamp`: datetime - When version check was performed

**Validation Rules**:
- `current_version` and `latest_version` must follow semver (X.Y.Z) if present
- `update_available` is True only if `latest_version > current_version`
- `update_type` determined by semver comparison:
  - major: Breaking changes (X changes)
  - minor: New features (Y changes)
  - patch: Bug fixes (Z changes)
  - none: No update available

**Relationships**:
- **One-to-one**: MCPServerConfig (existing) - each stdio server has update status
- **Zero for**: HTTP servers (no version tracking)
- **Used by**: MCPManager.update_server() and MCPManager.update_all_servers()

**State Transitions**:
```
none → checking → update_available → updating → updated
        ↓                             ↓
      error                         error
```

**Example**:
```python
UpdateStatus(
    server_name="shadcn",
    current_version="1.2.3",
    latest_version="1.3.0",
    update_available=True,
    update_type="minor",
    dry_run=False,
    package_name="shadcn",
    check_timestamp=datetime(2025, 10, 13, 14, 30)
)
```

---

### 3. AuditConfiguration

**Purpose**: Configurable project directory paths for audit operations

**Fields**:
- `search_directories`: List[Path] - User-specified directories to scan
- `default_directories`: List[Path] - Built-in default paths
- `use_defaults`: bool - Whether to include defaults if no custom paths provided
- `validate_paths`: bool - Whether to check path existence before scanning (default: True)

**Validation Rules**:
- All paths in `search_directories` must be absolute
- If `validate_paths` is True, all paths must exist and be directories
- `default_directories` is immutable: [~/Apps, ~/projects, ~/repos]
- If `search_directories` is empty and `use_defaults` is False → error

**Relationships**:
- **Composition**: MCPManager.audit_configurations() uses this
- **Configuration source**: CLI flags (--search-dir) or config file (~/.config/mcp-manager/config.json)

**Priority Order** (for path resolution):
1. CLI flags (highest priority)
2. Configuration file
3. Default directories (lowest priority)

**Example**:
```python
AuditConfiguration(
    search_directories=[
        Path("/home/user/custom-projects"),
        Path("/mnt/shared/work")
    ],
    default_directories=[
        Path.home() / "Apps",
        Path.home() / "projects",
        Path.home() / "repos"
    ],
    use_defaults=False,  # Only use custom paths
    validate_paths=True
)
```

---

### 4. VersionMetadata

**Purpose**: Project version information from pyproject.toml for consistency checks

**Fields**:
- `version`: str - Project version (e.g., "0.1.0")
- `python_requirement`: str - Required Python version (e.g., ">=3.11")
- `mcp_server_count`: int - Number of supported MCP servers (current: 6)
- `dependencies`: Dict[str, str] - Key dependencies and versions
- `source_file`: Path - Location of pyproject.toml

**Validation Rules**:
- `version` must follow semver (X.Y.Z)
- `python_requirement` must be valid Python version specifier
- `mcp_server_count` must be > 0
- `source_file` must exist and be a valid TOML file

**Relationships**:
- **Parsed from**: pyproject.toml (project root)
- **Used by**:
  - Version display in website (Astro build)
  - Documentation consistency checks
  - Feature count validation

**Example**:
```python
VersionMetadata(
    version="0.1.0",
    python_requirement=">=3.11",
    mcp_server_count=6,
    dependencies={
        "typer": ">=0.12.0",
        "rich": ">=13.0.0",
        "httpx": ">=0.27.0"
    },
    source_file=Path("/home/user/mcp-manager/pyproject.toml")
)
```

---

## Entity Relationships Diagram

```
┌─────────────────────┐
│ MCPManager          │
│ (existing)          │
└─────────┬───────────┘
          │
          ├─── uses ──► ┌──────────────────┐
          │             │ AuditConfiguration│
          │             └──────────────────┘
          │
          ├─── manages ─► ┌─────────────────┐
          │               │ MCPServerConfig │
          │               │ (existing)      │
          │               └────────┬────────┘
          │                        │
          │                        │ has (stdio only)
          │                        │
          │                        ▼
          ├─── creates ──► ┌──────────────┐
          │                │ UpdateStatus │
          │                └──────────────┘
          │
          └─── syncs to ─► ┌───────────────────┐
                           │ GeminiCLISettings │
                           │ (contains)        │
                           │ MCPServerConfig   │
                           └───────────────────┘

┌──────────────────┐
│ version_utils.py │
│ (new module)     │
└────────┬─────────┘
         │
         └─── parses ──► ┌─────────────────┐
                         │ VersionMetadata │
                         └─────────────────┘
```

---

## Validation & Constraints

### UpdateStatus Constraints
- Version comparison using `packaging.version`:
  ```python
  from packaging.version import Version, InvalidVersion

  def compare_versions(current: str, latest: str) -> str:
      """Returns 'major', 'minor', 'patch', or 'none'"""
      try:
          curr = Version(current)
          new = Version(latest)
          if new > curr:
              if new.major > curr.major:
                  return "major"
              elif new.minor > curr.minor:
                  return "minor"
              else:
                  return "patch"
          return "none"
      except InvalidVersion:
          return "none"
  ```

### AuditConfiguration Constraints
- Path validation:
  ```python
  def validate_search_paths(paths: List[str]) -> List[Path]:
      """Convert and validate path strings"""
      validated = []
      for path_str in paths:
          path = Path(path_str).expanduser().resolve()
          if not path.exists():
              raise InvalidPathError(f"Path not found: {path}")
          if not path.is_dir():
              raise InvalidPathError(f"Not a directory: {path}")
          validated.append(path)
      return validated
  ```

### GeminiCLISettings Constraints
- Server name uniqueness (merge strategy):
  ```python
  def merge_servers(
      claude_servers: Dict[str, Any],
      gemini_servers: Dict[str, Any]
  ) -> Dict[str, Any]:
      """Merge with Claude Code as source of truth"""
      merged = gemini_servers.copy()
      merged.update(claude_servers)  # Overwrite duplicates
      return merged
  ```

### VersionMetadata Constraints
- TOML parsing safety:
  ```python
  import tomllib  # Python 3.11+

  def parse_pyproject() -> VersionMetadata:
      """Parse pyproject.toml safely"""
      with open("pyproject.toml", "rb") as f:
          data = tomllib.load(f)
      return VersionMetadata(
          version=data["project"]["version"],
          python_requirement=data["project"]["requires-python"],
          mcp_server_count=6,  # Hardcoded for now
          dependencies=data["project"]["dependencies"],
          source_file=Path("pyproject.toml").resolve()
      )
  ```

---

## Storage & Persistence

### GeminiCLISettings
- **Location**: `~/.config/gemini/settings.json`
- **Format**: JSON
- **Permissions**: 0644 (readable by user, read-only for others)
- **Backup**: Not required (can be regenerated from ~/.claude.json)

### AuditConfiguration
- **Location**: `~/.config/mcp-manager/config.json` (optional)
- **Format**: JSON
- **Permissions**: 0644
- **Fallback**: Default paths if config file doesn't exist

### UpdateStatus
- **Location**: In-memory only (transient)
- **Not persisted**: Always recalculated on demand
- **Cache**: Could cache for performance (future enhancement)

### VersionMetadata
- **Source**: `pyproject.toml` (parsed on demand)
- **Not persisted**: Always read from source file
- **Used during**: Website build, documentation generation

---

## Example Usage Scenarios

### Scenario 1: Update MCP Server
```python
manager = MCPManager()

# Check for updates (dry-run)
status = manager.check_server_update("shadcn", dry_run=True)
print(f"{status.server_name}: {status.current_version} → {status.latest_version}")
print(f"Update type: {status.update_type}")

# Perform update if available
if status.update_available:
    result = manager.update_server("shadcn", dry_run=False)
    print(f"Updated: {result['updated']}")
```

### Scenario 2: Sync to Gemini CLI
```python
from mcp_manager.gemini_integration import GeminiCLIIntegration

gemini = GeminiCLIIntegration()

# Sync MCP servers from Claude Code
result = gemini.sync_from_claude(force=False)
print(f"Synced {len(result['servers_synced'])} servers")
print(f"Config: {result['config_path']}")
print(f"Env var configured: {result['env_var_configured']}")
```

### Scenario 3: Custom Audit Paths
```python
audit_config = AuditConfiguration(
    search_directories=[
        Path("/home/user/work-projects"),
        Path("/mnt/external/code")
    ],
    use_defaults=False
)

manager = MCPManager()
results = manager.audit_configurations(config=audit_config)
```

### Scenario 4: Version Metadata
```python
from mcp_manager.version_utils import get_version_metadata

metadata = get_version_metadata()
print(f"MCP Manager v{metadata.version}")
print(f"Python: {metadata.python_requirement}")
print(f"Supports {metadata.mcp_server_count} MCP servers")
```

---

## Summary

**4 new entities** defined with complete specifications:
- ✅ GeminiCLISettings (Gemini CLI synchronization)
- ✅ UpdateStatus (version tracking and updates)
- ✅ AuditConfiguration (configurable paths)
- ✅ VersionMetadata (project version information)

**All entities**:
- Have clear validation rules
- Define relationships to existing models
- Include example usage
- Specify storage/persistence requirements
- Support constitutional principles (UV-first, global config, zero downtime)

**Ready for**: Contract generation (Phase 1, step 2)
