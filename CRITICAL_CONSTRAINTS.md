# ⚠️ CRITICAL DEPLOYMENT CONSTRAINTS

**Status:** MANDATORY - NON-NEGOTIABLE  
**Last Updated:** 2026-05-28  
**Severity:** CRITICAL - VIOLATION CAUSES DEPLOYMENT FAILURE

---

## 🚫 ABSOLUTE CONSTRAINTS

### 1. VM DEPLOYMENT ONLY - NO LXC CONTAINERS

**CONSTRAINT:** All deployments MUST use QEMU VMs, NOT LXC containers.

**REASON:** LXC containers have Docker compatibility issues that cause deployment failures.

**REFERENCE:** Project inception decision made before vm103 deployment.

**VIOLATION CONSEQUENCE:** Immediate deployment failure, wasted resources, time waste.

**CHECK BEFORE PROCEEDING:**
```
[ ] Is this a QEMU VM deployment?
[ ] NOT an LXC container?
[ ] Confirmed via Proxmox node specification?
```

**EXAMPLE - CORRECT:**
```python
proxmox_mcp_pve1_create_vm(
    node="pve1",
    vmid=151,
    name="cloud-platform-batch1-test"
)
# ✅ CORRECT - QEMU VM
```

**EXAMPLE - WRONG:**
```python
proxmox_mcp_pve1_create_lxc(
    node="pve1",
    vmid=150,
    ostemplate="local:vztmpl/ubuntu..."
)
# ❌ WRONG - LXC CONTAINER - VIOLATES CONSTRAINT
```

---

### 2. VM SPECIFICATIONS - MATCH vm103 BASELINE

**CONSTRAINT:** All VMs must have these minimum specs:

| Property | Value | Reason |
|----------|-------|--------|
| **OS** | Ubuntu 24.04 LTS | Tested baseline |
| **vCPU** | 4 cores | Sufficient for Docker build |
| **RAM** | 4GB (4096 MB) | Required for 8 containers |
| **Disk** | 20GB | Required for images + data |
| **Type** | QEMU VM | Docker compatibility |

**CHECK BEFORE PROCEEDING:**
```
[ ] VM is QEMU type (not LXC)
[ ] OS is Ubuntu 24.04 LTS
[ ] vCPU >= 4
[ ] RAM >= 4GB
[ ] Disk >= 20GB
[ ] Network bridge configured (vmbr0)
```

---

### 3. CODE DEPLOYMENT MUST USE FORK BRANCH

**CONSTRAINT:** All deployments deploy from `cloudforproxmox-new` fork, not upstream.

**REFERENCE:** TWO_REPO_WORKFLOW.md

**AVAILABLE BRANCHES:** 
- ✅ `phase-1-batch-1` (16 commits, all fixes merged in 2026-05-28)
- ✅ `main` (master branch with all fixes, recommended)

**CHECK BEFORE PROCEEDING:**
```
[ ] Cloning from: https://github.com/peppekerstens/cloudforproxmox-new.git
[ ] Branch: phase-1-batch-1
[ ] NOT cloning from cloudforproxmox-upstream
[ ] All code fixes included (timezone imports, docker-compose paths, etc.)
```

---

### 4. DOCKER DEPLOYMENT REQUIRES ALL FIXES

**CONSTRAINT:** No deployment without all critical code fixes applied.

**REQUIRED FIXES:**
- ✅ `timezone` import in auth.py
- ✅ `timezone` import in security.py
- ✅ docker-compose volume mount paths (`../backend:/app`, not `...`)
- ✅ uvicorn `--reload` flag removed
- ✅ Credentials in `.env`, not documented

**CHECK BEFORE PROCEEDING:**
```
[ ] All timezone imports present
[ ] Volume mounts use ../backend:/app format
[ ] No --reload in uvicorn command
[ ] .env configured from .env.example
[ ] No hardcoded credentials in code/docs
```

---

### 5. NETWORK CONFIGURATION - UNIQUE IP PER VM

**CONSTRAINT:** Each VM must have unique IP on network with CORRECT gateway.

**REFERENCE:** vm103 uses 192.168.2.186

**DEPLOYMENT ON pve1 MUST USE:** 192.168.2.187 (or next available)

**CRITICAL:** Gateway MUST be 192.168.2.250 (NOT 192.168.2.1)

**CHECK BEFORE PROCEEDING:**
```
[ ] IP address is unique (not 192.168.2.186)
[ ] IP is on 192.168.2.0/24 subnet
[ ] Gateway is 192.168.2.250 (NOT .1)
[ ] Cloud-init ipconfig: ip=192.168.2.187/24,gw=192.168.2.250
[ ] No IP conflicts with existing VMs
```

---

## 🔴 DEPLOYMENT DECISION CHECKLIST

**MUST complete this before ANY VM creation:**

```
DEPLOYMENT CHECKLIST - CRITICAL CONSTRAINTS
============================================

VM TYPE:
  [ ] QEMU VM selected (NOT LXC)
  [ ] Node specified (pve1 or pve2)
  [ ] VMID chosen and unique

SPECIFICATIONS:
  [ ] OS: Ubuntu 24.04 LTS
  [ ] vCPU: 4 cores minimum
  [ ] RAM: 4GB minimum
  [ ] Disk: 20GB minimum
  [ ] Network: bridge vmbr0

CODE DEPLOYMENT:
  [ ] Source: cloudforproxmox-new fork (not upstream)
  [ ] Branch: phase-1-batch-1
  [ ] All fixes applied (timezone, paths, reload, creds)
  [ ] .env.example copied to .env
  [ ] Admin user seeding ready

NETWORK:
  [ ] IP address unique (not 192.168.2.186)
  [ ] Subnet: 192.168.2.0/24
  [ ] Gateway: 192.168.2.1
  [ ] No conflicts verified

APPROVAL:
  [ ] Constraints reviewed by developer
  [ ] Decision logged with timestamp
  [ ] Proceeding with confidence

DATE: __________
APPROVER: __________
VM ID: __________
NOTES: __________
```

---

## ⚠️ INCIDENT LOG

### Incident 2026-05-28 22:05 UTC

**What happened:** Created LXC container (vmid 150) instead of QEMU VM

**Root cause:** Did not review explicit constraint before starting deployment

**Consequence:** Wasted time, violated requirements, deployment not executable

**Fix:** Deleted LXC, created QEMU VM

**Prevention:** This document created to prevent recurrence

---

### Incident 2026-05-28 23:14 UTC

**What happened:** VM 151 created with gateway 192.168.2.1 (incorrect)

**Root cause:** Assumed standard gateway, didn't verify network topology

**Consequence:** VM unreachable, no network connectivity

**Fix:** Deleted VM, recreated with gateway 192.168.2.250, agent=1 enabled

**Prevention:** Gateway value saved in .env for reference; updated CRITICAL_CONSTRAINTS to specify 192.168.2.250 explicitly

---

---

### 6. DEPLOYMENT METHOD - SNAPSHOT-BASED RECOVERY (New as of 2026-05-29)

**CONSTRAINT:** Batch deployments do NOT do full OS installs. Use snapshot cloning + code updates only.

**REASON:** Complete redeploys are time-consuming and error-prone. Snapshot recovery is ~5 min vs 30+ min.

**PROCESS:**
1. Clone working baseline snapshot (e.g., vm103 phase-1-batch-1-final)
2. Update code via git checkout
3. Run DB migrations if needed
4. Test

**DO NOT:**
- ❌ Create fresh VMs from ISO
- ❌ Install Ubuntu, Docker, dependencies manually
- ❌ Attempt full deployment automation

**EXCEPTION:** Only perform full VM creation/setup if explicitly instructed by user for a specific reason.

**REFERENCE:** BATCH2_DEPLOYMENT_PLAN.md (updated 2026-05-29)

---

### 7. VM USAGE POLICY - DEFAULT vs TEMPORARY (New as of 2026-05-29)

**VM 103 (pve2, 192.168.2.186) - DEFAULT DEV MACHINE**

**CONSTRAINT:** vm103 is your default development machine. I can use it for testing, code updates, and quick development work WITHOUT asking.

**Rules:**
- ✅ I may deploy new code to vm103 (update branch, test)
- ✅ I may create snapshots of vm103 for reference
- ✅ I may run quick tests on vm103
- ❌ I must NOT destroy vm103
- ❌ I must NOT break vm103 permanently
- ✅ If vm103 breaks, I restore from latest snapshot

**When vm103 is used:**
1. Code is deployed to vm103 to test new batch
2. If test passes → create snapshot (e.g., `phase-1-batch-2-verified`)
3. If test fails → rollback to previous snapshot
4. Keep vm103 in working state for next batch

**Snapshot retention on vm103:** Keep last 3 (current + previous 2 batches), delete older.

---

**VM 105 (temporary, vm151 was temp for Batch 1) - TEMPORARY TEST MACHINE**

**CONSTRAINT:** Temporary VMs are ONLY created when you explicitly instruct me to deploy a specific batch for testing on a separate node.

**Rules:**
- ❌ I do NOT create vm105+ without explicit instruction
- ❌ I do NOT deploy to vm105+ unless you say "deploy to vm105"
- ✅ Once created, I follow snapshot-based workflow
- ✅ Once testing complete, I can keep snapshot but can delete VM
- ❌ Temporary VMs are not for ongoing development

**When temporary VMs are used:**
1. You say: "Deploy Batch 2 to a temporary VM for testing"
2. I clone baseline → vm105
3. Update code, test, verify
4. Create snapshot `phase-1-batch-2-final` for reference
5. Optionally delete vm105 to free resources
6. Keep snapshot for regression testing

**Current temporary VMs:**
- vm151 (pve1, 192.168.2.196) - Phase 1 Batch 1 test (snapshot: `phase-1-batch1-main-branch-working`)

---

**SUMMARY TABLE**

| VM | Node | IP | Status | Usage | Snapshots |
|---|---|---|---|---|---|
| vm103 | pve2 | 192.168.2.186 | DEFAULT | Dev/test all batches | Keep 3 latest |
| vm151 | pve1 | 192.168.2.196 | ARCHIVED | Batch 1 test (kept for reference) | 1 (final) |
| vm105+ | varies | varies | TEMPORARY | Only when you say "deploy" | Delete after test or keep 1 |

**REFERENCE:** VM_USAGE_POLICY.md (new document)

---

## 🛑 IF VIOLATING CONSTRAINT

If constraints are about to be violated:
1. **STOP immediately**
2. **Do NOT proceed**
3. **Review this document**
4. **Verify constraints with user**
5. **Log the incident**
6. **Correct course before proceeding**

---

## 📋 RELATED DOCUMENTS

- PHASE1_BATCH1_COMPLETE.md - Current deployment status
- TWO_REPO_WORKFLOW.md - Deployment workflow
- BATCH1_FIXES.md - Code fixes required
- CREDENTIALS_MANAGEMENT.md - Security requirements
- REPLAY_STATUS.md - Execution tracking

---

## ✅ SIGN OFF

This document is:
- ✅ Non-negotiable
- ✅ Must be checked before EVERY deployment decision
- ✅ Required approval before proceeding
- ✅ Incident logged if violated

**Violation = Deployment failure = Wasted time = STOP AND REVIEW**
