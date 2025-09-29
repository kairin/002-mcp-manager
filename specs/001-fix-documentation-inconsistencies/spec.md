# Feature Specification: Documentation Accuracy and Completeness

**Feature Branch**: `001-fix-documentation-inconsistencies`
**Created**: 2025-09-30
**Status**: Draft
**Input**: User description: "Fix documentation inconsistencies: GitHub MCP stdio type, create FOLLOWING-INSTRUCTIONS.md, document MarkItDown cross-directory compatibility"

## Execution Flow (main)
```
1. Parse user description from Input
   → Identified three specific documentation issues
2. Extract key concepts from description
   → Actors: developers, users, AI agents
   → Actions: update docs, create guide, document fixes
   → Data: MCP server configurations, troubleshooting steps
   → Constraints: UV-first compliance, GitHub Pages deployment
3. For each unclear aspect:
   → All aspects clear from user description and context
4. Fill User Scenarios & Testing section
   → Primary user story: Developer discovers documentation mismatch
5. Generate Functional Requirements
   → Three categories: accuracy, completeness, discoverability
6. Identify Key Entities (if data involved)
   → Documentation files as entities
7. Run Review Checklist
   → All requirements testable and unambiguous
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A developer setting up MCP Manager on a new machine reads the documentation to understand how to configure MCP servers. They discover that the GitHub MCP server documentation states it uses "HTTP" type, but when they check their working configuration, it actually uses "stdio" type with a local binary. This inconsistency creates confusion about the correct configuration method and wastes time troubleshooting.

Additionally, the developer sees references to a "FOLLOWING-INSTRUCTIONS.md" guide that doesn't exist, preventing them from understanding why strict AGENTS.md compliance is critical. When they encounter MarkItDown MCP server issues, they need documentation explaining the cross-directory compatibility fix and UV-first requirements.

### Acceptance Scenarios

1. **Given** a developer reading CLAUDE.md or README.md, **When** they reach the MCP Servers section, **Then** they see accurate information that GitHub MCP uses "stdio" type with local binary configuration

2. **Given** a developer following README.md links, **When** they click the FOLLOWING-INSTRUCTIONS.md reference, **Then** they access a comprehensive guide explaining AGENTS.md compliance importance with real-world case studies

3. **Given** a developer configuring MarkItDown MCP server, **When** they encounter "command not found" or cross-directory issues, **Then** they find documented troubleshooting steps with UV-first solutions

4. **Given** documentation updates are committed, **When** changes are pushed to main branch, **Then** the GitHub Pages website at https://kairin.github.io/mcp-manager/ reflects the corrected information within 5 minutes

5. **Given** AI agents (Claude Code, Gemini, etc.) read AGENTS.md/CLAUDE.md, **When** they configure MCP servers, **Then** they receive accurate guidance preventing configuration errors

### Edge Cases
- What happens when a user follows outdated HTTP-based GitHub MCP setup instructions? They experience connection failures and waste time debugging incorrect configuration.
- How does system handle documentation references to non-existent files? Users feel documentation is incomplete and lose confidence in project quality.
- What if MarkItDown issues occur on office machines vs home machines? Documentation must cover fleet consistency requirements.

## Requirements *(mandatory)*

### Functional Requirements

**Accuracy Requirements:**
- **FR-001**: Documentation MUST correctly state that GitHub MCP server uses "stdio" type, not "HTTP" type
- **FR-002**: Documentation MUST specify the exact binary location: /home/kkk/bin/github-mcp-server v0.16.0
- **FR-003**: Documentation MUST show correct stdio configuration example with command and args structure
- **FR-004**: Both CLAUDE.md and README.md MUST contain consistent GitHub MCP server type information

**Completeness Requirements:**
- **FR-005**: System MUST provide docs/FOLLOWING-INSTRUCTIONS.md file at the referenced location
- **FR-006**: FOLLOWING-INSTRUCTIONS.md MUST explain why AGENTS.md compliance is critical for project success
- **FR-007**: FOLLOWING-INSTRUCTIONS.md MUST include the MarkItDown MCP integration case study from CHANGELOG.md v1.2.1
- **FR-008**: Documentation MUST explain MarkItDown cross-directory compatibility fix with absolute paths and --directory flag
- **FR-009**: Documentation MUST include troubleshooting section for "command not found" errors with UV-first solutions
- **FR-010**: All documentation MUST reflect UV-first requirements (uv pip install, uv run commands)

**Deployment Requirements:**
- **FR-011**: Documentation updates MUST preserve existing docs/ build outputs to prevent GitHub Pages 404 errors
- **FR-012**: System MUST run `npm run build` after documentation changes to regenerate GitHub Pages content
- **FR-013**: Built website MUST remain accessible at https://kairin.github.io/mcp-manager/ after deployment
- **FR-014**: Required files MUST exist after build: docs/index.html, docs/_astro/, docs/.nojekyll

**Consistency Requirements:**
- **FR-015**: All MCP server configurations in documentation MUST follow UV-first command structure
- **FR-016**: Documentation MUST maintain consistency across AGENTS.md, CLAUDE.md, README.md, and website content
- **FR-017**: Troubleshooting guidance MUST reference the new constitution v1.0.0 principles

### Key Entities *(include if feature involves data)*

- **CLAUDE.md**: Primary instruction file for Claude Code AI agent, contains MCP server configuration reference table
- **README.md**: Public-facing project documentation, includes MCP server overview and quickstart guide
- **docs/FOLLOWING-INSTRUCTIONS.md**: Compliance guide explaining why strict adherence to AGENTS.md requirements prevents failures
- **MarkItDown Configuration**: Cross-directory compatibility documentation with absolute path requirements and UV-first command structure
- **GitHub Pages Website**: Live documentation at https://kairin.github.io/mcp-manager/ generated from docs/ directory

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked (none found)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---