<!--
Sync Impact Report (v2.0.0):
- Version change: 1.0.0 → 2.0.0 (MAJOR)
- Modified principles:
  * Platform Agnosticism (enhanced with multi-CLI support)
  * Configuration Correctness (added cross-platform validation)
  * Developer Experience (enhanced with UV-first tooling requirements)
- Added principles:
  * X. UV-First Development (NEW - enforces UV as exclusive Python package manager)
  * XI. Project Organization (NEW - enforces repository structure standards)
  * XII. Dependency Health (NEW - requires current dependency management)
- Templates requiring updates:
  * ✅ plan-template.md - Updated (constitution checks aligned)
  * ✅ spec-template.md - Updated (requirement categories aligned)
  * ✅ tasks-template.md - Updated (task categorization aligned)
- Follow-up TODOs: None - all placeholders resolved
- Ratification date set to: 2025-10-15 (date of consolidation)
-->

# MCP Manager Constitution

## Core Principles

### I. Platform Agnosticism (MANDATORY)

Configuration format shall adapt to platform requirements automatically. MCP Manager provides universal MCP server configuration management that works seamlessly across ALL major AI CLI platforms (Claude Code, Gemini CLI, GitHub Copilot CLI) without requiring platform-specific workarounds or manual configuration changes.

**Requirements**:
- Single Source of Truth: One canonical MCP server definition works across all platforms
- Automatic Translation: Platform-specific formats generated from canonical config
- Zero Manual Intervention: No user editing of platform-specific config files
- Validation Before Deployment: Verify compatibility before applying configurations

**Rationale**: Developers use multiple AI CLI tools simultaneously. Manual configuration synchronization is error-prone and breaks development flow. Each platform has subtle differences that must be handled programmatically.

### II. Configuration Correctness by Design (MANDATORY)

Invalid configurations shall be impossible to create. Type-safe models enforce configuration structure, and platform-specific requirements are validated before generation.

**Requirements**:
- Pydantic models enforce configuration structure
- Platform-specific validation (required headers, field names, version formats)
- Real-time verification through health checks
- Automatic detection and correction of common configuration errors

**Rationale**: Silent configuration failures waste development time. The Gemini CLI timeout issue (context7 using `url` instead of `httpUrl`) must never happen again. Validation must be proactive and explicit.

### III. Explicit Platform Support Declaration (MANDATORY)

Supported platforms and their requirements shall be explicitly documented and programmatically enforced.

**Supported Platforms**:
1. Claude Code (Primary) - `.claude.json` format
2. Gemini CLI (Primary) - `~/.config/gemini/settings.json` format
3. GitHub Copilot CLI (Secondary) - `.mcp.json` format

**Configuration Compatibility Matrix**:
| Field | Claude Code | Gemini CLI | Copilot CLI |
|-------|-------------|------------|-------------|
| `type` | Required | Optional | Required |
| `url` | HTTP servers | ❌ Not supported | HTTP servers |
| `httpUrl` | ❌ Not supported | Required for HTTP | Optional |
| `headers.Accept` | Optional | **Required** for HTTP | Optional |
| `command` | stdio servers | stdio servers | stdio servers |
| `args` | Array | Array | Array |
| `env` | Object | Object | Object |

**Rationale**: Each platform has subtle differences. Explicit support matrix prevents configuration errors and guides implementation.

### IV. Version-Specific Best Practices (MANDATORY)

Package versions shall follow platform-specific best practices. Development tools use `@latest` by default; production-critical servers may use fixed versions with explicit justification.

**Requirements**:
- `@latest` for Development Tools: shadcn, playwright, etc.
- Fixed Versions for Stability: Only when required with documented rationale
- Documentation Alignment: Version recommendations match official MCP server docs
- Automatic Update Detection: Notify when newer versions available

**Rationale**: Fixed versions cause dependency staleness and compatibility issues. `@latest` ensures compatibility with evolving MCP protocol. Official documentation is the authoritative source.

### V. Comprehensive Testing Across Platforms (MANDATORY)

All configurations shall be tested on all supported platforms before deployment.

**Testing Requirements**:
1. Syntax Validation: JSON schema validation for each platform
2. Health Checks: Verify server connectivity after deployment
3. Integration Tests: Real CLI tool integration testing
4. Contract Tests: Platform-specific configuration contracts
5. Regression Prevention: Prevent re-occurrence of known issues

**Test Coverage Requirements**:
- Unit Tests: >80% line coverage
- Integration Tests: All MCP servers × All platforms
- Contract Tests: Platform-specific configuration formats
- Performance Tests: Health checks <5 seconds

**Rationale**: What works on Claude Code may fail on Gemini CLI. Universal testing prevents platform-specific failures and ensures reliability.

### VI. Backward Compatibility Guarantee (MANDATORY)

Existing configurations shall continue working after upgrades. Breaking changes require migration paths, deprecation warnings, and fallback support.

**Requirements**:
- Automatic migration from old to new format
- Clear deprecation warnings before breaking changes
- Legacy format support during transition periods
- Version detection and appropriate handling

**Rationale**: Users have existing working configurations. Breaking them without migration causes frustration and erodes trust.

### VII. Developer Experience First (MANDATORY)

Configuration management shall be effortless and intuitive. Single-command setup, automatic detection, smart defaults, and clear error messages are mandatory.

**User Experience Goals**:
- Single Command Setup: `mcp-manager init` works for all platforms
- Automatic Detection: Detect installed AI CLI tools automatically
- Smart Defaults: Reasonable defaults for all configuration options
- Clear Error Messages: Actionable error descriptions with fix suggestions
- Visual Feedback: Rich CLI output showing deployment progress
- UV-First Tooling: All Python operations use `uv` exclusively

**Rationale**: If configuration is hard, developers won't use the tool. Simplicity drives adoption. Consistent tooling reduces cognitive load.

### VIII. Security by Default (MANDATORY)

Sensitive credentials shall never be exposed or committed to version control. Environment variables, template-only documentation, and pre-commit scanning are mandatory.

**Requirements**:
- Environment Variables: API keys stored in environment, not config files
- Template-Only Configs: Documentation shows `{"API_KEY": "..."}` never real keys
- Gitignore Protection: All sensitive files automatically excluded
- Security Scanning: Pre-commit hooks prevent credential leaks
- Encrypted Storage: Optional encryption for stored credentials

**Rationale**: One leaked API key can compromise entire accounts. Security must be automatic, not optional.

### IX. Observable and Debuggable (MANDATORY)

System state shall be transparent and issues easily diagnosable. Health dashboards, structured logging, diagnostic modes, and validation reports are required.

**Observability Features**:
- Health Dashboard: Real-time server status across all platforms
- Structured Logging: Detailed logs with trace IDs
- Diagnostic Mode: Verbose output for troubleshooting
- Configuration Diff: Show differences between platform configs
- Validation Reports: Detailed validation results with line numbers

**Rationale**: When things break, developers need immediate clarity on what's wrong and how to fix it. Observability is not optional.

### X. UV-First Development (MANDATORY)

All Python package management MUST use `uv` exclusively. No `pip`, `poetry`, or other package managers shall be used in project scripts, documentation, or workflows.

**Requirements**:
- UV Exclusive: All Python dependencies installed and managed via `uv`
- System Python: Python 3.13+ system Python enforced via `[tool.uv]` in pyproject.toml
- No pip Commands: Zero `pip` usage in scripts, docs, or automation
- UV Verification: Pre-commit hooks scan for `pip` usage and fail commits
- Dependency Sync: `uv pip sync` for reproducible environments

**Rationale**: Mixed package managers cause environment instability, dependency conflicts, and reproducibility issues. UV provides faster, more reliable Python package management. Consistency is critical for development environment health.

### XI. Project Organization (MANDATORY)

Repository structure shall maintain clean separation of concerns with minimal root-level files. Backend and frontend codebases are organized separately.

**Required Structure**:
```
002-mcp-manager/
├── backend/
│   ├── src/mcp_manager/        # Python source code
│   └── tests/                   # All test files
├── frontend/                    # Astro website (if applicable)
│   └── src/                     # Astro source following conventions
├── docs/                        # Documentation
│   └── archive/                 # Historical status files
├── specs/                       # Feature specifications
├── scripts/                     # Utility scripts
├── README.md                    # Essential project docs
├── LICENSE                      # License file
├── AGENTS.md                    # Primary AI instruction file
├── pyproject.toml               # Python project config
├── package.json                 # Node.js project config
└── .gitignore                   # Git exclusions
```

**Essential Root Files**: Only files required by standard tooling in CWD are permitted at root level: README.md, LICENSE, pyproject.toml, package.json, .gitignore, AGENTS.md (and symlinks), tool configuration files, and lock files.

**Rationale**: Clean directory structure improves navigation, clarifies architecture, and signals professionalism. Historical artifacts belong in archives, not the root directory.

### XII. Dependency Health (MANDATORY)

All project dependencies (Python and Node.js) MUST be kept current with their latest stable versions. Outdated dependencies introduce security vulnerabilities and compatibility issues.

**Requirements**:
- Automated Checks: Pre-commit hooks verify no outdated dependencies
- Update Process: `uv pip list --outdated` and `npm outdated` must report zero packages
- Breaking Changes: Pin failing dependencies, update others, create GitHub issue
- Test Validation: All tests must pass after dependency updates
- Regular Audits: Weekly dependency health checks via CI/CD

**Rationale**: Security vulnerabilities and compatibility issues compound over time. Regular updates are cheaper than emergency patches. Automated enforcement prevents degradation.

## Testing & Quality Standards

### Test-First Development (MANDATORY)

- TDD required: Tests written → User approved → Tests fail → Implementation begins
- Red-Green-Refactor cycle strictly enforced
- Contract tests for platform-specific configurations
- Integration tests for multi-platform deployments
- Regression tests for all known issues

### Code Quality Gates (MANDATORY)

**Before Every Commit**:
1. Security audit: Scan for secrets and credentials
2. Code formatting: `black` compliance required
3. Linting: `ruff check` must pass
4. Type checking: `mypy` must pass with zero errors
5. Tests: `pytest` with >80% coverage
6. UV verification: No `pip` usage detected
7. Dependency audit: No outdated packages
8. Website build: `npm run build` must succeed (if frontend changes)

## Governance

### Amendment Process

This constitution supersedes all other development practices. Amendments require:
1. Documented rationale for change
2. Impact analysis on existing principles
3. Migration plan for breaking changes
4. Approval from project maintainers
5. Version increment following semantic versioning

### Version Semantics

- **MAJOR**: Backward incompatible governance/principle removals or redefinitions
- **MINOR**: New principles added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Enforcement

- All pull requests must verify constitutional compliance
- Pre-commit hooks enforce mandatory requirements
- CI/CD pipelines validate quality gates
- Complexity and deviations must be explicitly justified
- Constitutional violations block deployment

### Runtime Development Guidance

For day-to-day development guidance and AI assistant instructions, see `AGENTS.md` (symlinked as `CLAUDE.md`, `GEMINI.md` for platform-specific access).

**Version**: 2.0.0 | **Ratified**: 2025-10-15 | **Last Amended**: 2025-10-15
