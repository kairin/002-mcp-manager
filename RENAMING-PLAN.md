# Feature Folder Renaming Plan

**Date**: 2025-10-15
**Purpose**: Rename feature folders to match implementation order (PHASE 1 → PHASE 2 → PHASE 3)

## Proposed Renaming Scheme

### Current Structure (Chronological Order)
```
specs/
├── 001-system-python-enforcement/     ← Created 2025-10-15 (implement 2nd)
├── 002-referencing-to-this/           ← Created earlier (implement 3rd)
├── 003-system-python-enforcement-ARCHIVED/  ← Duplicate, archived
└── 004-multi-cli-support/             ← Created earlier (implement 1st)
```

### Proposed Structure (Implementation Order)
```
specs/
├── 001-project-restructure/           ← PHASE 1 (was: 004-multi-cli-support)
├── 002-system-python-enforcement/     ← PHASE 2 (was: 001-system-python-enforcement)
├── 003-mcp-improvements/              ← PHASE 3 (was: 002-referencing-to-this)
└── 999-archived-duplicate/            ← ARCHIVED (was: 003-system-python-enforcement-ARCHIVED)
```

## Renaming Operations

| Current Name | New Name | Reason |
|--------------|----------|--------|
| `004-multi-cli-support` | `001-project-restructure` | Implement FIRST (restructures project) |
| `001-system-python-enforcement` | `002-system-python-enforcement` | Implement SECOND (unchanged name, new number) |
| `002-referencing-to-this` | `003-mcp-improvements` | Implement THIRD (clearer name) |
| `003-system-python-enforcement-ARCHIVED` | `999-archived-duplicate` | Archived (move to end) |

## Internal Path References to Update

### Feature 001 → 002 (System Python Enforcement)
Files that need path updates:
- `plan.md`: Line 4 references `/specs/001-system-python-enforcement/spec.md`
- `plan.md`: Line 75-83 shows directory structure `specs/001-system-python-enforcement/`
- `tasks.md`: Line 3 references `/specs/001-system-python-enforcement/`

**Find/Replace**:
- `specs/001-system-python-enforcement` → `specs/002-system-python-enforcement`
- `/001-system-python-enforcement/` → `/002-system-python-enforcement/`

### Feature 002 → 003 (MCP Improvements)
Files that need path updates:
- Check all .md files for self-references

### Feature 004 → 001 (Project Restructure)
Files that need path updates:
- Check all .md files for self-references

## Execution Steps

1. **Backup Current State**
   ```bash
   cp -r /home/kkk/Apps/002-mcp-manager/specs /home/kkk/Apps/002-mcp-manager/specs-backup-20251015
   ```

2. **Rename Folders** (in dependency order to avoid conflicts)
   ```bash
   cd /home/kkk/Apps/002-mcp-manager/specs

   # Step 1: Rename 003-ARCHIVED first (gets it out of the way)
   mv 003-system-python-enforcement-ARCHIVED 999-archived-duplicate

   # Step 2: Rename 002 to temp name (avoids conflict with 001 rename)
   mv 002-referencing-to-this 002-TEMP-mcp-improvements

   # Step 3: Rename 001 to 002 (now safe, no conflict)
   mv 001-system-python-enforcement 002-system-python-enforcement

   # Step 4: Rename 004 to 001 (now safe)
   mv 004-multi-cli-support 001-project-restructure

   # Step 5: Rename 002-TEMP to final name
   mv 002-TEMP-mcp-improvements 003-mcp-improvements
   ```

3. **Update Internal References**
   ```bash
   # Feature 002 (was 001): Update self-references
   cd /home/kkk/Apps/002-mcp-manager/specs/002-system-python-enforcement
   sed -i 's|specs/001-system-python-enforcement|specs/002-system-python-enforcement|g' plan.md
   sed -i 's|/001-system-python-enforcement/|/002-system-python-enforcement/|g' plan.md
   sed -i 's|specs/001-system-python-enforcement|specs/002-system-python-enforcement|g' tasks.md

   # Feature 003 (was 002): Update self-references (if any)
   # Feature 001 (was 004): Update self-references (if any)
   ```

4. **Update IMPLEMENTATION-ORDER.md**
   ```bash
   # Update /home/kkk/Apps/002-mcp-manager/IMPLEMENTATION-ORDER.md
   # Replace all folder references with new names
   ```

5. **Verify Structure**
   ```bash
   ls -la /home/kkk/Apps/002-mcp-manager/specs/
   # Should show:
   # 001-project-restructure/
   # 002-system-python-enforcement/
   # 003-mcp-improvements/
   # 999-archived-duplicate/
   ```

6. **Test File Integrity**
   ```bash
   # Verify all spec files still load
   ls specs/001-project-restructure/spec.md
   ls specs/002-system-python-enforcement/spec.md
   ls specs/003-mcp-improvements/spec.md
   ```

## Benefits of Renaming

✅ **Clarity**: Folder numbers match implementation order (001 = first, 002 = second, 003 = third)
✅ **Simplicity**: Easier to remember sequence
✅ **Alignment**: Folder order matches IMPLEMENTATION-ORDER.md
✅ **Organization**: Archived feature moved to 999 (out of active sequence)

## Risks & Mitigations

⚠️ **Risk**: Internal path references break
**Mitigation**: Systematic sed find/replace updates

⚠️ **Risk**: Git history becomes confusing
**Mitigation**: Keep branch names unchanged (they preserve historical context)

⚠️ **Risk**: External documentation references old names
**Mitigation**: IMPLEMENTATION-ORDER.md documents original names

## Git Branch Names (UNCHANGED)

Branch names remain unchanged to preserve history:
- `001-system-python-enforcement` (branch name)
- `002-referencing-to-this` (branch name)
- `004-multi-cli-support` (branch name)

Only **folder names** change, not branch names.

## Rollback Plan

If issues arise:
```bash
rm -rf /home/kkk/Apps/002-mcp-manager/specs
mv /home/kkk/Apps/002-mcp-manager/specs-backup-20251015 /home/kkk/Apps/002-mcp-manager/specs
```

---

**Status**: PROPOSED - Awaiting execution
**Ready**: Yes - All steps documented
**Next Action**: Execute renaming operations
