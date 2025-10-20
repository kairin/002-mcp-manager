#!/usr/bin/env bash
# Log Cleanup Script - 30-day retention policy
# Removes CI/CD log files older than 30 days
# See: specs/001-local-cicd-astro-site/contracts/ci-script.contract.md Step 7

set -euo pipefail

# Get script directory and repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LOG_DIR="$REPO_ROOT/logs"

# Retention period in days
RETENTION_DAYS=30

# Source logger if available (for structured logging)
if [ -f "$SCRIPT_DIR/logger.sh" ]; then
    source "$SCRIPT_DIR/logger.sh"
    USE_LOGGER=1
else
    USE_LOGGER=0
fi

# Check if logs directory exists
if [ ! -d "$LOG_DIR" ]; then
    if [ "$USE_LOGGER" -eq 1 ]; then
        log_warn "cleanup" "Log directory not found: $LOG_DIR"
    else
        echo "WARNING: Log directory not found: $LOG_DIR" >&2
    fi
    exit 0
fi

# Count files before cleanup
FILES_BEFORE=$(find "$LOG_DIR" -name "ci-*.json" -type f 2>/dev/null | wc -l)

if [ "$USE_LOGGER" -eq 1 ]; then
    log_info "cleanup" "Starting log cleanup (retention: ${RETENTION_DAYS} days)"
    log_info "cleanup" "Log files before cleanup: $FILES_BEFORE"
fi

# Find and delete log files older than retention period
DELETED_FILES=0
while IFS= read -r -d '' file; do
    if [ "$USE_LOGGER" -eq 1 ]; then
        log_info "cleanup" "Deleting old log file: $(basename "$file")"
    fi
    rm -f "$file"
    DELETED_FILES=$((DELETED_FILES + 1))
done < <(find "$LOG_DIR" -name "ci-*.json" -type f -mtime +${RETENTION_DAYS} -print0 2>/dev/null)

# Count files after cleanup
FILES_AFTER=$(find "$LOG_DIR" -name "ci-*.json" -type f 2>/dev/null | wc -l)

if [ "$USE_LOGGER" -eq 1 ]; then
    log_success "cleanup" "Log cleanup complete: deleted $DELETED_FILES files, $FILES_AFTER files remaining"
else
    echo "Log cleanup complete: deleted $DELETED_FILES files, $FILES_AFTER files remaining"
fi

exit 0
