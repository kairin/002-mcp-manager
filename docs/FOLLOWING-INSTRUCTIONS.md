# Following Instructions Guide

> **Why AGENTS.md Compliance is Critical**

## Overview

This guide explains why following the instructions in [AGENTS.md](../AGENTS.md) (also accessible as CLAUDE.md, GEMINI.md) is essential for successful development on this project.

## The AGENTS.md File

AGENTS.md is the **PRIMARY instruction document** for all AI assistants working on this repository. It contains:

- Non-negotiable requirements
- Branch management strategies
- GitHub Pages deployment rules
- Security & privacy standards
- Python development standards
- MCP server management protocols

## Why Compliance Matters

### 1. Branch Preservation (MANDATORY)
- **NEVER DELETE BRANCHES** without explicit permission
- All branches contain valuable development history
- Branch naming follows `YYYYMMDD-HHMMSS-type-description` format

### 2. GitHub Pages Deployment
- **MUST BUILD** before committing website changes
- Failure to build causes 404 errors on live site
- Pre-commit hook automates this process

### 3. Security Standards
- **NO SECRETS** in repository
- Environment variables for sensitive data
- Templates only, never actual API keys

### 4. Python Development
- **UV-FIRST ONLY** - No pip install allowed
- Python 3.11+ required
- Full type annotations mandatory

## Real-World Impact

The [MarkItDown Case Study](../CHANGELOG.md#120---2025-09-25) demonstrates what happens when UV-first requirements are ignored:

- ❌ ModuleNotFoundError for installed packages
- ❌ Command not found errors
- ❌ MCP server configuration failures

Following instructions exactly prevented these issues.

## Quick Compliance Checklist

Before any commit:

- [ ] Read AGENTS.md requirements
- [ ] Follow branch naming convention
- [ ] Use UV for all Python operations
- [ ] Build website if docs/ changed
- [ ] No secrets in code
- [ ] Type annotations present

## Learn More

- [AGENTS.md](../AGENTS.md) - Complete instruction set
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Common issues
- [CHANGELOG.md](../CHANGELOG.md) - Historical examples