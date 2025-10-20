# Quickstart: Local CI/CD for Astro Site

**Feature**: 001-local-cicd-astro-site | **Date**: 2025-10-19 | **Time to Complete**: < 10 minutes (SC-003)

---

## Prerequisites

- **Node.js 18+ LTS** (`node --version`)
- **npm 9+** (`npm --version`)
- **Bash 4.0+** (`bash --version`)
- **jq 1.6+** (`jq --version`) - For JSON logging
- **Git** (`git --version`)

---

## Quick Setup

### 1. Clone & Install (2 min)

```bash
git clone https://github.com/kairin/002-mcp-manager.git
cd 002-mcp-manager/web
npm install
npx playwright install  # E2E test browsers
```

### 2. Configure Environment (1 min)

```bash
cp .env.example .env.local
# Edit .env.local: NODE_ENV=development, PUBLIC_SITE_URL=http://localhost:4321
```

### 3. Setup Pre-Commit Hooks (2 min)

```bash
cd web
npm install --save-dev husky lint-staged
npx husky init
# Install gitleaks: brew install gitleaks (macOS) or download binary
```

### 4. Run Local CI/CD (3 min)

```bash
cd ..  # Back to repo root
./scripts/local-ci/run.sh

# Expected: JSON logs ending with {"level":"success","step":"complete"}
# Exit code 0 = success
```

---

## Daily Workflow

```bash
# 1. Make changes
git checkout -b my-feature
vim web/src/pages/index.astro

# 2. Commit (pre-commit hook scans for secrets)
git add .
git commit -m "feat: add feature"

# 3. Run local CI/CD
./scripts/local-ci/run.sh  # Or use ./scripts/tui/run.sh for interactive menu

# 4. Push (only if CI passes)
git push origin my-feature
```

---

## Common Commands

```bash
# Full pipeline
./scripts/local-ci/run.sh

# Skip tests (faster)
./scripts/local-ci/run.sh --skip-tests

# Verbose output
./scripts/local-ci/run.sh --verbose

# View logs
cat logs/ci-*.json | jq .

# Development server
cd web && npm run dev
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| "jq: command not found" | `brew install jq` (macOS) or `apt-get install jq` (Linux) |
| "Prettier check failed" | Auto-fixed by default, or run `cd web && npx prettier --write .` |
| "Tests failed" | View logs: `cat logs/ci-*.json \| tail -20 \| jq .` |
| Pre-commit hook not running | `chmod +x .husky/pre-commit` |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - safe to push |
| 1 | Lint failure |
| 2 | Test failure |
| 3 | Build failure |
| 4 | Environment validation failure |

---

## Next Steps

1. Read `plan.md` for implementation details
2. Review `contracts/ci-script.contract.md` for full CLI reference
3. Check `data-model.md` for log structure

**Setup complete in < 10 minutes** ✅ | **Understanding in < 30 minutes** ✅
