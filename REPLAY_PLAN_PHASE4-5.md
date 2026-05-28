# REPLAY_PLAN_PHASE4-5.md

## Executive Summary
- **Phase:** Multi-Tenant → RBAC
- **Commits:** 51
- **Hash range:** 18f428b...7e91680
- **Date range:** 2026-05-21 → 2026-05-26
- **Target:** Reach 7e91680 with all tests passing

## Deployment Context
- **VM:** vm103 (Ubuntu 22.04 LTS, 4vCPU/4GB/20GB, Docker 26.x)
- **Containers:** 8 total (PostgreSQL 16, Redis 7, FastAPI backend, React frontend, Nginx, Celery worker, Celery beat, AdGuard)
- **Repo:** ~/github/proxmox-isp
- **Deploy method:** git checkout → docker-compose up → batch test
- **Exclude:** LXC deployment references (VM-only)

## Commits in This Phase

### Commit 18f428b (2026-05-21)
**Message:** fix: add /settings redirect to /organization/settings

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 18f428b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-base

### Commit 08473a3 (2026-05-21)
**Message:** feat: add superadmin user and organization management

**Files Changed:** BE:2 FE:5 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 08473a3
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-18f428b

### Commit 8fbb637 (2026-05-21)
**Message:** fix: move /organizations/me route before /{org_id} to prevent path collision

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8fbb637
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-08473a3

### Commit 38d389b (2026-05-21)
**Message:** docs: add Phase 4 Multi-Tenant as P0 priority

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 38d389b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8fbb637

### Commit 4333766 (2026-05-21)
**Message:** feat: multi-tenant organization flow (Phase 4.1, 4.2, 4.3)

**Files Changed:** BE:3 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4333766
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-38d389b

### Commit 4ad7380 (2026-05-21)
**Message:** fix: add missing createOrg method to organizationsApi, improve token refresh interceptor

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4ad7380
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4333766

### Commit 93c26de (2026-05-22)
**Message:** feat: org-scoped user overview, role display, org selector in user creation, admin user step in org creation

**Files Changed:** BE:5 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 93c26de
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4ad7380

### Commit f7baf27 (2026-05-22)
**Message:** fix: specify foreign_keys on User.organizations relationship for disambiguation

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f7baf27
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-93c26de


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

### Commit 7749e6d (2026-05-22)
**Message:** feat: implement user-level quotas (Tier 3)

**Files Changed:** BE:8 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7749e6d
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f7baf27

### Commit df444bc (2026-05-22)
**Message:** feat: add superadmin quota management UI (admin panel)

**Files Changed:** BE:1 FE:4 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout df444bc
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7749e6d

### Commit 79cfa91 (2026-05-22)
**Message:** docs: update PLAN.md, PROJECT_STATUS.md, API.md for superadmin quota GUI

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 79cfa91
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-df444bc

### Commit e8fdfe0 (2026-05-23)
**Message:** feat: role promotion/demotion UI (Epic 5.3 #33)

**Files Changed:** BE:1 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout e8fdfe0
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-79cfa91

### Commit 8c5d9ad (2026-05-23)
**Message:** docs: add superadmin member role change endpoint to API.md

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8c5d9ad
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-e8fdfe0

### Commit 1559ffa (2026-05-23)
**Message:** fix: revert inline role dropdown, add role editing to EditUserModal, add superadmin toggle

**Files Changed:** BE:2 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 1559ffa
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8c5d9ad

### Commit dcaf1d1 (2026-05-24)
**Message:** fix: sidebar sections below Quotas render greyish in Firefox (#49) (#51)

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout dcaf1d1
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-1559ffa

### Commit 81ff0b9 (2026-05-24)
**Message:** feat: new orgs inherit quotas from default org instead of hardcoded defaults (#52) (#53)

**Files Changed:** BE:3 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 81ff0b9
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-dcaf1d1


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

### Commit 5fafd72 (2026-05-24)
**Message:** fix: TOCTOU race in quota enforcement — atomic check_and_reserve (#69) (#80)

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5fafd72
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-81ff0b9

### Commit 80f6475 (2026-05-24)
**Message:** fix: Celery task failure now decrements UserQuota (#74) (#82)

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 80f6475
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5fafd72

### Commit 5cf9af2 (2026-05-24)
**Message:** fix: validate quota limit not below current usage

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5cf9af2
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-80f6475

### Commit 78b93c4 (2026-05-24)
**Message:** fix: cleanup script handles 500 errors and resets quota via SQL

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 78b93c4
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5cf9af2

### Commit 285d8f2 (2026-05-24)
**Message:** fix(org-settings): add role change confirmation dialog

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 285d8f2
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-78b93c4

### Commit 855357b (2026-05-24)
**Message:** perf(quotas): batch query for admin quota overview

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 855357b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-285d8f2

### Commit 33db0b2 (2026-05-24)
**Message:** fix(quotas): remove dead user_quotas[0] statement

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 33db0b2
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-855357b

### Commit b85ebd7 (2026-05-24)
**Message:** fix(quota-page): show error state and keyboard shortcut hints

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b85ebd7
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-33db0b2


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

### Commit 78ebb53 (2026-05-24)
**Message:** feat(quotas): add reconciliation endpoint and periodic task

**Files Changed:** BE:4 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 78ebb53
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b85ebd7

### Commit 2f7a88d (2026-05-24)
**Message:** fix(quota-page): align user quotas table with admin quotas layout

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2f7a88d
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-78ebb53

### Commit 8e39291 (2026-05-24)
**Message:** feat(rbac): add custom org roles with per-resource CRUD permissions

**Files Changed:** BE:10 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8e39291
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2f7a88d

### Commit 61be233 (2026-05-24)
**Message:** feat(rbac): add role management UI for org admins

**Files Changed:** BE:0 FE:4 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 61be233
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8e39291

### Commit 408edd2 (2026-05-24)
**Message:** test(quota): add unit tests for quota_service.py

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 408edd2
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-61be233

### Commit a05e462 (2026-05-24)
**Message:** test(api): add organizations endpoint tests (37 tests)

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout a05e462
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-408edd2

### Commit 44f0922 (2026-05-24)
**Message:** test(api): add VMs, disks, snapshots, ISOs, storage, quotas, networks, DNS, console tests

**Files Changed:** BE:6 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 44f0922
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-a05e462

### Commit fe1b1a6 (2026-05-24)
**Message:** feat: compress user quotas to card+chip layout (#125)

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout fe1b1a6
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-44f0922


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

### Commit 7ddbec0 (2026-05-24)
**Message:** fix: remove path/header conflict in org_roles endpoint

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7ddbec0
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-fe1b1a6

### Commit bc9247b (2026-05-25)
**Message:** fix: AdminQuotasPage shows all resource types from all orgs

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout bc9247b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7ddbec0

### Commit 3246a9f (2026-05-25)
**Message:** fix: add plan_id migration for organizations table

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 3246a9f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-bc9247b

### Commit 81849bf (2026-05-25)
**Message:** fix: move quota operations inside DB transaction (#146)

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 81849bf
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-3246a9f

### Commit 2475afe (2026-05-25)
**Message:** docs: update status — quota transaction integrity (#146) fixed

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2475afe
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-81849bf

### Commit 9d15bdf (2026-05-25)
**Message:** fix(auth): eliminate TOCTOU race, first user gets admin role

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 9d15bdf
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2475afe

### Commit 6e6b014 (2026-05-25)
**Message:** fix: show all org members in User Quotas tab, enable adding quotas to users without entries

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 6e6b014
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-9d15bdf

### Commit 5e098c7 (2026-05-25)
**Message:** fix: add ARIA roles and focus trap to ConfirmDialog

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5e098c7
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-6e6b014


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

### Commit f437821 (2026-05-25)
**Message:** fix: wire role assignments endpoint to frontend, fix empty assigned users list

**Files Changed:** BE:1 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f437821
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5e098c7

### Commit 1bc206d (2026-05-25)
**Message:** fix: add defensive checks for undefined user_username in QuotaPage User Quotas tab

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 1bc206d
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f437821

### Commit 8aeadab (2026-05-25)
**Message:** fix: User Quotas shows correct usernames from org members endpoint

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8aeadab
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-1bc206d

### Commit 8c37cb7 (2026-05-26)
**Message:** fix: show loading placeholder in OrganizationSwitcher instead of null

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8c37cb7
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8aeadab

### Commit 0a0bc60 (2026-05-26)
**Message:** fix: role assignment endpoint exhausts SQL ResultProxy

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 0a0bc60
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8c37cb7

### Commit 5c7f424 (2026-05-26)
**Message:** fix: seed system roles for existing and new orgs

**Files Changed:** BE:4 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5c7f424
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-0a0bc60

### Commit 15381f8 (2026-05-26)
**Message:** refactor: full role system unification to OrgRole table

**Files Changed:** BE:5 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 15381f8
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5c7f424

### Commit 7b3e19f (2026-05-26)
**Message:** fix(frontend): add safety checks for organizations array

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7b3e19f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-15381f8


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

### Commit e59aea2 (2026-05-26)
**Message:** fix(api): reorder org-roles endpoints to fix FastAPI route conflict

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout e59aea2
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7b3e19f

### Commit 2011596 (2026-05-26)
**Message:** fix(frontend): add safety checks for organizations array in more pages

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2011596
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-e59aea2

### Commit 7e91680 (2026-05-26)
**Message:** fix(#140): prevent OrganizationSwitcher layout shift on load

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7e91680
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2011596


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
