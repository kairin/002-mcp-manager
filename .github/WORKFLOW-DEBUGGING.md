# Workflow Debugging Quick Reference

## Using gh CLI to Diagnose Issues

### 1. List and Filter Workflows

```bash
# List recent runs
gh run list --limit 20

# List failed runs
gh run list --status failure --limit 10

# List by specific workflow
gh run list --workflow deploy.yml --limit 20

# Filter by branch
gh run list --branch main --limit 10

# Show advanced status info
gh run list --json number,name,status,conclusion,createdAt --limit 10
```

### 2. Get Detailed Run Information

```bash
# Get full run details
gh run view <run-id>

# View with JSON output (machine readable)
gh run view <run-id> --json status,conclusion,headBranch

# Get logs for a specific run
gh run view <run-id> --log

# Get logs for a specific job
gh run view <run-id> --log | grep "job-name"
```

### 3. Debug Specific Failures

```bash
# Get errors from a failed run
gh run view <run-id> --log 2>&1 | grep -i "error\|failed"

# Get last 100 lines of logs (most error info at end)
gh run view <run-id> --log 2>&1 | tail -100

# Look for syntax errors
gh run view <run-id> --log 2>&1 | grep -E "syntax|error:|failed|Error"

# Get job logs by name
gh run view <run-id> --log | grep -A 50 "job-name"
```

### 4. Re-run and Monitor

```bash
# Re-run all jobs
gh run rerun <run-id>

# Re-run only failed jobs
gh run rerun <run-id> --failed

# Check status in real-time
watch 'gh run list --limit 5'

# Cancel a running workflow
gh run cancel <run-id>
```

### 5. Analyze Patterns

```bash
# Get failure statistics
gh run list --status failure --limit 50 --json conclusion | \
  jq 'group_by(.conclusion) | map({conclusion: .[0].conclusion, count: length})'

# Find most common errors
gh run list --status failure --limit 30 --json number | \
  jq '.[] | .number' | while read run; do
    echo "=== Run $run ==="
    gh run view $run --log 2>&1 | grep -i error | head -2
  done

# Check for recent improvements
gh run list --all --limit 100 --json conclusion | \
  jq '[.[] | select(.conclusion | IN("success", "failure"))] | 
      group_by(.conclusion) | map({status: .[0].conclusion, count: length})'
```

## Common Errors and Solutions

### Error: "syntax error, unexpected INVALID_CHARACTER"

**From jq:**
```
jq: error: syntax error, unexpected INVALID_CHARACTER (Unix shell quoting issues?)
```

**Cause:** Mixed shell variable expansion with jq variables

**Fix:**
```bash
# ❌ WRONG
jq --arg var ${{ github.sha }} ...

# ✅ RIGHT
SHA=${{ github.sha }}
jq --arg sha "$SHA" ...
```

**Prevention:** Run validation script
```bash
bash .github/scripts/validate-workflow.sh
```

---

### Error: "Status code: 404"

**From Lighthouse or curl:**
```
Lighthouse was unable to reliably load the page you requested
(Status code: 404)
```

**Cause:** URL not accessible or not ready yet

**Fix:**
1. Check URL format: `https://owner.github.io/repo/`
2. Add wait/retry logic
3. Verify GitHub Pages is enabled

---

### Error: "failed to push: repository not found"

**Cause:** Authentication issue or wrong remote

**Fix:**
```bash
# Check remote
git remote -v

# Verify gh CLI auth
gh auth status

# Re-authenticate if needed
gh auth login
```

---

## Validation Before Committing Workflow Changes

```bash
# 1. Run local validation
bash .github/scripts/validate-workflow.sh

# 2. Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yml'))"

# 3. Verify shell scripts work locally
bash -n .github/scripts/*.sh

# 4. Test in isolated environment
docker run -it ubuntu:latest bash < .github/scripts/deploy.sh
```

## Setting Up Monitoring

### Create a simple dashboard
```bash
#!/bin/bash
# Monitor workflow health
while true; do
  clear
  echo "=== Workflow Health Dashboard ==="
  echo "Recent runs:"
  gh run list --limit 5 --json name,status,conclusion,createdAt
  echo ""
  echo "Failed (last 24h):"
  gh run list --status failure --limit 5 --json name,createdAt
  echo ""
  sleep 30
done
```

### Set up alerts
```bash
#!/bin/bash
# Alert on repeated failures
RECENT_FAILURES=$(gh run list --status failure --limit 10 \
  --json createdAt | \
  jq '[.[] | select(.createdAt > now - 3600)] | length')

if [ "$RECENT_FAILURES" -gt 5 ]; then
  echo "ALERT: $RECENT_FAILURES failures in last hour"
  gh run list --status failure --limit 5 --json name,createdAt
fi
```

## Quick Troubleshooting Steps

1. **Workflow failing on every push?**
   - Check recent commits: `git log --oneline -5`
   - View latest failed run: `gh run list --limit 1 | head -1`
   - Get error details: `gh run view <run-id> --log | tail -50`

2. **Don't know which workflow is failing?**
   - List all: `gh run list --limit 20`
   - Filter by status: `gh run list --status failure`
   - Check specific one: `gh run view <run-id>`

3. **Need to see full error context?**
   - Download logs: `gh run download <run-id>`
   - Check full log file: `cat run-<run-id>-<job-id>.txt`

4. **Want to rollback a change?**
   - Find the problematic commit: `git log --oneline`
   - Revert it: `git revert <commit-sha>`
   - Push: `git push origin main`

5. **Workflow was working, now it's not?**
   - Check recent changes: `git diff HEAD~5`
   - Review workflow file: `.github/workflows/deploy.yml`
   - Compare to last success: `git show <last-working-sha>:.github/workflows/deploy.yml`

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [gh CLI Reference](https://cli.github.com/manual/)
- [jq Manual](https://stedolan.github.io/jq/manual/)
- [YAML Specification](https://yaml.org/)

---

**Last Updated**: 2025-10-22  
**For Issues**: See docs/WORKFLOW-FAILURE-ANALYSIS.md
