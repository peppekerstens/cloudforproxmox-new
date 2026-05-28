# REPLAY_PLAN_PHASE12.md

## Executive Summary
- **Phase:** HTTPS (EXPECTED FAILURE)
- **Commits:** 11
- **Hash range:** 9e628f9...d974568
- **Date range:** 2026-05-25 → 2026-05-26
- **Target:** Reach d974568 with all tests passing

## Deployment Context
- **VM:** vm103 (Ubuntu 22.04 LTS, 4vCPU/4GB/20GB, Docker 26.x)
- **Containers:** 8 total (PostgreSQL 16, Redis 7, FastAPI backend, React frontend, Nginx, Celery worker, Celery beat, AdGuard)
- **Repo:** ~/github/proxmox-isp
- **Deploy method:** git checkout → docker-compose up → batch test
- **Exclude:** LXC deployment references (VM-only)

## Commits in This Phase

### Commit 9e628f9 (2026-05-25)
**Message:** docs: add comprehensive HTTPS certificate management design document

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 9e628f9
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-base

### Commit a59ada0 (2026-05-25)
**Message:** docs: refine certificate management scope for Phase 12.1 MVP

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a59ada0
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-9e628f9

### Commit 146775f (2026-05-25)
**Message:** feat: implement Phase 12.1 certificate management backend

**Files Changed:** BE:8 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 146775f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a59ada0

### Commit 3ee496f (2026-05-25)
**Message:** feat: add certificate management frontend page (Phase 12.1 UI)

**Files Changed:** BE:0 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 3ee496f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-146775f

### Commit f36a9bb (2026-05-25)
**Message:** feat: add Nginx TLS reverse proxy configuration (Phase 12.1)

**Files Changed:** BE:0 FE:0 Infra:5

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f36a9bb
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-3ee496f

### Commit 8a8a5e0 (2026-05-25)
**Message:** fix: remove non-existent API endpoints from certificate page

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8a8a5e0
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f36a9bb

### Commit eb47cde (2026-05-25)
**Message:** fix: remove duplicate function definitions in certificates endpoint

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout eb47cde
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8a8a5e0

### Commit 647b3f1 (2026-05-25)
**Message:** feat: enable HTTPS with Nginx TLS reverse proxy

**Files Changed:** BE:0 FE:0 Infra:2

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 647b3f1
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-eb47cde


---

## Batch Test #1 (Commits 1-8)
## Batch Testing (After every 5-10 commits deployed)
Run via SSH on vm103:
```bash
docker ps
docker logs postgres 2>&1 | grep -i critical | wc -l
docker logs redis 2>&1 | grep -i critical | wc -l
docker logs backend 2>&1 | grep -i critical | wc -l
curl -s http://localhost:8000/health | grep -q "ok" && echo "API healthy" || echo "API unhealthy"
curl -s http://localhost | grep -q "<!DOCTYPE" && echo "UI loads" || echo "UI broken"
```

**Success Criteria:** All tests pass, 0 CRITICAL logs, 8 containers healthy

### Commit cb7ae51 (2026-05-25)
**Message:** docs: add comprehensive HTTPS deployment guide with gotchas

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout cb7ae51
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-647b3f1

### Commit b8cc5cd (2026-05-25)
**Message:** fix: set VITE_API_URL=/api/v1 for frontend HTTPS proxy

**Files Changed:** BE:0 FE:0 Infra:1

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b8cc5cd
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-cb7ae51

### Commit d974568 (2026-05-26)
**Message:** fix(#156): fix ProxmoxService URL parsing and SSL verification

**Files Changed:** BE:3 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d974568
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b8cc5cd


---

## Batch Testing (After every 5-10 commits deployed)
Run via SSH on vm103:
```bash
docker ps
docker logs postgres 2>&1 | grep -i critical | wc -l
docker logs redis 2>&1 | grep -i critical | wc -l
docker logs backend 2>&1 | grep -i critical | wc -l
curl -s http://localhost:8000/health | grep -q "ok" && echo "API healthy" || echo "API unhealthy"
curl -s http://localhost | grep -q "<!DOCTYPE" && echo "UI loads" || echo "UI broken"
```

**Success Criteria:** All tests pass, 0 CRITICAL logs, 8 containers healthy

---

## Phase Boundary Verification (Git History Spot-Check)
After this phase complete:
```bash
git log --oneline | head -20
```
Verify:
- Current HEAD matches expected end hash
- All major commits from phase present
- No unexpected commits

---

## Snapshot Management
**Active slots:** Track 3 snapshots during execution

**Rotation rule:** When limit reached, delete oldest; keep newest 2 + current working

**Exclusion:** Do not delete existing backup files from old repo

---

## Failure Handling Protocol
If batch tests fail at any commit:
1. Check failure symptoms in docker logs
2. Rollback to previous working snapshot
3. Retry with smaller batch (5 commits instead of 10)
4. If still fail: STOP, escalate to user
5. Document in REPLAY_STATUS.md:
   - Failed commit(s)
   - Symptom (which test failed, what error)
   - Last successful snapshot
   - Next steps for user

---

## ⚠️ EXPECTED FAILURE NOTES
Phase 12 (HTTPS) is marked as **EXPECTED FAILURE**.

**Known Issues:**
- Certificate management endpoints may have incomplete coverage
- HTTPS proxy configuration may conflict with Docker networking
- AdGuard and other services may not bind correctly to HTTPS ports

**If tests fail:**
1. Verify Nginx config: `docker exec nginx cat /etc/nginx/nginx.conf`
2. Check SSL cert paths: `docker exec nginx ls -la /certs/`
3. Review logs: `docker logs nginx | tail -50`
4. Document failure mode and escalate
