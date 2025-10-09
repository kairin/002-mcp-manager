# 🏢 Office Deployment Guide

Complete guide for deploying and managing MCP configurations across multiple office machines.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Setup SSH Access](#setup-ssh-access)
- [Register Office Machines](#register-office-machines)
- [Deploy MCP Configuration](#deploy-mcp-configuration)
- [Verify Deployments](#verify-deployments)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Overview

The office deployment feature allows you to:

- **📋 Register multiple office machines** for centralized management
- **🚀 Deploy MCP configurations** to all machines with one command
- **✅ Verify synchronization** across your office network
- **🔄 Pull configurations** from any machine (reverse sync)
- **📊 Monitor status** of all registered machines

## Quick Start

### 1. Get Current Machine Info

On each machine you want to manage, first get its connection information:

```bash
uv run python -m mcp_manager.cli office info
```

This displays:
- Hostname
- IP Address
- SSH Username

### 2. Register from Master Machine

On your **master machine** (where you'll manage configurations from), register each office machine:

```bash
# Basic registration (password authentication)
uv run python -m mcp_manager.cli office register office-pc-01 192.168.1.100 --user kkk

# With SSH key
uv run python -m mcp_manager.cli office register office-pc-02 192.168.1.101 --user kkk --key ~/.ssh/id_rsa
```

### 3. Check Connectivity

Verify SSH connectivity to registered machines:

```bash
# Check specific machine
uv run python -m mcp_manager.cli office check office-pc-01

# View status of all machines
uv run python -m mcp_manager.cli office status
```

### 4. Deploy Configuration

Deploy your MCP configuration to all office machines:

```bash
# Dry run first (safe preview)
uv run python -m mcp_manager.cli office deploy --dry-run

# Deploy to all machines
uv run python -m mcp_manager.cli office deploy

# Deploy to specific machine
uv run python -m mcp_manager.cli office deploy office-pc-01
```

### 5. Verify Synchronization

Check that configurations match across machines:

```bash
# Verify all machines
uv run python -m mcp_manager.cli office verify

# Verify specific machine
uv run python -m mcp_manager.cli office verify office-pc-01
```

## Setup SSH Access

### Option 1: Password-less SSH (Recommended)

1. **Generate SSH key pair** (if you don't have one):
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

2. **Copy public key to office machines**:
   ```bash
   ssh-copy-id kkk@192.168.1.100
   ssh-copy-id kkk@192.168.1.101
   # Repeat for each machine
   ```

3. **Test connection**:
   ```bash
   ssh kkk@192.168.1.100 echo "Connection successful"
   ```

### Option 2: SSH Config File

Create `~/.ssh/config` for easier management:

```
# Office PC 01
Host office-pc-01
    HostName 192.168.1.100
    User kkk
    IdentityFile ~/.ssh/id_rsa
    Port 22

# Office PC 02
Host office-pc-02
    HostName 192.168.1.101
    User kkk
    IdentityFile ~/.ssh/id_rsa
    Port 22
```

Then register using the alias:

```bash
uv run python -m mcp_manager.cli office register office-pc-01 192.168.1.100 --user kkk --key ~/.ssh/id_rsa
```

## Register Office Machines

### List Registered Machines

```bash
uv run python -m mcp_manager.cli office list
```

Output shows:
- Hostname
- IP Address
- SSH User
- Connection Status
- Last Sync Time

### Remove Machine

```bash
# With confirmation
uv run python -m mcp_manager.cli office remove office-pc-01

# Force remove (no confirmation)
uv run python -m mcp_manager.cli office remove office-pc-01 --force
```

## Deploy MCP Configuration

### Full Deployment Workflow

1. **Configure MCP servers locally** on your master machine
2. **Test configuration** using `claude mcp` command
3. **Dry run deployment** to preview changes
4. **Deploy to office machines**
5. **Verify synchronization**

```bash
# Step 1: Verify local MCP configuration
uv run python -m mcp_manager.cli mcp status

# Step 2: Dry run deployment
uv run python -m mcp_manager.cli office deploy --dry-run

# Step 3: Deploy to all machines
uv run python -m mcp_manager.cli office deploy

# Step 4: Verify deployment
uv run python -m mcp_manager.cli office verify
```

### Selective Deployment

Deploy to specific machines:

```bash
# Deploy to single machine
uv run python -m mcp_manager.cli office deploy office-pc-01

# Deploy to multiple machines (run separately)
uv run python -m mcp_manager.cli office deploy office-pc-01
uv run python -m mcp_manager.cli office deploy office-pc-02
```

## Verify Deployments

### Verification Process

The verification command checks:
- **Configuration hash** matches between machines
- **Number of MCP servers** is consistent
- **Remote machine reachability**

```bash
# Verify all machines
uv run python -m mcp_manager.cli office verify

# Verify specific machine
uv run python -m mcp_manager.cli office verify office-pc-01
```

### Understanding Verification Results

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ Match | Configurations are identical | No action needed |
| ❌ Mismatch | Configurations differ | Run `deploy` to sync |
| 🔴 Unreachable | SSH connection failed | Check network/SSH |
| ❌ Error | Read error occurred | Check permissions |

## Troubleshooting

### Common Issues

#### 1. SSH Connection Refused

**Problem**: `Connection refused` or `Unreachable` status

**Solutions**:
- Verify SSH service is running: `sudo systemctl status ssh`
- Check firewall rules: `sudo ufw status`
- Test manual SSH: `ssh user@hostname`
- Verify IP address is correct

#### 2. Permission Denied

**Problem**: SSH authentication fails

**Solutions**:
- Check SSH key permissions: `chmod 600 ~/.ssh/id_rsa`
- Verify public key on remote: `cat ~/.ssh/authorized_keys`
- Try password authentication first
- Check SSH user has correct permissions

#### 3. Configuration Mismatch

**Problem**: Verification shows mismatch after deployment

**Solutions**:
```bash
# Re-deploy to sync
uv run python -m mcp_manager.cli office deploy office-pc-01

# Or pull from working machine
uv run python -m mcp_manager.cli office pull office-pc-01
```

#### 4. Backup Files Growing

**Problem**: Multiple backup files on remote machines

**Solution**: Backups are created automatically. To clean old backups:

```bash
ssh user@office-machine "ls -lt ~/.claude.json.backup.* | tail -n +6 | awk '{print \$9}' | xargs rm"
```

### Debug Commands

```bash
# Get current machine info
uv run python -m mcp_manager.cli office info

# Check connectivity
uv run python -m mcp_manager.cli office check hostname

# View deployment status
uv run python -m mcp_manager.cli office status

# List registered machines
uv run python -m mcp_manager.cli office list
```

## Advanced Usage

### Pull Configuration from Remote

Sometimes you might want to pull configuration from an office machine to your master:

```bash
# This overwrites your local ~/.claude.json
uv run python -m mcp_manager.cli office pull office-pc-01
```

**⚠️ Warning**: This will back up and replace your local configuration.

### Automated Deployment with Cron

Set up automatic daily synchronization:

```bash
# Add to crontab
crontab -e

# Deploy at 8 AM daily
0 8 * * * cd /home/kkk/Apps/002-mcp-manager && uv run python -m mcp_manager.cli office deploy >> /tmp/mcp-deploy.log 2>&1
```

### Deployment in CI/CD

Integrate office deployment in your workflows:

```bash
#!/bin/bash
# deploy-office.sh

set -e

echo "🔍 Checking office machine connectivity..."
uv run python -m mcp_manager.cli office status

echo "🚀 Deploying MCP configuration..."
uv run python -m mcp_manager.cli office deploy

echo "✅ Verifying deployment..."
uv run python -m mcp_manager.cli office verify

echo "✨ Office deployment complete!"
```

### Managing Multiple Offices

You can manage different office locations by using profiles:

```bash
# Register machines with location prefixes
uv run python -m mcp_manager.cli office register hq-pc-01 192.168.1.100 --user kkk
uv run python -m mcp_manager.cli office register branch-pc-01 192.168.2.100 --user kkk

# Deploy to all
uv run python -m mcp_manager.cli office deploy
```

## Configuration Files

### Office Nodes Registry

Location: `~/.config/mcp-manager/office-nodes.json`

Structure:
```json
{
  "office-pc-01": {
    "hostname": "office-pc-01",
    "ip_address": "192.168.1.100",
    "ssh_user": "kkk",
    "ssh_key_path": "/home/kkk/.ssh/id_rsa",
    "status": "active",
    "last_sync": "2025-09-25T10:30:00",
    "mcp_config_hash": "a1b2c3d4e5f6g7h8"
  }
}
```

### MCP Configuration

Location: `~/.claude.json`

This is the file that gets deployed to all office machines.

## Best Practices

### 1. Master Machine Strategy

- **Designate one master machine** for configuration management
- Keep this machine's configuration as the source of truth
- Test changes locally before deploying

### 2. Deployment Workflow

1. ✅ Test locally first
2. ✅ Use `--dry-run` before actual deployment
3. ✅ Deploy during off-hours if possible
4. ✅ Verify after every deployment
5. ✅ Monitor office status regularly

### 3. Backup Strategy

- Automatic backups are created on remote machines
- Master machine backups: Manual Git tracking recommended
- Keep at least 5 recent backup files

### 4. Security Considerations

- ✅ Use SSH keys instead of passwords
- ✅ Restrict SSH key permissions (`chmod 600`)
- ✅ Use SSH config file for organization
- ✅ Regularly audit registered machines
- ✅ Remove unused machine registrations

### 5. Network Requirements

- All office machines must be on the same network or VPN
- Firewall must allow SSH (port 22) between machines
- Consider static IP addresses for stability
- Document IP address assignments

## Example Workflows

### Initial Office Setup

```bash
# Day 1: Setup master machine
cd ~/Apps/002-mcp-manager
uv venv .venv && source .venv/bin/activate
uv pip install -e .

# Configure MCP servers
uv run python -m mcp_manager.cli mcp setup-all

# Test configuration
claude mcp

# Get master machine info
uv run python -m mcp_manager.cli office info

# Register all office machines
uv run python -m mcp_manager.cli office register office-pc-01 192.168.1.100 --user kkk --key ~/.ssh/id_rsa
uv run python -m mcp_manager.cli office register office-pc-02 192.168.1.101 --user kkk --key ~/.ssh/id_rsa
uv run python -m mcp_manager.cli office register office-pc-03 192.168.1.102 --user kkk --key ~/.ssh/id_rsa

# Verify connectivity
uv run python -m mcp_manager.cli office status

# Deploy to all
uv run python -m mcp_manager.cli office deploy

# Verify synchronization
uv run python -m mcp_manager.cli office verify
```

### Adding New MCP Server

```bash
# 1. Add server locally
uv run python -m mcp_manager.cli mcp add my-server --type http --url https://api.example.com/mcp

# 2. Test locally
uv run python -m mcp_manager.cli mcp status my-server

# 3. Deploy to office
uv run python -m mcp_manager.cli office deploy

# 4. Verify
uv run python -m mcp_manager.cli office verify
```

### Regular Maintenance

```bash
# Weekly: Check office status
uv run python -m mcp_manager.cli office status

# Monthly: Verify all configurations
uv run python -m mcp_manager.cli office verify

# As needed: Re-sync specific machine
uv run python -m mcp_manager.cli office deploy office-pc-01
```

## Getting Help

### CLI Help

```bash
# Office management help
uv run python -m mcp_manager.cli office --help

# Specific command help
uv run python -m mcp_manager.cli office deploy --help
```

### Command Reference

| Command | Description |
|---------|-------------|
| `office register` | Register new office machine |
| `office list` | List all registered machines |
| `office remove` | Remove machine from registry |
| `office status` | Show deployment status |
| `office check` | Test SSH connectivity |
| `office deploy` | Deploy MCP configuration |
| `office verify` | Verify configuration sync |
| `office pull` | Pull config from remote |
| `office info` | Show current machine info |

## Next Steps

- [MCP Server Management](../README.md#mcp-server-management)
- [Project Standardization](../README.md#project-standardization)
- [Fleet Management](../README.md#fleet-management)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)

---

**Version**: 1.0.0
**Last Updated**: 2025-09-25
**Maintainer**: @kairin
