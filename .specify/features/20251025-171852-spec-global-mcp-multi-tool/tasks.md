# Tasks: Global MCP Server Installation & Multi-Tool Sync

**Input**: Design documents from `/home/kkk/Apps/002-mcp-manager/.specify/features/20251025-171852-spec-global-mcp-multi-tool/`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 0: Pre-Implementation

- [ ] T000 [P] Verify all items in `checklists/checklist.md` are complete before release.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure directories for profiles and backups exist.

- [X] T001 [P] Create global profiles directory if missing in `~/.config/mcp-profiles/`
- [X] T002 [P] Create backup directory for Claude Code if missing in `~/.config/claude-code/backups/`
- [X] T003 [P] Create backup directory for Gemini CLI if missing in `~/.config/gemini/backups/`
- [X] T004 [P] Create backup directory for Copilot CLI if missing in `~/.config/mcp-manager/backups/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement core logic required by all user stories.

- [X] T005 Implement argument parsing for `--tool=<tool_name>` in `scripts/mcp/mcp-profile`
- [X] T006 Implement core profile reading logic from `~/.config/mcp-profiles/` in `scripts/mcp/mcp-profile`
- [X] T007 Implement timestamped backup creation for a given file path in `scripts/mcp/mcp-profile`
- [X] T008 Implement tool detection logic (claude, gemini, gh) in `scripts/mcp/mcp-profile`

---

## Phase 3: User Story 1 - One-click multi-tool profile sync (Priority: P1) 🎯 MVP

**Goal**: Apply the same MCP servers from a profile JSON across Claude Code, Gemini CLI, and Copilot CLI.

**Independent Test**: Run `mcp-profile dev --tool=all` and verify `~/.claude.json`, `~/.config/gemini/settings.json`, and `~/.config/mcp-config.json` have the same server keys as the profile.

### Implementation for User Story 1

- [X] T009 [US1] Implement `switch_profile` function in `scripts/mcp/mcp-profile`
- [X] T010 [P] [US1] Add logic to `switch_profile` to back up and write the Claude Code config to `~/.claude.json`
- [X] T011 [P] [US1] Add logic to `switch_profile` to back up and write the Gemini CLI config to `~/.config/gemini/settings.json`
- [X] T012 [P] [US1] Add logic to `switch_profile` to back up and write the Copilot CLI config to `~/.config/mcp-config.json`

---

## Phase 4: User Story 2 - Claude Code verification (Priority: P1)

**Goal**: Verify the current project's MCP servers match the selected profile and pass health checks.

**Independent Test**: Run `mcp-profile test` and see 5 boxed, colored sections with real API/CLI outputs.

### Implementation for User Story 2

- [X] T013 [US2] Implement `status` subcommand logic in `scripts/mcp/mcp-profile` to show active profiles and server lists.
- [X] T014 [US2] Implement `test` subcommand logic in `scripts/mcp/mcp-profile` to run health checks.
- [X] T015 [US2] Implement `verify` subcommand in `scripts/mcp/mcp-profile` to compare server keys.

---

## Phase 5: User Story 3 - Drift protection on git pull/push (Priority: P2)

**Goal**: Prevent regressions where `scripts/mcp/mcp-profile` gets reverted.

**Independent Test**: A CI build fails if `scripts/mcp/mcp-profile` is modified in a commit that lacks the `allow-mcp-profile-update` tag.

### Implementation for User Story 3

- [X] T016 [US3] Add a script to the CI workflow in `.github/workflows/deploy.yml` that fails the build if `scripts/mcp/mcp-profile` has been modified without the required commit message tag.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize auxiliary commands and documentation.

- [X] T017 [P] Implement `list` subcommand in `scripts/mcp/mcp-profile`
- [X] T018 [P] Implement `backup` subcommand in `scripts/mcp/mcp-profile`
- [X] T019 [P] Implement `help` subcommand in `scripts/mcp/mcp-profile`
- [X] T020 [P] Update `README.md` with new commands and multi-tool support.

---

## Dependencies & Execution Order

- **Foundational (Phase 2)** depends on **Setup (Phase 1)**.
- **All User Stories (Phase 3, 4, 5)** depend on **Foundational (Phase 2)**.
- User Stories 1 and 2 can be implemented in parallel.
- **Polish (Phase 6)** can be done after User Stories 1 and 2 are complete.

## Suggested MVP Scope

- Complete Phase 1, 2, and 3 (User Story 1).