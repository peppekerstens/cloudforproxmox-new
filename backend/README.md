# Backend — FastAPI Application

REST API for Proxmox ISP. Built with FastAPI, SQLAlchemy 2.0 (async), and Celery.

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables (or create .env)
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/proxmoxisp
export REDIS_URL=redis://localhost:6379/0
export JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
export PROXMOX_API_URL=https://<pve-ip>:8006/api2/json
export PROXMOX_API_TOKEN_ID=isp-portal
export PROXMOX_API_TOKEN_VALUE=your-token

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info
```

- **API docs:** http://localhost:8000/docs
- **API base:** http://localhost:8000/api/v1

## Architecture

```
app/
├── api/v1/endpoints/    # Route handlers (auth, vms, networks, etc.)
├── core/                # Config, security, dependencies
├── models/              # SQLAlchemy models (database schema)
├── schemas/             # Pydantic models (request/response validation)
├── services/            # Business logic (Proxmox, network, quota, SDN)
├── tasks/               # Celery async tasks (VM provisioning, ISO transfer)
└── db/                  # Database session management
```

## Testing

```bash
# Unit tests (fast, no external dependencies)
pytest tests/unit/ -v

# Integration tests (requires live LXC deployment)
pytest tests/integration/ -v --integration

# All tests
pytest tests/ -v --integration
```

### Test Structure

| Directory | Purpose | CI |
|---|---|---|
| `tests/unit/` | Service logic, in-memory SQLite | Runs on every PR |
| `tests/integration/` | Live API, Proxmox, DB | Runs on `main` merge |

## API Reference

See [`docs/API.md`](../docs/API.md) for the complete API reference.

## Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Conventions

- FastAPI with async/await throughout
- SQLAlchemy 2.0 async session pattern
- Pydantic v2 for request/response schemas
- Service layer for business logic (not in endpoints)
- Celery for async operations (VM provisioning, ISO transfer)
- Soft deletes via `deleted_at` timestamp on all models
