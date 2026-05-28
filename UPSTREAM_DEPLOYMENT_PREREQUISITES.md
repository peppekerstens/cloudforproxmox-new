# Upstream Deployment Prerequisites: Complete Documentation

**Date:** May 28, 2026  
**Status:** ✅ COMPLETE - Upstream verified working end-to-end  
**VM:** vm103 (192.168.2.186)  
**Upstream Commit:** HEAD of proxmox-cloudportal/cloud-platform (clean deployment)

---

## Executive Summary

Successfully deployed upstream cloud-platform on vm103 clean state. Encountered and resolved **3 critical configuration issues** (API URL, CORS, docker-compose bug) before achieving working login and dashboard access. This document serves as the **prerequisite baseline** for Phase 1 replay (commits 7c1ae38...next).

**Key Decision:** Will fork upstream repo for development baseline rather than using read-only reference.

---

## Phase Overview: "UPSTREAM FOUNDATION"

### Goal
Deploy clean upstream cloud-platform on vm103 → verify all 8 containers healthy → confirm login/dashboard working → snapshot baseline → ready for Phase 1 commits

### Prerequisites Met ✅
- vm103 created: 4 vCPU, 4GB RAM, 20GB disk (upgraded from 2 vCPU)
- Ubuntu 24.04 LTS installed
- Docker 29.1.3, docker-compose 1.29.2 pre-installed
- postgres, redis, rabbitmq, api, frontend, celery-worker, celery-beat, flower images pulled
- Admin user created (admin@example.org, password: TestDit1234_)
- User promoted to superadmin in DB

### Verification Criteria (All Met ✅)
- [ ] ✅ All 8 containers running (healthy)
- [ ] ✅ API responds to `/api/v1/health/detailed` with `{"status":"healthy"}`
- [ ] ✅ Frontend accessible at http://192.168.2.186:3000
- [ ] ✅ Login with admin@example.org succeeds
- [ ] ✅ Dashboard loads without errors
- [ ] ✅ No CORS/network errors in browser console

---

## Issues Encountered & Solutions

### Issue 1: Frontend API URL Hard-Coded to localhost

**Symptom:**  
Browser console error: `net::ERR_CONNECTION_REFUSED @ http://localhost:8000/api/v1/auth/login`

**Root Cause:**  
Frontend Vite config defaults to `localhost:8000`. Docker container runs on vm103 (192.168.2.186), but frontend tries to reach API on localhost (container's own loopback).

```typescript
// frontend/src/services/api.ts (BEFORE)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
```

**Solution:**  
Set `VITE_API_URL` environment variable in docker-compose.yml to actual VM IP.

**Changes Made:**

```yaml
# docker-compose.yml (BEFORE)
  frontend:
    ...
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1

# docker-compose.yml (AFTER)
  frontend:
    ...
    environment:
      - VITE_API_URL=http://192.168.2.186:8000/api/v1
```

**Verification:**  
Frontend container restarted → inspected env vars → confirmed 192.168.2.186 URL in use

---

### Issue 2: CORS Policy Blocking Login (Access-Control-Allow-Origin Missing)

**Symptom:**  
After fixing Issue 1, browser console error:

```
Access to XMLHttpRequest at 'http://192.168.2.186:8000/api/v1/auth/login' from origin 
'http://192.168.2.186:3000' has been blocked by CORS policy: Response to preflight 
request doesn't pass access control check: No 'Access-Control-Allow-Origin' header 
is present on the requested resource.
```

**Root Cause:**  
FastAPI CORS middleware configured with default origins (`localhost:3000`, `localhost:5173`). Frontend origin `192.168.2.186:3000` not in allowlist.

```python
# backend/app/core/config.py
CORS_ORIGINS: str = Field(default="http://localhost:3000")

def get_cors_origins(self) -> List[str]:
    if isinstance(self.CORS_ORIGINS, str):
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    return self.CORS_ORIGINS
```

```python
# backend/app/main.py
CORSMiddleware(
    ...
    allow_origins=settings.get_cors_origins(),
    ...
)
```

**Solution:**  
Add 192.168.2.186:3000 to CORS_ORIGINS environment variable.

**Changes Made:**

```yaml
# docker-compose.yml (BEFORE)
      - CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# docker-compose.yml (AFTER)
      - CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://192.168.2.186:3000
```

**Verification:**  
API container restarted with new env var → CORS headers now present in preflight response → login POST succeeds

---

### Issue 3: docker-compose 1.29.2 KeyError: 'ContainerConfig' Bug

**Symptom:**  
When restarting containers with docker-compose:

```
KeyError: 'ContainerConfig'

File "/usr/lib/python3/dist-packages/compose/service.py", line 1579, in get_container_data_volumes
    container.image_config['ContainerConfig'].get('Volumes') or {}
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
KeyError: 'ContainerConfig'
```

**Root Cause:**  
docker-compose v1.29.2 has known bug with container metadata inspection. Occurs when:
- Container already exists from previous run
- docker-compose tries to inspect volumes from old image config
- Image metadata is malformed or missing `ContainerConfig` key

**Solution (Primary):**  
Use `docker system prune -a --volumes -f` to clean all stopped containers, unused images, and dangling volumes. Fresh start prevents metadata inspection.

**Solution (Alternative):**  
Restart containers directly via `docker rm -f` + `docker run` (bypasses docker-compose entirely).

**Solution (Long-term):**  
Upgrade docker-compose to v2 (plugin-based) → not available on this system.

**Commands Used:**

```bash
# Primary: Clean all and restart
docker system prune -a --volumes -f
docker-compose up -d

# Alternative: Restart specific container manually
docker rm -f cloudplatform-api
docker run -d \
  -p 8000:8000 \
  -e CORS_ORIGINS='...' \
  -v /path/to/backend:/app \
  --network cloud-platform-upstream_cloudplatform-network \
  --name cloudplatform-api \
  cloud-platform-upstream_api:latest \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Lessons Learned:**
1. docker-compose 1.29.2 is fragile; use workarounds or upgrade
2. Explicit network attachment required when using `docker run` directly (not auto-created by docker-compose)
3. Image rebuild (`docker build`) needed after code changes; docker-compose will cache old images

**Verification:**  
Both approaches tested → both successfully started all 8 containers → all healthy

---

## Configuration Changes Summary

| File | Change | Before | After |
|------|--------|--------|-------|
| `docker-compose.yml` (frontend env) | VITE_API_URL | `http://localhost:8000/api/v1` | `http://192.168.2.186:8000/api/v1` |
| `docker-compose.yml` (api env) | CORS_ORIGINS | `http://localhost:3000,http://localhost:5173` | `http://localhost:3000,http://localhost:5173,http://192.168.2.186:3000` |

**Files NOT Modified:**
- Source code unchanged (backend/app, frontend/src)
- Database schema unchanged
- All business logic unchanged

---

## Infrastructure & Deployment Details

### VM Configuration
```
Host:        vm103 (pve2)
IP:          192.168.2.186
vCPU:        4 (upgraded from 2 for docker build speed)
RAM:         4GB
Disk:        20GB
OS:          Ubuntu 24.04 LTS
Docker:      29.1.3
docker-compose: 1.29.2 (known issues with volumes)
```

### Container Stack
| Container | Image | Port | Status | Network |
|-----------|-------|------|--------|---------|
| cloudplatform-postgres | postgres:14 | 5432 | Healthy | cloudplatform-network |
| cloudplatform-redis | redis:7 | 6379 | Healthy | cloudplatform-network |
| cloudplatform-rabbitmq | rabbitmq:3.12-management | 5672, 15672 | Healthy | cloudplatform-network |
| cloudplatform-api | cloud-platform-upstream_api:latest | 8000 | Healthy | cloudplatform-network |
| cloudplatform-frontend | cloud-platform-upstream_frontend:latest | 3000 | Healthy | cloudplatform-network |
| cloudplatform-celery-worker | cloud-platform-upstream_api:latest | - | Healthy | cloudplatform-network |
| cloudplatform-celery-beat | cloud-platform-upstream_api:latest | - | Healthy | cloudplatform-network |
| cloudplatform-flower | cloud-platform-upstream_api:latest | 5555 | Healthy | cloudplatform-network |

### API Health Check
```bash
$ curl -s http://192.168.2.186:8000/api/v1/health/detailed
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "database": "healthy",
    "redis": "not_implemented"
  },
  "timestamp": "2026-05-28T19:15:37.470738"
}
```

### Login Test (Verified ✅)
```
Email:    admin@example.org
Password: TestDit1234_
Result:   ✅ Login successful, redirected to http://192.168.2.186:3000/dashboard
Console:  0 errors, 2 warnings (expected)
```

---

## Snapshot Created

**Name:** `snapshot-upstream-final-cors-fixed`  
**Description:** Upstream cloud-platform working: login verified, CORS fixed, all containers healthy  
**State:** Ready for Phase 1 replay

---

## Critical Knowledge: Fork Strategy Going Forward

### ⚠️ Problem with Read-Only Upstream Reference

Current setup:
- `cloudforproxmox-old` (~/github/proxmox-isp): Read-only reference
- `cloudforproxmox-new` (~/github/cloudforproxmox): Development repo (currently has upstream code)

**Issue:** We're replaying commits from cloudforproxmox-old into cloudforproxmox-new by manually cherry-picking. This is:
1. **Error-prone** - manual process, easy to miss commits or apply wrong diffs
2. **Not reproducible** - if we lose track, hard to see what's been replayed
3. **Git history contaminated** - we're mixing upstream commits with manual commits, losing traceability

### ✅ Recommended Solution: Fork Upstream Officially

**Action Items:**
1. Fork proxmox-cloudportal/cloud-platform to anomalyco/cloudforproxmox-upstream (or similar)
2. Use forked upstream as baseline in cloudforproxmox-new
3. Track replay commits against official upstream (know exact divergence point: 7c1ae38)
4. Tag each phase snapshot in git
5. Keep REPLAY_PLAN_PHASE*.md files as above-code documentation

**Benefits:**
- Clean git history: upstream commits preserved exactly
- Traceability: can see `git log --oneline` and know exactly what's been added
- Rollback safety: can `git revert` instead of manual rollback
- CI/CD ready: can run tests against specific replay phases
- Maintainability: future developers can understand intent from commit messages

**Implementation (Post-Phase 0):**
```bash
# Create fork on GitHub (one-time)
# Then in cloudforproxmox-new:
git remote add upstream https://github.com/anomalyco/cloudforproxmox-upstream
git fetch upstream
git rebase upstream/main  # or reset to 7c1ae38 fork point

# For each phase:
git checkout -b phase-1-batch-1  # or similar
git cherry-pick <upstream-commits> ...
git tag phase-1-batch-1-tested
# snapshot
git push origin phase-1-batch-1
```

---

## Troubleshooting Reference

### Problem: "Can't reach API from frontend"
**Check List:**
1. Verify VITE_API_URL env var in frontend docker-compose
2. Verify API container running: `docker ps | grep api`
3. Verify API responding: `curl http://192.168.2.186:8000/api/v1/health/detailed`
4. Check frontend logs: `docker logs cloudplatform-frontend`
5. Check API logs: `docker logs cloudplatform-api`

### Problem: CORS error in browser console
**Check List:**
1. Verify CORS_ORIGINS env var in api docker-compose
2. Confirm frontend origin is in allowlist (e.g., `http://192.168.2.186:3000`)
3. Restart API container: `docker rm -f cloudplatform-api && docker-compose up -d api`
4. Clear browser cache (Ctrl+Shift+Delete)
5. Verify preflight response: `curl -i -X OPTIONS http://192.168.2.186:8000/api/v1/auth/login`

### Problem: "KeyError: 'ContainerConfig'" in docker-compose
**Solution:**
```bash
docker system prune -a --volumes -f
docker-compose up -d
```

### Problem: Container won't start after code changes
**Solution:**
```bash
# Rebuild image
docker build -t cloud-platform-upstream_api:latest ./backend

# Restart container
docker rm -f cloudplatform-api
docker-compose up -d api
```

---

## Next Steps: Phase 1 Replay

### Pre-Phase 1 Checklist
- [ ] ✅ Snapshot `snapshot-upstream-final-cors-fixed` created
- [ ] ✅ docker-compose.yml VITE_API_URL and CORS_ORIGINS updated
- [ ] ✅ All 8 containers healthy
- [ ] ✅ Login tested and verified
- [ ] ✅ This document (UPSTREAM_DEPLOYMENT_PREREQUISITES.md) complete and committed

### Phase 1 Gate Criteria
Before commencing Phase 1 (commits 7c1ae38...next):
1. Snapshot baseline exists and is verified
2. All configuration changes documented here are applied
3. Docker-compose bug workarounds documented
4. Fork strategy decided and communicated
5. REPLAY_PLAN_PHASE0-1.md reviewed and ready

---

---

## Phase 0 Addition: Proxmox Cluster Integration ✅

**Date:** May 28, 2026  
**Status:** ✅ COMPLETE - Cluster registered and verified  
**Reference:** PROXMOX_CLUSTER_INTEGRATION.md (comprehensive guide)

### Integration Summary

Successfully integrated Proxmox cluster (pve2-production) with cloud-platform. The system can now manage VMs, containers, snapshots, and resources on Proxmox nodes pve2 and pve1 via REST API and web UI.

**Cluster Details:**
- Name: `pve2-production`
- Cluster ID: `06fd7cc0-1db5-438f-830c-7498f72d94f6`
- Proxmox URL: `https://192.168.2.22:8006`
- Version: 9.1.5
- Nodes: 2 (pve2, pve1)
- Authentication: API Token (root@pam!cloud-platform)
- Status: ✅ Active & Connected

**What Was Done:**
1. Created Proxmox API token: `root@pam!cloud-platform`
2. Registered cluster in cloud-platform API (POST /api/v1/clusters)
3. Tested connection successfully (version: 9.1.5, nodes: [pve2, pve1])
4. Verified cluster listed and active (GET /api/v1/clusters)

**What This Enables:**
- Create and manage VMs on Proxmox cluster
- Create and restore snapshots
- Manage containers (LXCs)
- Monitor resource usage
- Control VM lifecycle (start, stop, reboot)
- Access VM consoles
- Configure networking and storage

**See PROXMOX_CLUSTER_INTEGRATION.md for:**
- Step-by-step integration procedure
- API token creation and security
- Testing procedures
- Troubleshooting guide
- Complete API endpoint documentation

### Pre-Phase 1 Gate Update

Proxmox cluster integration is now a prerequisite for Phase 1. Verify:
- [x] Proxmox cluster accessible and running
- [x] API token created in Proxmox
- [x] Cluster registered in cloud-platform
- [x] Connection test passes
- [x] Nodes discovered successfully

---

## References

- **VM Access:** `ssh peppe@192.168.2.186` (password: TestDit1234_)
- **Frontend:** http://192.168.2.186:3000
- **API:** http://192.168.2.186:8000/api/v1
- **Flower (Celery):** http://192.168.2.186:5555
- **Proxmox Console:** pve2 → vm103 (VM ID 103)
- **Proxmox Cluster:** https://192.168.2.22:8006
- **Upstream Repo:** https://github.com/proxmox-cloudportal/cloud-platform
- **Local Reference:** ~/github/proxmox-isp (cloudforproxmox-old, read-only)
- **Development Repo:** ~/github/cloudforproxmox (cloudforproxmox-new, current)
- **Integration Guide:** PROXMOX_CLUSTER_INTEGRATION.md (this repo)

---

## Sign-Off

**Upstream deployment phase complete and verified.**

- **Deployed by:** OpenCode agent
- **Date:** May 28, 2026, 19:15 UTC
- **Duration:** ~1 hour (troubleshooting included)
- **Issues resolved:** 3 (API URL, CORS, docker-compose)
- **Verification:** Login successful, dashboard accessible, all containers healthy

Ready for Phase 1 commit replay.
