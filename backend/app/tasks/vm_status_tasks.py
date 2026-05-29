"""
VM power state polling task.

STUB: Disabled in Phase 1 (Batch 2). Real implementation added in Phase 8.

poll_vm_power_state.delay() is called after VM operations to sync power state
from Proxmox into the database. Without it, VM power status is stale until
manual refresh.

In Phase 1, this is a no-op to allow Batch 2 features to deploy.
"""


class VMStatusPollingStub:
    """Stub Celery task for VM power state polling.
    
    Allows code to call poll_vm_power_state.delay(vmid, node) without errors.
    """

    def delay(self, *args, **kwargs):
        """Stub: Background polling disabled in Phase 1 Batch 2.
        
        In Phase 8, this will be replaced with real Celery task that:
        - Polls Proxmox API for VM power state
        - Updates database with current state
        - Handles stale connections gracefully
        """
        pass

    def apply_async(self, *args, **kwargs):
        """Stub: Alternative async interface."""
        pass

    def apply(self, *args, **kwargs):
        """Stub: Synchronous interface."""
        pass


# Global instance for vms.py to call
poll_vm_power_state = VMStatusPollingStub()
