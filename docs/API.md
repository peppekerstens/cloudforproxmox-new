# Proxmox ISP — API Reference

> Auto-generated from source code. All endpoints require authentication unless noted.
> Base URL: `http://<server>:8000/api/v1`

---

## Authentication

### `POST /auth/login`
Login with email/password. Returns JWT access + refresh tokens.

**Body:**
```json
{
  "email": "user@example.org",
  "password": "secret"
}
```

**Response:** `Token` — `{ access_token, refresh_token, token_type }`

---

### `POST /auth/register`
Register a new user account.

**Body:**
```json
{
  "email": "user@example.org",
  "password": "secret",
  "username": "username"
}
```

**Response:** `UserResponse`

---

### `POST /auth/refresh`
Refresh an expired access token.

**Body:** `{ refresh_token }`

**Response:** `Token`

---

### `POST /auth/logout`
Invalidate current session.

**Response:** `204 No Content`

---

### `GET /auth/me`
Get current user details.

**Response:** `UserResponse`

---

## Users

### `GET /users/me`
Get current user profile.

**Response:** `UserResponse`

---

### `PATCH /users/me`
Update current user profile.

**Body:** `UserUpdate`

**Response:** `UserResponse`

---

### `GET /users`
List users (superadmin only). Paginated.

**Query:** `page`, `per_page`

**Response:** `UserListResponse`

---

### `GET /users/{user_id}`
Get user by ID (superadmin only).

**Response:** `UserResponse`

---

### `DELETE /users/{user_id}`
Delete user (superadmin only).

**Response:** `204 No Content`

---

## Organizations

### `GET /organizations/me`
Get current user's organization memberships.

**Response:** `List[OrganizationMembershipResponse]`

---

### `GET /organizations/members`
List members of current user's organization.

**Response:** `List[OrganizationMemberDetailResponse]`

---

### `POST /organizations/members`
Add a member to the organization.

**Body:** `OrganizationMemberCreate`

**Response:** `OrganizationMemberDetailResponse` (201)

---

### `PATCH /organizations/members/{user_id}`
Update member role/permissions.

**Body:** `OrganizationMemberUpdate`

**Response:** `OrganizationMemberDetailResponse`

---

### `DELETE /organizations/members/{user_id}`
Remove member from organization.

**Response:** `204 No Content`

---

## Clusters

### `GET /clusters`
List all Proxmox clusters. Superadmin only. Paginated.

**Query:** `page`, `per_page`, `is_active`, `search`

**Response:** `ProxmoxClusterListResponse`

---

### `POST /clusters`
Create a new Proxmox cluster. Superadmin only.

**Body:** `ProxmoxClusterCreate`
```json
{
  "name": "pve1",
  "api_url": "https://192.168.2.21:8006/api2/json",
  "auth_method": "token",
  "api_token": "root@pam!isp-portal",
  "api_token_value": "uuid-here",
  "organization_id": null,
  "is_shared": true,
  "datacenter": "dc1",
  "region": "us-east"
}
```

**Response:** `ProxmoxClusterResponse` (201)

---

### `GET /clusters/{cluster_id}`
Get cluster details.

**Response:** `ProxmoxClusterResponse`

---

### `PATCH /clusters/{cluster_id}`
Update cluster configuration. Superadmin only.

**Body:** `ProxmoxClusterUpdate`

**Response:** `ProxmoxClusterResponse`

---

### `DELETE /clusters/{cluster_id}`
Delete cluster. Superadmin only.

**Response:** `204 No Content`

---

### `POST /clusters/test`
Test Proxmox cluster connection before creation.

**Body:** `ClusterTestRequest`
```json
{
  "api_url": "https://192.168.2.21:8006/api2/json",
  "auth_method": "token",
  "api_token": "root@pam!isp-portal",
  "api_token_value": "uuid-here"
}
```

**Response:** `ClusterTestResponse`

---

### `POST /clusters/{cluster_id}/sync`
Sync cluster — fetch nodes, resources, and existing VMs from Proxmox.

**Response:** `ProxmoxClusterResponse`

---

### `POST /clusters/{cluster_id}/sync-vms`
Sync VMs only from cluster.

**Response:** `202 Accepted`

---

## Virtual Machines

### `GET /vms`
List VMs in organization. Paginated.

**Query:** `page`, `per_page`, `status`, `search`

**Response:** `VMListResponse`

**Note:** Members see only their own VMs. Admins/viewers see all org VMs.

---

### `POST /vms`
Create a new VM. Provisioned asynchronously via Celery.

**Body:** `VMCreate`
```json
{
  "name": "web-server-01",
  "hostname": "web01.example.com",
  "description": "Production web server",
  "cpu_cores": 2,
  "cpu_sockets": 1,
  "memory_mb": 2048,
  "disks": [
    {
      "size_gb": 20,
      "storage_pool": "local-lvm",
      "disk_interface": "scsi",
      "disk_format": "raw",
      "is_boot_disk": true
    }
  ],
  "iso_image_id": null,
  "boot_order": null,
  "os_type": "linux",
  "proxmox_cluster_id": null,
  "network_id": null,
  "tags": []
}
```

**Response:** `VMResponse` (202 Accepted) — VM created in DB, provisioning queued.

**VM provisioning behavior:**
- Disk format `raw` on `local-lvm` (LVM-Thin) → **thin-provisioned**
- Disk format `raw` on directory storage → **thick-provisioned**
- CPU overcommit: **allowed** (no `cpulimit` set)
- Memory ballooning: **enabled** (Proxmox default, never disabled)
- VM type: always `qemu` (no LXC creation endpoint exists)

---

### `GET /vms/{vm_id}`
Get VM details.

**Response:** `VMResponse`

---

### `PATCH /vms/{vm_id}`
Update VM configuration (name, description, CPU, memory).

**Body:** `VMUpdate`

**Response:** `VMResponse`

---

### `DELETE /vms/{vm_id}`
Delete VM. Stops and removes from Proxmox.

**Response:** `204 No Content`

---

### `POST /vms/{vm_id}/start`
Start VM.

**Body:** `{ force: false }` (optional)

**Response:** `202 Accepted`

---

### `POST /vms/{vm_id}/stop`
Stop VM.

**Body:** `{ force: false }` (optional)

**Response:** `202 Accepted`

---

### `POST /vms/{vm_id}/restart`
Restart VM.

**Response:** `202 Accepted`

---

### `POST /vms/{vm_id}/force-stop`
Force stop VM (hard power off).

**Response:** `VMResponse`

---

### `POST /vms/{vm_id}/reboot`
Reboot VM (guest OS reboot).

**Response:** `VMResponse`

---

### `POST /vms/{vm_id}/reset`
Reset VM (hard reset).

**Response:** `VMResponse`

---

### `PATCH /vms/{vm_id}/resize`
Resize VM CPU/memory.

**Body:** `VMResize`
```json
{
  "cpu_cores": 4,
  "cpu_sockets": 1,
  "memory_mb": 4096
}
```

**Response:** `VMResponse`

---

### `GET /vms/{vm_id}/console`
Get VM console URL (noVNC proxy).

**Response:** `{ console_url }`

---

### `POST /vms/{vm_id}/sync`
Sync VM state from Proxmox.

**Response:** `VMResponse`

---

### `POST /vms/{vm_id}/attach-network`
Attach network interface to VM.

**Body:** `VMNetworkAttachRequest`

**Response:** `VMResponse`

---

### `DELETE /vms/{vm_id}/detach-network/{interface_name}`
Detach network interface from VM.

**Response:** `204 No Content`

---

## Disks

### `GET /vms/{vm_id}/disks`
List disks attached to VM.

**Response:** `DiskListResponse`

---

### `POST /vms/{vm_id}/disks`
Add a new disk to VM.

**Body:** `DiskCreate`

**Response:** `DiskResponse` (202 Accepted)

---

### `DELETE /vms/{vm_id}/disks/{disk_id}`
Remove disk from VM.

**Response:** `204 No Content`

---

### `POST /vms/{vm_id}/disks/attach-iso`
Attach ISO as CD-ROM to VM.

**Body:** `{ iso_image_id }`

**Response:** `DiskResponse` (202 Accepted)

---

### `PATCH /vms/{vm_id}/disks/{disk_id}/resize`
Resize disk.

**Body:** `{ size_gb }`

**Response:** `DiskResponse`

---

## Snapshots

### `GET /vms/{vm_id}/snapshots`
List VM snapshots.

**Response:** `SnapshotListResponse`

---

### `POST /vms/{vm_id}/snapshots`
Create VM snapshot.

**Body:** `{ name, description }`

**Response:** `{ message }` (202 Accepted)

---

### `POST /vms/{vm_id}/snapshots/{snapshot_name}/rollback`
Rollback VM to snapshot.

**Response:** `{ message }`

---

### `DELETE /vms/{vm_id}/snapshots/{snapshot_name}`
Delete snapshot.

**Response:** `204 No Content`

---

## Networks (VPC)

### `POST /networks`
Create VPC network. Supports VLAN (default), VXLAN, and Simple SDN types.

**Body:** `NetworkCreate`
```json
{
  "name": "Production Network",
  "description": "Primary production network",
  "cidr": "10.100.0.0/24",
  "gateway": "10.100.0.1",
  "dns_servers": ["8.8.8.8", "8.8.4.4"],
  "is_shared": false,
  "bridge": "vmbr0",
  "network_type": "vlan"
}
```

**Fields:**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | str | yes | — | Network display name |
| `description` | str | no | `null` | Optional description |
| `cidr` | str | yes | — | CIDR block (e.g. `10.100.0.0/24`) |
| `gateway` | str | no | `null` | Gateway IP address |
| `dns_servers` | list[str] | no | `[]` | DNS server IPs |
| `is_shared` | bool | no | `false` | Shareable across orgs |
| `bridge` | str | no | `"vmbr0"` | Proxmox bridge for VLAN type |
| `network_type` | str | no | `"vlan"` | Network type: `vlan`, `vxlan`, or `simple` |

**Response:** `NetworkResponse` (201)

**Network creation logic by type:**

- **`vlan`** (default): VLAN ID auto-allocated from pool. VM config uses `tag=<vlan_id>,bridge=<bridge>`.
- **`vxlan`**: VNI auto-allocated from VNI pool. SDN zone `isp-vxlan` created if not exists. VNet created in zone. VM attaches to VNet's bridge (`bridge=vn-<sdn_vnet>`). Requires a registered Proxmox cluster.
- **`simple`**: VNI auto-allocated from VNI pool. SDN zone `isp-simple` created if not exists. VNet created in zone. VM attaches to VNet's bridge (`bridge=vn-<sdn_vnet>`). Requires a registered Proxmox cluster.

**NetworkResponse additional fields for SDN types:**

| Field | Type | Description |
|---|---|---|
| `network_type` | str | `"vlan"`, `"vxlan"`, or `"simple"` |
| `vni` | int \| null | VXLAN VNI (for `vxlan`/`simple` types) |
| `sdn_zone` | str \| null | SDN zone name |
| `sdn_vnet` | str \| null | SDN VNet name |

---

### `GET /networks`
List VPC networks in organization. Paginated.

**Query:** `page`, `per_page`

**Response:** `NetworkListResponse`

---

### `GET /networks/{network_id}`
Get network details.

**Response:** `NetworkResponse`

---

### `PATCH /networks/{network_id}`
Update network. CIDR and VLAN cannot be changed after creation.

**Body:** `NetworkUpdate`

**Response:** `NetworkResponse`

---

### `DELETE /networks/{network_id}`
Delete network and release VLAN. Fails if VMs attached.

**Response:** `204 No Content`

---

### `POST /networks/{network_id}/set-default`
Set network as default for organization.

**Response:** `NetworkResponse`

---

### SDN Networking

The portal supports three network isolation types through Proxmox's SDN stack:

| Type | Mechanism | Resource Pool | Proxmox Config |
|---|---|---|---|
| `vlan` | 802.1Q tagging on bridge | VLAN pool (DB) | `tag=<vlan_id>,bridge=<bridge>` |
| `vxlan` | VXLAN overlay tunnel | VNI pool (100000–16777215) | `bridge=vn-<sdn_vnet>` |
| `simple` | Isolated SDN bridge | VNI pool (100000–16777215) | `bridge=vn-<sdn_vnet>` |

**Architecture:**

- **VLAN** networks use traditional 802.1Q tagging directly on the Proxmox bridge (`vmbr0`). VLAN IDs are drawn from a database pool. No SDN configuration is required.
- **VXLAN** networks create an SDN zone (`isp-vxlan`) on the Proxmox cluster using VXLAN encapsulation. Each network gets a VNet within this zone. VMs connect to the VNet's automatically created Linux bridge (`vn-<vnet_name>`). VXLAN enables layer-2 segmentation across cluster nodes without requiring physical VLAN trunking.
- **Simple** networks create an SDN zone (`isp-simple`) using isolated Linux bridges. Each network gets a VNet. This is the lightest-weight SDN option — no tunnel encapsulation, no additional switch configuration.

**Prerequisites:**

- `libpve-network-perl` must be installed on all cluster nodes (already present on pve1/pve2).
- The Proxmox API token must include the `PVESDNUser` role (required for all SDN operations).
- VXLAN and Simple types require at least one registered Proxmox cluster.
- VM200 (OPNsense) stays on `vmbr0` with standard config — SDN changes are additive and do not affect existing VMs or bridges.

---

### `GET /networks/{network_id}/stats`
Get network statistics (IP usage, VM count).

**Response:** `{ stats }`

---

### `POST /networks/{network_id}/ip-pools`
Create IP pool within network.

**Body:** `IPPoolCreate`
```json
{
  "pool_name": "VM Pool",
  "start_ip": "10.100.0.10",
  "end_ip": "10.100.0.250",
  "description": "IP pool for VMs"
}
```

**Response:** `IPPoolResponse` (201)

---

### `GET /networks/{network_id}/ip-pools`
List IP pools in network.

**Response:** `List[IPPoolResponse]`

---

### `DELETE /networks/ip-pools/{pool_id}`
Delete IP pool. Fails if pool has active allocations.

**Response:** `204 No Content`

---

### `POST /networks/{network_id}/allocate-ip`
Allocate IP address from network.

**Body:** `IPAllocationRequest` (optional)
```json
{
  "ip_pool_id": null,
  "preferred_ip": "10.100.0.50"
}
```

**Response:** `IPAllocationResponse` (201)

**Strategy:** If `preferred_ip` specified, try it. If `ip_pool_id` specified, allocate from pool. Otherwise, find first available.

---

### `GET /networks/{network_id}/ip-allocations`
List IP allocations in network.

**Query:** `status_filter` (allocated, released, reserved)

**Response:** `List[IPAllocationResponse]`

---

### `DELETE /networks/ip-allocations/{allocation_id}`
Release IP allocation.

**Response:** `204 No Content`

---

## ISO Images

### `POST /isos/upload`
Upload ISO file via multipart form.

**Body:** multipart/form-data with `file`, `name`, `display_name`, `description`, `os_type`, `os_version`, `architecture`, `is_public`

**Response:** `ISOUploadInitResponse` (202)

**Note:** File saved locally, queued for transfer to Proxmox (TODO: not implemented).

---

### `POST /isos/upload-from-url`
Upload ISO from URL via Proxmox download.

**Body:** `ISOUploadFromURL`
```json
{
  "url": "https://example.com/ubuntu.iso",
  "display_name": "Ubuntu 24.04",
  "description": "Ubuntu Server 24.04 LTS",
  "os_type": "linux",
  "os_version": "24.04",
  "architecture": "x86_64",
  "is_public": false
}
```

**Response:** `ISOUploadInitResponse` (202)

---

### `GET /isos`
List ISO images. Includes public ISOs by default.

**Query:** `page`, `per_page`, `include_public`, `os_type`

**Response:** `ISOListResponse`

---

### `GET /isos/{iso_id}`
Get ISO details.

**Response:** `ISOResponse`

---

### `PATCH /isos/{iso_id}`
Update ISO metadata. Only owning org or superadmin.

**Body:** `ISOUpdate`

**Response:** `ISOResponse`

---

### `DELETE /isos/{iso_id}`
Delete ISO (soft delete). Only owning org or superadmin.

**Response:** `204 No Content`

---

## Storage

### `GET /storage/clusters/{cluster_id}/pools`
List storage pools in cluster.

**Query:** `content_type` (images, rootdir, vztmpl, iso, backup)

**Response:** `StoragePoolListResponse`

---

### `GET /storage/clusters/{cluster_id}/pools/{pool_id}`
Get storage pool details.

**Response:** `StoragePoolResponse`

---

### `POST /storage/clusters/{cluster_id}/pools/sync`
Sync storage pools from Proxmox.

**Response:** `StoragePoolSyncResponse`

---

### `GET /storage/pools`
List all storage pools.

**Response:** `StoragePoolListResponse`

---

## Quotas

### `GET /quotas`
List all quotas for current organization.

**Response:** `List[QuotaResponse]`

---

### `GET /quotas/usage`
Get current quota usage.

**Response:** `QuotaUsageResponse`

---

### `PUT /quotas/{resource_type}`
Set quota limit. Superadmin only (via `X-Organization-ID` header).

**Body:** `{ limit }`

**Response:** `QuotaResponse`

**Resource types:** `cpu_cores`, `memory_gb`, `storage_gb`, `vm_count`, `cluster_count`, `network_segments`

---

### `POST /quotas/recalculate`
Recalculate all quota usage from actual resources.

**Response:** `202 Accepted`

---

## Console Proxy

### `GET /console/{vm_id}`
Get noVNC console page for VM.

**Response:** HTML page with embedded noVNC client

---

## Health

### `GET /health`
Basic health check.

**Response:** `{ status: "healthy" }`

---

### `GET /health/detailed`
Detailed health check with database, Redis, Celery status.

**Response:** `{ status, database, redis, celery }`

---

## Known Gaps

| Feature | Status | Notes |
|---|---|---|---|
| LXC container creation | ❌ Not implemented | Model supports `vm_type=lxc` but no creation endpoint exists |
| VM templates | ❌ Not implemented | No template/`is_template` field on VM model; Proxmox supports `template=1` |
| ISO transfer to Proxmox | ❌ TODO | Upload saves locally; transfer-to-Proxmox task is commented out (`iso_tasks.py`) |
| CPU overcommit control | ❌ Not implemented | No `cpulimit` or `cpuunits` set during VM creation; Proxmox freely overcommits |
| Memory ballooning config | ❌ Not implemented | Balloon enabled by default (Proxmox default), no minimum floor configured |
| Cluster detail UI page | ❌ Not implemented | API endpoint exists (`GET /clusters/{id}`) but no frontend route for `/clusters/:id` |
| Settings page | ❌ Not implemented | Sidebar links to `/settings` but route doesn't exist; use `/organization/settings` |
| **Interface cascade-delete** | ❌ Not implemented | Soft-deleting a VM (`DELETE /vms/{id}`) does not cascade to `vm_network_interfaces`. Interfaces remain active, blocking network deletion. |
| VXLAN/Simple SDN prerequisites | ✅ Documented | `libpve-network-perl` required on all cluster nodes; already installed on pve1/pve2 |
| VXLAN VNI range | ✅ Implemented | VNI range 100000–16777215, on-demand allocation, no pre-population needed |
| VM200 unaffected by SDN | ✅ By design | VM200 (OPNsense) stays on `vmbr0` — SDN changes are additive, do not touch existing VMs or bridges |

### Issues Found (2026-05-21)

| Issue | Status | Details |
|---|---|---|
| **Celery task uses sync session + async services** | 🔧 Fixed | `vm_tasks.py:328` — `quota_service.decrement_usage()` called without `await` (coroutine never awaited). Replaced with sync DB operations. |
| **Quota decrement on retry** | 🔧 Fixed | Each Celery retry decremented quota again (3× total). Added `need_quota_release` guard — only decrement on first failure. |
| **VLAN pool not initialized** | 🔧 Fixed | Network creation fails with `VLAN pool not initialized. Run initialize_vlan_pool() first.` — run `scripts/init_vlan_pool.py` after DB setup. |
| **Proxmox token permissions** | 🔧 Fixed | Default `PVEAuditor` insufficient for VM creation. Need: `PVEAuditor` + `PVEVMAdmin` + `PVESDNUser` + `PVEDatastoreAdmin`. |
| **X-Organization-ID header required** | ✅ By design | All org-scoped endpoints require this header. Must be sent with every request. |
| **Quota recalculation stale** | ⚠️ Minor | After VM creation/deletion, `POST /quotas/recalculate` needed to sync usage. |
| **VM creation always picks pve2** | 👀 Observation | `select_best_node()` picked pve2 for both VM attempts. May be due to load scoring. PVE resources confirmed healthy. |
| **Delete VM leaks Proxmox resources** | ❌ Bug | `DELETE /vms/{id}` (`vms.py:528-530`) silently catches Proxmox errors with bare `except Exception`, soft-deletes DB record, but leaves VM running on Proxmox. Orphaned resources accumulate. Fix: either raise the error or queue a cleanup task. |
| **Interface cascade-delete missing** | ❌ Bug | Soft-deleting a VM does not cascade to `vm_network_interfaces`. Interfaces remain active, blocking network deletion with "VM(s) still attached". Cleanup scripts must force-clean via direct SQL. Fix: add cascade soft-delete in `delete_vm` endpoint. |
| **`datetime.utcnow()` deprecated** | ⚠️ Warning | Python 3.12+ deprecates `datetime.utcnow()`. Generates 96,000+ test warnings. Affected files: `vlan_service.py:127`, `vni_service.py:63`, `quota_service.py`, `vms.py`, `network_service.py`. Fix: replace with `datetime.now(datetime.UTC)`. |
| **Cleanup script fragile** | ⚠️ Technical debt | `scripts/cleanup_test_resources.py` required 7 fixes: inherits `DATABASE_URL` from test env, wrong relative path, single-node only, `qm destroy` fails on running VMs, async provisioning needs delay, network deletion blocked by interfaces, quota recalc returns 202. |

### Token Permissions Summary

The Proxmox API token (`root@pam!isp-portal`) requires these roles at the root `/` path:

| Role | Purpose |
|---|---|
| `PVEAuditor` | Read access (node listing, resource monitoring) |
| `PVEVMAdmin` | VM lifecycle management (create, start, stop, delete) |
| `PVESDNUser` | VLAN-tagged networking (`SDN.Use`) |
| `PVEDatastoreAdmin` | Disk storage allocation (`Datastore.AllocateSpace`)
