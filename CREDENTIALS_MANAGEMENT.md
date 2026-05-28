# Credentials Management & Security

**Status:** Development phase  
**Audience:** DevOps, Security teams, Developers  
**Last Updated:** 2026-05-28

---

## Overview

This document describes how credentials are managed across different deployment environments and development phases.

### Key Principle
> **Credentials are NEVER committed to git.** Use `.env` files and secure vaults.

---

## Environments

### Development (Local / vm103)

**Purpose:** Testing, debugging, feature development  
**Credential Source:** `.env` file (git-ignored)  
**Lifecycle:** Reset per deployment

**Initial Admin User:**
```
Email:    admin@example.org
Username: admin
Password: superadmin (TEMPORARY - for testing only)
Status:   Active, Superadmin role
```

**Setup:**
```bash
# 1. Copy template
cp .env.example .env

# 2. Edit with your values
vi .env

# 3. Deploy
docker-compose up -d

# 4. Seed admin user (if needed)
docker exec cloudplatform-api python create_admin_user.py
```

### Staging (Pre-production testing)

**Purpose:** Testing in production-like environment  
**Credential Source:** AWS Secrets Manager / HashiCorp Vault / Environment variables  
**Lifecycle:** Persist across deployments (rotate quarterly)

**Requirements:**
- [ ] Use strong random passwords (32+ characters)
- [ ] Rotate credentials every 90 days
- [ ] Enable MFA for admin accounts
- [ ] Audit all credential access

### Production

**Purpose:** Live customer-facing service  
**Credential Source:** HashiCorp Vault or equivalent  
**Lifecycle:** Persist, rotate on schedule, revoke on compromise

**Security Requirements:**
- [ ] Zero hardcoded secrets anywhere (code, docs, configs)
- [ ] All credentials in secure vault (never in .env files)
- [ ] Environment variables injected at runtime
- [ ] Encrypted at rest, encrypted in transit
- [ ] Audit logs for all credential access
- [ ] Automated credential rotation
- [ ] Incident response plan for compromise

---

## Credentials by Component

### 1. Database (PostgreSQL)

**Development:**
```
User:     cloudplatform
Password: cloudplatform_dev_password
Host:     postgres (container)
```

**Production:**
- Use AWS RDS with IAM authentication, OR
- Use managed database service with encrypted credentials
- Never use default passwords

### 2. Cache (Redis)

**Development:**
```
Password: cloudplatform_redis_password
Host:     redis (container)
Port:     6379
```

**Production:**
- Enable Redis ACL (access control lists)
- Use Redis TLS encryption
- Store password in vault, never in code

### 3. Message Queue (RabbitMQ)

**Development:**
```
User:     cloudplatform
Password: cloudplatform_rabbit_password
Host:     rabbitmq (container)
```

**Production:**
- Use RabbitMQ user/password from vault
- Enable TLS for AMQP connections
- Rotate credentials monthly

### 4. JWT Secret Key

**Development:**
```
Length:   32+ characters (minimum)
Renewal:  Per deployment/testing
```

**Production:**
```
Length:   256 bits minimum
Storage:  Vault (not environment variable)
Renewal:  Annually or on key compromise
Rotation: Gradual (old key valid for 30 days)
```

**Generate Strong Key:**
```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: OpenSSL
openssl rand -base64 32

# Option 3: ssh-keygen
ssh-keygen -t ed25519 -f jwt_key -N ""
```

### 5. Admin User

**Development (Batch 1):**
```
Email:    admin@example.org
Username: admin
Password: superadmin (TEST ONLY - reset on production)
```

**Production:**
```
Email:    <change per deployment>
Username: <change per deployment>
Password: <generate 16+ random characters>
MFA:      Enabled
```

**Generate Secure Password:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(16))"
# Example output: abc123def456ghi789jklmno
```

---

## Deployment Workflows

### Local Development

```bash
# 1. Clone repo
git clone https://github.com/peppekerstens/cloudforproxmox-new.git
cd cloudforproxmox-new

# 2. Create .env from template
cp .env.example .env

# 3. Edit .env with your values (keep defaults for dev)
nano .env

# 4. Deploy
docker-compose up -d

# 5. Seed initial admin (if database empty)
docker exec cloudplatform-api python /scripts/seed_admin.py

# 6. Login
# Email:    admin@example.org
# Password: superadmin (or whatever you set in .env)
```

### Staging Deployment

```bash
# 1. Load credentials from vault
export $(cat /secure/staging.env | xargs)

# 2. Deploy with vault-supplied credentials
docker-compose up -d --build

# 3. Verify no credentials in logs
docker-compose logs | grep -i password  # Should be empty

# 4. Run security checks
docker exec cloudplatform-api python -m pytest tests/security/
```

### Production Deployment

```bash
# 1. All credentials come from Kubernetes Secrets / Vault
# No .env file committed or used

# 2. Kubernetes deployment
kubectl apply -f k8s/production/

# 3. Vault injects credentials at runtime
# See: helm/values.prod.yaml

# 4. Verify no secrets in logs/errors
kubectl logs -f deployment/cloudplatform-api | grep -i secret
```

---

## Security Checklist

### Before Each Deployment

- [ ] No `.env` file in git
- [ ] `.env` in `.gitignore`
- [ ] All secrets sourced from vault/secrets manager (production)
- [ ] Credentials not in debug output/logs
- [ ] Default passwords changed
- [ ] JWT secret key is strong (256+ bits)
- [ ] Database password is strong (32+ characters)
- [ ] No credentials in shell history

### Before Production Release

- [ ] All hardcoded credentials removed
- [ ] All test credentials documented and tracked
- [ ] Vault/Secrets Manager configured
- [ ] Automated credential rotation enabled
- [ ] Incident response plan created
- [ ] Security audit completed
- [ ] Credentials rotation documented in runbook

### Ongoing

- [ ] Quarterly credential rotation
- [ ] Access logs reviewed monthly
- [ ] Compromised credentials revoked immediately
- [ ] New team members receive vault access only
- [ ] Old credentials removed after rotation grace period

---

## Common Mistakes (DON'T DO THIS)

❌ **Commit .env to git**
```bash
git add .env  # WRONG - contains credentials
```

❌ **Commit credentials in docker-compose.yml**
```yaml
environment:
  - DATABASE_PASSWORD=my_password  # WRONG - visible to anyone with git access
```

❌ **Log credentials in error messages**
```python
logger.error(f"Failed to connect: {db_password}")  # WRONG
```

❌ **Share credentials in documentation**
```markdown
Admin: admin@example.org
Password: superadmin  # WRONG - commit history is forever
```

❌ **Use the same password everywhere**
```
db_password = admin_password = redis_password = "same123"  # WRONG
```

---

## Correct Approach

✅ **Use .env.example as template**
```bash
cp .env.example .env
# Edit .env with actual values
# .env is automatically git-ignored
```

✅ **Reference environment variables in code**
```python
db_password = os.environ.get("DATABASE_PASSWORD")
```

✅ **Inject credentials at runtime**
```bash
docker run \
  -e DATABASE_PASSWORD=${DATABASE_PASSWORD} \  # From vault/secrets manager
  myapp
```

✅ **Document placeholders, not values**
```markdown
Set ADMIN_PASSWORD=<strong-random-password> in .env
```

✅ **Use different credentials per environment**
```
dev:  admin@example.org / superadmin
staging: ops-staging@company.com / [generated]
prod: ops-prod@company.com / [generated]
```

---

## Vault Integration (Future)

### HashiCorp Vault Setup
```bash
# Store credentials in Vault
vault kv put secret/cloudplatform/dev \
  database_password="..." \
  jwt_secret="..." \
  admin_password="..."

# Retrieve at runtime
vault kv get -format=json secret/cloudplatform/dev | jq -r '.data.data'
```

### Kubernetes Secrets
```bash
# Create secret from file
kubectl create secret generic cloudplatform-secrets \
  --from-file=.env=.env.prod \
  --namespace=production

# Reference in pod spec
env:
  - name: JWT_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: cloudplatform-secrets
        key: jwt_secret_key
```

---

## References

- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [12-Factor App: Config](https://12factor.net/config)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)

---

## Questions?

For credential security concerns, contact the security team or create an issue at https://github.com/peppekerstens/cloudforproxmox-new/issues

