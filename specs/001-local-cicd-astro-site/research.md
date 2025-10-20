# Research Findings: Local CI/CD for Astro Site

This document contains consolidated research findings for the local CI/CD feature implementation.

## Research 1: E2E Testing with Astro and Playwright

### Decision

We will use Playwright for end-to-end (E2E) testing of the Astro.js website.

### Rationale

Playwright is a modern, capable, and reliable E2E testing framework that is well-suited for Astro applications. It offers a good developer experience with features like auto-waits, a test runner, and a trace viewer. It is also easy to set up and integrate into a CI/CD pipeline.

### Alternatives Considered

- **Cypress:** Cypress is another popular E2E testing framework. However, Playwright's ability to run tests in parallel and its better support for multiple browser contexts make it a better choice for this project.
- **Selenium:** Selenium is a long-standing E2E testing framework, but it is more complex to set up and use than Playwright.

---

## Research 2: Structured JSON Logging for CI/CD Pipeline

**Date**: 2025-10-19
**Requirement**: FR-010 - Structured logging with machine-parseable JSON format

### Decision

**Use jq-based custom logging functions** for structured JSON logging in the local CI/CD pipeline.

**Implementation**:
- JSON generation via `jq -nc` with `--arg` parameters
- ISO 8601 timestamps with milliseconds: `date -u +%Y-%m-%dT%H:%M:%S.%3NZ`
- Log schema: `{timestamp, level, step, message, ...extra}`
- Single-file library: `scripts/local-ci/lib/logger.sh`
- Time-based retention: Keep last 30 days

### Rationale

1. **Correctness Over Performance**: jq guarantees valid JSON with proper escaping of special characters (quotes, backslashes, newlines), while printf and custom bash functions break with these characters.

2. **Acceptable Performance**: Benchmarks show jq is 3.7x slower than printf (0.469s vs 0.128s for 100 iterations), but for a CI/CD pipeline with ~50 log messages, this adds only ~0.2 seconds to a 5-minute budget (0.07% overhead).

3. **No Heavy Dependencies**: jq is already required by the project (`scripts/mcp/mcp-profile` uses it) and is installed on the system.

4. **Simple Implementation**: Single-file library (~50 lines) with no external dependencies beyond jq.

5. **Compliance**: Meets FR-010 requirement for machine-parseable structured logging and Principle III (Structured Observability) from the constitution.

### Alternatives Considered

**Alternative 1: printf with Manual Escaping**
- Rejected: Complex escaping logic prone to edge cases, still breaks with certain character combinations
- Performance gain (3.7x) is meaningless when overhead is only 0.2 seconds in a 5-minute pipeline
- Higher maintenance burden for minimal benefit

**Alternative 2: Bash Logging Libraries (log4bash, bashlog)**
- Rejected: External dependencies not currently in project
- Overkill for requirements (need ~50 lines, not 500+ line library)
- Violates project philosophy of simplicity and minimal files

**Alternative 3: No Structured Logging (Status Quo)**
- Rejected: Violates FR-010 and Principle III requirements
- No timestamps, error tracking, or machine parseability
- Identified as critical blocking issue #7 in plan.md

### Implementation Notes

**Log Schema**:
```json
{
  "timestamp": "2025-10-19T14:30:54.847Z",
  "level": "info",
  "step": "lint",
  "message": "Starting prettier check"
}
```

**Log Levels**: `info`, `success`, `warn`, `error`

**Timestamp Format**: ISO 8601 with milliseconds and UTC (`date -u +%Y-%m-%dT%H:%M:%S.%3NZ`)

**Output Strategy**: Dual output to STDOUT (real-time feedback) and log file (permanent record) using `tee -a`

**Log Management**: Simple time-based retention - delete logs older than 30 days using `find -mtime +30 -delete`

**Validation**: Test that logger produces valid JSON using `jq .` validation

**Full details**: See `research-json-logging.md` for complete implementation guide, benchmarks, and testing strategy.

---

## Research 3: Pre-Commit Hook Framework for Secret Detection

**Date**: 2025-10-19
**Requirement**: FR-009 - Pre-commit hook validation to block secrets

### Decision

**Use Husky + lint-staged + Gitleaks** for pre-commit secret validation.

**Implementation Stack**:
- **Husky v9+**: Version-controlled hook management
- **lint-staged**: Performance optimization (scan only staged files)
- **Gitleaks**: Fast binary-based secret detection (Go binary, <1s scans)

### Rationale

1. **Husky v9+ Over Native Git Hooks**:
   - Cross-platform compatible (Windows/macOS/Linux)
   - Version controlled (hooks auto-installed via `npm install`)
   - Standard for Node.js projects (3,200+ dependent packages)
   - Team collaboration friendly (consistent behavior across developers)

2. **Gitleaks Over Alternatives**:
   - **Fastest** option: Go binary executes in <1 second
   - **Most comprehensive**: 150+ built-in secret patterns
   - **Actively maintained**: 11.2k GitHub stars, regular updates
   - **Production-proven**: Used by major organizations

3. **lint-staged for Performance**:
   - Scans only **staged files** (not entire codebase)
   - Batch processing for speed
   - Maintains <1 second requirement for typical commits

### Alternatives Considered

**Alternative 1: TruffleHog**
- Rejected: Too slow for pre-commit use (entropy scanning adds latency)
- Better suited for CI/CD full repository scans

**Alternative 2: detect-secrets (npm)**
- Rejected: Package abandoned 5 years ago (last update 2020)
- Security risk to use unmaintained tool

**Alternative 3: Secretlint**
- Rejected: More configuration overhead than Gitleaks
- Slower execution (Node.js vs Go binary)
- Better for IDE real-time checks than pre-commit hooks

**Alternative 4: git-secrets (AWS)**
- Rejected: AWS-focused patterns, less community adoption
- Manual pattern management required

**Alternative 5: Native Git Hooks**
- Rejected: Not version controlled, manual setup on each machine
- Platform-specific issues (Windows file permissions)
- No team collaboration benefits

### Implementation Notes

**Installation**:
```bash
npm install --save-dev husky lint-staged
npx husky init
brew install gitleaks  # or download binary from releases
```

**Hook Configuration** (`.husky/pre-commit`):
```bash
#!/bin/sh
npx lint-staged
```

**lint-staged Configuration** (`package.json`):
```json
{
  "lint-staged": {
    "*": [
      "gitleaks protect --staged --no-banner --redact -v"
    ]
  }
}
```

**Performance Expectations**:
| Commit Size | Files Changed | Expected Time |
|-------------|---------------|---------------|
| Small | 1-3 files | 0.1-0.3s |
| Medium | 5-10 files | 0.3-0.6s |
| Large | 20+ files | 0.6-1.5s |

**False Positive Handling**:
- `.gitleaksignore` file for known false positives
- `# gitleaks:allow` inline comments for specific lines
- Developer education on legitimate vs problematic patterns

**Multi-Layer Defense Strategy**:
1. **Pre-commit** (Gitleaks) - Fast feedback, 80-90% catch rate
2. **Pre-push** (optional) - Deeper scan before remote push
3. **CI/CD** (GitHub Actions) - Full repo scan as backup
4. **Periodic scans** - Weekly full history audit

**Testing Strategy**:
```bash
# Test hook installation
cat .husky/pre-commit

# Test secret detection (should fail)
echo "api_key=sk_live_FAKE_KEY_EXAMPLE" > test.txt
git add test.txt
git commit -m "test"  # Should be blocked

# Test normal commit (should pass)
echo "# Normal file" > test.txt
git add test.txt
git commit -m "test"  # Should succeed
```

**Full details**: See `pre-commit-secrets-research.md` for complete guide including installation steps, configuration, false positive strategies, and team education checklist.

---

## Research 4: Repository Structure Investigation - web/web/ Directory

**Date**: 2025-10-19
**Context**: Critical Issue #3 identified during planning review

### Decision

**REMOVE `/home/kkk/Apps/002-mcp-manager/web/web/` entirely**

### Investigation Findings

**What exists**:
- `web/web/package.json` (3 bytes, contains only `{}`)
- `web/web/package-lock.json` (6 lines, minimal/empty content)
- Created: 2025-10-19 20:38:20 (recent artifact)

**What it is NOT**:
- ❌ Not a build artifact (Astro builds to `dist/`, not nested `web/`)
- ❌ Not referenced in any configuration files (grep found zero references)
- ❌ Not part of Astro build process
- ❌ Not tracked by git (shows as `??` untracked)
- ❌ Not in git history (first appearance is current state)

**Root cause**: Accidental directory nesting during development (likely `mkdir -p web/web` mistake or incomplete file reorganization cleanup)

### Rationale for Removal

| Criterion | Finding | Impact |
|-----------|---------|--------|
| Functional purpose | None - empty files | Clutter only |
| Build artifact | No - not used by Astro | False positive |
| Configuration need | No - parent `/web/` has complete config | Redundant |
| Git tracking | Untracked - not part of repo | Dead artifact |
| Constitution compliance | Violates FR-005 (NO unnecessary files) | High priority fix |
| Code clarity | Creates confusion about structure | Developer friction |

### Implementation Notes

**Removal command**:
```bash
rm -rf /home/kkk/Apps/002-mcp-manager/web/web/
```

**Safety verification**:
- No functional content lost (empty `{}` file)
- No code references to remove
- No git history to preserve
- No scripts depend on this directory

**Benefits of removal**:
- Fixes CRITICAL ISSUE #3 in specification
- Achieves FR-005 compliance (NO unnecessary files)
- Improves code clarity and project structure
- Removes confusion about module boundaries
- Aligns with Constitution Principle I (Modular-First Design)

**Impact**: Zero negative impacts, clear quality improvement.

---

## Research 5: Test Directory Structure Decision

**Date**: 2025-10-19
**Context**: Critical Issue #4 - tests exist in both `web/tests/` and `web/src/tests/`

### Decision

**CONSOLIDATE to `/home/kkk/Apps/002-mcp-manager/web/tests/` (top-level sibling to `src/`)**

### Rationale

1. **Industry Standard**: Top-level `tests/` is conventional for Node.js/Astro projects
   - Separates test code from production source code
   - Clearer boundary between application and test infrastructure
   - Matches common patterns in open-source projects

2. **Test Organization by Type**:
   ```
   web/tests/
   ├── unit/                # Component/function tests
   ├── integration/         # Module interaction tests
   └── e2e/                 # Playwright end-to-end tests
   ```

3. **Build Clarity**: Tests outside `src/` won't be accidentally included in build output

4. **Constitution Compliance**:
   - Fixes Violation #4 (clear structure reflecting boundaries)
   - Achieves FR-005 (NO unnecessary duplicate directories)
   - Supports Principle I (Modular-First Design)

### Migration Plan

**Current state**:
- `web/tests/` exists (preferred location)
- `web/src/tests/` exists (to be moved/removed)
- Scripts reference `src/tests/*.test.js` (needs update)

**Migration steps**:
1. Move all test files from `web/src/tests/` to `web/tests/unit/`
2. Remove empty `web/src/tests/` directory
3. Update `scripts/local-ci/run.sh` test paths:
   ```bash
   # OLD: cd web && npx mocha src/tests/*.test.js
   # NEW: cd web && npx mocha tests/unit/**/*.test.js
   ```
4. Update Playwright config to use `tests/e2e/`
5. Verify all tests discoverable and passing

### Alternatives Considered

**Alternative: Consolidate to `web/src/tests/`**
- Rejected: Less conventional, mixes production and test code
- Harder to exclude from builds
- Doesn't match Astro/Node.js community standards

**Alternative: Keep both locations**
- Rejected: Violates FR-005 (unnecessary files)
- Creates confusion about where new tests go
- Split test suite harder to maintain

### Implementation Notes

**Package.json scripts to update**:
```json
{
  "scripts": {
    "test": "mocha tests/unit/**/*.test.js",
    "test:integration": "mocha tests/integration/**/*.integration.test.js",
    "test:e2e": "playwright test tests/e2e"
  }
}
```

**Gitignore patterns** (verify these exist):
```
web/dist/
web/.astro/
node_modules/
```

**No gitignore for tests** - test files should be tracked.

---

## Summary of Research Phase

All "NEEDS CLARIFICATION" items from Technical Context have been resolved:

| Item | Decision | Status |
|------|----------|--------|
| Pre-commit hook framework | Husky + lint-staged + Gitleaks | ✅ Resolved |
| JSON logging library | jq-based custom functions | ✅ Resolved |
| Deployment state tracking | (Defer to Phase 1 design) | ⏭️ Phase 1 |
| Test directory location | Consolidate to `web/tests/` | ✅ Resolved |
| web/web/ directory | Remove (artifact) | ✅ Resolved |

**Phase 0 Status**: Complete - Ready for Phase 1 Design