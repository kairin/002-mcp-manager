# MCP Manager with Local CI/CD Constitution

## Core Principles

### I. Modular-First Design (PRIMARY PRINCIPLE)
Every feature MUST be independently buildable, testable, and deployable with clear separation of concerns.

**Requirements**:
- Each module (website, TUI, scripts) must be self-contained
- Modules must have clear, well-defined interfaces
- Changes to one module must not break others
- NO unnecessary files - every file must serve a clear purpose
- Directory structure must reflect module boundaries

**Rationale**: Ensures long-term maintainability, reduces complexity, and aligns with user's explicit requirement for modularity and simplicity.

### II. Local-First CI/CD
All CI/CD processes MUST execute locally before pushing to remote repositories to minimize GitHub Actions costs.

**Requirements**:
- Single command to run entire CI/CD pipeline locally
- Local CI/CD output must be identical to GitHub Actions output
- Remote repository only executes deployment actions, not CI/CD
- 100% of checks (linting, testing, building) run locally

**Rationale**: Cost optimization - avoid GitHub Actions charges for CI/CD while maintaining quality gates.

### III. Structured Observability
All processes MUST provide structured logging with step-by-step progress, timestamps, and machine-parseable output.

**Requirements**:
- JSON format for logs to enable debugging and monitoring
- Clear error messages with actionable guidance
- Warnings and errors must be surfaced immediately
- Logs must include timestamps and context

**Rationale**: Enables effective debugging, monitoring, and troubleshooting of local CI/CD processes.

### IV. Security by Default
Secrets and sensitive data MUST be protected through automated validation and enforcement.

**Requirements**:
- Use `.env` files with `.gitignore` patterns for secrets
- Pre-commit hooks MUST block commits containing secrets
- Validation must identify offending files/lines
- NO secrets or API keys committed to repository

**Rationale**: Prevent accidental exposure of credentials and API keys in version control.

### V. Test Coverage Completeness
CI/CD pipeline MUST include comprehensive test coverage across all layers.

**Requirements**:
- Unit tests for individual components
- Integration tests for module interactions
- End-to-end tests for complete workflows
- Tests must pass before code can be pushed

**Rationale**: Ensures quality and prevents regressions, especially critical when CI/CD runs locally.

## Quality Attributes

### Performance Standards
- Astro website page load: < 1.5 seconds on 3G (95% of scenarios)
- Lighthouse Performance score: > 90
- Local CI/CD pipeline completion: < 5 minutes for typical changes

### Deployment Standards
- Automatic rollback on deployment failure
- Notification to developer via log file on rollback
- Last known good deployment must be preserved

### Developer Experience
- Setup and run local CI/CD pipeline: < 10 minutes
- New developer module comprehension: < 30 minutes
- TUI must provide clear options without requiring flag memorization

## Technology Constraints

### Required Stack
- Astro.build for website
- GitHub Pages for hosting
- Node.js and npm for build tooling
- Environment-specific configuration files (`.env.local`, `.env.production`)

### Prohibited Practices
- Hardcoded credentials or secrets
- Unnecessary file proliferation
- Tightly coupled modules
- Remote CI/CD for quality gates (deployment only)

## Development Workflow

### Local CI/CD Execution
1. Developer makes commits locally
2. Run local CI/CD script (single command)
3. Pipeline executes: linting → testing → building
4. On failure: attempt auto-fix (e.g., `prettier --write`), else exit non-zero
5. On success: push to remote repository
6. Remote: deployment action only (no CI/CD)

### Module Development
1. Identify module boundaries clearly
2. Implement with clear separation of concerns
3. Test module independently
4. Ensure no cross-module dependencies

### Secrets Management
1. Store secrets in `.env` files (gitignored)
2. Pre-commit hook validates no secrets in commits
3. Use environment-specific configs for different environments

## Governance

This constitution supersedes all other development practices and guidelines. All code reviews, pull requests, and feature implementations MUST verify compliance with these principles.

**Complexity Justification**: Any deviation from simplicity or addition of files/dependencies must be explicitly justified and approved.

**Amendment Process**: Changes to this constitution require documentation of rationale, approval, and migration plan for existing code.

**Version**: 1.0.0 | **Ratified**: 2025-10-19 | **Last Amended**: 2025-10-19
