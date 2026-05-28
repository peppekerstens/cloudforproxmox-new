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

**CURRENT BRANCH:** `phase-1-batch-1` (16 commits applied, all fixes included)

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
