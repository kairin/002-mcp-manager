# Research: Structured JSON Logging for Local CI/CD Pipeline

**Research Date**: 2025-10-19
**Context**: Local CI/CD pipeline for Astro.build site (Feature 001)
**Requirement**: FR-010 - Structured logging with timestamps, warnings, errors in machine-parseable JSON format

## Decision

**Use jq-based custom logging functions** with the following characteristics:

- JSON generation via `jq -nc` with `--arg` parameters
- ISO 8601 timestamps with milliseconds (`date -u +%Y-%m-%dT%H:%M:%S.%3NZ`)
- Structured log schema: `{timestamp, level, step, message, ...extra}`
- Single-file logging library at `scripts/local-ci/lib/logger.sh`
- Simple time-based log retention (keep last 30 days)

## Rationale

### 1. Correctness Over Performance

**jq provides guaranteed valid JSON output**, which is critical for machine-parseability:

| Aspect | jq | printf | Custom bash |
|--------|-----|--------|-------------|
| Valid JSON with special chars | ✅ Always | ❌ Breaks | ❌ Breaks |
| Handles quotes | ✅ Yes | ❌ No | ❌ No |
| Handles backslashes | ✅ Yes | ❌ No | ❌ No |
| Handles newlines | ✅ Yes | ❌ No | ❌ No |
| Validation | ✅ Built-in | ❌ Manual | ❌ Manual |

**Test Results** (from `/tmp/json_escaping_test.sh`):
```bash
message='Test with "quotes" and \backslash and $variables and newlines'

# jq output: ✓ Valid JSON
{"message":"Test with \"quotes\" and \\backslash and $variables and \nnewlines"}

# printf output: ✗ Invalid JSON (broken by unescaped quotes)
{"message":"Test with "quotes" and \backslash and $variables and newlines"}
```

### 2. Acceptable Performance for CI/CD Use Case

**Performance benchmarks** (100 iterations):

| Method | Real Time | User Time | Sys Time | Relative Speed |
|--------|-----------|-----------|----------|----------------|
| jq | 0.469s | 0.152s | 0.332s | 1x (baseline) |
| printf | 0.128s | 0.030s | 0.103s | 3.7x faster |
| Custom bash | 0.134s | 0.025s | 0.114s | 3.5x faster |

**Analysis**:
- jq is ~3.7x slower than printf
- For CI/CD with < 50 log messages per run, overhead is **~0.2 seconds** total
- NFR-003 requires pipeline completion in < 5 minutes (300 seconds)
- **0.2 seconds is 0.07% of budget** - negligible for correctness guarantee

**Conclusion**: Performance difference is irrelevant for this use case.

### 3. No Heavy Dependencies

**jq is already required** by this project:
- `scripts/mcp/mcp-profile` uses jq for reading MCP server configs
- jq 1.7 is installed on the system (`/usr/bin/jq`)
- Meets "no heavy dependencies" requirement from AGENTS.md

### 4. Simplicity of Implementation

**Single-file library** (`scripts/local-ci/lib/logger.sh`):
```bash
#!/bin/bash

# JSON logging library using jq

log_json() {
  local level=$1
  local step=$2
  local message=$3
  local extra=${4:-"{}"}

  jq -nc \
    --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" \
    --arg level "$level" \
    --arg step "$step" \
    --arg message "$message" \
    --argjson extra "$extra" \
    '{
      timestamp: $timestamp,
      level: $level,
      step: $step,
      message: $message
    } + $extra'
}

# Convenience functions
log_info() { log_json "info" "$1" "$2" "${3:-{}}"; }
log_warn() { log_json "warn" "$1" "$2" "${3:-{}}"; }
log_error() { log_json "error" "$1" "$2" "${3:-{}}"; }
log_success() { log_json "success" "$1" "$2" "${3:-{}}"; }
```

**Usage in CI script**:
```bash
#!/bin/bash
source "$(dirname "$0")/lib/logger.sh"

log_info "lint" "Starting prettier check"
# ... run prettier ...
log_success "lint" "Prettier check passed"

log_info "test" "Running unit tests"
# ... run tests ...
log_warn "test" "3 tests skipped" '{"skipped":3}'
```

## Alternatives Considered

### Alternative 1: printf with Manual Escaping

**Approach**:
```bash
# Escape special characters manually
escape_json() {
  echo "$1" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | tr '\n' ' '
}

log_printf() {
  printf '{"timestamp":"%s","level":"%s","message":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" "$1" "$(escape_json "$2")"
}
```

**Rejected Because**:
- Complex escaping logic prone to edge cases
- Still breaks with certain character combinations
- 3.7x performance gain is meaningless (0.2s → 0.05s in 5-minute pipeline)
- Higher maintenance burden for minimal benefit
- Violates "simple, no heavy dependencies" principle (sed piping is complexity)

### Alternative 2: Bash Logging Libraries

**Libraries Evaluated**:
1. **fredpalmer/log4bash** - Functions like `log_info`, `log_warning`, `log_error`
2. **negrel/log4bash** - Minimal one-file library with log levels
3. **Zordrak/bashlog** - Supports syslog, file logging, JSON output
4. **klhochhalter/bashlog** - 8 log levels, file/STDERR/syslog support

**Rejected Because**:
- **Additional dependency**: External libraries not currently in project
- **Unclear JSON support**: Most focus on text logging, not structured JSON
- **Overkill for requirements**: We need ~50 lines of code, not 500+ line library
- **Maintenance risk**: External dependencies can break or become unmaintained
- **Violates project philosophy**: AGENTS.md emphasizes simplicity and minimal files

**From AGENTS.md**:
> Keep it simple - resist over-engineering
> No Python backends, no web frameworks, no complex dependencies

### Alternative 3: No Structured Logging (Status Quo)

**Current implementation** in `scripts/local-ci/run.sh`:
```bash
echo "Running local CI/CD..."
echo "Linting..."
cd web && npx prettier --check .
echo "Testing..."
cd web && npx mocha src/tests/*.test.js
```

**Rejected Because**:
- **Violates FR-010**: "MUST provide structured logging... in machine-parseable format (JSON)"
- **Violates Principle III**: "Structured Observability" from constitution
- **Critical violation #7**: Identified in `plan.md` as blocking issue
- No timestamps, no error tracking, no machine parseability
- Cannot debug failures or monitor pipeline health

## Implementation Notes

### Log Schema

**Standard log entry**:
```json
{
  "timestamp": "2025-10-19T14:30:54.847Z",
  "level": "info",
  "step": "lint",
  "message": "Starting prettier check"
}
```

**Extended log entry with extra fields**:
```json
{
  "timestamp": "2025-10-19T14:35:50.799Z",
  "level": "info",
  "step": "deploy",
  "message": "Deployment successful",
  "url": "https://example.com",
  "duration": 45
}
```

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| `info` | Normal operation | "Starting lint check" |
| `success` | Successful completion | "All tests passed" |
| `warn` | Non-critical issues | "3 tests skipped" |
| `error` | Critical failures | "Build failed: missing dependency" |

### Timestamp Format

**ISO 8601 with milliseconds and UTC**:
```bash
date -u +%Y-%m-%dT%H:%M:%S.%3NZ
# Example: 2025-10-19T14:30:54.847Z
```

**Rationale**:
- ISO 8601 standard for machine parsing
- UTC avoids timezone ambiguity
- Milliseconds for precise timing (3-digit precision via `%3N`)
- `Z` suffix indicates UTC timezone

**Command breakdown**:
- `-u`: Use UTC timezone
- `%Y-%m-%d`: Date in YYYY-MM-DD format
- `T`: ISO 8601 separator
- `%H:%M:%S`: Time in HH:MM:SS format
- `.%3N`: Milliseconds (truncate nanoseconds to 3 digits)
- `Z`: Zulu time (UTC) indicator

### Log Output Strategy

**Dual output: STDOUT + File**:
```bash
#!/bin/bash
source "$(dirname "$0")/lib/logger.sh"

# Log file with timestamp
LOG_FILE="$(dirname "$0")/../../logs/ci-$(date +%Y%m%d-%H%M%S).json"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log to both STDOUT and file
log_dual() {
  local entry
  entry=$(log_json "$@")
  echo "$entry" | tee -a "$LOG_FILE"
}

# Example usage
log_dual "info" "lint" "Starting prettier check"
```

**Rationale**:
- STDOUT: Real-time feedback for developer
- File: Permanent record for debugging
- `tee -a`: Append to file while showing on screen
- Timestamped filename prevents collisions

### Log File Management

**Simple time-based retention** (keep last 30 days):

```bash
#!/bin/bash
# scripts/local-ci/lib/cleanup-logs.sh

LOG_DIR="$(dirname "$0")/../../logs"
RETENTION_DAYS=30

# Delete logs older than retention period
find "$LOG_DIR" -name "ci-*.json" -type f -mtime +$RETENTION_DAYS -delete

# Optional: Log cleanup action
echo "Cleaned up logs older than $RETENTION_DAYS days"
```

**Call from CI script**:
```bash
# At the end of scripts/local-ci/run.sh
"$(dirname "$0")/lib/cleanup-logs.sh"
```

**Rationale**:
- **30 days** is standard for development logs (per web search on retention policies)
- Simple `find -mtime` command, no external tools
- Automatic cleanup prevents disk space issues
- Longer retention (90+ days) only needed for compliance/security logs

**Alternative considered**: Log rotation by count (keep last 50 runs)
- **Rejected**: Time-based is simpler and more predictable
- With daily runs, 30 days ≈ 30 files, manageable size

### Error Handling

**Exit on error + log capture**:
```bash
#!/bin/bash
set -euo pipefail  # Exit on error

source "$(dirname "$0")/lib/logger.sh"

LOG_FILE="logs/ci-$(date +%Y%m%d-%H%M%S).json"
mkdir -p logs

log_step() {
  local step=$1
  local command=$2
  local output
  local exit_code

  log_json "info" "$step" "Starting $step" | tee -a "$LOG_FILE"

  if output=$($command 2>&1); then
    exit_code=$?
    log_json "success" "$step" "Completed successfully" | tee -a "$LOG_FILE"
    return 0
  else
    exit_code=$?
    log_json "error" "$step" "Failed with exit code $exit_code" \
      "{\"exit_code\":$exit_code,\"output\":\"${output//\"/\\\"}\"}" | tee -a "$LOG_FILE"
    return $exit_code
  fi
}

# Usage
log_step "lint" "cd web && npx prettier --check ."
log_step "test" "cd web && npx mocha src/tests/*.test.js"
```

## Best Practices for Implementation

### 1. Single Responsibility

**Logger library** (`lib/logger.sh`):
- Only handles JSON formatting
- No business logic
- Reusable across all scripts

**CI script** (`run.sh`):
- Orchestrates pipeline steps
- Uses logger library
- Handles error logic

### 2. Validation

**Test log output is valid JSON**:
```bash
# In CI script
source "$(dirname "$0")/lib/logger.sh"

# Test logging function
test_log=$(log_json "info" "test" "Test message")
if echo "$test_log" | jq . > /dev/null 2>&1; then
  echo "✓ Logger produces valid JSON"
else
  echo "✗ Logger validation failed" >&2
  exit 1
fi
```

### 3. Consistent Field Naming

**Use lowercase snake_case for field names**:
```json
{
  "timestamp": "2025-10-19T14:30:54.847Z",
  "level": "info",
  "step_name": "lint",
  "exit_code": 0,
  "duration_ms": 1234
}
```

**Avoid**:
- camelCase: `exitCode`, `durationMs`
- UPPER_CASE: `EXIT_CODE`
- Mixed styles: `stepName`, `exit_code`

### 4. Avoid Logging Secrets

**Filter sensitive patterns**:
```bash
# In logger.sh
log_json() {
  local level=$1
  local step=$2
  local message=$3

  # Redact common secret patterns
  message=$(echo "$message" | sed 's/ghp_[a-zA-Z0-9]\{36\}/[GITHUB_TOKEN]/g')
  message=$(echo "$message" | sed 's/sk-[a-zA-Z0-9]\{48\}/[API_KEY]/g')

  jq -nc \
    --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" \
    --arg level "$level" \
    --arg step "$step" \
    --arg message "$message" \
    '{timestamp: $timestamp, level: $level, step: $step, message: $message}'
}
```

## Performance Optimization (If Needed)

**Current implementation is sufficient** for < 5 minute pipeline, but if performance becomes critical:

### Option 1: Background Logging

```bash
# Non-blocking log writes
log_json "info" "test" "Message" >> "$LOG_FILE" &
```

**Trade-off**: Logs may not be written if script crashes

### Option 2: Batch Logging

```bash
# Accumulate logs in memory, write at end
LOGS=()
LOGS+=("$(log_json "info" "lint" "Starting")")
LOGS+=("$(log_json "success" "lint" "Done")")

# Write all at once
printf "%s\n" "${LOGS[@]}" > "$LOG_FILE"
```

**Trade-off**: No real-time output

### Option 3: Conditional Structured Logging

```bash
# Simple output during run
echo "Running lint..."

# JSON summary at end
log_json "info" "pipeline" "Completed" \
  '{"duration":120,"steps":5,"failures":0}' >> "$LOG_FILE"
```

**Trade-off**: Less detailed logs

**Recommendation**: Start with synchronous logging. Only optimize if profiling shows logging as bottleneck.

## Testing Strategy

### Unit Tests for Logger

**Test file**: `scripts/local-ci/lib/logger.test.sh`

```bash
#!/bin/bash

source "$(dirname "$0")/logger.sh"

# Test 1: Valid JSON output
test_valid_json() {
  local output
  output=$(log_json "info" "test" "message")
  echo "$output" | jq . > /dev/null 2>&1 || {
    echo "FAIL: Invalid JSON output"
    return 1
  }
  echo "PASS: Valid JSON output"
}

# Test 2: Special characters
test_special_chars() {
  local output
  output=$(log_json "info" "test" 'Message with "quotes" and \backslashes')
  echo "$output" | jq . > /dev/null 2>&1 || {
    echo "FAIL: Special characters broke JSON"
    return 1
  }
  echo "PASS: Special characters handled"
}

# Test 3: Required fields
test_required_fields() {
  local output
  output=$(log_json "info" "test" "message")

  echo "$output" | jq -e '.timestamp' > /dev/null || return 1
  echo "$output" | jq -e '.level' > /dev/null || return 1
  echo "$output" | jq -e '.step' > /dev/null || return 1
  echo "$output" | jq -e '.message' > /dev/null || return 1

  echo "PASS: All required fields present"
}

# Run tests
test_valid_json
test_special_chars
test_required_fields
```

### Integration Test

**Verify CI script produces valid log file**:

```bash
#!/bin/bash
# tests/test-ci-logging.sh

# Run CI script
./scripts/local-ci/run.sh

# Find most recent log file
LOG_FILE=$(ls -t logs/ci-*.json | head -1)

# Validate entire log file
if jq -s . "$LOG_FILE" > /dev/null 2>&1; then
  echo "✓ CI log file contains valid JSON"
else
  echo "✗ CI log file contains invalid JSON"
  exit 1
fi

# Check for required log levels
if grep -q '"level":"error"' "$LOG_FILE"; then
  echo "✓ Error logging works"
fi

if grep -q '"level":"success"' "$LOG_FILE"; then
  echo "✓ Success logging works"
fi
```

## References

### Web Search Results

1. **Structured Logging Best Practices** (Uptrace, 2025)
   - Use structured formats (JSON/key-value pairs)
   - ISO 8601 timestamps
   - Flatten nested objects
   - Uniform data types per field

2. **JSON Logging bash scripts** (DEV Community, 2024)
   - Bash output formatted with message, log levels, timestamps
   - Error logs streamed to temp file, formatted, redirected to stdout
   - Use jq with `--monochrome-output`, `--compact-output`, `--raw-output`

3. **Structured Logging in Shell Script with jq** (Medium, 2024)
   - jq takes care of escaping, produces valid single-line JSON
   - Redirect output to JSON encoder co-process automatically

4. **Performance Considerations**
   - JSON logging requires 1.5-2x more storage than plain text
   - Medium app (1M requests/day): 1-5GB logs/day before compression
   - GZIP compression reduces by 60-80%
   - jq streaming parser sacrifices speed for memory efficiency

5. **Log Retention Policies** (Sematext, GitLab, Coralogix)
   - Different retention for different log types
   - Development logs: 7-30 days typical
   - Security logs: 90+ days for compliance
   - Use multiple indexes for different retention periods
   - Plan for load peaks (errors increase log volume)

### Performance Testing

**Benchmarks** (100 iterations each):
- jq: 0.469s (baseline)
- printf: 0.128s (3.7x faster, but breaks on special chars)
- Custom bash: 0.134s (3.5x faster, but breaks on special chars)

**Validation testing**:
- jq: 100% valid JSON with all special characters
- printf: Breaks with quotes, backslashes, newlines
- Custom bash: Same issues as printf

### System Information

- **jq version**: 1.7 (installed at `/usr/bin/jq`)
- **Bash version**: 4.0+ (supports arrays, functions)
- **Platform**: Linux (date command with `%3N` for milliseconds)

## Conclusion

**jq-based logging is the clear choice** for this project:

1. **Correctness**: Guaranteed valid JSON, handles all edge cases
2. **Performance**: Negligible overhead for CI/CD use case (0.2s in 300s budget)
3. **Simplicity**: Single-file library (~50 lines), no external dependencies
4. **Maintainability**: Easy to understand, test, and extend
5. **Compliance**: Meets FR-010 and Principle III requirements

**Next Steps** (for Phase 2 implementation):
1. Create `scripts/local-ci/lib/logger.sh` with jq-based functions
2. Update `scripts/local-ci/run.sh` to use structured logging
3. Add log cleanup script (`lib/cleanup-logs.sh`)
4. Write unit tests (`lib/logger.test.sh`)
5. Add integration test to verify CI produces valid JSON logs

---

**Document Status**: ✅ Complete - Ready for Phase 2 implementation
**Review Date**: 2025-10-19
**Approved By**: Research phase (auto-approved per plan.md workflow)
