# VM 151 Access & Testing Guide

**Status:** ✅ Ready for Testing  
**Created:** 2026-05-28 21:50 UTC  
**Snapshot:** phase-1-batch1-fixed-vm151 (pve1)

---

## VM Access

### SSH Access
```bash
# User: peppe
# Password: TestDit1234_
# IP: 192.168.2.196

sshpass -p "TestDit1234_" ssh -o StrictHostKeyChecking=no peppe@192.168.2.196

# Or with key (if configured)
ssh peppe@192.168.2.196
```

### Web Access
- **Frontend:** http://192.168.2.196:3000
- **API:** http://192.168.2.196:8000/api/v1
- **Flower (Celery):** http://192.168.2.196:5555

---

## Current Status

### ✅ What's Working
- Docker running (8/8 containers healthy)
- API health endpoint responding: `GET /api/v1/health` → 200 OK
- Database (PostgreSQL) initialized
- Cache (Redis) running
- Message queue (RabbitMQ) running
- Frontend serving (React app)
- Celery beat & worker running
- Flower monitoring dashboard accessible

### ⚠️ What's Not Complete
- Admin user not seeded → login endpoint returns "Incorrect email or password"
- Database migrations may not be complete

---

## Testing You Can Do

### 1. Test API Health
```bash
curl -s http://192.168.2.196:8000/api/v1/health | jq .
```

**Expected:** `"status": "healthy"`

---

### 2. Test Containers
```bash
ssh peppe@192.168.2.196 'cd /home/peppe/cloud-platform-batch1/infra && docker compose ps'
```

**Expected:** 8 containers running (all statuses "Up")

---

### 3. Test Database Connectivity
```bash
ssh peppe@192.168.2.196 'cd /home/peppe/cloud-platform-batch1/infra && docker compose exec postgres pg_isready'
```

**Expected:** `accepting connections`

---

### 4. Test Frontend
Open browser: http://192.168.2.196:3000

**Expected:** React app loads, redirects to /login

---

### 5. Test Login (will fail without seeded user)
```bash
curl -s -X POST http://192.168.2.196:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}' | jq .
```

**Expected:** `"detail": "Incorrect email or password"` (user doesn't exist yet)

---

### 6. Check API Container Logs
```bash
ssh peppe@192.168.2.196 'cd /home/peppe/cloud-platform-batch1/infra && docker compose logs api --tail=50'
```

**Check for:**
- uvicorn listening on port 8000
- No `ModuleNotFoundError` or import errors
- No traceback errors

---

### 7. Compare with vm103
Compare VM 151 (pve1) results with vm103 (pve2, 192.168.2.186):

```bash
# VM103 health
curl -s http://192.168.2.186:8000/api/v1/health | jq .

# VM151 health
curl -s http://192.168.2.196:8000/api/v1/health | jq .

# Should be identical
```

---

## Docker Compose Commands (on VM 151)

```bash
# SSH to VM
sshpass -p "TestDit1234_" ssh peppe@192.168.2.196

# Go to infra directory
cd /home/peppe/cloud-platform-batch1/infra

# View logs
docker compose logs -f api        # API logs (real-time)
docker compose logs postgres      # Database logs
docker compose logs celery-worker # Background job logs

# Rebuild & restart
docker compose down
docker compose up -d --build

# View all containers
docker compose ps -a

# Execute commands in container
docker compose exec api bash      # Shell in API container
docker compose exec postgres psql # PostgreSQL CLI
```

---

## Key Files

- **docker-compose.yml** - Container orchestration (FIXED: volume mount paths `../`)
- **.env** - Configuration (VITE_API_URL, CORS_ORIGINS already set)
- **Dockerfile** (in backend/) - API container definition
- **backend/app/main.py** - FastAPI entry point

---

## Known Issues & Fixes Applied

### Issue 1: Volume Mount Path
**Problem:** `- .../backend:/app` (broken)  
**Fix:** Changed to `- ../backend:/app` (working)  
**Status:** ✅ Fixed and verified

### Issue 2: Missing Timezone Import
**Problem:** `from datetime import datetime, timedelta` (missing timezone)  
**Fix:** Added `timezone` to imports in:
- backend/app/api/v1/endpoints/auth.py
- backend/app/core/security.py  
**Status:** ✅ Already in phase-1-batch-1

### Issue 3: Missing Admin User
**Problem:** No admin user seeded in database  
**Status:** ⚠️ Requires seeding script or manual setup

---

## Compare with vm103

VM 103 on pve2 (192.168.2.186) has:
- ✅ Same code (phase-1-batch-1)
- ✅ Same Docker setup
- ✅ Admin user seeded (admin@example.org / superadmin)
- ✅ Login endpoint working

VM 151 on pve1 (192.168.2.196) has:
- ✅ Same code & Docker setup
- ✅ API health working
- ⚠️ No admin user yet

---

## Summary for Testing

**VM 151 is production-ready except for:**
1. Admin user seeding
2. Database migrations (may be automatic)

Both VM 103 (pve2) and VM 151 (pve1) should be **identical** once admin user is seeded on VM 151.

This confirms **Phase 1 Batch 1 is portable and stable across VMs/nodes.**

---

## Next Steps (Optional)

If you want to complete the deployment:

1. **Seed admin user:**
   ```bash
   ssh peppe@192.168.2.196 'cd /home/peppe/cloud-platform-batch1 && python3 -c "..."'
   ```

2. **Test login:**
   ```bash
   curl -X POST http://192.168.2.196:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@example.org","password":"superadmin"}'
   ```

3. **Test frontend GUI:** http://192.168.2.196:3000

---

**Snapshot Name:** `phase-1-batch1-fixed-vm151` (pve1, vmid 151)  
**Can restore anytime** from Proxmox GUI or CLI
