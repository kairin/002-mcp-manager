# Quickstart: Using the MCP Profile Switcher

**Generated**: 2025-10-25

This guide provides quick, copy-pasteable commands for the most common use cases of the `mcp-profile` script.

## 1. Switch All Tools to a Profile

To synchronize all supported AI tools (Claude, Gemini, Copilot) to use the `dev` profile:

```bash
mcp-profile dev
```

To switch to the `full` profile:

```bash
mcp-profile full
```

## 2. Check Current Status

To see which profile is active for each tool and what servers are configured:

```bash
mcp-profile status
```

To check the status of only the Gemini CLI:

```bash
mcp-profile status --tool=gemini
```

## 3. Test Your Configuration

To run health checks on your authentication and currently configured MCP servers:

```bash
mcp-profile test
```

## 4. List Available Profiles

To see all profiles available to switch to:

```bash
mcp-profile list
```

## 5. Verify Configuration Sync

After switching to the `dev` profile, you can manually verify that the configurations have been applied correctly.

**Check Claude Code:**
```bash
jq -r '.projects["$(git rev-parse --show-toplevel)"].mcpServers | keys | sort' ~/.claude.json
```

**Check Gemini CLI:**
```bash
jq -r '.mcpServers | keys | sort' ~/.config/gemini/settings.json
```

**Check Copilot CLI:**
```bash
jq -r 'keys | sort' ~/.config/mcp-config.json
```

All three commands should output the same list of server names, matching the keys in `~/.config/mcp-profiles/dev.json`.
