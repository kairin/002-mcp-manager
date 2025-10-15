# Tasks: Project Health and Standardization Audit (Modular & Automated)

**Input**: Design documents from `/home/kkk/Apps/002-mcp-manager/specs/005-we-ve-gone/`
**Prerequisites**: plan.md, spec.md, research.md

## Phase 1: Create Modular Audit Scripts

**Purpose**: Create individual, single-purpose scripts for each health check.

- [ ] T001 [P] Create the `pip` usage audit script at `scripts/audit/check_pip_usage.sh`.
- [ ] T002 [P] Create the dependency audit script at `scripts/audit/check_outdated.sh`.
- [ ] T003 [P] Create the root directory audit script at `scripts/audit/find_root_files.sh`.
- [ ] T004 [P] Create the MCP config audit script at `scripts/audit/check_mcp_configs.py`.

---

## Phase 2: Create the Orchestrator

**Purpose**: Create a single entry-point script to run all modular audits in sequence.

- [ ] T005 Create the orchestrator script `scripts/run_all_audits.sh`.
- [ ] T006 Implement the logic in the orchestrator to call each script from Phase 1, check its exit code, and fail immediately if any audit fails.
- [ ] T007 Make all scripts in `scripts/` executable with `chmod +x scripts/audit/*.sh scripts/run_all_audits.sh`.

---

## Phase 3: Integrate with Pre-Commit CI/CD

**Purpose**: Automate the entire audit process by integrating it into the existing local CI/CD pipeline.

- [ ] T008 Modify `.pre-commit-config.yaml` to add a new hook that executes the `scripts/run_all_audits.sh` orchestrator.

**Checkpoint**: The automated audit system is now in place. Subsequent phases will involve implementing the logic for each check, which will now be automatically enforced on every commit.

---

## Phase 4: Implement and Fix - `uv`-first Policy (US1)

**Goal**: Implement the logic for the `uv`-first check and fix any issues found.

- [ ] T009 [US1] In `scripts/audit/check_pip_usage.sh`, implement the `grep` logic to find `pip` usages. The script should exit with a non-zero code if any are found.
- [ ] T010 [US1] In `pyproject.toml`, add `[tool.uv]` and set `python = "3.11"` to enforce the system Python version.
- [ ] T011 [US1] Run `git commit` to trigger the pre-commit hook. It should fail if `pip` usages exist.
- [ ] T012 [US1] Based on the failure report, edit the identified files to replace `pip` with `uv` until the commit succeeds.

---

## Phase 5: Implement and Fix - Dependency Health (US2)

**Goal**: Implement the logic for the dependency health check.

- [ ] T013 [US2] In `scripts/audit/check_outdated.sh`, implement the logic to run `uv pip list --outdated` and `npm outdated`. The script should fail if outdated packages are found.
- [ ] T014 [US2] Run `git commit` and let the hook fail. Update dependencies in `pyproject.toml` and `package.json` as reported.
- [ ] T015 [US2] Run `uv pip sync` and `npm install`, then run the `pytest` suite to ensure no breaking changes.

---

## Phase 6: Refactor Project Structure for Maintainability (US3)

**Goal**: Physically separate the Python backend from the Astro frontend and archive historical documents.

**Independent Test**: The application builds and all tests pass after the file structure has been completely reorganized.

- [ ] T016 [US3] Create a new top-level `backend/` directory.
- [ ] T017 [US3] Create a new top-level `frontend/` directory.
- [ ] T018 [US3] Move the Python source code from `src/mcp_manager` to `backend/src/mcp_manager`.
- [ ] T019 [US3] Move the Astro source code (`src/components`, `src/layouts`, `src/pages`, etc.) to `frontend/src/`.
- [ ] T020 [US3] Move the `public/` directory into the `frontend/` directory.
- [ ] T021 [US3] Create a `docs/archive/` directory.
- [ ] T022 [US3] Move all historical status and completion `.md` files from the root directory into `docs/archive/`.
- [ ] T023 [US3] Update `astro.config.mjs` to point to the new `frontend/` directory as the project root (e.g., `root: './frontend'`).
- [ ] T024 [US3] Update `pyproject.toml` to correctly point to the new Python source directory under `backend/`.
- [ ] T025 [US3] Delete the now-empty `src/` directory.
- [ ] T026 [US3] Run `pytest` and `npm run build` to ensure all paths are correct and the application is fully functional after the refactor.

---

## Phase 7: Implement and Fix - MCP Config Audit (US4)

**Goal**: Implement the logic for the MCP configuration audit.

- [ ] T019 [US4] In `scripts/audit/check_mcp_configs.py`, implement the Python logic to parse MCP config files and check for known cross-platform issues.
- [ ] T020 [US4] Run `git commit` and let the hook fail. Manually fix any reported configuration errors.

---

## Phase 8: Polish & Documentation

- [ ] T021 Update `README.md` to document the new, automated project health checks that run on every commit.
