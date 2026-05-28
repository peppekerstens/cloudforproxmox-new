#!/bin/bash

# Deploy Cloud Platform Phase 1 Batch 1 to VM 151
# Run this script on VM 151 after SSH access is available

set -e

VM_IP="192.168.2.187"
REPO_URL="https://github.com/peppekerstens/cloudforproxmox-new.git"
BRANCH="phase-1-batch-1"
DEPLOY_DIR="/home/peppe/cloud-platform-batch1"

echo "=========================================="
echo "Cloud Platform Phase 1 Batch 1 Deployment"
echo "=========================================="
echo "VM: $VM_IP"
echo "Branch: $BRANCH"
echo ""

# ==========================================
# 1. Update System
# ==========================================
echo "[1/7] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y
echo "✅ System updated"
echo ""

# ==========================================
# 2. Install Docker & Docker Compose
# ==========================================
echo "[2/7] Installing Docker & Docker Compose..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker peppe
sudo apt-get install -y docker-compose
docker --version
docker-compose --version
echo "✅ Docker installed"
echo ""

# ==========================================
# 3. Clone Repository
# ==========================================
echo "[3/7] Cloning cloudforproxmox-new repository..."
cd /home/peppe
git clone $REPO_URL $DEPLOY_DIR
cd $DEPLOY_DIR
git checkout $BRANCH
echo "✅ Repository cloned"
echo ""

# ==========================================
# 4. Configure Environment
# ==========================================
echo "[4/7] Configuring environment..."
cd infra
cp ../.env.example .env

# Update .env with VM151 specific values
sed -i "s|VITE_API_URL=.*|VITE_API_URL=http://192.168.2.187:8000/api/v1|g" .env
sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=http://192.168.2.187:3000,http://192.168.2.187:8000|g" .env

echo "✅ .env configured for VM 151"
cat .env | grep -E "VITE_API_URL|CORS_ORIGINS"
echo ""

# ==========================================
# 5. Deploy Containers
# ==========================================
echo "[5/7] Starting Docker containers..."
docker-compose down 2>/dev/null || true
docker-compose up -d --build

echo "Waiting 30s for database migrations..."
sleep 30

echo "✅ Containers started"
docker-compose ps
echo ""

# ==========================================
# 6. Seed Admin User
# ==========================================
echo "[6/7] Seeding admin user..."
cd ..
python3 scripts/seed_admin_user.py

echo "✅ Admin user seeded"
echo ""

# ==========================================
# 7. Test Deployment
# ==========================================
echo "[7/7] Testing deployment..."
echo ""

echo "Health Check:"
curl -s http://192.168.2.187:8000/api/v1/health | python3 -m json.tool || echo "API not ready yet"
echo ""

echo "Login Test:"
TOKEN=$(curl -s -X POST http://192.168.2.187:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', 'FAILED'))")

if [ "$TOKEN" != "FAILED" ] && [ ! -z "$TOKEN" ]; then
  echo "✅ Login successful, token issued"
  echo ""
  echo "User Info:"
  curl -s -H "Authorization: Bearer $TOKEN" http://192.168.2.187:8000/api/v1/auth/me | python3 -m json.tool
else
  echo "⚠️  Login not yet available (API still initializing)"
fi

echo ""
echo "=========================================="
echo "✅ Phase 1 Batch 1 Deployment Complete"
echo "=========================================="
echo "Frontend: http://192.168.2.187:3000"
echo "API: http://192.168.2.187:8000/api/v1"
echo "Admin: admin@example.org / superadmin"
echo ""
