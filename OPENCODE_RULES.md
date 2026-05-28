# OpenCode Development Rules Handbook

**Project:** Cloud for ProxMox (cloudforproxmox-new)  
**Version:** 1.0  
**Effective Date:** 2026-05-28  
**Source:** cloudforproxmox-old AGENTS.md + PLAN.md + lessons learned

---

## Overview

This handbook distills the 40 core rules adopted for cloudforproxmox-new development. Rules are organized by category. Each rule has:
- **Purpose:** Why the rule exists
- **Rule:** What to do
- **Verification:** How to verify compliance

---

## 1. Communication & Caveman Mode (4 rules)

### 1.1 Caveman Mode Intensity Levels
**Purpose:** Reduce token usage while keeping technical accuracy.

**Rule:** Caveman mode available in intensity levels:
- `lite`: Drop articles, filler, pleasantries; keep all technical substance
- `full`: Drop articles, filler, hedging; fragments OK; code/commits normal
- `ultra`: Minimal English; technical terms stay; code unmodified
- `wenyan-lite/full/ultra`: Chinese for internal optimizations (never shown to user)

**Verification:** Use `/caveman [lite|full|ultra|wenyan]` or invoke via prompt. Output should be terse but technically complete.

### 1.2 Caveman Mode Auto-Clarity Rule
**Purpose:** Ensure users always understand critical information.

**Rule:** Automatically drop caveman mode for:
- Security warnings
- Irreversible actions
- User confusion signals

Resume caveman after clarity restored.

**Verification:** Security messages always in plain English. Destructive actions (delete, revert) explained clearly.

### 1.3 Subagent Prompts Use Caveman Style
**Purpose:** Keep subagent context minimal, reduce bloat.

**Rule:** When delegating to subagent:
- Use caveman-style prompt (fragments, no filler)
- Include minimal context (only relevant files/functions)
- Do NOT dump full conversation history

**Verification:** Subagent prompt <500 chars. Output is caveman-compressed (~60% smaller than vanilla).

### 1.4 Parent Context Stays Clean
**Purpose:** Preserve context budget across long sessions.

**Rule:** 
- Review subagent result
- Accept or reject (don't redo work in parent)
- Move on; don't accumulate state

**Verification:** Parent thread doesn't repeat subagent work. Each tool call has clear purpose, no redundancy.

---

## 2. Issue Tracking (3 rules)

### 2.1 Issue-First Workflow (MANDATORY)
**Purpose:** All work tracked. Root causes documented. Regressions prevented.

**Rule:** 
- ALWAYS create GitHub issue FIRST before writing code
- Exception: Trivial 1-line typo fixes (but comment on issue if it changes behavior)
- Every bug, feature, refactor, investigation gets an issue

**Verification:** Check `git log` — every commit references issue #number. `gh issue list` shows current work.

### 2.2 Issue Comment Format
**Purpose:** Actionable, traceable updates.

**Rule:** Comments should be:
- Short (1-3 lines)
- Include file:line references
- State root cause found, fix implemented, or blocker
- Example: "Root cause at `backend/app/api/v1/endpoints/org_roles.py:221` — SQL ResultProxy exhausted. Fix in commit `0a0bc60`."

**Verification:** Issue comments are scannable. No paragraphs. Precise file references.

### 2.3 Use gh CLI
**Purpose:** Consistent, scriptable issue tracking.

**Rule:**
```bash
gh issue create --title "bug: X doesn't work" --body "..." --label "bug,P1"
gh issue comment <number> --body "Root cause found at path:line"
gh issue view <number>
```

**Verification:** All issue operations use `gh` command. No manual GitHub web edits.

---

## 3. Git & Commits (3 rules)

### 3.1 Conventional Commits
**Purpose:** Standardized messages enable automation, clear history.

**Rule:** Format: `type: description`
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Test addition/change
- `refactor`: Code restructure (no behavior change)
- `chore`: Cleanup, dependencies
- `ci`: CI/CD changes

Messages: describe WHAT and WHY, not HOW. Atomic commits only (one logical change per commit).

**Verification:** `git log --oneline` reads like a feature summary. No "fix stuff" messages.

### 3.2 Pull Requests ≤300 lines, ≤5 files
**Purpose:** Keep PRs reviewable, prevent merge hell.

**Rule:**
- Each PR = one logical feature/fix
- ≤300 lines of code changes
- ≤5 files touched
- CI must pass before merge
- Update docs/API.md if API changed

**Verification:** `git diff main..feature | wc -l` < 300. PR description links the issue.

### 3.3 Main Branch Always Deployable
**Purpose:** Every commit on main should work in production.

**Rule:**
- No direct pushes to main
- All work via feature branches (`feat/*`, `fix/*`, `chore/*`)
- Merge only via PR after CI passes
- Delete branch after merge

**Verification:** `git log main` shows only merged PRs, no WIP commits.

---

## 4. Credential Management (3 rules)

### 4.1 All Secrets in infra/.env
**Purpose:** Prevent credential leaks via git.

**Rule:**
- All secrets (passwords, tokens, keys) go in `infra/.env` (gitignored)
- Never hardcode in docker-compose.yml, source code, or docs
- Never store creds in markdown files
- Reference variable names instead (e.g., `${PROXMOX_TOKEN_VALUE}`)

**Verification:** `git status` shows no .env files. `grep -r "password\|token" src/` returns no actual secrets.

### 4.2 infra/.env.example = Template
**Purpose:** Enable new deployments without hardcoded secrets.

**Rule:**
- Committed template uses `CHANGE_ME_*` placeholders
- Copy to `infra/.env` and fill in actual values
- Never commit actual `.env`

**Verification:** `infra/.env.example` exists, contains `CHANGE_ME_*` for all secrets.

### 4.3 docs/CREDENTIALS.md = Inventory
**Purpose:** Document which services use which credentials.

**Rule:**
- Single source of truth for variable names
- Lists what each variable is, which services use it
- Never contains actual values
- Points to `infra/.env` for actual credentials

**Verification:** `docs/CREDENTIALS.md` is complete. `infra/.env.example` matches variable list.

---

## 5. Testing (4 rules + enhancements)

### 5.1 All Functionality Tested
**Purpose:** Every API endpoint, every UI flow must be tested.

**Rule:** 
- Unit tests for all functions (fast, in-memory SQLite)
- Integration tests on main merge (live deployment)
- Phase-gate tests at phase boundaries (verify from API + Proxmox + GUI angles)

**Verification:** `pytest tests/` passes. Test coverage >80%. Phase-gate tests pass before advancing.

### 5.2 Never Touch VM200 (OPNsense)
**Purpose:** VM200 provides internet connectivity for entire homelab. Breaking it breaks everything.

**Rule:** 
- Never snapshot VM200
- Never migrate VM200
- Never restart VM200
- Never modify VM200 configuration

**Verification:** Deployment scripts exclude VM200. No snapshots of VMID 200 created.

### 5.3 Unit Tests Every PR
**Purpose:** Fast feedback, catch regressions early.

**Rule:**
- All new code has unit tests
- Tests run in-memory (no external dependencies)
- SQLite for database tests
- Must pass before PR merge

**Verification:** `pytest tests/unit/ -v` shows all tests passing. PR has "Tests passing" checkmark.

### 5.4 Integration Tests on Main Merge
**Purpose:** Verify features work against live deployment.

**Rule:**
- Integration tests run after PR merged to main
- Require `--integration` flag (slower, hits live deployment)
- Cleanup script runs before/after integration test session

**Verification:** `pytest tests/integration/ --integration` passes on main after merge.

### 5.5 Phase-Gate Tests (3-Angle Verification) — ENHANCED
**Purpose:** Verify not just features work, but deployment state matches expected.

**Rule:** At each phase boundary, run `test_phase<N>_<name>.py` that verifies:
1. **API:** Correct HTTP status codes, response schemas, error handling (curl/requests)
2. **Proxmox:** Direct API calls confirm resources exist on hypervisor (proxmoxer)
3. **GUI:** Playwright MCP confirms pages render and display correct data (browser snapshot)
4. **Deployment State:** (ENHANCED) Verify expected files exist, logs show no errors, containers healthy

**Verification:** Phase-gate test output shows 3/4 verification points passing before advancing phase.

### 5.6 Version Compatibility Checks
**Purpose:** Proxmox API varies by version. Prevent version mismatch errors.

**Rule:**
- New features depending on Proxmox API capabilities must include version checks
- Add entries to `proxmox_service.py` `MIN_VERSIONS`
- Call `check_feature_support()` before using version-sensitive endpoints
- Unit tests verify version checks trigger correctly

**Verification:** `proxmox_service.py` has MIN_VERSIONS dict. Features check `check_feature_support()`.

---

## 6. Documentation (2 rules)

### 6.1 docs/API.md = Single Source of Truth
**Purpose:** API reference always current, no drift between code and docs.

**Rule:**
- Every new API endpoint documented in `docs/API.md`
- Every endpoint change updated in same PR
- docs/API.md the ONLY place to look for API reference

**Verification:** `docs/API.md` lists all endpoints in current code. No endpoint exists without docs entry.

### 6.2 Component READMEs Stay Current
**Purpose:** backend/README.md, frontend/README.md, infra/README.md guide future work.

**Rule:**
- Update component READMEs when architecture changes
- Document deployment procedures, testing procedures, known issues

**Verification:** READMEs reflect current project structure. Setup instructions work.

---

## 7. Architectural Decisions (9 rules)

### 7.1 Functionality First, Security Later
**Purpose:** Code changes significantly between phases. Security on unstable code wastes effort.

**Rule:**
- Prioritize functional bugs, UX, features before security hardening
- Exception: P0 security enabling immediate data loss or auth bypass
- Security audits happen at phase gates, not mid-phase

**Verification:** Phase checklist includes "security review" gate. P0 exploits are separate issue track.

### 7.2 Docker Compose (Not K8s)
**Rule:** Single vm103 deployment. No microservices complexity.

**Verification:** docker-compose.yml is deployment definition. No Helm charts, no K8s manifests.

### 7.3 Celery + Redis (Not RabbitMQ)
**Rule:** Async tasks via Celery. Redis for broker + state. Simpler than RabbitMQ.

**Verification:** docker-compose includes celery-worker, celery-beat, redis containers.

### 7.4 Single FastAPI Process (No Microservices)
**Rule:** One FastAPI instance serves all API endpoints.

**Verification:** `docker ps` shows one fastapi container, not multiple backend services.

### 7.5 Prepaid Credits Model (Not Postpaid)
**Rule:** Users purchase credits upfront. Billing simpler, less churn.

**Verification:** Billing schema uses credits table, not invoices.

### 7.6 Mono-Repo (Backend + Frontend + Infra)
**Rule:** All code in one repo. Replay commits atomically.

**Verification:** `ls -la` shows `backend/`, `frontend/`, `infra/`, `tests/`.

### 7.7 AGPL-3.0 License
**Rule:** Strong copyleft. Closes SaaS loophole (derivative works must share source).

**Verification:** LICENSE file contains AGPL-3.0 text.

### 7.8 AdGuard Home for DNS
**Rule:** Single shared DNS instance on LXC 100. Tenant isolation via OPNsense firewall, not DNS layer.

**Verification:** AdGuard container runs. DNS queries go through it. Firewall rules isolate tenants.

### 7.9 DNS Provider Abstraction (MANDATORY)
**Rule:** All DNS operations via `DNSProvider` abstract interface. AdGuard Home is first implementation. Swap backends via config, not code.

**Verification:** No code imports `adguard` directly. All DNS ops go through `DNSProvider`.

---

## 8. Subagent Delegation (4 rules)

### 8.1 Subagent Threshold: 2+ Tool Calls
**Purpose:** Prevent context bloat. Subagents are cheaper, faster for multi-step work.

**Rule:** 
- Single file read/edit/query → do directly
- 2+ tool calls → spawn subagent
- No exceptions

**Verification:** Parent context doesn't accumulate >10 simultaneous tool calls.

### 8.2 Prefer cavecrew-investigator (Research)
**Rule:** Fast, read-only code lookups. Returns file:line table of matches.

**Verification:** Use for "where is X defined", "what calls Y", "list all uses of Z".

### 8.3 Prefer cavecrew-builder (1-2 File Edits)
**Rule:** Surgical edits. Typo fixes, single-function rewrites, mechanical renames.

**Verification:** Used for bounded scope, obvious fixes. Returns caveman diff receipt.

### 8.4 Prefer cavecrew-reviewer (Diff Review)
**Rule:** One-line PR feedback, severity-tagged, no praise, no scope creep.

**Verification:** Used for "review this PR", "audit this file". Output format: `path:line: emoji severity: problem. fix.`

---

## 9. Proxmox Infrastructure (2 rules)

### 9.1 Proxmox API Tokens (Not Passwords)
**Rule:** Use API tokens for auth (granular, safer). Never use root password.

**Verification:** `infra/.env` has `PROXMOX_TOKEN_NAME` and `PROXMOX_TOKEN_VALUE`, not passwords.

### 9.2 ProxmoxService Version Checks
**Rule:** Check Proxmox API version before using version-sensitive endpoints.

**Verification:** `proxmox_service.py` has MIN_VERSIONS dict. Code calls `check_feature_support()`.

---

## 10. AI-Optimized Development (3 rules)

### 10.1 Small PRs, Clean History
**Rule:** (Covered in section 3.2)

### 10.2 Parent Context Stays Clean
**Rule:** (Covered in section 1.4)

### 10.3 Subagent Gets Minimal Context
**Rule:** (Covered in section 8.1)

---

## Compliance Checklist

Use this checklist to verify rule compliance:

- [ ] All PRs use conventional commits
- [ ] All secrets in `infra/.env` (gitignored)
- [ ] `docs/API.md` updated for new endpoints
- [ ] `docs/CREDENTIALS.md` inventories all variables
- [ ] All code has unit tests
- [ ] Phase-gate tests verify 3 angles (API, Proxmox, GUI)
- [ ] No direct pushes to main; all via PR
- [ ] Issue created before starting work
- [ ] Issues commented with root cause + fix reference
- [ ] PRs ≤300 lines, ≤5 files
- [ ] docker-compose.yml uses env variable substitution (${VAR})
- [ ] No hardcoded secrets in any file
- [ ] Version checks in `proxmox_service.py` for Proxmox API features

---

## References

- Full assessment: `OPENCODE_ASSESSMENT.md`
- Phase-gate procedures: `PHASE12_SECURITY_CHECKPOINT.md`, `INFRASTRUCTURE_SAFEGUARDS.md`
- Replay plan: `REPLAY_PLAN_PHASE*.md`
- Baseline status: `REPLAY_STATUS.md`
