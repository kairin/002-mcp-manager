# MCP Profile Switcher - AI Agent Instructions

> 🤖 **CRITICAL**: This file (AGENTS.md) is the PRIMARY instruction document for ALL AI assistants (Claude, Gemini, ChatGPT, etc.) working on this repository. ALL requirements in this file are NON-NEGOTIABLE and MUST be followed at ALL times.

> 📝 **NOTE**: CLAUDE.md and GEMINI.md are symlinks to this AGENTS.md file to ensure consistent instructions across all AI platforms.

## 🎯 Project Overview

**MCP Profile Switcher** is a simple shell script utility for managing Claude Code's MCP (Model Context Protocol) server configurations. It allows users to quickly switch between different server profiles to optimize context token usage based on their current workflow needs.

**Repository**: https://github.com/kairin/002-mcp-manager
**Type**: Shell utility script
**Language**: Bash
**Primary File**: `scripts/mcp/mcp-profile`

## ⚡ NON-NEGOTIABLE REQUIREMENTS

### 🚨 CRITICAL: Project Scope & Philosophy

**THIS IS A SIMPLE SHELL SCRIPT PROJECT**
- Keep it simple - resist over-engineering
- One shell script, one purpose: switch MCP profiles
- No Python backends, no web frameworks, no complex dependencies
- Dynamic data reading from JSON configs (no hardcoded values)
- Modern best practices (XDG standards)

### 🚨 CRITICAL: File Structure (MANDATORY)

```
002-mcp-manager/
├── .git/                    # Version control
├── .gitignore              # Git ignore patterns
├── LICENSE                 # MIT license
├── README.md               # User documentation
├── AGENTS.md               # AI agent instructions (this file)
├── CLAUDE.md               # Symlink → AGENTS.md
├── GEMINI.md               # Symlink → AGENTS.md
└── scripts/
    └── mcp/
        ├── mcp-profile     # Main shell script
        └── README.md       # Script documentation
```

**TOTAL FILES**: 5 essential files + 3 documentation/config files

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

**✅ User Configurations**: `~/.config/claude-code/`
```bash
~/.config/claude-code/mcp-servers.json
~/.config/claude-code/mcp-servers-dev.json
~/.config/claude-code/mcp-servers-ui.json
~/.config/claude-code/mcp-servers-full.json
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

### Profile Management

The script manages three profiles:

1. **dev** (~7K tokens) - Minimal servers for basic coding
2. **ui** (~12K tokens) - UI/design work with component libraries
3. **full** (~85K tokens) - All available MCP servers

### Key Operations

**Interactive Mode (Default)**:
```bash
mcp-profile           # Launch interactive menu with numbered selections
```

**Command Line Mode**:
```bash
mcp-profile status    # Show current profile
mcp-profile dev       # Switch to dev profile
mcp-profile ui        # Switch to ui profile
mcp-profile full      # Switch to full profile
mcp-profile list      # List available profiles
mcp-profile backup    # Show recent backups
mcp-profile help      # Show help message
```

### How It Works

1. **Profile Detection**: Compares `mcp-servers.json` with profile files using `cmp`
2. **Server Reading**: Uses `jq` to dynamically read server lists from JSON
3. **Backup Creation**: Automatic timestamped backups before switching
4. **Profile Switching**: Copies selected profile to active config
5. **Status Display**: Shows current profile with color-coded token usage

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
jq -r '.mcpServers | keys | join(", ")' ~/.config/claude-code/mcp-servers.json

# Test error conditions
mcp-profile invalid   # Should show error message
```

## 🔧 Maintenance Guidelines

### Adding New Profiles

To add a new profile (e.g., "lite"):

1. Create config: `~/.config/claude-code/mcp-servers-lite.json`
2. Add to PROFILES array: `PROFILES[lite]="Description|XK"`
3. Add to profile loops: `for profile in dev ui full lite`
4. Update README.md documentation
5. Test thoroughly

### Modifying Server Lists

**NEVER** modify hardcoded values. Server lists are read dynamically:

```bash
# This function reads from actual configs
get_servers() {
    local profile=$1
    jq -r '.mcpServers | keys | join(", ")' "$CONFIG_DIR/mcp-servers-$profile.json"
}
```

To change servers, edit the JSON config files in `~/.config/claude-code/`

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
- [ ] Script tested with all three profiles
- [ ] XDG paths used consistently (`~/.local/bin`, `~/.config`)
- [ ] README.md updated if functionality changed
- [ ] Branch naming follows YYYYMMDD-HHMMSS format
- [ ] Commit message includes co-authorship
- [ ] File count remains minimal (≤8 files total)

## 🚫 ABSOLUTE PROHIBITIONS

### DO NOT

- Add Python, Node.js, or any complex dependencies beyond `jq`
- Create web interfaces, APIs, or backends
- Hardcode server lists, descriptions, or configuration data
- Use legacy locations (`~/bin/`, `/usr/bin/` for user scripts)
- Delete branches without explicit user permission
- Commit secrets, API keys, or credentials
- Over-engineer a simple shell script
- Create unnecessary files or directories
- Break the simple, focused nature of this tool

### DO NOT BYPASS

- Security scanning before commits
- XDG Base Directory standards
- Dynamic data reading from JSON configs
- Branch preservation requirements
- Minimal file structure principle

## 📊 Success Metrics

This project is successful when:

1. **Simplicity**: Single shell script, minimal dependencies
2. **Accuracy**: Server lists always match actual configs (100%)
3. **Standards**: Full XDG Base Directory compliance
4. **Security**: Zero secrets leaked, all scans pass
5. **Maintainability**: Easy to understand, modify, extend
6. **Documentation**: Clear, accurate, helpful

## 🎓 Philosophy

**Keep It Simple**
- This is a shell script, not an enterprise application
- Resist the urge to add frameworks or complex architectures
- Value clarity and simplicity over clever solutions
- One file, one purpose, done well

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
