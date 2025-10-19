# Tasks: Local CI/CD for Astro Site

**Input**: Design documents from `/home/kkk/Apps/002-mcp-manager/specs/001-local-cicd-astro-site/`
**Prerequisites**: plan.md, spec.md

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Create project structure per implementation plan (`scripts/tui`, `scripts/local-ci`, `web`)
- [X] T002 [P] Initialize Astro.js project in `web/`
- [X] T003 [P] Initialize TUI project in `scripts/tui/`
- [X] T004 [P] Create local CI/CD script in `scripts/local-ci/run.sh`

---

## Phase 2: User Story 1 - Local CI/CD Execution (Priority: P1) 🎯 MVP

**Goal**: As a developer, I want to run all CI/CD processes locally before pushing to the remote repository, so that I can avoid incurring additional charges on GitHub Actions.

**Independent Test**: A developer can run a single command to execute the entire CI/CD pipeline locally. The output of the local run should be identical to what a GitHub Actions runner would produce.

### Implementation for User Story 1

- [X] T005 [US1] Implement linting in `scripts/local-ci/run.sh`
- [X] T006 [US1] Implement unit testing in `scripts/local-ci/run.sh`
- [X] T007 [US1] Implement Astro site build in `scripts/local-ci/run.sh`

---

## Phase 3: User Story 2 - Modular Implementation (Priority: P2)

**Goal**: As a developer, I want the implementation to be modular, with a clear separation between the website, the TUI, and other scripts, so that the project is simple and easy to maintain.

**Independent Test**: The website, TUI, and scripts can be developed and tested independently of each other.

### Implementation for User Story 2

- [X] T008 [US2] Implement TUI in `scripts/tui/` to present options for running the app
- [X] T009 [US2] Ensure the TUI can trigger the local CI/CD script
- [X] T010 [US2] Ensure the TUI can start the Astro development server

---

## Phase 4: User Story 3 - Astro.build Website on GitHub Pages (Priority: P3)

**Goal**: As a project owner, I want to have a website built with Astro.build and hosted on GitHub Pages, so that I can have a fast and modern web presence for free.

**Independent Test**: The website can be built and deployed to GitHub Pages.

### Implementation for User Story 3

- [X] T011 [US3] Create a basic Astro.js website in `web/` with a few pages and components
- [X] T012 [US3] Configure Astro.js for deployment to GitHub Pages
- [X] T013 [US3] Create a GitHub Actions workflow to deploy the website from the `web/dist` directory

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T014 [P] Add documentation for the TUI
- [X] T015 [P] Add documentation for the local CI/CD script
- [X] T016 [P] Add documentation for the website

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** must be completed before any other phase.
- **Phase 2 (User Story 1)** can be completed independently.
- **Phase 3 (User Story 2)** depends on Phase 2.
- **Phase 4 (User Story 3)** can be completed independently.
- **Phase 5 (Polish)** can be done at any time after the relevant features are complete.

## Parallel Opportunities

- Within Phase 1, T002, T003, and T004 can be done in parallel.
- Within Phase 5, T014, T015, and T016 can be done in parallel.

## Implementation Strategy

### MVP First (User Story 1 Only)

1.  Complete Phase 1: Setup
2.  Complete Phase 2: User Story 1
3.  **STOP and VALIDATE**: Test User Story 1 independently

### Incremental Delivery

1.  Complete Setup
2.  Add User Story 1 → Test independently
3.  Add User Story 3 → Test independently
4.  Add User Story 2 → Test independently
