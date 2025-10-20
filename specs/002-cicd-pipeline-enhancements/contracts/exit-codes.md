# Pipeline Exit Codes

**Branch**: `002-cicd-pipeline-enhancements` | **Date**: 2025-10-20 | **Phase**: 1

## Overview

This document defines the exit code contract for the CI/CD pipeline. Exit codes communicate pipeline outcomes to the TUI, CLI, and GitHub Actions workflows.

## Exit Code Table

| Code | Meaning | Triggered By | Example Scenario |
|------|---------|--------------|------------------|
| 0    | Success | All steps passed, duration < 300s | Pipeline completes in 285s, all tests pass, build succeeds |
| 1    | Lint failure | Prettier/linter errors not auto-fixable | Code style issues detected by Prettier that require manual fixes |
| 2    | Test failure | Unit, integration, or E2E tests failed after retries | 3 unit tests fail, E2E retry exhausted (2 attempts) |
| 3    | Build failure | npm run build failed | Build errors (TypeScript errors, module resolution failures) |
| 4    | Environment validation failure | Missing dependencies (node, npm, jq) | `env-check` step detects missing `jq` or unsupported Node version |
| 5    | Timeout violation (NFR-003) | Duration ≥ 300 seconds | Pipeline exceeds 5-minute hard limit (checked periodically) |

## Exit Code Precedence

**Rule**: If multiple failures occur during a single pipeline run, use the **lowest code** except for timeout (5), which is **overridden** by other failures.

### Precedence Order (Lowest to Highest)

1. Success (0)
2. Lint failure (1)
3. Test failure (2)
4. Build failure (3)
5. Environment validation failure (4)
6. Timeout violation (5) - **LOWEST PRIORITY**

### Precedence Examples

**Scenario 1**: Test failure + Timeout
- Tests fail at 280s (exit 2)
- Pipeline times out at 300s (exit 5)
- **Result**: Exit 2 (test failure takes precedence per spec User Story 1 scenario 3)

**Scenario 2**: Lint failure only
- Linter detects errors at 30s (exit 1)
- Pipeline stops immediately
- **Result**: Exit 1

**Scenario 3**: Build failure + Lint failure
- Linter passes, tests pass, build fails at 250s (exit 3)
- **Result**: Exit 3 (even though lint would be lower, build failure occurred)

**Scenario 4**: Timeout only
- All steps pass, but pipeline duration = 305s
- **Result**: Exit 5 (timeout violation)

**Scenario 5**: Multiple test failures
- Unit tests fail at 100s (exit 2)
- Integration tests fail at 120s (exit 2)
- E2E tests skipped (previous failure)
- **Result**: Exit 2 (first test failure reported)

## Implementation Logic

### Bash Exit Code Handling

```bash
#!/usr/bin/env bash

# Global exit code variable (default: success)
PIPELINE_EXIT_CODE=0

# Update exit code with precedence rules
set_exit_code() {
    local new_code=$1

    # If current code is 0, always update
    if (( PIPELINE_EXIT_CODE == 0 )); then
        PIPELINE_EXIT_CODE=$new_code
        return
    fi

    # If current code is 5 (timeout), any other failure overrides
    if (( PIPELINE_EXIT_CODE == 5 && new_code != 5 )); then
        PIPELINE_EXIT_CODE=$new_code
        return
    fi

    # Otherwise, keep lowest code (first failure)
    if (( new_code < PIPELINE_EXIT_CODE && new_code != 5 )); then
        PIPELINE_EXIT_CODE=$new_code
    fi
}

# Example usage in pipeline steps
run_step_lint() {
    if ! npm run lint; then
        log_error "Lint step failed"
        set_exit_code 1
        return 1
    fi
}

run_step_test_unit() {
    if ! npm run test:unit; then
        log_error "Unit tests failed"
        set_exit_code 2
        return 2
    fi
}

# Timeout check (called periodically)
check_timeout() {
    local elapsed=$((SECONDS - START_TIME))
    if (( elapsed >= TIMEOUT_SECONDS )); then
        log_error "Pipeline timeout: $elapsed seconds (limit: $TIMEOUT_SECONDS)"
        set_exit_code 5
        # Exit immediately on timeout (but check if other failures occurred)
        exit $PIPELINE_EXIT_CODE
    fi
}

# Final exit
exit $PIPELINE_EXIT_CODE
```

## Exit Code Logging

All exit codes are logged in the final log entry:

```json
{
  "timestamp": "2025-10-20T14:32:15Z",
  "level": "error",
  "message": "Pipeline completed with exit code 2: Test failure",
  "run_id": "run-20251020-143045-k8m3q2",
  "source_file": "scripts/local-ci/run.sh",
  "line_number": 450,
  "function_name": "main",
  "step_name": "complete",
  "duration_ms": 285000
}
```

## TUI Display

The TUI displays exit codes with color coding:

| Exit Code | Display | Color |
|-----------|---------|-------|
| 0 | ✓ Success | Green |
| 1 | ✗ Lint Failure | Yellow |
| 2 | ✗ Test Failure | Red |
| 3 | ✗ Build Failure | Red |
| 4 | ✗ Environment Error | Red |
| 5 | ✗ Timeout | Orange |

## GitHub Actions Integration

GitHub Actions workflows use exit codes to determine deployment eligibility:

```yaml
- name: Run local CI/CD pipeline
  id: ci
  run: ./scripts/local-ci/run.sh
  continue-on-error: true

- name: Check pipeline result
  run: |
    if [[ "${{ steps.ci.outcome }}" != "success" ]]; then
      echo "Pipeline failed, skipping deployment"
      exit 1
    fi
```

## Testing Exit Codes

```bash
# Test exit code 0 (success)
./scripts/local-ci/run.sh
echo "Exit code: $?"  # Should be 0

# Test exit code 1 (lint failure)
# Introduce lint error, run pipeline
echo "Exit code: $?"  # Should be 1

# Test exit code 2 (test failure)
# Introduce test failure, run pipeline
echo "Exit code: $?"  # Should be 2

# Test exit code 5 (timeout)
# Add artificial delay > 300s, run pipeline
echo "Exit code: $?"  # Should be 5 (or 2 if tests fail first)
```

---

**Exit Code Contract Status**: ✅ COMPLETE
**Precedence Rules Defined**: ✅ YES
**Ready for Implementation**: ✅ YES
