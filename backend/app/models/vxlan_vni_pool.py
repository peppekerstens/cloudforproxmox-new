"""VXLAN VNI pool management for tracking VNI allocations."""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.vpc_network import VPCNetwork


class VXLANVNIPool(BaseModel):
    """VXLAN VNI pool for tracking VNI allocations across the cluster.

    VXLAN uses a 24-bit VNI (0-16777215). We reserve 1-99999 for
    infrastructure and allocate from 100000 onwards.
    """

    __tablename__ = "vxlan_vni_pool"

    vni: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="available",
        index=True
    )  # available, allocated, reserved

    # Allocation tracking
    allocated_to_network_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("vpc_networks.id", ondelete="SET NULL"),
        nullable=True
    )
    allocated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationship
    network: Mapped[Optional["VPCNetwork"]] = relationship("VPCNetwork", lazy="selectin")
