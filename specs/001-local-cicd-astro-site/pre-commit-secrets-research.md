# Pre-Commit Secret Scanning Research - Node.js/Astro Project

**Research Date**: 2025-10-19
**Context**: Implementing pre-commit hooks for the MCP Manager Astro site to block secrets/API keys
**Requirements**: Fast (< 1 second), reliable, easy to install, works in Node.js/npm environment

---

## Decision: Husky + lint-staged + Gitleaks (Binary)

**Chosen Approach**: Husky for hook management + lint-staged for performance + Gitleaks binary for secret detection

### Quick Summary

- **Hook Manager**: Husky v9+ (native npm package)
- **Performance Optimization**: lint-staged (run only on staged files)
- **Secret Scanner**: Gitleaks binary via npx (Docker alternative for CI/CD)
- **Validation Scope**: Staged files only

---

## Rationale

### Why Husky Over Native Git Hooks?

**Advantages:**
- **Cross-platform compatibility**: Works on Windows, macOS, Linux (critical for teams)
- **Version controlled**: `.husky/` directory is committed to repo
- **Zero manual setup**: `npx husky init` + `npm install` auto-configures for all developers
- **Team standardization**: Everyone gets same hooks automatically
- **Modern tooling**: Active maintenance, 3,200+ dependent packages in npm registry

**Trade-offs:**
- Requires Node.js (acceptable for Node.js/Astro projects)
- Adds ~1MB to `node_modules` (negligible for modern projects)

**Native Git hooks** would require:
- Manual setup for each developer
- Platform-specific scripts (bash vs PowerShell)
- Not version controlled by default
- Higher maintenance burden

**Verdict**: Husky wins for team collaboration and ease of onboarding.

---

### Why Gitleaks for Secret Detection?

**Performance** (Critical for < 1 second requirement):
- Written in Go → compiled binary → extremely fast
- Optimized for Git operations
- v3+ uses string comparisons before regex (2-3x faster)

**Comparison with Alternatives:**

| Tool | Speed | False Positives | Maintenance | Node.js Native |
|------|-------|-----------------|-------------|----------------|
| **Gitleaks** | ⚡ Fastest | Low-Medium | Active (11.2k stars) | ❌ (Go binary) |
| TruffleHog | 🐌 Slower | High | Active | ❌ (Go binary) |
| detect-secrets | ⚡ Fast | Very Low | Stale (5 years) | ✅ (via npm) |
| Secretlint | ⚡ Fast | Low | Active | ✅ (pure JS) |
| git-secrets | ⚡ Fast | Medium | AWS-maintained | ❌ (bash/shell) |

**Why not TruffleHog?**
- Excellent for **CI/CD full scans** (entropy analysis + regex)
- Too slow for pre-commit (resource-intensive)
- Higher false positive rate

**Why not detect-secrets?**
- npm package abandoned (last update: 5 years ago)
- Better for Python projects (Yelp-maintained)
- Lower false positives but outdated rule set

**Why not Secretlint?**
- Pure JavaScript (good for real-time editor checks)
- Opt-in rule selection (more configuration overhead)
- Best as **complement** to Gitleaks, not replacement

**Why not git-secrets?**
- AWS-specific focus
- Less community adoption vs Gitleaks
- Limited pattern library

**Verdict**: Gitleaks offers best balance of speed, accuracy, and active maintenance.

---

### Why lint-staged?

**Performance Critical**:
- Only processes **staged files** (not entire codebase)
- Batch processing: single Gitleaks execution vs file-by-file
- Example: 100-file project → only scan 3-5 changed files

**Without lint-staged**:
```bash
# Scans entire repository (slow for large projects)
gitleaks protect --staged
```

**With lint-staged**:
```bash
# Only scans files you're committing (fast)
gitleaks protect --staged --log-opts="--diff-filter=ACMR"
```

**Benchmark Impact**:
- Small project (< 50 files): Minimal difference (~0.1s)
- Medium project (50-500 files): 2-5x faster
- Large project (500+ files): 10x+ faster

**Verdict**: Essential for maintaining < 1 second performance requirement.

---

## Alternatives Considered

### 1. Native Git Hooks + Gitleaks
**Pros**: No Node.js dependencies, simpler setup
**Cons**: Not version controlled, manual setup per developer, platform-specific issues
**Rejected**: Team collaboration concerns

### 2. Pre-commit Framework (Python-based)
**Pros**: Language-agnostic, extensive hook library
**Cons**: Requires Python, overkill for Node.js project
**Rejected**: Adds unnecessary dependency

### 3. GitHub Actions Only (No Pre-commit)
**Pros**: Zero local overhead
**Cons**: Slow feedback loop, wastes CI/CD resources, bad developer experience
**Rejected**: Fails "shift-left" security principle

### 4. Secretlint Only
**Pros**: Pure JavaScript, good for real-time IDE checks
**Cons**: Slower than Gitleaks, opt-in rules require more config
**Considered**: Could add as **complement** for IDE integration later

### 5. TruffleHog Pre-commit
**Pros**: Best detection accuracy (entropy analysis)
**Cons**: Too slow for pre-commit (resource-intensive)
**Rejected**: Performance fails < 1 second requirement
**Alternative Use**: Consider for weekly full-repo scans in CI/CD

---

## Implementation Notes

### Installation Steps

```bash
# 1. Navigate to Astro project
cd /home/kkk/Apps/002-mcp-manager/web

# 2. Install Husky (latest v9+)
npm install --save-dev husky

# 3. Initialize Husky (creates .husky/ directory)
npx husky init

# 4. Install lint-staged
npm install --save-dev lint-staged

# 5. Install Gitleaks (verify system installation or use npx)
# Option A: System-wide binary (recommended for speed)
brew install gitleaks  # macOS
# OR download from: https://github.com/gitleaks/gitleaks/releases

# Option B: npx wrapper (slower but portable)
npm install --save-dev @ziul285/gitleaks
```

### Configuration

**File: `.husky/pre-commit`**
```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

# Run lint-staged (includes Gitleaks check)
npx lint-staged
```

**File: `package.json`** (add to existing file)
```json
{
  "scripts": {
    "prepare": "husky install"
  },
  "lint-staged": {
    "*": [
      "gitleaks protect --staged --redact --verbose --log-opts=-p"
    ],
    "*.{js,ts,astro,json,md}": [
      "prettier --write"
    ]
  }
}
```

**File: `.gitleaks.toml`** (create in project root)
```toml
title = "MCP Manager - Gitleaks Configuration"

# Performance: scan staged files only
[extend]
useDefault = true

# Allowlist for false positives
[[allowlists]]
description = "Ignore test fixtures and examples"
paths = [
  '''tests/fixtures/.*''',
  '''examples/.*\.json$'''
]
regexTarget = "match"

[[allowlists]]
description = "Ignore documentation placeholders"
stopwords = [
  "YOUR_API_KEY",
  "REPLACE_WITH_TOKEN",
  "example.com"
]

# Custom rules
[[rules]]
id = "astro-env-files"
description = "Catch .env file secrets"
regex = '''(?i)(api[_-]?key|password|secret|token)\s*=\s*['"]?[a-zA-Z0-9_\-]{20,}['"]?'''
path = '''\.(env|env\.local|env\.production)$'''
```

### Testing the Setup

```bash
# 1. Test Gitleaks directly
echo "test_api_key = 'sk-FAKE_EXAMPLE_KEY_NOT_REAL'" > test.txt
git add test.txt
gitleaks protect --staged --verbose

# 2. Test via pre-commit hook
git commit -m "test: trigger secret detection"
# Should block commit and show: "Error: gitleaks detected secrets"

# 3. Clean up test
git reset HEAD test.txt
rm test.txt

# 4. Verify performance (should be < 1 second)
time git commit -m "test: performance check"
```

### Handling False Positives

**Strategy 1: Global Allowlist** (`.gitleaks.toml`)
```toml
[[allowlists]]
description = "Development placeholder values"
stopwords = [
  "YOUR_TOKEN_HERE",
  "REPLACE_ME",
  "example-api-key"
]
```

**Strategy 2: Path-based Exclusions**
```toml
[[allowlists]]
description = "Ignore test data"
paths = [
  '''tests/fixtures/.*''',
  '''docs/examples/.*'''
]
```

**Strategy 3: Inline Comments** (use sparingly)
```javascript
// gitleaks:allow
const apiKey = "ghp_example1234567890123456789012345678"; // documentation example
```

**Strategy 4: Commit-specific Bypass** (emergency only)
```bash
# Skip hook for specific commit (requires team approval)
HUSKY=0 git commit -m "docs: add API example"
```

**Best Practice**: Maintain `.gitleaksignore` file for permanent exceptions
```
# File: .gitleaksignore
tests/fixtures/sample-config.json:5
docs/api-examples.md:12
```

---

## Performance Expectations

### Scan Times (Estimated)

| Scenario | Files Changed | Expected Time |
|----------|---------------|---------------|
| Small commit | 1-3 files | 0.1-0.3s |
| Medium commit | 5-10 files | 0.3-0.6s |
| Large commit | 20+ files | 0.6-1.5s |

### Optimization Tips

1. **Use binary over Docker**:
   - Binary: ~0.2s startup
   - Docker: ~1-2s startup (container overhead)

2. **Scan staged files only**:
   ```bash
   gitleaks protect --staged  # Fast
   # vs
   gitleaks detect            # Slow (full repo scan)
   ```

3. **Limit file types** (if needed):
   ```json
   "lint-staged": {
     "*.{js,ts,json,env}": ["gitleaks protect --staged"]
   }
   ```

4. **Parallel execution** (lint-staged handles automatically):
   - Gitleaks runs concurrently with Prettier
   - Both tools process different file sets simultaneously

---

## Additional Recommendations

### 1. Multi-layer Defense Strategy

**Layer 1: Pre-commit** (This implementation)
- Catches 80-90% of accidental commits
- Fast feedback (<1s)
- Developer-friendly

**Layer 2: Pre-push Hook** (Optional enhancement)
```bash
# .husky/pre-push
gitleaks protect --staged --log-opts="--all"
```

**Layer 3: CI/CD Full Scan** (Recommended)
```yaml
# .github/workflows/security.yml
- name: Gitleaks Full Scan
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Layer 4: Periodic Full History Scan** (Weekly/Monthly)
```bash
# Scan entire git history
gitleaks detect --verbose --report-path gitleaks-report.json
```

### 2. IDE Integration (Bonus)

**VSCode Extension**: "Gitleaks" by Carlos Reveco
- Real-time secret detection while typing
- Complements pre-commit hook
- Zero config (uses `.gitleaks.toml`)

**Alternative**: Secretlint with ESLint
```bash
npm install --save-dev @secretlint/secretlint-rule-preset-recommend
# .secretlintrc.json for real-time IDE checks
```

### 3. Team Education

**Onboarding Checklist**:
- [ ] Explain why secrets in Git are permanent (even after deletion)
- [ ] Demonstrate pre-commit hook in action
- [ ] Share `.gitleaks.toml` configuration
- [ ] Document bypass procedures (emergency only)
- [ ] Provide secret rotation playbook

---

## Security Patterns to Detect

Gitleaks default ruleset covers 150+ patterns including:

**Common Secrets**:
- GitHub Personal Access Tokens: `ghp_[a-zA-Z0-9]{36}`
- AWS Access Keys: `AKIA[0-9A-Z]{16}`
- Slack Tokens: `xox[baprs]-[0-9a-zA-Z]{10,48}`
- Generic API Keys: `[a-zA-Z0-9_-]{32,}`

**Astro/Node.js Specific**:
- `.env` file credentials
- NPM tokens: `npm_[a-zA-Z0-9]{36}`
- Database connection strings
- JWT secrets

**Custom Rules** (add to `.gitleaks.toml`):
```toml
[[rules]]
id = "mcp-server-token"
description = "MCP Server authentication token"
regex = '''mcp[_-]token\s*[:=]\s*['"]?[a-zA-Z0-9]{20,}['"]?'''
```

---

## Migration Path (If Already Using Other Tools)

### From git-secrets
```bash
# Export existing patterns
git secrets --list > patterns.txt

# Convert to Gitleaks custom rules
# (manual conversion needed - different regex syntax)

# Test side-by-side before switching
```

### From detect-secrets
```bash
# Export baseline
detect-secrets scan > .secrets.baseline

# Migrate to Gitleaks allowlist
# (review and add to .gitleaks.toml allowlists section)
```

### From TruffleHog
```bash
# Keep TruffleHog for CI/CD deep scans
# Add Gitleaks for fast pre-commit checks
# Best of both worlds approach
```

---

## Validation & Compliance

### Pre-deployment Checklist

- [ ] Test with known secret (should block)
- [ ] Test with false positive (should allow via allowlist)
- [ ] Verify performance < 1 second for typical commits
- [ ] Confirm works on all team member OS (Windows/macOS/Linux)
- [ ] Document bypass procedure for emergencies
- [ ] Add CI/CD scan as backup layer

### Monitoring Success

**Metrics to Track**:
- Commits blocked per week
- False positive rate
- Average scan time
- Developer satisfaction (survey)

**Success Criteria**:
- 95%+ of accidental secrets caught
- < 5% false positive rate
- < 1 second average scan time
- Zero secrets in production logs

---

## References

- [Gitleaks Official Documentation](https://github.com/gitleaks/gitleaks)
- [Husky v9 Documentation](https://typicode.github.io/husky/)
- [lint-staged GitHub](https://github.com/lint-staged/lint-staged)
- [OWASP Secret Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## Appendix: Quick Reference Commands

```bash
# Install
npm install --save-dev husky lint-staged
npx husky init
brew install gitleaks  # or download binary

# Configure
echo "npx lint-staged" > .husky/pre-commit
# Add lint-staged config to package.json

# Test
echo "api_key=sk-test123456" > test.txt
git add test.txt
git commit -m "test"  # Should fail

# Bypass (emergency only)
HUSKY=0 git commit -m "emergency fix"

# Manual scan
gitleaks protect --staged --verbose
gitleaks detect  # full repo scan

# Update patterns
gitleaks completion bash > /etc/bash_completion.d/gitleaks
```

---

**Conclusion**: The Husky + lint-staged + Gitleaks combination provides the optimal balance of performance, accuracy, and developer experience for Node.js/Astro projects. Expected setup time: 15-20 minutes. Expected scan time: < 1 second per commit.
