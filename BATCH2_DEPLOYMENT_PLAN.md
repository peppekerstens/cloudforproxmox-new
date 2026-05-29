# Phase 1 Batch 2: Deployment Plan

**Status:** Ready for deployment  
**Date:** 2026-05-29  
**Target:** vm152 on pve2 (192.168.2.187)  
**Branch:** `cloudforproxmox-new/phase-1-batch-2`

---

## Overview

Phase 1 Batch 2 adds 3 major features (LXC support, VM templates, cluster pages) on top of Batch 1 foundation.

**Commits:** 10 commits (8bbd9b8..be13bb8)
- LXC container creation support
- VM template management (convert, list, clone)
- Cluster detail page (/clusters/:id)
- ISO transfer & Celery cleanup
- Settings redirect fix

---

## Deployment Steps

### 1. Create VM 152 on pve2

```bash
# SSH to pve2
ssh pve2

# Create VM (4vCPU, 4GB RAM, 20GB disk)
qm create 152 \
  --name cloud-platform-batch2 \
  --memory 4096 \
  --cores 4 \
  --scsi0 local-lvm:20 \
  --net0 model=virtio,bridge=vmbr0 \
  --agent 1

# Boot from Ubuntu 24.04 ISO
qm set 152 --ide2 local:iso/ubuntu-24.04-live-server-amd64.iso,media=cdrom
qm start 152

# Access console and install Ubuntu
```

### 2. Configure VM 152 Network

```bash
# Get DHCP IP, then configure static
ssh ubuntu@<DHCP_IP>
sudo nano /etc/netplan/01-netcfg.yaml

# Set:
# IP: 192.168.2.187/24
# Gateway: 192.168.2.250
# DNS: 8.8.8.8

sudo netplan apply
```

### 3. Deploy Batch 2 Code

```bash
# Clone cloudforproxmox-new
git clone https://github.com/peppekerstens/cloudforproxmox-new.git ~/cloud-platform-batch2
cd ~/cloud-platform-batch2
git checkout phase-1-batch-2

# Copy .env from vm103
scp ubuntu@192.168.2.186:~/cloud-platform-upstream/.env ./.env

# Verify .env (check all credentials are correct)
cat .env | head -20

# Start deployment
docker-compose up -d
docker-compose logs -f api
```

### 4. Wait for Containers

```bash
# Monitor until 8/8 containers healthy
docker ps --format "table {{.Names}}\t{{.Status}}"

# Expected: postgres, redis, rabbitmq, api, frontend, celery-beat, flower, celery-worker
```

### 5. Test Endpoints

```bash
# Login endpoint
curl -X POST http://192.168.2.187:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}'

# Should return: {"access_token": "...", "token_type": "bearer"}

# Check GUI
curl -s http://192.168.2.187:3000/ | head -20

# Should return HTML with React app
```

### 6. Verify New Batch 2 Features

```bash
# Test LXC endpoint (if implemented in API)
curl http://192.168.2.187:8000/api/v1/vms/lxc

# Test VM templates
curl http://192.168.2.187:8000/api/v1/vms/templates

# Test cluster detail page
curl http://192.168.2.187:8000/api/v1/clusters/1
```

---

## Rollback Plan

If Batch 2 fails:
1. Delete vm152: `qm destroy 152`
2. Revert main to previous: `git checkout 11c0a9b`
3. Redeploy from Batch 1 (vm103 snapshot exists)

---

## Success Criteria

- [x] phase-1-batch-2 branch created
- [x] 10 commits applied to branch
- [ ] VM 152 created on pve2
- [ ] 8/8 containers healthy
- [ ] Login endpoint working
- [ ] Dashboard loads
- [ ] New features testable

---

## Notes

- Batch 2 adds significant features (LXC, templates) - test thoroughly
- Monitor logs for migration issues (is_template column added to virtual_machines table)
- If DB migration fails, may need to recreate DB and reseed
- Keep vm103 snapshot as fallback reference
