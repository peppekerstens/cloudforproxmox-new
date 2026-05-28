# Phase 12 Security Checkpoint

**Phase:** Phase 12 (HTTPS/TLS/Certificate Management)  
**Objective:** Enable HTTPS on web portal before Phase 12 replay  
**Status:** Pre-Deployment Checklist  
**Applies To:** cloudforproxmox-new REPLAY_PLAN_PHASE12.md execution

---

## Context

**Phase 12 is the KNOWN FAILURE POINT** in cloudforproxmox-old. Repo history shows HTTPS/backend-frontend TLS split failed with certificate/proxy issues.

**Goals of this checkpoint:**
1. Pre-identify all TLS/cert/proxy configurations
2. Verify architecture before deploying Phase 12 commits
3. Create rollback plan if Phase 12 fails again
4. Document exact failure symptoms for analysis

---

## Pre-Phase 12 Security Audit Checklist

### A. TLS Certificate Strategy

**Question:** How are certificates generated and managed?

**Verification steps:**
- [ ] Check REPLAY_PLAN_PHASE12.md for certificate generation commits
- [ ] Identify certificate backend: self-signed, Let's Encrypt, acme.sh, or manual?
- [ ] Verify cert storage location in docker-compose.yml volumes
- [ ] Check cert renewal mechanism (cron? systemd timer? Certbot?)

**Action if found issue:**
- Self-signed certs: Verify cert path in nginx config matches volume mount
- Let's Encrypt: Ensure domain resolves to vm103 IP (or use DNS-01 challenge)
- acme.sh: Verify API credentials available in infra/.env
- Manual certs: Verify files exist and perms are 644 (readable by nginx)

**Exit criteria:**
- Cert generation method documented in commit message
- Cert path and storage documented
- Renewal procedure (if automated) documented

---

### B. Nginx Proxy TLS Configuration

**Question:** How is Nginx configured for HTTPS?

**Verification steps:**
- [ ] Find nginx config in docker-compose or infra/
- [ ] Verify cert file path: does it match docker-compose volume mount?
- [ ] Verify key file path: separate from cert? Correct perms (600)?
- [ ] Check TLS version: should be ≥1.2 (TLS 1.3 preferred)
- [ ] Verify cipher suite: no deprecated ciphers
- [ ] Check HSTS header: `Strict-Transport-Security` enabled?
- [ ] Verify SSL protocols: `ssl_protocols TLSv1.2 TLSv1.3;`

**Example expected nginx.conf snippet:**
```nginx
server {
  listen 443 ssl http2;
  server_name _;
  
  ssl_certificate /etc/nginx/certs/cert.pem;
  ssl_certificate_key /etc/nginx/certs/key.pem;
  
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers HIGH:!aNULL:!MD5;
  ssl_prefer_server_ciphers on;
  
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  
  # ...
}
```

**Action if found issue:**
- Cert path mismatch: Update docker-compose volume
- Cert not found in volume: Check if cert generation commit ran
- TLS version too old: Update nginx.conf
- HSTS missing: Add header

**Exit criteria:**
- Nginx config reviewed and verified
- Cert/key paths match docker-compose volumes
- TLS 1.2+ enforced
- HSTS header present

---

### C. Backend API HTTPS Configuration

**Question:** Does FastAPI enforce HTTPS for API endpoints?

**Verification steps:**
- [ ] Check FastAPI code: does it have `@app.get(..., secure=True)` decorators?
- [ ] Verify CORS config includes HTTPS origins: `https://192.168.2.186:443` or `https://localhost:443`?
- [ ] Check env var: `HTTPS_ENABLED` or similar?
- [ ] Verify backend listens on all interfaces (0.0.0.0) for nginx proxy
- [ ] Check if backend redirects HTTP → HTTPS or lets nginx handle it

**Example expected config:**
```python
# .env
HTTPS_ENABLED=true
CORS_ORIGINS=https://192.168.2.186:443,https://localhost:443

# FastAPI code
app = FastAPI()
app.add_middleware(CORSMiddleware, 
    allow_origins=CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**Action if found issue:**
- HTTPS_ENABLED not set: Add to infra/.env
- CORS origins missing https: Update infra/.env
- Backend redirects HTTP: Let nginx handle (no redirect needed if behind proxy)

**Exit criteria:**
- FastAPI CORS includes HTTPS origins
- Backend listens on 0.0.0.0:8000 (nginx proxies)
- No backend HTTP→HTTPS redirect (nginx handles)

---

### D. Frontend HTTPS Configuration

**Question:** Does React frontend use HTTPS API endpoint?

**Verification steps:**
- [ ] Check frontend/.env.example: `VITE_API_URL`
- [ ] Expected value: `https://192.168.2.186:443/api/v1` or similar
- [ ] Verify env var is used in API client (not hardcoded)
- [ ] Check browser console for mixed-content warnings (HTTP resource on HTTPS page)
- [ ] Verify CSP headers don't block HTTPS API calls

**Example expected config:**
```javascript
// frontend/.env
VITE_API_URL=https://192.168.2.186:443/api/v1

// frontend/src/api.ts
const API_URL = import.meta.env.VITE_API_URL || "https://localhost:443/api/v1";
const response = await fetch(`${API_URL}/users`, {...});
```

**Action if found issue:**
- API_URL uses HTTP: Update frontend/.env to HTTPS
- API_URL hardcoded: Extract to env var
- Mixed content warnings: Check nginx headers, CSP policy
- CSP blocks API: Relax CSP or add API domain explicitly

**Exit criteria:**
- Frontend VITE_API_URL uses HTTPS
- No hardcoded HTTP endpoints in frontend code
- No mixed-content browser warnings when loaded over HTTPS

---

### E. Docker Compose Volume Mounts

**Question:** Are certificate files properly mounted from host to containers?

**Verification steps:**
- [ ] Check docker-compose.yml: does nginx service have cert volumes?
- [ ] Example: `- ./infra/certs:/etc/nginx/certs:ro`
- [ ] Verify cert directory exists on vm103: `ls -la /home/peppe/github/proxmox-isp/infra/certs/`
- [ ] Check perms: cert files readable (644), key files restricted (600)?
- [ ] Verify volume path in Dockerfile or docker-compose is correct

**Example expected config:**
```yaml
services:
  nginx:
    image: nginx:latest
    volumes:
      - ./infra/certs:/etc/nginx/certs:ro
    ports:
      - "443:443"
```

**Action if found issue:**
- Volume path doesn't exist: Create `infra/certs/` directory
- Cert files missing: Generate/retrieve from git LFS or pre-phase commit
- Perms too open (777): Restrict to 644 (cert) and 600 (key)
- Volume mount path wrong: Fix docker-compose.yml

**Exit criteria:**
- `infra/certs/` directory exists
- Cert files are present (cert.pem, key.pem, or equivalent)
- File perms are correct (644/600)
- docker-compose volume mounts to `/etc/nginx/certs`

---

### F. Port Mapping & Network Config

**Question:** Are ports 80/443 mapped correctly from host to containers?

**Verification steps:**
- [ ] Check docker-compose: nginx should map `80:80` and `443:443`
- [ ] Verify no other service conflicts with these ports: `netstat -tlnp | grep :80\|:443`
- [ ] Check iptables/firewall rules don't block 443: `sudo iptables -L -n | grep 443`
- [ ] Verify nginx is listening: `docker logs nginx | grep "listen"`

**Example expected config:**
```yaml
nginx:
  ports:
    - "80:80"
    - "443:443"
```

**Action if found issue:**
- Port 443 already in use: Find conflicting process, stop it
- Firewall blocks 443: Add rule: `sudo ufw allow 443/tcp`
- Nginx fails to start: Check cert files exist, perms correct, no syntax errors

**Exit criteria:**
- Ports 80/443 mapped in docker-compose
- No conflicting processes on ports 80/443
- Firewall allows inbound 443
- Nginx container starts without error

---

### G. Health Check & Verification

**Question:** Can we verify HTTPS is working before Phase 12 commit replay?

**Verification steps:**
- [ ] Manual curl test (after containers up): `curl -k https://localhost/` (should not hang)
- [ ] Check TLS cert: `echo | openssl s_client -connect localhost:443 2>/dev/null | openssl x509 -noout -text | grep -A5 "Subject:"`
- [ ] Check HTTP redirect: `curl -L http://localhost/ | head -20` (should redirect to HTTPS or serve HTTPS content)
- [ ] Browser test: Navigate to `https://192.168.2.186/login`, check cert is valid (not self-signed warning)
- [ ] API health: `curl -k https://localhost:8000/health` should return 200

**Exit criteria:**
- TLS certificate present and valid (curl -k succeeds)
- Nginx listens on 443 (netstat shows LISTEN on :443)
- HTTP redirects to HTTPS (or both serve content)
- API accessible over HTTPS

---

## Known Failure Modes (from old repo)

**Phase 12 failed with these symptoms:**

1. **Certificate file missing at boot**
   - Symptom: Nginx container exits with "permission denied" reading /etc/nginx/certs/cert.pem
   - Root cause: Volume mount path wrong or cert not generated before docker-compose up
   - Prevention: Run cert generation commit BEFORE nginx starts

2. **TLS handshake timeout**
   - Symptom: `curl https://localhost` hangs for 30s then times out
   - Root cause: Nginx SSL config syntax error (bad cipher, protocol mismatch)
   - Prevention: Test nginx config locally: `docker exec nginx nginx -t`

3. **Backend unreachable from frontend over HTTPS**
   - Symptom: Frontend loads, but API calls fail with "ERR_CERT_AUTHORITY_INVALID"
   - Root cause: Self-signed cert not trusted by browser OR CORS headers missing
   - Prevention: Test API via curl first (bypasses cert validation)

4. **CORS error on HTTPS calls**
   - Symptom: Browser console: "Access to XMLHttpRequest blocked by CORS policy"
   - Root cause: CORS_ORIGINS env var doesn't include HTTPS scheme
   - Prevention: Ensure CORS_ORIGINS=https://...:443, not http://...:80

5. **Cert renewal fails**
   - Symptom: Cert expires, renewal script doesn't run or fails
   - Root cause: Certbot credentials not in .env, cron job not set up
   - Prevention: Document renewal procedure before Phase 12, test it

---

## Rollback Decision Tree

**If Phase 12 fails:**

1. **Get exact error from logs:**
   ```bash
   docker logs nginx 2>&1 | tail -50
   docker logs fastapi 2>&1 | tail -50
   docker logs react 2>&1 | tail -50
   ```

2. **Identify failure type:**
   - **Cert missing:** Rollback to snapshot-{previous-phase}, re-run cert generation commit
   - **TLS config error:** Rollback, fix nginx.conf, re-test locally, re-run deploy
   - **CORS error:** Rollback, update infra/.env CORS_ORIGINS, re-run
   - **Backend unreachable:** Rollback, verify API health before proxy, test curl

3. **Fallback strategy:**
   - Rollback to snapshot-040259b if available
   - Document actual error vs. expected error
   - Compare with cloudforproxmox-old issue tracker
   - Escalate to user with full logs + analysis

---

## Pre-Phase 12 Deployment Checklist

**Run this BEFORE executing REPLAY_PLAN_PHASE12.md:**

- [ ] **Certificates ready:** Cert files exist, perms correct, location documented
- [ ] **Nginx config reviewed:** TLS version ≥1.2, HSTS enabled, cert paths correct
- [ ] **Backend HTTPS:** FastAPI CORS includes https:// origins
- [ ] **Frontend HTTPS:** VITE_API_URL uses https:// scheme
- [ ] **Docker volumes:** infra/certs exists, docker-compose.yml has volume mounts
- [ ] **Ports available:** 80/443 not in use, firewall allows inbound
- [ ] **Previous phase healthy:** Snapshot-{previous-phase} exists, passes health check
- [ ] **Rollback plan:** Snapshot before Phase 12 deploy, rollback procedure documented

**When all checks pass:** Execute REPLAY_PLAN_PHASE12.md

**If Phase 12 fails:** Use rollback decision tree above.

---

## Reference Commits (from cloudforproxmox-old)

- `146775f` (05-25): Cert management backend — where certs generated?
- `647b3f1` (05-25): Enable HTTPS Nginx proxy — where TLS config?
- `5300e90` (05-26): Close DNS/audit gaps — final fixes
- `7e93408` (05-26): Billing provider abstraction — API updates?
- `2ca9e1b` (05-26): Billing refactor complete — before HTTPS
- `040259b` (05-26): Deployment checklist — EXPECTED FAILURE HERE

**Action:** Review these commits during Phase 12 prep to understand cert/TLS approach.

---

## Success Criteria

**Phase 12 is successful when:**
- [ ] `curl -k https://localhost:443/` returns 200 (nginx responds)
- [ ] `curl -k https://localhost:8000/health` returns 200 (API responds)
- [ ] Browser access to `https://192.168.2.186/login` loads login page
- [ ] Login form submits without CORS errors
- [ ] API calls from frontend succeed (check network tab in browser dev tools)
- [ ] TLS certificate is valid (curl shows cert chain)
- [ ] All 8 Docker containers healthy: `docker ps --format "table {{.Names}}\t{{.Status}}" | grep Up`

**When all succeeded:** Document in REPLAY_STATUS.md and move to final assessment phase.
