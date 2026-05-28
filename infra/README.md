# Infrastructure

Deployment configuration for Proxmox ISP.

## Files

| File | Purpose |
|---|---|
| `docker-compose.yml` | Docker Compose stack (PostgreSQL, Redis, FastAPI, Celery, React) |
| `.env.example` | Environment variable template — copy to `.env` and fill in |

## Quick Deploy

```bash
cp infra/.env.example infra/.env
# Edit infra/.env with your values

docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
docker compose -f infra/docker-compose.yml exec api python scripts/create_admin.py
```

## Services

| Service | Port | Description |
|---|---|---|
| `api` | 8000 | FastAPI backend (REST API) |
| `frontend` | 3000 | React frontend (Vite dev server) |
| `postgres` | 5432 | PostgreSQL 16 database |
| `redis` | 6379 | Redis (cache + Celery broker) |
| `celery-worker` | — | Celery async task worker |
| `celery-beat` | — | Celery periodic task scheduler |

## LXC Deployment

The stack runs inside a Proxmox LXC container:

1. Create Ubuntu 24.04 LXC (2 CPU, 2GB RAM, 16GB disk)
2. Install Docker inside LXC
3. Copy repo to LXC `/root/`
4. Create `.env` from `.env.example`
5. Run `docker compose up -d`

## Backup

```bash
# Database backup
docker compose -f infra/docker-compose.yml exec postgres pg_dump -U proxmoxisp proxmoxisp > backup.sql

# Restore
docker compose -f infra/docker-compose.yml exec -T postgres psql -U proxmoxisp proxmoxisp < backup.sql
```
