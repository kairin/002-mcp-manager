<!--
Sync Impact Report:
- Version change: 1.0.0 -> 1.1.0
- Modified principles: "Minimal Dependencies", "File Structure"
- Added sections: None
- Removed sections: None
- Templates requiring updates: None
- Follow-up TODOs: None
-->
# MCP Profile Switcher Constitution

## Core Principles

### I. Simplicity
This is a simple shell script project. Resist over-engineering. The project must remain a single shell script with one purpose: to switch MCP profiles. No Python backends, no web frameworks, no complex dependencies.

### II. No Hardcoded Values
All dynamic data MUST be read from source files, specifically JSON configuration files. This ensures a single source of truth, accuracy, and that changes to configs are automatically reflected.

### III. XDG Base Directory Compliance
Follow modern Linux/Unix standards for file locations. User binaries must be in `~/.local/bin/`, and user configurations in `~/.config/claude-code/`.

### IV. Minimal Dependencies
The project must only rely on `bash` (or `zsh`), `jq`, the `claude-code-cli`, and `git`. For the web-based components, `Node.js` and `Astro` are also approved dependencies.

### V. Strict Branching and Git Strategy
A strict branch naming convention (`YYYYMMDD-HHMMSS-type-short-description`) and Git workflow must be followed. Branches must never be deleted without explicit user permission.

### VI. Security First
Never commit API keys, tokens, personal email addresses, or other secrets. A security scan must be performed before every commit.

### VII. Shell Script Best Practices
Use `set -euo pipefail` for error handling, quote all variables, use `local` for function variables, and provide clear error messages.

### VIII. Thorough Testing
All profiles and error conditions must be tested before committing changes to the script.

### IX. Dynamic Data Reading
Server lists and other configuration data must be read dynamically from JSON files using `jq`.

### X. Clear Documentation
The `README.md` file and script comments must be clear, accurate, and comprehensive.

## File Structure

The project must adhere to the following file structure:
```
002-mcp-manager/
├── .git/
├── .gitignore
├── LICENSE
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── scripts/
│   ├── mcp/
│   │   ├── mcp-profile
│   │   └── README.md
│   ├── tui/
│   │   └── ...
│   └── local-ci/
│       └── ...
└── web/
    └── ...
```

## Development Workflow

The development workflow must follow the GitHub Safety Strategy outlined in `AGENTS.md`. All commits must be done on a feature branch, which is then merged into `main`.

## Governance

This Constitution supersedes all other practices. Amendments require documentation, approval, and a migration plan. All pull requests and reviews must verify compliance with this constitution.

**Version**: 1.1.0 | **Ratified**: 2025-10-19 | **Last Amended**: 2025-10-19
