<!--
Sync Impact Report:
- Version change: None (initial constitution) → 1.0.0
- Modified principles: N/A (initial creation)
- Added sections: All core principles, governance, and compliance sections
- Removed sections: None
- Templates requiring updates:
  ✅ plan-template.md - Constitution Check section reviewed and compatible
  ✅ spec-template.md - Requirements alignment verified
  ✅ tasks-template.md - Task categorization aligns with principles
- Follow-up TODOs: None
-->

# MCP Profile Switcher Constitution

## Core Principles

### I. Dynamic Data Reading (Single Source of Truth)

All configuration data MUST be read dynamically from authoritative source files. NO hardcoded values are permitted for:
- MCP server lists (read from JSON profile files)
- Server descriptions or metadata
- Configuration values that exist in files
- Token counts or profile statistics

**Rationale**: Ensures 100% accuracy by eliminating manual synchronization errors. Changes to configuration files automatically propagate through all displays and reports without code changes.

**Enforcement**: Code review MUST verify all data sources trace back to JSON configs or runtime interrogation.

### II. XDG Base Directory Compliance

All file locations MUST follow modern Linux/Unix XDG Base Directory specification:

- **User binaries**: `~/.local/bin/` (NOT `~/bin/` or `/usr/bin/`)
- **User configurations**: `~/.config/[tool-name]/`
- **User data**: `~/.local/share/[tool-name]/`
- **Cache files**: `~/.cache/[tool-name]/`

**Rationale**: Modern standard compliance ensures predictable file locations, reduces conflicts, and follows community best practices.

**Non-compliance exceptions**: MUST be documented with explicit justification (e.g., `~/.claude.json` is Claude Code's documented location).

### III. Multi-Tool Consistency

MCP server configurations MUST work identically across all supported AI CLI tools:

- Claude Code (project-specific configurations)
- Gemini CLI (global configurations)
- GitHub Copilot CLI (documentation and awareness)

Profile JSON files are tool-agnostic. The script MUST:
- Detect which tools are installed
- Apply same profile data to each tool's configuration format
- Use shared authentication (gh CLI, API keys, OAuth tokens)
- Maintain consistent behavior regardless of tool

**Rationale**: Reduces cognitive load, ensures consistent AI capabilities across tools, and simplifies multi-computer deployment.

### IV. Deployment Simplicity (30-Minute Target)

The entire system MUST be deployable on a new office computer in under 30 minutes, including:

- Repository clone
- Dependency installation and verification
- MCP server setup
- API key configuration
- Profile creation and testing
- Health verification via TUI

**Rationale**: Fast deployment across multiple office computers is the project's primary value proposition.

**Enforcement**: Deployment checklists MUST be tested on clean systems quarterly.

### V. Security & Secrets Management

Secrets MUST NEVER be committed to version control:

- API keys (GitHub, HuggingFace, Context7, etc.)
- OAuth tokens
- Personal email addresses (use noreply@ alternatives)
- Real credentials in example configurations

**Required practices**:
- Use environment variables: `${VAR_NAME}` syntax in configs
- Security scan MUST pass before every commit
- Profile files MUST be safe to commit publicly
- Secrets rotation MUST NOT require config file changes

**Rationale**: Protects credentials while allowing configuration sharing across computers.

### VI. Branch Preservation

Git branches MUST NEVER be deleted without explicit user permission:

- ALL branches contain valuable development history
- NO automatic cleanup with `git branch -d`
- Branches MAY be merged to main, but original branch preserved
- Branch naming MUST follow format: `YYYYMMDD-HHMMSS-type-description`

**Rationale**: Preserves complete development history for audit, learning, and recovery purposes.

### VII. Automated Verification

System health MUST be easily verifiable:

- TUI displays MCP server connection status
- Visual indicators for server health (✓ Ready, ⚠ Warning, ✗ Error)
- API key testing via `mcp-profile test` command
- Dependency checking via installation scripts
- Automated backups before configuration changes

**Rationale**: Reduces troubleshooting time, increases confidence in deployments, and catches issues early.

## Development Standards

### Code Quality Requirements

**Shell Scripts MUST**:
- Quote all variables: `"$variable"`
- Use `local` for function-scoped variables
- Provide clear, actionable error messages
- Use color coding for output clarity (consistent palette)
- Include function documentation headers

**Shell Scripts MUST NOT**:
- Use global variables unnecessarily
- Ignore error conditions silently
- Make assumptions about file locations
- Skip input validation

### Testing Requirements

Before committing script changes, ALL of the following MUST pass:

```bash
# Profile switching tests
mcp-profile dev && mcp-profile status    # Verify DEV active
mcp-profile ui && mcp-profile status     # Verify UI active
mcp-profile full && mcp-profile status   # Verify FULL active

# Server list verification
jq '.projects["/home/kkk/Apps/002-mcp-manager"].mcpServers | keys' ~/.claude.json

# Cross-directory functionality
cd ~ && mcp-profile status    # Must detect correct project via git root

# Error handling
mcp-profile invalid_profile   # Must show clear error message
```

### Documentation Requirements

**README.md MUST include**:
- Installation instructions (verifiable on clean system)
- Usage examples (copy-pasteable)
- Profile descriptions (dynamically sourced, not hardcoded)
- Requirements (including `jq`, `git`, shell version)
- Troubleshooting section
- Configuration file locations (XDG-compliant)

**Script comments MUST include**:
- Function purpose and behavior
- Parameter descriptions
- Return value documentation
- Example usage where non-obvious

## Governance

### Amendment Process

Constitution amendments require:

1. Documentation of proposed changes in a dedicated branch
2. Justification for the amendment (problem being solved)
3. Review of impact on existing codebase
4. Approval before implementation
5. Version bump according to semantic versioning:
   - **MAJOR**: Backward incompatible governance changes or principle removals
   - **MINOR**: New principles or materially expanded guidance
   - **PATCH**: Clarifications, wording fixes, non-semantic refinements

### Compliance Verification

**All code reviews MUST verify**:
- No hardcoded configuration data
- XDG Base Directory compliance
- Security scan passed (no secrets)
- Multi-tool compatibility maintained
- Testing requirements completed
- Documentation updated if needed

**Complexity MUST be justified**:
- Supporting features (TUI, CI/CD, install scripts) are considered ESSENTIAL for deployment automation
- New dependencies MUST solve real problems
- Simpler alternatives MUST be considered and rejected with reasoning

### Version Control

**Git workflow MUST follow**:

```bash
# Create timestamped feature branch
git checkout -b "$(date +%Y%m%d-%H%M%S)-type-description"

# Make changes, then commit
git add .
git commit -m "Descriptive commit message

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"

# Push feature branch
git push -u origin "$(git branch --show-current)"

# Merge to main (no fast-forward to preserve history)
git checkout main
git merge "$(git branch --show-current)" --no-ff
git push origin main

# PRESERVE branch - do NOT delete
```

### Acceptable Development Paths

**✅ ACCEPTABLE in commits**:
- Development paths: `/home/kkk/Apps/002-mcp-manager`
- Binary locations: `~/.local/bin/github-mcp-server`
- Environment variable names: `GITHUB_PERSONAL_ACCESS_TOKEN`, `CONTEXT7_API_KEY`
- Privacy-protected emails: `noreply@anthropic.com`
- Configuration file paths: `~/.config/claude-code/profiles/dev.json`

**❌ NEVER ACCEPTABLE**:
- Actual secret values: `ghp_[TOKEN]`, `sk-[API_KEY]`
- Real personal emails
- Hardcoded credentials
- Production secrets in any form

## Success Metrics

This constitution is successful when:

1. **Deployment Speed**: New computer setup consistently completes in < 30 minutes
2. **Multi-Tool Support**: Same profile JSON works across Claude Code, Gemini CLI, and Copilot CLI
3. **Accuracy**: Server lists match actual configs 100% (verified by automated tests)
4. **Standards Compliance**: Full XDG Base Directory compliance across all components
5. **Security**: Zero secrets leaked, all security scans pass, shared auth works reliably
6. **Verification**: TUI clearly shows health status, issues are diagnosable in < 5 minutes
7. **Documentation**: Deployment checklists and specs enable new contributors to deploy successfully

**Version**: 1.0.0 | **Ratified**: 2025-10-20 | **Last Amended**: 2025-10-23
