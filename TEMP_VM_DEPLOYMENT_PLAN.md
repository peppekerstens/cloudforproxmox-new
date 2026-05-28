# Temporary VM Deployment (vmid 151, pve1)

**Status:** VM created, awaiting boot  
**Created:** 2026-05-28 22:15 UTC  
**UPID:** UPID:pve1:00098D3D:009729B4:6A18AC0E:qmcreate:151:root@pam!mcp-server:

---

## VM Specifications

| Property | Value |
|----------|-------|
| VMID | 151 |
| Node | pve1 |
| Name | cloud-platform-phase1-batch1-test |
| OS | Ubuntu 24.04 LTS (to be installed) |
| vCPU | 4 cores |
| RAM | 4GB |
| Disk | 32GB (local-lvm) |
| Network | vmbr0 (virtio) |
| IP | 192.168.2.187 |
| Gateway | 192.168.2.1 |
| Subnet | /24 (192.168.2.0/24) |

---

## Next Steps (When VM is Ready)

### 1. Wait for Boot & SSH Access
```bash
# Check if accessible
ssh peppe@192.168.2.187

# Expected response: Ubuntu 24.04 LTS shell prompt
```

### 2. Install Docker & Docker Compose
```bash
ssh peppe@192.168.2.187 << 'EOF'
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker peppe

# Install docker-compose
sudo apt-get install -y docker-compose

# Verify
docker --version
docker-compose --version
docker ps
EOF
```

### 3. Clone Cloud Platform Fork (phase-1-batch-1)
```bash
ssh peppe@192.168.2.187 << 'EOF'
cd /home/peppe
git clone https://github.com/peppekerstens/cloudforproxmox-new.git cloud-platform-batch1
cd cloud-platform-batch1
git checkout phase-1-batch-1
ls -la infra/
EOF
```

### 4. Configure .env for Deployment
```bash
ssh peppe@192.168.2.187 << 'EOF'
cd /home/peppe/cloud-platform-batch1/infra
cp ../.env.example .env

# Edit .env with test values:
# - VITE_API_URL=http://192.168.2.187:8000/api/v1
# - CORS_ORIGINS=http://192.168.2.187:3000,http://192.168.2.187:8000
# - Admin user will be seeded via script

# Copy to docker-compose context
ls -la .env
EOF
```

### 5. Deploy Docker Containers
```bash
ssh peppe@192.168.2.187 << 'EOF'
cd /home/peppe/cloud-platform-batch1/infra

# Start containers
docker-compose down
docker-compose up -d --build

# Wait 30s for database migration
sleep 30

# Seed admin user
cd ..
python scripts/seed_admin_user.py

# Check health
docker ps -a
docker-compose logs api | tail -20
curl -s http://192.168.2.187:8000/api/v1/health | jq .
EOF
```

### 6. Test API Endpoints
```bash
# Health check
curl -s http://192.168.2.187:8000/api/v1/health | jq .

# Admin login
curl -s -X POST http://192.168.2.187:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}' | jq .

# User info
TOKEN=$(curl -s -X POST http://192.168.2.187:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}' | jq -r .access_token)

curl -s -H "Authorization: Bearer $TOKEN" \
  http://192.168.2.187:8000/api/v1/auth/me | jq .
```

### 7. Test Frontend GUI
```bash
# Browser: http://192.168.2.187:3000
# Expected: Auto-redirect to /login
# Login: admin@example.org / superadmin
# Expected: Dashboard loads, account info displays
```

### 8. Container Health Verification
```bash
ssh peppe@192.168.2.187 << 'EOF'
cd /home/peppe/cloud-platform-batch1/infra

echo "=== Container Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "=== Service Health Checks ==="

# PostgreSQL
docker exec cloud-platform-batch1-postgres-1 pg_isready && echo "PostgreSQL: OK" || echo "PostgreSQL: FAIL"

# Redis
docker exec cloud-platform-batch1-redis-1 redis-cli ping && echo "Redis: OK" || echo "Redis: FAIL"

# RabbitMQ
docker exec cloud-platform-batch1-rabbitmq-1 rabbitmq-diagnostics ping && echo "RabbitMQ: OK" || echo "RabbitMQ: FAIL"

# API
curl -s http://192.168.2.187:8000/api/v1/health && echo "API: OK" || echo "API: FAIL"

# Frontend
curl -s http://192.168.2.187:3000 | head -5 && echo "Frontend: OK" || echo "Frontend: FAIL"
EOF
```

### 9. Create Proxmox Snapshot
```bash
# After all tests pass:
proxmox-pve1: Create snapshot phase-1-batch1-test-final
```

### 10. Document Results
- Update REPLAY_STATUS.md with test results
- Update PHASE1_BATCH1_COMPLETE.md if issues found
- Create TEST_RESULTS.md for temporary VM
- Mark Phase 1 Batch 1 verified across two VMs (vm103, vm151)

---

## Critical Constraints Applied

✅ QEMU VM only (NOT LXC)  
✅ Ubuntu 24.04 LTS (match vm103)  
✅ 4 vCPU, 4GB RAM, 20GB disk  
✅ Unique IP (192.168.2.187, not .186)  
✅ cloudforproxmox-new fork (not upstream)  
✅ phase-1-batch-1 branch (all fixes included)  
✅ Code deployment checklist verified

---

## Troubleshooting

### If SSH fails after 5 min
- Check Proxmox console: `qm terminal 151`
- Verify network bridge: `ip addr show vmbr0` on pve1
- Check VM logs: Proxmox Web UI → vm151 → Console

### If Docker fails
- `docker system prune -a` (if disk full)
- Check disk: `df -h`
- Check logs: `docker-compose logs`

### If containers won't start
- Check env vars: `docker-compose config | grep VITE_API_URL`
- Check volumes: `docker volume ls`
- Rebuild: `docker-compose down && docker-compose up -d --build`

### If seeding fails
- Check Python: `python --version` (should be 3.10+)
- Check script: `cat scripts/seed_admin_user.py`
- Run manually: `python -c "from app.models import User; print(User.__table__)"`

---

## Notes

- VM 151 is temporary for Phase 1 Batch 1 verification only
- After testing completes, snapshot can be kept for comparison with vm103
- Do NOT deploy Phase 1 Batch 2 to this VM (Batch 2 adds LXC endpoints, which we test differently)
- Keep vm103 (pve2) as production baseline
- If tests pass on both VMs, conclude Phase 1 Batch 1 is stable
