# Research: Project Health Audit Tooling

**Spec ID**: 005-we-ve-gone
**Research Date**: 2025-10-15

## 1. Research: Identifying `pip` Usage

**Task**: Determine the most effective way to find all hardcoded `pip` commands across the entire project, including scripts and documentation.

**Decision**: Use the `grep` command for a comprehensive search.

**Rationale**: `grep` is a standard, powerful, and universally available tool for text search. A recursive search from the root directory will catch all occurrences.

**Command**:
```bash
grep -r -n --color=always "pip " .
```

**Alternatives Considered**:
- Manually searching files: Too slow and error-prone.
- Using IDE search: Not easily scriptable or reproducible in a CI/CD context.

## 2. Research: Detecting Outdated Dependencies

**Task**: Identify a reliable and scriptable method to find all outdated Python and Node.js dependencies.

**Decision**: Use the built-in commands provided by the respective package managers.
- For Python: `uv pip list --outdated`
- For Node.js: `npm outdated`

**Rationale**: These commands are the authoritative source for dependency status. They are designed for this exact purpose and provide clear, parseable output.

**Commands**:
```bash
# For Python dependencies
uv pip list --outdated

# For Node.js dependencies
npm outdated
```

**Alternatives Considered**:
- Third-party dependency analysis tools: Adds unnecessary complexity and dependencies to the project when first-party tools are sufficient.

## 3. Research: Locating Misplaced Root-Level Files

**Task**: Formulate a script or command to identify and list all non-essential files in the root directory that should be moved to subfolders.

**Decision**: Use the `find` command with a `-maxdepth` of 1 to list all files in the root, and then manually filter for files that are not essential configuration.

**Rationale**: This approach is simple, effective, and requires no special tooling. It provides a clear list of candidates for relocation.

**Command**:
```bash
# List all files in the current directory
find . -maxdepth 1 -type f
```

**Alternatives Considered**:
- A complex script with a hardcoded list of allowed files: Too rigid and would require maintenance as the project evolves.
