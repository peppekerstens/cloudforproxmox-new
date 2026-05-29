"""
Firewall schemas for API request/response validation.

STUB: Disabled in Phase 1 (Batch 2). Real implementation added in Phase 8.
"""
from typing import Optional, List
from pydantic import BaseModel


class FirewallRuleCreate(BaseModel):
    """Schema for creating a firewall rule."""
    direction: str  # "in" or "out"
    protocol: str  # "tcp", "udp", "icmp", etc.
    port: Optional[int] = None
    action: str  # "accept" or "drop"
    comment: Optional[str] = None


class FirewallRuleUpdate(BaseModel):
    """Schema for updating a firewall rule."""
    direction: Optional[str] = None
    protocol: Optional[str] = None
    port: Optional[int] = None
    action: Optional[str] = None
    comment: Optional[str] = None


class FirewallRuleResponse(BaseModel):
    """Schema for firewall rule response."""
    id: str
    direction: str
    protocol: str
    port: Optional[int]
    action: str
    comment: Optional[str]

    class Config:
        from_attributes = True


class FirewallRuleListResponse(BaseModel):
    """Schema for list of firewall rules."""
    rules: List[FirewallRuleResponse]
    total: int
