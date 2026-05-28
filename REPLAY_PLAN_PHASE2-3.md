# REPLAY_PLAN_PHASE2-3.md

## Executive Summary
- **Phase:** Network → Onboard
- **Commits:** 22
- **Hash range:** ba81e42...8b05695
- **Date range:** 2026-05-21 → 2026-05-26
- **Target:** Reach 8b05695 with all tests passing

## Deployment Context
- **VM:** vm103 (Ubuntu 22.04 LTS, 4vCPU/4GB/20GB, Docker 26.x)
- **Containers:** 8 total (PostgreSQL 16, Redis 7, FastAPI backend, React frontend, Nginx, Celery worker, Celery beat, AdGuard)
- **Repo:** ~/github/proxmox-isp
- **Deploy method:** git checkout → docker-compose up → batch test
- **Exclude:** LXC deployment references (VM-only)

## Commits in This Phase

### Commit ba81e42 (2026-05-21)
**Message:** feat: implement SDN networking (VXLAN/Simple), test infrastructure, and cleanup automation

**Files Changed:** BE:19 FE:2 Infra:1

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout ba81e42
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-base

### Commit 010082a (2026-05-21)
**Message:** feat: add firewall rules management (Epic 2.3)

**Files Changed:** BE:9 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 010082a
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-ba81e42

### Commit 7431dc0 (2026-05-21)
**Message:** fix: add missing and_ import in vms.py firewall endpoints

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7431dc0
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-010082a

### Commit 43a09d7 (2026-05-21)
**Message:** fix: use integer 1/0 for Proxmox firewall enable param

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 43a09d7
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7431dc0

### Commit 602dcb9 (2026-05-21)
**Message:** docs: update PLAN.md with Phase 2 progress (IPAM ✅, Firewall backend ✅)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 602dcb9
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-43a09d7

### Commit 5da63b6 (2026-05-21)
**Message:** feat: add Firewall tab to VM detail page (Epic 2.3 GUI)

**Files Changed:** BE:0 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5da63b6
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-602dcb9

### Commit 29e3153 (2026-05-21)
**Message:** feat: enable firewall by default on VM/LXC creation

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 29e3153
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5da63b6

### Commit f900dba (2026-05-21)
**Message:** feat: complete DNS integration (auto-registration, admin UI, AdGuard deployment)

**Files Changed:** BE:15 FE:5 Infra:2

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f900dba
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-29e3153


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

### Commit 1a0392c (2026-05-21)
**Message:** test: add Phase 2 networking phase-gate integration tests (24 tests)

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 1a0392c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f900dba

### Commit 2a661d5 (2026-05-21)
**Message:** docs: add Phase 3 Onboarding as P0 priority epic

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2a661d5
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-1a0392c

### Commit eb1685c (2026-05-21)
**Message:** feat: add user self-registration flow (Phase 3.1, 3.2, 3.3)

**Files Changed:** BE:0 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout eb1685c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2a661d5

### Commit 2c7095e (2026-05-21)
**Message:** docs: mark Phase 3 Onboarding complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2c7095e
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-eb1685c

### Commit a40b75d (2026-05-24)
**Message:** feat: dedicated Admin Networking page with org selector (#47) (#48)

**Files Changed:** BE:0 FE:4 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a40b75d
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2c7095e

### Commit 29106bf (2026-05-24)
**Message:** fix(admin-networking): add required indicator and toast on missing org

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 29106bf
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a40b75d

### Commit 77f2b7c (2026-05-24)
**Message:** test(dns): add unit tests for dns_service orchestration layer

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 77f2b7c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-29106bf

### Commit bf0e04c (2026-05-24)
**Message:** fix(tests): skip DNS tests when AdGuard unavailable, add firewall timeout

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout bf0e04c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-77f2b7c


---

## Batch Test #2 (Commits 9-16)
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

### Commit 8a78186 (2026-05-25)
**Message:** fix: import dns_adguard to register adguard provider

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8a78186
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-bf0e04c

### Commit f35d43b (2026-05-25)
**Message:** fix: remove duplicate Networking menu in sidebar for superadmins

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f35d43b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8a78186

### Commit 3f25ad4 (2026-05-25)
**Message:** fix: unify DNS provider resolution across endpoints and Celery tasks

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 3f25ad4
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f35d43b

### Commit fcf383d (2026-05-25)
**Message:** fix: reorder registration form, required fields first

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout fcf383d
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-3f25ad4

### Commit 475ac4c (2026-05-25)
**Message:** fix: add aria-label to DNS admin toggle and switch buttons

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 475ac4c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-fcf383d

### Commit 8b05695 (2026-05-26)
**Message:** feat: add Phase 6 test suites - network and DNS services

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8b05695
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-475ac4c


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
