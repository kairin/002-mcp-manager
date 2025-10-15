# MCP Manager - Feature Implementation Order

**Created**: 2025-10-15
**Status**: ACTIVE - MANDATORY COMPLIANCE

## Critical Implementation Sequence

Features MUST be implemented in this order due to architectural dependencies:

### Phase 1: Project Restructure (FIRST - BLOCKING)
**Feature**: 001-project-restructure (originally 004-multi-cli-support)
**Branch**: `004-multi-cli-support` (original branch name preserved)
**Priority**: P0 (MUST complete before any other features)
**Reason**: Restructures entire project (`src/` → `backend/src/`). If done last, would break all previously implemented features.

**Deliverables**:
- Move `src/mcp_manager/` → `backend/src/mcp_manager/`
- Move `tests/` → `backend/tests/`
- Create `frontend/` structure
- Update `pyproject.toml` and create `backend/pyproject.toml`

**Validation Before Next Phase**:
```bash
cd /home/kkk/Apps/002-mcp-manager/backend
pytest tests/ -v
mcp-manager --help  # Should work from new location
```

---

### Phase 2: System Python Enforcement (SECOND)
**Feature**: 002-system-python-enforcement (originally 001-system-python-enforcement)
**Branch**: `001-system-python-enforcement` (original branch name preserved)
**Priority**: P1
**Dependencies**: Feature 001-project-restructure complete (needs `backend/` structure)

**Deliverables**:
- Create `backend/src/mcp_manager/python_env.py`
- Create `backend/src/mcp_manager/uv_config.py`
- Create `backend/src/mcp_manager/validators.py`
- Add `mcp-manager validate` command
- Create `uv.toml` at project root
- Update `pyproject.toml` to `requires-python = ">=3.13"`

**Validation Before Next Phase**:
```bash
mcp-manager validate --verbose  # Must PASS
uv python find  # Must return /usr/bin/python3.13
pytest backend/tests/ --cov=mcp_manager  # Coverage >80%
```

---

### Phase 3: MCP Manager Improvements (THIRD)
**Feature**: 003-mcp-improvements (originally 002-referencing-to-this)
**Branch**: `002-referencing-to-this` (original branch name preserved)
**Priority**: P2
**Dependencies**: Features 001 + 002 complete (needs `backend/` structure + Python 3.13 environment)

**Deliverables**:
- Update `backend/src/mcp_manager/core.py` (enhance MCP logic)
- Update `backend/src/mcp_manager/cli.py` (add `update`, `sync-gemini` commands)
- Create `backend/src/mcp_manager/gemini_integration.py`
- Enhanced MCP server management

**Validation After Completion**:
```bash
mcp-manager validate  # From Feature 001 - must still pass
mcp-manager update --all  # Feature 002 - must work
mcp-manager sync-gemini  # Feature 002 - must work
pytest backend/tests/ -v  # All tests pass
```

---

## Dependency Graph

```
┌──────────────────────────────────────────────────┐
│  Phase 1: Feature 004 (Project Restructure)      │
│  STATUS: Ready for implementation                │
│  FILES: Complete (spec.md, plan.md, tasks.md)    │
│  ⚠️  BLOCKING: Must complete before 001 or 002   │
└──────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│  Phase 2: Feature 001 (Python Enforcement)       │
│  STATUS: Ready for implementation                │
│  FILES: Complete (spec.md, plan.md, tasks.md)    │
│  DEPENDS ON: Feature 004 (backend/ structure)    │
└──────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│  Phase 3: Feature 002 (MCP Improvements)         │
│  STATUS: Ready for implementation                │
│  FILES: Complete (spec.md, plan.md, tasks.md)    │
│  DEPENDS ON: Features 004 + 001                  │
└──────────────────────────────────────────────────┘
```

## Why This Order?

### Original User Request
- Sequential implementation: 001 → 004

### Revised Recommendation
- Sequential implementation: 004 → 001 → 002

### Rationale for Change

**Feature 004 MUST be first** because:
1. Restructures project: `src/` → `backend/src/`, `tests/` → `backend/tests/`
2. If implemented after 001 or 002, would require rewriting all their code
3. Creates foundation that both 001 and 002 depend on

**Example of problem if 004 done last**:
```bash
# If we implement 001 first (creates files in src/mcp_manager/):
src/mcp_manager/python_env.py ✓ Created
src/mcp_manager/uv_config.py ✓ Created

# Then implement 004 (moves src/ → backend/src/):
backend/src/mcp_manager/python_env.py  # Must rewrite/move
backend/src/mcp_manager/uv_config.py   # Must rewrite/move
# All import paths change, tests break, wasted effort
```

**Correct sequence** (004 first):
```bash
# Implement 004 first:
backend/src/mcp_manager/ ✓ Structure created

# Then implement 001 (creates files in correct location):
backend/src/mcp_manager/python_env.py ✓ Created in final location
backend/src/mcp_manager/uv_config.py ✓ Created in final location
# No rework needed
```

## File Conflict Prevention

### High-Risk File: `backend/src/mcp_manager/cli.py`

All three features modify this file:

**Feature 004**: Moves `src/cli.py` → `backend/src/mcp_manager/cli.py`
**Feature 001**: Adds `validate` command
**Feature 002**: Adds `update` and `sync-gemini` commands

**Resolution Strategy**: Sequential implementation with namespace allocation
- Feature 004 establishes location
- Feature 001 adds `validate` (no conflict - new command)
- Feature 002 adds `update` + `sync-gemini` (no conflict - different commands)

✅ **NO CONFLICTS** if implemented sequentially

### Medium-Risk File: `pyproject.toml`

**Feature 004**: Creates `backend/pyproject.toml`
**Feature 001**: Updates `requires-python = ">=3.13"`
**Feature 002**: No changes

**Resolution**: Feature 001 updates to `>=3.13` after 004 restructures

## Feature Status Matrix

| Feature | Folder | Spec | Plan | Tasks | Ready | Order |
|---------|--------|------|------|-------|-------|-------|
| 004 | specs/001-project-restructure | ✓ | ✓ | ✓ | ✅ | **1st** |
| 001 | specs/002-system-python-enforcement | ✓ | ✓ | ✓ | ✅ | **2nd** |
| 002 | specs/003-mcp-improvements | ✓ | ✓ | ✓ | ✅ | **3rd** |
| 003 | specs/999-archived-duplicate | ✓ | ✓ | ✓ | ❌ | **ARCHIVED** |

## Archived Features

**Feature 003 (original 003-system-python-enforcement)** - DUPLICATE:
- **Status**: ARCHIVED (not for implementation)
- **Reason**: Duplicate of original 001-system-python-enforcement (now 002-system-python-enforcement)
- **Location**: `specs/999-archived-duplicate/`
- **Action**: Files deleted (incorporated into Feature 002-system-python-enforcement)

## Implementation Checklist

- [ ] **Phase 1**: Implement Feature 004 (Project Restructure)
  - [ ] Follow `specs/001-project-restructure/tasks.md`
  - [ ] Validate: `pytest backend/tests/ -v`
  - [ ] Validate: `mcp-manager --help` works
  - [ ] Merge to main, preserve branch

- [ ] **Phase 2**: Implement Feature 001 (System Python Enforcement)
  - [ ] Prerequisite: Feature 004 merged and validated
  - [ ] Follow `specs/002-system-python-enforcement/tasks.md`
  - [ ] Validate: `mcp-manager validate --verbose` passes
  - [ ] Validate: `uv python find` returns system Python 3.13
  - [ ] Merge to main, preserve branch

- [ ] **Phase 3**: Implement Feature 002 (MCP Improvements)
  - [ ] Prerequisite: Features 004 + 001 merged and validated
  - [ ] Follow `specs/003-mcp-improvements/tasks.md`
  - [ ] Validate: `mcp-manager update --all` works
  - [ ] Validate: All previous commands still work
  - [ ] Merge to main, preserve branch

## Cross-Feature Integration Tests

After ALL features complete, run:

```bash
# Verify all commands work together
mcp-manager --help
mcp-manager validate --verbose
mcp-manager audit
mcp-manager update --all
mcp-manager sync-gemini

# Verify test coverage maintained
cd backend
pytest tests/ -v --cov=mcp_manager
# Must maintain >80% coverage

# Verify Python 3.13 enforcement active
uv python find  # Must return /usr/bin/python3.13
```

---

**CRITICAL**: Do NOT deviate from this implementation order. Feature 004 MUST be completed first, or Features 001 and 002 will require complete rewrites.

**Last Updated**: 2025-10-15
**Status**: ACTIVE - MANDATORY COMPLIANCE
**Review**: Required before starting any implementation
