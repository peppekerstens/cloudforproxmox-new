"""
Virtual Machine management endpoints.
"""
from typing import Optional
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import joinedload, raiseload
from kombu.exceptions import OperationalError as KombuOperationalError

logger = logging.getLogger(__name__)

from app.db.session import get_db
from app.models.virtual_machine import VirtualMachine
from app.models.proxmox_cluster import ProxmoxCluster
from app.models.vm_disk import VMDisk
from app.models.iso_image import ISOImage
from app.schemas.virtual_machine import (
    VMCreate,
    VMUpdate,
    VMResponse,
    VMListResponse,
    VMActionRequest,
    VMResize,
    VMTemplateCreate,
    VMCloneRequest,
)
from app.schemas.network import VMNetworkAttachRequest
from app.core.audit import create_audit_log
from app.models.audit_log import AuditAction
from app.core.deps import OrgContext, RequirePermission
from app.core.rbac import Role, Permission
from app.services.proxmox_service import ProxmoxService
from app.services.quota_service import QuotaService
from app.tasks.vm_status_tasks import poll_vm_power_state

router = APIRouter(prefix="/vms", tags=["Virtual Machines"])


def _get_dns_provider_for_endpoint():
    """Get DNS provider instance for endpoint operations."""
    from app.core.config import settings
    if not settings.DNS_ENABLED:
        return None
    # Import provider registry lazily
    try:
        from app.services.dns_adguard import AdGuardHomeProvider
        if settings.DNS_PROVIDER == "adguard":
            return AdGuardHomeProvider.from_settings()
    except ImportError:
        pass
    return None


def _get_dns_provider_sync():
    """Get DNS provider for sync operations (Celery tasks, no async DB).

    Reads config from DB using a sync session if available, falls back to env vars.
    """
    from app.core.config import settings
    if not settings.DNS_ENABLED:
        return None
    try:
        from app.services.dns_adguard import AdGuardHomeProvider, AdGuardConfig
        from app.db.session import SessionLocal
        from app.models.dns_config import DNSConfig
        from sqlalchemy import select

        provider_name = settings.DNS_PROVIDER
        connection_config = None

        try:
            db = SessionLocal()
            query = select(DNSConfig).where(
                DNSConfig.deleted_at.is_(None),
                DNSConfig.is_active.is_(True),
            )
            result = db.execute(query)
            db_config = result.scalar_one_or_none()
            if db_config and db_config.enabled:
                provider_name = db_config.provider_name
                connection_config = db_config.connection_config
        except Exception as e:
            logger.warning(f"Failed to load DNS config from DB: {e}")
        finally:
            try:
                db.close()
            except Exception as e:
                logger.debug(f"Error closing DB session: {e}")

        if connection_config and provider_name == "adguard":
            config = AdGuardConfig(
                host=connection_config.get("host", settings.ADGUARD_HOST),
                port=connection_config.get("port", settings.ADGUARD_PORT),
                username=connection_config.get("username", settings.ADGUARD_USERNAME),
                password=connection_config.get("password", settings.ADGUARD_PASSWORD),
                use_tls=connection_config.get("use_tls", settings.ADGUARD_USE_TLS),
                verify_ssl=connection_config.get("verify_ssl", settings.ADGUARD_VERIFY_SSL),
            )
            return AdGuardHomeProvider(config)
        elif provider_name == "adguard":
            return AdGuardHomeProvider.from_settings()
    except ImportError:
        pass
    return None


def map_ostype_to_proxmox(ostype: Optional[str]) -> str:
    """
    Map user-friendly OS type to Proxmox ostype codes.

    Proxmox valid values:
    - other, wxp, w2k, w2k3, w2k8, wvista, win7, win8, win10, win11
    - l24, l26, solaris
    """
    ostype_map = {
        "linux": "l26",
        "ubuntu": "l26",
        "debian": "l26",
        "centos": "l26",
        "rhel": "l26",
        "fedora": "l26",
        "rocky": "l26",
        "alma": "l26",
        "windows": "win11",
        "windows-11": "win11",
        "windows-10": "win10",
        "windows-8": "win8",
        "windows-7": "win7",
        "windows-vista": "wvista",
        "windows-2008": "w2k8",
        "windows-2003": "w2k3",
        "windows-2000": "w2k",
        "windows-xp": "wxp",
        "solaris": "solaris",
        "other": "other",
    }

    if not ostype:
        return "l26"  # Default to Linux 2.6+

    # If already a valid Proxmox code, return as-is
    valid_proxmox_codes = ["other", "wxp", "w2k", "w2k3", "w2k8", "wvista",
                          "win7", "win8", "win10", "win11", "l24", "l26", "solaris"]
    if ostype in valid_proxmox_codes:
        return ostype

    # Map user-friendly name to Proxmox code
    return ostype_map.get(ostype.lower(), "l26")


@router.get("", response_model=VMListResponse)
async def list_vms(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name"),
    node: Optional[str] = Query(None, description="Filter by Proxmox node"),
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_READ)),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    List virtual machines in organization.

    - Org admins and superadmins see all VMs in the organization
    - Org members see only their own VMs
    - Org viewers see all VMs (read-only)

    Requires: VM_READ permission
    """
    per_page = min(per_page, 100)

    # Build query - filter by organization
    query = select(VirtualMachine).options(
        joinedload(VirtualMachine.disks),
        joinedload(VirtualMachine.proxmox_cluster),
        joinedload(VirtualMachine.owner),
        raiseload(VirtualMachine.network_interfaces),
    ).where(
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None),
        VirtualMachine.is_template.is_(False)
    )

    # Members only see their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    # Apply filters
    if status:
        query = query.where(VirtualMachine.status == status)

    if search:
        search_filter = f"%{search}%"
        query = query.where(VirtualMachine.name.ilike(search_filter))

    if node:
        query = query.where(VirtualMachine.proxmox_node == node)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    query = query.order_by(VirtualMachine.created_at.desc())

    # Execute query
    result = await db.execute(query)
    vms = result.scalars().all()

    return {
        "data": vms,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.post("", response_model=VMResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_vm(
    vm_data: VMCreate,
    background_tasks: BackgroundTasks,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_CREATE)),
    db: AsyncSession = Depends(get_db)
) -> VirtualMachine:
    """
    Create a new virtual machine or LXC container with quota enforcement.

    For QEMU VMs: supports multiple disks, ISO boot, and full virtualization.
    For LXC containers: lightweight containers with rootfs and template-based provisioning.

    Requires: VM_CREATE permission
    """
    # Calculate total storage
    if vm_data.vm_type == "lxc":
        total_storage_gb = vm_data.rootfs_size or 8
    else:
        total_storage_gb = sum(disk.size_gb for disk in vm_data.disks)

    # Validate ISO access if provided (qemu only)
    iso_image = None
    if vm_data.iso_image_id and vm_data.vm_type == "qemu":
        result = await db.execute(
            select(ISOImage).where(
                ISOImage.id == vm_data.iso_image_id,
                ISOImage.deleted_at.is_(None)
            )
        )
        iso_image = result.scalar_one_or_none()

        if not iso_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ISO image not found"
            )

        if not iso_image.is_public and iso_image.organization_id != org_context.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this ISO image"
            )

        if iso_image.upload_status != "ready":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ISO is not ready yet (status: {iso_image.upload_status})"
            )

    # Validate LXC template if provided
    if vm_data.vm_type == "lxc" and not vm_data.ostemplate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ostemplate is required for LXC containers"
        )

    # Check and reserve quota atomically (prevents TOCTOU race)
    quota_service = QuotaService(db)

    quota_check = await quota_service.check_and_reserve(
        organization_id=org_context.org_id,
        cpu_cores=vm_data.cpu_cores,
        memory_gb=vm_data.memory_mb / 1024,
        storage_gb=total_storage_gb,
        vm_count=1
    )

    if not quota_check.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quota exceeded: {', '.join(quota_check.exceeded_resources)}"
        )

    # Select cluster
    if vm_data.proxmox_cluster_id:
        result = await db.execute(
            select(ProxmoxCluster).where(
                ProxmoxCluster.id == vm_data.proxmox_cluster_id,
                ProxmoxCluster.is_active.is_(True),
                ProxmoxCluster.deleted_at.is_(None),
                or_(
                    ProxmoxCluster.organization_id == org_context.org_id,
                    ProxmoxCluster.is_shared.is_(True)
                )
            )
        )
        cluster = result.scalar_one_or_none()
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proxmox cluster not found or not accessible by your organization"
            )
    else:
        result = await db.execute(
            select(ProxmoxCluster).where(
                ProxmoxCluster.is_active.is_(True),
                ProxmoxCluster.deleted_at.is_(None),
                or_(
                    ProxmoxCluster.organization_id == org_context.org_id,
                    ProxmoxCluster.is_shared.is_(True)
                )
            ).order_by(
                ProxmoxCluster.organization_id == org_context.org_id,
                ProxmoxCluster.load_score.asc()
            ).limit(1)
        )
        cluster = result.scalar_one_or_none()
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No active Proxmox clusters available for your organization"
            )

    # Get next VMID and best node
    proxmox_service = get_proxmox_service(cluster)
    try:
        best_node = await proxmox_service.select_best_node_async()
        if not best_node:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No available nodes in Proxmox cluster"
            )
        proxmox_vmid = await proxmox_service.get_next_vmid_async(node=best_node)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Proxmox cluster: {str(e)}"
        )

    # Validate network access if provided
    if vm_data.network_id:
        from app.models.vpc_network import VPCNetwork
        result = await db.execute(
            select(VPCNetwork).where(
                VPCNetwork.id == vm_data.network_id,
                VPCNetwork.deleted_at.is_(None),
                or_(
                    VPCNetwork.organization_id == org_context.org_id,
                    VPCNetwork.is_shared.is_(True)
                )
            )
        )
        network = result.scalar_one_or_none()
        if not network:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Network not found or not accessible by your organization"
            )

    # Create VM/LXC record
    vm = VirtualMachine(
        name=vm_data.name,
        hostname=vm_data.hostname,
        description=vm_data.description,
        organization_id=org_context.org_id,
        owner_id=org_context.user.id,
        vm_type=vm_data.vm_type,
        proxmox_cluster_id=cluster.id,
        proxmox_vmid=proxmox_vmid,
        proxmox_node=best_node,
        cpu_cores=vm_data.cpu_cores,
        cpu_sockets=vm_data.cpu_sockets,
        memory_mb=vm_data.memory_mb,
        os_type=vm_data.os_type,
        status="provisioning",
        tags=vm_data.tags or [],
        network_id=vm_data.network_id,
    )

    db.add(vm)
    await db.flush()

    # Create disk records (qemu only)
    if vm_data.vm_type == "qemu":
        default_storage = "local-lvm"
        for idx, disk_spec in enumerate(vm_data.disks):
            disk = VMDisk(
                vm_id=vm.id,
                disk_index=idx,
                disk_interface=disk_spec.disk_interface,
                disk_number=idx,
                storage_pool=disk_spec.storage_pool or default_storage,
                size_gb=disk_spec.size_gb,
                disk_format=disk_spec.disk_format,
                is_boot_disk=disk_spec.is_boot_disk,
                is_cdrom=False,
                status="creating"
            )
            db.add(disk)

        if iso_image:
            cdrom_disk = VMDisk(
                vm_id=vm.id,
                disk_index=len(vm_data.disks),
                disk_interface="ide",
                disk_number=2,
                storage_pool="",
                size_gb=0,
                disk_format=None,
                is_boot_disk=False,
                is_cdrom=True,
                iso_image_id=iso_image.id,
                status="creating"
            )
            db.add(cdrom_disk)

    # Increment user quota usage BEFORE commit (same transaction)
    await quota_service.increment_user_usage(
        user_id=org_context.user.id,
        organization_id=org_context.org_id,
        cpu_cores=vm_data.cpu_cores,
        memory_gb=vm_data.memory_mb / 1024,
        storage_gb=total_storage_gb,
        vm_count=1
    )

    await db.commit()
    await db.refresh(vm)

    # Queue provisioning task
    try:
        if vm_data.vm_type == "lxc":
            from app.tasks.vm_tasks import provision_lxc_container

            provision_lxc_container.delay(
                str(vm.id),
                vm_data.ostemplate,
                vm_data.rootfs_size or 8,
                vm_data.storage_pool or "local-lvm"
            )

            logger.info(f"LXC {vm.id} provisioning queued with template {vm_data.ostemplate}")
        else:
            from app.tasks.vm_tasks import provision_vm_with_disks

            provision_vm_with_disks.delay(str(vm.id))

            logger.info(f"VM {vm.id} provisioning queued with {len(vm_data.disks)} disk(s)")

    except ImportError as e:
        logger.error(f"Provisioning task import failed: {e}")
        vm.status = "error"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Provisioning task unavailable"
        )
    except (KombuOperationalError, ConnectionError, OSError) as e:
        logger.error(f"Task queue unavailable: {e}")
        vm.status = "error"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task queue unavailable"
        )
    except Exception as e:
        logger.error(f"Failed to queue provisioning task: {e}")
        vm.status = "error"
        await db.commit()

    # Audit: VM created
    await create_audit_log(
        db=db,
        action=AuditAction.VM_CREATED,
        resource_type="vm",
        resource_id=vm.id,
        resource_name=vm.name,
        user_id=org_context.user.id,
        organization_id=org_context.org_id,
        details={
            "vm_type": vm.vm_type,
            "cpu_cores": vm.cpu_cores,
            "memory_mb": vm.memory_mb,
            "proxmox_vmid": vm.proxmox_vmid,
        },
    )

    return vm


@router.get("/templates", response_model=VMListResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    os_type: Optional[str] = None,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """
    List available VM templates.

    Returns public templates and templates owned by the organization.

    Requires: VM_CREATE permission
    """
    per_page = min(per_page, 100)

    conditions = [
            VirtualMachine.is_template.is_(True),
        VirtualMachine.deleted_at.is_(None),
        or_(
            VirtualMachine.organization_id == org_context.org_id,
            VirtualMachine.organization_id.is_(None)
        )
    ]

    if os_type:
        conditions.append(VirtualMachine.os_type == os_type)

    query = select(VirtualMachine).options(
        joinedload(VirtualMachine.disks),
        joinedload(VirtualMachine.proxmox_cluster),
        joinedload(VirtualMachine.owner),
        raiseload(VirtualMachine.network_interfaces),
    ).where(*conditions).order_by(VirtualMachine.created_at.desc())

    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar_one()

    offset = (page - 1) * per_page
    result = await db.execute(query.offset(offset).limit(per_page))
    templates = list(result.scalars().all())

    return VMListResponse(
        data=templates,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.get("/containers/templates")
async def list_lxc_templates(
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """
    List available LXC OS templates from Proxmox storage.

    Queries all accessible storage pools for vztmpl content.
    Returns friendly names and raw paths for dropdown selection.

    Requires: VM_CREATE permission
    """
    from app.services.proxmox_service import ProxmoxService

    # Get accessible clusters
    cluster_query = select(ProxmoxCluster).where(
        ProxmoxCluster.is_active.is_(True),
        ProxmoxCluster.deleted_at.is_(None),
        or_(
            ProxmoxCluster.is_shared.is_(True),
            ProxmoxCluster.organization_id == org_context.org_id
        )
    )
    result = await db.execute(cluster_query)
    clusters = list(result.scalars().all())

    if not clusters:
        return {"data": [], "total": 0}

    # Get storage pools that support vztmpl
    from app.models.storage_pool import StoragePool
    from sqlalchemy import cast, Text

    cluster_ids = [c.id for c in clusters]
    storage_query = select(StoragePool).where(
        StoragePool.proxmox_cluster_id.in_(cluster_ids),
        StoragePool.deleted_at.is_(None),
        StoragePool.is_active.is_(True),
        cast(StoragePool.content_types, Text).contains('"vztmpl"')
    )
    storage_result = await db.execute(storage_query)
    storage_pools = list(storage_result.scalars().all())

    templates = []
    seen_volid = set()
    proxmox_service = ProxmoxService()

    for pool in storage_pools:
        cluster = next((c for c in clusters if c.id == pool.proxmox_cluster_id), None)
        if not cluster:
            continue

        try:
            # Get node from cluster API URL or use first node
            node = cluster.datacenter or "pve1"
            content = await proxmox_service.get_storage_content_async(
                node=node, storage=pool.storage_name, content_type="vztmpl"
            )
            for item in content:
                volid = item.get("volid", "")
                if volid and volid not in seen_volid:
                    seen_volid.add(volid)
                    # Extract friendly name from volid
                    # e.g., "local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst"
                    filename = volid.split("/")[-1] if "/" in volid else volid
                    # Remove extension and version info for display
                    display_name = filename.replace(".tar.zst", "").replace(".tar.gz", "").replace(".tar.xz", "")
                    # Clean up: debian-12-standard_12.2-1_amd64 -> Debian 12 Standard
                    display_name = display_name.replace("_", " ").replace("-", " ").strip()
                    # Capitalize words
                    display_name = " ".join(w.capitalize() if w.islower() else w for w in display_name.split())

                    templates.append({
                        "volid": volid,
                        "display_name": display_name,
                        "storage": pool.storage_name,
                        "cluster": cluster.name,
                    })
        except Exception as e:
            logger.warning(f"Failed to list templates from {pool.storage_name} on {cluster.name}: {e}")

    # Sort by display name
    templates.sort(key=lambda t: t["display_name"])

    return {"data": templates, "total": len(templates)}


@router.post("/templates/{template_id}/clone", response_model=VMResponse, status_code=status.HTTP_201_CREATED)
async def clone_template(
    template_id: str,
    clone_data: VMCloneRequest,
    background_tasks: BackgroundTasks,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """
    Clone a VM from a template.

    Creates a new VM by cloning the specified template.
    Resource limits (CPU, memory) can be overridden.

    Requires: VM_CREATE permission
    """
    result = await db.execute(
        select(VirtualMachine).where(
            VirtualMachine.id == template_id,
        VirtualMachine.is_template.is_(True),
            VirtualMachine.deleted_at.is_(None),
            or_(
                VirtualMachine.organization_id == org_context.org_id,
                VirtualMachine.organization_id.is_(None)
            )
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    quota_service = QuotaService(db)

    cpu_cores = clone_data.cpu_cores or template.cpu_cores
    memory_mb = clone_data.memory_mb or template.memory_mb

    # Check and reserve quota atomically (prevents TOCTOU race)
    quota_check = await quota_service.check_and_reserve(
        organization_id=org_context.org_id,
        cpu_cores=cpu_cores,
        memory_gb=memory_mb / 1024,
        storage_gb=sum(d.size_gb for d in template.disks),
        vm_count=1
    )

    if not quota_check.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization quota exceeded: {', '.join(quota_check.exceeded_resources)}"
        )

    # Check user-level quota
    user_quota_check = await quota_service.check_user_quota_availability(
        user_id=org_context.user.id,
        organization_id=org_context.org_id,
        cpu_cores=cpu_cores,
        memory_gb=memory_mb / 1024,
        storage_gb=sum(d.size_gb for d in template.disks),
        vm_count=1
    )

    if not user_quota_check.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User quota exceeded: {', '.join(user_quota_check.exceeded_resources)}"
        )

    if clone_data.proxmox_cluster_id:
        result = await db.execute(
            select(ProxmoxCluster).where(
                ProxmoxCluster.id == clone_data.proxmox_cluster_id,
                ProxmoxCluster.is_active.is_(True),
                ProxmoxCluster.deleted_at.is_(None),
                or_(
                    ProxmoxCluster.organization_id == org_context.org_id,
                    ProxmoxCluster.is_shared.is_(True)
                )
            )
        )
        cluster = result.scalar_one_or_none()
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target cluster not found or not accessible"
            )
    else:
        cluster = template.proxmox_cluster

    proxmox_service = get_proxmox_service(cluster)
    try:
        clone_node = template.proxmox_node
        proxmox_vmid = await proxmox_service.get_next_vmid_async(node=clone_node)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Proxmox cluster: {str(e)}"
        )

    vm = VirtualMachine(
        name=clone_data.name,
        hostname=clone_data.hostname,
        description=clone_data.description,
        organization_id=org_context.org_id,
        owner_id=org_context.user.id,
        proxmox_cluster_id=cluster.id,
        proxmox_vmid=proxmox_vmid,
        proxmox_node=clone_node,
        cpu_cores=cpu_cores,
        cpu_sockets=template.cpu_sockets,
        memory_mb=memory_mb,
        os_type=template.os_type,
        status="provisioning",
        tags=template.tags or [],
        network_id=clone_data.network_id,
    )

    db.add(vm)
    await db.flush()

    for disk in template.disks:
        new_disk = VMDisk(
            vm_id=vm.id,
            disk_index=disk.disk_index,
            disk_interface=disk.disk_interface,
            disk_number=disk.disk_number,
            storage_pool=disk.storage_pool,
            size_gb=disk.size_gb,
            disk_format=disk.disk_format,
            is_boot_disk=disk.is_boot_disk,
            is_cdrom=disk.is_cdrom,
            status="creating"
        )
        db.add(new_disk)

    # Increment user quota BEFORE commit (same transaction)
    await quota_service.increment_user_usage(
        user_id=org_context.user.id,
        organization_id=org_context.org_id,
        cpu_cores=cpu_cores,
        memory_gb=memory_mb / 1024,
        storage_gb=sum(d.size_gb for d in template.disks),
        vm_count=1
    )

    await db.commit()
    await db.refresh(vm)

    try:
        from app.tasks.vm_tasks import clone_vm_from_template

        clone_vm_from_template.delay(str(vm.id), str(template.id))

        logger.info(f"VM {vm.id} clone from template {template.id} queued")

    except ImportError as e:
        logger.error(f"Clone task import failed: {e}")
        vm.status = "error"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clone task unavailable"
        )
    except (KombuOperationalError, ConnectionError, OSError) as e:
        logger.error(f"Task queue unavailable: {e}")
        vm.status = "error"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task queue unavailable"
        )
    except Exception as e:
        logger.error(f"Failed to queue VM clone task: {e}")
        vm.status = "error"
        await db.commit()

    return vm


@router.get("/{vm_id}", response_model=VMResponse)
async def get_vm(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_READ)),
    db: AsyncSession = Depends(get_db)
) -> VirtualMachine:
    """
    Get VM details by ID.

    Members can only view their own VMs.
    Admins and viewers can view all org VMs.

    Requires: VM_READ permission
    """
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only see their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    return vm


@router.patch("/{vm_id}", response_model=VMResponse)
async def update_vm(
    vm_id: str,
    vm_update: VMUpdate,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
) -> VirtualMachine:
    """
    Update VM configuration.

    Members can only update their own VMs.
    Admins can update any VM in the organization.

    Requires: VM_UPDATE permission
    """
    # Get VM
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only update their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found"
        )

    # Update fields
    if vm_update.name is not None:
        vm.name = vm_update.name
    if vm_update.hostname is not None:
        vm.hostname = vm_update.hostname
    if vm_update.description is not None:
        vm.description = vm_update.description
    if vm_update.cpu_cores is not None:
        vm.cpu_cores = vm_update.cpu_cores
    if vm_update.memory_mb is not None:
        vm.memory_mb = vm_update.memory_mb

    await db.commit()
    await db.refresh(vm)

    return vm


@router.delete("/{vm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vm(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_DELETE)),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a VM and release quota.

    Members can only delete their own VMs.
    Admins can delete any VM in the organization.

    Requires: VM_DELETE permission
    """
    # Get VM with org check
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only delete their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    # Get disks to calculate storage for quota release
    result = await db.execute(
        select(VMDisk).where(
            VMDisk.vm_id == vm_id,
            VMDisk.deleted_at.is_(None),
            VMDisk.is_cdrom.is_(False)
        )
    )
    disks = list(result.scalars().all())

    # Calculate total storage from disks
    total_storage_gb = sum(disk.size_gb for disk in disks) if disks else 20  # Fallback to 20
    cpu_cores = vm.cpu_cores
    memory_gb = vm.memory_mb / 1024

    # Unregister DNS record before Proxmox deletion
    if vm.hostname and vm.primary_ip_address:
        try:
            from app.services.dns_provider import DNSProviderError
            dns = _get_dns_provider_for_endpoint()
            if dns:
                dns.unregister(vm.hostname, vm.primary_ip_address)
                logger.info(f"DNS unregistered for VM {vm_id}: {vm.hostname}")
        except DNSProviderError as e:
            logger.warning(f"DNS unregistration failed for VM {vm_id}: {e}")
            # Non-fatal — continue with deletion

    # Delete from Proxmox first — fail fast if Proxmox deletion fails
    proxmox_service = get_proxmox_service(vm.proxmox_cluster)
    try:
        await proxmox_service.delete_vm_async(vm.proxmox_node, vm.proxmox_vmid)
    except Exception as e:
        error_msg = str(e)
        # Treat "does not exist" as already deleted (idempotent delete)
        if "does not exist" in error_msg or "Configuration file" in error_msg:
            logger.warning(f"VM {vm_id} (Proxmox VMID {vm.proxmox_vmid}) not found on {vm.proxmox_node}, treating as already deleted")
        else:
            logger.error(f"Failed to delete VM {vm_id} (Proxmox VMID {vm.proxmox_vmid}) from Proxmox: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete VM from Proxmox: {e}"
            )

    # Proxmox deletion succeeded — now soft-delete from database
    now = datetime.now(timezone.utc)
    vm.deleted_at = now

    # Soft delete disk records
    for disk in disks:
        disk.deleted_at = now

    # Cascade soft-delete network interfaces
    from app.models.vm_network_interface import VMNetworkInterface
    result = await db.execute(
        select(VMNetworkInterface).where(
            VMNetworkInterface.vm_id == vm_id,
            VMNetworkInterface.deleted_at.is_(None)
        )
    )
    interfaces = list(result.scalars().all())
    for interface in interfaces:
        interface.deleted_at = now

    # Cascade soft-delete IP allocations
    from app.models.network_ip_allocation import NetworkIPAllocation
    result = await db.execute(
        select(NetworkIPAllocation).where(
            NetworkIPAllocation.vm_id == vm_id,
            NetworkIPAllocation.deleted_at.is_(None)
        )
    )
    allocations = list(result.scalars().all())
    for allocation in allocations:
        allocation.deleted_at = now

    # Release org quota BEFORE commit (same transaction)
    quota_service = QuotaService(db)
    await quota_service.decrement_usage(
        organization_id=vm.organization_id,
        cpu_cores=cpu_cores,
        memory_gb=memory_gb,
        storage_gb=total_storage_gb,
        vm_count=1
    )

    # Release user quota BEFORE commit (same transaction)
    await quota_service.decrement_user_usage(
        user_id=vm.owner_id,
        organization_id=vm.organization_id,
        cpu_cores=cpu_cores,
        memory_gb=memory_gb,
        storage_gb=total_storage_gb,
        vm_count=1
    )

    await db.commit()

    # Audit: VM deleted
    await create_audit_log(
        db=db,
        action=AuditAction.VM_DELETED,
        resource_type="vm",
        resource_id=vm.id,
        resource_name=vm.name,
        user_id=org_context.user.id,
        organization_id=org_context.org_id,
        details={"proxmox_vmid": vm.proxmox_vmid, "vm_type": vm.vm_type},
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{vm_id}/start", status_code=status.HTTP_202_ACCEPTED)
async def start_vm(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_START)),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Start a VM.

    Requires: VM_START permission
    """
    # Get VM with org check
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only start their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    # Start VM on Proxmox
    try:
        proxmox_service = get_proxmox_service(vm.proxmox_cluster)
        result = await proxmox_service.start_vm_async(vm.proxmox_node, vm.proxmox_vmid)

        # Set transitional status
        vm.status = "starting"
        vm.power_state = "on"
        vm.started_at = datetime.now(timezone.utc)
        await db.commit()

        # Queue polling task to update status when Proxmox confirms
        task_upid = result.get("task_id")
        poll_vm_power_state.delay(
            vm_id=str(vm.id),
            proxmox_node=vm.proxmox_node,
            task_upid=task_upid,
            expected_final_status="running"
        )

        return {
            "message": "VM start initiated",
            "task_id": task_upid
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start VM: {str(e)}"
        )


@router.post("/{vm_id}/stop", status_code=status.HTTP_202_ACCEPTED)
async def stop_vm(
    vm_id: str,
    action_data: VMActionRequest = VMActionRequest(),
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_STOP)),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Stop a VM.

    Requires: VM_STOP permission
    """
    # Get VM with org check
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only stop their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    # Stop VM on Proxmox
    try:
        proxmox_service = get_proxmox_service(vm.proxmox_cluster)
        result = await proxmox_service.stop_vm_async(vm.proxmox_node, vm.proxmox_vmid, force=action_data.force)

        # Set transitional status
        vm.status = "stopping"
        vm.power_state = "off"
        vm.stopped_at = datetime.now(timezone.utc)
        await db.commit()

        # Queue polling task to update status when Proxmox confirms
        task_upid = result.get("task_id")
        poll_vm_power_state.delay(
            vm_id=str(vm.id),
            proxmox_node=vm.proxmox_node,
            task_upid=task_upid,
            expected_final_status="stopped"
        )

        return {
            "message": "VM stop initiated",
            "task_id": task_upid
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop VM: {str(e)}"
        )


@router.post("/{vm_id}/restart", status_code=status.HTTP_202_ACCEPTED)
async def restart_vm(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_RESTART)),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Restart a VM.

    Requires: VM_RESTART permission
    """
    # Get VM with org check
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only restart their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    # Restart VM on Proxmox
    try:
        proxmox_service = get_proxmox_service(vm.proxmox_cluster)
        result = await proxmox_service.restart_vm_async(vm.proxmox_node, vm.proxmox_vmid)

        # Set transitional status
        vm.status = "rebooting"
        vm.started_at = datetime.now(timezone.utc)
        await db.commit()

        # Queue polling task to update status when Proxmox confirms
        task_upid = result.get("task_id")
        poll_vm_power_state.delay(
            vm_id=str(vm.id),
            proxmox_node=vm.proxmox_node,
            task_upid=task_upid,
            expected_final_status="running"
        )

        return {
            "message": "VM restart initiated",
            "task_id": task_upid
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart VM: {str(e)}"
        )


@router.get("/{vm_id}/console")
async def get_vm_console(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_READ)),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get noVNC console URL for a VM.

    Returns a URL that can be opened in a new window to access the VM's console.

    **Known Limitation:** Due to browser cross-domain security restrictions, users
    must be logged into the Proxmox web interface in a separate tab before the
    console will work. This is because Proxmox requires the PVEAuthCookie to be
    set as an actual HTTP cookie, which cannot be done cross-domain from JavaScript.

    **Workaround:**
    1. Open Proxmox web interface in a new tab (https://proxmox-server:8006)
    2. Log in with your credentials
    3. Return to this portal and click the Console button

    Requires: VM_READ permission
    """
    # Get VM with org check
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only access their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    # Get console URL from Proxmox
    try:
        proxmox_service = get_proxmox_service(vm.proxmox_cluster)
        console_info = await proxmox_service.get_console_url_async(vm.proxmox_node, vm.proxmox_vmid)

        # Extract Proxmox server URL for workaround instructions
        proxmox_url = console_info["console_url"]
        proxmox_host = proxmox_url.split("?")[0] if "?" in proxmox_url else proxmox_url

        return {
            "console_url": console_info["console_url"],
            "message": "Console URL generated successfully",
            "workaround_note": (
                f"If you see 'Error 401: No ticket', please log into Proxmox web interface first: {proxmox_host}"
            )
        }
    except Exception as e:
        logger.error(f"Failed to get console URL for VM {vm_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get console access: {str(e)}"
        )


@router.post("/{vm_id}/sync", response_model=VMResponse)
async def sync_vm_status(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_READ)),
    db: AsyncSession = Depends(get_db)
) -> VirtualMachine:
    """
    Sync VM status from Proxmox.

    Updates the VM status in the database to match the actual status in Proxmox.
    Useful for VMs stuck in "provisioning" status.

    Requires: VM_READ permission
    """
    # Get VM with org check
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only sync their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    # Get status from Proxmox
    try:
        proxmox_service = get_proxmox_service(vm.proxmox_cluster)
        proxmox_status = await proxmox_service.get_vm_status_async(vm.proxmox_node, vm.proxmox_vmid)

        # Update VM status based on Proxmox
        vm_status = proxmox_status.get("status", "unknown")
        vm.power_state = vm_status

        # Map Proxmox status to our status
        if vm_status == "running":
            vm.status = "running"
        elif vm_status == "stopped":
            vm.status = "stopped"
        elif vm_status == "paused":
            vm.status = "stopped"
        else:
            vm.status = "unknown"

        # Update IP if available
        if proxmox_status.get("ip"):
            vm.primary_ip_address = proxmox_status.get("ip")

        await db.commit()
        await db.refresh(vm)

        logger.info(f"Synced VM {vm.id} status from Proxmox: {vm_status}")
        return vm

    except Exception as e:
        logger.error(f"Failed to sync VM {vm.id} status: {e}")
        # If VM doesn't exist in Proxmox (404), mark as error
        if "404" in str(e) or "not found" in str(e).lower():
            vm.status = "error"
            await db.commit()
            await db.refresh(vm)
            return vm

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync VM status from Proxmox: {str(e)}"
        )


@router.post("/{vm_id}/force-stop", response_model=VMResponse)
async def force_stop_vm(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """
    Force stop (shutdown) a VM immediately.

    This forces the VM to stop without waiting for a graceful shutdown.

    Requires: VM_UPDATE permission
    """
    # Get VM with org check
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only force stop their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    # Force stop VM on Proxmox
    try:
        proxmox_service = get_proxmox_service(vm.proxmox_cluster)
        await proxmox_service.force_stop_vm_async(vm.proxmox_node, vm.proxmox_vmid)

        vm.status = "stopped"
        await db.commit()
        await db.refresh(vm)

        # Audit: VM force stopped
        await create_audit_log(
            db=db,
            action=AuditAction.VM_FORCE_STOPPED,
            resource_type="vm",
            resource_id=vm.id,
            resource_name=vm.name,
            user_id=org_context.user.id,
            organization_id=org_context.org_id,
            details={"proxmox_vmid": vm.proxmox_vmid},
        )

        logger.info(f"Force stopped VM {vm.id}")
        return vm
    except Exception as e:
        logger.error(f"Failed to force stop VM {vm.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to force stop VM: {str(e)}"
        )


@router.post("/{vm_id}/reboot", response_model=VMResponse)
async def reboot_vm(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """
    Reboot a VM.

    Sends a reboot signal to the VM.

    Requires: VM_UPDATE permission
    """
    # Get VM with org check
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only reboot their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    # Reboot VM on Proxmox
    try:
        proxmox_service = get_proxmox_service(vm.proxmox_cluster)
        await proxmox_service.reboot_vm_async(vm.proxmox_node, vm.proxmox_vmid)

        logger.info(f"Rebooted VM {vm.id}")
        await db.refresh(vm)
        return vm
    except Exception as e:
        logger.error(f"Failed to reboot VM {vm.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reboot VM: {str(e)}"
        )


@router.post("/{vm_id}/reset", response_model=VMResponse)
async def reset_vm(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """
    Reset a VM (hard reset).

    This performs a hard reset, similar to pressing the reset button on a physical computer.

    Requires: VM_UPDATE permission
    """
    # Get VM with org check
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only reset their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    # Reset VM on Proxmox
    try:
        proxmox_service = get_proxmox_service(vm.proxmox_cluster)
        await proxmox_service.reset_vm_async(vm.proxmox_node, vm.proxmox_vmid)

        logger.info(f"Reset VM {vm.id}")
        await db.refresh(vm)
        return vm
    except Exception as e:
        logger.error(f"Failed to reset VM {vm.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset VM: {str(e)}"
        )


@router.patch("/{vm_id}/resize", response_model=VMResponse)
async def resize_vm_resources(
    vm_id: str,
    resize_data: VMResize,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """
    Resize VM CPU and/or memory.

    **Note:** VM must be stopped to resize resources.
    **Permissions Required:** VM_UPDATE
    """
    # Get VM with org check
    query = select(VirtualMachine).where(
        VirtualMachine.id == vm_id,
        VirtualMachine.organization_id == org_context.org_id,
        VirtualMachine.deleted_at.is_(None)
    )

    # Members can only resize their own VMs
    if org_context.role == Role.ORG_MEMBER:
        query = query.where(VirtualMachine.owner_id == org_context.user.id)

    result = await db.execute(query)
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found or access denied"
        )

    # Verify at least one resource is specified
    if resize_data.cpu_cores is None and resize_data.cpu_sockets is None and resize_data.memory_mb is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one resource (CPU cores, CPU sockets, or memory) must be specified"
        )

    # Check quota for resource changes
    from app.services.quota_service import QuotaService

    quota_service = QuotaService(db)

    # Calculate deltas
    cpu_delta = 0
    memory_delta = 0

    if resize_data.cpu_cores is not None:
        cpu_delta = resize_data.cpu_cores - vm.cpu_cores

    if resize_data.memory_mb is not None:
        memory_delta = resize_data.memory_mb - vm.memory_mb

    # Check and reserve quota if resources are increasing (prevents TOCTOU race)
    if cpu_delta > 0 or memory_delta > 0:
        quota_check = await quota_service.check_and_reserve(
            organization_id=org_context.org_id,
            cpu_cores=cpu_delta if cpu_delta > 0 else 0,
            memory_gb=(memory_delta / 1024) if memory_delta > 0 else 0
        )

        if not quota_check.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization quota exceeded: {', '.join(quota_check.exceeded_resources)}"
            )

    # Check user-level quota if resources are increasing
    if cpu_delta > 0 or memory_delta > 0:
        user_quota_check = await quota_service.check_user_quota_availability(
            user_id=org_context.user.id,
            organization_id=org_context.org_id,
            cpu_cores=cpu_delta if cpu_delta > 0 else 0,
            memory_gb=(memory_delta / 1024) if memory_delta > 0 else 0
        )

        if not user_quota_check.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User quota exceeded: {', '.join(user_quota_check.exceeded_resources)}"
            )

    # Resize VM on Proxmox
    try:
        proxmox_service = get_proxmox_service(vm.proxmox_cluster)

        await proxmox_service.resize_vm_async(
            node=vm.proxmox_node,
            vmid=vm.proxmox_vmid,
            cpu_cores=resize_data.cpu_cores,
            cpu_sockets=resize_data.cpu_sockets,
            memory_mb=resize_data.memory_mb
        )

        # Update VM record
        if resize_data.cpu_cores is not None:
            vm.cpu_cores = resize_data.cpu_cores

        if resize_data.cpu_sockets is not None:
            vm.cpu_sockets = resize_data.cpu_sockets

        if resize_data.memory_mb is not None:
            vm.memory_mb = resize_data.memory_mb

        # Update user quota BEFORE commit (same transaction)
        if cpu_delta > 0 or memory_delta > 0:
            await quota_service.increment_user_usage(
                user_id=org_context.user.id,
                organization_id=org_context.org_id,
                cpu_cores=cpu_delta if cpu_delta > 0 else 0,
                memory_gb=(memory_delta / 1024) if memory_delta > 0 else 0
            )
        elif cpu_delta < 0 or memory_delta < 0:
            # Decrement both org and user quota if shrinking
            await quota_service.decrement_usage(
                organization_id=org_context.org_id,
                cpu_cores=abs(cpu_delta) if cpu_delta < 0 else 0,
                memory_gb=(abs(memory_delta) / 1024) if memory_delta < 0 else 0
            )
            await quota_service.decrement_user_usage(
                user_id=org_context.user.id,
                organization_id=org_context.org_id,
                cpu_cores=abs(cpu_delta) if cpu_delta < 0 else 0,
                memory_gb=(abs(memory_delta) / 1024) if memory_delta < 0 else 0
            )

        await db.commit()
        await db.refresh(vm)

        logger.info(f"Resized VM {vm.id}")
        return vm
    except Exception as e:
        logger.error(f"Failed to resize VM {vm.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resize VM: {str(e)}"
        )


# ==================== Network Management ====================

@router.post("/{vm_id}/attach-network", response_model=VMResponse)
async def attach_network_to_vm(
    vm_id: str,
    attach_request: VMNetworkAttachRequest,
    org_context: OrgContext = Depends(RequirePermission(Permission.NETWORK_ATTACH)),
    db: AsyncSession = Depends(get_db)
):
    """Attach network to VM with VLAN configuration.

    Attaches a VPC network to VM, automatically applying VLAN tagging.
    Optionally allocates IP address from network pool.

    **Required Permission**: network:attach

    Request body:
    ```json
    {
        "network_id": "string",
        "interface_order": 0,  // 0-3 for net0-net3
        "model": "virtio",  // virtio, e1000, rtl8139
        "allocate_ip": true,
        "ip_pool_id": "optional_pool_id"
    }
    ```
    """
    from app.models.vm_network_interface import VMNetworkInterface
    from app.services.network_service import NetworkService
    from app.services.ipam_service import IPAMService
    from app.schemas.network import IPAllocationRequest

    network_id = attach_request.network_id
    interface_order = attach_request.interface_order
    model = attach_request.model
    allocate_ip = attach_request.allocate_ip
    ip_pool_id = attach_request.ip_pool_id

    # Get VM with permission check
    result = await db.execute(
        select(VirtualMachine).where(
            VirtualMachine.id == vm_id,
            VirtualMachine.organization_id == org_context.org_id,
            VirtualMachine.deleted_at.is_(None)
        )
    )
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VM {vm_id} not found"
        )

    # Get network
    network_service = NetworkService(db)
    network = await network_service.get_network(network_id, org_context.org_id)

    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network {network_id} not found"
        )

    # Check if interface already exists
    interface_name = f"net{interface_order}"
    existing_result = await db.execute(
        select(VMNetworkInterface).where(
            VMNetworkInterface.vm_id == vm_id,
            VMNetworkInterface.interface_name == interface_name,
            VMNetworkInterface.deleted_at.is_(None)
        )
    )
    existing_interface = existing_result.scalar_one_or_none()

    if existing_interface:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interface {interface_name} already attached to VM"
        )

    # Check max interfaces (4)
    interfaces_result = await db.execute(
        select(func.count(VMNetworkInterface.id)).where(
            VMNetworkInterface.vm_id == vm_id,
            VMNetworkInterface.deleted_at.is_(None)
        )
    )
    interface_count = interfaces_result.scalar() or 0

    if interface_count >= 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 4 network interfaces per VM"
        )

    # Build Proxmox network config
    proxmox_service = get_proxmox_service(vm.proxmox_cluster)
    net_config = await proxmox_service.build_network_config_async(
        interface_name=interface_name,
        vlan_id=network.vlan_id,
        bridge=network.bridge,
        model=model
    )

    # Apply to Proxmox
    try:
        await proxmox_service.attach_network_to_vm_async(
            node=vm.proxmox_node,
            vmid=vm.proxmox_vmid,
            interface_name=interface_name,
            vlan_id=network.vlan_id,
            bridge=network.bridge,
            model=model
        )
    except Exception as e:
        logger.error(f"Failed to attach network to Proxmox VM {vm.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to attach network on Proxmox: {str(e)}"
        )

    # Create interface record
    is_primary = (interface_count == 0)  # First interface is primary
    interface = VMNetworkInterface(
        vm_id=vm.id,
        network_id=network.id,
        interface_name=interface_name,
        interface_order=interface_order,
        model=model,
        is_primary=is_primary,
        proxmox_config=net_config
    )
    db.add(interface)
    await db.flush()

    # Allocate IP if requested
    if allocate_ip:
        ipam_service = IPAMService(db)
        try:
            allocation_request = IPAllocationRequest(
                ip_pool_id=ip_pool_id
            ) if ip_pool_id else None

            ip_allocation = await ipam_service.allocate_ip(
                network_id=network.id,
                organization_id=org_context.org_id,
                vm_id=vm.id,
                interface_name=interface_name,
                allocation_request=allocation_request
            )
            interface.ip_allocation_id = ip_allocation.id

            logger.info(
                f"Allocated IP {ip_allocation.ip_address} to VM {vm.id} "
                f"interface {interface_name}"
            )
        except ValueError as e:
            logger.warning(f"Could not allocate IP for VM {vm.id}: {e}")
            # Continue without IP allocation - not critical

    await db.commit()
    await db.refresh(vm)

    logger.info(
        f"Attached network {network.id} (VLAN {network.vlan_id}) to VM {vm.id} "
        f"as {interface_name}"
    )

    return vm


@router.delete("/{vm_id}/detach-network/{interface_name}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_network_from_vm(
    vm_id: str,
    interface_name: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Detach network interface from VM.

    Removes network interface and releases IP allocation.

    **Required Permission**: vm:update
    """
    from app.models.vm_network_interface import VMNetworkInterface
    from app.services.ipam_service import IPAMService

    # Validate interface name
    if interface_name not in ["net0", "net1", "net2", "net3"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="interface_name must be one of: net0, net1, net2, net3"
        )

    # Get VM with permission check
    result = await db.execute(
        select(VirtualMachine).where(
            VirtualMachine.id == vm_id,
            VirtualMachine.organization_id == org_context.org_id,
            VirtualMachine.deleted_at.is_(None)
        )
    )
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VM {vm_id} not found"
        )

    # Get interface
    interface_result = await db.execute(
        select(VMNetworkInterface).where(
            VMNetworkInterface.vm_id == vm_id,
            VMNetworkInterface.interface_name == interface_name,
            VMNetworkInterface.deleted_at.is_(None)
        )
    )
    interface = interface_result.scalar_one_or_none()

    if not interface:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interface {interface_name} not found on VM"
        )

    # Detach from Proxmox
    try:
        proxmox_service = get_proxmox_service(vm.proxmox_cluster)
        await proxmox_service.detach_network_from_vm_async(
            node=vm.proxmox_node,
            vmid=vm.proxmox_vmid,
            interface_name=interface_name
        )
    except Exception as e:
        logger.error(f"Failed to detach network from Proxmox VM {vm.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detach network on Proxmox: {str(e)}"
        )

    # Release IP allocation if exists
    if interface.ip_allocation_id:
        ipam_service = IPAMService(db)
        await ipam_service.release_ip(
            interface.ip_allocation_id,
            org_context.org_id
        )

    # Soft delete interface
    interface.deleted_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info(f"Detached network interface {interface_name} from VM {vm.id}")


@router.post("/{vm_id}/convert-to-template", response_model=VMResponse)
async def convert_to_template(
    vm_id: str,
    template_data: VMTemplateCreate,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """
    Convert an existing VM to a template.

    The VM will be converted to a template on Proxmox and marked as immutable.
    Templates can be used to clone new VMs.

    Requires: VM_CREATE permission
    """
    result = await db.execute(
        select(VirtualMachine).where(
            VirtualMachine.id == vm_id,
            VirtualMachine.organization_id == org_context.org_id,
            VirtualMachine.deleted_at.is_(None)
        )
    )
    vm = result.scalar_one_or_none()

    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found"
        )

    if vm.is_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VM is already a template"
        )

    if vm.status != "stopped":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VM must be stopped before converting to template"
        )

    proxmox_service = get_proxmox_service(vm.proxmox_cluster)

    try:
        await proxmox_service.convert_vm_to_template_async(
            node=vm.proxmox_node,
            vmid=vm.proxmox_vmid
        )
    except Exception as e:
        logger.error(f"Failed to convert VM {vm_id} to template on Proxmox: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert to template on Proxmox: {str(e)}"
        )

    vm.is_template = True
    vm.name = template_data.name
    vm.description = template_data.description
    vm.os_type = template_data.os_type or vm.os_type
    vm.tags = template_data.tags or vm.tags
    vm.status = "template"

    await db.commit()
    await db.refresh(vm)

    logger.info(f"VM {vm_id} converted to template")
    return vm


# ==================== Firewall Management ====================

from app.services.firewall_service import FirewallService
from app.schemas.firewall import (
    FirewallRuleCreate,
    FirewallRuleUpdate,
    FirewallRuleResponse,
    FirewallRuleListResponse,
)


@router.get("/{vm_id}/firewall/status")
async def get_firewall_status(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_READ)),
    db: AsyncSession = Depends(get_db)
):
    """Get firewall status for a VM.

    Returns firewall enabled state, policies, and rules from Proxmox.

    **Required Permission**: vm:read
    """
    result = await db.execute(
        select(VirtualMachine).where(
            and_(
                VirtualMachine.id == vm_id,
                VirtualMachine.organization_id == org_context.org_id,
                VirtualMachine.deleted_at.is_(None)
            )
        )
    )
    vm = result.scalar_one_or_none()
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VM {vm_id} not found"
        )

    if not vm.proxmox_cluster:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VM has no Proxmox cluster configured"
        )

    firewall_service = FirewallService(db)
    proxmox_service = get_proxmox_service(vm.proxmox_cluster)

    status_data = await firewall_service.get_firewall_status(
        vm_id=vm_id,
        organization_id=org_context.org_id,
        proxmox_service=proxmox_service
    )
    return status_data


@router.post("/{vm_id}/firewall/enable", status_code=status.HTTP_204_NO_CONTENT)
async def enable_firewall(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Enable firewall for a VM.

    **Required Permission**: vm:update
    """
    result = await db.execute(
        select(VirtualMachine).where(
            and_(
                VirtualMachine.id == vm_id,
                VirtualMachine.organization_id == org_context.org_id,
                VirtualMachine.deleted_at.is_(None)
            )
        )
    )
    vm = result.scalar_one_or_none()
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VM {vm_id} not found"
        )

    if not vm.proxmox_cluster:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VM has no Proxmox cluster configured"
        )

    firewall_service = FirewallService(db)
    proxmox_service = get_proxmox_service(vm.proxmox_cluster)

    await firewall_service.enable_firewall(
        vm_id=vm_id,
        organization_id=org_context.org_id,
        proxmox_service=proxmox_service
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{vm_id}/firewall/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_firewall(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Disable firewall for a VM.

    **Required Permission**: vm:update
    """
    result = await db.execute(
        select(VirtualMachine).where(
            and_(
                VirtualMachine.id == vm_id,
                VirtualMachine.organization_id == org_context.org_id,
                VirtualMachine.deleted_at.is_(None)
            )
        )
    )
    vm = result.scalar_one_or_none()
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VM {vm_id} not found"
        )

    if not vm.proxmox_cluster:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VM has no Proxmox cluster configured"
        )

    firewall_service = FirewallService(db)
    proxmox_service = get_proxmox_service(vm.proxmox_cluster)

    await firewall_service.disable_firewall(
        vm_id=vm_id,
        organization_id=org_context.org_id,
        proxmox_service=proxmox_service
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{vm_id}/firewall/resync")
async def resync_firewall_rules(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Resync local firewall rules with Proxmox.

    Deletes all Proxmox rules and recreates from local database.

    **Required Permission**: vm:update
    """
    result = await db.execute(
        select(VirtualMachine).where(
            and_(
                VirtualMachine.id == vm_id,
                VirtualMachine.organization_id == org_context.org_id,
                VirtualMachine.deleted_at.is_(None)
            )
        )
    )
    vm = result.scalar_one_or_none()
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VM {vm_id} not found"
        )

    if not vm.proxmox_cluster:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VM has no Proxmox cluster configured"
        )

    firewall_service = FirewallService(db)
    proxmox_service = get_proxmox_service(vm.proxmox_cluster)

    result = await firewall_service.resync_rules(
        vm_id=vm_id,
        organization_id=org_context.org_id,
        proxmox_service=proxmox_service
    )
    return result


@router.get("/{vm_id}/firewall/rules", response_model=FirewallRuleListResponse)
async def list_firewall_rules(
    vm_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_READ)),
    db: AsyncSession = Depends(get_db)
):
    """List firewall rules for a VM.

    **Required Permission**: vm:read
    """
    result = await db.execute(
        select(VirtualMachine).where(
            and_(
                VirtualMachine.id == vm_id,
                VirtualMachine.organization_id == org_context.org_id,
                VirtualMachine.deleted_at.is_(None)
            )
        )
    )
    vm = result.scalar_one_or_none()
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VM {vm_id} not found"
        )

    firewall_service = FirewallService(db)
    rules = await firewall_service.list_rules(vm_id, org_context.org_id)

    return FirewallRuleListResponse(
        rules=rules,
        total=len(rules)
    )


@router.post(
    "/{vm_id}/firewall/rules",
    response_model=FirewallRuleResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_firewall_rule(
    vm_id: str,
    rule_data: FirewallRuleCreate,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Create a firewall rule for a VM.

    Rule is stored locally and synced to Proxmox.

    **Required Permission**: vm:update
    """
    result = await db.execute(
        select(VirtualMachine).where(
            and_(
                VirtualMachine.id == vm_id,
                VirtualMachine.organization_id == org_context.org_id,
                VirtualMachine.deleted_at.is_(None)
            )
        )
    )
    vm = result.scalar_one_or_none()
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VM {vm_id} not found"
        )

    if not vm.proxmox_cluster:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VM has no Proxmox cluster configured"
        )

    firewall_service = FirewallService(db)
    proxmox_service = get_proxmox_service(vm.proxmox_cluster)

    try:
        rule = await firewall_service.create_rule(
            vm_id=vm_id,
            organization_id=org_context.org_id,
            rule_data=rule_data,
            proxmox_service=proxmox_service
        )
        return rule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{vm_id}/firewall/rules/{rule_id}", response_model=FirewallRuleResponse)
async def get_firewall_rule(
    vm_id: str,
    rule_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_READ)),
    db: AsyncSession = Depends(get_db)
):
    """Get a single firewall rule.

    **Required Permission**: vm:read
    """
    firewall_service = FirewallService(db)

    try:
        rule = await firewall_service.get_rule(rule_id, org_context.org_id)
        return rule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{vm_id}/firewall/rules/{rule_id}",
    response_model=FirewallRuleResponse
)
async def update_firewall_rule(
    vm_id: str,
    rule_id: str,
    rule_data: FirewallRuleUpdate,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Update a firewall rule.

    **Required Permission**: vm:update
    """
    firewall_service = FirewallService(db)

    result = await db.execute(
        select(VirtualMachine).where(
            and_(
                VirtualMachine.id == vm_id,
                VirtualMachine.organization_id == org_context.org_id,
                VirtualMachine.deleted_at.is_(None)
            )
        )
    )
    vm = result.scalar_one_or_none()
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VM {vm_id} not found"
        )

    if not vm.proxmox_cluster:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VM has no Proxmox cluster configured"
        )

    proxmox_service = get_proxmox_service(vm.proxmox_cluster)

    try:
        rule = await firewall_service.update_rule(
            rule_id=rule_id,
            organization_id=org_context.org_id,
            rule_data=rule_data,
            proxmox_service=proxmox_service
        )
        return rule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{vm_id}/firewall/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_firewall_rule(
    vm_id: str,
    rule_id: str,
    org_context: OrgContext = Depends(RequirePermission(Permission.VM_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Delete a firewall rule.

    **Required Permission**: vm:update
    """
    result = await db.execute(
        select(VirtualMachine).where(
            and_(
                VirtualMachine.id == vm_id,
                VirtualMachine.organization_id == org_context.org_id,
                VirtualMachine.deleted_at.is_(None)
            )
        )
    )
    vm = result.scalar_one_or_none()
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VM {vm_id} not found"
        )

    if not vm.proxmox_cluster:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VM has no Proxmox cluster configured"
        )

    firewall_service = FirewallService(db)
    proxmox_service = get_proxmox_service(vm.proxmox_cluster)

    try:
        await firewall_service.delete_rule(
            rule_id=rule_id,
            organization_id=org_context.org_id,
            proxmox_service=proxmox_service
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
