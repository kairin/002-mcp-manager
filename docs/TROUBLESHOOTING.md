# 🛠️ Troubleshooting Guide - MCP Manager

This guide documents common problems encountered when **not following the UV-first requirements** and their solutions.

## 🚨 Most Common Issue: Ignoring UV-First Requirements

### The Golden Rule: **ALWAYS USE UV**

```bash
# ✅ CORRECT - Use UV for everything
uv pip install package-name
uv run command-name
uv run python script.py

# ❌ WRONG - Never use system pip/python
pip install package-name
command-name
python script.py
```

---

## 🐛 Problem Category 1: Module Import Errors

### ❌ Symptoms
```bash
ModuleNotFoundError: No module named 'httpx'
ModuleNotFoundError: No module named 'markitdown_mcp'
ModuleNotFoundError: No module named 'mcp_manager'
```

### 🔍 Root Cause
You installed packages with `pip` instead of `uv pip install`, or you're running Python directly instead of using `uv run`.

### ✅ Solution
```bash
# 1. Install packages with UV
uv pip install httpx
uv pip install markitdown-mcp
uv pip install -e .

# 2. Run Python with UV
uv run python -m mcp_manager.cli status
```

### 📋 Prevention Checklist
- [ ] Did I use `uv pip install` for ALL package installations?
- [ ] Am I using `uv run python` instead of direct `python`?
- [ ] Did I activate the UV environment properly?

---

## 🐛 Problem Category 2: Command Not Found Errors

### ❌ Symptoms
```bash
command not found: markitdown-mcp
command not found: mcp-manager
bash: markitdown-mcp: command not found
```

### 🔍 Root Cause
Packages were installed with UV but you're trying to run them directly instead of through `uv run`.

### ✅ Solution
```bash
# ❌ WRONG
markitdown-mcp --help

# ✅ CORRECT
uv run markitdown-mcp --help
```

### 📋 MCP Server Configuration Fix
```json
// ❌ WRONG - Direct command execution
{
  "markitdown": {
    "type": "stdio",
    "command": "markitdown-mcp",
    "args": []
  }
}

// ✅ CORRECT - UV-managed execution
{
  "markitdown": {
    "type": "stdio",
    "command": "uv",
    "args": ["run", "markitdown-mcp"]
  }
}
```

---

## 🐛 Problem Category 3: Python Path Issues

### ❌ Symptoms
```bash
Error while finding module specification for 'mcp_manager.cli'
No module named 'mcp_manager'
ImportError: attempted relative import with no known parent package
```

### 🔍 Root Cause
Using system Python instead of UV-managed Python environment.

### ✅ Solution
```bash
# 1. Verify UV environment is active
uv venv .venv
source .venv/bin/activate

# 2. Install project in development mode
uv pip install -e .

# 3. Run CLI with UV
uv run python -m mcp_manager.cli status

# Not: python -m mcp_manager.cli status
```

---

## 🐛 Problem Category 4: MCP Server Health Issues

### ❌ Symptoms
```bash
# MCP server shows as unhealthy or missing
❌ markitdown: unhealthy
# OR server doesn't appear in status list at all
```

### 🔍 Root Cause
MCP server was configured with direct command execution instead of UV-managed execution.

### ✅ Solution
1. **Check Current Configuration**:
   ```bash
   uv run python -m mcp_manager.cli mcp status
   ```

2. **Fix Server Configuration**:
   ```bash
   # Remove incorrectly configured server
   uv run python -m mcp_manager.cli mcp remove markitdown

   # Add with correct UV configuration
   uv run python -m mcp_manager.cli mcp add markitdown \
     --type stdio \
     --command "uv" \
     --arg "run" \
     --arg "markitdown-mcp"
   ```

3. **Verify Health**:
   ```bash
   uv run python -m mcp_manager.cli status
   # Should show: ✅ markitdown: healthy
   ```

---

## 🐛 Problem Category 5: Environment Inconsistencies

### ❌ Symptoms
```bash
# Different behavior in different terminals
# Packages work sometimes but not others
# Inconsistent module availability
```

### 🔍 Root Cause
Mixed usage of system Python and UV Python environments.

### ✅ Solution
**Complete Environment Reset:**

```bash
# 1. Clean slate - remove any system installations
pip uninstall markitdown-mcp httpx mcp-manager 2>/dev/null || true

# 2. Fresh UV environment
cd /home/kkk/Apps/mcp-manager
rm -rf .venv
uv venv .venv
source .venv/bin/activate

# 3. Install everything with UV
uv pip install -e .
uv pip install markitdown-mcp

# 4. Test with UV
uv run python -m mcp_manager.cli status
```

---

## 🎯 Quick Diagnostic Commands

### 1. Environment Verification
```bash
# Check UV installation
uv --version

# Check active environment
which python
# Should show: /home/kkk/Apps/mcp-manager/.venv/bin/python

# Check UV-managed packages
uv pip list
```

### 2. MCP Manager Health Check
```bash
# Full system status
uv run python -m mcp_manager.cli status

# MCP servers specifically
uv run python -m mcp_manager.cli mcp status

# Test specific server
uv run python -m mcp_manager.cli mcp status markitdown
```

### 3. Package Verification
```bash
# Test markitdown-mcp installation
uv run markitdown-mcp --help

# Test Python imports
uv run python -c "import markitdown_mcp; print('✅ markitdown_mcp imported')"
uv run python -c "import mcp_manager; print('✅ mcp_manager imported')"
```

---

## 🆘 Emergency Reset Procedure

If everything is broken and you need to start fresh:

```bash
# 1. Navigate to project directory
cd /home/kkk/Apps/mcp-manager

# 2. Complete environment wipe
rm -rf .venv
deactivate 2>/dev/null || true

# 3. Fresh UV setup
uv venv .venv
source .venv/bin/activate

# 4. Install from scratch with UV only
uv pip install -e .
uv pip install markitdown-mcp

# 5. Configure MCP servers properly
uv run python -m mcp_manager.cli mcp add markitdown \
  --type stdio \
  --command "uv" \
  --arg "run" \
  --arg "markitdown-mcp"

# 6. Verify everything works
uv run python -m mcp_manager.cli status
```

---

## 📚 Learning from the MarkItDown Integration

The MarkItDown MCP server integration provided a perfect case study of what happens when UV-first requirements are ignored:

### Timeline of Problems (Due to UV-First Violations)
1. ❌ Used `pip install markitdown-mcp` → Module import failures
2. ❌ Used `python -m mcp_manager.cli` → Module specification errors
3. ❌ Used `markitdown-mcp` directly → Command not found errors
4. ❌ Configured MCP server without UV → Server health failures

### Timeline of Solutions (Following UV-First Properly)
1. ✅ Used `uv pip install markitdown-mcp` → Clean installation
2. ✅ Used `uv run python -m mcp_manager.cli` → Proper module resolution
3. ✅ Used `uv run markitdown-mcp` → Command execution success
4. ✅ Configured MCP server with UV → Healthy server status

### Key Lesson
**Every single problem was caused by not following UV-first requirements. Every solution was simply following the requirements properly.**

---

## 🎯 Prevention Strategies

### 1. Pre-Work Checklist
Before starting any work on this project:
- [ ] Read AGENTS.md instructions completely
- [ ] Verify UV is installed and working
- [ ] Activate UV environment: `source .venv/bin/activate`
- [ ] Test basic commands with `uv run`

### 2. During Development
- [ ] Use `uv pip install` for ALL package installations
- [ ] Use `uv run` for ALL command executions
- [ ] Test frequently with `uv run python -m mcp_manager.cli status`
- [ ] Configure MCP servers with UV execution paths

### 3. Before Commits
- [ ] Verify all MCP servers are healthy
- [ ] Test CLI commands with UV
- [ ] Check that documentation reflects UV-first approach
- [ ] Build website successfully with `npm run build`

---

## 💡 Pro Tips

### 1. Alias Commands for Efficiency
```bash
# Add to ~/.bashrc or ~/.zshrc
alias mcp='uv run python -m mcp_manager.cli'
alias mcps='uv run python -m mcp_manager.cli status'
alias mcptest='uv run markitdown-mcp --help'
```

### 2. Always Verify After Changes
```bash
# Quick verification pipeline
uv run python -m mcp_manager.cli status && \
uv run markitdown-mcp --help && \
echo "✅ All systems operational"
```

### 3. Document UV Commands in Scripts
```bash
#!/bin/bash
# Always use UV in scripts
uv run python -m mcp_manager.cli mcp add new-server \
  --type stdio \
  --command "uv" \
  --arg "run" \
  --arg "new-server-command"
```

---

## 🔍 Still Having Issues?

1. **Check AGENTS.md**: All requirements are NON-NEGOTIABLE
2. **Use Context7**: Get latest documentation for packages
3. **Reset Environment**: Use the emergency reset procedure above
4. **Follow UV-First**: Every command must use UV

**Remember: 100% of environment issues are caused by not following UV-first requirements exactly.**