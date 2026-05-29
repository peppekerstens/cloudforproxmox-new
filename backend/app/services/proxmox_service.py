"""
Proxmox VE service wrapper for managing VMs via Proxmox API.
"""
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from proxmoxer import ProxmoxAPI
from proxmoxer.core import ResourceException
import logging

from app.models.proxmox_cluster import ProxmoxCluster

logger = logging.getLogger(__name__)

# Module-level cache: cluster_id -> ProxmoxService instance
_service_cache: Dict[int, "ProxmoxService"] = {}
_cache_lock = asyncio.Lock()


def get_proxmox_service(cluster: ProxmoxCluster) -> "ProxmoxService":
    """Return cached ProxmoxService for a cluster, creating if needed.

    Thread-safe for async context. Reuses the same ProxmoxAPI connection
    across requests for the same cluster.
    """
    cid = cluster.id
    if cid in _service_cache:
        return _service_cache[cid]
    svc = ProxmoxService(cluster=cluster)
    _service_cache[cid] = svc
    return svc


async def get_proxmox_service_async(cluster: ProxmoxCluster) -> "ProxmoxService":
    """Async-safe version of get_proxmox_service for concurrent request handling."""
    cid = cluster.id
    if cid in _service_cache:
        return _service_cache[cid]
    async with _cache_lock:
        # Double-check after acquiring lock
        if cid in _service_cache:
            return _service_cache[cid]
        svc = ProxmoxService(cluster=cluster)
        _service_cache[cid] = svc
        return svc


# Minimum Proxmox VE versions for feature support
MIN_VERSIONS = {
    "lxc": (4, 0),          # LXC containers (pct API)
    "vm_template": (4, 0),   # VM → template conversion
    "vm_clone": (4, 0),      # VM cloning
    "vm_clone_target": (5, 0),  # Cross-node clone (target parameter)
    "api_token_auth": (6, 2),   # API token authentication
    "sdn": (7, 4),            # SDN (VXLAN zones) stable
    "unprivileged_lxc": (4, 0),  # Unprivileged containers
}


class ProxmoxVersionError(Exception):
    """Raised when Proxmox version does not support a feature."""

    def __init__(self, feature: str, required: Tuple[int, int], actual: Tuple[int, int]):
        self.feature = feature
        self.required = required
        self.actual = actual
        super().__init__(
            f"Feature '{feature}' requires Proxmox VE {'.'.join(map(str, required))}+, "
            f"but running {'.'.join(map(str, actual))}"
        )


class ProxmoxService:
    """Service for interacting with Proxmox VE API."""

    def __init__(
        self,
        cluster: Optional[ProxmoxCluster] = None,
        host: Optional[str] = None,
        user: Optional[str] = None,
        token_name: Optional[str] = None,
        token_value: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: bool = False,
    ):
        """
        Initialize Proxmox service with cluster credentials.

        Args:
            cluster: ProxmoxCluster model instance (preferred)
            host: Proxmox host (alternative to cluster)
            user: Username (alternative to cluster)
            token_name: API token name (alternative to cluster)
            token_value: API token value (alternative to cluster)
            password: Password (alternative to cluster)
            verify_ssl: Verify SSL certificate
        """
        self.cluster = cluster
        self._host = host
        self._user = user
        self._token_name = token_name
        self._token_value = token_value
        self._password = password
        self._verify_ssl = verify_ssl
        self._proxmox: Optional[ProxmoxAPI] = None

    def _get_connection(self) -> ProxmoxAPI:
        """Get or create Proxmox API connection."""
        if self._proxmox is None:
            host, port, user, token_name, token_value, password, verify_ssl = self._get_credentials()

            # Use token authentication if available, otherwise password
            if token_name and token_value:
                # Strip "user!" prefix if user pasted the full Proxmox token ID (e.g. "root@pam!theanh")
                if "!" in token_name:
                    token_name = token_name.split("!", 1)[1]
                self._proxmox = ProxmoxAPI(
                    host,
                    user=user,
                    token_name=token_name,
                    token_value=token_value,
                    port=port,
                    verify_ssl=verify_ssl,
                )
            else:
                self._proxmox = ProxmoxAPI(
                    host,
                    user=user,
                    password=password,
                    port=port,
                    verify_ssl=verify_ssl,
                )

        return self._proxmox

    def _get_credentials(self) -> Tuple[str, int, str, Optional[str], Optional[str], Optional[str], bool]:
        """Get connection credentials.

        Returns:
            Tuple of (host, port, user, token_name, token_value, password, verify_ssl)
        """
        if self.cluster:
            if not self.cluster.api_url:
                raise ValueError("ProxmoxCluster api_url is required")
            from urllib.parse import urlparse
            parsed = urlparse(self.cluster.api_url)
            host = parsed.hostname
            if not host:
                raise ValueError(f"Invalid api_url: {self.cluster.api_url} (could not extract hostname)")
            port = parsed.port or 8006  # Proxmox default port
            user = self.cluster.api_username
            token_name = self.cluster.api_token_id
            token_value = self.cluster.api_token_secret_encrypted
            password = self.cluster.api_password_encrypted
            verify_ssl = self.cluster.verify_ssl
        else:
            host = self._host
            port = 8006  # Default port for direct instantiation
            user = self._user
            token_name = self._token_name
            token_value = self._token_value
            password = self._password
            verify_ssl = self._verify_ssl

        return host, port, user, token_name, token_value, password, verify_ssl

    def get_version_tuple(self) -> Tuple[int, int]:
        """
        Get Proxmox VE version as a (major, minor) tuple.

        Returns:
            Tuple of (major, minor) version numbers
        """
        version_data = self.get_version()
        release = version_data.get("release", "0.0")
        parts = release.split(".")
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        return (major, minor)

    def check_feature_support(self, feature: str) -> None:
        """
        Check if the connected Proxmox version supports a feature.

        Args:
            feature: Feature name (see MIN_VERSIONS dict)

        Raises:
            ProxmoxVersionError: If version is too old
        """
        if feature not in MIN_VERSIONS:
            logger.warning(f"Unknown feature '{feature}' — skipping version check")
            return

        required = MIN_VERSIONS[feature]
        actual = self.get_version_tuple()

        if actual < required:
            raise ProxmoxVersionError(feature, required, actual)

        logger.debug(f"Feature '{feature}' supported (Proxmox {'.'.join(map(str, actual))} >= {'.'.join(map(str, required))})")

    def get_next_vmid(self, node: Optional[str] = None) -> int:
        """
        Get next available VMID from Proxmox cluster.

        Uses Proxmox's nextid API with retry logic to handle race conditions
        when multiple VMs are created simultaneously.

        Args:
            node: Optional node name to check VMID availability on.
                  If provided, ensures the VMID doesn't already exist on that node.

        Returns:
            Next available VMID
        """
        try:
            proxmox = self._get_connection()
            for attempt in range(20):
                vmid = proxmox.cluster.nextid.get()
                vmid = int(vmid) if vmid else 100

                if node:
                    if self._vmid_exists_on_node(proxmox, node, vmid):
                        logger.warning(f"VMID {vmid} already exists on node {node}, trying next")
                        continue
                return vmid

            logger.error("Failed to find available VMID after 20 attempts")
            import random
            return random.randint(1000, 9999)
        except ResourceException as e:
            # Handle "VMID already exists" race condition
            if "already exists" in str(e).lower():
                logger.warning(f"VMID collision detected, retrying: {e}")
                try:
                    proxmox = self._get_connection()
                    for attempt in range(20):
                        vmid = proxmox.cluster.nextid.get()
                        vmid = int(vmid) if vmid else 100
                        if node and self._vmid_exists_on_node(proxmox, node, vmid):
                            continue
                        return vmid
                except Exception:
                    pass
            logger.error(f"Failed to get next VMID: {e}")
            import random
            return random.randint(1000, 9999)
        except Exception as e:
            logger.error(f"Failed to get next VMID: {e}")
            import random
            return random.randint(1000, 9999)

    def _vmid_exists_on_node(self, proxmox: ProxmoxAPI, node: str, vmid: int) -> bool:
        """Check if a VMID already exists on a specific node."""
        try:
            try:
                proxmox.nodes(node).qemu(vmid).config.get()
                return True
            except ResourceException:
                pass
            try:
                proxmox.nodes(node).lxc(vmid).config.get()
                return True
            except ResourceException:
                pass
            return False
        except Exception as e:
            logger.warning(f"Error checking VMID {vmid} on node {node}: {e}")
            return False

    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Get list of nodes enriched with per-node CPU/memory status.
        proxmox.nodes.get() only returns basic info; maxcpu/maxmem require
        a separate GET /nodes/{node}/status call for each online node.
        """
        try:
            proxmox = self._get_connection()
            nodes = proxmox.nodes.get()
            for node in nodes:
                if node.get("status") == "online":
                    try:
                        status = proxmox.nodes(node["node"]).status.get()
                        node["maxcpu"] = status.get("cpuinfo", {}).get("cpus", 0)
                        node["maxmem"] = status.get("memory", {}).get("total", 0)
                    except Exception as e:
                        logger.warning(f"Failed to get status for node {node['node']}: {e}")
            return nodes
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
            return []

    def get_version(self) -> Dict[str, Any]:
        """
        Get Proxmox VE version information.

        Returns:
            Version information dictionary
        """
        try:
            proxmox = self._get_connection()
            return proxmox.version.get()
        except Exception as e:
            logger.error(f"Failed to get version: {e}")
            return {}

    def get_cluster_status(self) -> List[Dict[str, Any]]:
        """Get cluster status including node IPs.

        Returns:
            List of cluster member dicts (nodes have ``ip``, ``name``, ``online``).
        """
        try:
            proxmox = self._get_connection()
            return proxmox.cluster.status.get()
        except Exception as e:
            logger.error(f"Failed to get cluster status: {e}")
            return []

    def select_best_node(self) -> Optional[str]:
        """
        Select the best node for VM placement based on available resources.

        Returns:
            Node name or None if no nodes available
        """
        nodes = self.get_nodes()
        if not nodes:
            return None

        # Find node with most available memory
        best_node = max(nodes, key=lambda n: n.get("maxmem", 0) - n.get("mem", 0))
        return best_node.get("node")

    def create_vm(
        self,
        node: str,
        vmid: int,
        name: str,
        cores: int,
        memory: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new VM on Proxmox.

        Args:
            node: Node name where VM should be created
            vmid: VM ID
            name: VM name
            cores: Number of CPU cores
            memory: Memory in MB
            **kwargs: Additional VM configuration options

        Returns:
            Task ID and status information

        Raises:
            ResourceException: If VM creation fails
        """
        try:
            proxmox = self._get_connection()

            # Base configuration
            config = {
                "vmid": vmid,
                "name": name,
                "cores": cores,
                "memory": memory,
                "sockets": kwargs.get("sockets", 1),
                "ostype": kwargs.get("ostype", "l26"),  # Linux 2.6+
                "net0": kwargs.get("net0", "virtio,bridge=vmbr0"),
            }

            # Add disk configuration if provided
            if "disk_gb" in kwargs:
                # Use raw format which is universally supported (LVM-Thin, ZFS, Directory)
                # Don't specify format to let Proxmox choose the appropriate one for the storage
                config["scsi0"] = f"local-lvm:{kwargs['disk_gb']}"

            # Create VM
            logger.info(f"Creating VM {vmid} ({name}) on node {node}")
            task = proxmox.nodes(node).qemu.create(**config)

            return {
                "task_id": task,
                "vmid": vmid,
                "node": node,
                "status": "creating"
            }

        except ResourceException as e:
            logger.error(f"Failed to create VM {vmid}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating VM {vmid}: {e}")
            raise

    def start_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Start a VM.

        Args:
            node: Node name where VM is located
            vmid: VM ID

        Returns:
            Task ID and status
        """
        try:
            proxmox = self._get_connection()
            task = proxmox.nodes(node).qemu(vmid).status.start.post()
            logger.info(f"Started VM {vmid} on node {node}")
            return {"task_id": task, "status": "starting"}
        except Exception as e:
            logger.error(f"Failed to start VM {vmid}: {e}")
            raise

    def stop_vm(self, node: str, vmid: int, force: bool = False) -> Dict[str, Any]:
        """
        Stop a VM.

        Args:
            node: Node name where VM is located
            vmid: VM ID
            force: Force stop (equivalent to power off)

        Returns:
            Task ID and status
        """
        try:
            proxmox = self._get_connection()
            if force:
                task = proxmox.nodes(node).qemu(vmid).status.stop.post()
            else:
                task = proxmox.nodes(node).qemu(vmid).status.shutdown.post()

            logger.info(f"Stopped VM {vmid} on node {node} (force={force})")
            return {"task_id": task, "status": "stopping"}
        except Exception as e:
            logger.error(f"Failed to stop VM {vmid}: {e}")
            raise

    def update_vm_config(
        self,
        node: str,
        vmid: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update VM configuration.

        Args:
            node: Node name where VM is located
            vmid: VM ID
            **kwargs: Configuration parameters (cores, memory, name, ostype, etc.)

        Returns:
            Success status
        """
        try:
            proxmox = self._get_connection()
            proxmox.nodes(node).qemu(vmid).config.put(**kwargs)
            logger.info(f"Updated VM {vmid} configuration on node {node}")
            return {"status": "updated"}
        except Exception as e:
            logger.error(f"Failed to update VM {vmid} configuration: {e}")
            raise

    def create_lxc(
        self,
        node: str,
        vmid: int,
        ostemplate: str,
        hostname: str,
        password: str,
        storage: str,
        disk_size: int,
        cores: int = 1,
        memory: int = 512,
        net0: str = "name=eth0,bridge=vmbr0,type=veth,firewall=1",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create an LXC container.

        Requires: Proxmox VE 4.0+ (LXC API), 4.0+ (unprivileged containers)

        Args:
            node: Target node name
            vmid: Container ID
            ostemplate: Template path (e.g., local:vztmpl/ubuntu-22.04-standard)
            hostname: Container hostname
            password: Root password
            storage: Target storage for rootfs
            disk_size: Rootfs size in GB
            cores: CPU cores
            memory: Memory in MB
            net0: Network configuration

        Returns:
            Task ID and status

        Raises:
            ProxmoxVersionError: If Proxmox version < 4.0
        """
        self.check_feature_support("lxc")
        self.check_feature_support("unprivileged_lxc")

        try:
            proxmox = self._get_connection()
            config = {
                "vmid": vmid,
                "ostemplate": ostemplate,
                "hostname": hostname,
                "password": password,
                "rootfs": f"{storage}:{disk_size}",
                "cores": cores,
                "memory": memory,
                "net0": net0,
                "unprivileged": 1,
            }
            config.update(kwargs)

            logger.info(f"Creating LXC {vmid} ({hostname}) on node {node}")
            task = proxmox.nodes(node).lxc.create(**config)

            return {
                "task_id": task,
                "vmid": vmid,
                "node": node,
                "status": "creating"
            }
        except Exception as e:
            logger.error(f"Failed to create LXC {vmid}: {e}")
            raise

    def start_lxc(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Start an LXC container.

        Args:
            node: Node name where container is located
            vmid: Container ID

        Returns:
            Task ID and status
        """
        try:
            proxmox = self._get_connection()
            task = proxmox.nodes(node).lxc(vmid).status.start.post()
            logger.info(f"Started LXC {vmid} on node {node}")
            return {"task_id": task, "status": "starting"}
        except Exception as e:
            logger.error(f"Failed to start LXC {vmid}: {e}")
            raise

    def stop_lxc(self, node: str, vmid: int, force: bool = False) -> Dict[str, Any]:
        """
        Stop an LXC container.

        Args:
            node: Node name where container is located
            vmid: Container ID
            force: Force stop

        Returns:
            Task ID and status
        """
        try:
            proxmox = self._get_connection()
            if force:
                task = proxmox.nodes(node).lxc(vmid).status.stop.post()
            else:
                task = proxmox.nodes(node).lxc(vmid).status.shutdown.post()

            logger.info(f"Stopped LXC {vmid} on node {node} (force={force})")
            return {"task_id": task, "status": "stopping"}
        except Exception as e:
            logger.error(f"Failed to stop LXC {vmid}: {e}")
            raise

    def restart_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Restart a VM.

        Args:
            node: Node name where VM is located
            vmid: VM ID

        Returns:
            Task ID and status
        """
        try:
            proxmox = self._get_connection()
            task = proxmox.nodes(node).qemu(vmid).status.reboot.post()
            logger.info(f"Restarted VM {vmid} on node {node}")
            return {"task_id": task, "status": "restarting"}
        except Exception as e:
            logger.error(f"Failed to restart VM {vmid}: {e}")
            raise

    def delete_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Delete a VM.

        Args:
            node: Node name where VM is located
            vmid: VM ID

        Returns:
            Task ID and status
        """
        try:
            proxmox = self._get_connection()
            task = proxmox.nodes(node).qemu(vmid).delete()
            logger.info(f"Deleted VM {vmid} from node {node}")
            return {"task_id": task, "status": "deleting"}
        except Exception as e:
            logger.error(f"Failed to delete VM {vmid}: {e}")
            raise

    def convert_vm_to_template(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Convert a VM to a template on Proxmox.

        Requires: Proxmox VE 4.0+ (template endpoint)

        Args:
            node: Node name where VM is located
            vmid: VM ID

        Returns:
            Task ID and status

        Raises:
            ProxmoxVersionError: If Proxmox version < 4.0
        """
        self.check_feature_support("vm_template")

        try:
            proxmox = self._get_connection()
            task = proxmox.nodes(node).qemu(vmid).template.post()
            logger.info(f"Converted VM {vmid} to template on node {node}")
            return {"task_id": task, "status": "converting"}
        except Exception as e:
            logger.error(f"Failed to convert VM {vmid} to template: {e}")
            raise

    def clone_vm_from_template(
        self,
        node: str,
        template_vmid: int,
        new_vmid: int,
        name: str,
        target_node: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Clone a VM from a template.

        Requires: Proxmox VE 4.0+ (clone endpoint), 5.0+ for cross-node clone

        Args:
            node: Node name where template is located
            template_vmid: Template VM ID
            new_vmid: New VM ID
            name: New VM name
            target_node: Target node (defaults to source node)

        Returns:
            Task ID and status

        Raises:
            ProxmoxVersionError: If Proxmox version < 4.0 (or < 5.0 for cross-node)
        """
        self.check_feature_support("vm_clone")
        if target_node:
            self.check_feature_support("vm_clone_target")

        try:
            proxmox = self._get_connection()
            params = {
                "newid": new_vmid,
                "name": name,
            }
            if target_node:
                params["target"] = target_node

            task = proxmox.nodes(node).qemu(template_vmid).clone.post(**params)
            logger.info(f"Cloning template {template_vmid} to VM {new_vmid} on node {node}")
            return {"task_id": task, "status": "cloning"}
        except Exception as e:
            logger.error(f"Failed to clone from template {template_vmid}: {e}")
            raise

    def get_console_url(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Get noVNC console URL for a VM.

        Creates a simple console URL that relies on the user being logged into
        Proxmox in their browser. The browser's existing Proxmox session cookies
        will be used for authentication.

        Args:
            node: Node name where VM is located
            vmid: VM ID

        Returns:
            Dict containing console URL

        Raises:
            Exception: If VM information cannot be retrieved
        """
        try:
            proxmox = self._get_connection()

            # Get VM name for the URL
            vm_config = proxmox.nodes(node).qemu(vmid).config.get()
            vm_name = vm_config.get('name', f'vm-{vmid}')

            # Get cluster host
            if self.cluster:
                api_url = self.cluster.api_url
                host = api_url.replace("https://", "").replace("http://", "").split(":")[0]
                port = 8006  # Default Proxmox web interface port
            else:
                host = self._host
                port = 8006

            # Build simple console URL that uses browser's existing Proxmox session
            console_url = (
                f"https://{host}:{port}/"
                f"?console=kvm&novnc=1&vmid={vmid}&vmname={vm_name}&node={node}"
                f"&resize=off&cmd="
            )

            logger.info(f"Generated console URL for VM {vmid} ({vm_name}) on node {node}")

            return {
                "console_url": console_url,
                "node": node,
                "vmid": vmid,
                "vm_name": vm_name
            }

        except Exception as e:
            logger.error(f"Failed to get console URL for VM {vmid}: {e}")
            raise

    def get_vm_status(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Get VM status and configuration.

        Args:
            node: Node name where VM is located
            vmid: VM ID

        Returns:
            VM status information
        """
        try:
            proxmox = self._get_connection()
            status = proxmox.nodes(node).qemu(vmid).status.current.get()
            return status
        except Exception as e:
            logger.error(f"Failed to get VM {vmid} status: {e}")
            raise

    def get_vm_config(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Get VM configuration.

        Args:
            node: Node name where VM is located
            vmid: VM ID

        Returns:
            VM configuration
        """
        try:
            proxmox = self._get_connection()
            config = proxmox.nodes(node).qemu(vmid).config.get()
            return config
        except Exception as e:
            logger.error(f"Failed to get VM {vmid} config: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test connection to Proxmox cluster.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            proxmox = self._get_connection()
            # Try to get cluster status
            proxmox.cluster.status.get()
            return True
        except Exception as e:
            logger.error(f"Proxmox connection test failed: {e}")
            return False

    # ===== Storage Pool Methods =====

    def get_storage_pools(self, node: str) -> List[Dict[str, Any]]:
        """
        Get list of storage pools available on a node.

        Args:
            node: Node name

        Returns:
            List of storage pool information
        """
        try:
            proxmox = self._get_connection()
            storage_list = proxmox.nodes(node).storage.get()
            # Ensure we have a list, not a ProxmoxResource wrapper
            if not isinstance(storage_list, list):
                storage_list = list(storage_list) if hasattr(storage_list, '__iter__') else []
            logger.info(f"Retrieved {len(storage_list)} storage pools from node {node}")
            return storage_list
        except Exception as e:
            logger.error(f"Failed to get storage pools from node {node}: {e}")
            raise

    def get_storage_status(self, node: str, storage: str) -> Dict[str, Any]:
        """
        Get detailed status of a specific storage pool.

        Args:
            node: Node name
            storage: Storage pool name

        Returns:
            Storage status including capacity information
        """
        try:
            proxmox = self._get_connection()
            status = proxmox.nodes(node).storage(storage).status.get()
            return status
        except Exception as e:
            logger.error(f"Failed to get storage {storage} status on node {node}: {e}")
            raise

    def get_storage_content(self, node: str, storage: str, content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get content (ISOs, images, etc.) from a storage pool.

        Args:
            node: Node name
            storage: Storage pool name
            content_type: Filter by content type (iso, images, backup, vztmpl)

        Returns:
            List of storage content items
        """
        try:
            proxmox = self._get_connection()
            params = {}
            if content_type:
                params['content'] = content_type

            content = proxmox.nodes(node).storage(storage).content.get(**params)
            return content
        except Exception as e:
            logger.error(f"Failed to get storage {storage} content on node {node}: {e}")
            raise

    # ===== ISO Management Methods =====

    def upload_iso(self, node: str, storage: str, filename: str, file_path: str) -> Dict[str, Any]:
        """
        Upload an ISO file to Proxmox storage.

        Uses requests directly because proxmoxer has issues with multipart
        file uploads to the Proxmox upload endpoint.

        Args:
            node: Node name
            storage: Storage pool name
            filename: Name for the ISO file
            file_path: Local path to the ISO file

        Returns:
            Upload task information
        """
        try:
            proxmox = self._get_connection()
            host, _, _, _, _, verify_ssl = self._get_credentials()

            # Build the upload URL
            upload_url = f"https://{host}:8006/api2/json/nodes/{node}/storage/{storage}/upload"

            # Get auth headers from proxmoxer's session
            session = proxmox.get_session()

            # Use the Authorization header from the session (works for both token and cookie auth)
            auth_headers = {}
            if "Authorization" in session.headers:
                auth_headers["Authorization"] = session.headers["Authorization"]
            else:
                # Fallback to CSRF token for cookie-based auth
                auth_headers["CSRFPreventionToken"] = session.headers.get("CSRFPreventionToken", "")

            # Prepare multipart form data
            with open(file_path, 'rb') as iso_file:
                files = {
                    'file': (filename, iso_file, 'application/octet-stream'),
                }
                data = {
                    'content': 'iso',
                    'filename': filename,
                }

                response = session.post(
                    upload_url,
                    files=files,
                    data=data,
                    headers=auth_headers,
                    verify=verify_ssl,
                )

            if response.status_code not in (200, 201):
                raise Exception(f"ISO upload failed with status {response.status_code}: {response.text}")

            result = response.json()
            task = result.get('data')

            logger.info(f"Uploaded ISO {filename} to {storage} on node {node}")
            return {"task_id": task, "status": "uploading"}
        except Exception as e:
            logger.error(f"Failed to upload ISO {filename} to {storage} on node {node}: {e}")
            raise

    def download_iso_from_url(
        self,
        node: str,
        storage: str,
        filename: str,
        url: str,
        checksum: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download an ISO file from a URL directly to Proxmox storage.

        This uses Proxmox's built-in download-url feature which is more efficient
        than downloading to our backend and then uploading.

        Args:
            node: Node name
            storage: Storage pool name
            filename: Name for the ISO file (with .iso extension)
            url: URL to download the ISO from
            checksum: Optional SHA256 checksum for verification

        Returns:
            Task information including task ID (UPID)

        Raises:
            Exception: If download initiation fails
        """
        try:
            proxmox = self._get_connection()

            # Prepare parameters for download-url API
            params = {
                'content': 'iso',
                'filename': filename,
                'url': url
            }

            # Add checksum verification if provided
            if checksum:
                params['checksum'] = checksum
                params['checksum-algorithm'] = 'sha256'

            # Initiate download task
            task_id = proxmox.nodes(node).storage(storage).post('download-url', **params)

            logger.info(f"Initiated ISO download from URL to {storage} on node {node}: {filename}")
            return {
                "task_id": task_id,
                "status": "downloading",
                "node": node,
                "storage": storage,
                "filename": filename
            }

        except Exception as e:
            logger.error(f"Failed to initiate ISO download from URL for {filename}: {e}")
            raise

    def get_task_status(self, node: str, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a Proxmox task (UPID).

        Args:
            node: Node name where the task is running
            task_id: Task ID (UPID format)

        Returns:
            Dict containing task status information:
            - status: 'running', 'stopped'
            - exitstatus: 'OK' if successful, error message if failed
            - type: task type
            - node: node name
            - upid: task UPID

        Raises:
            Exception: If task status check fails
        """
        try:
            proxmox = self._get_connection()

            # Get task status
            task_status = proxmox.nodes(node).tasks(task_id).status.get()

            logger.debug(f"Task {task_id} status: {task_status.get('status')}")
            return task_status

        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            raise

    def delete_iso(self, node: str, volid: str) -> Dict[str, Any]:
        """
        Delete an ISO file from Proxmox storage.

        Args:
            node: Node name
            volid: Volume ID (format: storage:iso/filename.iso)

        Returns:
            Task information
        """
        try:
            proxmox = self._get_connection()

            # Parse volid to get storage and volume
            storage, volume = volid.split(':', 1)

            task = proxmox.nodes(node).storage(storage).content(volid).delete()
            logger.info(f"Deleted ISO {volid} from node {node}")
            return {"task_id": task, "status": "deleted"}
        except Exception as e:
            logger.error(f"Failed to delete ISO {volid} from node {node}: {e}")
            raise

    # ===== Multi-Disk VM Creation Methods =====

    def create_vm_base(
        self,
        node: str,
        vmid: int,
        name: str,
        cores: int,
        memory: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a base VM without disks.
        Disks can be added later using set_vm_config.

        Args:
            node: Node name where VM should be created
            vmid: VM ID
            name: VM name
            cores: Number of CPU cores
            memory: Memory in MB
            **kwargs: Additional VM configuration options

        Returns:
            Task ID and status information
        """
        try:
            proxmox = self._get_connection()

            # Base configuration without disks
            config = {
                "vmid": vmid,
                "name": name,
                "cores": cores,
                "memory": memory,
                "sockets": kwargs.get("sockets", 1),
                "ostype": kwargs.get("ostype", "l26"),
                "net0": kwargs.get("net0", "virtio,bridge=vmbr0"),
            }

            # Add any additional configuration
            config.update({k: v for k, v in kwargs.items() if k not in config})

            # Create VM
            logger.info(f"Creating base VM {vmid} ({name}) on node {node}")
            task = proxmox.nodes(node).qemu.create(**config)

            return {
                "task_id": task,
                "vmid": vmid,
                "node": node,
                "status": "creating"
            }

        except ResourceException as e:
            logger.error(f"Failed to create base VM {vmid}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating base VM {vmid}: {e}")
            raise

    def set_vm_config(self, node: str, vmid: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set VM configuration parameters (e.g., add disks, change settings).

        Args:
            node: Node name where VM is located
            vmid: VM ID
            config: Configuration parameters to set

        Returns:
            Task or success status

        Example:
            # Add a disk
            set_vm_config(node, vmid, {"scsi0": "local-lvm:40"})

            # Mount an ISO
            set_vm_config(node, vmid, {"ide2": "local:iso/ubuntu-22.04.iso,media=cdrom"})

            # Set boot order
            set_vm_config(node, vmid, {"boot": "order=ide2;scsi0"})
        """
        try:
            proxmox = self._get_connection()
            result = proxmox.nodes(node).qemu(vmid).config.put(**config)
            logger.info(f"Updated VM {vmid} config on node {node}: {config}")
            return {"status": "updated", "result": result}
        except Exception as e:
            logger.error(f"Failed to set VM {vmid} config on node {node}: {e}")
            raise

    def add_disk_to_vm(
        self,
        node: str,
        vmid: int,
        disk_interface: str,
        disk_number: int,
        storage: str,
        size_gb: int,
        disk_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a disk to an existing VM.

        Args:
            node: Node name
            vmid: VM ID
            disk_interface: Disk interface (scsi, ide, virtio, sata)
            disk_number: Disk number (0, 1, 2, ...)
            storage: Storage pool name
            size_gb: Disk size in GB
            disk_format: Disk format (raw, qcow2) - optional

        Returns:
            Task or success status
        """
        disk_key = f"{disk_interface}{disk_number}"

        # Format: storage:size or storage:size,format=raw
        if disk_format:
            disk_value = f"{storage}:{size_gb},format={disk_format}"
        else:
            disk_value = f"{storage}:{size_gb}"

        config = {disk_key: disk_value}

        logger.info(f"Adding disk {disk_key} to VM {vmid}: {disk_value}")
        return self.set_vm_config(node, vmid, config)

    def mount_iso_to_vm(
        self,
        node: str,
        vmid: int,
        iso_volid: str,
        disk_interface: str = "ide",
        disk_number: int = 2
    ) -> Dict[str, Any]:
        """
        Mount an ISO file to a VM as a CD-ROM device.

        Args:
            node: Node name
            vmid: VM ID
            iso_volid: ISO volume ID (format: storage:iso/filename.iso)
            disk_interface: Disk interface (default: ide)
            disk_number: Disk number (default: 2 for ide2)

        Returns:
            Task or success status
        """
        disk_key = f"{disk_interface}{disk_number}"
        disk_value = f"{iso_volid},media=cdrom"

        config = {disk_key: disk_value}

        logger.info(f"Mounting ISO {iso_volid} to VM {vmid} as {disk_key}")
        return self.set_vm_config(node, vmid, config)

    def detach_disk_from_vm(
        self,
        node: str,
        vmid: int,
        disk_interface: str,
        disk_number: int
    ) -> Dict[str, Any]:
        """
        Detach/remove a disk from a VM.

        Args:
            node: Node name
            vmid: VM ID
            disk_interface: Disk interface (scsi, ide, virtio, sata)
            disk_number: Disk number

        Returns:
            Task or success status
        """
        disk_key = f"{disk_interface}{disk_number}"
        # Use delete parameter to remove the disk
        config = {"delete": disk_key}

        logger.info(f"Detaching disk {disk_key} from VM {vmid}")
        return self.set_vm_config(node, vmid, config)

    def unmount_iso_from_vm(
        self,
        node: str,
        vmid: int,
        disk_interface: str = "ide",
        disk_number: int = 2
    ) -> Dict[str, Any]:
        """
        Unmount an ISO file from a VM's CD-ROM device.

        Args:
            node: Node name
            vmid: VM ID
            disk_interface: Disk interface (default: ide)
            disk_number: Disk number (default: 2 for ide2)

        Returns:
            Task or success status
        """
        disk_key = f"{disk_interface}{disk_number}"
        # Setting to "none" unmounts the ISO
        config = {disk_key: "none,media=cdrom"}

        logger.info(f"Unmounting ISO from VM {vmid} at {disk_key}")
        return self.set_vm_config(node, vmid, config)

    def resize_disk(
        self,
        node: str,
        vmid: int,
        disk_interface: str,
        disk_number: int,
        new_size_gb: int
    ) -> Dict[str, Any]:
        """
        Resize a VM disk to a larger size.

        Args:
            node: Node name
            vmid: VM ID
            disk_interface: Disk interface (scsi, ide, virtio, sata)
            disk_number: Disk number
            new_size_gb: New disk size in GB (must be larger than current)

        Returns:
            Task or success status
        """
        disk_key = f"{disk_interface}{disk_number}"

        # Size must be specified with unit (e.g., "100G")
        size_value = f"{new_size_gb}G"

        logger.info(f"Resizing disk {disk_key} on VM {vmid} to {new_size_gb}GB")

        try:
            proxmox = self._get_connection()
            result = proxmox.nodes(node).qemu(vmid).resize.put(
                disk=disk_key,
                size=size_value
            )
            logger.info(f"Successfully resized disk {disk_key} on VM {vmid}")
            return {"status": "resized", "result": result}
        except Exception as e:
            logger.error(f"Failed to resize disk {disk_key} on VM {vmid}: {e}")
            raise

    def set_boot_order(self, node: str, vmid: int, boot_order: List[str]) -> Dict[str, Any]:
        """
        Set boot order for a VM.

        Args:
            node: Node name
            vmid: VM ID
            boot_order: List of boot devices (e.g., ['ide2', 'scsi0'])

        Returns:
            Task or success status
        """
        boot_value = f"order={';'.join(boot_order)}"
        config = {"boot": boot_value}

        logger.info(f"Setting boot order for VM {vmid}: {boot_value}")
        return self.set_vm_config(node, vmid, config)

    # Snapshot Management Methods

    def create_snapshot(
        self,
        node: str,
        vmid: int,
        snapshot_name: str,
        description: Optional[str] = None,
        include_memory: bool = False
    ) -> Dict[str, Any]:
        """
        Create a snapshot of a VM.

        Args:
            node: Node name
            vmid: VM ID
            snapshot_name: Name for the snapshot
            description: Optional description
            include_memory: Include VM memory state (for running VMs)

        Returns:
            Task or success status
        """
        try:
            proxmox = self._get_connection()

            params = {
                "snapname": snapshot_name
            }

            if description:
                params["description"] = description

            if include_memory:
                params["vmstate"] = 1

            result = proxmox.nodes(node).qemu(vmid).snapshot.post(**params)

            logger.info(f"Created snapshot '{snapshot_name}' for VM {vmid}")
            return {"status": "created", "result": result, "snapshot_name": snapshot_name}
        except Exception as e:
            logger.error(f"Failed to create snapshot for VM {vmid}: {e}")
            raise

    def list_snapshots(self, node: str, vmid: int) -> List[Dict[str, Any]]:
        """
        List all snapshots for a VM.

        Args:
            node: Node name
            vmid: VM ID

        Returns:
            List of snapshot information
        """
        try:
            proxmox = self._get_connection()
            snapshots = proxmox.nodes(node).qemu(vmid).snapshot.get()

            logger.info(f"Listed {len(snapshots)} snapshots for VM {vmid}")
            return snapshots
        except Exception as e:
            logger.error(f"Failed to list snapshots for VM {vmid}: {e}")
            raise

    def rollback_snapshot(
        self,
        node: str,
        vmid: int,
        snapshot_name: str
    ) -> Dict[str, Any]:
        """
        Rollback VM to a specific snapshot.

        Args:
            node: Node name
            vmid: VM ID
            snapshot_name: Name of snapshot to rollback to

        Returns:
            Task or success status
        """
        try:
            proxmox = self._get_connection()
            result = proxmox.nodes(node).qemu(vmid).snapshot(snapshot_name).rollback.post()

            logger.info(f"Rolled back VM {vmid} to snapshot '{snapshot_name}'")
            return {"status": "rolled_back", "result": result, "snapshot_name": snapshot_name}
        except Exception as e:
            logger.error(f"Failed to rollback VM {vmid} to snapshot '{snapshot_name}': {e}")
            raise

    def delete_snapshot(
        self,
        node: str,
        vmid: int,
        snapshot_name: str
    ) -> Dict[str, Any]:
        """
        Delete a VM snapshot.

        Args:
            node: Node name
            vmid: VM ID
            snapshot_name: Name of snapshot to delete

        Returns:
            Task or success status
        """
        try:
            proxmox = self._get_connection()
            result = proxmox.nodes(node).qemu(vmid).snapshot(snapshot_name).delete()

            logger.info(f"Deleted snapshot '{snapshot_name}' from VM {vmid}")
            return {"status": "deleted", "result": result, "snapshot_name": snapshot_name}
        except Exception as e:
            logger.error(f"Failed to delete snapshot '{snapshot_name}' from VM {vmid}: {e}")
            raise

    # VM Control Methods

    def force_stop_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Force stop a VM immediately (hard stop).

        This immediately stops the VM process without graceful shutdown.

        Args:
            node: Node name
            vmid: VM ID

        Returns:
            Task or success status
        """
        try:
            proxmox = self._get_connection()
            result = proxmox.nodes(node).qemu(vmid).status.stop.post()

            logger.info(f"Force stopped VM {vmid}")
            return {"status": "force_stopped", "result": result}
        except Exception as e:
            logger.error(f"Failed to force stop VM {vmid}: {e}")
            raise

    def reboot_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Reboot a VM.

        Args:
            node: Node name
            vmid: VM ID

        Returns:
            Task or success status
        """
        try:
            proxmox = self._get_connection()
            result = proxmox.nodes(node).qemu(vmid).status.reboot.post()

            logger.info(f"Rebooted VM {vmid}")
            return {"status": "rebooted", "result": result}
        except Exception as e:
            logger.error(f"Failed to reboot VM {vmid}: {e}")
            raise

    def reset_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """
        Reset a VM (hard reset, like pressing reset button).

        Args:
            node: Node name
            vmid: VM ID

        Returns:
            Task or success status
        """
        try:
            proxmox = self._get_connection()
            result = proxmox.nodes(node).qemu(vmid).status.reset.post()

            logger.info(f"Reset VM {vmid}")
            return {"status": "reset", "result": result}
        except Exception as e:
            logger.error(f"Failed to reset VM {vmid}: {e}")
            raise

    def resize_vm(
        self,
        node: str,
        vmid: int,
        cpu_cores: Optional[int] = None,
        cpu_sockets: Optional[int] = None,
        memory_mb: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Resize VM CPU and/or memory.

        Args:
            node: Node name
            vmid: VM ID
            cpu_cores: Number of CPU cores
            cpu_sockets: Number of CPU sockets
            memory_mb: Memory in MB

        Returns:
            Task or success status
        """
        try:
            config = {}

            if cpu_cores is not None:
                config["cores"] = cpu_cores

            if cpu_sockets is not None:
                config["sockets"] = cpu_sockets

            if memory_mb is not None:
                config["memory"] = memory_mb

            if not config:
                raise ValueError("At least one resource (CPU or memory) must be specified")

            logger.info(f"Resizing VM {vmid} with config: {config}")
            return self.set_vm_config(node, vmid, config)
        except Exception as e:
            logger.error(f"Failed to resize VM {vmid}: {e}")
            raise

    # ------------------------------------------------------------------ #
    #  SDN (Software Defined Network) methods
    # ------------------------------------------------------------------ #

    def get_sdn_zones(self) -> List[Dict[str, Any]]:
        """List all SDN zones on the cluster.

        Returns:
            List of zone dicts (each with ``zone``, ``type``, …)
        """
        try:
            proxmox = self._get_connection()
            return proxmox.cluster.sdn.zones.get()
        except Exception as e:
            logger.error(f"Failed to list SDN zones: {e}")
            return []

    def create_sdn_zone(self, zone: str, zone_type: str, **kwargs) -> Dict[str, Any]:
        """Create an SDN zone.

        Args:
            zone: Zone name (e.g. ``isp-vxlan``)
            zone_type: Zone type (``vlan``, ``vxlan``, ``simple``, …)
            **kwargs: Additional zone parameters passed to the API

        Returns:
            API result

        Raises:
            RuntimeError: If zone creation fails
        """
        try:
            proxmox = self._get_connection()
            payload = {"zone": zone, "type": zone_type, **kwargs}
            result = proxmox.cluster.sdn.zones.post(**payload)
            logger.info(f"Created SDN zone {zone} (type={zone_type})")
            return result
        except Exception as e:
            logger.error(f"Failed to create SDN zone {zone}: {e}")
            raise RuntimeError(f"Failed to create SDN zone {zone}: {e}") from e

    def create_sdn_vnet(self, vnet_name: str, zone: str, **kwargs) -> Dict[str, Any]:
        """Create an SDN VNet.

        The VNet must belong to an existing zone. For VLAN zones you need
        ``tag=<vlan_id>``; for VXLAN zones you need ``vni=<vni>``.

        Args:
            vnet_name: VNet name (max 12 chars — ``vn-{name}`` must be <= 15)
            zone: Zone name
            **kwargs: VNet parameters (tag, vni, …)

        Returns:
            API result

        Raises:
            RuntimeError: If VNet creation fails
        """
        try:
            proxmox = self._get_connection()
            payload = {"vnet": vnet_name, "zone": zone, **kwargs}
            result = proxmox.cluster.sdn.vnets.post(**payload)
            logger.info(f"Created SDN VNet {vnet_name} in zone {zone}")
            return result
        except Exception as e:
            logger.error(f"Failed to create SDN VNet {vnet_name}: {e}")
            raise RuntimeError(f"Failed to create SDN VNet {vnet_name}: {e}") from e

    def delete_sdn_vnet(self, vnet_name: str) -> Dict[str, Any]:
        """Delete an SDN VNet.

        Args:
            vnet_name: VNet name to delete

        Returns:
            API result

        Raises:
            RuntimeError: If deletion fails
        """
        try:
            proxmox = self._get_connection()
            result = proxmox.cluster.sdn.vnets(vnet_name).delete()
            logger.info(f"Deleted SDN VNet {vnet_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete SDN VNet {vnet_name}: {e}")
            raise RuntimeError(f"Failed to delete SDN VNet {vnet_name}: {e}") from e

    def apply_sdn(self) -> Dict[str, Any]:
        """Apply pending SDN configuration changes.

        Must be called after creating / deleting zones or VNets.

        Returns:
            API result
        """
        try:
            proxmox = self._get_connection()
            result = proxmox.cluster.sdn.put()
            logger.info("Applied SDN configuration")
            return result
        except Exception as e:
            logger.warning(f"Failed to apply SDN configuration: {e}")
            return {}

    def get_vm_rrd_data(self, node: str, vmid: int, timeframe: str = "hour") -> List[Dict]:
        """Get VM resource usage data from Proxmox RRD API.

        Args:
            node: Proxmox node name
            vmid: VM ID
            timeframe: hour, day, week, month, year

        Returns:
            List of RRD data points with netin/netout bytes
        """
        try:
            proxmox = self._get_connection()
            result = proxmox.nodes(node).qemu(vmid).rrd.get(timeframe=timeframe, cf="AVERAGE")
            return result
        except Exception as e:
            logger.error(f"Failed to get RRD data for VM {vmid} on node {node}: {e}")
            return []

    # ------------------------------------------------------------------ #
    #  Network config helpers
    # ------------------------------------------------------------------ #

    def build_network_config(
        self,
        interface_name: str,
        vlan_id: Optional[int] = None,
        bridge: str = "vmbr0",
        model: str = "virtio",
        mac_address: Optional[str] = None,
        firewall: bool = True,
        rate_limit: Optional[int] = None
    ) -> str:
        """Build Proxmox network interface configuration string.

        Creates network configuration with optional VLAN tagging for VPC network isolation.

        Args:
            interface_name: Interface name (net0, net1, net2, net3)
            vlan_id: Optional VLAN ID for network isolation (100-4094)
            bridge: Bridge name (default: vmbr0)
            model: NIC model (virtio, e1000, rtl8139)
            mac_address: Optional MAC address (auto-generated if None)
            firewall: Enable Proxmox firewall on interface
            rate_limit: Optional rate limit in MB/s

        Returns:
            Proxmox network config string

        Examples:
            >>> # Without VLAN (legacy/untagged)
            >>> build_network_config("net0")
            'virtio,bridge=vmbr0,firewall=1'

            >>> # With VLAN tagging for VPC isolation
            >>> build_network_config("net0", vlan_id=100, bridge="vmbr0")
            'virtio,bridge=vmbr0,tag=100,firewall=1'

            >>> # With custom MAC and rate limit
            >>> build_network_config("net1", vlan_id=200, mac_address="AA:BB:CC:DD:EE:FF", rate_limit=100)
            'virtio=AA:BB:CC:DD:EE:FF,bridge=vmbr0,tag=200,firewall=1,rate=100'
        """
        # Start with model
        config_parts = [model]

        # Add MAC address if specified
        if mac_address:
            config_parts[0] = f"{model}={mac_address}"

        # Add bridge (required)
        config_parts.append(f"bridge={bridge}")

        # Add VLAN tag if specified
        if vlan_id is not None:
            if not (1 <= vlan_id <= 4094):
                raise ValueError(f"VLAN ID must be between 1 and 4094, got {vlan_id}")
            config_parts.append(f"tag={vlan_id}")

        # Add firewall setting
        if firewall:
            config_parts.append("firewall=1")
        else:
            config_parts.append("firewall=0")

        # Add rate limit if specified
        if rate_limit is not None:
            config_parts.append(f"rate={rate_limit}")

        config_string = ",".join(config_parts)

        logger.debug(
            f"Built network config for {interface_name}: {config_string} "
            f"(VLAN: {vlan_id if vlan_id else 'untagged'})"
        )

        return config_string

    def attach_network_to_vm(
        self,
        node: str,
        vmid: int,
        interface_name: str,
        vlan_id: Optional[int] = None,
        bridge: str = "vmbr0",
        model: str = "virtio",
        mac_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Attach network interface to VM with optional VLAN tagging.

        Args:
            node: Node name
            vmid: VM ID
            interface_name: Interface name (net0, net1, net2, net3)
            vlan_id: Optional VLAN ID for network isolation
            bridge: Bridge name
            model: NIC model
            mac_address: Optional MAC address

        Returns:
            Configuration result

        Example:
            >>> proxmox_service.attach_network_to_vm(
            ...     node="pve1",
            ...     vmid=100,
            ...     interface_name="net1",
            ...     vlan_id=100,
            ...     bridge="vmbr0"
            ... )
        """
        # Build network configuration
        net_config = self.build_network_config(
            interface_name=interface_name,
            vlan_id=vlan_id,
            bridge=bridge,
            model=model,
            mac_address=mac_address
        )

        # Apply configuration to VM
        config = {interface_name: net_config}
        result = self.set_vm_config(node, vmid, config)

        logger.info(
            f"Attached network interface {interface_name} to VM {vmid} "
            f"with VLAN {vlan_id} on bridge {bridge}"
        )

        return result

    def detach_network_from_vm(
        self,
        node: str,
        vmid: int,
        interface_name: str
    ) -> Dict[str, Any]:
        """Detach network interface from VM.

        Args:
            node: Node name
            vmid: VM ID
            interface_name: Interface name (net0, net1, net2, net3)

        Returns:
            Configuration result

        Example:
            >>> proxmox_service.detach_network_from_vm("pve1", 100, "net1")
        """
        # Set interface to empty string to delete it
        config = {interface_name: ""}
        result = self.set_vm_config(node, vmid, config)

        logger.info(f"Detached network interface {interface_name} from VM {vmid}")

        return result

    # ==================== Firewall Methods ====================

    def get_vm_firewall_options(
        self,
        node: str,
        vmid: int,
        vm_type: str = "qemu"
    ) -> Dict[str, Any]:
        """Get firewall options for a VM/CT.

        Args:
            node: Proxmox node name
            vmid: VM/CT ID on Proxmox
            vm_type: 'qemu' or 'lxc'

        Returns:
            Dict of firewall options
        """
        proxmox = self._get_connection()
        if vm_type == "lxc":
            return proxmox.nodes(node).lxc(vmid).firewall.options.get()
        return proxmox.nodes(node).qemu(vmid).firewall.options.get()

    def enable_vm_firewall(
        self,
        node: str,
        vmid: int,
        vm_type: str = "qemu"
    ) -> None:
        """Enable firewall for a VM/CT.

        Args:
            node: Proxmox node name
            vmid: VM/CT ID on Proxmox
            vm_type: 'qemu' or 'lxc'
        """
        proxmox = self._get_connection()
        params = {"enable": 1}
        if vm_type == "lxc":
            proxmox.nodes(node).lxc(vmid).firewall.options.put(**params)
        else:
            proxmox.nodes(node).qemu(vmid).firewall.options.put(**params)
        logger.info(f"Enabled firewall for {vm_type} {vmid} on {node}")

    def disable_vm_firewall(
        self,
        node: str,
        vmid: int,
        vm_type: str = "qemu"
    ) -> None:
        """Disable firewall for a VM/CT.

        Args:
            node: Proxmox node name
            vmid: VM/CT ID on Proxmox
            vm_type: 'qemu' or 'lxc'
        """
        proxmox = self._get_connection()
        params = {"enable": 0}
        if vm_type == "lxc":
            proxmox.nodes(node).lxc(vmid).firewall.options.put(**params)
        else:
            proxmox.nodes(node).qemu(vmid).firewall.options.put(**params)
        logger.info(f"Disabled firewall for {vm_type} {vmid} on {node}")

    def get_vm_firewall_rules(
        self,
        node: str,
        vmid: int,
        vm_type: str = "qemu"
    ) -> List[Dict[str, Any]]:
        """List firewall rules for a VM/CT.

        Args:
            node: Proxmox node name
            vmid: VM/CT ID on Proxmox
            vm_type: 'qemu' or 'lxc'

        Returns:
            List of rule dicts with 'pos' field
        """
        proxmox = self._get_connection()
        if vm_type == "lxc":
            return proxmox.nodes(node).lxc(vmid).firewall.rules.get()
        return proxmox.nodes(node).qemu(vmid).firewall.rules.get()

    def create_vm_firewall_rule(
        self,
        node: str,
        vmid: int,
        vm_type: str = "qemu",
        **rule_params
    ) -> None:
        """Create a firewall rule for a VM/CT.

        Args:
            node: Proxmox node name
            vmid: VM/CT ID on Proxmox
            vm_type: 'qemu' or 'lxc'
            **rule_params: Rule parameters (type, action, source, dest, etc.)
        """
        proxmox = self._get_connection()
        if vm_type == "lxc":
            proxmox.nodes(node).lxc(vmid).firewall.rules.post(**rule_params)
        else:
            proxmox.nodes(node).qemu(vmid).firewall.rules.post(**rule_params)
        logger.info(
            f"Created firewall rule for {vm_type} {vmid} on {node}: "
            f"{rule_params.get('type')} {rule_params.get('action')}"
        )

    def update_vm_firewall_rule(
        self,
        node: str,
        vmid: int,
        vm_type: str = "qemu",
        pos: int = 0,
        **rule_params
    ) -> None:
        """Update a firewall rule for a VM/CT.

        Args:
            node: Proxmox node name
            vmid: VM/CT ID on Proxmox
            vm_type: 'qemu' or 'lxc'
            pos: Rule position in the ruleset
            **rule_params: Updated rule parameters
        """
        proxmox = self._get_connection()
        if vm_type == "lxc":
            proxmox.nodes(node).lxc(vmid).firewall.rules(pos).put(**rule_params)
        else:
            proxmox.nodes(node).qemu(vmid).firewall.rules(pos).put(**rule_params)
        logger.info(f"Updated firewall rule at pos {pos} for {vm_type} {vmid} on {node}")

    def delete_vm_firewall_rule(
        self,
        node: str,
        vmid: int,
        vm_type: str = "qemu",
        pos: int = 0
    ) -> None:
        """Delete a firewall rule from a VM/CT.

        Args:
            node: Proxmox node name
            vmid: VM/CT ID on Proxmox
            vm_type: 'qemu' or 'lxc'
            pos: Rule position in the ruleset
        """
        proxmox = self._get_connection()
        if vm_type == "lxc":
            proxmox.nodes(node).lxc(vmid).firewall.rules(pos).delete()
        else:
            proxmox.nodes(node).qemu(vmid).firewall.rules(pos).delete()
        logger.info(f"Deleted firewall rule at pos {pos} for {vm_type} {vmid} on {node}")

    # ==================== Async Wrappers ====================
    # These methods wrap sync Proxmox API calls in asyncio.to_thread()
    # to prevent blocking the event loop when called from async endpoints.

    async def get_next_vmid_async(self, node: Optional[str] = None) -> int:
        """Async wrapper for get_next_vmid."""
        return await asyncio.to_thread(self.get_next_vmid, node)

    async def select_best_node_async(self) -> Optional[str]:
        """Async wrapper for select_best_node."""
        return await asyncio.to_thread(self.select_best_node)

    async def create_vm_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for create_vm."""
        return await asyncio.to_thread(self.create_vm, *args, **kwargs)

    async def start_vm_async(self, node: str, vmid: int) -> Dict[str, Any]:
        """Async wrapper for start_vm."""
        return await asyncio.to_thread(self.start_vm, node, vmid)

    async def stop_vm_async(self, node: str, vmid: int, force: bool = False) -> Dict[str, Any]:
        """Async wrapper for stop_vm."""
        return await asyncio.to_thread(self.stop_vm, node, vmid, force)

    async def restart_vm_async(self, node: str, vmid: int) -> Dict[str, Any]:
        """Async wrapper for restart_vm."""
        return await asyncio.to_thread(self.restart_vm, node, vmid)

    async def delete_vm_async(self, node: str, vmid: int) -> Dict[str, Any]:
        """Async wrapper for delete_vm."""
        return await asyncio.to_thread(self.delete_vm, node, vmid)

    async def get_console_url_async(self, node: str, vmid: int) -> Dict[str, Any]:
        """Async wrapper for get_console_url."""
        return await asyncio.to_thread(self.get_console_url, node, vmid)

    async def get_vm_status_async(self, node: str, vmid: int) -> Dict[str, Any]:
        """Async wrapper for get_vm_status."""
        return await asyncio.to_thread(self.get_vm_status, node, vmid)

    async def force_stop_vm_async(self, node: str, vmid: int) -> Dict[str, Any]:
        """Async wrapper for force_stop_vm."""
        return await asyncio.to_thread(self.force_stop_vm, node, vmid)

    async def reboot_vm_async(self, node: str, vmid: int) -> Dict[str, Any]:
        """Async wrapper for reboot_vm."""
        return await asyncio.to_thread(self.reboot_vm, node, vmid)

    async def reset_vm_async(self, node: str, vmid: int) -> Dict[str, Any]:
        """Async wrapper for reset_vm."""
        return await asyncio.to_thread(self.reset_vm, node, vmid)

    async def resize_vm_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for resize_vm."""
        return await asyncio.to_thread(self.resize_vm, *args, **kwargs)

    async def convert_vm_to_template_async(self, node: str, vmid: int) -> Dict[str, Any]:
        """Async wrapper for convert_vm_to_template."""
        return await asyncio.to_thread(self.convert_vm_to_template, node, vmid)

    async def clone_vm_from_template_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for clone_vm_from_template."""
        return await asyncio.to_thread(self.clone_vm_from_template, *args, **kwargs)

    async def create_lxc_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for create_lxc."""
        return await asyncio.to_thread(self.create_lxc, *args, **kwargs)

    async def start_lxc_async(self, node: str, vmid: int) -> Dict[str, Any]:
        """Async wrapper for start_lxc."""
        return await asyncio.to_thread(self.start_lxc, node, vmid)

    async def stop_lxc_async(self, node: str, vmid: int, force: bool = False) -> Dict[str, Any]:
        """Async wrapper for stop_lxc."""
        return await asyncio.to_thread(self.stop_lxc, node, vmid, force)

    async def get_storage_pools_async(self, node: str) -> List[Dict[str, Any]]:
        """Async wrapper for get_storage_pools."""
        return await asyncio.to_thread(self.get_storage_pools, node)

    async def get_storage_content_async(self, node: str, storage: str, content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Async wrapper for get_storage_content."""
        return await asyncio.to_thread(self.get_storage_content, node, storage, content_type)

    async def build_network_config_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for build_network_config."""
        return await asyncio.to_thread(self.build_network_config, *args, **kwargs)

    async def attach_network_to_vm_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for attach_network_to_vm."""
        return await asyncio.to_thread(self.attach_network_to_vm, *args, **kwargs)

    async def detach_network_from_vm_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for detach_network_from_vm."""
        return await asyncio.to_thread(self.detach_network_from_vm, *args, **kwargs)

    async def mount_iso_to_vm_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for mount_iso_to_vm."""
        return await asyncio.to_thread(self.mount_iso_to_vm, *args, **kwargs)

    async def unmount_iso_from_vm_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for unmount_iso_from_vm."""
        return await asyncio.to_thread(self.unmount_iso_from_vm, *args, **kwargs)

    async def list_snapshots_async(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Async wrapper for list_snapshots."""
        return await asyncio.to_thread(self.list_snapshots, *args, **kwargs)

    async def create_snapshot_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for create_snapshot."""
        return await asyncio.to_thread(self.create_snapshot, *args, **kwargs)

    async def rollback_snapshot_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for rollback_snapshot."""
        return await asyncio.to_thread(self.rollback_snapshot, *args, **kwargs)

    async def delete_snapshot_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for delete_snapshot."""
        return await asyncio.to_thread(self.delete_snapshot, *args, **kwargs)

    async def resize_disk_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for resize_disk."""
        return await asyncio.to_thread(self.resize_disk, *args, **kwargs)

    async def test_connection_async(self) -> bool:
        """Async wrapper for test_connection."""
        return await asyncio.to_thread(self.test_connection)

    async def add_disk_to_vm_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for add_disk_to_vm."""
        return await asyncio.to_thread(self.add_disk_to_vm, *args, **kwargs)

    async def detach_disk_from_vm_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async wrapper for detach_disk_from_vm."""
        return await asyncio.to_thread(self.detach_disk_from_vm, *args, **kwargs)
