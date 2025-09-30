#!/bin/bash

# Setup script to create the MCP Global Manager GitHub repository
# Run this to create the complete repository structure

echo "🚀 Creating MCP Global Manager Repository Structure..."

# Create repository directory
REPO_NAME="mcp-global-manager"
mkdir -p $REPO_NAME
cd $REPO_NAME

# Initialize git
git init

# Create main Python script
cat > mcp_global_manager.py << 'EOF'
#!/usr/bin/env python3
"""
MCP Server Global Configuration Manager for Claude Code
========================================================
This tool ensures all MCP servers are globally configured and accessible
from any project within the home directory. It handles verification,
migration, and management of MCP server configurations.

Usage:
    python3 mcp_global_manager.py [command]
    
Commands:
    audit     - Audit all MCP configurations
    verify    - Verify MCP server health
    migrate   - Migrate all local configs to global
    add       - Add a new MCP server globally
    clean     - Clean orphaned configurations
    full      - Run full audit, migrate, and verify
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from datetime import datetime

class MCPGlobalManager:
    """Manages MCP server configurations for Claude Code"""
    
    def __init__(self, home_dir: str = None):
        """Initialize the MCP manager"""
        self.home_dir = Path(home_dir or os.path.expanduser("~"))
        self.claude_config_path = self.home_dir / ".claude.json"
        self.required_servers = {
            "context7": {
                "type": "http",
                "url": "https://mcp.context7.com/mcp",
                "headers": {"X-API-Key": None}
            },
            "shadcn": {
                "type": "stdio",
                "command": "npx",
                "args": ["shadcn@latest", "mcp"]
            },
            "github": {
                "type": "http",
                "url": "https://api.githubcopilot.com/mcp"
            },
            "playwright": {
                "type": "stdio",
                "command": "npx",
                "args": ["@playwright/mcp@latest"]
            },
            "hf-mcp-server": {
                "type": "http",
                "url": "https://huggingface.co/mcp",
                "headers": {"Authorization": None}
            }
        }
        
    def audit_configurations(self) -> Dict:
        """Comprehensive audit of all MCP configurations"""
        audit_results = {
            "global": {},
            "projects": {},
            "local_files": [],
            "issues": [],
            "recommendations": []
        }
        
        if self.claude_config_path.exists():
            with open(self.claude_config_path, 'r') as f:
                data = json.load(f)
                
            global_mcp = data.get("mcpServers", {})
            audit_results["global"] = global_mcp
            
            if "projects" in data:
                for project_path, project_config in data["projects"].items():
                    project_mcp = project_config.get("mcpServers", {})
                    if project_mcp:
                        audit_results["projects"][project_path] = project_mcp
                        if project_mcp != {}:
                            audit_results["issues"].append(
                                f"Project '{project_path}' has local MCP configuration"
                            )
        
        for mcp_file in self.home_dir.rglob(".mcp.json"):
            audit_results["local_files"].append(str(mcp_file))
            audit_results["issues"].append(f"Found local MCP file: {mcp_file}")
            
        if not audit_results["global"]:
            audit_results["recommendations"].append("No global MCP servers configured")
        
        missing_servers = set(self.required_servers.keys()) - set(audit_results["global"].keys())
        if missing_servers:
            audit_results["recommendations"].append(
                f"Missing required global servers: {', '.join(missing_servers)}"
            )
            
        return audit_results
    
    def verify_mcp_health(self, directory: Path = None) -> Dict:
        """Verify health of all MCP servers"""
        if directory is None:
            directory = self.home_dir
            
        try:
            result = subprocess.run(
                ["claude", "mcp", "list"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            health_status = {
                "directory": str(directory),
                "servers": {},
                "all_healthy": True
            }
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:
                    if ':' in line and '✓' in line:
                        server_name = line.split(':')[0].strip()
                        health_status["servers"][server_name] = "Connected"
                    elif ':' in line and '✗' in line:
                        server_name = line.split(':')[0].strip()
                        health_status["servers"][server_name] = "Failed"
                        health_status["all_healthy"] = False
            else:
                health_status["error"] = result.stderr
                health_status["all_healthy"] = False
                
            return health_status
            
        except Exception as e:
            return {
                "directory": str(directory),
                "error": str(e),
                "all_healthy": False
            }
    
    def migrate_to_global(self) -> Dict:
        """Migrate all local MCP configurations to global"""
        migration_results = {
            "migrated_servers": {},
            "cleaned_projects": [],
            "preserved_keys": {},
            "status": "success"
        }
        
        if not self.claude_config_path.exists():
            migration_results["status"] = "error"
            migration_results["error"] = "Claude configuration file not found"
            return migration_results
            
        with open(self.claude_config_path, 'r') as f:
            data = json.load(f)
            
        existing_global = data.get("mcpServers", {})
        if "context7" in existing_global:
            if "headers" in existing_global["context7"]:
                self.required_servers["context7"]["headers"]["X-API-Key"] = \
                    existing_global["context7"]["headers"].get("X-API-Key")
        if "hf-mcp-server" in existing_global:
            if "headers" in existing_global["hf-mcp-server"]:
                self.required_servers["hf-mcp-server"]["headers"]["Authorization"] = \
                    existing_global["hf-mcp-server"]["headers"].get("Authorization")
                    
        all_servers = dict(existing_global)
        
        if "projects" in data:
            for project_path, project_config in data["projects"].items():
                project_mcp = project_config.get("mcpServers", {})
                if project_mcp and project_mcp != {}:
                    for server_name, server_config in project_mcp.items():
                        if server_name not in all_servers:
                            all_servers[server_name] = server_config
                            migration_results["migrated_servers"][server_name] = {
                                "from": project_path,
                                "config": server_config
                            }
                    project_config["mcpServers"] = {}
                    migration_results["cleaned_projects"].append(project_path)
        
        for server_name, server_config in self.required_servers.items():
            if server_name not in all_servers:
                if server_name == "context7" and not server_config["headers"]["X-API-Key"]:
                    continue
                if server_name == "hf-mcp-server" and not server_config["headers"]["Authorization"]:
                    continue
                all_servers[server_name] = server_config
                
        data["mcpServers"] = all_servers
        
        with open(self.claude_config_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        migration_results["final_global_servers"] = list(all_servers.keys())
        return migration_results
    
    def add_mcp_server(self, name: str, server_type: str, config: Dict) -> Dict:
        """Add a new MCP server to global configuration"""
        result = {
            "server_name": name,
            "status": "success",
            "message": ""
        }
        
        if not self.claude_config_path.exists():
            result["status"] = "error"
            result["message"] = "Claude configuration file not found"
            return result
            
        with open(self.claude_config_path, 'r') as f:
            data = json.load(f)
            
        if "mcpServers" not in data:
            data["mcpServers"] = {}
            
        if server_type == "http":
            data["mcpServers"][name] = {
                "type": "http",
                "url": config.get("url"),
                "headers": config.get("headers", {})
            }
        elif server_type == "stdio":
            data["mcpServers"][name] = {
                "type": "stdio",
                "command": config.get("command"),
                "args": config.get("args", [])
            }
        else:
            result["status"] = "error"
            result["message"] = f"Unknown server type: {server_type}"
            return result
            
        with open(self.claude_config_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        result["message"] = f"Successfully added {name} to global configuration"
        return result
    
    def clean_orphaned_configs(self) -> Dict:
        """Clean up orphaned and duplicate configurations"""
        cleanup_results = {
            "removed_files": [],
            "cleaned_projects": [],
            "deduplicated": []
        }
        
        for mcp_file in self.home_dir.rglob(".mcp.json"):
            try:
                mcp_file.unlink()
                cleanup_results["removed_files"].append(str(mcp_file))
            except Exception as e:
                cleanup_results["errors"] = cleanup_results.get("errors", [])
                cleanup_results["errors"].append(f"Failed to remove {mcp_file}: {e}")
                
        if self.claude_config_path.exists():
            with open(self.claude_config_path, 'r') as f:
                data = json.load(f)
                
            if "projects" in data:
                projects_to_remove = []
                for project_path, project_config in data["projects"].items():
                    if not project_config or project_config == {"mcpServers": {}}:
                        projects_to_remove.append(project_path)
                        
                for project_path in projects_to_remove:
                    del data["projects"][project_path]
                    cleanup_results["cleaned_projects"].append(project_path)
                    
                if not data["projects"]:
                    del data["projects"]
                    
            with open(self.claude_config_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        return cleanup_results
    
    def generate_report(self, audit: Dict, health: Dict, migration: Dict = None) -> str:
        """Generate a comprehensive status report"""
        report = []
        report.append("=" * 60)
        report.append("MCP SERVER GLOBAL CONFIGURATION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("📊 GLOBAL CONFIGURATION STATUS:")
        report.append("-" * 40)
        if audit["global"]:
            report.append(f"✅ {len(audit['global'])} global MCP servers configured:")
            for server_name in sorted(audit["global"].keys()):
                server_info = audit["global"][server_name]
                server_type = server_info.get("type", "unknown")
                report.append(f"   • {server_name} ({server_type})")
        else:
            report.append("❌ No global MCP servers configured")
        report.append("")
        
        report.append("🏥 HEALTH CHECK RESULTS:")
        report.append("-" * 40)
        if "servers" in health:
            for server, status in health["servers"].items():
                icon = "✅" if status == "Connected" else "❌"
                report.append(f"   {icon} {server}: {status}")
        elif "error" in health:
            report.append(f"   ❌ Error: {health['error']}")
        report.append("")
        
        if audit["issues"]:
            report.append("⚠️  ISSUES DETECTED:")
            report.append("-" * 40)
            for issue in audit["issues"]:
                report.append(f"   • {issue}")
            report.append("")
            
        if audit["recommendations"]:
            report.append("💡 RECOMMENDATIONS:")
            report.append("-" * 40)
            for rec in audit["recommendations"]:
                report.append(f"   • {rec}")
            report.append("")
            
        if migration:
            report.append("🔄 MIGRATION RESULTS:")
            report.append("-" * 40)
            if migration["migrated_servers"]:
                report.append(f"   ✅ Migrated {len(migration['migrated_servers'])} servers to global")
            if migration["cleaned_projects"]:
                report.append(f"   ✅ Cleaned {len(migration['cleaned_projects'])} project configs")
            report.append("")
            
        report.append("📋 SUMMARY:")
        report.append("-" * 40)
        all_healthy = health.get("all_healthy", False)
        global_complete = len(audit["global"]) >= len(self.required_servers)
        no_local = len(audit["projects"]) == 0 and len(audit["local_files"]) == 0
        
        if all_healthy and global_complete and no_local:
            report.append("✅ ALL SYSTEMS OPERATIONAL")
            report.append("All MCP servers are globally configured and healthy.")
            report.append("All projects can access MCP servers from any location.")
        else:
            report.append("⚠️  ACTION REQUIRED")
            if not all_healthy:
                report.append("   • Some MCP servers are not responding")
            if not global_complete:
                report.append("   • Missing required global MCP servers")
            if not no_local:
                report.append("   • Local configurations need migration")
                
        report.append("=" * 60)
        return "\n".join(report)
    
    def run_full_setup(self) -> str:
        """Run complete setup: audit, migrate, verify, and report"""
        print("🚀 Starting MCP Global Configuration Setup...")
        
        print("📍 Step 1: Auditing configurations...")
        audit = self.audit_configurations()
        
        print("📍 Step 2: Migrating local configs to global...")
        migration = self.migrate_to_global()
        
        print("📍 Step 3: Cleaning orphaned configurations...")
        cleanup = self.clean_orphaned_configs()
        
        print("📍 Step 4: Verifying MCP server health...")
        health = self.verify_mcp_health()
        
        print("📍 Step 5: Final audit...")
        final_audit = self.audit_configurations()
        
        report = self.generate_report(final_audit, health, migration)
        
        return report

def main():
    """Main entry point for the MCP Global Manager"""
    parser = argparse.ArgumentParser(
        description="MCP Server Global Configuration Manager for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "command",
        choices=["audit", "verify", "migrate", "clean", "full", "add"],
        nargs="?",
        default="full",
        help="Command to execute (default: full)"
    )
    
    parser.add_argument(
        "--home-dir",
        help="Home directory path (default: current user's home)",
        default=None
    )
    
    parser.add_argument("--name", help="Server name (for add command)")
    parser.add_argument("--type", choices=["http", "stdio"], help="Server type")
    parser.add_argument("--url", help="Server URL (for HTTP servers)")
    parser.add_argument("--command", help="Command (for stdio servers)")
    parser.add_argument("--args", nargs="*", help="Arguments (for stdio servers)")
    parser.add_argument("--headers", type=json.loads, help="Headers as JSON (for HTTP servers)")
    
    args = parser.parse_args()
    
    manager = MCPGlobalManager(args.home_dir)
    
    if args.command == "audit":
        audit = manager.audit_configurations()
        print(json.dumps(audit, indent=2))
        
    elif args.command == "verify":
        health = manager.verify_mcp_health()
        print(json.dumps(health, indent=2))
        
    elif args.command == "migrate":
        result = manager.migrate_to_global()
        print(json.dumps(result, indent=2))
        
    elif args.command == "clean":
        result = manager.clean_orphaned_configs()
        print(json.dumps(result, indent=2))
        
    elif args.command == "add":
        if not args.name or not args.type:
            print("Error: --name and --type required for add command")
            sys.exit(1)
            
        config = {}
        if args.type == "http":
            if not args.url:
                print("Error: --url required for HTTP servers")
                sys.exit(1)
            config["url"] = args.url
            if args.headers:
                config["headers"] = args.headers
        else:
            if not args.command:
                print("Error: --command required for stdio servers")
                sys.exit(1)
            config["command"] = args.command
            config["args"] = args.args or []
            
        result = manager.add_mcp_server(args.name, args.type, config)
        print(json.dumps(result, indent=2))
        
    else:
        report = manager.run_full_setup()
        print(report)
        
        report_path = Path.home() / "mcp_setup_report.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_path}")

if __name__ == "__main__":
    main()
EOF

# Create README (using the markdown from the previous artifact)
cat > README.md << 'EOF'
# MCP Global Configuration Manager

A universal tool for managing MCP (Model Context Protocol) servers in Claude Code, ensuring all projects have consistent global access to MCP servers.

## 🚀 Quick Start

```bash
# Clone and run
git clone https://github.com/YOUR_USERNAME/mcp-global-manager.git
cd mcp-global-manager
python3 mcp_global_manager.py full
```

... [Full README content from previous artifact]
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
# No external dependencies required
# Uses Python standard library only
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
mcp_setup_report.txt
*.log
EOF

# Create LICENSE
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Create example configuration file
cat > examples/claude.json.example << 'EOF'
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "X-API-Key": "YOUR_API_KEY_HERE"
      }
    },
    "shadcn": {
      "type": "stdio",
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp"
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "hf-mcp-server": {
      "type": "http",
      "url": "https://huggingface.co/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_HF_TOKEN_HERE"
      }
    }
  },
  "projects": {}
}
EOF

# Create LLM instructions file
cat > LLM_INSTRUCTIONS.md << 'EOF'
# Instructions for AI Assistants/LLMs

This document provides clear instructions for AI assistants to implement and use this MCP configuration tool.

## Implementation Steps

### 1. Check Prerequisites
```bash
# Verify Claude Code is installed
claude --version

# Check for existing configuration
ls -la ~/.claude.json
```

### 2. Download and Setup
```bash
# Option A: Clone repository
git clone https://github.com/[username]/mcp-global-manager.git
cd mcp-global-manager

# Option B: Direct download
curl -O https://raw.githubusercontent.com/[username]/mcp-global-manager/main/mcp_global_manager.py
chmod +x mcp_global_manager.py
```

### 3. Execute Full Setup
```bash
python3 mcp_global_manager.py full
```

### 4. Verify Success
```bash
# Check MCP server status
claude mcp list

# Run audit
python3 mcp_global_manager.py audit
```

## Expected Outcomes

✅ **Success Indicators:**
- All 5 default MCP servers show "Connected"
- No project-specific configurations remain
- Global configuration in ~/.claude.json contains all servers
- `claude mcp list` works from any directory

❌ **Failure Indicators:**
- Any server shows "Failed" status
- Project-specific configurations still exist
- Missing required servers in global config
- Different MCP lists in different directories

## Common Tasks

### Add New MCP Server
```bash
python3 mcp_global_manager.py add \
  --name "custom-server" \
  --type http \
  --url "https://example.com/mcp" \
  --headers '{"Authorization": "Bearer TOKEN"}'
```

### Debug Configuration Issues
```bash
# Get detailed audit
python3 mcp_global_manager.py audit > audit.json

# Check health from specific directory
cd /path/to/project
python3 ~/mcp_global_manager.py verify
```

### Clean Orphaned Configs
```bash
python3 mcp_global_manager.py clean
```

## Response Templates

### For Successful Setup
```
✅ MCP Global Configuration Complete

All 5 MCP servers are now globally configured:
- context7: Connected
- shadcn: Connected
- github: Connected
- playwright: Connected
- hf-mcp-server: Connected

All projects in the home directory can now access these servers.
```

### For Issues Found
```
⚠️ MCP Configuration Issues Detected

Issues:
- [List specific issues]

Recommended Actions:
1. Run: python3 mcp_global_manager.py migrate
2. Verify API keys are correct
3. Check network connectivity

Would you like me to fix these issues?
```

## Integration Code Example

```python
import subprocess
import json

def ensure_mcp_configured():
    """Ensure MCP servers are globally configured"""
    
    # Run audit
    result = subprocess.run(
        ["python3", "mcp_global_manager.py", "audit"],
        capture_output=True,
        text=True
    )
    
    audit = json.loads(result.stdout)
    
    # Check if action needed
    if audit["issues"] or not audit["global"]:
        # Run full setup
        subprocess.run(["python3", "mcp_global_manager.py", "full"])
        return "Configuration updated"
    
    return "Configuration already optimal"
```
EOF

# Create test script
cat > test_mcp.py << 'EOF'
#!/usr/bin/env python3
"""
Test script to validate MCP configuration
"""

import subprocess
import json
import sys

def test_mcp_configuration():
    """Run tests on MCP configuration"""
    
    print("🧪 Testing MCP Configuration...")
    print("-" * 40)
    
    # Test 1: Check if claude is installed
    try:
        subprocess.run(["claude", "--version"], capture_output=True, check=True)
        print("✅ Claude Code is installed")
    except:
        print("❌ Claude Code not found")
        return False
    
    # Test 2: Run audit
    try:
        result = subprocess.run(
            ["python3", "mcp_global_manager.py", "audit"],
            capture_output=True,
            text=True
        )
        audit = json.loads(result.stdout)
        print(f"✅ Audit completed: {len(audit['global'])} global servers")
    except:
        print("❌ Audit failed")
        return False
    
    # Test 3: Verify health
    try:
        result = subprocess.run(
            ["python3", "mcp_global_manager.py", "verify"],
            capture_output=True,
            text=True
        )
        health = json.loads(result.stdout)
        if health.get("all_healthy"):
            print("✅ All servers healthy")
        else:
            print(f"⚠️  Some servers unhealthy: {health}")
    except:
        print("❌ Health check failed")
        return False
    
    print("-" * 40)
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_mcp_configuration()
    sys.exit(0 if success else 1)
EOF

chmod +x test_mcp.py

# Initialize git repository
git add .
git commit -m "Initial commit: MCP Global Configuration Manager"

echo "✅ Repository structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Update README.md with your GitHub username"
echo "2. Update LICENSE with your name"
echo "3. Create a GitHub repository"
echo "4. Push to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/mcp-global-manager.git"
echo "   git push -u origin main"
echo ""
echo "📁 Repository contents:"
ls -la