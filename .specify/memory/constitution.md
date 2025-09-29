<!--
Sync Impact Report:
Version change: None → 1.0.0
Modified principles: N/A (initial constitution creation)
Added sections:
  - I. UV-First Development (new)
  - II. Global Configuration First (new)
  - III. Zero Downtime Operations (new)
  - IV. Branch Preservation (new)
  - V. GitHub Pages Protection (new)
  - VI. Security by Design (new)
  - VII. Cross-Platform Compatibility (new)
  - Quality Standards section (new)
  - Enforcement section (new)
Removed sections: N/A
Templates requiring updates:
  ✅ plan-template.md - Updated constitution check section
  ✅ spec-template.md - No changes required (implementation-agnostic)
  ✅ tasks-template.md - No changes required (follows plan)
Follow-up TODOs: None
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

**Rationale:** UV provides deterministic dependency resolution, faster installs, and consistent virtual environment management across the Ubuntu 25.04 + Python 3.13 fleet. Direct `pip` usage bypasses UV's environment isolation, causing 90% of observed failures.

**Real-world validation:** MarkItDown MCP integration (v1.2.1) demonstrated that 100% of environment issues were resolved by strict UV-first compliance. See CHANGELOG.md and TROUBLESHOOTING.md for case study.

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
- Python: 3.13+ (verified via `python --version`)
- Package manager: UV (verified via `uv --version`)
- Node.js: 18+ for stdio MCP servers (verified via `node --version`)
- Git: 2.40+ for branch strategy (verified via `git --version`)

**Fleet management commands:**
```bash
mcp-manager fleet register <name> <ip>  # Add node to fleet
mcp-manager fleet sync                  # Sync configs across nodes
mcp-manager fleet audit                 # Verify compliance
```

**Rationale:** Consistent environments across home office, work office, and cloud VMs enable:
1. One-command setup: `mcp-manager init` works identically everywhere
2. Configuration portability: `~/.claude.json` syncs via Git
3. Reproducible builds: Same Python/Node versions guarantee deterministic results
4. Zero-cost operations: Local CI/CD prevents GitHub billing overages

## Quality Standards

**Testing requirements (MANDATORY):**
- Unit test coverage: ≥80% (enforced via `pytest --cov-fail-under=80`)
- Integration tests: All MCP server connectivity scenarios
- CLI tests: All `mcp-manager` commands with success/failure paths
- Performance tests: Health checks complete in <5 seconds
- Security tests: Automated secret scanning and credential validation

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
1. **Automated checks:** Pre-commit hooks validate UV-first, code quality, tests, security scanning
2. **GitHub Actions:** CI pipeline verifies all quality gates (when enabled)
3. **Local CI/CD:** Zero-cost workflows executed before GitHub deployment
4. **Agent validation:** Claude Code agents verify AGENTS.md compliance
5. **Security audit:** Mandatory credential scanning and information classification
6. **Manual review:** Constitution violations require explicit justification

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

## Governance

**Constitution supersedes all other practices.** When conflicts arise between constitution and other documentation, constitution takes precedence.

**Compliance review expectations:**
- All PRs verified against constitutional principles
- Complexity deviations require explicit justification
- Integration tests validate zero downtime operations
- Website deployment validates GitHub Pages protection

**Reference documents:**
- **Runtime guidance:** AGENTS.md (symlinked as CLAUDE.md, GEMINI.md)
- **Troubleshooting:** TROUBLESHOOTING.md, docs/FOLLOWING-INSTRUCTIONS.md
- **Case studies:** CHANGELOG.md (MarkItDown integration, v1.2.1)
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

**Version**: 1.0.0 | **Ratified**: 2025-09-23 | **Last Amended**: 2025-09-30