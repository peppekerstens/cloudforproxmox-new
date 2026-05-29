# Admin User Setup Guide

## Critical Requirement
**admin@example.org MUST ALWAYS be set as superadmin during development deployment.**

This is required because:
1. Cluster registration endpoint (`POST /api/v1/clusters`) requires superadmin permissions
2. User management and infrastructure setup require elevated privileges
3. API token creation for Proxmox integration requires admin-level access

## Problem
When admin@example.org is created via `/api/v1/auth/register`, the `is_superadmin` field defaults to `false`.

## Solution
Update the database directly after user creation:

```bash
# SSH to vm103 (or equivalent deployment VM)
ssh root@192.168.2.186

# Access the database
sqlite3 /app/backend/db.sqlite

# Execute update
UPDATE users SET is_superadmin=1 WHERE email='admin@example.org';
.exit
```

Verify:
```bash
curl -s http://192.168.2.186:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" | jq .is_superadmin
```

Expected output: `true`

## Automated Setup (Development Only)
For PostgreSQL (current deployment):

```bash
docker exec cloudplatform-postgres psql -U cloudplatform -d cloudplatform \
  -c "UPDATE users SET is_superadmin=true WHERE email='admin@example.org';"
```

Or via SSH to VM with sudo:

```bash
sshpass -p "PASSWORD" ssh peppe@VM_IP \
  "sudo -S docker exec cloudplatform-postgres psql -U cloudplatform -d cloudplatform \
  -c \"UPDATE users SET is_superadmin=true WHERE email='admin@example.org';\"" <<< "PASSWORD"
```

## When This Applies
- Phase 1+ deployments to any VM
- Fresh database initialization
- After running `/api/v1/auth/register` to create admin user
- Before attempting cluster registration or admin operations

## Proxmox Cluster Integration

### Create API Token (One-time)
On any Proxmox node (pve1 or pve2):

```bash
# Create user
pveum user add cloudforproxmox@pve --comment 'Cloud For Proxmox API User'

# Grant Administrator role
pveum acl modify / -user cloudforproxmox@pve -role Administrator

# Create token (non-expiring)
pveum user token add cloudforproxmox@pve cloudforproxmox-token --expire 0
```

Output:
```
full-tokenid: cloudforproxmox@pve!cloudforproxmox-token
value:        c945da6d-8095-45aa-b0a7-f74c7557ec8a
```

### Register Clusters in App
With superadmin token, POST to `/api/v1/clusters`:

```bash
curl -X POST http://API_URL:8000/api/v1/clusters \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "pve2-cluster",
    "datacenter": "pve2-dc",
    "region": "local",
    "api_url": "https://192.168.2.22:8006",
    "api_username": "cloudforproxmox@pve",
    "api_token_id": "cloudforproxmox@pve!cloudforproxmox-token",
    "api_token_secret": "c945da6d-8095-45aa-b0a7-f74c7557ec8a",
    "verify_ssl": false
  }'
```

### Sync VMs from Cluster
POST to `/api/v1/clusters/{cluster_id}/sync-vms`:

```bash
curl -X POST http://API_URL:8000/api/v1/clusters/CLUSTER_ID/sync-vms \
  -H "Authorization: Bearer $TOKEN"
```

Response: `{"added": N, "updated": M, "nodes_scanned": K}`

## Related
- See `.env` for admin credentials: `ADMIN_EMAIL=admin@example.org`, `ADMIN_PASSWORD=superadmin`
- Proxmox API token stored in `.env` as `PROXMOX_API_TOKEN_ID` and `PROXMOX_API_TOKEN_SECRET`
- Both clusters use same API token (they're in the same Proxmox cluster)
