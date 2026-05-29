# VM Usage Policy

**Effective:** 2026-05-29  
**Purpose:** Clear rules about which VMs I can use, when, and how  
**Status:** MANDATORY

---

## Quick Reference

| VM | Role | Who Can Use | When | Snapshots |
|---|---|---|---|---|
| **vm103** | Default dev | Me (without asking) | Anytime for testing | Keep 3 latest |
| **vm105+** | Temporary test | Me (only if instructed) | Only when you say "deploy" | Delete after test |

---

## VM 103: DEFAULT DEVELOPMENT MACHINE

**Location:** pve2, 192.168.2.186  
**Status:** Always available, always in working state  
**Purpose:** Primary test bed for all batch deployments

### I Can Do (Without Asking)

✅ Deploy new batch code to vm103
```bash
git checkout phase-1-batch-2
docker-compose restart
```

✅ Run tests on vm103
```bash
curl http://192.168.2.186:8000/api/v1/auth/login
```

✅ Create snapshots of vm103
```bash
qm snapshot 103 phase-1-batch-2-verified
```

✅ Update code/dependencies
```bash
cd ~/cloud-platform-upstream
git pull origin main
```

### I Must NOT Do

❌ **Destroy vm103** - It's your main dev machine
❌ **Leave vm103 broken** - Always maintain working state
❌ **Violate constraints** - QEMU only, gateway 192.168.2.250, etc.
❌ **Skip backup** - Create snapshot before major changes

### Recovery Process (If vm103 Breaks)

```bash
# List snapshots
qm listsnapshot 103

# Restore to last good snapshot
qm snapshot rollback 103 phase-1-batch-1-final

# Restart containers
docker-compose restart

# Verify
curl http://192.168.2.186:8000/api/v1/auth/login
```

### Snapshot Retention

Keep only last 3 snapshots on vm103:
- Current batch (e.g., `phase-1-batch-2-verified`)
- Previous batch (e.g., `phase-1-batch-1-final`)
- Fallback (e.g., `phase-1-batch-0-final`)

Delete older snapshots to save space.

---

## VM 105+ (Temporary): ONLY WHEN INSTRUCTED

**Location:** pve1 or pve2 (varies)  
**Status:** Created on demand, deleted after testing  
**Purpose:** Isolated test environment for specific batch verification

### When Can I Create vm105+?

**ONLY when you say:**
- "Deploy Batch 2 to a temporary VM"
- "Test Batch 3 on vm105"
- "Create vm105 for parallel testing"

**NOT when:**
- You haven't explicitly instructed it
- You said "deploy" without specifying temporary
- Default is vm103, not temporary VMs

### Standard Workflow for Temporary VMs

1. You say: "Deploy Batch 2 to temporary VM for testing"
2. I clone vm103 snapshot → vm105
3. I update code: `git checkout phase-1-batch-2`
4. I test: login, endpoints, new features
5. I create snapshot: `qm snapshot 105 phase-1-batch-2-final`
6. I report results
7. You decide: delete vm105 or keep for reference

### After Testing

**Option A: Delete Temporary VM**
```bash
# Snapshot is kept for regression testing
qm destroy 105
# Space freed, snapshot remains for reference
```

**Option B: Keep for Reference**
```bash
# Keep vm105 as-is
# Next batch: either redeploy to vm105 or create vm106
qm snapshot 105 phase-1-batch-2-final
```

---

## Current VM Inventory

### Active Machines

| VM | Node | IP | Branch | Snapshot | Status |
|---|---|---|---|---|---|
| 103 | pve2 | 192.168.2.186 | main | phase-1-batch-1-final | ✅ DEFAULT |

### Archived/Reference

| VM | Node | IP | Branch | Snapshot | Status |
|---|---|---|---|---|---|
| 151 | pve1 | 192.168.2.196 | main | phase-1-batch1-main-branch-working | ✅ Batch 1 test proof |

---

## Rules Enforcement

### Violation: Attempting to Deploy Without Instruction

**Scenario:** You haven't said to deploy, but I attempt to create vm105.

**Result:** I STOP and ask for confirmation.

**Example:**
```
You: "What's next?"
Me: "Ready to deploy Batch 2 to temporary VM (vm105)?"
You: "No, deploy to vm103 instead"
Me: "Understood, using vm103 (default dev). Cloning..."
```

### Violation: Destroying vm103

**Scenario:** I accidentally delete vm103.

**Result:** CRITICAL FAILURE - I immediately stop and report.

**Prevention:** All destruction commands require explicit instruction from you.

---

## Snapshot Naming Convention

### vm103 (Default Dev) Snapshots

```
phase-1-batch-<N>-verified
```

Examples:
- `phase-1-batch-1-verified` - Batch 1 tested on vm103
- `phase-1-batch-2-verified` - Batch 2 tested on vm103
- `phase-1-batch-3-verified` - Batch 3 tested on vm103

Keep last 3, delete older.

### Temporary VM Snapshots

```
phase-1-batch-<N>-final
```

Examples:
- `phase-1-batch-2-final` (vm105) - Batch 2 parallel test
- `phase-1-batch-3-final` (vm106) - Batch 3 parallel test

Delete VM after test, keep snapshot for 2 weeks for regression testing.

---

## Decision Tree

```
User says "Deploy Batch 2":
├─ Do you say "to temporary VM"?
│  ├─ YES → Create vm105, clone from vm103, deploy, test, snapshot, keep for reference
│  └─ NO → Use vm103 (default), deploy, test, snapshot, clean up old snapshots
│
User says "What's the status?":
├─ I check vm103 (main dev machine)
├─ I report: which branch, which snapshot, container health
└─ vm103 always ready for next batch

User says "Delete vm105":
├─ I delete vm105
├─ I keep snapshot phase-1-batch-2-final for reference
└─ Freed space available
```

---

## Implementation Checklist

Before any deployment:
- [ ] Is this a temporary VM request or default vm103?
- [ ] Do I have explicit instruction for temporary deployment?
- [ ] If temporary: which VM (vm105, vm106, etc.)?
- [ ] Have I checked vm103 is in good state?
- [ ] Will I create a snapshot after testing?
- [ ] Will I clean up old snapshots to save space?

---

## Related Documents

- CRITICAL_CONSTRAINTS.md (Constraint #7)
- SNAPSHOT_RECOVERY_WORKFLOW.md
- BATCH2_DEPLOYMENT_PLAN.md
