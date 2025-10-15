# Constitutional Principles: Multi-CLI MCP Server Support

**Spec ID**: 004-multi-cli-support
**Created**: 2025-10-15
**Status**: Constitutional Phase
**Target AI Platforms**: Claude Code, Gemini CLI, GitHub Copilot CLI

## 🎯 Core Mission

> **MCP Manager shall provide UNIVERSAL MCP server configuration management that works seamlessly across ALL major AI CLI platforms without requiring platform-specific workarounds or manual configuration changes.**

## 📜 Constitutional Principles

### 1. Platform Agnosticism (MANDATORY)

**Principle**: *Configuration format shall adapt to platform requirements automatically*

- **Single Source of Truth**: One canonical MCP server definition works across all platforms
- **Automatic Translation**: Platform-specific formats generated from canonical config
- **Zero Manual Intervention**: No user editing of platform-specific config files
- **Validation Before Deployment**: Verify compatibility before applying configurations

**Rationale**: Developers use multiple AI CLI tools simultaneously. Manual configuration synchronization is error-prone and breaks development flow.

### 2. Configuration Correctness by Design (MANDATORY)

**Principle**: *Invalid configurations shall be impossible to create*

- **Type-Safe Models**: Pydantic models enforce configuration structure
- **Platform Validation**: Each platform's requirements validated before generation
- **Real-Time Verification**: Health checks confirm servers are accessible
- **Automatic Correction**: Detect and fix common configuration errors

**Rationale**: The timeout issue we discovered (context7 using `url` instead of `httpUrl` for Gemini) must never happen again.

### 3. Explicit Platform Support Declaration (MANDATORY)

**Principle**: *Supported platforms and their requirements shall be explicitly documented*

**Supported Platforms**:
1. **Claude Code** (Primary) - `.claude.json` format
2. **Gemini CLI** (Primary) - `~/.config/gemini/settings.json` format
3. **GitHub Copilot CLI** (Secondary) - `.mcp.json` format

**Configuration Compatibility Matrix**:
| Field | Claude Code | Gemini CLI | Copilot CLI |
|-------|-------------|------------|-------------|
| `type` | Required | Optional | Required |
| `url` | HTTP servers | ❌ Not supported | HTTP servers |
| `httpUrl` | ❌ Not supported | Required for HTTP | Optional |
| `headers.Accept` | Optional | **Required** for HTTP | Optional |
| `command` | stdio servers | stdio servers | stdio servers |
| `args` | Array | Array | Array |
| `env` | Object | Object | Object |

**Rationale**: Each platform has subtle differences. Explicit support matrix prevents configuration errors.

### 4. Version-Specific Best Practices (MANDATORY)

**Principle**: *Package versions shall follow platform-specific best practices*

- **`@latest` for Development Tools**: shadcn, playwright, etc. use `@latest`
- **Fixed Versions for Stability**: Production-critical servers may use fixed versions
- **Documentation Alignment**: Version recommendations match official docs
- **Automatic Update Detection**: Notify when newer versions available

**Example Violations Fixed**:
- ❌ `shadcn@3.4.0` (outdated fixed version)
- ✅ `shadcn@latest` (recommended by official docs)

**Rationale**: Fixed versions cause dependency staleness. `@latest` ensures compatibility with evolving MCP protocol.

### 5. Comprehensive Testing Across Platforms (MANDATORY)

**Principle**: *All configurations shall be tested on all supported platforms*

**Testing Requirements**:
1. **Syntax Validation**: JSON schema validation for each platform
2. **Health Checks**: Verify server connectivity after deployment
3. **Integration Tests**: Real CLI tool integration testing
4. **Contract Tests**: Platform-specific configuration contracts
5. **Regression Prevention**: Prevent re-occurrence of known issues

**Test Matrix**:
```
┌─────────────┬─────────────┬─────────────┬──────────────┐
│   Server    │ Claude Code │ Gemini CLI  │ Copilot CLI  │
├─────────────┼─────────────┼─────────────┼──────────────┤
│ context7    │     ✅      │     ✅      │      ✅      │
│ shadcn      │     ✅      │     ✅      │      ✅      │
│ playwright  │     ✅      │     ✅      │      ✅      │
│ github      │     ✅      │     ✅      │      ✅      │
│ hf-mcp      │     ✅      │     ✅      │      ✅      │
│ markitdown  │     ✅      │     ✅      │      ✅      │
└─────────────┴─────────────┴─────────────┴──────────────┘
```

**Rationale**: What works on Claude Code may fail on Gemini CLI (as we discovered). Universal testing prevents platform-specific failures.

### 6. Backward Compatibility Guarantee (MANDATORY)

**Principle**: *Existing configurations shall continue working after upgrades*

- **Migration Path**: Automatic migration from old to new format
- **Deprecation Warnings**: Clear warnings before breaking changes
- **Fallback Support**: Legacy formats supported during transition
- **Version Detection**: Detect config version and handle appropriately

**Rationale**: Users have existing working configurations. Breaking them without migration causes frustration.

### 7. Developer Experience First (MANDATORY)

**Principle**: *Configuration management shall be effortless and intuitive*

**User Experience Goals**:
- **Single Command Setup**: `mcp-manager init` works for all platforms
- **Automatic Detection**: Detect installed AI CLI tools automatically
- **Smart Defaults**: Reasonable defaults for all configuration options
- **Clear Error Messages**: Actionable error descriptions with fix suggestions
- **Visual Feedback**: Rich CLI output showing deployment progress

**Example Good UX**:
```bash
$ mcp-manager deploy --all-platforms

🔍 Detected AI CLI tools:
  ✅ Claude Code (v0.8.2) at ~/.claude.json
  ✅ Gemini CLI (v0.8.2) at ~/.config/gemini/settings.json
  ⚠️  Copilot CLI not detected

📋 Deploying 6 MCP servers:
  ✅ context7 → Claude Code, Gemini CLI
  ✅ shadcn → Claude Code, Gemini CLI
  ✅ playwright → Claude Code, Gemini CLI
  ✅ github → Claude Code, Gemini CLI
  ✅ hf-mcp → Claude Code, Gemini CLI
  ✅ markitdown → Claude Code, Gemini CLI

✨ Deployment complete! All servers operational.
```

**Rationale**: If configuration is hard, developers won't use the tool. Simplicity drives adoption.

### 8. Security by Default (MANDATORY)

**Principle**: *Sensitive credentials shall never be exposed or committed*

- **Environment Variables**: API keys stored in environment, not config files
- **Template-Only Configs**: Documentation shows `{"API_KEY": "..."}` never real keys
- **Gitignore Protection**: All sensitive files automatically excluded
- **Security Scanning**: Pre-commit hooks prevent credential leaks
- **Encrypted Storage**: Optional encryption for stored credentials

**Rationale**: One leaked API key can compromise entire accounts. Security must be automatic.

### 9. Observable and Debuggable (MANDATORY)

**Principle**: *System state shall be transparent and issues easily diagnosable*

**Observability Features**:
- **Health Dashboard**: Real-time server status across all platforms
- **Detailed Logs**: Structured logging with trace IDs
- **Diagnostic Mode**: Verbose output for troubleshooting
- **Configuration Diff**: Show differences between platform configs
- **Validation Reports**: Detailed validation results with line numbers

**Example Diagnostic Output**:
```bash
$ mcp-manager diagnose

🔍 Diagnosing MCP Manager Configuration

Platform: Gemini CLI
Config: ~/.config/gemini/settings.json
Status: ⚠️  Issues Found

Issues:
1. ❌ context7: Using 'url' field instead of 'httpUrl' (Gemini requirement)
   Location: Line 4
   Fix: Change "url" to "httpUrl"

2. ❌ context7: Missing required 'Accept' header
   Location: Line 6 (headers section)
   Fix: Add "Accept": "application/json, text/event-stream"

3. ⚠️  shadcn: Using fixed version 'shadcn@3.4.0'
   Location: Line 13
   Recommendation: Change to 'shadcn@latest' per official docs

🔧 Auto-fix available: Run 'mcp-manager fix --platform gemini'
```

**Rationale**: When things break, developers need immediate clarity on what's wrong and how to fix it.

## 🎓 Lessons from Real-World Issues

### Issue #1: Gemini CLI Timeout (Root Cause Analysis)

**Symptom**: `gemini mcp list` command timed out after 2 minutes

**Root Cause**:
```json
// INCORRECT for Gemini CLI
"context7": {
  "type": "http",
  "url": "https://mcp.context7.com/mcp",  // ❌ Wrong field
  "headers": {
    "CONTEXT7_API_KEY": "..."  // ❌ Missing Accept header
  }
}
```

**Correct Configuration**:
```json
// CORRECT for Gemini CLI
"context7": {
  "httpUrl": "https://mcp.context7.com/mcp",  // ✅ Right field
  "headers": {
    "CONTEXT7_API_KEY": "...",
    "Accept": "application/json, text/event-stream"  // ✅ Required header
  }
}
```

**Constitutional Violation**: Principle #2 (Configuration Correctness by Design)

**Prevention Strategy**: Type-safe models with platform-specific validation

### Issue #2: Outdated Package Versions

**Symptom**: `shadcn@3.4.0` instead of recommended `shadcn@latest`

**Root Cause**: Fixed version in configuration didn't align with official documentation

**Constitutional Violation**: Principle #4 (Version-Specific Best Practices)

**Prevention Strategy**: Version validation against official recommendations

## 🏗️ Implementation Requirements

### Core Requirements (MANDATORY)

1. **Platform Adapters**
   - Claude Code adapter (`.claude.json` format)
   - Gemini CLI adapter (`~/.config/gemini/settings.json` format)
   - Copilot CLI adapter (`.mcp.json` format)

2. **Configuration Models**
   - Canonical MCP server model (platform-agnostic)
   - Platform-specific models (Claude, Gemini, Copilot)
   - Automatic conversion between formats

3. **Validation Engine**
   - JSON schema validation per platform
   - Semantic validation (required headers, version formats)
   - Health check validation (server accessibility)

4. **CLI Commands**
   ```bash
   mcp-manager init --platform <claude|gemini|copilot|all>
   mcp-manager deploy --platform <claude|gemini|copilot|all>
   mcp-manager validate --platform <claude|gemini|copilot|all>
   mcp-manager fix --platform <claude|gemini|copilot|all>
   mcp-manager diagnose
   ```

5. **Testing Framework**
   - Unit tests for each adapter
   - Integration tests with real CLI tools
   - Contract tests for configuration formats
   - Regression tests for known issues

## ✅ Success Criteria

### Functional Metrics
- **Platform Coverage**: 100% support for Claude Code, Gemini CLI, Copilot CLI
- **Configuration Accuracy**: 0 manual corrections needed after generation
- **Health Check Speed**: <5 seconds to verify all servers across all platforms
- **Auto-Fix Success**: >95% of issues fixed automatically

### Quality Metrics
- **Test Coverage**: >90% line coverage
- **Type Coverage**: 100% type annotations
- **Platform Parity**: All 6 servers work on all 3 platforms
- **Zero Regressions**: Known issues (Gemini timeout, version staleness) never recur

### User Experience Metrics
- **Setup Time**: <3 minutes for multi-platform deployment
- **Error Resolution**: <1 minute from detection to fix
- **Documentation Clarity**: <5 minutes to understand platform differences
- **Confidence Level**: Users trust configurations work without manual verification

## 🚫 Non-Negotiable Constraints

### What We Will NOT Do

1. ❌ **Platform-Specific Manual Configuration**: Users shall never manually edit platform config files
2. ❌ **Silent Failures**: Configuration errors shall always be loud and clear
3. ❌ **Breaking Changes Without Migration**: Existing configs shall auto-migrate
4. ❌ **Credential Exposure**: API keys shall never appear in documentation or logs
5. ❌ **Untested Platforms**: New platform support requires full test coverage

### What We WILL Always Do

1. ✅ **Validate Before Deploy**: Never deploy untested configurations
2. ✅ **Provide Fix Commands**: Every error includes fix suggestion
3. ✅ **Maintain Compatibility**: Old configs work forever (with warnings)
4. ✅ **Document Platform Differences**: Explicit compatibility matrix
5. ✅ **Test on Real Tools**: Integration tests with actual CLI tools

## 📊 Acceptance Criteria

**This constitutional phase succeeds when:**

1. ✅ All stakeholders agree on these principles
2. ✅ Platform compatibility matrix is complete and accurate
3. ✅ Success criteria are measurable and achievable
4. ✅ Non-negotiable constraints are clearly defined
5. ✅ Next phase (specification) can begin with clear requirements

---

**Constitutional Status**: DRAFT → REVIEW → APPROVED → ACTIVE
**Next Phase**: Specification (spec.md)
**Approval Required**: Yes (Project Owner)
