# Quickstart: Running the Project Health Audit

**Spec ID**: 005-we-ve-gone

This guide provides the steps to perform the project health and standardization audit.

## 1. Audit for `pip` Usage

To ensure the project is exclusively using `uv`, run the following command from the root directory to search for any remaining `pip` commands.

```bash
grep -r -n --color=always "pip " .
```

Any findings should be replaced with the equivalent `uv` command.

## 2. Check for Outdated Dependencies

Run the following commands to check for outdated Python and Node.js packages.

```bash
# Check Python dependencies
uv pip list --outdated

# Check Node.js dependencies
npm outdated
```

Review the output and update dependencies as needed, ensuring that all tests pass after updating.

## 3. Audit Root Directory Files

Run this command to list all files in the root directory. Review the list and identify any non-essential files that should be moved to a subdirectory like `docs/` or `specs/`.

```bash
find . -maxdepth 1 -type f
```
