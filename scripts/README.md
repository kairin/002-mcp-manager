# Scripts Directory

> **Organized utility scripts for MCP Manager**

## Directory Structure

### `setup/` - Initial Setup and Configuration
Scripts for first-time setup and MCP server configuration:

- **`hf_quick_setup.sh`**: Quick setup for Hugging Face MCP server with CLI authentication
- **`test_claude_fix.sh`**: Verify Claude Code and MCP server configuration

**Usage**:
```bash
# Set up Hugging Face MCP server
./scripts/setup/hf_quick_setup.sh

# Test MCP server configuration
./scripts/setup/test_claude_fix.sh
```

### `deployment/` - Deployment and CI/CD
Scripts for deploying changes to GitHub Pages:

- **`deploy.sh`**: Complete interactive deployment workflow (build → commit → push → merge)
- **`local-ci.sh`**: Local CI/CD execution script

**Usage**:
```bash
# Interactive deployment with prompts
./scripts/deployment/deploy.sh

# Run local CI checks
./scripts/deployment/local-ci.sh
```

### `git/` - Git Workflow Utilities
Scripts for git operations and branch management:

- **`check-branch-name.sh`**: Validate branch name follows YYYYMMDD-HHMMSS-type-description format
- **`push-workflow.sh`**: Push changes with validation

**Usage**:
```bash
# Check branch name format
./scripts/git/check-branch-name.sh

# Push with validation
./scripts/git/push-workflow.sh
```

### `legacy/` - Archived Scripts
Deprecated scripts kept for historical reference:

- **`repo-setup-script.sh`**: Original repository setup script (superseded by MCP Manager)

**Note**: Scripts in this directory are no longer maintained and may not work with current setup.

## Script Conventions

### Naming Convention
All scripts follow lowercase-with-hyphens naming:
- ✅ `hf-quick-setup.sh`
- ✅ `test-claude-fix.sh`
- ❌ `HFQuickSetup.sh`

### Shebang
All scripts start with:
```bash
#!/bin/bash
```

### Permissions
All scripts are executable:
```bash
chmod +x scripts/**/*.sh
```

### Documentation
Each script should include:
- Purpose comment at the top
- Usage instructions
- Error handling
- Exit codes

## Development Workflow

### Adding New Scripts

1. **Choose appropriate subdirectory**:
   - Setup tasks → `setup/`
   - Deployment tasks → `deployment/`
   - Git operations → `git/`

2. **Create script with documentation**:
   ```bash
   cat > scripts/setup/new-script.sh << 'EOF'
   #!/bin/bash
   # Brief description of what this script does

   # Script implementation
   EOF
   ```

3. **Make executable**:
   ```bash
   chmod +x scripts/setup/new-script.sh
   ```

4. **Update this README**:
   Add entry to appropriate section above

5. **Update references**:
   - README.md (if user-facing)
   - AGENTS.md (if mandatory workflow)
   - Documentation files

### Testing Scripts

Before committing new scripts:

```bash
# Test script execution
./scripts/category/script-name.sh

# Verify exit codes
echo $?  # Should be 0 for success

# Check for shellcheck issues
shellcheck scripts/**/*.sh
```

## Integration with Pre-Commit Hook

The pre-commit hook at `.git/hooks/pre-commit` automatically runs builds when needed. It does not directly call scripts from this directory but implements similar logic for deployment verification.

## Related Documentation

- [AGENTS.md](../AGENTS.md) - Complete project requirements
- [README.md](../README.md) - Project overview
- [CHANGELOG.md](../docs/CHANGELOG.md) - Historical changes

---

**Last Updated**: 2025-09-30
**Maintained By**: MCP Manager Project