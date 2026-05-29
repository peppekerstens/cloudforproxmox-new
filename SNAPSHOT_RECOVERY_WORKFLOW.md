# Snapshot Recovery Workflow

**Effective:** 2026-05-29  
**Purpose:** Fast, reliable batch deployments using snapshot cloning  
**Status:** Standard procedure for all future batches

---

## Why Snapshots?

**Full VM deployment (❌ old approach):**
- Ubuntu ISO + install: 10-15 min
- Docker setup: 5 min
- App deploy: 10-15 min
- Network config: 5 min
- **Total: 30-45 min**
- Error points: 5+
- Manual SSH required: 8-10 commands

**Snapshot recovery (✅ new approach):**
- Clone baseline: 2-3 min
- Update code: 1-2 min
- Restart containers: 30 sec
- **Total: 5 min**
- Error points: 0 (pre-tested baseline)
- Manual SSH required: 2-3 commands

---

## Available Baselines

| VM | Node | IP | Role | Snapshot | Status |
|---|---|---|---|---|---|
| **vm103** | pve2 | 192.168.2.186 | **DEFAULT dev machine** | phase-1-batch-1-final | ✅ Active |
| vm151 | pve1 | 192.168.2.196 | Batch 1 test reference | phase-1-batch1-main-branch-working | ✅ Archived |

**vm103 is your default development machine.** I clone from vm103 for every batch deployment. It stays in working state at all times.

**vm151+ are temporary test machines,** only used when you explicitly instruct parallel testing.

See VM_USAGE_POLICY.md for detailed rules.

---

## Standard Workflow per Batch

### Phase: Code Preparation

1. ✅ **Already done:** Branch created, commits applied, merged to main
2. ✅ **Already done:** Code reviewed, documented
3. ✅ **Already done:** Deployment plan created

### Phase: VM Clone (When User Says "Deploy")

```bash
# SSH to target node (pve1 or pve2)
ssh root@192.168.2.21  # pve1
# or
ssh root@192.168.2.22  # pve2

# Clone baseline snapshot
# Format: qm clone <source_vmid> <new_vmid> --name <name> --full

# Example for Batch 2 on pve2:
qm clone 103 152 --name cloud-platform-batch2 --full

# Verify clone
qm list | grep 152

# Start VM
qm start 152

# Wait for boot (~30 sec)
sleep 30
```

### Phase: Code Update (5 min)

```bash
# SSH to new VM
ssh ubuntu@192.168.2.187  # (or appropriate new IP)

# Enter app directory
cd ~/cloud-platform-upstream  # or ~/cloud-platform-batch2

# Update git remote if needed
git remote set-url origin https://github.com/peppekerstens/cloudforproxmox-new.git

# Fetch & checkout new batch branch
git fetch origin
git checkout phase-1-batch-2  # (or current batch)

# Restart containers with new code
docker-compose down
docker-compose up -d

# Monitor logs (~2 min for migrations + startup)
docker-compose logs -f api
```

### Phase: Verification (2 min)

```bash
# Container health
docker ps --format "table {{.Names}}\t{{.Status}}"
# Expected: 8/8 running

# Quick API test
curl -X POST http://192.168.2.187:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}'
# Expected: {"access_token":"...", "token_type":"bearer"}

# GUI test
curl -s http://192.168.2.187:3000/ | grep -q "<title>" && echo "✅ GUI loads"
```

### Phase: Snapshot (1 min)

```bash
# Create snapshot on target node
# Format: qm snapshot <vmid> <snapname> -d "<description>"

# Example for Batch 2:
qm snapshot 152 phase-1-batch-2-final -d "Phase 1 Batch 2 verified, LXC + templates + cluster pages"

# Verify
qm listsnapshot 152
```

---

## Snapshot Naming Convention

```
phase-1-batch-<N>-final
phase-2-batch-<N>-final
...
phase-12-batch-<N>-final
```

**Example:**
- `phase-1-batch-1-final` - Batch 1 complete & verified
- `phase-1-batch-2-final` - Batch 2 complete & verified
- `phase-1-batch-3-final` - Batch 3 complete & verified

---

## Rollback Procedure

If code update causes issues:

### Quick Rollback (git undo)
```bash
# SSH to VM
ssh ubuntu@192.168.2.187

# Revert code
cd ~/cloud-platform-upstream
git checkout <previous_branch>  # e.g., phase-1-batch-1

# Restart
docker-compose down
docker-compose up -d

# Verify
curl -X POST http://192.168.2.187:8000/api/v1/auth/login ...
```

### Full Rollback (delete VM, keep snapshot)
```bash
# If VM is broken beyond recovery, delete it
qm destroy 152

# Keep snapshot for reference/retry
qm listsnapshot 103 | grep phase-1-batch-1-final  # Verify baseline exists

# Next attempt: clone from baseline again
qm clone 103 152 --name cloud-platform-batch2-retry --full
```

---

## Important Notes

1. **IP Assignment:** Cloned VM inherits netplan config from baseline, so IP addresses must be:
   - Updated in netplan if moving to different subnet, OR
   - Pre-assigned via DHCP reservation, OR
   - Left as-is if using same subnet

2. **Storage:** Clone is **full clone** (not linked), so each VM needs full disk space:
   - vm103: 20GB
   - vm151: 20GB
   - vm152+: 20GB each (total 60GB+ needed on target node)

3. **Credentials:** Already in .env from baseline, so no manual credential copy needed.

4. **Docker Compose State:** Containers start fresh on `docker-compose up -d`, including DB migrations.

---

## Advantages Over Full Deployment

| Aspect | Full Deploy | Snapshot Clone |
|---|---|---|
| Time | 30-45 min | 5-10 min |
| Manual steps | 8-10 | 2-3 |
| Error risk | High | Very low |
| Rollback time | 5+ min | <1 min |
| Requires SSH | Yes | Yes (minimal) |
| Testing | Needed after | Already done |

---

## When to Use Full Deployment

Full VM creation is justified **only if:**
1. No baseline snapshot exists
2. Baseline snapshot is corrupted
3. Testing fresh OS behavior needed
4. User explicitly requests it

In all other cases, use snapshot cloning.

---

## Snapshot Cleanup

Keep last 2 snapshots per VM, delete old ones:

```bash
# List all snapshots for vm103
qm listsnapshot 103

# Delete old snapshot
qm snapshot delete 103 <old_snapshot_name>
```

**Retention policy:** Keep current + previous batch (e.g., batch-2 and batch-1), delete older.
