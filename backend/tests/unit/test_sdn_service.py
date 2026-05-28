"""Unit tests for SDN service naming conventions and config generation."""
import pytest

from app.services.sdn_service import (
    SDNService,
    SDN_ZONE_VLAN,
    SDN_ZONE_VXLAN,
    SDN_ZONE_SIMPLE,
    _short_name,
    _vnet_bridge,
    VNET_NAME_CHARS,
)


# --------------------------------------------------------------------------- #
#  Naming convention tests (pure functions, no Proxmox needed)
# --------------------------------------------------------------------------- #

class TestNamingConventions:
    """Test SDN ID naming constraints."""

    def test_zone_names_max_8_chars(self):
        """Proxmox zone IDs must be <= 8 characters."""
        assert len(SDN_ZONE_VLAN) <= 8
        assert len(SDN_ZONE_VXLAN) <= 8
        assert len(SDN_ZONE_SIMPLE) <= 8

    def test_zone_names_alphanumeric(self):
        """Proxmox zone IDs must be alphanumeric only."""
        assert SDN_ZONE_VLAN.isalnum()
        assert SDN_ZONE_VXLAN.isalnum()
        assert SDN_ZONE_SIMPLE.isalnum()

    def test_vnet_name_max_8_chars(self):
        """VNet IDs must be <= 8 characters."""
        uuid = "a5345ea6-caaa-4838-bb66-69c5b8d88ef2"
        name = _short_name(uuid)
        assert len(name) <= 8

    def test_vnet_name_starts_with_letter(self):
        """Proxmox IDs must start with a letter."""
        uuid = "0ee900e7-9b99-4949-a504-8eb70573c547"
        name = _short_name(uuid)
        assert name[0].isalpha()

    def test_vnet_name_alphanumeric(self):
        """VNet IDs must be alphanumeric."""
        uuid = "a5345ea6-caaa-4838-bb66-69c5b8d88ef2"
        name = _short_name(uuid)
        assert name.isalnum()

    def test_bridge_name_within_ifnamsiz(self):
        """Bridge name vn-{vnet} must be <= 15 chars (IFNAMSIZ-1)."""
        uuid = "a5345ea6-caaa-4838-bb66-69c5b8d88ef2"
        bridge = _vnet_bridge(uuid)
        assert len(bridge) <= 15

    def test_bridge_name_prefix(self):
        """Bridge names must start with vn-."""
        uuid = "a5345ea6-caaa-4838-bb66-69c5b8d88ef2"
        bridge = _vnet_bridge(uuid)
        assert bridge.startswith("vn-")

    def test_vnet_name_chars_constant(self):
        """VNET_NAME_CHARS should leave room for prefix."""
        # vx + 6 chars = 8 total (max Proxmox ID length)
        assert VNET_NAME_CHARS + 2 <= 8


# --------------------------------------------------------------------------- #
#  VM network config generation tests
# --------------------------------------------------------------------------- #

class TestVMNetworkConfig:
    """Test get_vm_network_config for each network type."""

    def test_vlan_config_uses_tag(self):
        """VLAN type should return bridge + vlan_id."""
        result = SDNService.get_vm_network_config(
            network_type="vlan",
            bridge="vmbr0",
            vlan_id=100,
        )
        assert result["bridge"] == "vmbr0"
        assert result["vlan_id"] == 100

    def test_vxlan_config_uses_vnet_bridge(self):
        """VXLAN type should return VNet bridge with no tag."""
        result = SDNService.get_vm_network_config(
            network_type="vxlan",
            bridge="vmbr0",
            vnet_bridge="vn-vxa5345e",
        )
        assert result["bridge"] == "vn-vxa5345e"
        assert result["vlan_id"] is None

    def test_simple_config_uses_vnet_bridge(self):
        """Simple type should return VNet bridge with no tag."""
        result = SDNService.get_vm_network_config(
            network_type="simple",
            bridge="vmbr0",
            vnet_bridge="vn-vx477b1b",
        )
        assert result["bridge"] == "vn-vx477b1b"
        assert result["vlan_id"] is None

    def test_vlan_config_ignores_vnet_bridge(self):
        """VLAN type should ignore vnet_bridge parameter."""
        result = SDNService.get_vm_network_config(
            network_type="vlan",
            bridge="vmbr0",
            vlan_id=200,
            vnet_bridge="vn-vx123456",
        )
        assert result["bridge"] == "vmbr0"
        assert result["vlan_id"] == 200
