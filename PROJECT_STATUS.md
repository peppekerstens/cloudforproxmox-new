# Project Status

> Track current work, open issues, and phase progress.
> Updated at the end of each development session.

---

## Current Phase: **B — Code Hygiene**

**Started:** 2026-05-21
**Goal:** Fix all known bugs, clean up deprecation warnings, improve code quality.

### Active Work

| Issue | Status | Branch | Notes |
|---|---|---|---|
| [#1 Cascade soft-delete interfaces](https://github.com/peppekerstens/proxmox-isp/issues/1) | ✅ Fixed | main | Committed 77c4ef7 |
| [#2 Replace datetime.utcnow()](https://github.com/peppekerstens/proxmox-isp/issues/2) | ✅ Fixed | main | Committed b28bec1 |
| [#3 VM delete leaks Proxmox resources](https://github.com/peppekerstens/proxmox-isp/issues/3) | ✅ Fixed | main | Committed e989faf — returns 202 with error details on Proxmox failure |

### Open Issues

| # | Title | Type | Priority |
|---|---|---|---|
| [#1](https://github.com/peppekerstens/proxmox-isp/issues/1) | Cascade soft-delete network interfaces when VM is deleted | bug | P0 |
| [#2](https://github.com/peppekerstens/proxmox-isp/issues/2) | Replace datetime.utcnow() with datetime.now(datetime.UTC) | bug | P1 |
| [#3](https://github.com/peppekerstens/proxmox-isp/issues/3) | DELETE /vms/{id} silently swallows Proxmox errors, leaks VMs | bug | P0 |
| [#4](https://github.com/peppekerstens/proxmox-isp/issues/4) | Add /settings route or redirect to /organization/settings | feature | P2 |
| [#5](https://github.com/peppekerstens/proxmox-isp/issues/5) | Add cluster detail page at /clusters/:id | feature | P2 |
| [#6](https://github.com/peppekerstens/proxmox-isp/issues/6) | Implement LXC container creation endpoint | feature | P1 |
| [#7](https://github.com/peppekerstens/proxmox-isp/issues/7) | Add VM template support | feature | P2 |
| [#8](https://github.com/peppekerstens/proxmox-isp/issues/8) | Implement ISO transfer task to Proxmox storage | bug | P1 |

### Phase History

| Phase | Status | Date | Notes |
|---|---|---|---|
| **A — Foundation** | ✅ Complete | 2026-05-21 | License (AGPL-3.0), CI, git workflow, docs, test structure |
| **0 — Fork & Clean Slate** | ✅ Complete | 2026-05-20 | Upstream forked, stripped, deployed on LXC |

---

## Branch Protection

**Status:** ⚠️ Requires GitHub Pro for private repos (or make repo public).

Required settings (manual setup when available):
- `main` requires PR before merge
- CI status checks required: `Backend Lint`, `Backend Tests`, `Frontend Lint`, `Docker Build`
- No force pushes to `main`
- No deleting `main`

---

## Version History

| Version | Tag | Date | Notes |
|---|---|---|---|
| — | — | — | No releases yet. First release: `v0.1.0` after Phase B. |
