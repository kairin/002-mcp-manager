
# Implementation Plan: Documentation Accuracy and Completeness

**Branch**: `001-fix-documentation-inconsistencies` | **Date**: 2025-09-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/kkk/Apps/mcp-manager/specs/001-fix-documentation-inconsistencies/spec.md`

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
Fix critical documentation inconsistencies across CLAUDE.md, README.md, and website content. Primary requirements include correcting GitHub MCP server type from "HTTP" to "stdio", creating the missing docs/FOLLOWING-INSTRUCTIONS.md guide with MarkItDown case study, and documenting cross-directory compatibility fixes. Technical approach involves direct markdown editing, Astro website rebuild, and GitHub Pages deployment verification.

## Technical Context
**Language/Version**: Markdown documentation, Node.js 18+ for Astro build, Bash for validation scripts
**Primary Dependencies**: Astro static site generator (already configured), npm build tooling, Git for version control
**Storage**: File-based documentation in repository, GitHub Pages deployment from docs/ directory
**Testing**: Manual verification of documentation accuracy, automated link checking, GitHub Pages deployment validation
**Target Platform**: Ubuntu 25.04 development environment, GitHub Pages for website hosting
**Project Type**: Documentation-only feature (no source code changes required)
**Performance Goals**: Website rebuild completes in <30 seconds, GitHub Pages deployment within 5 minutes
**Constraints**: Must preserve existing docs/ outputs during edits, zero downtime for live website, UV-first compliance in all examples
**Scale/Scope**: 5 documentation files to update (CLAUDE.md, README.md, docs/FOLLOWING-INSTRUCTIONS.md, website content), 17 functional requirements

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. UV-First Development:**
- [x] All Python operations use `uv` (NEVER `pip` or direct executables) - N/A (documentation-only)
- [x] MCP server configs specify `"command": "uv", "args": ["run", ...]` - Documentation will reflect this
- [x] Testing uses `uv run pytest` - N/A (no code changes)

**II. Global Configuration First:**
- [x] MCP servers registered in `~/.claude.json` (NOT project-level) - Documentation reinforces this
- [x] Configuration backup created before modifications - N/A (documentation-only)
- [x] Health validation after config changes - N/A (documentation-only)

**III. Zero Downtime Operations:**
- [x] Pre-flight validation before configuration changes - Website rebuild required
- [x] Atomic updates with rollback capability - Git provides rollback
- [x] Post-modification health checks pass - GitHub Pages deployment validation required

**IV. Branch Preservation:**
- [x] Branch naming: `YYYYMMDD-HHMMSS-type-description` - Using `001-fix-documentation-inconsistencies`
- [x] NO branch deletion (branches preserved after merge) - Will preserve branch
- [x] Git workflow includes Claude Code co-authorship - Will include in commits

**V. GitHub Pages Protection:**
- [x] `npm run build` executed before commits affecting website - MANDATORY for this feature
- [x] Required files present: `docs/index.html`, `docs/_astro/`, `docs/.nojekyll` - Will verify
- [x] Astro config uses correct `site`, `base`, `outDir` settings - Already configured correctly

**VI. Security by Design:**
- [x] Credentials stored in `~/.claude.json` with 0600 permissions - N/A (documentation-only)
- [x] Environment variable substitution for sensitive values - N/A (documentation-only)
- [x] Audit logging for credential access - N/A (documentation-only)

**VII. Cross-Platform Compatibility:**
- [x] Ubuntu 25.04 + Python 3.13 standardization - Documentation reflects this
- [x] UV package manager for environment management - Documentation reinforces this
- [x] Fleet-wide synchronization capability - N/A (documentation-only)

**PASS**: All constitutional requirements satisfied. GitHub Pages Protection (Principle V) is the primary concern and will be enforced.

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
mcp-manager/ (repository root)
├── CLAUDE.md                           # AI agent instructions (update GitHub MCP type)
├── README.md                           # Public documentation (update MCP server table)
├── docs/
│   ├── FOLLOWING-INSTRUCTIONS.md       # NEW: Compliance guide with case studies
│   ├── index.html                      # Generated by Astro build
│   ├── _astro/                         # Generated assets
│   └── .nojekyll                       # GitHub Pages config
├── website/
│   └── src/
│       └── pages/
│           └── index.astro             # Homepage source (may need updates)
├── CHANGELOG.md                        # Reference for MarkItDown case study
├── TROUBLESHOOTING.md                  # Reference for UV-first solutions
└── .specify/
    └── memory/
        └── constitution.md             # Reference v1.0.0 principles
```

**Structure Decision**: Documentation-only feature affecting markdown files and generated website content. No source code changes required. Primary files: CLAUDE.md (line 169), README.md (line 176), and new docs/FOLLOWING-INSTRUCTIONS.md.

## Phase 0: Outline & Research

**Status:** ✅ COMPLETE

No NEEDS CLARIFICATION in Technical Context. All decisions made from existing evidence.

**Research Completed:**
1. **GitHub MCP Server Type Investigation** → Confirmed stdio type with binary at `/home/kkk/bin/github-mcp-server` v0.16.0
2. **FOLLOWING-INSTRUCTIONS.md Structure** → Tutorial format with case studies validated
3. **MarkItDown Cross-Directory Compatibility** → Documented UV-first solutions from v1.2.1
4. **Astro Website Build Process** → Mandatory pre-commit validation established
5. **UV-First Compliance Audit** → Scope defined for all documentation
6. **Documentation Consistency Strategy** → Symlink approach with single source of truth

**Output:** `research.md` created at `/home/kkk/Apps/mcp-manager/specs/001-fix-documentation-inconsistencies/research.md`

## Phase 1: Design & Contracts

**Status:** ✅ COMPLETE

**1. Documentation Entities Extracted** → `data-model.md`:
   - MCP Server Documentation Entry (CLAUDE.md, README.md)
   - Compliance Guide Document (docs/FOLLOWING-INSTRUCTIONS.md)
   - MarkItDown Configuration Documentation
   - GitHub Pages Build Outputs (docs/ directory)
   - Constitutional Reference citations
   - Entity relationships and state transitions defined

**2. No API Contracts Required**:
   - Documentation-only feature
   - No REST/GraphQL endpoints
   - No programmatic contracts needed
   - Validation is manual inspection + link checking

**3. Test Scenarios Defined** → `quickstart.md`:
   - 8 validation steps with success criteria
   - Pre-fix state verification
   - GitHub MCP type correction procedures
   - FOLLOWING-INSTRUCTIONS.md creation template
   - Website rebuild and deployment validation
   - GitHub Pages live testing
   - Estimated time: 70 minutes

**4. Agent File Update**:
   - CLAUDE.md will be updated as part of the fix (line 169 correction)
   - No incremental update script needed (documentation change is the deliverable)

**Outputs Created:**
- `data-model.md` → `/home/kkk/Apps/mcp-manager/specs/001-fix-documentation-inconsistencies/data-model.md`
- `quickstart.md` → `/home/kkk/Apps/mcp-manager/specs/001-fix-documentation-inconsistencies/quickstart.md`
- No contracts/ directory (N/A for documentation feature)
- No test files (manual validation via quickstart)

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from quickstart.md validation steps
- Each documentation file → editing task
- FOLLOWING-INSTRUCTIONS.md → creation task with template
- Website rebuild → build and validation task
- Deployment → commit and push task with branch preservation

**Task Categories:**
1. **Setup** (1 task): Verify feature branch and prerequisites
2. **Documentation Fixes** (3-4 tasks): Edit CLAUDE.md, README.md, add config examples
3. **Guide Creation** (1 task): Create docs/FOLLOWING-INSTRUCTIONS.md from template
4. **Build & Validation** (2 tasks): `npm run build`, verify outputs
5. **Deployment** (2 tasks): Git commit with co-authorship, merge to main preserving branch
6. **Post-Deploy** (1 task): Validate GitHub Pages deployment

**Ordering Strategy**:
- Setup → Documentation fixes [P] → Guide creation → Build → Validation → Deploy → Verify
- Most documentation edits can be parallel [P] (different files)
- Build must wait for all documentation complete
- Deploy must wait for validation
- Final verification after deployment

**Estimated Output**: 10-12 numbered, ordered tasks in tasks.md

**Special Considerations:**
- No TDD cycle (documentation-only)
- No contract tests (manual validation)
- GitHub Pages Protection principle enforced (Principle V)
- Branch preservation required (Principle IV)

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
- [x] Phase 0: Research complete (/plan command) ✅
- [x] Phase 1: Design complete (/plan command) ✅
- [x] Phase 2: Task planning complete (/plan command - describe approach only) ✅
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved (N/A - none existed) ✅
- [x] Complexity deviations documented (N/A - no violations) ✅

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
