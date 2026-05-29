"""
Audit logging helper functions.

Provides:
- sanitize_dict(): Remove sensitive keys before storage
- create_audit_log(): Async helper to write AuditLog entries
"""
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog

SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "jwt",
    "credentials",
    "authorization",
    "api_key",
    "api_secret",
    "api_key_hash",
    "proxmox_token_value",
}


def sanitize_dict(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Recursively remove sensitive keys from dict. Returns None if input is None."""
    if data is None:
        return None
    if not isinstance(data, dict):
        return {"value": str(data)[:100]}

    sanitized: Dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in SENSITIVE_KEYS:
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized


async def create_audit_log(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    resource_name: Optional[str] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    method: Optional[str] = None,
    url: Optional[str] = None,
    status_code: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    before_state: Optional[Dict[str, Any]] = None,
    after_state: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """Create a sanitized, immutable audit log entry.

    All dict fields are sanitized to remove sensitive keys.
    Commits the session after creation.
    """
    entry = AuditLog(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        user_id=user_id,
        organization_id=organization_id,
        method=method,
        url=url,
        status_code=status_code,
        ip_address=ip_address,
        user_agent=user_agent,
        before_state=sanitize_dict(before_state),
        after_state=sanitize_dict(after_state),
        error_message=error_message,
        details=sanitize_dict(details),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry
