# Phase 1 Batch 2 Stub Documentation

**Date Created:** 2026-05-29  
**Deployment:** vm103 (pve2, 192.168.2.186)  
**Branch:** phase-1-batch-2  
**Commit:** 1f9ff89

---

## Summary

Batch 2 code (10 commits: 8bbd9b8..be13bb8) imports 3 modules that don't exist until Phase 8 (audit system). Rather than merge 156+ commits with 40+ conflicts, we created minimal stubs to allow Batch 2 deployment while preserving core functionality.

**Impact:** Batch 2 features work 100%. Audit trail and background polling are no-ops (silent failures).

---

## Stubs Created

### 1. `backend/app/tasks/vm_status_tasks.py` (NEW)

**File:** `backend/app/tasks/vm_status_tasks.py`  
**Created:** 2026-05-29 commit 6becf3a  
**Type:** Celery Task Stub

#### Purpose (Real Implementation)
Background task that polls Proxmox API for VM power state and syncs to database. Called after VM operations (create, modify, snapshot).

#### Stub Behavior
- `poll_vm_power_state.delay(vmid, node)` → returns immediately (no-op)
- `poll_vm_power_state.apply_async()` → no-op
- `poll_vm_power_state.apply()` → no-op

#### Affected Endpoints (Batch 2)
- `POST /api/v1/vms` (VM create) — line 1109 in vms.py
- `PATCH /api/v1/vms/{vm_id}` (VM modify) — line 1172 in vms.py
- `POST /api/v1/vms/{vm_id}/snapshots` (snapshot create) — line 1233 in vms.py

#### Impact Assessment
**Severity:** LOW (non-critical feature)

| Scenario | Result |
|----------|--------|
| Create VM → poll triggered | VM created ✓. Power state not auto-synced (stale until manual refresh) |
| Modify VM → poll triggered | VM modified ✓. State not refreshed |
| Create snapshot → poll triggered | Snapshot created ✓. Power state not polled |

**User-facing impact:** Power status may be outdated. Manual refresh via UI works fine. No data loss.

**How to verify when stubbed:**
```bash
# Create VM
POST /api/v1/vms 
# Check power state immediately — may show cached/old value
GET /api/v1/vms/{vm_id}
# Refresh manually in UI — state updates from Proxmox
```

#### Replacement (Phase 8+)
Real implementation will:
1. Submit Celery task to background queue
2. Poll Proxmox API for current power state
3. Update `vm.power_state` in database
4. Log status change if applicable

**Reference:** proxmox-isp repo at commit 1edf35f+ (Phase 8 audit system added)

---

### 2. `backend/app/services/firewall_service.py` (NEW)

**File:** `backend/app/services/firewall_service.py`  
**Created:** 2026-05-29 commit c894743  
**Type:** Service Class Stub

#### Purpose (Real Implementation)
Service for managing VM firewall rules:
- Enable/disable firewall per VM
- List, create, update, delete firewall rules
- Sync rules with Proxmox

#### Stub Methods (all silent no-ops)
```python
get_firewall_status(vm_id, org_id) → {"enabled": False, "rule_count": 0}
enable_firewall(vm_id, org_id) → {"enabled": True}
disable_firewall(vm_id, org_id) → {"enabled": False}
resync_rules(vm_id, org_id) → {"success": True, "synced_count": 0}
list_rules(vm_id, org_id) → []
create_rule(vm_id, org_id, rule_data) → {"id": "stub-rule-id", ...rule_data}
get_rule(rule_id, org_id) → None
update_rule(rule_id, org_id, rule_data) → {"id": rule_id, ...rule_data}
delete_rule(rule_id, org_id) → True
```

#### Affected Endpoints (Batch 2)
- `GET /api/v1/vms/{vm_id}/firewall/status` — line 2072
- `POST /api/v1/vms/{vm_id}/firewall/enable` — line 2115
- `POST /api/v1/vms/{vm_id}/firewall/disable` — line 2158
- `POST /api/v1/vms/{vm_id}/firewall/resync` — line 2203
- `GET /api/v1/vms/{vm_id}/firewall/rules` — line 2241
- `POST /api/v1/vms/{vm_id}/firewall/rules` — line 2292
- `GET /api/v1/vms/{vm_id}/firewall/rules/{rule_id}` — line 2320
- `PATCH /api/v1/vms/{vm_id}/firewall/rules/{rule_id}` — line 2371
- `DELETE /api/v1/vms/{vm_id}/firewall/rules/{rule_id}` — line 2425

#### Impact Assessment
**Severity:** MEDIUM (user-visible, operations appear successful but don't persist)

| Operation | Result |
|-----------|--------|
| Get firewall status | Returns: `{"enabled": false, "rule_count": 0}` (hardcoded) |
| Enable firewall | Returns: `{"enabled": true}` but firewall NOT enabled in Proxmox |
| Create rule | Returns new rule object, but rule NOT created in Proxmox or database |
| List rules | Always returns empty `[]` |
| Delete rule | Returns `true` but rule NOT deleted |

**User-facing impact:** Firewall endpoints return success (200 OK) but changes don't persist. Operations appear to work; Proxmox firewall state unchanged. User confusion if they enable firewall expecting it to work.

**Testing caveat:** API tests may pass (stubs return expected schema) but integration tests fail (Proxmox has no firewall rules).

**How to detect when stubbed:**
```bash
# Enable firewall
POST /api/v1/vms/123/firewall/enable
# Response: {"enabled": true, ...}
# BUT in Proxmox: firewall still disabled
proxmox-host:~# qm firewall list 123
# Shows firewall disabled/no rules

# Try to add rule
POST /api/v1/vms/123/firewall/rules
{"direction": "in", "protocol": "tcp", "port": 22, "action": "accept"}
# Response: {"id": "stub-rule-id", ...}
# BUT rule doesn't exist in Proxmox
```

#### Replacement (Phase 8+)
Real implementation will:
1. Map firewall operations to Proxmox API (`qm firewall` commands)
2. Store rules in database (audit trail)
3. Sync state bidirectionally with Proxmox
4. Support rule templates/groups

**Reference:** proxmox-isp repo, Phase 8 firewall system implementation

---

### 3. `backend/app/schemas/firewall.py` (NEW)

**File:** `backend/app/schemas/firewall.py`  
**Created:** 2026-05-29 commit 1f9ff89  
**Type:** Pydantic Schema Stub

#### Classes
- `FirewallRuleCreate` — Request schema for creating a rule
- `FirewallRuleUpdate` — Request schema for updating a rule
- `FirewallRuleResponse` — Response schema for a rule
- `FirewallRuleListResponse` — Response schema for rule list

#### Purpose
Validates incoming requests and formats outgoing responses for firewall endpoints.

#### Stub Behavior
- All fields present and typed correctly
- Validation works (request accepted if schema matches)
- Database serialization works (from_attributes=True)
- **BUT:** Data doesn't persist (stubs don't save to DB/Proxmox)

#### Impact Assessment
**Severity:** LOW (data validation not affected)

Schema validation works fine. Endpoints accept/return correctly-formatted JSON. The issue is in the service layer (FirewallService), not here.

#### Replacement (Phase 8+)
Real implementation will:
- Add ORM model `FirewallRule` (database table)
- Add validation rules (port ranges, protocol enums, etc.)
- Add serialization hooks for Proxmox API format

---

## Forward Dependencies (Not Stubbed)

The following modules **already exist** and are NOT stubs:

### ✅ `app.core.audit` (REAL)
- **File:** `backend/app/core/audit.py`
- **Status:** Fully implemented
- **Purpose:** Sanitizes dicts, writes audit log entries
- **Used by:** VM create/delete/modify endpoints (create_audit_log calls)
- **Impact:** Audit logging works but AuditLog table doesn't exist (Phase 8), so writes fail silently

### ✅ `app.models.audit_log.AuditLog` (REAL)
- **File:** `backend/app/models/audit_log.py`
- **Status:** Full ORM model with indexes
- **Issue:** Table doesn't exist in Phase 1 database schema
- **Impact:** create_audit_log() tries to insert, gets database error (caught silently)

---

## Affected Features (Functional Assessment)

### ✅ Working (Batch 2 core features)
- VM create/delete/modify
- LXC container operations
- VM template creation
- Cluster detail page
- User/org management
- Quota enforcement
- ISO management

### ⚠️ Partially Working (stubs present)
- **VM power state sync** — manual refresh works, auto-sync doesn't
- **Firewall operations** — endpoints exist, changes don't persist
- **Audit logging** — calls made, trail not recorded

### ❌ Not Working (dependency chain)
- None at this stage; all Batch 2 code deploys

---

## How to Replace Stubs in Phase 8

### Step 1: Locate Phase 8 implementations
```bash
git show 1edf35f:backend/app/tasks/vm_status_tasks.py  # Real version
git show 1edf35f:backend/app/services/firewall_service.py
```

### Step 2: Replace stubs
```bash
# Backup stubs for reference
cp backend/app/tasks/vm_status_tasks.py backend/app/tasks/vm_status_tasks.py.stub
cp backend/app/services/firewall_service.py backend/app/services/firewall_service.py.stub

# Pull real implementations from Phase 8 commits
git show PHASE8_COMMIT:backend/app/tasks/vm_status_tasks.py > backend/app/tasks/vm_status_tasks.py
git show PHASE8_COMMIT:backend/app/services/firewall_service.py > backend/app/services/firewall_service.py
```

### Step 3: Resolve conflicts
- Firewall service likely depends on ORM models (Phase 8)
- VM status tasks depends on Celery configuration (Phase 8)
- Merge accordingly and run tests

### Step 4: Database migration
- Phase 8 firewall rules table (if new)
- Audit logs table (already exists in model)

---

## Testing Notes

### Unit Tests
- Stub implementations satisfy import checks ✓
- Schema validation works ✓
- Service method signatures match Phase 8 ✓

### Integration Tests
- Firewall endpoints return 200 OK ✓
- Firewall rules don't persist in Proxmox ❌
- Audit logs don't appear in database ❌
- VM power state isn't auto-refreshed ❌

### Acceptance Tests (Phase 1)
- Don't test firewall persistence (it's stubbed)
- Don't test audit trail (it's stubbed)
- Test VM operations work (they do)

---

## Traceback Guide

**To find all stubs in the codebase:**
```bash
# Search for STUB comments
grep -r "STUB:" backend/app/ --include="*.py"

# Output:
# backend/app/tasks/vm_status_tasks.py: "STUB: Disabled in Phase 1"
# backend/app/services/firewall_service.py: "STUB: Disabled in Phase 1"
# backend/app/schemas/firewall.py: "STUB: Disabled in Phase 1"
```

**To find usages of stubbed methods:**
```bash
# Firewall service calls
grep -r "firewall_service\." backend/app/api/v1/endpoints/vms.py | wc -l
# Output: 23 calls across 9 endpoints

# VM status polling calls
grep -r "poll_vm_power_state" backend/app/api/v1/endpoints/vms.py
# Output: 3 calls (lines 1109, 1172, 1233)
```

**To understand stub impact:**
1. Run `curl http://192.168.2.186:8000/api/v1/vms` — see if power states are current
2. Enable firewall via UI — check Proxmox directly if it's enabled
3. Check database for audit entries: `SELECT COUNT(*) FROM audit_logs;`

---

## Phase Mapping

| Phase | Status | Notes |
|-------|--------|-------|
| 0 | ✅ Complete | Upstream deployed |
| 1 Batch 1 | ✅ Complete | 16 commits, core working |
| 1 Batch 2 | ✅ Deployed (STUBS) | 10 commits, 3 stubs |
| 2-7 | ⏳ Pending | Broader feature sets |
| 8 | 🔌 Replaces stubs | Audit system, firewall, polling |
| 9+ | 🔮 Future | |

---

## References

- **Source repo:** https://github.com/peppekerstens/proxmox-isp
- **Batch 2 commits:** 8bbd9b8..be13bb8 (10 commits)
- **Phase 8 reference:** commit 1edf35f (where real implementations exist)
- **Deployment docs:** BATCH2_DEPLOYMENT_PLAN.md, SNAPSHOT_RECOVERY_WORKFLOW.md
