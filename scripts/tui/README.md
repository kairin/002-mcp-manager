# TUI (Text User Interface) for Local CI/CD Pipeline

**Feature**: 001-local-cicd-astro-site
**Created**: 2025-10-20
**Status**: Fully Functional
**Purpose**: Interactive menu-driven interface for the Local CI/CD pipeline

## Overview

The TUI provides a user-friendly, menu-driven interface to the Local CI/CD pipeline, eliminating the need to memorize command-line flags. It satisfies **FR-006** (Modular Implementation) requirement from the feature specification.

## Quick Start

```bash
# Run the TUI from anywhere in the project
./scripts/tui/run.sh

# Or add to PATH and run directly
export PATH="$HOME/Apps/002-mcp-manager/scripts/tui:$PATH"
run.sh
```

## Menu Options

### CI/CD Operations

**1) Run Full CI/CD Pipeline**
- Executes complete pipeline: lint → unit tests → integration tests → e2e tests → build
- Equivalent to: `./scripts/local-ci/run.sh`
- Use for: Final validation before pushing to remote

**2) Run CI/CD (Skip Tests - faster)**
- Skips all test steps (unit, integration, e2e)
- Runs: lint → build only
- Equivalent to: `./scripts/local-ci/run.sh --skip-tests`
- Use for: Quick syntax/build checks

**3) Run CI/CD (Verbose Mode)**
- Shows detailed output for each step
- Equivalent to: `./scripts/local-ci/run.sh --verbose`
- Use for: Debugging pipeline issues

**4) Run CI/CD (No Auto-Fix)**
- Disables automatic linting fixes
- Lint failures will halt pipeline immediately
- Equivalent to: `./scripts/local-ci/run.sh --no-fix`
- Use for: Validating code quality without modifications

### Monitoring & Maintenance

**5) View Recent Logs**
- Lists recent CI/CD log files from `logs/` directory
- Option to display full log with JSON formatting (via `jq`)
- Use for: Reviewing past pipeline runs

**6) Check Environment**
- Validates all dependencies and versions
- Checks: bash (≥5.0), jq (≥1.6), node (≥18.0), npm (≥9.0)
- Use for: Troubleshooting setup issues

**7) Clean Old Logs**
- Runs cleanup script to remove logs older than 30 days
- Shows count of deleted files
- Use for: Disk space management

### Help & Info

**8) Help & Documentation**
- Shows pipeline documentation
- Lists all exit codes and their meanings
- Use for: Reference and troubleshooting

**9) Exit**
- Returns to shell

## Exit Code Interpretation

The TUI interprets CI/CD exit codes and displays color-coded feedback:

- **0 (Green)**: Pipeline completed successfully
- **1 (Yellow)**: Linting failed
- **2 (Red)**: Tests failed
- **3 (Red)**: Build failed
- **4 (Red)**: Environment validation failed
- **5 (Red)**: Timeout - pipeline exceeded 300 seconds (Feature 002)

## Features

- **No Dependencies**: Pure bash with ANSI colors (no dialog, whiptail, or gum)
- **Error Handling**: Graceful handling of CI script failures
- **User Feedback**: Clear messages and pause for user confirmation
- **Color Coding**: Visual hierarchy with cyan headers, green success, red errors
- **Integration**: Seamlessly calls existing CI/CD script and libraries

## Example Session

```
╔════════════════════════════════════════════════════════════════╗
║  Local CI/CD Pipeline - Interactive Menu                      ║
╚════════════════════════════════════════════════════════════════╝

CI/CD Operations:
  1) Run Full CI/CD Pipeline (lint + tests + build)
  2) Run CI/CD (Skip Tests - faster)
  3) Run CI/CD (Verbose Mode)
  4) Run CI/CD (No Auto-Fix)

Monitoring & Maintenance:
  5) View Recent Logs
  6) Check Environment
  7) Clean Old Logs

Help & Info:
  8) Help & Documentation
  9) Exit

Enter your choice [1-9]: 6

╔════════════════════════════════════════════════════════════════╗
║  Checking Environment                                          ║
╚════════════════════════════════════════════════════════════════╝

✓ bash 5.2.21
✓ jq 1.6
✓ node 18.17.0
✓ npm 9.8.1

All dependencies validated successfully!

Press Enter to continue...
```

## Comparison with Direct CLI Usage

| Task | TUI Approach | CLI Approach |
|------|--------------|--------------|
| Full pipeline | Menu option 1 | `./scripts/local-ci/run.sh` |
| Skip tests | Menu option 2 | `./scripts/local-ci/run.sh --skip-tests` |
| Verbose output | Menu option 3 | `./scripts/local-ci/run.sh --verbose` |
| No auto-fix | Menu option 4 | `./scripts/local-ci/run.sh --no-fix` |
| View logs | Menu option 5 | `ls logs/ && jq . logs/ci-*.log` |
| Check environment | Menu option 6 | `bash scripts/local-ci/lib/validator.sh` |
| Clean logs | Menu option 7 | `bash scripts/local-ci/lib/cleanup-logs.sh` |

## Architecture

The TUI is a thin wrapper around the core CI/CD script:

```
scripts/tui/run.sh
    ↓
scripts/local-ci/run.sh (with flags)
    ↓
scripts/local-ci/lib/*.sh (libraries)
```

This maintains **module independence** (FR-006): changes to the TUI don't affect the CI/CD pipeline or website.

## File Locations

- **TUI Script**: `scripts/tui/run.sh`
- **CI/CD Script**: `scripts/local-ci/run.sh`
- **Libraries**: `scripts/local-ci/lib/*.sh`
- **Logs**: `logs/ci-YYYYMMDD_HHMMSS.log`
- **Specification**: `specs/001-local-cicd-astro-site/spec.md`

## Troubleshooting

**Issue**: "CI/CD script not found"
- **Solution**: Ensure you're running from project root or script uses absolute paths

**Issue**: Colors not displaying correctly
- **Solution**: Ensure terminal supports ANSI escape codes (most modern terminals do)

**Issue**: "command not found: jq"
- **Solution**: Install jq: `sudo apt install jq` (Ubuntu/Debian) or `brew install jq` (macOS)

## Development

To modify menu options:

1. Edit `scripts/tui/run.sh`
2. Add new function for the operation (e.g., `run_custom_option()`)
3. Add menu item in `main_menu()` function
4. Update this README with the new option

## Integration Tests

Module independence is verified by integration tests (Phase 6, T070-T071):
- TUI changes don't affect CI/CD script functionality
- CI/CD changes don't require TUI modifications
- Both can run independently

## Related Documentation

- **Feature Specification**: `specs/001-local-cicd-astro-site/spec.md` (FR-006)
- **Task Tracker**: `specs/001-local-cicd-astro-site/tasks.md` (Phase 4: T050-T063)
- **CI/CD Script**: `scripts/local-ci/run.sh` (implementation details)
- **MCP Profile TUI**: `scripts/mcp/mcp-profile` (similar TUI pattern)

---

**Version**: 1.0
**Last Updated**: 2025-10-20
**Status**: Fully Functional
**Requirements**: FR-006 (Modular Implementation) ✓ Satisfied
