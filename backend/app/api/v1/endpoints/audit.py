"""
Admin audit log query endpoints.

Provides paginated, filtered access to audit logs for superadmins.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.core.deps import get_current_superadmin
from app.models.user import User

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=500),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    organization_id: Optional[str] = Query(None, description="Filter by organization ID"),
    action: Optional[str] = Query(None, description="Filter by action (e.g., vm.created)"),
    action_prefix: Optional[str] = Query(None, description="Filter by action prefix (e.g., vm)"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    status_code: Optional[int] = Query(None, description="Filter by HTTP status code"),
    created_after: Optional[datetime] = Query(None, description="ISO8601: 2026-05-01T00:00:00Z"),
    created_before: Optional[datetime] = Query(None, description="ISO8601: 2026-05-31T23:59:59Z"),
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List audit logs with pagination and filters (superadmin only).

    Supports filtering by user, org, action, resource type, status code,
    and created_at range. Results ordered by created_at DESC.
    """
    conditions = []

    if user_id:
        conditions.append(AuditLog.user_id == user_id)
    if organization_id:
        conditions.append(AuditLog.organization_id == organization_id)
    if action:
        conditions.append(AuditLog.action == action)
    if action_prefix:
        conditions.append(AuditLog.action.startswith(action_prefix))
    if resource_type:
        conditions.append(AuditLog.resource_type == resource_type)
    if status_code is not None:
        conditions.append(AuditLog.status_code == status_code)
    if created_after:
        conditions.append(AuditLog.created_at >= created_after)
    if created_before:
        conditions.append(AuditLog.created_at <= created_before)

    # Count
    count_query = select(func.count(AuditLog.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total = (await db.execute(count_query)).scalar_one()

    # Fetch page
    query = select(AuditLog)
    if conditions:
        query = query.where(and_(*conditions))
    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    rows = (await db.execute(query)).scalars().all()

    return {
        "data": [
            {
                "id": r.id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "user_id": r.user_id,
                "organization_id": r.organization_id,
                "action": r.action,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "resource_name": r.resource_name,
                "method": r.method,
                "url": r.url,
                "status_code": r.status_code,
                "ip_address": r.ip_address,
                "user_agent": r.user_agent,
                "error_message": r.error_message,
                "details": r.details,
            }
            for r in rows
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if total > 0 else 0,
    }
