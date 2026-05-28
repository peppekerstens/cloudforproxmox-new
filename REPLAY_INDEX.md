# Deployment Replay Index

**Commit Range:** `7c1ae38` → `040259b`  
**Total Commits:** 303  
**Coverage:** 100%  
**Generated:** 2026-05-28

---

## Quick Start

1. **Start here:** Read `REPLAY_SUMMARY.md` for overview
2. **Select phase:** Choose `REPLAY_PLAN_PHASE{X-Y}.md` to deploy
3. **Follow sequence:** Execute commits in order
4. **Batch test:** After 8 commits, run health checks
5. **On failure:** Consult failure handling protocol in each file

---

## Files Overview

| File | Phase | Commits | Size | Purpose |
|------|-------|---------|------|---------|
| **REPLAY_SUMMARY.md** | — | — | 7.4 KB | Overview, statistics, deployment guide |
| **REPLAY_PLAN_PHASE0-1.md** | Setup → VM/LXC | 179 | 96 KB | Foundation & core infrastructure |
| **REPLAY_PLAN_PHASE2-3.md** | Network → Onboard | 22 | 14 KB | Networking & user onboarding |
| **REPLAY_PLAN_PHASE4-5.md** | Multi-Tenant → RBAC | 51 | 29 KB | Organization & role management |
| **REPLAY_PLAN_PHASE8-9.md** | Audit → Billing | 40 | 23 KB | Audit trail & billing system |
| **REPLAY_PLAN_PHASE12.md** | HTTPS ⚠️ | 11 | 8.1 KB | HTTPS/TLS (expected failure) |

**Total:** 303 commits, 171 KB, 7,314 lines

---

## Phase Details

### Phase 0-1: Setup → VM/LXC (179 commits)
**Hash:** `7c1ae38` → `66ad710`  
**Date:** 2026-05-20 → 2026-05-26

Foundation phase. Covers:
- Fork upstream cloud-platform repo
- Core SDN networking (VXLAN)
- Test infrastructure
- VM/LXC creation APIs
- Bug fixes (#2, #3, #9-11)
- Phase 1 foundation complete

**File:** `REPLAY_PLAN_PHASE0-1.md`

---

### Phase 2-3: Network → Onboard (22 commits)
**Hash:** `ba81e42` → `8b05695`  
**Date:** 2026-05-21 → 2026-05-26

Networking & onboarding. Covers:
- Firewall rules management
- DNS integration & admin UI
- IP address management (IPAM)
- User self-registration flow
- Phase-gate tests (24 tests)

**File:** `REPLAY_PLAN_PHASE2-3.md`

---

### Phase 4-5: Multi-Tenant → RBAC (51 commits)
**Hash:** `18f428b` → `7e91680`  
**Date:** 2026-05-21 → 2026-05-26

Organization & roles. Covers:
- Superadmin user management
- Organization creation flow
- Multi-tenant support
- User quotas
- Role promotion/demotion
- Toast notifications
- 94+ tests passing

**File:** `REPLAY_PLAN_PHASE4-5.md`

---

### Phase 8-9: Audit → Billing (40 commits)
**Hash:** `be24213` → `040259b`  
**Date:** 2026-05-21 → 2026-05-26

Business logic. Covers:
- Audit trail implementation
- Billing data models
- Stripe payment integration
- Provider abstraction (#206)
- Per-org billing override
- Superadmin Stripe UX
- 94+ tests

**File:** `REPLAY_PLAN_PHASE8-9.md`

---

### Phase 12: HTTPS (11 commits) ⚠️ EXPECTED FAILURE
**Hash:** `9e628f9` → `d974568`  
**Date:** 2026-05-25 → 2026-05-26

HTTPS/TLS implementation. Covers:
- Certificate management backend/frontend
- Nginx TLS reverse proxy
- HTTPS deployment guide
- ProxmoxService SSL fixes

**⚠️ EXPECTED FAILURE** - Known integration challenges with:
- Certificate endpoint coverage
- Nginx proxy Docker networking
- AdGuard HTTPS port binding

**File:** `REPLAY_PLAN_PHASE12.md`

---

## Deployment Workflow

### Pre-Deployment
```bash
# Verify VM103 is healthy
ssh vm103 "docker ps | wc -l"  # Should show 8 containers
ssh vm103 "df -h /"            # Check storage >500MB

# Create base snapshot
proxmox snapshot vm103 snapshot-base "Before replay"
```

### Per-Phase Deployment
1. Navigate to phase file: `REPLAY_PLAN_PHASE{X-Y}.md`
2. Read Executive Summary
3. For each commit:
   - Check Pre-flight Checklist
   - Run Deploy script
   - Monitor logs for 30s
4. After 8 commits: Run Batch Tests section
5. After phase complete: Run Phase Boundary Verification

### Batch Testing (Every 8 commits)
```bash
ssh vm103 << 'BASH'
docker ps
docker logs postgres 2>&1 | grep -i critical | wc -l
docker logs redis 2>&1 | grep -i critical | wc -l
docker logs backend 2>&1 | grep -i critical | wc -l
curl -s http://localhost:8000/health | grep -q "ok" && echo "API healthy" || echo "FAILED"
curl -s http://localhost | grep -q "<!DOCTYPE" && echo "UI loads" || echo "FAILED"
BASH
```

### On Failure
1. Consult "Failure Handling Protocol" in phase file
2. Rollback to previous snapshot
3. Review docker logs
4. Retry with smaller batch (5 commits)
5. If persistent: escalate to user

---

## VM103 Configuration

| Property | Value |
|----------|-------|
| **OS** | Ubuntu 22.04 LTS |
| **CPU** | 4 vCPU |
| **RAM** | 4 GB |
| **Disk** | 20 GB |
| **Docker** | 26.x |
| **Containers** | 8 |

### Container Stack
1. **PostgreSQL 16** - Data persistence
2. **Redis 7** - Caching & task queue
3. **FastAPI backend** - REST API
4. **React frontend** - Web UI
5. **Nginx** - Reverse proxy / HTTPS
6. **Celery worker** - Async tasks
7. **Celery beat** - Scheduled tasks
8. **AdGuard** - DNS management

---

## Snapshot Management

### Strategy
- Keep **3 active snapshots** during deployment
- Each successful batch (8 commits) = new snapshot
- Delete oldest when limit reached
- Keep newest 2 + current working

### Naming Convention
```
snapshot-{hash}     # Commit-specific snapshot
snapshot-base       # Initial pre-replay state
snapshot-phase-0-1  # Phase completion (optional)
```

### Rotation Example
```
Slot 1: snapshot-7c1ae38  (old)     → DELETE
Slot 2: snapshot-ba81e42  (middle)  → KEEP
Slot 3: snapshot-18f428b  (current) → KEEP
NEW:    snapshot-08473a3  (latest)  → KEEP
```

---

## Key Statistics

### Commit Distribution
- **Phase 0-1:** 179 commits (59%)
- **Phase 4-5:** 51 commits (17%)
- **Phase 8-9:** 40 commits (13%)
- **Phase 2-3:** 22 commits (7%)
- **Phase 12:** 11 commits (4%)

### File Impact
- **Backend:** 226 commits modified
- **Frontend:** 157 commits modified
- **Infrastructure:** 82 commits modified
- **Documentation only:** 68 commits

### Timeline
- **2026-05-20:** 2 commits (foundation)
- **2026-05-21:** 134 commits (rapid development)
- **2026-05-22-24:** 95 commits (testing & refinement)
- **2026-05-25:** 64 commits (audit, billing, HTTPS)
- **2026-05-26:** 8 commits (final fixes)

### Test Coverage
- Phase 2 integration tests: 24
- Phase 6 unit/integration tests: 94+
- Total test suite: 94+ passing

---

## Navigation

### By Deployment Phase
- **Foundation:** → `REPLAY_PLAN_PHASE0-1.md`
- **Networking:** → `REPLAY_PLAN_PHASE2-3.md`
- **Organizations:** → `REPLAY_PLAN_PHASE4-5.md`
- **Business Logic:** → `REPLAY_PLAN_PHASE8-9.md`
- **HTTPS:** → `REPLAY_PLAN_PHASE12.md`

### By Topic
- **Overview:** → `REPLAY_SUMMARY.md`
- **Deployment Guide:** → `REPLAY_SUMMARY.md` (Usage section)
- **Failure Handling:** → Any `REPLAY_PLAN_PHASE*.md` (end of file)
- **Docker Commands:** → `REPLAY_PLAN_PHASE*.md` (Batch Testing)

### By Issue/Feature
- **Bug fixes:** Referenced in commit messages (e.g., #2, #3, #206)
- **Features:** Marked as `feat:` in commit messages
- **Issues:** Check commit messages for issue numbers

---

## Troubleshooting

### Container Won't Start
1. Check logs: `docker logs {container-name}`
2. Verify previous snapshot exists
3. Rollback: `git checkout {previous-hash}`
4. Re-deploy: `docker-compose up -d`

### CRITICAL Errors in Logs
1. Note which container
2. Find error in docker logs
3. Check git blame for recent changes
4. Rollback to previous snapshot
5. Retry with smaller batch

### API Health Check Fails
```bash
curl -s http://localhost:8000/health
# Expected: {"status":"ok"}
```
If fails:
1. Check backend logs: `docker logs backend`
2. Check PostgreSQL: `docker logs postgres`
3. Verify VITE_API_URL in frontend config
4. Check firewall rules

### UI Won't Load
```bash
curl -s http://localhost | head -20
# Expected: <!DOCTYPE html>
```
If fails:
1. Check Nginx: `docker logs nginx`
2. Check frontend: `docker logs frontend`
3. Verify port 80/443 bindings
4. Check CORS_ORIGINS config

### Phase 12 HTTPS Issues
1. Check Nginx config: `docker exec nginx cat /etc/nginx/nginx.conf`
2. Verify certs: `docker exec nginx ls -la /certs/`
3. Test TLS: `openssl s_client -connect localhost:443`
4. Review logs: `docker logs nginx | tail -50`
5. Document failure & escalate (expected)

---

## Quick Reference

### Deploy Single Commit
```bash
cd ~/github/proxmox-isp
git checkout {hash}
docker-compose up -d
sleep 5 && docker ps
```

### Rollback to Snapshot
```bash
# Via Proxmox (example)
qm rollback vm103 snapshot-{hash}
docker-compose up -d
```

### View Current Status
```bash
git log -1 --oneline
docker ps
docker stats --no-stream
```

### Run Batch Tests
```bash
docker ps
for container in postgres redis backend; do
  docker logs $container 2>&1 | grep -i critical | wc -l
done
curl -s http://localhost:8000/health
curl -s http://localhost | head -1
```

---

## Support

### If Deployment Fails
1. **First:** Check the phase file's "Failure Handling Protocol"
2. **Then:** Review docker logs for the specific error
3. **Next:** Rollback to previous snapshot
4. **Finally:** Document in REPLAY_STATUS.md and escalate

### If Phase 12 (HTTPS) Fails (Expected)
- This is **expected to fail** - it's a known integration challenge
- Follow diagnostic steps in REPLAY_PLAN_PHASE12.md
- Document the failure mode
- Escalate to user for guidance

### Contact
- For deployment issues: See failure protocol in each phase file
- For code issues: Check commit messages for issue numbers
- For infrastructure: Review docker logs and VM103 health

---

**Last Updated:** 2026-05-28  
**Ready for deployment replay**
