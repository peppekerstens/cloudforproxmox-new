# Fork Strategy: Two-Repo Architecture for 303-Commit Replay

**Status:** ✅ DECIDED (Option 2 Selected)  
**Decision Date:** May 28, 2026  
**Rationale:** Authentic git history, reproducibility, traceability, maintainability  
**Impact:** Core architecture for entire Phase 1-12 replay

---

## Current Problem: Read-Only Reference Model

### Setup Today
```
cloudforproxmox-old (~/github/proxmox-isp)
  └─ Read-only reference copy of upstream
  └─ Contains commits 7c1ae38...2ca9e1b (fork point to target)

cloudforproxmox-new (~/github/cloudforproxmox)
  └─ Development repo with upstream code
  └─ Manual cherry-pick of commits from cloudforproxmox-old
  └─ Git history: [upstream commit] + [REPLAY_PLAN docs] + [manual replays]
```

### Risks
1. **Manual error-prone process**
   - Replaying 303 commits across 12 phases manually = high error rate
   - Easy to miss commits, apply partial diffs, or double-apply
   - No automated verification of replay correctness

2. **Lost traceability**
   - If we diverge from upstream, unclear what's added vs what came from fork
   - git log shows mix of upstream and replay commits, no clear story
   - Hard for new developers to understand intent

3. **No rollback safety**
   - Can't `git revert` because commits aren't authentic
   - Must manually undo changes
   - Snapshot rollback is only safety net (fragile)

4. **CI/CD unfriendly**
   - Can't run tests against specific replay phases
   - Can't tag releases cleanly
   - Difficult to maintain parallel branches

5. **Maintainability nightmare**
   - After replay complete, unclear how to merge future upstream changes
   - Merge conflicts likely
   - No clear base for feature branches

---

## Recommended Solution: Upstream Fork

### New Setup
```
anomalyco/cloudforproxmox-upstream (official fork on GitHub)
  └─ Exact copy of proxmox-cloudportal/cloud-platform
  └─ Baseline for all development
  └─ Tracks upstream for future merges

cloudforproxmox-new (development repo)
  ├─ Remote: upstream = anomalyco/cloudforproxmox-upstream
  ├─ Remote: origin = anomalyco/cloudforproxmox (main development)
  └─ Git history:
      ├─ upstream/main (pristine upstream)
      ├─ phase-1-batch-1 (commits 7c1ae38...7c2b456 replayed)
      ├─ phase-1-batch-2 (next batch)
      ├─ phase-2-batch-1 (phase 2 commits)
      └─ ... (clean, traceable branches)
```

### Benefits

#### 1. **Clean Git History**
```bash
$ git log --oneline --graph upstream/main..main

* abc1234 phase-12-final: replayed final commits 2ca5e1a...2ca9e1b
* abc1233 phase-12-batch-1: replayed commits 2c91e1a...2ca5e1a
* abc1232 phase-11-batch-2: replayed commits 2b51e1a...2c91e1a
...
* upstream-fork-point UPSTREAM: forked from proxmox-cloudportal (7c1ae38)
```

#### 2. **Traceability**
- Each phase/batch is a clean branch tag
- Commit messages indicate replay phase
- Easy to see divergence from upstream
- `git diff upstream/main..main` shows all changes added during replay

#### 3. **Reproducibility**
- Can checkout exact replay state: `git checkout phase-1-batch-1-tested`
- Can verify against snapshot: "Phase 1 Batch 1 replayed, tested, snapshot taken"
- Future developers can run tests against any phase

#### 4. **Safety**
```bash
# If replay goes wrong midway:
git revert <bad-commit>  # Clean revert, clear history
git tag phase-1-batch-1-failed

# Vs. current:
# Manual undo, unclear what's broken, snapshot rollback (slow)
```

#### 5. **Future-Proof**
- Easy to merge upstream updates: `git merge upstream/main`
- Conflict resolution visible in git history
- Feature branches can diverge from specific replay phase
- Release tags meaningful: `v1.0.0-phase-1-complete`

---

## Implementation Plan

### Step 1: Create Fork (One-Time)
```bash
# On GitHub:
# 1. Fork proxmox-cloudportal/cloud-platform
# 2. Name it: anomalyco/cloudforproxmox-upstream
# 3. Set as public (reference, no write needed from main repo)
```

### Step 2: Update cloudforproxmox-new Remotes
```bash
cd ~/github/cloudforproxmox

# Add upstream fork as remote
git remote add upstream https://github.com/anomalyco/cloudforproxmox-upstream

# Verify
git remote -v
# origin   https://github.com/anomalyco/cloudforproxmox
# upstream https://github.com/anomalyco/cloudforproxmox-upstream

# Fetch upstream
git fetch upstream

# View where we are relative to upstream
git log --oneline --graph --all | head -20
```

### Step 3: Phase 1 Workflow

```bash
# Start Phase 1
git checkout -b phase-1-batch-1

# Manually replay commits (or use git cherry-pick if from upstream):
# Option A: Cherry-pick from upstream
git cherry-pick 7c1ae38^..7c2b456

# Option B: Manual edits (following REPLAY_PLAN_PHASE0-1.md)
# ... apply diffs manually ...

# Test batch locally:
cd /home/peppe/cloud-platform-upstream
# ... restore from snapshot-upstream-final-cors-fixed ...
# ... apply phase-1-batch-1 changes ...
# ... test all 8 containers, login, etc ...

# Commit batch
git add -A
git commit -m "phase-1-batch-1: replayed commits 7c1ae38...7c2b456

Batch 1 of Phase 1 (Proxmox Integration - Infrastructure).
Commits replayed from upstream fork.
Tested: all containers healthy, login verified.
Snapshot: phase-1-batch-1-tested

See REPLAY_PLAN_PHASE0-1.md for details."

# Tag batch
git tag phase-1-batch-1-tested

# Push to origin
git push origin phase-1-batch-1
git push origin --tags
```

### Step 4: Continue Through All Phases
- Repeat Step 3 for each batch in REPLAY_PLAN_PHASE*.md
- Each batch gets its own branch and tag
- Each snapshot named: `phase-X-batch-Y-tested`
- Each phase gate: `all-tests-pass && snapshot-verified`

### Step 5: Final State
```bash
# After all 12 phases replayed (303 commits):
git log --oneline --all | head -15

* 2ca9e1b phase-12-batch-3: final commits (HTTPS working)
* 2ca5e1a phase-12-batch-2: HTTPS prep
* 2b91e1a phase-12-batch-1: cert generation
* ...
* 7c1ae38 UPSTREAM: fork point from proxmox-cloudportal
*         (pristine upstream commits before 7c1ae38)
```

---

## Branch Naming Convention

```
main/
  └─ Development mainline (after Phase 1+)

phase-X-batch-Y/
  └─ Temporary branch for replay of phase X, batch Y
  └─ Deleted after merge to main (keep clean history)
  └─ Tagged as: phase-X-batch-Y-tested

upstream/
  └─ Remote branch (read-only reference)
  └─ Never commit directly, only fetch

Feature branches (post-replay):
  feature/proxy-support
  feature/api-v2
  bugfix/cors-edge-case
  └─ Branch from specific replay phase if needed
```

---

## Snapshot Naming Consistency

Align VM snapshots with git tags:

| Git | Snapshot | Purpose |
|-----|----------|---------|
| `7c1ae38` (fork point) | `snapshot-upstream-final-cors-fixed` | Baseline (Phase 0) |
| `phase-1-batch-1-tested` | `snapshot-phase-1-batch-1-tested` | Phase 1 Batch 1 verified |
| `phase-1-batch-2-tested` | `snapshot-phase-1-batch-2-tested` | Phase 1 Batch 2 verified |
| ... | ... | ... |
| `2ca9e1b` (target) | `snapshot-phase-12-complete-https-working` | Final state (Phase 12) |

---

## Decision: OPTION 2 SELECTED ✅

### What Was Evaluated

**Option 1: Revert & Restart (Single Repo)**
- Revert da8053e, apply 303 commits manually into cloudforproxmox-new
- ❌ Git history inauthentic, not reproducible, high error risk
- ❌ Can't `git checkout phase-1` and get exact state
- ❌ Doesn't solve traceability problem
- ❌ CI/CD unfeasible
- **Decision: REJECTED**

**Option 2: Fork Upstream (Two-Repo Architecture)** ✅
- Create fork: `anomalyco/cloudforproxmox-upstream` (primary code)
- Keep cloudforproxmox-new as docs/orchestration (secondary tracking)
- ✅ Authentic git history, clean branches per batch
- ✅ Reproducible (anyone can checkout and get exact state)
- ✅ Traceable (know upstream vs added changes)
- ✅ CI/CD ready
- ✅ Safe rollback (git revert, not manual undo)
- **Decision: SELECTED** ✅

### Rationale

- **303 commits deserve authentic history** — not manual application
- **Reproducibility critical** — must validate accuracy per batch
- **Future maintainability** — future developers need git intent
- **Low setup cost** (10 min), high payoff (100+ hours saved)
- **Aligns with 2026 DevOps best practices** (git as single source of truth)

---

## Action Items (Phase 0 → Phase 1 Gate)

**Before Phase 1 Begins:**
- [ ] Create fork on GitHub: `anomalyco/cloudforproxmox-upstream` (5 min)
- [ ] Add fork as remote to cloudforproxmox-new: `git remote add upstream <url>` (1 min)
- [ ] Verify setup: `git fetch upstream; git log --oneline --all` (1 min)
- [ ] Create Phase 1 branch in fork: `phase-1-batch-1` (1 min)
- [ ] Review REPLAY_PLAN_PHASE0-1.md and TWO_REPO_WORKFLOW.md (20 min)

**Total Setup Time:** ~30 minutes

**See Also:** TWO_REPO_WORKFLOW.md for detailed per-batch workflow

---

## Implementation: See TWO_REPO_WORKFLOW.md

This file explains the high-level strategy. For the **detailed per-batch workflow**, including:
- Step-by-step procedure for each batch
- Git commands (create branch, cherry-pick, tag, push)
- Testing procedures on vm103
- Status tracking in orchestration repo
- Snapshot management
- Rollback procedures

**See:** TWO_REPO_WORKFLOW.md

---

## References

- **TWO_REPO_WORKFLOW.md** ← START HERE (per-batch workflow)
- **GitHub Fork Docs:** https://docs.github.com/en/get-started/quickstart/fork-a-repo
- **Git Remote Management:** https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
- **Cherry-Pick Guide:** https://git-scm.com/docs/git-cherry-pick
- **Upstream Tracking:** https://git-scm.com/book/en/v2/Git-Branching-Remote-Branches

---

## Summary

**Problem:** Manual replay from read-only reference (error-prone, untraceable)  
**Solution:** Two-repo architecture
- Fork (anomalyco/cloudforproxmox-upstream): Authentic code history, branches per batch
- Orchestration (anomalyco/cloudforproxmox): Docs, status tracking, decision records

**Benefits:**
✅ Authentic git history (commits preserved exactly)  
✅ Reproducible (checkout branch = exact state)  
✅ Traceable (know upstream vs added changes)  
✅ Safe (git revert instead of manual undo)  
✅ CI/CD ready (can test per branch)  
✅ Scalable (teams can work on different batches)  
✅ Maintainable (future developers understand intent)

**Effort:** ~30 min setup + 2-4 hours per batch (including testing)  
**Scope:** 303 commits across 12 phases  
**Status:** ✅ DECIDED & DOCUMENTED

**Start:** See TWO_REPO_WORKFLOW.md for per-batch procedure
