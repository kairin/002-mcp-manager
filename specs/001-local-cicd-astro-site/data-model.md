# Data Model: Local CI/CD for Astro Site

**Feature**: 001-local-cicd-astro-site | **Date**: 2025-10-19 | **Status**: Phase 1 Design

---

## Overview

This document defines data entities for the local CI/CD system. As a **script-based automation system**, the data model focuses on:

1. Structured JSON log entries
2. Environment configuration (`.env` files)
3. CI/CD pipeline execution state
4. Deployment state (for rollback capability)

---

## Entity 1: CI/CD Log Entry

**Purpose**: Structured JSON log record for observability (FR-010, Principle III)

**Schema**:
```json
{
  "timestamp": "2025-10-19T14:30:54.847Z",  // ISO 8601 UTC with milliseconds
  "level": "info",                          // info|success|warn|error
  "step": "lint",                           // Pipeline step name
  "message": "Starting prettier check",     // Human-readable description
  "duration": 2.3,                          // Optional: seconds
  "exitCode": 0,                            // Optional: command exit code
  "error": {                                // Optional: error details
    "code": "PRETTIER_FAIL",
    "fixAttempted": true,
    "fixSucceeded": false
  }
}
```

**Pipeline Steps**: `init`, `env-check`, `lint`, `test-unit`, `test-integration`, `test-e2e`, `build`, `cleanup`, `complete`

**Storage**: `logs/ci-YYYYMMDD-HHMMSS.json` (newline-delimited JSON), 30-day retention

---

## Entity 2: Environment Configuration

**Purpose**: Environment-specific settings with secrets protection (FR-009, Principle IV)

**Files**:
- `.env.example` - Template (committed to git)
- `.env.local` - Development settings (gitignored)
- `.env.production` - Production settings (gitignored)

**Schema**:
```bash
NODE_ENV=development                        # development|production
ASTRO_TELEMETRY_DISABLED=1                  # 0|1
PUBLIC_SITE_URL=http://localhost:4321       # Valid HTTP/HTTPS URL
GITHUB_TOKEN=                               # Optional: GitHub API access
CI_LOG_LEVEL=info                           # debug|info|warn|error
```

**Secret Detection Patterns** (blocked by pre-commit hook):
- `GITHUB_TOKEN=gh[ps]_[A-Za-z0-9]{36,}`
- `API_KEY=sk_live_.*`
- `AWS_SECRET_ACCESS_KEY=.*`
- `PRIVATE_KEY=.*BEGIN.*PRIVATE KEY.*`

---

## Entity 3: CI/CD Pipeline Run

**Purpose**: Track pipeline execution, metrics, and compliance with NFR-003 (<5 min duration)

**Schema**:
```json
{
  "runId": "20251019-143054",
  "startTime": "2025-10-19T14:30:54.847Z",
  "endTime": "2025-10-19T14:33:22.184Z",
  "status": "success",                       // running|success|failed|aborted
  "triggeredBy": "developer",
  "gitBranch": "001-local-cicd-astro-site",
  "gitCommit": "787df1e",
  "steps": [
    {
      "step": "lint",
      "status": "success",
      "duration": 2.3,
      "exitCode": 0
    }
  ],
  "metrics": {
    "totalDuration": 147.3,                  // MUST be <300s (NFR-003)
    "testsPassed": 24,
    "testsFailed": 0,
    "lintErrors": 0,
    "lintFixed": 0
  }
}
```

**State Transitions**:
```
pending → running → success|failed|aborted
```

**Storage**: Appended as final entry to pipeline log file

---

## Entity 4: Deployment State

**Purpose**: Enable automatic rollback on deployment failure (FR-011)

**Schema**:
```json
{
  "currentDeployment": "deploy-20251019-140500",
  "lastKnownGood": "deploy-20251019-140500",
  "deployments": [
    {
      "deploymentId": "deploy-20251019-140500",
      "timestamp": "2025-10-19T14:05:00.000Z",
      "gitCommit": "c5757e0",
      "status": "success",
      "url": "https://kairin.github.io/002-mcp-manager",
      "lighthouseScore": 94                  // Must be ≥90 (NFR-002)
    }
  ],
  "rollbacks": [
    {
      "timestamp": "2025-10-19T15:05:00.000Z",
      "failedDeploymentId": "deploy-20251019-150312",
      "rolledBackTo": "deploy-20251019-140500",
      "reason": "GitHub Pages deployment failed: 404 error",
      "triggeredBy": "automatic"
    }
  ]
}
```

**Rollback Triggers**:
1. Deployment exits with non-zero code
2. Post-deployment health check fails (404/500)
3. Lighthouse score < 80 (configurable)

**Storage**: `.github/deployment-state.json` (updated atomically on each deployment)

---

## Entity 5: Secret Scan Result

**Purpose**: Pre-commit hook secret detection output (FR-009, Principle IV)

**Schema**:
```json
{
  "timestamp": "2025-10-19T14:25:30.123Z",
  "scanType": "pre-commit",
  "filesScanned": 3,
  "secretsFound": 1,
  "blockCommit": true,
  "findings": [
    {
      "file": ".env.local",
      "lineNumber": 4,
      "ruleId": "github-pat",
      "description": "GitHub Personal Access Token",
      "match": "GITHUB_TOKEN=ghp_**********************",  // Redacted
      "severity": "high"
    }
  ]
}
```

**Blocking Rule**: `blockCommit = true` if any finding has `severity: "high"`

**Storage**: Ephemeral (displayed to user, not persisted)

---

## Data Flow

```
Developer Commit
      │
      ▼
┌─────────────────┐
│ Pre-Commit Hook │──▶ Secret Scan Result (Entity 5)
│ (Husky+Gitleaks)│    ├─ Block if secrets found
└────────┬────────┘    └─ Allow if clean
         │ (if pass)
         ▼
┌─────────────────────────────┐
│ Local CI/CD Pipeline        │
│ (scripts/local-ci/run.sh)   │
├─────────────────────────────┤
│ Creates: Pipeline Run (E3)  │
│ Writes: Log Entries (E1)    │
│ Reads: Env Config (E2)      │
│                             │
│ Steps: lint → test → build  │
└────────┬────────────────────┘
         │ (if success)
         ▼
     git push
         │
         ▼
┌──────────────────────────────────┐
│ GitHub Actions Deployment        │
│ (.github/workflows/deploy.yml)   │
├──────────────────────────────────┤
│ Reads: web/dist/ (pre-built)     │
│ Writes: Deployment State (E4)    │
│                                   │
│ On success: Update lastKnownGood │
│ On failure: Rollback to last good│
└───────────┬──────────────────────┘
            │
            ▼
    Live Website (GitHub Pages)
```

---

## Validation Rules Summary

| Entity | Key Validation | Enforcement |
|--------|---------------|-------------|
| Log Entry | Valid ISO 8601 timestamp | Logger library |
| Log Entry | `level` ∈ {info, success, warn, error} | Runtime check |
| Env Config | `NODE_ENV` ∈ {development, production} | Startup validation |
| Env Config | No secrets in committed files | Pre-commit hook |
| Pipeline Run | `totalDuration` < 300s (NFR-003) | Warning if exceeded |
| Deployment | `lighthouseScore` ≥ 90 (NFR-002) | Warning if below |
| Deployment | `lastKnownGood` references valid deploy | State validation |
| Secret Scan | Block if any `severity: high` | Gitleaks exit code |

---

## Performance Estimates

**Log Storage Growth**:
- Per run: ~50 logs × 500 bytes = 25KB
- Per day: 10 runs × 25KB = 250KB
- 30-day retention: ~7.5MB total (negligible)

**Deployment State**:
- File size: <10KB JSON
- Updates: 1-10 times per day
- Atomic writes via `mv temp deployment-state.json`

---

## Summary

This data model defines **5 entities** supporting core requirements:

1. **Log Entry** → FR-010 (structured observability)
2. **Env Config** → FR-009 (secrets management)
3. **Pipeline Run** → NFR-003 (< 5min duration tracking)
4. **Deployment State** → FR-011 (rollback capability)
5. **Secret Scan** → FR-009 (pre-commit security)

All use **JSON** for structured data with clear validation rules.

**Next**: See `contracts/` for module interface specifications.
