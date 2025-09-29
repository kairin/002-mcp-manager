# Data Model: Documentation Accuracy and Completeness

## Overview

This feature involves documentation files as the primary entities. No database, API contracts, or programmatic data models are required. This document defines the structure and relationships of documentation artifacts.

## Documentation Entities

### 1. MCP Server Documentation Entry

**Entity**: MCP Server Configuration Reference
**Files**: CLAUDE.md (line 169), README.md (line 176)

**Attributes:**
- Server Name: String (e.g., "github", "context7", "markitdown")
- Server Type: Enum ["stdio", "http"] (MANDATORY)
- Binary Location: String (for stdio type) or URL (for http type)
- Version: String (e.g., "v0.16.0")
- Configuration Example: JSON structure with command/args or url/headers

**Validation Rules:**
- Type MUST match actual server implementation
- stdio type MUST include command field
- http type MUST include url field
- Configuration example MUST follow UV-first structure for stdio servers
- All entries MUST be consistent across CLAUDE.md and README.md

**Current State (INCORRECT):**
```markdown
| github | HTTP | ✅ Global | GitHub API integration and management |
```

**Target State (CORRECT):**
```markdown
| github | stdio | ✅ Global | GitHub API integration and management |
```

**Relationships:**
- Referenced by: CLAUDE.md MCP server table, README.md MCP server overview
- References: ~/.claude.json global configuration
- Depends on: Constitution Principle II (Global Configuration First)

### 2. Compliance Guide Document

**Entity**: FOLLOWING-INSTRUCTIONS.md
**File**: docs/FOLLOWING-INSTRUCTIONS.md (NEW)

**Attributes:**
- Title: String ("Following Instructions: Why AGENTS.md Compliance Matters")
- Sections: Array of Section objects
- Case Studies: Array of CaseStudy objects
- Best Practices: Array of Guideline objects
- Last Updated: ISO 8601 date

**Section Structure:**
1. Introduction (why compliance matters)
2. Constitutional Principles (v1.0.0 reference)
3. Case Study 1: MarkItDown Integration
4. Case Study 2: GitHub MCP Configuration
5. Best Practices for MCP Integration
6. Troubleshooting Patterns

**Case Study Structure:**
- Title: String
- Problem Description: Markdown text
- Root Cause: Markdown text
- Solution: Code example + explanation
- Lessons Learned: Bullet list
- Related Requirements: Array of constitutional principle references

**Validation Rules:**
- Must reference constitution v1.0.0
- All code examples MUST follow UV-first structure
- Case studies MUST include real evidence from CHANGELOG.md
- Links to related documentation MUST be valid relative paths
- Markdown formatting MUST be GitHub-flavored

**Relationships:**
- Referenced by: README.md (line 28)
- References: CHANGELOG.md (v1.2.1), TROUBLESHOOTING.md, constitution.md
- Deployed to: GitHub Pages at https://kairin.github.io/mcp-manager/FOLLOWING-INSTRUCTIONS

### 3. MarkItDown Configuration Documentation

**Entity**: MarkItDown MCP Setup Guide
**Files**: README.md (MCP servers section), docs/FOLLOWING-INSTRUCTIONS.md (troubleshooting section)

**Attributes:**
- Configuration Type: "stdio" (MANDATORY)
- Command Structure: `"command": "uv", "args": ["run", "markitdown-mcp"]`
- Cross-Directory Fix: Absolute paths with --directory flag
- Troubleshooting Patterns: Array of Problem-Solution pairs

**Validation Rules:**
- MUST use UV-first command structure
- MUST document cross-directory compatibility fix from v1.2.1
- MUST include "command not found" troubleshooting
- Code examples MUST show `uv run` prefix

**Problem-Solution Pairs:**
```markdown
1. Problem: ModuleNotFoundError after installation
   Solution: Use `uv pip install` instead of `pip install`

2. Problem: "command not found: markitdown-mcp"
   Solution: Use `uv run markitdown-mcp` instead of direct executable

3. Problem: Cross-directory compatibility issues
   Solution: Use absolute paths with --directory flag
```

**Relationships:**
- Part of: docs/FOLLOWING-INSTRUCTIONS.md case study
- References: CHANGELOG.md v1.2.1, constitution Principle I
- Validates: Constitution UV-First Development principle

### 4. GitHub Pages Build Outputs

**Entity**: Generated Website Content
**Directory**: docs/

**Required Files:**
- docs/index.html (entry point)
- docs/_astro/ (compiled assets directory)
- docs/.nojekyll (GitHub Pages config)
- docs/favicon.svg (branding)
- docs/FOLLOWING-INSTRUCTIONS.html (generated from .md)

**Validation Rules:**
- MUST exist after `npm run build`
- MUST NOT be deleted without rebuilding
- MUST be committed with documentation changes
- index.html MUST reference correct asset paths in _astro/

**Build Process:**
```bash
npm run clean-docs   # Remove old outputs
npm run build        # Astro build to docs/
# Verify: test -f docs/index.html && test -d docs/_astro && test -f docs/.nojekyll
```

**Relationships:**
- Generated from: website/src/ Astro components
- Deployed to: https://kairin.github.io/mcp-manager/
- Protected by: Constitution Principle V (GitHub Pages Protection)
- Validated by: Pre-commit checks

### 5. Constitutional Reference

**Entity**: Constitution Principle Citation
**Files**: All documentation files

**Attributes:**
- Version: "1.0.0"
- Principle Number: Roman numeral I-VII
- Principle Name: String
- Citation Format: "Constitution v1.0.0 Principle [N]: [Name]"

**Validation Rules:**
- MUST reference current version (v1.0.0)
- MUST use correct principle numbering
- MUST link to .specify/memory/constitution.md when in repository docs
- MUST provide inline summary when in website docs

**Example Citations:**
```markdown
Following [Constitution v1.0.0 Principle I: UV-First Development](.specify/memory/constitution.md)
```

**Relationships:**
- Source: .specify/memory/constitution.md
- Referenced by: All documentation files
- Governs: All code examples and configuration guidance

## Entity Relationships Diagram

```
Constitution v1.0.0
    ↓ (governs)
MCP Server Docs (CLAUDE.md, README.md)
    ↓ (references)
~/.claude.json Global Config
    ↑ (described by)
FOLLOWING-INSTRUCTIONS.md
    ↓ (includes)
MarkItDown Case Study + GitHub MCP Case Study
    ↓ (validates)
UV-First Compliance Examples
    ↓ (generates)
GitHub Pages Website (docs/)
    ↓ (deployed to)
https://kairin.github.io/mcp-manager/
```

## State Transitions

### MCP Server Documentation Entry
1. **INCORRECT** → Review research findings
2. **CORRECTED** → Update CLAUDE.md and README.md
3. **VALIDATED** → Verify consistency across both files
4. **DEPLOYED** → Rebuild website and push to GitHub Pages

### FOLLOWING-INSTRUCTIONS.md
1. **MISSING** → Create file with structure
2. **DRAFT** → Write case studies with evidence
3. **COMPLETE** → Add best practices and troubleshooting
4. **DEPLOYED** → Rebuild website for GitHub Pages

### GitHub Pages Build Outputs
1. **STALE** → Run `npm run build`
2. **FRESH** → Validate required files exist
3. **COMMITTED** → Stage docs/ directory
4. **DEPLOYED** → Push to main branch, verify website

## Validation Checklist

**Pre-Commit:**
- [ ] All MCP server types are accurate
- [ ] CLAUDE.md and README.md have consistent MCP info
- [ ] FOLLOWING-INSTRUCTIONS.md exists with all case studies
- [ ] All code examples use UV-first structure
- [ ] Constitution references use correct version (v1.0.0)
- [ ] `npm run build` completes successfully
- [ ] docs/ directory contains all required files

**Post-Deploy:**
- [ ] https://kairin.github.io/mcp-manager/ loads correctly
- [ ] FOLLOWING-INSTRUCTIONS link from README works
- [ ] No 404 errors for assets
- [ ] Website deployment completed within 5 minutes