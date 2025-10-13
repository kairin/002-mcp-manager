<!--
Sync Impact Report:
Version change: 1.1.0 → 1.2.0
Modified principles:
  - I. UV-First Development → Added explicit uv configuration requirements
  - VII. Cross-Platform Compatibility → Enforced Python 3.13+ system Python (zero bloat strategy)
Added sections:
  - IX. Multi-Agent Support (NEW principle for Claude/Gemini/universal AI integration)
  - Testing Completeness subsection under Quality Standards
Removed sections: None
Templates requiring updates:
  ✅ plan-template.md - Python 3.13+ system Python, UV config, Gemini CLI checks
  ✅ pyproject.toml - requires-python = ">=3.13", [tool.uv] python = "python3.13"
  ⚠ spec-template.md - May need multi-agent context guidance
  ⚠ tasks-template.md - Add runtime testing validation tasks
Follow-up TODOs:
  - Update AGENTS.md to reflect Python 3.13+ requirement (currently incorrectly states 3.11+)
  - Create spec-kit specification for system Python enforcement
  - Add Gemini CLI integration validation to quality gates
  - Document runtime testing requirements for refactored CLI modules
-->

# MCP Manager Constitution

## Core Principles

### I. UV-First Development (MANDATORY)

**ALL Python package operations MUST use the UV package manager.** Using `pip` directly is **PROHIBITED** and will cause import errors, module resolution failures, and MCP server configuration issues.

**Enforcement rules:**
- Package installation: `uv pip install <package>` (NEVER `pip install`)
- Command execution: `uv run <command>` (NEVER direct executable)
- Script execution: `uv run python <script.py>` (NEVER direct `python`)
- MCP server configs: `"command": "uv", "args": ["run", "executable"]`
- Testing: `uv run pytest` (NEVER `pytest` directly)

**Configuration requirements (MANDATORY):**
```toml
# pyproject.toml
[tool.uv]
python = "python3.11"  # Or "python3.13" for explicit version pinning
```

**Rationale:** UV provides deterministic dependency resolution, faster installs, and consistent virtual environment management across the Ubuntu 25.04 + Python 3.11+ fleet. Direct `pip` usage bypasses UV's environment isolation, causing 90% of observed failures. The explicit `[tool.uv]` configuration ensures UV uses the intended system Python interpreter, preventing version drift.

**Real-world validation:** MarkItDown MCP integration (v1.2.1) demonstrated that 100% of environment issues were resolved by strict UV-first compliance. See docs/CHANGELOG.md and docs/TROUBLESHOOTING.md for case study.

### II. Global Configuration First (MANDATORY)

**MCP servers MUST be managed globally in `~/.claude.json` by default.** Project-specific MCP configurations are prohibited unless explicitly justified and documented.

**Enforcement rules:**
- All MCP servers registered in `~/.claude.json`
- Zero project-level `.claude.json` files in repositories
- `mcp-manager migrate` command for legacy project configs
- Backup created before any configuration modification
- Health validation after every configuration change

**Rationale:** Global configuration ensures:
1. Zero configuration drift across 174+ discovered agents
2. Single source of truth for credentials (Context7, Hugging Face APIs)
3. Instant availability in new projects without manual setup
4. Fleet-wide synchronization via `mcp-manager fleet sync`

### III. Zero Downtime Operations (MANDATORY)

**Configuration changes MUST NEVER break existing MCP server setups.** All modifications require pre-flight validation, backup, and rollback capability.

**Enforcement rules:**
- Pre-modification backup: `mcp-manager config backup` (automatic)
- Health check before change: All servers must be operational
- Atomic updates: Configuration written only if validation passes
- Post-modification validation: All servers re-tested
- Automatic rollback on failure: Restore from backup within 5 seconds

**Rationale:** Claude Code, GitHub workflows, and deployed agents depend on continuous MCP server availability. A single configuration error can cascade across all projects and break active development workflows. Zero downtime is non-negotiable.

### IV. Branch Preservation (MANDATORY)

**Branches MUST NEVER be deleted without explicit user permission.** All development history is valuable and must be preserved.

**Branch naming schema (MANDATORY):**
```
YYYYMMDD-HHMMSS-type-short-description

Examples:
20250923-143000-feat-mcp-server-manager
20250923-143515-fix-configuration-audit
20250923-144030-docs-api-reference
```

**Git workflow (MANDATORY):**
```bash
DATETIME=$(date +"%Y%m%d-%H%M%S")
BRANCH_NAME="${DATETIME}-feat-description"
git checkout -b "$BRANCH_NAME"
git add .
git commit -m "Descriptive message

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>"
git push -u origin "$BRANCH_NAME"
git checkout main
git merge "$BRANCH_NAME" --no-ff
git push origin main
# NEVER: git branch -d "$BRANCH_NAME"
```

**Rationale:** Branch preservation enables:
1. Complete development history for auditing and learning
2. Rollback capability to any historical state
3. Parallel exploration of multiple approaches
4. Compliance with organizational record-keeping requirements

### V. GitHub Pages Protection (MANDATORY)

**The live website at `https://kairin.github.io/mcp-manager/` MUST remain functional at all times.** Any commit that causes 404 errors is a critical failure.

**Build requirements (NON-NEGOTIABLE):**
```bash
# ALWAYS run before committing changes affecting the website
npm run build                        # Build Astro site to docs/
test -f docs/index.html || exit 1    # Verify main page exists
test -d docs/_astro || exit 1        # Verify assets directory
test -f docs/.nojekyll || exit 1     # Verify GH Pages config

# Required files in docs/:
- index.html (entry point)
- _astro/ (compiled assets)
- .nojekyll (bypass Jekyll processing)
- favicon.svg (branding)
```

**Astro configuration (REQUIRED):**
```javascript
// astro.config.mjs
export default defineConfig({
  site: 'https://kairin.github.io',
  base: '/mcp-manager',
  outDir: './docs',
  output: 'static',
});
```

**Deployment validation:**
- Pre-push: Verify `docs/` contains built files
- Post-push: Confirm website loads within 5 minutes
- Error recovery: Immediate rebuild and redeploy on 404

**Rationale:** The GitHub Pages website serves as:
1. Public documentation for MCP Manager features
2. Office setup guide for new environment deployment
3. Visual showcase of system capabilities
4. Integration point for spec-kit workflows

Breaking the live website disrupts external users and organizational workflows.

### VI. Security by Design (MANDATORY)

**Credentials MUST be stored securely with rotation capability.** Plain-text secrets in configuration files are prohibited.

**Information Classification (MANDATORY):**
- **SAFE**: Development paths (`/home/kkk/`), binary locations, environment variable names, privacy-protected emails
- **RESTRICTED**: API keys, tokens, passwords, actual credential values
- **PROHIBITED**: Hardcoded secrets, real API keys, personal email addresses, private system information

**Repository Security Standards:**
- `.gitignore` protection: `*.env`, `*.key`, `secrets.json`, `.env.*` patterns mandatory
- Template-only approach: Show `{"API_KEY": "..."}` never `{"API_KEY": "sk-real-key"}`
- Local configuration: Real secrets in `~/.claude.json` (excluded from repository)
- Audit requirement: Security scan mandatory before every commit

**Acceptable Information Exposure:**
- Development context paths: `/home/kkk/Apps/mcp-manager` (local deployment reference)
- Binary locations: `/home/kkk/bin/github-mcp-server` (installation guidance)
- Environment variable names: `CONTEXT7_API_KEY`, `HUGGINGFACE_TOKEN` (configuration templates)
- Privacy-protected contact: `678459+kairin@users.noreply.github.com` (GitHub standard)

**Enforcement rules:**
- API keys in `~/.claude.json` with restricted file permissions (0600)
- Environment variable substitution for sensitive values
- `mcp-manager secrets rotate` command for credential updates
- Audit logging for all credential access
- Encrypted backup of credential files
- Pre-commit security scanning (automated)

**Supported credential types:**
- Context7 API key: `CONTEXT7_API_KEY`
- Hugging Face token: `HUGGINGFACE_TOKEN` (via `huggingface-cli login`)
- GitHub PAT: `GITHUB_TOKEN` (via `gh auth login`)

**Security audit commands:**
```bash
# Mandatory pre-commit security scan
git ls-files | xargs grep -l -i -E "(sk-|ghp_|ghs_|api_key.*=|token.*=)" || echo "✅ No secrets"
grep -r "CONTEXT7_API_KEY.*=" . && echo "❌ Hardcoded key" || echo "✅ Template only"
test -f ~/.claude.json && echo "✅ Local config exists" || echo "❌ Missing config"
```

**Rationale:** MCP servers access external APIs (Context7, Hugging Face, GitHub) requiring authentication. Compromised credentials could expose:
- Library documentation access patterns
- AI model usage history
- Repository access and code visibility

Secure credential management with information classification prevents 99% of accidental exposures while maintaining development transparency.

### VII. Cross-Platform Compatibility (MANDATORY)

**The system MUST operate identically on all Ubuntu 25.04 + Python 3.13 nodes in the fleet.**

**Standardization requirements:**
- OS: Ubuntu 25.04 (verified via `lsb_release -a`)
- Python: 3.13+ (system Python, verified via `python --version`)
- Package manager: UV (verified via `uv --version`)
- Node.js: 18+ for stdio MCP servers (verified via `node --version`)
- Git: 2.40+ for branch strategy (verified via `git --version`)

**Python version management (MANDATORY):**
```toml
# pyproject.toml REQUIRED configuration
[project]
requires-python = ">=3.13"

[tool.uv]
python = "python3.13"  # MANDATORY: Use system Python (no additional installations)
```

**Rationale:** The Python 3.13 system Python requirement ensures:
1. **Zero bloat**: Uses Ubuntu 25.04 system Python (no additional Python installations)
2. **Performance**: Python 3.13 speed improvements and better memory management
3. **Fleet consistency**: Identical behavior across all nodes (no version drift)
4. **Modern features**: Latest type checking, error messages, and async improvements
5. **Simplified management**: Single interpreter, no UV version juggling

**Fleet management commands:**
```bash
mcp-manager fleet register <name> <ip>  # Add node to fleet
mcp-manager fleet sync                  # Sync configs across nodes
mcp-manager fleet audit                 # Verify compliance
```

**Benefits:** Consistent environments across home office, work office, and cloud VMs enable:
1. One-command setup: `mcp-manager init` works identically everywhere
2. Configuration portability: `~/.claude.json` syncs via Git
3. Reproducible builds: Same Python/Node versions guarantee deterministic results
4. Zero-cost operations: Local CI/CD prevents GitHub billing overages

### VIII. Repository Organization (MANDATORY)

**Files MUST be organized in structured directories to prevent code creep and maintain navigability.** Root folder clutter is prohibited.

**Mandatory root folder structure:**
```
mcp-manager/
├── AGENTS.md              # Primary AI instructions (MANDATORY in root)
├── CLAUDE.md              # Symlink to AGENTS.md (MANDATORY in root)
├── GEMINI.md              # Symlink to AGENTS.md (MANDATORY in root)
├── README.md              # Project documentation (standard)
├── LICENSE                # Open source license (standard)
├── .gitignore             # Git exclusions (standard)
├── .python-version        # Python version spec (standard)
├── .pre-commit-config.yaml # Pre-commit hooks (standard)
├── pyproject.toml         # Python metadata (standard)
├── uv.lock                # Dependency lock (standard)
├── package.json           # Node.js dependencies (Astro)
├── astro.config.mjs       # Astro configuration (website)
├── tailwind.config.mjs    # Tailwind CSS config (website)
├── docs/                  # Documentation and built website
│   ├── *.md              # ALL markdown documentation
│   ├── guides/           # Reference guides
│   ├── images/           # Documentation images
│   └── _astro/           # Built website assets (GitHub Pages)
├── src/                   # Source code
│   ├── mcp_manager/      # Python package
│   └── components/       # Astro components
├── scripts/               # Utility and automation scripts
│   ├── setup/            # Setup scripts (*.py)
│   ├── verify/           # Verification utilities
│   ├── deployment/       # Deployment automation
│   └── legacy/           # Deprecated scripts
├── tests/                 # Test suite
└── .specify/              # Spec-kit workflow (constitution, templates)
```

**File placement rules (MANDATORY):**

1. **Documentation files → `docs/`**
   - CHANGELOG.md → docs/CHANGELOG.md
   - TROUBLESHOOTING.md → docs/TROUBLESHOOTING.md
   - *-guide.md → docs/guides/*-guide.md
   - *-setup.md → docs/*-setup.md
   - All reference documentation → docs/

2. **Setup scripts → `scripts/setup/`**
   - setup_*.py → scripts/setup/setup_*.py
   - *_setup.py → scripts/setup/*_setup.py
   - Installation utilities → scripts/setup/

3. **Verification scripts → `scripts/verify/`**
   - verify_*.py → scripts/verify/verify_*.py
   - *_verify.py → scripts/verify/*_verify.py
   - Health check utilities → scripts/verify/

4. **Legacy/deprecated code → `scripts/legacy/`**
   - Old standalone scripts → scripts/legacy/
   - Pre-refactor utilities → scripts/legacy/
   - Mark with deprecation notice

5. **Build automation → `scripts/` or root (context-dependent)**
   - Makefile: Can stay in root if widely used, otherwise → scripts/
   - Build scripts: scripts/build/ if multiple, root if single

**Prohibited patterns:**
- ❌ Creating files in root when appropriate subdirectory exists
- ❌ Creating new top-level directories without justification
- ❌ Scattering related files across multiple locations
- ❌ Duplicating documentation (e.g., OFFICE_SETUP.md when docs/OFFICE-DEPLOYMENT.md exists)
- ❌ Leaving scripts in root after `scripts/` directory created

**File relocation workflow (MANDATORY):**
```bash
# Use git mv to preserve history
git mv old-location/file.py new-location/file.py

# Update all references (imports, docs, README)
grep -r "old-location/file" . --exclude-dir=node_modules --exclude-dir=.git

# Test functionality after move
uv run pytest tests/

# Commit with clear message
git commit -m "refactor: relocate file.py to new-location for organization"
```

**Enforcement rules:**
- Pre-merge check: No new files in root unless justified
- File placement validation: Automated check in pre-commit hook
- Documentation updates: README must reflect current structure
- Import updates: All Python imports adjusted after moves
- Reference updates: All docs updated to new paths

**Rationale:** Repository organization prevents:
1. **Code creep:** Files accumulating in root without structure
2. **Navigation difficulty:** Developers unable to locate utilities
3. **Duplication:** Multiple files serving similar purposes
4. **Import confusion:** Unclear which version of script to use
5. **Maintenance burden:** Scattered files harder to update systematically

Clear organization enables:
1. **Instant location:** Developers know exactly where files belong
2. **Scalability:** Structure supports growth without refactoring
3. **Onboarding:** New contributors understand layout immediately
4. **Automation:** Scripts can reliably locate dependencies
5. **Auditing:** Easy to identify deprecated/redundant code

**Examples of proper organization:**

✅ **GOOD:**
```
docs/CHANGELOG.md              # Documentation in docs/
scripts/setup/setup_hf_mcp.py  # Setup utility in scripts/setup/
scripts/verify/verify_mcp.py   # Verification in scripts/verify/
```

❌ **BAD:**
```
CHANGELOG.md                   # Clutters root
setup_hf_mcp.py               # Unclear purpose from root
verify.py                      # Generic name in root
mcp-thing.md                   # Ambiguous documentation
```

### IX. Multi-Agent Support (MANDATORY)

**The system MUST support multiple AI agents (Claude Code, Gemini CLI, universal AI platforms) with synchronized MCP server configurations.** Agent-specific workflows must remain synchronized while respecting platform differences.

**Supported AI platforms:**
- **Claude Code**: Primary development agent (MCP via `~/.claude.json`)
- **Gemini CLI**: Secondary agent (MCP via `~/.config/gemini/settings.json`)
- **Universal agents**: OpenCode, GitHub Copilot (via `AGENTS.md` symlinks)

**Configuration synchronization (MANDATORY):**
```bash
# System-wide Gemini CLI integration
mcp-manager gemini sync              # Sync ~/.claude.json → ~/.config/gemini/settings.json
export GEMINI_CLI_SYSTEM_SETTINGS_PATH="$HOME/.config/gemini/settings.json"

# Verification
mcp-manager gemini verify            # Validate Gemini MCP configuration
```

**Agent instruction files (MANDATORY):**
- **AGENTS.md**: Primary instruction file (universal, platform-agnostic)
- **CLAUDE.md**: Symlink to AGENTS.md (Claude Code discovery)
- **GEMINI.md**: Symlink to AGENTS.md (Gemini CLI discovery)
- **Platform-specific files**: `.github/copilot-instructions.md`, `QWEN.md` (only if needed)

**Enforcement rules:**
- All agent instructions consolidated in `AGENTS.md`
- Platform-specific files are symlinks (NEVER duplicate content)
- MCP server configurations synchronized across `~/.claude.json` and `~/.config/gemini/settings.json`
- `mcp-manager mcp add/remove` updates both configurations when `--global` flag used
- `mcp-manager init` configures both Claude Code and Gemini CLI environments

**Configuration structure consistency:**
```json
// Both ~/.claude.json and ~/.config/gemini/settings.json use identical structure
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
    // ... other servers
  }
}
```

**Rationale:** Multi-agent support ensures:
1. **Flexibility**: Developers can use their preferred AI coding assistant
2. **Consistency**: All agents have access to same MCP servers and capabilities
3. **Maintainability**: Single source of truth (AGENTS.md) prevents instruction drift
4. **Scalability**: Easy to add support for new AI platforms (OpenCode, Qwen, etc.)
5. **Integration**: Spec-kit workflows work identically across all agents

**Benefits:**
- **Zero duplication**: Agent instructions synchronized via symlinks
- **Automatic sync**: `mcp-manager gemini sync` keeps configurations aligned
- **Fleet-wide deployment**: `mcp-manager fleet sync` propagates to all nodes
- **Platform agnostic**: Core logic works with any AI agent that supports MCP

## Quality Standards

**Testing requirements (MANDATORY):**
- Unit test coverage: ≥80% (enforced via `pytest --cov-fail-under=80`)
- Integration tests: All MCP server connectivity scenarios
- CLI tests: All `mcp-manager` commands with success/failure paths
- Performance tests: Health checks complete in <5 seconds
- Security tests: Automated secret scanning and credential validation
- **Runtime testing**: All refactored CLI modules verified with end-to-end tests (MANDATORY after modularization)

**Testing completeness (MANDATORY):**
- Deferred runtime testing MUST be completed before feature considered complete
- CLI modularization requires full regression test suite execution
- All command groups (`mcp`, `gemini`, `project`, `fleet`, `agent`, `office`) tested
- Basic execution, options, error handling, and verbose mode validated
- Test results documented and failures resolved before merge

**Code quality (MANDATORY):**
- Formatting: `black` (88 char line length)
- Linting: `ruff` (pycodestyle, pyflakes, isort, flake8-bugbear)
- Type checking: `mypy` (strict mode with complete type annotations)
- Security scanning: Pre-commit secret detection and audit validation
- Pre-commit hooks: Automated quality gates before every commit

**Documentation (MANDATORY):**
- API documentation: Complete Python API reference
- CLI reference: Every command with examples
- Troubleshooting guide: Common issues with UV-first solutions
- Following instructions guide: Why AGENTS.md compliance is critical
- Multi-agent setup guide: Claude Code + Gemini CLI integration

**Quality gates (blocking):**
```bash
# Must pass before any commit
git ls-files | xargs grep -l -i -E "(sk-|ghp_|ghs_|api_key.*=|token.*=)" || echo "✅ Security scan passed"
black src/ tests/                    # Code formatting
ruff check src/ tests/               # Linting
mypy src/                           # Type checking
pytest tests/ --cov=mcp_manager     # Testing with coverage
```

## Enforcement

**Constitution compliance is MANDATORY for all changes.** Violations block merge to main branch.

**Enforcement mechanisms:**
1. **Automated checks:** Pre-commit hooks validate UV-first, code quality, tests, security scanning, file placement
2. **GitHub Actions:** CI pipeline verifies all quality gates (when enabled)
3. **Local CI/CD:** Zero-cost workflows executed before GitHub deployment
4. **Agent validation:** Claude Code agents verify AGENTS.md compliance
5. **Security audit:** Mandatory credential scanning and information classification
6. **Organization audit:** File placement validation against repository structure rules
7. **Multi-agent sync:** Gemini CLI configuration validation
8. **Manual review:** Constitution violations require explicit justification

**Amendment procedure:**
1. Propose changes in dedicated branch: `YYYYMMDD-HHMMSS-constitution-amendment`
2. Document rationale in Sync Impact Report
3. Update dependent templates (plan, spec, tasks)
4. Increment version using semantic versioning:
   - **MAJOR:** Backward-incompatible principle changes
   - **MINOR:** New principles or significant expansions
   - **PATCH:** Clarifications, wording fixes, typo corrections
5. Commit with clear message: `docs: amend constitution to vX.Y.Z (summary)`
6. Merge to main after validation

**Conflict resolution:**
- Constitution supersedes all other documentation
- AGENTS.md must align with constitution principles
- Template updates required within same PR as constitution changes
- Runtime guidance (README, TROUBLESHOOTING) must reflect current principles

**Version increment guidelines:**
- Initial adoption: v1.0.0
- Adding UV-first principle: v1.1.0 (MINOR - new principle)
- Clarifying branch preservation rules: v1.0.1 (PATCH - clarification)
- Removing principle entirely: v2.0.0 (MAJOR - breaking change)
- Adding repository organization principle: v1.1.0 (MINOR - new principle)
- Resolving Python version conflict: v1.2.0 (MINOR - significant change to existing principle)
- Adding multi-agent support principle: v1.2.0 (MINOR - new principle)

## Governance

**Constitution supersedes all other practices.** When conflicts arise between constitution and other documentation, constitution takes precedence.

**Compliance review expectations:**
- All PRs verified against constitutional principles
- Complexity deviations require explicit justification
- Integration tests validate zero downtime operations
- Website deployment validates GitHub Pages protection
- File placement validates repository organization rules
- Multi-agent configuration synchronization verified

**Reference documents:**
- **Runtime guidance:** AGENTS.md (symlinked as CLAUDE.md, GEMINI.md)
- **Troubleshooting:** docs/TROUBLESHOOTING.md, docs/FOLLOWING-INSTRUCTIONS.md
- **Case studies:** docs/CHANGELOG.md (MarkItDown integration, v1.2.1)
- **Templates:** .specify/templates/plan-template.md, spec-template.md, tasks-template.md

**Success metrics:**
- Configuration audit: 100% accurate project vs global detection
- Migration success: >99% successful project-to-global transitions
- Health monitoring: <5 second server health check completion
- Error recovery: Automatic recovery for >90% of common issues
- Test coverage: >80% line coverage maintained
- Type coverage: 100% type annotation compliance
- Performance: CLI commands complete in <2 seconds
- Reliability: >99.9% uptime for monitoring operations
- Security compliance: 0 exposed secrets, 100% template-only credential references
- Organization compliance: 0 misplaced files, 100% adherence to directory structure
- Multi-agent sync: 100% configuration parity between Claude and Gemini CLI
- Runtime testing: 0 deferred tests, 100% CLI module validation

**Version**: 1.2.0 | **Ratified**: 2025-09-23 | **Last Amended**: 2025-10-14
