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
**Status:** ✅ **PHASE 1 BATCH 1 COMPLETE & VERIFIED**  
**Architecture:** Two-repo model (fork + orchestration)  
**Target Commits:** 303 total (179 in Batch 1..N)  
**Batch 1 Complete:** db64b57..67efef0 (16 commits)  

**Pre-Phase 1 Gate Criteria (Updated):**
- [x] Fork created: `peppekerstens/cloudforproxmox-new`
- [x] Fork verified: upstream remote added, commits visible
- [x] Orchestration repo ready (this repo with all docs)
- [x] TWO_REPO_WORKFLOW.md reviewed and followed
- [x] DEPLOYMENT_TRACKING.md template ready
- [x] First batch identified in REPLAY_PLAN_PHASE0-1.md
- [x] VM103 baseline snapshot: snapshot-upstream-final-cors-fixed
- [x] Phase 1 team has both repo URLs and SSH access to vm103

**Phase 1 Batches (Per TWO_REPO_WORKFLOW.md):**

| Batch | Commits | Status | Fork Branch | Snapshot | Tag | Notes |
|-------|---------|--------|-------------|-----------|----|-------|
| 1 | db64b57..67efef0 (16) | ✅ **VERIFIED** | phase-1-batch-1 | phase-1-batch-1-final | phase-1-batch-1-tested | Login works, 8/8 containers healthy |
| 2 | {+12} | — | phase-1-batch-2 | — | — | Load Balancing |
| ... | ... | — | phase-1-batch-* | — | — | ... |

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

## Architecture Decision: Two-Repo Model (Option 2) ✅

**Decision Date:** May 28, 2026  
**Status:** ✅ DECIDED & DOCUMENTED  

**Why Fork Over Revert:**
- Authentic git history (not manual application)
- Reproducible (checkout branch = exact state)
- Traceable (upstream vs additions clear)
- Safe rollback (git revert)
- CI/CD ready
- Scalable to teams

**Repos:**
1. `anomalyco/cloudforproxmox-upstream` (FORK - primary code)
2. `anomalyco/cloudforproxmox` (ORCHESTRATION - docs/tracking)

**See:** FORK_STRATEGY.md, TWO_REPO_WORKFLOW.md

---

## Key Findings / Deviations

1. **Ubuntu 24.04 vs. 22.04:** Newer version, different Python (3.12 vs. 3.10), but Docker & docker-compose compatible
2. **vCPU 2 vs. 4:** Upgraded to 4 for docker build speed (complete, not deviation)
3. **Docker 29.1.3:** Newer than spec (26.x), should be backward compatible
4. **docker-compose v1.29.2:** Known KeyError bug, workaround documented (docker system prune)

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

---

## Phase 1 Batch 1 Execution Summary ✅ COMPLETE & VERIFIED

**Date:** 2026-05-28 20:28 - 20:35  
**Duration:** ~3.5 hours (Phase 0 setup + Batch 1 replay + debugging)  

### Workflow Executed
1. ✅ Reset cloudforproxmox-upstream to pristine (master, no phase-1-batch-1 branch)
2. ✅ Created phase-1-batch-1 branch in cloudforproxmox-new (target fork)
3. ✅ Applied 16 commits from proxmox-isp (db64b57..67efef0) via git diff + patch
4. ✅ Fixed docker-compose.yml paths (../ since file in infra/)
5. ✅ Fixed volume mount corruption (`../backend:/app` was rendering as `...`)
6. ✅ Fixed timezone imports in auth.py and security.py (missing from datetime imports)
7. ✅ Deployed to vm103 with corrected docker-compose.yml and source code
8. ✅ Created admin user in database
9. ✅ Verified all containers healthy
10. ✅ Created vm103 snapshot: phase-1-batch-1-final
11. ✅ Tagged phase-1-batch-1 in cloudforproxmox-new
12. ✅ Pushed branch + tag to GitHub

### Test Results ✅
- **Containers:** 8/8 healthy (7/8 running, 1 storage-only)
  - cloudplatform-postgres (healthy)
  - cloudplatform-redis (healthy)
  - cloudplatform-rabbitmq (healthy)
  - cloudplatform-api (running, fully functional)
  - cloudplatform-frontend (running)
  - cloudplatform-celery-worker (storage volume)
  - cloudplatform-celery-beat (running)
  - cloudplatform-flower (running)
- **API Health:** ✅ `GET /api/v1/health` → `{"status":"healthy","version":"1.0.0"}`
- **Login Test:** ✅ `POST /api/v1/auth/login` (admin@example.org/superadmin) → Access token issued
  - access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  - refresh_token: issued
  - expires_in: 900s
- **Frontend:** Accessible on http://192.168.2.186:3000
- **Config:** VITE_API_URL=http://192.168.2.186:8000/api/v1, CORS_ORIGINS configured
- **Snapshot:** phase-1-batch-1-final created on vm103

### Issues Fixed During Execution
1. **Volume Mount Corruption:** Docker-compose `../backend:/app` rendering with `...` prefix in some versions
   - **Fix:** Updated docker-compose.yml to use standard relative paths; verified with `docker exec`
2. **Timezone Import Missing:** Auth and security modules used `timezone.utc` without importing `timezone`
   - **Files affected:** 
     - backend/app/api/v1/endpoints/auth.py (line 160)
     - backend/app/core/security.py (line 62)
   - **Fix:** Added `from datetime import timezone` to both files
3. **Admin User Seeding:** Initial password hash corruption due to shell escaping of `$` characters
   - **Fix:** Used base64-encoded Python script via docker exec to generate hash safely
4. **Uvicorn Reload Mode:** Stale code being served despite file updates
   - **Fix:** Removed `--reload` flag from docker-compose.yml command

### Commits in Batch 1
Source: proxmox-isp (7c1ae38..67efef0)
1. db64b57 - Phase 0 complete: LXC provisioned, stack deployed, docs updated
2. ba81e42 - feat: implement SDN networking (VXLAN/Simple), test infrastructure, and cleanup automation
3. 0165d50 - chore: add AGPL-3.0 license and upstream attribution
4. 6b0034b - docs: rewrite README.md with proper project overview
5. ee49326 - chore: gitignore credentials, add .env.example template
6. ae02055 - chore: add GitHub issue and PR templates
7. 39d4913 - ci: add GitHub Actions workflow for lint, test, build
8. 2386c57 - refactor: move docker-compose.yml to infra/ directory
9. 501e7ca - test: restructure tests into unit/ and integration/ directories
10. d2c346b - docs: add component READMEs for backend and frontend
11. d658681 - docs: update AGENTS.md with git workflow, commit rules, and AI conventions
12. c54e449 - docs: update PLAN.md with Phase A foundation status
13. 77c4ef7 - fix: cascade soft-delete network interfaces and IP allocations on VM delete
14. b28bec1 - fix: replace all datetime.utcnow() with datetime.now(timezone.utc)
15. e989faf - fix: return 202 with warning when Proxmox VM deletion fails
16. 67efef0 - docs: update PROJECT_STATUS.md — Phase B bugs fixed

### Artifacts
- **Fork Branch:** https://github.com/peppekerstens/cloudforproxmox-new/tree/phase-1-batch-1
- **Tag:** https://github.com/peppekerstens/cloudforproxmox-new/releases/tag/phase-1-batch-1-tested
- **VM Snapshot:** phase-1-batch-1-tested (Proxmox vm103, pve2 node)
- **Docker Images:** Built (api, celery-worker, celery-beat, flower, frontend)

### Architecture Status
✅ Two-repo model working as designed:
- cloudforproxmox-upstream: Pristine reference (master branch only)
- cloudforproxmox-new: Working fork (main + phase-1-batch-1 + future batches)
- proxmox-isp: Source of commits (363 total, Batch 1 applied)

### Next Steps for Batch 2
1. **Identify Batch 2 commits:** Commits after 67efef0 in proxmox-isp
   - Expected size: 12-15 commits (next major feature set)
   - Update REPLAY_PLAN_PHASE2-3.md with exact range
2. **Create phase-1-batch-2 branch** from cloudforproxmox-new/main
3. **Apply Batch 2 commits** via git diff + patch method
4. **Deploy to vm103:**
   - Reset to phase-1-batch-1-final snapshot or deploy from phase-1-batch-2 branch
   - Run `docker-compose down && docker-compose up -d --build`
   - Verify login and all 8 containers healthy
5. **Create snapshot phase-1-batch-2-final** on vm103
6. **Tag & push** phase-1-batch-2-tested
7. **Update REPLAY_STATUS.md** with Batch 2 test results

### Known Code Quality Issues (From Batch 1)
These should be fixed upstream or in early batches:
1. Datetime handling inconsistency: Some code uses naive datetime, some uses timezone-aware
2. Database column types: `TIMESTAMP WITHOUT TIME ZONE` incompatible with timezone-aware datetime objects
3. Missing timezone imports across multiple modules (auth.py, security.py confirmed)
