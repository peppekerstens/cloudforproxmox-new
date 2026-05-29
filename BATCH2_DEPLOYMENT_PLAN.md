# Phase 1 Batch 2: Deployment Plan (Snapshot-Based)

**Status:** Ready for deployment  
**Date:** 2026-05-29  
**Default Target:** vm103 on pve2 (192.168.2.186) - DEFAULT DEV MACHINE  
**Temporary Target:** vm151 on pve1 (192.168.2.196) - TEMPORARY TEST MACHINE  
**Branch:** `cloudforproxmox-new/phase-1-batch-2`  
**Deployment Method:** Code update on existing working baseline

**VM USAGE RULES:**
- ✅ vm103 is my DEFAULT dev machine (deploy there without asking)
- ❌ vm151 is TEMPORARY (only deploy there if you explicitly say "test on vm151")

See VM_USAGE_POLICY.md for details.

---

## Strategy: Snapshot Recovery (NOT Full Redeploy)

Full VM deployments are complex and error-prone. **New strategy:** Use existing working VMs and their snapshots as baselines.

**Available Baselines:**
- **vm103** (pve2, 192.168.2.186): Phase 1 Batch 1 working snapshot `phase-1-batch-1-final` ← **DEFAULT**
- **vm151** (pve1, 192.168.2.196): Phase 1 Batch 1 working snapshot `phase-1-batch1-main-branch-working`

**Process:**
1. Update code: `git checkout phase-1-batch-2` (on vm103 or clone to temporary)
2. Restart containers: `docker-compose restart`
3. Test & verify (2-3 min)
4. Create snapshot (1 min)

This avoids 30-45 min of Ubuntu install + Docker setup + credential copy.

---

## Deployment Scenarios (When Instructed)

### Scenario A: Deploy to Default VM (vm103)

**When:** Default behavior, OR you say "deploy to vm103"  
**What I do:** Update code in-place on vm103, snapshot as `phase-1-batch-2-verified`

```bash
# SSH to vm103
ssh ubuntu@192.168.2.186

# Update code
cd ~/cloud-platform-upstream
git fetch origin
git checkout phase-1-batch-2

# Restart containers
docker-compose down
docker-compose up -d
docker-compose logs -f api

# Wait for containers to start (~2 min)
```

**Snapshot location:** `phase-1-batch-2-verified` on vm103

---

### Scenario B: Deploy to Temporary VM (vm151)

**When:** You explicitly say "test on temporary VM" or "deploy to vm151"  
**What I do:** Clone vm103 → vm151, update code, snapshot as `phase-1-batch-2-final`

```bash
# Step 1: Clone vm103 snapshot (on pve1)
qm clone 103 151 --name cloud-platform-batch2-temp --full

# Step 2: SSH to vm151
ssh ubuntu@192.168.2.196  # vm151 IP

# Step 3: Update code
cd ~/cloud-platform-upstream
git fetch origin
git checkout phase-1-batch-2

# Step 4: Restart containers
docker-compose down
docker-compose up -d
docker-compose logs -f api
```

**Snapshot location:** `phase-1-batch-2-final` on vm151

---

## Post-Deployment Verification (Both Scenarios)

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"
# Expected: 8/8 running (postgres, redis, rabbitmq, api, frontend, celery-beat, flower, celery-worker)

# Test login endpoint
curl -X POST http://192.168.2.186:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}'
# Expected: {"access_token": "...", "token_type": "bearer"}

# Test GUI loads
curl -s http://192.168.2.186:3000/ | grep -q "<title>" && echo "✅ GUI loads"

# Test Batch 2 LXC endpoint (if available)
curl http://192.168.2.186:8000/api/v1/vms/lxc 2>/dev/null || echo "LXC endpoint not available yet"
```

---

## Snapshot Creation

**After successful deployment:**

**If on vm103:**
```bash
# On pve2
qm snapshot 103 phase-1-batch-2-verified -d "Phase 1 Batch 2 verified on vm103, LXC + templates + cluster pages"

# Clean up old snapshots (keep 3)
qm listsnapshot 103
qm snapshot delete 103 <old_snapshot_name>
```

**If on temporary VM (vm151):**
```bash
# On pve1
qm snapshot 151 phase-1-batch-2-final -d "Phase 1 Batch 2 tested on vm151, LXC + templates + cluster pages"

# vm151 stays available for next test (no deletion needed)
```

---

## Rollback Plan

If Batch 2 fails:

**Option 1: Quick git rollback (on vm103)**
```bash
git checkout phase-1-batch-1
docker-compose restart
```

**Option 2: Restore from snapshot (on vm103)**
```bash
qm snapshot rollback 103 phase-1-batch-1-final
docker-compose restart
```

**Option 3: Reset vm151 for next test**
```bash
# Restore vm151 to baseline (clean state)
qm snapshot rollback 151 phase-1-batch-1-final
# vm151 ready for next batch test
```

---

## Success Criteria

- [x] phase-1-batch-2 branch created & merged to main
- [x] 10 commits applied to code
- [ ] Deployed to vm103 (default) ← **Default behavior**
- [ ] OR deployed to vm151 (if you say "test on vm151")
- [ ] 8/8 containers healthy
- [ ] Login endpoint works
- [ ] Dashboard loads
- [ ] Batch 2 features testable (LXC, templates, cluster pages)
- [ ] Snapshot created (`phase-1-batch-2-verified` on vm103 or `phase-1-batch-2-final` on vm151)

---

## Key Differences from Batch 1

| Aspect | Batch 1 | Batch 2+ |
|--------|---------|----------|
| Deployment | Manual (full OS install) | Code update only |
| Time | 30-45 min | 5 min |
| Baseline | Created from scratch | Cloned from working vm103 |
| Complexity | High (many manual steps) | Low (2-3 commands) |
| Error recovery | Slow (30+ min to retry) | Fast (1 min to rollback) |

---

## Related Documents

- VM_USAGE_POLICY.md - VM roles and rules
- CRITICAL_CONSTRAINTS.md - Constraint #6 (deployment method) & #7 (VM usage)
- SNAPSHOT_RECOVERY_WORKFLOW.md - Complete snapshot procedure
