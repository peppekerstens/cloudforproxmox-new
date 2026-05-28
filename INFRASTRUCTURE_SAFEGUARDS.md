# Infrastructure Safeguards for Replay Execution

**Project:** Cloud for ProxMox Replay (cloudforproxmox-new)  
**Date:** 2026-05-28  
**Purpose:** Define safeguards, snapshot strategy, testing procedures, rollback gates  
**Applies To:** Phase 0-1 → Phase 12 replay on vm103

---

## Overview

This document implements lessons learned from cloudforproxmox-old failure:
1. **Backup/snapshot history** — protect against catastrophic failures
2. **Phase gates** — explicit checkpoints before advancing
3. **Deployment testing** — verify actual state matches expectations
4. **Rollback procedures** — clear decision tree for each phase

---

## Snapshot Rotation Policy

### Strategy: Rolling Window (Max 3 Active, Min 2 History)

**Purpose:** Protect against bad deployments while conserving storage.

**Naming Convention:** `snapshot-{commit-hash-short}` (7 chars)  
Example: `snapshot-7c1ae38`, `snapshot-be13bb8`, `snapshot-040259b`

**Rotation Rules:**

1. **Before each commit deploy:**
   - Check available snapshots (max 3)
   - If at limit (3), delete oldest snapshot
   - Keep newest 2

2. **After successful deploy + test:**
   - Create snapshot: `snapshot-{commit-hash}`
   - Log in REPLAY_STATUS.md

3. **If commit fails tests:**
   - Don't create snapshot
   - Rollback to previous snapshot
   - Document failure in REPLAY_STATUS.md

**Example slot progression:**

```
Initial state:
  Slot 1: snapshot-initial (baseline)
  Slot 2: (empty)
  Slot 3: (empty)

After commit 7c1ae38 (success):
  Slot 1: snapshot-initial
  Slot 2: snapshot-7c1ae38
  Slot 3: (empty)

After commit d388cc6 (success):
  Slot 1: snapshot-initial
  Slot 2: snapshot-7c1ae38
  Slot 3: snapshot-d388cc6

After commit 010082a (success):
  Slot 1: snapshot-7c1ae38
  Slot 2: snapshot-d388cc6
  Slot 3: snapshot-010082a
  (snapshot-initial deleted due to rotation)

If commit f900dba fails:
  Slot 1: snapshot-7c1ae38
  Slot 2: snapshot-d388cc6
  Slot 3: snapshot-010082a
  (No snapshot for f900dba; rollback to snapshot-010082a)
```

### Operational Procedure

**Before deploying batch of commits:**
```bash
# Check current snapshots
proxmox-mcp list_snapshots node=pve2 vmid=103 type=qemu

# Count active snapshots
# If count >= 3, identify oldest (earliest date)
# Plan to delete it after next batch succeeds
```

**After successful batch + tests:**
```bash
# Create snapshot
proxmox-mcp create_snapshot node=pve2 vmid=103 type=qemu snapname=snapshot-{hash} description="After commit {hash}: {message}"

# Update REPLAY_STATUS.md
# Log: Slot N: snapshot-{hash} ({date})
```

**If batch fails:**
```bash
# Rollback
proxmox-mcp rollback_snapshot node=pve2 vmid=103 type=qemu snapname=snapshot-{last-good}

# Update REPLAY_STATUS.md
# Log failure reason, last-good snapshot
# Stop and escalate
```

---

## Phase Gate Checklist

**Before advancing to next phase, verify:**

### Pre-Phase Gate (Every Commit/Batch)

- [ ] Previous phase snapshot exists and is healthy
- [ ] vm103 storage >500MB free
- [ ] All 8 Docker containers running: `docker ps | wc -l` should be 9 (including header)
- [ ] No CRITICAL logs in past 30 seconds: `docker logs {container} 2>&1 | grep CRITICAL | wc -l` should be 0

### Post-Batch Testing

- [ ] API health check passes: `curl -s http://localhost:8000/health | grep -q "ok"`
- [ ] UI loads: `curl -s http://localhost | grep -q "<!DOCTYPE"`
- [ ] Database accessible: Run test query via psql in postgres container
- [ ] No unexpected errors in logs (allow DEBUG/INFO, fail on ERROR/CRITICAL)

### Phase Boundary Gate (Between Phases)

**Run AFTER completing all commits in a phase, BEFORE moving to next:**

1. **Git history verification (spot-check):**
   ```bash
   git log --oneline | head -20
   # Verify: current HEAD is expected end-commit of phase
   # Verify: major commits from phase are present
   ```

2. **Deployment state verification:**
   ```bash
   # Check all 8 containers healthy
   docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "Up|Healthy"
   # Should have 8 running containers (postgres, redis, fastapi, react, nginx, celery-worker, celery-beat, adguard)
   
   # Check database schema matches expected version
   docker exec postgres psql -U proxmoxisp -d proxmoxisp -c "\dt" | wc -l
   # Should match schema version in commits
   ```

3. **Feature verification (phase-specific):**
   - Phase 0-1: VM creation, LXC templating, ISO upload work
   - Phase 2-3: Firewall rules, DNS A records, IP allocation work
   - Phase 4-5: Org creation, user quota enforcement works
   - Phase 8-9: Audit logs appear, billing models exist
   - Phase 12: HTTPS loads, TLS cert valid

4. **Snapshot creation:**
   - Create snapshot: `snapshot-{end-commit-of-phase}`
   - Log in REPLAY_STATUS.md

---

## Test Procedures by Phase

### Phase 0-1: Setup → VM/LXC Foundation

**After each batch of commits:**

```bash
# Check containers
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check API responds
curl -s http://localhost:8000/health

# Check UI loads
curl -s http://localhost | head -20

# Check database
docker exec postgres psql -U proxmoxisp -d proxmoxisp -c "SELECT version();"

# Optional: Create test VM via API
curl -X POST http://localhost:8000/api/v1/vms \
  -H "Content-Type: application/json" \
  -d '{"name":"test-vm","node":"pve1","cores":2,"memory":2048}'
```

### Phase 2-3: Network → Onboarding

**After batch:**

```bash
# Test DNS
curl -X POST http://localhost:8000/api/v1/dns \
  -H "Content-Type: application/json" \
  -d '{"fqdn":"test.local","type":"A","value":"192.168.2.1"}'

# Test firewall rule
curl -X POST http://localhost:8000/api/v1/firewall \
  -H "Content-Type: application/json" \
  -d '{"source":"192.168.0.0/16","dest":"10.0.0.0/8","action":"accept"}'

# Test self-registration
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.org","password":"TestPassword123!"}'
```

### Phase 4-5: Multi-Tenant → RBAC

**After batch:**

```bash
# Test org creation
curl -X POST http://localhost:8000/api/v1/orgs \
  -H "Content-Type: application/json" \
  -d '{"name":"test-org","owner":"admin"}'

# Test user quota
curl -X POST http://localhost:8000/api/v1/quotas \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"vm_count":5,"cpu_limit":16}'

# Test quota enforcement (should fail if over limit)
curl -X POST http://localhost:8000/api/v1/vms -d '...' | grep -q "quota exceeded"
```

### Phase 8-9: Audit → Billing

**After batch:**

```bash
# Check audit logs appear
docker exec postgres psql -U proxmoxisp -d proxmoxisp -c "SELECT COUNT(*) FROM audit_logs;"

# Check billing tables exist
docker exec postgres psql -U proxmoxisp -d proxmoxisp -c "SELECT * FROM billing_plans LIMIT 1;"

# Optional: Test Stripe webhook (requires mock)
curl -X POST http://localhost:8000/api/v1/webhooks/stripe \
  -H "Content-Type: application/json" \
  -d '{"type":"payment_intent.succeeded"}'
```

### Phase 12: HTTPS (PRE-DEPLOYMENT CHECK)

**BEFORE starting Phase 12 commits, run PHASE12_SECURITY_CHECKPOINT.md first.**

**After Phase 12 commits:**

```bash
# TLS certificate present
ls -la /etc/nginx/certs/ | grep -E "cert|key"

# TLS handshake works
echo | openssl s_client -connect localhost:443 2>/dev/null | grep -A2 "Subject:"

# Nginx config valid
docker exec nginx nginx -t

# HTTPS login
curl -k -X POST https://localhost:443/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"..."}'
```

---

## Failure Handling Protocol

**If any test fails at any phase:**

### Step 1: Capture Diagnostics (5 min)

```bash
# Get container logs (last 100 lines each)
for container in postgres redis fastapi react nginx celery-worker celery-beat adguard; do
  docker logs --tail 100 $container > /tmp/${container}.log 2>&1
done

# Get docker stats
docker stats --no-stream > /tmp/docker-stats.txt

# Get host disk/mem
df -h > /tmp/disk.txt
free -h > /tmp/memory.txt

# Get git status
git log --oneline -5 > /tmp/git-log.txt
git status > /tmp/git-status.txt
```

### Step 2: Analyze Failure

**Common failure types:**

| Symptom | Root Cause | Action |
|---------|-----------|--------|
| `docker: API call failed` | Docker daemon crashed | Restart docker daemon |
| `connection refused on port 8000` | FastAPI container exited | Check docker logs fastapi |
| `CRITICAL error in logs` | Code bug introduced | Check commit diff |
| `Out of memory` | VM resource exhaustion | Reduce container memory limit or rollback |
| `Certificate file not found` | Volume mount issue | Check docker-compose volumes |

### Step 3: Decision Tree

**Question 1: Is this a deployment/infrastructure issue (not code)?**
- Yes → Fix locally, test, re-run batch
- No → Go to Question 2

**Question 2: Did the previous batch pass?**
- Yes → Rollback to snapshot-{previous-batch}, skip failing commits, escalate
- No → Check git history; maybe two consecutive bad commits

**Question 3: Can we identify the exact failing commit?**
- Yes → Rollback, run commits 1-by-1 to isolate failure
- No → Rollback to last known good, document partial progress, escalate

### Step 4: Rollback Procedure

```bash
# Rollback to last good snapshot
proxmox-mcp rollback_snapshot node=pve2 vmid=103 type=qemu snapname=snapshot-{last-good-hash}

# Update REPLAY_STATUS.md
echo "Rollback at commit {failed-hash}: {failure-reason}" >> REPLAY_STATUS.md

# If retrying:
git checkout snapshot-{last-good-hash}
docker-compose up -d
# Wait 30 seconds
docker ps  # Verify all containers healthy
# Re-run tests for this phase
```

### Step 5: Escalation

**Stop and escalate if:**
- Three consecutive commits fail (indicates systematic issue)
- Database corruption (CRITICAL error in postgres logs)
- Infrastructure failure (storage full, network down)
- Phase 12 HTTPS test fails (documented failure point)

**Escalation message should include:**
- Failed commit hash and message
- Exact error message from logs
- Last successful snapshot
- Diagnostic files (/tmp/*.log, /tmp/*.txt)
- Number of retry attempts

---

## Batch Testing Strategy

**Goal:** Minimize snapshots while catching failures early.

**Batch size recommendation:**
- **Phase 0-1 (179 commits):** Batch 8-10 commits, test, snapshot
- **Phase 2-3 (22 commits):** Batch 5-6 commits, test, snapshot
- **Phase 4-5 (51 commits):** Batch 5-6 commits, test, snapshot
- **Phase 8-9 (40 commits):** Batch 5-6 commits, test, snapshot
- **Phase 12 (11 commits):** Batch 2-3 commits, test, snapshot (PRE-SECURITY-CHECK)

**Batch test execution:**
```bash
# Deploy batch
git checkout {end-commit-of-batch}
docker-compose up -d
sleep 30

# Run phase-specific tests
# ... (see Test Procedures by Phase above)

# If tests pass
proxmox-mcp create_snapshot ...
echo "Batch success" >> REPLAY_STATUS.md

# If tests fail
# ... (see Failure Handling above)
```

---

## Monitoring During Replay

**Real-time health indicators (check every 5 min during deploy):**

```bash
# Container status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Resource usage
docker stats --no-stream | grep -E "fastapi|postgres|redis"

# Recent logs (errors only)
for c in postgres fastapi nginx; do docker logs --tail 20 $c 2>&1 | grep -i error || echo "$c: OK"; done

# Disk space
df -h /var/lib/docker
```

**Automated monitoring (optional):**

```bash
# Create health check script
cat > /tmp/health-check.sh << 'EOF'
#!/bin/bash
echo "[$(date)] Health check:"
docker ps --format "{{.Names}}\t{{.Status}}" | grep -v "Up"
curl -s http://localhost:8000/health || echo "API: FAIL"
curl -s http://localhost | head -1 || echo "UI: FAIL"
EOF

chmod +x /tmp/health-check.sh

# Run every 5 min
while true; do /tmp/health-check.sh >> /tmp/health.log; sleep 300; done
```

---

## Recovery Procedures

### If Storage Full
```bash
# Clean old docker images
docker image prune -a

# Clean unused volumes
docker volume prune

# Expand disk (if using LVM)
# This requires hypervisor access (out of scope for vm103 guest)
```

### If Docker Daemon Crashes
```bash
# Restart docker
sudo systemctl restart docker

# Verify containers restart
docker ps | wc -l
```

### If Database Corrupted
```bash
# Check postgres logs
docker logs postgres 2>&1 | tail -50

# Attempt repair (PostgreSQL)
docker exec postgres vacuumdb -U proxmoxisp -d proxmoxisp

# If still broken: Rollback to snapshot
proxmox-mcp rollback_snapshot ...
```

### If Network Lost
```bash
# Verify vm103 connectivity
ping 8.8.8.8

# Check docker network
docker network ls
docker inspect bridge | grep -A10 "Containers"

# Restart docker network
docker network prune
```

---

## Documentation Requirements

**REPLAY_STATUS.md must be updated after each batch:**

```markdown
| Batch | Commits | Status | Last Snapshot | Notes |
|-------|---------|--------|----------------|-------|
| Phase0-1, Batch 1 | 7c1ae38...d388cc6 | ✅ Passed | snapshot-d388cc6 | All tests passed |
| Phase0-1, Batch 2 | 010082a...f900dba | ⚠️ Failed | snapshot-010082a | Rollback: f900dba commit syntax error |
```

**Each batch entry should include:**
- Commit range (first...last)
- Status (Passed/Failed)
- Snapshot name
- Notes (tests passed, failure reason, retry notes)

---

## Success Metrics

**Replay is successful when:**
- [ ] All 303 commits replayed from 7c1ae38 → 040259b
- [ ] Each phase-boundary spot-check passes (git history verified)
- [ ] Final snapshot at 040259b created
- [ ] REPLAY_STATUS.md documents all phases with test results
- [ ] Known failure at 040259b reproduced and documented
- [ ] No data loss (snapshots preserved)

**Phase 12 specifically:**
- [ ] Pre-security checkpoint passed
- [ ] HTTPS certificates present and valid
- [ ] TLS handshake succeeds
- [ ] API and UI accessible over HTTPS
- [ ] HTTPS failure mode documented (if fails as expected)
