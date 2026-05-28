# Fork Setup Procedure: Proper Code History & Merging

**Status:** IN PROGRESS - Phase 0 → Phase 1 Preparation  
**Objective:** Create fork with clean git history, proper remotes, and merge workflows  
**Date:** May 28, 2026

---

## Architecture Overview

```
GitHub (Public)
├─ anomalyco/cloudforproxmox-upstream (FORK - TO BE CREATED)
│  ├─ upstream/main (pristine proxmox-cloudportal/cloud-platform)
│  ├─ phase-1-batch-1 (commits 7c1ae38...7c2b456, tested)
│  ├─ phase-1-batch-2 (next batch, tested)
│  └─ phase-12-complete (target: 2ca9e1b or 040259b)
│
└─ anomalyco/cloudforproxmox (ORCHESTRATION - EXISTING)
   ├─ main (docs, status tracking)
   ├─ remotes/upstream → fork (read-only reference)
   └─ remotes/origin → orchestration repo

Local Clones
├─ ~/github/cloudforproxmox-upstream/ (fork, development)
│  └─ Code, branches, git history
│
└─ ~/github/cloudforproxmox/ (orchestration, current)
   └─ REPLAY_PLAN*.md, REPLAY_STATUS.md, docs only
```

---

## Step 1: Create Fork on GitHub

**You need to do this on GitHub UI:**

1. Go to: https://github.com/proxmox-cloudportal/cloud-platform
2. Click **Fork** button (top right)
3. Owner: Select your account (anomalyco or peppekerstens)
4. Repository name: `cloudforproxmox-upstream`
5. Description: "Upstream cloud-platform fork for cloudforproxmox replay"
6. Visibility: Public (so it's findable, mirrors upstream)
7. Copy only main branch: **YES** (we want clean history)
8. Click **Create fork**

**Result:** You now have `https://github.com/anomalyco/cloudforproxmox-upstream`

---

## Step 2: Configure Local Fork Repository

Once fork is created, I'll clone it and set up proper remotes.

**What I'll do:**

```bash
# Clone the fork (as separate repo for code)
git clone https://github.com/anomalyco/cloudforproxmox-upstream ~/github/cloudforproxmox-upstream

# Configure remotes
cd ~/github/cloudforproxmox-upstream

# Remote 1: upstream (pristine reference, read-only)
git remote add upstream https://github.com/proxmox-cloudportal/cloud-platform

# Remote 2: origin (your fork, write access)
# (already set to fork by clone)

# Verify remotes
git remote -v
# Output should show:
# origin   https://github.com/anomalyco/cloudforproxmox-upstream (fetch)
# origin   https://github.com/anomalyco/cloudforproxmox-upstream (push)
# upstream https://github.com/proxmox-cloudportal/cloud-platform (fetch)
# upstream https://github.com/proxmox-cloudportal/cloud-platform (no push)
```

---

## Step 3: Fetch Upstream & Create Tracking Branch

**Purpose:** Establish pristine upstream reference

```bash
cd ~/github/cloudforproxmox-upstream

# Fetch upstream commits
git fetch upstream

# Create tracking branch for upstream main
git branch upstream-main --track upstream/main

# Verify
git branch -a
# Should show:
# * main
#   upstream-main
#   remotes/upstream/main
```

---

## Step 4: Configure Orchestration Repo Remotes

In the current repo (`~/github/cloudforproxmox`), add fork as secondary remote for reference.

```bash
cd ~/github/cloudforproxmox

# Add fork as remote (for tracking batch branches)
git remote add fork https://github.com/anomalyco/cloudforproxmox-upstream

# Verify
git remote -v
# Output:
# origin   https://github.com/anomalyco/cloudforproxmox (fetch)
# origin   https://github.com/anomalyco/cloudforproxmox (push)
# fork     https://github.com/anomalyco/cloudforproxmox-upstream (fetch)
# fork     https://github.com/anomalyco/cloudforproxmox-upstream (no push - read-only)
```

---

## Step 5: Test Remote Connectivity

**Verify all remotes are accessible:**

```bash
# From fork repo
cd ~/github/cloudforproxmox-upstream
git fetch upstream
git fetch origin

# From orchestration repo
cd ~/github/cloudforproxmox
git fetch fork
git fetch origin
```

---

## Git Workflow: Per-Batch Branching & Merging

### Workflow for Each Batch

**In Fork Repo:**

```bash
cd ~/github/cloudforproxmox-upstream

# Step 1: Create batch branch from upstream-main
git checkout upstream-main
git pull upstream main  # Ensure latest
git checkout -b phase-1-batch-1

# Step 2: Apply commits from REPLAY_PLAN
# Option A: Cherry-pick (if commits are identifiable)
git cherry-pick 7c1ae38^..7c2b456

# Option B: Manual application (following REPLAY_PLAN diffs)
# ... make edits according to plan ...

# Step 3: Commit changes
git add .
git commit -m "phase-1-batch-1: setup infrastructure (10 commits)

Replayed commits 7c1ae38...7c2b456 from upstream
See REPLAY_PLAN_PHASE0-1.md for details"

# Step 4: Push to fork
git push origin phase-1-batch-1

# Step 5: After testing, tag
git tag -a phase-1-batch-1-tested \
  -m "Phase 1 Batch 1 tested on vm103
  
Snapshot: snapshot-phase-1-batch-1-tested
All tests passed: containers, login, dashboard"

git push origin phase-1-batch-1-tested
```

**In Orchestration Repo:**

```bash
cd ~/github/cloudforproxmox

# Step 1: Update REPLAY_STATUS.md
# Edit: Mark phase-1-batch-1 as COMPLETE
# Add: Branch: phase-1-batch-1
# Add: Snapshot: snapshot-phase-1-batch-1-tested
# Add: Tag: phase-1-batch-1-tested

# Step 2: Commit status update
git add REPLAY_STATUS.md
git commit -m "status: phase-1-batch-1 tested and verified

Batch 1 of Phase 1 (Setup Infrastructure):
- Fork branch: phase-1-batch-1
- Commits replayed: 7c1ae38...7c2b456 (10 commits)
- VM snapshot: snapshot-phase-1-batch-1-tested
- Git tag: phase-1-batch-1-tested
- Tests: ✅ All containers healthy, login verified
- Status: Ready for Batch 2"

# Step 3: Push status update
git push origin main
```

---

## Merging Strategy (Future Reference)

### When Upstream Updates

If upstream has new commits, we can update our fork:

```bash
cd ~/github/cloudforproxmox-upstream

# Fetch latest upstream
git fetch upstream

# Update upstream-main tracking branch
git checkout upstream-main
git pull upstream main

# Now can base new batches on latest upstream
git checkout -b phase-X-batch-Y
git rebase upstream-main  # If needed to rebase on newer upstream
```

### If Phase Overlaps with Upstream

```bash
# Check for conflicts
git merge upstream/main --no-commit --no-ff

# Resolve conflicts if any
# Re-run tests
# Then commit or abort if issues

git merge --abort  # If problematic
```

---

## Commit Message Convention (Fork)

**For replay commits in fork:**

```
phase-X-batch-Y: <short description> (<number of commits>)

Replayed commits <hash1>...<hash2> from upstream
See REPLAY_PLAN_PHASE<X>.md for batch details

Tested on: vm103 (pve2)
Snapshot: snapshot-phase-X-batch-Y-tested
Status: ✅ All tests passed
```

**Example:**
```
phase-1-batch-1: setup infrastructure (10 commits)

Replayed commits 7c1ae38...7c2b456 from upstream
See REPLAY_PLAN_PHASE0-1.md for batch details

Tested on: vm103 (pve2)
Snapshot: snapshot-phase-1-batch-1-tested
Status: ✅ All containers healthy, login verified
```

---

## Commit Message Convention (Orchestration)

**For status updates in orchestration repo:**

```
status: phase-X-batch-Y <status>

<Batch details>
- Fork branch: phase-X-batch-Y
- Commits: <hash1>...<hash2> (<count> commits)
- Snapshot: snapshot-phase-X-batch-Y-<status>
- Tests: <result>
- Status: <Ready for next batch / BLOCKED / etc>
```

**Example:**
```
status: phase-1-batch-1 tested and verified

Batch 1 of Phase 1 (Setup Infrastructure):
- Fork branch: phase-1-batch-1
- Commits: 7c1ae38...7c2b456 (10 commits)
- Snapshot: snapshot-phase-1-batch-1-tested
- Tests: ✅ All containers healthy, login verified
- Status: Ready for Batch 2
```

---

## Branch Protection & Workflow

### Fork Repo (cloudforproxmox-upstream)

**Branches:**
- `main` — current development baseline (don't push to directly)
- `upstream-main` — pristine upstream reference (never touch)
- `phase-X-batch-Y` — temporary per-batch branches (deleted after testing)

**Tags:**
- `phase-X-batch-Y-tested` — immutable, marks verified states
- `upstream-fork-point` — marks where we diverged from upstream

**Rules:**
- ✅ Can branch from `upstream-main`
- ✅ Can push `phase-X-batch-Y` branches
- ✅ Can push tags
- ❌ Don't force-push (maintain history)
- ❌ Don't rewrite main
- ❌ Don't merge random changes

### Orchestration Repo (cloudforproxmox)

**Branches:**
- `main` — single development branch (status updates only)

**Commits:**
- Status updates only (no code)
- Reference fork branches

**Rules:**
- ✅ Can commit status updates
- ✅ Can push to main
- ❌ No code commits
- ❌ No binary files

---

## Verification Checklist

After setup, verify everything works:

- [ ] Fork created on GitHub
- [ ] Fork cloned locally
- [ ] `origin` points to fork
- [ ] `upstream` points to proxmox-cloudportal/cloud-platform
- [ ] Can fetch from both remotes
- [ ] `upstream-main` tracking branch created
- [ ] Orchestration repo has `fork` remote
- [ ] git log shows clean history (no merge commits)
- [ ] Can view remotes: `git remote -v`
- [ ] Can view branches: `git branch -a`

---

## Testing the Setup

**Test 1: Fetch from upstream**
```bash
cd ~/github/cloudforproxmox-upstream
git fetch upstream
git log --oneline upstream/main | head -5
# Should show latest proxmox-cloudportal commits
```

**Test 2: Create test branch**
```bash
git checkout -b test-branch upstream-main
git log --oneline | head -3
# Should show upstream commits
git checkout main
git branch -D test-branch
```

**Test 3: View all remotes**
```bash
git remote -v
# Should show origin and upstream with correct URLs
```

**Test 4: From orchestration repo**
```bash
cd ~/github/cloudforproxmox
git fetch fork
git log --oneline fork/main | head -3
# Should show upstream commits (fork has upstream code)
```

---

## File Structure After Setup

```
~/ (home)
├─ github/
│  ├─ cloudforproxmox/ (orchestration repo - current)
│  │  ├─ .git/
│  │  ├─ remotes/
│  │  │  ├─ origin (cloudforproxmox)
│  │  │  └─ fork (cloudforproxmox-upstream)
│  │  ├─ REPLAY_PLAN_PHASE*.md
│  │  ├─ REPLAY_STATUS.md
│  │  └─ ... (docs)
│  │
│  ├─ cloudforproxmox-upstream/ (fork repo - NEW)
│  │  ├─ .git/
│  │  ├─ remotes/
│  │  │  ├─ origin (cloudforproxmox-upstream)
│  │  │  └─ upstream (proxmox-cloudportal/cloud-platform)
│  │  ├─ backend/
│  │  ├─ frontend/
│  │  ├─ docker-compose.yml
│  │  └─ ... (actual source code)
│  │
│  └─ proxmox-isp/ (reference, read-only)
│
└─ cloud-platform-upstream/ (vm103 working dir)
```

---

## Rollback / Recovery

If something goes wrong:

```bash
# Reset fork main to upstream-main
cd ~/github/cloudforproxmox-upstream
git fetch upstream
git reset --hard upstream/main

# Delete accidental branch
git branch -D accidental-branch

# Delete accidental tag
git tag -d accidental-tag
git push origin :refs/tags/accidental-tag  # Remove from remote
```

---

## Next Steps After Setup

1. ✅ Create fork on GitHub
2. ✅ I'll clone and configure locally
3. ✅ Verify remotes
4. ✅ Create first batch branch
5. → Start Phase 1 Batch 1 replay

---

## References

- **Git Remotes:** https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
- **Branching Strategy:** https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows
- **Cherry-pick:** https://git-scm.com/docs/git-cherry-pick
- **Tags:** https://git-scm.com/book/en/v2/Git-Basics-Tagging

---

**Status:** READY FOR EXECUTION

**What I need from you:**
1. Create fork on GitHub (link instructions above)
2. Provide fork URL when done
3. I'll complete steps 2-5 and verify everything

Then we're ready for Phase 1 Batch 1!
