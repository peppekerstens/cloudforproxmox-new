"""
Firewall service for VM firewall management.

STUB: Disabled in Phase 1 (Batch 2). Real implementation added in Phase 8.

FirewallService handles all firewall operations for VMs including:
- Enable/disable firewall for a VM
- List, create, update, delete firewall rules
- Resync rules with Proxmox

In Phase 1, this is a stub to allow Batch 2 features to deploy.
"""
from typing import Any, Dict, List, Optional


class FirewallService:
    """Stub firewall service for VM management.
    
    Allows code to call firewall operations without errors.
    In Phase 8, this will be replaced with real firewall functionality.
    """

    def __init__(self, db: Any):
        """Initialize with database session."""
        self.db = db

    async def get_firewall_status(self, vm_id: str, org_id: str) -> Dict[str, Any]:
        """Stub: Get firewall status for a VM."""
        return {"enabled": False, "rule_count": 0}

    async def enable_firewall(self, vm_id: str, org_id: str) -> Dict[str, Any]:
        """Stub: Enable firewall for a VM."""
        return {"enabled": True}

    async def disable_firewall(self, vm_id: str, org_id: str) -> Dict[str, Any]:
        """Stub: Disable firewall for a VM."""
        return {"enabled": False}

    async def resync_rules(self, vm_id: str, org_id: str) -> Dict[str, Any]:
        """Stub: Resync firewall rules with Proxmox."""
        return {"success": True, "synced_count": 0}

    async def list_rules(self, vm_id: str, org_id: str) -> List[Dict[str, Any]]:
        """Stub: List firewall rules for a VM."""
        return []

    async def create_rule(self, vm_id: str, org_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stub: Create a firewall rule."""
        return {"id": "stub-rule-id", **rule_data}

    async def get_rule(self, rule_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        """Stub: Get a specific firewall rule."""
        return None

    async def update_rule(self, rule_id: str, org_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stub: Update a firewall rule."""
        return {"id": rule_id, **rule_data}

    async def delete_rule(self, rule_id: str, org_id: str) -> bool:
        """Stub: Delete a firewall rule."""
        return True
