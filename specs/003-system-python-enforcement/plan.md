
# Implementation Plan: System Python 3.13 Enforcement

**Branch**: `003-system-python-enforcement` | **Date**: 2025-10-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/kkk/Apps/002-mcp-manager/specs/003-system-python-enforcement/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Enforce Python 3.13 system Python exclusively across all mcp-manager operations to eliminate version bloat, ensure fleet consistency, and maintain constitutional compliance. UV package manager will manage all dependencies while preventing additional Python interpreter installations. Implementation includes validation commands, pre-commit hooks, MCP server configuration updates, and constitution compliance checkers.

## Technical Context
**Language/Version**: Python 3.13 (system Python, MANDATORY per Constitution v1.2.0 Principle VII)
**Primary Dependencies**: UV (package manager), Typer (CLI), Rich (output), Pydantic v2 (validation), pytest (testing)
**Storage**: N/A (validation state only, ephemeral)
**Testing**: pytest via `uv run pytest` (MANDATORY, never direct pytest)
**Target Platform**: Ubuntu 25.04 fleet nodes (standardized environment)
**Project Type**: Single project (Python CLI tool with validation utilities)
**Performance Goals**:
- Python version validation: <100ms
- UV configuration checks: <50ms
- Constitution compliance validation: <200ms
- CLI command overhead from UV: <50ms additional latency
**Constraints**:
- MUST use system Python 3.13 (zero additional Python installations)
- MUST prevent UV from auto-downloading Python interpreters
- MUST maintain backward compatibility with existing MCP configurations
- MUST not break current CLI workflows
**Scale/Scope**:
- Fleet: 174+ discovered agents across multiple nodes
- MCP servers: 6 active servers (context7, shadcn, github, playwright, hf-mcp-server, markitdown)
- Validation scope: pyproject.toml, UV config, MCP server configs, CLI execution paths
- Pre-commit hook integration: all commits validated

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. UV-First Development:**
- [x] All Python operations use `uv` (NEVER `pip` or direct executables) - Core feature requirement
- [x] MCP server configs specify `"command": "uv", "args": ["run", ...]` - Validation enforced
- [x] Testing uses `uv run pytest` - FR-013 requirement

**II. Global Configuration First:**
- [x] MCP servers registered in `~/.claude.json` (NOT project-level) - No project-level changes
- [x] Configuration backup created before modifications - Part of core.py integration
- [x] Health validation after config changes - Constitution validator checks this

**III. Zero Downtime Operations:**
- [x] Pre-flight validation before configuration changes - Python validator runs before operations
- [x] Atomic updates with rollback capability - Validator failures prevent operations
- [x] Post-modification health checks pass - Constitution compliance validation post-change

**IV. Branch Preservation:**
- [x] Branch naming: `YYYYMMDD-HHMMSS-type-description` - Branch created as 003-system-python-enforcement
- [x] NO branch deletion (branches preserved after merge) - Constitutional requirement respected
- [x] Git workflow includes Claude Code co-authorship - Standard practice

**V. GitHub Pages Protection:**
- [x] `npm run build` executed before commits affecting website - Not applicable (backend-only feature)
- [x] Required files present: `docs/index.html`, `docs/_astro/`, `docs/.nojekyll` - No website changes
- [x] Astro config uses correct `site`, `base`, `outDir` settings - Not affected

**VI. Security by Design:**
- [x] Credentials stored in `~/.claude.json` with 0600 permissions - No credential changes
- [x] Environment variable substitution for sensitive values - Not applicable
- [x] Audit logging for credential access - Not applicable (validation-only feature)

**VII. Cross-Platform Compatibility:**
- [x] Ubuntu 25.04 + Python 3.13 system Python (zero bloat strategy) - **PRIMARY FEATURE GOAL**
- [x] UV package manager with mandatory `[tool.uv] python = "python3.13"` configuration - **ENFORCED BY VALIDATORS**
- [x] Fleet-wide synchronization capability - FR-015 fleet verification

**VIII. Repository Organization:**
- [x] Files organized in structured directories (no root clutter) - New validators/ directory, scripts/verify/ placement
- [x] Documentation in `docs/`, scripts in `scripts/{setup,verify,deployment,legacy}` - verify_python_enforcement.py in scripts/verify/
- [x] File placement validation automated in pre-commit hooks - FR-011 pre-commit hook integration

**IX. Multi-Agent Support:**
- [x] MCP configurations synchronized for Claude Code (`~/.claude.json`) - MCP server validation includes Claude
- [x] MCP configurations synchronized for Gemini CLI (`~/.config/gemini/settings.json`) - Validation applies to both
- [x] Agent instructions consolidated in `AGENTS.md` with symlinks (CLAUDE.md, GEMINI.md) - No changes to agent instructions

**Constitution Check Result**: ✅ **PASS** - All principles satisfied. This feature directly implements Principle VII enforcement.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/mcp_manager/
├── cli/
│   └── validate_commands.py     # New: Python version validation CLI commands
├── validators/                   # New: Validation subsystem
│   ├── __init__.py
│   ├── python_validator.py      # System Python 3.13 checker
│   ├── uv_validator.py          # UV configuration validator
│   └── constitution_validator.py # Constitution compliance checker
├── models/
│   └── validation_models.py     # New: Pydantic models for validation results
├── exceptions.py                # Extend with validation-specific exceptions
└── core.py                      # Extend with constitution compliance methods

tests/
├── contract/
│   └── test_validation_api.py   # New: Validation command contracts
├── integration/
│   ├── test_python_enforcement.py   # End-to-end Python 3.13 validation
│   ├── test_uv_integration.py      # UV + system Python integration
│   └── test_mcp_server_launch.py   # MCP servers via UV validation
└── unit/
    ├── test_python_validator.py    # Unit tests for Python validator
    ├── test_uv_validator.py        # Unit tests for UV validator
    └── test_constitution_validator.py # Unit tests for constitution validator

scripts/verify/
└── verify_python_enforcement.py # New: Standalone verification utility

.pre-commit-config.yaml          # Update: Add Python version validation hook
pyproject.toml                   # Already updated: requires-python >=3.13, [tool.uv]
```

**Structure Decision**: Single project structure (Option 1). This feature extends the existing mcp-manager CLI with new validation subsystems. New components are added to `src/mcp_manager/validators/` to maintain separation of concerns. CLI commands are extended in `cli/validate_commands.py`. Tests follow TDD approach with contract tests defining interfaces before implementation.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- **CLI contracts** → 4 contract test tasks [P] (validate python, validate uv, validate mcp-servers, validate constitution)
- **Data models** → 6 entity creation tasks [P] (PythonVersionInfo, UVConfiguration, MCPServerConfig, ValidationResult, ConstitutionCheckResult, PythonEnforcementStatus)
- **Validators** → 3 validator implementation tasks (python_validator.py, uv_validator.py, constitution_validator.py)
- **CLI commands** → 1 CLI integration task (validate_commands.py)
- **Pre-commit** → 1 pre-commit hook task (.pre-commit-config.yaml update)
- **User stories** → 5 integration test tasks (matching acceptance scenarios from spec.md)
- **Verification** → 1 standalone utility task (scripts/verify/verify_python_enforcement.py)

**Ordering Strategy**:
- **TDD order**: Contract tests → Models → Validators → CLI → Integration tests
- **Dependency order**:
  1. Contract tests (define interfaces) - ALL [P]
  2. Data models (no dependencies) - ALL [P]
  3. Core validators (depend on models)
  4. Constitution validator (depends on core validators)
  5. CLI commands (depend on all validators)
  6. Pre-commit hook (depends on CLI)
  7. Integration tests (validate end-to-end)
  8. Verification utility (standalone, [P] with tests)
- **Parallelization**: Mark [P] for independent files (contracts, models, standalone utilities)

**Estimated Task Breakdown** (28 total tasks):
- **Setup**: 2 tasks (directory structure, exception classes)
- **Contract Tests**: 4 tasks [P] (one per CLI command)
- **Models**: 6 tasks [P] (one per entity)
- **Validators**: 3 tasks (sequential, depend on models)
- **CLI Integration**: 1 task (depends on validators)
- **Pre-commit Hook**: 1 task (depends on CLI)
- **Unit Tests**: 3 tasks [P] (one per validator)
- **Integration Tests**: 5 tasks [P] (one per acceptance scenario)
- **Verification Utility**: 1 task [P] (standalone)
- **Documentation**: 1 task (update TROUBLESHOOTING.md)
- **Final Validation**: 1 task (run quickstart.md)

**Critical Path** (non-parallel tasks):
1. Models → Validators → CLI → Pre-commit → Validation

**Estimated Output**: 28 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md created
- [x] Phase 1: Design complete (/plan command) - data-model.md, contracts/, quickstart.md, AGENTS.md updated
- [x] Phase 2: Task planning complete (/plan command - describe approach only) - 28 tasks estimated
- [ ] Phase 3: Tasks generated (/tasks command) - Ready for /tasks
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS - All 9 principles satisfied
- [x] Post-Design Constitution Check: PASS - No new violations introduced
- [x] All NEEDS CLARIFICATION resolved - No unknowns in Technical Context
- [x] Complexity deviations documented - No deviations (Complexity Tracking empty)

---
*Based on Constitution v1.2.0 - See `.specify/memory/constitution.md`*
