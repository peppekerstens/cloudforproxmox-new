"""
Audit middleware — captures all mutating API operations.

Intercepts POST/PUT/PATCH/DELETE requests, extracts user context
from JWT, sanitizes request body, and writes AuditLog entry.
"""
import json
import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.audit import create_audit_log, sanitize_dict
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


def _get_ip(request: Request) -> str:
    """Extract client IP from headers or direct connection."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host or ""
    return ""


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all mutating HTTP requests to audit_logs."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return await call_next(request)

        # Read request body (cached by Starlette, available to handlers)
        body_bytes = await request.body()
        body_dict = None
        if body_bytes:
            try:
                body_dict = json.loads(body_bytes)
            except (json.JSONDecodeError, UnicodeDecodeError):
                body_dict = {"raw": body_bytes[:512].decode("utf-8", errors="replace")}

        # Extract user info from JWT
        user_id = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            payload = decode_token(auth_header[7:])
            if payload:
                user_id = payload.get("sub")

        # Extract org context
        org_id = request.headers.get("X-Organization-ID")

        ip_address = _get_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        url = str(request.url)
        if len(url) > 2048:
            url = url[:2048]

        # Process the actual request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log the error but let it propagate
            try:
                async with AsyncSessionLocal() as db:
                    await create_audit_log(
                        db=db,
                        action=f"http.{request.method.lower()}_error",
                        resource_type=request.url.path,
                        user_id=user_id,
                        organization_id=org_id,
                        method=request.method,
                        url=url,
                        status_code=500,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        error_message=str(exc)[:1024],
                        details=sanitize_dict(body_dict),
                    )
            except Exception as log_err:
                logger.warning("AuditMiddleware: failed to log error: %s", log_err)
            raise

        # Log the successful request (fire-and-forget via background task)
        try:
            async with AsyncSessionLocal() as db:
                await create_audit_log(
                    db=db,
                    action=f"http.{request.method.lower()}",
                    resource_type=request.url.path.split("/")[-1] or "unknown",
                    user_id=user_id,
                    organization_id=org_id,
                    method=request.method,
                    url=url,
                    status_code=response.status_code,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details=sanitize_dict(body_dict),
                )
        except Exception as log_err:
            logger.warning("AuditMiddleware: failed to log request: %s", log_err)

        return response
