# MCP Manager: Areas for Improvement

This document outlines identified issues within the `mcp-manager` repository, their criticality, and suggestions for how to address them. This document is intended to be used by another LLM to implement the proposed changes.

---

## 1. Code and CLI Refinements

### 1.1. Reduce Code Duplication in `cli.py`

*   **File:** `src/mcp_manager/cli.py`
*   **Criticality:** **Medium** (Affects maintainability and readability)
*   **Issue:** The `cli.py` file contains a large number of repetitive `try...except MCPManagerError` blocks within each command function. This makes the code verbose and harder to maintain.
*   **Suggestion:** Centralize the error handling by using a custom decorator or a Typer callback. This would involve creating a single error-handling function that can be applied to all CLI commands, reducing code duplication and simplifying future modifications.

### 1.2. Organize the CLI with Submodules

*   **File:** `src/mcp_manager/cli.py`
*   **Criticality:** **Low** (Affects code organization and navigability)
*   **Issue:** The `cli.py` file is very large and contains the logic for all CLI commands. This can make it difficult to find and modify specific commands.
*   **Suggestion:** Split the CLI into multiple files, with each file managing a specific subcommand (e.g., `mcp.py`, `project.py`, `fleet.py`). Typer natively supports this structure, which would make the codebase more modular and easier to navigate.

### 1.3. Implement Missing Core Functionality

*   **File:** `src/mcp_manager/core.py`
*   **Criticality:** **High** (A core feature is not implemented)
*   **Issue:** The `update_server` and `update_all_servers` methods in `src/mcp_manager/core.py` are currently placeholders and do not contain any implementation.
*   **Suggestion:** Implement the logic for these methods. This would likely involve checking for new versions of stdio-based servers (e.g., via `npm view <package> version`) and providing a mechanism to update the configuration accordingly.

---

## 2. Configuration and Consistency

### 2.1. Remove Hardcoded Paths

*   **File:** `src/mcp_manager/core.py`
*   **Criticality:** **Medium** (Reduces flexibility and portability)
*   **Issue:** The `audit_configurations` method in `src/mcp_manager/core.py` uses hardcoded search directories (`~/Apps`, `~/projects`, `~/repos`). This limits the tool's usability for developers who organize their projects differently.
*   **Suggestion:** Make these search directories configurable. This could be achieved by adding a configuration option to `~/.claude.json` or by adding a command-line argument to the `project audit` command.

### 2.2. Synchronize Version Numbers

*   **Status:** ✅ **Completed**
*   **Files:**
    *   `pyproject.toml` (Single Source of Truth)
    *   `astro.config.mjs` (Build-time injection)
    *   `src/pages/index.astro`
    *   `src/components/Features.astro`
*   **Criticality:** Low
*   **Issue:** The project version number was hardcoded in several frontend files, leading to potential inconsistencies.
*   **Resolution:** The version is now dynamically read from `pyproject.toml` during the Astro build process and injected as an environment variable (`import.meta.env.PROJECT_VERSION`). This ensures the version number is consistent across the Python backend and the frontend components.
*   **Follow-up:** A minor issue remains in `src/pages/index.astro` where version numbers in the descriptive text for past updates ("Latest Updates" section) are still hardcoded (e.g., "Version 1.2.3"). While not breaking, these could be updated or removed for full consistency.

### 2.3. Refactor "Latest Updates" for Full Dynamism

*   **File:** `src/pages/index.astro`
*   **Criticality:** **Low** (Improves maintainability and adheres to best practices)
*   **Issue:** The "Latest Updates" section on the homepage contains hardcoded text and version numbers within its HTML structure. This makes the content difficult to update and mixes data with presentation.
*   **Suggestion:** Refactor the section to be data-driven. Move the content for the update cards into a data structure (an array of objects) in the component's frontmatter. Then, use Astro's template directives to render the cards by iterating over this array. This separates content from presentation, making it much easier to manage and update in the future.

#### Implementation Steps:

1.  **Define a data structure:** In the frontmatter of `src/pages/index.astro`, create an array named `updates` to hold the data for each card.
2.  **Render dynamically:** In the body of the component, replace the three hardcoded `<div>` blocks for the cards with a `.map()` call on the `updates` array.
3.  **Update the main heading:** Change the `<h2>` to use the dynamic project version.

#### Code to Implement:

This change can be implemented by replacing the "Version Highlight Section" in `src/pages/index.astro`.

**Old Code (`src/pages/index.astro`):**
```astro
{/* START: Old "Version Highlight Section" */}
<section class="bg-primary/5 py-16 sm:py-24">
  <div class="mx-auto max-w-7xl px-6 lg:px-8">
    <div class="mx-auto max-w-2xl text-center">
      <h2 class="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
        🎉 Latest Updates - Version 1.2.3
      </h2>
      <p class="mt-6 text-lg leading-8 text-muted-foreground">
        Comprehensive security framework, documentation consistency fixes, and constitutional governance.
      </p>
    </div>
    
    <div class="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-8 lg:mx-0 lg:max-w-none lg:grid-cols-3">
      <div class="flex flex-col bg-card rounded-2xl p-8 ring-1 ring-border">
        <div class="flex items-center gap-x-4">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
            <span class="text-primary-foreground">🔒</span>
          </div>
          <h3 class="text-lg font-semibold text-card-foreground">Security Framework v{version}</h3>
        </div>
        <p class="mt-4 text-sm text-muted-foreground">
          Information classification system, mandatory secret scanning, and template-only credential approach preventing 99% of exposures.
        </p>
      </div>
      
      <div class="flex flex-col bg-card rounded-2xl p-8 ring-1 ring-border">
        <div class="flex items-center gap-x-4">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
            <span class="text-primary-foreground">📋</span>
          </div>
          <h3 class="text-lg font-semibold text-card-foreground">Constitution v1.0.0</h3>
        </div>
        <p class="mt-4 text-sm text-muted-foreground">
          Seven mandatory principles: UV-first development, global configuration, zero downtime operations, branch preservation, and more.
        </p>
      </div>
      
      <div class="flex flex-col bg-card rounded-2xl p-8 ring-1 ring-border">
        <div class="flex items-center gap-x-4">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
            <span class="text-primary-foreground">📚</span>
          </div>
          <h3 class="text-lg font-semibold text-card-foreground">Documentation Fixes v1.2.2</h3>
        </div>
        <p class="mt-4 text-sm text-muted-foreground">
          GitHub MCP type corrections (HTTP → stdio), FOLLOWING-INSTRUCTIONS.md creation, and complete documentation consistency.
        </p>
      </div>
    </div>
    
    <div class="mt-12 text-center">
      <a href="https://github.com/kairin/mcp-manager/blob/main/CHANGELOG.md" class="text-sm font-semibold text-primary hover:text-primary/80">
        View complete changelog →
      </a>
    </div>
  </div>
</section>
{/* END: Old "Version Highlight Section" */}
```

**New Code (`src/pages/index.astro`):**
```astro
---
// (Existing frontmatter)
const updates = [
  {
    icon: '🔒',
    title: `Security Framework v${version}`,
    description: 'Information classification system, mandatory secret scanning, and template-only credential approach preventing 99% of exposures.',
  },
  {
    icon: '📋',
    title: 'Constitution v1.0.0',
    description: 'Seven mandatory principles: UV-first development, global configuration, zero downtime operations, branch preservation, and more.',
  },
  {
    icon: '📚',
    title: 'Documentation Fixes v1.2.2',
    description: 'GitHub MCP type corrections (HTTP → stdio), FOLLOWING-INSTRUCTIONS.md creation, and complete documentation consistency.',
  },
];
---
{/* (Existing Layout component) */}

{/* START: New "Version Highlight Section" */}
<section class="bg-primary/5 py-16 sm:py-24">
  <div class="mx-auto max-w-7xl px-6 lg:px-8">
    <div class="mx-auto max-w-2xl text-center">
      <h2 class="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
        🎉 Latest Updates - Version {version}
      </h2>
      <p class="mt-6 text-lg leading-8 text-muted-foreground">
        Comprehensive security framework, documentation consistency fixes, and constitutional governance.
      </p>
    </div>
    
    <div class="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-8 lg:mx-0 lg:max-w-none lg:grid-cols-3">
      {updates.map(update => (
        <div class="flex flex-col bg-card rounded-2xl p-8 ring-1 ring-border">
          <div class="flex items-center gap-x-4">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
              <span class="text-primary-foreground">{update.icon}</span>
            </div>
            <h3 class="text-lg font-semibold text-card-foreground">{update.title}</h3>
          </div>
          <p class="mt-4 text-sm text-muted-foreground">{update.description}</p>
        </div>
      ))}
    </div>
    
    <div class="mt-12 text-center">
      <a href="https://github.com/kairin/mcp-manager/blob/main/CHANGELOG.md" class="text-sm font-semibold text-primary hover:text-primary/80">
        View complete changelog →
      </a>
    </div>
  </div>
</section>
{/* END: New "Version Highlight Section" */}
```

---

## 3. Documentation and Frontend Accuracy

### 3.1. Align `README.md` with Project State

*   **Files:**
    *   `README.md`
    *   `pyproject.toml`
*   **Criticality:** **Medium** (Causes confusion for new contributors)
*   **Issue:** The `README.md` specifies Python 3.13 and Ubuntu 25.04, but `pyproject.toml` only requires Python >=3.11. The "One-Command Setup" is also not fully representative of the `init` command's capabilities.
*   **Suggestion:**
    *   Update the Python requirement in `README.md` to match `pyproject.toml` (>=3.11).
    *   Expand the "One-Command Setup" section to better describe the full initialization process.

### 3.2. Update Frontend Components

*   **File:** `src/components/Features.astro`
*   **Criticality:** **Low** (Minor visual inaccuracy)
*   **Issue:** The "Features" component on the homepage lists "5 critical MCP servers," but the project now supports six (including `MarkItDown`).
*   **Suggestion:** Update the text in `src/components/Features.astro` to state that there are six MCP servers.

### 3.3. Improve Documentation Discoverability

*   **File:** `README.md`
*   **Criticality:** **Low** (Reduces the value of existing documentation)
*   **Issue:** The `docs` directory contains valuable guides like `CHANGELOG.md` and `complete-mcp-guide.md` that are not linked from the main `README.md`.
---

## 4. Gemini CLI Integration

### 4.1. Configure MCP Servers for Gemini CLI

*   **Files:** `~/.config/gemini/settings.json` (or a project-specific `.gemini/settings.json`)
*   **Criticality:** **High** (Essential for using MCP servers with Gemini CLI)
*   **Issue:** The `mcp-manager` is currently configured to work with Claude Code's `~/.claude.json`. To use the same MCP servers with Gemini CLI, a similar configuration is needed.
*   **Suggestion:**

    The Gemini CLI uses a `settings.json` file for configuration, which supports an `mcpServers` object similar to Claude Code's `.claude.json`. To enable the existing MCP servers for Gemini, the following steps should be taken:

    1.  **Create or Locate `settings.json`**: The Gemini CLI configuration can be placed at either the user level (`~/.config/gemini/settings.json`) or the project level (`<project_root>/.gemini/settings.json`).

    2.  **Translate Configuration**: The `mcpServers` configuration from `~/.claude.json` can be translated to the `settings.json` file. The structure is nearly identical.

    **Example `settings.json` configuration:**

    ```json
    {
      "mcpServers": {
        "context7": {
          "type": "http",
          "url": "https://mcp.context7.com/mcp",
          "headers": {
            "CONTEXT7_API_KEY": "..."
          }
        },
        "shadcn": {
          "type": "stdio",
          "command": "npx",
          "args": [
            "shadcn@latest",
            "mcp"
          ]
        },
        "github": {
          "type": "stdio",
          "command": "sh",
          "args": [
            "-c",
            "GH_TOKEN=$(gh auth token) /home/kkk/.nvm/versions/node/v24.8.0/bin/npx @modelcontextprotocol/server-github"
          ]
        },
        "markitdown": {
          "type": "stdio",
          "command": "uv",
          "args": [
            "tool",
            "run",
            "markitdown-mcp"
          ]
        }
      }
    }
    ```

    3.  **Automate with `mcp-manager`**: A new feature could be added to `mcp-manager` to automatically generate or update the Gemini CLI's `settings.json` based on the existing `.claude.json` configuration. This would ensure that both CLIs are always synchronized. A new command, such as `mcp-manager sync-gemini`, could be implemented for this purpose.

### 4.2. System-Wide Gemini CLI Integration Strategy

*   **Goal:** Ensure that all MCP servers managed by `mcp-manager` are automatically available in the Gemini CLI across the entire system for the current user.
*   **Criticality:** **High**
*   **Suggestion:**

    To achieve system-wide integration, the `mcp-manager` tool should be updated to directly manage the Gemini CLI's global configuration file and ensure it is discoverable.

    1.  **Target Configuration File:** The primary file to create and manage is `~/.config/gemini/settings.json`. This will serve as the central, system-wide configuration for the user.

    2.  **Environment Variable for Discoverability**: The Gemini CLI uses the `GEMINI_CLI_SYSTEM_SETTINGS_PATH` environment variable to locate the system-wide settings file. This environment variable should be set in the user's shell profile (e.g., `~/.bashrc`, `~/.zshrc`) to point to the target configuration file:

        ```bash
        export GEMINI_CLI_SYSTEM_SETTINGS_PATH="$HOME/.config/gemini/settings.json"
        ```

    3.  **New CLI Command: `mcp-manager gemini sync`**

        A new command should be created to handle the synchronization.

        `mcp-manager gemini sync`

        This command should perform the following actions:
        *   Read the existing MCP server configurations from `~/.claude.json`.
        *   Read the existing Gemini CLI settings from `~/.config/gemini/settings.json`, if the file exists.
        *   Merge the MCP server configurations into the `mcpServers` section of the Gemini settings. If the `mcpServers` section already exists, the command should intelligently merge the servers, overwriting any with the same name.
        *   Write the updated configuration back to `~/.config/gemini/settings.json`.
        *   The command should create the file (and the directory `~/.config/gemini`) if it doesn't exist.

    4.  **Update `mcp-manager init`:** The main `mcp-manager init` command should be updated to call `mcp-manager gemini sync` and to add the `GEMINI_CLI_SYSTEM_SETTINGS_PATH` environment variable to the user's shell profile.

    5.  **Update `mcp-manager mcp add/remove`:** The `mcp-manager mcp add` and `mcp-manager mcp remove` commands should be updated to also modify the Gemini CLI `settings.json` file when the `--global` flag is used. This will keep both configurations in sync.

This approach will provide a seamless, system-wide integration between `mcp-manager` and the Gemini CLI.

---

## 5. Implementation Verification

### 5.1. Dynamic Versioning System (Verification Complete)

*   **Status:** ✅ **Verified**
*   **Summary:** A review of the dynamic versioning implementation was conducted by comparing the new code against best practices from the Google Python Style Guide and official Astro documentation.
*   **Findings:**
    *   **Python (`version_utils.py`):** The implementation is of high quality, demonstrating excellent adherence to best practices in documentation (docstrings), typing, code structure, and error handling.
    *   **Astro (`astro.config.mjs`, `.astro` files):** The method of injecting the version via Vite's `define` property is a pragmatic and effective solution. The variable is correctly accessed in the Astro components. The implementation aligns with common patterns in the Vite ecosystem.
*   **Conclusion:** The implementation successfully resolves the "Synchronize Version Numbers" issue (2.2) by creating a single source of truth for the project version. The code is robust, readable, and maintainable.

---

## 6. Repository Organization and Scripting

### 6.1. Clean Up Root Directory

*   **Criticality:** **Medium** (Affects project clarity and navigability)
*   **Issue:** The root directory is cluttered with numerous temporary status and log files (e.g., `PHASE2-COMPLETE.md`, `T041-COMPLETED.md`, `SESSION-SUMMARY.md`). These appear to be artifacts from development sessions.
*   **Impact:** This clutter makes it difficult to locate important configuration and documentation files, mixing ephemeral development logs with permanent project source code.
*   **Suggestion:**
    1.  **Review and Consolidate:** Check if any of these files contain critical information not present in `CHANGELOG.md` or git history. If so, consolidate that information into the appropriate permanent document.
    2.  **Delete:** Once reviewed, delete the temporary files.
    3.  **Future Workflow:** For future development, any similar logs or temporary artifacts should be written to a git-ignored directory, such as `.logs/` or `tmp/`.
*   **Files to Review/Delete:**
    *   `CLI-MODULARIZATION-COMPLETE.md`
    *   `IMPROVEMENT-PLAN-STATUS.md`
    *   `IMPROVEMENT-PLAN-VERIFICATION-COMPLETE.md`
    *   `PHASE2-COMPLETE.md`
    *   `PHASE2-ERROR-HANDLING-COMPLETE.md`
    *   `SESSION-SUMMARY.md`
    *   All `T...-COMPLETED.md` files

### 6.2. Audit and Refactor Scripts

*   **Criticality:** **Medium** (Affects maintainability and developer experience)
*   **Issue:** The `scripts/` directory contains multiple files with overlapping responsibilities, creating confusion about which scripts are current and which are legacy.
*   **Initial Analysis (`scripts/setup/`):
    *   `setup_hf_with_cli.py`: Appears to be the main, feature-complete script for setting up the Hugging Face MCP server with proper authentication.
    *   `setup_hf_mcp.py`: A simplified, unauthenticated setup script that is entirely superseded by the `..._with_cli.py` version.
    *   `hf_quick_setup.sh`: A thin wrapper that just calls the main Python script.
*   **Suggestion:**
    1.  **Consolidate:** Remove redundant scripts. For the Hugging Face setup, `setup_hf_mcp.py` should be deleted or moved to `scripts/legacy/`.
    2.  **Clarify Entry Points:** Decide if wrapper scripts like `hf_quick_setup.sh` are necessary. If so, keep them; if not, remove them to simplify the structure. The `Makefile` already provides clean, high-level commands (`make setup`, `make test`, etc.) and could be the primary entry point for developers.
    3.  **Document:** Add a `README.md` inside the `scripts/` directory to explain the purpose of each remaining script and its subdirectories (`deployment`, `git`, etc.).

---

## 7. Analysis of Development Artifacts

### 7.1. Review of Temporary Log Files

*   **Criticality:** **High** (Potential for hidden bugs and incomplete features)
*   **Issue:** The root directory contains numerous development logs (`*.md` files) that document the implementation process. An analysis of these files was performed to uncover any documented, but incomplete, work.
*   **Findings:** The logs indicate a high standard of completion, but revealed three key areas that require follow-up:

    1.  **Deferred Runtime Testing for CLI Modularization:**
        *   **Source:** `T041-COMPLETED.md`, `CLI-MODULARIZATION-COMPLETE.md`.
        *   **Details:** The logs explicitly state that while the modularized CLI files passed static syntax and structure checks, full **runtime testing was deferred** because project dependencies were not installed at the time.
        *   **Impact:** There is a risk of runtime errors (e.g., incorrect function calls, logic errors, import issues) that were not caught. The successful refactoring of 42% of the main CLI file has not been fully validated with end-to-end tests.
        *   **Suggestion:** Create a dedicated testing task to run a full regression test suite on all CLI commands, especially the `mcp` and `gemini` subcommands that were moved. This should include testing basic execution, options, error handling, and verbose mode.

    2.  **Incomplete CLI Modularization:**
        *   **Source:** `CLI-MODULARIZATION-COMPLETE.md`.
        *   **Details:** The "Next Steps" section of the modularization summary clearly states that the refactoring was only partial. The `project`, `fleet`, `agent`, and `office` command groups were left in the main `cli.py` file.
        *   **Impact:** The `cli.py` file is still large (910 lines), and the goal of full modularity has not been achieved. This leaves technical debt and an inconsistent code structure.
        *   **Suggestion:** Continue the modularization effort as outlined in the log file. Create new files (`project_commands.py`, `fleet_commands.py`, etc.) in the `src/mcp_manager/cli/` directory and move the remaining command groups out of `cli.py`.

    3.  **Verification Required for Hardcoded Path Removal:**
        *   **Source:** `IMPROVEMENT-PLAN-STATUS.md`.
        *   **Details:** The status report claims that Issue 2.1 ("Remove Hardcoded Paths") is complete, citing the creation of an `AuditConfiguration` model. However, this is a self-reported status.
        *   **Impact:** Without verification, it's possible the `core.py` file still contains hardcoded paths, or that the new configuration model is not being used correctly.
        *   **Suggestion:** Create a task to specifically audit the `audit_configurations` function in `src/mcp_manager/core.py`. The audit should confirm that the function correctly uses the `AuditConfiguration` model and that no hardcoded directory paths (e.g., `~/Apps`, `~/projects`) remain in the implementation.

---

## 8. Constitutional and Spec-Kit Alignment Review

### 8.1. Constitutional Adherence Analysis

*   **Criticality:** **High** (Core principles of the project are not being met by the current configuration).
*   **Summary:** A review of `constitution.md` against the project's current configuration (`pyproject.toml`) and structure reveals several violations that need to be addressed to maintain project integrity.

*   **Findings:**

    1.  **VIOLATION: Principle VII (Cross-Platform Compatibility)**
        *   **Constitution Mandate:** The system **MUST** operate on **Python 3.13+**.
        *   **Actual Configuration (`pyproject.toml`):** The project is configured for `requires-python = ">=3.11"`.
        *   **Impact:** This is a critical conflict. The `uv` package manager could select a Python interpreter (e.g., 3.11, 3.12) that does not meet the constitution's requirement, leading to an environment that is not compliant with the fleet standard.

    2.  **VIOLATION: Principle I (UV-First Development) - Weak Enforcement**
        *   **Constitution Mandate:** All Python operations **MUST** use `uv` to ensure a consistent environment.
        *   **Actual Configuration (`pyproject.toml`):** The configuration lacks a `[tool.uv]` section to explicitly pin the Python interpreter. This relates to your concern about not using the specified system Python.
        *   **Impact:** `uv` will attempt to auto-discover a compatible Python version based on the loose `>=3.11` requirement. It might not select the intended system-wide Python 3.13, undermining the principle of a consistent, fleet-wide environment.

    3.  **VIOLATION: Principle VIII (Repository Organization)**
        *   **Constitution Mandate:** Files **MUST** be organized in structured directories. Root folder clutter is **prohibited**.
        *   **Actual State:** The root directory contains numerous temporary log and status files.
        *   **Impact:** This violates the explicit rules of the constitution and makes the repository difficult to navigate. (This finding is also detailed in section 6.1).

### 8.2. Recommendations for `spec-kit` Workflow

*   **Summary:** The identified constitutional violations are ideal inputs for the `spec-kit` workflow to generate precise specifications and tasks for remediation.

*   **Actionable Steps:**

    1.  **Run `/constitution` to Review and Amend:**
        *   **Prompt:** Use the `/constitution` command to re-evaluate the project's principles, focusing on the Python version conflict.
        *   **Decision Point:** The team/user must decide whether to:
            *   **Option A (Enforce Constitution):** Keep the Python 3.13+ mandate and update the project configuration to match.
            *   **Option B (Amend Constitution):** Downgrade the constitutional requirement to `>=3.11` if Python 3.13 is not a strict necessity.
        *   **Example Prompt for `/constitution`:** `/constitution Review Principle VII. The project currently requires Python >=3.11 but the constitution mandates 3.13+. Decide whether to enforce 3.13+ in the project or amend the constitution to >=3.11.`

    2.  **Run `/specify` to Create Remediation Tasks:**
        *   **Prompt:** Use the `/specify` command with the findings from this analysis to generate tasks for fixing the violations.
        *   **Example Prompts for `/specify`:**
            *   `/specify Align the project's Python version with the constitution. This involves updating pyproject.toml to require Python 3.13+ and configuring uv to use the correct Python interpreter.`
            *   `/specify Enforce constitutional repository organization by creating a plan to review, consolidate, and delete the temporary log files from the root directory.`
            *   `/specify Complete the CLI modularization as outlined in the development artifacts. Extract the remaining 'project', 'fleet', 'agent', and 'office' command groups from cli.py into their own modules.`

    3.  **Technical Solution for Python Version Enforcement:**
        *   To enforce the use of a specific Python version (e.g., 3.13) and align with the constitution, the following changes should be made in `pyproject.toml`:

        **Update the Python requirement:**
        ```toml
        [project]
        # ...
        requires-python = ">=3.13"
        ```

        **Add a `tool.uv` section to pin the interpreter:**
        ```toml
        [tool.uv]
        python = "python3.13" # Or the specific path to the interpreter
        ```
        *   **Benefit:** This configuration explicitly tells `uv` which Python interpreter to use for creating the virtual environment, guaranteeing that the project runs on the constitutionally mandated version and addressing the concern about using the correct system Python.