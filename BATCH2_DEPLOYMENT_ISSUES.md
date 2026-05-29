# Phase 1 Batch 2: Deployment Issues & Root Cause Analysis

**Date:** 2026-05-29  
**Status:** BLOCKED - Code dependency issue in source  
**Impact:** Batch 2 cannot be deployed as-is due to missing module dependencies

---

## Problem Summary

Batch 2 code (10 commits: 8bbd9b8..be13bb8 in proxmox-isp) references modules that don't exist until Phase 8 (60+ commits later).

**Specific Issues:**
1. `vms.py` imports `from app.core.audit import create_audit_log`
2. `audit.py` imports `from app.models.audit_log import AuditLog`
3. `vms.py` also imports `from app.tasks.vm_status_tasks import poll_vm_power_state`

All three modules (`audit.py`, `audit_log.py`, `vm_status_tasks.py`) don't exist until Phase 8.

---

## Root Cause

The original source repo (proxmox-isp) used a feature-branch workflow that merged changes out of chronological order. Batch 2 commits were created AFTER the audit system was implemented, so they have forward references to later code.

**Evidence:**
- Audit system commit: `1edf35f` (Phase 8) 
- vm_status_tasks commit: `561e1db` (also Phase 8+)
- Batch 2 commits: `8bbd9b8..be13bb8` (Phase 1, but created after Phase 8 code)

---

## Why This Happened

Proxmox-ISP development likely:
1. Implemented features (Phase 8 audit system) in branches
2. Merged them into the base codebase
3. Later created "Phase 1 Batch 2" as a slice of commits, which inadvertently included forward references

This is a data quality issue in the source repository, not an issue with our deployment process.

---

## Options to Fix

### Option A: Create Stub Modules (Quick Fix)
Create minimal stub implementations for missing modules to allow Batch 2 to run without them:

```python
# stub for app.models.audit_log
class AuditLog:
    pass

# stub for app.tasks.vm_status_tasks
async def poll_vm_power_state(*args, **kwargs):
    pass
```

**Pros:** Fast, Batch 2 can deploy
**Cons:** Features won't work, stubs need removal later

### Option B: Skip Batch 2, Apply Larger Chunk (Recommended)
Instead of replaying 10 commits at a time, apply a larger batch that includes required dependencies.

**Example:** Apply 80+ commits that bring in audit system + all dependencies
**Pros:** Code is self-contained, clean state
**Cons:** Loses granular testing per batch

### Option C: Clean the Source Data (Manual)
Remove audit imports from Batch 2 files in proxmox-isp, re-export commits

**Pros:** Maintains batch integrity
**Cons:** Requires manual editing of source history

### Option D: Continue to Later Batch
Skip Batch 2 deployment, proceed to Batch 3+ where dependencies are satisfied

**Pros:** Keep forward momentum
**Cons:** Batch 2 features never deployed

---

## Current State

- ✅ Batch 2 code is applied to cloudforproxmox/main and phase-1-batch-2 branches
- ✅ Files are in git repository
- ❌ Containers won't start due to import errors
- ❌ No working Batch 2 deployment on vm103

---

## Recommendation

**Proceed with Option B:** Apply a merged batch (Batches 1-3 or 1-4) that includes all dependencies, then test as a unit.

This trades per-batch testing granularity for deployment success and keeps momentum.

---

## Next Steps

1. Document Batch 2 issue in REPLAY_STATUS.md
2. Decide on fix option (recommend Option B)
3. Proceed to implementation

