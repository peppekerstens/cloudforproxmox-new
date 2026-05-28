# REPLAY_PLAN_PHASE8-9.md

## Executive Summary
- **Phase:** Audit → Billing
- **Commits:** 40
- **Hash range:** be24213...040259b
- **Date range:** 2026-05-21 → 2026-05-26
- **Target:** Reach 040259b with all tests passing

## Deployment Context
- **VM:** vm103 (Ubuntu 22.04 LTS, 4vCPU/4GB/20GB, Docker 26.x)
- **Containers:** 8 total (PostgreSQL 16, Redis 7, FastAPI backend, React frontend, Nginx, Celery worker, Celery beat, AdGuard)
- **Repo:** ~/github/proxmox-isp
- **Deploy method:** git checkout → docker-compose up → batch test
- **Exclude:** LXC deployment references (VM-only)

## Commits in This Phase

### Commit be24213 (2026-05-21)
**Message:** docs: add rationale for Phase 2 (Networking) before Billing

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout be24213
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-base

### Commit 32ef879 (2026-05-24)
**Message:** fix: org creation silent failure — single transaction, validated schema, UX improvements (#66) (#67)

**Files Changed:** BE:3 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 32ef879
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-be24213

### Commit ef3ce86 (2026-05-24)
**Message:** docs: add Phase 6.5 — Bug Fix + UX Polish

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout ef3ce86
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-32ef879

### Commit ffd5a81 (2026-05-24)
**Message:** fix: P2 batch — 10 UX/code quality improvements (#55, #56, #58, #59, #61, #64, #65, #76, #78, #79)

**Files Changed:** BE:11 FE:6 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout ffd5a81
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-ef3ce86

### Commit 7913500 (2026-05-24)
**Message:** docs: update project status and Phase 8 plan with audit trail research

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7913500
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-ffd5a81

### Commit 39d2053 (2026-05-24)
**Message:** fix(ux): TemplatesPage clone modal dismiss + ISO upload real progress

**Files Changed:** BE:0 FE:3 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 39d2053
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7913500

### Commit ff11b83 (2026-05-25)
**Message:** feat: #115 UX templating - APP_NAME customization

**Files Changed:** BE:0 FE:5 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout ff11b83
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-39d2053

### Commit 1edf35f (2026-05-25)
**Message:** feat: implement Phase 8 Audit Trail

**Files Changed:** BE:14 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 1edf35f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-ff11b83


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

### Commit cd4dbb2 (2026-05-25)
**Message:** feat: implement Phase 9 Billing data models + APIs

**Files Changed:** BE:13 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout cd4dbb2
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-1edf35f

### Commit ce1d96d (2026-05-25)
**Message:** feat: add billing frontend UI

**Files Changed:** BE:0 FE:7 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout ce1d96d
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-cd4dbb2

### Commit c6d84ca (2026-05-25)
**Message:** feat: add Stripe payment integration backend (#160)

**Files Changed:** BE:12 FE:0 Infra:1

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout c6d84ca
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-ce1d96d

### Commit d7cca43 (2026-05-25)
**Message:** feat: add Stripe payment frontend (checkout, payment methods, history)

**Files Changed:** BE:0 FE:12 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d7cca43
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-c6d84ca

### Commit d57c094 (2026-05-25)
**Message:** fix: handle missing Stripe publishable key gracefully

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d57c094
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d7cca43

### Commit 4c07024 (2026-05-25)
**Message:** refactor: abstract billing provider interface (#164)

**Files Changed:** BE:10 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 4c07024
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d57c094

### Commit 20227b5 (2026-05-25)
**Message:** docs: update status — billing provider abstraction and onboarding complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 20227b5
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-4c07024

### Commit 87ef671 (2026-05-25)
**Message:** feat: implement per-org billing provider override (#163)

**Files Changed:** BE:11 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 87ef671
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-20227b5


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

### Commit 15e9ab9 (2026-05-25)
**Message:** docs: update status — per-org billing override (#163) complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 15e9ab9
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-87ef671

### Commit df8b94f (2026-05-25)
**Message:** feat: add superadmin UX for per-org Stripe configuration (#162)

**Files Changed:** BE:0 FE:4 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout df8b94f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-15e9ab9

### Commit cd10b88 (2026-05-25)
**Message:** docs: update status — superadmin Stripe UX (#162) complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout cd10b88
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-df8b94f

### Commit 57c84b1 (2026-05-25)
**Message:** feat: add GET /billing/payments and /billing/invoices endpoints

**Files Changed:** BE:2 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 57c84b1
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-cd10b88

### Commit f450b12 (2026-05-25)
**Message:** docs: add billing endpoints to API reference

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f450b12
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-57c84b1

### Commit 3a0460b (2026-05-25)
**Message:** docs: update PLAN.md — P2 UX/backend bugs complete, 13 P2 deferred to Phase 12

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 3a0460b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f450b12

### Commit f23c6e3 (2026-05-25)
**Message:** docs: prioritize remaining P2 bugs — functional bugs first, then UX, security deferred to Phase 12

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout f23c6e3
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-3a0460b

### Commit 550851b (2026-05-25)
**Message:** fix: add ARIA semantics to BillingPage tabs

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 550851b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-f23c6e3


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

### Commit 7f51c46 (2026-05-25)
**Message:** feat: add billing plan subscription endpoint and UI integration

**Files Changed:** BE:2 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7f51c46
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-550851b

### Commit c997070 (2026-05-25)
**Message:** fix: indentation error in billing.py

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout c997070
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7f51c46

### Commit 89665db (2026-05-25)
**Message:** fix: use correct permission constant BILLING_UPDATE

**Files Changed:** BE:1 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 89665db
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-c997070

### Commit 1cb2f36 (2026-05-25)
**Message:** feat: add audit log UI for org admins and superadmins

**Files Changed:** BE:2 FE:5 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 1cb2f36
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-89665db

### Commit 8f160ea (2026-05-26)
**Message:** fix: remove conflicting h-screen wrappers from audit log pages

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 8f160ea
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-1cb2f36

### Commit 9593a9b (2026-05-26)
**Message:** feat: add Phase 6 test suites - auth and billing

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 9593a9b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-8f160ea

### Commit 5300e90 (2026-05-26)
**Message:** feat: close Phase 2/8 gaps - DNSAdminPage + DNS E2E tests + audit trail tests

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5300e90
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-9593a9b

### Commit 7624d6f (2026-05-26)
**Message:** feat: #205 - streamline quota UX consistency between /quotas and /admin/quotas

**Files Changed:** BE:0 FE:2 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7624d6f
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5300e90


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

### Commit 11228d6 (2026-05-26)
**Message:** docs: architecture review session - #206 billing provider analysis

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 11228d6
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7624d6f

### Commit 7e93408 (2026-05-26)
**Message:** feat: #206 Phase 1 - Backend provider configuration (configurable billing provider)

**Files Changed:** BE:5 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 7e93408
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-11228d6

### Commit b7f1ed8 (2026-05-26)
**Message:** feat: #206 Phase 2 - API consolidation (merge billing config endpoints)

**Files Changed:** BE:3 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b7f1ed8
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-7e93408

### Commit d053fa5 (2026-05-26)
**Message:** feat: #206 Phase 3 WIP - Create provider-agnostic billing config component

**Files Changed:** BE:0 FE:1 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout d053fa5
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b7f1ed8

### Commit 5de141e (2026-05-26)
**Message:** docs: #206 billing refactor session summary - Phases 1-2 complete

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 5de141e
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-d053fa5

### Commit b5eb237 (2026-05-26)
**Message:** feat: #206 Phase 3 COMPLETE - Merge AdminStripeConfigPage into AdminBillingPage

**Files Changed:** BE:0 FE:4 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout b5eb237
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-5de141e

### Commit 2ca9e1b (2026-05-26)
**Message:** docs: #206 COMPLETE - Billing refactor final summary (all 3 phases)

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 2ca9e1b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-b5eb237

### Commit 040259b (2026-05-26)
**Message:** docs: add deployment checklist for billing refactor #206

**Files Changed:** BE:0 FE:0 Infra:0

**Pre-flight Checklist:**
- [ ] vm103 healthy (docker ps shows 8 containers)
- [ ] Previous snapshot exists
- [ ] Storage >500MB free
- [ ] No running tests

**Deploy:**
```bash
git checkout 040259b
docker-compose up -d
sleep 5 && docker ps
```
Monitor logs 30s for CRITICAL errors.

**Rollback Target:** snapshot-2ca9e1b


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
