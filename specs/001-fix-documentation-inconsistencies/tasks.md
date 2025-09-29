# Tasks: Documentation Accuracy and Completeness

**Input**: Design documents from `/home/kkk/Apps/mcp-manager/specs/001-fix-documentation-inconsistencies/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Task Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- Repository root: `/home/kkk/Apps/mcp-manager`
- Documentation files: `CLAUDE.md`, `README.md`, `docs/FOLLOWING-INSTRUCTIONS.md`
- Website source: `website/src/`
- Build output: `docs/`

## Phase 3.1: Setup & Verification

- [ ] T001 Verify feature branch `001-fix-documentation-inconsistencies` checked out and working directory clean
- [ ] T002 Verify prerequisite tools: Node.js 18+, Git configured, npm installed

## Phase 3.2: Pre-Fix Verification (Document Current State)

- [ ] T003 [P] Verify GitHub MCP type shows "HTTP" in CLAUDE.md line ~169
- [ ] T004 [P] Verify GitHub MCP type shows "HTTP" in README.md line ~176
- [ ] T005 Verify docs/FOLLOWING-INSTRUCTIONS.md does NOT exist (confirm missing file)

## Phase 3.3: Documentation Corrections

- [ ] T006 [P] Edit CLAUDE.md: Change GitHub MCP server type from "HTTP" to "stdio" in MCP server table (line ~169)
- [ ] T007 [P] Edit README.md: Change GitHub MCP server type from "HTTP" to "stdio" in MCP server table (line ~176)
- [ ] T008 [P] Add GitHub MCP configuration example to CLAUDE.md:
  ```json
  "github": {
    "type": "stdio",
    "command": "github-mcp-server",
    "args": []
  }
  ```
  Binary location: `/home/kkk/bin/github-mcp-server` v0.16.0
- [ ] T009 Add GitHub MCP configuration example to README.md (same as T008)

## Phase 3.4: Compliance Guide Creation

- [ ] T010 Create docs/FOLLOWING-INSTRUCTIONS.md with complete content including:
  - Introduction explaining why AGENTS.md compliance matters
  - Constitutional Foundation section referencing v1.0.0
  - Case Study 1: MarkItDown MCP Integration from CHANGELOG.md v1.2.1
  - Case Study 2: GitHub MCP Configuration Evolution
  - Best Practices for MCP Server Integration
  - Troubleshooting Common Issues with UV-first solutions
  - Validation checklist
  - Use template from quickstart.md Step 3b

## Phase 3.5: Website Build & Validation

- [ ] T011 Run `npm run clean-docs` to remove old build outputs
- [ ] T012 Run `npm run build` to generate Astro website to docs/ directory
- [ ] T013 Verify required files exist:
  - docs/index.html (main entry point)
  - docs/_astro/ (compiled assets directory)
  - docs/.nojekyll (GitHub Pages config)
  - docs/FOLLOWING-INSTRUCTIONS.html (generated from markdown)
  - All checks must pass or FAIL entire task

## Phase 3.6: Documentation Consistency Validation

- [ ] T014 [P] Verify GitHub MCP type is "stdio" in both CLAUDE.md and README.md (grep validation)
- [ ] T015 [P] Verify FOLLOWING-INSTRUCTIONS.md contains MarkItDown case study (grep "MarkItDown")
- [ ] T016 [P] Verify all code examples use UV-first structure (grep "uv pip install\|uv run")
- [ ] T017 Verify constitution v1.0.0 is referenced in FOLLOWING-INSTRUCTIONS.md (grep "v1.0.0")

## Phase 3.7: Git Commit with Branch Preservation

- [ ] T018 Stage all documentation changes: `git add CLAUDE.md README.md docs/`
- [ ] T019 Commit with descriptive message and Claude Code co-authorship:
  ```
  docs: fix GitHub MCP type and create FOLLOWING-INSTRUCTIONS guide

  - Correct GitHub MCP server type from HTTP to stdio in CLAUDE.md and README.md
  - Add binary location and configuration example
  - Create comprehensive docs/FOLLOWING-INSTRUCTIONS.md with case studies
  - Include MarkItDown v1.2.1 case study demonstrating UV-first importance
  - Document GitHub MCP configuration evolution
  - Add troubleshooting section with UV-first solutions
  - Rebuild website with npm run build for GitHub Pages deployment

  Fixes documentation inconsistencies identified in system audit.
  Aligns with Constitution v1.0.0 Principles I, IV, and V.

  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```
- [ ] T020 Push feature branch: `git push -u origin 001-fix-documentation-inconsistencies`
- [ ] T021 Merge to main preserving branch: `git checkout main && git merge 001-fix-documentation-inconsistencies --no-ff && git push origin main`
- [ ] T022 Verify branch still exists: `git branch | grep 001-fix-documentation-inconsistencies` (Constitution Principle IV: Branch Preservation)

## Phase 3.8: GitHub Pages Deployment Validation

- [ ] T023 Wait for GitHub Pages deployment (2-5 minutes): `sleep 180`
- [ ] T024 [P] Verify main page loads: `curl -I https://kairin.github.io/mcp-manager/ | head -n1` (expect HTTP/1.1 200 OK)
- [ ] T025 [P] Verify FOLLOWING-INSTRUCTIONS page loads: `curl -I https://kairin.github.io/mcp-manager/FOLLOWING-INSTRUCTIONS | head -n1` (expect HTTP/1.1 200 OK)
- [ ] T026 Verify content shows stdio type: `curl -s https://kairin.github.io/mcp-manager/ | grep -o "github.*stdio"`
- [ ] T027 Manual verification: Open https://kairin.github.io/mcp-manager/ in browser and confirm:
  - No 404 errors
  - MCP server section shows GitHub as "stdio"
  - FOLLOWING-INSTRUCTIONS link works
  - Case studies are formatted correctly

## Dependencies

**Phase Dependencies:**
- Phase 3.2 (Verification) must complete before Phase 3.3 (Corrections)
- Phase 3.3 (Corrections) must complete before Phase 3.4 (Guide Creation)
- Phase 3.4 (Guide Creation) must complete before Phase 3.5 (Build)
- Phase 3.5 (Build) must complete before Phase 3.6 (Validation)
- Phase 3.6 (Validation) must complete before Phase 3.7 (Commit)
- Phase 3.7 (Commit) must complete before Phase 3.8 (Deployment)

**Task-Level Dependencies:**
- T001-T002 (Setup) before everything
- T003-T005 (Pre-fix verification) before T006-T009 (Corrections)
- T006-T009 (Corrections) before T010 (Guide creation)
- T010 (Guide) before T011-T013 (Build)
- T011-T013 (Build) before T014-T017 (Validation)
- T014-T017 (Validation) before T018-T022 (Commit)
- T018-T022 (Commit) before T023-T027 (Deployment validation)

**Parallel Execution:**
- T003, T004, T005 can run in parallel (different files, read-only)
- T006, T007, T008 can run in parallel (different files or different sections)
- T014, T015, T016 can run in parallel (read-only validation)
- T024, T025 can run in parallel (independent HTTP requests)

## Parallel Execution Examples

### Example 1: Pre-Fix Verification (T003-T005)
```bash
# Run in parallel - all read-only operations
grep -n "github.*HTTP" CLAUDE.md &
grep -n "GitHub MCP.*HTTP" README.md &
test -f docs/FOLLOWING-INSTRUCTIONS.md && echo "EXISTS" || echo "MISSING" &
wait
```

### Example 2: Documentation Corrections (T006-T008)
```bash
# Edit CLAUDE.md (T006 + T008)
# Edit README.md (T007 + T009)
# Can run in parallel as they modify different files
```

### Example 3: Consistency Validation (T014-T016)
```bash
# Run in parallel - all grep operations
grep "github.*stdio" CLAUDE.md && grep "GitHub MCP.*stdio" README.md &
grep "MarkItDown" docs/FOLLOWING-INSTRUCTIONS.md &
grep -c "uv run\|uv pip install" docs/FOLLOWING-INSTRUCTIONS.md &
wait
```

### Example 4: Deployment Validation (T024-T025)
```bash
# Run in parallel - independent HTTP requests
curl -I https://kairin.github.io/mcp-manager/ | head -n1 &
curl -I https://kairin.github.io/mcp-manager/FOLLOWING-INSTRUCTIONS | head -n1 &
wait
```

## Task Execution Notes

### Constitutional Compliance
- **Principle I (UV-First)**: All code examples in documentation must use UV
- **Principle IV (Branch Preservation)**: Branch must NOT be deleted after merge (T022 validates)
- **Principle V (GitHub Pages Protection)**: Website build is MANDATORY (T011-T013)

### Critical Tasks
- **T012-T013**: Build failure blocks deployment - must verify all outputs exist
- **T019**: Commit message must include Claude Code co-authorship
- **T022**: CRITICAL - Verify branch not deleted (constitutional violation if deleted)
- **T024-T026**: Website deployment validation - must pass within 5 minutes

### Error Handling
- If T012 build fails: Check Node.js version, run `npm install`, retry
- If T024-T026 show 404: Verify docs/ committed, check .nojekyll exists, wait longer
- If T022 shows no branch: CONSTITUTIONAL VIOLATION - restore from remote

### Estimated Time
- Phase 3.1-3.2 (Setup): 5 minutes
- Phase 3.3 (Corrections): 10 minutes
- Phase 3.4 (Guide): 30 minutes
- Phase 3.5 (Build): 5 minutes
- Phase 3.6 (Validation): 5 minutes
- Phase 3.7 (Commit): 5 minutes
- Phase 3.8 (Deployment): 10 minutes (includes waiting)

**Total**: ~70 minutes (matches quickstart estimate)

## Success Criteria

All 27 tasks must complete successfully:
- [x] GitHub MCP type corrected to "stdio" in CLAUDE.md and README.md
- [x] Configuration examples added showing stdio structure
- [x] docs/FOLLOWING-INSTRUCTIONS.md created with 2 case studies
- [x] MarkItDown case study from v1.2.1 included
- [x] UV-first compliance throughout all examples
- [x] Website rebuilt with `npm run build`
- [x] All required docs/ files exist
- [x] Git commit includes Claude Code co-authorship
- [x] Branch preserved after merge (NOT deleted)
- [x] GitHub Pages website accessible at https://kairin.github.io/mcp-manager/
- [x] FOLLOWING-INSTRUCTIONS page loads without 404
- [x] All 17 functional requirements from spec.md satisfied

## Validation Checklist

Before marking feature complete:
- [ ] All 27 tasks marked as completed
- [ ] No constitutional violations (especially branch preservation)
- [ ] Website loads without errors
- [ ] Documentation consistent across all files
- [ ] UV-first examples throughout
- [ ] Constitution v1.0.0 properly referenced

---

**Generated**: 2025-09-30 | **Based on**: plan.md, data-model.md, quickstart.md | **Constitution**: v1.0.0