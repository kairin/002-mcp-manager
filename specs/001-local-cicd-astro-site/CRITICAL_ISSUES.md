# Critical Repository Issues Identified (2025-10-19)

## Executive Summary

During the planning review, **5 critical issues** were identified that violate the constitution and spec requirements. These MUST be addressed during implementation.

---

## CRITICAL Issue #1: Local CI Script Violates Multiple Requirements

**File**: `scripts/local-ci/run.sh`
**Severity**: 🚨 BLOCKER

### Problems:

1. **No Structured Logging** (Violates FR-010, Constitution Principle III)
   - Uses simple `echo` statements instead of JSON logging
   - No timestamps
   - No machine-parseable format
   - Cannot track progress or debug effectively

2. **No Auto-Fix on Failure** (Violates Clarification #1, Edge Case)
   - Does not attempt `prettier --write` on lint failure
   - Does not provide non-zero exit code handling

3. **Hardcoded Paths** (Violates Best Practices)
   - Repeats `cd web &&` on every line
   - Not modular or maintainable

4. **Missing Error Handling**
   - No check if commands succeed
   - No rollback mechanism
   - No validation that tests exist before running

### Required Fix:
Rewrite `scripts/local-ci/run.sh` to:
- Use JSON logging with timestamps
- Implement auto-fix (prettier --write) before failing
- Proper error handling and exit codes
- Modular structure
- Duration tracking for NFR-003 (< 5 min completion)

---

## CRITICAL Issue #2: Missing Pre-Commit Hook

**Severity**: 🚨 BLOCKER (Security)

### Problem:
No pre-commit hook exists to validate secrets/API keys before commits.

**Violates**:
- FR-009: Pre-commit hook validation MUST block secrets
- Constitution Principle IV: Security by Default
- Edge Case: Block commits with secrets

### Impact:
- Risk of accidental credential exposure
- No enforcement of security policy
- Constitution violation

### Required Fix:
Create `.git/hooks/pre-commit` (or `.husky/pre-commit`) that:
- Scans for common secret patterns (API keys, tokens, passwords)
- Validates `.env` files are gitignored
- Blocks commit if secrets detected
- Displays clear error with offending files/lines

---

## CRITICAL Issue #3: web/ Directory Structure Violates Modular-First

**Severity**: 🔴 HIGH

### Problem:
`/home/kkk/Apps/002-mcp-manager/web/web/` directory exists (nested web/web)

This indicates:
- Unclear directory structure
- Potential file duplication
- Violation of FR-005 (NO unnecessary files)
- Violation of Constitution Principle I (clear module boundaries)

### Investigation Needed:
```bash
ls -la /home/kkk/Apps/002-mcp-manager/web/web/
```

### Required Fix:
- Remove redundant nested directories
- Clarify if this is build artifact or structural error
- Update .gitignore if build artifact

---

## CRITICAL Issue #4: Test Infrastructure Missing Components

**Severity**: 🔴 HIGH

### Problem:
`/home/kkk/Apps/002-mcp-manager/web/src/tests/` exists but scripts reference different paths:

**Script says**: `cd web && npx mocha src/tests/*.test.js`
**Actual path**: `/web/src/tests/` (exists)
**Also exists**: `/web/tests/` (separate top-level)

This causes:
- Test discovery failure
- Unclear test organization
- Violates modular-first (unclear boundaries)

### Required Fix:
- Consolidate test directories (choose ONE location)
- Update CI script to match actual structure
- Document test organization in data-model.md

---

## CRITICAL Issue #5: Missing Environment Configuration Files

**Severity**: 🟡 MEDIUM

### Problem:
No `.env.local`, `.env.production`, `.env.example` files exist.

**Violates**:
- Clarification #2: Different configs for environments
- FR-009: `.env` files for secrets management
- Best practices for Astro + GitHub Pages

### Required Fix:
Create:
1. `.env.example` (template, safe to commit)
2. `.env.local` (local development, gitignored)
3. `.env.production` (production settings, gitignored)
4. Document required environment variables

---

## MODERATE Issue #6: TUI Not Implemented

**Severity**: 🟡 MEDIUM

### Problem:
`scripts/tui/run.sh` exists but TUI functionality not implemented per FR-006.

**Violates**:
- FR-006: MUST include TUI for easy app running
- User requirement: "options available without remembering flags"

### Required Fix:
Implement TUI in Phase 2 implementation (not blocking for plan)

---

## MODERATE Issue #7: No GitHub Actions Workflow

**Severity**: 🟡 MEDIUM

### Problem:
`.github/` directory exists but no deployment workflow defined.

**Violates**:
- FR-002: Website MUST be deployable to GitHub Pages
- FR-011: Deployment rollback capability required

### Required Fix:
Create `.github/workflows/deploy.yml` with:
- Trigger on push to main (after local CI passes)
- Deploy to GitHub Pages
- Rollback on failure
- Notification to developer

---

## Summary Table

| Issue | Severity | Violates | Blocks Planning? |
|-------|----------|----------|-----------------|
| #1: CI Script | 🚨 BLOCKER | FR-010, Principle III | No, but must document |
| #2: Pre-commit Hook | 🚨 BLOCKER | FR-009, Principle IV | No, but must document |
| #3: web/web/ Nested Dir | 🔴 HIGH | FR-005, Principle I | Needs investigation |
| #4: Test Paths Mismatch | 🔴 HIGH | Test requirements | Impacts data-model |
| #5: Missing .env Files | 🟡 MEDIUM | FR-009, Clarification #2 | No |
| #6: TUI Not Implemented | 🟡 MEDIUM | FR-006 | No (Phase 2) |
| #7: No Deploy Workflow | 🟡 MEDIUM | FR-002, FR-011 | No |

---

## Recommendation

**Proceed with planning** BUT:

1. Document all issues in `plan.md` Complexity Tracking section
2. Create research tasks for #3 (investigate web/web/)
3. Include fixes in Phase 2 tasks generation
4. Flag as constitution violations requiring justification/remediation

**Next Step**: Fill Technical Context in plan.md with these findings integrated.
