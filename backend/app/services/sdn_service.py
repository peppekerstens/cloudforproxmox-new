"""Proxmox SDN orchestration service for VNet lifecycle management."""
from typing import Optional
import logging

from app.services.proxmox_service import ProxmoxService

logger = logging.getLogger(__name__)

# SDN zone names — created once per cluster
# Proxmox zone IDs: max 8 chars, alphanumeric only.
SDN_ZONE_VLAN = "ispvlan"
SDN_ZONE_VXLAN = "ispvxlan"
SDN_ZONE_SIMPLE = "ispsimpl"

# Max 8 characters for Proxmox zone / VNet IDs (alphanumeric only, must start with letter).
# Bridge names are vn-{vnet-id} (11 chars, well within the 15-char IFNAMSIZ limit).
VNET_NAME_CHARS = 6  # 2-char prefix + 6 UUID chars = 8 total


def _short_name(network_id: str) -> str:
    """Generate a short VNet/zone name from a network UUID (max 8 chars, starts with letter)."""
    return f"vx{network_id[:VNET_NAME_CHARS]}"


def _vnet_bridge(network_id: str) -> str:
    """Return the bridge name Proxmox will create for a VNet.

    Proxmox SDN creates a bridge named ``vn-{vnet-name}`` for each VNet.
    """
    return f"vn-{_short_name(network_id)}"


class SDNService:
    """Orchestrates Proxmox SDN zones and VNets.

    Responsibilities:
    - Ensure required SDN zones exist on the cluster
    - Create / delete VNets for networks
    - Apply SDN config changes
    """

    def __init__(self, proxmox: ProxmoxService):
        self.proxmox = proxmox

    def ensure_zone(self, network_type: str) -> str:
        """Ensure the SDN zone for a given network type exists.

        Creates the zone only if it doesn't already exist.
        Only the zone needed for the requested network type is created.

        Args:
            network_type: 'vlan', 'vxlan', or 'simple'

        Returns:
            "created" or "already_exists"

        Raises:
            RuntimeError: If zone creation fails
        """
        zone_map = {
            "vlan": (SDN_ZONE_VLAN, "vlan"),
            "vxlan": (SDN_ZONE_VXLAN, "vxlan"),
            "simple": (SDN_ZONE_SIMPLE, "simple"),
        }

        if network_type not in zone_map:
            raise ValueError(f"Unsupported network_type: {network_type}")

        zone_name, zone_type = zone_map[network_type]

        existing = self.proxmox.get_sdn_zones()
        existing_names = {z.get("zone") for z in existing}

        if zone_name in existing_names:
            return "already_exists"

        if network_type == "vxlan":
            peers = self._get_cluster_node_ips()
            self.proxmox.create_sdn_zone(zone_name, zone_type, peers=peers)
        elif network_type == "vlan":
            # VLAN zones must reference the underlying bridge
            self.proxmox.create_sdn_zone(zone_name, zone_type, bridge="vmbr0")
        else:
            self.proxmox.create_sdn_zone(zone_name, zone_type)

        self.proxmox.apply_sdn()
        return "created"

    def _get_cluster_node_ips(self) -> str:
        """Get comma-separated list of cluster node IPs for VXLAN peers."""
        members = self.proxmox.get_cluster_status()
        ips = []
        for member in members:
            if member.get("type") != "node":
                continue
            if not member.get("online"):
                continue
            addr = member.get("ip")
            if addr:
                ips.append(addr)
        if not ips:
            logger.warning("Could not determine cluster node IPs for VXLAN peers")
            return ""
        return ",".join(ips)

    def create_vnet(self, network_id: str, network_type: str,
                    vlan_id: Optional[int] = None,
                    vni: Optional[int] = None) -> dict:
        """Create a VNet for a network in the appropriate SDN zone.

        The required SDN zone is created automatically if it doesn't exist.

        Args:
            network_id: Network UUID
            network_type: 'vlan', 'vxlan', or 'simple'
            vlan_id: VLAN tag (required for vlan type)
            vni: VXLAN VNI (required for vxlan type)

        Returns:
            Dict with vnet_name and bridge name

        Raises:
            ValueError: If required params missing for the network type
            RuntimeError: If Proxmox API call fails
        """
        vnet_name = _short_name(network_id)

        if network_type == "vlan":
            if vlan_id is None:
                raise ValueError("vlan_id is required for network_type='vlan'")
            zone = SDN_ZONE_VLAN
            params = {"tag": str(vlan_id)}
        elif network_type == "vxlan":
            if vni is None:
                raise ValueError("vni is required for network_type='vxlan'")
            zone = SDN_ZONE_VXLAN
            # VXLAN VNets use 'tag' for the VNI identifier
            params = {"tag": str(vni)}
        elif network_type == "simple":
            zone = SDN_ZONE_SIMPLE
            params = {}
        else:
            raise ValueError(f"Unsupported network_type: {network_type}")

        # Ensure the zone exists before creating the VNet
        self.ensure_zone(network_type)

        self.proxmox.create_sdn_vnet(
            vnet_name=vnet_name,
            zone=zone,
            **params
        )
        self.proxmox.apply_sdn()

        bridge = _vnet_bridge(network_id)
        logger.info(
            f"Created SDN VNet {vnet_name} in zone {zone} "
            f"(bridge={bridge}, params={params})"
        )

        return {
            "sdn_zone": zone,
            "sdn_vnet": vnet_name,
            "bridge": bridge,
        }

    def delete_vnet(self, network_id: str) -> None:
        """Delete a VNet and re-apply SDN config.

        Args:
            network_id: Network UUID whose VNet to delete
        """
        vnet_name = _short_name(network_id)
        try:
            self.proxmox.delete_sdn_vnet(vnet_name)
            self.proxmox.apply_sdn()
            logger.info(f"Deleted SDN VNet {vnet_name}")
        except Exception as e:
            logger.warning(f"Failed to delete SDN VNet {vnet_name}: {e}")

    @staticmethod
    def get_vm_network_config(network_type: str,
                              bridge: str,
                              vlan_id: Optional[int] = None,
                              vnet_bridge: Optional[str] = None) -> dict:
        """Build the Proxmox VM network config for a given network type.

        Returns a dict suitable for ``build_network_config()``.

        Args:
            network_type: 'vlan', 'vxlan', or 'simple'
            bridge: The Proxmox bridge (used for vlan type)
            vlan_id: VLAN tag (used for vlan type)
            vnet_bridge: The SDN VNet bridge (used for vxlan/simple)

        Returns:
            Dict with keys for build_network_config
        """
        if network_type == "vlan":
            return {
                "bridge": bridge,
                "vlan_id": vlan_id,
            }
        else:
            # vxlan / simple — VM attaches directly to the VNet bridge
            return {
                "bridge": vnet_bridge or bridge,
                "vlan_id": None,
            }
