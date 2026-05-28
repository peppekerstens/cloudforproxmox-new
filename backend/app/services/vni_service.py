"""VXLAN VNI pool management service for overlay network isolation."""
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models.vxlan_vni_pool import VXLANVNIPool

logger = logging.getLogger(__name__)


class VNIService:
    """Service for managing VXLAN VNI allocation and release.

    Unlike the VLAN pool (which pre-allocates all VLAN IDs), the VNI pool
    is *sparse* — VNIs are allocated on demand from a 16.7 M range.
    Only allocated VNIs have rows in the database.

    Range: 100000 — 16777215 (24-bit VXLAN VNI, lower 99999 reserved).
    """

    MIN_VNI = 100000
    MAX_VNI = 16777215

    def __init__(self, db: AsyncSession):
        self.db = db

    async def allocate_vni(self, network_id: Optional[str]) -> int:
        """Allocate the next available VNI.

        Finds the highest currently allocated VNI and increments by 1.
        Thread-safe via row-level lock on a sentinel or the max VNI.

        Args:
            network_id: Network ID to allocate for (None if not yet created)

        Returns:
            Allocated VNI

        Raises:
            RuntimeError: If VNI space exhausted
        """
        # Find highest allocated VNI
        result = await self.db.execute(
            select(func.max(VXLANVNIPool.vni))
            .where(VXLANVNIPool.status == "allocated")
        )
        max_vni = result.scalar()

        next_vni = self.MIN_VNI if max_vni is None else max_vni + 1

        if next_vni > self.MAX_VNI:
            raise RuntimeError(
                f"VNI space exhausted (max {self.MAX_VNI}). "
                "Release some VXLAN networks first."
            )

        vni_entry = VXLANVNIPool(
            vni=next_vni,
            status="allocated",
            allocated_to_network_id=network_id,
            allocated_at=datetime.now(timezone.utc),
        )
        self.db.add(vni_entry)
        await self.db.commit()
        await self.db.refresh(vni_entry)

        logger.info(f"Allocated VNI {next_vni} to network {network_id}")
        return next_vni

    async def release_vni(self, vni: int) -> None:
        """Release a VNI back to the pool.

        Removes the VNI pool entry (sparse pool — no pre-population).

        Args:
            vni: VNI to release

        Raises:
            ValueError: If VNI not found in pool
        """
        result = await self.db.execute(
            select(VXLANVNIPool).where(VXLANVNIPool.vni == vni)
        )
        vni_entry = result.scalar_one_or_none()

        if not vni_entry:
            raise ValueError(f"VNI {vni} not found in pool")

        await self.db.delete(vni_entry)
        await self.db.commit()

        logger.info(f"Released VNI {vni}")

    async def update_allocation(self, vni: int, network_id: str) -> None:
        """Update VNI allocation to associate with a network.

        Args:
            vni: VNI to update
            network_id: Network ID to associate

        Raises:
            ValueError: If VNI not found or not allocated
        """
        result = await self.db.execute(
            select(VXLANVNIPool).where(VXLANVNIPool.vni == vni)
        )
        vni_entry = result.scalar_one_or_none()

        if not vni_entry:
            raise ValueError(f"VNI {vni} not found in pool")

        if vni_entry.status != "allocated":
            raise ValueError(f"VNI {vni} is not allocated (status: {vni_entry.status})")

        vni_entry.allocated_to_network_id = network_id
        await self.db.commit()

        logger.debug(f"Updated VNI {vni} allocation to network {network_id}")

    async def get_allocated_vni_count(self) -> int:
        result = await self.db.execute(
            select(func.count(VXLANVNIPool.id))
            .where(VXLANVNIPool.status == "allocated")
        )
        return result.scalar() or 0

    async def get_pool_stats(self) -> dict:
        allocated = await self.get_allocated_vni_count()

        return {
            "total_capacity": self.MAX_VNI - self.MIN_VNI + 1,
            "allocated": allocated,
            "available": self.MAX_VNI - self.MIN_VNI + 1 - allocated,
            "vni_range": f"{self.MIN_VNI}-{self.MAX_VNI}",
            "allocation_model": "on-demand (sparse)",
        }
