# REPLAY_PLAN_PHASE0-1.md

## Executive Summary
- **Phase:** Setup → VM/LXC
- **Commits:** 179
- **Hash range:** 7c1ae38...66ad710
- **Date range:** 2026-05-20 → 2026-05-26
- **Target:** Reach 66ad710 with all tests passing

## Deployment Context
- **VM:** vm103 (Ubuntu 22.04 LTS, 4vCPU/4GB/20GB, Docker 26.x)
- **Containers:** 8 total (PostgreSQL 16, Redis 7, FastAPI backend, React frontend, Nginx, Celery worker, Celery beat, AdGuard)
- **Repo:** ~/github/proxmox-isp
- **Deploy method:** git checkout → docker-compose up → batch test
- **Exclude:** LXC deployment references (VM-only)

## Commits in This Phase

### Commit 7c1ae38 (2026-05-20)
**Message:** Phase 0: fork upstream cloud-platform, strip aspirational cruft

**Files Changed:** BE:87 FE:37 Infra:1

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7c1ae38
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-base

### Commit db64b57 (2026-05-20)
**Message:** Phase 0 complete: LXC provisioned, stack deployed, docs updated

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout db64b57
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7c1ae38

### Commit 0165d50 (2026-05-21)
**Message:** chore: add AGPL-3.0 license and upstream attribution

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 0165d50
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-db64b57

### Commit 6b0034b (2026-05-21)
**Message:** docs: rewrite README.md with proper project overview

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 6b0034b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-0165d50

### Commit ee49326 (2026-05-21)
**Message:** chore: gitignore credentials, add .env.example template

**Files Changed:** BE:0 FE:0 Infra:1

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout ee49326
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-6b0034b

### Commit ae02055 (2026-05-21)
**Message:** chore: add GitHub issue and PR templates

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout ae02055
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-ee49326

### Commit 39d4913 (2026-05-21)
**Message:** ci: add GitHub Actions workflow for lint, test, build

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 39d4913
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-ae02055

### Commit 2386c57 (2026-05-21)
**Message:** refactor: move docker-compose.yml to infra/ directory

**Files Changed:** BE:0 FE:0 Infra:3

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2386c57
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-39d4913


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

### Commit 501e7ca (2026-05-21)
**Message:** test: restructure tests into unit/ and integration/ directories

**Files Changed:** BE:11 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 501e7ca
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2386c57

### Commit d2c346b (2026-05-21)
**Message:** docs: add component READMEs for backend and frontend

**Files Changed:** BE:1 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d2c346b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-501e7ca

### Commit d658681 (2026-05-21)
**Message:** docs: update AGENTS.md with git workflow, commit rules, and AI conventions

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d658681
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d2c346b

### Commit c54e449 (2026-05-21)
**Message:** docs: update PLAN.md with Phase A foundation status

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout c54e449
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d658681

### Commit 77c4ef7 (2026-05-21)
**Message:** fix: cascade soft-delete network interfaces and IP allocations on VM delete

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 77c4ef7
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-c54e449

### Commit b28bec1 (2026-05-21)
**Message:** fix: replace all datetime.utcnow() with datetime.now(timezone.utc)

**Files Changed:** BE:17 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b28bec1
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-77c4ef7

### Commit e989faf (2026-05-21)
**Message:** fix: return 202 with warning when Proxmox VM deletion fails

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout e989faf
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b28bec1

### Commit 67efef0 (2026-05-21)
**Message:** docs: update PROJECT_STATUS.md — Phase B bugs fixed

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 67efef0
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-e989faf


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

### Commit 8bbd9b8 (2026-05-21)
**Message:** docs: mark Phase B complete, add next phase planning

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8bbd9b8
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-67efef0

### Commit 8d5ad15 (2026-05-21)
**Message:** docs: archive project history, streamline PLAN.md, update status

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8d5ad15
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8bbd9b8

### Commit 770a2de (2026-05-21)
**Message:** fix: enable ISO transfer and cleanup Celery tasks

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 770a2de
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8d5ad15

### Commit 3c1f1d7 (2026-05-21)
**Message:** docs: update status for Phase 1 epics 1.3 and 1.4 complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 3c1f1d7
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-770a2de

### Commit fe4fac0 (2026-05-21)
**Message:** feat: add cluster detail page at /clusters/:id

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout fe4fac0
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-3c1f1d7

### Commit ad5f6c3 (2026-05-21)
**Message:** docs: update status for Phase 1 epic 1.5 complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout ad5f6c3
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-fe4fac0

### Commit f978333 (2026-05-21)
**Message:** feat: add VM template support (convert, list, clone)

**Files Changed:** BE:6 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f978333
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-ad5f6c3

### Commit 296be75 (2026-05-21)
**Message:** docs: update status for Phase 1 epic 1.1 complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 296be75
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f978333


---

## Batch Test #3 (Commits 17-24)
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

### Commit 1c89305 (2026-05-21)
**Message:** feat: add LXC container creation support

**Files Changed:** BE:4 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 1c89305
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-296be75

### Commit be13bb8 (2026-05-21)
**Message:** docs: Phase 1 complete — all 5 epics done

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout be13bb8
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-1c89305

### Commit 6a826ed (2026-05-21)
**Message:** test: add Proxmox version checks and Phase 1 integration tests

**Files Changed:** BE:5 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 6a826ed
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-be13bb8

### Commit 2fdb609 (2026-05-21)
**Message:** docs: add phase-gate testing and version compatibility rules to AGENTS.md

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2fdb609
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-6a826ed

### Commit 434aff9 (2026-05-21)
**Message:** docs: add Phase 1 phase-gate test results and new issues #9-#11

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 434aff9
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2fdb609

### Commit d388cc6 (2026-05-21)
**Message:** fix: resolve Phase 1 integration test failures (#9, #10, #11)

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d388cc6
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-434aff9

### Commit 6161989 (2026-05-21)
**Message:** docs: add ACTIONS.md with deployment commands and credentials

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 6161989
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d388cc6

### Commit f44c321 (2026-05-21)
**Message:** docs: update status — Phase 1 bugs #9, #10, #11 fixed, awaiting deployment

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f44c321
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-6161989


---

## Batch Test #4 (Commits 25-32)
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

### Commit 9d68349 (2026-05-21)
**Message:** fix: complete Phase B bug fixes (#2, #3)

**Files Changed:** BE:6 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 9d68349
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f44c321

### Commit c2e3788 (2026-05-21)
**Message:** fix: add missing timezone import in auth.py and security.py

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout c2e3788
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-9d68349

### Commit 4b6cf8d (2026-05-21)
**Message:** fix: convert all DateTime columns to timezone-aware

**Files Changed:** BE:12 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4b6cf8d
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-c2e3788

### Commit 941e4d8 (2026-05-21)
**Message:** fix: correct table names in timezone migration (vlan_pool, vxlan_vni_pool)

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 941e4d8
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4b6cf8d

### Commit 742f006 (2026-05-21)
**Message:** fix: use UserResponse Pydantic schema instead of SQLAlchemy User model

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 742f006
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-941e4d8

### Commit c64c4e8 (2026-05-21)
**Message:** fix: persist user object in localStorage for admin nav visibility

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout c64c4e8
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-742f006

### Commit 00ac92f (2026-05-21)
**Message:** fix: move /members routes before /{org_id} to prevent 404

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 00ac92f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-c64c4e8

### Commit 6dc6085 (2026-05-21)
**Message:** test: add unit tests for ISO transfer Celery tasks

**Files Changed:** BE:3 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 6dc6085
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-00ac92f


---

## Batch Test #5 (Commits 33-40)
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

### Commit 3692f46 (2026-05-21)
**Message:** docs: update PROJECT_STATUS.md — Epic 1.3 complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 3692f46
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-6dc6085

### Commit fb3a415 (2026-05-21)
**Message:** feat: add LXC container creation support to CreateVMPage

**Files Changed:** BE:0 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout fb3a415
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-3692f46

### Commit d759135 (2026-05-21)
**Message:** docs: update PROJECT_STATUS.md — Epic 1.2 LXC UI complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d759135
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-fb3a415

### Commit 2f23344 (2026-05-21)
**Message:** feat: add VM template catalog page with clone functionality

**Files Changed:** BE:0 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2f23344
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d759135

### Commit f6f70cd (2026-05-21)
**Message:** docs: update PROJECT_STATUS.md — Phase 1 complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f6f70cd
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2f23344

### Commit 3198a6b (2026-05-21)
**Message:** fix: add missing import time in vm_tasks.py

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 3198a6b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f6f70cd

### Commit 16a141e (2026-05-21)
**Message:** docs: add architecture documentation and update phase status

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 16a141e
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-3198a6b

### Commit a7d632a (2026-05-21)
**Message:** fix: add iso_uploads shared volume to docker-compose

**Files Changed:** BE:0 FE:0 Infra:1

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a7d632a
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-16a141e


---

## Batch Test #6 (Commits 41-48)
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

### Commit 1afa293 (2026-05-21)
**Message:** fix: add aiosqlite to requirements for unit tests

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 1afa293
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a7d632a

### Commit fba5071 (2026-05-21)
**Message:** fix: add httpx to requirements for integration tests

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout fba5071
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-1afa293

### Commit 54cbf8c (2026-05-21)
**Message:** fix: update integration tests for available templates and unique ISO names

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 54cbf8c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-fba5071

### Commit bfaf107 (2026-05-21)
**Message:** fix: use unique content for test ISO to avoid checksum collision

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout bfaf107
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-54cbf8c

### Commit fca6ae1 (2026-05-21)
**Message:** fix: detect Docker environment for integration test API URL

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout fca6ae1
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-bfaf107

### Commit f966ee4 (2026-05-21)
**Message:** fix: add 192.168.2.133:3000 to CORS_ORIGINS

**Files Changed:** BE:0 FE:0 Infra:1

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f966ee4
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-fca6ae1

### Commit 0900fa3 (2026-05-21)
**Message:** chore: rebrand from Proxmox ISP to Cloud for Proxmox

**Files Changed:** BE:3 FE:4 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 0900fa3
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f966ee4

### Commit d065951 (2026-05-21)
**Message:** docs: add test coverage gaps to PLAN.md with issue references

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d065951
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-0900fa3


---

## Batch Test #7 (Commits 49-56)
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

### Commit 82bf556 (2026-05-21)
**Message:** docs: mark Phase 2 complete, update test counts in PLAN.md

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 82bf556
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d065951

### Commit 5ae81df (2026-05-21)
**Message:** fix: update hardcoded DB password from old ProxmoxISP2024! to dev_password_change_me

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5ae81df
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-82bf556

### Commit 1f0b942 (2026-05-22)
**Message:** docs: documentation sync, credential security overhaul, and structural cleanup

**Files Changed:** BE:2 FE:0 Infra:3

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 1f0b942
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5ae81df

### Commit 1f79eb1 (2026-05-22)
**Message:** fix: split UserResponse/UserWithOrgsResponse to avoid detached session errors

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 1f79eb1
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-1f0b942

### Commit 0b8f55d (2026-05-22)
**Message:** feat: add superadmin user update (PATCH /users/{user_id}) + edit modal + delete confirmation dialog

**Files Changed:** BE:2 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 0b8f55d
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-1f79eb1

### Commit 8b9b26c (2026-05-22)
**Message:** docs: update PLAN.md, PROJECT_STATUS.md, docs/API.md to reflect completed admin UI gaps and user CRUD

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8b9b26c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-0b8f55d

### Commit 0d27926 (2026-05-22)
**Message:** fix: atomic org creation with admin user (fixes orphaned orgs)

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 0d27926
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8b9b26c

### Commit d57cc31 (2026-05-22)
**Message:** docs: update PROJECT_STATUS.md with org creation fix

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d57cc31
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-0d27926


---

## Batch Test #8 (Commits 57-64)
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

### Commit 5418b21 (2026-05-23)
**Message:** feat: install toast notification system, replace all alert()/confirm() calls, add mutation feedback across all pages

**Files Changed:** BE:0 FE:23 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5418b21
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d57cc31

### Commit 8d27386 (2026-05-23)
**Message:** fix: add toast.ts wrapper module (was excluded by lib/ gitignore)

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8d27386
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5418b21

### Commit 0d60192 (2026-05-23)
**Message:** fix: scope lib/ gitignore to root only (was blocking frontend/src/lib)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 0d60192
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8d27386

### Commit a97b9e0 (2026-05-23)
**Message:** feat: include org name in creation toast, mark Epic 5.2 complete

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a97b9e0
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-0d60192

### Commit e593904 (2026-05-23)
**Message:** fix: add is_superadmin and is_active to UserInfo schema for org member responses

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout e593904
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a97b9e0

### Commit 317a89c (2026-05-24)
**Message:** fix: exclude soft-deleted users from org member lists (#38)

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 317a89c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-e593904

### Commit fa9be2b (2026-05-24)
**Message:** fix: specify explicit join condition to avoid ambiguous foreign keys

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout fa9be2b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-317a89c

### Commit 2296204 (2026-05-24)
**Message:** fix: improve sidebar visibility - adjust admin section header and border colors (#44)

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2296204
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-fa9be2b


---

## Batch Test #9 (Commits 65-72)
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

### Commit b1bd071 (2026-05-24)
**Message:** Merge pull request #45 from peppekerstens/fix/44-sidebar-visibility

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b1bd071
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2296204

### Commit e4749c4 (2026-05-24)
**Message:** chore: add opencode rule to ensure GitHub issues are always labeled

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout e4749c4
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b1bd071

### Commit 697b4f7 (2026-05-24)
**Message:** docs: research GitHub Caveman for token optimization and cost reduction

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 697b4f7
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-e4749c4

### Commit 0e484f7 (2026-05-24)
**Message:** docs: comprehensive guide for Caveman integration into OpenCode

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 0e484f7
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-697b4f7

### Commit b1ed58e (2026-05-24)
**Message:** docs: quick start guide for Caveman + OpenCode integration

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b1ed58e
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-0e484f7

### Commit 200580a (2026-05-24)
**Message:** chore: add caveman mode rules and commands to AGENTS.md

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 200580a
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b1ed58e

### Commit a241155 (2026-05-24)
**Message:** chore: enforce subagent preference + caveman-style subagent prompts (MANDATORY)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a241155
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-200580a

### Commit 11e8134 (2026-05-24)
**Message:** feat: per-org network type restrictions for VPC creation (#42) (#46)

**Files Changed:** BE:5 FE:6 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 11e8134
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a241155


---

## Batch Test #10 (Commits 73-80)
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

### Commit a24e0d3 (2026-05-24)
**Message:** fix: Administration section header text unreadable (#49) (#50)

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a24e0d3
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-11e8134

### Commit f3fb744 (2026-05-24)
**Message:** fix: remove all visible borders causing greyish sidebar sections (#49)

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f3fb744
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a24e0d3

### Commit bc55d86 (2026-05-24)
**Message:** fix: org creation fails — org.id is None when creating membership (#66)

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout bc55d86
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f3fb744

### Commit 2805b33 (2026-05-24)
**Message:** chore: add .hook-logs/ to gitignore and opencode hooks config

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2805b33
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-bc55d86

### Commit 8cf1c83 (2026-05-24)
**Message:** fix: add rate limiting to login/register endpoints (#72, #75) (#81)

**Files Changed:** BE:3 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8cf1c83
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2805b33

### Commit 34a3231 (2026-05-24)
**Message:** fix: P1 batch — clone status, dead code, shared state, IP toggle, confirm focus, timer leak (#71, #73, #57, #60, #63, #77)

**Files Changed:** BE:2 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 34a3231
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8cf1c83

### Commit faa9341 (2026-05-24)
**Message:** fix: store and return LXC root password (#70)

**Files Changed:** BE:4 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout faa9341
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-34a3231

### Commit 40a612b (2026-05-24)
**Message:** docs: Phase 6.5 complete — 20 reviewer issues fixed, 1 deferred (#62)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 40a612b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-faa9341


---

## Batch Test #11 (Commits 81-88)
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

### Commit 078a71f (2026-05-24)
**Message:** refactor: improve error handling and add rate limit config

**Files Changed:** BE:10 FE:0 Infra:1

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 078a71f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-40a612b

### Commit 4e9a182 (2026-05-24)
**Message:** fix: resolve lint errors and type issues

**Files Changed:** BE:26 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4e9a182
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-078a71f

### Commit 2c05af6 (2026-05-24)
**Message:** fix: treat missing Proxmox config as idempotent delete

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2c05af6
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4e9a182

### Commit e70c9a8 (2026-05-24)
**Message:** docs: add functionality-first prioritization principle

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout e70c9a8
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2c05af6

### Commit 0b34361 (2026-05-24)
**Message:** docs: add language rule - English for user, Chinese OK for AI internals

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 0b34361
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-e70c9a8

### Commit 9ef64b8 (2026-05-24)
**Message:** fix: ensure get_storage_pools returns list, not ProxmoxResource

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 9ef64b8
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-0b34361

### Commit 0d48f0d (2026-05-24)
**Message:** fix: prevent IP allocation TOCTOU race with unique constraint

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 0d48f0d
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-9ef64b8

### Commit 5e3ac39 (2026-05-24)
**Message:** fix: check_and_reserve no longer rolls back caller's transaction

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5e3ac39
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-0d48f0d


---

## Batch Test #12 (Commits 89-96)
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

### Commit 6ddaa7c (2026-05-24)
**Message:** fix: restrict cluster endpoints to superadmin only

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 6ddaa7c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5e3ac39

### Commit e74c41a (2026-05-24)
**Message:** fix: DatabaseTask._db no longer shared across task instances

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout e74c41a
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-6ddaa7c

### Commit 7ad1bec (2026-05-24)
**Message:** fix: ISO checksum no longer stores fake URL hash

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7ad1bec
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-e74c41a

### Commit 83d7c5c (2026-05-24)
**Message:** fix: reduce ISO download worker blocking from 10min to ~100s

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 83d7c5c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7ad1bec

### Commit e727318 (2026-05-24)
**Message:** fix(containers): add delete confirmation dialog

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout e727318
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-83d7c5c

### Commit 222e43c (2026-05-24)
**Message:** fix(clusters): per-row sync button state

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 222e43c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-e727318

### Commit 12c0d40 (2026-05-24)
**Message:** fix(create-cluster): surface API error detail instead of generic message

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 12c0d40
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-222e43c

### Commit 49c19fc (2026-05-24)
**Message:** test(network): add unit tests for network_service.py

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 49c19fc
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-12c0d40


---

## Batch Test #13 (Commits 97-104)
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

### Commit 71dac03 (2026-05-24)
**Message:** docs: update plan and status — break #19 into 8 sub-epics

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 71dac03
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-49c19fc

### Commit 8e56d6f (2026-05-24)
**Message:** test(api): add auth + users endpoint tests (29 tests)

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8e56d6f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-71dac03

### Commit 4fb3e29 (2026-05-24)
**Message:** test(api): add clusters endpoint tests (31 tests)

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4fb3e29
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8e56d6f

### Commit 858051a (2026-05-24)
**Message:** docs: prioritize enhancements, update phase status

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 858051a
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4fb3e29

### Commit 2abf038 (2026-05-25)
**Message:** docs: update plan and status for Session 4

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2abf038
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-858051a

### Commit d91eef8 (2026-05-25)
**Message:** fix: two regressions from earlier fixes

**Files Changed:** BE:0 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d91eef8
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2abf038

### Commit 0e6aeac (2026-05-25)
**Message:** docs: add working deployment method to infra/README.md

**Files Changed:** BE:0 FE:0 Infra:1

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 0e6aeac
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d91eef8

### Commit d88f898 (2026-05-25)
**Message:** feat: add admin seed script (#127)

**Files Changed:** BE:0 FE:0 Infra:1

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d88f898
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-0e6aeac


---

## Batch Test #14 (Commits 105-112)
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

### Commit 6253f7f (2026-05-25)
**Message:** fix: allow extra env vars in pydantic settings

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 6253f7f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d88f898

### Commit cbecf6f (2026-05-25)
**Message:** refactor: move create_admin.py to backend/scripts/

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout cbecf6f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-6253f7f

### Commit 782cfaa (2026-05-25)
**Message:** feat: implement global + per-org branding (#115)

**Files Changed:** BE:9 FE:8 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 782cfaa
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-cbecf6f

### Commit 808fcc3 (2026-05-25)
**Message:** docs: sanitize ACTIONS.md + add branding/backup docs

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 808fcc3
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-782cfaa

### Commit 8c403f4 (2026-05-25)
**Message:** fix: handle multiple active global_settings rows in root endpoint

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8c403f4
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-808fcc3

### Commit ca8e61f (2026-05-25)
**Message:** feat: add network bandwidth metering via Proxmox RRD API

**Files Changed:** BE:8 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout ca8e61f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8c403f4

### Commit ecb6e70 (2026-05-25)
**Message:** fix: remove invalid Pydantic constraints from plan schemas

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout ecb6e70
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-ca8e61f

### Commit 7087235 (2026-05-25)
**Message:** fix: admin plans endpoint response model

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7087235
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-ecb6e70


---

## Batch Test #15 (Commits 113-120)
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

### Commit 4410593 (2026-05-25)
**Message:** docs: update plan and status — Phases 7-9 complete, add Phase 9.x

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4410593
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7087235

### Commit 5137fee (2026-05-25)
**Message:** fix: wrap ProxmoxService calls in asyncio.to_thread (#145)

**Files Changed:** BE:5 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5137fee
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4410593

### Commit 3de9d54 (2026-05-25)
**Message:** docs: update status — ProxmoxService event loop fix (#145) complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 3de9d54
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5137fee

### Commit 3f9ecaf (2026-05-25)
**Message:** fix: resolve singleton query error in admin settings endpoint

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 3f9ecaf
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-3de9d54

### Commit a10e194 (2026-05-25)
**Message:** docs: update status — Phase 9.x complete, close #165-#168

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a10e194
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-3f9ecaf

### Commit b62bb34 (2026-05-25)
**Message:** fix: VM status set transitional before Proxmox confirms

**Files Changed:** BE:3 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b62bb34
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a10e194

### Commit e8f4c3c (2026-05-25)
**Message:** fix: add stop confirm dialog in VMDetailPage

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout e8f4c3c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b62bb34

### Commit 39df9a5 (2026-05-25)
**Message:** docs: all P1 issues resolved

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 39df9a5
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-e8f4c3c


---

## Batch Test #16 (Commits 121-128)
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

### Commit 25c74c6 (2026-05-25)
**Message:** fix: exclude templates from GET /vms list

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 25c74c6
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-39df9a5

### Commit 599eb54 (2026-05-25)
**Message:** test: add Pydantic validation tests for attach-network endpoint

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 599eb54
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-25c74c6

### Commit 259bcc5 (2026-05-25)
**Message:** fix: cap per_page at 100, replace selectin with joinedload in list_vms

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 259bcc5
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-599eb54

### Commit 94a0913 (2026-05-25)
**Message:** fix: split broad except into ImportError/broker-specific handlers

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 94a0913
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-259bcc5

### Commit d41e86f (2026-05-25)
**Message:** fix: remove auto-commit from get_db() to prevent silent GET mutations

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d41e86f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-94a0913

### Commit a99c298 (2026-05-25)
**Message:** fix: open VM console in new tab instead of popup

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a99c298
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d41e86f

### Commit c15d312 (2026-05-25)
**Message:** fix: add retry button to VMsPage error state, server-side node filter

**Files Changed:** BE:1 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout c15d312
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a99c298

### Commit 561e1db (2026-05-25)
**Message:** fix: cache ProxmoxService instances, add VMID collision retry

**Files Changed:** BE:11 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 561e1db
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-c15d312


---

## Batch Test #17 (Commits 129-136)
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

### Commit 4e91e02 (2026-05-25)
**Message:** feat: add shared LoadingState and ErrorState components

**Files Changed:** BE:0 FE:7 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4e91e02
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-561e1db

### Commit 19f562c (2026-05-25)
**Message:** fix: make network selection cards keyboard accessible

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 19f562c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4e91e02

### Commit 99ed5eb (2026-05-25)
**Message:** fix: add ARIA labels to progress bars and status badges

**Files Changed:** BE:0 FE:6 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 99ed5eb
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-19f562c

### Commit 42b8cf6 (2026-05-25)
**Message:** feat: replace LXC ostemplate free-text with dropdown from API

**Files Changed:** BE:1 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 42b8cf6
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-99ed5eb

### Commit 26d11a2 (2026-05-25)
**Message:** fix: add mobile-responsive sidebar with hamburger toggle

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 26d11a2
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-42b8cf6

### Commit f1c9ee8 (2026-05-25)
**Message:** feat: split VM creation form into multi-step wizard with progress indicator

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f1c9ee8
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-26d11a2

### Commit 643a91e (2026-05-25)
**Message:** docs: add external review log, update priorities after review session (17 new issues)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 643a91e
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f1c9ee8

### Commit b3eb693 (2026-05-25)
**Message:** fix: ContainersPage create button opens LXC wizard, not QEMU

**Files Changed:** BE:0 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b3eb693
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-643a91e


---

## Batch Test #18 (Commits 137-144)
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

### Commit 4c1b039 (2026-05-25)
**Message:** docs: mark #170 and #176 resolved in external review log

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4c1b039
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b3eb693

### Commit dde727f (2026-05-25)
**Message:** fix: add aria-label to icon-only action buttons in ClustersPage

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout dde727f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4c1b039

### Commit 4d3cca1 (2026-05-25)
**Message:** fix: add label elements to AdminUsersPage create form

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4d3cca1
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-dde727f

### Commit dcc4892 (2026-05-25)
**Message:** fix: add Escape handler and close button to NetworksPage modal

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout dcc4892
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4d3cca1

### Commit a216580 (2026-05-25)
**Message:** docs: update external review log — 5 A11y fixes resolved (#175,#177,#178,#179,#186)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a216580
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-dcc4892

### Commit 70c8e4a (2026-05-25)
**Message:** fix: cap frontend per_page at 100 to match backend validation (#150 follow-up)

**Files Changed:** BE:0 FE:4 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 70c8e4a
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a216580

### Commit c1c13fc (2026-05-25)
**Message:** fix: listMembers endpoint path (remove duplicate /api/v1 prefix)

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout c1c13fc
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-70c8e4a

### Commit aaadae5 (2026-05-25)
**Message:** refactor: extract color utilities, remove dead button, delete leftover file, fix NetworksPage colors

**Files Changed:** BE:0 FE:9 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout aaadae5
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-c1c13fc


---

## Batch Test #19 (Commits 145-152)
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

### Commit 9364875 (2026-05-25)
**Message:** fix: replace custom modal with ConfirmDialog in AdminUsersPage, add delete button to ISO list

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 9364875
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-aaadae5

### Commit befa390 (2026-05-25)
**Message:** docs: update PLAN.md with fixed issues from this session

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout befa390
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-9364875

### Commit b225ace (2026-05-25)
**Message:** fix: resolve all TypeScript compilation errors in frontend

**Files Changed:** BE:0 FE:17 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b225ace
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-befa390

### Commit bed96ed (2026-05-25)
**Message:** docs: simplify fallback strategy and clarify upload policy

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout bed96ed
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b225ace

### Commit de4a728 (2026-05-25)
**Message:** docs: add Phase 12.2 Let's Encrypt scaffolding with UI stubs

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout de4a728
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-bed96ed

### Commit f60c0d2 (2026-05-25)
**Message:** docs: add Phase 12 progress summary

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f60c0d2
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-de4a728

### Commit b2fd935 (2026-05-25)
**Message:** docs: update project status for Phase 12.1 and add deployment guide

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b2fd935
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f60c0d2

### Commit 511e2df (2026-05-25)
**Message:** docs: add documentation index (docs/README.md)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 511e2df
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b2fd935


---

## Batch Test #20 (Commits 153-160)
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

### Commit c4cb501 (2026-05-25)
**Message:** fix: correct YAML indentation in docker-compose.yml

**Files Changed:** BE:0 FE:0 Infra:2

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout c4cb501
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-511e2df

### Commit a4b7d53 (2026-05-25)
**Message:** fix: rewrite docker-compose.yml with correct YAML syntax

**Files Changed:** BE:0 FE:0 Infra:2

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a4b7d53
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-c4cb501

### Commit f1ebf2c (2026-05-25)
**Message:** docs: add VITE_API_URL setup, login troubleshooting, and admin user creation guide

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f1ebf2c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a4b7d53

### Commit 06ad281 (2026-05-26)
**Message:** docs: add issue-first workflow and update session 7 status

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 06ad281
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f1ebf2c

### Commit b714694 (2026-05-26)
**Message:** fix(frontend): add missing </div> in AdminUsersPage.tsx

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b714694
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-06ad281

### Commit 62a25a4 (2026-05-26)
**Message:** fix: resolve layout height conflicts causing content clipping

**Files Changed:** BE:0 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 62a25a4
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b714694

### Commit 31765fd (2026-05-26)
**Message:** fix: add Array.isArray() safety checks for useQuery data

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 31765fd
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-62a25a4

### Commit cfce7a2 (2026-05-26)
**Message:** docs: update PLAN.md with session 2026-05-26 fixes

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout cfce7a2
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-31765fd


---

## Batch Test #21 (Commits 161-168)
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

### Commit 9a3f023 (2026-05-26)
**Message:** docs: update PLAN.md with session 2026-05-26 P2 fixes

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 9a3f023
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-cfce7a2

### Commit 6ba6f6e (2026-05-26)
**Message:** docs: add production deployment plan for #197, #198, #199

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 6ba6f6e
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-9a3f023

### Commit 4e81197 (2026-05-26)
**Message:** docs: add session summary for 2026-05-26 (B → C → A plan)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4e81197
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-6ba6f6e

### Commit 03b4a7c (2026-05-26)
**Message:** docs: add PRODUCTION_INDEX for easy navigation

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 03b4a7c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4e81197

### Commit 79a71e6 (2026-05-26)
**Message:** docs: fix PLAN.md to match actual status (Phase 2/6/8 gaps + deprioritize prod work)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 79a71e6
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-03b4a7c

### Commit 1306fc7 (2026-05-26)
**Message:** feat: #203 - create test infrastructure scaffold + first unit test

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 1306fc7
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-79a71e6

### Commit 4aae81a (2026-05-26)
**Message:** docs: add reassessment session summary - pivot to Phase 6 tests

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4aae81a
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-1306fc7

### Commit af30c1c (2026-05-26)
**Message:** docs: add Phase 6 completion summary - 75 tests passing, foundation solid

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout af30c1c
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4aae81a


---

## Batch Test #22 (Commits 169-176)
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

### Commit 8f7492f (2026-05-26)
**Message:** docs: Phase 2/8 gaps complete - 94 total tests, all gaps closed

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8f7492f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-af30c1c

### Commit c3ddedd (2026-05-26)
**Message:** docs: add provider abstraction pattern guide (#206)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout c3ddedd
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8f7492f

### Commit 66ad710 (2026-05-26)
**Message:** docs: update PLAN.md - session complete, ready for staging demo

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 66ad710
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-c3ddedd


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
