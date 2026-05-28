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
| **vCPU** | 4 | 4 | ✅ Match (upgraded from 2) |
| **RAM** | 4GB | 4GB (4096MB) | ✅ Match |
| **Disk** | 20GB | 20GB | ✅ Match |
| **Docker** | 26.x | 29.1.3 | ✅ Compatible (newer) |
| **docker-compose** | 1.29.2 | 1.29.2 | ✅ Match |

### Baseline Snapshots (Phase 0: Upstream Deployment)
- **snapshot-upstream-working**
  - Created: 2026-05-28 21:04:59
  - Description: Upstream cloud-platform deployed, all 8 containers healthy
  - State: Upstream code running, no login tested

- **snapshot-upstream-final-cors-fixed** ⭐ **CURRENT BASELINE**
  - Created: 2026-05-28 21:19:14
  - Description: Upstream cloud-platform working: login verified, CORS fixed, all containers healthy
  - State: ✅ Ready for Phase 1 replay
  - Prerequisites: VITE_API_URL, CORS_ORIGINS configured
  - Verified: Login successful, dashboard accessible

---

## Replay Progress

### Phase 0: Upstream Deployment ✅ **COMPLETE**
**Status:** ✅ COMPLETE  
**Duration:** ~1 hour  
**Issues Resolved:** 3 (API URL, CORS, docker-compose bug)

**Deliverables:**
- ✅ vm103 upgraded to 4 vCPU
- ✅ Upstream cloud-platform deployed
- ✅ All 8 containers healthy (postgres, redis, rabbitmq, api, frontend, celery-worker, celery-beat, flower)
- ✅ API responding (`/api/v1/health/detailed` → healthy)
- ✅ Frontend accessible (http://192.168.2.186:3000)
- ✅ Login verified (admin@example.org → dashboard)
- ✅ Configuration documented: VITE_API_URL, CORS_ORIGINS
- ✅ Snapshot: `snapshot-upstream-final-cors-fixed` (baseline for Phase 1)
- ✅ Documentation: UPSTREAM_DEPLOYMENT_PREREQUISITES.md, FORK_STRATEGY.md

**Issues & Solutions:**
1. **API URL:** VITE_API_URL hardcoded to localhost → set env var to 192.168.2.186:8000
2. **CORS:** Frontend origin 192.168.2.186:3000 not in allowlist → added to CORS_ORIGINS env
3. **docker-compose:** v1.29.2 KeyError: 'ContainerConfig' bug → workaround: `docker system prune -a --volumes -f`

**Pre-Phase 1 Gate:** ✅ PASSED

---

### Phase 0-1: Setup → VM/LXC Foundation
**Status:** Pending  
**Target Commits:** 179  
**Target End Hash:** TBD  
**Gate:** Fork upstream, update REPLAY_PLAN with branch/tag naming

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

## Execution Strategy (REVISED)

**Phase 1: Install & validate upstream base**
- Rebuild vm103 clean (rollback to snapshot-initial)
- Clone https://github.com/proxmox-cloudportal/cloud-platform
- Deploy upstream, verify all tests pass
- Create snapshot: snapshot-upstream-working
- Commit working upstream to cloudforproxmox-new

**Phase 2: Replay commits on upstream base**
- Deploy commits 7c1ae38 → 2ca9e1b (fork + modifications)
- Git commit structure: Per-batch (Option C)
- Each batch of 5-10 commits = 1 commit in cloudforproxmox-new
- Total: ~38-42 commits by 2ca9e1b

**Endpoint:** Build to commit 2ca9e1b (working state before HTTPS failure)

**Documents in repo:** ALL (REPLAY_PLAN, OPENCODE_RULES, INFRASTRUCTURE_SAFEGUARDS, etc.) - critical for tracking

## Execution Progress

### Upstream Base: Working ✅
**Status:** Deployed & Healthy  
**Snapshot:** snapshot-upstream-working  
**All 8 Containers:** Running & Healthy
- postgres (timescaledb) - healthy
- redis - healthy
- rabbitmq - healthy
- api (FastAPI) - running
- frontend (React) - running
- celery-worker - running
- celery-beat - running
- flower - running

**VM Config:** 4 vCPU, 4GB RAM, 20GB disk (upgraded from 2 vCPU)

### Phase 0-1: Setup → VM/LXC Foundation (Fork Commits)
**Status:** Pending  
**Target:** 179 commits, end at be13bb8  
**Batches planned:** ~18-20
**Starting from:** 7c1ae38 (Phase 0: fork upstream, strip cruft)

### Phase 2-3: Network → Onboarding
**Status:** Pending  
**Target:** 22 commits

### Phase 4-5: Multi-Tenant → RBAC
**Status:** Pending  
**Target:** 51 commits

### Phase 8-9: Audit → Billing
**Status:** Pending  
**Target:** 40 commits, end at 2ca9e1b
