# Phase 1 Batch 2 Deployment: Issues & Fixes

**Deployment Date:** 2026-05-29  
**VM:** vm103 (pve2, 192.168.2.186)  
**Status:** ✅ WORKING - Login functional, Proxmox clusters connected  
**Last Updated:** Commit e498925

---

## Overview

This document captures every issue encountered during Phase 1 Batch 2 deployment to vm103 and its resolution. All fixes are committed to the repo and tested on the live VM.

---

## CRITICAL ISSUES FIXED

### Issue #1: Login Failed - Timezone Bug in auth.py

**Status:** ✅ FIXED (Commit: e498925)

**Symptom:**
```
POST /api/v1/auth/login
Response: 500 Internal Server Error
Error: database column "last_login" is type timestamp without time zone, 
but app tried to insert timezone-aware datetime
```

**Root Cause:**
File: `backend/app/api/v1/endpoints/auth.py:160`
```python
# BROKEN
user.last_login = datetime.now(timezone.utc)  # timezone-aware
# ERROR: TIMESTAMP WITHOUT TIME ZONE doesn't accept timezone-aware values
```

**Fix Applied:**
```python
# FIXED
user.last_login = datetime.utcnow()  # naive datetime (no timezone info)
# WORKS: TIMESTAMP WITHOUT TIME ZONE accepts naive datetimes
```

**Verification:**
```bash
# Test login endpoint
curl -X POST http://192.168.2.186:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}'

# Expected: {"access_token": "...", "refresh_token": "...", ...}
# Status: ✅ WORKS
```

**Files Modified:**
- `backend/app/api/v1/endpoints/auth.py` (line 160)

**Commit:** `e498925`

---

### Issue #2: CORS Blocking All API Calls from Frontend

**Status:** ✅ FIXED (Commits: 271e62c, 8e8eeec)

**Symptom:**
```
Frontend (192.168.2.186:3000) tries to call API (192.168.2.186:8000)
Response: CORS error
Access-Control-Allow-Origin missing or incorrect
All API calls fail silently
```

**Root Cause:**
File: `docker-compose.yml:85`
```yaml
# BROKEN - INDENTATION ERROR
environment:
- CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://192.168.2.186:3000
  - CORS_ORIGINS=http://192.168.2.186:3000    # EXTRA INDENT - not parsed by shell!
```

The extra spaces before the second CORS_ORIGINS caused Docker to treat it as a separate line instead of YAML list item. The env var was never actually set in the container.

**Fix Applied:**
```yaml
# FIXED - CORRECT INDENTATION
environment:
- ENVIRONMENT=development
- DEBUG=true
- LOG_LEVEL=debug
- DATABASE_URL=postgresql+asyncpg://cloudplatform:cloudplatform_dev_password@postgres:5432/cloudplatform
- REDIS_URL=redis://:cloudplatform_redis_password@redis:6379/0
- CELERY_BROKER_URL=amqp://cloudplatform:cloudplatform_rabbit_password@rabbitmq:5672//
- CELERY_RESULT_BACKEND=redis://:cloudplatform_redis_password@redis:6379/1
- JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-min-32-chars
- CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://192.168.2.186:3000
```

All entries now consistent indentation, CORS_ORIGINS properly parsed.

**Verification:**
```bash
# After fix, frontend can call API
curl -X GET http://192.168.2.186:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# Expected: 200 OK, user profile returned
# Status: ✅ WORKS
```

**Files Modified:**
- `docker-compose.yml` (lines 85, 271e62c to add 192.168.2.186:3000, then 8e8eeec to fix indentation)

**Commits:** `271e62c`, `8e8eeec`

---

### Issue #3: Frontend Environment Variable Not Set

**Status:** ✅ FIXED (Commits: da62458, ff14714)

**Symptom:**
```
Frontend starts, but VITE_API_URL is undefined
console.log: "API URL is: undefined"
API calls to /api/v1 fail (hit wrong endpoint)
```

**Root Cause:**
File: `frontend/src/stores/configStore.ts`
```typescript
// BROKEN
const apiUrl = import.meta.env.VITE_API_URL;  // undefined (not set in container)
```

The Dockerfile.dev was complex with entrypoint.sh script that never properly set the env var before Vite started.

**Fix Applied:**
Multiple attempts, final solution: Set ENV directly in Dockerfile.dev and use CMD

File: `frontend/Dockerfile.dev`
```dockerfile
# BROKEN (old approach)
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

# FIXED (new approach)
ENV VITE_API_URL=http://192.168.2.186:8000/api/v1
CMD ["npm", "run", "dev"]
```

This ensures the environment variable is set before `npm run dev` starts the Vite dev server.

**Verification:**
```bash
# Inside frontend container
echo $VITE_API_URL
# Output: http://192.168.2.186:8000/api/v1

# In browser console
console.log(import.meta.env.VITE_API_URL)
# Output: "http://192.168.2.186:8000/api/v1"
```

**Files Modified:**
- `frontend/Dockerfile.dev` (removed entrypoint.sh approach, added ENV + CMD)
- `frontend/src/stores/configStore.ts` (already using import.meta.env correctly)

**Commits:** `da62458`, `ff14714`, and cleanup commits

---

### Issue #4: Frontend Referencing Non-existent Pages

**Status:** ✅ FIXED (Commit: dc49ce5)

**Symptom:**
```
Frontend starts but shows error in browser console:
"Cannot find module 'pages/RegisterPage'"
"Cannot find module 'pages/AdminUsersPage'"
... 15+ missing pages

App crashes or shows blank screen
Navigation broken for non-existent routes
```

**Root Cause:**
File: `frontend/src/App.tsx`

Batch 2 code added imports and routes for ~15 admin pages that don't exist in Phase 1:
```typescript
// BROKEN - references pages that don't exist
import RegisterPage from 'pages/RegisterPage';
import AdminUsersPage from 'pages/AdminUsersPage';
import AdminOrganizationsPage from 'pages/AdminOrganizationsPage';
// ... + 12 more missing pages

<Route path="/register" element={<RegisterPage />} />
<Route path="/admin/users" element={<AdminUsersPage />} />
// ... all broken routes
```

**Fix Applied:**
File: `frontend/src/App.tsx` (Commit: dc49ce5)

Removed all references to Phase 8+ admin pages. Kept only pages that exist in Phase 1:
- ClusterDetailPage (from Batch 2)
- ClusterListPage
- DashboardPage
- Other Phase 0/1 pages

```typescript
// FIXED - only routes to existing pages
<Route path="/clusters" element={<ClusterListPage />} />
<Route path="/clusters/:clusterId" element={<ClusterDetailPage />} />
<Route path="/dashboard" element={<DashboardPage />} />
// No admin routes yet
```

**Verification:**
```bash
# Frontend builds without errors
docker logs cloudplatform-frontend | grep -i error
# No "Cannot find module" errors

# App loads in browser
curl http://192.168.2.186:3000
# Status: 200 OK, HTML served
```

**Files Modified:**
- `frontend/src/App.tsx` (removed 15+ missing page imports)

**Commit:** `dc49ce5`

---

## INFRASTRUCTURE SETUP (Required for Cluster Integration)

### Issue #5: Admin User Not Superadmin

**Status:** ✅ FIXED (Manual DB update)

**Symptom:**
```
User created via /api/v1/auth/register has is_superadmin=false
Cannot call /api/v1/clusters (requires superadmin)
Cluster registration blocked
```

**Root Cause:**
User registration endpoint creates `is_superadmin=false` by default. There's no admin initialization endpoint to promote users.

**Fix Applied:**
Direct database update on PostgreSQL:
```bash
# SSH to vm103, execute in cloudplatform-postgres container
docker exec cloudplatform-postgres psql -U cloudplatform -d cloudplatform \
  -c "UPDATE users SET is_superadmin=true WHERE email='admin@example.org';"
```

Result:
```
UPDATE 1
 email       | is_superadmin 
 admin@example.org | t
```

**Verification:**
```bash
curl http://192.168.2.186:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" | jq .is_superadmin
# Output: true
```

**Documentation:** See `ADMIN_SETUP.md` for complete procedure (manual + automated)

**Status:** ✅ DOCUMENTED, ready for future deployments

---

### Issue #6: Proxmox API Credentials Missing

**Status:** ✅ FIXED (Created API token, stored in .env)

**Symptom:**
```
Cannot register Proxmox clusters in app
No API credentials available
Cluster integration unavailable
```

**Fix Applied:**
Created API token on Proxmox cluster (pve2, root@pam):

```bash
# Create user
pveum user add cloudforproxmox@pve --comment 'Cloud For Proxmox API User'

# Grant admin role
pveum acl modify / -user cloudforproxmox@pve -role Administrator

# Create token (non-expiring)
pveum user token add cloudforproxmox@pve cloudforproxmox-token --expire 0
```

Output:
```
full-tokenid: cloudforproxmox@pve!cloudforproxmox-token
value:        c945da6d-8095-45aa-b0a7-f74c7557ec8a
```

Saved to `.env`:
```bash
PROXMOX_API_USER=cloudforproxmox@pve
PROXMOX_API_TOKEN_ID=cloudforproxmox@pve!cloudforproxmox-token
PROXMOX_API_TOKEN_SECRET=c945da6d-8095-45aa-b0a7-f74c7557ec8a
```

**Verification:**
```bash
# Test token directly
curl -k https://192.168.2.22:8006/api2/json/version \
  -H "Authorization: PVEAPIToken=cloudforproxmox@pve!cloudforproxmox-token=c945da6d-8095-45aa-b0a7-f74c7557ec8a"
# Returns: {"data": {"version": "9.1.5", ...}}
```

**Clusters Registered:**
- pve1-cluster: https://192.168.2.21:8006 ✅ Active
- pve2-cluster: https://192.168.2.22:8006 ✅ Active

Both synced successfully (2 nodes each, 0 VMs added).

**Documentation:** See `ADMIN_SETUP.md` for complete procedure

---

## DEPLOYMENT CHECKLIST FOR FUTURE VMs

Use this checklist to ensure working deployments:

```markdown
## Pre-Deployment
- [ ] DNS/network: vm103 (or target) can reach 192.168.2.0/24
- [ ] Docker: docker-compose.yml correctly indented (validate with `yamllint`)
- [ ] Credentials: .env populated with ADMIN_PASSWORD, PROXMOX_API_TOKEN_SECRET

## During Deployment
- [ ] docker-compose up completes without errors
- [ ] Check: `docker-compose ps` — all containers healthy
- [ ] Check: `/api/v1/health` returns 200 OK

## Post-Deployment (Required Steps)
1. [ ] Create test user via POST /api/v1/auth/register
2. [ ] Promote admin user to superadmin:
   ```bash
   docker exec cloudplatform-postgres psql -U cloudplatform -d cloudplatform \
     -c "UPDATE users SET is_superadmin=true WHERE email='admin@example.org';"
   ```
3. [ ] Test login: POST /api/v1/auth/login
4. [ ] Verify superadmin: GET /api/v1/users/me (check is_superadmin=true)
5. [ ] Register Proxmox clusters:
   ```bash
   POST /api/v1/clusters with credentials from .env
   ```
6. [ ] Sync VMs: POST /api/v1/clusters/{id}/sync-vms
7. [ ] Test UI: http://192.168.2.186:3000, login, navigate

## Validation
- [ ] Frontend loads without errors
- [ ] API calls work (no CORS errors)
- [ ] Login functional
- [ ] Clusters registered and synced
```

---

## KNOWN LIMITATIONS (Phase 1 Batch 2)

These are deferred to Phase 8+. See `PHASE1_BATCH2_TECHNICAL_GAPS.md` for details:

1. **Firewall operations are stubs** — POST/PATCH/DELETE firewall rules don't persist to Proxmox
2. **Audit trail missing** — create/delete VM ops not logged (table doesn't exist)
3. **Power state not auto-synced** — Celery worker not running, manual refresh required
4. **Celery workers don't start** — Task imports broken, but Phase 1 doesn't need them

**Workarounds exist for all**. See linked doc for details.

---

## Files Changed Summary

| File | Changes | Commit |
|------|---------|--------|
| `backend/app/api/v1/endpoints/auth.py` | Line 160: datetime.utcnow() instead of datetime.now(timezone.utc) | e498925 |
| `docker-compose.yml` | CORS_ORIGINS fix (indentation + add 192.168.2.186:3000) | 271e62c, 8e8eeec |
| `frontend/Dockerfile.dev` | Set ENV VITE_API_URL, use CMD instead of entrypoint | ff14714 |
| `frontend/src/App.tsx` | Remove 15+ non-existent admin page routes | dc49ce5 |
| `.env` | Add PROXMOX_API_* credentials | (new, not committed to prevent secrets) |
| `ADMIN_SETUP.md` | Created comprehensive admin setup guide | (new) |

---

## Testing Performed

### Functional Tests (vm103)
- ✅ Login: admin@example.org / superadmin
- ✅ Dashboard loads
- ✅ Cluster list shows 2 clusters (pve1, pve2)
- ✅ VM sync succeeds (0 VMs in test environment)
- ✅ Navigation works (ClusterDetailPage accessible)

### API Tests
- ✅ GET /api/v1/health — 200 OK
- ✅ POST /api/v1/auth/login — 200 OK, token returned
- ✅ GET /api/v1/users/me — 200 OK, user details returned
- ✅ POST /api/v1/clusters — 201 Created, both clusters registered
- ✅ POST /api/v1/clusters/{id}/sync-vms — 200 OK, 2 nodes scanned

### Frontend Tests (Browser)
- ✅ http://192.168.2.186:3000 loads
- ✅ Login page displays
- ✅ Login succeeds, redirects to dashboard
- ✅ Dashboard renders (clusters visible)
- ✅ No console errors

---

## Next Steps

1. **Create snapshot:** `phase-1-batch-2-final` on vm103
2. **Prepare Phase 2 deployment:** Merge any remaining fixes, test on snapshot
3. **Document Phase 8 migration:** When replacing stubs with real implementations
4. **Team onboarding:** Provide teams with ADMIN_SETUP.md and this document

---

**Status:** ✅ Phase 1 Batch 2 deployment is WORKING and DOCUMENTED
