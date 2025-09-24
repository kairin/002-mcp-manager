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
                "headers": {"X-API-Key": None}  # Will be preserved from existing config
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
                "headers": {"Authorization": None}  # Will be preserved from existing config
            },
            "markitdown": {
                "type": "stdio",
                "command": "uv",
                "args": ["run", "markitdown-mcp"]
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
        
        # Check global configuration
        if self.claude_config_path.exists():
            with open(self.claude_config_path, 'r') as f:
                data = json.load(f)
                
            # Get global MCP servers
            global_mcp = data.get("mcpServers", {})
            audit_results["global"] = global_mcp
            
            # Check project-specific configurations
            if "projects" in data:
                for project_path, project_config in data["projects"].items():
                    project_mcp = project_config.get("mcpServers", {})
                    if project_mcp:
                        audit_results["projects"][project_path] = project_mcp
                        if project_mcp != {}:
                            audit_results["issues"].append(
                                f"Project '{project_path}' has local MCP configuration"
                            )
        
        # Search for local .mcp.json files
        for mcp_file in self.home_dir.rglob(".mcp.json"):
            audit_results["local_files"].append(str(mcp_file))
            audit_results["issues"].append(f"Found local MCP file: {mcp_file}")
            
        # Generate recommendations
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
            # Change to specified directory and run mcp list
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
                for line in lines[1:]:  # Skip header
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
            
        # Preserve existing authentication keys
        existing_global = data.get("mcpServers", {})
        if "context7" in existing_global:
            if "headers" in existing_global["context7"]:
                self.required_servers["context7"]["headers"]["X-API-Key"] = \
                    existing_global["context7"]["headers"].get("X-API-Key")
        if "hf-mcp-server" in existing_global:
            if "headers" in existing_global["hf-mcp-server"]:
                self.required_servers["hf-mcp-server"]["headers"]["Authorization"] = \
                    existing_global["hf-mcp-server"]["headers"].get("Authorization")
                    
        # Collect all MCP servers from projects
        all_servers = dict(existing_global)
        
        if "projects" in data:
            for project_path, project_config in data["projects"].items():
                project_mcp = project_config.get("mcpServers", {})
                if project_mcp and project_mcp != {}:
                    # Merge project servers into global
                    for server_name, server_config in project_mcp.items():
                        if server_name not in all_servers:
                            all_servers[server_name] = server_config
                            migration_results["migrated_servers"][server_name] = {
                                "from": project_path,
                                "config": server_config
                            }
                    # Clear project-specific MCP servers
                    project_config["mcpServers"] = {}
                    migration_results["cleaned_projects"].append(project_path)
        
        # Ensure all required servers are present
        for server_name, server_config in self.required_servers.items():
            if server_name not in all_servers:
                # Only add if we have valid auth for servers that need it
                if server_name == "context7" and not server_config["headers"]["X-API-Key"]:
                    continue  # Skip if no API key
                if server_name == "hf-mcp-server" and not server_config["headers"]["Authorization"]:
                    continue  # Skip if no HF token
                all_servers[server_name] = server_config
                
        # Update global configuration
        data["mcpServers"] = all_servers
        
        # Write back the configuration
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
            
        # Ensure mcpServers exists
        if "mcpServers" not in data:
            data["mcpServers"] = {}
            
        # Add the new server
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
            
        # Write back the configuration
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
        
        # Remove local .mcp.json files
        for mcp_file in self.home_dir.rglob(".mcp.json"):
            try:
                mcp_file.unlink()
                cleanup_results["removed_files"].append(str(mcp_file))
            except Exception as e:
                cleanup_results["errors"] = cleanup_results.get("errors", [])
                cleanup_results["errors"].append(f"Failed to remove {mcp_file}: {e}")
                
        # Clean empty project configurations
        if self.claude_config_path.exists():
            with open(self.claude_config_path, 'r') as f:
                data = json.load(f)
                
            if "projects" in data:
                projects_to_remove = []
                for project_path, project_config in data["projects"].items():
                    # Remove projects with empty or default configurations
                    if not project_config or project_config == {"mcpServers": {}}:
                        projects_to_remove.append(project_path)
                        
                for project_path in projects_to_remove:
                    del data["projects"][project_path]
                    cleanup_results["cleaned_projects"].append(project_path)
                    
                # If projects is now empty, remove it
                if not data["projects"]:
                    del data["projects"]
                    
            # Write back cleaned configuration
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
        
        # Global Configuration Status
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
        
        # Health Check Results
        report.append("🏥 HEALTH CHECK RESULTS:")
        report.append("-" * 40)
        if "servers" in health:
            for server, status in health["servers"].items():
                icon = "✅" if status == "Connected" else "❌"
                report.append(f"   {icon} {server}: {status}")
        elif "error" in health:
            report.append(f"   ❌ Error: {health['error']}")
        report.append("")
        
        # Issues and Recommendations
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
            
        # Migration Results
        if migration:
            report.append("🔄 MIGRATION RESULTS:")
            report.append("-" * 40)
            if migration["migrated_servers"]:
                report.append(f"   ✅ Migrated {len(migration['migrated_servers'])} servers to global")
            if migration["cleaned_projects"]:
                report.append(f"   ✅ Cleaned {len(migration['cleaned_projects'])} project configs")
            report.append("")
            
        # Summary
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
        
        # Step 1: Audit
        print("📍 Step 1: Auditing configurations...")
        audit = self.audit_configurations()
        
        # Step 2: Migrate
        print("📍 Step 2: Migrating local configs to global...")
        migration = self.migrate_to_global()
        
        # Step 3: Clean
        print("📍 Step 3: Cleaning orphaned configurations...")
        cleanup = self.clean_orphaned_configs()
        
        # Step 4: Verify
        print("📍 Step 4: Verifying MCP server health...")
        health = self.verify_mcp_health()
        
        # Re-audit after changes
        print("📍 Step 5: Final audit...")
        final_audit = self.audit_configurations()
        
        # Generate report
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
    
    # Arguments for add command
    parser.add_argument("--name", help="Server name (for add command)")
    parser.add_argument("--type", choices=["http", "stdio"], help="Server type")
    parser.add_argument("--url", help="Server URL (for HTTP servers)")
    parser.add_argument("--command", help="Command (for stdio servers)")
    parser.add_argument("--args", nargs="*", help="Arguments (for stdio servers)")
    parser.add_argument("--headers", type=json.loads, help="Headers as JSON (for HTTP servers)")
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = MCPGlobalManager(args.home_dir)
    
    # Execute command
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
        else:  # stdio
            if not args.command:
                print("Error: --command required for stdio servers")
                sys.exit(1)
            config["command"] = args.command
            config["args"] = args.args or []
            
        result = manager.add_mcp_server(args.name, args.type, config)
        print(json.dumps(result, indent=2))
        
    else:  # full
        report = manager.run_full_setup()
        print(report)
        
        # Also save report to file
        report_path = Path.home() / "mcp_setup_report.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_path}")

if __name__ == "__main__":
    main()
