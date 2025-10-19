# Contract: Local CI/CD Script

**Module**: scripts/local-ci/
**Owner**: Local CI Module
**Consumers**: Developers (CLI), TUI Module, Pre-push hooks

---

## Purpose

Execute all CI/CD checks locally before pushing to remote repository, ensuring zero GitHub Actions usage for CI/CD (FR-003, Principle II).

---

## CLI Interface

### Primary Command

```bash
scripts/local-ci/run.sh [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--no-fix` | Skip auto-fix attempts on lint failures | false (auto-fix enabled) |
| `--verbose` | Enable verbose logging (all command output) | false (structured JSON only) |
| `--skip-tests` | Skip test execution (lint + build only) | false (run all tests) |
| `--log-file <path>` | Custom log file location | `logs/ci-$(date +%Y%m%d-%H%M%S).json` |

### Exit Codes

| Code | Meaning | Action Required |
|------|---------|-----------------|
| 0 | Success - all checks passed | Safe to push to remote |
| 1 | Lint failure (after auto-fix attempt) | Fix remaining lint errors manually |
| 2 | Test failure | Fix failing tests |
| 3 | Build failure | Fix build errors |
| 4 | Environment validation failure | Check `.env` files, install dependencies |
| 130 | User aborted (Ctrl+C) | N/A |

---

## JSON Log Output

### Format

Newline-delimited JSON (one object per line) written to STDOUT and log file.

### Log Entry Schema

See `data-model.md` Entity 1 for complete schema. Key fields:

```json
{
  "timestamp": "2025-10-19T14:30:54.847Z",
  "level": "info|success|warn|error",
  "step": "init|env-check|lint|test-unit|test-integration|test-e2e|build|cleanup|complete",
  "message": "Human-readable description",
  "duration": 2.3,
  "exitCode": 0
}
```

### Example Output

```bash
$ scripts/local-ci/run.sh
{"timestamp":"2025-10-19T14:30:54.847Z","level":"info","step":"init","message":"Starting local CI/CD pipeline"}
{"timestamp":"2025-10-19T14:30:55.000Z","level":"info","step":"lint","message":"Running prettier check"}
{"timestamp":"2025-10-19T14:30:57.300Z","level":"success","step":"lint","message":"Prettier check passed","duration":2.3}
{"timestamp":"2025-10-19T14:30:57.400Z","level":"info","step":"test-unit","message":"Running unit tests"}
{"timestamp":"2025-10-19T14:31:15.800Z","level":"success","step":"test-unit","message":"24 tests passed","duration":18.4}
{"timestamp":"2025-10-19T14:31:16.000Z","level":"info","step":"build","message":"Building Astro site"}
{"timestamp":"2025-10-19T14:33:22.000Z","level":"success","step":"build","message":"Build complete","duration":126.0}
{"timestamp":"2025-10-19T14:33:22.184Z","level":"success","step":"complete","message":"Pipeline completed successfully","duration":147.3}
```

---

## Environment Requirements

### System Dependencies

| Dependency | Version | Purpose | Installation Check |
|------------|---------|---------|-------------------|
| Bash | 4.0+ | Shell execution | `bash --version` |
| jq | 1.6+ | JSON logging | `jq --version` |
| Node.js | 18+ LTS | Build tooling | `node --version` |
| npm | 9+ | Package management | `npm --version` |

### Node.js Dependencies

Must be installed in `web/` directory:
- `prettier` (linting)
- `mocha` (unit/integration tests)
- `playwright` (e2e tests)
- `astro` (build)

### Environment Variables

Read from `.env.local` (development) or `.env.production` (production):

| Variable | Required | Purpose |
|----------|----------|---------|
| `NODE_ENV` | Yes | Environment: development\|production |
| `CI_LOG_LEVEL` | No | Logging verbosity (default: info) |
| `ASTRO_TELEMETRY_DISABLED` | No | Disable Astro telemetry (recommended: 1) |

---

## Pipeline Steps

### Step 1: Environment Check (`env-check`)

**Purpose**: Validate dependencies and environment before execution

**Actions**:
1. Check system dependencies (bash, jq, node, npm)
2. Verify Node.js version ≥ 18
3. Check `web/node_modules/` exists (run `npm install` if missing)
4. Load `.env.local` or `.env.production`
5. Validate `NODE_ENV` is set

**Exit codes**: 0 (success), 4 (validation failure)

### Step 2: Lint (`lint`)

**Purpose**: Code formatting check with auto-fix capability

**Actions**:
1. Run `cd web && npx prettier --check .`
2. If fails AND `--no-fix` NOT set:
   - Run `npx prettier --write .` (auto-fix)
   - Re-run `npx prettier --check .`
3. Log result (success or failure after auto-fix attempt)

**Exit codes**: 0 (success), 1 (failure after auto-fix)

### Step 3: Unit Tests (`test-unit`)

**Purpose**: Run component/function unit tests

**Actions**:
1. Run `cd web && npx mocha tests/unit/**/*.test.js`
2. Capture test count (passed/failed)
3. Log results

**Exit codes**: 0 (all pass), 2 (any fail)

### Step 4: Integration Tests (`test-integration`)

**Purpose**: Run module interaction tests

**Actions**:
1. Run `cd web && npx mocha tests/integration/**/*.integration.test.js`
2. Capture test count
3. Log results

**Exit codes**: 0 (all pass), 2 (any fail)

### Step 5: E2E Tests (`test-e2e`)

**Purpose**: Run Playwright end-to-end tests

**Actions**:
1. Run `cd web && npx playwright test tests/e2e/`
2. Capture test count
3. Log results

**Exit codes**: 0 (all pass), 2 (any fail)

**Note**: Skipped if `--skip-tests` flag provided

### Step 6: Build (`build`)

**Purpose**: Build Astro site for GitHub Pages deployment

**Actions**:
1. Run `cd web && npm run build`
2. Verify `web/dist/` directory created
3. Check dist size (warn if > 100MB)
4. Log result

**Exit codes**: 0 (success), 3 (build failure)

### Step 7: Cleanup (`cleanup`)

**Purpose**: Post-execution maintenance

**Actions**:
1. Clean logs older than 30 days: `find logs/ -name "ci-*.json" -type f -mtime +30 -delete`
2. Log cleanup summary

**Exit codes**: Always 0

### Step 8: Complete (`complete`)

**Purpose**: Final summary log

**Actions**:
1. Calculate total duration
2. Output summary JSON log with all metrics (see Entity 3 in data-model.md)

**Exit codes**: Always 0

---

## Performance SLA

**NFR-003 Compliance**: Pipeline MUST complete in < 300 seconds (5 minutes) for typical changes.

**Typical breakdown**:
- env-check: 1-2s
- lint: 2-5s
- test-unit: 10-20s
- test-integration: 5-10s
- test-e2e: 20-40s
- build: 60-120s
- cleanup: <1s
- **Total**: 98-198s (well under 300s)

**Warning**: If total duration exceeds 300s, log warning message.

---

## Error Handling

### Auto-Fix Behavior

When lint fails:
1. Log error with `fixAttempted: true`
2. Run `prettier --write .`
3. Re-run `prettier --check .`
4. If still fails: Log `fixSucceeded: false`, exit 1
5. If succeeds: Log `fixSucceeded: true`, continue

### Graceful Degradation

- Missing `.env` file: Use defaults (warn user)
- Playwright not installed: Skip e2e tests (warn user)
- Network errors during npm: Retry once, then fail

### User Interruption

- Catch SIGINT (Ctrl+C)
- Log `"level":"warn","step":"complete","message":"Pipeline aborted by user"`
- Exit code 130

---

## Module Boundaries

### What This Module Does

✅ Execute CI/CD checks locally
✅ Produce structured JSON logs
✅ Auto-fix lint errors
✅ Validate environment dependencies

### What This Module Does NOT Do

❌ Commit code (developer responsibility)
❌ Push to remote (developer responsibility)
❌ Deploy to GitHub Pages (GitHub Actions responsibility)
❌ Manage TUI/interactive menus (TUI module responsibility)
❌ Validate secrets (pre-commit hook responsibility)

---

## Dependencies

### Depends On

- `web/package.json` - Node.js dependencies
- `.env.local` or `.env.production` - Environment configuration
- `scripts/local-ci/lib/logger.sh` - JSON logging functions

### Depended Upon By

- TUI module (`scripts/tui/run.sh`) - Calls this script
- Pre-push hooks (optional) - Can call this script before push
- Developers - Manual CLI execution

---

## Testing Contract

### Unit Tests

Location: `scripts/local-ci/lib/logger.test.sh`

Test cases:
- Valid JSON output from logger
- Special character escaping
- Timestamp format validation
- Exit code propagation

### Integration Tests

Test the full pipeline:
1. Create sample web project with intentional lint errors
2. Run `scripts/local-ci/run.sh`
3. Verify auto-fix attempts
4. Verify JSON log structure
5. Verify exit codes match expected

### Contract Tests

Verify:
- All promised exit codes are used correctly
- JSON schema matches data-model.md Entity 1
- All pipeline steps execute in documented order
- Performance SLA met (<300s typical)

---

## Future Enhancements (Out of Scope for V1)

- Parallel test execution (reduce duration)
- Incremental builds (only rebuild changed files)
- Caching layer for faster re-runs
- Custom step plugins/hooks
- Configurable step ordering

---

**Contract Version**: 1.0
**Last Updated**: 2025-10-19
**Status**: Phase 1 Design Complete
