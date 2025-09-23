"""Project Standardization Manager for MCP Manager."""

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from .exceptions import MCPManagerError


@dataclass
class ProjectStandard:
    """Represents a project standardization requirement."""

    name: str
    description: str
    check_command: str
    fix_command: str
    required: bool = True
    files_to_create: list[str] = None
    files_to_modify: list[str] = None


class ProjectStandardsManager:
    """Manages project standardization across all repositories."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self.home_dir = Path.home()
        self.standards = self._load_standards()

    def _load_standards(self) -> dict[str, ProjectStandard]:
        """Load project standardization requirements."""
        return {
            "branch_strategy": ProjectStandard(
                name="Branch Strategy",
                description="YYYYMMDD-HHMMSS-type-description branch naming",
                check_command="git config --get branch.main.remote",
                fix_command="mcp-manager project fix-branching",
                files_to_create=[".github/branch-protection.yml"],
            ),
            "astro_pages": ProjectStandard(
                name="Astro GitHub Pages",
                description="Astro.build with automatic .nojekyll generation",
                check_command="test -f astro.config.mjs && test -f docs/.nojekyll",
                fix_command="mcp-manager project setup-astro",
                files_to_create=["astro.config.mjs", "package.json"],
            ),
            "local_cicd": ProjectStandard(
                name="Local CI/CD",
                description="Zero-cost local workflows before GitHub push",
                check_command="test -f local-infra/runners/gh-workflow-local.sh",
                fix_command="mcp-manager project setup-local-cicd",
                files_to_create=["local-infra/runners/gh-workflow-local.sh"],
            ),
            "uv_python": ProjectStandard(
                name="UV Python Management",
                description="uv-based Python environment and dependency management",
                check_command="test -f pyproject.toml && grep -q 'requires-python.*3.13' pyproject.toml",
                fix_command="mcp-manager project setup-uv-python",
                files_to_create=["pyproject.toml", ".python-version"],
            ),
            "spec_kit": ProjectStandard(
                name="Spec-Kit Integration",
                description="Ready for spec-kit workflow integration",
                check_command="test -f AGENTS.md && test -L CLAUDE.md && test -L GEMINI.md",
                fix_command="mcp-manager project setup-spec-kit",
                files_to_create=["AGENTS.md"],
                files_to_modify=["CLAUDE.md", "GEMINI.md"],
            ),
            "shadcn_ui": ProjectStandard(
                name="shadcn/ui + Tailwind",
                description="Consistent design system with shadcn/ui and Tailwind CSS",
                check_command="test -f components.json && test -f tailwind.config.mjs",
                fix_command="mcp-manager project setup-design-system",
                files_to_create=["components.json", "tailwind.config.mjs"],
            ),
        }

    def audit_project(self, project_path: Path) -> dict[str, dict[str, Any]]:
        """Audit a single project for compliance with standards."""
        results = {}

        for standard_id, standard in self.standards.items():
            result = {"compliant": False, "issues": [], "recommendations": []}

            try:
                # Change to project directory for checks
                original_cwd = Path.cwd()
                project_path.resolve()

                if project_path.exists() and project_path.is_dir():
                    # Run compliance check
                    check_result = subprocess.run(
                        standard.check_command,
                        shell=True,
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                    )

                    result["compliant"] = check_result.returncode == 0

                    if not result["compliant"]:
                        result["issues"].append(
                            f"Failed check: {standard.check_command}"
                        )
                        result["recommendations"].append(f"Run: {standard.fix_command}")

                        # Check for missing files
                        if standard.files_to_create:
                            for file_path in standard.files_to_create:
                                full_path = project_path / file_path
                                if not full_path.exists():
                                    result["issues"].append(
                                        f"Missing file: {file_path}"
                                    )

                else:
                    result["issues"].append("Project directory does not exist")

            except Exception as e:
                result["issues"].append(f"Check failed: {str(e)}")

            results[standard_id] = result

        return results

    def audit_all_projects(
        self, scan_dirs: list[str] | None = None
    ) -> dict[str, dict[str, Any]]:
        """Audit all projects in specified directories."""
        if scan_dirs is None:
            scan_dirs = [
                str(self.home_dir / "Apps"),
                str(self.home_dir / "projects"),
                str(self.home_dir / "repos"),
            ]

        results = {}

        for scan_dir in scan_dirs:
            scan_path = Path(scan_dir)
            if not scan_path.exists():
                continue

            for project_dir in scan_path.iterdir():
                if project_dir.is_dir() and (project_dir / ".git").exists():
                    project_name = f"{scan_path.name}/{project_dir.name}"
                    results[project_name] = self.audit_project(project_dir)

        return results

    def fix_project_standard(self, project_path: Path, standard_id: str) -> bool:
        """Fix a specific standard for a project."""
        if standard_id not in self.standards:
            raise MCPManagerError(f"Unknown standard: {standard_id}")

        standard = self.standards[standard_id]

        try:
            if standard_id == "branch_strategy":
                return self._fix_branch_strategy(project_path)
            elif standard_id == "astro_pages":
                return self._fix_astro_pages(project_path)
            elif standard_id == "local_cicd":
                return self._fix_local_cicd(project_path)
            elif standard_id == "uv_python":
                return self._fix_uv_python(project_path)
            elif standard_id == "spec_kit":
                return self._fix_spec_kit(project_path)
            elif standard_id == "shadcn_ui":
                return self._fix_shadcn_ui(project_path)
            else:
                # Generic fix using the fix command
                result = subprocess.run(
                    standard.fix_command,
                    shell=True,
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                )
                return result.returncode == 0

        except Exception as e:
            self.console.print(f"[red]Error fixing {standard_id}: {e}[/red]")
            return False

    def _fix_branch_strategy(self, project_path: Path) -> bool:
        """Implement branch strategy standardization."""
        try:
            # Create branch protection config
            github_dir = project_path / ".github"
            github_dir.mkdir(exist_ok=True)

            branch_protection = {
                "branch_protection": {
                    "naming_strategy": "YYYYMMDD-HHMMSS-type-description",
                    "preserve_branches": True,
                    "auto_merge_to_main": True,
                    "require_pr": False,
                }
            }

            with open(github_dir / "branch-protection.yml", "w") as f:
                import yaml

                yaml.dump(branch_protection, f, default_flow_style=False)

            return True
        except Exception as e:
            self.console.print(f"[red]Error setting up branch strategy: {e}[/red]")
            return False

    def _fix_astro_pages(self, project_path: Path) -> bool:
        """Set up Astro.build with GitHub Pages."""
        try:
            # Copy Astro config from mcp-manager template
            template_dir = Path(__file__).parent.parent.parent
            astro_config_src = template_dir / "astro.config.mjs"
            package_json_src = template_dir / "package.json"

            if astro_config_src.exists():
                shutil.copy2(astro_config_src, project_path / "astro.config.mjs")

            if package_json_src.exists():
                shutil.copy2(package_json_src, project_path / "package.json")

            # Create basic src structure
            src_dir = project_path / "src"
            src_dir.mkdir(exist_ok=True)

            # Create components and pages directories
            (src_dir / "components").mkdir(exist_ok=True)
            (src_dir / "pages").mkdir(exist_ok=True)

            return True
        except Exception as e:
            self.console.print(f"[red]Error setting up Astro: {e}[/red]")
            return False

    def _fix_local_cicd(self, project_path: Path) -> bool:
        """Set up local CI/CD infrastructure."""
        try:
            # Copy local-infra from mcp-manager template
            template_dir = Path(__file__).parent.parent.parent
            local_infra_src = template_dir / "local-infra"
            local_infra_dest = project_path / "local-infra"

            if local_infra_src.exists():
                shutil.copytree(local_infra_src, local_infra_dest, dirs_exist_ok=True)

                # Make scripts executable
                for script in local_infra_dest.rglob("*.sh"):
                    script.chmod(0o755)

            return True
        except Exception as e:
            self.console.print(f"[red]Error setting up local CI/CD: {e}[/red]")
            return False

    def _fix_uv_python(self, project_path: Path) -> bool:
        """Set up uv-based Python environment."""
        try:
            # Create pyproject.toml
            pyproject_content = f"""[project]
name = "{project_path.name}"
version = "0.1.0"
description = "Add your description here"
requires-python = ">=3.13"
dependencies = [
    "typer[all]>=0.12.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "black>=24.0.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 88
target-version = ["py313"]

[tool.ruff]
target-version = "py313"
line-length = 88

[tool.mypy]
python_version = "3.13"
strict = true
"""

            with open(project_path / "pyproject.toml", "w") as f:
                f.write(pyproject_content)

            # Create .python-version
            with open(project_path / ".python-version", "w") as f:
                f.write("3.13\n")

            return True
        except Exception as e:
            self.console.print(f"[red]Error setting up UV Python: {e}[/red]")
            return False

    def _fix_spec_kit(self, project_path: Path) -> bool:
        """Set up spec-kit integration."""
        try:
            # Create AGENTS.md
            agents_content = f"""# {project_path.name.replace('-', ' ').title()} - AI Agent Instructions

> 🤖 **CRITICAL**: This file contains NON-NEGOTIABLE requirements that ALL AI assistants (Claude, Gemini, ChatGPT, etc.) working on this repository MUST follow at ALL times.

## 🎯 Project Overview

**{project_path.name}** - Add your project description here.

**Repository**: https://github.com/kairin/{project_path.name}
**Integration**: Prepared for [spec-kit](https://github.com/kairin/spec-kit) workflow

## ⚡ NON-NEGOTIABLE REQUIREMENTS

### 🚨 CRITICAL: Branch Management & Git Strategy (MANDATORY)

#### Branch Preservation (MANDATORY)
- **NEVER DELETE BRANCHES** without explicit user permission
- **ALL BRANCHES** contain valuable development history
- **NO** automatic cleanup with `git branch -d`
- **YES** to automatic merge to main branch, preserving dedicated branch

#### Branch Naming (MANDATORY SCHEMA)
**Format**: `YYYYMMDD-HHMMSS-type-short-description`

Examples:
- `20250923-143000-feat-new-feature`
- `20250923-143515-fix-bug-description`
- `20250923-144030-docs-update-readme`

### 🚨 CRITICAL: Development Standards (MANDATORY)

#### Python Version & Dependencies
- **Python 3.13+**: Minimum required version
- **UV Package Manager**: ONLY package manager allowed
- **Modern Type Hints**: Full type annotations required

#### Code Quality (NON-NEGOTIABLE)
- **Black**: Code formatting
- **Ruff**: Linting and imports
- **MyPy**: Type checking
- **Pytest**: Testing framework

---

**Version**: 1.0
**Last Updated**: 2025-09-23
**Status**: ACTIVE - MANDATORY COMPLIANCE
"""

            with open(project_path / "AGENTS.md", "w") as f:
                f.write(agents_content)

            # Create symlinks for CLAUDE.md and GEMINI.md
            claude_link = project_path / "CLAUDE.md"
            gemini_link = project_path / "GEMINI.md"

            # Remove existing files if they exist
            if claude_link.exists() or claude_link.is_symlink():
                claude_link.unlink()
            if gemini_link.exists() or gemini_link.is_symlink():
                gemini_link.unlink()

            # Create symlinks
            claude_link.symlink_to("AGENTS.md")
            gemini_link.symlink_to("AGENTS.md")

            return True
        except Exception as e:
            self.console.print(f"[red]Error setting up spec-kit: {e}[/red]")
            return False

    def _fix_shadcn_ui(self, project_path: Path) -> bool:
        """Set up shadcn/ui and Tailwind CSS."""
        try:
            # Create components.json
            components_config = {
                "$schema": "https://ui.shadcn.com/schema.json",
                "style": "default",
                "rsc": False,
                "tsx": False,
                "tailwind": {
                    "config": "tailwind.config.mjs",
                    "css": "src/styles/globals.css",
                    "baseColor": "slate",
                    "cssVariables": True,
                },
                "aliases": {"components": "src/components", "utils": "src/lib/utils"},
            }

            with open(project_path / "components.json", "w") as f:
                json.dump(components_config, f, indent=2)

            # Create tailwind config
            tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  theme: {
    extend: {},
  },
  plugins: [],
}
"""

            with open(project_path / "tailwind.config.mjs", "w") as f:
                f.write(tailwind_config)

            return True
        except Exception as e:
            self.console.print(f"[red]Error setting up design system: {e}[/red]")
            return False

    def get_compliance_summary(
        self, audit_results: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate a compliance summary from audit results."""
        total_projects = len(audit_results)
        compliant_projects = 0
        total_standards = len(self.standards)

        standard_compliance = dict.fromkeys(self.standards.keys(), 0)

        for project_name, project_results in audit_results.items():
            project_compliant = True
            for standard_id, standard_result in project_results.items():
                if standard_result["compliant"]:
                    standard_compliance[standard_id] += 1
                else:
                    project_compliant = False

            if project_compliant:
                compliant_projects += 1

        return {
            "total_projects": total_projects,
            "compliant_projects": compliant_projects,
            "compliance_percentage": (
                (compliant_projects / total_projects * 100) if total_projects > 0 else 0
            ),
            "standard_compliance": standard_compliance,
            "total_standards": total_standards,
        }
