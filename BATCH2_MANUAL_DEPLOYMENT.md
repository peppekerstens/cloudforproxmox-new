# Phase 1 Batch 2: Manual Deployment Guide

**Status:** Ready for manual execution  
**Date:** 2026-05-29  
**Target:** vm103 (192.168.2.186)  
**Time:** ~5 minutes

---

## Step 1: SSH to vm103

```bash
ssh ubuntu@192.168.2.186
```

**Expected:** Connected to vm103

---

## Step 2: Update Code to Batch 2

```bash
cd ~/cloud-platform-upstream

# Fetch latest code
git fetch origin

# Checkout Batch 2 branch
git checkout phase-1-batch-2

# Verify you're on the right branch
git branch --show-current
git log --oneline -1
```

**Expected output:**
```
phase-1-batch-2
96f1811 feat: Phase 1 Batch 2 - LXC, VM templates, cluster detail page, ISO transfers
```

---

## Step 3: Restart Containers

```bash
# Stop old containers
docker-compose down

# Start new containers with Batch 2 code
docker-compose up -d

# Wait for containers to start
sleep 30

# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Expected:** 8 containers running
- postgres
- redis
- rabbitmq
- cloud-platform-api
- cloud-platform-frontend
- cloud-platform-celery-beat
- cloud-platform-celery-worker
- flower

---

## Step 4: Test Deployment

```bash
# Test login endpoint
curl -X POST http://192.168.2.186:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.org","password":"superadmin"}'
```

**Expected response:**
```json
{"access_token":"eyJ0eXAiOiJKV1QiLCJhbGc...","token_type":"bearer"}
```

If you see `access_token`, login is working ✅

---

## Step 5: Test GUI

```bash
curl -s http://192.168.2.186:3000/ | head -20
```

**Expected:** HTML with `<title>` tag (React app)

---

## Step 6: Check Batch 2 Features (Optional)

```bash
# Test LXC endpoint (if available in Batch 2)
curl -X GET http://192.168.2.186:8000/api/v1/vms/lxc \
  -H "Authorization: Bearer <your_token_from_step_4>"

# Test VM templates endpoint
curl -X GET http://192.168.2.186:8000/api/v1/vms/templates \
  -H "Authorization: Bearer <your_token_from_step_4>"

# Test cluster detail page
curl -X GET http://192.168.2.186:8000/api/v1/clusters/1 \
  -H "Authorization: Bearer <your_token_from_step_4>"
```

These are new Batch 2 features - they may not be fully wired yet.

---

## Step 7: Check Logs for Errors

```bash
# View last 50 lines of API logs
docker logs cloud-platform-api | tail -50

# Check for migration errors
docker logs cloud-platform-api | grep -i "error\|migration\|alembic"
```

If you see errors, report them. Otherwise, deployment is clean ✅

---

## Step 8: Exit vm103

```bash
exit
```

---

## Step 9: Create Snapshot (on pve2)

Run this on your local machine or pve2:

```bash
# SSH to pve2
ssh root@192.168.2.22

# Create snapshot
qm snapshot 103 phase-1-batch-2-verified -d "Phase 1 Batch 2 verified on vm103, LXC + templates + cluster pages"

# Verify snapshot created
qm listsnapshot 103 | grep phase-1-batch-2-verified

# Optional: Clean up old snapshots (keep last 3)
qm listsnapshot 103 | grep "phase-1-batch" | sort

# Exit pve2
exit
```

**Expected output:**
```
phase-1-batch-2-verified                 <timestamp>
```

---

## Step 10: Verification Summary

After completing all steps, you should have:

- ✅ vm103 running phase-1-batch-2 branch
- ✅ 8/8 containers healthy and running
- ✅ Login endpoint responding with access_token
- ✅ GUI loads at http://192.168.2.186:3000
- ✅ No errors in docker logs
- ✅ Snapshot phase-1-batch-2-verified created on pve2

---

## Troubleshooting

### Login fails with "access_token not in response"
- Check API is running: `docker ps | grep api`
- Check logs: `docker logs cloud-platform-api`
- Verify .env credentials: `cat .env | grep ADMIN`

### Containers not starting
- Check docker-compose syntax: `docker-compose config`
- Check disk space: `df -h`
- Check logs: `docker-compose logs`

### Network issues
- Verify IP: `ip addr show`
- Test gateway: `ping 192.168.2.250`
- Test DNS: `ping 8.8.8.8`

### Snapshot creation fails
- Verify pve2 connectivity: `ping 192.168.2.22`
- Check qm available: `qm list`
- Check vm103 exists: `qm status 103`

---

## Next Steps

Once deployment verified:

1. **Option A:** Continue to Phase 1 Batch 3
   - Apply 8 more commits (ba81e42..8b05695)
   - Test on vm103 or vm151

2. **Option B:** Run detailed tests
   - Playwright GUI tests
   - API endpoint tests
   - Load testing

3. **Option C:** Deploy to vm151 (temporary)
   - Clone vm103 → vm151
   - Verify cross-node functionality
   - Compare results

---

## Time Estimate

- Steps 1-3: 3 minutes (code update + restart)
- Steps 4-7: 2 minutes (testing)
- Step 8: 30 seconds (exit)
- Step 9: 1 minute (snapshot)
- **Total: ~5 minutes**

