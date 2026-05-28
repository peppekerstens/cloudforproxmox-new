"""Unit tests for ProxmoxService network config builder."""
import pytest

from app.services.proxmox_service import ProxmoxService


class TestBuildNetworkConfig:
    """Test build_network_config string generation."""

    def setup_method(self):
        self.service = ProxmoxService(
            host="127.0.0.1",
            user="root@pam",
            token_name="test",
            token_value="test",
        )

    def test_untagged_on_vmbr0(self):
        """Default config: virtio on vmbr0 with firewall."""
        result = self.service.build_network_config("net0")
        assert result == "virtio,bridge=vmbr0,firewall=1"

    def test_vlan_tagged(self):
        """VLAN tag should be included."""
        result = self.service.build_network_config(
            "net0", vlan_id=100, bridge="vmbr0"
        )
        assert "tag=100" in result
        assert "bridge=vmbr0" in result

    def test_vnet_bridge_no_tag(self):
        """VNet bridge (VXLAN/Simple) should have no tag."""
        result = self.service.build_network_config(
            "net0", vlan_id=None, bridge="vn-vxa5345e"
        )
        assert "bridge=vn-vxa5345e" in result
        assert "tag=" not in result

    def test_custom_mac(self):
        """MAC address should be included in config."""
        result = self.service.build_network_config(
            "net0", mac_address="AA:BB:CC:DD:EE:FF"
        )
        assert "virtio=AA:BB:CC:DD:EE:FF" in result

    def test_firewall_disabled(self):
        """Firewall can be disabled."""
        result = self.service.build_network_config(
            "net0", firewall=False
        )
        assert "firewall=0" in result

    def test_rate_limit(self):
        """Rate limit should be included."""
        result = self.service.build_network_config(
            "net0", rate_limit=100
        )
        assert "rate=100" in result

    def test_invalid_vlan_id_too_low(self):
        """VLAN ID < 1 should raise ValueError."""
        with pytest.raises(ValueError, match="between 1 and 4094"):
            self.service.build_network_config("net0", vlan_id=0)

    def test_invalid_vlan_id_too_high(self):
        """VLAN ID > 4094 should raise ValueError."""
        with pytest.raises(ValueError, match="between 1 and 4094"):
            self.service.build_network_config("net0", vlan_id=4095)

    def test_vlan_id_none_skips_validation(self):
        """vlan_id=None should not trigger validation (VXLAN/Simple)."""
        result = self.service.build_network_config(
            "net0", vlan_id=None, bridge="vn-vxa5345e"
        )
        assert "bridge=vn-vxa5345e" in result

    def test_full_config(self):
        """All options combined."""
        result = self.service.build_network_config(
            "net0",
            vlan_id=200,
            bridge="vmbr0",
            model="virtio",
            mac_address="AA:BB:CC:DD:EE:FF",
            firewall=True,
            rate_limit=50,
        )
        assert result == (
            "virtio=AA:BB:CC:DD:EE:FF,"
            "bridge=vmbr0,"
            "tag=200,"
            "firewall=1,"
            "rate=50"
        )
