# Changelog

All notable changes to MCP Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-14

### Added

#### Phase 1: MCP Updates & Gemini Integration (FR001-FR010)
- **FR001**: Update server detection - Added MCP server update checking with version comparison
- **FR002**: Context7 updates - Implemented HTTP-based update checks for Context7 MCP server
- **FR003**: GitHub MCP updates - Added stdio-based update checks for GitHub MCP server
- **FR004**: Semantic versioning - Implemented semver parsing, comparison, and categorization (major/minor/patch)
- **FR005**: Update metadata - Created UpdateStatus model with current_version, latest_version, update_available fields
- **FR006**: Gemini MCP sync - Implemented sync from Claude's global ~/.claude.json to Gemini's ~/.config/gemini/
- **FR007**: Gemini integration - Added GeminiCLIIntegration class with sync_from_claude() method
- **FR008**: Gemini CLI commands - Created `mcp-manager gemini sync` and `mcp-manager gemini status` commands
- **FR009**: Conditional sync - Implemented smart sync that skips if Gemini config is up-to-date
- **FR010**: Force sync - Added `--force` flag to override conditional sync logic

#### Phase 2: Error Handling & Documentation (FR011-FR019)
- **FR011**: Custom exceptions - Added UpdateCheckError, NoUpdateAvailableError, UpdateFailedError
- **FR012**: Error handling - Comprehensive try/catch blocks with specific error types
- **FR013**: Logging - Structured logging with context for debugging update failures
- **FR014**: Validation - Pre-flight checks before attempting updates or sync operations
- **FR015**: API documentation - Complete docstrings for all public methods and classes
- **FR016**: Contract tests - Test files for update_server and gemini_sync contracts
- **FR017**: Integration tests - End-to-end workflow tests for MCP updates and Gemini sync
- **FR018**: Error scenarios - Tests for network failures, invalid versions, missing configs
- **FR019**: README updates - Documented new features, CLI commands, and workflows

#### Phase 3: CLI Modularization & Dynamic Versioning (FR020-FR029)
- **FR020**: Configurable audit - Added AuditConfiguration model with search_directories, use_defaults
- **FR021**: Custom paths - Support for custom search paths beyond default ~/.claude.json and ~/Apps/
- **FR022**: Configuration file - Load audit config from ~/.mcp-manager/config.json
- **FR023**: Gemini settings - GeminiCLISettings model with auto_sync, config_path, sync_interval
- **FR024**: Audit contract - Contract tests for audit functionality with custom paths
- **FR025**: CLI refactoring - Modularized cli.py into cli/mcp_commands.py and cli/gemini_commands.py
- **FR026**: Command separation - Separated MCP and Gemini commands into dedicated modules
- **FR027**: Dynamic versioning - Created version_utils.py to parse pyproject.toml using tomllib
- **FR028**: Astro integration - Updated astro.config.mjs to inject PROJECT_VERSION from pyproject.toml
- **FR029**: Website versioning - Updated index.astro and Features.astro to use dynamic version

### Changed
- Refactored CLI interface from single 1700-line file into modular structure
- Improved error handling with specific exception types for different failure scenarios
- Enhanced audit functionality to support custom search directories
- Updated website to display version dynamically from pyproject.toml (single source of truth)

### Technical Details
- **Python 3.11+**: Uses tomllib for native TOML parsing
- **Pydantic Models**: UpdateStatus, AuditConfiguration, GeminiCLISettings, VersionMetadata
- **Type Hints**: Full type annotations throughout codebase
- **Test Coverage**: 66 tests passing (contract + integration tests)
- **Code Quality**: Black formatting, Ruff linting applied
- **Build System**: Astro 5.x with dynamic version injection via Vite

### Testing
- 66 tests implemented and passing
- Contract tests for update_server, gemini_sync, audit_with_paths
- Integration tests for mcp_update_workflow, gemini_sync_workflow, configurable_audit
- Error scenario testing for network failures and missing configurations

### Documentation
- Complete API documentation with docstrings
- CLI command reference for MCP and Gemini operations
- Contract documentation for update and sync workflows
- README updates with feature descriptions and usage examples

## [Unreleased]

### Planned
- Additional MCP server support (Playwright, Hugging Face, MarkItDown)
- Health monitoring dashboard with real-time metrics
- Automated update installation (currently only detection)
- Configuration migration tools for project-to-global conversion
- Performance optimization for large-scale audits

---

**Repository**: https://github.com/kairin/mcp-manager
**License**: MIT
**Author**: Mister K <678459+kairin@users.noreply.github.com>
