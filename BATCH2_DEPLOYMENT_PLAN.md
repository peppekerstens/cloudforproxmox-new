# Phase 1 Batch 2: Deployment Plan (Snapshot-Based)

**Status:** Ready for deployment  
**Date:** 2026-05-29  
**Target:** vm152 on pve2 (192.168.2.187)  
**Branch:** `cloudforproxmox-new/phase-1-batch-2`  
**Deployment Method:** Clone from Batch 1 working snapshot + code update

---

## Strategy: Snapshot Recovery (NOT Full Redeploy)

Full VM deployments are complex and error-prone. **New strategy:** Use existing working VMs and their snapshots as baselines.

**Available Baselines:**
- **vm103** (pve2): Phase 1 Batch 1 working snapshot `phase-1-batch-1-final`
- **vm151** (pve1): Phase 1 Batch 1 working snapshot `phase-1-batch1-main-branch-working`

**Process:**
1. Clone vm103 snapshot → vm152 (copies all state: OS, Docker, DB, credentials)
2. Update code: `git checkout phase-1-batch-2`
3. Run DB migrations if needed
4. Test

This avoids 30-45 min of Ubuntu install + Docker setup + credential copy.

---

## Deployment (When Instructed)

### Step 1: Clone vm103 Snapshot to vm152

```bash
# On pve2 console
qm clone 103 152 --name cloud-platform-batch2 --full

# Or restore from snapshot:
qm snapshot rollback 103 phase-1-batch-1-final
qm clone 103 152 --name cloud-platform-batch2 --full

# Start vm152
qm start 152
```

### Step 2: Update Code to Batch 2

```bash
# SSH to vm152 (will have IP 192.168.2.187 from cloned config)
ssh ubuntu@192.168.2.187

# Update code
cd ~/cloud-platform-upstream  # (or ~/cloud-platform-batch2 if path differs)
git remote set-url origin https://github.com/peppekerstens/cloudforproxmox-new.git
git fetch origin
git checkout phase-1-batch-2

# Restart containers with new code
docker-compose down
docker-compose up -d
docker-compose logs -f api
```

### Step 3: Monitor Container Health

```bash
# Wait for migrations + startup (~2 min)
docker ps --format "table {{.Names}}\t{{.Status}}"

# Should show 8/8 containers running (postgres, redis, rabbitmq, api, frontend, celery-beat, flower, celery-worker)

# Check API logs for errors
docker logs cloud-platform-api
```

### Step 4: Quick Smoke Test

```bash
# Login endpoint
curl -X POST http://192.168.2.187:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}'

# Expected: {"access_token": "...", "token_type": "bearer"}

# Dashboard
curl -s http://192.168.2.187:3000/ | grep -q "<title>" && echo "✅ GUI loads"

# Test Batch 2 LXC feature (if API endpoint exists)
curl http://192.168.2.187:8000/api/v1/vms/lxc || echo "LXC endpoint not yet available"
```

### Step 5: Create Snapshot

```bash
# On pve2
qm snapshot 152 phase-1-batch-2-final -d "Phase 1 Batch 2 verified, LXC + templates + cluster pages"
```

---

## Recovery Plan

If Batch 2 fails during code update:
1. **Quick rollback:** `git checkout phase-1-batch-1` + `docker-compose restart`
2. **Full rollback:** `qm destroy 152` (keep snapshot `phase-1-batch-1-final` for next attempt)

---

## Success Criteria

- [x] phase-1-batch-2 branch created & merged to main
- [x] 10 commits applied to code
- [ ] vm152 cloned from vm103 snapshot ← **Do this when instructed**
- [ ] Batch 2 code deployed (git checkout)
- [ ] 8/8 containers healthy
- [ ] Login endpoint works
- [ ] Dashboard loads
- [ ] snapshot `phase-1-batch-2-final` created

---

## Why This Approach

1. **Speed:** Clone + code update takes ~5 min vs 30+ min full install
2. **Reliability:** Known-good DB state, Docker config already correct
3. **Easy rollback:** Snapshot recovery faster than troubleshooting
4. **Consistency:** Every Batch starts from proven Batch 1 baseline
