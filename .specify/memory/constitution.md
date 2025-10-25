# MCP-Manager Constitution

**Version**: 1.0
**Ratified**: 2025-10-25

## Core Principles

### I. Simple Deployment & Verification
The project philosophy is not about minimalism, but about **easy deployment and verification**. The core purpose is to allow a developer to install `mcp-manager` on any office computer and, with one script, ensure all dependencies are available, all supported AI tools are configured consistently with shared authentication, and the installation can be easily verified.

### II. Multi-Tool Consistency
The same MCP server configurations, authentication (gh CLI, API keys, OAuth), and profiles MUST be shared and work consistently across all supported AI tools (Claude Code, Gemini CLI, Copilot CLI). Profiles are tool-agnostic.

### III. No Hardcoded Values (NON-NEGOTIABLE)
All dynamic data, especially MCP server lists and configurations, MUST be read dynamically from their source-of-truth JSON files (e.g., `~/.config/mcp-profiles/<profile>.json`). Hardcoding server lists, paths, or other configuration data is strictly prohibited to ensure accuracy and maintainability.

### IV. XDG Base Directory Compliance
The project MUST adhere to modern Linux/Unix standards (XDG Base Directory Specification).
- **User Binaries**: `~/.local/bin/`
- **User Configurations**: `~/.config/`
- **Legacy directories** (`~/bin/`, `/usr/bin/` for user scripts) MUST NOT be used.

### V. CLI-First Interface & Verification
All core functionality MUST be exposed and verifiable through the command-line interface. This includes profile switching, status checks, and health verification. TUI interfaces are for enhancing CLI verification, not replacing it. Health checks MUST use real API/CLI calls to provide accurate status.

## Development Workflow & Quality Gates

### I. Branch Management & Preservation
- **Branch Naming**: All branches MUST follow the schema: `YYYYMMDD-HHMMSS-type-short-description`.
- **Branch Preservation**: Branches MUST NEVER be deleted without explicit user permission. They contain valuable development history.
- **Merge Strategy**: All features MUST be merged into `main` via a pull request with the `--no-ff` option to preserve history.

### II. Security (NON-NEGOTIABLE)
- **No Secrets in Commits**: Committing API keys, tokens, personal emails, or any other credentials is a critical violation.
- **Mandatory Scans**: A security scan for secrets MUST be performed before every commit.

### III. Testing & Verification
- **Test-First**: Changes should be verifiable via CLI-based tests.
- **Accuracy**: Reported values (e.g., from `status` command) MUST be verified to match the actual configuration files.

## Governance
This constitution supersedes all other practices and documentation. All pull requests and reviews must verify compliance with these principles. Any amendment to this constitution requires documentation, team approval, and a clear migration plan.