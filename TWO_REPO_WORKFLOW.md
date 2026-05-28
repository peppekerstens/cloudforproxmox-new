# Two-Repo Workflow: Fork + Orchestration Architecture

**Effective Date:** May 28, 2026  
**Status:** ✅ DECIDED (Option 2: Fork Upstream)  
**Scope:** Phase 1-12 replay (303 commits across 12 phases)

---

## Overview: The Two-Repo Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB (Public)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  anomalyco/cloudforproxmox-upstream (FORK - PRIMARY CODE)      │
│  ├─ upstream/main (pristine from proxmox-cloudportal)           │
│  ├─ phase-1-batch-1 (commits 7c1ae38...7c2b456, TESTED)        │
│  ├─ phase-1-batch-2 (next commits, TESTED)                     │
│  ├─ phase-2-batch-1 (etc, TESTED)                              │
│  └─ phase-12-complete (target: 2ca9e1b or 040259b)             │
│                                                                   │
│  anomalyco/cloudforproxmox (ORCHESTRATION - TRACKING ONLY)     │
│  ├─ REPLAY_PLAN_PHASE*.md (what commits to apply)              │
│  ├─ REPLAY_STATUS.md (current status, blockers)                │
│  ├─ TWO_REPO_WORKFLOW.md (this file, procedure)                │
│  ├─ FORK_STRATEGY.md (decision rationale)                      │
│  ├─ DEPLOYMENT_TRACKING.md (maps vm103 to fork branches)       │
│  └─ DOCUMENTATION_INDEX.md (navigation guide)                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
        │                                    │
        │ git clone, pull, checkout branch   │ git clone, pull, status update
        ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VM103 (Deployment)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  /home/peppe/cloud-platform-upstream/                          │
│  (checked out from fork, branch per batch)                      │
│  ├─ origin → anomalyco/cloudforproxmox-upstream                │
│  └─ docker-compose up -d (tests container state)               │
│                                                                   │
│  Snapshots:                                                      │
│  ├─ snapshot-upstream-final-cors-fixed (baseline)              │
│  ├─ snapshot-phase-1-batch-1-tested (after batch 1)            │
│  ├─ snapshot-phase-1-batch-2-tested (after batch 2)            │
│  └─ ... (one per batch, max 3 active per INFRASTRUCTURE_SAFEGUARDS) │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

### Fork (Primary Code): `anomalyco/cloudforproxmox-upstream`

**Purpose:** Authentic git history of all 303 replay commits

**Branches:**
```
upstream/main
├─ pristine upstream code (never touch)
├─ tag: upstream-fork-point (7c1ae38, marks divergence)

phase-1-batch-1
├─ commits: 7c1ae38...7c2b456 (from REPLAY_PLAN_PHASE0-1.md)
├─ tested: ✅
├─ snapshot: snapshot-phase-1-batch-1-tested
├─ tag: phase-1-batch-1-tested (git tag, pushed)

phase-1-batch-2
├─ commits: (next batch after phase-1-batch-1)
├─ tested: ✅
├─ snapshot: snapshot-phase-1-batch-2-tested
├─ tag: phase-1-batch-2-tested

... (repeat for all phases)

phase-12-complete
├─ target: 2ca9e1b (HTTPS working) OR 040259b (HTTPS failure)
├─ tag: phase-12-complete-target
```

**Commits in Fork:**
- Authentic (same as upstream, if cherry-picked)
- Traceable (can see `git log --oneline` and identify each batch)
- Reproducible (anyone can `git checkout phase-1-batch-1` and build)
- Verifiable (tags mark tested states)

### Orchestration Repo (Secondary): `anomalyco/cloudforproxmox`

**Purpose:** Planning, tracking, and documentation of the replay process

**Files:**
```
cloudforproxmox-new/
├─ REPLAY_PLAN_PHASE0-1.md (what commits in phase 1)
├─ REPLAY_PLAN_PHASE2-3.md (what commits in phase 2-3)
├─ REPLAY_PLAN_PHASE4-5.md (what commits in phase 4-5)
├─ REPLAY_PLAN_PHASE8-9.md (what commits in phase 8-9)
├─ REPLAY_PLAN_PHASE12.md (what commits in phase 12)
│
├─ REPLAY_STATUS.md (current status, which batch deployed)
├─ REPLAY_INDEX.md (searchable commit index)
├─ REPLAY_SUMMARY.md (high-level overview)
│
├─ UPSTREAM_DEPLOYMENT_PREREQUISITES.md (phase 0 guide)
├─ FORK_STRATEGY.md (why we chose fork approach)
├─ TWO_REPO_WORKFLOW.md (this file, how to use both repos)
├─ DEPLOYMENT_TRACKING.md (maps vm103 state to fork branches) ← NEW
│
├─ INFRASTRUCTURE_SAFEGUARDS.md (snapshot procedures)
├─ OPENCODE_RULES.md (operational guidelines)
├─ OPENCODE_ASSESSMENT.md (capability assessment)
├─ PHASE12_SECURITY_CHECKPOINT.md (HTTPS security audit)
│
├─ DOCUMENTATION_INDEX.md (master navigation)
│
├─ .git/ (version control of docs/status only)
└─ .gitignore (no code files in this repo)
```

**NOT in Orchestration Repo (anymore):**
- ❌ backend/ (source code)
- ❌ frontend/ (source code)
- ❌ docker-compose.yml (now only in fork)

**Commits in Orchestration Repo:**
- Status updates (after each batch)
- Documentation changes
- Decision records
- Tracking only (no code changes)

---

## Per-Batch Workflow

### Phase 1, Batch 1: Complete Example

#### Step 1: Identify Commits (Using REPLAY_PLAN_PHASE0-1.md)

```bash
# In cloudforproxmox-new repo:
grep -A 50 "## Batch 1" REPLAY_PLAN_PHASE0-1.md

# Output (example):
# Batch 1 (10 commits: Setup Infrastructure)
# - 7c1ae38 commit message 1
# - 7c1ae39 commit message 2
# ... (8 more)
# - 7c2b456 commit message 10
```

#### Step 2: Create Branch in Fork

```bash
cd ~/github/cloudforproxmox-upstream

# Create branch for batch
git checkout -b phase-1-batch-1

# Cherry-pick commits from upstream (or apply manually per REPLAY_PLAN)
git cherry-pick 7c1ae38^..7c2b456
# OR:
# Manual edits following REPLAY_PLAN_PHASE0-1.md diffs
```

#### Step 3: Test on vm103

```bash
# On vm103:
cd /home/peppe/cloud-platform-upstream

# Fetch new branch
git fetch origin

# Checkout batch branch
git checkout phase-1-batch-1

# Restore from baseline snapshot if not already
qm snapshot 103 -restore snapshot-upstream-final-cors-fixed  # (from pve2)

# Bring up containers
docker-compose up -d

# Wait for startup
sleep 15

# Test
## 1. Check containers
docker ps --format 'table {{.Names}}\t{{.Status}}'

## 2. Check API
curl -s http://192.168.2.186:8000/api/v1/health/detailed | jq

## 3. Test login
curl -s -X POST http://192.168.2.186:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"TestDit1234_"}' | jq

## 4. Check frontend
curl -s http://192.168.2.186:3000 | head -20

# Additional tests per batch (see REPLAY_PLAN_PHASE0-1.md "Testing" section)
# ... phase-specific tests ...
```

#### Step 4: Verify & Snapshot

```bash
# If all tests pass:

# From pve2:
qm snapshot 103 snapshot-phase-1-batch-1-tested \
  -description "Batch 1 (commits 7c1ae38...7c2b456) tested and verified"

# Verify
qm listsnapshot 103 | grep phase-1-batch-1-tested
```

#### Step 5: Tag in Fork

```bash
cd ~/github/cloudforproxmox-upstream

# Tag tested batch
git tag -a phase-1-batch-1-tested -m "Batch 1 (10 commits: Setup) tested on vm103, snapshot-phase-1-batch-1-tested verified"

# Push branch and tag
git push origin phase-1-batch-1
git push origin phase-1-batch-1-tested
```

#### Step 6: Update Orchestration Repo

```bash
cd ~/github/cloudforproxmox

# Update REPLAY_STATUS.md
# Edit:
# ### Phase 1, Batch 1: Setup Infrastructure
# Status: ✅ COMPLETE
# Branch: phase-1-batch-1 (https://github.com/anomalyco/cloudforproxmox-upstream)
# Commits: 7c1ae38...7c2b456 (10 commits)
# Snapshot: snapshot-phase-1-batch-1-tested
# Tag: phase-1-batch-1-tested
# Verified: 2026-05-28 by OpenCode

# Commit status update
git add REPLAY_STATUS.md
git commit -m "status: phase-1-batch-1 tested and verified

Batch 1 of Phase 1 (Setup Infrastructure):
- Commits: 7c1ae38...7c2b456 (10 commits)
- Fork: anomalyco/cloudforproxmox-upstream
- Branch: phase-1-batch-1
- Snapshot: snapshot-phase-1-batch-1-tested
- Tests: ✅ All containers healthy, login verified
- Tag: phase-1-batch-1-tested (pushed to fork)

Ready for batch 2."

git push origin main
```

#### Step 7: Begin Next Batch

```bash
# Back to fork, create branch for batch 2
cd ~/github/cloudforproxmox-upstream

git checkout -b phase-1-batch-2

# Cherry-pick next batch commits from REPLAY_PLAN
# ... repeat workflow ...
```

---

## Git Commands Reference

### Setup (One-Time)

```bash
# Clone both repos
git clone https://github.com/anomalyco/cloudforproxmox-upstream ~/github/cloudforproxmox-upstream
git clone https://github.com/anomalyco/cloudforproxmox ~/github/cloudforproxmox

# In fork, add upstream as remote
cd ~/github/cloudforproxmox-upstream
git remote add upstream https://github.com/proxmox-cloudportal/cloud-platform
git fetch upstream

# Verify
git log --oneline --all | head -20
# Should show upstream/main, upstream/refs...
```

### Per-Batch Commands

```bash
# Create batch branch
git checkout -b phase-X-batch-Y
git cherry-pick <commit-range>

# Test locally (dry-run)
git show <commit>  # Review what changed
git log --oneline <previous-branch>..<current-branch>  # See batch commits

# After testing on vm103, tag
git tag -a phase-X-batch-Y-tested -m "Description"
git push origin phase-X-batch-Y
git push origin --tags

# View all batches
git branch -a | grep phase
git tag | sort

# If batch fails, revert
git revert <bad-commit>  # Creates new commit undoing changes
git push origin phase-X-batch-Y-revised
```

### Maintenance

```bash
# Find which batch changed a file
git log --oneline --all -- <filename> | head -20

# Find commit in which phase
git log --oneline upstream/main..main | grep <commit-hash>
# or
git branch -a --contains <commit-hash>

# Diff fork vs upstream
git diff upstream/main..main --stat
```

---

## Snapshot Rotation Strategy

**Reference:** INFRASTRUCTURE_SAFEGUARDS.md

**Active Snapshots (Keep 2-3):**
```
Max 3 active at a time:
├─ snapshot-upstream-final-cors-fixed (baseline, never delete)
├─ snapshot-phase-1-batch-1-tested (current batch)
└─ snapshot-phase-1-batch-2-tested (previous batch, for rollback)

When phase-1-batch-3 tested:
├─ Delete snapshot-upstream-final-cors-fixed? NO, keep as ultimate baseline
├─ Delete snapshot-phase-1-batch-1-tested? YES (delete oldest non-baseline)
└─ Current active: batch-2 and batch-3
```

**Why:** Thin pool in Proxmox has space limits. Strategy documented in INFRASTRUCTURE_SAFEGUARDS.md.

---

## Status Tracking in Orchestration Repo

### REPLAY_STATUS.md Structure (Updated)

```markdown
## Phase 1: Setup & Foundation

### Batch 1: Setup Infrastructure (10 commits)
- Status: ✅ COMPLETE
- Fork Branch: phase-1-batch-1
- Commits: 7c1ae38...7c2b456
- Fork Link: https://github.com/anomalyco/cloudforproxmox-upstream/tree/phase-1-batch-1
- VM Snapshot: snapshot-phase-1-batch-1-tested
- Git Tag: phase-1-batch-1-tested
- Tested: 2026-05-28
- Notes: All containers healthy, login verified

### Batch 2: Load Balancing (12 commits)
- Status: ⏳ IN PROGRESS
- Fork Branch: phase-1-batch-2
- Commits: 7c2b457...7c3b999
- Fork Link: (pending)
- VM Snapshot: (pending)
- Git Tag: (pending)
- Tested: (pending)
```

### DEPLOYMENT_TRACKING.md (New File)

Maps vm103 state to fork branches:

```markdown
## Current Deployment State

### VM103 (192.168.2.186)
- Current Branch: phase-1-batch-1
- Current Snapshot: snapshot-phase-1-batch-1-tested
- Containers: 8/8 healthy (as of 2026-05-28 21:30 UTC)
- API: ✅ Responding
- Frontend: ✅ Accessible
- Login: ✅ Verified

### Fork Branch Status

| Branch | Status | Commits | Snapshot | Tag | Date |
|--------|--------|---------|----------|-----|------|
| phase-1-batch-1 | ✅ TESTED | 7c1ae38...7c2b456 | phase-1-batch-1-tested | ✅ | 2026-05-28 |
| phase-1-batch-2 | ⏳ IN PROGRESS | 7c2b457...7c3b999 | — | — | — |
| phase-2-batch-1 | 📍 PLANNED | TBD | — | — | — |
```

---

## Key Differences: Fork vs Orchestration Repo

| Aspect | Fork Repo | Orchestration Repo |
|--------|-----------|-------------------|
| **Purpose** | Authentic code history | Planning & tracking |
| **Content** | Source code + docker-compose.yml | Docs, REPLAY_PLAN, status |
| **Git Commits** | Upstream commits (replay) | Status updates only |
| **Branches** | phase-X-batch-Y per batch | main (tracking only) |
| **Tags** | phase-X-batch-Y-tested (critical) | None |
| **Push Frequency** | After each batch (weekly) | Daily (status updates) |
| **Access** | By developers (code changes) | By everyone (tracking) |
| **CI/CD** | Tests run in fork per branch | Status queries only |
| **Reproducibility** | Can checkout any batch | Refers to fork for actual state |

---

## Why This Works

1. **Fork = Source of Truth** 
   - Git commits are authentic
   - Anyone can reproduce: `git checkout phase-1-batch-1`
   - Full history traceable

2. **Orchestration Repo = Team Coordination**
   - Status clear (who's working on what)
   - No code confusion (single source in fork)
   - Lightweight (docs only)

3. **Two-Repo Separation of Concerns**
   - Fork: "What code is running?"
   - Orchestration: "Where are we in the replay?"
   - Clear roles, no mixing

4. **Scalable to Teams**
   - Multiple devs can work on different batches in fork
   - Orchestration repo tracks unified status
   - No conflicts

5. **Archival & Reproducibility**
   - In 2027, can checkout `phase-5-batch-3` and know exactly what was running
   - Git history unchanged (authentic)
   - REPLAY_PLAN files frozen (documenting intent)

---

## Common Workflows

### "Where is the code currently running?"
```bash
# Check REPLAY_STATUS.md in orchestration repo
cat REPLAY_STATUS.md | grep "Current"
# Output: Currently deployed: phase-1-batch-2

# Verify on vm103
ssh peppe@192.168.2.186 "cd /home/peppe/cloud-platform-upstream && git branch"
# Output: * phase-1-batch-2

# See exact commits
cd ~/github/cloudforproxmox-upstream
git log --oneline upstream/main..phase-1-batch-2
```

### "What changed in batch 3?"
```bash
cd ~/github/cloudforproxmox-upstream
git diff phase-1-batch-2..phase-1-batch-3

# Or see commits only
git log --oneline phase-1-batch-2..phase-1-batch-3
```

### "Roll back if batch 3 fails"
```bash
# On vm103
cd /home/peppe/cloud-platform-upstream
git checkout phase-1-batch-2  # Back to working state
docker-compose up -d

# In orchestration repo
cd ~/github/cloudforproxmox
# Edit REPLAY_STATUS.md: mark batch 3 as FAILED
git add REPLAY_STATUS.md
git commit -m "status: phase-1-batch-3 FAILED - rolled back to batch 2"
```

### "See which batch added feature X"
```bash
# In fork
cd ~/github/cloudforproxmox-upstream
git log --all --oneline | grep "feature X"

# Or search commits
git log --all -S "feature X" --oneline | head -5
```

---

## Handoff to Phase 1 Team

**Before Phase 1 Begins:**

1. ✅ Fork created: `anomalyco/cloudforproxmox-upstream`
2. ✅ Orchestration repo ready: `anomalyco/cloudforproxmox`
3. ✅ REPLAY_PLAN_PHASE0-1.md has 303 commits documented
4. ✅ DEPLOYMENT_TRACKING.md template ready
5. ✅ Baseline snapshot: `snapshot-upstream-final-cors-fixed`
6. ✅ First batch identified (commits 7c1ae38...~10 commits)
7. ✅ This document explains workflow

**Developer Checklist:**
- [ ] Clone fork: `git clone <fork-url>`
- [ ] Add upstream remote: `git remote add upstream <proxmox-cloudportal>`
- [ ] Clone orchestration repo: `git clone <orchestration-url>`
- [ ] Read REPLAY_PLAN_PHASE0-1.md for batch 1
- [ ] Read this document (TWO_REPO_WORKFLOW.md)
- [ ] Create phase-1-batch-1 branch and begin replay

---

## References

- **FORK_STRATEGY.md** - Why we chose this approach
- **REPLAY_PLAN_PHASE0-1.md** - What commits to apply in Phase 1
- **REPLAY_STATUS.md** - Current status, blocker tracking
- **INFRASTRUCTURE_SAFEGUARDS.md** - Snapshot procedures
- **DEPLOYMENT_TRACKING.md** - Maps vm103 state to branches (created per-batch)
- **DOCUMENTATION_INDEX.md** - Master navigation guide

---

## Summary

**Two-Repo Model:**
1. Fork (anomalyco/cloudforproxmox-upstream): Code, branches, tags, authentic history
2. Orchestration (anomalyco/cloudforproxmox): Docs, status, tracking, decision records

**Per-Batch Workflow:**
1. Create branch in fork (phase-X-batch-Y)
2. Apply commits per REPLAY_PLAN_PHASE*.md
3. Test on vm103 (all containers, login, features)
4. Create snapshot (phase-X-batch-Y-tested)
5. Tag in fork (phase-X-batch-Y-tested)
6. Update REPLAY_STATUS.md in orchestration repo
7. Commit status update
8. Repeat for next batch

**Result:** 303 commits replayed with authentic git history, full traceability, reproducibility, and team coordination.
