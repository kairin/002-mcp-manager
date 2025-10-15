# Feature Specification: Project Health and Standardization Audit

**Feature Branch**: `005-we-ve-gone`
**Created**: 2025-10-15
**Status**: Draft
**Input**: User description: "we've gone through several implementation, but for the tech stack, can you check through the subfolders to identify anything else that i might miss /home/kkk/Apps/002-mcp-manager/specs especially with regards to ensure that the app is uv first, and updated to all latest versions. all python related requirements should be uv only, and critically, to ensure that the root folder does not end up with so many documents files and everything should be properly stored within subfolders."

## Clarifications

### Session 2025-10-15

- Q: When refactoring to `backend/` and `frontend/` directories, what should happen to the current hybrid structure where Python source is in `src/mcp_manager/` and Astro is in `website/src/`? → A: Complete restructure: `backend/src/`, `backend/tests/` as separate top-level, `frontend/` follows Astro defaults
- Q: The spec mentions: "What happens if a dependency update introduces a breaking change that causes tests to fail?" What should be the recovery strategy? → A: Pin the specific failing dependency to previous version, update others, create GitHub issue to track
- Q: How should "essential root-level configuration files" be distinguished from "non-essential files that should be moved"? → A: Files required by standard tooling in CWD
- Q: When moving to `backend/src/` and `backend/tests/`, how should `pyproject.toml` package discovery be configured? → A: Use `packages = [{include = "mcp_manager", from = "backend/src"}]` in pyproject.toml

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enforce `uv`-first Development (Priority: P1)

As a developer, I want to ensure all Python package management is handled exclusively by `uv`, so that the development environment is consistent, reproducible, and free of `pip`-related conflicts or errors.

**Why this priority**: This is critical for environment stability and preventing the kind of dependency issues that have occurred in the past. It is a foundational requirement for the project.

**Independent Test**: A new developer can clone the repository, follow the setup instructions, and successfully run all project verification scripts using only `uv` commands. No `pip` commands should be present or required.

**Acceptance Scenarios**:

1.  **Given** a clean checkout of the project, **When** a developer follows the setup instructions, **Then** the entire environment is bootstrapped using only `uv`.
2.  **Given** the project's scripts and documentation, **When** they are searched for the term "pip", **Then** no occurrences are found in an execution context.

---

### User Story 2 - Update All Dependencies (Priority: P2)

As a developer, I want to ensure all project dependencies (both Python and Node.js) are updated to their latest stable versions, so that the project benefits from the latest features, security patches, and performance improvements.

**Why this priority**: Using outdated packages introduces security vulnerabilities and can lead to compatibility issues. Regular updates are a key part of project maintenance.

**Independent Test**: After running an update process, tools like `uv pip list --outdated` and `npm outdated` report no available updates for project dependencies.

**Acceptance Scenarios**:

1.  **Given** the project's `pyproject.toml` and `package.json` files, **When** an update command is run, **Then** all dependencies are upgraded to their latest stable versions and the lock files (`uv.lock`, `package-lock.json`) are updated.
2.  **Given** the updated dependencies, **When** the project's test suite is run, **Then** all tests pass, confirming no breaking changes were introduced.

---

### User Story 3 - Refactor Project Structure for Maintainability (Priority: P1)

As a developer, I want to refactor the project structure to cleanly separate the Python backend from the Astro frontend and to archive historical documents, so that the codebase is more modular, easier to navigate, and adheres to standard repository conventions.

**Why this priority**: A clean separation of concerns is fundamental to a healthy codebase. It simplifies dependency management, clarifies the project architecture for new contributors, and improves long-term maintainability.

**Independent Test**: After the refactor, the top-level directory should contain distinct `backend/` and `frontend/` folders. The old `src/` directory should not exist. The root folder should be free of historical status files. The application must remain fully functional and all tests must pass.

**Acceptance Scenarios**:

1.  **Given** the project's file structure, **When** the refactoring is complete, **Then** a `backend/src/` directory exists containing the Python source code, a `backend/tests/` directory exists containing all test files, and a `frontend/` directory exists containing the Astro source following Astro's default conventions. The old `src/mcp_manager/` path must not exist.
2.  **Given** the project's root directory, **When** its contents are listed, **Then** historical status files (e.g., `PHASE2-COMPLETE.md`) are no longer present and have been moved to a `docs/archive/` directory.
3.  **Given** the refactored structure, **When** the test suite is run, **Then** all unit, integration, and contract tests pass successfully.
4.  **Given** the refactored structure, **When** the website is built via `npm run build`, **Then** it compiles successfully without path-related errors.

### Edge Cases

- **Dependency Update Failures**: If a dependency update introduces a breaking change that causes tests to fail, the failing dependency MUST be pinned to its previous working version in `pyproject.toml` or `package.json`. All other successful updates MUST be retained. A GitHub issue MUST be created to track the incompatible dependency for later resolution.
- **Essential vs Non-Essential Root Files**: Essential root-level files are those required by standard tooling when executing from the current working directory (CWD). This includes: README.md, LICENSE, pyproject.toml, package.json, .gitignore, AGENTS.md and its symlinks (CLAUDE.md, GEMINI.md), configuration files for tools (astro.config.mjs, tsconfig.json, etc.), and lock files (uv.lock, package-lock.json). All documentation files (*.md except README and LICENSE), historical status files, and spec artifacts belong in subdirectories.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST use `uv` for all Python dependency installation, management, and execution within scripts.
- **FR-002**: All project documentation and scripts MUST be updated to replace any `pip` commands with their `uv` equivalents.
- **FR-003**: A repeatable process or script MUST be created to check for outdated dependencies and apply updates.
- **FR-004**: All non-essential files and documents in the root directory MUST be moved to appropriate subdirectories (`specs/`, `docs/`, etc.). Essential files are limited to those required by standard tooling in CWD: README.md, LICENSE, pyproject.toml, package.json, .gitignore, AGENTS.md (and symlinks), tool configuration files, and lock files.
- **FR-005**: The `.gitignore` file MUST be reviewed to ensure it covers all temporary and local files generated by the development process.
- **FR-006**: The project structure MUST be refactored to: `backend/src/` for Python source code, `backend/tests/` for all test files, and `frontend/` for Astro application following Astro's default directory conventions. The `pyproject.toml` MUST use explicit package discovery: `packages = [{include = "mcp_manager", from = "backend/src"}]`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Python package management commands found in project scripts and documentation use `uv`.
- **SC-002**: The `uv pip list --outdated` and `npm outdated` commands report zero outdated packages after the update process is run.
- **SC-003**: The number of markdown files in the root directory is reduced to only include essential project-level files like `README.md`, `CHANGELOG.md`, `LICENSE`, and `AGENTS.md`.
- **SC-004**: A new contributor can successfully set up the development environment and run all verification checks using only the `uv`-based instructions in the `README.md`.