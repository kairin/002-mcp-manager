# MCP Profile Switcher - AI Agent Instructions

> 🤖 **CRITICAL**: This file (AGENTS.md) is the PRIMARY instruction document for ALL AI assistants (Claude, Gemini, ChatGPT, etc.) working on this repository. ALL requirements in this file are NON-NEGOTIABLE and MUST be followed at ALL times.

> 📝 **NOTE**: CLAUDE.md and GEMINI.md are symlinks to this AGENTS.md file to ensure consistent instructions across all AI platforms.

## 🎯 Project Overview

**MCP Profile Switcher** is a unified deployment tool for managing MCP (Model Context Protocol) server configurations across multiple AI CLI tools (Claude Code, Gemini CLI, and GitHub Copilot CLI where supported). It enables rapid, consistent setup of AI development environments across multiple office computers with shared authentication and configurations.

**Repository**: https://github.com/kairin/002-mcp-manager
**Type**: Multi-tool deployment automation
**Language**: Bash
**Primary File**: `scripts/mcp/mcp-profile`
**Supported Tools**: Claude Code, Gemini CLI, GitHub Copilot CLI

## ⚡ NON-NEGOTIABLE REQUIREMENTS

### 🚨 CRITICAL: Project Scope & Philosophy

**SIMPLE DEPLOYMENT ACROSS MULTIPLE COMPUTERS**

The philosophy is **not** about minimalism - it's about **easy deployment and verification**:

**Core Purpose:**
- Install mcp-manager on any office computer
- One script ensures all dependencies are available
- All 3 AI tools (Claude Code, Gemini CLI, Copilot CLI) configured consistently
- Same MCP servers installed with shared API keys and OAuth
- Same gh CLI authentication across all computers
- TUI for easy verification that installations are correct

**Key Principles:**
- Simple to deploy, not necessarily minimal
- Shared authentication (gh CLI, API keys, OAuth)
- Same MCP server configurations across all tools
- Automated dependency checking and installation
- Visual TUI for health verification
- No hardcoded values - dynamic JSON reading
- Modern best practices (XDG standards)

### 🚨 CRITICAL: File Structure

```
002-mcp-manager/
├── .git/                         # Version control
├── .gitignore                   # Git ignore patterns
├── LICENSE                      # MIT license
├── README.md                    # User documentation
├── AGENTS.md                    # AI agent instructions (this file)
├── CLAUDE.md                    # Symlink → AGENTS.md
├── GEMINI.md                    # Symlink → AGENTS.md
├── scripts/
│   ├── mcp/
│   │   ├── mcp-profile         # Main multi-tool profile switcher
│   │   └── README.md           # Script documentation
│   ├── install/                # Installation and dependency scripts
│   ├── tui/                    # Terminal UI for verification
│   └── local-ci/               # Local CI/CD pipeline scripts
├── checklists/                  # Deployment and verification checklists
└── specs/                       # Feature specifications
```

**Structure Philosophy:**
- Core script: `scripts/mcp/mcp-profile` (multi-tool profile management)
- Supporting tools: Installation, TUI, CI/CD for deployment automation
- Documentation: Checklists and specs for features and deployment
- All scripts are deployment-focused, not over-engineered applications

### 🚨 CRITICAL: No Hardcoded Values

All dynamic data MUST be read from source files:

**✅ CORRECT - Dynamic:**
```bash
# Read server list from actual JSON config
servers=$(jq -r '.mcpServers | keys | join(", ")' "$config_file")
```

**❌ WRONG - Hardcoded:**
```bash
# Hardcoded server list
servers="github, markitdown, shadcn"
```

**Why This Matters:**
- Single source of truth (JSON config files)
- Always accurate
- Changes to configs automatically reflected
- Fully verifiable

### 🚨 CRITICAL: XDG Base Directory Compliance

Follow modern Linux/Unix standards:

**✅ User Binaries**: `~/.local/bin/`
```bash
~/.local/bin/github-mcp-server    # NOT ~/bin/
```

**✅ User Configurations**:
```bash
~/.claude.json                             # Main Claude Code config (project-scoped)
~/.config/claude-code/profiles/dev.json    # Dev profile definition
~/.config/claude-code/profiles/ui.json     # UI profile definition
~/.config/claude-code/profiles/full.json   # Full profile definition
~/.config/claude-code/backups/             # Automatic backups
```

**✅ Project Scripts**: `~/Apps/002-mcp-manager/scripts/mcp/`

**❌ NEVER USE**:
- `~/bin/` (legacy location)
- `/usr/bin/` (requires root, wrong for user scripts)
- Random locations not in PATH

### 🚨 CRITICAL: Dependencies

**Required:**
- Bash or Zsh shell
- `jq` - JSON processor (CRITICAL for reading server lists)
- Claude Code CLI
- Git

**Installation Verification:**
```bash
# Check jq is installed
which jq || echo "❌ jq not installed"

# Check script is executable
test -x scripts/mcp/mcp-profile || echo "❌ Not executable"
```

### 🚨 CRITICAL: Branch Management & Git Strategy

#### Branch Preservation (MANDATORY)
- **NEVER DELETE BRANCHES** without explicit user permission
- **ALL BRANCHES** contain valuable development history
- **NO** automatic cleanup with `git branch -d`
- **YES** to automatic merge to main branch, preserving dedicated branch

#### Branch Naming (MANDATORY SCHEMA)
**Format**: `YYYYMMDD-HHMMSS-type-short-description`

Examples:
- `20251019-143000-feat-dynamic-server-detection`
- `20251019-143515-fix-symlink-paths`
- `20251019-144030-docs-installation-guide`

#### GitHub Safety Strategy (MANDATORY)
```bash
# MANDATORY: Every commit must use this workflow
git checkout -b "$(date +%Y%m%d-%H%M%S)-type-description"
git add .
git commit -m "Descriptive commit message

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"
git push -u origin "$(git branch --show-current)"
git checkout main
git merge "$(git branch --show-current)" --no-ff
git push origin main
# NEVER: git branch -d (preserve all branches)
```

### 🚨 CRITICAL: Security Requirements

**NEVER commit:**
- API keys or tokens
- Personal email addresses (use privacy-protected: noreply@)
- Hardcoded credentials
- Real secrets in example configs

**Security Scan Before Every Commit:**
```bash
# Scan for actual secrets
git ls-files | xargs grep -l -E "(ghp_[a-zA-Z0-9]{36}|ghs_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{48})"

# Verify no hardcoded credentials
grep -r "API_KEY.*=" . --include="*.sh" --include="*.json"
```

**✅ ACCEPTABLE**:
- Development paths: `/home/kkk/Apps/002-mcp-manager`
- Binary locations: `~/.local/bin/github-mcp-server`
- Environment variable names: `GITHUB_PERSONAL_ACCESS_TOKEN`
- Privacy-protected emails: `noreply@anthropic.com`

## 📋 Core Functionality

### Multi-Tool Support

The `mcp-profile` script manages MCP configurations for:

1. **Claude Code** - Project-specific MCP server configurations
2. **Gemini CLI** - Global MCP server configurations
3. **GitHub Copilot CLI** - Documentation and awareness (limited MCP support)

### Profile Management

The script manages five configurable profiles:

1. **github** (~3K tokens) - GitHub only
2. **hf** (~73K tokens) - HuggingFace only
3. **dev** (~7K tokens) - Minimal development servers
4. **ui** (~12K tokens) - UI/design work servers
5. **full** (~12K tokens) - All available servers

Profiles are **tool-agnostic** - the same profile JSON files work across all supported tools.

### Active MCP Servers (6 Working)

- **github** - GitHub API integration (stdio)
- **markitdown** - Document to markdown conversion (stdio)
- **playwright** - Browser automation (stdio)
- **shadcn** - shadcn/ui CLI (stdio)
- **shadcn-ui** - shadcn/ui components server (stdio)
- **hf-mcp-server** - HuggingFace Hub integration (http)
- **context7** - Up-to-date library documentation (http/SSE)

**Note**: Server availability may vary by tool capabilities.

### Key Operations

**Interactive Mode (Default)**:
```bash
mcp-profile           # Launch interactive menu with numbered selections
```

**Command Line Mode - Multi-Tool**:
```bash
# Manage both Claude Code and Gemini CLI (default)
mcp-profile dev                    # Switch both tools to dev profile
mcp-profile status                 # Show status for both tools
mcp-profile backup                 # Show backups for both tools

# Manage specific tools
mcp-profile full --tool=claude     # Switch only Claude Code to full profile
mcp-profile status --tool=gemini   # Show only Gemini CLI status
MCP_TOOL=gemini mcp-profile dev    # Use environment variable

# Other commands
mcp-profile list      # List available profiles
mcp-profile test      # Test API keys and MCP servers
mcp-profile help      # Show help message
```

### How It Works

1. **Tool Detection**: Checks which AI tools are installed (Claude Code, Gemini CLI)
2. **Project Detection**: Uses git root for Claude Code (project-specific configs)
3. **Profile Reading**: Dynamically reads server lists from shared JSON profile files
4. **Backup Creation**: Automatic timestamped backups before any changes
5. **Multi-Tool Switching**:
   - Claude Code: Updates project-specific MCP servers in `~/.claude.json`
   - Gemini CLI: Updates global MCP servers in `~/.config/gemini/settings.json`
6. **Health Verification**: TUI displays connection status and server health
7. **Shared Authentication**: Uses same gh CLI auth, API keys, OAuth across tools

## 🎯 Code Quality Standards

### Shell Script Best Practices

**✅ DO:**
- Use `set -euo pipefail` for error handling (if appropriate)
- Quote all variables: `"$variable"`
- Use `local` for function variables
- Provide clear error messages
- Use color coding for output clarity

**❌ DON'T:**
- Hardcode server lists or data
- Use global variables unnecessarily
- Ignore error conditions
- Make assumptions about file locations
- Skip input validation

### Testing Requirements

Before committing changes to the script:

```bash
# Test all profiles
mcp-profile dev
mcp-profile status    # Verify shows DEV
mcp-profile ui
mcp-profile status    # Verify shows UI
mcp-profile full
mcp-profile status    # Verify shows FULL

# Verify server lists match configs
jq '.projects["/home/kkk/Apps/002-mcp-manager"].mcpServers | keys' ~/.claude.json

# Test from different directories
cd ~
mcp-profile status    # Should still detect correct project via git root

# Test error conditions
mcp-profile invalid   # Should show error message
```

## 🔧 Maintenance Guidelines

### Adding New Profiles

To add a new profile (e.g., "lite"):

1. Create profile config: `~/.config/claude-code/profiles/lite.json`
2. Add to PROFILES array in script: `PROFILES[lite]="Description|XK"`
3. Add to profile comparison loop: `for profile in dev ui full lite`
4. Update AGENTS.md and README.md documentation
5. Test thoroughly

### Modifying Server Lists

**NEVER** modify hardcoded values. Server lists are read dynamically:

```bash
# Profile files are read from ~/.config/claude-code/profiles/
get_servers_from_profile() {
    local profile=$1
    jq -r 'keys | join(", ")' "$PROFILES_DIR/$profile.json"
}
```

To change servers:
1. Edit profile files in `~/.config/claude-code/profiles/`
2. Or use `claude mcp add/remove` commands to modify `~/.claude.json`
3. Then run `mcp-profile <profile>` to sync

## 📚 Documentation Requirements

### README.md

Must include:
- Clear installation instructions
- Usage examples
- Profile descriptions (dynamic, not hardcoded)
- Requirements (including `jq`)
- Troubleshooting section
- Configuration file locations

### Script Comments

```bash
# Function: get_servers
# Purpose: Dynamically read server list from profile config
# Args: $1 - profile name (dev|ui|full)
# Returns: Comma-separated server list
get_servers() {
    # Implementation
}
```

## ✅ Pre-Commit Checklist

Before committing any changes:

- [ ] No hardcoded server lists in script
- [ ] All data read dynamically from JSON files
- [ ] Security scan completed (no secrets)
- [ ] Script tested with all supported tools (Claude, Gemini)
- [ ] XDG paths used consistently (`~/.local/bin`, `~/.config`)
- [ ] README.md updated if functionality changed
- [ ] Branch naming follows YYYYMMDD-HHMMSS format
- [ ] Commit message includes co-authorship
- [ ] Symlinks (CLAUDE.md, GEMINI.md) point to AGENTS.md

## 🚫 ABSOLUTE PROHIBITIONS

### DO NOT

- Hardcode server lists, descriptions, or configuration data
- Use legacy locations (`~/bin/`, `/usr/bin/` for user scripts)
- Delete branches without explicit user permission
- Commit secrets, API keys, or credentials
- Create unnecessary web interfaces or complex GUIs
- Break multi-tool compatibility
- Remove deployment automation features (TUI, CI/CD, install scripts)

### DO NOT BYPASS

- Security scanning before commits
- XDG Base Directory standards
- Dynamic data reading from JSON configs
- Branch preservation requirements
- Multi-tool support (Claude Code + Gemini CLI)
- Shared authentication principle

## 📊 Success Metrics

This project is successful when:

1. **Easy Deployment**: Can set up new office computer in < 30 minutes
2. **Multi-Tool Support**: Same configs work across Claude Code, Gemini CLI
3. **Accuracy**: Server lists always match actual configs (100%)
4. **Standards**: Full XDG Base Directory compliance
5. **Security**: Zero secrets leaked, shared auth works, all scans pass
6. **Verification**: TUI shows health status clearly
7. **Documentation**: Clear deployment checklists and specs

## 🎓 Philosophy

**Simple Deployment, Not Minimal Features**
- The goal is **easy setup** across multiple computers
- Supporting features (TUI, CI/CD, install scripts) are **essential**
- Automation reduces human error in deployment
- One-command setup is the ideal

**Multi-Tool Consistency**
- Same MCP servers across all AI tools
- Shared authentication (gh CLI, API keys, OAuth)
- Tool-agnostic profile configurations
- Consistent behavior regardless of tool

**Be Accurate**
- Read data from source files, never hardcode
- Verify reported values match actual configs
- Single source of truth principle

**Follow Standards**
- XDG Base Directory specification
- Modern Unix/Linux conventions
- Shell script best practices

---

**Version**: 1.0
**Last Updated**: 2025-10-19
**Status**: ACTIVE - MANDATORY COMPLIANCE
**Project Type**: Simple shell utility
**Review**: Required before major changes
