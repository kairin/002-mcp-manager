# Feature Specification: Multi-Tool MCP Profile Management

**Feature Branch**: `003-multi-tool-support`
**Created**: 2025-10-23
**Status**: Completed (Retroactive Documentation)
**Input**: Document and verify the multi-tool support implementation including Gemini CLI integration, symlink fixes, and updated project philosophy

## Clarifications

### Session 2025-10-26
- Q: The specification details how to switch between profiles, but not how they are created or deleted. How should users manage the lifecycle of MCP profiles? → A: TUI-based management: Add a new section to the Terminal UI (TUI) that allows users to create, edit, and delete profiles interactively.
- Q: The spec lists `jq` as a critical dependency. What is the desired behavior if `jq` is not installed when the `mcp-profile` script is run? → A: Attempt auto-install: The script tries to install `jq` using the system's package manager (e.g., `apt-get`, `brew`), which may require `sudo` privileges.
- Q: The spec mentions creating timestamped backups of configuration files (`~/.claude.json`, `~/.config/gemini/settings.json`). These files might contain sensitive information like API keys or tokens. What is the security requirement for these backups? → A: Redacted: Before creating the backup, redact any values that look like secrets (e.g., API keys) and replace them with placeholders.
- Q: The spec does not define any limits on the number of profiles or servers. To prevent performance issues or unexpected behavior, what is a reasonable upper limit for the number of profiles and the number of servers within a single profile? → A: No technical limit: The script should be written to handle any number of profiles and servers, with performance degradation being the only consequence of very large numbers.
- Q: The spec assumes a "standard MCP server configuration schema". To prevent issues if this schema changes in the future, should the script include a versioning mechanism for the profile files? → A: Per-profile versioning: Add a version number (e.g., `"$schema_version": "1.0"`) to each profile JSON file. The script will check this version to handle different schemas.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Unified Profile Management Across AI Tools (Priority: P1)

As a developer using multiple AI CLI tools (Claude Code and Gemini CLI), I want to switch MCP server profiles consistently across all tools with a single command, so that I have the same capabilities available regardless of which AI tool I'm using.

**Why this priority**: This is the core value proposition - enabling consistent AI capabilities across multiple tools without manual configuration synchronization.

**Independent Test**: Run `mcp-profile dev` and verify both `~/.claude.json` and `~/.config/gemini/settings.json` are updated with the dev profile servers. Switching to a different profile should update both configs atomically.

**Acceptance Scenarios**:

1. **Given** I have both Claude Code and Gemini CLI installed, **When** I run `mcp-profile dev`, **Then** both `~/.claude.json` and `~/.config/gemini/settings.json` should contain only the servers from the dev profile
2. **Given** I have only Claude Code installed (Gemini CLI missing), **When** I run `mcp-profile full`, **Then** the script should update Claude Code's config and display a message that Gemini CLI was skipped (graceful degradation)
3. **Given** I want to update only one tool, **When** I run `mcp-profile ui --tool=claude`, **Then** only `~/.claude.json` should be updated, leaving Gemini CLI config unchanged
4. **Given** I'm in any directory within the project, **When** I run `mcp-profile status`, **Then** I should see the active profile for all installed tools with server counts and health indicators

**Verification Requirements**:
- [ ] Actual JSON files are modified (not just messages displayed)
- [ ] Server lists in configs match the profile JSON files exactly
- [ ] Timestamp backups are created before each switch
- [ ] Tool detection actually checks for installed binaries (not hardcoded)
- [ ] --tool flag correctly filters operations to specified tool(s)

---

### User Story 2 - Tool-Specific Profile Switching (Priority: P2)

As a developer who wants fine-grained control, I want to switch profiles for individual AI tools independently, so that I can use different MCP server configurations for Claude Code versus Gemini CLI when needed.

**Why this priority**: Provides flexibility for advanced users who may want different capabilities per tool (e.g., project-specific Claude setup vs global Gemini setup).

**Independent Test**: Run `mcp-profile full --tool=gemini` and verify only Gemini CLI config changes while Claude Code config remains untouched. The `mcp-profile status` command should show different active profiles for each tool.

**Acceptance Scenarios**:

1. **Given** Claude Code is on dev profile and Gemini CLI is on ui profile, **When** I run `mcp-profile status`, **Then** the output should clearly show different active profiles for each tool with distinct server lists
2. **Given** I want to update only Gemini CLI, **When** I run `MCP_TOOL=gemini mcp-profile full`, **Then** only `~/.config/gemini/settings.json` should change to the full profile
3. **Given** I specify an invalid tool name, **When** I run `mcp-profile dev --tool=invalid`, **Then** I should see a clear error message listing valid tool options (claude, gemini, all)

**Verification Requirements**:
- [ ] Tool-specific operations don't affect other tools' configs
- [ ] Environment variable MCP_TOOL is respected
- [ ] Status command shows per-tool active profiles accurately
- [ ] Error messages for invalid tool names are actionable

---

### User Story 3 - Consistent AI Instructions via Symlinks (Priority: P3)

As an AI assistant (Claude, Gemini, or ChatGPT), I want to read project instructions from my respective instruction file (CLAUDE.md, GEMINI.md) which are symlinks to AGENTS.md, so that all AI tools receive identical, synchronized guidance.

**Why this priority**: Ensures consistency across AI platforms and simplifies maintenance (single source of truth for AI instructions).

**Independent Test**: Verify `CLAUDE.md` and `GEMINI.md` are actual symlinks (not copies) pointing to `AGENTS.md`. Modifying `AGENTS.md` should be immediately visible when reading through the symlinks.

**Acceptance Scenarios**:

1. **Given** the repository is freshly cloned, **When** I run `ls -la CLAUDE.md GEMINI.md`, **Then** both files should show as symlinks with `->` pointing to `AGENTS.md`
2. **Given** I update `AGENTS.md` with new instructions, **When** I read `CLAUDE.md` or `GEMINI.md`, **Then** the content should match `AGENTS.md` exactly (no stale copies)
3. **Given** I delete a symlink and recreate it, **When** I check the symlink target, **Then** it should point to `AGENTS.md` (relative path, not absolute)

**Verification Requirements**:
- [ ] Files are actual symlinks (check with `test -L CLAUDE.md`)
- [ ] Symlinks use relative paths (not absolute `/home/user/...` paths)
- [ ] Reading symlinks returns identical content to `AGENTS.md`
- [ ] Symlinks are committed to git as symlinks (not as file copies)

---

### User Story 4 - TUI-based Profile Lifecycle Management (Priority: P2)

As a developer, I want to manage my MCP profiles (create, edit, delete) directly from within the TUI, so that I don't have to manually edit JSON files.

**Acceptance Scenarios**:
1. **Given** I am in the TUI, **When** I select the "Manage Profiles" option, **Then** I should see a list of my current profiles.
2. **Given** I am in the profile management screen, **When** I choose to create a new profile, **Then** I should be prompted for a profile name and a list of servers.
3. **Given** I am in the profile management screen, **When** I choose to delete a profile, **Then** I should be asked for confirmation before the profile file is removed.

---

### Edge Cases

- What happens when user runs `mcp-profile` on a system with neither Claude Code nor Gemini CLI installed?
  - **Expected**: Clear error message listing installation instructions for both tools

- What happens when profile JSON file is missing or malformed?
  - **Expected**: Error message with specific file path and JSON validation error

- What happens when user tries to switch to a profile that doesn't exist?
  - **Expected**: List available profiles and suggest correct spelling

- What happens when Claude Code config file doesn't have the project path initialized?
  - **Expected**: Initialize project structure or provide clear setup instructions

- What happens when Gemini CLI settings.json doesn't exist?
  - **Expected**: Create settings file with proper structure and MCP servers section

- What happens if the automatic installation of `jq` fails?
  - **Expected**: The script should print a clear error message explaining that `jq` is required and could not be installed automatically, then provide manual installation instructions and exit.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect which AI CLI tools are installed (Claude Code, Gemini CLI) by checking for their binary executables
- **FR-002**: System MUST support switching profiles for all installed tools simultaneously (default behavior)
- **FR-003**: System MUST support switching profiles for individual tools using `--tool=claude|gemini|all` flag
- **FR-004**: System MUST support tool selection via `MCP_TOOL` environment variable
- **FR-005**: System MUST create timestamped backups before modifying any configuration files. Before saving, the backup process MUST redact any values that match common secret patterns (e.g., API keys, tokens).
- **FR-006**: System MUST read profile definitions from tool-agnostic JSON files in `~/.config/mcp-profiles/`
- **FR-007**: System MUST update Claude Code's project-specific MCP servers in `~/.claude.json`
- **FR-008**: System MUST update Gemini CLI's global MCP servers in `~/.config/gemini/settings.json`
- **FR-009**: System MUST gracefully handle missing tools by skipping their configuration updates with informative messages
- **FR-010**: System MUST display current active profile for each installed tool via `mcp-profile status` command
- **FR-011**: `CLAUDE.md` and `GEMINI.md` MUST be symlinks (not file copies) pointing to `AGENTS.md`
- **FR-012**: Symlinks MUST use relative paths for cross-platform compatibility
- **FR-013**: `AGENTS.md` MUST document the deployment-focused philosophy (not minimalism)
- **FR-014**: Documentation MUST reflect multi-tool support in all usage examples
- **FR-015**: System MUST validate profile JSON structure before applying to tool configs
- **FR-016**: The TUI MUST provide a section for creating, editing, and deleting MCP profiles.
- **FR-017**: The system MUST check for the `jq` dependency on startup. If missing, it MUST attempt to install it using the appropriate system package manager.
- **FR-018**: Each profile JSON file MUST contain a `"$schema_version"` key. The script MUST validate this version and handle different versions appropriately.

### Non-Functional Requirements

- **NFR-001 (Scalability)**: The system MUST NOT enforce any hard limits on the number of profiles or the number of servers per profile. It should be designed to handle a large number of items, with the understanding that performance may degrade.

### Implementation Verification Requirements

These requirements ensure the implementation is complete and functional (not placeholder code):

- **VR-001**: Actual file I/O operations MUST occur (verify by checking file modification timestamps)
- **VR-002**: JSON parsing MUST use actual libraries (e.g., `jq`), not string manipulation
- **VR-003**: Tool detection MUST check actual binary paths using `which` or `command -v`
- **VR-004**: Backup creation MUST result in physical files in backup directories
- **VR-005**: Configuration updates MUST be verifiable by reading the config files directly
- **VR-006**: Symlink creation MUST use `ln -s` (not `cp`), verifiable with `test -L`
- **VR-007**: Error handling MUST produce specific error messages (not generic "failed" messages)
- **VR-008**: Profile switching MUST be idempotent (running twice produces same result)
- **VR-009**: Status command MUST read actual config files (not cached state)
- **VR-010**: All user-facing features MUST have corresponding test cases in verification checklist
- **VR-011**: Redacted backups MUST NOT contain plain-text secrets. Verify by inspecting backup files after a profile switch.

### Key Entities

- **MCP Profile**: A named collection of MCP server configurations (e.g., dev, ui, full) stored as tool-agnostic JSON files
  - Attributes: name, server list (with configurations), token count estimate, `$schema_version`
  - Location: `~/.config/mcp-profiles/{profile-name}.json`

- **Tool Configuration**: AI-tool-specific config file containing active MCP servers
  - Claude Code: `~/.claude.json` (project-specific, contains multiple projects)
  - Gemini CLI: `~/.config/gemini/settings.json` (global, single MCP section)

- **Configuration Backup**: Timestamped snapshot of tool config before modifications. The content MUST be redacted to remove secrets.
  - Attributes: timestamp, original config content, tool name
  - Location: Tool-specific backup directories

- **AI Instruction Document**: Symlinked files providing AI-specific guidance
  - `AGENTS.md`: Master instruction file (single source of truth)
  - `CLAUDE.md`, `GEMINI.md`: Symlinks to AGENTS.md for tool-specific discovery

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can switch MCP profiles for all installed AI tools with a single command in under 5 seconds
- **SC-002**: Profile switching operation completes successfully 100% of the time when tools are properly installed (no silent failures)
- **SC-003**: Configuration files are backed up before every modification, with backups retrievable for at least 30 days
- **SC-004**: Tool detection correctly identifies installed tools and skips missing tools with clear messages (0% false positives)
- **SC-005**: Symlinks remain functional after git operations (clone, pull, checkout) on Linux, macOS, and Windows (with symlink support)
- **SC-006**: AI assistants reading CLAUDE.md or GEMINI.md receive identical, synchronized instructions from AGENTS.md
- **SC-007**: Developers can verify implementation completeness by running all verification requirements in under 10 minutes
- **SC-008**: Multi-computer deployment using the same repository maintains consistent symlinks and profile configurations across all systems

### Verification Outcomes

- **VC-001**: All symlinks pass `test -L` check and point to correct relative target
- **VC-002**: Running `mcp-profile dev` followed by `jq '.projects[].mcpServers | keys' ~/.claude.json` returns exact server list from dev profile
- **VC-003**: Running `mcp-profile full --tool=gemini` updates only Gemini CLI config (Claude config mtime unchanged)
- **VC-004**: Profile JSON files contain no hardcoded values - all data comes from profile definitions
- **VC-005**: Tool detection gracefully handles missing binaries (test by temporarily removing tool from PATH)
- **VC-006**: Backup directories contain timestamped files after profile switches (verify with `ls -lt`)
- **VC-007**: Status command output shows different profiles for Claude vs Gemini when set independently

## Assumptions

- Users have basic command-line experience and can read shell output
- Git is installed and symlinks are supported on the target platform
- Users have write permissions to `~/.config/` and `~/.claude.json`
- The user's environment has a common package manager (`apt`, `yum`, `brew`, etc.) and the user has permissions to install packages (or can provide `sudo` password).
- Profile JSON files use standard MCP server configuration schema
- Tool binaries (claude, gemini) are in system PATH when installed
- Backup retention is handled by users (automatic cleanup not implemented)
- Project philosophy documentation is maintained in AGENTS.md as the authoritative source

## Dependencies

- External: `jq` for JSON processing (CRITICAL requirement)
- External: `git` for repository operations and branch management
- External: Claude Code CLI (optional, graceful degradation if missing)
- External: Gemini CLI (optional, graceful degradation if missing)
- Internal: Profile JSON files in `~/.config/mcp-profiles/` directory
- Internal: AGENTS.md as the symlink target for AI instructions

## Out of Scope

- Automatic installation of Claude Code or Gemini CLI tools (users install manually)
- Automatic cleanup of old backups (users manage retention manually)
- Profile synchronization across multiple computers (handled by git repository sharing)
- MCP server health monitoring beyond basic configuration validation
- Migration of existing configurations from other tools
- GUI or web interface for profile management (CLI only)
- Support for additional AI tools beyond Claude Code, Gemini CLI, and Copilot CLI (future enhancement)
