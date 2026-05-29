# Phase 1 Batch 2: Technical Gaps & What Needs Fixing

**Deployment Date:** 2026-05-29  
**Status:** Live on vm103 with stubs  
**Last Updated:** 1f9ff89

---

## Executive Summary

Batch 2 deploys successfully with 3 stubbed modules. **Core VM/LXC operations work.** Audit trail and firewall persistence are missing. This document tracks what's broken and what needs fixing in later phases.

---

## Critical Issues (Need Immediate Fix)

### ❌ Issue #1: Firewall Operations Are No-ops

**Severity:** 🔴 HIGH (user-visible, data-loss risk)

**What's broken:**
```
User tries to enable firewall → API returns 200 OK
Firewall is NOT enabled in Proxmox
User assumes it's enabled → security misconfiguration
```

**Root cause:** `FirewallService` methods are stubbed, don't call Proxmox API

**Affected endpoints:**
- `POST /api/v1/vms/{vm_id}/firewall/enable`
- `POST /api/v1/vms/{vm_id}/firewall/disable`
- `POST /api/v1/vms/{vm_id}/firewall/rules` (create rule)
- `PATCH /api/v1/vms/{vm_id}/firewall/rules/{rule_id}` (update rule)
- `DELETE /api/v1/vms/{vm_id}/firewall/rules/{rule_id}` (delete rule)

**Workaround (Phase 1):**
- Configure firewall directly in Proxmox
- Don't use Batch 2 firewall API endpoints
- Document: "Firewall management unavailable in Phase 1"

**Fix (Phase 8+):**
- Replace `backend/app/services/firewall_service.py` with real implementation
- Implement Proxmox `qm firewall` command mapping
- Add FirewallRule ORM model (if not exists)
- Add database schema migration
- Test against Proxmox directly

**Verification test:**
```python
# Test stub vs real
vm_id = "123"

# Stub (current):
response = POST /api/v1/vms/{vm_id}/firewall/enable
assert response.status_code == 200
assert response.json()["enabled"] == true
# BUT firewall is disabled in Proxmox (BUG)

# Real (Phase 8):
# Proxmox firewall should be enabled
proxmox_status = check_proxmox_firewall(vm_id)
assert proxmox_status["enabled"] == true
```

---

### ❌ Issue #2: Audit Trail Missing

**Severity:** 🟠 MEDIUM (compliance/ops issue)

**What's broken:**
```
VM create/delete/modify → create_audit_log() called
But AuditLog table doesn't exist → silent failure
No audit trail recorded
```

**Root cause:** 
- `AuditLog` ORM model exists (code) but table not in Phase 1 schema
- Database migration missing
- Writes fail silently (caught by exception handler)

**Affected operations:**
- VM creation (line 487 in vms.py)
- VM deletion (line 1051)
- VM modification (line 1439)
- Implicit: cluster changes, quota changes (future endpoints)

**Impact:**
- No compliance audit trail for critical operations
- Cannot trace who changed what when
- Audit logs table exists in ORM (Phase 8+) but not accessible in Phase 1

**Workaround (Phase 1):**
- Use Proxmox task log for VM operations audit
- Use PostgreSQL transaction log for schema changes
- Document: "Audit trail deferred to Phase 8"

**Fix (Phase 8):**
- Run Alembic migration to create `audit_logs` table
- Ensure schema matches `AuditLog` ORM model
- Verify indexes are created (org_id, user_id, action, created_at)
- Test create_audit_log() inserts successfully

**Verification test:**
```python
# Stub (current):
POST /api/v1/vms
vm = response.json()

# Check audit table (should be empty or error)
SELECT COUNT(*) FROM audit_logs WHERE resource_id = vm['id'];
# Returns: 0 or ERROR (table doesn't exist)

# Real (Phase 8):
# Should see audit entry
SELECT * FROM audit_logs WHERE resource_id = vm['id'] AND action = 'vm.created';
# Returns: 1 row with user_id, org_id, timestamp, before_state, after_state
```

---

### ❌ Issue #3: VM Power State Not Auto-synced

**Severity:** 🟡 LOW-MEDIUM (UX degradation)

**What's broken:**
```
Create VM → Poll trigger called → poll_vm_power_state.delay() is no-op
Power state stays cached/stale
User sees "Unknown" until manual refresh
```

**Root cause:** `poll_vm_power_state` task is stubbed, Celery doesn't execute

**Affected endpoints:**
- `POST /api/v1/vms` — after creation (line 1109)
- `PATCH /api/v1/vms/{vm_id}` — after modification (line 1172)
- `POST /api/v1/vms/{vm_id}/snapshots` — after snapshot create (line 1233)

**Impact:**
- UI shows stale power state after VM operations
- Manual refresh works (fetches from Proxmox)
- Core functionality unaffected (VM is created/modified correctly)
- Database state correct, just not auto-refreshed

**Workaround (Phase 1):**
- Document: Users must manually refresh power state
- Click "Refresh" button in UI after VM operations
- Polling will auto-update if user waits/navigates

**Fix (Phase 8+):**
- Replace `backend/app/tasks/vm_status_tasks.py` with real Celery task
- Implement Proxmox API polling: `GET /api2/json/nodes/{node}/qemu/{vmid}/status/current`
- Update database: `vm.power_state = response['data']['status']`
- Ensure Redis is configured for task queue
- Test with Celery: `celery -A app.tasks.celery_app worker`

**Verification test:**
```bash
# Stub (current):
curl -X POST http://192.168.2.186:8000/api/v1/vms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-vm",
    "node": "pve2",
    "ram": 2048
  }'

# Check power state immediately
curl http://192.168.2.186:8000/api/v1/vms/new-vm-id
# Returns: {"power_state": "unknown"} or cached value

# Wait 30 sec for auto-poll (stub: nothing happens)
curl http://192.168.2.186:8000/api/v1/vms/new-vm-id
# Still returns old value

# Manual refresh works
POST /api/v1/vms/new-vm-id/refresh-state
# Returns: {"power_state": "running"} ✓
```

---

## Secondary Issues (Workarounds Exist)

### ⚠️ Issue #4: Celery Workers Not Starting

**Severity:** 🟡 LOW (tasks don't run, but app doesn't need them yet)

**What's broken:**
```
$ docker-compose ps | grep celery
cloudplatform-celery-worker  Exit 1
cloudplatform-celery-beat    Exit 1
cloudplatform-flower         Exit 1
```

**Root cause:** Celery task imports broken (stubs + missing modules), workers can't start

**Impact:**
- Background tasks don't run (acceptable, we have stubs)
- Celery UI (Flower) unavailable
- Phase 1 doesn't need background tasks yet

**Workaround (Phase 1):**
- It's OK — Phase 1 doesn't use background tasks
- Ignore Celery worker errors in logs
- Document: "Celery deferred to Phase 8"

**Fix (Phase 8):**
- Replace stub modules with real implementations
- Ensure all Celery task imports resolve
- Run workers: `celery -A app.tasks.celery_app worker`
- Monitor with Flower: `http://192.168.2.186:5555`

**Verification test:**
```bash
# Check worker status (Phase 8)
docker-compose logs celery-worker | tail -20
# Should show: "mingle: connected to broker!", not "ModuleNotFoundError"

# Test task execution
celery -A app.tasks.celery_app inspect active
# Returns: {'worker1': {'active': {...}}}
```

---

### ⚠️ Issue #5: Audit Log Writes Fail Silently

**Severity:** 🟡 MEDIUM (hidden failures)

**What's broken:**
```
create_audit_log(db, action="vm.created", ...) called
Inside function: db.add(AuditLog(...)) succeeds in memory
db.commit() fails → ERROR: relation "audit_logs" does not exist
Exception caught by middleware → silent failure, request continues
```

**Root cause:** No database migration, table doesn't exist

**Evidence:**
```
# Check database schema
psql cloudplatform -c "\dt"
# Output: No audit_logs table

# Check ORM model
cat backend/app/models/__init__.py
# Imports: AuditLog (model exists in code, but no table)
```

**Impact:**
- VM operations appear to succeed (from user's perspective)
- Audit trail is empty (from ops/compliance perspective)
- No error thrown to user (silent)
- Developers might not notice until Phase 8

**Workaround (Phase 1):**
- Catch exceptions in `create_audit_log()` and log them
- Add try/except in vms.py endpoints
- Document: "Audit logging disabled pending Phase 8"

**Fix (Phase 8):**
```bash
# Create migration
alembic revision --autogenerate -m "Add audit_logs table"

# Review generated migration
# Check: columns, indexes, constraints match AuditLog ORM model

# Apply migration
alembic upgrade head

# Verify
psql cloudplatform -c "\dt audit_logs"
# Output: Should show table with proper columns/indexes
```

---

### ⚠️ Issue #6: Firewall Schemas Don't Match Service

**Severity:** 🟡 LOW (data validation OK, persistence broken)

**What's broken:**
```
Request: POST /api/v1/vms/123/firewall/rules
Body: {
  "direction": "in",
  "protocol": "tcp",
  "port": 22,
  "action": "accept"
}

Schema validation: PASS ✓
Service call: FirewallService.create_rule() → Returns mock object
Persistence: FAIL ❌ (stub doesn't save)
```

**Root cause:** Schema validates fine, but service is stub

**Impact:**
- API accepts valid firewall rules
- Rules don't persist to database or Proxmox
- User sees rule in list after creation (mocked response) but it's not real

**Workaround (Phase 1):**
- Document: Firewall endpoints not functional
- Don't test with real firewall data

**Fix (Phase 8+):**
- Ensure `FirewallRuleResponse` schema matches ORM model fields
- Update schemas to include `created_at`, `updated_at` if needed
- Validate port ranges, protocol enums
- Add custom validators (CIDR validation, etc.)

---

## Data Integrity Concerns

### 🔴 Risk: Firewall Changes Lost

**Scenario:**
```
1. User enables firewall via UI
2. System returns success (stubs don't know better)
3. User thinks firewall is on
4. But Proxmox firewall is off → VM is unprotected
```

**Mitigation (Phase 1):**
- Add UI warning: "Firewall management deferred to Phase 8"
- Disable firewall endpoints in API routes (comment out or return 501 Not Implemented)
- Force users to configure firewall directly in Proxmox

**Fix (Phase 8):**
- Implement real FirewallService with Proxmox API calls
- Add transaction safety (rollback if Proxmox call fails)
- Add validation (rule conflicts, duplicate detection)

---

### 🟡 Risk: Audit Trail Gaps

**Scenario:**
```
1. User deletes sensitive VM
2. Audit log should record: who, when, what
3. But table doesn't exist → audit entry lost
4. Compliance audit fails later
```

**Mitigation (Phase 1):**
- Use Proxmox task log as backup audit source
- Export/document manual operations
- Document: "Full audit trail in Phase 8"

**Fix (Phase 8):**
- Create audit_logs table
- Ensure all critical operations log to audit
- Add retention policy (immutable, 7-year retention for compliance)

---

### 🟡 Risk: Stale Power State

**Scenario:**
```
1. Create VM → power_state cached as "stopped"
2. Proxmox starts VM in background
3. UI still shows "stopped" (stale cache)
4. User clicks start again → error
```

**Mitigation (Phase 1):**
- Document: Manual refresh needed after VM ops
- UI shows last-known state, not real-time

**Fix (Phase 8):**
- Implement auto-polling every 30 sec
- Real-time status via WebSocket (optional Phase 9+)

---

## Testing Requirements by Phase

### Phase 1 (Current, Stubs)
✅ Should test:
- VM create/delete/modify — core operations work
- LXC provisioning
- Schema validation
- API response formats

❌ Should NOT test:
- Firewall persistence (stub)
- Audit trail (table missing)
- Power state auto-sync (Celery broken)
- Celery tasks

### Phase 8+ (Real Implementation)
✅ Add tests:
- Firewall enable/disable actually changes Proxmox
- Create rule persists to database AND Proxmox
- Audit entry created for each operation
- Power state auto-syncs via Celery polling
- Celery workers start and execute tasks

---

## Cleanup Tasks for Phase 8

1. **Remove all stub markers** — grep for "STUB:" and replace real code
2. **Merge stub files with real implementations** — might have manual edits
3. **Run database migrations** — create audit_logs table
4. **Enable Celery workers** — fix import errors, start background tasks
5. **Test end-to-end** — firewall ops + audit trail + polling
6. **Update this doc** — mark issues as resolved

---

## Dependencies on Phase 8

This document assumes Phase 8 contains:

| Component | Status | File |
|-----------|--------|------|
| FirewallService (real) | 📦 In proxmox-isp | backend/app/services/firewall_service.py |
| VM status polling task | 📦 In proxmox-isp | backend/app/tasks/vm_status_tasks.py |
| Audit system | 📦 In proxmox-isp | backend/app/core/audit.py (real) |
| FirewallRule ORM | 📦 In proxmox-isp | backend/app/models/firewall.py (new) |
| Database migrations | ⏳ Need to extract | alembic/versions/*.py |

**Action:** When starting Phase 8, diff these components against proxmox-isp commit 1edf35f+ to ensure nothing is missed.

---

## Reference Commits

- **Stubs created:** 1f9ff89 (latest)
- **Batch 2 start:** 8bbd9b8
- **Batch 2 end:** be13bb8
- **Phase 8 reference:** 1edf35f (proxmox-isp repo)

---

## Questions for Phase 1 Users

If you encounter issues, check:

1. **Firewall not working?** → Stub. Use Proxmox UI.
2. **No audit trail?** → Stub. Check Proxmox task log.
3. **Power state stale?** → Stub. Click refresh.
4. **Celery workers crashing?** → Stub modules. Expected.

These will be fixed in Phase 8.
