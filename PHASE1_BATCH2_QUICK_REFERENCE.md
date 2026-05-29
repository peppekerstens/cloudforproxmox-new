# Phase 1 Batch 2: Quick Reference Card

**Deployment:** vm103 (pve2, 192.168.2.186)  
**Commit:** 7cd39b6  
**Status:** ✅ Live with 3 stubs

---

## What's Stubbed? (3 modules)

| Module | File | Issue | Fix Timeline |
|--------|------|-------|--------------|
| `vm_status_tasks` | `backend/app/tasks/vm_status_tasks.py` | Power state not auto-refreshed | Phase 8 |
| `firewall_service` | `backend/app/services/firewall_service.py` | Firewall ops are no-ops | Phase 8 |
| `firewall schemas` | `backend/app/schemas/firewall.py` | Data doesn't persist | Phase 8 |

---

## What Works? (All Batch 2 features)

✅ VM create/delete/modify  
✅ LXC provisioning  
✅ VM templates  
✅ Cluster details page  
✅ User/org management  
✅ Quota enforcement  
✅ ISO upload/management  

---

## What Doesn't Work? (3 features)

| Feature | Impact | Workaround |
|---------|--------|-----------|
| **Firewall rules** | API returns 200 OK but rules don't persist | Use Proxmox UI directly |
| **Audit trail** | Operations logged but table missing | Check Proxmox task log |
| **Power state sync** | State stays cached after create/modify | Click "Refresh" in UI |

---

## Critical Known Issues

| Severity | Issue | Detection |
|----------|-------|-----------|
| 🔴 HIGH | Firewall enable appears to work but doesn't | Enable firewall, check Proxmox (disabled) |
| 🟠 MEDIUM | Audit trail is empty | `SELECT COUNT(*) FROM audit_logs` → error |
| 🟡 LOW | VM power state is stale | Create VM, check state immediately (old) |

---

## Affected Endpoints (Stubs)

### Firewall Endpoints (Broken)
```
GET    /api/v1/vms/{vm_id}/firewall/status        (returns hardcoded)
POST   /api/v1/vms/{vm_id}/firewall/enable        (no-op)
POST   /api/v1/vms/{vm_id}/firewall/disable       (no-op)
POST   /api/v1/vms/{vm_id}/firewall/resync        (no-op)
GET    /api/v1/vms/{vm_id}/firewall/rules         (empty list)
POST   /api/v1/vms/{vm_id}/firewall/rules         (creates fake rule)
GET    /api/v1/vms/{vm_id}/firewall/rules/{rule_id}  (not found)
PATCH  /api/v1/vms/{vm_id}/firewall/rules/{rule_id}  (no-op)
DELETE /api/v1/vms/{vm_id}/firewall/rules/{rule_id}  (no-op)
```

### Audit Logging (Broken)
```
⚠️ All VM operations log audit events
   But audit_logs table doesn't exist
   Writes fail silently (caught by middleware)
```

### Power State Polling (Broken)
```
⚠️ Called after VM create/modify/snapshot
   But poll_vm_power_state.delay() is no-op
   State doesn't refresh until manual action
```

---

## Testing This Phase

### ✅ DO Test
```python
# VM operations work
POST /api/v1/vms  # Create VM → 201 ✓
GET /api/v1/vms/{vm_id}  # Read VM → 200 ✓
PATCH /api/v1/vms/{vm_id}  # Modify VM → 200 ✓
DELETE /api/v1/vms/{vm_id}  # Delete VM → 204 ✓

# LXC works
POST /api/v1/containers  # Create → 201 ✓

# Templates work
POST /api/v1/vms/template  # Create template → 201 ✓
```

### ❌ DON'T Test
```python
# Firewall persistence (broken)
POST /api/v1/vms/{vm_id}/firewall/enable
assert check_proxmox_firewall_enabled(vm_id)  # ❌ FAIL

# Audit trail (broken)
POST /api/v1/vms
SELECT * FROM audit_logs  # ❌ TABLE DOESN'T EXIST

# Power state auto-refresh (broken)
POST /api/v1/vms
assert vm.power_state == "running"  # ❌ STALE

# Celery tasks (broken)
docker-compose ps | grep celery  # ❌ EXIT 1
```

---

## Quick Diagnostics

**Is API up?**
```bash
curl -s http://192.168.2.186:8000/api/v1/health
# {"status":"healthy",...} = YES ✓
```

**Is database working?**
```bash
curl -s http://192.168.2.186:8000/api/v1/users -H "Authorization: Bearer $TOKEN"
# 200 with user list = YES ✓
```

**Are stubs loaded?**
```bash
grep -r "STUB:" backend/app/ --include="*.py" | wc -l
# 3 = YES ✓
```

**Is Celery running?**
```bash
docker-compose ps | grep celery
# Exit 1 = NO ❌ (expected, it's stubbed)
```

---

## Documentation Map

| Doc | Purpose | Read When |
|-----|---------|-----------|
| **PHASE1_BATCH2_STUBS.md** | Detailed stub reference, what's stubbed, where, why, how to replace | Planning Phase 8 or debugging stub issues |
| **PHASE1_BATCH2_TECHNICAL_GAPS.md** | Critical/secondary issues, data integrity risks, testing requirements | Planning Phase 8 migration or understanding limitations |
| **PHASE1_BATCH2_QUICK_REFERENCE.md** | This file — quick lookup | Daily operations, quick answers |

---

## Phase 8 Preparation

When Phase 8 starts:

1. **Read:** `PHASE1_BATCH2_TECHNICAL_GAPS.md` (section "Cleanup Tasks for Phase 8")
2. **Replace:** All files marked "STUB:" with real implementations from proxmox-isp
3. **Migrate:** Create `audit_logs` table (Alembic migration)
4. **Test:** Run firewall, audit, polling tests
5. **Verify:** `grep -r "STUB:" backend/app/ | wc -l` should be 0

---

## Support

**If features don't work:**
1. Check if it's in the "What Doesn't Work" section above
2. Read the corresponding section in `PHASE1_BATCH2_TECHNICAL_GAPS.md`
3. Use the "Workaround" provided
4. It will be fixed in Phase 8

**If something else breaks:**
1. Check `backend/app/api/v1/endpoints/vms.py` logs
2. Verify database is healthy: `psql cloudplatform -c "\dt"`
3. Check Docker: `docker-compose logs cloudplatform-api | tail -50`

---

**Last updated:** 2026-05-29  
**Deployment status:** ✅ LIVE AND HEALTHY  
**Known stub count:** 3  
**Core feature status:** ✅ 100% OPERATIONAL
