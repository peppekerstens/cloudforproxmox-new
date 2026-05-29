# VM Usage Policy

**Effective:** 2026-05-29  
**Purpose:** Clear rules about which VMs I can use, when, and how  
**Status:** MANDATORY

---

## Quick Reference

| VM | Role | Who Can Use | When | Snapshots |
|---|---|---|---|---|
| **vm103** | Default dev | Me (without asking) | Anytime for testing | Keep 3 latest |
| **vm151** | Temporary test | Me (only if instructed) | Only when you say "test on vm151" | 1 per batch |

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

## VM 151: TEMPORARY TEST MACHINE - ONLY WHEN INSTRUCTED

**Location:** pve1, 192.168.2.196  
**Status:** Available for testing when you instruct  
**Purpose:** Isolated test environment on separate cluster for parallel verification

### When Can I Use vm151?

**ONLY when you say:**
- "Deploy Batch 2 to temporary VM"
- "Test Batch 3 on vm151"
- "Verify on vm151"
- Any instruction that explicitly mentions testing on a separate node

**NOT when:**
- You haven't explicitly instructed it
- You said "deploy" without specifying temporary
- Default assumption is vm103, not vm151

### Standard Workflow for vm151

1. You say: "Deploy Batch 2 to temporary VM" or "Test on vm151"
2. I clone vm103 snapshot → vm151 (on pve1)
3. I update code: `git checkout phase-1-batch-2`
4. I test: login, endpoints, new features
5. I create snapshot: `qm snapshot 151 phase-1-batch-2-final`
6. I report results
7. vm151 stays available for next test

### After Testing

**Option A: Keep vm151 for Next Batch**
```bash
# Keep running with current batch code
# Next test: clone again or update code
qm status 151  # Verify still running
```

**Option B: Reset vm151 to Baseline**
```bash
# Restore to vm103 snapshot for clean state
qm snapshot rollback 151 phase-1-batch-1-final
```

---

## Current VM Inventory

### Active Machines

| VM | Node | IP | Branch | Snapshot | Status |
|---|---|---|---|---|---|
| 103 | pve2 | 192.168.2.186 | main | phase-1-batch-1-final | ✅ DEFAULT dev |
| 151 | pve1 | 192.168.2.196 | main | phase-1-batch1-main-branch-working | ✅ TEMPORARY test |

---

## Rules Enforcement

### Violation: Attempting to Deploy Without Instruction

**Scenario:** You haven't said to test on temporary VM, but I deploy to vm151 without asking.

**Result:** I STOP and ask for confirmation.

**Example:**
```
You: "What's next?"
Me: "Ready to deploy Batch 2 to vm103 (default)?"
You: "Test on vm151 instead"
Me: "Understood, cloning vm103 → vm151..."
```

### Violation: Destroying vm103

**Scenario:** I accidentally delete vm103.

**Result:** CRITICAL FAILURE - I immediately stop and report.

**Prevention:** All destruction commands require explicit instruction from you.

### Violation: Using vm151 Without Instruction

**Scenario:** I deploy to vm151 without you explicitly saying "test on vm151".

**Result:** I STOP and ask for clarification.

**Rule:** Default is always vm103. vm151 ONLY on explicit instruction.

---

## Snapshot Naming Convention

### vm103 (Default Dev) Snapshots

```
phase-<PHASE>-batch-<N>-verified
```

Examples:
- `phase-1-batch-1-verified` - Batch 1 tested on vm103
- `phase-1-batch-2-verified` - Batch 2 tested on vm103
- `phase-1-batch-3-verified` - Batch 3 tested on vm103

Policy: Keep last 3, delete older.

### vm151 (Temporary Test) Snapshots

```
phase-<PHASE>-batch-<N>-final
```

Examples:
- `phase-1-batch-2-final` (vm151) - Batch 2 parallel test
- `phase-1-batch-3-final` (vm151) - Batch 3 parallel test (replaces previous)
- `phase-2-batch-1-final` (vm151) - Phase 2 Batch 1 test

Policy: Keep 1 current snapshot per batch, overwrite with next batch test.

---

## Decision Tree

```
User says "Deploy Batch 2":
├─ Default assumption: Use vm103
│  └─ Update code, test, snapshot, keep working state
│
User says "Test on vm151":
├─ Clone vm103 → vm151
├─ Update code, test, snapshot phase-1-batch-2-final
└─ Report results, vm151 ready for next test
│
User says "What's the status?":
├─ Check vm103 (main dev machine)
├─ Report: which branch, which snapshot, container health
└─ vm103 always ready for next batch

User says "Reset vm151":
├─ Restore vm151 to baseline (phase-1-batch-1-final)
└─ vm151 ready for next test
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
