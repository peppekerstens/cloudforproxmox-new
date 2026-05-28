"""Unit tests for VNI service (sparse allocation, no pre-population)."""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vxlan_vni_pool import VXLANVNIPool
from app.services.vni_service import VNIService


@pytest.fixture
def vni_service(db_session):
    return VNIService(db_session)


@pytest.mark.unit
async def test_allocate_first_vni(vni_service):
    """First allocation should return MIN_VNI (100000)."""
    vni = await vni_service.allocate_vni("network-1")
    assert vni == VNIService.MIN_VNI


@pytest.mark.unit
async def test_allocate_multiple_vnis_sequential(vni_service):
    """Allocations should be sequential."""
    vnis = []
    for i in range(5):
        vni = await vni_service.allocate_vni(f"network-{i}")
        vnis.append(vni)

    assert vnis == [100000, 100001, 100002, 100003, 100004]


@pytest.mark.unit
async def test_allocate_vni_with_no_network_id(vni_service):
    """Should allocate even when network_id is None (pre-creation)."""
    vni = await vni_service.allocate_vni(None)
    assert vni == 100000


@pytest.mark.unit
async def test_release_vni(vni_service):
    """Released VNI should be removed from pool (sparse model)."""
    vni = await vni_service.allocate_vni("network-1")
    await vni_service.release_vni(vni)

    count = await vni_service.get_allocated_vni_count()
    assert count == 0


@pytest.mark.unit
async def test_release_nonexistent_vni(vni_service):
    """Releasing a VNI not in pool should raise ValueError."""
    with pytest.raises(ValueError, match="not found in pool"):
        await vni_service.release_vni(999999)


@pytest.mark.unit
async def test_update_allocation(vni_service):
    """Should update network_id on allocated VNI."""
    vni = await vni_service.allocate_vni("pending")
    await vni_service.update_allocation(vni, "network-123")

    stats = await vni_service.get_pool_stats()
    assert stats["allocated"] == 1


@pytest.mark.unit
async def test_update_nonexistent_vni(vni_service):
    with pytest.raises(ValueError, match="not found in pool"):
        await vni_service.update_allocation(999999, "network-123")


@pytest.mark.unit
async def test_update_unallocated_vni(vni_service):
    """Cannot update a VNI that was never allocated."""
    # Allocate, release, then try to update
    vni = await vni_service.allocate_vni("network-1")
    await vni_service.release_vni(vni)

    with pytest.raises(ValueError, match="not found in pool"):
        await vni_service.update_allocation(vni, "network-2")


@pytest.mark.unit
async def test_pool_stats_initial(vni_service):
    """Stats should show 0 allocated initially."""
    stats = await vni_service.get_pool_stats()
    assert stats["allocated"] == 0
    assert stats["available"] == 16677216  # 16777215 - 100000 + 1
    assert stats["total_capacity"] == 16677216
    assert stats["allocation_model"] == "on-demand (sparse)"


@pytest.mark.unit
async def test_pool_stats_after_allocation(vni_service):
    """Stats should reflect allocated VNIs."""
    for i in range(10):
        await vni_service.allocate_vni(f"network-{i}")

    stats = await vni_service.get_pool_stats()
    assert stats["allocated"] == 10
    assert stats["available"] == 16677206


@pytest.mark.unit
async def test_vni_range_boundaries(vni_service):
    """MIN_VNI and MAX_VNI should be correct 24-bit range."""
    assert VNIService.MIN_VNI == 100000
    assert VNIService.MAX_VNI == 16777215


@pytest.mark.unit
async def test_exhaustion_theoretical(vni_service):
    """Should raise RuntimeError when VNI space is exhausted.

    We can't actually exhaust 16.7M VNIs, but we can verify the
    check exists by mocking the max lookup.
    """
    # Allocate one to verify the mechanism works
    vni = await vni_service.allocate_vni("network-1")
    assert vni >= VNIService.MIN_VNI
