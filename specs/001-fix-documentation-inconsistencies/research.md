# Research: Documentation Accuracy and Completeness

## Research Summary

This research phase identifies existing documentation structure, validates the inconsistencies reported, and establishes best practices for documentation maintenance with GitHub Pages deployment.

## 1. GitHub MCP Server Type Investigation

### Decision: Correct type is "stdio"

**Rationale:**
- Current working configuration in `~/.claude.json` shows GitHub MCP server uses stdio type
- Binary location: `/home/kkk/bin/github-mcp-server` v0.16.0
- Configuration structure: `"command": "github-mcp-server", "args": []`
- NOT an HTTP server requiring URL/headers like Context7 or Hugging Face MCP

**Incorrect Documentation Found:**
- CLAUDE.md line 169: States "HTTP" type (INCORRECT)
- README.md line 176: MCP server table shows "HTTP" (INCORRECT)

**Alternatives Considered:**
- HTTP type with localhost URL - Rejected because binary is stdio-based CLI tool
- Hybrid configuration - Rejected because MCP protocol requires single type
- No change - Rejected because incorrect documentation causes user confusion

**Evidence:**
```json
// Correct configuration from ~/.claude.json
"github": {
  "type": "stdio",
  "command": "github-mcp-server",
  "args": []
}
```

## 2. FOLLOWING-INSTRUCTIONS.md Structure Research

### Decision: Comprehensive guide with case studies approach

**Rationale:**
- Referenced in README.md line 28 but file doesn't exist
- Purpose: Explain why strict AGENTS.md compliance prevents failures
- Format: Tutorial-style with real-world examples (MarkItDown case study)
- Location: `docs/FOLLOWING-INSTRUCTIONS.md` for GitHub Pages deployment

**Content Structure:**
1. **Introduction**: Why instruction compliance matters
2. **Constitutional Principles**: Reference to v1.0.0 constitution
3. **Case Study 1: MarkItDown Integration** (from CHANGELOG.md v1.2.1)
   - Problem: UV-first violations causing ModuleNotFoundError
   - Solution: Strict UV-first compliance
   - Lessons learned: 100% of environment issues resolved
4. **Case Study 2: GitHub MCP Configuration Evolution**
   - Problem: HTTP vs stdio type confusion
   - Solution: Accurate documentation with stdio config
   - Lessons learned: Clear server type documentation prevents setup failures
5. **Best Practices**: Guidelines for new MCP server integration
6. **Troubleshooting**: Common patterns with UV-first solutions

**Alternatives Considered:**
- Brief FAQ format - Rejected because insufficient depth for complex topics
- Separate files per case study - Rejected because fragmented navigation
- Code comments only - Rejected because not discoverable via web search

**References:**
- CHANGELOG.md v1.2.1: MarkItDown integration with UV-first fixes
- TROUBLESHOOTING.md: UV-first diagnostic patterns
- .specify/memory/constitution.md: Constitutional principles v1.0.0

## 3. MarkItDown Cross-Directory Compatibility Documentation

### Decision: Troubleshooting section with absolute paths solution

**Rationale:**
- v1.2.1 introduced cross-directory compatibility fix
- Key issue: `markitdown` command fails with "command not found" when working directory differs from installation directory
- Solution: Absolute paths with `--directory` flag: `markitdown --directory /path/to/dir`
- UV-first requirement: `uv run markitdown-mcp` instead of direct `markitdown-mcp`

**Documentation Additions Needed:**
1. **MarkItDown MCP Configuration** in README.md:
   ```json
   "markitdown": {
     "type": "stdio",
     "command": "uv",
     "args": ["run", "markitdown-mcp"]
   }
   ```

2. **Troubleshooting Section** in FOLLOWING-INSTRUCTIONS.md:
   - Problem: "command not found: markitdown-mcp"
   - Cause: Not using UV-first command structure
   - Solution: Always use `uv run` prefix
   - Problem: Cross-directory compatibility issues
   - Solution: Use absolute paths with `--directory` flag

**Alternatives Considered:**
- Symlinks to markitdown binary - Rejected because violates UV-first principle
- PATH manipulation - Rejected because inconsistent across environments
- Direct pip installation - Rejected because violates constitution principle I

**Evidence from v1.2.1:**
- Before: `pip install markitdown-mcp && markitdown-mcp` (FAILED)
- After: `uv pip install markitdown-mcp && uv run markitdown-mcp` (SUCCESS)
- Result: 100% resolution of environment-related failures

## 4. Astro Website Build Process Research

### Decision: Mandatory pre-commit build validation

**Rationale:**
- GitHub Pages deployment from `docs/` directory (not `gh-pages` branch)
- Astro configuration already correct: `outDir: './docs'`, `base: '/mcp-manager'`
- Critical files required: `docs/index.html`, `docs/_astro/`, `docs/.nojekyll`
- Build command: `npm run build` (includes clean-docs, prebuild, build, postbuild)

**Validation Process:**
1. Before committing documentation changes: `npm run build`
2. Verify outputs: `test -f docs/index.html && test -d docs/_astro && test -f docs/.nojekyll`
3. Commit all changes including built files: `git add docs/`
4. Post-deploy validation: Check https://kairin.github.io/mcp-manager/ within 5 minutes

**Alternatives Considered:**
- GitHub Actions for automatic builds - Rejected to avoid GitHub billing (zero-cost requirement)
- gh-pages branch deployment - Rejected because existing setup uses docs/ directory
- Manual HTML editing - Rejected because Astro provides component reusability

**Constitutional Compliance:**
- Principle V: GitHub Pages Protection (MANDATORY)
- Zero tolerance for commits breaking live website
- Pre-push verification of docs/ contents

## 5. UV-First Compliance in Documentation

### Decision: Audit and update all command examples

**Rationale:**
- Constitution Principle I mandates UV-first for ALL Python operations
- Documentation inconsistencies undermine constitutional compliance
- AI agents learn from documentation examples

**Required Changes:**
- Replace `pip install` → `uv pip install`
- Replace `python script.py` → `uv run python script.py`
- Replace `command-name` → `uv run command-name`
- MCP configs use `"command": "uv", "args": ["run", "executable"]`

**Audit Scope:**
- CLAUDE.md: All command examples
- README.md: Installation instructions, quickstart examples
- docs/FOLLOWING-INSTRUCTIONS.md: All code examples
- TROUBLESHOOTING.md: Solution commands

**Evidence:**
- Constitution v1.0.0 principle I: "UV provides deterministic dependency resolution"
- Real-world validation: MarkItDown case study demonstrates 100% success rate

## 6. Documentation Consistency Best Practices

### Decision: Single source of truth with symlinks

**Rationale:**
- AGENTS.md is symlinked as CLAUDE.md and GEMINI.md
- README.md serves public users
- Website content must match repository documentation
- Constitution must be referenced (not duplicated)

**Consistency Validation:**
```bash
# Check symlinks
ls -la CLAUDE.md GEMINI.md  # Should show -> AGENTS.md

# Verify MCP server table consistency
grep "github" CLAUDE.md README.md  # Should match stdio type

# Validate constitution references
grep "v1.0.0" .specify/memory/constitution.md docs/FOLLOWING-INSTRUCTIONS.md
```

**Maintenance Strategy:**
- Update AGENTS.md first (authoritative source)
- Sync README.md MCP server tables
- Reference (not duplicate) constitution principles
- Rebuild website after any documentation change

## Research Conclusions

**No NEEDS CLARIFICATION remain.** All technical decisions documented with rationale and evidence.

**Key Findings:**
1. GitHub MCP server definitively uses stdio type with local binary
2. FOLLOWING-INSTRUCTIONS.md structure validated with case study approach
3. MarkItDown UV-first fixes documented with cross-directory solutions
4. Astro build process requires mandatory pre-commit validation
5. UV-first compliance audit scope defined
6. Documentation consistency strategy established with symlinks

**Ready for Phase 1: Design & Contracts**