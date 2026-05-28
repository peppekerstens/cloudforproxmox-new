# Documentation Index: Cloud for ProxMox Replay Project

**Last Updated:** May 28, 2026  
**Status:** Phase 0 Complete, Phase 1 Pending  
**Total Documentation:** 15 markdown files, ~300KB

---

## Quick Navigation

### 🎯 Start Here (Phase 1 Team)
1. **TWO_REPO_WORKFLOW.md** ⭐ (NEW - per-batch workflow)
   - Complete guide: fork + orchestration repo
   - Step-by-step workflow (identify → branch → test → tag → track)
   - Git commands, testing procedures, snapshot management
   - Handoff checklist

2. **FORK_STRATEGY.md** (Decision rationale)
   - Why fork upstream (Option 2 selected)
   - Comparison with alternatives (Option 1 rejected)
   - Two-repo architecture explained

3. **REPLAY_STATUS.md** (Current status)
   - Which batch is deployed
   - Gate criteria (pre-Phase 1)
   - Phase progress tracking

### 📋 Planning & Tracking (Orchestration Repo)
- **REPLAY_PLAN_PHASE0-1.md** (96K) - Setup & Foundation (179 commits) ← Use in fork
- **REPLAY_PLAN_PHASE2-3.md** (14K) - Network & Onboarding (22 commits) ← Use in fork
- **REPLAY_PLAN_PHASE4-5.md** (29K) - Multi-Tenant & RBAC (51 commits) ← Use in fork
- **REPLAY_PLAN_PHASE8-9.md** (23K) - Audit & Billing (40 commits) ← Use in fork
- **REPLAY_PLAN_PHASE12.md** (8.1K) - HTTPS (11 commits, expected failure) ← Use in fork
- **REPLAY_INDEX.md** (9.3K) - Searchable commit index for all phases
- **REPLAY_SUMMARY.md** (7.8K) - High-level overview
- **DEPLOYMENT_TRACKING.md** (TBD) - Maps vm103 state to fork branches (per-batch)

### 🔌 Infrastructure Integration
- **PROXMOX_CLUSTER_INTEGRATION.md** ⭐ (NEW - comprehensive guide)
  - Complete cluster attachment procedure
  - API token creation and security
  - Testing and verification procedures
  - Troubleshooting guide
  - API endpoints documentation
  - Integration checklist

### ⚙️ Operations & Safety
- **INFRASTRUCTURE_SAFEGUARDS.md** (14K) - Snapshot rotation, batch testing, failure handling
- **OPENCODE_RULES.md** (14K) - 40-rule handbook for this project
- **OPENCODE_ASSESSMENT.md** (11K) - Assessment of OpenCode capabilities
- **PHASE12_SECURITY_CHECKPOINT.md** (13K) - Pre-HTTPS audit checklist

---

## Document Purpose Summary

| File | Type | Size | Purpose | Status |
|------|------|------|---------|--------|
| **TWO_REPO_WORKFLOW.md** ⭐ | Operations | TBD | Per-batch workflow (identify, branch, test, tag, track) | ✅ NEW |
| **UPSTREAM_DEPLOYMENT_PREREQUISITES.md** ⭐ | Operations | 13K | Complete phase 0 guide: deployment, issues, solutions, config changes, Proxmox integration | ✅ DONE |
| **PROXMOX_CLUSTER_INTEGRATION.md** ⭐ | Infrastructure | TBD | Cluster attachment guide: API token, registration, testing, troubleshooting | ✅ NEW |
| **FORK_STRATEGY.md** ⭐ | Planning | 8.5K | Why fork was chosen (Option 2 selected) | ✅ DECIDED |
| **REPLAY_STATUS.md** | Tracking | 6.5K | Current status, phases, deliverables, gate criteria | ✅ CURRENT |
| REPLAY_PLAN_PHASE0-1.md | Planning | 96K | 179 commits for Setup & Foundation phase | 📍 REFERENCE |
| REPLAY_PLAN_PHASE2-3.md | Planning | 14K | 22 commits for Network & Onboarding | 📍 REFERENCE |
| REPLAY_PLAN_PHASE4-5.md | Planning | 29K | 51 commits for Multi-Tenant & RBAC | 📍 REFERENCE |
| REPLAY_PLAN_PHASE8-9.md | Planning | 23K | 40 commits for Audit & Billing | 📍 REFERENCE |
| REPLAY_PLAN_PHASE12.md | Planning | 8.1K | 11 commits for HTTPS (failure expected) | 📍 REFERENCE |
| REPLAY_INDEX.md | Reference | 9.3K | Searchable index of all 303 commits | 📍 LOOKUP |
| REPLAY_SUMMARY.md | Overview | 7.8K | High-level summary of all phases | 📍 OVERVIEW |
| INFRASTRUCTURE_SAFEGUARDS.md | Operations | 14K | Snapshot rotation, batch testing, rollback procedures | 📍 SAFETY |
| OPENCODE_RULES.md | Guidelines | 14K | 40-rule handbook for caveman mode, testing, credentials | 📍 POLICY |
| OPENCODE_ASSESSMENT.md | Assessment | 11K | OpenCode capabilities analysis for this project | 📍 INFO |
| PHASE12_SECURITY_CHECKPOINT.md | Audit | 13K | Pre-HTTPS security checklist and failure modes | 📍 REVIEW |
| DOCUMENTATION_INDEX.md | Navigation | TBD | This file | ✅ THIS |

---

## Phase Overview

### Phase 0: Upstream Deployment ✅ COMPLETE
**Documentation:** UPSTREAM_DEPLOYMENT_PREREQUISITES.md

**What Happened:**
- Deployed proxmox-cloudportal/cloud-platform on vm103 clean state
- Encountered 3 issues (API URL, CORS, docker-compose bug)
- All issues resolved and documented
- Upstream verified working: login tested, dashboard accessible
- Snapshot baseline created: `snapshot-upstream-final-cors-fixed`

**Issues Documented:**
1. Frontend API URL hard-coded to localhost → Fixed via VITE_API_URL env var
2. CORS policy blocking login → Fixed via CORS_ORIGINS env var
3. docker-compose v1.29.2 KeyError bug → Worked around via docker system prune

**Configuration Changes:**
- `docker-compose.yml` VITE_API_URL: localhost → 192.168.2.186:8000
- `docker-compose.yml` CORS_ORIGINS: added 192.168.2.186:3000

**Verification:**
- ✅ All 8 containers healthy
- ✅ API responding: /api/v1/health/detailed → healthy
- ✅ Login verified: admin@example.org → dashboard
- ✅ Frontend: http://192.168.2.186:3000 accessible

**Pre-Phase 1 Gate:** ✅ PASSED

---

### Phase 1: Setup & Foundation (7c1ae38...?) 
**Documentation:** REPLAY_PLAN_PHASE0-1.md (96K)

**What Will Happen:**
- Replay ~10-15 commits per batch
- ~179 total commits across Phase 1
- Focus: VM/LXC infrastructure, basic proxmox integration
- Testing: each batch → snapshot → commit & tag

**Batches Planned:** ~12-18 batches (per REPLAY_PLAN_PHASE0-1.md)

**Gate Criteria:**
- [ ] Fork upstream created
- [ ] Branch/tag naming finalized
- [ ] First batch commits identified
- [ ] Testing procedure verified

---

### Phases 2-12: Full Replay
**Documentation:** REPLAY_PLAN_PHASE*.md files

**Scope:** 303 total commits across 12 phases
- Phase 2-3: Network & Onboarding (22 commits)
- Phase 4-5: Multi-Tenant & RBAC (51 commits)
- Phase 8-9: Audit & Billing (40 commits)
- Phase 12: HTTPS (11 commits, expected failure at 040259b)

**Each Phase Follows:**
1. Restore from previous snapshot
2. Apply batch commits from REPLAY_PLAN_PHASE*.md
3. Test containers, login, specific features
4. Create snapshot: phase-X-batch-Y-tested
5. Commit & push: phase-X-batch-Y branch/tag
6. Repeat for next batch

---

## Key Files for Each Role

### For Developers (Replaying Commits)
1. **UPSTREAM_DEPLOYMENT_PREREQUISITES.md** - Understand baseline, known issues, config changes
2. **FORK_STRATEGY.md** - How to branch/tag per batch
3. **REPLAY_PLAN_PHASE*.md** - Specific commits for your phase
4. **REPLAY_STATUS.md** - Current status, gate criteria
5. **INFRASTRUCTURE_SAFEGUARDS.md** - Snapshot procedures, rollback process

### For DevOps (Operations)
1. **UPSTREAM_DEPLOYMENT_PREREQUISITES.md** - Phase 0 complete guide, troubleshooting
2. **PROXMOX_CLUSTER_INTEGRATION.md** - Cluster attachment and management
3. **INFRASTRUCTURE_SAFEGUARDS.md** - Snapshot rotation, disaster recovery
4. **OPENCODE_RULES.md** - Operational guidelines
5. **REPLAY_STATUS.md** - Current deployments, snapshots

### For Security Review
1. **PHASE12_SECURITY_CHECKPOINT.md** - Pre-HTTPS audit checklist
2. **OPENCODE_RULES.md** - Credential handling, safety procedures
3. **INFRASTRUCTURE_SAFEGUARDS.md** - Rollback/recovery safety

### For Project Management
1. **REPLAY_STATUS.md** - Current phase, deliverables, blockers
2. **REPLAY_SUMMARY.md** - High-level overview of all work
3. **FORK_STRATEGY.md** - Implementation timeline and effort estimates

---

## Critical Knowledge Points

### Configuration Management
**Reference:** UPSTREAM_DEPLOYMENT_PREREQUISITES.md (Configuration Changes Summary)

Only 2 env var changes needed:
- `VITE_API_URL=http://192.168.2.186:8000/api/v1` (frontend)
- `CORS_ORIGINS=...http://192.168.2.186:3000` (api)

NO source code changes, NO database schema changes.

### Issue Resolution Patterns
**Reference:** UPSTREAM_DEPLOYMENT_PREREQUISITES.md (Troubleshooting Reference)

Common issues & solutions:
1. Can't reach API → Check VITE_API_URL, container running, health endpoint
2. CORS errors → Check CORS_ORIGINS, confirm origin in allowlist
3. docker-compose failures → Use `docker system prune -a --volumes -f`
4. Container won't start → Rebuild image, check logs

### Snapshot Strategy
**Reference:** INFRASTRUCTURE_SAFEGUARDS.md

- Keep 2-3 active snapshots (rotate out old ones)
- Name format: `snapshot-phase-X-batch-Y-tested`
- Create after every batch (testing barrier)
- Store in REPLAY_STATUS.md log

### Fork & Branch Strategy
**Reference:** FORK_STRATEGY.md

Before Phase 1:
1. Fork upstream: `anomalyco/cloudforproxmox-upstream`
2. Add remote: `git remote add upstream <fork-url>`
3. Use branches: `phase-X-batch-Y`
4. Tag each batch: `phase-X-batch-Y-tested`
5. Push branches & tags to origin

### Pre-HTTPS Audit
**Reference:** PHASE12_SECURITY_CHECKPOINT.md

Before attempting Phase 12 (HTTPS commits):
- [ ] Certificate generation verified
- [ ] Secret management audit
- [ ] TLS endpoint testing
- [ ] Downtime acceptable (migration window)

---

## Quick Reference: File Locations

```
~/github/cloudforproxmox/
├── UPSTREAM_DEPLOYMENT_PREREQUISITES.md (Phase 0 guide ⭐)
├── FORK_STRATEGY.md (Phase 1+ strategy ⭐)
├── REPLAY_STATUS.md (Current status)
├── REPLAY_PLAN_PHASE0-1.md (Setup commits)
├── REPLAY_PLAN_PHASE2-3.md (Network commits)
├── REPLAY_PLAN_PHASE4-5.md (Multi-Tenant commits)
├── REPLAY_PLAN_PHASE8-9.md (Audit/Billing commits)
├── REPLAY_PLAN_PHASE12.md (HTTPS commits)
├── REPLAY_INDEX.md (Commit search)
├── REPLAY_SUMMARY.md (Overview)
├── INFRASTRUCTURE_SAFEGUARDS.md (Operations)
├── OPENCODE_RULES.md (Policies)
├── OPENCODE_ASSESSMENT.md (Capabilities)
├── PHASE12_SECURITY_CHECKPOINT.md (Security audit)
├── DOCUMENTATION_INDEX.md (This file)
├── docker-compose.yml (Config: VITE_API_URL, CORS_ORIGINS)
├── backend/ (Source code)
├── frontend/ (Source code)
└── infra/ (Infrastructure scripts)

Reference (read-only):
~/github/proxmox-isp/ (cloudforproxmox-old, commit source)
```

---

## Snapshots

All snapshots on vm103 (pve2, 192.168.2.186):

| Name | State | Date | Purpose |
|------|-------|------|---------|
| snapshot-upstream-working | containers up | 2026-05-28 21:04:59 | Baseline (before CORS fix) |
| **snapshot-upstream-final-cors-fixed** ⭐ | ✅ LOGIN VERIFIED | 2026-05-28 21:19:14 | Phase 0 baseline (ready for Phase 1) |
| (phase-1-batch-*) | TBD | TBD | Phase 1 batches (to be created) |
| ... | TBD | TBD | ... |

---

## Useful Commands

### Setup Two-Repo Model (One-Time)
```bash
# Clone fork (primary code)
git clone https://github.com/anomalyco/cloudforproxmox-upstream ~/github/cloudforproxmox-upstream

# Clone orchestration repo (docs/tracking)
git clone https://github.com/anomalyco/cloudforproxmox ~/github/cloudforproxmox

# In fork, verify upstream remote
cd ~/github/cloudforproxmox-upstream
git remote add upstream https://github.com/proxmox-cloudportal/cloud-platform
git fetch upstream
git log --oneline --all | head -20
```

### Check Current Deployment Status
```bash
# Which batch is currently deployed?
cat ~/github/cloudforproxmox/REPLAY_STATUS.md | grep "Current"

# Verify on vm103
ssh peppe@192.168.2.186 "cd /home/peppe/cloud-platform-upstream && git branch -v"

# Check containers
ssh peppe@192.168.2.186 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

### Create Batch Branch (Per-Batch Workflow)
```bash
cd ~/github/cloudforproxmox-upstream

# Create and checkout branch
git checkout -b phase-1-batch-1

# Cherry-pick commits (example: 7c1ae38 to 7c2b456)
git cherry-pick 7c1ae38^..7c2b456

# View commits in batch
git log --oneline upstream/main..phase-1-batch-1

# After testing, tag
git tag -a phase-1-batch-1-tested -m "Tested on vm103"
git push origin phase-1-batch-1 phase-1-batch-1-tested
```

### Test Batch on vm103
```bash
ssh peppe@192.168.2.186 "
  cd /home/peppe/cloud-platform-upstream && \
  git fetch origin && \
  git checkout phase-1-batch-1 && \
  docker-compose up -d && \
  sleep 15 && \
  docker ps --format 'table {{.Names}}\t{{.Status}}' && \
  curl -s http://192.168.2.186:8000/api/v1/health/detailed | jq .status
"
```

### Update Status in Orchestration Repo
```bash
cd ~/github/cloudforproxmox

# Edit REPLAY_STATUS.md to mark batch as complete
# Update: Branch, Snapshot, Tag, Date

git add REPLAY_STATUS.md
git commit -m "status: phase-1-batch-1 tested and verified

Branch: phase-1-batch-1 (commits 7c1ae38...7c2b456)
Snapshot: snapshot-phase-1-batch-1-tested
Tests: ✅ All containers healthy, login verified"

git push origin main
```

### Rollback to Previous Batch (If Needed)
```bash
cd ~/github/cloudforproxmox-upstream

# Check commit to revert
git log --oneline phase-1-batch-2 | head -5

# Revert bad commit
git revert <bad-commit-hash>
git push origin phase-1-batch-2-revised

# On vm103, switch back to previous batch
ssh peppe@192.168.2.186 "
  cd /home/peppe/cloud-platform-upstream && \
  git checkout phase-1-batch-1 && \
  docker-compose up -d
"
```

### View Which Phase Contains a Commit
```bash
cd ~/github/cloudforproxmox-upstream
git branch -a --contains 7c1ae38
# Output: phase-1-batch-1

# Or search all branches
git log --all --oneline | grep "specific message"
```

### List All Batch Tags
```bash
cd ~/github/cloudforproxmox-upstream
git tag | grep phase | sort
```

---

## Document Maintenance

**When to Update:**
- After each completed batch: update REPLAY_STATUS.md
- After phase complete: mark in REPLAY_STATUS.md
- After snapshot: add to snapshot log
- After new issue: add to troubleshooting section

**What NOT to Change:**
- REPLAY_PLAN_PHASE*.md (reference, locked after creation)
- REPLAY_INDEX.md (commit list, locked)
- UPSTREAM_DEPLOYMENT_PREREQUISITES.md (historical record)

**What to Update:**
- REPLAY_STATUS.md (current status, batches, blockers)
- REPLAY_SUMMARY.md (if major changes)
- FORK_STRATEGY.md (if process changes)

---

## Abbreviations Used

- **vm103** = virtual machine ID 103 on pve2 (192.168.2.186)
- **pve2** = Proxmox VE node 2 (hypervisor)
- **LXC** = Linux Container (not used, VM-only)
- **QM** = QEMU Management (Proxmox VM tools)
- **CORS** = Cross-Origin Resource Sharing (browser security)
- **VITE** = Frontend build tool environment variables
- **Batch** = Group of related commits replayed together
- **Snapshot** = VM disk state at point in time (recovery point)
- **Phase** = Group of related features (12 phases total)
- **Replay** = Applying historical commits to clean baseline

---

## Support & References

**Project References:**
- Upstream: https://github.com/proxmox-cloudportal/cloud-platform
- Fork (to create): https://github.com/anomalyco/cloudforproxmox-upstream (TBD)
- Main dev repo: https://github.com/anomalyco/cloudforproxmox

**VM Access:**
- SSH: `ssh peppe@192.168.2.186` (password: TestDit1234_)
- Proxmox console: pve2 → vm103

**Running Services:**
- Frontend: http://192.168.2.186:3000
- API: http://192.168.2.186:8000/api/v1
- Flower (Celery): http://192.168.2.186:5555

---

## Document History

| Date | Event | Files |
|------|-------|-------|
| 2026-05-28 | Phase 0 Upstream Deployment Complete | UPSTREAM_DEPLOYMENT_PREREQUISITES.md, FORK_STRATEGY.md, REPLAY_STATUS.md (updated) |
| 2026-05-28 | Documentation Index Created | DOCUMENTATION_INDEX.md |
| Earlier | REPLAY_PLAN_PHASE*.md created | 5 phase files with 303 commits documented |
| Earlier | INFRASTRUCTURE_SAFEGUARDS.md created | Operations procedures |
| Earlier | OPENCODE_*.md created | Guidelines and assessment |

---

**This document is a living navigation guide. Bookmark and reference when starting/resuming work.**

Last updated: 2026-05-28 by OpenCode agent  
Phase 0 status: ✅ COMPLETE  
Phase 1 gate: Fork upstream (action item)
