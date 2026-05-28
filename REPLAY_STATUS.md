# REPLAY_STATUS.md

## Execution Status Tracking
**Project:** Cloud for ProxMox Replay  
**Baseline VM:** vm103 (pve2)  
**Target:** Commit 040259b (HTTPS/Backend-Frontend Split Failure Point)  
**Execution Start Date:** 2026-05-28

---

## Repository Clarification (CRITICAL)

**Three repos involved — DO NOT CONFUSE:**

| Repo | Location | Purpose | Status | Touch? |
|------|----------|---------|--------|--------|
| **cloudforproxmox-old** | https://github.com/peppekerstens/cloudforproxmox-old | Reference (failed state at 040259b) | Read-only archive | 🚫 **NO** |
| **proxmox-isp** | ~/github/proxmox-isp | Local working copy (replay source data) | Active checkout | ✅ Git operations only |
| **cloudforproxmox-new** | https://github.com/peppekerstens/cloudforproxmox-new | THIS REPO (replay plan & status docs) | Active deployment tracking | ✅ **YES** |

**What each is used for:**
- `cloudforproxmox-old`: Source of commit hashes, diffs, and failure analysis. Extracted for REPLAY_PLAN files.
- `proxmox-isp`: Local git checkout used to replay commits on vm103. Deploy from here.
- `cloudforproxmox-new`: Tracks replay progress, stores REPLAY_PLAN docs, documents vm103 state.

---

---

## Baseline Environment (Actual)

| Item | Specification | Actual | Status |
|------|---------------|--------|--------|
| **OS** | Ubuntu 22.04 LTS | Ubuntu 24.04.4 LTS | ⚠️ Newer (tested OK) |
| **Kernel** | 6.8 | 6.8 | ✅ Match |
| **vCPU** | 4 | 2 | ⚠️ Half (will monitor) |
| **RAM** | 4GB | 4GB (4096MB) | ✅ Match |
| **Disk** | 20GB | 20GB | ✅ Match |
| **Docker** | 26.x | 29.1.3 | ✅ Compatible (newer) |
| **docker-compose** | 1.29.2 | 1.29.2 | ✅ Match |

### Baseline Snapshot
- **Name:** snapshot-initial
- **Created:** 2026-05-28
- **Description:** Baseline: Ubuntu 24.04, Docker 29.1.3, docker-compose 1.29.2
- **State:** Clean (Docker/compose installed, no containers running)

---

## Replay Progress

### Phase 0-1: Setup → VM/LXC Foundation
**Status:** Pending  
**Target Commits:** 179  
**Target End Hash:** TBD  

| Batch | Commits | Status | Last Snapshot | Notes |
|-------|---------|--------|----------------|-------|
| 1 | 7c1ae38...{+10} | — | — | — |

### Phase 2-3: Network → Onboarding
**Status:** Pending  
**Target Commits:** 22  

### Phase 4-5: Multi-Tenant → RBAC
**Status:** Pending  
**Target Commits:** 51  

### Phase 8-9: Audit → Billing
**Status:** Pending  
**Target Commits:** 40  

### Phase 12: HTTPS (Expected Failure)
**Status:** Pending  
**Target Commits:** 11  
**Expected Failure Point:** 040259b

---

## Key Findings / Deviations

1. **Ubuntu 24.04 vs. 22.04:** Newer version, different Python (3.12 vs. 3.10), but Docker & docker-compose compatible
2. **vCPU 2 vs. 4:** May impact performance; will monitor for timeouts/slowdowns
3. **Docker 29.1.3:** Newer than spec (26.x), should be backward compatible
4. **docker-compose v1.29.2:** Installed via pip (apt version had distutils dependency issue with Python 3.12)

---

## Snapshot Rotation Log

| Slot | Snapshot Name | Commit | Date | Status |
|------|---------------|--------|------|--------|
| 1 | snapshot-initial | baseline | 2026-05-28 | Active |
| 2 | — | — | — | Empty |
| 3 | — | — | — | Empty |

---

## Test Results Summary

(Updated after each phase)

---

## Blockers / Issues

(None yet)

---

## Next Steps

1. Execute Phase 0-1 replay (commit 7c1ae38 onwards)
2. Deploy, test, snapshot per-batch
3. Monitor for vCPU/Python 3.12 compatibility issues
4. Document actual state at Phase 12 (040259b) failure point
