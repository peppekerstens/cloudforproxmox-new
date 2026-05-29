"""
AuditLog model for immutable audit trail.

Key properties:
- Immutable: No UPDATE or DELETE operations (except retention policy hard deletes)
- All state changes captured with before/after context
- Sanitized: No passwords/tokens stored
- Indexed for common query patterns (time-range, org, user, action)
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, String, Integer, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AuditLog(Base):
    """Immutable audit log entry.

    Records all mutable API operations and critical state changes.
    Never updated or soft-deleted — retention policy uses hard DELETE.

    Query patterns:
    - "Show all actions by user X in last 7 days"
    - "Show all quota changes for org Y in May 2026"
    - "Show all failed login attempts from IP Z"
    """

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
    resource_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    method: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )
    url: Mapped[Optional[str]] = mapped_column(
        String(2048),
        nullable=True,
    )
    status_code: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    before_state: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    after_state: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )
    details: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    __table_args__ = (
        Index(
            "idx_audit_org_created",
            "organization_id",
            "created_at",
            postgresql_using="btree",
            postgresql_ops={"created_at": "DESC"},
        ),
        Index(
            "idx_audit_user_created",
            "user_id",
            "created_at",
            postgresql_using="btree",
            postgresql_ops={"created_at": "DESC"},
        ),
        Index(
            "idx_audit_action_created",
            "action",
            "created_at",
            postgresql_using="btree",
            postgresql_ops={"created_at": "DESC"},
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, action={self.action}, "
            f"resource_type={self.resource_type}, created_at={self.created_at})>"
        )


class AuditAction:
    """Constants for audit action types.

    Organized by priority (P0 = critical, P1 = important, P2 = useful).
    """

    VM_CREATED = "vm.created"
    VM_DELETED = "vm.deleted"
    VM_STARTED = "vm.started"
    VM_STOPPED = "vm.stopped"
    VM_REBOOTED = "vm.rebooted"
    VM_FORCE_STOPPED = "vm.force_stopped"
    VM_UPDATED = "vm.updated"

    LXC_CREATED = "lxc.created"
    LXC_DELETED = "lxc.deleted"
    LXC_STARTED = "lxc.started"
    LXC_STOPPED = "lxc.stopped"

    QUOTA_UPDATED = "quota.updated"
    USER_QUOTA_UPDATED = "user_quota.updated"

    USER_CREATED = "user.created"
    USER_DELETED = "user.deleted"
    USER_UPDATED = "user.updated"

    ORG_CREATED = "org.created"
    ORG_DELETED = "org.deleted"
    ORG_UPDATED = "org.updated"
    ORG_MEMBER_ADDED = "org.member_added"
    ORG_MEMBER_REMOVED = "org.member_removed"
    ORG_ROLE_UPDATED = "org.role_updated"

    AUTH_LOGIN = "auth.login"
    AUTH_LOGIN_FAILED = "auth.login_failed"
    AUTH_LOGOUT = "auth.logout"
    AUTH_TOKEN_REFRESHED = "auth.token_refreshed"
    AUTH_REGISTERED = "auth.registered"

    NETWORK_CREATED = "network.created"
    NETWORK_DELETED = "network.deleted"
    NETWORK_UPDATED = "network.updated"

    FIREWALL_RULE_CREATED = "firewall.rule_created"
    FIREWALL_RULE_DELETED = "firewall.rule_deleted"
    FIREWALL_ENABLED = "firewall.enabled"
    FIREWALL_DISABLED = "firewall.disabled"

    SNAPSHOT_CREATED = "snapshot.created"
    SNAPSHOT_DELETED = "snapshot.deleted"
    SNAPSHOT_ROLLBACK = "snapshot.rollback"

    DNS_PROVIDER_SWITCHED = "dns.provider_switched"
    DNS_RECORD_CREATED = "dns.record_created"
    DNS_RECORD_DELETED = "dns.record_deleted"

    GLOBAL_SETTINGS_UPDATED = "global_settings.updated"
    ORG_BRANDING_UPDATED = "org_branding.updated"

    BILLING_CREDIT_ADDED = "billing.credit_added"
    BILLING_CREDIT_DEDUCTED = "billing.credit_deducted"
    BILLING_INVOICE_GENERATED = "billing.invoice_generated"

    ADMIN_ROLE_GRANTED = "admin.role_granted"
    ADMIN_ROLE_REVOKED = "admin.role_revoked"


P0_ACTIONS = {
    AuditAction.QUOTA_UPDATED,
    AuditAction.USER_QUOTA_UPDATED,
    AuditAction.VM_CREATED,
    AuditAction.VM_DELETED,
    AuditAction.VM_FORCE_STOPPED,
    AuditAction.AUTH_LOGIN,
    AuditAction.AUTH_LOGIN_FAILED,
    AuditAction.AUTH_LOGOUT,
    AuditAction.AUTH_REGISTERED,
    AuditAction.USER_CREATED,
    AuditAction.USER_DELETED,
    AuditAction.ORG_ROLE_UPDATED,
}

P1_ACTIONS = {
    AuditAction.FIREWALL_RULE_CREATED,
    AuditAction.FIREWALL_RULE_DELETED,
    AuditAction.FIREWALL_ENABLED,
    AuditAction.FIREWALL_DISABLED,
    AuditAction.NETWORK_CREATED,
    AuditAction.NETWORK_DELETED,
    AuditAction.ORG_CREATED,
    AuditAction.ORG_DELETED,
    AuditAction.ORG_MEMBER_ADDED,
    AuditAction.ORG_MEMBER_REMOVED,
    AuditAction.DNS_PROVIDER_SWITCHED,
}

P2_ACTIONS = {
    AuditAction.SNAPSHOT_CREATED,
    AuditAction.SNAPSHOT_DELETED,
    AuditAction.SNAPSHOT_ROLLBACK,
    AuditAction.VM_STARTED,
    AuditAction.VM_STOPPED,
    AuditAction.VM_REBOOTED,
    AuditAction.VM_UPDATED,
    AuditAction.LXC_CREATED,
    AuditAction.LXC_DELETED,
    AuditAction.LXC_STARTED,
    AuditAction.LXC_STOPPED,
    AuditAction.DNS_RECORD_CREATED,
    AuditAction.DNS_RECORD_DELETED,
    AuditAction.GLOBAL_SETTINGS_UPDATED,
    AuditAction.ORG_BRANDING_UPDATED,
}
