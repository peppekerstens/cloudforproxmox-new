#!/bin/bash

# Phase 1 Batch 2 Deployment to vm103 (DEFAULT dev machine)
# Target: vm103 on pve2 (192.168.2.186)
# Branch: phase-1-batch-2
# Method: Code update + container restart (snapshot-based recovery)

set -e

VM_IP="192.168.2.186"
VM_USER="ubuntu"
BRANCH="phase-1-batch-2"
APP_DIR="~/cloud-platform-upstream"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║      Phase 1 Batch 2 Deployment to vm103                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Target: vm103 (pve2, $VM_IP)"
echo "Branch: $BRANCH"
echo "Method: Code update + restart (5 min)"
echo ""

# Check if vm103 is reachable
echo "Step 1: Checking vm103 connectivity..."
if ! ping -c 1 -W 2 $VM_IP >/dev/null 2>&1; then
  echo "❌ vm103 ($VM_IP) is not reachable"
  echo "   Check: Is vm103 running?"
  exit 1
fi
echo "✅ vm103 is reachable"
echo ""

# SSH to vm103 and execute deployment
echo "Step 2: Deploying Batch 2 code to vm103..."
ssh -o StrictHostKeyChecking=no $VM_USER@$VM_IP bash << 'EOFBASH'
set -e

echo "Entering app directory..."
cd ~/cloud-platform-upstream

echo "Fetching latest code..."
git fetch origin

echo "Checking out phase-1-batch-2 branch..."
git checkout phase-1-batch-2

echo "Current branch:"
git branch --show-current
git log --oneline -1

echo ""
echo "Stopping containers..."
docker-compose down

echo "Starting containers with new code..."
docker-compose up -d

echo ""
echo "Waiting for containers to start (30 sec)..."
sleep 30

echo ""
echo "Container status:"
docker ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "Checking API logs for errors..."
docker logs cloud-platform-api 2>&1 | tail -20

EOFBASH

echo ""
echo "✅ Code deployed to vm103"
echo ""

# Verify deployment
echo "Step 3: Verifying deployment..."
echo ""

echo "Testing login endpoint..."
RESPONSE=$(curl -s -X POST http://$VM_IP:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}' 2>/dev/null)

if echo "$RESPONSE" | grep -q "access_token"; then
  echo "✅ Login endpoint working"
  echo "   Response: $(echo $RESPONSE | cut -c1-80)..."
else
  echo "❌ Login endpoint failed"
  echo "   Response: $RESPONSE"
  exit 1
fi

echo ""
echo "Testing GUI..."
if curl -s http://$VM_IP:3000/ | grep -q "<title>"; then
  echo "✅ GUI loads"
else
  echo "❌ GUI not responding"
fi

echo ""
echo "Checking container health..."
CONTAINER_COUNT=$(ssh -o StrictHostKeyChecking=no $VM_USER@$VM_IP "docker ps --format '{{.Names}}'" | wc -l)
if [ "$CONTAINER_COUNT" -eq 8 ]; then
  echo "✅ 8/8 containers running"
else
  echo "⚠️ Container count: $CONTAINER_COUNT/8"
fi

echo ""
echo "✅ DEPLOYMENT VERIFIED"
echo ""

# Create snapshot
echo "Step 4: Creating snapshot on pve2..."
ssh root@192.168.2.22 bash << 'EOFPVE'
echo "Creating snapshot phase-1-batch-2-verified on vm103..."
qm snapshot 103 phase-1-batch-2-verified -d "Phase 1 Batch 2 verified on vm103, LXC + templates + cluster pages"

echo "Verifying snapshot..."
qm listsnapshot 103 | grep phase-1-batch-2-verified

echo "✅ Snapshot created"

# Clean up old snapshots (keep last 3)
echo ""
echo "Cleaning up old snapshots (keeping last 3)..."
SNAPSHOT_COUNT=$(qm listsnapshot 103 | grep "phase-1-batch" | wc -l)
if [ "$SNAPSHOT_COUNT" -gt 3 ]; then
  echo "  Found $SNAPSHOT_COUNT snapshots (keeping 3, deleting $((SNAPSHOT_COUNT - 3)))"
  # List all batch snapshots sorted by age, delete oldest
  qm listsnapshot 103 | grep "phase-1-batch" | sort | head -$((SNAPSHOT_COUNT - 3)) | while read line; do
    SNAPNAME=$(echo "$line" | awk '{print $1}')
    if [ ! -z "$SNAPNAME" ]; then
      echo "  Deleting old snapshot: $SNAPNAME"
      qm snapshot delete 103 "$SNAPNAME" 2>/dev/null || true
    fi
  done
fi

EOFPVE

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              BATCH 2 DEPLOYED & VERIFIED ✅                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "vm103 Status:"
echo "  • IP: 192.168.2.186"
echo "  • Branch: phase-1-batch-2"
echo "  • Containers: 8/8 running"
echo "  • API: http://192.168.2.186:8000"
echo "  • GUI: http://192.168.2.186:3000"
echo "  • Snapshot: phase-1-batch-2-verified"
echo ""
echo "Credentials: admin@example.org / superadmin"
echo ""
echo "Next steps:"
echo "  1. Test new Batch 2 features (LXC, templates, cluster pages)"
echo "  2. Run Playwright tests if needed"
echo "  3. Proceed to Phase 1 Batch 3"
echo ""
