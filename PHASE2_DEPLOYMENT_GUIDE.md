# Phase 2 Deployment Guide: Network & Onboarding

**Effective Date:** Phase 2 planning (before Batch 1)  
**Based on:** PHASE0-1_RETROSPECTIVE.md, DEPLOYMENT_STRATEGY_ANALYSIS.md  
**Process:** Improved from Phases 0-1 using Option A + lessons learned

---

## Quick Start

Before deploying Phase 2 Batch 1:

```bash
# 1. Pre-flight validation (5 min) - MANDATORY
bash scripts/validate-deployment.sh

# 2. If pass: prepare deployment
# 3. If fail: fix issues, rerun validation

# 4. Deploy to vm103
docker-compose up

# 5. Post-deployment setup (15 min)
# See "Post-Deployment Checklist" below
```

---

## Phase 2 Overview

**Phase Name:** Network & Onboarding  
**Commits:** ~22 (per REPLAY_PLAN_PHASE2-3.md)  
**Expected Batches:** 2-3 (8-10 commits per batch)  
**Estimated Duration:** 2-3 weeks  
**VM:** vm103 (continue from Phase 1 Batch 2)  
**Snapshot Parent:** phase-1-batch-2-final

**Key Features:**
- Network setup (VLANs, bridges, SDN)
- Onboarding UI (signup, email verification)
- Organization management
- User invitations

---

## Pre-Deployment Planning

### Step 1: Analyze Phase 2 Commits (1 hour)

Before the first batch merge:

```bash
# Get Phase 2 commits
git log --oneline phase2-start..phase2-end

# Identify imports and dependencies
grep -r "^from\|^import" phase2-commits/ | grep -v "app\." | sort | uniq > /tmp/phase2-imports.txt

# Check against existing modules
grep "^from\|^import" backend/app/ > /tmp/existing-modules.txt

# Find missing modules
comm -23 <(sort /tmp/phase2-imports.txt) <(sort /tmp/existing-modules.txt)
```

**Document findings:**
- [ ] Which Phase 8+ modules are imported?
- [ ] Which are critical vs. optional?
- [ ] Which can be stubbed?

### Step 2: Identify Forward Dependencies

**Expected for Phase 2:**
- Network validation (might reference firewall service - Phase 8)
- User validation (might reference audit system - Phase 8)
- Email sending (might reference notification service - Phase 8)

**Action:** Create stubs for these before batch merge

### Step 3: Plan Stub Modules

**Potential stubs for Phase 2:**
```
backend/app/services/
  ├── network_service_stub.py (VLAN/SDN validation only, no persistence)
  ├── email_service_stub.py (print to console, don't send)
  └── notification_service_stub.py (silent no-op)

backend/app/tasks/
  └── onboarding_tasks_stub.py (welcome email = print)
```

**Document stub behavior in PHASE2_STUBS.md** (similar to PHASE1_BATCH2_STUBS.md)

### Step 4: Prepare Test Data

**What to test Phase 2:**
- [ ] Organization signup workflow
- [ ] User invitation system
- [ ] Network creation (stub persistence)
- [ ] Email notifications (console output)

**Test plan:**
1. Sign up as new org
2. Create user + invite
3. Verify email in console logs
4. Create network (verify doesn't persist to Proxmox)

### Step 5: Check Infrastructure Requirements

**Phase 2 might need:**
- [ ] SMTP configuration (for email stubs)
- [ ] SDN/network database tables (check migrations)
- [ ] New roles (org-admin, org-member - check RBAC)

**Verify before deployment:**
```bash
# Check database migrations
alembic current  # Should be up to date

# Check environment variables
grep -E "SMTP|EMAIL|NETWORK" .env

# Check for missing models
grep -r "class.*Model" backend/app/models/ | wc -l
```

---

## Pre-Deployment Validation (Option A)

### Mandatory: Pre-Flight Checks

**Run BEFORE any deployment:**

```bash
bash scripts/validate-deployment.sh
```

**This validates:**
- ✓ YAML syntax (docker-compose.yml)
- ✓ Python imports (all backend modules)
- ✓ TypeScript imports (all frontend modules)
- ✓ Environment variables (all REQUIRED vars set)

**Expected output:**
```
✓ PASS | validate-yaml.sh
✓ PASS | validate-backend.sh
✓ PASS | validate-frontend.sh
✓ PASS | validate-imports.sh
```

**If any FAIL:**
1. Read error message (includes file name and line number)
2. Refer to PRE_FLIGHT_CHECKLIST.md troubleshooting section
3. Fix issue
4. Rerun: `bash scripts/validate-deployment.sh`
5. Don't deploy until all pass

### Issues Option A Will Catch (Based on Phase 0-1)

**Caught by YAML validation:**
- Indentation errors in docker-compose.yml
- Missing services/volumes
- Invalid env var format

**Caught by Python validation:**
- Import errors (missing modules)
- Syntax errors (indentation, typos)
- Missing files

**Caught by TypeScript validation:**
- Missing imports (components, pages)
- Type errors
- ESLint rule violations

**Caught by import validation:**
- Environment variables not set
- Files referenced don't exist
- Path resolution failures

**NOT caught (needs runtime testing):**
- Database type mismatches
- Logic bugs in code
- External service unavailability

---

## Pre-Deployment Checklist (Manual Review)

Run after pre-flight validation PASSES.

### Configuration Review

- [ ] **docker-compose.yml**
  - [ ] All container images specified
  - [ ] All ports available (8000, 3000, 5432, etc.)
  - [ ] Environment variables properly formatted
  - [ ] No hardcoded localhost (except in examples)
  - [ ] Volumes mounted for persistence

- [ ] **.env file**
  - [ ] All required variables present (check .env.example)
  - [ ] ADMIN_EMAIL=admin@example.org
  - [ ] ADMIN_PASSWORD set (secure for prod)
  - [ ] PROXMOX_API_TOKEN_ID and SECRET
  - [ ] New Phase 2 vars (SMTP config, SDN settings, etc.)
  - [ ] No secrets committed to git

- [ ] **Frontend Configuration**
  - [ ] VITE_API_URL points to correct server
  - [ ] Dockerfile.dev has ENV VITE_API_URL
  - [ ] No hardcoded localhost URLs
  - [ ] Build succeeds: `npm run build`

- [ ] **Backend Configuration**
  - [ ] DATABASE_URL points to postgres
  - [ ] CORS_ORIGINS includes deployment IP
  - [ ] JWT_SECRET_KEY set (32+ chars)
  - [ ] Log levels configured (DEBUG for dev, INFO for prod)
  - [ ] New Phase 2 config sections reviewed

### Database & Infrastructure

- [ ] **Proxmox Integration**
  - [ ] API token exists and valid
  - [ ] Both pve1 and pve2 URLs accessible
  - [ ] Token in .env (not in code)

- [ ] **Database Migrations**
  - [ ] All Phase 2 migrations exist
  - [ ] Alembic can run migrations: `alembic upgrade head` (dry run)
  - [ ] New tables/columns match ORM models

- [ ] **New Phase 2 Services** (if any)
  - [ ] SMTP configuration (email stubs)
  - [ ] SDN/network backend setup
  - [ ] New environment variables documented

### Deployment Readiness

- [ ] **Backup & Recovery**
  - [ ] Previous snapshot exists: phase-1-batch-2-final
  - [ ] Rollback procedure documented
  - [ ] Team knows how to revert

- [ ] **Pre-deployment**
  - [ ] SSH access to vm103 verified
  - [ ] docker-compose.yml copied (or ready to git pull)
  - [ ] .env secrets prepared (secure storage)
  - [ ] Team notified of deployment window

- [ ] **Post-deployment Steps Documented**
  - [ ] Admin promotion step ready
  - [ ] Cluster registration steps ready
  - [ ] Test user creation ready

---

## Deployment Steps

### Step 1: Pre-Flight Validation (5 minutes)

```bash
cd /home/peppe/github/cloudforproxmox

# Run all validators
bash scripts/validate-deployment.sh

# If FAIL: fix issues and rerun
# If PASS: continue to Step 2
```

### Step 2: Deploy to vm103 (30 minutes)

```bash
# SSH to vm103 (or have root access)
ssh root@192.168.2.186

# Navigate to app directory
cd /home/peppe/github/cloudforproxmox-new/main

# Pull latest code
git pull origin main

# Start services
docker-compose up -d

# Wait for containers to become healthy
docker-compose ps
# All should show "Up (healthy)" or "Up"

# Check logs for errors
docker-compose logs --tail=50 | grep -i error
# Should be minimal/none
```

### Step 3: Verify Deployment (10 minutes)

```bash
# Check API health
curl -s http://192.168.2.186:8000/api/v1/health
# Should return: {"status": "ok"}

# Check frontend is serving
curl -s http://192.168.2.186:3000 | head -5
# Should return HTML (not error)

# Check database connectivity
docker-compose exec api python -c "from app.main import app; print('OK')"
# Should return: OK
```

### Step 4: Post-Deployment Setup (15 minutes)

**CRITICAL:** These steps must be done immediately after deployment

#### 4a. Promote Admin User to Superadmin

```bash
docker exec cloudplatform-postgres psql -U cloudplatform -d cloudplatform \
  -c "UPDATE users SET is_superadmin=true WHERE email='admin@example.org';"
```

**Verify:**
```bash
curl -X POST http://192.168.2.186:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}' \
  | jq -r '.access_token'

# Save token in /tmp/admin-token.txt
TOKEN=$(curl -s -X POST http://192.168.2.186:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}' \
  | jq -r '.access_token')

# Verify superadmin status
curl -s http://192.168.2.186:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" | jq '.is_superadmin'
# Should return: true
```

#### 4b. Register Proxmox Clusters (if Phase 2 changes them)

```bash
curl -X POST http://192.168.2.186:8000/api/v1/clusters \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "pve2-cluster",
    "datacenter": "pve2-dc",
    "region": "local",
    "api_url": "https://192.168.2.22:8006",
    "api_username": "cloudforproxmox@pve",
    "api_token_id": "cloudforproxmox@pve!cloudforproxmox-token",
    "api_token_secret": "$PROXMOX_API_TOKEN_SECRET",
    "verify_ssl": false
  }'
```

#### 4c. Sync VMs from Proxmox

```bash
# Get cluster ID from previous response
CLUSTER_ID="..."

curl -X POST http://192.168.2.186:8000/api/v1/clusters/$CLUSTER_ID/sync-vms \
  -H "Authorization: Bearer $TOKEN"
```

### Step 5: Test Core Workflows (15 minutes)

**These verify Phase 2 features are working:**

#### Test 1: Organization Signup (New in Phase 2)

```bash
curl -X POST http://192.168.2.186:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test-org@example.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "Org",
    "organization_name": "Test Organization"
  }' | jq '.'

# Should return: new user + org created
```

#### Test 2: Organization Management (New in Phase 2)

```bash
curl -s -X GET http://192.168.2.186:8000/api/v1/organizations \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {name, id}'

# Should return: list of organizations
```

#### Test 3: User Invitation (New in Phase 2)

```bash
curl -X POST http://192.168.2.186:8000/api/v1/organizations/$ORG_ID/invite-user \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invited@example.com",
    "role": "org-member"
  }' | jq '.'

# Should return: invitation created
# Check console logs for email (should print, not actually send)
docker-compose logs api | grep -i "email\|invited"
```

#### Test 4: Network Creation (Stubbed in Phase 2)

```bash
curl -X POST http://192.168.2.186:8000/api/v1/networks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-network",
    "cidr": "10.0.0.0/24",
    "gateway": "10.0.0.1"
  }' | jq '.'

# Should return: network created
# BUT: won't persist to Proxmox (stubbed)
```

#### Test 5: UI Workflows

```
1. Open http://192.168.2.186:3000
2. Login as admin@example.org / superadmin
3. Navigate to Organizations (should see Phase 2 UI)
4. Navigate to Networks (should see Phase 2 UI)
5. Check browser console for errors (should be none)
```

---

## Post-Deployment Documentation

### Create Deployment Report

After everything works, document:

```markdown
# Phase 2 Batch 1 Deployment Report

**Date:** [Date]
**Commits:** [commit range]
**VM:** vm103
**Duration:** [time]

## What Worked
- Organization signup
- User invitations
- Network creation (UI)

## What's Stubbed
- Network persistence (doesn't save to Proxmox)
- Email notifications (logs to console)

## Issues Found & Fixed
- [List any issues discovered]
- [How they were fixed]
- [Commit that fixed them]

## Next Steps
- Phase 2 Batch 2 deployment
- Team handoff for testing
```

### Create Snapshot

After everything verified:

```bash
# SSH to pve2
ssh root@192.168.2.22

# Create snapshot
qm snapshot 103 phase-2-batch-1-final \
  -description "Phase 2 Batch 1: Network & Onboarding features deployed and tested"

# Verify snapshot
qm listsnapshot 103 | grep phase-2
```

---

## Expected Issues & Resolutions

Based on PHASE0-1_RETROSPECTIVE.md, these issues are likely in Phase 2:

### Issue Type 1: Missing Module Imports (83% probability)

**Symptom:**
```
ModuleNotFoundError: No module named 'app.services.email_service'
```

**Root Cause:** Phase 2 imports Phase 8+ modules that don't exist

**Resolution:**
1. Pre-flight validation should have caught this (validate-imports.sh)
2. If not caught: create stub module
3. Re-run validation
4. Redeploy

**Prevention:** Analyze commits pre-deployment for missing imports

### Issue Type 2: Environment Variable Not Set (67% probability)

**Symptom:**
```
KeyError: 'SMTP_HOST' not found in environment
```

**Root Cause:** Phase 2 adds new config vars but .env not updated

**Resolution:**
1. Check .env.example for new variables
2. Add missing variables to .env
3. Re-run validation (validate-imports.sh checks env vars)
4. Redeploy

**Prevention:** Pre-flight checklist includes env var review

### Issue Type 3: Database Migration Failed (40% probability)

**Symptom:**
```
alembic.util.CommandError: Can't locate revision identified by 'abc123'
```

**Root Cause:** New Phase 2 tables/columns not migrated

**Resolution:**
1. Check Alembic status: `alembic current`
2. Run migration: `docker-compose exec api alembic upgrade head`
3. Verify schema: `docker-compose exec postgres psql -c "\dt"`
4. Redeploy if needed

**Prevention:** Check migrations exist before deployment

### Issue Type 4: CORS Blocking API Calls (50% probability)

**Symptom:**
```
Access-Control-Allow-Origin header missing
All API calls fail silently in browser
```

**Root Cause:** docker-compose.yml CORS_ORIGINS not updated for deployment IP

**Resolution:**
1. Check docker-compose.yml line 85: CORS_ORIGINS
2. Add deployment IP if missing: `http://192.168.2.186:3000`
3. Restart API: `docker-compose restart api`
4. Test: API calls should work

**Prevention:** Pre-flight validation checks indentation; manual checklist reviews IP

### Issue Type 5: Frontend Build Fails (30% probability)

**Symptom:**
```
ERR! Command failed: npm run build
ERR! missing import: @/components/missing-page
```

**Root Cause:** Phase 2 references components that don't exist yet (Phase 8)

**Resolution:**
1. Remove missing import OR create stub component
2. Re-run validation: `bash scripts/validate-frontend.sh`
3. Rebuild: `npm run build` (in container)
4. Redeploy

**Prevention:** Pre-flight validation (validate-frontend.sh) checks imports

---

## Rollback Procedure

If deployment fails at any point:

```bash
# SSH to pve2
ssh root@192.168.2.22

# List snapshots
qm listsnapshot 103 | grep phase

# Identify snapshot to restore
# Example: phase-1-batch-2-final

# Rollback VM to snapshot
qm snapshot rollback 103 phase-1-batch-2-final

# VM will shut down and restore to known-good state
# Start VM when ready: qm start 103

# On vm103, verify you're back to working state:
curl http://192.168.2.186:8000/api/v1/health
```

---

## Integration with Option A

**Phase 2 deployment MUST use Option A:**

```bash
# This is now mandatory, not optional
bash scripts/validate-deployment.sh

# All 4 validators must PASS before deployment
# If any FAIL: fix and rerun (don't skip validation)

# Expected runtime: <7 seconds
```

---

## Phase 2 Batch Plan

**Batch 1 (Commits: ~11)**
- Network infrastructure setup
- Organization management
- User invitation system

**Expected Issues:**
- Missing email service stub
- Network persistence stub needed
- SMTP env vars missing

**Pre-flight Validation Should Catch:** ~4-5 issues (83%)

---

**Batch 2 (Commits: ~11)**
- Onboarding workflows
- Email verification
- Advanced network features

**Expected Issues:** Similar to Batch 1

---

## Signoff Checklist

Before declaring Phase 2 deployment complete:

- [ ] Pre-flight validation PASSED
- [ ] All 4 validators showed PASS
- [ ] Post-deployment setup completed
- [ ] Admin is superadmin
- [ ] All test workflows succeeded
- [ ] Browser console shows no errors
- [ ] Snapshot created (phase-2-batch-1-final)
- [ ] Deployment report documented
- [ ] No issues outstanding (or documented for Phase 8)
- [ ] Ready for Phase 2 Batch 2

---

**Status:** Phase 2 Deployment Guide READY

This guide incorporates all lessons from Phase 0-1 plus Option A pre-flight validation. Ready for team to execute.
